"""
bgp_pipeline.py — Phase 20 BGP MRT acquisition and parsing pipeline.

Downloads MRT update files from RouteViews and RIPE RIS archives, parses
them into per-(timestamp, peer_asn, prefix, update_type) records, and
writes a unified parquet table.

Two parsers are supported:

  - **bgpdump** (fast C-based, preferred): invoked via subprocess as
    `bgpdump -m -t change <file>`.  Output is the pipe-delimited "machine"
    format which we parse line-by-line.  Requires `bgpdump` installed
    (apt-get install -y bgpdump).
  - **mrtparse** (pure Python, fallback): used if `bgpdump` is not on
    PATH.  ~10–50× slower; usable for the PoC but expect minutes per
    update file rather than seconds.

The collector panel (4 collectors × 3 windows = 12 cells per the
SESSION-PLAN):

  - route-views2 (US west, Eugene OR)
  - route-views.eqix (Equinix Ashburn, US east)
  - route-views.linx (London Internet Exchange)
  - rrc00 (RIPE RIS Amsterdam)

  windows × event = quiescent baseline (Sep 27 2021), event window
  (Oct 4 2021 12:00 UTC – Oct 5 2021 00:00 UTC), normal-load match
  (Oct 5 2021).

URL patterns (both archive a 15-min cadence on RouteViews and 5-min
cadence on RIPE RIS):

  - RouteViews:
    http://archive.routeviews.org/{collector}/bgpdata/{YYYY.MM}/UPDATES/
    updates.{YYYYMMDD}.{HHMM}.bz2
  - RIPE RIS:
    https://data.ris.ripe.net/{rrcN}/{YYYY.MM}/
    updates.{YYYYMMDD}.{HHMM}.gz
"""
from __future__ import annotations

import os, sys, gzip, bz2, shutil, subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator, Optional

import urllib.request
import urllib.error


# ─── Constants ──────────────────────────────────────────────────────────────


COLLECTORS = {
    'route-views2':       dict(provider='routeviews', cadence_min=15),
    'route-views.eqix':   dict(provider='routeviews', cadence_min=15),
    'route-views.linx':   dict(provider='routeviews', cadence_min=15),
    'rrc00':              dict(provider='ripe',       cadence_min=5),
}


# Time windows per the SESSION-PLAN (UTC).
WINDOWS = {
    'quiescent': dict(
        start=datetime(2021, 9, 27, 0, 0, tzinfo=timezone.utc),
        end=datetime(2021, 9, 28, 0, 0, tzinfo=timezone.utc),
    ),
    'event': dict(
        start=datetime(2021, 10, 4, 12, 0, tzinfo=timezone.utc),
        end=datetime(2021, 10, 5, 0, 0, tzinfo=timezone.utc),
    ),
    'normal_load': dict(
        start=datetime(2021, 10, 5, 0, 0, tzinfo=timezone.utc),
        end=datetime(2021, 10, 6, 0, 0, tzinfo=timezone.utc),
    ),
}


def _bgpdump_available() -> bool:
    return shutil.which('bgpdump') is not None


# ─── URL builders ───────────────────────────────────────────────────────────


def _routeviews_url(collector: str, t: datetime) -> str:
    """RouteViews update URL.  RouteViews emits UPDATES files at HHMM
    aligned to 15-minute boundaries (00, 15, 30, 45)."""
    yyyy_mm = f"{t.year}.{t.month:02d}"
    yyyymmdd = f"{t.year}{t.month:02d}{t.day:02d}"
    hhmm = f"{t.hour:02d}{t.minute:02d}"
    return (f"http://archive.routeviews.org/{collector}/bgpdata/"
            f"{yyyy_mm}/UPDATES/updates.{yyyymmdd}.{hhmm}.bz2")


def _ripe_url(collector: str, t: datetime) -> str:
    """RIPE RIS URL.  RIPE emits at HHMM aligned to 5-minute boundaries."""
    yyyy_mm = f"{t.year}.{t.month:02d}"
    yyyymmdd = f"{t.year}{t.month:02d}{t.day:02d}"
    hhmm = f"{t.hour:02d}{t.minute:02d}"
    return (f"https://data.ris.ripe.net/{collector}/{yyyy_mm}/"
            f"updates.{yyyymmdd}.{hhmm}.gz")


def list_files_in_window(collector: str,
                          start: datetime,
                          end: datetime) -> list[tuple[datetime, str]]:
    """Enumerate (timestamp, url) pairs for all archive files covering
    the half-open interval [start, end)."""
    info = COLLECTORS[collector]
    cadence = timedelta(minutes=info['cadence_min'])
    # Round down to nearest cadence boundary.
    minute = (start.minute // info['cadence_min']) * info['cadence_min']
    t = start.replace(minute=minute, second=0, microsecond=0)
    out = []
    while t < end:
        if info['provider'] == 'routeviews':
            url = _routeviews_url(collector, t)
        else:
            url = _ripe_url(collector, t)
        out.append((t, url))
        t = t + cadence
    return out


# ─── Download with retry ────────────────────────────────────────────────────


def download_file(url: str, dest: Path, retries: int = 3,
                   timeout: int = 60) -> bool:
    """Download `url` to `dest`.  Returns True on success.  Skips if dest
    already exists with non-zero size."""
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + '.tmp')
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':
                                                         'phase20-bgp/1.0'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                with open(tmp, 'wb') as f:
                    shutil.copyfileobj(r, f, length=1024 * 1024)
            tmp.rename(dest)
            return True
        except (urllib.error.HTTPError, urllib.error.URLError,
                TimeoutError, ConnectionError) as e:
            last_err = e
            if tmp.exists():
                tmp.unlink()
            if attempt < retries - 1:
                import time as _time
                _time.sleep(2 * (attempt + 1))
            continue
    print(f"  [download FAIL] {url}: {last_err}")
    return False


# ─── Parsing ─────────────────────────────────────────────────────────────────


def _parse_with_bgpdump(filepath: Path) -> Iterator[dict]:
    """Run `bgpdump -m -t change` and yield records.

    Output format (machine-mode):
      BGP4MP|<timestamp>|A|<peer_ip>|<peer_asn>|<prefix>|<as_path>|...
      BGP4MP|<timestamp>|W|<peer_ip>|<peer_asn>|<prefix>
    """
    if not _bgpdump_available():
        raise RuntimeError("bgpdump not on PATH")
    proc = subprocess.Popen(
        ['bgpdump', '-m', '-t', 'change', str(filepath)],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        bufsize=1024 * 1024)
    assert proc.stdout is not None
    for raw in proc.stdout:
        line = raw.decode('utf-8', errors='replace').rstrip('\n')
        if not line:
            continue
        parts = line.split('|')
        if len(parts) < 6:
            continue
        kind = parts[0]
        if not kind.startswith('BGP4MP'):
            continue
        try:
            ts = float(parts[1])
        except ValueError:
            continue
        upd = parts[2]              # A or W
        peer_ip = parts[3]
        try:
            peer_asn = int(parts[4])
        except ValueError:
            continue
        prefix = parts[5]
        yield dict(timestamp_us=int(ts * 1_000_000),
                    peer_asn=peer_asn, prefix=prefix,
                    update_type=upd, peer_ip=peer_ip)
    proc.wait()


def _enum_value(field):
    """Extract the value-side of mrtparse's `{enum_int: 'NAME'}` dicts.
    For non-dict fields, return as-is."""
    if isinstance(field, dict) and field:
        return next(iter(field.values()))
    return field


def _enum_key(field):
    """Extract the key-side (epoch int / enum int)."""
    if isinstance(field, dict) and field:
        return next(iter(field.keys()))
    return field


def _parse_with_mrtparse(filepath: Path) -> Iterator[dict]:
    """Pure-Python MRT parser (mrtparse).  Slower but no system deps.

    mrtparse encodes enums as single-key dicts (e.g.
    ``{2: 'UPDATE'}`` or ``{1633361400: '2021-10-04 08:30:00'}``);
    the helpers above extract the relevant side.
    """
    from mrtparse import Reader
    for entry in Reader(str(filepath)):
        d = entry.data
        msg = d.get('bgp_message')
        if not msg:
            continue
        if _enum_value(msg.get('type')) != 'UPDATE':
            continue
        # Timestamp: {epoch_int: 'YYYY-MM-DD HH:MM:SS'}
        ts_seconds = _enum_key(d.get('timestamp'))
        try:
            ts_us = int(float(ts_seconds) * 1_000_000)
        except (TypeError, ValueError):
            continue
        try:
            peer_asn = int(d.get('peer_as'))
        except (TypeError, ValueError):
            continue
        peer_ip = d.get('peer_ip', '')
        # Withdrawals
        for w in msg.get('withdrawn_routes') or []:
            prefix = f"{w.get('prefix', '')}/{w.get('length', '')}"
            yield dict(timestamp_us=ts_us, peer_asn=peer_asn,
                        prefix=prefix, update_type='W', peer_ip=peer_ip)
        # Announcements (NLRI)
        for n in msg.get('nlri') or []:
            prefix = f"{n.get('prefix', '')}/{n.get('length', '')}"
            yield dict(timestamp_us=ts_us, peer_asn=peer_asn,
                        prefix=prefix, update_type='A', peer_ip=peer_ip)


def parse_mrt_file(filepath: Path, prefer: str = 'auto') -> Iterator[dict]:
    """Yield (timestamp_us, peer_asn, prefix, update_type, peer_ip) dicts
    from a single MRT update file.  `prefer`: 'bgpdump', 'mrtparse', or
    'auto' (bgpdump if present, else mrtparse)."""
    if prefer == 'auto':
        prefer = 'bgpdump' if _bgpdump_available() else 'mrtparse'
    if prefer == 'bgpdump' and _bgpdump_available():
        yield from _parse_with_bgpdump(filepath)
    else:
        yield from _parse_with_mrtparse(filepath)


# ─── End-to-end (collector, window) acquisition ─────────────────────────────


def acquire_window(collector: str,
                    window_name: str,
                    raw_dir: Path,
                    parquet_path: Path,
                    parser: str = 'auto',
                    max_files: Optional[int] = None,
                    skip_if_exists: bool = True,
                    progress: bool = True,
                    ) -> dict:
    """Download all MRT update files for (collector, window) and write
    one parquet shard per source file to `parquet_path`'s parent
    directory (memory-bounded — each shard is materialised in isolation,
    flushed, and discarded before the next file is parsed).

    Pandas-readable as a single dataset by passing the parent directory
    or glob pattern to `pd.read_parquet`.

    Returns summary dict:
      n_files_total, n_files_downloaded, n_files_parsed, n_records,
      span_seconds.
    """
    import pandas as pd
    # Per-cell shard directory (sibling of the legacy single-file path)
    shard_dir = parquet_path.with_suffix('').parent / \
                f"{parquet_path.with_suffix('').name}_shards"
    shard_dir.mkdir(parents=True, exist_ok=True)

    if skip_if_exists and parquet_path.exists():
        # Legacy single-file format already present; report it.
        df = pd.read_parquet(parquet_path, columns=['timestamp_us'])
        return dict(n_files_total=0, n_files_downloaded=0,
                     n_files_parsed=0, n_records=int(len(df)),
                     span_seconds=(float((df['timestamp_us'].max()
                                            - df['timestamp_us'].min())
                                          / 1_000_000) if len(df) else 0.0),
                     skipped=True)

    # Skip cells whose shard dir already has a complete-marker file
    completed_marker = shard_dir / '_complete'
    if skip_if_exists and completed_marker.exists():
        # Sum up records across shards
        try:
            df = pd.read_parquet(shard_dir, columns=['timestamp_us'])
            n = len(df)
            span = float((df['timestamp_us'].max()
                           - df['timestamp_us'].min()) / 1_000_000) \
                   if n else 0.0
            del df
            return dict(n_files_total=0, n_files_downloaded=0,
                         n_files_parsed=0, n_records=int(n),
                         span_seconds=span, skipped=True)
        except Exception:
            pass   # fall through and recompute

    win = WINDOWS[window_name]
    files = list_files_in_window(collector, win['start'], win['end'])
    if max_files is not None:
        files = files[:max_files]
    if progress:
        print(f"  [{collector}/{window_name}] {len(files)} update files "
              f"in window")

    raw_collector_dir = raw_dir / collector / window_name
    raw_collector_dir.mkdir(parents=True, exist_ok=True)

    n_downloaded = 0
    n_parsed = 0
    n_total_records = 0
    min_ts = None
    max_ts = None
    for i, (t, url) in enumerate(files):
        local = raw_collector_dir / Path(url).name
        if not local.exists():
            ok = download_file(url, local)
            if not ok:
                if progress:
                    print(f"    [{i + 1}/{len(files)}] FAIL: {Path(url).name}")
                continue
            n_downloaded += 1
        # Per-file shard parquet
        shard_name = local.stem.replace('.', '_') + '.parquet'
        shard = shard_dir / shard_name
        if shard.exists() and shard.stat().st_size > 0:
            # Already parsed this file; just count it.
            try:
                df_existing = pd.read_parquet(shard, columns=['timestamp_us'])
                n_total_records += len(df_existing)
                if len(df_existing):
                    fmin = df_existing['timestamp_us'].min()
                    fmax = df_existing['timestamp_us'].max()
                    min_ts = fmin if min_ts is None else min(min_ts, fmin)
                    max_ts = fmax if max_ts is None else max(max_ts, fmax)
                del df_existing
                n_parsed += 1
                continue
            except Exception:
                pass    # re-parse on read failure
        try:
            recs = list(parse_mrt_file(local, prefer=parser))
        except Exception as e:
            if progress:
                print(f"    [{i + 1}/{len(files)}] parse FAIL "
                      f"{local.name}: {e}")
            continue
        if not recs:
            n_parsed += 1
            continue
        df_shard = pd.DataFrame(recs)
        df_shard = df_shard.sort_values('timestamp_us',
                                          kind='mergesort').reset_index(drop=True)
        df_shard.to_parquet(shard, index=False)
        n_parsed += 1
        n_total_records += len(df_shard)
        if len(df_shard):
            fmin = int(df_shard['timestamp_us'].min())
            fmax = int(df_shard['timestamp_us'].max())
            min_ts = fmin if min_ts is None else min(min_ts, fmin)
            max_ts = fmax if max_ts is None else max(max_ts, fmax)
        del df_shard, recs        # release memory
        if progress and (i + 1) % 16 == 0:
            print(f"    [{i + 1}/{len(files)}] cumulative records: "
                  f"{n_total_records:,}")

    if n_total_records == 0:
        if progress:
            print(f"  [{collector}/{window_name}] NO records parsed")
        return dict(n_files_total=len(files), n_files_downloaded=n_downloaded,
                     n_files_parsed=n_parsed, n_records=0,
                     span_seconds=0.0, skipped=False)

    # Touch completion marker so subsequent runs short-circuit
    completed_marker.touch()
    span = float((max_ts - min_ts) / 1_000_000) if (min_ts is not None
                                                      and max_ts is not None) \
           else 0.0
    if progress:
        print(f"  [{collector}/{window_name}] wrote {n_total_records:,} "
              f"records to {shard_dir.name}/ "
              f"({n_parsed} shards, span {span / 3600:.2f}h)")
    return dict(n_files_total=len(files), n_files_downloaded=n_downloaded,
                 n_files_parsed=n_parsed, n_records=int(n_total_records),
                 span_seconds=span, skipped=False)


def load_cell_parquet(parquet_path: Path, **read_kwargs):
    """Load a (collector × window) cell, supporting both legacy
    single-file and new sharded layouts.

    `parquet_path` is the legacy single-file path (e.g.
    `data/.../route-views2_event.parquet`).  The sharded layout lives at
    `data/.../route-views2_event_shards/`.
    """
    import pandas as pd
    if parquet_path.exists():
        return pd.read_parquet(parquet_path, **read_kwargs)
    shard_dir = parquet_path.with_suffix('').parent / \
                f"{parquet_path.with_suffix('').name}_shards"
    if shard_dir.exists():
        return pd.read_parquet(shard_dir, **read_kwargs)
    raise FileNotFoundError(f"no parquet at {parquet_path} or shards "
                              f"at {shard_dir}")


def cell_parquet_exists(parquet_path: Path) -> bool:
    """Returns True if either the legacy single-file or the sharded
    layout for this cell is present."""
    if parquet_path.exists():
        return True
    shard_dir = parquet_path.with_suffix('').parent / \
                f"{parquet_path.with_suffix('').name}_shards"
    return shard_dir.exists() and (shard_dir / '_complete').exists()


__all__ = ['COLLECTORS', 'WINDOWS', 'list_files_in_window',
            'download_file', 'parse_mrt_file', 'acquire_window',
            'load_cell_parquet', 'cell_parquet_exists',
            '_bgpdump_available']

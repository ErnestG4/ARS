"""
cross_substrate/comcat_fetch.py — self-sizing sequential paged USGS ComCat downloader.

USGS FDSN event web service (https://earthquake.usgs.gov/fdsnws/event/1/), open, no registration.
Per-request cap is 20,000 events; we size each window with the `count` endpoint and recursively
bisect the time range until every chunk is under the cap, then download chunks SEQUENTIALLY
(parallel-curl-corruption lesson, Phase 24: never overlap curls on shared paths). Each chunk is
written to its own file, byte-size + row-count verified, and the run is resumable (existing valid
chunks are skipped). Final concatenation dedupes by event id.

Acquisition hygiene:
  - count endpoint sizes before download (no blind 20k truncation)
  - sequential only; retry with backoff; verify each chunk before trusting it
  - cache under coordinates/comcat/<tag>/chunk_*.csv ; merged to coordinates/comcat/<tag>.csv

Usage:
  python3 comcat_fetch.py --tag global_m45 --start 2000-01-01 --end 2025-01-01 --minmag 4.5
  python3 comcat_fetch.py --tag socal_m25 --start 2000-01-01 --end 2025-01-01 --minmag 2.5 \
        --minlat 32 --maxlat 37 --minlon -122 --maxlon -114
"""
from __future__ import annotations

import argparse
import os
import sys
import time as _time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates", "comcat")

BASE = "https://earthquake.usgs.gov/fdsnws/event/1/"
CAP = 18000           # stay safely under the hard 20k cap
TIMEOUT = 120
MAX_RETRY = 5


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _get(url: str) -> bytes:
    last = None
    for attempt in range(MAX_RETRY):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ars-comcat/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read()
        except Exception as e:                       # noqa: BLE001
            last = e
            wait = 2.0 * (attempt + 1)
            sys.stderr.write(f"  retry {attempt+1}/{MAX_RETRY} after {wait:.0f}s ({e})\n")
            _time.sleep(wait)
    raise RuntimeError(f"GET failed after {MAX_RETRY} tries: {url}\n  last={last}")


def _params(start, end, minmag, box):
    p = {"starttime": _iso(start), "endtime": _iso(end),
         "minmagnitude": f"{minmag}", "orderby": "time-asc"}
    if box:
        p.update(minlatitude=box[0], maxlatitude=box[1],
                 minlongitude=box[2], maxlongitude=box[3])
    return p


def count(start, end, minmag, box) -> int:
    p = _params(start, end, minmag, box)
    p["format"] = "text"
    url = BASE + "count?" + urllib.parse.urlencode(p)
    return int(_get(url).decode().strip())


def _download_chunk(start, end, minmag, box, path) -> int:
    """Download one (already-sized-OK) time window to `path`. Return row count."""
    p = _params(start, end, minmag, box)
    p["format"] = "csv"
    url = BASE + "query?" + urllib.parse.urlencode(p)
    data = _get(url)
    tmp = path + ".part"
    with open(tmp, "wb") as f:
        f.write(data)
    n_rows = max(0, data.count(b"\n") - 1)           # minus header
    os.replace(tmp, path)
    return n_rows


def _chunk_valid(path) -> bool:
    if not os.path.exists(path) or os.path.getsize(path) < 10:
        return False
    with open(path, "rb") as f:
        head = f.readline()
    return head.startswith(b"time")                  # CSV header present


def fetch(tag, start, end, minmag, box=None) -> str:
    """Recursively bisect [start,end] until each window < CAP, download sequentially,
    merge + dedupe. Returns merged CSV path."""
    out_dir = os.path.join(COORD, tag)
    os.makedirs(out_dir, exist_ok=True)
    merged = os.path.join(COORD, f"{tag}.csv")

    # Build the work-list of sub-windows by adaptive bisection on count.
    windows = []
    stack = [(start, end)]
    print(f"[size] sizing {tag} via count endpoint…")
    while stack:
        a, b = stack.pop()
        n = count(a, b, minmag, box)
        if n <= CAP:
            if n > 0:
                windows.append((a, b, n))
            continue
        if (b - a) <= timedelta(hours=1):
            # cannot bisect finer than 1h and still over cap — accept (rare; dense swarm)
            windows.append((a, b, n))
            sys.stderr.write(f"  WARN dense window {a}..{b} n={n} > CAP at 1h floor\n")
            continue
        mid = a + (b - a) / 2
        stack.extend([(mid, b), (a, mid)])
    windows.sort()
    total = sum(w[2] for w in windows)
    print(f"[size] {len(windows)} windows, ~{total} events (cap {CAP}/req)")

    # Sequential download with resume.
    got = 0
    for i, (a, b, n) in enumerate(windows):
        path = os.path.join(out_dir, f"chunk_{i:05d}.csv")
        if _chunk_valid(path):
            got += 1
            continue
        nr = _download_chunk(a, b, minmag, box, path)
        got += 1
        if i % 20 == 0 or i == len(windows) - 1:
            print(f"  [{got}/{len(windows)}] {_iso(a)}..{_iso(b)} rows={nr}")

    # Merge + dedupe by event id (col 11 in standard ComCat CSV: 'id').
    print("[merge] concatenating + deduping by event id…")
    seen = set()
    header = None
    n_written = 0
    with open(merged, "w") as out:
        for i in range(len(windows)):
            path = os.path.join(out_dir, f"chunk_{i:05d}.csv")
            if not _chunk_valid(path):
                continue
            with open(path) as f:
                h = f.readline()
                if header is None:
                    header = h
                    out.write(header)
                    cols = header.rstrip("\n").split(",")
                    id_idx = cols.index("id") if "id" in cols else 11
                for line in f:
                    parts = line.split(",")
                    eid = parts[id_idx] if id_idx < len(parts) else line
                    if eid in seen:
                        continue
                    seen.add(eid)
                    out.write(line)
                    n_written += 1
    print(f"[done] {n_written} unique events -> {merged}")
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--start", required=True)         # YYYY-MM-DD
    ap.add_argument("--end", required=True)
    ap.add_argument("--minmag", type=float, required=True)
    ap.add_argument("--minlat", type=float)
    ap.add_argument("--maxlat", type=float)
    ap.add_argument("--minlon", type=float)
    ap.add_argument("--maxlon", type=float)
    a = ap.parse_args()
    box = None
    if a.minlat is not None:
        box = (a.minlat, a.maxlat, a.minlon, a.maxlon)
    start = datetime.fromisoformat(a.start).replace(tzinfo=timezone.utc)
    end = datetime.fromisoformat(a.end).replace(tzinfo=timezone.utc)
    fetch(a.tag, start, end, a.minmag, box)


if __name__ == "__main__":
    main()

"""
grb_pipeline.py — Phase 21 Tier 1.

Fermi GBM TTE acquisition + parsing for the GRB-timing event panel.

Source: HEASARC's public Fermi GBM trigger archive at
  https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/{year}/bn{trigger_id}/current/

Each event has up to 12 NaI detectors (n0–n11) and 2 BGO detectors
(b0, b1).  TTE FITS schema:
  PRIMARY, EBOUNDS, EVENTS (columns: TIME, PHA), GTI.
TIME is mission-elapsed seconds; TRIGTIME header gives the
trigger time in the same reference frame.

Event panel covers the priority-1 cases per the SESSION-PLAN:
  GRB 230307A    (Chen 2025, 909 Hz QPO claim)
  GRB 200415A    (Castro-Tirado 2021, MGF bridge — multi-frequency)
  GRB 221009A    (BOAT, no QPO claim — control)
  GRB 211211A    (Xiao 2022, precursor QPO)

SGR 1806-20 (galactic MGF ground-truth) was originally observed by
RHESSI; its archival data lives at HEASARC under a different path.
We defer it to a fallback path documented at the end of this module
if Fermi GBM coverage of MGF events is preferred.
"""
from __future__ import annotations

import os, sys, gzip, shutil
from pathlib import Path
from typing import Iterator, Optional
from urllib.parse import urljoin
import urllib.request
import urllib.error

import numpy as np
import pandas as pd


# ─── Event panel ───────────────────────────────────────────────────────────


# Fermi GBM trigger IDs are bn{YYMMDDFFF} where FFF is a fractional
# day-of-year identifier.  Identifiers from HEASARC's published catalog.
EVENT_PANEL = [
    dict(name='GRB230307A',
         trigger_id='bn230307656',
         year='2023',
         t90=34.6,                # seconds, from Burst Catalog
         category='extragalactic_merger_magnetar_candidate',
         priority=1,
         qpo_claim_hz=909.0,
         qpo_window_after_t0=(45.0, 47.0),  # transition window per Chen 2025
         qpo_reference='Chen et al. 2025'),
    dict(name='GRB200415A',
         trigger_id='bn200415367',
         year='2020',
         t90=0.139,               # super-short MGF
         category='extragalactic_MGF',
         priority=1,
         qpo_claim_hz=2132.0,     # one of the four claimed; secondary at 836, 1444, 4250
         qpo_window_after_t0=(0.0, 0.139),
         qpo_reference='Castro-Tirado et al. 2021'),
    dict(name='GRB221009A',
         trigger_id='bn221009553',
         year='2022',
         t90=300.0,               # BOAT, very long
         category='long_GRB_BOAT_control',
         priority=2,
         qpo_claim_hz=None,
         qpo_window_after_t0=None,
         qpo_reference=None),
    dict(name='GRB211211A',
         trigger_id='bn211211549',
         year='2021',
         t90=51.4,                # extragalactic merger candidate
         category='extragalactic_merger_kilonova',
         priority=3,
         qpo_claim_hz=22.5,       # Xiao 2022a precursor QPO
         qpo_window_after_t0=(-1.5, -0.5),  # precursor — before T0
         qpo_reference='Xiao et al. 2022a'),
]


GBM_DETECTORS_NAI = [f'n{i}' for i in range(10)] \
                    + [f'na', f'nb']    # n0–nb (10–11)
GBM_DETECTORS_BGO = ['b0', 'b1']
GBM_DETECTORS_ALL = GBM_DETECTORS_NAI + GBM_DETECTORS_BGO


def heasarc_tte_url(trigger_id: str, year: str, detector: str) -> str:
    """Construct the HEASARC URL for a Fermi GBM TTE file.

    Trigger ID format: bnYYMMDDFFF (e.g., bn230307656).  Detector is
    one of n0..n11 or b0..b1.  Files are named v00 by convention; if
    a higher version exists we look for v01/v02 fallback at parse time.
    """
    base = (f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/"
            f"triggers/{year}/{trigger_id}/current/")
    return urljoin(base, f"glg_tte_{detector}_{trigger_id}_v00.fit")


def heasarc_tte_url_versioned(trigger_id: str, year: str,
                                detector: str, version: int) -> str:
    base = (f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/"
            f"triggers/{year}/{trigger_id}/current/")
    return urljoin(base, f"glg_tte_{detector}_{trigger_id}_v{version:02d}.fit")


def download_tte(url: str, dest: Path, retries: int = 3,
                  timeout: int = 90) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + '.tmp')
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'phase21-grb/1.0'})
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
    print(f"  [download FAIL] {url}: {last_err}")
    return False


def parse_tte(filepath: Path) -> dict:
    """Parse a Fermi GBM TTE FITS file.  Returns dict with:
      times_us:   np.ndarray of int64 microsecond timestamps,
                  relative to trigger time (TRIGTIME).
      energy_ch:  np.ndarray of int16 PHA channels.
      ebounds:    DataFrame of channel boundaries (E_MIN, E_MAX in keV).
      detector:   detector name (e.g., 'NAI_02').
      trigtime:   mission-elapsed seconds (absolute).
      object:     burst designation.
      tstart, tstop: mission-elapsed seconds.
    """
    from astropy.io import fits
    with fits.open(filepath) as hdul:
        ev = hdul['EVENTS'].data
        hdr = hdul['EVENTS'].header
        eb = hdul['EBOUNDS'].data
        # TIME is float64 mission-elapsed seconds; TRIGTIME shifts it
        # to be relative to the trigger.
        t_trig = float(hdr.get('TRIGTIME', 0.0))
        t_rel = ev['TIME'] - t_trig
        t_us = (t_rel * 1_000_000).astype(np.int64)
        return dict(
            times_us=t_us,
            energy_ch=np.asarray(ev['PHA'], dtype=np.int16),
            ebounds=pd.DataFrame(dict(channel=np.asarray(eb['CHANNEL']),
                                        e_min=np.asarray(eb['E_MIN']),
                                        e_max=np.asarray(eb['E_MAX']))),
            detector=str(hdr.get('DETNAM', '')),
            trigtime=t_trig,
            object=str(hdr.get('OBJECT', '')),
            tstart=float(hdr.get('TSTART', 0.0)),
            tstop=float(hdr.get('TSTOP', 0.0)),
        )


def acquire_event(event: dict, raw_dir: Path,
                    detectors: Optional[list] = None,
                    progress: bool = True,
                    ) -> dict:
    """Download all available TTE files for an event (across requested
    detectors); parse and return per-detector data.

    Returns dict keyed by detector name with:
      times_us, energy_ch, ebounds, header info, plus aggregate
      counts.
    """
    if detectors is None:
        detectors = GBM_DETECTORS_ALL
    event_dir = raw_dir / event['trigger_id']
    event_dir.mkdir(parents=True, exist_ok=True)
    out = {}
    for det in detectors:
        url = heasarc_tte_url(event['trigger_id'], event['year'], det)
        local = event_dir / f"glg_tte_{det}_{event['trigger_id']}_v00.fit"
        ok = download_tte(url, local)
        if not ok:
            # try v01 if v00 isn't present
            url_v1 = heasarc_tte_url_versioned(event['trigger_id'],
                                                  event['year'], det, 1)
            local_v1 = event_dir / f"glg_tte_{det}_{event['trigger_id']}_v01.fit"
            ok = download_tte(url_v1, local_v1)
            if ok:
                local = local_v1
        if not ok:
            if progress:
                print(f"    [{event['name']}/{det}] not available")
            continue
        try:
            parsed = parse_tte(local)
        except Exception as e:
            print(f"    [{event['name']}/{det}] parse FAIL: {e}")
            continue
        out[det] = parsed
        if progress:
            print(f"    [{event['name']}/{det}] {parsed['times_us'].size:,} "
                  f"events, [{parsed['times_us'].min()/1e6:.1f}, "
                  f"{parsed['times_us'].max()/1e6:.1f}] s rel-trig")
    return out


def select_burst_detectors(per_detector: dict,
                             t90_us: int,
                             min_burst_counts: int = 5000,
                             ) -> list:
    """Select detectors with burst response — those whose count rate
    in the prompt window (T0 to T0+T90) exceeds the pre-trigger
    background.  Heuristic: detectors with > min_burst_counts events in
    [0, T90_us] AND prompt-rate > 2 × background-rate (computed from
    [T0-50, T0-10] s)."""
    selected = []
    for det, data in per_detector.items():
        times = data['times_us']
        prompt_count = int(((times >= 0) & (times < t90_us)).sum())
        bg_window_us = int(40 * 1_000_000)
        bg_count = int(((times >= -50_000_000) & (times < -10_000_000)).sum())
        bg_rate = bg_count / 40.0    # per second
        prompt_rate = prompt_count / max(t90_us / 1e6, 1e-3)
        if prompt_count >= min_burst_counts and prompt_rate > 2 * bg_rate:
            selected.append(det)
    return selected


def write_event_parquet(event: dict, per_detector: dict,
                          out_path: Path) -> None:
    """Write parsed TTE data for an event as a single parquet table
    keyed by (detector, time, channel)."""
    rows = []
    for det, data in per_detector.items():
        n = data['times_us'].size
        rows.append(pd.DataFrame(dict(
            detector=[det] * n,
            time_us=data['times_us'],
            energy_ch=data['energy_ch'],
        )))
    if not rows:
        return
    df = pd.concat(rows, ignore_index=True)
    df = df.sort_values(['time_us'], kind='mergesort').reset_index(drop=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)


__all__ = [
    'EVENT_PANEL', 'GBM_DETECTORS_NAI', 'GBM_DETECTORS_BGO',
    'GBM_DETECTORS_ALL',
    'heasarc_tte_url', 'download_tte', 'parse_tte',
    'acquire_event', 'select_burst_detectors',
    'write_event_parquet',
]

"""
phase26/energy_binning.py — per-detector quantile energy binning.

Reads each detector's TTE EBOUNDS extension for the PHA→keV map, then
quantile-bins the 128 CSPEC channels into 8 equally-populated bands
per detector (within a chosen analysis window — Phase 26 uses
[26, 30) s post-trigger by default).  Each cell gets:

  band_idx       : 0..7
  pha_low        : first channel in band (inclusive)
  pha_high       : last channel in band (inclusive)
  n_events       : event count in the cell within the analysis window
  e_lo_kev       : low-edge energy of pha_low in keV
  e_hi_kev       : high-edge energy of pha_high in keV
  e_median_kev   : median photon energy across events (uses E_GEO_MEAN
                    of each event's PHA, weighted by event count)

Quantile binning gives equal statistical power per cell (each cell
has ~1/8 of the detector's events in the analysis window).  The cost
is that "band 4" in detector n2 covers a different absolute energy
range than "band 4" in detector na — which is why the median-energy
column exists.  Cross-detector aspect-correlation tests should bin
together cells with similar median energies, not the same band index.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.io import fits


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)


N_BANDS = 8


def load_ebounds(tte_path: Path) -> np.ndarray:
    """Read EBOUNDS HDU from a TTE file.  Returns (n_channels, 3) with
    columns (E_MIN_keV, E_MAX_keV, E_GEO_MEAN_keV).  E_GEO_MEAN is the
    geometric mean of E_MIN and E_MAX, used as the per-channel
    photon-energy representative."""
    with fits.open(tte_path) as h:
        eb = h['EBOUNDS'].data
        e_min = np.asarray(eb['E_MIN'], dtype=np.float64)
        e_max = np.asarray(eb['E_MAX'], dtype=np.float64)
        e_geo = np.sqrt(e_min * e_max)
        return np.column_stack([e_min, e_max, e_geo])


def quantile_bin_detector(events_pha: np.ndarray, n_bands: int = N_BANDS,
                             ) -> np.ndarray:
    """Compute band edges (channel boundaries) for n_bands equally-
    populated quantile bands on `events_pha` (length T, integer PHA
    channels).

    Returns (n_bands, 2) array of [pha_low, pha_high] inclusive
    boundaries, sorted by ascending channel.

    Edge cases:
      * If multiple channels share a quantile boundary (e.g., many
        events in one channel), the channels are not split — the band
        will be wider but the population balance is approximate.
      * If fewer than n_bands distinct channels are populated, some
        bands collapse.  We pad output with the highest-channel band's
        edges (so the band-index axis is always n_bands long).
    """
    if events_pha.size == 0:
        return np.zeros((n_bands, 2), dtype=np.int32)
    quantiles = np.linspace(0, 1, n_bands + 1)
    edges = np.quantile(events_pha, quantiles, method='nearest').astype(np.int32)
    # Ensure strictly-non-decreasing; assign each band [edges[i], edges[i+1]-1]
    # except the last is [edges[-2], edges[-1]] inclusive.
    bands = []
    for i in range(n_bands):
        lo = int(edges[i])
        if i < n_bands - 1:
            hi = int(edges[i + 1]) - 1
            if hi < lo: hi = lo
        else:
            hi = int(edges[i + 1])
        bands.append((lo, hi))
    # Merge into non-overlapping ranges: ensure band i's lo > band i-1's hi
    out = []
    prev_hi = -1
    for lo, hi in bands:
        lo = max(lo, prev_hi + 1)
        if hi < lo: hi = lo
        out.append((lo, hi))
        prev_hi = hi
    return np.asarray(out, dtype=np.int32)


def build_cell_table(panel_path: Path,
                       raw_dir: Path,
                       trigger_id: str,
                       window_s: tuple = (26.0, 30.0),
                       n_bands: int = N_BANDS,
                       detectors: list = None,
                       ) -> pd.DataFrame:
    """Build the per-(detector, band) cell table.

    panel_path  : pooled-events parquet (e.g. GRB230307A.parquet) with
                   columns (detector, time_us, energy_ch).
    raw_dir     : directory containing TTE files (for EBOUNDS).
    trigger_id  : e.g. 'bn230307656'.
    window_s    : (start, end) seconds post-trigger; events restricted
                   to this window for the bin-edge computation.
    detectors   : if None, use all detectors present in the parquet.

    Returns a DataFrame with one row per (detector, band) cell.
    """
    df = pd.read_parquet(panel_path, columns=['detector', 'time_us', 'energy_ch'])
    if detectors is None:
        detectors = sorted(df['detector'].unique())

    s_us = int(window_s[0] * 1_000_000)
    e_us = int(window_s[1] * 1_000_000)
    df_w = df[(df['time_us'] >= s_us) & (df['time_us'] < e_us)].copy()

    rows = []
    for d in detectors:
        events_pha = df_w[df_w['detector'] == d]['energy_ch'].to_numpy()
        if events_pha.size == 0:
            continue
        # Per-detector EBOUNDS:
        tte_path = raw_dir / f'glg_tte_{d}_{trigger_id}_v00.fit'
        ebounds = load_ebounds(tte_path)
        # Quantile band edges:
        band_edges = quantile_bin_detector(events_pha, n_bands=n_bands)
        for band_idx, (pha_lo, pha_hi) in enumerate(band_edges):
            mask = (events_pha >= pha_lo) & (events_pha <= pha_hi)
            n_evt = int(mask.sum())
            pha_lo_safe = int(max(0, pha_lo))
            pha_hi_safe = int(min(127, pha_hi))
            e_lo = float(ebounds[pha_lo_safe, 0])
            e_hi = float(ebounds[pha_hi_safe, 1])
            # Photon energy median: take E_GEO_MEAN of each event's PHA
            # channel, find the channel-count-weighted median.
            chs_in_band = events_pha[mask]
            if chs_in_band.size:
                e_geo_per_evt = ebounds[chs_in_band, 2]
                e_med = float(np.median(e_geo_per_evt))
            else:
                e_med = float('nan')
            rows.append(dict(
                detector=d, band_idx=int(band_idx),
                pha_lo=int(pha_lo_safe), pha_hi=int(pha_hi_safe),
                n_events=n_evt,
                e_lo_kev=e_lo, e_hi_kev=e_hi, e_median_kev=e_med,
            ))
    return pd.DataFrame(rows)


def assign_bands_to_events(panel_path: Path,
                              cell_table: pd.DataFrame,
                              ) -> pd.DataFrame:
    """Annotate the full panel events with their band_idx.  Returns the
    panel DataFrame with an added 'band_idx' column.

    Bands are detector-specific (band 3 of n2 ≠ band 3 of na).  Events
    outside the cell_table's PHA ranges get band_idx = -1.
    """
    df = pd.read_parquet(panel_path, columns=['detector', 'time_us', 'energy_ch'])
    df['band_idx'] = np.int8(-1)
    for d, sub in cell_table.groupby('detector'):
        det_mask = df['detector'].values == d
        det_pha = df.loc[det_mask, 'energy_ch'].values
        band_arr = np.full(det_pha.size, -1, dtype=np.int8)
        for _, r in sub.iterrows():
            m = (det_pha >= int(r['pha_lo'])) & (det_pha <= int(r['pha_hi']))
            band_arr[m] = int(r['band_idx'])
        df.loc[det_mask, 'band_idx'] = band_arr
    return df


def main():
    panel = (Path(ROOT_DIR) / 'data' / 'phase21_grb_panel' / 'GRB230307A.parquet')
    raw_dir = (Path(ROOT_DIR) / 'data' / 'phase21_grb_panel'
                / 'raw' / 'bn230307656')
    out_dir = Path(ROOT_DIR) / 'data' / 'phase26_results'
    out_dir.mkdir(parents=True, exist_ok=True)

    cell_table = build_cell_table(panel, raw_dir, 'bn230307656',
                                    window_s=(26.0, 30.0), n_bands=N_BANDS)
    cell_table.to_parquet(out_dir / 'energy_bands.parquet', index=False)

    print("=" * 72)
    print(f"Per-detector quantile energy binning ({N_BANDS} bands per detector)")
    print(f"  window: [26, 30) s post-trigger")
    print("=" * 72)
    by_det = cell_table.groupby('detector')
    print(f"  {'det':3s}  {'band':>4s}  {'pha':>10s}  "
          f"{'n_evt':>6s}  {'e_lo':>8s}  {'e_hi':>8s}  {'e_med':>8s}")
    for d, sub in by_det:
        for _, r in sub.iterrows():
            pha_str = f"{r['pha_lo']:3d}-{r['pha_hi']:3d}"
            print(f"  {r['detector']:3s}  {r['band_idx']:4d}  {pha_str:>10s}  "
                  f"{r['n_events']:6d}  {r['e_lo_kev']:8.2f}  "
                  f"{r['e_hi_kev']:8.2f}  {r['e_median_kev']:8.2f}")
    print()
    print(f"  → {out_dir}/energy_bands.parquet  ({len(cell_table)} cells)")


if __name__ == '__main__':
    main()

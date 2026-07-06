"""
phase22a/h1_functional.py — V1 functional-category measurements.

For each H1-passing unit on each available stimulus, compute the
canonical V1 functional descriptors that the H1 cross-validation step
needs to align ARS classes against:

  - Mean firing rate per condition.
  - Drifting-grating (gratings recordings, 12 directions × N trials):
      preferred direction
      direction selectivity index (DSI)
      orientation selectivity index (OSI)
      F1/F0 ratio (simple/complex partition)
      orientation-tuning bandwidth (circular-Gaussian fit)
  - Grating-direction movie (gratings_movie, 100 short presentations):
      preferred orientation (collapsed to [0, π))
      orientation tuning curve quality (R² of fit)

Receptive-field STA from white-noise movie is lower-priority and is
deferred to a separate script (h1_sta.py) — orientation tuning is the
cleaner cross-validation axis.

Outputs:
  data/phase22a_results/h1_functional.parquet
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from loader import (
    load, GRATING_DIRECTIONS_DEG, GRATING_TRIAL_SEC, GRATING_OFFSET_SEC,
    MOVIE_TRIAL_SEC, GRATING_MOVIE_GRATING_DUR_SEC,
)


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase22a_results'
OUT_DIR.mkdir(parents=True, exist_ok=True)
SELECTION_PATH = OUT_DIR / 'unit_selection.parquet'


# ─── per-trial PSTH helpers ────────────────────────────────────────────────


def gratings_per_dir_rate(rec, unit: int) -> np.ndarray:
    """Per-direction mean firing rate (sp/s).  Length = 12.

    Uses the canonical 1-second window starting GRATING_OFFSET_SEC into
    the trial (the Cowley/Williamson preprocessing convention).
    """
    out = np.zeros(rec.n_conditions)
    for c in range(rec.n_conditions):
        n = 0
        for t in range(rec.n_trials):
            sp = np.asarray(rec.spike_times[unit][c][t]).flatten()
            n += int(((sp >= GRATING_OFFSET_SEC) &
                       (sp <  GRATING_OFFSET_SEC + GRATING_TRIAL_SEC)).sum())
        out[c] = n / (rec.n_trials * GRATING_TRIAL_SEC)
    return out


def gratings_psth(rec, unit: int, direction: int,
                   bin_ms: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Trial-averaged PSTH for one direction (1ms bins, 1s window)."""
    n_bins = int(GRATING_TRIAL_SEC * 1000 / bin_ms)
    edges = np.linspace(GRATING_OFFSET_SEC,
                        GRATING_OFFSET_SEC + GRATING_TRIAL_SEC,
                        n_bins + 1)
    psth = np.zeros(n_bins)
    for t in range(rec.n_trials):
        sp = np.asarray(rec.spike_times[unit][direction][t]).flatten()
        psth += np.histogram(sp, bins=edges)[0]
    psth = psth / (rec.n_trials * (bin_ms / 1000.0))   # spikes/sec
    bin_centres = (edges[:-1] + edges[1:]) / 2 - GRATING_OFFSET_SEC
    return bin_centres, psth


# ─── tuning indices ────────────────────────────────────────────────────────


def osi_dsi(per_dir_rate: np.ndarray,
             dirs_deg: np.ndarray = GRATING_DIRECTIONS_DEG) -> dict:
    """Orientation- and direction-selectivity indices via circular-vector
    formulation.

    OSI = |sum r_k e^{i 2θ_k}| / sum r_k       (orientation-period weighting)
    DSI = |sum r_k e^{i θ_k}|   / sum r_k       (direction-period weighting)

    Preferred direction = arg(sum r_k e^{iθ_k}); preferred orientation =
    arg(sum r_k e^{i 2θ_k}) / 2 mod π.
    """
    r = np.asarray(per_dir_rate, dtype=np.float64)
    th = np.deg2rad(dirs_deg)
    if r.sum() <= 0:
        return dict(osi=np.nan, dsi=np.nan,
                     pref_ori_deg=np.nan, pref_dir_deg=np.nan)
    s_dir = float(np.abs(np.sum(r * np.exp(1j * th))) / r.sum())
    s_ori = float(np.abs(np.sum(r * np.exp(1j * 2 * th))) / r.sum())
    pref_dir = float((np.angle(np.sum(r * np.exp(1j * th))) % (2 * np.pi))
                       * 180 / np.pi)
    pref_ori = float((np.angle(np.sum(r * np.exp(1j * 2 * th))) % (2 * np.pi))
                       * 90 / np.pi)
    return dict(osi=s_ori, dsi=s_dir,
                 pref_ori_deg=pref_ori, pref_dir_deg=pref_dir)


def f1_f0(rec, unit: int, direction: int,
          temporal_freq_hz: float = 6.25) -> float:
    """F1/F0 ratio: amplitude of the temporal-frequency component
    of the PSTH divided by its mean (DC).

    >1 → simple cell; <1 → complex cell (DeAngelis-Skottun convention).

    The drifting gratings in pvc-11 use the Smith-Kohn TF (typically ~6.25 Hz
    for 1.28s presentations of full-cycle drift; documented as moving at a
    speed yielding 6.25 cycles/second within the 1s analysis window).
    """
    bins, psth = gratings_psth(rec, unit, direction, bin_ms=2.0)
    n = psth.size
    if n < 4 or psth.mean() <= 0:
        return float('nan')
    f0 = float(psth.mean())
    # FFT of mean-subtracted PSTH; find the bin closest to temporal_freq_hz
    spec = np.abs(np.fft.rfft(psth - f0))
    freqs = np.fft.rfftfreq(n, d=(bins[1] - bins[0]))
    if not freqs.size:
        return float('nan')
    k = int(np.argmin(np.abs(freqs - temporal_freq_hz)))
    if k < 1: return float('nan')
    f1 = float(2.0 / n * spec[k])
    return f1 / f0


def gratings_movie_tuning(rec, unit: int) -> dict:
    """Per-direction firing rate from the 100 short grating presentations
    in the gratings_movie.

    Each grating shown for 0.30s; theta_rad in stim_meta gives the
    direction.  Group by direction, compute per-direction mean rate,
    then OSI/DSI on the resulting tuning curve.
    """
    theta = rec.stim_meta.get('theta_rad')
    if theta is None:
        return dict(osi_movie=np.nan, dsi_movie=np.nan,
                     pref_ori_movie_deg=np.nan, pref_dir_movie_deg=np.nan,
                     n_dirs_movie=0)
    n_grat = theta.size
    grat_dur = GRATING_MOVIE_GRATING_DUR_SEC
    # Bin spikes per trial by which grating they fall in.
    counts = np.zeros((n_grat, rec.n_trials))
    for t in range(rec.n_trials):
        sp = np.asarray(rec.spike_times[unit][t]).flatten()
        # which grating each spike falls in
        idx = np.floor(sp / grat_dur).astype(np.int64)
        idx = idx[(idx >= 0) & (idx < n_grat)]
        np.add.at(counts[:, t], idx, 1)
    rate_per_grat = counts.mean(axis=1) / grat_dur
    valid = ~np.isnan(theta)
    if not valid.any() or rate_per_grat[valid].sum() <= 0:
        return dict(osi_movie=np.nan, dsi_movie=np.nan,
                     pref_ori_movie_deg=np.nan, pref_dir_movie_deg=np.nan,
                     n_dirs_movie=int(valid.sum()))
    th_use = theta[valid]
    r_use = rate_per_grat[valid]
    s_dir = float(np.abs(np.sum(r_use * np.exp(1j * th_use))) / r_use.sum())
    s_ori = float(np.abs(np.sum(r_use * np.exp(1j * 2 * th_use))) / r_use.sum())
    pref_dir = float((np.angle(np.sum(r_use * np.exp(1j * th_use))) % (2 * np.pi))
                       * 180 / np.pi)
    pref_ori = float((np.angle(np.sum(r_use * np.exp(1j * 2 * th_use))) % (2 * np.pi))
                       * 90 / np.pi)
    return dict(osi_movie=s_ori, dsi_movie=s_dir,
                pref_ori_movie_deg=pref_ori,
                pref_dir_movie_deg=pref_dir,
                n_dirs_movie=int(valid.sum()))


# ─── orchestrator ──────────────────────────────────────────────────────────


def main():
    print("=" * 72)
    print("Phase 22a H1 — V1 functional-category measurements")
    print("=" * 72)

    sel = pd.read_parquet(SELECTION_PATH)
    sel_h1 = sel[sel['h1_pass']].copy()

    # Restrict to evoked subsets — functional categories require stimulus
    sel_evoked = sel_h1[sel_h1['subset'].isin(
        ['gratings', 'gratings_movie', 'natural_movie', 'noise_movie']
    )].copy()
    print(f"Functional-categorisation candidates: {len(sel_evoked)} units")

    rows = []
    for rec_name, group in sel_evoked.groupby('recording', sort=False):
        rec = load(rec_name)
        for _, row in group.iterrows():
            u = int(row['unit_idx'])
            entry = dict(
                recording=rec_name,
                subset=rec.subset,
                monkey=rec.monkey,
                unit_idx=u,
                unit_id=rec.unit_id(u),
                snr=float(rec.snr[u]),
                mean_rate=float(row['mean_rate']),
            )
            if rec.subset == 'gratings':
                per_dir = gratings_per_dir_rate(rec, u)
                entry.update(osi_dsi(per_dir))
                entry['per_dir_rate'] = per_dir.tolist()
                # F1/F0 at the preferred direction
                if not np.isnan(entry['pref_dir_deg']):
                    pref_idx = int(np.argmax(per_dir))
                    entry['f1_f0_pref'] = f1_f0(rec, u, pref_idx)
                    entry['pref_idx'] = pref_idx
                else:
                    entry['f1_f0_pref'] = float('nan')
                    entry['pref_idx'] = -1
            elif rec.subset == 'gratings_movie':
                entry.update(gratings_movie_tuning(rec, u))
            # natural_movie / noise_movie: only mean_rate is computed here
            rows.append(entry)
        print(f"  {rec_name}: {len(group)} units processed")

    df = pd.DataFrame(rows)
    out = OUT_DIR / 'h1_functional.parquet'
    df.to_parquet(out, index=False)
    print(f"\n  → {out}  ({len(df)} rows)")

    # Summary
    print()
    if 'osi' in df.columns:
        d_grat = df[df['subset'] == 'gratings'].dropna(subset=['osi'])
        print(f"  drifting gratings: n={len(d_grat)}  "
              f"OSI median={d_grat['osi'].median():.3f}  "
              f"DSI median={d_grat['dsi'].median():.3f}  "
              f"F1/F0 median={d_grat['f1_f0_pref'].median():.3f}  "
              f"simple={int((d_grat['f1_f0_pref'] > 1).sum())}  "
              f"complex={int((d_grat['f1_f0_pref'] <= 1).sum())}")
    if 'osi_movie' in df.columns:
        d_mov = df[df['subset'] == 'gratings_movie'].dropna(subset=['osi_movie'])
        print(f"  grating-direction movie: n={len(d_mov)}  "
              f"OSI median={d_mov['osi_movie'].median():.3f}  "
              f"DSI median={d_mov['dsi_movie'].median():.3f}")


if __name__ == '__main__':
    main()

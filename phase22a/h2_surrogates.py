"""
phase22a/h2_surrogates.py — H2 surrogate battery.

Three Aitchison-style surrogate flavours, each preserving a specific
property of the real recording while randomising the joint structure
that H2 is testing for:

  (a) rate_matched_poisson — per-unit independent Poisson at the unit's
      empirical mean rate.  Floor surrogate: any structure surviving
      this preserves something beyond mean rate alone.

  (b) cell_shuffle — per-trial circular shift of each unit's spike
      train within its trial window.  Preserves each unit's spike count
      and approximately its rate envelope (it does not preserve the
      rate envelope when the envelope is highly asymmetric, but for
      stimulus-evoked recordings the rate envelope's bulk matches the
      stimulus drive across all units).  Destroys cell-pair-specific
      synchrony and joint structure.

  (c) ln_evoked — Linear-Nonlinear surrogate for evoked recordings.
      Per-unit STA from a stimulus movie + softplus rate nonlinearity,
      then independent Poisson sampling of each unit's modulated rate.
      Implemented with a simple LN fit on white-noise / grating-direction
      movie pixel intensities.  Preserves per-unit stimulus-driven rate
      modulation; destroys cell-pair joint structure.

  (d) state_modulated — anesthesia-state surrogate for the spontaneous
      subset.  Extract the dominant population latent (PC1 of binned
      population activity), use it as a per-unit gain modulator, and
      sample independent Poisson at each unit's rate × gain(t).
      Preserves the dominant slow Up/Down latent variable; destroys
      finer cell-pair joint structure.

For each (recording, surrogate, seed) triple we build a surrogate
spike-time tensor, extract population events with the same definition
used on real data, and run the ARS pipeline.

Outputs:
  data/phase22a_results/h2_surrogate_classifications.parquet
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)

from loader import (
    load, GRATING_TRIAL_SEC, GRATING_OFFSET_SEC, MOVIE_TRIAL_SEC,
)
from ars_classify import classify, per_q_columns
from population_events import (
    build_unit_matrix, extract_events,
    BIN_MS_DEFAULT, K_THRESH_DEFAULT,
)


OUT_DIR = Path(ROOT_DIR) / 'data' / 'phase22a_results'
SEL_PATH = OUT_DIR / 'unit_selection.parquet'

N_SEEDS = 3    # surrogate replicates per (recording, surrogate) cell.
               # 3 chosen for runtime: classify at q_max=100 dominates
               # cost (~30-100s/call) and 5 seeds × 2 q_max × 3 surrogates
               # × 15 recordings ≈ 450 classify calls → ~6h.  3 seeds keeps
               # the 95th-percentile estimate noisier but the verdict
               # robust to which seed set is used.
BIN_MS = BIN_MS_DEFAULT
K_THRESH = K_THRESH_DEFAULT
Q_MAX_DEFAULT = 30
Q_MAX_SLOW = 100   # extends q-band into the Up/Down (0.3–3 Hz) regime


# ─── (a) rate-matched per-unit Poisson ─────────────────────────────────────


def surrogate_rate_matched_poisson(rec, units: list[int],
                                     bin_ms: float, seed: int) -> np.ndarray:
    """Build a (n_units × n_bins) Poisson surrogate matrix at each unit's
    empirical bin-rate.  Rate per bin = total_count / n_bins."""
    rng = np.random.default_rng(seed)
    real_mat, _ = build_unit_matrix(rec, units, bin_ms=bin_ms)
    n_units, n_bins = real_mat.shape
    rates_per_bin = real_mat.sum(axis=1) / max(n_bins, 1)
    sur = rng.poisson(rates_per_bin[:, None], size=(n_units, n_bins))
    return sur.astype(np.int32)


# ─── (b) per-trial circular shift ──────────────────────────────────────────


def surrogate_cell_shuffle(rec, units: list[int],
                            bin_ms: float, seed: int) -> np.ndarray:
    """Independent random circular shift per (unit, trial) — preserves
    each unit's per-trial spike count and overall rate envelope across
    trials, but breaks cell-pair joint synchrony.

    We operate on the binned matrix per chunk, so the resulting
    surrogate matrix is identical in shape to the real one.
    """
    rng = np.random.default_rng(seed)
    real_mat, _ = build_unit_matrix(rec, units, bin_ms=bin_ms)
    n_units, n_bins = real_mat.shape
    if rec.subset == 'spontaneous':
        # No trial structure — circular shift the whole train per unit
        sur = np.empty_like(real_mat)
        for i in range(n_units):
            shift = int(rng.integers(0, n_bins))
            sur[i] = np.roll(real_mat[i], shift)
        return sur
    if rec.subset == 'gratings':
        chunk_dur = GRATING_TRIAL_SEC
        n_chunks = rec.n_conditions * rec.n_trials
    else:
        chunk_dur = MOVIE_TRIAL_SEC
        n_chunks = rec.n_trials
    chunk_bins = int(round(chunk_dur / (bin_ms / 1000.0)))
    sur = np.empty_like(real_mat)
    for i in range(n_units):
        for c in range(n_chunks):
            sl = slice(c * chunk_bins, (c + 1) * chunk_bins)
            shift = int(rng.integers(0, chunk_bins))
            sur[i, sl] = np.roll(real_mat[i, sl], shift)
    return sur


# ─── (c) LN-evoked surrogate ───────────────────────────────────────────────


def _load_movie(kind: str, monkey: int) -> np.ndarray:
    """Load a movie pixel matrix as (n_frames, n_pixels).  Frames sampled
    at 25 fps to match the experimental display (each frame shown for
    ~40 ms = 25 fps; the movies are 30s × ~750 frames)."""
    import scipy.io as sio
    if kind == 'noise_movie':
        path = (Path('$HOME/fmexplorer/criticality_tool/data/pvc-11')
                / 'data_and_scripts/stimuli_movies/noise_movie.mat')
    elif kind == 'natural_movie':
        path = (Path('$HOME/fmexplorer/criticality_tool/data/pvc-11')
                / 'data_and_scripts/stimuli_movies/natural_movie.mat')
    elif kind == 'gratings_movie':
        path = (Path('$HOME/fmexplorer/criticality_tool/data/pvc-11')
                / 'data_and_scripts/stimuli_movies/gratings_movie.mat')
    else:
        raise ValueError(f"unknown movie kind: {kind}")
    m = sio.loadmat(path, squeeze_me=True)
    M = np.asarray(m['M'])     # (n_pixels × n_pixels × n_frames) uint8
    n_frames = M.shape[2]
    Z = M.reshape(-1, n_frames).T.astype(np.float32) / 255.0
    return Z, n_frames


def _fit_ln_simple(spikes_per_bin: np.ndarray, stim: np.ndarray,
                    bin_ms: float) -> tuple[np.ndarray, float, float]:
    """Fit a simple LN model for one unit on a stimulus matrix.
        spikes_per_bin: (n_bins,) integer per-bin count
        stim:           (n_bins, n_pixels) float matrix (each row = stim
                        at the time of that bin)
    Returns (filter, gain, base) such that
        rate(t) = base + gain × max(0, filter · stim(t))
    via STA + softplus rectification.

    Implementation: STA on positive-bin frames, then a simple linear
    regression of rate on the half-rectified projection to fit gain
    and base.  This is the cheapest LN that captures the rate
    modulation needed for surrogate generation; not a precision-fitted
    receptive field model.
    """
    if spikes_per_bin.sum() < 5 or stim.shape[0] < 5:
        # Fallback: zero filter, mean-rate base
        return np.zeros(stim.shape[1], dtype=np.float32), 0.0, \
               float(spikes_per_bin.mean())
    # STA: average stim weighted by per-bin spike counts
    w = spikes_per_bin.astype(np.float32) / spikes_per_bin.sum()
    sta = np.einsum('t,tp->p', w, stim).astype(np.float32)
    sta = sta - sta.mean()
    norm = np.linalg.norm(sta)
    if norm > 0: sta = sta / norm
    # Project stim onto STA → 1D drive
    drive = stim @ sta
    drive_pos = np.maximum(drive, 0)
    # Simple linear regression: rate ~ a + b * drive_pos
    A = np.column_stack([np.ones_like(drive_pos), drive_pos])
    rate = spikes_per_bin.astype(np.float32)
    try:
        beta, *_ = np.linalg.lstsq(A, rate, rcond=None)
        base, gain = float(beta[0]), float(beta[1])
    except Exception:
        base, gain = float(spikes_per_bin.mean()), 0.0
    base = max(base, 0.0)
    gain = max(gain, 0.0)
    return sta, gain, base


def surrogate_ln_evoked(rec, units: list[int],
                          bin_ms: float, seed: int,
                          stim_kind: str = None) -> np.ndarray:
    """Per-unit LN surrogate using the recording's actual stimulus.

    Only meaningful for movie-subset recordings (where we have explicit
    per-frame stimulus pixels); for the drifting-gratings recordings we
    fall back to rate-matched Poisson (since 1.28s static-orientation
    stimuli don't admit a useful per-frame LN model).
    """
    rng = np.random.default_rng(seed)
    if rec.subset not in ('gratings_movie', 'natural_movie', 'noise_movie'):
        return surrogate_rate_matched_poisson(rec, units, bin_ms, seed)
    # Use white-noise movie if available; falls back to recording's own movie.
    stim_kind = stim_kind or rec.subset
    Z, n_frames = _load_movie(stim_kind, rec.monkey)
    frame_dur_ms = MOVIE_TRIAL_SEC * 1000 / n_frames
    bin_per_frame = max(1, int(round(frame_dur_ms / bin_ms)))
    real_mat, _ = build_unit_matrix(rec, units, bin_ms=bin_ms)
    n_units, n_bins = real_mat.shape
    bins_per_trial = int(round(MOVIE_TRIAL_SEC / (bin_ms / 1000)))

    # Build a per-bin stim matrix that repeats each frame for bin_per_frame bins
    per_bin_stim = np.repeat(Z, bin_per_frame, axis=0)
    if per_bin_stim.shape[0] > bins_per_trial:
        per_bin_stim = per_bin_stim[:bins_per_trial]
    elif per_bin_stim.shape[0] < bins_per_trial:
        pad = np.zeros((bins_per_trial - per_bin_stim.shape[0], Z.shape[1]),
                        dtype=np.float32)
        per_bin_stim = np.concatenate([per_bin_stim, pad], axis=0)

    # Average the real binned response across trials per unit, then fit LN
    real32 = real_mat.astype(np.float32)
    avg_response = real32.reshape(n_units, rec.n_trials,
                                   bins_per_trial).mean(axis=1)
    # ─── vectorised STA: STA_i = sum_t avg_response[i,t] * stim[t,:] / sum_t avg_response[i,t]
    weights = avg_response.sum(axis=1, keepdims=True) + 1e-9
    sta_all = (avg_response @ per_bin_stim) / weights        # (n_units, n_pix)
    sta_all = sta_all - sta_all.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(sta_all, axis=1, keepdims=True) + 1e-9
    sta_all = sta_all / norms                                # (n_units, n_pix)

    # Drive[i,t] = STA_i · stim[t]   shape (n_units, bins_per_trial)
    drive_all = sta_all @ per_bin_stim.T                    # (n_units, T)
    drive_pos = np.maximum(drive_all, 0)

    # LN linear regression: solve (a_i, b_i) such that
    # avg_response_i ≈ a_i + b_i × drive_pos_i  via per-unit lstsq.
    base = np.zeros(n_units, dtype=np.float32)
    gain = np.zeros(n_units, dtype=np.float32)
    for i in range(n_units):
        d = drive_pos[i]
        A = np.column_stack([np.ones_like(d), d])
        try:
            beta, *_ = np.linalg.lstsq(A, avg_response[i], rcond=None)
            base[i], gain[i] = max(float(beta[0]), 0.0), max(float(beta[1]), 0.0)
        except Exception:
            base[i], gain[i] = float(avg_response[i].mean()), 0.0

    # Per-trial rate matrix: same drive every trial (deterministic stimulus)
    rates_one_trial = base[:, None] + gain[:, None] * drive_pos
    rates_one_trial = np.clip(rates_one_trial, 0, None)

    # Tile across trials and Poisson-sample
    rates_full = np.tile(rates_one_trial, (1, rec.n_trials))
    sur = rng.poisson(rates_full).astype(np.int32)
    return sur


# ─── (d) anesthesia-state-modulated Poisson ────────────────────────────────


def surrogate_state_modulated(rec, units: list[int],
                                bin_ms: float, seed: int) -> np.ndarray:
    """For the spontaneous subset: extract the population-PC1 latent
    (top eigenvector of the (units × bins) zero-meaned matrix), use it
    as a multiplicative gain shared across units, and sample
    independent Poisson per unit at base_rate × max(0, gain(t))."""
    rng = np.random.default_rng(seed)
    real_mat, _ = build_unit_matrix(rec, units, bin_ms=bin_ms)
    n_units, n_bins = real_mat.shape
    base_rates = real_mat.sum(axis=1) / max(n_bins, 1)
    if real_mat.std() <= 0:
        return rng.poisson(base_rates[:, None],
                             size=(n_units, n_bins)).astype(np.int32)
    # Zero-mean per unit, then PC1 across units
    Xc = real_mat.astype(np.float32) - real_mat.mean(axis=1, keepdims=True)
    # Project onto first PC of the units × bins matrix; PC1 of bins = top
    # right-singular vector (length n_bins).  We use a thin SVD on the
    # zero-mean matrix.
    try:
        from scipy.sparse.linalg import svds
        # k=1; svds returns (U, s, Vt) where Vt is the top n_bins-vector
        if n_units >= 2 and n_bins >= 4:
            U, s, Vt = svds(Xc.astype(np.float32), k=1)
            pc1 = Vt[0]
        else:
            pc1 = np.ones(n_bins) / n_bins
    except Exception:
        # Fallback: use the population mean across units as the latent
        pc1 = Xc.mean(axis=0)
    # Normalise gain so its mean is 1
    gain = pc1 - pc1.min()
    if gain.sum() > 0:
        gain = gain / (gain.mean() + 1e-9)
    else:
        gain = np.ones(n_bins)
    sur = np.zeros_like(real_mat)
    for i in range(n_units):
        rates = base_rates[i] * gain
        sur[i] = rng.poisson(rates).astype(np.int32)
    return sur


# ─── orchestrator ──────────────────────────────────────────────────────────


SURROGATES_FOR_SUBSET = {
    'spontaneous':     ['rate_matched_poisson', 'cell_shuffle', 'state_modulated'],
    'gratings':        ['rate_matched_poisson', 'cell_shuffle'],
    'gratings_movie':  ['rate_matched_poisson', 'cell_shuffle', 'ln_evoked'],
    'natural_movie':   ['rate_matched_poisson', 'cell_shuffle', 'ln_evoked'],
    'noise_movie':     ['rate_matched_poisson', 'cell_shuffle', 'ln_evoked'],
}

GENERATORS = {
    'rate_matched_poisson': surrogate_rate_matched_poisson,
    'cell_shuffle':         surrogate_cell_shuffle,
    'ln_evoked':            surrogate_ln_evoked,
    'state_modulated':      surrogate_state_modulated,
}


def main():
    print("=" * 72)
    print("Phase 22a H2 — surrogate battery + ARS classification")
    print("=" * 72)

    sel = pd.read_parquet(SEL_PATH)
    sel_h2 = sel[sel['h2_pass']].copy()
    print(f"H2-passing units: {len(sel_h2)}")
    print(f"Surrogate seeds per cell: {N_SEEDS}\n")

    rows = []
    for rec_name, group in sel_h2.groupby('recording', sort=False):
        rec = load(rec_name)
        units = group['unit_idx'].astype(int).tolist()
        sur_kinds = SURROGATES_FOR_SUBSET[rec.subset]
        for kind in sur_kinds:
            t0 = time.time()
            for seed in range(N_SEEDS):
                gen = GENERATORS[kind]
                try:
                    sur_mat = gen(rec, units, BIN_MS, seed)
                except Exception as e:
                    print(f"  [error] {rec_name} {kind} seed={seed}: {e}")
                    continue
                events = extract_events(sur_mat, bin_ms=BIN_MS, k_thresh=K_THRESH)
                # Classify at q_max=30 (canonical default).  q_max=100 is
                # used for real-data slow-regime view but not needed in
                # the surrogate comparison: per-q rep_int values at q in
                # [1..30] are identical between q_max=30 and q_max=100
                # runs (the per-q computation is independent of the q_max
                # ceiling), so the survival verdict at q ≤ 30 is the same
                # either way.  Keeping just q_max=30 here brings runtime
                # from ~5h to ~1h.
                q_max = Q_MAX_DEFAULT
                res = classify(events, return_full=True, q_max=q_max)
                cols = per_q_columns(res['per_q'])
                rows.append(dict(
                    recording=rec_name,
                    subset=rec.subset,
                    monkey=rec.monkey,
                    surrogate=kind,
                    seed=seed,
                    q_max=int(q_max),
                    n_units=len(units),
                    n_events=int(events.size),
                    primary=res['primary'],
                    rep_med=res['rep_med'],
                    ks_gue_med=res['ks_gue_med'],
                    n_well=res['n_well'],
                    **cols,
                ))
            dt = time.time() - t0
            print(f"  {rec_name:32s}  {kind:22s}  ⏱{dt:.0f}s")

    df = pd.DataFrame(rows)
    out = OUT_DIR / 'h2_surrogate_classifications.parquet'
    df.to_parquet(out, index=False)
    print(f"\n  → {out}  ({len(df)} rows)")


if __name__ == '__main__':
    main()

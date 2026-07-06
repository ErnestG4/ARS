"""
phase22b/pass_d_glm_surrogate.py — Phase 22b Pass D.

Coupled-GLM (Pillow-style) surrogate for monkey1_natural_movie.

Model per unit i:
    log(lambda_i(t)) = b_i + alpha_i * stim_drive_i(t)
                       + sum_l h_{i,l} * basis_l(history_i)(t)

where:
  - stim_drive_i(t) = STA_i . stim(t)     (1D scalar; STA fit as in
                                            phase22a/h2_surrogates.py)
  - basis_l         = raised-cosine temporal basis on post-spike
                       history (5 functions, log-spaced centres
                       from ~1 to ~20 bins, i.e. 5–100 ms at 5 ms
                       bin width).
  - lambda_i(t)     = exp(linear predictor); Poisson sampling per bin.

Fit: Poisson NLL via scipy.optimize.minimize (L-BFGS-B) with mild L2
regularisation on history weights to prevent runaway after large
spike counts.  No coupling across units (per-unit fit, parallelisable).
History buffer is reset at each trial boundary.

Forward simulation: vectorised across units.  At each bin, store a
rolling (n_units × H) buffer of recent spikes, compute
history_contrib[i] = sum_tau h_kernel[i, tau] * recent_spikes[i, tau-1],
sample Poisson, shift buffer.  ~10 s per seed for monkey1_natural_movie.

5 seeds (up from 3 in Phase 22a) — Phase 22b's headline test deserves
tighter null estimation.

Outputs:
  data/phase22b_results/pass_d_glm_fits.parquet      (per-unit fit
                                                       quality + params)
  data/phase22b_results/pass_d_surrogate_classifications.parquet
  data/phase22b_results/pass_d_survival.parquet
  Stdout: GLM fit quality, surrogate primary distribution, survival
          verdict.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, THIS_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22a'))

from loader import load, MOVIE_TRIAL_SEC
from ars_classify import classify, per_q_columns
from population_events import build_unit_matrix, extract_events
from h2_surrogates import _load_movie

OUT_DIR_22A = Path(ROOT_DIR) / 'data' / 'phase22a_results'
OUT_DIR_22B = Path(ROOT_DIR) / 'data' / 'phase22b_results'
OUT_DIR_22B.mkdir(parents=True, exist_ok=True)
SEL_PATH = OUT_DIR_22A / 'unit_selection.parquet'

RECORDING = 'monkey1_natural_movie'
BIN_MS = 5.0
K_THRESH = 5
N_SEEDS = 5
N_HISTORY_BINS = 20            # 100 ms post-spike at 5 ms bins
N_HISTORY_BASIS = 5            # raised-cosine basis count
N_STIM_BASIS = 4               # 4 raised-cosine basis functions on
                               # past stim_drive (1..40 bins = 5..200 ms
                               # past).  Decouples stimulus-driven
                               # temporal autocorrelation from spike
                               # history — without it, the unconstrained
                               # history kernel absorbs stim autocorr
                               # and produces runaway-positive feedback.
N_STIM_BINS = 40               # 200 ms past stim drive at 5 ms bins
L2_HISTORY = 0.1
L2_STIM = 0.01
Q_MAX = 30


# ─── raised-cosine basis (Pillow log-spaced) ────────────────────────────────


def raised_cosine_basis(n_bins: int, n_basis: int,
                          min_offset: float = 0.5,
                          stretch: float = 1.0) -> np.ndarray:
    """Pillow-style log-spaced raised-cosine basis on [0, n_bins-1].

    Each basis function is a raised cosine centred at log-spaced
    centres, with width chosen so adjacent peaks are at the cosine
    half-amplitude crossings (i.e. neighbouring basis functions sum
    to ~constant in log space).  Standard reference: Pillow et al.
    (2008) Nature, supplementary methods.

    Returns an array of shape (n_basis, n_bins).
    """
    eps = 1e-12
    t = np.arange(n_bins, dtype=np.float64) + min_offset
    # log-stretch the time axis
    nlin = np.log(t * stretch + eps)
    centres = np.linspace(nlin[0], nlin[-1], n_basis)
    spacing = float(centres[1] - centres[0]) if n_basis > 1 else 1.0
    basis = np.zeros((n_basis, n_bins))
    for k in range(n_basis):
        d = (nlin - centres[k]) * np.pi / (2 * spacing)
        basis[k] = np.where(np.abs(d) < np.pi / 2,
                              0.5 * (np.cos(d) + 1), 0.0)
    return basis


# ─── per-unit GLM fit ───────────────────────────────────────────────────────


def fit_one_unit(spikes_per_bin: np.ndarray,
                  stim_drive: np.ndarray,
                  history_basis: np.ndarray,
                  stim_basis: np.ndarray,
                  bins_per_trial: int,
                  l2_history: float = L2_HISTORY,
                  l2_stim: float = L2_STIM,
                  non_positive_history: bool = True,
                  ) -> tuple[np.ndarray, dict]:
    """Fit GLM for one unit.

    spikes_per_bin: (T,) integer spike counts.
    stim_drive:     (T,) STA-projected stimulus drive (zero-mean).
    history_basis:  (n_basis, n_history_bins) basis values.
    non_positive_history: if True, history-basis weights are
        reparameterised as h_k = -softplus(theta_k) so the effective
        post-spike kernel is ≤ 0 everywhere (refractory + slow
        inhibition only).  This is Pillow's standard recommendation
        for stable GLMs and is the default here because the
        unconstrained fit on natural-movie data produces uniformly
        positive history kernels (the GLM absorbs stimulus-driven
        temporal autocorrelation that the cheap STA stim filter
        cannot model), leading to runaway positive feedback in
        forward simulation.

    Returns:
      params        np.ndarray of length 2 + n_basis = (b, alpha, h_1..h_K)
      diagnostics   dict with ll_glm, ll_null, dev_explained, n_spikes,
                    n_bins, history_kernel (length n_history_bins).
    """
    T = spikes_per_bin.size
    n_basis, H = history_basis.shape
    n_stim_basis, S = stim_basis.shape

    # Build per-bin history-basis matrix
    n_trials = T // bins_per_trial
    spikes_2d = spikes_per_bin.reshape(n_trials, bins_per_trial)
    X_hist_2d = np.zeros((n_basis, n_trials, bins_per_trial))
    for k in range(n_basis):
        for trial in range(n_trials):
            sp = spikes_2d[trial]
            for h_off in range(H):
                start = h_off + 1
                if start >= bins_per_trial: continue
                X_hist_2d[k, trial, start:] += (history_basis[k, h_off]
                                                  * sp[:bins_per_trial - start])
    X_hist = X_hist_2d.reshape(n_basis, T)

    # Build per-bin temporal-stim-basis matrix:
    #   X_stim_t[t, k] = sum_{tau=0..S-1} stim_basis[k, tau] * stim_drive[t-tau]
    # Same trial-reset bookkeeping (stim_drive repeats each trial).
    stim_2d = stim_drive.reshape(n_trials, bins_per_trial)
    X_stim_t_2d = np.zeros((n_stim_basis, n_trials, bins_per_trial))
    for k in range(n_stim_basis):
        for trial in range(n_trials):
            sd = stim_2d[trial]
            for h_off in range(S):
                start = h_off
                if start >= bins_per_trial: continue
                X_stim_t_2d[k, trial, start:] += (stim_basis[k, h_off]
                                                    * sd[:bins_per_trial - start])
    X_stim_t = X_stim_t_2d.reshape(n_stim_basis, T)

    # Design matrix: [1, stim_basis_1..S, hist_basis_1..K]
    # → length 1 + n_stim_basis + n_basis
    X = np.column_stack([np.ones(T)] + list(X_stim_t) + list(X_hist))
    y = spikes_per_bin.astype(np.float64)

    n_p_total = 1 + n_stim_basis + n_basis      # bias + stim coeffs + history coeffs

    def _theta_to_history(theta):
        if non_positive_history:
            return -np.log1p(np.exp(np.clip(theta, -30, 30)))
        return theta

    def _grad_theta(theta):
        if non_positive_history:
            return -1.0 / (1.0 + np.exp(-np.clip(theta, -30, 30)))
        return np.ones_like(theta)

    def neg_ll(params_unc):
        # params_unc layout: [bias, stim_1..S, theta_1..K]
        bias = params_unc[0]
        stim_coef = params_unc[1:1 + n_stim_basis]
        theta = params_unc[1 + n_stim_basis:]
        h = _theta_to_history(theta)
        beta = np.concatenate(([bias], stim_coef, h))
        eta = X @ beta
        eta = np.clip(eta, -50, 50)
        lam = np.exp(eta)
        ll = float(np.sum(lam - y * eta))
        if l2_stim > 0:
            ll += l2_stim * float(np.sum(stim_coef ** 2))
        if l2_history > 0:
            ll += l2_history * float(np.sum(h ** 2))
        return ll

    def grad(params_unc):
        bias = params_unc[0]
        stim_coef = params_unc[1:1 + n_stim_basis]
        theta = params_unc[1 + n_stim_basis:]
        h = _theta_to_history(theta)
        dh_dtheta = _grad_theta(theta)
        beta = np.concatenate(([bias], stim_coef, h))
        eta = X @ beta
        eta = np.clip(eta, -50, 50)
        lam = np.exp(eta)
        g_beta = X.T @ (lam - y)
        g = np.zeros_like(params_unc)
        g[0] = g_beta[0]
        g[1:1 + n_stim_basis] = g_beta[1:1 + n_stim_basis]
        g[1 + n_stim_basis:] = g_beta[1 + n_stim_basis:] * dh_dtheta
        if l2_stim > 0:
            g[1:1 + n_stim_basis] += 2 * l2_stim * stim_coef
        if l2_history > 0:
            g[1 + n_stim_basis:] += 2 * l2_history * h * dh_dtheta
        return g

    rate = max(y.mean(), 1e-6)
    x0 = np.zeros(n_p_total)
    x0[0] = float(np.log(rate))
    if non_positive_history:
        x0[1 + n_stim_basis:] = -2.0
    res = minimize(neg_ll, x0, jac=grad, method='L-BFGS-B',
                    options={'maxiter': 300, 'ftol': 1e-9})
    stim_coef_final = res.x[1:1 + n_stim_basis]
    h_final = _theta_to_history(res.x[1 + n_stim_basis:])
    params = np.concatenate(([res.x[0]], stim_coef_final, h_final))

    ll_glm = -res.fun
    ll_null = -float(np.sum(rate - y * np.log(rate))) if rate > 0 else float('nan')
    dev_explained = ((ll_glm - ll_null) / max(abs(ll_null), 1e-9)
                       if np.isfinite(ll_null) else float('nan'))
    # Effective history kernel
    history_kernel = (h_final[:, None] * history_basis).sum(axis=0)
    # Effective stim temporal kernel
    stim_kernel = (stim_coef_final[:, None] * stim_basis).sum(axis=0)
    return params, dict(
        ll_glm=float(ll_glm), ll_null=float(ll_null),
        dev_explained=float(dev_explained),
        n_spikes=int(y.sum()), n_bins=T,
        bias=float(params[0]),
        stim_kernel_l2=float(np.linalg.norm(stim_coef_final)),
        stim_kernel_max=float(stim_kernel.max()),
        history_kernel_max=float(history_kernel.max()),
        history_kernel_min=float(history_kernel.min()),
        history_kernel_l2=float(np.linalg.norm(h_final)),
        converged=bool(res.success),
    )


# ─── forward simulation ─────────────────────────────────────────────────────


def simulate_glm_population(params_per_unit: np.ndarray,
                              stim_drive_per_bin: np.ndarray,
                              history_basis: np.ndarray,
                              stim_basis: np.ndarray,
                              n_stim_basis: int,
                              bins_per_trial: int, n_trials: int,
                              rng: np.random.Generator) -> np.ndarray:
    """Simulate spike counts forward for the population.

    params_per_unit:    (n_units, 1 + n_stim_basis + n_basis) GLM params.
    stim_drive_per_bin: (n_units, bins_per_trial) STA-projected scalar
                        per (unit, bin) — same every trial.
    history_basis:      (n_basis, H).
    stim_basis:         (n_stim_basis, S).

    Returns: (n_units, n_trials * bins_per_trial) integer spike counts.
    """
    n_units = params_per_unit.shape[0]
    n_basis, H = history_basis.shape
    _, S = stim_basis.shape
    out = np.zeros((n_units, n_trials * bins_per_trial), dtype=np.int32)

    bias = params_per_unit[:, 0]                                        # (n_units,)
    stim_coefs = params_per_unit[:, 1:1 + n_stim_basis]                 # (n_units, n_stim_basis)
    h_coefs = params_per_unit[:, 1 + n_stim_basis:]                     # (n_units, n_basis)

    # Effective history kernel per unit: (n_units, H)
    h_kernel = h_coefs @ history_basis

    # Pre-compute stim contribution per (unit, bin) — deterministic stim,
    # same every trial.  stim_temporal_drive[i, t] = sum_k coef[i, k]
    #   * sum_tau stim_basis[k, tau] * stim_drive_per_bin[i, t-tau]
    # Equivalent to: project stim_drive_per_bin via the per-unit
    # temporal stim kernel (k_temporal[i, tau] = stim_coefs[i] @ stim_basis[:, tau])
    k_temporal = stim_coefs @ stim_basis                                # (n_units, S)
    stim_temporal_drive = np.zeros((n_units, bins_per_trial))
    for tau in range(S):
        if tau >= bins_per_trial: break
        stim_temporal_drive[:, tau:] += (k_temporal[:, tau:tau+1]
                                           * stim_drive_per_bin[:, :bins_per_trial - tau])

    ETA_MAX_SIM = 5.0
    for trial in range(n_trials):
        recent = np.zeros((n_units, H), dtype=np.float64)
        for t in range(bins_per_trial):
            history_contrib = (h_kernel * recent).sum(axis=1)
            eta = bias + stim_temporal_drive[:, t] + history_contrib
            eta = np.clip(eta, -50, ETA_MAX_SIM)
            lam = np.exp(eta)
            y = rng.poisson(lam).astype(np.int32)
            global_t = trial * bins_per_trial + t
            out[:, global_t] = y
            recent[:, 1:] = recent[:, :-1]
            recent[:, 0] = y
    return out


# ─── orchestrator ───────────────────────────────────────────────────────────


def main():
    print("=" * 72)
    print("Phase 22b Pass D — Coupled-GLM surrogate for monkey1_natural_movie")
    print("=" * 72)

    sel = pd.read_parquet(SEL_PATH)
    sel_h2 = sel[(sel['recording'] == RECORDING) & sel['h2_pass']]
    units = sel_h2['unit_idx'].astype(int).tolist()
    print(f"  recording: {RECORDING}, H2 units: {len(units)}, "
          f"bin={BIN_MS}ms, history={N_HISTORY_BINS}*{BIN_MS}ms"
          f"={N_HISTORY_BINS * BIN_MS:.0f}ms, n_basis={N_HISTORY_BASIS}")
    print()

    rec = load(RECORDING)
    bin_s = BIN_MS / 1000.0
    bins_per_trial = int(round(MOVIE_TRIAL_SEC / bin_s))   # 6000 at 5ms
    n_trials = rec.n_trials                                  # 120

    # Stimulus matrix: per-bin stim from the natural movie
    Z, n_frames = _load_movie('natural_movie', rec.monkey)
    bin_per_frame = max(1, int(round(MOVIE_TRIAL_SEC * 1000
                                         / n_frames / BIN_MS)))
    per_bin_stim = np.repeat(Z, bin_per_frame, axis=0)
    if per_bin_stim.shape[0] > bins_per_trial:
        per_bin_stim = per_bin_stim[:bins_per_trial]
    elif per_bin_stim.shape[0] < bins_per_trial:
        pad = np.zeros((bins_per_trial - per_bin_stim.shape[0],
                          Z.shape[1]), dtype=np.float32)
        per_bin_stim = np.concatenate([per_bin_stim, pad], axis=0)

    # Real population matrix
    real_mat, total_dur = build_unit_matrix(rec, units, bin_ms=BIN_MS)
    n_units, T = real_mat.shape
    print(f"  population matrix: {real_mat.shape}, total_dur={total_dur:.0f}s")

    # ─── STA per unit (reuse the LN logic) ─────
    print("  computing STA per unit...")
    real32 = real_mat.astype(np.float32)
    avg_response = real32.reshape(n_units, n_trials,
                                    bins_per_trial).mean(axis=1)
    weights = avg_response.sum(axis=1, keepdims=True) + 1e-9
    sta_all = (avg_response @ per_bin_stim) / weights
    sta_all = sta_all - sta_all.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(sta_all, axis=1, keepdims=True) + 1e-9
    sta_all = sta_all / norms

    # Stim drive per unit (one trial's worth; identical every trial)
    stim_drive = sta_all @ per_bin_stim.T            # (n_units, bins_per_trial)

    # Build raised-cosine bases
    history_basis = raised_cosine_basis(N_HISTORY_BINS, N_HISTORY_BASIS,
                                          min_offset=0.5, stretch=1.0)
    stim_basis = raised_cosine_basis(N_STIM_BINS, N_STIM_BASIS,
                                       min_offset=0.5, stretch=1.0)
    print(f"  history basis: {history_basis.shape} (n_basis × H bins)")
    print(f"  stim temporal basis: {stim_basis.shape}")

    # ─── per-unit GLM fit ─────
    print(f"  fitting {n_units} per-unit Poisson GLMs...")
    fit_rows = []
    n_p_total = 1 + N_STIM_BASIS + N_HISTORY_BASIS
    params_all = np.zeros((n_units, n_p_total))
    t0 = time.time()
    for i in range(n_units):
        unit_stim = np.tile(stim_drive[i], n_trials)
        # Default: non_positive_history=True (Pillow recommendation
        # for stable GLMs).  Save the canonical Pass D output here.
        # The companion unconstrained-history run is preserved under
        # pass_d_unconstrained_*.parquet for diagnostic comparison.
        params_i, diag = fit_one_unit(real_mat[i].astype(np.float64),
                                        unit_stim, history_basis,
                                        stim_basis, bins_per_trial,
                                        non_positive_history=True)
        params_all[i] = params_i
        fit_rows.append(dict(unit_idx=units[i], unit_id=rec.unit_id(units[i]),
                              **diag))
        if (i + 1) % 10 == 0 or i == n_units - 1:
            dt = time.time() - t0
            print(f"    {i+1:3d}/{n_units}  ⏱{dt:.0f}s")
    fits_df = pd.DataFrame(fit_rows)
    fits_df.to_parquet(OUT_DIR_22B / 'pass_d_glm_fits.parquet', index=False)
    print(f"  → {OUT_DIR_22B}/pass_d_glm_fits.parquet  ({len(fits_df)} units)")

    print()
    print("GLM fit-quality summary:")
    print(f"  units converged:              {int(fits_df['converged'].sum())} / {len(fits_df)}")
    print(f"  median dev_explained vs null: {fits_df['dev_explained'].median():.3f}")
    print(f"  fraction units dev>0.01:      {(fits_df['dev_explained']>0.01).mean():.2f}")
    print(f"  history kernel median |l2|:   {fits_df['history_kernel_l2'].median():.3f}")
    print(f"  history kernel min (median):  {fits_df['history_kernel_min'].median():.3f}  "
          f"(should be negative — refractory)")
    print(f"  history kernel max (median):  {fits_df['history_kernel_max'].median():.3f}  "
          f"(non-positive constraint → max ≤ 0)")
    print(f"  stim temporal kernel l2:      {fits_df['stim_kernel_l2'].median():.3f}")

    # ─── forward simulation × N seeds ─────
    print()
    print(f"  simulating {N_SEEDS} surrogate replicates...")
    surrogate_rows = []
    for seed in range(N_SEEDS):
        rng = np.random.default_rng(seed)
        t0 = time.time()
        sur_mat = simulate_glm_population(params_all, stim_drive,
                                            history_basis, stim_basis,
                                            N_STIM_BASIS,
                                            bins_per_trial,
                                            n_trials, rng)
        events = extract_events(sur_mat, bin_ms=BIN_MS, k_thresh=K_THRESH)
        res = classify(events, return_full=True, q_max=Q_MAX)
        cols = per_q_columns(res['per_q'])
        surrogate_rows.append(dict(
            recording=RECORDING, surrogate='glm_history_coupled',
            seed=seed, q_max=Q_MAX,
            n_units=n_units, n_events=int(events.size),
            primary=res['primary'], rep_med=res['rep_med'],
            ks_gue_med=res['ks_gue_med'], n_well=res['n_well'],
            **cols,
        ))
        dt = time.time() - t0
        print(f"    seed {seed}: events={events.size:6d}  primary={res['primary']:13s}  "
              f"rep_med={res['rep_med']:.3f}  ⏱{dt:.0f}s")

    sur_df = pd.DataFrame(surrogate_rows)
    sur_df.to_parquet(OUT_DIR_22B / 'pass_d_surrogate_classifications.parquet',
                       index=False)

    # ─── survival vs Phase 22a real ─────
    real_pop = pd.read_parquet(OUT_DIR_22A / 'h2_population_classifications.parquet')
    real_row = real_pop[(real_pop['recording'] == RECORDING) &
                          (real_pop['q_max'] == Q_MAX)]
    if not len(real_row):
        print("  ERROR: no Phase 22a real-data row for monkey1_natural_movie q_max=30")
        return
    real_row = real_row.iloc[0]
    real_rep = np.array(list(real_row['rep_int_per_q']), dtype=float)
    real_quad = list(real_row['quadrants_per_q'])

    sur_reps = np.stack([np.array(list(r['rep_int_per_q']), dtype=float)
                          for r in surrogate_rows])
    pct_hi = np.nanpercentile(sur_reps, 95, axis=0)
    from collections import Counter
    quad_modal = []
    for qi in range(real_rep.size):
        items = [r['quadrants_per_q'][qi] for r in surrogate_rows
                  if r['quadrants_per_q'] is not None and qi < len(r['quadrants_per_q'])]
        items = [x for x in items if x is not None]
        if items:
            quad_modal.append(Counter(items).most_common(1)[0][0])
        else:
            quad_modal.append(None)

    surv_rows = []
    n_rep = n_quad = n_both = 0
    for qi in range(real_rep.size):
        sr = (not np.isnan(real_rep[qi])) and (not np.isnan(pct_hi[qi])) \
              and (real_rep[qi] > pct_hi[qi])
        rq = real_quad[qi] if qi < len(real_quad) else None
        sq = quad_modal[qi]
        sq_diff = (rq is not None and sq is not None and rq != sq)
        sb = sr and sq_diff
        n_rep += int(sr); n_quad += int(sq_diff); n_both += int(sb)
        surv_rows.append(dict(
            q=qi + 1, real_rep_int=float(real_rep[qi]),
            surr_rep_int_p95=float(pct_hi[qi]),
            real_quadrant=rq, surr_modal_quadrant=sq,
            survives_rep=sr, survives_quad=sq_diff, survives_both=sb,
        ))
    surv_df = pd.DataFrame(surv_rows)
    surv_df.to_parquet(OUT_DIR_22B / 'pass_d_survival.parquet', index=False)

    print()
    print("Survival of monkey1_natural_movie real vs GLM-history-coupled surrogate:")
    print(f"  q-bands surviving rep_int>p95:    {n_rep} / {real_rep.size}")
    print(f"  q-bands with quadrant difference: {n_quad} / {real_rep.size}")
    print(f"  q-bands with BOTH (strict):       {n_both} / {real_rep.size}")
    print()
    if n_both >= 1:
        print("  PASS — Aitchison-null engagement strengthened.  The "
              "elimination space now excludes per-unit history-coupled "
              "LN-Poisson generative models.")
    elif n_rep >= 1:
        print("  SOFT PASS — real exceeds GLM-surrogate at the rep level "
              "but not the quadrant level.  Substantive elimination beyond "
              "cheap-LN; partial-success worth surfacing.")
    else:
        print("  FAIL — GLM surrogate reproduces the real structure.  "
              "Phase 22a's monkey1_natural_movie finding downgrades to: "
              "structure consistent with per-unit history-coupled LN-Poisson, "
              "not an Aitchison-null-surviving claim about cross-cell joint "
              "dynamics.")


if __name__ == '__main__':
    main()

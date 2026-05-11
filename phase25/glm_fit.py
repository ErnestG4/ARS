"""
phase25/glm_fit.py — per-unit Pillow-style Poisson GLM fit, generalised
from Phase 22b's pass_d_glm_surrogate.fit_one_unit.

Differences from Phase 22b:
  * Stimulus drive is computed externally (via multi-frame STA) and
    passed in; this module is agnostic to whether the STA is single-
    or multi-frame.
  * Bin width is parameterised (5 / 10 / 20 / 40 ms); the GLM operates
    entirely at the bin width chosen for fit.  Per-bin design matrices
    are built from spikes_per_bin and stim_drive at that resolution.
  * History timescale and stim-history timescale are fixed in
    milliseconds (default: 100 ms and 200 ms), then converted to bin
    counts so the GLM's effective temporal extent is bin-width-
    invariant.  At coarser bins this means fewer basis bins → smaller
    history-kernel basis.
  * Raised-cosine basis is reused from Phase 22b
    (pass_d_glm_surrogate.raised_cosine_basis).

Variant axis (`non_positive_history`):
  * True  — canonical Pillow recommendation; history weights are
            -softplus(theta), so the post-spike kernel is ≤ 0 (refractory
            + slow inhibition).  Stable in principle but on
            natural-movie data with insufficient stim absorption it
            collapses both kernels to ~0 (Phase 22b).
  * False — unconstrained; history weights are theta directly.  On
            insufficient-stim-absorption data this routes stim
            autocorrelation into the history kernel and produces
            runaway-positive feedback (Phase 22b).

Phase 25's hypothesis: at the right (n_lags, bin_width), neither
failure mode occurs because the multi-frame STA absorbs the stim
autocorr at the projection step.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22a'))
sys.path.insert(0, str(Path(ROOT_DIR) / 'phase22b'))

from pass_d_glm_surrogate import raised_cosine_basis


# Bin-width-invariant temporal extents (milliseconds):
HISTORY_MS = 100.0     # post-spike history window
STIM_TEMPORAL_MS = 200.0   # past-drive temporal-basis window on the
                            # projected drive — additional flexibility on
                            # top of the STA's own lag structure
N_HISTORY_BASIS_MAX = 5
N_STIM_BASIS_MAX = 4

L2_HISTORY = 0.1
L2_STIM = 0.01


def basis_config(bin_ms: float) -> dict:
    """Return basis configuration for the given bin width.

    n_history_bins covers 100 ms; n_stim_bins covers 200 ms.  At 40 ms
    bins these become 3 and 5 respectively (rounded up), giving the
    GLM a meaningful but coarse history kernel.

    n_basis is reduced when bin coverage is < basis-count to avoid
    over-parameterised bases on a few bins.
    """
    n_history_bins = max(1, int(round(HISTORY_MS / bin_ms)))
    n_stim_bins = max(1, int(round(STIM_TEMPORAL_MS / bin_ms)))
    n_history_basis = min(N_HISTORY_BASIS_MAX, n_history_bins)
    n_stim_basis = min(N_STIM_BASIS_MAX, n_stim_bins)
    return dict(
        n_history_bins=n_history_bins, n_history_basis=n_history_basis,
        n_stim_bins=n_stim_bins, n_stim_basis=n_stim_basis,
    )


def fit_one_unit(spikes_per_bin: np.ndarray,
                  stim_drive: np.ndarray,
                  history_basis: np.ndarray,
                  stim_basis: np.ndarray,
                  bins_per_trial: int,
                  l2_history: float = L2_HISTORY,
                  l2_stim: float = L2_STIM,
                  non_positive_history: bool = True,
                  maxiter: int = 300,
                  ) -> tuple[np.ndarray, dict]:
    """Fit GLM for one unit.  See module-level docstring for variant
    semantics.

    spikes_per_bin: (T,) integer spike counts at the chosen bin width.
    stim_drive:     (T,) STA-projected stimulus drive (per-bin scalar).
    history_basis:  (n_history_basis, n_history_bins).
    stim_basis:     (n_stim_basis, n_stim_bins).
    bins_per_trial: int — trial reset boundary, so history doesn't
                    bleed across trial onsets.

    Returns:
      params        np.ndarray length 1 + n_stim_basis + n_history_basis
                    = (bias, stim_coef_1..S, history_kernel_1..K).
      diagnostics   dict matching Phase 22b's diag fields plus
                    history_kernel (the effective per-bin post-spike
                    kernel) and stim_kernel (the effective per-bin past-
                    drive kernel) as arrays for diagnostic plotting.
    """
    T = spikes_per_bin.size
    n_basis, H = history_basis.shape
    n_stim_basis, S = stim_basis.shape

    # Per-bin history-basis features (n_basis, T)
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

    # Per-bin stim-temporal-basis features (n_stim_basis, T)
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
    X = np.column_stack([np.ones(T)] + list(X_stim_t) + list(X_hist))
    y = spikes_per_bin.astype(np.float64)
    n_p_total = 1 + n_stim_basis + n_basis

    def _theta_to_history(theta):
        if non_positive_history:
            return -np.log1p(np.exp(np.clip(theta, -30, 30)))
        return theta

    def _grad_theta(theta):
        if non_positive_history:
            return -1.0 / (1.0 + np.exp(-np.clip(theta, -30, 30)))
        return np.ones_like(theta)

    def neg_ll(params_unc):
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
                    options={'maxiter': maxiter, 'ftol': 1e-9})

    stim_coef_final = res.x[1:1 + n_stim_basis]
    h_final = _theta_to_history(res.x[1 + n_stim_basis:])
    params = np.concatenate(([res.x[0]], stim_coef_final, h_final))

    ll_glm = -res.fun
    ll_null = (-float(np.sum(rate - y * np.log(rate)))
                if rate > 0 else float('nan'))
    dev_explained = ((ll_glm - ll_null) / max(abs(ll_null), 1e-9)
                       if np.isfinite(ll_null) else float('nan'))
    history_kernel = (h_final[:, None] * history_basis).sum(axis=0)
    stim_kernel = (stim_coef_final[:, None] * stim_basis).sum(axis=0)
    return params, dict(
        ll_glm=float(ll_glm), ll_null=float(ll_null),
        dev_explained=float(dev_explained),
        n_spikes=int(y.sum()), n_bins=T,
        bias=float(params[0]),
        stim_kernel_l2=float(np.linalg.norm(stim_coef_final)),
        stim_kernel_max=float(stim_kernel.max()),
        stim_kernel_min=float(stim_kernel.min()),
        history_kernel_max=float(history_kernel.max()),
        history_kernel_min=float(history_kernel.min()),
        history_kernel_l2=float(np.linalg.norm(h_final)),
        history_kernel=history_kernel.tolist(),
        stim_kernel=stim_kernel.tolist(),
        converged=bool(res.success),
        n_iter=int(res.nit),
    )


def simulate_glm_population(params_per_unit: np.ndarray,
                              stim_drive_per_bin: np.ndarray,
                              history_basis: np.ndarray,
                              stim_basis: np.ndarray,
                              n_stim_basis: int,
                              bins_per_trial: int, n_trials: int,
                              rng: np.random.Generator,
                              eta_max: float = 5.0,
                              ) -> np.ndarray:
    """Forward-simulate spike counts for the population at the GLM's
    bin width.  Vectorised across units.

    eta_max: clip on linear predictor before exp.  Phase 22b uses 5.0
    to prevent unconstrained-history runaway from saturating to
    Poisson(exp(50)) per bin — at the cost of biasing the surrogate
    rate downward when the history kernel is genuinely runaway.  For
    fit-quality-verified configurations this clip is rarely engaged.

    params_per_unit:    (n_units, 1 + n_stim_basis + n_history_basis).
    stim_drive_per_bin: (n_units, bins_per_trial) STA-projected scalar
                        per (unit, bin) — same every trial.
    Returns:            (n_units, n_trials*bins_per_trial) int32.
    """
    n_units = params_per_unit.shape[0]
    n_basis, H = history_basis.shape
    _, S = stim_basis.shape

    bias = params_per_unit[:, 0]                                        # (n_units,)
    stim_coefs = params_per_unit[:, 1:1 + n_stim_basis]                 # (n_units, n_stim_basis)
    h_coefs = params_per_unit[:, 1 + n_stim_basis:]                     # (n_units, n_basis)

    # Effective per-bin history kernel per unit: (n_units, H)
    h_kernel = h_coefs @ history_basis

    # Stim contribution per (unit, bin): convolve the projected drive
    # with the per-unit effective stim temporal kernel.
    k_temporal = stim_coefs @ stim_basis                                # (n_units, S)
    stim_temporal_drive = np.zeros((n_units, bins_per_trial))
    for tau in range(S):
        if tau >= bins_per_trial: break
        stim_temporal_drive[:, tau:] += (k_temporal[:, tau:tau+1]
                                           * stim_drive_per_bin[:, :bins_per_trial - tau])

    out = np.zeros((n_units, n_trials * bins_per_trial), dtype=np.int32)
    for trial in range(n_trials):
        recent = np.zeros((n_units, H), dtype=np.float64)
        for t in range(bins_per_trial):
            history_contrib = (h_kernel * recent).sum(axis=1)
            eta = bias + stim_temporal_drive[:, t] + history_contrib
            eta = np.clip(eta, -50, eta_max)
            lam = np.exp(eta)
            y = rng.poisson(lam).astype(np.int32)
            out[:, trial * bins_per_trial + t] = y
            recent[:, 1:] = recent[:, :-1]
            recent[:, 0] = y
    return out


def resample_to_5ms(sim_mat: np.ndarray, bin_ms: float,
                      rng: np.random.Generator) -> np.ndarray:
    """Resample a GLM-bin-width spike-count matrix to 5 ms bins.

    Within each B-ms bin the GLM rate is constant, so each unit's per-
    sub-bin spike count is independent Poisson with rate λ_unit / (B/5).
    Equivalently, distribute the per-B-ms-bin count uniformly across
    the (B/5) sub-bins as a multinomial split.  This second formulation
    is more memory-efficient and is what we use.

    For bin_ms == 5 ms this is a no-op.
    """
    factor = int(round(bin_ms / 5.0))
    if factor <= 1:
        return sim_mat.astype(np.int32)
    n_units, T_coarse = sim_mat.shape
    out = np.zeros((n_units, T_coarse * factor), dtype=np.int32)
    p = np.full(factor, 1.0 / factor)
    for i in range(n_units):
        # vectorise per unit: multinomial split of each coarse-bin count
        counts = sim_mat[i].astype(np.int32)
        for t in range(T_coarse):
            c = int(counts[t])
            if c == 0: continue
            out[i, t * factor:(t + 1) * factor] = rng.multinomial(c, p)
    return out


__all__ = [
    'HISTORY_MS', 'STIM_TEMPORAL_MS', 'N_HISTORY_BASIS_MAX', 'N_STIM_BASIS_MAX',
    'L2_HISTORY', 'L2_STIM', 'basis_config', 'fit_one_unit',
    'simulate_glm_population', 'resample_to_5ms', 'raised_cosine_basis',
]

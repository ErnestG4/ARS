"""
cross_substrate/axes.py — landscape coordinate computations (v0).

Pure axis functions for the cross-substrate fingerprint landscape, per
viewpoints.md §2/§5. Families I (NNS distances), II (long-range), III
(RF arithmetic), VI (extraction-meta) for the initial AM + pvc-11 pass.
Families IV (spectral character) / V (dynamical) deferred.

MATCHED-INSTRUMENT CONTRACT
---------------------------
Every substrate hands Family I/II its UNFOLDED POSITIONS (unit-mean-ish
sequence on the real line). Family I derives the canonical spacing array
via `phase35a.unfold_rotnum.spacings` (2–98% tail trim + unit-mean
renorm) — the SAME extractor AM's W1δ uses — so I.1–I.9 are computed
identically across AM and pvc-11. Family II consumes the positions
directly (no trim; long-range). Reference NNS distributions are the
universality.py canonical forms — the same GUE the pvc-11 ks_gue_med
H1 work used.

Comparison-validity is annotated at banking time, not enforced here:
non-matching instruments (e.g. pvc-11's Farey-q-banded ks_gue_med) are
carried as separately-labelled axes (see carry-viewpoints-annotate-validity).

N/A CONVENTION
--------------
Each axis returns either a float (or vector for III.2-type), or None when
the axis does not apply or there is insufficient data. The caller records
the None + reason in the coordinate record; never stub with 0/sentinel
numbers that could be mistaken for measurements (instructions §4).
"""
from __future__ import annotations

import os
import sys
from typing import Optional, Sequence

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scipy.optimize import minimize_scalar
from scipy.special import gamma as _gamma

from universality import (                       # canonical references + long-range
    nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue,
    number_variance, spectral_form_factor, pair_correlation,
)
from phase35a.unfold_rotnum import spacings as _trim_spacings  # matched leg
from phase34e.run_berry_robnik import fit_rho as _fit_br_rho   # CORRECTED fitter


# ── thresholds (event-count gates) ───────────────────────────────────────────
MIN_N_NNS = 20          # Family I distance axes
MIN_N_FIT = 50          # Brody / Berry-Robnik MLE
MIN_N_LONGRANGE = 200   # Σ²(L), Δ₃(L) — long-range needs many events


# ── helpers ──────────────────────────────────────────────────────────────────
def canonical_spacings(positions: Sequence[float]) -> np.ndarray:
    """The matched spacing array: 2–98% trim + unit-mean renorm of the
    unfolded positions. Identical extractor across substrates."""
    return _trim_spacings(np.asarray(positions, dtype=np.float64))


def _w1_cdf(s: np.ndarray, cdf_func, grid_max: float = 8.0,
            n_grid: int = 2000) -> float:
    """1-Wasserstein between empirical spacings and a reference whose CDF
    is `cdf_func`, via W1 = ∫|F_emp − F_ref| ds on a fine grid (deterministic)."""
    s = np.sort(np.asarray(s, dtype=np.float64))
    if s.size == 0:
        return float("nan")
    grid = np.linspace(0.0, max(grid_max, float(s[-1])), n_grid)
    f_emp = np.searchsorted(s, grid, side="right") / s.size
    f_ref = np.asarray(cdf_func(grid), dtype=np.float64)
    return float(np.trapezoid(np.abs(f_emp - f_ref), grid))


def _ks_cdf(s: np.ndarray, cdf_func) -> float:
    s = np.sort(np.asarray(s, dtype=np.float64))
    n = s.size
    emp = np.arange(1, n + 1) / n
    return float(np.max(np.abs(emp - np.asarray(cdf_func(s), dtype=np.float64))))


# ── Family I — NNS distribution distances ────────────────────────────────────
def I1_w1_clock(s) -> Optional[float]:
    """W1δ = E|s−1|. Closed form of W1 to δ(s−1). Matches unfold_rotnum.W1d."""
    s = np.asarray(s, dtype=np.float64)
    if s.size < MIN_N_NNS:
        return None
    return float(np.mean(np.abs(s - 1.0)))


def I2_w1_gue(s) -> Optional[float]:
    s = np.asarray(s, dtype=np.float64)
    return _w1_cdf(s, nns_cdf_gue) if s.size >= MIN_N_NNS else None


def I3_w1_goe(s) -> Optional[float]:
    s = np.asarray(s, dtype=np.float64)
    return _w1_cdf(s, nns_cdf_goe) if s.size >= MIN_N_NNS else None


def I4_w1_poisson(s) -> Optional[float]:
    s = np.asarray(s, dtype=np.float64)
    return _w1_cdf(s, nns_cdf_poisson) if s.size >= MIN_N_NNS else None


def I5_ks_gue(s) -> Optional[float]:
    """KS to GUE on the matched plain-NNS object (object (a)). Distinct from
    pvc-11's banked Farey-q-banded ks_gue_med (carry that separately)."""
    s = np.asarray(s, dtype=np.float64)
    return _ks_cdf(s, nns_cdf_gue) if s.size >= MIN_N_NNS else None


def I6_ks_clock(s) -> Optional[float]:
    """KS to δ(s−1): max|F_emp − 1{s≥1}|."""
    s = np.sort(np.asarray(s, dtype=np.float64))
    if s.size < MIN_N_NNS:
        return None
    n = s.size
    emp = np.arange(1, n + 1) / n
    step = (s >= 1.0).astype(np.float64)
    return float(np.max(np.abs(emp - step)))


def I7_ks_poisson(s) -> Optional[float]:
    s = np.asarray(s, dtype=np.float64)
    return _ks_cdf(s, nns_cdf_poisson) if s.size >= MIN_N_NNS else None


def _brody_b(q: float) -> float:
    """Normalization constant b(q) giving unit-mean Brody P(s)."""
    return float(_gamma((q + 2.0) / (q + 1.0)) ** (q + 1.0))


def brody_pdf(s: np.ndarray, q: float) -> np.ndarray:
    """Brody P(s;q) = (q+1) b s^q exp(−b s^{q+1}); unit integral & unit mean.
    q=0 → Poisson exp(−s); q=1 → Wigner GOE."""
    s = np.asarray(s, dtype=np.float64)
    b = _brody_b(q)
    return (q + 1.0) * b * np.power(s, q) * np.exp(-b * np.power(s, q + 1.0))


def I8_brody_q(s) -> Optional[float]:
    """MLE of Brody q ∈ [0,1]. Validate via validate_fitters before banking."""
    s = np.asarray(s, dtype=np.float64)
    s = s[(s > 0) & (s < 10.0)]
    if s.size < MIN_N_FIT:
        return None

    def nll(q):
        p = np.maximum(brody_pdf(s, q), 1e-300)
        return -np.sum(np.log(p))

    res = minimize_scalar(nll, bounds=(0.0, 1.0), method="bounded",
                          options={"xatol": 1e-4})
    return float(res.x)


def I9_berry_robnik_rho(s) -> Optional[float]:
    """MLE of Berry-Robnik ρ (GOE fraction) via the phase34e corrected fitter.
    ρ=0 → Poisson, ρ=1 → GOE. Validate before banking."""
    s = np.asarray(s, dtype=np.float64)
    s = s[s > 0]
    if s.size < MIN_N_FIT:
        return None
    # only rho_mle is banked (bootstrap σ discarded); n_bootstrap=1 keeps the
    # phase34e fitter's percentile step non-empty while staying cheap on large s.
    return float(_fit_br_rho(s, n_bootstrap=1)["rho_mle"])


FAMILY_I = {
    "I.1_w1_clock": I1_w1_clock, "I.2_w1_gue": I2_w1_gue,
    "I.3_w1_goe": I3_w1_goe, "I.4_w1_poisson": I4_w1_poisson,
    "I.5_ks_gue": I5_ks_gue, "I.6_ks_clock": I6_ks_clock,
    "I.7_ks_poisson": I7_ks_poisson, "I.8_brody_q": I8_brody_q,
    "I.9_berry_robnik_rho": I9_berry_robnik_rho,
}


def compute_family_I(positions) -> dict:
    """All Family I axes from unfolded positions (routes through the matched
    canonical_spacings extractor)."""
    s = canonical_spacings(positions)
    return {name: fn(s) for name, fn in FAMILY_I.items()}


# ── Family II — long-range NNS correlations ──────────────────────────────────
def matched_L(n_events: int, frac: float = 0.02, lo: float = 5.0,
              hi: float = 50.0) -> float:
    """Cross-substrate-matched window length: a fixed FRACTION of event count
    (in mean-spacing units), clipped to [lo, hi]. Flagged choice — see
    instructions §8.4 / implementation_notes."""
    return float(np.clip(n_events * frac, lo, hi))


# long-range averages need only a bounded number of window placements; sliding by
# tiny steps over all N events is wasteful and scales badly (was ~17 min/cell). Cap.
N_WIN_CAP = 400          # window placements for the Σ²/Δ₃ averages
DELTA3_EVAL = 64         # staircase eval points per Δ₃ window


def _window_starts(e, L):
    span = float(e[-1] - e[0])
    if L >= span:
        return None
    n_win = int(np.clip(span / L, 5, N_WIN_CAP))   # ~independent windows, capped
    return np.linspace(e[0], e[-1] - L, n_win)


def II1_sigma2_at_L(positions, L: Optional[float] = None) -> Optional[float]:
    """Number variance Σ²(L) = var(count in window of length L). Capped windows +
    searchsorted (O(n_win·log N)), matched-L."""
    e = np.sort(np.asarray(positions, dtype=np.float64))
    if e.size < MIN_N_LONGRANGE:
        return None
    if L is None:
        L = matched_L(e.size)
    x0 = _window_starts(e, L)
    if x0 is None:
        return None
    counts = (np.searchsorted(e, x0 + L, "left")
              - np.searchsorted(e, x0, "left")).astype(np.float64)
    return float(np.var(counts, ddof=1)) if counts.size > 1 else None


def II2_delta3_at_L(positions, L: Optional[float] = None) -> Optional[float]:
    """Spectral rigidity Δ₃(L): mean-square deviation of the counting staircase
    from a best-fit line over a length-L window, averaged over capped placements."""
    e = np.sort(np.asarray(positions, dtype=np.float64))
    if e.size < MIN_N_LONGRANGE:
        return None
    if L is None:
        L = matched_L(e.size)
    starts = _window_starts(e, L)
    if starts is None or starts.size < 5:
        return None
    vals = []
    for x0 in starts:
        xs = np.linspace(x0, x0 + L, DELTA3_EVAL)
        Nx = np.searchsorted(e, xs, side="right").astype(np.float64)
        A = np.vstack([xs, np.ones_like(xs)]).T
        coef, *_ = np.linalg.lstsq(A, Nx, rcond=None)
        resid = Nx - A @ coef
        vals.append(np.mean(resid ** 2))
    return float(np.mean(vals))


def II3_K_at_tau(positions, tau: float = 1.0) -> Optional[float]:
    """Spectral form factor K(τ) at fixed τ. Lower priority (initial pass)."""
    e = np.asarray(positions, dtype=np.float64)
    if e.size < MIN_N_LONGRANGE:
        return None
    sff = spectral_form_factor(e, t_max=max(tau * 1.2, 2.0), n_t=120)
    t, K = sff["t"], sff["K"]
    if t.size == 0:
        return None
    return float(K[int(np.argmin(np.abs(t - tau)))])


def compute_family_II(positions, L: Optional[float] = None) -> dict:
    return {
        "II.1_sigma2_L": II1_sigma2_at_L(positions, L),
        "II.2_delta3_L": II2_delta3_at_L(positions, L),
        "II.3_K_tau1": II3_K_at_tau(positions, 1.0),
        "II.4_R2_shape": None,   # applicable, not computed (initial pass)
    }


# ── Family III — RF arithmetic ───────────────────────────────────────────────
# pvc-11 already banks rf_amp_per_q (q=1..30) per unit; derive from that.
SMALL_PRIMES = (2, 3, 5, 7)


def III1_p_concentration(rf_amp_per_q: Sequence[float], p: int) -> Optional[float]:
    """RF amplitude at the mode corresponding to denominator q=p.
    FLAGGED reduction: 'amplitude at q=p' (peak), not sum over multiples —
    see implementation_notes / instructions §8.3."""
    v = np.asarray(rf_amp_per_q, dtype=np.float64)
    if v.size < p:
        return None
    return float(v[p - 1])


def III2_small_prime_vector(rf_amp_per_q) -> Optional[list]:
    out = [III1_p_concentration(rf_amp_per_q, p) for p in SMALL_PRIMES]
    return None if any(x is None for x in out) else out


def III4_scalar_reduction(rf_amp_per_q) -> Optional[float]:
    """Default scalar = SUM over small primes (reversible: III.2 vector banked too)."""
    vec = III2_small_prime_vector(rf_amp_per_q)
    return None if vec is None else float(np.sum(vec))


def compute_family_III_from_rf(rf_amp_per_q) -> dict:
    return {
        "III.1_p2": III1_p_concentration(rf_amp_per_q, 2),
        "III.1_p3": III1_p_concentration(rf_amp_per_q, 3),
        "III.1_p5": III1_p_concentration(rf_amp_per_q, 5),
        "III.1_p7": III1_p_concentration(rf_amp_per_q, 7),
        "III.2_small_prime_vector": III2_small_prime_vector(rf_amp_per_q),
        "III.4_scalar_sum": III4_scalar_reduction(rf_amp_per_q),
    }


# ── Family VI — extraction-meta ──────────────────────────────────────────────
def VI1_L_iter_alpha(loglog_alpha_mean: Optional[float],
                     loglog_alpha_spread: Optional[float] = None) -> Optional[dict]:
    """L_iter convergence rate α (read from banked Phase 35 loglog_alpha).
    Returns mean + spread; caller flags L-range-dependence where known."""
    if loglog_alpha_mean is None:
        return None
    return {"alpha_mean": float(loglog_alpha_mean),
            "alpha_spread": None if loglog_alpha_spread is None
            else float(loglog_alpha_spread)}


def VI2_N_scaling_beta(N_values: Sequence[float],
                       spreads: Sequence[float]) -> Optional[dict]:
    """N-scaling exponent β: log(L-converged spread) ~ β·log(N). Substrate-level
    (not per-cell). Reports β, the per-segment local slopes, and a 3-point caveat."""
    N = np.asarray(N_values, dtype=np.float64)
    g = np.asarray(spreads, dtype=np.float64)
    ok = (N > 0) & (g > 0)
    N, g = N[ok], g[ok]
    if N.size < 2:
        return None
    coef = np.polyfit(np.log(N), np.log(g), 1)
    pred = np.polyval(coef, np.log(N))
    rmse_log = float(np.sqrt(np.mean((np.log(g) - pred) ** 2)))
    order = np.argsort(N)
    Ns, gs = N[order], g[order]
    local = [float((np.log(gs[i + 1]) - np.log(gs[i])) /
                   (np.log(Ns[i + 1]) - np.log(Ns[i])))
             for i in range(Ns.size - 1)]
    return {"beta": float(coef[0]), "rmse_log": rmse_log,
            "local_slopes": local, "n_points": int(N.size),
            "caveat": "few-point fit; summary feature, not a predictor"
            if N.size < 4 else None}


__all__ = [
    "canonical_spacings", "compute_family_I", "compute_family_II",
    "compute_family_III_from_rf", "brody_pdf", "matched_L",
    "VI1_L_iter_alpha", "VI2_N_scaling_beta",
    "FAMILY_I", "SMALL_PRIMES", "MIN_N_NNS", "MIN_N_FIT", "MIN_N_LONGRANGE",
]

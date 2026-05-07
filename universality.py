"""
Phase 3 — universality class statistics.

Given a sorted point process (e.g. lock-onset times pooled across PLLs and
unfolded so the pooled mean spacing is 1), compute the four statistics the
brief specifies and compare to the analytical forms for Poisson, GOE
(Wigner orthogonal), and GUE (Wigner unitary):

    1.  Nearest-neighbour spacing distribution (NNS)
    2.  Pair correlation function R₂(r)
    3.  Number variance Σ²(L)
    4.  Spectral form factor K(t)

Each function takes the event array and returns numerical values plus the
KS distance to the analytical references where applicable.
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass


# ── Analytical reference distributions ────────────────────────────────────────
def nns_poisson(s):
    return np.exp(-np.asarray(s, dtype=np.float64))


def nns_goe(s):
    s = np.asarray(s, dtype=np.float64)
    return (np.pi / 2.0) * s * np.exp(-np.pi * s * s / 4.0)


def nns_gue(s):
    s = np.asarray(s, dtype=np.float64)
    return (32.0 / np.pi**2) * s * s * np.exp(-4.0 * s * s / np.pi)


def nns_cdf_poisson(s):
    return 1.0 - np.exp(-np.asarray(s, dtype=np.float64))


def nns_cdf_goe(s):
    s = np.asarray(s, dtype=np.float64)
    return 1.0 - np.exp(-np.pi * s * s / 4.0)


def nns_cdf_gue(s):
    """CDF of P_GUE(s) = (32/π²)·s²·exp(-4s²/π).

    F(s) = ∫_0^s P(u) du.  Via integration:
        ∫ s² exp(-α s²) ds  with  α = 4/π
        = -(s/(2α)) exp(-α s²) + (1/(4α^(3/2))) sqrt(π) erf(s sqrt(α))
    Then multiply by the prefactor and clean up.

    Result (after simplification with α = 4/π):
        F(s) = erf(2s/√π) - (8s)/(π·exp(4s²/π))/(...)  — easier numerically:
    just integrate trapezoidally over a fine grid.  We use that here.
    """
    s = np.asarray(s, dtype=np.float64)
    out = np.zeros_like(s)
    grid = np.linspace(0, max(float(s.max()) if s.size else 1.0, 5.0), 4001)
    pdf = nns_gue(grid)
    cdf_grid = np.concatenate([[0.0], np.cumsum(0.5 * (pdf[:-1] + pdf[1:]) * np.diff(grid))])
    return np.interp(s, grid, cdf_grid)


# ── Statistic 1 — NNS ─────────────────────────────────────────────────────────
@dataclass
class NNSResult:
    spacings:   np.ndarray   # normalised (unit-mean) spacings
    ks_poisson: float
    ks_goe:     float
    ks_gue:     float
    p_poisson:  float
    p_goe:      float
    p_gue:      float
    best_fit:   str


def _ks_pvalue(ks, n):
    """Asymptotic Kolmogorov p-value."""
    if n < 2 or ks <= 0:
        return 1.0
    sn = np.sqrt(n)
    x = ks * (sn + 0.12 + 0.11 / sn)
    p = 0.0
    for k in range(1, 100):
        term = 2.0 * ((-1) ** (k - 1)) * np.exp(-2.0 * k * k * x * x)
        p += term
        if abs(term) < 1e-12:
            break
    return float(np.clip(p, 0.0, 1.0))


def compute_nns(events: np.ndarray) -> NNSResult:
    """
    Nearest-neighbour spacing distribution.  `events` should be already
    unfolded so the mean spacing is 1.  Returns the empirical spacings
    and KS distances to Poisson / GOE / GUE.
    """
    e = np.asarray(events, dtype=np.float64)
    if e.size < 5:
        return NNSResult(np.zeros(0), np.nan, np.nan, np.nan,
                          np.nan, np.nan, np.nan, 'insufficient')
    e = np.sort(e)
    s = np.diff(e)
    if s.size == 0 or s.mean() <= 0:
        return NNSResult(s, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 'empty')
    # Re-normalise to unit mean (in case events weren't already).
    s = s / s.mean()
    s_sorted = np.sort(s)
    n = s_sorted.size
    emp = np.arange(1, n + 1) / n

    ks_p = float(np.max(np.abs(emp - nns_cdf_poisson(s_sorted))))
    ks_o = float(np.max(np.abs(emp - nns_cdf_goe(s_sorted))))
    ks_u = float(np.max(np.abs(emp - nns_cdf_gue(s_sorted))))
    pp = _ks_pvalue(ks_p, n)
    po = _ks_pvalue(ks_o, n)
    pu = _ks_pvalue(ks_u, n)
    best = min([('poisson', ks_p), ('goe', ks_o), ('gue', ks_u)], key=lambda x: x[1])[0]
    return NNSResult(s, ks_p, ks_o, ks_u, pp, po, pu, best)


# ── Statistic 3 — Number variance Σ²(L) ───────────────────────────────────────
def number_variance(events: np.ndarray, L_max: float = 20.0,
                    n_L: int = 40, slide_step: float = 0.1) -> dict:
    """
    Σ²(L) = var(N(L)) computed by sliding a window of length L (in
    mean-spacing units) across the unfolded process.  Reference forms:
        Poisson:   Σ² = L
        GOE:       Σ² ≈ (1/π²) (log(2π L) + γ + 1)              for L≫1
        GUE:       Σ² ≈ (2/π²) (log(2π L) + γ + 1 − π²/8)       for L≫1
    Returns dict with L_vals, sigma2 (observed), and analytic forms.
    """
    e = np.sort(np.asarray(events, dtype=np.float64))
    if e.size < 50:
        return dict(L=np.zeros(0), sigma2=np.zeros(0),
                     poisson=np.zeros(0), goe=np.zeros(0), gue=np.zeros(0))
    L_vals = np.linspace(0.5, L_max, n_L)
    sigma2 = np.zeros_like(L_vals)
    span = float(e[-1] - e[0])
    for i, L in enumerate(L_vals):
        if L >= span:
            sigma2[i] = np.nan
            continue
        step = max(L * slide_step, 1.0)
        positions = np.arange(e[0], e[-1] - L, step)
        if positions.size < 5:
            sigma2[i] = np.nan
            continue
        counts = np.array([
            np.sum((e >= t0) & (e < t0 + L)) for t0 in positions
        ], dtype=np.float64)
        sigma2[i] = float(counts.var(ddof=1))
    GAMMA_EULER = 0.5772156649015329
    poiss_curve = L_vals.copy()
    # Use full RMT formulas (small-L regime omitted; valid for L≳1).
    log_term = np.log(np.maximum(2.0 * np.pi * L_vals, 1.0))
    goe_curve = (1.0 / (np.pi ** 2)) * (log_term + GAMMA_EULER + 1.0)
    gue_curve = (2.0 / (np.pi ** 2)) * (log_term + GAMMA_EULER + 1.0 - (np.pi ** 2) / 8.0)
    return dict(L=L_vals, sigma2=sigma2,
                  poisson=poiss_curve, goe=goe_curve, gue=gue_curve)


# ── Statistic 4 — Spectral form factor K(t) ───────────────────────────────────
def spectral_form_factor(events: np.ndarray, t_max: float = 5.0,
                          n_t: int = 100) -> dict:
    """
    K(t) = (1/N) |Σ_n exp(2πi t·x_n)|², where x_n are the unfolded events.
    Reference shapes:
        Poisson:  K(t) ≈ 1 (flat)
        GUE:      K(t) ≈ t for 0 < t < 1, K(t) ≈ 1 for t > 1 (ramp-plateau)
    """
    e = np.asarray(events, dtype=np.float64)
    if e.size < 10:
        return dict(t=np.zeros(0), K=np.zeros(0))
    t_vals = np.linspace(0.01, t_max, n_t)
    N = e.size
    K = np.zeros_like(t_vals)
    for i, t in enumerate(t_vals):
        z = np.exp(2j * np.pi * t * e)
        K[i] = float(np.abs(z.sum()) ** 2 / N)
    return dict(t=t_vals, K=K)


# ── Statistic 2 — pair correlation (kept simple) ──────────────────────────────
def pair_correlation(events: np.ndarray, r_max: float = 5.0,
                      n_bins: int = 30) -> dict:
    """
    R₂(r) — density of pairs at separation r (mean-spacing units).
    Computed as the histogram of pair separations divided by an expected
    constant for a Poisson reference.

    Analytic forms:
        Poisson: R₂(r) = 1
        GUE:     R₂(r) = 1 - (sin(π r) / (π r))²
        GOE:     R₂(r) = 1 - (sin(π r) / (π r))² - d/dr[Si(π r) sin(π r)/(π r)]
    """
    e = np.sort(np.asarray(events, dtype=np.float64))
    if e.size < 20:
        return dict(r=np.zeros(0), R2=np.zeros(0),
                     poisson=np.zeros(0), gue=np.zeros(0), goe=np.zeros(0))
    # All pair separations |e_j − e_k| / mean spacing (already unit-mean).
    n = e.size
    seps = []
    for i in range(n):
        # only i<j, separations ≤ r_max
        nbr = e[i + 1:i + 1 + 200]   # cap neighbours for speed
        d = nbr - e[i]
        d = d[d <= r_max]
        seps.append(d)
    seps = np.concatenate(seps) if seps else np.zeros(0)
    bins = np.linspace(0.0, r_max, n_bins + 1)
    h, _ = np.histogram(seps, bins=bins)
    centers = 0.5 * (bins[:-1] + bins[1:])
    bin_w = bins[1] - bins[0]
    # Expected for Poisson: number of pairs in bin = n * bin_w  (rate = 1)
    expected = float(n) * bin_w
    R2 = h / max(expected, 1e-12)
    sinc = np.where(centers > 0,
                    np.sin(np.pi * centers) / (np.pi * centers + 1e-12),
                    1.0)
    R2_gue = 1.0 - sinc ** 2
    return dict(r=centers, R2=R2, gue=R2_gue, poisson=np.ones_like(centers))

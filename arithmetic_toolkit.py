"""
arithmetic_toolkit.py — five analysis engines for any point-process t_k.

Each engine takes a sorted numpy array of event times and returns a dict.
`full_analysis(t_k, label)` runs all five plus the primary direct NNS and
returns a combined fingerprint.

Engines:
    1. ramanujan_fourier(t_k, q_max=200, normalize=True)
    2. padic_profile(t_k, primes=(2,3,5,7,11,13), q_max=8)
    3. fano_curve(t_k, n_scales=30, t_min_factor=2, t_max_factor=0.5)
    4. pair_correlation_full(t_k, r_max=10.0, n_bins=100)
    5. sb_directional_split(t_k, q_max=8, fc_ref=1.0)

The fingerprint vector returned by full_analysis is fixed-length:
    [KS_GUE, KS_GOE, KS_Poisson, mass<0.3,
     F(T=1), F(T=5), repulsion_integral,
     top_ramanujan_q, sb_symmetry_ks, padic_dominant_prime]
"""
from __future__ import annotations
import os, sys
from typing import Sequence
from math import gcd

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THIS_DIR)
from universality import (
    nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue,
    pair_correlation as _pair_correlation_universality,
    _ks_pvalue,
)
from pll_bank import farey_rationals


# ─── number-theoretic helpers ────────────────────────────────────────────────

def _factorize(n: int) -> list[tuple[int, int]]:
    out = []
    nn = n
    p = 2
    while p * p <= nn:
        if nn % p == 0:
            e = 0
            while nn % p == 0:
                nn //= p; e += 1
            out.append((p, e))
        p += 1
    if nn > 1:
        out.append((nn, 1))
    return out


def euler_phi(n: int) -> int:
    if n <= 1: return 1
    result = n
    for p, _ in _factorize(n):
        result = result // p * (p - 1)
    return result


def mobius(n: int) -> int:
    if n == 1: return 1
    cnt = 0
    for _, e in _factorize(n):
        if e > 1: return 0
        cnt += 1
    return -1 if cnt & 1 else 1


_phi_cache: dict[int, int] = {}
_mu_cache: dict[int, int] = {}


def _phi(n: int) -> int:
    if n not in _phi_cache:
        _phi_cache[n] = euler_phi(n)
    return _phi_cache[n]


def _mu(n: int) -> int:
    if n not in _mu_cache:
        _mu_cache[n] = mobius(n)
    return _mu_cache[n]


def ramanujan_sum_array(q: int, N: int) -> np.ndarray:
    """c_q(n) for n = 1..N via Hölder's identity:
        c_q(n) = μ(q/d) · φ(q) / φ(q/d)   where d = gcd(n, q)
    """
    n_arr = np.arange(1, N + 1)
    g = np.gcd(n_arr, q)
    out = np.zeros(N, dtype=np.float64)
    phi_q = _phi(q)
    for d in np.unique(g):
        d_int = int(d)
        m = q // d_int
        out[g == d_int] = _mu(m) * phi_q / _phi(m)
    return out


# ─── direct NNS classification (used inside engines) ─────────────────────────

def _classify(spacings: np.ndarray) -> dict:
    if spacings.size < 5:
        return dict(n=int(spacings.size), best='insufficient')
    s = np.sort(spacings); n = s.size
    F = np.arange(1, n + 1) / n
    ks_p = float(np.max(np.abs(F - nns_cdf_poisson(s))))
    ks_o = float(np.max(np.abs(F - nns_cdf_goe(s))))
    ks_u = float(np.max(np.abs(F - nns_cdf_gue(s))))
    best = min([('Poisson', ks_p), ('GOE', ks_o), ('GUE', ks_u)],
               key=lambda x: x[1])[0]
    return dict(n=n, ks_p=ks_p, ks_o=ks_o, ks_u=ks_u, gap=ks_o - ks_u,
                mass03=float((spacings < 0.3).mean()), best=best)


def _direct_nns(t_k: np.ndarray) -> dict:
    if t_k.size < 5: return dict(n=int(t_k.size), best='insufficient')
    sp = np.diff(np.sort(t_k))
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0:
        return dict(n=int(sp.size), best='insufficient')
    return _classify(sp / sp.mean())


# ─── Engine 1 — Ramanujan-Fourier spectrum ───────────────────────────────────

def ramanujan_fourier(t_k: np.ndarray, q_max: int = 200,
                      normalize: bool = True,
                      n_bins: int | None = None) -> dict:
    """
    Compute Ramanujan-Fourier coefficients a_q.

    normalize=True (default):
        f(n) = (t_k[n+1] - t_k[n]) / mean(intervals).  RF detects
        spacing-correlation patterns; insensitive to absolute period.
        a_q = (1/φ(q)) · E_n[f(n) · c_q(n)]

    normalize=False:
        f(n) = indicator function on uniform integer bins of the raw t_k.
        Specifically, f(n) = #{k : floor(t_k - t_min) == n} for
        n = 0..n_bins-1.  Detects integer-period structure of the
        original event times (e.g. weekly = 7, monthly = 30) when t_k is
        in days; defaults n_bins = int(t.max() - t.min()) + 1, i.e. 1 bin
        per t-unit.  Pass `n_bins` explicitly to control bin width.
    """
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    if t.size < 5:
        return dict(q_values=[], amplitudes=[], top10_q=[], peak_q=0,
                    error='insufficient (<5 events)', mode=('normalised' if normalize else 'indicator'))

    if normalize:
        intervals = np.diff(t)
        intervals = intervals[intervals > 0]
        if intervals.size < 5:
            return dict(q_values=[], amplitudes=[], top10_q=[], peak_q=0,
                        error='insufficient intervals', mode='normalised')
        intervals = intervals / intervals.mean()
        f = intervals
        N = intervals.size
        mode = 'normalised'
    else:
        if n_bins is None:
            n_bins = int(np.ceil(t.max() - t.min())) + 1
        if n_bins < 5:
            return dict(q_values=[], amplitudes=[], top10_q=[], peak_q=0,
                        error=f'n_bins={n_bins} < 5', mode='indicator')
        bin_idx = np.clip(np.floor(t - t.min()).astype(np.int64),
                          0, n_bins - 1)
        f = np.zeros(n_bins, dtype=np.float64)
        np.add.at(f, bin_idx, 1.0)
        N = n_bins
        mode = 'indicator'

    a = np.zeros(q_max, dtype=np.float64)
    for q in range(1, q_max + 1):
        c = ramanujan_sum_array(q, N)
        a[q - 1] = float(np.mean(f * c)) / _phi(q)

    abs_a = np.abs(a)
    # Rank q ≥ 2 by amplitude (q = 1 is the DC term, mean of intervals)
    if q_max >= 2:
        order = np.argsort(abs_a[1:])[::-1] + 2     # array of q values
        top10_q = order[:10].tolist()
        top10_amp = abs_a[np.array(top10_q) - 1].tolist()
        peak_q = int(top10_q[0])
    else:
        top10_q, top10_amp, peak_q = [1], [float(abs_a[0])], 1

    return dict(q_values=list(range(1, q_max + 1)),
                amplitudes=abs_a.tolist(),
                top10_q=top10_q, top10_amplitudes=top10_amp,
                peak_q=peak_q,
                a0=float(a[0]),
                mode=mode, n_bins=int(N) if not normalize else None)


# ─── Engine 2 — p-adic sensitivity profile ───────────────────────────────────

def _analytical_passage(t_k: np.ndarray, fc_ref: float, pq_pairs):
    """Pool normalised passage-time spacings across the given p:q PLL bands."""
    pooled = []
    info = []
    for p, q in pq_pairs:
        if q == 0: continue
        f_pll = fc_ref * p / q
        if f_pll <= 0: continue
        passage = np.sort(t_k * f_pll - 1.0)
        passage = passage[passage > 0]
        if passage.size < 5: continue
        sp = np.diff(passage)
        if sp.size == 0 or sp.mean() <= 0: continue
        pooled.append(sp / sp.mean())
        info.append((p, q, int(passage.size)))
    pooled_arr = np.concatenate(pooled) if pooled else np.zeros(0)
    return pooled_arr, info


def _is_p_power(q: int, p: int) -> bool:
    """True iff q == p^k for some k ≥ 1."""
    if q < p: return False
    while q > 1:
        if q % p != 0: return False
        q //= p
    return True


def padic_per_band(t_k: np.ndarray,
                    primes: Sequence[int] = (2, 3, 5, 7, 11, 13),
                    q_max: int = 64, fc_ref: float = 1.0) -> dict:
    """
    p-adic engine v3 — per-band Wigner-fit table on pure-p-power Farey
    rationals.

    For each prime p, enumerate the pure powers q_p ∈ {p, p², p³, …}
    with q_p ≤ q_max.  For each q_p, classify *every* Farey rational
    (a, q_p) individually (NOT pool them).  Aggregate by prime+q with
    median KS scores per (p, q) cell — this preserves the asymmetry
    that pooling washes out.

    The acceptance criterion: for Poisson + period-7 injection,
    median KS_GUE at (p=7, q=7) cell should be visibly elevated above
    the (p=2, q=2..64) cells that see only the Poisson background.

    Returns dict keyed by prime → list of per-q cells, each with:
        q, n_bands, median_ks_p, median_ks_o, median_ks_u, median_mass03,
        max_ks_u, median_n, bands (per-band detailed classifications)
    """
    t = np.asarray(t_k, dtype=np.float64)
    pairs = farey_rationals(q_max)
    by_q = {}                                 # q → list of (a, q) pairs
    for a, q in pairs:
        by_q.setdefault(q, []).append((a, q))

    table: dict[int, list[dict]] = {}
    for p in primes:
        per_q = []
        q_pow = p
        while q_pow <= q_max:
            bands = []
            for a, q in by_q.get(q_pow, []):
                f_pll = fc_ref * a / q
                if f_pll <= 0: continue
                passage = np.sort(t * f_pll - 1.0)
                passage = passage[passage > 0]
                if passage.size < 5: continue
                sp = np.diff(passage)
                if sp.size == 0 or sp.mean() <= 0: continue
                cl = _classify(sp / sp.mean())
                cl['a'] = int(a); cl['q'] = int(q)
                bands.append(cl)
            if bands:
                ks_p = np.array([b.get('ks_p', np.nan) for b in bands], dtype=np.float64)
                ks_o = np.array([b.get('ks_o', np.nan) for b in bands], dtype=np.float64)
                ks_u = np.array([b.get('ks_u', np.nan) for b in bands], dtype=np.float64)
                mass = np.array([b.get('mass03', np.nan) for b in bands], dtype=np.float64)
                n_arr = np.array([b.get('n', 0) for b in bands], dtype=np.int64)
                per_q.append(dict(
                    q=int(q_pow), n_bands=len(bands),
                    median_ks_p=float(np.nanmedian(ks_p)),
                    median_ks_o=float(np.nanmedian(ks_o)),
                    median_ks_u=float(np.nanmedian(ks_u)),
                    median_mass03=float(np.nanmedian(mass)),
                    max_ks_u=float(np.nanmax(ks_u)),
                    max_ks_p=float(np.nanmax(ks_p)),
                    median_n=int(np.median(n_arr)),
                    bands=bands,
                ))
            q_pow *= p
        if per_q:
            table[int(p)] = per_q
    return dict(per_band_table=table, q_max=q_max,
                filter_mode='pure_power_per_band')


def padic_amplitude_v4(t_k: np.ndarray,
                        primes: Sequence[int] = (2, 3, 5, 7, 11, 13),
                        q_max: int = 200,
                        n_bins: int | None = None) -> dict:
    """
    p-adic amplitude profile via Ramanujan-Fourier decomposition (v4).

    Reuses the validated v2 RF engine (normalize=False — indicator
    function on integer time bins of raw t_k) to compute |a_q| for
    q = 1..q_max.  For each prime p, sums |a_q| over q ∈ {p, p², p³, …}
    and normalises by total RF power (excluding the q = 1 DC term).

    Returns
    -------
    {
      'per_prime':       {p: {amplitude, normalised, q_powers}},
      'total_power':     float,
      'q_max':           int,
      'dominant_prime':  int     # arg-max of normalised amplitude
    }

    A peak at p means the signal has Ramanujan-Fourier power
    concentrated at q's that are pure powers of p — i.e., genuine
    p-adic resonance structure in the original event times.

    Side-steps the band-invariance pathology of v1-v3 by *not* pooling
    PLL passage NNS (which is invariant under linear time-scaling for
    stationary signals).  Detection happens entirely in the RF spectrum.
    """
    rf = ramanujan_fourier(t_k, q_max=q_max, normalize=False, n_bins=n_bins)
    amps = rf.get('amplitudes')
    if not amps:
        return dict(error='RF returned no spectrum',
                    per_prime={}, total_power=0.0, dominant_prime=0)
    amps = np.asarray(amps, dtype=np.float64)   # |a_q| for q = 1..q_max
    total_power = float(np.sum(amps[1:])) + 1e-12   # exclude DC

    # Mean RF amplitude across all q ≥ 2 — the "noise floor" reference.
    mean_amp_all = float(np.mean(amps[1:])) + 1e-12

    out: dict[int, dict] = {}
    dom_sum = (None, -1.0)
    dom_per_q = (None, -1.0)
    for p in primes:
        q_pows: list[int] = []
        q_pow = p
        while q_pow <= q_max:
            q_pows.append(q_pow); q_pow *= p
        if not q_pows:
            out[int(p)] = dict(amplitude=0.0, normalised=0.0,
                               normalised_per_q=0.0, q_powers=[])
            continue
        p_power = float(sum(amps[q - 1] for q in q_pows))
        mean_p = p_power / len(q_pows)
        normed_sum = p_power / total_power
        # Per-q normalisation — divides out the "more bands → bigger sum"
        # confound that biases v4-sum toward small primes (which have more
        # pure-power bands ≤ q_max).  Compares mean per-band amplitude to
        # the global mean noise floor.
        normed_per_q = mean_p / mean_amp_all
        out[int(p)] = dict(amplitude=p_power, normalised=normed_sum,
                           normalised_per_q=normed_per_q,
                           mean_amplitude=mean_p,
                           q_powers=q_pows)
        if normed_sum > dom_sum[1]:
            dom_sum = (int(p), normed_sum)
        if normed_per_q > dom_per_q[1]:
            dom_per_q = (int(p), normed_per_q)
    return dict(per_prime=out, total_power=total_power,
                mean_amplitude=mean_amp_all,
                q_max=q_max,
                rf_n_bins=rf.get('n_bins'),
                dominant_prime=int(dom_sum[0]) if dom_sum[0] is not None else 0,
                dominant_prime_per_q=int(dom_per_q[0]) if dom_per_q[0] is not None else 0)


def padic_profile(t_k: np.ndarray, primes: Sequence[int] = (2, 3, 5, 7, 11, 13),
                  q_max: int = 8, fc_ref: float = 1.0,
                  pure_power: bool = False) -> dict:
    """
    For each prime p, run analytical NNS on a subset of Farey rationals.

    pure_power=False (default, "p-adic-divisible" filter):
        subset = {(a, b) ∈ Farey(q_max) : p | b}
        Pools heavily overlap across primes (q=6 ∈ both p=2 and p=3 pools)
        — engine ties on most signals.

    pure_power=True ("pure-p-power" filter):
        subset = {(a, b) ∈ Farey(q_max) : b ∈ {p, p², p³, …}}
        Disjoint per-prime subsets → cleaner discrimination, but few
        bands when p is large (e.g. p=11 has only q=11 at q_max=16).
    """
    pairs = farey_rationals(q_max)
    out = {}
    best_by_prime = {}
    ks_min_overall = (None, 1.0)
    for p in primes:
        if pure_power:
            sub = [(a, b) for (a, b) in pairs if _is_p_power(b, p)]
        else:
            sub = [(a, b) for (a, b) in pairs if b % p == 0]
        if not sub:
            out[int(p)] = dict(n_pairs=0, classification=dict(best='insufficient'))
            continue
        pooled, info = _analytical_passage(np.asarray(t_k, dtype=np.float64),
                                            fc_ref, sub)
        cl = _classify(pooled)
        out[int(p)] = dict(n_pairs=len(sub), n_pooled=int(pooled.size),
                           classification=cl, q_values=sorted({b for _, b in sub}))
        ks_min = min(cl.get('ks_p', 1), cl.get('ks_o', 1), cl.get('ks_u', 1))
        best_by_prime[int(p)] = dict(best=cl.get('best', 'insufficient'),
                                     ks_min=ks_min)
        if ks_min < ks_min_overall[1]:
            ks_min_overall = (int(p), ks_min)
    dominant = ks_min_overall[0] if ks_min_overall[0] is not None else 0
    return dict(primes=list(primes), per_prime=out,
                best_by_prime=best_by_prime,
                dominant_prime=int(dominant),
                filter_mode='pure_power' if pure_power else 'p_divides_q')


# ─── Engine 3 — Multiscale Fano factor F(T) ──────────────────────────────────

def fano_curve(t_k: np.ndarray, n_scales: int = 30,
               t_min_factor: float = 2.0,
               t_max_factor: float = 0.5) -> dict:
    """
    F(T) = Var(N(T)) / Mean(N(T)) using non-overlapping windows of length T.
    T values logarithmically spaced over
        [t_min_factor·mean_spacing,  t_max_factor·total_duration].

    Reports F(T) at T = 1, 5, 20 (units of mean spacing) for the
    fingerprint vector.
    """
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    if t.size < 20:
        return dict(T=[], F=[], F_at_1=0.0, F_at_5=0.0, F_at_20=0.0,
                    error='insufficient')
    duration = float(t[-1] - t[0])
    intervals = np.diff(t)
    mean_sp = float(intervals.mean())
    if mean_sp <= 0 or duration <= 0:
        return dict(T=[], F=[], F_at_1=0.0, F_at_5=0.0, F_at_20=0.0,
                    error='degenerate')

    T_lo = t_min_factor * mean_sp
    T_hi = t_max_factor * duration
    if T_hi <= T_lo:
        return dict(T=[], F=[], F_at_1=0.0, F_at_5=0.0, F_at_20=0.0,
                    error='range')

    Ts = np.geomspace(T_lo, T_hi, n_scales)
    F = np.zeros_like(Ts)
    for i, T in enumerate(Ts):
        n_bins = int(duration // T)
        if n_bins < 5: F[i] = np.nan; continue
        edges = np.linspace(t[0], t[0] + n_bins * T, n_bins + 1)
        counts, _ = np.histogram(t, bins=edges)
        m = counts.mean()
        F[i] = (counts.var() / m) if m > 0 else np.nan

    # Sample F at T = 1, 5, 20 (units of mean spacing) — compute directly
    # using non-overlapping windows of length T_norm·mean_sp.
    def _F_at(T_norm):
        T_abs = T_norm * mean_sp
        if T_abs <= 0 or T_abs > duration:
            return float('nan')
        n_bins = int(duration // T_abs)
        if n_bins < 5: return float('nan')
        edges = np.linspace(t[0], t[0] + n_bins * T_abs, n_bins + 1)
        cnts, _ = np.histogram(t, bins=edges)
        m = cnts.mean()
        return float(cnts.var() / m) if m > 0 else float('nan')

    return dict(T=Ts.tolist(),
                T_in_mean_sp=(Ts / mean_sp).tolist(),
                F=F.tolist(),
                F_at_1=_F_at(1.0),
                F_at_5=_F_at(5.0),
                F_at_20=_F_at(20.0),
                mean_sp=mean_sp,
                duration=duration)


# ─── Engine 4 — Multiscale pair correlation R₂(r) ────────────────────────────

def pair_correlation_full(t_k: np.ndarray, r_max: float = 10.0,
                           n_bins: int = 100) -> dict:
    """
    R₂(r) using the unfolded spacings (assumes t_k has unit-mean spacing
    after np.diff; if not, R₂ is computed on the raw t_k anyway, which is
    standard since the bin width r is in the input units of t_k).

    Computes the repulsion integral
        I_rep = ∫₀¹ (1 − R₂(r)) dr
    a single number measuring total level repulsion (positive → repulsion,
    zero → Poisson, negative → clustering).
    """
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    if t.size < 20:
        return dict(r=[], R2=[], R2_GUE=[], repulsion_integral=0.0,
                    error='insufficient')
    res = _pair_correlation_universality(t, r_max=r_max, n_bins=n_bins)
    r = np.asarray(res['r'])
    R2 = np.asarray(res['R2'])
    sinc = np.where(r > 0, np.sin(np.pi * r) / (np.pi * r + 1e-12), 1.0)
    R2_gue = 1 - sinc ** 2
    # Repulsion integral over r ∈ [0, 1]
    mask = r <= 1.0
    I_rep = float(np.trapezoid(np.maximum(0, 1 - R2[mask]), r[mask])) \
            if mask.any() else 0.0
    return dict(r=r.tolist(), R2=R2.tolist(), R2_GUE=R2_gue.tolist(),
                repulsion_integral=I_rep,
                R2_at_0_1=float(R2[np.argmin(np.abs(r - 0.1))]) if r.size else 0,
                R2_at_0_5=float(R2[np.argmin(np.abs(r - 0.5))]) if r.size else 0,
                R2_at_1=float(R2[np.argmin(np.abs(r - 1.0))]) if r.size else 0)


# ─── Engine 5 — Stern-Brocot directional split ───────────────────────────────

def _ks_two(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    s1, s2 = np.sort(a), np.sort(b)
    n1, n2 = s1.size, s2.size
    if n1 < 5 or n2 < 5: return float('nan'), float('nan')
    pts = np.concatenate([s1, s2])
    cdf1 = np.searchsorted(s1, pts, side='right') / n1
    cdf2 = np.searchsorted(s2, pts, side='right') / n2
    ks = float(np.max(np.abs(cdf1 - cdf2)))
    p = float(_ks_pvalue(ks, int(n1 * n2 / (n1 + n2))))
    return ks, p


def sb_directional_split(t_k: np.ndarray, q_max: int = 8,
                         fc_ref: float = 1.0) -> dict:
    """
    Run the analytical-passage NNS separately on Farey rationals with
    p/q < 1 (Stern-Brocot left subtree) and p/q > 1 (right subtree),
    plus a two-sample KS between the two distributions to test
    sub/super-unison symmetry.
    """
    pairs = farey_rationals(q_max)
    left = [(p, q) for (p, q) in pairs if p < q]
    right = [(p, q) for (p, q) in pairs if p > q]
    t = np.asarray(t_k, dtype=np.float64)
    pool_l, _ = _analytical_passage(t, fc_ref, left)
    pool_r, _ = _analytical_passage(t, fc_ref, right)
    cl_l = _classify(pool_l)
    cl_r = _classify(pool_r)
    if pool_l.size >= 5 and pool_r.size >= 5:
        ks, p = _ks_two(pool_l, pool_r)
    else:
        ks, p = float('nan'), float('nan')
    return dict(left=cl_l, right=cl_r,
                n_left_pairs=len(left), n_right_pairs=len(right),
                symmetry_ks=ks, symmetry_p=p)


# ─── full_analysis — the combined fingerprint ────────────────────────────────

def full_analysis(t_k, label: str = '', fc_ref: float = 1.0,
                  q_max: int = 8, ramanujan_q_max: int = 200,
                  pair_r_max: float = 10.0,
                  pair_n_bins: int = 100,
                  rf_normalize: bool = True,
                  rf_n_bins: int | None = None,
                  padic_pure_power: bool = False) -> dict:
    """
    Run all five engines + a primary direct NNS classification, and
    pack into a fingerprint dict.

    Optional engine-redesign flags:
        rf_normalize=True   — RF on unit-mean-normalised intervals (default).
        rf_normalize=False  — RF on event-count indicator (period detection).
        padic_pure_power=False — Farey rationals with p | q (default).
        padic_pure_power=True  — Farey rationals with q ∈ {p, p², …}.

    Returns dict with keys:
        label, n_events,
        primary_nns, ramanujan, padic_profile,
        fano_curve, pair_correlation, sb_split,
        fingerprint_vector (10-dim).
    """
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    if t.size < 20:
        return dict(label=label, n_events=int(t.size),
                    error='insufficient (<20 events)')

    primary = _direct_nns(t)
    ram = ramanujan_fourier(t, q_max=ramanujan_q_max,
                             normalize=rf_normalize, n_bins=rf_n_bins)
    pad = padic_profile(t, q_max=q_max, fc_ref=fc_ref,
                         pure_power=padic_pure_power)
    fan = fano_curve(t)
    pc = pair_correlation_full(t, r_max=pair_r_max, n_bins=pair_n_bins)
    sbs = sb_directional_split(t, q_max=q_max, fc_ref=fc_ref)

    # Fingerprint vector — fixed length 10
    fp = [
        float(primary.get('ks_u', float('nan'))),
        float(primary.get('ks_o', float('nan'))),
        float(primary.get('ks_p', float('nan'))),
        float(primary.get('mass03', float('nan'))),
        float(fan.get('F_at_1', float('nan'))),
        float(fan.get('F_at_5', float('nan'))),
        float(pc.get('repulsion_integral', float('nan'))),
        float(ram.get('peak_q', 0)),
        float(sbs.get('symmetry_ks', float('nan'))),
        float(pad.get('dominant_prime', 0)),
    ]
    fp_keys = ['KS_GUE', 'KS_GOE', 'KS_Poisson', 'mass<0.3',
               'F(T=1)', 'F(T=5)', 'repulsion_integral',
               'top_ramanujan_q', 'sb_symmetry_ks',
               'padic_dominant_prime']

    return dict(label=label, n_events=int(t.size),
                primary_nns=primary, ramanujan=ram, padic_profile=pad,
                fano_curve=fan, pair_correlation=pc, sb_split=sbs,
                fingerprint_vector=fp, fingerprint_keys=fp_keys)


def joint_q_profile(t_k, q_max: int = 200, min_events_per_q: int = 30,
                    fc_ref: float = 1.0,
                    rf_n_bins: int | None = None):
    """
    Joint per-denominator profile combining the two q-indexed engines:

      - Ramanujan-Fourier amplitude `|a_q|` from the indicator-mode RF
        (ramanujan_fourier with normalize=False) — measures resonance
        strength at integer-period q in the raw event-time grid.
      - Per-q-band passage-time level statistics, pooled across all
        Farey rationals (a, q) with denominator q (a coprime to q).

    Each q yields one row of the returned DataFrame.  Bands with
    `n_events_q < min_events_per_q` are flagged via the `underpowered`
    column; downstream visualisation and aggregation should respect
    the flag.

    Pooling choice: events are pooled by *denominator q* (across all
    coprime numerators), matching the RF coefficient indexing.  A
    per-(p,q) breakdown is available via `padic_per_band`.

    Returns a pandas DataFrame with columns:
        q, rf_amplitude_q, rf_amplitude_q_normalized,
        n_events_q, ks_gue_q, ks_goe_q, ks_p_q, mass_lt_0_3_q,
        rep_int_q, F_T1_q, F_T5_q, n_pq_bands, underpowered
    """
    import pandas as pd
    t = np.sort(np.asarray(t_k, dtype=np.float64))

    # 1. RF amplitudes (indicator mode — period-detection on raw grid)
    rf = ramanujan_fourier(t, q_max=q_max, normalize=False, n_bins=rf_n_bins)
    rf_amps = np.abs(np.asarray(rf.get('amplitudes', []), dtype=np.float64))
    if rf_amps.size != q_max:
        rf_amps = np.full(q_max, np.nan)
    rf_total = float(np.sum(rf_amps[1:])) + 1e-12   # exclude DC
    rf_mean = rf_total / max(1, q_max - 1)

    # 2. Group Farey rationals by denominator
    pairs = farey_rationals(q_max)
    by_q: dict[int, list[int]] = {}
    for (a, q) in pairs:
        by_q.setdefault(q, []).append(a)

    rows = []
    for q in range(1, q_max + 1):
        a_list = by_q.get(q, [])
        # Pool unit-mean-normalised passage spacings across all
        # (a, q) with this denominator.
        pooled_sp_chunks = []
        n_events_q = 0
        for a in a_list:
            f_pll = fc_ref * a / q
            if f_pll <= 0: continue
            passage = np.sort(t * f_pll - 1.0)
            passage = passage[passage > 0]
            if passage.size < 2: continue
            sp = np.diff(passage)
            if sp.size and sp.mean() > 0:
                pooled_sp_chunks.append(sp / sp.mean())
                n_events_q += int(passage.size)
        pooled_sp = (np.concatenate(pooled_sp_chunks)
                      if pooled_sp_chunks else np.zeros(0))

        # Classification on pooled normalised spacings
        if pooled_sp.size >= 5:
            cl = _classify(pooled_sp)
        else:
            cl = dict(best='insufficient', ks_p=np.nan, ks_o=np.nan,
                       ks_u=np.nan, mass03=np.nan, n=int(pooled_sp.size))

        # F(T) and rep_int via a synthetic cumulative sequence built
        # from the pooled spacings (preserves spacing distribution
        # while giving fano_curve / pair_correlation a usable t array).
        if pooled_sp.size >= 50:
            t_synth = np.cumsum(pooled_sp)
            fan = fano_curve(t_synth)
            pc = pair_correlation_full(t_synth, r_max=5.0, n_bins=50)
            F1 = float(fan.get('F_at_1', np.nan))
            F5 = float(fan.get('F_at_5', np.nan))
            rep = float(pc.get('repulsion_integral', np.nan))
        else:
            F1 = F5 = np.nan
            rep = np.nan

        rf_amp_q = float(rf_amps[q - 1]) if q - 1 < rf_amps.size else np.nan
        rf_amp_q_normed = rf_amp_q / rf_mean if rf_mean > 0 else np.nan

        rows.append(dict(
            q=int(q),
            rf_amplitude_q=rf_amp_q,
            rf_amplitude_q_normalized=rf_amp_q_normed,
            n_events_q=int(n_events_q),
            ks_gue_q=float(cl.get('ks_u', np.nan)),
            ks_goe_q=float(cl.get('ks_o', np.nan)),
            ks_p_q=float(cl.get('ks_p', np.nan)),
            mass_lt_0_3_q=float(cl.get('mass03', np.nan)),
            rep_int_q=rep,
            F_T1_q=F1,
            F_T5_q=F5,
            n_pq_bands=len(a_list),
            underpowered=bool(n_events_q < min_events_per_q),
        ))

    return pd.DataFrame(rows)


def joint_quadrant_diagnostic(joint_df,
                              rep_int_low: float = 0.10,
                              rep_int_mid: float = 0.55,
                              rf_spike_factor: float = 5.0,
                              ks_gue_calibrator: float = 0.10):
    """Classify each q-band of a `joint_q_profile` DataFrame into a
    quadrant + supplementary-diagnostic label.

    Quadrant assignment (axes from Tier 2 calibrator scatter, Phase 15):

      BL   low rep_int (< rep_int_low) AND no RF spike   → Poisson noise
      TR   mid rep_int (rep_int_low..rep_int_mid) AND no RF spike  → Wigner-class
      BR   high rep_int (≥ rep_int_mid) AND no RF spike  → uniform-like;
           further classified BR_artifact vs BR_novel by Σ²(L) /
           ks-vs-n correlation diagnostics (see below)
      TL   RF spike at this q (|a_q| > rf_spike_factor × median(|a_q|))
           AND high rep_int                              → periodic at q

    Ambiguous: any row that doesn't satisfy a clean rule lands in
    `ambiguous`.

    BR sub-labelling.  Within BR (low RF, high rep_int):
      `BR_artifact`: KS_GUE_q ≥ ks_gue_calibrator AND
                     KS_GUE distribution roughly stable across n_events_q
                     (the toolkit's nearest-Wigner-form rule fitting a
                     non-Wigner shape — produces stable but non-clean KS).
      `BR_novel`:    KS_GUE_q < ks_gue_calibrator (the band actually fits
                     Wigner GUE well despite saturated rep_int — currently
                     not produced by any calibrator; reserved for genuine
                     surprises).

    Returns the input DataFrame extended with three new columns:
      `quadrant`, `rf_spike`, `quadrant_confidence`.

    The aggregate verdict (per-class quadrant occupancy fractions) is
    available by groupby downstream; this function operates per-row.
    """
    import pandas as pd
    df = joint_df.copy()

    # RF spike per row: |a_q| > rf_spike_factor × the median |a_q| at q ≥ 2
    rf_q2_plus = df.loc[df['q'] >= 2, 'rf_amplitude_q']
    rf_med = float(rf_q2_plus.median()) if len(rf_q2_plus) else 0.0
    df['rf_spike'] = (df['q'] >= 2) & (df['rf_amplitude_q'] > rf_spike_factor * rf_med)

    quadrants = []
    confidence = []
    for _, row in df.iterrows():
        rep = row.get('rep_int_q', np.nan)
        ks_u = row.get('ks_gue_q', np.nan)
        spike = bool(row['rf_spike'])
        underpwr = bool(row.get('underpowered', False))
        if np.isnan(rep) or underpwr:
            quadrants.append('ambiguous')
            confidence.append('underpowered' if underpwr else 'missing_data')
            continue
        if spike:
            if rep >= rep_int_low:
                quadrants.append('TL')
                confidence.append('clean')
            else:
                quadrants.append('ambiguous')
                confidence.append('rf_spike_low_rep_int')
            continue
        # No RF spike: classify by rep_int axis only
        if rep < rep_int_low:
            quadrants.append('BL')
            confidence.append('clean')
        elif rep < rep_int_mid:
            quadrants.append('TR')
            confidence.append('clean')
        else:
            # BR — distinguish artifact vs novel via KS_GUE quality
            if not np.isnan(ks_u) and ks_u < ks_gue_calibrator:
                quadrants.append('BR_novel')
                confidence.append('clean')
            else:
                quadrants.append('BR_artifact')
                confidence.append('clean')
    df['quadrant'] = quadrants
    df['quadrant_confidence'] = confidence
    return df


__all__ = ['ramanujan_fourier', 'padic_profile', 'padic_per_band',
           'padic_amplitude_v4',
           'fano_curve', 'pair_correlation_full', 'sb_directional_split',
           'full_analysis', 'joint_q_profile', 'joint_quadrant_diagnostic',
           'ramanujan_sum_array', 'euler_phi', 'mobius']

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
                      normalize: bool = True) -> dict:
    """
    Compute Ramanujan-Fourier coefficients a_q for the inter-event interval
    sequence f(n) = t_k[n+1] - t_k[n].

    a_q = (1/φ(q)) · (1/N) · Σ_n  f(n) · c_q(n)

    Returns the full spectrum (q = 1..q_max) and the top-10 resonance orders.
    """
    t = np.sort(np.asarray(t_k, dtype=np.float64))
    intervals = np.diff(t)
    intervals = intervals[intervals > 0]
    if intervals.size < 5:
        return dict(q_values=[], amplitudes=[], top10_q=[], peak_q=0,
                    error='insufficient intervals')
    if normalize:
        intervals = intervals / intervals.mean()
    N = intervals.size

    a = np.zeros(q_max, dtype=np.float64)
    for q in range(1, q_max + 1):
        c = ramanujan_sum_array(q, N)
        a[q - 1] = float(np.mean(intervals * c)) / _phi(q)

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
                a0=float(a[0]))


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


def padic_profile(t_k: np.ndarray, primes: Sequence[int] = (2, 3, 5, 7, 11, 13),
                  q_max: int = 8, fc_ref: float = 1.0) -> dict:
    """
    For each prime p, run analytical NNS using only Farey rationals whose
    denominator q has p | q (p-adic valuation ≥ 1).
    """
    pairs = farey_rationals(q_max)
    out = {}
    best_by_prime = {}
    ks_min_overall = (None, 1.0)
    for p in primes:
        sub = [(a, b) for (a, b) in pairs if b % p == 0]
        if not sub:
            out[int(p)] = dict(n_pairs=0, classification=dict(best='insufficient'))
            continue
        pooled, info = _analytical_passage(np.asarray(t_k, dtype=np.float64),
                                            fc_ref, sub)
        cl = _classify(pooled)
        out[int(p)] = dict(n_pairs=len(sub), n_pooled=int(pooled.size),
                           classification=cl)
        ks_min = min(cl.get('ks_p', 1), cl.get('ks_o', 1), cl.get('ks_u', 1))
        best_by_prime[int(p)] = dict(best=cl.get('best', 'insufficient'),
                                     ks_min=ks_min)
        if ks_min < ks_min_overall[1]:
            ks_min_overall = (int(p), ks_min)
    dominant = ks_min_overall[0] if ks_min_overall[0] is not None else 0
    return dict(primes=list(primes), per_prime=out,
                best_by_prime=best_by_prime,
                dominant_prime=int(dominant))


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
                  pair_n_bins: int = 100) -> dict:
    """
    Run all five engines + a primary direct NNS classification, and
    pack into a fingerprint dict.

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
    ram = ramanujan_fourier(t, q_max=ramanujan_q_max)
    pad = padic_profile(t, q_max=q_max, fc_ref=fc_ref)
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


__all__ = ['ramanujan_fourier', 'padic_profile', 'fano_curve',
           'pair_correlation_full', 'sb_directional_split',
           'full_analysis', 'ramanujan_sum_array',
           'euler_phi', 'mobius']

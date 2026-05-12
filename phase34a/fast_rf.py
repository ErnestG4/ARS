"""
phase34a/fast_rf.py — fast Ramanujan-Fourier + p-adic v4 for indicator-
mode analysis on integer event positions.

Bottleneck in the brief is the surrogate ensemble (≥1000 seeds × full
Q_MAX RF spectrum).  The reference implementation in
`arithmetic_toolkit.ramanujan_fourier(normalize=False)` materialises
the full n_bins-length indicator vector and c_q array per q, which is
~10^7 × 30 ≈ 3×10^8 ops per surrogate.

Optimisation here uses the fact that c_q(n) depends only on n mod q.
For an event-position list (sparse 0/1 indicator), the RF coefficient
reduces to a residue-class sum:

    a_q = (1 / (N · φ(q))) · Σ_{r=0..q-1}  c_q(r) · counts_q[r]

with `counts_q[r] = #{events ≡ r (mod q)}` and N = n_bins (the
indicator vector length used for normalisation, conventionally
ceil(t.max() - t.min()) + 1).

We validate parity with the reference engine in a unit test.

API:
    fast_rf_indicator(positions, q_max, n_bins=None) → np.ndarray (|a_q| for q=1..q_max)
    fast_padic_v4(positions, primes, q_max, n_bins=None) → dict
"""
from __future__ import annotations

import os
import sys
from typing import Sequence

import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, ROOT_DIR)

from arithmetic_toolkit import _phi, _mu      # cached φ / μ


def _ramanujan_residue_values(q: int) -> np.ndarray:
    """c_q(r) for r = 0, 1, ..., q-1 via Hölder's identity.

    For r = 0 use n = q (since gcd(q, q) = q ≡ gcd(0, q) by convention).
    """
    out = np.zeros(q, dtype=np.float64)
    phi_q = _phi(q)
    # gcd(r, q) for r=0..q-1: gcd(0, q) = q.
    g = np.gcd(np.arange(q, dtype=np.int64), q)
    g[0] = q
    for d in np.unique(g):
        d_int = int(d)
        m = q // d_int
        out[g == d_int] = _mu(m) * phi_q / _phi(m)
    return out


def fast_rf_indicator(positions: np.ndarray,
                       q_max: int,
                       n_bins: int | None = None) -> dict:
    """Compute |a_q| for q = 1..q_max via the residue-count trick.

    Matches `arithmetic_toolkit.ramanujan_fourier(positions, q_max,
    normalize=False, n_bins=n_bins)` to within float64 round-off, but
    in O((Σ_q q) + K·q_max) instead of O(N·q_max).

    Parameters
    ----------
    positions : integer event positions (sorted or unsorted; we copy).
    q_max     : max denominator.
    n_bins    : indicator vector length used for the mean.  Default
                = int(ceil(positions.max() - positions.min())) + 1, the
                reference convention.

    Returns
    -------
    {
      'amplitudes_signed' : np.ndarray (a_q for q=1..q_max, signed),
      'amplitudes'        : np.ndarray (|a_q|),
      'q_values'          : [1..q_max],
      'n_bins'            : int,
      'a0'                : float,
    }
    """
    pos = np.sort(np.asarray(positions, dtype=np.int64))
    if pos.size == 0:
        return dict(amplitudes=np.zeros(q_max), amplitudes_signed=np.zeros(q_max),
                     q_values=list(range(1, q_max + 1)), n_bins=0, a0=0.0,
                     error='empty positions')
    pmin = int(pos.min())
    pmax = int(pos.max())
    if n_bins is None:
        n_bins = int(np.ceil(pmax - pmin)) + 1
    # bin_idx[k] is the 0-based bin of event k; corresponds to n = bin_idx+1
    # in ramanujan_sum_array(q, N)'s 1-based indexing.
    bin_idx = (pos - pmin).astype(np.int64)
    if n_bins < 5:
        return dict(amplitudes=np.full(q_max, np.nan),
                     amplitudes_signed=np.full(q_max, np.nan),
                     q_values=list(range(1, q_max + 1)),
                     n_bins=int(n_bins), a0=float('nan'),
                     error=f'n_bins={n_bins} < 5')

    a_signed = np.zeros(q_max, dtype=np.float64)
    # n_arr index used inside ramanujan_sum_array is n=1..N, so bin index i
    # (0-based) maps to n = i + 1. Residue is (i+1) mod q.
    for q in range(1, q_max + 1):
        c_q = _ramanujan_residue_values(q)         # c_q at residue r=0..q-1
        residues = (bin_idx + 1) % q
        # Sum c_q(residue) over events: equivalent to Σ_r counts[r] c_q(r).
        # np.bincount is faster than direct lookup for repeated residues.
        if pos.size > 4 * q:
            counts = np.bincount(residues, minlength=q)
            s = float(np.dot(counts.astype(np.float64), c_q))
        else:
            s = float(np.sum(c_q[residues]))
        a_signed[q - 1] = s / (n_bins * _phi(q))

    return dict(
        amplitudes=np.abs(a_signed),
        amplitudes_signed=a_signed,
        q_values=list(range(1, q_max + 1)),
        n_bins=int(n_bins),
        a0=float(a_signed[0]),
    )


def fast_padic_v4(positions: np.ndarray,
                   primes: Sequence[int] = (2, 3, 5, 7, 11, 13),
                   q_max: int = 200,
                   n_bins: int | None = None) -> dict:
    """Replicate `padic_amplitude_v4` using `fast_rf_indicator`.

    Returns the same dict shape so it is drop-in compatible with
    downstream consumers expecting padic_amplitude_v4 output.
    """
    rf = fast_rf_indicator(positions, q_max=q_max, n_bins=n_bins)
    amps = rf['amplitudes']
    if amps.size == 0 or 'error' in rf:
        return dict(error=rf.get('error', 'empty'),
                     per_prime={}, total_power=0.0,
                     dominant_prime=0, dominant_prime_per_q=0,
                     q_max=int(q_max), rf_n_bins=int(rf.get('n_bins', 0)))
    total_power = float(np.sum(amps[1:])) + 1e-12
    mean_amp_all = float(np.mean(amps[1:])) + 1e-12

    out: dict = {}
    dom_sum = (None, -1.0)
    dom_per_q = (None, -1.0)
    for p in primes:
        q_pows = []
        q_pow = p
        while q_pow <= q_max:
            q_pows.append(int(q_pow))
            q_pow *= p
        if not q_pows:
            out[int(p)] = dict(amplitude=0.0, normalised=0.0,
                                normalised_per_q=0.0,
                                mean_amplitude=0.0, q_powers=[])
            continue
        p_power = float(sum(amps[q - 1] for q in q_pows))
        mean_p = p_power / len(q_pows)
        normed_sum = p_power / total_power
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
                 q_max=int(q_max), rf_n_bins=int(rf['n_bins']),
                 dominant_prime=int(dom_sum[0]) if dom_sum[0] is not None else 0,
                 dominant_prime_per_q=int(dom_per_q[0]) if dom_per_q[0] is not None else 0)


# ─── Parity test against arithmetic_toolkit reference ────────────────────────

def _parity_test():
    """Confirm fast_rf_indicator matches arithmetic_toolkit.ramanujan_fourier
    on a small case."""
    from arithmetic_toolkit import ramanujan_fourier
    rng = np.random.default_rng(0)
    pos = np.sort(rng.choice(np.arange(1, 1000), size=200, replace=False))
    Q = 30
    ref = ramanujan_fourier(pos.astype(np.float64), q_max=Q, normalize=False)
    ref_amps = np.asarray(ref['amplitudes'])
    fast = fast_rf_indicator(pos, q_max=Q)
    diff = np.max(np.abs(ref_amps - fast['amplitudes']))
    print(f"  parity max |Δ|a_q|| over q=1..{Q}: {diff:.2e}")
    print(f"  ref n_bins: {ref['n_bins']}  fast n_bins: {fast['n_bins']}")
    if diff < 1e-10:
        print("  ✓ fast_rf_indicator matches reference")
    else:
        # Locate biggest discrepancy
        bad_q = int(np.argmax(np.abs(ref_amps - fast['amplitudes']))) + 1
        print(f"  ✗ mismatch at q={bad_q}: ref={ref_amps[bad_q - 1]:.6e}, "
              f"fast={fast['amplitudes'][bad_q - 1]:.6e}")
    return diff < 1e-10


if __name__ == '__main__':
    print("=" * 60)
    print("Phase 34a fast_rf parity test against arithmetic_toolkit")
    print("=" * 60)
    ok = _parity_test()
    sys.exit(0 if ok else 1)

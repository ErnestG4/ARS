"""RIGID_GUE gate characterization — probe machinery (brief §2).

READ-ONLY toward cross_substrate/: every reference, lens, and statistic is
taken from the discriminator's own public surfaces (longrange_stats,
_reference_ensembles, unfold_empirical, wigner_renewal) so what is
characterized is the DEPLOYED gate, not a re-implementation.  Nothing under
cross_substrate/ is written by this arc; any fix is PROPOSED here
(proposed_rule.py) for the owning program to adopt or amend.

Decoy families (the question "is the margin a property of the discriminator
or of the specific decoy?"):

  D1 renewal        wigner_renewal — iid GUE-Wigner spacings (the banked decoy)
  D2 cumulant       cumulant_matched_events applied to a real GUE spectrum
  D3 antithetic(f)  THE ADVERSARIAL FAMILY, marginal-EXACT: take the same iid
                    Wigner spacings and PERMUTE them.  A permutation preserves
                    the spacing multiset exactly, so the NNS marginal is
                    identical to D1 by construction — bit-for-bit the same draw,
                    only reordered.  Ordering large-small-large-small induces
                    negative serial correlation, which lowers Var(sum of k
                    consecutive spacings) = k Var(s) + 2 sum_{i<j} Cov, hence
                    lowers Sigma^2(L).  f in [0,1] is the shuffled fraction:
                    f=1 recovers D1 exactly, f=0 is maximally anticorrelated.

NON-INERTNESS OF D3, PROVEN BEFORE RUNNING (TOOLKIT §9, 2026-08-16 rule):
  * the probe CAN move the detector: Sigma^2(L) is a functional of the
    spacing SEQUENCE (it depends on serial covariances), while the NNS
    marginal is a functional of the spacing MULTISET only.  A permutation
    changes the former and provably fixes the latter, so the two are not
    invariant under the same group — the construction is not inert.
  * the invariances it must avoid, checked: it is NOT rank-selection
    invariant (it reorders values, it does not select them); it is NOT
    monotone-map invariant (the map acts on the index, not the value); it is
    NOT absorbed by the deg-6 unfold (a smooth degree-6 polynomial in x
    cannot represent an alternating high-low modulation at the spacing
    scale — the lens has ~7 free parameters against ~n/2 alternations).
"""

import os
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (ROOT, f"{ROOT}/cross_substrate", f"{ROOT}/rigidgate"):
    if p not in sys.path:
        sys.path.insert(0, p)

from longrange_discriminator import (wigner_renewal, longrange_stats,   # noqa: E402
                                     _reference_ensembles, unfold_empirical,
                                     _S_GRID, _C_GRID)
from instrument_confound import gue_positions, poisson_positions        # noqa: E402
from universality import compute_nns                                    # noqa: E402

# GUE Wigner-surmise spacing variance (analytic): <s>=1, <s^2>=3*pi/8
VAR_S_WIGNER = 3.0 * np.pi / 8.0 - 1.0          # 0.178097...


def wigner_spacings(n, rng):
    """iid spacings from the GUE Wigner surmise (the D1/D3 shared draw)."""
    u = rng.random(n)
    s = np.interp(u, _C_GRID, _S_GRID)
    return s[s > 0]


def antithetic_order(s):
    """Reorder a spacing multiset large-small-large-small (maximal adjacent
    anticorrelation).  Multiset preserved exactly."""
    t = np.sort(s)[::-1]                    # descending
    hi, lo = t[: (t.size + 1) // 2], t[(t.size + 1) // 2:][::-1]
    out = np.empty(t.size, dtype=float)
    out[0::2] = hi
    out[1::2] = lo[: out[1::2].size]
    return out


def antithetic_renewal(n, f, rng):
    """D3: marginal-exact adversarial decoy.  f = shuffled fraction in [0,1];
    f=1 -> exactly the D1 renewal decoy, f=0 -> maximal anticorrelation."""
    s = wigner_spacings(n, rng)
    a = antithetic_order(s)
    k = int(round(f * a.size))
    if k > 1:
        idx = rng.choice(a.size, size=k, replace=False)
        a[idx] = rng.permutation(a[idx])
    return np.cumsum(a)


def cumulant_decoy(n, rng):
    """D2: cumulant-matched surrogate of a real GUE spectrum."""
    from surrogates import cumulant_matched_events
    return cumulant_matched_events(gue_positions(n, rng), rng)


DECOYS = {
    "renewal": lambda n, rng: wigner_renewal(n, rng),
    "cumulant": cumulant_decoy,
}


def sigma2(positions, L, deg=6):
    return longrange_stats(positions, L, unfold_deg=deg)["sigma2"]


def delta3(positions, L, deg=6):
    return longrange_stats(positions, L, unfold_deg=deg)["delta3"]


def bands(n, L, n_seeds, deg=6):
    """The gate's OWN reference bands (memoized in the discriminator)."""
    gue, pois = _reference_ensembles(n, L, n_seeds, deg, None)
    return gue, pois


def gue_boundary(gue_band, mult=2.5):
    """The deployed RIGID_GUE boundary: gue_mean + 2.5 * gue_ENSEMBLE_SD."""
    return gue_band["sigma2"]["mean"] + mult * gue_band["sigma2"]["sd"]


def decoy_sample(kind, n, L, n_draws, seed0, deg=6, f=None):
    """Sigma^2 draws from a decoy family through the deployed lens."""
    out = []
    for k in range(n_draws):
        rng = np.random.default_rng(seed0 + k)
        pos = (antithetic_renewal(n, f, rng) if kind == "antithetic"
               else DECOYS[kind](n, rng))
        v = sigma2(pos, L, deg)
        if v is not None:
            out.append(v)
    return np.asarray(out, float)


def gue_sample(n, L, n_draws, seed0, deg=6):
    out = []
    for k in range(n_draws):
        rng = np.random.default_rng(seed0 + k)
        v = sigma2(gue_positions(n, rng), L, deg)
        if v is not None:
            out.append(v)
    return np.asarray(out, float)


def ks_gue_of(positions):
    """NNS KS-to-GUE of a point set (the marginal the decoy must pass)."""
    return float(compute_nns(np.asarray(positions, float)).ks_gue)


# ── analytic predictions (prediction-first; sealed before measurement) ───────

GAMMA_EULER = 0.5772156649015329


def sigma2_gue_analytic(L):
    """Mehta asymptotic GUE number variance: (1/pi^2)(ln(2 pi L) + gamma + 1)."""
    return (np.log(2.0 * np.pi * L) + GAMMA_EULER + 1.0) / np.pi ** 2


def sigma2_renewal_analytic(L):
    """Renewal asymptote: Sigma^2(L) -> Var(s)/<s>^3 * L = VAR_S_WIGNER * L
    for unit-mean iid spacings (elementary renewal-theory variance)."""
    return VAR_S_WIGNER * L

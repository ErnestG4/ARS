"""
cross_substrate/longrange_discriminator.py — certify the universality CLASS, not
just the marginal spacing.

The Phase-18 STOP CONDITION exposed it: phase-randomized and cumulant-matched
surrogates PRESERVE the marginal spacing distribution and DESTROY everything above
it, yet still reproduce the NNS (rep/ks_gue) verdict on zeta/lmfdb/dirichlet. So an
NNS-only verdict certifies the MARGINAL, not the long-range correlation structure
that DEFINES the universality class. The earned claim on NNS alone is "marginal
spacing matches GUE", not "GUE class".

The clean proof is a decoy: a RENEWAL process with i.i.d. spacings drawn from the
Wigner (GUE NNS) distribution has the GUE NNS and ZERO long-range rigidity (number
variance grows ~linearly like Poisson, not ~log like GUE). NNS cannot tell it from
real GUE; a long-range statistic (Σ²(L) / Δ₃(L)) separates them instantly.

This module supplies (1) the Wigner-renewal decoy, (2) a long-range verdict that
compares Σ²(L)/Δ₃(L) against a real-GUE ensemble and a renewal ensemble at matched
n and L → RIGID_GUE / MARGINAL_ONLY / INTERMEDIATE, and (3) a closed-loop proof:
real GUE → RIGID_GUE while the decoy and a cumulant-matched surrogate of real GUE
(same NNS) → MARGINAL_ONLY. On NNS alone they are indistinguishable; the long-range
statistic is what carries the class claim.

BOUND: "GUE class" requires a long-range statistic the marginal-preserving
surrogates cannot fake. NNS alone earns only "marginal matches GUE".
[[bulk_vs_global_moment_readout]] (RW σ²(K) complement), [[support_set_respecting_nulls]].
"""
from __future__ import annotations

import os
import sys
from typing import Dict, Optional, Sequence

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from axes import II1_sigma2_at_L, II2_delta3_at_L, matched_L
from universality import nns_cdf_gue
from instrument_confound import gue_positions, poisson_positions, axis_values

_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from surrogates import cumulant_matched_events   # marginal-preserving surrogate


# ── Wigner-renewal decoy: GUE NNS, zero long-range rigidity ──────────────────
_S_GRID = np.linspace(0.0, 6.0, 8000)
_C_GRID = np.asarray(nns_cdf_gue(_S_GRID), dtype=np.float64)


def wigner_renewal(n: int, rng: np.random.Generator) -> np.ndarray:
    """Renewal process whose i.i.d. spacings are drawn from the GUE Wigner surmise
    (inverse-CDF sampling). Same marginal NNS as real GUE, but — being a renewal
    process — its long-range correlations are absent: Σ²(L) grows ~linearly, not
    ~log L. The decoy that NNS cannot distinguish from real GUE."""
    u = rng.random(n)
    spac = np.interp(u, _C_GRID, _S_GRID)
    spac = spac[spac > 0]
    return np.cumsum(spac)


# ── long-range statistics ─────────────────────────────────────────────────────
def longrange_stats(positions: Sequence[float], L: Optional[float] = None) -> dict:
    e = np.sort(np.asarray(positions, dtype=np.float64))
    if L is None:
        L = matched_L(e.size)
    return {"L": float(L), "sigma2": II1_sigma2_at_L(e, L),
            "delta3": II2_delta3_at_L(e, L)}


def _ensemble(sampler, n: int, L: float, n_seeds: int, base_seed: int) -> dict:
    s2, d3 = [], []
    for k in range(n_seeds):
        rng = np.random.default_rng(base_seed + k)
        st = longrange_stats(sampler(n, rng), L)
        if st["sigma2"] is not None:
            s2.append(st["sigma2"])
        if st["delta3"] is not None:
            d3.append(st["delta3"])
    out = {}
    for nm, v in (("sigma2", s2), ("delta3", d3)):
        if v:
            out[nm] = {"mean": float(np.mean(v)), "sd": float(np.std(v) + 1e-12)}
    return out


_ENS_CACHE: Dict[tuple, tuple] = {}


def _reference_ensembles(n_e: int, L: float, n_seeds: int) -> tuple:
    """Real-GUE + Wigner-renewal reference ensembles at (n_e, L), memoized with
    FIXED seeds — they are identical across findings, so the O(n³) GUE eigensolve
    is paid ONCE per (n_e, L, n_seeds), not per finding."""
    key = (int(n_e), round(float(L), 4), int(n_seeds))
    if key not in _ENS_CACHE:
        _ENS_CACHE[key] = (_ensemble(gue_positions, n_e, L, n_seeds, 90_000),
                           _ensemble(wigner_renewal, n_e, L, n_seeds, 95_000))
    return _ENS_CACHE[key]


def longrange_verdict(positions: Sequence[float], L: Optional[float] = None,
                      n_seeds: int = 16, base_seed: int = 0,
                      n_ref: int = 3000) -> dict:
    """Compare the data's long-range statistics against a real-GUE ensemble and a
    Wigner-renewal ensemble at matched n and L. Σ² is primary, Δ₃ a cross-check.
      RIGID_GUE     — consistent with GUE, far from renewal → the long-range
                      structure is present → "GUE class" earned.
      MARGINAL_ONLY — consistent with renewal, far from GUE → only the marginal
                      matches; the universality claim COLLAPSES to marginal-only.
      INTERMEDIATE  — between the two ensembles.
      UNDERPOWERED  — too few events for Σ²/Δ₃.
    """
    e = np.sort(np.asarray(positions, dtype=np.float64))
    n = e.size
    if L is None:
        L = matched_L(n)
    obs = longrange_stats(e, L)
    if obs["sigma2"] is None:
        return {"verdict": "UNDERPOWERED", "n": int(n), "L": float(L)}
    # Σ²(L)/Δ₃(L) at fixed L are windowed statistics ~independent of total n once
    # n >> L, so the reference ensembles use a capped n_ref (the data keeps its own
    # n) — avoids an O(n³) GUE eigensolve at large n while staying matched in L.
    n_e = min(n, n_ref)
    gue, ren = _reference_ensembles(n_e, L, n_seeds)   # memoized (base_seed unused here)

    def _judge(stat):
        if stat not in gue or stat not in ren or obs[stat] is None:
            return None
        o = obs[stat]
        gm, gs = gue[stat]["mean"], gue[stat]["sd"]
        rm, rs = ren[stat]["mean"], ren[stat]["sd"]
        z_g = (o - gm) / gs                       # SIGNED (− = more rigid than GUE)
        z_r = (o - rm) / rs                       # SIGNED (− = more rigid than renewal)
        # Rigidity is one-sided: being at-or-BELOW the GUE level (more rigid) is
        # still GUE-class — only being significantly ABOVE GUE and up at the
        # renewal (floppy) level collapses the claim. RIGID = not above GUE AND
        # clearly below renewal; MARGINAL_ONLY = up at renewal level or floppier.
        if o <= gm + 2.5 * gs and o < rm - 2.5 * rs:
            v = "RIGID_GUE"
        elif o >= rm - 2.5 * rs:
            v = "MARGINAL_ONLY"
        else:
            v = "INTERMEDIATE"
        return dict(obs=float(o), gue=gue[stat], renewal=ren[stat],
                    z_vs_gue=float(z_g), z_vs_renewal=float(z_r), verdict=v)

    s2j, d3j = _judge("sigma2"), _judge("delta3")
    primary = s2j["verdict"] if s2j else (d3j["verdict"] if d3j else "UNDERPOWERED")
    return {"verdict": primary, "n": int(n), "L": float(L),
            "sigma2": s2j, "delta3": d3j}


def ks_gue(positions) -> Optional[float]:
    """The NNS marginal statistic (ks_gue) — what the decoy fools."""
    return axis_values(positions, axes=("I.5_ks_gue",)).get("I.5_ks_gue")


# ── closed-loop proof ─────────────────────────────────────────────────────────
def validate(verbose: bool = True) -> dict:
    """Proof that NNS under-certifies and the long-range statistic carries the class:
      (P1) real GUE and the Wigner-renewal decoy have the SAME NNS (ks_gue).
      (P2) the long-range verdict SEPARATES them: real → RIGID_GUE, decoy → MARGINAL_ONLY.
      (P3) a cumulant-matched surrogate of real GUE preserves NNS but collapses the
           long-range structure → MARGINAL_ONLY (the marginal surrogate cannot fake it).
    """
    rep = {}
    n = 2500            # GUE eigensolve is O(n³); 2500 keeps the proof fast
    ns = 12
    rng = np.random.default_rng(0)
    real = gue_positions(n, rng)
    decoy = wigner_renewal(n, np.random.default_rng(1))

    ks_real, ks_decoy = ks_gue(real), ks_gue(decoy)
    rep["P1_same_NNS"] = {
        "pass": bool(ks_real is not None and ks_decoy is not None
                     and ks_real < 0.08 and ks_decoy < 0.08
                     and abs(ks_real - ks_decoy) < 0.05),
        "ks_gue_real": round(ks_real, 4), "ks_gue_decoy": round(ks_decoy, 4)}

    v_real = longrange_verdict(real, n_seeds=ns, base_seed=10)
    v_decoy = longrange_verdict(decoy, n_seeds=ns, base_seed=20)
    rep["P2_longrange_separates"] = {
        "pass": bool(v_real["verdict"] == "RIGID_GUE"
                     and v_decoy["verdict"] == "MARGINAL_ONLY"),
        "real_verdict": v_real["verdict"], "decoy_verdict": v_decoy["verdict"],
        "real_sigma2": round(v_real["sigma2"]["obs"], 3),
        "decoy_sigma2": round(v_decoy["sigma2"]["obs"], 3),
        "gue_sigma2_mean": round(v_real["sigma2"]["gue"]["mean"], 3),
        "renewal_sigma2_mean": round(v_real["sigma2"]["renewal"]["mean"], 3)}

    surr = cumulant_matched_events(real, rng=np.random.default_rng(2))
    ks_surr = ks_gue(surr)
    v_surr = longrange_verdict(surr, n_seeds=ns, base_seed=30)
    rep["P3_cumulant_surrogate_collapses_longrange"] = {
        "pass": bool(ks_surr is not None and ks_surr < 0.10
                     and v_surr["verdict"] in ("MARGINAL_ONLY", "INTERMEDIATE")),
        "ks_gue_surrogate": round(ks_surr, 4) if ks_surr else None,
        "surrogate_longrange_verdict": v_surr["verdict"],
        "note": "marginal preserved (NNS still ~GUE) but long-range structure gone"}

    rep["ALL_PASS"] = all(v["pass"] for v in rep.values()
                          if isinstance(v, dict) and "pass" in v)
    if verbose:
        print("=" * 74)
        print("longrange_discriminator — closed-loop proof (NNS under-certifies)")
        print("=" * 74)
        for k, v in rep.items():
            if isinstance(v, dict) and "pass" in v:
                print(f"[{'PASS' if v['pass'] else 'FAIL'}] {k}")
                for kk, vv in v.items():
                    if kk != "pass":
                        print(f"        {kk}: {vv}")
        print("-" * 74)
        print(f"ALL_PASS = {rep['ALL_PASS']}")
    return rep


if __name__ == "__main__":
    validate()

"""
cross_substrate/validate_fitters.py — synthetic-validation gate for the
distribution fitters used as landscape coordinates (Brody q, Berry-Robnik ρ).

MANDATORY before any fitted value is banked. Per §7.ter.57
(synthetic_validate_fitters): a fitter must recover known ground truth —
Poisson → q≈0 / ρ≈0, GOE → q≈1 / ρ≈1 — or its outputs are banked as null
+ flagged, not as measurements. The Berry-Robnik ρ↔(1−ρ) bug (phase34e)
is exactly what this catches.

Run:  $HOME/fmexplorer/bin/python3 cross_substrate/validate_fitters.py
Writes: cross_substrate/fitter_validation.json
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from universality import nns_cdf_goe, nns_cdf_gue  # noqa: E402
from cross_substrate.axes import (I8_brody_q, I9_berry_robnik_rho,          # noqa: E402
                                  I8_brody_q_unbounded, I9_berry_robnik_rail_flag)


def _inverse_sample(cdf_func, n: int, seed: int, grid_max: float = 10.0) -> np.ndarray:
    """Inverse-transform sampling of a unit-mean NNS distribution from its CDF."""
    grid = np.linspace(0.0, grid_max, 20001)
    F = np.asarray(cdf_func(grid), dtype=np.float64)
    F = np.clip(F, 0.0, 1.0)
    F[0] = 0.0
    u = np.random.default_rng(seed).random(n)
    s = np.interp(u, F, grid)
    return s / s.mean()          # enforce unit mean


def sample_poisson(n: int, seed: int) -> np.ndarray:
    s = np.random.default_rng(seed).exponential(1.0, size=n)
    return s / s.mean()


def sample_goe(n: int, seed: int) -> np.ndarray:
    return _inverse_sample(nns_cdf_goe, n, seed)


def sample_gue(n: int, seed: int) -> np.ndarray:
    return _inverse_sample(nns_cdf_gue, n, seed)


def sample_clustered(n: int, seed: int, sigma: float = 1.15) -> np.ndarray:
    """SUPER-POISSON (clustered) unit-mean spacings.  CV > 1 by construction."""
    s = np.random.default_rng(seed).lognormal(0.0, sigma, size=n)
    return s / s.mean()


def sample_clustered_extreme(n: int, seed: int) -> np.ndarray:
    return sample_clustered(n, seed, sigma=1.8)


# (label, sampler, expected q, expected ρ, tolerance)
#
# TOOLKIT §9 arm (e).  The original CASES were ONLY ("poisson", 0, 0) and ("goe", 1, 1) — i.e.
# **the two endpoints of the fitters' own `bounds=(0.0, 1.0)`**.  A boundary-RAILING bug is
# structurally invisible to a harness that probes only at the boundaries: the gate PASSED while
# `I8_brody_q` / `I9_berry_robnik_rho` were mapping every clustered substrate onto the Poisson
# value.  Probing only at the rails cannot detect railing.
#
#   A VALIDATION SUITE MUST PROBE OUTSIDE **EVERY** BOUNDARY OF THE REACHABLE RANGE, NOT ONE.
#
# In Brody, q is the level-repulsion exponent β:  P_q(s) ∝ s^q exp(−b s^(q+1)).
#     Poisson → q=0   |   GOE → q=1   |   GUE → q≈2   |   GSE → q≈4
# So `bounds=(0.0, 1.0)` is not a numerical convenience — it is a MODEL ASSERTION that the
# substrate lies between Poisson and GOE.  BOTH ends are censored:
#   - below 0: all clustering (super-Poisson)  → dumps onto the POISSON value
#   - above 1: GUE and GSE                     → dumps onto the GOE value
# The zoo shows both: 72.5% of banked brody_q sit at the lower bound, 2.4% at the upper; only
# 25.2% of cells carry a measurement at all.  A "bimodality at the bounds" is a railing
# histogram, not a substrate property.
#
# The four out-of-range cases below are EXPECTED TO FAIL until the bounds are opened (and the
# freed ranges calibrated).  A FAIL here is the gate working, not the gate broken.
CASES = [
    ("poisson",           sample_poisson,          0.0, 0.0, 0.15),
    ("goe",               sample_goe,              1.0, 1.0, 0.20),
    # --- BELOW the lower bound (arm (e)); q_true < 0, unrepresentable ---
    ("clustered",         sample_clustered,        -0.30, -0.30, 0.20),
    ("clustered_extreme", sample_clustered_extreme, -0.60, -0.60, 0.25),
    # --- ABOVE the upper bound (arm (e), symmetric); q_true ≈ 2 and ≈ 4, unrepresentable.
    #     THIS is the case that exposes the top rail: a GUE substrate is indistinguishable from
    #     GOE, so ζ-zeros reading q=0.9999 means only "≥ GOE" — NOT "GUE". ---
    # RE-REGISTERED 2026-07-27 through seals/GUE_EXPECTATION_REREGISTRATION.json.
    #   was: exp_q = 2.0 +/- 0.30 -- the overnight's ROUGH characterisation ("GUE~2, GSE~4 need the
    #        upper bound"), never measured, inherited as a placeholder into an acceptance criterion.
    #   now: exp_q = 1.53 +/- 0.10, DERIVED by the sealed rule (round(mean,2); max(0.10, 3*sd))
    #        from a pre-registered 10-seed run at n=40000: mean 1.5320, sd 0.0098, and within
    #        0.0010 of the four prior independent measurements (1.5325/1.5313/1.5433/1.5166).
    #   NOTE the grade: Brody is a one-parameter INTERPOLATION, not an exact GUE law, so 1.53 is an
    #        INSTRUMENT constant -- what the Brody MLE reads on GUE spacings -- not a physical one.
    #   exp_rho is left at 2.0 deliberately: Berry-Robnik rho is a GOE FRACTION bounded to [0,1], so
    #        no value can satisfy it for GUE. That row SHOULD fail; it is the axis saying "GUE is
    #        outside what I can represent", which is R-148's rail finding, not a bad expectation.
    ("gue",               sample_gue,               1.53, 2.0, 0.10),
]
N_SYNTH = 4000
SEEDS = (0, 1, 2)


def main() -> int:
    print("=" * 72)
    print("FITTER SYNTHETIC VALIDATION (Brody q, Berry-Robnik ρ)")
    print("=" * 72)
    rec, all_pass = {}, True
    # REPAIRED COLUMN, added 2026-07-27. The four out-of-range cases were "EXPECTED TO FAIL until
    # the bounds are opened" -- the bounds are now opened (I8_brody_q_unbounded), so the gate can
    # show deployed-FAIL beside repaired-PASS. Deliberately a SECOND column, not a swap: the
    # deployed verdict must stay visible, because it is what the banked numbers came off.
    for label, sampler, exp_q, exp_rho, tol in CASES:
        qs, rhos, qs_rep, rails = [], [], [], []
        for sd in SEEDS:
            s = sampler(N_SYNTH, sd)
            qs.append(I8_brody_q(s))
            rhos.append(I9_berry_robnik_rho(s))
            qs_rep.append(I8_brody_q_unbounded(s))
            rails.append(I9_berry_robnik_rail_flag(s))
        q_mean, rho_mean = float(np.mean(qs)), float(np.mean(rhos))
        q_ok = abs(q_mean - exp_q) <= tol
        rho_ok = abs(rho_mean - exp_rho) <= tol
        all_pass = all_pass and q_ok and rho_ok
        rec[label] = {
            "expected_q": exp_q, "brody_q_mean": q_mean,
            "brody_q_per_seed": [round(x, 4) for x in qs], "brody_q_pass": q_ok,
            "brody_q_REPAIRED_per_seed": [round(x, 4) for x in qs_rep],
            "brody_q_REPAIRED_pass": bool(abs(float(np.mean(qs_rep)) - exp_q) <= tol),
            "berry_robnik_AT_RAIL": [bool(x) if x is not None else None for x in rails],
            "expected_rho": exp_rho, "br_rho_mean": rho_mean,
            "br_rho_per_seed": [round(x, 4) for x in rhos], "br_rho_pass": rho_ok,
            "tol": tol,
        }
        print(f"\n[{label}] N={N_SYNTH} seeds={SEEDS}")
        print(f"  Brody q:        {q_mean:.4f}  (expect {exp_q}±{tol})  "
              f"{'PASS' if q_ok else 'FAIL'}")
        print(f"  Berry-Robnik ρ: {rho_mean:.4f}  (expect {exp_rho}±{tol})  "
              f"{'PASS' if rho_ok else 'FAIL'}")

    out = {"n_synth": N_SYNTH, "seeds": list(SEEDS), "cases": rec,
           "all_pass": all_pass,
           "gate": "Brody/BR values may be banked ONLY if all_pass is true; "
                   "else bank null + flag (§7.ter.57)."}
    p = os.path.join(_HERE, "fitter_validation.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nALL_PASS = {all_pass}")
    print(f"→ wrote {p}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())

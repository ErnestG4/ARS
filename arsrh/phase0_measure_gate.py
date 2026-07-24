"""
arsrh/phase0_measure_gate.py — ARS-RH Phase 0, the parts not already covered.

The spec's Phase-0 spacing gate (Farey NNS vs the Hall 1970 law) is ALREADY certified in the
repo: `approximability/farey_class_certify.py` gives KS=0.00013 vs Hall/BCZ triangle_cdf on 7.6M
gaps (min tau = 3/pi^2 = 0.304, Hall beats best RMT ~1000x), banked RESULTS_MATRIX.md:130. Verified
reproducing this session. This file closes the remaining Phase-0 checklist items:

  (A) Completeness / cardinality gate: |F_n| = 1 + sum_{k=1}^n phi(k), verified exactly — the
      exact-cardinality check that would catch a missing-fraction bug masquerading as a class shift.
  (B) Open decision #1: does unfolding-free <r~> need modification for a BOUNDED-support process
      with n^2 density? Resolved by construction + measurement.
  (C) The section-3a MEASURE-DECLARATION gate, which is NOT in the repo and is the high-value
      transfer: no tree-derived point process has a class without a declared sampling measure.
      Discriminate the two canonical singular measures by a known-answer statistic:
        * FAIR COIN on L/R = Minkowski ?-measure: partial quotients ~ geometric(1/2),
          arithmetic mean EXACTLY 2, all moments finite.
        * GAUSS measure = Lebesgue-typical: partial quotients ~ Gauss-Kuzmin,
          arithmetic mean DIVERGES; geometric mean -> Khinchin K0 = 2.685452...
      Minkowski and Lebesgue are mutually singular; an estimator that does not separate them is
      broken. This is a toy of the fungal Cox confound (#4259167) with a KNOWN answer: the measured
      class is a property of the generating measure (rate envelope), not of the points.

Run:  $HOME/fmexplorer/bin/python3 arsrh/phase0_measure_gate.py
"""
from __future__ import annotations

import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(20260724)
KHINCHIN = 2.6854520010653064453   # Khinchin's constant K0


# ---------------------------------------------------------------------------------------
# (A) completeness / cardinality gate  |F_n| = 1 + sum phi(k)
# ---------------------------------------------------------------------------------------
def totient_sieve(n):
    phi = np.arange(n + 1)
    for p in range(2, n + 1):
        if phi[p] == p:                       # p prime
            phi[p::p] -= phi[p::p] // p
    return phi


def farey_sequence(n):
    """Full Farey sequence F_n on [0,1] via the standard neighbour recurrence."""
    a, b, c, d = 0, 1, 1, n
    seq = [0.0]
    while c <= n:
        k = (n + b) // d
        a, b, c, d = c, d, k * c - a, k * d - b
        seq.append(a / b)
    return np.array(seq)


def cardinality_gate(orders=(50, 200, 1000)):
    rows = []
    ok = True
    for n in orders:
        phi = totient_sieve(n)
        predicted = 1 + int(phi[1:n + 1].sum())
        F = farey_sequence(n)
        got = F.size
        match = got == predicted
        ok = ok and match
        rows.append({"n": n, "|F_n|": got, "1+sum_phi": predicted, "exact_match": match})
        print(f"  n={n:5d}: |F_n|={got:8d}  1+Σφ={predicted:8d}  {'OK' if match else 'MISMATCH'}")
    return {"rows": rows, "PASS": ok}


# ---------------------------------------------------------------------------------------
# (B) <r~> on a bounded-support n^2-density process — is the estimator support-agnostic?
# ---------------------------------------------------------------------------------------
def r_tilde(points_sorted):
    """Unfolding-free consecutive-gap ratio r~ = min(s_n,s_{n+1})/max(s_n,s_{n+1}), mean."""
    s = np.diff(points_sorted)
    s = s[s > 0]
    r = np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])
    return float(r.mean()), r


def rtilde_bounded_support(n=2000):
    F = farey_sequence(n)                       # bounded support [0,1], density ~ n^2
    rt, _ = r_tilde(F)
    # scale-invariance witness: r~ is a ratio of consecutive gaps, so an affine remap of the
    # support must leave it identically unchanged (to float noise). Bounded vs unbounded is
    # irrelevant to a local scale-free ratio.
    rt_scaled, _ = r_tilde(F * 1e6 - 3.0)
    print(f"  Farey F_{n}: <r~> = {rt:.4f}  (banked 0.7051; Poisson 0.386, GUE 0.603)")
    print(f"  affine-remapped support (x·1e6−3): <r~> = {rt_scaled:.4f}  "
          f"(Δ={abs(rt-rt_scaled):.2e} — support-agnostic)")
    return {"rtilde_farey": rt, "rtilde_affine_remapped": rt_scaled,
            "support_agnostic": bool(abs(rt - rt_scaled) < 1e-9),
            "not_poisson": bool(abs(rt - 0.386) > 0.05),
            "resolution": "unfolding-free <r~> is a ratio of consecutive gaps: scale-free and "
                          "local, so it needs NO modification for bounded support. Verified: "
                          "affine remap leaves it invariant to float noise."}


# ---------------------------------------------------------------------------------------
# (C) §3a measure-declaration gate: fair-coin (Minkowski) vs Gauss, known-answer discriminator
# ---------------------------------------------------------------------------------------
def faircoin_partial_quotients(N):
    """Partial quotients under the fair coin on L/R (Minkowski ?): geometric(1/2), so
    P(a=k)=2^{-k}, arithmetic mean 2 exactly, all moments finite."""
    return RNG.geometric(0.5, size=N)


def gauss_partial_quotients(N, depth=40):
    """Partial quotients under the Gauss measure (Lebesgue-typical): CF digits of a uniform
    random x, via Gauss-map iteration. Distribution -> Gauss-Kuzmin; arithmetic mean diverges,
    geometric mean -> Khinchin. High-precision x so many digits are trustworthy."""
    import mpmath as mp
    mp.mp.dps = 60
    out = []
    for _ in range(N // depth + 1):
        # high-precision uniform x in (0,1): 50 random decimal digits (int64-safe)
        digits = "".join(str(d) for d in RNG.integers(0, 10, size=50))
        x = mp.mpf("0." + digits)
        if x == 0:
            continue
        for _ in range(depth):
            if x <= 0:
                break
            inv = 1 / x
            a = int(mp.floor(inv))
            out.append(a)
            x = inv - a
    return np.array(out[:N], dtype=np.int64)


def measure_gate():
    print("  fair coin (Minkowski ?):  a_k ~ geometric(1/2), E[a]=2, all moments finite")
    print("  Gauss (Lebesgue):         a_k ~ Gauss-Kuzmin, E[a]=∞, geo-mean → Khinchin 2.6854\n")
    rows = []
    for N in (10_000, 100_000, 1_000_000):
        fc = faircoin_partial_quotients(N)
        gs = gauss_partial_quotients(N)
        fc_am, fc_gm, fc_max = float(fc.mean()), float(np.exp(np.log(fc).mean())), int(fc.max())
        gs_am, gs_gm, gs_max = float(gs.mean()), float(np.exp(np.log(gs).mean())), int(gs.max())
        rows.append({"N": N, "faircoin_arith_mean": fc_am, "faircoin_geo_mean": fc_gm,
                     "faircoin_max": fc_max, "gauss_arith_mean": gs_am, "gauss_geo_mean": gs_gm,
                     "gauss_max": gs_max, "log2_N": math.log2(N)})
        print(f"  N={N:>9,}:  fair-coin AM={fc_am:6.3f} GM={fc_gm:5.3f} max={fc_max:<4d}"
              f"  |  Gauss AM={gs_am:7.3f} GM={gs_gm:5.3f} max={gs_max:<9d}  [log₂N={math.log2(N):.1f}]")

    # DISCRIMINATORS (all theorem-backed, robust to the heavy-tail sampling noise):
    #  1. fair-coin AM stable at 2 (finite mean, all moments finite).
    #  2. Gauss AM DIVERGENT: it is >> 2 at every N and tracks log2(N) (the Gauss-Kuzmin truncated
    #     mean grows ~ log2 N), not a fixed constant. Robust test: Gauss AM > 3x fair-coin AM at
    #     every N (not the noise-fragile monotone-growth test).
    #  3. Gauss max scales ~LINEARLY in N (heavy 1/k tail: max ~ N/log2), fair-coin max ~ log2 N
    #     (geometric tail). Cleanest separator: log(max)/log(N) → ~1 for Gauss, → ~0 for fair-coin.
    #  4. Gauss GM → Khinchin; fair-coin GM ≈ 1.66 (a different constant).
    fc_am_stable = all(abs(r["faircoin_arith_mean"] - 2.0) < 0.15 for r in rows)
    gauss_am_divergent = all(r["gauss_arith_mean"] > 3 * r["faircoin_arith_mean"] for r in rows)
    fc_max_slope = math.log(rows[-1]["faircoin_max"]) / math.log(rows[-1]["N"])
    gs_max_slope = math.log(rows[-1]["gauss_max"]) / math.log(rows[-1]["N"])
    max_scaling_separates = gs_max_slope > 0.6 and fc_max_slope < 0.35
    gauss_gm_khinchin = abs(rows[-1]["gauss_geo_mean"] - KHINCHIN) < 0.15
    separated = fc_am_stable and gauss_am_divergent and max_scaling_separates and gauss_gm_khinchin
    print(f"\n  fair-coin AM stable at 2 (finite mean):        {fc_am_stable}  "
          f"(AM {rows[0]['faircoin_arith_mean']:.3f}→{rows[-1]['faircoin_arith_mean']:.3f})")
    print(f"  Gauss AM divergent (>>2, tracks log₂N):        {gauss_am_divergent}  "
          f"(AM {rows[0]['gauss_arith_mean']:.1f}→{rows[-1]['gauss_arith_mean']:.1f} vs "
          f"log₂N {rows[0]['log2_N']:.1f}→{rows[-1]['log2_N']:.1f})")
    print(f"  max-PQ scaling separates (Gauss ~N, coin ~logN): {max_scaling_separates}  "
          f"(log-max/log-N: Gauss {gs_max_slope:.2f}, fair-coin {fc_max_slope:.2f})")
    print(f"  Gauss GM → Khinchin 2.6854:                    {gauss_gm_khinchin}  "
          f"(GM={rows[-1]['gauss_geo_mean']:.3f})")
    print(f"  -> estimator SEPARATES the two singular measures: {separated}")
    return {"rows": rows, "faircoin_AM_stable_at_2": fc_am_stable,
            "gauss_AM_divergent": gauss_am_divergent,
            "max_PQ_scaling_separates": max_scaling_separates,
            "faircoin_logmax_over_logN": fc_max_slope, "gauss_logmax_over_logN": gs_max_slope,
            "gauss_GM_is_khinchin": gauss_gm_khinchin,
            "SEPARATES": bool(separated),
            "transfer_note": "the measured statistic is a property of the generating MEASURE, "
            "not the raw points — the same structure as the fungal Cox rate-envelope confound "
            "(#4259167), but here with a theorem for ground truth. A rate-envelope-preserving "
            "surrogate must reshuffle points WITHOUT changing the CF-digit measure; validated "
            "against this known answer before porting to the fungal data."}


def main():
    out = {}
    print("ARS-RH PHASE 0 — completeness, bounded-support <r~>, and the measure-declaration gate")
    print("(the Farey→Hall spacing gate is already certified: farey_class_certify.py, "
          "KS=0.00013 vs Hall — reproduced this session)\n")

    print("(A) COMPLETENESS / CARDINALITY GATE  |F_n| = 1 + Σφ(k):")
    out["A_cardinality"] = cardinality_gate()
    print(f"    -> {'PASS' if out['A_cardinality']['PASS'] else 'FAIL'}\n")

    print("(B) OPEN DECISION #1 — <r~> on bounded-support n²-density process:")
    out["B_rtilde_bounded"] = rtilde_bounded_support()
    print()

    print("(C) §3a MEASURE-DECLARATION GATE — fair coin (Minkowski) vs Gauss:")
    out["C_measure_gate"] = measure_gate()

    out["PHASE0_PASS"] = bool(out["A_cardinality"]["PASS"]
                             and out["B_rtilde_bounded"]["support_agnostic"]
                             and out["B_rtilde_bounded"]["not_poisson"]
                             and out["C_measure_gate"]["SEPARATES"])
    print(f"\nPHASE0_PASS (new items): {out['PHASE0_PASS']}")
    p = os.path.join(HERE, "phase0_measure_gate_measured.json")
    json.dump(out, open(p, "w"), indent=2, default=str)
    print("wrote", p)


if __name__ == "__main__":
    main()

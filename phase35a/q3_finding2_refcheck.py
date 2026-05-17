"""
phase35a/q3_finding2_refcheck.py — MANDATED artifact-clearance of §Q3 Finding 2
(the large-N λ-collapse). Will's directive 2026-05-17: "the reference-resolution
check is NOT optional." SCOPING; NO §3 adjudication; §3 untouched; brief-and-hold.

Finding 1 established §Q3 absolute W1δ are reference-sensitive and a striking
quantitative pattern in them was artifact. Finding 2 (λ-collapse to 4 dp at
F_26) is a striking quantitative pattern in the SAME numbers ⇒ inherits the
suspicion until cleared by the three checks:

  (a) per-λ own reference vs common — ANSWERED BY CODE INSPECTION: §Q3 built
      `ref = am_eigs(lam, N_REF, 0.0)` INSIDE the per-λ loop ⇒ each λ has its
      OWN λ-specific reference. (Closes the common-ref pathway; the cell-N/
      ref-N RATIO is still λ-flat — the mechanism Will named.)
  (c) >1 cell-N — ANSWERED FROM EXISTING §Q3 LOG: inter-λ rel-spread shrinks
      monotonically as cell-N→ref-N (F_22 ~2.7% → F_24 ~0.15% → F_26 ~0.014%):
      real λ-dependence at small cell-N; the 4-dp collapse is large-cell-N-
      near-ref-N. Signature of the ratio mechanism, not a substrate constant.
  (b) THIS SCRIPT — the decisive test: at FIXED cell-N, vary the reference
      resolution ref-N. Artifact ⇒ W1δ value &/or inter-λ spread move with
      ref-N (the cell-N/ref-N ratio carries no λ). Substrate ⇒ invariant
      across ref-N and the tight collapse persists at >1 cell-N.

Pre-stated disposition (no §3 adjudication — artifact status only):
  • REFERENCE_ARTIFACT_CONFIRMED — at fixed cell-N, mean W1δ shifts across
    ref-N by ≫ the inter-λ spread, and/or the λ-ordering/spread changes with
    ref-N ⇒ Finding 2 is a phantom; struck permanently from the §3 framing.
  • SURVIVED_REFCHECK_ESCALATE — W1δ(λ,cell-N) invariant across ref-N within
    the inter-λ spread AND tight collapse persists at both cell-N ⇒ not a
    simple ref artifact; ESCALATE to Will (do NOT auto-promote to substrate).

cell-N ∈ {F_22, F_24} (both ≪ every ref-N below — valid IDS unfold).
ref-N ∈ {F_25, F_26, F_27} (λ-specific, per (a)). n_φ=3 (the collapse is
in the φ-stable mean). Cost ≈ refs 3λ×(F_25 40s+F_26 106s+F_27 278s)≈21min
+ cells ≈3min ≈ bounded ~24 min.
"""
from __future__ import annotations
import os, sys, json, time
import numpy as np
from scipy.linalg import eigvalsh_tridiagonal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
GOLDEN = (np.sqrt(5.0) - 1.0) / 2.0


def fib_upto(k):
    F = [0, 1]
    while len(F) <= k:
        F.append(F[-1] + F[-2])
    return F

FIB = fib_upto(27)
assert (FIB[22], FIB[24], FIB[25], FIB[26], FIB[27]) == (17711, 46368, 75025, 121393, 196418)

LAMBDAS = [0.10, 0.30, 0.50]
PHIS = np.linspace(0.0, 1.0, 3, endpoint=False)
CELL_NS = [FIB[22], FIB[24]]                 # 17711, 46368
REF_NS  = [FIB[25], FIB[26], FIB[27]]        # 75025, 121393, 196418  (all > 46368)


def am_eigs(lam, N, phi):
    n = np.arange(N, dtype=np.float64)
    d = 2.0 * lam * np.cos(2.0 * np.pi * (GOLDEN * n + phi))
    return eigvalsh_tridiagonal(d, np.ones(N - 1))


def unfold_ids_ref(eigs, ref):
    er = np.sort(ref)
    idx = np.searchsorted(er, np.sort(eigs), side="right")
    return (idx / er.size) * len(eigs)


def W1d(eigs, ref):
    u = unfold_ids_ref(eigs, ref)
    d = np.diff(np.sort(u)); d = d[int(0.02*len(d)):int(0.98*len(d))]
    m = d.mean(); s = d/m if m > 0 else d
    return float(np.mean(np.abs(s - 1.0)))


def main():
    print("=" * 80)
    print("§Q3 FINDING-2 REFERENCE CHECK (mandated; SCOPING; no §3 adjudication)")
    print(f"  λ={LAMBDAS}  cell-N={CELL_NS}  ref-N={REF_NS}  n_φ={len(PHIS)}")
    print("  (a) per-λ OWN reference [code-inspection: confirmed]")
    print("  (c) collapse tightens as cell-N→ref-N [existing §Q3 log: artifact-consistent]")
    print("  (b) THIS RUN: does W1δ / inter-λ spread move with ref-N at fixed cell-N?")
    print("=" * 80)
    out = {"mandated_by": "Will 2026-05-17", "scoping": True,
           "a_own_reference": True, "lambdas": LAMBDAS,
           "cell_Ns": CELL_NS, "ref_Ns": REF_NS, "data": {}}

    # cell spectra: independent of reference — compute once per (λ, cell-N, φ)
    cell_eigs = {}
    for lam in LAMBDAS:
        for cN in CELL_NS:
            ts = time.time()
            cell_eigs[(lam, cN)] = [am_eigs(lam, cN, p) for p in PHIS]
            print(f"  cell (λ={lam}, N={cN}) ×{len(PHIS)}φ  ({time.time()-ts:.0f}s)",
                  flush=True)

    # λ-specific references at each ref-N
    for cN in CELL_NS:
        out["data"][cN] = {}
    for lam in LAMBDAS:
        for rN in REF_NS:
            ts = time.time()
            ref = np.sort(am_eigs(lam, rN, 0.0))
            dt = time.time() - ts
            for cN in CELL_NS:
                w = float(np.mean([W1d(e, ref) for e in cell_eigs[(lam, cN)]]))
                out["data"][cN].setdefault(str(lam), {})[str(rN)] = round(w, 6)
            print(f"  ref (λ={lam}, N={rN}) built ({dt:.0f}s) ; "
                  f"W1δ@cellN " + " ".join(
                      f"{cN}:{out['data'][cN][str(lam)][str(rN)]:.5f}"
                      for cN in CELL_NS), flush=True)

    print("\n" + "=" * 80)
    print("READOUT — at fixed cell-N, W1δ(λ) across ref-N; inter-λ spread per ref-N")
    print("=" * 80)
    disposition = {}
    for cN in CELL_NS:
        print(f"\ncell-N={cN}")
        print(f"{'ref-N':>8} | " + " ".join(f"λ={l:<5}" for l in LAMBDAS)
              + " |  inter-λ spread  rel%")
        spreads = {}
        ref_move = {l: [] for l in LAMBDAS}
        for rN in REF_NS:
            vals = [out["data"][cN][str(l)][str(rN)] for l in LAMBDAS]
            for l, v in zip(LAMBDAS, vals):
                ref_move[l].append(v)
            sp = max(vals) - min(vals)
            spreads[rN] = sp
            print(f"{rN:>8} | " + " ".join(f"{v:.5f}" for v in vals)
                  + f" |  {sp:.6f}  {100*sp/np.mean(vals):.3f}%")
        # how much does W1δ move with ref-N (per λ) vs the inter-λ spread?
        max_ref_swing = max(max(v) - min(v) for v in ref_move.values())
        med_spread = float(np.median(list(spreads.values())))
        verdict = ("REFERENCE_ARTIFACT_CONFIRMED"
                   if max_ref_swing > 3.0 * med_spread
                   else "SURVIVED_REFCHECK_ESCALATE")
        disposition[cN] = {"max_ref_swing": round(max_ref_swing, 6),
                           "median_interlambda_spread": round(med_spread, 6),
                           "verdict": verdict}
        print(f"  → max W1δ swing across ref-N = {max_ref_swing:.6f} ; "
              f"median inter-λ spread = {med_spread:.6f} ; {verdict}")

    out["disposition"] = disposition
    overall = ("REFERENCE_ARTIFACT_CONFIRMED"
               if all(d["verdict"] == "REFERENCE_ARTIFACT_CONFIRMED"
                      for d in disposition.values())
               else "MIXED_OR_SURVIVED_ESCALATE")
    out["overall"] = overall
    json.dump(out, open(os.path.join(HERE, "q3_finding2_refcheck_results.json"),
                        "w"), indent=1)
    print("\n" + "=" * 80)
    print(f"OVERALL: {overall}")
    print("Disposition is ARTIFACT-STATUS ONLY. No §3 adjudication. brief-and-hold.")
    print("=" * 80)


if __name__ == "__main__":
    main()

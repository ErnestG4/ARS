"""
phase35a/sup_phi_resolved_L.py — SUP-SIDE φ-RESOLVED L-CHECK (Will's
adjudication 2026-05-19 post-b1crocze1: "sup-side φ-resolved check
FIRST … more consequential, not less"). PREPARED, awaiting Will's
explicit go. brief-and-hold.

CONTEXT. b1crocze1 → `PHI_DEPENDENT_BOTH_CELLS` at sub side: L=1e5
artifact is φ-dependent with magnitude 1.67-2.5× the stored spread.
Step-1's `gap ≥ max(sub_spread, sup_spread)` test was typically
dominated by **sup_spread** (e.g. N=70k: sub_spread=2.7e-05 vs
sup_spread=7.66e-02), so the sup-side φ-mode is the
LOAD-BEARING-on-the-test axis. Sub-side characterized: the φ-mode of
the sup-side L=1e5 artifact is the open axis. This run closes it
non-adjudicatively.

PRE-REGISTERED (discriminant_exact_question_check):
 EXACT QUESTION (per sup cell): at L=1e5 (Step-1's L) and at more-
 converged L, what is the per-φ structure of the L-artifact in the
 SUPERCRITICAL regime? Is per-φ shift Δw(φ) = W1δ(L=1e5,φ) −
 W1δ(L_top,φ) approximately CONSTANT across φ (common-mode: SPREAD
 cancels under L-shift) or VARIES comparably to spread@L=1e5
 (per-φ artifact contribution to the spread)?

 DESIGN (mirror b1crocze1's instrument, sub→sup, locked):
  • 2 cells, both at N=70000 (matches Step-1's N AND the sub-mirror
    cells for direct apparatus comparability):
     - (δ=0.5, N=70k) → λ=1.5 — Step-1's ACTUAL sup coupling;
       localized/PP regime; LOAD-BEARING-on-the-Step-1-test cell.
     - (δ=0.005, N=70k) → λ=1.005 — near-critical sup control
       (mirrors sub's λ=0.995); tests δ-universality of the sup-side
       φ-mode (Will's structural observation: ratio ~invariant across
       δ on sub side; sup side may or may not mirror that).
  • 16 φ∈[0,0.5) endpoint=False — EXACT match Step-1's α-ensemble
    (§5 apparatus-invariance; identical to sub-side run).
  • L ∈ {100000, 400000, 1600000} — Step-1's L + two more L for
    trajectory. The sup L-convergence rate may differ from sub
    (localized vs AC), but the test does NOT require L_top to be
    fully L-converged — it requires only enough L-shift to expose
    the φ-mode of the displacement. Structurally robust to slower
    sup-side L-convergence (NOT a softening of the test).
  • Per-φ W1δ stored individually (the whole point — NO averaging).

 CODED TEST per cell (IDENTICAL to sub-side b1crocze1):
  per L: spread_L = ptp_φ(W1δ); mean_L = mean_φ(W1δ).
  Δw(φ) = w(L=1e5,φ) − w(L_top,φ).
  PHI_COMMON_MODE iff ptp_φ(Δw) ≤ TOL · spread@L=1e5  (TOL=0.25)
  PHI_DEPENDENT   iff ptp_φ(Δw) ≥ HI  · spread@L=1e5  (HI=1.0)
  PHI_MODE_INDETERMINATE otherwise.
  (Same thresholds as sub-side ⇒ directly comparable verdicts;
  TOL/HI proposed-not-fixed; structure fixed.)

 PER-CELL TERMINALS — REPORT implication, do NOT adjudicate Step-1:
  PHI_COMMON_MODE_ARTIFACT (sup) — L-shift ~uniform across φ ⇒ the
   sup-side L=1e5 spread captures substrate variation ⇒ Step-1's
   typically-dominant sup_spread floor is ROBUST against this
   artifact mode in this cell. Reported, not concluded.
  PHI_DEPENDENT_ARTIFACT (sup) — L-shift varies per φ ⇒ Step-1's
   typically-dominant sup_spread floor was partly artifact-driven;
   magnitude per-cell. Combined with sub-side already-DEPENDENT, this
   would place BOTH legs of Step-1's spread-floor under contamination
   (Step-1 conclusion remains Will's). Reported.
  PHI_MODE_INDETERMINATE — between criteria.

 OVERALL (combine 2 cells, δ=0.5/λ=1.5 is Step-1-direct load-bearing):
  SUP_PHI_COMMON_MODE_BOTH_CELLS — both common-mode.
  SUP_PHI_DEPENDENT_BOTH_CELLS   — both dependent.
  SUP_PHI_MODE_MIXED_CELLS       — cells differ.
  SUP_PHI_MODE_INDETERMINATE_OVERALL — any cell indeterminate.

SCOPE. Characterizes the φ-mode of the sup-side L=1e5 artifact ONLY.
NEVER adjudicates Step-1 (implications pre-registered; conclusion is
Will's). NEVER proves (A)/(B) (only §D/DGY). Does NOT decide §D. No
§3, no Class-II. Banked Step-1 untouched until Will adjudicates.
brief-and-hold; runs under Will's explicit go, then HOLDS.
**LOCAL, WORKERS=18** (Will: local, 18 threads); 96 tasks @ N=70k
across L tiers, ~35-40 min est (mirror sub-side b1crocze1 ~36 min);
np.ptp form (numpy-2 lesson); hardened (rawtable persist + 32-ckpt +
analyze-only). After this reports, the sub+sup pair characterizes the
φ-mode of Step-1's full spread floor; rev-5 brief becomes writable
(per Will's defer-both-sides logic).
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
import sys, json, time
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from unfold_rotnum import am_eigs, unfold_rotnum, W1d, GOLDEN

WORKERS = 18                                       # Will: local, 18 threads
PHIS = tuple(np.round(np.linspace(0.0, 0.5, 16, endpoint=False), 6))
CELLS = ((0.005, 70000), (0.5, 70000))            # (δ, N) — δ=0.5 ⇒ λ=1.5 Step-1-direct
LS = (100000, 400000, 1600000)
TOL = 0.25
HI = 1.0
OUT = os.path.join(HERE, "sup_phi_resolved_L_results.json")
RAW = os.path.join(HERE, "sup_phi_resolved_L_rawtable.json")


def cell(arg):
    delta, lam, N, L, phi = arg
    try:
        e = am_eigs(lam, int(N), float(phi))
        w = float(W1d(unfold_rotnum(e, lam, GOLDEN, int(L), phis=(float(phi),))))
        return (float(delta), float(lam), int(N), int(L), float(phi), w, None)
    except Exception as ex:
        return (float(delta), float(lam), int(N), int(L), float(phi), None, repr(ex))


def _dump_raw(table, total):
    recs = [[float(k[0]), int(k[1]), int(k[2]), float(k[3]), v]
            for k, v in table.items()]
    json.dump({"n": len(recs), "of": total, "recs": recs}, open(RAW, "w"))


def _load_raw():
    d = json.load(open(RAW))
    t = {}
    for dl, N, L, ph, w in d["recs"]:
        t[(round(float(dl), 6), int(N), int(L), round(float(ph), 6))] = w
    return t, d.get("n", len(t)), d.get("of")


def phi_vec(table, delta, N, L):
    v = [table.get((round(delta, 6), int(N), int(L), round(p, 6))) for p in PHIS]
    return None if any(x is None for x in v) else np.asarray(v, float)


def main():
    t0 = time.time()
    # supercritical: λ = 1 + δ  (mirror of sub's λ = 1 − δ)
    tasks = [(d, round(1.0 + d, 6), N, L, p)
             for (d, N) in CELLS for L in LS for p in PHIS]
    print("=" * 84)
    print(f"SUP φ-RESOLVED L-CHECK — {WORKERS}w ; AM golden θ ; "
          f"ratio-free leg")
    print(f"  cells(δ,N)={CELLS} → λ=1+δ ∈ {{1.005,1.5}}  "
          f"L-ladder={LS}  {len(PHIS)}φ  {len(tasks)} tasks")
    print("  Sup-side φ-mode of the L-artifact; NEVER adjudicates Step-1.")
    print("=" * 84, flush=True)

    errs, table = [], None
    if os.path.exists(RAW):
        tr, nr, ofr = _load_raw()
        if nr == ofr == len(tasks):
            table = tr
            print(f"  ANALYZE-ONLY: complete raw ({nr}) — skip compute.",
                  flush=True)
    if table is None:
        table, done = {}, 0
        with ProcessPoolExecutor(max_workers=WORKERS) as ex:
            for f in as_completed([ex.submit(cell, a) for a in tasks]):
                d, lam, N, L, phi, w, err = f.result()
                table[(round(d, 6), int(N), int(L), round(phi, 6))] = w
                done += 1
                if err:
                    errs.append({"delta": d, "N": N, "L": L, "phi": phi,
                                 "err": err})
                    print(f"  ERR δ={d} N={N} L={L} φ={phi}: {err}", flush=True)
                if done % 32 == 0:
                    _dump_raw(table, len(tasks))
                    print(f"  … {done}/{len(tasks)} [{time.time()-t0:.0f}s]",
                          flush=True)
        _dump_raw(table, len(tasks))
        print(f"  raw persisted ({len(table)}) — postproc free to re-run.",
              flush=True)

    Lref, Ltop = LS[0], LS[-1]
    per_cell, terminals = [], []
    for (d, N) in CELLS:
        per_L = {}
        ok = True
        for L in LS:
            v = phi_vec(table, d, N, L)
            if v is None: ok = False; break
            per_L[L] = v
        if not ok:
            per_cell.append({"delta": d, "N": N, "error": True})
            terminals.append("PHI_MODE_INDETERMINATE"); continue
        spread_ref = float(np.ptp(per_L[Lref]))
        mean_ref = float(per_L[Lref].mean())
        spread_top = float(np.ptp(per_L[Ltop]))
        mean_top = float(per_L[Ltop].mean())
        dw = per_L[Lref] - per_L[Ltop]
        dw_ptp = float(np.ptp(dw))
        dw_mean = float(dw.mean())
        if spread_ref <= 0:
            term = "PHI_MODE_INDETERMINATE"; ratio = None
        else:
            ratio = dw_ptp / spread_ref
            if ratio <= TOL: term = "PHI_COMMON_MODE_ARTIFACT"
            elif ratio >= HI: term = "PHI_DEPENDENT_ARTIFACT"
            else: term = "PHI_MODE_INDETERMINATE"
        terminals.append(term)
        per_cell.append({
            "delta": d, "lam_sup": round(1.0 + d, 6), "N": N,
            "L_ref": Lref, "L_top": Ltop,
            "mean_at_L_ref": round(mean_ref, 8),
            "mean_at_L_top": round(mean_top, 8),
            "spread_at_L_ref": round(spread_ref, 8),
            "spread_at_L_top": round(spread_top, 8),
            "per_phi_shift_ptp": round(dw_ptp, 8),
            "per_phi_shift_mean": round(dw_mean, 8),
            "ratio_phi_shift_to_L_ref_spread": (round(ratio, 4)
                                                if ratio is not None else None),
            "TOL": TOL, "HI": HI, "terminal": term,
            "phi_grid": [float(p) for p in PHIS],
            "phi_W1d_per_L": {str(L): [round(float(x), 8)
                                       for x in per_L[L]] for L in LS},
        })

    cset = set(terminals)
    if "PHI_MODE_INDETERMINATE" in cset:
        overall = "SUP_PHI_MODE_INDETERMINATE_OVERALL"
    elif cset == {"PHI_COMMON_MODE_ARTIFACT"}:
        overall = "SUP_PHI_COMMON_MODE_BOTH_CELLS"
    elif cset == {"PHI_DEPENDENT_ARTIFACT"}:
        overall = "SUP_PHI_DEPENDENT_BOTH_CELLS"
    else:
        overall = "SUP_PHI_MODE_MIXED_CELLS"

    rec = {"run": "sup φ-resolved L-check (Step-1 sup-side φ-dependence)",
           "cells_sup_lambda": [[round(1.0 + d, 6), N] for (d, N) in CELLS],
           "cells": [list(c) for c in CELLS], "LS": list(LS),
           "n_phi": len(PHIS), "TOL": TOL, "HI": HI,
           "per_cell": per_cell, "overall_terminal": overall,
           "implications_for_Step1_PRE_REGISTERED_NOT_CONCLUDED": {
               "SUP_PHI_COMMON_MODE_BOTH_CELLS":
                   "Sup-side L=1e5 artifact ~uniform across φ ⇒ Step-1's "
                   "typically-dominant sup_spread floor is ROBUST against "
                   "this artifact mode; combined with sub-side "
                   "PHI_DEPENDENT, the test's load-bearing leg survives "
                   "(Will's call).",
               "SUP_PHI_DEPENDENT_BOTH_CELLS":
                   "Sup-side too is dependent ⇒ BOTH legs of Step-1's "
                   "spread-floor under contamination; the dominant sup "
                   "leg's magnitude reported per-cell (Will's call).",
               "SUP_PHI_MODE_MIXED_CELLS":
                   "Substrate-modulated sup φ-mode; δ=0.5/λ=1.5 cell is "
                   "Step-1-direct (load-bearing).",
           },
           "errors": errs, "total_s": round(time.time() - t0, 0),
           "note": "Characterizes φ-mode of sup-side L=1e5 artifact. NEVER "
                   "adjudicates Step-1 — the implications are pre-registered; "
                   "the conclusion is Will's. Never proves (A)/(B); §D not "
                   "decided; banked Step-1 untouched. With sub-side already "
                   "PHI_DEPENDENT_BOTH_CELLS, this closes the sub+sup pair "
                   "and rev-5 becomes writable (per Will's defer-both-sides "
                   "logic)."}
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    for p in per_cell:
        if p.get("error"):
            print(f"  cell δ={p['delta']} N={p['N']}  ERROR"); continue
        print(f"  cell δ={p['delta']} N={p['N']} (λ={p['lam_sup']:.4f}) | "
              f"spread@1e5={p['spread_at_L_ref']:.6g} "
              f"mean@1e5={p['mean_at_L_ref']:.6g} "
              f"spread@{p['L_top']:.0e}={p['spread_at_L_top']:.6g} "
              f"mean@{p['L_top']:.0e}={p['mean_at_L_top']:.6g}")
        print(f"        per-φ shift ptp={p['per_phi_shift_ptp']:.6g} "
              f"mean={p['per_phi_shift_mean']:.6g}  "
              f"ratio_to_1e5_spread={p['ratio_phi_shift_to_L_ref_spread']}  "
              f"→ {p['terminal']}")
    print(f"  OVERALL: {overall}  [{rec['total_s']}s] errors={len(errs)}")
    print("  Implications pre-registered, NOT concluded. Step-1 adjudication = Will.")
    print("  Never proves (A)/(B); §D not decided; banked Step-1 untouched.")
    print("=" * 84)


if __name__ == "__main__":
    main()

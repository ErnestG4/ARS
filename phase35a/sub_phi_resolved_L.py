"""
phase35a/sub_phi_resolved_L.py — φ-RESOLVED L-CHECK (Will's
adjudication 2026-05-19 post-bh22pfzoa: option (iv) in specific form,
the precise measurement that closes the Step-1 φ-dependence
question). PREPARED, awaiting Will's explicit go. brief-and-hold.

CONTEXT. bh22pfzoa narrowed but did NOT close the Step-1 exposure.
The L-sweep analyzed ENSEMBLE MEANS (φ-averaged) per (δ,N,L), not
per-φ trajectories. At L=1e5 (where Step-1 ran) the leg's
subcritical W1δ is ~22× the L-converged substrate value at N=70k
near-critical; Step-1's α-ensemble FLOOR was the φ-spread of that
artifact-dominated quantity. Whether that artifact has
φ-common-mode behavior (shifts the whole ensemble together — SPREAD
cancels, Step-1 floor = substrate spread, exposure CLEARED in this
sense) or φ-dependent behavior (per-φ contribution to the spread —
Step-1 floor partly artifact-driven, exposure CONCRETELY LIVE with
magnitude) is the open question. This run measures it directly,
non-adjudicatively.

PRE-REGISTERED (discriminant_exact_question_check):
 EXACT QUESTION (per cell): at L=1e5 (Step-1's L) and at more-
 converged L, what is the per-φ structure of the L-artifact? Is the
 per-φ shift Δw_φ = W1δ(L=1e5,φ) − W1δ(L_top,φ) approximately
 CONSTANT across φ (⇒ common-mode: spread cancels under L-shift), or
 does it VARY across φ comparably to the L=1e5 spread (⇒ per-φ
 artifact contribution to the spread)?

 DESIGN (locked, justified):
  • 2 cells, both at N=70000 (Step-1's N AND where the artifact is
    biggest at L=1e5):
     - (δ=0.5, N=70k) — λ=0.5, Step-1's ACTUAL sub coupling; deep-AC
       (L-conv → 0.00013); the LOAD-BEARING cell for Step-1 exposure.
     - (δ=0.005, N=70k) — λ=0.995, near-critical control; non-trivial
       substrate (L-conv → 0.0155); tests whether the φ-mode is
       δ-universal or δ-modulated.
  • 16 φ∈[0,0.5) endpoint=False — EXACT match to Step-1's α-ensemble
    (apparatus-invariance §5; reuses Step-1's φ-grid verbatim).
  • L ∈ {100000, 400000, 1600000} — Step-1's L=1e5 + two more
    converged points (gives trajectory, not just two-point shift).
  • Per-φ W1δ stored individually (the whole point — NO ensemble
    averaging in cell()).

 CODED TEST per cell:
  per L: spread_L = ptp_φ(W1δ); mean_L = mean_φ(W1δ).
  per-φ shift: Δw(φ) = w(L=1e5, φ) − w(L_top, φ).
  PHI_COMMON_MODE iff ptp_φ(Δw) ≤ TOL · spread@L=1e5  (TOL=0.25)
  PHI_DEPENDENT   iff ptp_φ(Δw) ≥ HI  · spread@L=1e5  (HI=1.0)
  PHI_MODE_INDETERMINATE otherwise.
  (TOL/HI proposed-not-fixed; structure fixed: per-φ-shift-spread
  compared to the L=1e5 spread Step-1 actually stored. Below TOL the
  artifact is shifting the ensemble approximately uniformly; at/above
  HI the per-φ artifact variation matches the L=1e5 spread.)

 PER-CELL TERMINALS — each REPORTS an IMPLICATION for Step-1 but
 does NOT adjudicate Step-1 (Will's call):
  PHI_COMMON_MODE_ARTIFACT — L-shift ~uniform across φ ⇒ the L=1e5
   spread captures substrate variation, NOT artifact ⇒ Step-1's
   spread-based α-ensemble floor is ROBUST against this artifact
   mode in this cell. Reported, not concluded.
  PHI_DEPENDENT_ARTIFACT — L-shift varies per φ ⇒ the L=1e5 spread
   contains per-φ artifact contribution ⇒ Step-1's floor was partly
   artifact-driven IN THIS CELL; magnitude = the per-φ-shift-spread
   relative to the L=1e5 spread. Reported.
  PHI_MODE_INDETERMINATE — between criteria.

 OVERALL (combine 2 cells, the Step-1-direct δ=0.5 cell is
 load-bearing):
  PHI_COMMON_MODE_BOTH_CELLS — both common-mode (Step-1 floor robust
   against this artifact mode across regimes).
  PHI_DEPENDENT_BOTH_CELLS   — both dependent.
  PHI_MODE_MIXED_CELLS       — cells differ; substrate-modulated
   φ-mode; both cells' details matter.
  PHI_MODE_INDETERMINATE_OVERALL — any cell indeterminate.

SCOPE. Characterizes the φ-mode of the L-artifact ONLY. NEVER
adjudicates Step-1 (the implications are pre-registered; the
conclusion is Will's). NEVER proves (A)/(B) (only §D/DGY). Does NOT
decide §D. No §3, no Class-II. Banked Step-1 untouched until Will
adjudicates this report. brief-and-hold; runs under Will's explicit
go, then HOLDS. **LOCAL** (Will 2026-05-19: server loud, local more
efficient overall), 96 tasks @ N=70k across L tiers, **~90 min @
18w**; np.ptp form (numpy-2 lesson); hardened (rawtable persist +
32-ckpt + analyze-only).
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
CELLS = ((0.005, 70000), (0.5, 70000))            # (δ, N) — δ=0.5 is Step-1-direct
LS = (100000, 400000, 1600000)
TOL = 0.25                                         # common-mode threshold (×spread@1e5)
HI = 1.0                                           # dependent threshold
OUT = os.path.join(HERE, "sub_phi_resolved_L_results.json")
RAW = os.path.join(HERE, "sub_phi_resolved_L_rawtable.json")


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
    tasks = [(d, round(1.0 - d, 6), N, L, p)
             for (d, N) in CELLS for L in LS for p in PHIS]
    print("=" * 84)
    print(f"SUB φ-RESOLVED L-CHECK — {WORKERS}w ; AM golden θ ; "
          f"ratio-free leg")
    print(f"  cells(δ,N)={CELLS}  L-ladder={LS}  {len(PHIS)}φ  "
          f"{len(tasks)} tasks")
    print("  Step-1 φ-mode of the L-artifact; NEVER adjudicates Step-1.")
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

    Lref, Ltop = LS[0], LS[-1]                     # 1e5 (Step-1) vs top
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
        dw = per_L[Lref] - per_L[Ltop]              # per-φ shift L=1e5 → L_top
        dw_ptp = float(np.ptp(dw))
        dw_mean = float(dw.mean())
        # criterion
        if spread_ref <= 0:
            term = "PHI_MODE_INDETERMINATE"
            ratio = None
        else:
            ratio = dw_ptp / spread_ref
            if ratio <= TOL: term = "PHI_COMMON_MODE_ARTIFACT"
            elif ratio >= HI: term = "PHI_DEPENDENT_ARTIFACT"
            else: term = "PHI_MODE_INDETERMINATE"
        terminals.append(term)
        per_cell.append({
            "delta": d, "lam_sub": round(1.0 - d, 6), "N": N,
            "L_ref": Lref, "L_top": Ltop,
            "mean_at_L_ref": round(mean_ref, 8),
            "mean_at_L_top": round(mean_top, 8),
            "spread_at_L_ref": round(spread_ref, 8),
            "spread_at_L_top": round(spread_top, 8),
            "per_phi_shift_ptp": round(dw_ptp, 8),
            "per_phi_shift_mean": round(dw_mean, 8),
            "ratio_phi_shift_to_L_ref_spread": (round(ratio, 4)
                                                if ratio is not None else None),
            "TOL": TOL, "HI": HI,
            "terminal": term,
            "phi_grid": [float(p) for p in PHIS],
            "phi_W1d_per_L": {str(L): [round(float(x), 8)
                                       for x in per_L[L]] for L in LS},
        })

    # overall (load-bearing cell = δ=0.5)
    cset = set(terminals)
    if "PHI_MODE_INDETERMINATE" in cset:
        overall = "PHI_MODE_INDETERMINATE_OVERALL"
    elif cset == {"PHI_COMMON_MODE_ARTIFACT"}:
        overall = "PHI_COMMON_MODE_BOTH_CELLS"
    elif cset == {"PHI_DEPENDENT_ARTIFACT"}:
        overall = "PHI_DEPENDENT_BOTH_CELLS"
    else:
        overall = "PHI_MODE_MIXED_CELLS"

    rec = {"run": "sub φ-resolved L-check (Step-1 φ-dependence)",
           "cells": [list(c) for c in CELLS], "LS": list(LS),
           "n_phi": len(PHIS), "TOL": TOL, "HI": HI,
           "per_cell": per_cell, "overall_terminal": overall,
           "implications_for_Step1_PRE_REGISTERED_NOT_CONCLUDED": {
               "PHI_COMMON_MODE_BOTH_CELLS":
                   "L=1e5 artifact ~uniform across φ ⇒ Step-1 spread-based "
                   "α-ensemble floor captures substrate variation, not "
                   "artifact ⇒ exposure CLEARED in this sense (Will's call).",
               "PHI_DEPENDENT_BOTH_CELLS":
                   "L=1e5 spread contains per-φ artifact contribution ⇒ "
                   "Step-1 floor partly artifact-driven; magnitude reported "
                   "per-cell (Will's call).",
               "PHI_MODE_MIXED_CELLS":
                   "Substrate-modulated φ-mode; δ=0.5 cell is "
                   "Step-1-direct (load-bearing).",
           },
           "errors": errs, "total_s": round(time.time() - t0, 0),
           "note": "Characterizes φ-mode of L-artifact. NEVER adjudicates "
                   "Step-1 — the implications are pre-registered; the "
                   "conclusion is Will's. Never proves (A)/(B); §D not "
                   "decided; banked Step-1 untouched until Will adjudicates."}
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    for p in per_cell:
        if p.get("error"):
            print(f"  cell δ={p['delta']} N={p['N']}  ERROR"); continue
        print(f"  cell δ={p['delta']} N={p['N']} (λ={p['lam_sub']:.4f}) | "
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

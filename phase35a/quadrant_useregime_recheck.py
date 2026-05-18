"""
phase35a/quadrant_useregime_recheck.py — Step-1 SEAM closure (Will
2026-05-19): the combined "both halves ⇒ Step-1 complete" claim
assembles no-false-positive@N=2584 (quadrant) with sensitivity@N≳5e4
(sub-quadrant); the diagnostic's USE REGIME is N≳5e4 where
no-false-positive is unverified — and not idly (regimes could become
quadrant-level-distinguishable at large N, changing the test's
meaning). Also folds the earlier φ-seam (zoo-gap/35b were φ=0-only).
ONE quadrant-level robustness re-check across BOTH N(≥5e4) and φ.

PRE-REGISTERED (discriminant_exact_question_check; THIS adjudicates the
Step-1 stamp's seam, so mandatory & recorded):
 EXACT QUESTION: at use-regime N≳5e4, does transition_diagnostic still
 correctly return NO quadrant-level transition on the AM λ-trajectory,
 φ-robustly across the substrate α-ensemble, AND is the quadrant label
 still BR_artifact (not become quadrant-distinguishable ⇒ test-meaning
 change)?
 CODED TEST = the 35b no-false-positive test re-applied VERBATIM at the
 use regime (joint_q_profile→joint_quadrant_diagnostic→
 characterize_transition on the per-λ primary trajectory), across
 N∈{50000,70000,100000} × 8-φ α-ensemble + α-null parity. NOT a new
 discriminant. Honest terminals pre-allowed:
  (a) NO_FP_N_PHI_STABLE — uniform BR_artifact & transition_detected
      =False ∀N≥5e4 ∀φ ⇒ clean extension, Step-1 stamp clean;
  (b) QUADRANT_DISTINGUISHABLE_AT_USE_N — regimes quadrant-separated at
      large N ⇒ test-meaning CHANGES; honest re-frame, NOT a
      retraction of the N=2584 banked result;
  (c) PHI_DEPENDENT — label/verdict varies with φ ⇒ φ-robustness fails.
 No auto-soften; report the terminal the data lands in.

Instrument-validation seam closure (NOT an AM discovery/§3/Class-II).
MP 18w/24core thread-pinned, pure deterministic ⇒ bit-identical-serial.
brief-and-hold; Class II blocked; no §3 adjudication; banked verdicts
ADD-not-reopen.
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
import pandas as pd
from arithmetic_toolkit import joint_q_profile, joint_quadrant_diagnostic
from transition_diagnostic import characterize_transition
from unfold_rotnum import am_eigs, unfold_rotnum, GOLDEN

WORKERS = 18
LITER, QMAX, MINEV = 100_000, 30, 30
NS = [50000, 70000, 100000]                       # the use regime
SIG_LAMS = [0.50, 0.70, 0.85, 0.95, 1.05, 1.25, 1.50, 2.00]  # brackets λ=1, excluded
PHIS = tuple(np.round(np.linspace(0.0, 0.5, 8, endpoint=False), 6))  # α-ensemble
NULL_LAM = 1.50                                    # α-null parity (localised)
OUT = os.path.join(HERE, "quadrant_useregime_results.json")


def cell(arg):
    """(tag, lam, N, phi) → (tag, lam, N, phi, primary, err)."""
    tag, lam, N, phi = arg
    try:
        e = am_eigs(lam, int(N), float(phi))
        uf = np.sort(unfold_rotnum(e, lam, GOLDEN, LITER, phis=(float(phi),)))
        j = joint_q_profile(uf, q_max=QMAX, min_events_per_q=MINEV)
        qd = joint_quadrant_diagnostic(j)
        prim = str(qd['quadrant'].value_counts().idxmax())
        return (tag, lam, int(N), float(phi), prim, None)
    except Exception as ex:
        return (tag, lam, int(N), float(phi), None, repr(ex))


def main():
    t0 = time.time()
    tasks = [("sig", lam, N, ph) for N in NS for lam in SIG_LAMS for ph in PHIS]
    tasks += [("null", NULL_LAM, N, ph) for N in NS for ph in PHIS]
    print("=" * 86)
    print(f"QUADRANT USE-REGIME SEAM RE-CHECK — {WORKERS}w ; N={NS} ; "
          f"{len(PHIS)} φ∈[0,0.5) ; signal λ={SIG_LAMS}")
    print(f"  35b no-false-positive test VERBATIM at the use regime + φ-robust")
    print("=" * 86, flush=True)
    res = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for f in as_completed([ex.submit(cell, a) for a in tasks]):
            tag, lam, N, ph, prim, err = f.result()
            res[(tag, lam, N, ph)] = prim
            if err:
                print(f"  ERR {tag} λ={lam} N={N} φ={ph}: {err}", flush=True)

    rec = {"scoping_seam_closure": True, "Ns": NS, "phis": list(PHIS),
           "sig_lams": SIG_LAMS, "per_N": []}
    overall = "NO_FP_N_PHI_STABLE"
    for N in NS:
        per_phi = []
        for ph in PHIS:
            prims = [res.get(("sig", lam, N, ph)) for lam in SIG_LAMS]
            if any(p is None for p in prims):
                per_phi.append({"phi": ph, "error": True}); continue
            df = pd.DataFrame({"primary": prims,
                               "subwindow_start_us": range(len(prims))})
            ch = characterize_transition(df)
            uniq = sorted(set(prims))
            per_phi.append({
                "phi": ph, "primaries": prims, "uniq": uniq,
                "all_BR_artifact": uniq == ["BR_artifact"],
                "transition_detected": bool(ch["transition_detected"]),
                "shape": ch["shape_estimate"]})
        nullp = {ph: res.get(("null", NULL_LAM, N, ph)) for ph in PHIS}
        # φ-robustness + terminal logic
        tds = {pp.get("transition_detected") for pp in per_phi if "primaries" in pp}
        allbr = all(pp.get("all_BR_artifact") for pp in per_phi if "primaries" in pp)
        anytd = any(pp.get("transition_detected") for pp in per_phi if "primaries" in pp)
        labelsets = {tuple(pp["uniq"]) for pp in per_phi if "primaries" in pp}
        if not allbr and not anytd:
            term = "QUADRANT_DISTINGUISHABLE_AT_USE_N"   # uniform but NOT BR_artifact
        elif anytd:
            term = "QUADRANT_TRANSITION_DETECTED_AT_USE_N"  # a quadrant flip appears
        elif len(labelsets) > 1 or len(tds) > 1:
            term = "PHI_DEPENDENT"
        else:
            term = "NO_FP_N_PHI_STABLE"
        if term != "NO_FP_N_PHI_STABLE":
            overall = term if overall == "NO_FP_N_PHI_STABLE" else "MIXED"
        rec["per_N"].append({"N": N, "terminal": term,
            "all_phi_BR_artifact": allbr, "any_transition_detected": anytd,
            "phi_label_sets": [list(x) for x in labelsets],
            "transition_detected_set": list(tds),
            "alpha_null_primaries": nullp, "per_phi": per_phi})
        print(f"  N={N:7d} → {term} | all-φ BR_artifact={allbr} "
              f"any transition_detected={anytd} label-sets={[list(x) for x in labelsets]}",
              flush=True)
    rec["overall"] = overall; rec["total_s"] = round(time.time() - t0, 0)
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 86)
    print(f"  OVERALL: {overall}  [{rec['total_s']}s]")
    print("  (a) NO_FP_N_PHI_STABLE ⇒ seam closed, Step-1 stamp clean.")
    print("  (b) QUADRANT_DISTINGUISHABLE / _TRANSITION_DETECTED ⇒ test-meaning")
    print("      changes at use-N — honest re-frame, NOT a retraction of N=2584.")
    print("  (c) PHI_DEPENDENT / MIXED ⇒ φ-robustness fails — report honestly.")
    print("  Instrument seam-closure, NOT an AM discovery. brief-and-hold.")
    print("=" * 86)


if __name__ == "__main__":
    main()

"""
phase35a/sensitivity_confirm.py — Step-1 NON-CIRCULAR SENSITIVITY
CONFIRMATION at the pinned N (Will authorized 2026-05-19, "run it").

The no-false-positive half of 35b is banked-VALIDATED (non-circular).
This is the SENSITIVITY half — was on circular Phase-20.5 footing;
SENSITIVITY_NOT_ESTABLISHED at N=2584 (sup α-spread 0.556 ≫ gap 0.246).
The dense-in-log-N run pinned the lever: the EXACT criterion is robustly
True for N≳5×10⁴. This is the dedicated, pre-registered sensitivity
VERDICT run at that pinned N (NOT retro-read off the dense run, which
was scoped 'NOT a sensitivity re-verdict' — purpose-scoping discipline).

PRE-REGISTERED (discriminant_exact_question_check; this IS the verdict):
 EXACT QUESTION: at N in the dense-established ROBUST regime, does the
 sub-quadrant statistic separate the PROVEN subcritical (λ=0.5) vs
 supercritical (λ=1.5) regimes by more than the substrate-generated
 α-ensemble's own EXACT finite-N φ-spread?
 CODED TEST = the sharpening-run pre-registered EXACT criterion,
 VERBATIM UNCHANGED: per regime the exact period-0.5 α-ensemble
 (16 φ∈[0,0.5), L=1e5, golden θ) of W1δ; PASS iff ensembles strictly
 DISJOINT and inter-regime gap ≥ max(sub_spread, sup_spread). The
 SAME criterion that correctly FAILED at N=2584 — NOT a new
 discriminant. Only new choices: N∈{50000,70000,100000} (≥3, in the
 robust regime gap≥2·sup, deliberately NOT the thin-margin onset
 N*≈4.3e4 — no marginal cherry-pick); VERDICT = VALIDATED iff the
 criterion holds at ALL three N (conservative). Honest terminals:
 SENSITIVITY_VALIDATED_NON_CIRCULAR / SENSITIVITY_NOT_ESTABLISHED
 (if it fails at any N — report honestly, no softening).

Instrument-validation of transition_diagnostic's sensitivity (NOT an
AM discovery). MP 18w/24-core thread-pinned, pure deterministic ⇒
bit-identical-serial. brief-and-hold; Class II blocked; no §3.
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

WORKERS = 18
LAM = {"sub": 0.50, "sup": 1.50}
LITER = 100_000
PHIS = tuple(np.round(np.linspace(0.0, 0.5, 16, endpoint=False), 6))
NS = [50000, 70000, 100000]                       # robust regime; ≥3; not the onset
OUT = os.path.join(HERE, "sensitivity_confirm_results.json")


def task(arg):
    N, reg, lam, phi = arg
    try:
        e = am_eigs(lam, int(N), float(phi))
        return (N, reg, float(phi),
                float(W1d(unfold_rotnum(e, lam, GOLDEN, LITER, phis=(float(phi),)))),
                None)
    except Exception as ex:
        return (N, reg, float(phi), None, repr(ex))


def main():
    t0 = time.time()
    tasks = [(N, reg, LAM[reg], ph) for N in NS for reg in ("sub", "sup")
             for ph in PHIS]
    print("=" * 84)
    print(f"NON-CIRCULAR SENSITIVITY CONFIRMATION — {WORKERS}w, exact "
          f"sharpening criterion VERBATIM at pinned robust N={NS}")
    print(f"  λ_sub={LAM['sub']} λ_sup={LAM['sup']}, 16 φ∈[0,0.5), L={LITER}")
    print("=" * 84, flush=True)
    acc = {N: {"sub": {}, "sup": {}} for N in NS}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for f in as_completed([ex.submit(task, a) for a in tasks]):
            N, reg, ph, w, err = f.result()
            acc[N][reg][ph] = w
            if err:
                print(f"   ERROR N={N} {reg} φ={ph}: {err}", flush=True)
    rec = {"scoping_instrument_sensitivity": True, "exact_criterion": True,
           "criterion": "sharpening verbatim: disjoint AND gap>=max(sub_spread,"
           "sup_spread) on exact 16φ∈[0,0.5) α-ensemble",
           "lam": LAM, "L": LITER, "Ns": NS, "per_N": []}
    all_pass = True
    for N in NS:
        sv = np.array([acc[N]["sub"][p] for p in PHIS], float)
        pv = np.array([acc[N]["sup"][p] for p in PHIS], float)
        ss = float(sv.max() - sv.min()); sp = float(pv.max() - pv.min())
        gap = float(pv.min() - sv.max())
        disjoint = gap > 0
        crit = bool(disjoint and gap >= max(ss, sp))
        all_pass &= crit
        rec["per_N"].append({"N": N, "sub_spread": round(ss, 6),
            "sup_spread": round(sp, 6), "gap": round(gap, 6),
            "disjoint": disjoint, "gap_over_sup": round(gap / sp, 3) if sp else None,
            "PASS": crit})
        print(f"  N={N:7d} | sub_spread={ss:.5f} sup_spread={sp:.5f} "
              f"gap={gap:.5f} disjoint={disjoint} gap/sup={gap/sp:.2f} "
              f"→ {'PASS' if crit else 'FAIL'}", flush=True)
    verdict = ("SENSITIVITY_VALIDATED_NON_CIRCULAR" if all_pass else
               "SENSITIVITY_NOT_ESTABLISHED")
    rec["verdict"] = verdict; rec["total_s"] = round(time.time() - t0, 0)
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    print(f"  VERDICT: {verdict}  (criterion holds at ALL {len(NS)} N: "
          f"{all_pass})  [{rec['total_s']}s]")
    if all_pass:
        print("  ⇒ Step-1 35b sensitivity half now on NON-CIRCULAR footing")
        print("    (no-false-positive half already banked-VALIDATED).")
    print("  Instrument-validation of transition_diagnostic sensitivity, NOT")
    print("  an AM discovery. brief-and-hold; Class II blocked; no §3.")
    print("=" * 84)


if __name__ == "__main__":
    main()

"""
phase35a/highN_rate.py — Step-1 higher-N RATE run (Will authorized 2026-05-18).

Quantifies the lever's COST: unique ergodicity forces the α-null φ-spread→0
as N→∞ (the lever provably works — not in question); the decision figure
is the RATE / the N* at which the supercritical α-null φ-spread drops below
the regime gap, i.e. the N* at which the sharpening run's EXACT criterion
(disjoint AND gap ≥ larger within-regime φ-range) would flip to PASS.

This does NOT re-verdict sensitivity. SENSITIVITY_NOT_ESTABLISHED stands
at achievable N; this run only converts "non-trivial" into a number/range
so the "is non-circular sensitivity worth pursuing" decision is informed.
An actual high-N sensitivity confirmation at N* is a SEPARATE call — NOT
auto-run here.

EXACT path (memory discriminant_exact_question_check): the per-N φ-spread
is the exact deterministic period-0.5 family (machine-confirmed last run);
L-noise is ~φ-independent ⇒ does not inflate a max−min spread. The
extrapolation is an explicitly-flagged 3-point model: raw exact spreads
are primary, the fitted decay law is secondary/labeled, N* reported as
order-of-magnitude with the 3-point caveat — not false precision.

SCOPING / arc-finish. NOT a discovery, NOT §3, no stamping, Class II
blocked, brief-and-hold.
"""
from __future__ import annotations
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from unfold_rotnum import am_eigs, unfold_rotnum, W1d, GOLDEN

LAM_SUB, LAM_SUP = 0.50, 1.50
NS = [2584, 10000, 40000]                       # ~1.2 decades; bounded cost
LITER = 100_000                                  # spread ≫ L-noise; L-noise ~φ-indep
PHIS = list(np.round(np.linspace(0.0, 0.5, 16, endpoint=False), 5))  # exact period-0.5


def ensemble(lam, N):
    vals = []
    for phi in PHIS:
        e = am_eigs(lam, N, phi)
        vals.append(W1d(unfold_rotnum(e, lam, GOLDEN, LITER, phis=(phi,))))
    a = np.array(vals)
    return float(a.min()), float(a.max()), float(a.mean())


def run():
    print("=" * 80)
    print("HIGHER-N RATE RUN — exact α-null φ-spread vs N (cost of the lever)")
    print(f"  λ_sub={LAM_SUB} λ_sup={LAM_SUP} ; N={NS} ; L_iter={LITER} ; "
          f"|φ|={len(PHIS)} over [0,0.5)")
    print(f"  TARGET: N* where sup φ-spread < regime gap (sharpening EXACT "
          f"criterion → PASS). NOT a sensitivity re-verdict.")
    print("=" * 80)
    rows = []
    for N in NS:
        smn, smx, smean = ensemble(LAM_SUB, N)
        pmn, pmx, pmean = ensemble(LAM_SUP, N)
        sub_spread = smx - smn
        sup_spread = pmx - pmn
        gap = pmn - smx                          # >0 iff ensembles disjoint
        disjoint = gap > 0
        crit_pass = bool(disjoint and gap >= max(sub_spread, sup_spread))
        rows.append({"N": N, "sub_spread": round(sub_spread, 6),
                     "sup_spread": round(sup_spread, 6), "gap": round(gap, 6),
                     "disjoint": disjoint, "exact_criterion_pass": crit_pass,
                     "sub_mean": round(smean, 6), "sup_mean": round(pmean, 6)})
        print(f"  N={N:6d} | sub_spread={sub_spread:.5f} sup_spread={sup_spread:.5f} "
              f"gap={gap:.5f} disjoint={disjoint} EXACT-crit={'PASS' if crit_pass else 'FAIL'}",
              flush=True)

    # RATE: fit log(sup_spread) vs log(N) — power law sup_spread ≈ A·N^(−γ).
    Nv = np.array([r["N"] for r in rows], float)
    Sv = np.array([r["sup_spread"] for r in rows], float)
    Gv = np.array([r["gap"] for r in rows], float)
    gamma = A = Nstar = None
    fit_ok = bool(np.all(Sv > 0) and len(Nv) >= 2 and np.all(np.diff(Sv) != 0))
    if fit_ok:
        b, loga = np.polyfit(np.log(Nv), np.log(Sv), 1)
        gamma = float(-b); A = float(np.exp(loga))
        gap_ref = float(np.median(Gv))           # gap ≈ flat in N (sub tiny, sup mean ~const)
        if gamma > 1e-6 and A > gap_ref > 0:
            Nstar = float((A / gap_ref) ** (1.0 / gamma))
    # residual sanity: how well does the 3-pt power law actually fit?
    resid = (None if not fit_ok else
             round(float(np.max(np.abs(np.log(Sv) - (loga + b*np.log(Nv))))), 4))

    print("\n" + "=" * 80)
    print("RATE / N* (3-point extrapolation — EXPLICITLY a flagged model)")
    print(f"  raw EXACT sup φ-spreads (primary): "
          f"{[(r['N'], r['sup_spread']) for r in rows]}")
    print(f"  regime gap ≈ {np.median(Gv):.5f} (≈flat in N: sub tiny, sup mean ~const)")
    if gamma is not None:
        print(f"  power-law fit sup_spread ≈ {A:.4g}·N^(−{gamma:.3f})  "
              f"(3-pt; max log-resid {resid})")
        if Nstar is not None:
            order = int(np.floor(np.log10(Nstar)))
            print(f"  ⇒ N* (sup φ-spread = regime gap) ≈ 10^{order} "
                  f"(point est {Nstar:.3g}) — ORDER-OF-MAGNITUDE, 3-pt extrap, "
                  f"power-law-form ASSUMED; not precise.")
            feas = ("FEASIBLE (tridiagonal eigensolve O(N^2); ~minutes-class at "
                    "this order)" if order <= 6 else
                    "BORDERLINE (O(N^2) eigensolve heavy at this order)"
                    if order <= 8 else "INFEASIBLE at this order with O(N^2) solve")
            print(f"  feasibility of an actual sensitivity run at N*: {feas}")
        else:
            print("  N* not solvable from the fit (γ≈0 or A≤gap) — lever rate "
                  "not pinned by these N; report raw spreads, widen N if pursued.")
    else:
        print("  fit not well-posed on these points — report raw exact spreads only.")
    print("\n  This is the LEVER COST, not a sensitivity verdict. "
          "SENSITIVITY_NOT_ESTABLISHED stands. An actual run at N* = separate call.")
    print("=" * 80)
    json.dump({"scoping_arc_finish": True, "purpose": "lever cost / rate, NOT a "
               "sensitivity re-verdict", "rows": rows,
               "fit": {"power_law": fit_ok, "gamma": gamma, "A": A,
                       "max_log_resid": resid, "regime_gap_ref": float(np.median(Gv)),
                       "N_star_point": Nstar,
                       "caveat": "3-point extrapolation, power-law form assumed, "
                                 "order-of-magnitude only; raw exact spreads are "
                                 "primary"}},
              open(os.path.join(HERE, "highN_rate_results.json"), "w"), indent=1)


if __name__ == "__main__":
    run()

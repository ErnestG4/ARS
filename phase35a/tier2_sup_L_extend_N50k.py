"""
phase35a/tier2_sup_L_extend_N50k.py — Tier 2 at N=50k (Will
authorization 2026-05-20). Direct L-convergence measurement at the
sup load-bearing cell at N=50k; settles N=50k cell substrate
sup_spread directly (Sensitivity Tier 1 at this cell was model-based
via Test 1 ratio; this is the direct verification).

DESIGN. Mirror of Test 2 at N=50000 instead of N=70000:
- Single cell (δ=0.5, λ=1.5, N=50000).
- L ∈ {1.6e6, 6.4e6, 2.56e7}; two-phase cost-cap (8h budget).
- 16 φ ∈ [0,0.5); golden θ; ratio-free leg; WORKERS=18 local.
- Hardened (rawtable persist + 16-ckpt + analyze-only).

APPARATUS IDENTITY CHECK. At L=1.6e6 the 16 per-φ values must match
Test 1's stored values at the same cell (δ=0.5, λ=1.5, N=50000).
Tolerance: max(1e-6, 1e-4 × |stored max|). Halt as
`TIER2_N50K_INSTRUMENT_INCONSISTENT` on structural divergence.

PRE-REGISTERED TERMINALS (per Test 2 template).
- TIER2_N50K_SUP_L_CONVERGED: top_inc mean & spread both <5%.
- TIER2_N50K_SUP_L_STILL_DECAYING: top_inc ≥5% on at least one.
- TIER2_N50K_SUP_L_PATHOLOGICAL: non-monotone or other surprise.
- TIER2_N50K_INSTRUMENT_INCONSISTENT: apparatus check failed.

SCOPE. Single cell, sup-side, N=50k. Confirms/refines the
Sensitivity Tier 1 model-based result at this cell (Sensitivity Tier 1
said PASS by factor 1.96 with substrate sup_spread~0.191; Tier 2 will
return a direct substrate value to re-run the criterion). Never proves
(A)/(B); never decides §D; never adjudicates Step-1 verdicts
(sensitivity at N=50k stays Will's adjudication). Banked Step-1
untouched.

COST. ~4h estimated (Test 2 at N=70k was 5.6h; cost scales linearly
with N, so N=50k ≈ 5.6×5/7 ≈ 4h).
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
PHIS = tuple(np.round(np.linspace(0.0, 0.5, 16, endpoint=False), 6))
DELTA = 0.5
LAM = 1.0 + DELTA                                # 1.5 (sup, Step-1-direct)
N = 50000
LS_PHASE1 = (1600000, 6400000)
L_PHASE2 = 25600000
BUDGET_S = 8 * 3600
PROJECTION_FACTOR = 3.2
TOP_INC_CONVERGED = 0.05
ABS_TOL_FLOOR = 1e-6
REL_TOL_FRAC = 1e-4
OUT = os.path.join(HERE, "tier2_sup_L_extend_N50k_results.json")
RAW = os.path.join(HERE, "tier2_sup_L_extend_N50k_rawtable.json")
T1 = os.path.join(HERE, "test1_flipN_phi_results.json")
T1_RAW = os.path.join(HERE, "test1_flipN_phi_rawtable.json")


def cell(arg):
    L, phi = arg
    try:
        e = am_eigs(LAM, int(N), float(phi))
        w = float(W1d(unfold_rotnum(e, LAM, GOLDEN, int(L), phis=(float(phi),))))
        return (int(L), float(phi), w, None)
    except Exception as ex:
        return (int(L), float(phi), None, repr(ex))


def _dump_raw(table, total):
    recs = [[int(k[0]), float(k[1]), v] for k, v in table.items()]
    json.dump({"n": len(recs), "of": total, "recs": recs}, open(RAW, "w"))


def _load_raw():
    d = json.load(open(RAW))
    t = {}
    for L, ph, w in d["recs"]:
        t[(int(L), round(float(ph), 6))] = w
    return t, d.get("n", len(t)), d.get("of")


def phi_vec(table, L):
    v = [table.get((int(L), round(p, 6))) for p in PHIS]
    return None if any(x is None for x in v) else np.asarray(v, float)


def _t1_per_phi_at(N_target, L_target):
    """Get Test 1 per-φ values at (δ=0.5, leg=sup, N, L) from rawtable."""
    try:
        raw = json.load(open(T1_RAW))
        vals = {}
        for leg, n, l, ph, w in raw["recs"]:
            if leg == "sup" and int(n) == N_target and int(l) == L_target:
                vals[round(float(ph), 6)] = w
        if len(vals) == len(PHIS):
            return np.asarray([vals[round(p, 6)] for p in PHIS], float)
    except Exception:
        return None
    return None


def main():
    t0 = time.time()
    print("=" * 84)
    print(f"TIER 2 @N=50k — sup-side L-extension — {WORKERS}w ; AM golden θ ; "
          f"ratio-free leg")
    print(f"  cell (δ={DELTA}, λ={LAM}, N={N}) ; phase1 L={LS_PHASE1} ; "
          f"phase2 L={L_PHASE2} (conditional)")
    print(f"  budget={BUDGET_S}s ({BUDGET_S/3600:.1f}h)  "
          f"phase2_projection_factor=×{PROJECTION_FACTOR}")
    print("=" * 84, flush=True)

    errs, table = [], None
    if os.path.exists(RAW):
        tr, nr, ofr = _load_raw()
        if nr == ofr and nr in (16 * 2, 16 * 3):
            table = tr
            print(f"  ANALYZE-ONLY: complete raw ({nr}).", flush=True)
    if table is None:
        phase1_tasks = [(L, p) for L in LS_PHASE1 for p in PHIS]
        table, done = {}, 0
        t_p1 = time.time()
        with ProcessPoolExecutor(max_workers=WORKERS) as ex:
            for f in as_completed([ex.submit(cell, a) for a in phase1_tasks]):
                L, phi, w, err = f.result()
                table[(int(L), round(phi, 6))] = w
                done += 1
                if err:
                    errs.append({"L": L, "phi": phi, "err": err})
                    print(f"  ERR L={L} φ={phi}: {err}", flush=True)
                if done % 16 == 0:
                    _dump_raw(table, len(phase1_tasks))
                    print(f"  phase1 … {done}/{len(phase1_tasks)} "
                          f"[{time.time()-t0:.0f}s]", flush=True)
        p1_elapsed = time.time() - t_p1
        print(f"  phase1 done in {p1_elapsed:.0f}s ({p1_elapsed/60:.1f} min)",
              flush=True)
        proj_p2 = PROJECTION_FACTOR * p1_elapsed
        total_proj = (time.time() - t0) + proj_p2
        run_p2 = total_proj <= BUDGET_S
        print(f"  cost-cap: projected phase2 ≈ {proj_p2:.0f}s "
              f"({proj_p2/3600:.2f}h); projected total = "
              f"{total_proj:.0f}s ({total_proj/3600:.2f}h); "
              f"budget = {BUDGET_S}s; run_phase2 = {run_p2}", flush=True)
        if run_p2:
            p2_tasks = [(L_PHASE2, p) for p in PHIS]
            with ProcessPoolExecutor(max_workers=WORKERS) as ex:
                for f in as_completed([ex.submit(cell, a) for a in p2_tasks]):
                    L, phi, w, err = f.result()
                    table[(int(L), round(phi, 6))] = w
                    done += 1
                    if err:
                        errs.append({"L": L, "phi": phi, "err": err})
                        print(f"  ERR L={L} φ={phi}: {err}", flush=True)
                    if done % 16 == 0:
                        _dump_raw(table, len(phase1_tasks) + len(p2_tasks))
                        print(f"  phase2 … {done}/"
                              f"{len(phase1_tasks)+len(p2_tasks)} "
                              f"[{time.time()-t0:.0f}s]", flush=True)
            _dump_raw(table, len(phase1_tasks) + len(p2_tasks))
        else:
            print("  PHASE 2 SKIPPED per cost-cap.", flush=True)
            _dump_raw(table, len(phase1_tasks))
        print(f"  raw persisted ({len(table)}).", flush=True)

    available_L = sorted([L for L in (LS_PHASE1 + (L_PHASE2,))
                          if phi_vec(table, L) is not None])
    if not available_L:
        rec = {"run": "Tier 2 sup L-extend @N=50k", "terminal": "TIER2_ERROR",
               "errors": errs, "total_s": round(time.time() - t0, 0)}
        json.dump(rec, open(OUT, "w"), indent=1); print("no L"); return
    L_top = available_L[-1]
    L_2nd = available_L[-2] if len(available_L) >= 2 else None

    # ── Apparatus identity check vs Test 1 at L=1.6e6 ──────────────
    id_report = {}; id_ok = True
    if 1600000 in available_L:
        meas = phi_vec(table, 1600000)
        stored = _t1_per_phi_at(50000, 1600000)
        if meas is None or stored is None:
            id_ok = False
            id_report["L1.6e6_per_phi"] = {"error": "missing baseline"}
        else:
            tol = max(ABS_TOL_FLOOR, REL_TOL_FRAC * float(np.max(np.abs(stored))))
            diff = float(np.max(np.abs(meas - stored)))
            ok = diff <= tol
            id_report["L1.6e6_per_phi"] = {"max_abs_diff": round(diff, 12),
                                            "tol": round(tol, 12),
                                            "PASS": bool(ok)}
            id_ok = id_ok and ok

    if not id_ok:
        rec = {"run": "Tier 2 sup L-extend @N=50k",
               "terminal": "TIER2_N50K_INSTRUMENT_INCONSISTENT",
               "apparatus_identity": id_report,
               "errors": errs, "total_s": round(time.time() - t0, 0)}
        json.dump(rec, open(OUT, "w"), indent=1)
        print("=" * 84); print(f"  IDENTITY FAILED: {id_report}")
        print(f"  TERMINAL: TIER2_N50K_INSTRUMENT_INCONSISTENT  HALT.")
        print("=" * 84); return

    per_L = {L: phi_vec(table, L) for L in available_L}
    means = {L: float(per_L[L].mean()) for L in available_L}
    spreads = {L: float(np.ptp(per_L[L])) for L in available_L}

    converged, top_inc_m, top_inc_s = None, None, None
    if L_2nd is not None:
        top_inc_m = abs(means[L_top] - means[L_2nd]) / max(abs(means[L_top]), 1e-12)
        top_inc_s = abs(spreads[L_top] - spreads[L_2nd]) / max(abs(spreads[L_top]), 1e-12)
        converged = top_inc_m < TOP_INC_CONVERGED and top_inc_s < TOP_INC_CONVERGED

    mean_seq = [means[L] for L in available_L]
    spread_seq = [spreads[L] for L in available_L]
    ms = [mean_seq[i+1] - mean_seq[i] for i in range(len(mean_seq) - 1)]
    ss = [spread_seq[i+1] - spread_seq[i] for i in range(len(spread_seq) - 1)]
    mm = (all(x >= 0 for x in ms) or all(x <= 0 for x in ms))
    sm = (all(x >= 0 for x in ss) or all(x <= 0 for x in ss))
    poisson = 2.0 / np.e
    pathology = []
    if any(m > poisson * 1.05 for m in mean_seq): pathology.append("mean_overshoots_Poisson")
    if not sm and (max(spread_seq) - min(spread_seq) > 0.05 * max(spread_seq)):
        pathology.append("spread_non_monotone_significant")
    if not mm and (max(mean_seq) - min(mean_seq) > 0.05 * max(abs(x) for x in mean_seq)):
        pathology.append("mean_non_monotone_significant")

    alpha_m, alpha_s = None, None
    if len(available_L) >= 2:
        try:
            lx = np.log(np.array(available_L, float))
            alpha_m = float(-np.polyfit(lx, np.log(np.abs(np.array(mean_seq))), 1)[0])
            alpha_s = float(-np.polyfit(lx, np.log(np.abs(np.array(spread_seq))), 1)[0])
        except Exception: pass

    if pathology:
        terminal = "TIER2_N50K_SUP_L_PATHOLOGICAL"
    elif converged is True:
        terminal = "TIER2_N50K_SUP_L_CONVERGED"
    else:
        terminal = "TIER2_N50K_SUP_L_STILL_DECAYING"

    # ── Sensitivity criterion re-run with direct substrate ─────────
    # Sensitivity_confirm stored: gap=0.374969 sub_spread=0.000292 at N=50k
    GAP_50K = 0.374969; SUB_50K = 0.000292
    sup_substrate_direct = spreads[L_top]
    max_sp = max(SUB_50K, sup_substrate_direct)
    crit_pass = bool(GAP_50K > 0 and GAP_50K >= max_sp)
    crit_ratio = GAP_50K / max_sp if max_sp > 0 else None

    rec = {"run": "Tier 2 sup-side L-extension @N=50k",
           "cell": {"delta": DELTA, "lam": LAM, "N": N},
           "L_actual": available_L, "L_top": L_top,
           "apparatus_identity": id_report,
           "means_by_L": {str(L): round(means[L], 8) for L in available_L},
           "spreads_by_L": {str(L): round(spreads[L], 8) for L in available_L},
           "top_inc_mean": round(top_inc_m, 6) if top_inc_m is not None else None,
           "top_inc_spread": round(top_inc_s, 6) if top_inc_s is not None else None,
           "converged": converged,
           "monotone_mean": mm, "monotone_spread": sm,
           "pathology_flags": pathology,
           "loglog_alpha_mean": round(alpha_m, 4) if alpha_m is not None else None,
           "loglog_alpha_spread": round(alpha_s, 4) if alpha_s is not None else None,
           "phi_per_L": {str(L): [round(float(x), 9) for x in per_L[L]]
                          for L in available_L},
           "sensitivity_criterion_at_N50k_with_direct_substrate": {
               "stored_gap": GAP_50K, "stored_sub_spread": SUB_50K,
               "direct_substrate_sup_spread": sup_substrate_direct,
               "max_spread": max_sp, "gap_over_max": round(crit_ratio, 3)
                                                       if crit_ratio else None,
               "criterion_PASS": crit_pass,
               "tier1_model_predicted_PASS": True,
               "agreement": ("model_confirmed" if crit_pass else
                              "model_disconfirmed")},
           "terminal": terminal,
           "errors": errs, "total_s": round(time.time() - t0, 0),
           "note": "Tier 2 at N=50k. Direct substrate sup_spread now "
                   "measured (not model-extrapolated). Sensitivity criterion "
                   "at N=50k re-evaluated with direct substrate. SURFACED; "
                   "never adjudicates Step-1; banked Step-1 untouched."}
    json.dump(rec, open(OUT, "w"), indent=1)

    print("\n" + "=" * 84)
    print(f"  IDENTITY @L=1.6e6 vs Test 1: {id_report}")
    print(f"  L_actual = {available_L}  (top = {L_top})")
    for L in available_L:
        print(f"  L={L:>10d}: mean={means[L]:.6f}  spread={spreads[L]:.6f}")
    print(f"  top_inc mean={rec['top_inc_mean']}  spread={rec['top_inc_spread']}  "
          f"converged={converged}")
    print(f"  α(mean)={rec['loglog_alpha_mean']}  α(spread)={rec['loglog_alpha_spread']}  "
          f"monotone mean={mm} spread={sm}  pathology={pathology}")
    print(f"  TERMINAL (L-conv): {terminal}")
    print(f"  Sensitivity criterion @N=50k (DIRECT substrate):")
    print(f"    gap={GAP_50K}  sub_spread={SUB_50K}  "
          f"sup_substrate_direct={sup_substrate_direct:.6f}  "
          f"max={max_sp:.6f}  gap/max={crit_ratio}  → "
          f"{'PASS' if crit_pass else 'FAIL'}")
    print(f"  Sensitivity Tier 1 (model) predicted PASS; direct: "
          f"{'CONFIRMED' if crit_pass else 'DISCONFIRMED'}")
    print(f"  [{rec['total_s']}s] errors={len(errs)}")
    print("  SURFACED; Step-1/(A)/(B)/§D untouched.")
    print("=" * 84)


if __name__ == "__main__":
    main()

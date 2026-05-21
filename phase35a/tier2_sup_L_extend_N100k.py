"""
phase35a/tier2_sup_L_extend_N100k.py — Tier 2 at N=100k (Will
authorization 2026-05-20, rev-5.1 §12 item 5). Direct L-convergence
at the sup load-bearing cell at N=100k; replaces the §10 "≈ 1×
inferential" entry with measurement. Closes cell-granular banking on
the no-FP half (third directly-measured (N, L) point).

DESIGN. Mirror Tier 2 @N=50k (`tier2_sup_L_extend_N50k.py`) with
N=100000 instead of N=50000, plus L=1e5 folded into the ladder for
apparatus identity (no Test 1/bh22pfzoa baseline exists at N=100k
sup at L=1.6e6).

- Single cell (δ=0.5, λ=1.5, N=100000).
- L ∈ {1e5, 1.6e6, 6.4e6, 2.56e7} — L=1e5 added for identity check
  vs sensitivity_confirm's stored sup_spread@N=100k. Free bonus:
  4-tier L-trajectory cleanly characterizes WHERE the L-transition
  lives at N=100k (compare to N=70k: transition 1e5→1.6e6 was 4.6×;
  N=50k: transition essentially absent 1e5→2.56e7).
- Two-phase cost-cap: phase1 {1e5, 1.6e6, 6.4e6}, phase2 {2.56e7}.
- 16 φ ∈ [0,0.5); golden θ; ratio-free leg; WORKERS=18 local.
- Hardened (rawtable persist + 16-ckpt + analyze-only).

APPARATUS IDENTITY CHECK. spread@L=1e5 measured here vs stored
sensitivity_confirm sup_spread@N=100k = 0.007146. Tolerance
REL_TOL=1e-3 + ABS_TOL_FLOOR=1e-6 (mirrors Test 1's pattern,
accounts for 6-decimal stored rounding).

PRE-REGISTERED TERMINALS.
- TIER2_N100K_SUP_L_CONVERGED: top_inc mean & spread < 5%.
- TIER2_N100K_SUP_L_STILL_DECAYING.
- TIER2_N100K_SUP_L_PATHOLOGICAL.
- TIER2_N100K_INSTRUMENT_INCONSISTENT (apparatus failed).

POST-PROCESSING: re-evaluate sensitivity criterion @N=100k with
direct substrate; compare to the rev-5.1 inferential PASS; report
N=100k growth factor (substrate/stored) for the (N=50k:0.93×,
N=70k:4.99×, N=100k:??) growth-factor pattern that's the headline
N-localized finding.

COST. ~4.5h estimate (scales linearly with N from box6iq1j4 2.2h
at N=50k; N=100k is 2×; +16 trivial L=1e5 tasks adds <5 min).

SCOPE. Single cell, sup-side, N=100k. Settles the N=100k cell directly,
closes inferential gap. Never proves (A)/(B); never decides §D; never
adjudicates Step-1 verdicts (your call). Banked Step-1 untouched.
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
LAM = 1.0 + DELTA
N = 100000
LS_PHASE1 = (100000, 1600000, 6400000)
L_PHASE2 = 25600000
BUDGET_S = 8 * 3600
PROJECTION_FACTOR = 4.0    # 2.56e7 ≈ 4× 6.4e6 cost; phase1 totals ~5.05× 1.6e6 cost
                            # (1e5≈0.0625× + 1.6e6=1× + 6.4e6=4×); phase2 = 16×;
                            # phase2 / phase1 ≈ 16/5.05 ≈ 3.17 — use 4.0 conservatively
TOP_INC_CONVERGED = 0.05
ABS_TOL_FLOOR = 1e-6
REL_TOL_FRAC = 1e-3       # account for sensitivity_confirm 6-decimal rounding
OUT = os.path.join(HERE, "tier2_sup_L_extend_N100k_results.json")
RAW = os.path.join(HERE, "tier2_sup_L_extend_N100k_rawtable.json")
SENS = os.path.join(HERE, "sensitivity_confirm_results.json")


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


def _sens_sup_spread(N_target):
    try:
        r = json.load(open(SENS))
        for row in r["per_N"]:
            if row["N"] == N_target:
                return float(row["sup_spread"])
    except Exception:
        return None
    return None


def main():
    t0 = time.time()
    print("=" * 84)
    print(f"TIER 2 @N=100k — sup-side L-extension — {WORKERS}w ; AM golden θ ; "
          f"ratio-free leg")
    print(f"  cell (δ={DELTA}, λ={LAM}, N={N}) ; phase1 L={LS_PHASE1} ; "
          f"phase2 L={L_PHASE2} (conditional)")
    print(f"  budget={BUDGET_S}s ({BUDGET_S/3600:.1f}h)  "
          f"phase2_projection_factor=×{PROJECTION_FACTOR}")
    print(f"  L=1e5 included for apparatus identity vs sensitivity_confirm")
    print("=" * 84, flush=True)

    errs, table = [], None
    if os.path.exists(RAW):
        tr, nr, ofr = _load_raw()
        if nr == ofr and nr in (16 * 3, 16 * 4):
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
              f"({proj_p2/3600:.2f}h); total = {total_proj:.0f}s "
              f"({total_proj/3600:.2f}h); budget = {BUDGET_S}s; "
              f"run_phase2 = {run_p2}", flush=True)
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
        rec = {"run": "Tier 2 sup L-extend @N=100k", "terminal": "TIER2_ERROR",
               "errors": errs, "total_s": round(time.time() - t0, 0)}
        json.dump(rec, open(OUT, "w"), indent=1); print("no L"); return
    L_top = available_L[-1]
    L_2nd = available_L[-2] if len(available_L) >= 2 else None

    # Apparatus identity: spread@L=1e5 vs sensitivity_confirm stored
    id_report = {}; id_ok = True
    if 100000 in available_L:
        meas = phi_vec(table, 100000)
        meas_spread = float(np.ptp(meas))
        stored = _sens_sup_spread(100000)
        if stored is None:
            id_ok = False
            id_report["L1e5_spread"] = {"error": "missing sensitivity_confirm"}
        else:
            tol = max(ABS_TOL_FLOOR, REL_TOL_FRAC * float(stored))
            diff = abs(meas_spread - stored)
            ok = diff <= tol
            id_report["L1e5_spread"] = {"measured": round(meas_spread, 9),
                                          "stored": round(stored, 9),
                                          "abs_diff": round(diff, 9),
                                          "tol": round(tol, 9),
                                          "PASS": bool(ok)}
            id_ok = id_ok and ok

    if not id_ok:
        rec = {"run": "Tier 2 sup L-extend @N=100k",
               "terminal": "TIER2_N100K_INSTRUMENT_INCONSISTENT",
               "apparatus_identity": id_report,
               "errors": errs, "total_s": round(time.time() - t0, 0)}
        json.dump(rec, open(OUT, "w"), indent=1)
        print("=" * 84); print(f"  IDENTITY FAILED: {id_report}")
        print(f"  TERMINAL: TIER2_N100K_INSTRUMENT_INCONSISTENT  HALT.")
        print("=" * 84); return

    per_L = {L: phi_vec(table, L) for L in available_L}
    means = {L: float(per_L[L].mean()) for L in available_L}
    spreads = {L: float(np.ptp(per_L[L])) for L in available_L}

    converged, top_inc_m, top_inc_s = None, None, None
    if L_2nd is not None and L_top in spreads and L_2nd in spreads:
        # Compute top_inc using only the >=1.6e6 tail (skip L=1e5 since it's
        # for identity, not convergence)
        tail = [L for L in available_L if L >= 1600000]
        if len(tail) >= 2:
            top = tail[-1]; second = tail[-2]
            top_inc_m = abs(means[top] - means[second]) / max(abs(means[top]), 1e-12)
            top_inc_s = abs(spreads[top] - spreads[second]) / max(abs(spreads[top]), 1e-12)
            converged = top_inc_m < TOP_INC_CONVERGED and top_inc_s < TOP_INC_CONVERGED

    # Monotonicity / pathology checks: run on the convergence TAIL only
    # (L ≥ 1.6e6), matching top_inc's scope. The L=1e5 → 1.6e6 transition
    # is where the L-artifact lives; including it would over-flag the
    # mean-non-monotone check (per Test 2 at N=70k: mean dropped sharply
    # 1e5 → 1.6e6, then stable). L=1e5 is for identity check / growth-factor
    # computation, not convergence/pathology assessment.
    tail_Ls = [L for L in available_L if L >= 1600000]
    mean_seq = [means[L] for L in tail_Ls]
    spread_seq = [spreads[L] for L in tail_Ls]
    ms = [mean_seq[i+1] - mean_seq[i] for i in range(len(mean_seq) - 1)]
    ss = [spread_seq[i+1] - spread_seq[i] for i in range(len(spread_seq) - 1)]
    mm = (all(x >= 0 for x in ms) or all(x <= 0 for x in ms))
    sm = (all(x >= 0 for x in ss) or all(x <= 0 for x in ss))
    poisson = 2.0 / np.e
    pathology = []
    if any(m > poisson * 1.05 for m in mean_seq):
        pathology.append("mean_overshoots_Poisson")
    if not sm and (max(spread_seq) - min(spread_seq) > 0.05 * max(spread_seq)):
        pathology.append("spread_non_monotone_significant")
    if not mm and (max(mean_seq) - min(mean_seq) > 0.05 * max(abs(x) for x in mean_seq)):
        pathology.append("mean_non_monotone_significant")

    alpha_m, alpha_s = None, None
    if len(tail_Ls) >= 2:
        try:
            lx = np.log(np.array(tail_Ls, float))
            alpha_m = float(-np.polyfit(lx, np.log(np.abs(np.array(mean_seq))), 1)[0])
            alpha_s = float(-np.polyfit(lx, np.log(np.abs(np.array(spread_seq))), 1)[0])
        except Exception: pass

    if pathology:
        terminal = "TIER2_N100K_SUP_L_PATHOLOGICAL"
    elif converged is True:
        terminal = "TIER2_N100K_SUP_L_CONVERGED"
    else:
        terminal = "TIER2_N100K_SUP_L_STILL_DECAYING"

    # Sensitivity criterion re-run at N=100k with direct substrate
    GAP_100K = 0.496135; SUB_100K = 0.000146
    sup_substrate_direct = spreads[L_top]
    max_sp = max(SUB_100K, sup_substrate_direct)
    crit_pass = bool(GAP_100K > 0 and GAP_100K >= max_sp)
    crit_ratio = GAP_100K / max_sp if max_sp > 0 else None

    # Growth factor: substrate / stored
    stored_at_1e5 = spreads.get(100000)   # measured L=1e5 spread = same as stored
    growth_factor = (sup_substrate_direct / stored_at_1e5
                      if stored_at_1e5 and stored_at_1e5 > 0 else None)

    rec = {"run": "Tier 2 sup-side L-extension @N=100k",
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
           "sensitivity_criterion_at_N100k_with_direct_substrate": {
               "stored_gap": GAP_100K, "stored_sub_spread": SUB_100K,
               "direct_substrate_sup_spread": sup_substrate_direct,
               "max_spread": max_sp,
               "gap_over_max": round(crit_ratio, 3) if crit_ratio else None,
               "criterion_PASS": crit_pass,
               "rev5_1_inferential_predicted_PASS": True,
               "agreement": ("inference_confirmed" if crit_pass else
                              "inference_disconfirmed")},
           "growth_factor_substrate_over_L1e5": (round(growth_factor, 4)
                                                   if growth_factor else None),
           "growth_factor_pattern": {"N=50k": 0.93, "N=70k": 4.99,
                                      "N=100k": (round(growth_factor, 4)
                                                  if growth_factor else None)},
           "terminal": terminal,
           "errors": errs, "total_s": round(time.time() - t0, 0),
           "note": "Tier 2 at N=100k. Direct measurement at L-converged "
                   "replaces rev-5.1 inferential ≈1× entry. Closes "
                   "cell-granular banking on no-FP half. Never adjudicates "
                   "Step-1; banked Step-1 untouched."}
    json.dump(rec, open(OUT, "w"), indent=1)

    print("\n" + "=" * 84)
    print(f"  IDENTITY @L=1e5 vs sensitivity_confirm: {id_report}")
    print(f"  L_actual = {available_L}  (top = {L_top})")
    for L in available_L:
        print(f"  L={L:>10d}: mean={means[L]:.6f}  spread={spreads[L]:.6f}")
    print(f"  top_inc (over L≥1.6e6): mean={rec['top_inc_mean']}  "
          f"spread={rec['top_inc_spread']}  converged={converged}")
    print(f"  α(mean)={rec['loglog_alpha_mean']}  α(spread)={rec['loglog_alpha_spread']}  "
          f"monotone mean={mm} spread={sm}  pathology={pathology}")
    print(f"  TERMINAL (L-conv): {terminal}")
    print(f"  Sensitivity criterion @N=100k (DIRECT substrate):")
    print(f"    gap={GAP_100K}  sub_spread={SUB_100K}  "
          f"sup_substrate_direct={sup_substrate_direct:.6f}")
    print(f"    max={max_sp:.6f}  gap/max={crit_ratio}  → "
          f"{'PASS' if crit_pass else 'FAIL'}")
    print(f"  rev-5.1 inferential predicted PASS; direct: "
          f"{'CONFIRMED' if crit_pass else 'DISCONFIRMED'}")
    print(f"  Growth-factor pattern: N=50k:0.93×  N=70k:4.99×  "
          f"N=100k:{growth_factor:.2f}× — pathology-landscape data point")
    print(f"  [{rec['total_s']}s] errors={len(errs)}")
    print("  SURFACED; Step-1/(A)/(B)/§D untouched.")
    print("=" * 84)


if __name__ == "__main__":
    main()

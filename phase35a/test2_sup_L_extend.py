"""
phase35a/test2_sup_L_extend.py — Test 2 from Slate Unit 3 brief.
PREPARED + smoke-verified. Launched as #3 in the overnight chain.

QUESTION (per the slate-3 brief). What is the converged sup-side
magnitude at the b0haqgof3 load-bearing cell (δ=0.5, λ=1.5, N=70k)?
Converts the 4.86× lower bound to a tight estimate for verdict math.

DESIGN (locked, two-phase to enforce 8h cost-cap).
- Single cell: (δ=0.5, λ=1.5), N=70000 (b0haqgof3 load-bearing).
- L-ladder: {1.6e6, 6.4e6, 2.56e7} — extends b0haqgof3 by ×16.
- 16 φ ∈ [0,0.5); golden θ; ratio-free leg; WORKERS=18 local.
- Hardened (rawtable persist + 16-ckpt + analyze-only).

COST-CAP PROTOCOL (per brief).
- Phase 1: submit L ∈ {1.6e6, 6.4e6} (32 tasks). Wait.
- Decision: project Phase 2 cost = 3.2 × Phase 1 elapsed
  (Sturm cost ∝ L; L=2.56e7 = 4× L=6.4e6 and Phase 1 ≈ T_1.6e6 + 4T_1.6e6 = 5T_1.6e6,
  so T_2.56e7 = 4×T_6.4e6 = 16×T_1.6e6 = 16/5 × Phase1 = 3.2 × Phase1).
- If elapsed + 3.2×Phase1 > 8h budget, SKIP L=2.56e7 and report with
  top L = 6.4e6 and `SUP_L_STILL_DECAYING`.
- Else Phase 2: submit L=2.56e7 (16 tasks). Proceed.

APPARATUS IDENTITY CHECK. At L=1.6e6, the 16 per-φ values must match
b0haqgof3's stored values at the same cell to bit-determinism.
Tolerance: max(1e-9, 1e-4 × stored_max). Halt as
`SUP_L_INSTRUMENT_INCONSISTENT` on structural divergence.

PRE-REGISTERED TERMINALS (per brief).
- SUP_L_CONVERGED: at L_top (2.56e7 if available else 6.4e6), both
  mean and spread stable within 5% relative to L=6.4e6 (or 1.6e6 if
  only one extra L was reached).
- SUP_L_STILL_DECAYING: top_inc ≥ 0.05 on at least one (mean or
  spread). Report α-exponents per quantity separately.
- SUP_L_PATHOLOGICAL: non-monotone trajectory, spread reaches max
  then decreases, mean overshoots Poisson, etc.
- SUP_L_INSTRUMENT_INCONSISTENT: apparatus check failed.

SCOPE. Sup load-bearing cell only. Never proves (A)/(B); never
decides §D; never adjudicates Step-1; banked Step-1 untouched.
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
LAM = 1.0 + DELTA                                # 1.5 (Step-1 sup-direct)
N = 70000
LS_PHASE1 = (1600000, 6400000)
L_PHASE2 = 25600000                              # 2.56e7
BUDGET_S = 8 * 3600                              # 8h cost cap
PROJECTION_FACTOR = 3.2                          # phase-2 / phase-1 cost ratio
TOP_INC_CONVERGED = 0.05                         # relative top-inc threshold
ABS_TOL_FLOOR = 1e-9
REL_TOL_FRAC = 1e-4
OUT = os.path.join(HERE, "test2_sup_L_extend_results.json")
RAW = os.path.join(HERE, "test2_sup_L_extend_rawtable.json")
B0HA = os.path.join(HERE, "sup_phi_resolved_L_results.json")


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


def _b0haqgof3_at(L):
    """b0haqgof3 per-φ at (δ=0.5, N=70k, L). Returns array or None."""
    try:
        r = json.load(open(B0HA))
        for p in r["per_cell"]:
            if p.get("delta") == 0.5 and p.get("N") == 70000:
                arr = p["phi_W1d_per_L"].get(str(L))
                return np.asarray(arr, float) if arr else None
    except Exception:
        return None
    return None


def main():
    t0 = time.time()
    print("=" * 84)
    print(f"TEST 2 — sup-side L-extension — {WORKERS}w ; AM golden θ ; "
          f"ratio-free leg")
    print(f"  cell (δ={DELTA}, λ={LAM}, N={N}) ; phase1 L={LS_PHASE1} ; "
          f"phase2 L={L_PHASE2} (conditional) ; {len(PHIS)}φ")
    print(f"  budget={BUDGET_S}s ({BUDGET_S/3600:.1f}h)  "
          f"phase2_projection_factor=×{PROJECTION_FACTOR}")
    print("=" * 84, flush=True)

    errs, table = [], None
    if os.path.exists(RAW):
        tr, nr, ofr = _load_raw()
        # any complete tier set we can use; allow phase1-only resume too
        if nr == ofr and nr in (16 * 2, 16 * 3):
            table = tr
            print(f"  ANALYZE-ONLY: complete raw ({nr}) — skip compute.",
                  flush=True)
    if table is None:
        # ── Phase 1: L ∈ LS_PHASE1
        phase1_tasks = [(L, p) for L in LS_PHASE1 for p in PHIS]
        table, done = {}, 0
        t_phase1_start = time.time()
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
        phase1_elapsed = time.time() - t_phase1_start
        print(f"  phase1 done in {phase1_elapsed:.0f}s "
              f"({phase1_elapsed/60:.1f} min)", flush=True)

        # ── Cost-cap decision
        projected_phase2 = PROJECTION_FACTOR * phase1_elapsed
        total_projected = (time.time() - t0) + projected_phase2
        run_phase2 = total_projected <= BUDGET_S
        print(f"  cost-cap: projected phase2 ≈ {projected_phase2:.0f}s "
              f"({projected_phase2/3600:.2f}h); projected total = "
              f"{total_projected:.0f}s ({total_projected/3600:.2f}h); "
              f"budget = {BUDGET_S}s; run_phase2 = {run_phase2}",
              flush=True)

        # ── Phase 2 (conditional)
        if run_phase2:
            phase2_tasks = [(L_PHASE2, p) for p in PHIS]
            with ProcessPoolExecutor(max_workers=WORKERS) as ex:
                for f in as_completed([ex.submit(cell, a)
                                        for a in phase2_tasks]):
                    L, phi, w, err = f.result()
                    table[(int(L), round(phi, 6))] = w
                    done += 1
                    if err:
                        errs.append({"L": L, "phi": phi, "err": err})
                        print(f"  ERR L={L} φ={phi}: {err}", flush=True)
                    if done % 16 == 0:
                        _dump_raw(table, len(phase1_tasks) + len(phase2_tasks))
                        print(f"  phase2 … {done}/"
                              f"{len(phase1_tasks)+len(phase2_tasks)} "
                              f"[{time.time()-t0:.0f}s]", flush=True)
            _dump_raw(table, len(phase1_tasks) + len(phase2_tasks))
        else:
            print("  PHASE 2 SKIPPED per cost-cap (budget protection).",
                  flush=True)
            _dump_raw(table, len(phase1_tasks))
        print(f"  raw persisted ({len(table)}) — postproc free to re-run.",
              flush=True)

    # ── Determine actual L-ladder run
    available_L = sorted([L for L in (LS_PHASE1 + (L_PHASE2,))
                          if phi_vec(table, L) is not None])
    if not available_L:
        rec = {"run": "Test 2 sup L-extend", "terminal": "TEST2_ERROR",
               "errors": errs, "total_s": round(time.time() - t0, 0),
               "note": "no complete L-tier"}
        json.dump(rec, open(OUT, "w"), indent=1)
        print("ERROR — no complete L-tier."); return

    L_top = available_L[-1]
    L_2nd = available_L[-2] if len(available_L) >= 2 else None

    # ── Apparatus identity check vs b0haqgof3 at L=1.6e6
    id_report = {}
    id_ok = True
    if 1600000 in available_L:
        meas = phi_vec(table, 1600000)
        stored = _b0haqgof3_at(1600000)
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
        rec = {"run": "Test 2 sup L-extend",
               "terminal": "SUP_L_INSTRUMENT_INCONSISTENT",
               "apparatus_identity": id_report,
               "errors": errs, "total_s": round(time.time() - t0, 0),
               "note": "Apparatus identity vs b0haqgof3 failed. HALT."}
        json.dump(rec, open(OUT, "w"), indent=1)
        print("=" * 84)
        print(f"  APPARATUS IDENTITY: FAILED")
        print(f"  TERMINAL: SUP_L_INSTRUMENT_INCONSISTENT  HALT.")
        print("=" * 84); return

    # ── Per-L means, spreads, fitted α exponents
    per_L = {L: phi_vec(table, L) for L in available_L}
    means = {L: float(per_L[L].mean()) for L in available_L}
    spreads = {L: float(np.ptp(per_L[L])) for L in available_L}

    # ── Convergence test: top_inc on mean and spread between L_top and L_2nd
    converged, top_inc_mean, top_inc_spread = None, None, None
    if L_2nd is not None:
        top_inc_mean = abs(means[L_top] - means[L_2nd]) / max(abs(means[L_top]), 1e-12)
        top_inc_spread = abs(spreads[L_top] - spreads[L_2nd]) / max(abs(spreads[L_top]), 1e-12)
        converged = (top_inc_mean < TOP_INC_CONVERGED
                     and top_inc_spread < TOP_INC_CONVERGED)

    # ── Monotonicity / pathology check
    mean_seq = [means[L] for L in available_L]
    spread_seq = [spreads[L] for L in available_L]
    mean_steps = [mean_seq[i+1] - mean_seq[i] for i in range(len(mean_seq) - 1)]
    spread_steps = [spread_seq[i+1] - spread_seq[i] for i in range(len(spread_seq) - 1)]
    mean_mono = (all(s >= 0 for s in mean_steps) or all(s <= 0 for s in mean_steps))
    spread_mono = (all(s >= 0 for s in spread_steps) or all(s <= 0 for s in spread_steps))
    # Pathology: mean overshoots Poisson (>0.736) or spread non-monotone non-trivially
    poisson = 2.0 / np.e
    pathology_flags = []
    if any(m > poisson * 1.05 for m in mean_seq):
        pathology_flags.append("mean_overshoots_Poisson")
    if not spread_mono and (max(spread_seq) - min(spread_seq) > 0.05 * max(spread_seq)):
        pathology_flags.append("spread_non_monotone_significant")
    if not mean_mono and (max(mean_seq) - min(mean_seq) > 0.05 * max(mean_seq)):
        pathology_flags.append("mean_non_monotone_significant")

    # log-log α per quantity (only if ≥ 2 L-points)
    alpha_mean, alpha_spread = None, None
    if len(available_L) >= 2:
        try:
            lx = np.log(np.array(available_L, float))
            alpha_mean = float(-np.polyfit(lx, np.log(np.abs(np.array(mean_seq))), 1)[0])
            alpha_spread = float(-np.polyfit(lx, np.log(np.abs(np.array(spread_seq))), 1)[0])
        except Exception:
            pass

    # ── Terminal selection
    if pathology_flags:
        terminal = "SUP_L_PATHOLOGICAL"
    elif converged is True:
        terminal = "SUP_L_CONVERGED"
    else:
        terminal = "SUP_L_STILL_DECAYING"

    rec = {"run": "Test 2 sup-side L-extension at load-bearing cell",
           "cell": {"delta": DELTA, "lam": LAM, "N": N},
           "phase1_L": list(LS_PHASE1), "phase2_L_target": L_PHASE2,
           "L_actual": available_L, "L_top": L_top,
           "apparatus_identity": id_report,
           "means_by_L": {str(L): round(means[L], 8) for L in available_L},
           "spreads_by_L": {str(L): round(spreads[L], 8) for L in available_L},
           "top_inc_mean": round(top_inc_mean, 6) if top_inc_mean is not None else None,
           "top_inc_spread": round(top_inc_spread, 6) if top_inc_spread is not None else None,
           "converged": converged,
           "mean_monotone": mean_mono, "spread_monotone": spread_mono,
           "pathology_flags": pathology_flags,
           "loglog_alpha_mean": round(alpha_mean, 4) if alpha_mean is not None else None,
           "loglog_alpha_spread": round(alpha_spread, 4) if alpha_spread is not None else None,
           "phi_per_L": {str(L): [round(float(x), 9) for x in per_L[L]]
                          for L in available_L},
           "terminal": terminal,
           "errors": errs, "total_s": round(time.time() - t0, 0),
           "note": "Sup-side L-extension at load-bearing cell. "
                   "SURFACED, NOT adjudicating Step-1; never proves "
                   "(A)/(B); §D not decided; banked Step-1 untouched."}
    json.dump(rec, open(OUT, "w"), indent=1)
    print("\n" + "=" * 84)
    if id_report:
        print(f"  IDENTITY @L=1.6e6: {id_report}")
    print(f"  L_actual = {available_L}  (top = {L_top})")
    for L in available_L:
        print(f"  L={L:>10d}: mean={means[L]:.6f}  spread={spreads[L]:.6f}")
    print(f"  top_inc mean={rec['top_inc_mean']}  spread={rec['top_inc_spread']}  "
          f"converged={converged}")
    print(f"  α(mean)={rec['loglog_alpha_mean']}  α(spread)={rec['loglog_alpha_spread']}  "
          f"monotone mean={mean_mono} spread={spread_mono}  "
          f"pathology={pathology_flags}")
    print(f"  TERMINAL: {terminal}  [{rec['total_s']}s] errors={len(errs)}")
    print("  SURFACED; Step-1/(A)/(B)/§D untouched.")
    print("=" * 84)


if __name__ == "__main__":
    main()

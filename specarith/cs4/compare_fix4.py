"""Stage 2 prediction with the J13 sign fix (results/gs_zeta_fix4, run_gs_zeta_fix4_spot.sh) against the SEALED prediction
(results/gs_zeta, tag ph2s-stage2-prediction; the values the read used, ph2s2/results/read/S2_READ.json).

Will (2026-10-12): within the 1e-3 budget → record it and the PASS stands; larger → the sealed prediction was wrong and
the findings say so plainly, whatever it does to the verdict. Compared: per file g_B (the read's g_pred), v_B at every
rung, ρ₁, g; the pooled prediction with the read's weights (construction C); and the read's z_pool and per-file z
recomputed against the new prediction (descriptive: the sealed verdict is what it is).

  python compare_fix4.py FIX4_DIR   (FIX4_DIR holds gs_zeta_B_summary.json and gs_zeta_L*.json from the recompute)
    → results/compare_fix4.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUDGET = 1e-3


def main(fix_dir):
    sealed = json.load(open(os.path.join(HERE, "results", "gs_zeta", "gs_zeta_B_summary.json")))
    fixed = json.load(open(os.path.join(fix_dir, "gs_zeta_B_summary.json")))
    read = json.load(open(os.path.join(HERE, "..", "ph2s2", "results", "read", "S2_READ.json")))
    files = [k for k in sealed if k != "gue_B"]
    out = dict(budget=BUDGET, files={})
    worst = 0.0
    for ell in files:
        a, b = sealed[ell], fixed[ell]
        rungs = {}
        for r in a["rungs"]:
            ra, rb = a["rungs"][r], b["rungs"][r]
            rungs[r] = dict(vB_sealed=ra["vB"], vB_fixed=rb["vB"], vB_rel=(rb["vB"] - ra["vB"]) / ra["vB"],
                            rho1_sealed=ra["rho1"], rho1_fixed=rb["rho1"], v_rel=(rb["v"] - ra["v"]) / ra["v"])
        d = b["g_B"] - a["g_B"]
        worst = max(worst, abs(d), *[abs(x["vB_rel"]) for x in rungs.values()])
        out["files"][ell] = dict(gB_sealed=a["g_B"], gB_fixed=b["g_B"], gB_diff=d, g_sealed=a["g"], g_fixed=b["g"],
                                 positivity_fixed=b["positivity_B"], rungs=rungs)
        print(f"ℓ={ell}: g_B {a['g_B']:.10f} → {b['g_B']:.10f} (Δ {d:+.2e}); max |Δv_B/v_B| "
              f"{max(abs(x['vB_rel']) for x in rungs.values()):.2e}; positivity {b['positivity_B']}", flush=True)
    # pooled, with the read's weights (construction C); the read's g_pred must equal the sealed summary's g_B
    res = read["result"]
    per = res["per_file"]
    for ell in files:
        assert abs(per[ell]["g_pred"] - out["files"][ell]["gB_sealed"]) < 1e-12, ell
    w = {ell: per[ell]["weight"] for ell in files}
    g_sealed_pool = sum(w[ell] * out["files"][ell]["gB_sealed"] for ell in files)
    g_fixed_pool = sum(w[ell] * out["files"][ell]["gB_fixed"] for ell in files)
    assert abs(g_sealed_pool - res["g_pred_pool"]) < 1e-12
    out["pooled"] = dict(weights=w, sealed=g_sealed_pool, fixed=g_fixed_pool, diff=g_fixed_pool - g_sealed_pool,
                         z_pool_sealed=res["z_pool"],
                         z_pool_vs_fixed=(res["g_pool"] - g_fixed_pool) / res["se_pool"],
                         z_files_vs_fixed={ell: (per[ell]["g"] - out["files"][ell]["gB_fixed"]) / per[ell]["se_g"]
                                           for ell in files})
    worst = max(worst, abs(g_fixed_pool - g_sealed_pool))
    out["worst_abs_or_rel_change"] = worst
    out["WITHIN_BUDGET"] = worst <= BUDGET
    print(f"pooled prediction {g_sealed_pool:.10f} → {g_fixed_pool:.10f} (Δ {g_fixed_pool - g_sealed_pool:+.2e})")
    print("largest change (g_B absolute, v_B relative):", f"{worst:.2e}", "— within the 1e-3 budget" if out["WITHIN_BUDGET"]
          else "— BEYOND the 1e-3 budget: the sealed prediction was wrong")
    json.dump(out, open(os.path.join(HERE, "results", "compare_fix4.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    main(sys.argv[1])

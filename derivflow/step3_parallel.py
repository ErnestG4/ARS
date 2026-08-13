#!/usr/bin/env python3
"""Parallel driver for ROADMAP Step 3 (seals/SCALE_LAW_SEAL.json). Replicate-level
multiprocessing ONLY — each replicate is an independent SeedSequence child, so pooling changes
nothing about the computation or the artifact; arm order (iid first, GUE if-time) is preserved
across the pool barrier. Solver memory-chunked (DS_BLOCK, bitwise-identical; gates re-certified
2026-08-12) so 5 workers fit the 15GB WSL VM. Adjudication logic identical to step3_scale_law.
"""
import json, os, time
from multiprocessing import get_context
import numpy as np

WORKERS = 5


def one_rep(args):
    sc, child_idx, rep_i = args
    import sys
    sys.path.insert(0, "derivflow")
    import numpy as np
    from science_rate_question import one_flow, gue_seed, MASTER_SEED
    from science_dense import K_DENSE
    import step3_scale_law as S3          # sets TIS.CHUNK = 1024
    children = np.random.SeedSequence(MASTER_SEED).spawn(128)
    if sc == "iid":
        seed = np.sort(np.random.default_rng(children[child_idx]).uniform(-1.0, 1.0, S3.N))
    else:
        seed = gue_seed(S3.N, np.random.default_rng(children[child_idx]))
    t0 = time.time()
    rec = one_flow(seed, S3.N, K_DENSE, f"{sc} rep={rep_i}")
    print(f"    {sc} rep {rep_i}: {round((time.time()-t0)/60,1)} min", flush=True)
    return rep_i, rec


def run():
    import sys
    sys.path.insert(0, "derivflow")
    import step3_scale_law as S3
    from science_dense import K_DENSE, stats
    from science_rate_question import fit_ladder, kstar
    t0 = time.time()
    art = {"executes": "seals/SCALE_LAW_SEAL.json (parallel driver, replicate-level pool only)",
           "grade": S3.SEAL["grade"].split(" (")[0], "data": {}, "fits": {}, "adjudication": {}}
    ctx = get_context("fork")
    for sc, child0 in [("iid", 96), ("gue", 112)]:      # arm order per seal: iid first
        with ctx.Pool(WORKERS) as pool:
            results = pool.map(one_rep, [(sc, child0 + i, i) for i in range(S3.R)])
        reps = [rec for _, rec in sorted(results)]
        data = {str(k): stats(reps, k) for k in K_DENSE}
        art["data"][sc] = data
        fits = {}
        for band, mkey, skey in [("primary", "mean", "sigma_mean"),
                                 ("eps", "mean_epsraw", "sigma_mean_epsraw"),
                                 ("2eps", "mean_2eps", "sigma_mean_2eps")]:
            ks = [k for k in K_DENSE if data[str(k)][mkey] > S3.FIT_WINDOW_MIN]
            means = np.array([data[str(k)][mkey] for k in ks])
            sm = np.array([data[str(k)][skey] for k in ks])
            sel, lad = fit_ladder(np.array(ks, dtype=float), means, sm)
            fits[band] = {"fit_window_k": ks, "selected": sel, "ladder": lad}
        art["fits"][sc] = fits
        prim = fits["primary"]
        k0, km = kstar(prim["selected"], np.array(prim["ladder"][prim["selected"]]["params"]),
                       np.array(prim["ladder"][prim["selected"]]["cov"]),
                       np.random.default_rng(12345))
        pred = S3.SEAL["predictions_rederived_from_repo"]["iid" if sc == "iid" else "gue_if_time"]
        s_eff = float(np.sqrt(km ** 2 + pred["sigma_sys"] ** 2))
        d_flat, d_log = abs(k0 - pred["H_flat"]), abs(k0 - pred["H_log"])
        verdict = ("SCALE-FLAT" if d_flat < 3 * s_eff and d_log > 5 * s_eff else
                   "SCALE-LOG" if d_log < 3 * s_eff and d_flat > 5 * s_eff else "INCONCLUSIVE")
        art["adjudication"][sc] = {
            "kstar_16384": k0, "sigma_m": km, "sigma_eff": s_eff, "d_flat": d_flat,
            "d_log": d_log, "H_flat": pred["H_flat"], "H_log": pred["H_log"],
            "verdict": verdict,
            "form_consistency_rider": {b: fits[b]["selected"] for b in fits},
            "power_statement": (f"resolvable separation at 3 sigma_eff = {3*s_eff:.3f}; "
                                f"sealed separation {pred['H_log']-pred['H_flat']:.3f}")}
        print(f"\n{sc.upper()} ARM VERDICT [{art['grade']}]: {verdict}")
        print(f"  k*(16384) = {k0:.3f} +- {km:.3f}  (sigma_eff {s_eff:.3f})  "
              f"d_flat={d_flat:.3f} d_log={d_log:.3f}")
        with open("derivflow/step3_scale_law.json", "w") as f:
            json.dump(art, f, indent=1)
    art["runtime_s"] = round(time.time() - t0, 1)
    with open("derivflow/step3_scale_law.json", "w") as f:
        json.dump(art, f, indent=1)
    print(f"total {round(art['runtime_s']/3600, 2)} h")


if __name__ == "__main__":
    run()

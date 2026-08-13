#!/usr/bin/env python3
"""ROADMAP Step 3 — sealed n = 16384 scale-law discrimination. Transcribes
seals/SCALE_LAW_SEAL.json; instrument v1.5.1 unchanged; dense v1.6 k-grid; RNG children 96-111
(iid) / 112-127 (GUE if-time). iid arm first and alone sufficient; artifact written after the
iid arm so a mid-GUE death leaves the iid verdict standing.
"""
import json, time
import numpy as np
import track0_iid_scaling as TIS
from science_rate_question import (one_flow, gue_seed, fit_ladder, kstar, MASTER_SEED)
from science_dense import K_DENSE, stats

N = 16384
R = 16
FIT_WINDOW_MIN = 1e-3
SEAL = json.load(open("derivflow/seals/SCALE_LAW_SEAL.json"))
TIS.CHUNK = 1024   # memory guard at n=16384 (chunk x n complex); reference definition unchanged


def arm(sc, gen, child0, art):
    children = np.random.SeedSequence(MASTER_SEED).spawn(128)
    reps = []
    for i in range(R):
        t0 = time.time()
        reps.append(one_flow(gen(children[child0 + i]), N, K_DENSE, f"{sc} n={N} rep={i}"))
        print(f"    rep {i}: {round((time.time()-t0)/60,1)} min", flush=True)
    data = {str(k): stats(reps, k) for k in K_DENSE}
    art["data"][sc] = data
    fits = {}
    for band, mkey, skey in [("primary", "mean", "sigma_mean"),
                             ("eps", "mean_epsraw", "sigma_mean_epsraw"),
                             ("2eps", "mean_2eps", "sigma_mean_2eps")]:
        ks = [k for k in K_DENSE if data[str(k)][mkey] > FIT_WINDOW_MIN]
        means = np.array([data[str(k)][mkey] for k in ks])
        sm = np.array([data[str(k)][skey] for k in ks])
        sel, lad = fit_ladder(np.array(ks, dtype=float), means, sm)
        fits[band] = {"fit_window_k": ks, "selected": sel, "ladder": lad}
    art["fits"][sc] = fits
    prim = fits["primary"]
    k0, km = kstar(prim["selected"], np.array(prim["ladder"][prim["selected"]]["params"]),
                   np.array(prim["ladder"][prim["selected"]]["cov"]), np.random.default_rng(12345))
    pred = SEAL["predictions_rederived_from_repo"]["iid" if sc == "iid" else "gue_if_time"]
    s_eff = float(np.sqrt(km ** 2 + pred["sigma_sys"] ** 2))
    d_flat, d_log = abs(k0 - pred["H_flat"]), abs(k0 - pred["H_log"])
    if d_flat < 3 * s_eff and d_log > 5 * s_eff:
        verdict = "SCALE-FLAT"
    elif d_log < 3 * s_eff and d_flat > 5 * s_eff:
        verdict = "SCALE-LOG"
    else:
        verdict = "INCONCLUSIVE"
    art["adjudication"][sc] = {
        "kstar_16384": k0, "sigma_m": km, "sigma_eff": s_eff,
        "d_flat": d_flat, "d_log": d_log, "H_flat": pred["H_flat"], "H_log": pred["H_log"],
        "verdict": verdict,
        "form_consistency_rider": {b: fits[b]["selected"] for b in fits},
        "power_statement": (f"resolvable separation at 3 sigma_eff = {3*s_eff:.3f}; "
                            f"sealed separation {pred['H_log']-pred['H_flat']:.3f}")}
    print(f"\n{sc.upper()} ARM VERDICT [{art['grade']}]: {verdict}")
    print(f"  k*(16384) = {k0:.3f} +- {km:.3f}  (sigma_eff {s_eff:.3f})")
    print(f"  d_flat = {d_flat:.3f}  d_log = {d_log:.3f}  forms: {art['adjudication'][sc]['form_consistency_rider']}")
    with open("derivflow/step3_scale_law.json", "w") as f:
        json.dump(art, f, indent=1)


def run():
    t0 = time.time()
    art = {"executes": "seals/SCALE_LAW_SEAL.json", "grade": SEAL["grade"].split(" (")[0],
           "data": {}, "fits": {}, "adjudication": {}}
    arm("iid", lambda c: np.sort(np.random.default_rng(c).uniform(-1.0, 1.0, N)), 96, art)
    arm("gue", lambda c: gue_seed(N, np.random.default_rng(c)), 112, art)   # if-time arm
    art["runtime_s"] = round(time.time() - t0, 1)
    with open("derivflow/step3_scale_law.json", "w") as f:
        json.dump(art, f, indent=1)
    print(f"total runtime {round(art['runtime_s']/3600,1)} h")


if __name__ == "__main__":
    run()

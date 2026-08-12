#!/usr/bin/env python3
"""v1.6 dense-grid adjudication (scope §7 amendment, commit c986573). Executes the sealed
procedure on the dense fit grid k in {1..16} u {24,32,48,64}. AMENDMENT SCOPE: grid density and
nothing else — ladder, AICc, fit-window rule, z-thresholds, triple-band invariance clause, seed
roster, and RNG protocol unchanged from 95e1ad3 + v1.5.1; multi-start fitter (findings §10)
inherited as faithful AICc execution. The verdict this produces carries the grade label
SEALED-PROCEDURE, DISCLOSED-PRIOR-LOOK (second disclosure ledger in scope §7).

Flows are exact reproductions under the seal's SeedSequence (children 0-47 iid, 48-95 GUE);
the dense grid is references-only new information.
"""
import json, time
import numpy as np
from science_rate_question import (one_flow, gue_seed, fit_ladder, kstar, SHAPE_IDX,
                                   N_SCIENCE, FIT_WINDOW_MIN, Z_UNIVERSAL, Z_DEPENDENT,
                                   MASTER_SEED)

K_DENSE = list(range(1, 17)) + [24, 32, 48, 64]


def stats(reps, k):
    def col(key):
        v = np.array([r[k][key] for r in reps])
        return float(np.mean(v)), float(np.std(v, ddof=1) / np.sqrt(len(v)))
    m, sm = col("one_minus_rtilde")
    m1, sm1 = col("one_minus_rtilde_epsraw")
    m2, sm2 = col("one_minus_rtilde_2eps")
    return {"mean": m, "sigma_mean": sm, "mean_epsraw": m1, "sigma_mean_epsraw": sm1,
            "mean_2eps": m2, "sigma_mean_2eps": sm2}


def run():
    t0 = time.time()
    children = np.random.SeedSequence(MASTER_SEED).spawn(96)
    art = {"executes": "scope v1.6 dense-grid amendment (c986573)",
           "grade": "SEALED-PROCEDURE, DISCLOSED-PRIOR-LOOK",
           "k_grid": K_DENSE, "data": {}, "fits": {}, "kstar_table": {}, "adjudication": {}}
    for sc, gen, base in [("iid", lambda c, n: np.sort(np.random.default_rng(c).uniform(-1, 1, n)), 0),
                          ("gue", lambda c, n: gue_seed(n, np.random.default_rng(c)), 48)]:
        art["data"][sc] = {}
        for ni, n in enumerate(N_SCIENCE):
            reps = [one_flow(gen(children[base + ni * 16 + i], n), n, K_DENSE, f"{sc} n={n} rep={i}")
                    for i in range(16)]
            art["data"][sc][str(n)] = {str(k): stats(reps, k) for k in K_DENSE}

    rng_ci = np.random.default_rng(12345)
    for band, mkey, skey in [("primary", "mean", "sigma_mean"),
                             ("eps", "mean_epsraw", "sigma_mean_epsraw"),
                             ("2eps", "mean_2eps", "sigma_mean_2eps")]:
        for sc in ("iid", "gue"):
            art["fits"].setdefault(band, {})[sc] = {}
            for nn in map(str, N_SCIENCE):
                data = art["data"][sc][nn]
                ks = [k for k in K_DENSE if data[str(k)][mkey] > FIT_WINDOW_MIN]
                means = np.array([data[str(k)][mkey] for k in ks])
                sm = np.array([data[str(k)][skey] for k in ks])
                sel, fits = fit_ladder(np.array(ks, dtype=float), means, sm)
                art["fits"][band][sc][nn] = {"fit_window_k": ks, "selected": sel, "ladder": fits}
                if band == "primary" and "params" in fits[sel]:
                    k0, kerr = kstar(sel, np.array(fits[sel]["params"]),
                                     np.array(fits[sel]["cov"]), rng_ci)
                    art["kstar_table"].setdefault(sc, {})[nn] = {"kstar": k0, "err": kerr, "form": sel}

    fi, fg = art["fits"]["primary"]["iid"]["4096"], art["fits"]["primary"]["gue"]["4096"]
    adj = {"n_adjudicated": 4096, "iid_form": fi["selected"], "gue_form": fg["selected"],
           "band_forms": {b: {sc: art["fits"][b][sc]["4096"]["selected"] for sc in ("iid", "gue")}
                          for b in ("primary", "eps", "2eps")}}
    band_invariant = all(
        len({art["fits"][b][sc]["4096"]["selected"] for b in ("primary", "eps", "2eps")}) == 1
        for sc in ("iid", "gue"))
    adj["band_invariant"] = band_invariant
    if not band_invariant:
        adj["verdict"] = "INCONCLUSIVE-ON-INSTRUMENT-GROUNDS"
        adj["basis"] = f"selection not invariant across bands: {adj['band_forms']}"
    elif fi["selected"] != fg["selected"]:
        adj["verdict"] = "RATE-SEED-DEPENDENT"
        adj["basis"] = "form disagreement, invariant under the band"
    else:
        form = fi["selected"]
        pi, ci = np.array(fi["ladder"][form]["params"]), np.array(fi["ladder"][form]["cov"])
        pg, cg = np.array(fg["ladder"][form]["params"]), np.array(fg["ladder"][form]["cov"])
        zs = {f"param{idx}": float(abs(pi[idx] - pg[idx]) / np.sqrt(ci[idx][idx] + cg[idx][idx]))
              for idx in SHAPE_IDX[form]}
        adj["shape_z"] = zs
        adj["shape_params"] = {"iid": pi.tolist(), "gue": pg.tolist(), "form": form}
        zmax = max(zs.values())
        adj["verdict"] = ("RATE-UNIVERSAL" if zmax < Z_UNIVERSAL else
                          "RATE-SEED-DEPENDENT" if zmax >= Z_DEPENDENT else "INCONCLUSIVE")
        if adj["verdict"] == "RATE-SEED-DEPENDENT":
            adj["basis"] = f"same form {form}, shape z {zs} (>= {Z_DEPENDENT})"
    art["adjudication"] = adj
    art["runtime_s"] = round(time.time() - t0, 1)
    with open("derivflow/science_dense_grid.json", "w") as f:
        json.dump(art, f, indent=1)
    print(f"\nVERDICT [{art['grade']}]: {adj['verdict']}")
    print("band_forms:", json.dumps(adj["band_forms"]))
    if "shape_z" in adj:
        print("shape z:", adj["shape_z"], "params:", adj["shape_params"])
    for sc in art["kstar_table"]:
        for nn, v in art["kstar_table"][sc].items():
            print(f"k*({sc}, n={nn}) = {v['kstar']:.2f} ± {v['err']:.2f}  [{v['form']}]")
    print(f"runtime {art['runtime_s']}s")


if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""Re-adjudication of the v1.5.1 campaign science stage after the fit-ladder convergence fix.

DATA UNCHANGED: loads the banked campaign artifacts (science_rate_question.json for GUE/picket,
track0_ensemble.json for iid) and re-runs ONLY the sealed adjudication (fits, AICc selection,
band-invariance clause, z-rule, k*) with the multi-start fitter. The prior verdict
(INCONCLUSIVE-ON-INSTRUMENT-GROUNDS, fired by an optimizer non-convergence defaulting the GUE
primary arm to F2) is preserved in the campaign artifact; this writes a separate artifact with
the full chain disclosed.
"""
import json
import numpy as np
from science_rate_question import (fit_ladder, kstar, SHAPE_IDX, N_SCIENCE, K_GRID_FIT,
                                   FIT_WINDOW_MIN, Z_UNIVERSAL, Z_DEPENDENT)

sci = json.load(open("derivflow/science_rate_question.json"))
iid = json.load(open("derivflow/track0_ensemble.json"))["ensembles"]
gue = sci["gue"]
art = {"readjudication_of": "science_rate_question.json (campaign v1.5.1)",
       "reason": "fit-ladder multi-start convergence fix; data unchanged",
       "fits": {}, "kstar_table": {}, "adjudication": {}}
rng_ci = np.random.default_rng(12345)

for band, mkey, skey in [("primary", "mean", "sigma_mean"),
                         ("eps", "mean_epsraw", "sigma_mean_epsraw"),
                         ("2eps", "mean_2eps", "sigma_mean_2eps")]:
    for seed_class, data in [("iid", iid), ("gue", gue)]:
        art["fits"].setdefault(band, {})[seed_class] = {}
        for nn in map(str, N_SCIENCE):
            ks = [k for k in K_GRID_FIT if data[nn][str(k)][mkey] > FIT_WINDOW_MIN]
            means = np.array([data[nn][str(k)][mkey] for k in ks])
            sm = np.array([data[nn][str(k)][skey] for k in ks])
            sel, fits = fit_ladder(np.array(ks, dtype=float), means, sm)
            art["fits"][band][seed_class][nn] = {"fit_window_k": ks, "selected": sel, "ladder": fits}
            if band == "primary" and "params" in fits[sel]:
                k0, kerr = kstar(sel, np.array(fits[sel]["params"]), np.array(fits[sel]["cov"]), rng_ci)
                art["kstar_table"].setdefault(seed_class, {})[nn] = {"kstar": k0, "err": kerr, "form": sel}

fi, fg = art["fits"]["primary"]["iid"]["4096"], art["fits"]["primary"]["gue"]["4096"]
adj = {"n_adjudicated": 4096, "iid_form": fi["selected"], "gue_form": fg["selected"],
       "band_forms": {b: {sc: art["fits"][b][sc]["4096"]["selected"] for sc in ("iid", "gue")}
                      for b in ("primary", "eps", "2eps")}}
band_invariant = all(len({art["fits"][b][sc]["4096"]["selected"] for b in ("primary", "eps", "2eps")}) == 1
                     for sc in ("iid", "gue"))
adj["band_invariant"] = band_invariant
if not band_invariant:
    adj["verdict"] = "INCONCLUSIVE-ON-INSTRUMENT-GROUNDS"
    adj["basis"] = f"selection not invariant across bands: {adj['band_forms']}"
elif fi["selected"] != fg["selected"]:
    adj["verdict"] = "RATE-SEED-DEPENDENT"
    adj["basis"] = "form disagreement, invariant under the v1.5.1 band"
else:
    form = fi["selected"]
    pi, ci = np.array(fi["ladder"][form]["params"]), np.array(fi["ladder"][form]["cov"])
    pg, cg = np.array(fg["ladder"][form]["params"]), np.array(fg["ladder"][form]["cov"])
    zs = {f"param{idx}": float(abs(pi[idx] - pg[idx]) / np.sqrt(ci[idx][idx] + cg[idx][idx]))
          for idx in SHAPE_IDX[form]}
    adj["shape_z"] = zs
    adj["shape_params"] = {"iid": pi.tolist(), "gue": pg.tolist(), "form": form}
    zmax = max(zs.values())
    if zmax < Z_UNIVERSAL:
        adj["verdict"] = "RATE-UNIVERSAL"
    elif zmax >= Z_DEPENDENT:
        adj["verdict"] = "RATE-SEED-DEPENDENT"
        adj["basis"] = f"same form {form}, shape z {zs} (>= {Z_DEPENDENT})"
    else:
        adj["verdict"] = "INCONCLUSIVE"
adj["picket_fence_ceiling_invariant"] = sci["adjudication"]["picket_fence_ceiling_invariant"]
art["adjudication"] = adj
with open("derivflow/science_readjudicated.json", "w") as f:
    json.dump(art, f, indent=1)
print(f"VERDICT: {adj['verdict']}")
print("band_forms:", json.dumps(adj["band_forms"]))
if "shape_z" in adj:
    print("shape z:", adj["shape_z"])
for sc in art["kstar_table"]:
    for nn, v in art["kstar_table"][sc].items():
        print(f"k*({sc}, n={nn}) = {v['kstar']:.2f} ± {v['err']:.2f}  [{v['form']}]")

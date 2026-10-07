"""Write BANDS_PROVENANCE.json in each pre-read dir (review v3 m6): which configuration, seeds and run produced each
null-band file, so a band cannot be silently paired with the wrong window. Usage: python bands_provenance.py"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = {
    "results/preread": {"G0": "spot run 2026-10-07 02:24-02:55 (preread.py nulls)", "G0c": "same run", "G2": "same run"},
    "results/preread_proposed": {"G0": "copied from results/preread", "G0c": "copied from results/preread",
                                 "G2": "copied from results/preread_A4b (spot run 2026-10-07 ~05:00-05:11, T = 4e4)"},
}

for d, src in SOURCES.items():
    tab = json.load(open(os.path.join(HERE, d, "preread_tables.json")))
    prov = {}
    for n in ("G0", "G0c", "G2"):
        for k in ("gue", "poisson"):
            z = np.load(os.path.join(HERE, d, f"nulls_{n}_{k}.npz"))
            prov[f"nulls_{n}_{k}.npz"] = dict(config=tab["configs"][n],
                                             seeds=[int(z["seeds"].min()), int(z["seeds"].max())],
                                             n_draws=int(len(z["seeds"])), mean_levels=float(z["nlev"].mean()),
                                             source=src[n])
    json.dump(prov, open(os.path.join(HERE, d, "BANDS_PROVENANCE.json"), "w"), indent=1)
    print(d, {k: (v["config"]["E_hi"], v["seeds"], round(v["mean_levels"])) for k, v in prov.items() if "gue" in k})

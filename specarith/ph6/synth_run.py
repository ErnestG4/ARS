"""Crash/timing test of the sealed gate code paths on SYNTHETIC spectra (not part of the seal; not a gate).

Feeds GUE-null levels (seeds 7000+, never used by the calibration 1000-1099/2000-2099 or held-out 1100-1199/2100-2199
draws) in place of the zeta zeros, chi_-4 zeros and Maass levels, through gates.zeta_like_gate and gates.maass_gate, with
the REAL pre-read tables, tolerances, reachability and bands. Verdicts are meaningless (synthetic data); what is tested
is that the sealed run completes: keys, shapes, assertions, rulings, and how long each gate takes at full size.
G3/G3-c (held-out seeds) and G4 at G0's configuration are sealed objects and are NOT run here.

Usage: python synth_run.py PREREAD_DIR OUT.json
"""
import json
import os
import sys
import time

import numpy as np

import gates as G
import ph6lib as L


def main(pre_dir, out_path):
    tab = json.load(open(os.path.join(pre_dir, "preread_tables.json")))
    reach = G.Reach(tab["reachability"])
    C = {k: L.Config(**v) for k, v in tab["configs"].items()}
    pre = lambda n: np.load(os.path.join(pre_dir, f"rhs_{n}.npz"))
    band = lambda n: np.load(os.path.join(pre_dir, f"nulls_{n}_gue.npz"))["B"]
    out = {}
    rng = np.random.default_rng(7000)
    zsyn = L.null_levels("gue", L.nbar_zeta, C["G0"].E_hi, rng)
    zsyn = zsyn[zsyn <= C["G0"].E_hi]
    for name, kw in (("G0", dict(band=band("G0"))), ("G0s_a", {}), ("G0s_b", {}), ("G0s_c", {}),
                     ("G0c", dict(band=band("G0c")))):
        zz = zsyn[:30000] if name == "G0c" else zsyn
        t = time.time()
        r = G.zeta_like_gate(name, C[name], zz, pre(name), reach, **kw)
        out[name] = dict(wall_s=round(time.time() - t, 1), layer_a=r["layer_a"]["verdict"],
                         red_paths=[(x["red_path"], x["result"]) for x in r["red_paths"]],
                         layer_b=r.get("layer_b", {}).get("verdict"))
        print(name, out[name], flush=True)
    csyn = L.null_levels("gue", L.nbar_chi, C["G2"].E_hi, np.random.default_rng(7001))
    csyn = csyn[csyn <= C["G2"].E_hi]
    t = time.time()
    r = G.zeta_like_gate("G2", C["G2"], csyn, pre("G2"), reach, q=4, chi=L.chi4, a=1, delta=1e-30, band=band("G2"))
    out["G2"] = dict(wall_s=round(time.time() - t, 1), layer_a=r["layer_a"]["verdict"],
                     red_paths=[(x["red_path"], x["result"]) for x in r["red_paths"]], layer_b=r["layer_b"]["verdict"])
    print("G2", out["G2"], flush=True)
    import classes
    _, ls = classes.pari_counts(30, 30)
    ch = {t_: ls[("h", t_)] / 2 for (k, t_) in ls if k == "h"}
    cg = {t_: ls[("g", t_)] for (k, t_) in ls if k == "g"}
    rsyn = np.sort(np.random.default_rng(7002).uniform(9.5, 98.76, 600))
    t = time.time()
    r = G.maass_gate(C["G1"], rsyn[::2], rsyn[1::2], pre("G1_even"), pre("G1_odd"), reach, (ch, cg))
    out["G1"] = dict(wall_s=round(time.time() - t, 1),
                     even=(r["even"]["layer_a"]["verdict"], [(x["red_path"], x["result"]) for x in r["even"]["red_paths"]]),
                     odd=(r["odd"]["layer_a"]["verdict"], [(x["red_path"], x["result"]) for x in r["odd"]["red_paths"]]))
    print("G1", out["G1"], flush=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1, default=str)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

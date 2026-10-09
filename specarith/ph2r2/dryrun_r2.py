"""R₂ dry run (PH2R2_SEAL 1.0 §4): the read path end to end on surrogates, no fresh zero touched.
  1. Platt encode→decode round trip (r2run.roundtrip).
  2. A full-size windowed CUE_250 surrogate of each bin through r2run.mu_hat + verdict (known answer μ* = 0; with the
     sealed rule this must read FAIL where resolvable — the surrogate has no arithmetic term — or NOT RESOLVABLE).
  3. (achieved) witness: one bin's surrogate cut to the first 1% of its blocks — the achieved CI must be too wide or
     include 0, so the verdict must read NOT RESOLVABLE (achieved).
  python dryrun_r2.py G0B_DIR OUT
"""
import json
import os
import sys

import numpy as np

import g0b as G
import r2prep as P
import r2run as RR


def surrogate(name, frac=1.0, seed=99):
    g = P.geometry(name)
    rng = np.random.default_rng(seed)
    x0 = float(P.nbar(g["t0"]))
    nblocks = int(((float(P.nbar(g["t1"])) - x0) // G.BLOCK) * frac)
    lev, edges = [], [g["t0"]]
    for b in range(nblocks):
        xb = x0 + b * G.BLOCK
        lev.append(G.nbar_inv(xb + G.cue_block(rng), g["tc"]))
        edges.append(float(G.nbar_inv(np.array([xb + G.BLOCK]), g["tc"])[0]))
    return np.concatenate(lev), np.array(edges)


def main(g0b_dir, out):
    S = json.load(open(os.path.join(g0b_dir, "g0b_summary.json")))
    key = S["primary_choice"]["primary"]
    u, w = (float(x) for x in key.split("_"))
    res = dict(primary=key, roundtrip=RR.roundtrip(), bins={})
    rng = np.random.default_rng(2026)
    for name in P.BINS:
        sd = S[name][key]["sd_mu"]
        resolvable = S[name][key]["power_reject_mu0"] >= 0.80
        lev, edges = surrogate(name)
        m = RR.mu_hat(lev, edges, name, u, w, g0b_dir, sd, rng)
        m["verdict"] = RR.verdict(m, resolvable)
        m["expected"] = "FAIL (no arithmetic term; mu* = 0)" if resolvable else "NOT RESOLVABLE"
        res["bins"][name] = {k: v for k, v in m.items() if k != "boot_sd"} | dict(boot_sd=m["boot_sd"])
        print(name, m["verdict"], round(m["mu"], 4), [round(x, 4) for x in m["ci"]], flush=True)
    name = "R1"
    lev, edges = surrogate(name, frac=0.01, seed=5)
    sd_small = S[name][key]["sd_mu"] * 10.0          # SD scales as 1/√n: 1% of the bin ⇒ ×10
    m = RR.mu_hat(lev, edges, name, u, w, g0b_dir, sd_small, rng)
    m["verdict"] = RR.verdict(m, True)
    res["achieved_witness"] = dict(bin=name, fraction=0.01, mu=m["mu"], ci=m["ci"], halfwidth=m["halfwidth"],
                                   verdict=m["verdict"], FIRED=m["verdict"] == "NOT RESOLVABLE (achieved)")
    print("achieved witness", res["achieved_witness"], flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "dryrun.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

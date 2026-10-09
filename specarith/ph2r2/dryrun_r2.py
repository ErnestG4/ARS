"""R₂ dry run (PH2R2_SEAL 1.0 §4): the read path end to end on surrogates, no fresh zero touched.
  1. Platt encode→decode round trip (r2run.roundtrip).
  2. A full-size windowed CUE_250 surrogate of each bin through r2run.mu_hat + verdict, twice:
     (i) as is (known answer μ* = 0: the CI includes 0, so the sealed rule reads NOT RESOLVABLE (achieved) — the power
         arm correctly unable to exclude μ = 0 — or NOT RESOLVABLE pre-data);
     (ii) with the arithmetic term planted at μ = 1 (S_f + LOT_f, as Phase 6 planted lines): must read PASS where the
          bin is resolvable (1 ∈ CI, 0 ∉ CI).
  3. (achieved) witness, two points on R1's planted surrogate (resolvable pre-data, so only the achieved width can stop
     it), SD for the cut = SD(μ̂)/√frac:
     - FIRE: the first 0.22% of its blocks (41 blocks, 10,250 levels — the smallest cut on which every declared bootstrap
       block length, up to 10,000 levels, is defined); half-width ≥ 1.96·SD/√0.0022 > 0.5 by construction, so the
       verdict must read NOT RESOLVABLE (achieved);
     - CONTROL: the first 1% (half-width ≈ 0.26 < 0.5): must read PASS, so the width arm does not fire on an adequate CI.
     (The first version used 1% alone and read PASS on 2026-10-09 07:1x — the witness could not fire; this is the fix.)
  python dryrun_r2.py G0B_DIR OUT {R1..R5 | witness | merge}   (bins run in parallel on spot, then merge)
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


def one_bin(g0b_dir, out, name):
    S = json.load(open(os.path.join(g0b_dir, "g0b_summary.json")))
    key = S["primary_choice"]["primary"]
    u, w = (float(x) for x in key.split("_"))
    rng = np.random.default_rng(2026 + int(name[1:]))
    sd = S[name][key]["sd_mu"]
    resolvable = S[name][key]["power_reject_mu0"] >= 0.80
    lev, edges = surrogate(name)
    res = dict(resolvable=bool(resolvable))
    for tag, plant, exp in (("mu0", 0.0, "NOT RESOLVABLE (achieved)" if resolvable else "NOT RESOLVABLE"),
                            ("planted_mu1", 1.0, "PASS" if resolvable else "NOT RESOLVABLE")):
        m = RR.mu_hat(lev, edges, name, u, w, g0b_dir, sd, rng, plant=plant)
        m["verdict"] = RR.verdict(m, resolvable)
        m["expected"] = exp
        m["as_expected"] = m["verdict"] == exp
        res[tag] = m
        print(name, tag, m["verdict"], round(m["mu"], 4), [round(x, 4) for x in m["ci"]], "expected", exp, flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, f"dryrun_{name}.json"), "w"), indent=1, default=float)


def witness(g0b_dir, out):
    S = json.load(open(os.path.join(g0b_dir, "g0b_summary.json")))
    key = S["primary_choice"]["primary"]
    u, w = (float(x) for x in key.split("_"))
    name = "R1"
    pts = {}
    for tag, frac, exp in (("fire", 0.0022, "NOT RESOLVABLE (achieved)"), ("control", 0.01, "PASS")):
        lev, edges = surrogate(name, frac=frac, seed=5)
        sd_small = S[name][key]["sd_mu"] / np.sqrt(frac)          # SD scales as 1/√n
        m = RR.mu_hat(lev, edges, name, u, w, g0b_dir, sd_small, np.random.default_rng(5), plant=1.0)
        m["verdict"] = RR.verdict(m, True)
        pts[tag] = dict(fraction=frac, n=m["n"], mu=m["mu"], ci=m["ci"], halfwidth=m["halfwidth"], verdict=m["verdict"],
                        expected=exp, as_expected=m["verdict"] == exp)
    w_ = dict(bin=name, points=pts, FIRED=pts["fire"]["as_expected"], CONTROL_OK=pts["control"]["as_expected"])
    os.makedirs(out, exist_ok=True)
    json.dump(w_, open(os.path.join(out, "dryrun_witness.json"), "w"), indent=1, default=float)
    print("achieved witness", w_, flush=True)


def merge(g0b_dir, out):
    S = json.load(open(os.path.join(g0b_dir, "g0b_summary.json")))
    res = dict(primary=S["primary_choice"]["primary"], roundtrip=RR.roundtrip(),
               bins={n: json.load(open(os.path.join(out, f"dryrun_{n}.json"))) for n in P.BINS},
               achieved_witness=json.load(open(os.path.join(out, "dryrun_witness.json"))))
    json.dump(res, open(os.path.join(out, "dryrun.json"), "w"), indent=1, default=float)
    print(json.dumps({n: {k: (b[k]["verdict"], round(b[k]["mu"], 4)) for k in ("mu0", "planted_mu1")}
                      for n, b in res["bins"].items()}),
          "witness FIRED:", res["achieved_witness"]["FIRED"], "roundtrip:", res["roundtrip"]["PASS"])


if __name__ == "__main__":
    g0b_dir, out, what = sys.argv[1], sys.argv[2], sys.argv[3]          # what ∈ {R1..R5, witness, merge}
    if what == "witness":
        witness(g0b_dir, out)
    elif what == "merge":
        merge(g0b_dir, out)
    else:
        one_bin(g0b_dir, out, what)

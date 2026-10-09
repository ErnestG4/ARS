"""R₂ read — the other test-function members, DESCRIPTIVE (Will, 2026-10-09: "compute μ̂ at u = 1, 1.5 and 2"; all eight
family members are run, the sealed primary (0.5, 0.3) included as a reproduction check). Not sealed: the seal tests one
f. Same code path as the read (r2run.mu_hat on the whole Platt file as one window), CI = μ̂ ± 1.96·max(that member's G0b
surrogate SD, its widest bootstrap SD), the A2 rule applied descriptively.

  python members.py BIN      -> results/members/BIN.json
  python members.py table    -> results/members/MEMBERS.md
"""
import json
import os
import sys

import numpy as np

import r2prep as P
import r2run as RR

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results", "members")
SUMMARY = os.path.join(HERE, "results", "g0b", "g0b_summary.json")


def one_bin(name):
    S = json.load(open(SUMMARY))
    lev = RR.read_platt_heights(os.path.join(HERE, "data", "platt", RR.PLATT[name]))
    g = P.geometry(name)
    edges = np.array([g["t0"], g["t1"]])
    res = {}
    for u, w in P.FAMILY:
        k = f"{u}_{w}"
        s = S[name][k]
        m = RR.mu_hat(lev, edges, name, u, w, os.path.join(HERE, "results", "g0b"), s["sd_mu"],
                      np.random.default_rng(20261009))
        m["verdict_descriptive"] = RR.verdict(m, s["power_reject_mu0"] >= 0.80)
        m["power_reject_mu0"] = s["power_reject_mu0"]
        res[k] = m
        print(name, k, m["verdict_descriptive"], round(m["mu"], 4), [round(x, 4) for x in m["ci"]], flush=True)
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, f"{name}.json"), "w"), indent=1, default=float)


def table():
    keys = [f"{u}_{w}" for u, w in P.FAMILY]
    lines = ["# R₂ — all test-function members (descriptive; only (0.5, 0.3) is sealed)", "",
             "μ̂ [95% CI] per bin; bump at u mean spacings, width w; verdict letter by the A2 rule applied descriptively "
             "(P PASS, F FAIL, N NOT RESOLVABLE (achieved)).", "",
             "| member (u, w) | " + " | ".join(P.BINS) + " |", "|---|" + "---|" * len(P.BINS)]
    R = {n: json.load(open(os.path.join(OUT, f"{n}.json"))) for n in P.BINS}
    tag = {"PASS": "P", "FAIL": "F", "NOT RESOLVABLE (achieved)": "N", "NOT RESOLVABLE": "N (pre)"}
    for k in keys:
        cells = [f"{R[n][k]['mu']:.3f} [{R[n][k]['ci'][0]:.3f}, {R[n][k]['ci'][1]:.3f}] {tag[R[n][k]['verdict_descriptive']]}"
                 for n in P.BINS]
        lines.append(f"| ({k.replace('_', ', ')}) | " + " | ".join(cells) + " |")
    open(os.path.join(OUT, "MEMBERS.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    table() if sys.argv[1] == "table" else one_bin(sys.argv[1])

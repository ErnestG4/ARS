"""Own-bootstrap SE validation (round 71; OWNBOOT_SE_CHECK.md). Reads committed read records only. DESCRIPTIVE.
  python ownboot_chi2.py   → results/ownboot_chi2.json, printed summary
"""
import json
import os

import numpy as np
from scipy.stats import chi2

HERE = os.path.dirname(os.path.abspath(__file__))
CS4 = os.path.join(HERE, "..", "cs4")
READS = {"route_a": ("results/read/run1/ROUTE_A_READ.json", "results/calib/route_a_calib_declared.json"),
         "A": ("results/followup_read/A/run1/FOLLOWUP_READ.json", "results/calib/followup_calib_A_declared.json"),
         "B2": ("results/b2_read/run1/B2_READ.json", "results/calib/b2_calib_declared.json")}
BLOCK = "300"
GS = ("300", "1000", "3000", "10000")


def chi2_about_mean(mu, se):
    w = 1 / se ** 2
    m = float(np.sum(w * mu) / np.sum(w))
    return float(np.sum((mu - m) ** 2 / se ** 2)), len(mu) - 1, m


def pct(x, dof):
    return float(100 * chi2.cdf(x, dof))


def main():
    out, pooled = {}, {G: [0.0, 0] for G in GS}
    pooled_sealed = [0.0, 0]
    for test, (rp, cp) in READS.items():
        d = json.load(open(os.path.join(CS4, rp)))
        C = json.load(open(os.path.join(CS4, cp)))["files"]
        rec, res = d["records"], d["result"]
        files = list(res["mu_file"])
        mt = np.array([res["mu_file"][f] for f in files])
        g = np.array([(rec[f]["mu"] - C[f]["bias"]) / res["mu_file"][f] for f in files])
        row = dict(files=files, mu_tilde=mt.tolist(), gain=g.tolist(), by_G={})
        for G in GS:
            se = np.array([rec[f]["se"][G] for f in files]) / g
            x, dof, m = chi2_about_mean(mt, se)
            x1 = float(np.sum((mt - 1) ** 2 / se ** 2))
            row["by_G"][G] = dict(se_own=se.tolist(), weighted_mean=m, chi2=x, dof=dof, chi2_per_dof=x / dof,
                                  percentile=pct(x, dof), chi2_vs_1=x1, dof_vs_1=len(mt), percentile_vs_1=pct(x1, len(mt)))
            pooled[G][0] += x
            pooled[G][1] += dof
        ss = np.array([res["se_file"][f] for f in files])
        xs, dofs, _ = chi2_about_mean(mt, ss)
        row["sealed_se"] = dict(se=ss.tolist(), chi2=xs, dof=dofs, chi2_per_dof=xs / dofs, percentile=pct(xs, dofs))
        row["own_over_sealed_se"] = (np.array(row["by_G"][BLOCK]["se_own"]) / ss).tolist()
        pooled_sealed[0] += xs
        pooled_sealed[1] += dofs
        out[test] = row
    P = {G: dict(chi2=x, dof=n, chi2_per_dof=x / n, percentile=pct(x, n)) for G, (x, n) in pooled.items()}
    pb = P[BLOCK]
    single = [out[t]["by_G"][BLOCK]["percentile"] for t in out]
    validates = bool(2.5 <= pb["percentile"] <= 97.5 and all(0.5 <= p <= 99.5 for p in single))
    reading = ("validates" if validates else
               "too small: own SEs overstate the scatter" if pb["percentile"] < 2.5 else
               "too large: own SEs understate the scatter" if pb["percentile"] > 97.5 else
               "one statistic outside [0.5, 99.5]")
    res = dict(block=BLOCK, tests=out, pooled=P,
               pooled_sealed=dict(chi2=pooled_sealed[0], dof=pooled_sealed[1],
                                  chi2_per_dof=pooled_sealed[0] / pooled_sealed[1],
                                  percentile=pct(*pooled_sealed)),
               reading=reading, VALIDATES=validates,
               label="round 71; DESCRIPTIVE; data already seen (OWNBOOT_SE_CHECK.md)")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, "results", "ownboot_chi2.json"), "w"), indent=1)
    for t in out:
        b = out[t]["by_G"]
        print(t, " ".join(f"G={G}: chi2 {b[G]['chi2']:.2f}/{b[G]['dof']} pct {b[G]['percentile']:.1f}" for G in GS),
              f"| sealed SE: {out[t]['sealed_se']['chi2']:.2f}/{out[t]['sealed_se']['dof']} "
              f"pct {out[t]['sealed_se']['percentile']:.1f} | gain {np.round(out[t]['gain'], 4).tolist()}")
    print("pooled", {G: (round(v["chi2"], 2), v["dof"], round(v["chi2_per_dof"], 2), round(v["percentile"], 1))
                     for G, v in P.items()}, "sealed", round(res["pooled_sealed"]["chi2"], 2),
          round(res["pooled_sealed"]["percentile"], 1))
    print("reading:", reading)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

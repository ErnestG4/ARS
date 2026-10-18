"""POST-HOC, descriptive only (not part of either sealed rule): between-file consistency of the replications' sealed
reads (2026-10-18, after both compares). For each observable, χ²_between = Σ_f ((μ̃_f − μ̃_pool)/SE_f)² from the read
(run1; run1 = run2 bit for bit), against the same statistic on the 200 CUE calibration replicates (each file's μ̂ less
its bias, SE_f at the calibration SD floor, pooled with the sealed weights). Also each file's read bootstrap SEs
against its CUE SD.

  python followup_posthoc.py   → results/followup_read/POSTHOC_between_file.json
"""
import glob
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def one(obs):
    r = json.load(open(os.path.join(HERE, "results", "followup_read", obs, "run1", "FOLLOWUP_READ.json")))
    c = json.load(open(os.path.join(HERE, "results", "calib", f"followup_calib_{obs}_declared.json")))
    p = json.load(open(os.path.join(HERE, "results", f"followup_pred_{obs}.json")))
    v = r["result"]
    fs = list(v["mu_file"])
    mu, se = np.array([v["mu_file"][f] for f in fs]), np.array([v["se_file"][f] for f in fs])
    chi = float(np.sum(((mu - v["mu_pool"]) / se) ** 2))
    rows = {}
    for fn in glob.glob(os.path.join(HERE, "results", "followup_calfit", "fit_c*.jsonl")):
        for line in open(fn):
            q = json.loads(line)
            if q["obs"] == obs:
                rows.setdefault(q["rep"], {})[q["file"]] = q["mu"]
    w = np.array([p["weights"][f] for f in fs])
    sd = np.array([c["files"][f]["sd"] for f in fs])
    b = np.array([c["files"][f]["bias"] for f in fs])
    cal = []
    for d in rows.values():
        m = np.array([d[f] for f in fs]) - b
        cal.append(float(np.sum(((m - np.dot(w, m)) / sd) ** 2)))
    cal = np.array(cal)
    return dict(verdict=v["verdict"], mu_pool=v["mu_pool"], se_pool=v["se_pool"], band=v["band"],
                mu_file=dict(zip(fs, mu.tolist())), se_file=dict(zip(fs, se.tolist())),
                chi2_between=chi, dof=len(fs) - 1, calib_chi2_between=dict(
                    R=len(cal), mean=float(cal.mean()), q99=float(np.percentile(cal, 99)), max=float(cal.max()),
                    n_ge_read=int(np.sum(cal >= chi))),
                read_se_boot={f: r["records"][f]["se"] for f in fs}, calib_sd={f: c["files"][f]["sd"] for f in fs},
                read_estimate={f: {k: r["records"][f][k] for k in ("mu", "k3") if k in r["records"][f]} for f in fs})


if __name__ == "__main__":
    out = {"note": "POST-HOC, descriptive; not part of either sealed rule", "A": one("A"), "B": one("B")}
    json.dump(out, open(os.path.join(HERE, "results", "followup_read", "POSTHOC_between_file.json"), "w"), indent=1)
    for o in "AB":
        x = out[o]
        print(f"({o}) {x['verdict']}: χ²_between {x['chi2_between']:.1f} on {x['dof']}; calibration mean "
              f"{x['calib_chi2_between']['mean']:.2f}, q99 {x['calib_chi2_between']['q99']:.1f}, max "
              f"{x['calib_chi2_between']['max']:.1f} ({x['calib_chi2_between']['n_ge_read']}/200 ≥ the read)")

"""Round 73 (descriptive): the long-baseline block variance from disjoint blocks about the global mean
(L6_BIAS_CORRECTION.md). Spot, CPU.

  python round73.py blocks R OUT_DIR    per-block μ̂ for sequence R, every (test, file), G in GS → OUT_DIR/blocks_RRR.json
  python round73.py summary OUT_DIR     → OUT_DIR/R73_SUMMARY.json (W_glob, W_within, checks, revised zeros/long)
"""
import glob
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l6_base as B  # noqa: E402
import round72 as R72  # noqa: E402

GS = (300, 1000, 3000, 10000)
READS = {"route_a": "results/read/run1/ROUTE_A_READ.json", "A": "results/followup_read/A/run1/FOLLOWUP_READ.json",
         "B2": "results/b2_read/run1/B2_READ.json"}


def _mu_block(test, f, sp, x, S):
    RA, FR, BR, E, BP, fits, models, pb = S
    rng = np.random.default_rng(0)
    if test == "route_a":
        return RA.fit_file(fits[f], sp, rng, (), gof=False)["mu"]
    if test == "A":
        return FR.fit_file_A(models[f], FR.seq_A(sp), rng, block_lens=())["mu"]
    raw = E.zeros_stats(x, BP.L_star(), rng, n_boot=2)
    t = pb["files"][f]
    return (raw["k3bar"] - t["kappa3_sine"]) / t["dkappa3"]


def blocks(r, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    S = B._setup()
    x = np.load(os.path.join(R72.GEN, f"cue_{r:03d}.npy"))
    sp = np.diff(x)
    t = time.time()
    out = {}
    for test, files in R72._files(S):
        out[test] = {}
        for f in files:
            out[test][f] = {}
            for G in GS:
                k = len(x) // G
                mus = []
                for b in range(k):
                    if test == "B2":
                        sel = (x >= b * G) & (x < (b + 1) * G)
                        xb = x[sel] - b * G
                        mus.append(_mu_block(test, f, None, xb, S))
                    else:
                        mus.append(_mu_block(test, f, sp[b * G:(b + 1) * G], None, S))
                out[test][f][str(G)] = mus
    rec = dict(r=r, blocks=out, wall_s=round(time.time() - t, 1), env=B.env())
    json.dump(rec, open(os.path.join(out_dir, f"blocks_{r:03d}.json"), "w"), indent=1)
    print(r, rec["wall_s"], flush=True)
    return 0


def summary(out_dir):
    recs = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(out_dir, "blocks_*.json")))]
    cue = B._load(R72.STATS, "cue")
    cmp_ = json.load(open(os.path.join(HERE, "results", "base", "compare.json")))
    res = dict(n_seq=len(recs), tests={})
    changed_any = False
    for test in B.TESTS:
        rd = json.load(open(os.path.join(B.CS4, READS[test])))["records"]
        V = B._var_table(cue, test)
        res["tests"][test] = {}
        for f in V:
            nz = rd[f]["n_zeros"] if test == "B2" else rd[f]["n"]
            row = {}
            for G in GS:
                per = [np.array([m for m in rec["blocks"][test][f][str(G)] if m is not None], float) for rec in recs]
                n_fail = sum(len(rec["blocks"][test][f][str(G)]) for rec in recs) - sum(len(p) for p in per)
                allb = np.concatenate(per)
                M = len(allb)
                mbar = float(allb.mean())
                Wg = G * float(np.sum((allb - mbar) ** 2)) / (M - 1)
                per_seq = np.array([G * float(np.mean((p - mbar) ** 2)) for p in per])
                Wg_se = float(per_seq.std(ddof=1) / math.sqrt(len(per_seq)))
                Ww = float(np.mean([G * float(np.mean((p - p.mean()) ** 2)) for p in per]))
                Wm = float(V[f][str(G)].mean())
                Wm_se = float(V[f][str(G)].std(ddof=1) / math.sqrt(len(V[f][str(G)])))
                vz = rd[f]["se"][str(G)] ** 2
                old = cmp_["tests"][test][f][str(G)]
                new_ratio = vz / (Wg / nz)
                new_ratio_se = new_ratio * Wg_se / Wg
                ch = bool(G >= 3000 and abs(new_ratio - old["zeros_over_long"]) > new_ratio_se)
                changed_any |= ch
                row[str(G)] = dict(M=M, n_fit_fail=int(n_fail), W_glob=Wg, W_glob_se=Wg_se, W_within=Ww,
                                   within_over_glob=Ww / Wg, W_mbb=Wm, W_mbb_se=Wm_se,
                                   z_glob_vs_mbb=(Wg - Wm) / math.sqrt(Wg_se ** 2 + Wm_se ** 2),
                                   concat_over_glob=old["var_long_concat"] / (Wg / nz),
                                   zeros_over_long_old=old["zeros_over_long"],
                                   zeros_over_long_concat=old["zeros_over_long_concat"],
                                   zeros_over_long_revised=new_ratio, zeros_over_long_revised_se=new_ratio_se,
                                   changed=ch)
            res["tests"][test][f] = row
    res["changed"] = bool(changed_any)
    res["label"] = "round 73; DESCRIPTIVE (L6_BIAS_CORRECTION.md)"
    json.dump(res, open(os.path.join(out_dir, "R73_SUMMARY.json"), "w"), indent=1)
    for test in B.TESTS:
        for f, row in res["tests"][test].items():
            print(test, f[:16], " | ".join(
                f"G{G}: glob/mbb {row[str(G)]['W_glob'] / row[str(G)]['W_mbb']:.3f} (z {row[str(G)]['z_glob_vs_mbb']:+.1f}) "
                f"within/glob {row[str(G)]['within_over_glob']:.3f} ratio old {row[str(G)]['zeros_over_long_old']:.3f} "
                f"new {row[str(G)]['zeros_over_long_revised']:.3f}±{row[str(G)]['zeros_over_long_revised_se']:.3f}"
                f"{' *' if row[str(G)]['changed'] else ''} fail {row[str(G)]['n_fit_fail']}" for G in GS))
    print("changed:", res["changed"])
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "blocks":
        sys.exit(blocks(int(sys.argv[2]), sys.argv[3]))
    if sys.argv[1] == "summary":
        sys.exit(summary(sys.argv[2]))
    raise SystemExit(f"unknown command {sys.argv[1]}")

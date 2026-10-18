"""Corrected (B): calibration replicates from scratch (CORRECTED_B_DESIGN.md §4; round 57/58). Data-free.

R = 200 CUE_1000 replicates per F6 file at its pre-data size, through the offset-averaged estimator (b2_est.cue_stats,
the read's code path) at L = L* (results/b2_rule.json; fails closed without it). Stored per (replicate, file):
k̄₃, k₃ at each of the 32 offsets, and the joint-offset segment-bootstrap SE at each segment length (B = 200).
Prediction-independent (μ units come at declaration). Seed [20261018, 58, i, rep] (one stream: the draws, then the
bootstrap) — disjoint from every earlier use.

  python b2_calsamp.py run REP0 REP1 OUT_DIR      (char GPU)
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b2_est as E  # noqa: E402
import b2_pred as BP  # noqa: E402
import followup_pred as P  # noqa: E402


def run(r0, r1, out_dir):
    import cbe
    L = BP.L_star()
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"b2cal_{r0:03d}_{r1:03d}.jsonl")
    done = {(r["rep"], r["file"]) for r in map(json.loads, open(path))} if os.path.exists(path) else set()
    _, nf = P.counts(BP.F6)
    sampler = lambda rng, k: cbe.sample(rng, k, 1000, 2.0, gpu=True)[0]                      # noqa: E731
    for rep in range(r0, r1):
        for i, f in enumerate(BP.F6):
            if (rep, f) in done:
                continue
            t = time.time()
            n = int(round(nf[f]))
            res = E.cue_stats(sampler, n, L, np.random.default_rng([20261018, 58, i, rep]))
            res.update(rep=rep, file=f, i=i, n=n, t=round(time.time() - t, 1))
            with open(path, "a") as fh:
                fh.write(json.dumps(res) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            print(f"rep {rep} {f}: k̄3 {res['k3bar']:+.5f} ({res['t']} s)", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])

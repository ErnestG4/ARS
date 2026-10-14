"""Route (a) pre-read: the GUE calibration (fortieth round). Every replicate is a full-size CUE_1000 sample for each F3
file (n_f spacings, the pre-data count; consecutive matrices concatenated), fitted exactly as the read will fit the
zeros (route_a_read.MuFit, the same model and window); expected μ̂ ≈ 0. Recorded per (replicate, file): μ̂, the
moving-block bootstrap SE at each candidate block length, χ² (GoF), and timing. Checkpointed per (replicate, file):
append + fsync; a restart skips the done keys; a torn last line is dropped. Seeds are (file index, replicate).

  python route_a_calib.py run R0 R1 OUT.jsonl [BETA]     replicates R0..R1−1 (BETA = 2 is CUE; other β = red paths)
  python route_a_calib.py summary OUT.jsonl [...]        bias, spread, SE coverage per block length, χ² null quantiles
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cbe  # noqa: E402
import route_a_read as RR  # noqa: E402

N_MAT = 1000                       # fortieth round: N ≥ 10³ per block
BLOCK_LENS = (300, 1000, 3000, 10000)
CHUNK = 2000                       # matrices per GPU call


def cue_spacings(rng, n, beta=2.0, gpu=True):
    """n consecutive spacings from independent CβE_1000 matrices (Killip–Nenciu sampler), concatenated."""
    need = -(-n // N_MAT)
    out = []
    while need > 0:
        k = min(CHUNK, need)
        th, _ = cbe.sample(rng, k, N_MAT, beta, gpu=gpu)
        out.append(cbe.spacings(th).ravel())
        need -= k
    return np.concatenate(out)[:n]


def done_keys(path):
    keys, good = set(), []
    if os.path.exists(path):
        lines = open(path).read().split("\n")
        for ln in lines:
            if not ln.strip():
                continue
            try:
                r = json.loads(ln)
            except json.JSONDecodeError:          # torn last line
                continue
            keys.add((r["rep"], r["file"], r["beta"]))
            good.append(ln)
        with open(path, "w") as fh:               # rewrite without a torn line
            fh.write("".join(x + "\n" for x in good))
    return keys


def run(r0, r1, out, beta=2.0):
    pred = json.load(open(RR.PRED))
    _, n = RR.weights()
    fits = {f: RR.MuFit.for_file(f, pred) for f in RR.F3}
    done = done_keys(out)
    files = list(RR.F3)
    for rep in range(r0, r1):
        for i, f in enumerate(files):
            if (rep, f, beta) in done:
                continue
            t = time.time()
            rng = np.random.default_rng([20261013, i, rep, int(round(beta * 1000))])
            s = cue_spacings(rng, int(round(n[f])), beta)
            t1 = time.time()
            res = RR.fit_file(fits[f], s, rng, BLOCK_LENS)
            res.update(rep=rep, file=f, beta=beta, t_sample=round(t1 - t, 1), t_fit=round(time.time() - t1, 1))
            with open(out, "a") as fh:
                fh.write(json.dumps(res) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            print(f"rep {rep} {f}: μ̂ {res['mu']:+.4f} SE(1000) {res['se'][1000]:.4f} χ² {res['chi2']:.1f} "
                  f"({res['t_sample']}+{res['t_fit']} s)", flush=True)


def load(paths, beta=2.0):
    rows = {}
    for p in paths:
        for ln in open(p):
            if ln.strip():
                r = json.loads(ln)
                if r["beta"] == beta:
                    rows[(r["rep"], r["file"])] = r
    return rows


def summary(paths):
    rows = load(paths)
    files = list(RR.F3)
    out = {}
    for f in files:
        R = [r for (rep, ff), r in sorted(rows.items()) if ff == f]
        mu = np.array([r["mu"] for r in R])
        sd = float(mu.std(ddof=1))
        se = {L: float(np.mean([r["se"][str(L)] if str(L) in r["se"] else r["se"][L] for r in R])) for L in BLOCK_LENS}
        chi = np.array([r["chi2"] for r in R])
        out[f] = dict(n_rep=len(R), mu_mean=float(mu.mean()), mu_mean_se=sd / math.sqrt(len(R)), mu_sd=sd,
                      se_mean=se, se_over_sd={L: se[L] / sd for L in BLOCK_LENS},
                      chi2_mean=float(chi.mean()), chi2_var=float(chi.var(ddof=1)),
                      chi2_q=dict(zip(("50", "90", "99", "max"), map(float, np.percentile(chi, [50, 90, 99, 100])))))
        v = out[f]
        print(f"{f}: R={v['n_rep']}  μ̂ mean {v['mu_mean']:+.5f} ± {v['mu_mean_se']:.5f}  SD {sd:.5f}  "
              + "  ".join(f"SE{L}/SD {v['se_over_sd'][L]:.3f}" for L in BLOCK_LENS)
              + f"  χ² mean {v['chi2_mean']:.1f} var {v['chi2_var']:.1f} q99 {v['chi2_q']['99']:.1f}", flush=True)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], float(sys.argv[5]) if len(sys.argv) > 5 else 2.0)
    elif sys.argv[1] == "summary":
        summary(sys.argv[2:])

"""CUE_1000 replicates for the follow-up selection rule's SE_stat (FOLLOWUP_SELECTION_RULE.md, round 48). Data-free.

R = 100 replicates per F3-geometry file (n_f from θ, route_a_read.weights), the same replicates for both candidates,
seeds [20261015, 48, i, rep] (disjoint from the calibration's [20261013, …], the dry run's [20261014, 7, …] and the
pipeline check's [20261013, 99, …]). Killip–Nenciu sampler on char's GPU (cbe.py), as route (a)'s calibration.
Per replicate and file it stores only sufficient summaries, so either candidate's statistic can be evaluated later
without resampling:
  (A) the next-nearest-neighbour spacings s⁽²⁾ = s_i + s_{i+1} (circular within each matrix, first n_f): a histogram on
      [0, 3) with 30,000 bins of 1e-4, plus the count at or above 3 (results/followup_reps/hist/<rep>_<i>.npy, uint32);
  (B) for each L ∈ {0.5, 1.0, 1.5, 2.0, 3.0}: the distribution (bincount) of the counts N_j in the disjoint windows
      [jL, (j+1)L), j < ⌊1000/L⌋, of each matrix used (unfolded angle N·θ/2π), in the JSONL row.

  python followup_reps.py run REP0 REP1 OUT_DIR
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cbe  # noqa: E402
import route_a_read as RR  # noqa: E402

N_MAT, CHUNK = 1000, 2000
LS = (0.5, 1.0, 1.5, 2.0, 3.0)
HBINS, HMAX = 30_000, 3.0


def one(rng, n):
    need = -(-n // N_MAT)
    hist = np.zeros(HBINS + 1, np.uint64)
    counts = {L: np.zeros(64, np.int64) for L in LS}
    left = n
    while need > 0:
        k = min(CHUNK, need)
        th, _ = cbe.sample(rng, k, N_MAT, 2.0, gpu=True)
        th = np.asarray(th)
        s = cbe.spacings(th)
        s2 = (s + np.roll(s, -1, axis=1)).ravel()[:left]
        left -= len(s2)
        b = np.minimum((s2 / HMAX * HBINS).astype(np.int64), HBINS)
        hist += np.bincount(b, minlength=HBINS + 1).astype(np.uint64)
        x = np.sort(np.mod(th, 2 * np.pi), axis=1) * N_MAT / (2 * np.pi)
        for L in LS:
            nw = int(N_MAT // L)
            j = (x // L).astype(np.int64)
            ok = j < nw
            per = np.zeros((k, nw), np.int64)
            rows = np.broadcast_to(np.arange(k)[:, None], j.shape)
            np.add.at(per, (rows[ok], j[ok]), 1)
            counts[L] += np.bincount(per.ravel(), minlength=64)[:64]
        need -= k
    return hist.astype(np.uint32), {str(L): c.tolist() for L, c in counts.items()}


def run(r0, r1, out_dir):
    os.makedirs(os.path.join(out_dir, "hist"), exist_ok=True)
    path = os.path.join(out_dir, f"reps_{r0:03d}_{r1:03d}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["rep"], r["file"]) for r in map(json.loads, open(path))}
    _, nf = RR.weights()
    for rep in range(r0, r1):
        for i, f in enumerate(RR.F3):
            if (rep, f) in done:
                continue
            t = time.time()
            n = int(round(nf[f]))
            rng = np.random.default_rng([20261015, 48, i, rep])
            hist, counts = one(rng, n)
            hp = os.path.join(out_dir, "hist", f"{rep:03d}_{i}.npy")
            np.save(hp, hist)
            row = dict(rep=rep, file=f, n=n, hist=os.path.relpath(hp, out_dir), counts=counts,
                       t=round(time.time() - t, 1))
            with open(path, "a") as fh:
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            print(f"rep {rep} {f}: n {n}, ({row['t']} s)", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])

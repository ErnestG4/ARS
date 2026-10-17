"""Calibration samples for the two route (a) replications at the final geometry (round 52; FOLLOWUP_REPLICATION_RULES.md
§5 step 2). Data-free: CUE_1000 draws only.

R = 200 replicates per file (as route (a)'s calibration), at each file's pre-data size n_f (exact θ over the declared
height range, followup_pred.counts): F4's three files for (A), F5's four for (B). Killip–Nenciu sampler on char's GPU
(cbe.py), consecutive matrices concatenated, ⌈n_f/1000⌉ matrices per (replicate, file). Seeds [20261017, 52, SET, i, rep]
(SET = 4 or 5, i = the file's index in followup_pred.F4/F5), disjoint from every earlier use ([20261013, …] route (a)'s
calibration and pipeline check, [20261014, 7, …] the dry run, [20261015, 48, …] the selection replicates,
[20261016, 50|51, …] the CUE_N known-answer runs).

Stored per (replicate, file), prediction-independent, so the fits run after the prediction is tagged without resampling:
  (A) the bin index ⌊s⁽²⁾/1e-4⌋ (capped at 30,000) of every next-nearest-neighbour spacing s⁽²⁾_i = s_i + s_{i+1}, circular
      within each matrix, first n_f, in sequence order (uint16; the block bootstrap needs the order);
  (B) the counts N_j in the disjoint windows [jL, (j + 1)L), j < ⌊1000/L⌋, L = 3, of each matrix (unfolded angle
      N·θ/2π), in sequence order (uint8).
Checkpointed: the .npy is written first, then one JSONL row (append + fsync); a restart skips rows already written.

  python followup_calsamp.py run REP0 REP1 OUT_DIR
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cbe  # noqa: E402
import followup_pred as P  # noqa: E402

N_MAT, CHUNK = 1000, 2000
HB, HBINS = 1e-4, 30_000
L_B = P.L_B
SETS = {4: ("A", P.F4), 5: ("B", P.F5)}


def one(rng, n, obs):
    need = -(-n // N_MAT)
    out, left = [], n
    while need > 0:
        k = min(CHUNK, need)
        th, _ = cbe.sample(rng, k, N_MAT, 2.0, gpu=True)
        th = np.asarray(th)
        if obs == "A":
            s = cbe.spacings(th)
            s2 = (s + np.roll(s, -1, axis=1)).ravel()[:left]
            left -= len(s2)
            out.append(np.minimum((s2 / HB).astype(np.int64), HBINS).astype(np.uint16))
        else:
            x = np.sort(np.mod(th, 2 * np.pi), axis=1) * N_MAT / (2 * np.pi)
            nw = int(N_MAT // L_B)
            j = (x // L_B).astype(np.int64)
            ok = j < nw
            per = np.zeros((k, nw), np.int64)
            rows = np.broadcast_to(np.arange(k)[:, None], j.shape)
            np.add.at(per, (rows[ok], j[ok]), 1)
            assert per.max() < 256
            out.append(per.ravel().astype(np.uint8))
        need -= k
    return np.concatenate(out)


def run(r0, r1, out_dir):
    os.makedirs(os.path.join(out_dir, "seq"), exist_ok=True)
    path = os.path.join(out_dir, f"samp_{r0:03d}_{r1:03d}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["rep"], r["file"]) for r in map(json.loads, open(path))}
    nf = {}
    for S, (_, F) in SETS.items():
        nf.update(P.counts(F)[1])
    for rep in range(r0, r1):
        for S, (obs, F) in SETS.items():
            for i, f in enumerate(F):
                if (rep, f) in done:
                    continue
                t = time.time()
                n = int(round(nf[f]))
                rng = np.random.default_rng([20261017, 52, S, i, rep])
                seq = one(rng, n, obs)
                sp = os.path.join(out_dir, "seq", f"{obs}_{rep:03d}_{i}.npy")
                np.save(sp, seq)
                row = dict(rep=rep, set=f"F{S}", obs=obs, file=f, i=i, n=n, len=int(len(seq)),
                           seq=os.path.relpath(sp, out_dir), t=round(time.time() - t, 1))
                with open(path, "a") as fh:
                    fh.write(json.dumps(row) + "\n")
                    fh.flush()
                    os.fsync(fh.fileno())
                print(f"rep {rep} F{S} {f}: n {n}, len {len(seq)} ({row['t']} s)", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])

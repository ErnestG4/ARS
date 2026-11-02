# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 archive cost rule (TOOLKIT §9.H), as in run_fn1_archive2_spot.sh, for the pueue continuation.

  python fn1_archive2_costs.py ROOT first|check

The model is unchanged. Per field, the first-wave cost at k = 101 / 555 / 1009 is interpolated in k, flat beyond. Those
were wall seconds at nice 10 with free cores, and single-threaded, so wall ≈ CPU there (the dry reads at that time:
wall 1297 s, CPU 1290 s).

Measured cost per completed non-calibration task:
- **xargs phase:** the wall seconds in logs2/tasks_D*.log (as before).
- **pueue phase:** CPU seconds (user + sys) from logs2/cpu_D*.log (written by run_fn1_archive2_chunk.sh). Under
  pq-fill (CPUWeight=idle) wall time measures contention, not cost, and the approved price is in core-h.

Rule: sum measured / sum own model ≤ 1.25 → OK, else EXCEEDS. Single tasks above 2× their model are listed (reported,
not a stop rule). The last line printed is OK or EXCEEDS; exit status 0 for OK, 1 for EXCEEDS.
"""
import glob, json, os, sys
import numpy as np

root, mode = sys.argv[1], sys.argv[2]
jobs = [(int(l.split()[0]), int(l.split()[1])) for l in open(root + "/jobs2.txt")]
meas, src = {}, {}
for f in glob.glob(root + "/logs2/tasks_D*.log"):
    D = -int(os.path.basename(f)[7:-4])
    for l in open(f):
        w = l.split()
        if len(w) == 3:
            meas[(D, int(w[0]))] = float(w[2]); src[(D, int(w[0]))] = "wall"
for f in glob.glob(root + "/logs2/cpu_D*.log"):
    D = -int(os.path.basename(f)[5:-4])
    for l in open(f):
        w = l.split()
        if len(w) == 4:
            meas[(D, int(w[0]))] = float(w[1]) + float(w[2]); src[(D, int(w[0]))] = "cpu"
CAL = (101, 555, 1009)
fields = sorted({d for d, _ in jobs})
miss = [(D, k) for D in fields for k in CAL if (D, k) not in meas]
if miss:
    print("calibration points missing:", miss); print("EXCEEDS"); sys.exit(1)
model = {}
for D in fields:
    ys = [meas[(D, k)] for k in CAL]
    for d, k in jobs:
        if d == D:
            model[(d, k)] = float(np.interp(k, CAL, ys))
done = [j for j in jobs if j in meas and j[1] not in CAL]
out = {"projection_core_h_new_segments": sum(model.values()) / 3600, "n_jobs": len(jobs), "n_done_noncal": len(done),
       "n_done_by_source": {s: sum(1 for j in done if src[j] == s) for s in ("wall", "cpu")}}
if not done:
    print(json.dumps(out)); print("no measured non-calibration tasks"); print("EXCEEDS"); sys.exit(1)
r = sum(meas[j] for j in done) / sum(model[j] for j in done)
out["ratio_measured_over_own_model"] = r
for s in ("wall", "cpu"):
    d = [j for j in done if src[j] == s]
    if d:
        out[f"ratio_{s}_only"] = sum(meas[j] for j in d) / sum(model[j] for j in d)
out["over_2x"] = [[d, k, meas[(d, k)], model[(d, k)], src[(d, k)]] for d, k in done if meas[(d, k)] > 2 * model[(d, k)]]
print(json.dumps(out))
ok = r <= 1.25
print("OK" if ok else "EXCEEDS")
sys.exit(0 if ok else 1)

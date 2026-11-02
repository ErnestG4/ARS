#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1 stage 2 (Will, 2026-11-02: "Spot: approved for the archive extension; reads run sequentially"): extend the seven
# w = 2 angle archives to 1.01·10¹¹ (segments 0…1009 of 10⁸) in NEW directories /mnt/data/fn1/archive_1e11_D*, so the
# stage-1 directories and their sealed MANIFEST.json pins stay untouched.
#  1. byte-copy stage-1 segments 0…100 into the new directory and check each against the stage-1 MANIFEST.json sha256
#     (and that stage-1 manifest against its sealed pin in fn1_pins.json); any mismatch stops the run;
#  2. generate segments 101…1009 with the unchanged fn1_archive.py (task skips existing files);
#  3. TOOLKIT §9.H first wave (cheapest / median / most expensive segment per field), per-job interpolated cost
#     model, cost rule at half and end against each job's own model (stop above 1.25×);
#  4. fn1_archive.py manifest over all 1010 segments → archive_1e11_D*/MANIFEST.json (integrity re-checked on every row,
#     prefix included).
# Generation, integrity and hashes only; no statistic. Run inside tmux `claude`, after a load check:
#   bash run_fn1_archive2_spot.sh [NPROC]
set -u
NPROC=${1:-24}
CODE=~/tmp/claude/specarith/fn1
ROOT=/mnt/data/fn1; LG=$ROOT/logs2
PY=~/miniforge3/envs/ph6c/bin/python
mountpoint -q /mnt/data || { echo "REFUSED: /mnt/data is not a mount point"; exit 2; }
FREE_GB=$(df -BG --output=avail /mnt/data | tail -1 | tr -dc 0-9)
[ "$FREE_GB" -gt 160 ] || { echo "not enough space on /mnt/data: ${FREE_GB} GB free, about 125 + 35 margin needed"; exit 1; }
cd $CODE || exit 1
mkdir -p $LG
rm -f $ROOT/ALL_DONE2 $ROOT/STOPPED2
export OMP_NUM_THREADS=1 PY ROOT LG
$PY fn1_archive.py selftest > $LG/selftest.log 2>&1 || { echo "selftest failed" > $ROOT/STOPPED2; exit 1; }
# 1. prefix copy + check
$PY - "$ROOT" fn1_pins.json > $LG/prefix_check.log 2>&1 <<'PY' || { echo "prefix check failed" > $ROOT/STOPPED2; exit 1; }
import hashlib, json, os, shutil, sys
root, pins = sys.argv[1], json.load(open(sys.argv[2]))
for D in (-7, -8, -11, -19, -43, -67, -163):
    src, dst = f"{root}/archive_1e10_D{-D}", f"{root}/archive_1e11_D{-D}"
    mp = f"{src}/MANIFEST.json"
    assert hashlib.sha256(open(mp, "rb").read()).hexdigest() == pins["archives"][str(D)]["manifest_sha256"], ("stage-1 pin", D)
    os.makedirs(dst, exist_ok=True)
    for s in json.load(open(mp))["segments"]:
        a, b = f"{src}/seg_{s['k']:04d}.npy", f"{dst}/seg_{s['k']:04d}.npy"
        if not os.path.exists(b):
            shutil.copyfile(a, b + ".part"); os.replace(b + ".part", b)
        assert hashlib.sha256(open(b, "rb").read()).hexdigest() == s["sha256"], ("prefix sha", D, s["k"])
    print(D, "prefix ok", len(json.load(open(mp))["segments"]), "segments", flush=True)
print("ALL PREFIX OK")
PY
grep -q "ALL PREFIX OK" $LG/prefix_check.log || { echo "prefix check incomplete" > $ROOT/STOPPED2; exit 1; }
# 2. jobs: segments not yet present only
: > $ROOT/jobs2.txt
for D in -7 -8 -11 -19 -43 -67 -163; do
  $PY fn1_archive.py jobs $D 1.01e11 | awk -v D=$D '$1 >= 101 {print D, $1, $2}' >> $ROOT/jobs2.txt
done
NJ=$(wc -l < $ROOT/jobs2.txt)
[ "$NJ" -eq $((7 * 909)) ] || { echo "job count $NJ != 6363" > $ROOT/STOPPED2; exit 1; }
RUN='mountpoint -q /mnt/data && nice -n 10 $PY fn1_archive.py task $0 $1 $ROOT/archive_1e11_D${0#-} >> $LG/tasks_D${0#-}.log 2>&1 && echo "$0 $1" >> $LG/done.txt || echo "$0 $1" >> $LG/failed.txt'
# TOOLKIT §9.H (revision 2026-11-02, after a first launch whose first wave timed only k = 101..104, the cheapest
# segments; that launch was stopped by PID before wave 2, its 24 segments kept). Job kind = field D (7 kinds); cost
# covariate = segment index k (segment midpoint p; split-prime count x Cornacchia cost per prime), read without outcomes.
# First wave: k = 101 (cheapest), 555 (median), 1009 (most expensive) for every field. Each job's model is the measured
# cost interpolated linearly in k between those three, flat beyond them (no extrapolation). The cost rule then checks
# completed non-calibration tasks against their own job's model (sum measured / sum own model ≤ 1.25); single tasks
# above 2x their own model are listed (reported, not a stop rule).
costs() {
$PY - "$ROOT" "$1" <<'PY'
import sys, glob, os, json
import numpy as np
root, mode = sys.argv[1], sys.argv[2]
jobs = [(int(l.split()[0]), int(l.split()[1])) for l in open(root + "/jobs2.txt")]
meas = {}
for f in glob.glob(root + "/logs2/tasks_D*.log"):
    D = -int(os.path.basename(f)[7:-4])
    for l in open(f):
        w = l.split()
        if len(w) == 3:
            meas[(D, int(w[0]))] = float(w[2])
CAL = (101, 555, 1009)
miss = [(D, k) for D in sorted({d for d, _ in jobs}) for k in CAL if (D, k) not in meas]
if miss:
    print("calibration points missing:", miss); print("EXCEEDS"); sys.exit(0)
model = {}
for D in sorted({d for d, _ in jobs}):
    ys = [meas[(D, k)] for k in CAL]
    for d, k in jobs:
        if d == D:
            model[(d, k)] = float(np.interp(k, CAL, ys))
proj_h = sum(model.values()) / 3600
done = [j for j in jobs if j in meas and j[1] not in CAL]
out = {"projection_core_h_new_segments": proj_h, "n_jobs": len(jobs), "n_done_noncal": len(done),
       "calibration_s": {str(D): [meas[(D, k)] for k in CAL] for D in sorted({d for d, _ in jobs})}}
if mode == "first":
    print(json.dumps(out)); print("OK" if proj_h <= 1.25 * 175 else "EXCEEDS"); sys.exit(0)
if not done:
    print("no measured non-calibration tasks"); print("EXCEEDS"); sys.exit(0)
r = sum(meas[j] for j in done) / sum(model[j] for j in done)
out["ratio_measured_over_own_model"] = r
out["over_2x"] = [[d, k, meas[(d, k)], model[(d, k)]] for d, k in done if meas[(d, k)] > 2 * model[(d, k)]]
print(json.dumps(out)); print("OK" if r <= 1.25 else "EXCEEDS")
PY
}
echo "$(date -Is) [CC specarith] fn1 stage-2 archives to 1.01e11: start, 9.H first wave ($NPROC procs, $ROOT/archive_1e11_D*)" >> ~/claude-work.log
for D in -7 -8 -11 -19 -43 -67 -163; do for k in 101 555 1009; do echo "$D $k"; done; done > $ROOT/firstwave2_jobs.txt
cat $ROOT/firstwave2_jobs.txt | xargs -P 21 -n 2 sh -c "$RUN"
costs first > $ROOT/first_wave2.txt
if grep -q EXCEEDS $ROOT/first_wave2.txt || [ -s $LG/failed.txt ]; then echo "first wave over the approved price or a task failed" > $ROOT/STOPPED2; exit 1; fi
# remaining jobs (task skips existing segments), interleaved by k, in two chunks with the per-job cost rule after each
sort -k2,2n -k1,1n $ROOT/jobs2.txt | cut -d' ' -f1,2 > $ROOT/jobs2_order.txt
NJ=$(wc -l < $ROOT/jobs2_order.txt); HALF=$((NJ / 2))
head -n "$HALF" $ROOT/jobs2_order.txt | xargs -P "$NPROC" -n 2 sh -c "$RUN"
costs check > $ROOT/mid_run2.txt
if grep -q EXCEEDS $ROOT/mid_run2.txt || [ -s $LG/failed.txt ]; then echo "mid-run over the per-job cost model or a task failed" > $ROOT/STOPPED2; exit 1; fi
tail -n +"$((HALF + 1))" $ROOT/jobs2_order.txt | xargs -P "$NPROC" -n 2 sh -c "$RUN"
[ -s $LG/failed.txt ] && { echo "task failures" > $ROOT/STOPPED2; exit 1; }
costs check > $ROOT/final_ratio2.txt
mountpoint -q /mnt/data || { echo "REFUSED at manifest: /mnt/data is not a mount point" > $ROOT/STOPPED2; exit 2; }
for D in -7 -8 -11 -19 -43 -67 -163; do
  MANIFEST_PROCS=$NPROC nice -n 10 $PY fn1_archive.py manifest $D $ROOT/archive_1e11_D${D#-} 1.01e11 > $LG/manifest_D${D#-}.log 2>&1
  echo "D=$D exit=$?" >> $ROOT/summary2.exit
done
date -Is > $ROOT/ALL_DONE2
echo "$(date -Is) [CC specarith] fn1 stage-2 archives to 1.01e11: done" >> ~/claude-work.log

#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1 stage 2 (Will, 2026-11-02: "Spot: approved for the archive extension; reads run sequentially"): extend the seven
# w = 2 angle archives to 1.01·10¹¹ (segments 0…1009 of 10⁸) in NEW directories /mnt/data/fn1/archive_1e11_D*, so the
# stage-1 directories and their sealed MANIFEST.json pins stay untouched.
#  1. byte-copy stage-1 segments 0…100 into the new directory and check each against the stage-1 MANIFEST.json sha256
#     (and that stage-1 manifest against its sealed pin in fn1_pins.json); any mismatch stops the run;
#  2. generate segments 101…1009 with the unchanged fn1_archive.py (task skips existing files);
#  3. cost checks over the generated tasks at the first wave, half and end (stop above 1.25× the model);
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
ratio() {
$PY - "$ROOT" "$1" <<'PY'
import sys, glob, os
root, n = sys.argv[1], int(sys.argv[2])
pred = {(int(l.split()[0]), int(l.split()[1])): float(l.split()[2]) for l in open(root + "/jobs2.txt")}
meas = []
for f in glob.glob(root + "/logs2/tasks_D*.log"):
    D = -int(os.path.basename(f)[7:-4])
    meas += [((D, int(l.split()[0])), float(l.split()[2])) for l in open(f) if len(l.split()) == 3]
meas = meas[:n] if n else meas
if not meas:
    print("no measured tasks"); print("EXCEEDS"); sys.exit(0)
r = sum(s for _, s in meas) / sum(pred[k] for k, _ in meas)
print(f"{len(meas)} tasks, measured/model = {r:.3f}")
print("OK" if r <= 1.25 else "EXCEEDS")
PY
}
echo "$(date -Is) [CC specarith] fn1 stage-2 archives to 1.01e11: start ($NPROC procs, $ROOT/archive_1e11_D*)" >> ~/claude-work.log
# interleave fields so each wave mixes them
sort -k2,2n -k1,1n $ROOT/jobs2.txt > $ROOT/jobs2_order.txt
HALF=$((NJ / 2))
head -n "$NPROC" $ROOT/jobs2_order.txt | cut -d' ' -f1,2 | xargs -P "$NPROC" -n 2 sh -c "$RUN"
ratio $NPROC > $ROOT/first_wave2.txt
if grep -q EXCEEDS $ROOT/first_wave2.txt || [ -s $LG/failed.txt ]; then echo "first wave over the cost model or a task failed" > $ROOT/STOPPED2; exit 1; fi
sed -n "$((NPROC + 1)),${HALF}p" $ROOT/jobs2_order.txt | cut -d' ' -f1,2 | xargs -P "$NPROC" -n 2 sh -c "$RUN"
ratio $HALF > $ROOT/mid_run2.txt
if grep -q EXCEEDS $ROOT/mid_run2.txt || [ -s $LG/failed.txt ]; then echo "mid-run over the cost model or a task failed" > $ROOT/STOPPED2; exit 1; fi
tail -n +"$((HALF + 1))" $ROOT/jobs2_order.txt | cut -d' ' -f1,2 | xargs -P "$NPROC" -n 2 sh -c "$RUN"
[ -s $LG/failed.txt ] && { echo "task failures" > $ROOT/STOPPED2; exit 1; }
ratio 0 > $ROOT/final_ratio2.txt
mountpoint -q /mnt/data || { echo "REFUSED at manifest: /mnt/data is not a mount point" > $ROOT/STOPPED2; exit 2; }
for D in -7 -8 -11 -19 -43 -67 -163; do
  MANIFEST_PROCS=$NPROC nice -n 10 $PY fn1_archive.py manifest $D $ROOT/archive_1e11_D${D#-} 1.01e11 > $LG/manifest_D${D#-}.log 2>&1
  echo "D=$D exit=$?" >> $ROOT/summary2.exit
done
date -Is > $ROOT/ALL_DONE2
echo "$(date -Is) [CC specarith] fn1 stage-2 archives to 1.01e11: done" >> ~/claude-work.log

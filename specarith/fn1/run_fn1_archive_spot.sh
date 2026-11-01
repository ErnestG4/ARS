#!/usr/bin/env bash
# FN1 stage 1 (Will, 2026-10-31: staged, 10¹⁰ first): the seven w = 2 angle archives to 1.01·10¹⁰ (101 segments of 10⁸
# each) under /mnt/data/fn1/. Generation, integrity and hashes only; no statistic. The 10¹⁰ archives are a prefix of
# any later 10¹¹ stage (contiguous segments; a later run adds segments 101…1009). Mount guard and free-space check;
# cost checks over all fields' tasks at the first wave, half and end (stop above 1.25×). Model ≈ 15.9 spot core-h.
# Run inside tmux `claude`, after a load check:  bash run_fn1_archive_spot.sh [NPROC]
set -u
NPROC=${1:-20}
CODE=~/tmp/claude/specarith/fn1
ROOT=/mnt/data/fn1; LG=$ROOT/logs
PY=~/miniforge3/envs/ph6c/bin/python
mountpoint -q /mnt/data || { echo "REFUSED: /mnt/data is not a mount point"; exit 2; }
FREE_GB=$(df -BG --output=avail /mnt/data | tail -1 | tr -dc 0-9)
[ "$FREE_GB" -gt 40 ] || { echo "not enough space on /mnt/data: ${FREE_GB} GB free, 20 + 20 needed"; exit 1; }
cd $CODE || exit 1
mkdir -p $ROOT $LG
rm -f $ROOT/ALL_DONE $ROOT/STOPPED
export OMP_NUM_THREADS=1 PY ROOT LG
: > $ROOT/jobs.txt
for D in -7 -8 -11 -19 -43 -67 -163; do
  mkdir -p $ROOT/archive_1e10_D${D#-}
  $PY fn1_archive.py jobs $D 1.01e10 | awk -v D=$D '{print D, $1, $2}' >> $ROOT/jobs.txt
done
RUN='mountpoint -q /mnt/data && nice -n 10 $PY fn1_archive.py task $0 $1 $ROOT/archive_1e10_D${0#-} >> $LG/tasks_D${0#-}.log 2>&1 && echo "$0 $1" >> $LG/done.txt || echo "$0 $1" >> $LG/failed.txt'
ratio() {
$PY - "$ROOT" "$1" <<'PY'
import sys, glob, os
root, n = sys.argv[1], int(sys.argv[2])
pred = {(int(l.split()[0]), int(l.split()[1])): float(l.split()[2]) for l in open(root + "/jobs.txt")}
meas = []
for f in glob.glob(root + "/logs/tasks_D*.log"):
    D = -int(os.path.basename(f)[7:-4])
    meas += [((D, int(l.split()[0])), float(l.split()[2])) for l in open(f) if len(l.split()) == 3]
meas = meas[:n] if n else meas
r = sum(s for _, s in meas) / sum(pred[k] for k, _ in meas)
print(f"{len(meas)} tasks, measured/model = {r:.3f}")
print("OK" if r <= 1.25 else "EXCEEDS")
PY
}
echo "$(date -Is) [CC specarith] fn1 archives to 1.01e10: start ($NPROC procs, $ROOT)" >> ~/claude-work.log
NJ=$(wc -l < $ROOT/jobs.txt); HALF=$((NJ / 2))
head -n "$NPROC" $ROOT/jobs.txt | cut -d' ' -f1,2 | xargs -P "$NPROC" -n 2 sh -c "$RUN"
ratio $NPROC > $ROOT/first_wave.txt
if grep -q EXCEEDS $ROOT/first_wave.txt || [ -s $LG/failed.txt ]; then echo "first wave over the cost model or a task failed" > $ROOT/STOPPED; exit 1; fi
sed -n "$((NPROC + 1)),${HALF}p" $ROOT/jobs.txt | cut -d' ' -f1,2 | xargs -P "$NPROC" -n 2 sh -c "$RUN"
ratio $HALF > $ROOT/mid_run.txt
if grep -q EXCEEDS $ROOT/mid_run.txt || [ -s $LG/failed.txt ]; then echo "mid-run over the cost model or a task failed" > $ROOT/STOPPED; exit 1; fi
tail -n +"$((HALF + 1))" $ROOT/jobs.txt | cut -d' ' -f1,2 | xargs -P "$NPROC" -n 2 sh -c "$RUN"
[ -s $LG/failed.txt ] && { echo "task failures" > $ROOT/STOPPED; exit 1; }
ratio 0 > $ROOT/final_ratio.txt
mountpoint -q /mnt/data || { echo "REFUSED at manifest: /mnt/data is not a mount point" > $ROOT/STOPPED; exit 2; }
for D in -7 -8 -11 -19 -43 -67 -163; do
  MANIFEST_PROCS=$NPROC nice -n 10 $PY fn1_archive.py manifest $D $ROOT/archive_1e10_D${D#-} 1.01e10 > $LG/manifest_D${D#-}.log 2>&1
  echo "D=$D exit=$?" >> $ROOT/summary.exit
done
date -Is > $ROOT/ALL_DONE
echo "$(date -Is) [CC specarith] fn1 archives to 1.01e10: done" >> ~/claude-work.log

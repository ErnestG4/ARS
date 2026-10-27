#!/usr/bin/env bash
# RQ1 (round 93): the 10¹² angle archives on spot's /mnt/data, ℤ[√2] to 10¹² (10,000 segments of 10⁸), then ℤ[i] to
# 1.01·10¹² (10,100 segments; the extra 10¹⁰ so N can be matched at 10¹²). Generation, integrity and hashes only: no
# statistic of the angles is computed. Code runs from ~/tmp/claude/specarith/rq1; data go to /mnt/data/rq1/.
# Mount guard (round 92 note): nothing starts unless `mountpoint -q /mnt/data` succeeds, and every task re-checks it
# (a task whose mount has gone fails, and failures stop the run). Free space is checked against the field's size.
# Cost model (rq1_archive.py jobs; round 93): ℤ[√2] ≈ 275 spot core-h, ℤ[i] ≈ 277 (factor 2.8, from the 1e11 run);
# ≈ 10 h wall each at 28 processes. First-wave rule (round 84): the first NPROC tasks alone, stop above 1.25×. Mid-run
# checks (round 88): the running ratio after half and three quarters of the tasks, same stop.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/rq1/run_rq1_archive_1e12_spot.sh [NPROC]
set -u
NPROC=${1:-28}
CODE=~/tmp/claude/specarith/rq1
BASE=/mnt/data/rq1
PY=~/miniforge3/envs/ph6c/bin/python
mountpoint -q /mnt/data || { echo "REFUSED: /mnt/data is not a mount point"; exit 2; }
mkdir -p $BASE || exit 2
cd $CODE || exit 1
export OMP_NUM_THREADS=1 PY
ratio() {   # O N: measured / modelled seconds over the first N finished tasks (task-log order)
$PY - "$1" "$2" <<'PY'
import sys
o, n = sys.argv[1], int(sys.argv[2])
pred = {int(l.split()[0]): float(l.split()[1]) for l in open(o + "/jobs.txt")}
meas = []
for l in open(o + "/logs/tasks.log"):
    k, rows, s = l.split()
    meas.append((int(k), float(s)))
m = meas[:n]
r = sum(s for _, s in m) / sum(pred[k] for k, _ in m)
print(f"{len(m)} tasks, measured/model = {r:.3f}")
print("OK" if r <= 1.25 else "EXCEEDS")
PY
}
for spec in "zs2 1e12 150" "zi 1.01e12 153"; do
  set -- $spec; F=$1; X=$2; NEED_GB=$3
  O=$BASE/archive_1e12_$F; LG=$O/logs
  mountpoint -q /mnt/data || { echo "REFUSED: /mnt/data is not a mount point"; exit 2; }
  mkdir -p $O $LG
  rm -f $O/ALL_DONE $O/STOPPED
  FREE_GB=$(df -BG --output=avail /mnt/data | tail -1 | tr -dc 0-9)
  [ "$FREE_GB" -gt $((NEED_GB + 20)) ] || { echo "not enough space on /mnt/data: ${FREE_GB} GB free, ${NEED_GB} + 20 needed" > $O/STOPPED; exit 1; }
  export O LG F
  RUN='mountpoint -q /mnt/data && nice -n 10 $PY rq1_archive.py task $0 $O $F >> $LG/tasks.log 2>&1 || echo "$0" >> $LG/failed.txt'
  echo "$(date -Is) [CC specarith] rq1 1e12 archive $F: start ($NPROC procs, $O)" >> ~/claude-work.log
  $PY rq1_archive.py jobs $X $F > $O/jobs.txt
  NJ=$(wc -l < $O/jobs.txt); HALF=$((NJ / 2)); Q3=$((NJ * 3 / 4))
  head -n "$NPROC" $O/jobs.txt | cut -d' ' -f1 | xargs -P "$NPROC" -n 1 sh -c "$RUN"
  ratio $O $NPROC > $O/first_wave.txt
  if grep -q EXCEEDS $O/first_wave.txt || [ -s $LG/failed.txt ]; then echo "first wave over the cost model or a task failed" > $O/STOPPED; exit 1; fi
  sed -n "$((NPROC + 1)),${HALF}p" $O/jobs.txt | cut -d' ' -f1 | xargs -P "$NPROC" -n 1 sh -c "$RUN"
  ratio $O $HALF > $O/mid_run.txt
  if grep -q EXCEEDS $O/mid_run.txt || [ -s $LG/failed.txt ]; then echo "mid-run over the cost model or a task failed" > $O/STOPPED; exit 1; fi
  sed -n "$((HALF + 1)),${Q3}p" $O/jobs.txt | cut -d' ' -f1 | xargs -P "$NPROC" -n 1 sh -c "$RUN"
  ratio $O $Q3 > $O/q3_run.txt
  if grep -q EXCEEDS $O/q3_run.txt || [ -s $LG/failed.txt ]; then echo "three-quarter check over the cost model or a task failed" > $O/STOPPED; exit 1; fi
  tail -n +"$((Q3 + 1))" $O/jobs.txt | cut -d' ' -f1 | xargs -P "$NPROC" -n 1 sh -c "$RUN"
  [ -s $LG/failed.txt ] && { echo "task failures" > $O/STOPPED; exit 1; }
  ratio $O $NJ > $O/final_ratio.txt
  mountpoint -q /mnt/data || { echo "REFUSED at manifest: /mnt/data is not a mount point" > $O/STOPPED; exit 2; }
  MANIFEST_PROCS=$NPROC nice -n 10 $PY rq1_archive.py manifest $O $X $F > $O/summary.log 2>&1; echo "exit=$?" > $O/summary.exit
  date -Is > $O/ALL_DONE
  echo "$(date -Is) [CC specarith] rq1 1e12 archive $F: done" >> ~/claude-work.log
done

#!/usr/bin/env bash
# RQ1-c witnesses (round 97; rq1c_witness.py; synthetic only, nothing from any archive). Stage 1: P1 selection, P3 and
# P4 tasks interleaved (1,000 tasks), then their summaries; stage 2: P1 confirmation at the frozen t, then its summary.
# Cost model = measured spot CPU per task at N = 1e9 (wtest): P1 106 s, P3 800 s, P4 197 s → ≈ 112 spot core-h,
# ≈ 14 h wall at 8 processes. First-wave check (first NPROC tasks) and running-ratio checks after 25%, 50% and 75% of
# stage 1: stop (STOPPED) above 1.25×. A witness that misses its bars is reported, not rerun (round 97).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/rq1/run_rq1c_witness_spot.sh [NPROC]
set -u
NPROC=${1:-8}
cd ~/tmp/claude/specarith/rq1 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=rq1c_wit; mkdir -p $O/p1sel $O/p1conf $O/p3 $O/p4 $O/logs
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PY O
RUN='systemd-run --user --scope -q -p MemoryMax=16G -p MemorySwapMax=0 nice -n 10 $PY rq1c_witness.py task $0 $1 $2 $O/$0 >> $O/logs/tasks.log 2>&1 || echo "$0 $1 $2" >> $O/logs/failed.txt'
ratio() {
$PY - "$O" "$1" <<'PY'
import sys
o, n = sys.argv[1], int(sys.argv[2])
model = {"p1sel": 106.0, "p1conf": 106.0, "p3": 800.0, "p4": 197.0}
rows = [l.split() for l in open(o + "/logs/tasks.log") if l.strip()][:n]
r = sum(float(x[3]) for x in rows) / sum(model[x[0]] for x in rows)
print(f"{len(rows)} tasks, measured cpu/model = {r:.3f}")
print("OK" if r <= 1.25 else "EXCEEDS")
PY
}
echo "$(date -Is) [CC specarith] rq1c witnesses: stage 1 ($NPROC procs)" >> ~/claude-work.log
{ $PY rq1c_witness.py jobs p1sel | sed 's/^/p1sel /'; $PY rq1c_witness.py jobs p3 | sed 's/^/p3 /'; $PY rq1c_witness.py jobs p4 | sed 's/^/p4 /'; } | awk '{print NR%13, $0}' | sort -s -n -k1,1 | cut -d" " -f2- > $O/jobs1.txt
NJ=$(wc -l < $O/jobs1.txt)
start=1
for frac in 0 25 50 75 100; do
  if [ $frac = 0 ]; then stop=$NPROC; else stop=$((NJ * frac / 100)); fi
  sed -n "${start},${stop}p" $O/jobs1.txt | xargs -P "$NPROC" -L 1 sh -c "$RUN"
  if [ $frac -lt 100 ]; then
    ratio $stop > $O/check_$frac.txt
    if grep -q EXCEEDS $O/check_$frac.txt || [ -s $O/logs/failed.txt ]; then echo "over the cost model at $frac% or a task failed" > $O/STOPPED; exit 1; fi
  fi
  start=$((stop + 1))
done
[ -s $O/logs/failed.txt ] && { echo "task failures" > $O/STOPPED; exit 1; }
$PY rq1c_witness.py summary p1sel $O/p1sel $O/P1_SELECTION.json > $O/p1sel.log 2>&1
$PY rq1c_witness.py summary p3 $O/p3 $O/P3_WITNESS.json > $O/p3.log 2>&1
$PY rq1c_witness.py summary p4 $O/p4 $O/P4_WITNESS.json > $O/p4.log 2>&1
$PY -c "import json, sys; sys.exit(0 if json.load(open('$O/P1_SELECTION.json'))['OK'] else 3)" || { echo "P1 selection missed its bars; no confirmation" > $O/STOPPED; date -Is > $O/ALL_DONE; exit 1; }
echo "$(date -Is) [CC specarith] rq1c witnesses: stage 2 (P1 confirmation)" >> ~/claude-work.log
$PY rq1c_witness.py jobs p1conf | sed 's/^/p1conf /' | xargs -P "$NPROC" -L 1 sh -c "$RUN"
[ -s $O/logs/failed.txt ] && { echo "task failures" > $O/STOPPED; exit 1; }
$PY rq1c_witness.py summary p1conf $O/p1conf $O/P1_CONFIRM.json $O/P1_SELECTION.json > $O/p1conf.log 2>&1
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] rq1c witnesses: done" >> ~/claude-work.log

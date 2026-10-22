#!/usr/bin/env bash
# Round 72 on spot: CUE scatter control (50 x 1e5 segments, 5 x 1e6 segments) and the pair-approximation responses
# (50 sequences), then both summaries. nice 10, NPROC jobs, one BLAS thread each. Restartable (existing outputs kept).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/l6/run_r72_spot.sh [NPROC]
set -u
NPROC=${1:-28}
cd ~/tmp/claude/specarith/l6 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=results/r72; LG=$O/logs
mkdir -p $O $LG
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY O LG
echo "$(date -Is) [CC specarith] round 72: control + pair responses ($NPROC procs)" >> ~/claude-work.log
{ for r in $(seq 0 49); do echo "ctrl $r ctrl_$(printf %03d $r)"; done; for j in 0 1 2 3 4; do echo "ctrl_cat $j ctrlcat_$j"; done
  for r in $(seq 0 49); do echo "resp $r resp_$(printf %03d $r)"; done; } |
  xargs -P "$NPROC" -L 1 sh -c '[ -f "$O/$2.json" ] || nice -n 10 $PY round72.py $0 $1 $O > $LG/$2.log 2>&1; echo "exit=$?" > $LG/$2.exit'
grep -L "exit=0" $LG/*.exit > $O/failures.txt
[ -s $O/failures.txt ] && { echo "job failures" > $O/STOPPED; exit 1; }
nice -n 10 $PY round72.py ctrl_summary $O > $O/ctrl_summary.log 2>&1; echo "exit=$?" > $O/ctrl_summary.exit
nice -n 10 $PY round72.py pair_summary $O > $O/pair_summary.log 2>&1; echo "exit=$?" > $O/pair_summary.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] round 72: done" >> ~/claude-work.log

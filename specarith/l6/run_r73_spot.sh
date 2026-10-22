#!/usr/bin/env bash
# Round 73 on spot: disjoint-block, global-mean long-baseline variance (L6_BIAS_CORRECTION.md), 50 sequences, then the
# summary. nice 10, NPROC jobs, one BLAS thread each. Restartable (existing outputs kept).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/l6/run_r73_spot.sh [NPROC]
set -u
NPROC=${1:-28}
cd ~/tmp/claude/specarith/l6 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=results/r73; LG=$O/logs
mkdir -p $O $LG
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY O LG
echo "$(date -Is) [CC specarith] round 73: disjoint-block global-mean W ($NPROC procs)" >> ~/claude-work.log
seq 0 49 | xargs -P "$NPROC" -I{} sh -c 'r=$(printf %03d {}); [ -f "$O/blocks_$r.json" ] || nice -n 10 $PY round73.py blocks {} $O > $LG/blocks_$r.log 2>&1; echo "exit=$?" > $LG/blocks_$r.exit'
grep -L "exit=0" $LG/*.exit > $O/failures.txt
[ -s $O/failures.txt ] && { echo "job failures" > $O/STOPPED; exit 1; }
nice -n 10 $PY round73.py summary $O > $O/summary.log 2>&1; echo "exit=$?" > $O/summary.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] round 73: done" >> ~/claude-work.log

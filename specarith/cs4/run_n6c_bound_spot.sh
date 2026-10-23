#!/usr/bin/env bash
# n = 6 stage (c) bound on spot (l6/N6_STAGE_C.md, round 77): the 1,242 declared tasks (restartable: finished task
# files are kept), then the summary. nice 10, NPROC jobs, one BLAS thread each.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_n6c_bound_spot.sh [NPROC]
set -u
NPROC=${1:-28}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=results/n6c/bound; LG=$O/logs
mkdir -p $O $LG
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY O LG
echo "$(date -Is) [CC specarith] n6 stage (c) bound: 1242 tasks ($NPROC procs)" >> ~/claude-work.log
$PY n6c_bound.py jobs > $O/jobs.txt
xargs -P "$NPROC" -L 1 sh -c 'nice -n 10 $PY n6c_bound.py task $0 $1 $2 $3 $4 $5 $O >> $LG/tasks.log 2>&1 || echo "$0 $1 $2 $3 $4 $5" >> $LG/failed.txt' < $O/jobs.txt
[ -s $LG/failed.txt ] && { echo "task failures" > $O/STOPPED; exit 1; }
nice -n 10 $PY n6c_bound.py summary $O > $O/summary.log 2>&1; echo "exit=$?" > $O/summary.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] n6 stage (c) bound: done" >> ~/claude-work.log

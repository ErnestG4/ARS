#!/usr/bin/env bash
# n = 6 stage (b) session 2, the averaging question (l6/N6_STAGE_B.md S2.2): 360 tasks, then the summary.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_n6b_lavg_spot.sh [NPROC]
set -u
NPROC=${1:-20}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=results/n6b/lavg; LG=$O/logs
mkdir -p $O $LG
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY O LG
echo "$(date -Is) [CC specarith] n6 stage (b) S2.2 averaging: 360 tasks ($NPROC procs)" >> ~/claude-work.log
$PY n6b_lavg.py jobs > $O/jobs.txt
xargs -P "$NPROC" -L 1 sh -c 'nice -n 10 $PY n6b_lavg.py task $0 $1 $2 $O >> $LG/tasks.log 2>&1 || echo "$0 $1 $2" >> $LG/failed.txt' < $O/jobs.txt
[ -s $LG/failed.txt ] && { echo "task failures" > $O/STOPPED; exit 1; }
nice -n 10 $PY n6b_lavg.py summary $O > $O/summary.log 2>&1; echo "exit=$?" > $O/summary.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] n6 stage (b) S2.2 averaging: done" >> ~/claude-work.log

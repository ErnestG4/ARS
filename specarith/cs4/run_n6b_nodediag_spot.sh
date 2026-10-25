#!/usr/bin/env bash
# Round 83 node diagnostic on spot (l6/N6-2_PLAN.md §11): the (3, 3) piece at 6 nodes at the 24 dominant kernel points;
# 192 chunk tasks (restartable; skip-if-present; per-process temp names), then the summary against the 4-node values.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_n6b_nodediag_spot.sh [NPROC]
set -u
NPROC=${1:-48}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=results/n6b/nodediag; LG=$O/logs
mkdir -p $O $LG
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY O LG
echo "$(date -Is) [CC specarith] n6b node diagnostic: 192 tasks ($NPROC procs)" >> ~/claude-work.log
$PY n6b_nodediag.py jobs > $O/jobs.txt
xargs -P "$NPROC" -L 1 sh -c 'nice -n 10 $PY n6b_nodediag.py task $0 $1 $2 6 $O >> $LG/tasks.log 2>&1 || echo "$0 $1 $2" >> $LG/failed.txt' < $O/jobs.txt
[ -s $LG/failed.txt ] && { echo "task failures" > $O/STOPPED; exit 1; }
nice -n 10 $PY n6b_nodediag.py summary $O results/n6b/settle/tasks.tgz > $O/summary.log 2>&1; echo "exit=$?" > $O/summary.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] n6b node diagnostic: done" >> ~/claude-work.log

#!/usr/bin/env bash
# Stage (c) pilot helper (performance only): a second runner over the same task list in REVERSE order, on the cores the
# finished averaging run freed. Tasks are skip-if-present and written atomically, so the two runners only duplicate work
# where they meet. No summary here: the main launcher (run_n6c_pilot_spot.sh) runs it after its own pass.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_n6c_pilot_rev_spot.sh [NPROC]
set -u
NPROC=${1:-20}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=results/n6c/pilot; LG=$O/logs
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY O LG
echo "$(date -Is) [CC specarith] n6 stage (c) pilot: reverse helper ($NPROC procs)" >> ~/claude-work.log
tac $O/jobs.txt > $O/jobs_rev.txt
xargs -P "$NPROC" -L 1 sh -c 'nice -n 10 $PY n6c_conn.py task $0 $1 $2 $3 $4 $5 $O >> $LG/tasks_rev.log 2>&1 || echo "$0 $1 $2 $3 $4 $5" >> $LG/failed_rev.txt' < $O/jobs_rev.txt
date -Is > $O/REV_DONE
echo "$(date -Is) [CC specarith] n6 stage (c) pilot: reverse helper done" >> ~/claude-work.log

#!/usr/bin/env bash
# Round 80 settling test on spot (l6/N6_CLOSEOUT.md §3.3; POST-HOC): G-b3 under corrected (B)'s own kernel at r0 = 100
# and 300. Kernel + known answer first (void if it fails), then 158 point tasks (restartable; skip-if-present, per-process
# temp names), then the summary. REV=1 runs the task list reversed and skips kernel and summary (a helper on freed cores).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_n6b_settle_spot.sh [NPROC] [REV]
set -u
NPROC=${1:-8}; REV=${2:-0}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=results/n6b/settle; LG=$O/logs
mkdir -p $O $LG
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY O LG
if [ "$REV" = 0 ]; then
  rm -f $O/ALL_DONE $O/STOPPED
  echo "$(date -Is) [CC specarith] n6b settling test: kernel + 158 tasks ($NPROC procs)" >> ~/claude-work.log
  nice -n 10 $PY n6b_settle.py kernel ../l6/results/n6a $O > $O/kernel.log 2>&1; echo "exit=$?" > $O/kernel.exit
  grep -q '"KNOWN_ANSWER_OK": true' $O/KERNEL.json || { echo "known answer failed: test void" > $O/STOPPED; exit 1; }
  $PY n6b_settle.py jobs > $O/jobs.txt
  J=$O/jobs.txt; TL=$LG/tasks.log; FL=$LG/failed.txt
else
  echo "$(date -Is) [CC specarith] n6b settling test: reverse helper ($NPROC procs)" >> ~/claude-work.log
  tac $O/jobs.txt > $O/jobs_rev.txt
  J=$O/jobs_rev.txt; TL=$LG/tasks_rev.log; FL=$LG/failed_rev.txt
fi
export TL FL
xargs -P "$NPROC" -L 1 sh -c 'nice -n 10 $PY n6b_settle.py task $0 $1 $O >> $TL 2>&1 || echo "$0 $1" >> $FL' < $J
[ "$REV" = 0 ] || { date -Is > $O/REV_DONE; exit 0; }
[ -s $FL ] && { echo "task failures" > $O/STOPPED; exit 1; }
nice -n 10 $PY n6b_settle.py summary $O > $O/summary.log 2>&1; echo "exit=$?" > $O/summary.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] n6b settling test: done" >> ~/claude-work.log

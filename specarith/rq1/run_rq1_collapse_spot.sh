#!/usr/bin/env bash
# RQ1 POST-HOC conductor-scaling collapse on spot (round 92; rq1_collapse.py; descriptive, no verdict). Reads the
# already-read archives through rq1_read.load_field (segment hashes checked). One process, COLLAPSE_THREADS threads,
# 40 GB cap (one field in memory at a time; the read's measured peak at 10¹¹ is 30.8 GiB).
# Cost model ≈ 7.4 spot core-h (see rq1_collapse.py); the script stops itself above 1.25× at any stage.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/rq1/run_rq1_collapse_spot.sh [THREADS]
set -u
cd ~/tmp/claude/specarith/rq1 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=collapse; mkdir -p $O; rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 COLLAPSE_THREADS=${1:-16}
echo "$(date -Is) [CC specarith] rq1 r92 post-hoc collapse ($COLLAPSE_THREADS threads, 40G cap)" >> ~/claude-work.log
systemd-run --user --scope -q -p MemoryMax=40G -p MemorySwapMax=0 nice -n 10 $PY rq1_collapse.py archive archive_zi $O \
  > $O/collapse.log 2>&1
echo "exit=$?" >> $O/collapse.log
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] rq1 r92 post-hoc collapse: done" >> ~/claude-work.log

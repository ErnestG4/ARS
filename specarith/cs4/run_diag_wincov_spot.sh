#!/usr/bin/env bash
# Predicted window-to-window covariance at the estimator's spacing (diag_wincov.py), five F2 heights, nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_diag_wincov_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/diag_wincov
mkdir -p "$OUT"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] diag_wincov: 5 heights sequential, nice 10" >> ~/claude-work.log
for L in 15.7502 16.4972 17.2491 19.5003 21.75; do
  nice -n 10 $PY diag_wincov.py "$L" "$OUT"
done > "$OUT/run.log" 2>&1
echo "exit=$?" >> "$OUT/run.log"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] diag_wincov: done" >> ~/claude-work.log

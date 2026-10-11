#!/usr/bin/env bash
# Estimator B: amendment-7 osc check for the lag-1 covariance (diag_osc_lag1.py), pair (5,5), 64 stratified ℓ across
# the F2 15.75 file, Δr = 0.1 to 6·10⁴. 12 procs, nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_diag_osc_lag1_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/diag_osc_lag1
mkdir -p "$OUT"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] diag_osc_lag1: 64 tasks, 12 procs, nice 10" >> ~/claude-work.log
$PY -c "print('\n'.join('%.7f' % (15.7259 + (k + 0.5) * (15.7742 - 15.7259) / 64) for k in range(64)))" \
  | xargs -P 12 -I{} sh -c 'nice -n 10 '"$PY"' diag_osc_lag1.py {} '"$OUT"' > '"$OUT"'/l_{}.log 2>&1; echo "exit=$?" >> '"$OUT"'/l_{}.log'
$PY diag_osc_lag1.py summary "$OUT" > "$OUT/summary.txt" 2>&1
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] diag_osc_lag1: done" >> ~/claude-work.log

#!/usr/bin/env bash
# Corrected (B) (round 58): the data-free F6 prediction at L* (b2_pred.py run; 18 jobs: pmax 3e5 / 1e6 x triangle
# order 32 / 48 at each file's mean height, plus t0 / t1 at the lowest file), NCH procs, nice 10. Restartable.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_b2_pred_spot.sh [NCH]
set -u
NCH=${1:-18}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
OUT=results/b2_pred
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] corrected (B) F6 prediction at L*: $NCH procs, nice 10" >> ~/claude-work.log
seq 0 $((NCH - 1)) | xargs -P "$NCH" -I{} sh -c 'nice -n 10 '"$PY"' b2_pred.py run {} '"$NCH"' '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/c{}.exit'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] corrected (B) F6 prediction: done" >> ~/claude-work.log

#!/usr/bin/env bash
# Route (a) replications (A) and (B) (round 52): the data-free predictions at F4/F5 heights (followup_pred.py run),
# full run with the 10⁶ cutoff check at every node, NCH chunks, nice 10. Restartable (chunks skip jobs already done).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_followup_pred_spot.sh [NCH]
set -u
NCH=${1:-48}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
OUT=results/followup_pred
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) replications: predictions (A)/(B), $NCH procs, nice 10" >> ~/claude-work.log
seq 0 $((NCH - 1)) | xargs -P "$NCH" -I{} sh -c 'nice -n 10 '"$PY"' followup_pred.py run {} '"$NCH"' '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/c{}.exit'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] route (a) replications: predictions (A)/(B): done" >> ~/claude-work.log

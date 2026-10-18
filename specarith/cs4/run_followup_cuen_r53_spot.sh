#!/usr/bin/env bash
# Round 53: (B)'s CUE_N known-answer slope at L = 3 to SE ≤ 0.005 (followup_cuen.py, ROUND 53, ALLOC_53 batches per N;
# CUEN_EXTEND for the declared 25% extensions). NCH procs, nice 10. Restartable. Data-free.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_followup_cuen_r53_spot.sh [NCH] [EXTEND]
set -u
NCH=${1:-48}
export CUEN_ROUND=53 CUEN_EXTEND=${2:-0}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
OUT=results/followup_cuen_r53
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) follow-up (B) CUE_N slope (round 53, to SE 0.005, extend $CUEN_EXTEND): $NCH procs, nice 10" >> ~/claude-work.log
seq 0 $((NCH - 1)) | xargs -P "$NCH" -I{} sh -c 'nice -n 10 '"$PY"' followup_cuen.py run {} '"$NCH"' '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/c{}.exit'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] route (a) follow-up (B) CUE_N slope (round 53): done" >> ~/claude-work.log

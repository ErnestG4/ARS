#!/usr/bin/env bash
# Follow-up (B) (round 50): CUE_N known-answer k₃ batches for the slope dμ*/dμ
# (followup_cuen.py run), NCH chunks, nice 10. Data-free. Restartable (chunks skip jobs already done).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_followup_cuen_spot.sh [NCH]
set -u
NCH=${1:-40}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
OUT=results/followup_cuen
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export CUEN_BATCHES=2000 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) follow-up (B) CUE_N slope: $NCH procs, nice 10" >> ~/claude-work.log
seq 0 $((NCH - 1)) | xargs -P "$NCH" -I{} sh -c 'nice -n 10 '"$PY"' followup_cuen.py run {} '"$NCH"' '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/c{}.exit'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] route (a) follow-up (B) CUE_N slope: done" >> ~/claude-work.log

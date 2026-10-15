#!/usr/bin/env bash
# Follow-up candidate (A) (round 49): ζ's T₃/T₄ (and their error runs) on the NNN nodes of [0, 3.0]
# (followup_nnn.py run), NCH chunks, nice 10. Data-free. Restartable (chunks skip jobs already done).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_followup_nnn_spot.sh [NCH]
set -u
NCH=${1:-24}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
OUT=results/followup_nnn
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) follow-up (A) NNN terms: $NCH procs, nice 10" >> ~/claude-work.log
seq 0 $((NCH - 1)) | xargs -P "$NCH" -I{} sh -c 'nice -n 10 '"$PY"' followup_nnn.py run {} '"$NCH"' '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/c{}.exit'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] route (a) follow-up (A) NNN terms: done" >> ~/claude-work.log

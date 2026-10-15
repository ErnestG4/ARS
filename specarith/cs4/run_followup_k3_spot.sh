#!/usr/bin/env bash
# Follow-up candidate (B) (round 48): third cumulant of the counting function, ΔF₂/ΔF₃ at the F3 heights
# (followup_k3.py run), NCH chunks, nice 10. Data-free. Restartable.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_followup_k3_spot.sh [NCH]
set -u
NCH=${1:-16}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
OUT=results/followup_k3
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] follow-up (B) kappa3 terms: $NCH procs, nice 10" >> ~/claude-work.log
seq 0 $((NCH - 1)) | xargs -P "$NCH" -I{} sh -c 'nice -n 10 '"$PY"' followup_k3.py run {} '"$NCH"' '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/c{}.exit'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] follow-up (B) kappa3 terms: done" >> ~/claude-work.log

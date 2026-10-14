#!/usr/bin/env bash
# Route (a) cumulant cut (forty-fourth round): route_a_cumul.py run, NCH chunks (one process each), nice 10. Data-free.
# Restartable: each chunk appends one JSON line per job and skips jobs already done.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_route_a_cumul_spot.sh [NCH]
set -u
NCH=${1:-32}
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/cumul
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 CS4_CHUNK=32
echo "$(date -Is) [CC specarith] route (a) cumulant cut: $NCH procs, nice 10" >> ~/claude-work.log
seq 0 $((NCH - 1)) | xargs -P "$NCH" -I{} sh -c 'nice -n 10 '"$PY"' route_a_cumul.py run {} '"$NCH"' '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/c{}.exit'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] route (a) cumulant cut: done" >> ~/claude-work.log

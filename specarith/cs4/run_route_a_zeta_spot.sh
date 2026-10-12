#!/usr/bin/env bash
# Route (a) step 1 (thirtieth round): ζ spacing-law terms at the F3 heights (route_a_zeta.py run), 40 chunks, nice 10.
# Heights only; no F3 file is read. Restartable: each chunk appends one JSON line per job and skips jobs already done.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_route_a_zeta_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/route_a_zeta
mkdir -p "$OUT/logs"
rm -f "$OUT/DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 CS4_CHUNK=32
echo "$(date -Is) [CC specarith] route (a) zeta terms: 40 chunks, nice 10" >> ~/claude-work.log
seq 0 39 | xargs -P 40 -I{} sh -c 'nice -n 10 '"$PY"' route_a_zeta.py run {} 40 '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" >> '"$OUT"'/logs/c{}.log'
date -Is > "$OUT/DONE"
echo "$(date -Is) [CC specarith] route (a) zeta terms: done" >> ~/claude-work.log

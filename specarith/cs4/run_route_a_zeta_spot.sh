#!/usr/bin/env bash
# Route (a) step 1 (thirtieth round): ζ spacing-law terms at the F3 heights (route_a_zeta.py run), 40 chunks, nice 10.
# Heights only; no F3 file is read. Restartable: each chunk appends one JSON line per job and skips jobs already done.
# A chunk range C0..C1 (default 0..39) runs with one process per chunk, so disjoint ranges can be started separately as
# cores free up (never start overlapping ranges: two processes on one chunk would duplicate its jobs).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_route_a_zeta_spot.sh [C0 C1]
set -u
C0=${1:-0}
C1=${2:-39}
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/route_a_zeta
mkdir -p "$OUT/logs"
rm -f "$OUT/DONE_${C0}_${C1}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 CS4_CHUNK=32
P=$((C1 - C0 + 1))
echo "$(date -Is) [CC specarith] route (a) zeta terms: chunks $C0-$C1 of 40, $P procs, nice 10" >> ~/claude-work.log
seq "$C0" "$C1" | xargs -P "$P" -I{} sh -c 'nice -n 10 '"$PY"' route_a_zeta.py run {} 40 '"$OUT"' >> '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" >> '"$OUT"'/logs/c{}.log'
date -Is > "$OUT/DONE_${C0}_${C1}"
echo "$(date -Is) [CC specarith] route (a) zeta terms: chunks $C0-$C1 done" >> ~/claude-work.log

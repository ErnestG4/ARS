#!/usr/bin/env bash
# PH2S Stage 1 pre-read, seen R zeros (s1preread.py seen): R1–R5 in parallel, nice 10.
#   bash specarith/ph2s/run_seen_local.sh
set -u
D=$(cd "$(dirname "$0")" && pwd)
PY=/home/combust/fmexplorer/bin/python3
cd "$D"
OUT=results/preread
mkdir -p "$OUT/logs"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
printf '%s\n' R1 R2 R3 R4 R5 | xargs -P 5 -L 1 sh -c 'nice -n 10 '"$PY"' s1preread.py seen '"$OUT"' "$0" > '"$OUT"'/logs/seen_$0.log 2>&1; echo "exit=$?" >> '"$OUT"'/logs/seen_$0.log'

#!/usr/bin/env bash
# R₂ read (after the seal commit + tag only): r2run.py read R1..R5, three at a time (memory: ~1 GB each while decoding),
# nice 10. r2run refuses unless the seal JSON exists and pins this code and each Platt file's md5.
#   bash specarith/ph2r2/run_read_local.sh
set -u
D=$(cd "$(dirname "$0")" && pwd)
PY=/home/combust/fmexplorer/bin/python3
cd "$D"
OUT=results/read
mkdir -p "$OUT/logs" "$OUT/exits"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
printf '%s\n' R1 R2 R3 R4 R5 | xargs -P 3 -L 1 sh -c 'nice -n 10 '"$PY"' r2run.py read "$0" > '"$OUT"'/logs/read_$0.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/read_$0.txt'
date -Is > "$OUT/ALL_DONE"

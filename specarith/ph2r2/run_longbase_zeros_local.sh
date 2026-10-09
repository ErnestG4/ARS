#!/usr/bin/env bash
# Long-baseline comparison, zeros side (longbase.py zeros): R1–R5 at L = 2·10⁵ and 10⁶, five at a time, nice 10.
#   bash specarith/ph2r2/run_longbase_zeros_local.sh
set -u
D=$(cd "$(dirname "$0")" && pwd)
PY=/home/combust/fmexplorer/bin/python3
cd "$D"
OUT=results/longbase
mkdir -p "$OUT/logs"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for L in 200000 1000000; do for n in R1 R2 R3 R4 R5; do echo "$n $L"; done; done |
  xargs -P 5 -L 1 sh -c 'nice -n 10 '"$PY"' longbase.py zeros "$0" "$1" '"$OUT"' > '"$OUT"'/logs/zeros_$0_$1.log 2>&1; echo "exit=$?" >> '"$OUT"'/logs/zeros_$0_$1.log'
date -Is > "$OUT/ZEROS_DONE"

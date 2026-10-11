#!/usr/bin/env bash
# All test-function members, descriptive (members.py): R1–R5 in parallel, then the table. nice 10.
#   bash specarith/ph2r2/run_members_local.sh
set -u
D=$(cd "$(dirname "$0")" && pwd)
PY=/home/combust/fmexplorer/bin/python3
cd "$D"
OUT=results/members
mkdir -p "$OUT/logs"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
printf '%s\n' R1 R2 R3 R4 R5 | xargs -P 5 -L 1 sh -c 'nice -n 10 '"$PY"' members.py "$0" > '"$OUT"'/logs/$0.log 2>&1; echo "exit=$?" >> '"$OUT"'/logs/$0.log'
$PY members.py table > "$OUT/logs/table.log" 2>&1

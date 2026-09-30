#!/usr/bin/env bash
# B1b licences (sealed 766c92c), each under checkrun, sequential. STOP-aware between runs.
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=8
for s in armb/q2_licence.py armb/q1_warp.py armb/q1_licence.py; do
  [ -e STOP ] && exit 3
  ../checkrun.sh "$s" > "armb/$(basename "$s" .py).checkrun.log" 2>&1
done

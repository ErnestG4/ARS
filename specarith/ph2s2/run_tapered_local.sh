#!/usr/bin/env bash
# Tapered statistic (tapered.py), descriptive bridge: 16 Stage 1 GUE sequences (10⁶) and the six F1 bins, then summary.
#   bash specarith/ph2s2/run_tapered_local.sh
set -u
D=$(cd "$(dirname "$0")" && pwd)
PY=/home/combust/fmexplorer/bin/python3
cd "$D"
OUT=results/tapered
mkdir -p "$OUT/logs"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for f in gue_s1/gue_L1000000_s0*.npy; do nice -n 10 $PY tapered.py gue "$f" "$OUT" >> "$OUT/logs/gue.log" 2>&1; done
printf '%s\n' F1a F1b F1c F1d F1e F1x | xargs -P 3 -L 1 sh -c 'nice -n 10 '"$PY"' tapered.py zeros "$0" '"$OUT"' > '"$OUT"'/logs/zeros_$0.log 2>&1; echo "exit=$?" >> '"$OUT"'/logs/zeros_$0.log'
$PY tapered.py summary "$OUT" > "$OUT/logs/summary.log" 2>&1

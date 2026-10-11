#!/usr/bin/env bash
# PH2S Stage 1 pre-read, baseline step: waits for results/gue/ALL_DONE (a file), then maps every GUE seed onto every
# F1 and R bin (s1preread.py baseline), 40 at a time, nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph2s/run_baseline_spot.sh
set -u
D=~/tmp/claude/specarith/ph2s
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/preread
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/BASE_DONE"
while [ ! -f results/gue/ALL_DONE ]; do sleep 60; done
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ph2s Stage 1 baseline mapping: 11 bins x 16 seeds, nice 10" >> ~/claude-work.log
for b in F1a F1b F1c F1d F1e F1x R1 R2 R3 R4 R5; do for s in $(seq 0 15); do echo "$b $s"; done; done |
  xargs -P 40 -L 1 sh -c 'nice -n 10 '"$PY"' s1preread.py baseline results/gue '"$OUT"' "$0" "$1" > '"$OUT"'/logs/base_$0_$1.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/base_$0_$1.txt'
date -Is > "$OUT/BASE_DONE"
echo "$(date -Is) [CC specarith] ph2s Stage 1 baseline mapping: done" >> ~/claude-work.log

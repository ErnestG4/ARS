#!/usr/bin/env bash
# PH2S Stage 1 baseline: 16 fresh GUE sequences at L = 10⁶ and 16 at L = 2·10⁵ (gue_levels.py), nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph2s/run_gue_levels_spot.sh
set -u
D=~/tmp/claude/specarith/ph2s
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/gue
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ph2s Stage 1 GUE baseline: 16 x L=1e6 + 16 x L=2e5, nice 10" >> ~/claude-work.log
{ for s in $(seq 0 15); do echo "$s 1000000"; done; for s in $(seq 0 15); do echo "$s 200000"; done; } |
  xargs -P 30 -L 1 sh -c 'nice -n 10 '"$PY"' gue_levels.py "$0" "$1" '"$OUT"' > '"$OUT"'/logs/gue_$1_$0.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/gue_$1_$0.txt'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph2s Stage 1 GUE baseline: done" >> ~/claude-work.log

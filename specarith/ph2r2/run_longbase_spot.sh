#!/usr/bin/env bash
# Long sine-kernel baseline (longbase.py): 16 seeds at L = 2·10⁵ and 8 seeds at L = 10⁶, one process each, nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph2r2/run_longbase_spot.sh
set -u
D=~/tmp/claude/specarith/ph2r2
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/longbase
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ph2r2 long GUE baseline: 16 x L=2e5 + 8 x L=1e6, nice 10" >> ~/claude-work.log
{ for s in $(seq 0 7); do echo "$s 1000000"; done; for s in $(seq 100 115); do echo "$s 200000"; done; } |
  xargs -P 24 -L 1 sh -c 'nice -n 10 '"$PY"' longbase.py gue "$0" "$1" '"$OUT"' > '"$OUT"'/logs/gue_$1_$0.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/gue_$1_$0.txt'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph2r2 long GUE baseline: done" >> ~/claude-work.log

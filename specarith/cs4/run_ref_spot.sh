#!/usr/bin/env bash
# 50-digit reference at 8 sparse-check points (cs4ref.py), 8 procs, then the comparison. nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_ref_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/ref50
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] cs4 50-digit reference at 8 points, nice 10" >> ~/claude-work.log
seq 0 7 | xargs -P 8 -L 1 sh -c 'nice -n 10 '"$PY"' cs4ref.py "$0" 8 '"$OUT"' > '"$OUT"'/logs/c$0.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/c$0.txt'
nice -n 10 $PY cs4ref.py compare "$OUT" > "$OUT/logs/compare.log" 2>&1; echo "exit=$?" > "$OUT/exits/compare.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] cs4 50-digit reference: done" >> ~/claude-work.log

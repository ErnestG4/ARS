#!/usr/bin/env bash
# Sparse direct check of the ζ connected R₄ (sparse_check.py): 300 points in 10 parallel chunks, then merge. nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_sparse_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/sparse
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] cs4 sparse direct R4 check: 300 points, 10 procs, nice 10" >> ~/claude-work.log
seq 0 9 | xargs -P 10 -L 1 sh -c 'nice -n 10 '"$PY"' sparse_check.py "$0" 10 '"$OUT"' > '"$OUT"'/logs/c$0.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/c$0.txt'
nice -n 10 $PY sparse_check.py merge "$OUT" > "$OUT/logs/merge.log" 2>&1; echo "exit=$?" > "$OUT/exits/merge.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] cs4 sparse direct R4 check: done" >> ~/claude-work.log

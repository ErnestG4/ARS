#!/usr/bin/env bash
# Sparse direct check v2 (sparse_check_ref.py): 300 points vs the 50-digit reference, 32 chunks, then merge. nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_sparse_ref_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/sparse_ref
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 CS4_CHUNK=64
echo "$(date -Is) [CC specarith] cs4 sparse check v2 vs 50-digit reference: 300 points, 32 procs, nice 10" >> ~/claude-work.log
seq 0 31 | xargs -P 32 -L 1 sh -c 'nice -n 10 '"$PY"' sparse_check_ref.py "$0" 32 '"$OUT"' > '"$OUT"'/logs/c$0.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/c$0.txt'
nice -n 10 $PY sparse_check_ref.py merge "$OUT" > "$OUT/logs/merge.log" 2>&1; echo "exit=$?" > "$OUT/exits/merge.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] cs4 sparse check v2: done" >> ~/claude-work.log

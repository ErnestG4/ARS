#!/usr/bin/env bash
# Phase 1 zero generation (gen_zeros.py): quadratic characters then elliptic-curve isogeny classes, 16 chunks each, then
# the manifest. GENERATION ONLY (no statistics before the Phase 1 seal). nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph1/run_gen_spot.sh
set -u
D=~/tmp/claude/specarith/ph1
PY=~/miniforge3/envs/specarith/bin/python
cd "$D"
OUT=results/zeros
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph1 zero generation (chi_d |d|<=2e5, EC N<=5e4), 16 procs, nice 10" >> ~/claude-work.log
for kind in chi ec; do
  seq 0 15 | xargs -P 16 -L 1 sh -c 'nice -n 10 '"$PY"' gen_zeros.py '"$kind"' "$0" 16 '"$OUT"' > '"$OUT"'/logs/'"$kind"'_$0.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/'"$kind"'_$0.txt'
done
nice -n 10 $PY gen_zeros.py merge "$OUT" > "$OUT/logs/merge.log" 2>&1; echo "exit=$?" > "$OUT/exits/merge.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph1 zero generation: done" >> ~/claude-work.log

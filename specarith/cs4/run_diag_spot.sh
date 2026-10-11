#!/usr/bin/env bash
# Prime-cutoff diagnostic (diag_pmax.py v2): one process per cutoff, chunk sized so A*'s ~40 temporaries stay
# ≤ ~4 GB per process (CHUNK × #primes × 16 B × 40). nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_diag_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/diag
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] cs4 prime-cutoff diagnostic: pmax 1e4, 3e4, 1e5, 3e5, 1e6, nice 10" >> ~/claude-work.log
printf '%s\n' "10000 1024" "30000 1024" "100000 512" "300000 192" "1000000 64" |
  xargs -P 5 -L 1 sh -c 'CS4_CHUNK=$1 nice -n 10 '"$PY"' diag_pmax.py "$0" '"$OUT"' > '"$OUT"'/logs/p$0.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/p$0.txt'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] cs4 prime-cutoff diagnostic: done" >> ~/claude-work.log

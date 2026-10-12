#!/usr/bin/env bash
# Thirty-fourth round item 2: ζ T₅ from the ratios-conjecture definition at the edge nodes of every F3 height
# (ratios_t5.py zeta), after the U(N) gate passed (results/ratios_t5_ugate.json). 16 chunks, nice 10. Heights only.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_ratios_t5_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/ratios_t5
mkdir -p "$OUT/logs"
rm -f "$OUT/DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ratios_t5 zeta T5: 16 chunks, nice 10" >> ~/claude-work.log
seq 0 15 | xargs -P 16 -I{} sh -c 'nice -n 10 '"$PY"' ratios_t5.py zeta {} 16 '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" >> '"$OUT"'/logs/c{}.log'
nice -n 10 $PY ratios_t5.py merge "$OUT" > "$OUT/logs/merge.log" 2>&1; echo "exit=$?" >> "$OUT/logs/merge.log"
date -Is > "$OUT/DONE"
echo "$(date -Is) [CC specarith] ratios_t5 zeta T5: done" >> ~/claude-work.log

#!/usr/bin/env bash
# Stage 2 U(N) step: sine-kernel v(b) on the full ladder, direct and split (gs_unitary.py). One process, nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_gs_unitary_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/gs_unitary
mkdir -p "$OUT"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
echo "$(date -Is) [CC specarith] cs4 gs_unitary: sine-kernel v(b) ladder, direct + split, nice 10" >> ~/claude-work.log
nice -n 10 $PY gs_unitary.py run "$OUT" > "$OUT/run.log" 2>&1; echo "exit=$?" > "$OUT/exit.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] cs4 gs_unitary: done" >> ~/claude-work.log

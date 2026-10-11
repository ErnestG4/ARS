#!/usr/bin/env bash
# Does the dropped ℓ-oscillating long-range part dephase across a file's ℓ range? diag_osc_alias.py (full ladder,
# Δr = 0.1) for pair (5,5) at the 5 Gauss–Legendre nodes of the F2 15.75 file's range [15.7259, 15.7742]
# (weights ∝ GL·ℓe^ℓ: 0.115725 0.236002 0.284413 0.242620 0.121239). 5 procs, nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_diag_osc_lavg_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/diag_osc_lavg
mkdir -p "$OUT"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] diag_osc_lavg: 5 procs, nice 10" >> ~/claude-work.log
printf '15.728166\n15.737046\n15.750050\n15.763054\n15.771934\n' | xargs -P 5 -I{} sh -c 'nice -n 10 '"$PY"' diag_osc_alias.py {} 5 5 '"$OUT"' full > '"$OUT"'/l_{}.log 2>&1; echo "exit=$?" >> '"$OUT"'/l_{}.log'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] diag_osc_lavg: done" >> ~/claude-work.log

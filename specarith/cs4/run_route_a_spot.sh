#!/usr/bin/env bash
# Route (a) U(N) spacing-law gate (route_a_pgate.py), 24 procs on spot (the local run was lost in the 03:05 freeze). nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_route_a_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
mkdir -p results
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] cs4 route (a) U(N) spacing-law gate, 24 procs, nice 10" >> ~/claude-work.log
nice -n 10 $PY route_a_pgate.py 24 > results/route_a_pgate.log 2>&1; echo "exit=$?" > results/route_a_pgate.exit
echo "$(date -Is) [CC specarith] cs4 route (a) gate: done" >> ~/claude-work.log

#!/usr/bin/env bash
# Stage 2 U(N) step (ii): CUE_400 Monte Carlo of the tapered variance vs the assembly (gs_cue_mc.py).
# Prediction, then 50 chunks x 2000 matrices (1e5 total, seeds 1..50), 40 procs, then merge. nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_gs_cue_mc_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/gs_cue_mc
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] cs4 gs_cue_mc: CUE_400 MC 1e5 matrices, 40 procs, nice 10" >> ~/claude-work.log
nice -n 10 $PY gs_cue_mc.py pred 400 "$OUT" > "$OUT/logs/pred.log" 2>&1; echo "exit=$?" > "$OUT/exits/pred.txt"
seq 1 50 | xargs -P 40 -L 1 sh -c 'nice -n 10 '"$PY"' gs_cue_mc.py mc 400 2000 "$0" '"$OUT"' > '"$OUT"'/logs/s$0.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/s$0.txt'
nice -n 10 $PY gs_cue_mc.py merge 400 "$OUT" > "$OUT/logs/merge.log" 2>&1; echo "exit=$?" > "$OUT/exits/merge.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] cs4 gs_cue_mc: done" >> ~/claude-work.log

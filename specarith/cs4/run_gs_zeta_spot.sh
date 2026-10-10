#!/usr/bin/env bash
# Stage 2 ζ prediction (gs_zeta.py) at the five F2 files' zero-weighted mean heights ℓ (computed from the pinned
# height ranges in ph2r2/FRESH_SETS_F1_F3.md; no F2 data is read). nice 10.
#  1. ρ₃ tasks (5 heights × 8 chunks), 12 procs, now (alongside the CUE MC);
#  2. wait for the CUE MC to finish (results/gs_cue_mc/ALL_DONE), then the 210 node pairs per height in 42 chunks of 3-4
#     (136 pairs since gs_zeta v2; 210 tasks), 48 procs; resumable (existing pair files are skipped);
#  3. merge per height.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_gs_zeta_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/gs_zeta
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
ELLS="15.7502 16.4972 17.2491 19.5003 21.75"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] gs_zeta: rho3 (12 procs), then pairs (48 procs) after the CUE MC, 5 heights, nice 10" >> ~/claude-work.log
for L in $ELLS; do for c in $(seq 0 7); do echo "$L $c"; done; done | xargs -P 12 -L 1 sh -c 'nice -n 10 '"$PY"' gs_zeta.py rho3 "$0" "$1" 8 '"$OUT"' > '"$OUT"'/logs/r3_$0_$1.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/r3_$0_$1.txt'
while [ ! -f results/gs_cue_mc/ALL_DONE ]; do sleep 60; done
echo "$(date -Is) [CC specarith] gs_zeta: CUE MC done; starting pairs" >> ~/claude-work.log
for L in $ELLS; do for c in $(seq 0 41); do echo "$L $c"; done; done | xargs -P 48 -L 1 sh -c 'nice -n 10 '"$PY"' gs_zeta.py pairs "$0" "$1" 42 '"$OUT"' > '"$OUT"'/logs/pr_$0_$1.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/pr_$0_$1.txt'
for L in $ELLS; do
  nice -n 10 $PY gs_zeta.py merge "$L" "$OUT" > "$OUT/logs/merge_$L.log" 2>&1; echo "exit=$?" > "$OUT/exits/merge_$L.txt"
done
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] gs_zeta: done" >> ~/claude-work.log

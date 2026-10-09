#!/usr/bin/env bash
# R₂ pre-read G0b on spot: cache each fresh bin's CS07 kernel, then 40 surrogates per bin (CUE_250 blocks at the bin's
# density) in chunks of 2, 50 processes, nice 10, one thread each; then merge (bias, SD, bootstrap coverage, primary f).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph2r2/run_g0b_spot.sh
set -u
D=~/tmp/claude/specarith/ph2r2
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/g0b
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ph2r2 G0b: kernels + 200 surrogates (5 bins x 40), 50 procs, nice 10" >> ~/claude-work.log
printf '%s\n' R1 R2 R3 R4 R5 | xargs -P 5 -L 1 sh -c 'nice -n 10 '"$PY"' g0b.py kernel "$0" '"$OUT"' > '"$OUT"'/logs/kernel_$0.log 2>&1; echo "kernel $0 exit=$?" > '"$OUT"'/exits/kernel_$0.txt'
for b in R1 R2 R3 R4 R5; do for r in $(seq 0 2 38); do echo "$b $r $((r + 2))"; done; done > "$OUT/jobs.txt"
xargs -P 50 -L 1 sh -c 'nice -n 10 '"$PY"' g0b.py run "$0" "$1" "$2" '"$OUT"' > '"$OUT"'/logs/$0_r$1.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/$0_r$1.txt' < "$OUT/jobs.txt"
nice -n 10 $PY g0b.py merge "$OUT" > "$OUT/logs/merge.log" 2>&1; echo "exit=$?" > "$OUT/exits/merge.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph2r2 G0b: done" >> ~/claude-work.log

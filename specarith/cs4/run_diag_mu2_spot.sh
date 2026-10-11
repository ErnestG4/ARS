#!/usr/bin/env bash
# Two-point mean μ(ℓ) across each F2 file (diag_mu2.py): 5 files, one process each, nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_diag_mu2_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/diag_mu2
mkdir -p "$OUT"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] diag_mu2: 5 procs, nice 10" >> ~/claude-work.log
printf '0\n1\n2\n3\n4\n' | xargs -P 5 -I{} sh -c 'nice -n 10 '"$PY"' diag_mu2.py {} '"$OUT"' > '"$OUT"'/f{}.log 2>&1; echo "exit=$?" >> '"$OUT"'/f{}.log'
$PY diag_mu2.py summary "$OUT" > "$OUT/summary.txt" 2>&1
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] diag_mu2: done" >> ~/claude-work.log

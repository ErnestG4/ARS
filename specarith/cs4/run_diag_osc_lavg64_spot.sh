#!/usr/bin/env bash
# Dense ℓ average of pair (5,5)'s dropped ℓ-oscillating long-range part over the F2 15.75 file's range
# [15.7259, 15.7742]: 64 midpoint (stratified) ℓ values, diag_osc_alias.py full ladder, Δr = 0.1. The 5-node GL average
# cannot resolve it (the resonant phase turns ~70 rad between nodes at b = 10⁴). Weights ∝ ℓe^ℓ, applied in the reader.
# 32 procs, nice 10.  Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_diag_osc_lavg64_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/diag_osc_lavg64
mkdir -p "$OUT"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] diag_osc_lavg64: 64 tasks, 32 procs, nice 10" >> ~/claude-work.log
$PY -c "print('\n'.join('%.7f' % (15.7259 + (k + 0.5) * (15.7742 - 15.7259) / 64) for k in range(64)))" \
  | xargs -P 32 -I{} sh -c 'nice -n 10 '"$PY"' diag_osc_alias.py {} 5 5 '"$OUT"' full > '"$OUT"'/l_{}.log 2>&1; echo "exit=$?" >> '"$OUT"'/l_{}.log'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] diag_osc_lavg64: done" >> ~/claude-work.log

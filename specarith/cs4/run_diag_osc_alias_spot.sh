#!/usr/bin/env bash
# diag_osc_alias.py on spot. Pass 1: pairs (5,5), (2,8) at ℓ = 15.7502, 21.75, b ≤ 300; 4 procs, nice 10.
# Pass 2 (FULL=1): the whole ladder, + ℓ = 16.4972 (5,5); 5 procs.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_diag_osc_alias_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/diag_osc_alias
mkdir -p "$OUT"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] diag_osc_alias: 4 procs, nice 10" >> ~/claude-work.log
if [ "${FULL:-0}" = 1 ]; then
  printf '15.7502 5 5\n15.7502 2 8\n16.4972 5 5\n21.75 5 5\n21.75 2 8\n' | xargs -P 5 -L 1 sh -c 'nice -n 10 '"$PY"' diag_osc_alias.py "$0" "$1" "$2" '"$OUT"' full > '"$OUT"'/f_$0_$1_$2.log 2>&1; echo "exit=$?" >> '"$OUT"'/f_$0_$1_$2.log'
else
  printf '15.7502 5 5\n15.7502 2 8\n21.75 5 5\n21.75 2 8\n' | xargs -P 4 -L 1 sh -c 'nice -n 10 '"$PY"' diag_osc_alias.py "$0" "$1" "$2" '"$OUT"' > '"$OUT"'/a_$0_$1_$2.log 2>&1; echo "exit=$?" >> '"$OUT"'/a_$0_$1_$2.log'
fi
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] diag_osc_alias: done" >> ~/claude-work.log

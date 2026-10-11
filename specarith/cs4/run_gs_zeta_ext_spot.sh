#!/usr/bin/env bash
# Estimator B: extend the long-range non-oscillating C(r) to 6·10⁴ (gs_zeta_ext.py), 5 heights × 8 chunks = 40 procs,
# nice 10.  Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_gs_zeta_ext_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/gs_zeta
mkdir -p "$OUT/ext_logs"
rm -f "$OUT/EXT_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] gs_zeta_ext: 40 procs, nice 10" >> ~/claude-work.log
for L in 15.7502 16.4972 17.2491 19.5003 21.75; do for c in 0 1 2 3 4 5 6 7; do echo "$L $c"; done; done |
  xargs -P 40 -L 1 sh -c 'nice -n 10 '"$PY"' gs_zeta_ext.py pairs "$0" "$1" 8 '"$OUT"' > '"$OUT"'/ext_logs/L$0_c$1.log 2>&1; echo "exit=$?" >> '"$OUT"'/ext_logs/L$0_c$1.log'
date -Is > "$OUT/EXT_DONE"
echo "$(date -Is) [CC specarith] gs_zeta_ext: done" >> ~/claude-work.log

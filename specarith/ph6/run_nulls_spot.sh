#!/usr/bin/env bash
# Seal §9.4 on spot: calibration null draws (100 GUE + 100 Poisson) and bands at G0-c, G2 and G0's configurations.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph6/run_nulls_spot.sh
set -u
D=~/tmp/claude/specarith/ph6
PY=~/miniforge3/envs/specarith/bin/python
cd "$D"
rm -f preread_out/NULLS_DONE
echo "$(date -Is) [CC specarith] null calibration draws G0c, G2, G0 (16 procs, nice 10)" >> ~/claude-work.log
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for C in G0c G2 G0; do
  nice -n 10 $PY preread.py nulls preread_out "$C" 100 100 16 > "preread_out/nulls_$C.log" 2>&1
  echo "$C exit=$?" >> preread_out/nulls_exits.txt
done
date -Is > preread_out/NULLS_DONE
echo "$(date -Is) [CC specarith] null calibration draws done" >> ~/claude-work.log

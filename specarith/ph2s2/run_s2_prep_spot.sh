#!/usr/bin/env bash
# Stage 2 pre-seal on spot (twenty-seventh round): (1) tapered window sums of the 24 Stage 2 GUE sequences (F2 baseline,
# f2_gue_levels.py) -> results/tapered_f2gue; (2) s2read.py dryrun (F1 decoded through the read path; GUE stand-in;
# guard witness); (3) s2_preread.py seemp + guecal on both GUE sets. nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph2s2/run_s2_prep_spot.sh
set -u
D=~/tmp/claude/specarith/ph2s2
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
L=results/s2_prep_logs
mkdir -p "$L" results/tapered_f2gue results/s2_preread
rm -f results/S2_PREP_DONE
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ph2s2 Stage 2 pre-seal: tapered F2 GUE x24, dry run, calibration; nice 10" >> ~/claude-work.log
ls results/gue/gue_L1000000_s0*.npy |
  xargs -P 24 -I{} sh -c 'nice -n 10 '"$PY"' tapered.py gue {} results/tapered_f2gue >> '"$L"'/tapered_f2gue.log 2>&1; echo "exit=$? {}" >> '"$L"'/tapered_f2gue.exits'
nice -n 10 "$PY" s2read.py dryrun > "$L/dryrun.log" 2>&1; echo "exit=$?" >> "$L/dryrun.log"
nice -n 10 "$PY" s2_preread.py seemp results/s2_preread > "$L/seemp.log" 2>&1; echo "exit=$?" >> "$L/seemp.log"
nice -n 10 "$PY" s2_preread.py guecal results/s2_preread > "$L/guecal.log" 2>&1; echo "exit=$?" >> "$L/guecal.log"
date -Is > results/S2_PREP_DONE
echo "$(date -Is) [CC specarith] ph2s2 Stage 2 pre-seal: done" >> ~/claude-work.log

#!/usr/bin/env bash
# Round 54: the sealed read of one observable on the fresh F4/F5 files: run1, run2 (separate processes), compare.
# The compare report goes to compare_$OBS.log, opened only after BOTH observables' compares are done (round 54).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_followup_read_spot.sh OBS
set -u
OBS=$1
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
D=results/followup_read
mkdir -p $D
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) replications: sealed read ($OBS), run1/run2/compare" >> ~/claude-work.log
{ nice -n 10 $PY followup_sealread.py read $OBS run1 && nice -n 10 $PY followup_sealread.py read $OBS run2; } > $D/read_$OBS.log 2>&1
echo "exit=$?" > $D/read_$OBS.exit
nice -n 10 $PY followup_sealread.py compare $OBS > $D/compare_$OBS.log 2>&1
echo "exit=$?" > $D/compare_$OBS.exit
echo "$(date -Is) [CC specarith] route (a) replications: sealed read ($OBS): done" >> ~/claude-work.log

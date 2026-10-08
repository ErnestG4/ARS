#!/usr/bin/env bash
# Dry run (seal sequence: pre-read -> DRY RUN -> seal): full-size synthetic bins A, B, P1–P6 (CUE_N levels placed by
# N̄⁻¹ in each bin's representation; no zero file is opened), gates per bin, then the A6(iii) witness on P1 cut to
# 3,000 spacings. One process per bin, own output files; nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph2/run_dryrun_spot.sh
set -u
D=~/tmp/claude/specarith/ph2
PY=~/miniforge3/envs/specarith/bin/python
cd "$D"
mkdir -p results/run_synth/logs results/run_synth/exits
rm -f results/run_synth/ALL_DONE
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ph2 dry run: 8 synthetic bins, nice 10" >> ~/claude-work.log
printf '%s\n' "A 2" "B 3" "P1 3" "P2 3" "P3 4" "P4 4" "P5 5" "P6 5" |
  xargs -P 8 -L 1 sh -c 'nice -n 10 '"$PY"' run.py unfold "$0" --synthetic "$1" > results/run_synth/logs/$0.log 2>&1 && nice -n 10 '"$PY"' run.py gates "$0" --synthetic "$1" >> results/run_synth/logs/$0.log 2>&1; echo "exit=$?" > results/run_synth/exits/$0.txt'
nice -n 10 $PY run.py witness_achieved P1 --synthetic 3 --keep 3000 > results/run_synth/logs/witness_achieved.log 2>&1
echo "exit=$?" > results/run_synth/exits/witness_achieved.txt
date -Is > results/run_synth/ALL_DONE
echo "$(date -Is) [CC specarith] ph2 dry run: done" >> ~/claude-work.log

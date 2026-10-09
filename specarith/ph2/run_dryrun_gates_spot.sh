#!/usr/bin/env bash
# Dry run, final pass: re-run the gates (seal amendments A6–A8 included) on the synthetic spacings that
# run_dryrun_spot.sh already unfolded, all with one code version, then the A6(iii) witness on P1 cut to 3,000 spacings.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph2/run_dryrun_gates_spot.sh
set -u
D=~/tmp/claude/specarith/ph2
PY=~/miniforge3/envs/specarith/bin/python
cd "$D"
mkdir -p results/run_synth/logs2 results/run_synth/exits2
rm -f results/run_synth/GATES_DONE
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
md5sum ph2lib.py preread.py run.py > results/run_synth/code_md5_gates.txt
echo "$(date -Is) [CC specarith] ph2 dry run: final gates pass, 8 bins + witness, nice 10" >> ~/claude-work.log
printf '%s\n' "A 2" "B 3" "P1 3" "P2 3" "P3 4" "P4 4" "P5 5" "P6 5" |
  xargs -P 8 -L 1 sh -c 'nice -n 10 '"$PY"' run.py gates "$0" --synthetic "$1" > results/run_synth/logs2/$0.log 2>&1; echo "exit=$?" > results/run_synth/exits2/$0.txt'
nice -n 10 $PY run.py witness_achieved P1 --synthetic 3 --keep 3000 > results/run_synth/logs2/witness_achieved.log 2>&1
echo "exit=$?" > results/run_synth/exits2/witness_achieved.txt
date -Is > results/run_synth/GATES_DONE
echo "$(date -Is) [CC specarith] ph2 dry run: final gates pass done" >> ~/claude-work.log

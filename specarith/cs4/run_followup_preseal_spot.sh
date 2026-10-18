#!/usr/bin/env bash
# Round 53 pre-seal record on the final code: read selftest, refusals (A, B), witness, then both dry runs in parallel.
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
W=results/followup_witness
mkdir -p $W
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) replications: pre-seal record on the final code" >> ~/claude-work.log
md5sum followup_*.py route_a_read.py route_a_zeta.py ../ph2/ph2lib.py > $W/code_md5.txt
nice -n 10 $PY followup_read.py selftest > results/followup_gates_logs/read_selftest.log 2>&1; echo "exit=$?" > results/followup_gates_logs/read_selftest.exit
for O in A B; do nice -n 10 $PY followup_sealread.py refusals $O > $W/refusals_$O.log 2>&1; echo "exit=$?" > $W/refusals_$O.exit; done
nice -n 10 $PY followup_sealread.py witness > $W/witness.log 2>&1; echo "exit=$?" > $W/witness.exit
rm -rf results/followup_dryrun/A results/followup_dryrun/B
bash run_followup_dryrun_spot.sh A &
bash run_followup_dryrun_spot.sh B &
wait
date -Is > $W/PRESEAL_DONE
echo "$(date -Is) [CC specarith] route (a) replications: pre-seal record: done" >> ~/claude-work.log

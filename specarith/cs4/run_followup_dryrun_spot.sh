#!/usr/bin/env bash
# Round 53 pre-seal record: the sealed read on the CUE stand-ins under a dry-run seal, twice in separate processes, then
# compare and the dry-run record. Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_followup_dryrun_spot.sh OBS
set -u
OBS=$1
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
SYN=results/followup_dryrun_synth
LOG=results/followup_dryrun/dryrun_$OBS.log
mkdir -p results/followup_dryrun
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) replications: dry run ($OBS)" >> ~/claude-work.log
{ nice -n 10 $PY followup_sealread.py dryrun_prepare $OBS $SYN && \
  nice -n 10 $PY followup_sealread.py dryrun_read $OBS run1 $SYN && \
  nice -n 10 $PY followup_sealread.py dryrun_read $OBS run2 $SYN && \
  nice -n 10 $PY followup_sealread.py dryrun_record $OBS $SYN; } > "$LOG" 2>&1
echo "exit=$?" > results/followup_dryrun/dryrun_$OBS.exit
echo "$(date -Is) [CC specarith] route (a) replications: dry run ($OBS): done" >> ~/claude-work.log

#!/usr/bin/env bash
# Corrected (B) (round 58) pre-seal record, stage 2: the sealed read on the CUE stand-ins under a dry-run seal, twice in
# separate processes, then compare and the dry-run record; then the refusal red paths. Final code, pinned calibration.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_b2_dryrun_spot.sh
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
SYN=results/b2_dryrun_synth
OUT=results/b2_dryrun
mkdir -p "$OUT"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] corrected (B) dry run + refusals" >> ~/claude-work.log
{ nice -n 10 $PY b2_sealread.py dryrun_prepare $SYN && \
  nice -n 10 $PY b2_sealread.py dryrun_read run1 $SYN && \
  nice -n 10 $PY b2_sealread.py dryrun_read run2 $SYN && \
  nice -n 10 $PY b2_sealread.py dryrun_record $SYN; } > "$OUT/dryrun.log" 2>&1
echo "exit=$?" > "$OUT/dryrun.exit"
nice -n 10 $PY b2_sealread.py refusals > "$OUT/refusals.log" 2>&1
echo "exit=$?" > "$OUT/refusals.exit"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] corrected (B) dry run + refusals: done" >> ~/claude-work.log

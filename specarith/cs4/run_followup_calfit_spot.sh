#!/usr/bin/env bash
# Route (a) replications (round 52): calibration fits (followup_read.py calib_fit) on the char-sampled sequences in
# results/followup_calsamp (md5-checked against char before the run), NCH procs, nice 10. Run only after the
# predictions are tagged. Restartable (each chunk skips rows written).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_followup_calfit_spot.sh [NCH]
set -u
NCH=${1:-40}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
OUT=results/followup_calfit
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) replications: calibration fits, $NCH procs, nice 10" >> ~/claude-work.log
seq 0 $((NCH - 1)) | xargs -P "$NCH" -I{} sh -c 'nice -n 10 '"$PY"' followup_read.py calib_fit results/followup_calsamp '"$OUT"' {} '"$NCH"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/c{}.exit'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] route (a) replications: calibration fits: done" >> ~/claude-work.log

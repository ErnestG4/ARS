#!/usr/bin/env bash
# Corrected (B) (round 58) pre-seal record, stage 1: the CUE_1000 stand-ins at F6 geometry (b2_sealread.py sample →
# synth → pipeline), one process per F6 file, nice 10. Independent of the calibration and the stamp. Restartable per file.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_b2_standin_spot.sh
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
SYN=results/b2_dryrun_synth
mkdir -p "$SYN/logs"
rm -f "$SYN/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 SYN PY
echo "$(date -Is) [CC specarith] corrected (B) stand-ins at F6 geometry: 4 procs, nice 10" >> ~/claude-work.log
printf '%s\n' zeros_46646000.dat zeros_256646000.dat zeros_2365046000.dat zeros_10630646000.dat |
  xargs -P 4 -I{} sh -c '{ { [ -f "$SYN/{}.npy" ] || nice -n 10 $PY b2_sealread.py sample "$SYN" {}; } &&
    nice -n 10 $PY b2_sealread.py synth "$SYN" {} && nice -n 10 $PY b2_sealread.py pipeline "$SYN" {}; } \
    > "$SYN/logs/{}.log" 2>&1; echo "exit=$?" > "$SYN/logs/{}.exit"'
date -Is > "$SYN/ALL_DONE"
echo "$(date -Is) [CC specarith] corrected (B) stand-ins at F6 geometry: done" >> ~/claude-work.log

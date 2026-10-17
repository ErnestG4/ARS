#!/usr/bin/env bash
# Route (a) replications (round 52): calibration samples, CUE_1000 R = 200 per F4/F5 file at the pre-data sizes, on
# char's GPU, two processes (reps 0-99, 100-199), nice 10. Data-free. Restartable (each process skips rows written).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_followup_calsamp_char.sh
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/tmp/claude/venv/bin/python
OUT=results/followup_calsamp
mkdir -p "$OUT"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) replications: calibration samples R 0-199, 2 procs" >> ~/claude-work.log
nice -n 10 $PY followup_calsamp.py run 0 100 "$OUT" > "$OUT/a.log" 2>&1 &
A=$!
nice -n 10 $PY followup_calsamp.py run 100 200 "$OUT" > "$OUT/b.log" 2>&1 &
B=$!
wait $A; echo "exit=$?" > "$OUT/a.exit"
wait $B; echo "exit=$?" > "$OUT/b.exit"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] route (a) replications: calibration samples: done" >> ~/claude-work.log

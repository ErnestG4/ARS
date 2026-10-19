#!/usr/bin/env bash
# Corrected (B) (round 58): calibration from scratch, CUE_1000 R = 200 per F6 file at its pre-data size through the
# offset-averaged estimator at L* (b2_calsamp.py), char GPU, two processes (reps 0-99, 100-199), nice 10. Data-free.
# Restartable. Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_b2_calsamp_char.sh
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/tmp/claude/venv/bin/python
OUT=results/b2_calsamp
mkdir -p "$OUT"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] corrected (B) calibration samples R 0-199 at L*, 2 procs" >> ~/claude-work.log
nice -n 10 $PY b2_calsamp.py run 0 100 "$OUT" > "$OUT/a.log" 2>&1 &
A=$!
nice -n 10 $PY b2_calsamp.py run 100 200 "$OUT" > "$OUT/b.log" 2>&1 &
B=$!
wait $A; echo "exit=$?" > "$OUT/a.exit"
wait $B; echo "exit=$?" > "$OUT/b.exit"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] corrected (B) calibration samples: done" >> ~/claude-work.log

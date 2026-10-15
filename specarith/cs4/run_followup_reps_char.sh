#!/usr/bin/env bash
# Follow-up selection rule (round 48): CUE_1000 replicates R = 100 per F3-geometry file on char's GPU, two processes
# (reps 0-49, 50-99), nice 10. Data-free. Restartable (each process skips (rep, file) already written).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_followup_reps_char.sh
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/tmp/claude/venv/bin/python
OUT=results/followup_reps
mkdir -p "$OUT"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] follow-up CUE replicates: R 0-99, 2 procs" >> ~/claude-work.log
nice -n 10 $PY followup_reps.py run 0 50 "$OUT" > "$OUT/a.log" 2>&1 &
A=$!
nice -n 10 $PY followup_reps.py run 50 100 "$OUT" > "$OUT/b.log" 2>&1 &
B=$!
wait $A; echo "exit=$?" > "$OUT/a.exit"
wait $B; echo "exit=$?" > "$OUT/b.exit"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] follow-up CUE replicates: done" >> ~/claude-work.log

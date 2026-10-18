#!/usr/bin/env bash
# Corrected (B) L rule (CORRECTED_B_DESIGN.md §2): CUE_1000 R = 100 per F3 file, all L and offsets, char GPU, 2 procs,
# nice 10. Data-free. Restartable. Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_b2_rule_char.sh
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/tmp/claude/venv/bin/python
OUT=results/b2_rule
mkdir -p "$OUT"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] corrected (B) L-rule CUE replicates R 0-99, 2 procs" >> ~/claude-work.log
nice -n 10 $PY b2_rule.py samp 0 50 "$OUT" > "$OUT/a.log" 2>&1 &
A=$!
nice -n 10 $PY b2_rule.py samp 50 100 "$OUT" > "$OUT/b.log" 2>&1 &
B=$!
wait $A; echo "exit=$?" > "$OUT/a.exit"
wait $B; echo "exit=$?" > "$OUT/b.exit"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] corrected (B) L-rule CUE replicates: done" >> ~/claude-work.log

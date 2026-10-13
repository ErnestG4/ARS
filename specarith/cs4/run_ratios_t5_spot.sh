#!/usr/bin/env bash
# Thirty-fourth round item 2: ζ T₅ from the ratios-conjecture definition at the edge nodes of every F3 height
# (ratios_t5.py zeta), after the U(N) gate passed (results/ratios_t5_ugate.json). Heights only.
# Run 2 (2026-10-12, Will's rule: restart wins when the run is < half done): one task per job (54 tasks, chunk i of 54
# = job i), the four p ≤ 3000 cutoff-check jobs (indices 50–53, ~3× the cost) first, then the rest; P workers (default
# 16), nice 10. Run 1 (16 chunks of 3–4 jobs, previous code) was stopped after 7.5 h with no job finished.
# Run 3 (after the 2026-10-12 17:40 brownout reboot; run 2 had 12 of 54 jobs, kept): per-batch checkpoints
# (ratios_t5.T5_model; results/ratios_t5/ckpt/), so a reboot costs minutes, not hours. Finished jobs are skipped.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_ratios_t5_spot.sh [P]
set -u
P=${1:-15}
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/ratios_t5
mkdir -p "$OUT/logs"
rm -f "$OUT/DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ratios_t5 zeta T5 run 3 (checkpointed): remaining of 54 single-job tasks, heaviest first, $P procs, nice 10" >> ~/claude-work.log
{ seq 50 53; seq 0 49; } | xargs -P "$P" -I{} sh -c 'nice -n 10 '"$PY"' ratios_t5.py zeta {} 54 '"$OUT"' >> '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" >> '"$OUT"'/logs/c{}.log'
nice -n 10 $PY ratios_t5.py merge "$OUT" > "$OUT/logs/merge.log" 2>&1; echo "exit=$?" >> "$OUT/logs/merge.log"
date -Is > "$OUT/DONE"
echo "$(date -Is) [CC specarith] ratios_t5 zeta T5 run 3: done" >> ~/claude-work.log

#!/usr/bin/env bash
# Phase 1 zero generation, U family (gen_zeros_u.py; thirty-first round D1): the conjugate-convention check first (the
# run stops if it fails), then 16 chunks, then the merge. GENERATION ONLY (no statistic before the Phase 1 seal). nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph1/run_gen_u_spot.sh
set -u
D=~/tmp/claude/specarith/ph1
PY=~/miniforge3/envs/specarith/bin/python
cd "$D"
OUT=results/zeros_u
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph1 U-family zero generation: check, then 16 procs, nice 10" >> ~/claude-work.log
nice -n 10 $PY gen_zeros_u.py check > "$OUT/logs/check.log" 2>&1
rc=$?
echo "exit=$rc" > "$OUT/exits/check.txt"
if [ "$rc" -ne 0 ]; then
  echo "$(date -Is) [CC specarith] ph1 U-family: conjugate check did not pass (rc=$rc); generation not started" >> ~/claude-work.log
  date -Is > "$OUT/ALL_DONE"
  exit 1
fi
seq 0 15 | xargs -P 16 -I{} sh -c 'nice -n 10 '"$PY"' gen_zeros_u.py u {} 16 '"$OUT"' > '"$OUT"'/logs/u_{}.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/u_{}.txt'
nice -n 10 $PY gen_zeros_u.py merge "$OUT" > "$OUT/logs/merge.log" 2>&1; echo "exit=$?" > "$OUT/exits/merge.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph1 U-family zero generation: done" >> ~/claude-work.log

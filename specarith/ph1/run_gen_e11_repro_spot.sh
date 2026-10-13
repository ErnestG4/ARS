#!/usr/bin/env bash
# Phase 1 P5(i): zeros of the E₁₁ even quadratic twists, the DHKMS reproduction range d ≤ 4·10⁵ (8,431 twists).
# GENERATION ONLY (no statistic before the Phase 1 seal). Independent of X′, which concerns only the fresh range.
# 64 chunks (each chunk's file is written when the chunk finishes, so small chunks bound a brownout's loss), P workers
# (default 16: the cores route (a) leaves idle), nice 10; then the manifest (tag repro).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph1/run_gen_e11_repro_spot.sh [P]
set -u
P=${1:-16}
D=~/tmp/claude/specarith/ph1
PY=~/miniforge3/envs/specarith/bin/python
cd "$D"
OUT=results/zeros_e11_repro
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph1 E11 twist zeros, reproduction range d <= 4e5: 64 chunks, $P procs, nice 10" >> ~/claude-work.log
seq 0 63 | xargs -P "$P" -I{} sh -c 'f='"$OUT"'/e11_0_400000_$(printf %03d {}).jsonl; [ -s "$f" ] && exit 0; nice -n 10 '"$PY"' gen_twists_e11.py run 0 400000 {} 64 '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/c{}.txt'
nice -n 10 $PY gen_twists_e11.py merge "$OUT" repro > "$OUT/logs/merge.log" 2>&1; echo "exit=$?" > "$OUT/exits/merge.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph1 E11 reproduction-range zeros: done" >> ~/claude-work.log

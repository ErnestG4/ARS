#!/usr/bin/env bash
# E₁₁ X′ cost curve at a MEMORY-SAFE worker count (2026-10-13, after the 56-worker probe exhausted spot's 117 GB:
# peak RSS per worker ≈ 3.0 GB at d ≈ 10⁶ and 1.5·10⁶, so P = 30 keeps the peak ≈ 90 GB, ~77% of RAM).
# P workers × 1 twist at each of d ≈ 5·10⁵, 10⁶, 1.5·10⁶, 2·10⁶ (timings only), then the X′ projection at P. nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph1/run_e11_cost_spot.sh [P]
set -u
P=${1:-30}
D=~/tmp/claude/specarith/ph1
PY=~/miniforge3/envs/specarith/bin/python
cd "$D"
OUT=results/e11_probe
mkdir -p "$OUT"
rm -f "$OUT/DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] E11 X' cost curve at P = $P (memory-safe), d ~ 5e5..2e6" >> ~/claude-work.log
for MAG in 500000 1000000 1500000 2000000; do
  seq 0 $((P - 1)) | xargs -P "$P" -I{} nice -n 10 $PY e11_probe.py worker $MAG {} 1 "$OUT/cost_P${P}_$MAG.jsonl"
done
$PY e11_probe.py project "$OUT" "$P" > "$OUT/project.log" 2>&1
date -Is > "$OUT/DONE"
echo "$(date -Is) [CC specarith] E11 X' cost curve: done" >> ~/claude-work.log

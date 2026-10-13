#!/usr/bin/env bash
# E₁₁ X′ measurement on an IDLE spot (thirty-seventh round): (1) worker-count probe at d ≈ 10⁶: P = 16, 28, 40, 56
# workers, each timing 2 distinct twists, all started together; (2) cost curve at the best P (most twists per hour):
# P workers × 1 twist at each of d ≈ 5·10⁵, 10⁶, 1.5·10⁶, 2·10⁶; (3) X′ projection. Timings only, no zeros kept. nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph1/run_e11_probe_spot.sh
set -u
D=~/tmp/claude/specarith/ph1
PY=~/miniforge3/envs/specarith/bin/python
cd "$D"
OUT=results/e11_probe
mkdir -p "$OUT"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] E11 X' probe: worker-count probe at d~1e6 (P = 16, 28, 40, 56), then cost curve" >> ~/claude-work.log
for P in 16 28 40 56; do
  seq 0 $((P - 1)) | xargs -P "$P" -I{} nice -n 10 $PY e11_probe.py worker 1000000 {} 2 "$OUT/scale_P$P.jsonl"
done
BEST=$($PY - "$OUT" 2> "$OUT/scale.log" <<'EOF'
import json, sys, glob
best, bp = 0, None
for f in sorted(glob.glob(sys.argv[1] + "/scale_P*.jsonl")):
    P = int(f.split("_P")[1].split(".")[0])
    rows = [json.loads(l) for l in open(f)]
    mean = sum(r["secs"] for r in rows) / len(rows)
    thr = P / mean * 3600
    print(f"P = {P}: {len(rows)} twists, mean {mean:.0f} s per twist, throughput {thr:.0f} twists/h", file=sys.stderr)
    if thr > best:
        best, bp = thr, P
print(bp)
EOF
)
echo "$(date -Is) [CC specarith] E11 probe: best P = $BEST; cost curve" >> ~/claude-work.log
for MAG in 500000 1000000 1500000 2000000; do
  seq 0 $((BEST - 1)) | xargs -P "$BEST" -I{} nice -n 10 $PY e11_probe.py worker $MAG {} 1 "$OUT/cost_P${BEST}_$MAG.jsonl"
done
$PY e11_probe.py project "$OUT" "$BEST" > "$OUT/project.log" 2>&1
date -Is > "$OUT/DONE"
echo "$(date -Is) [CC specarith] E11 X' probe: done (best P = $BEST)" >> ~/claude-work.log

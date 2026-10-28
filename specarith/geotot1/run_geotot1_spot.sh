#!/bin/bash
# GEO-TOT1 enumeration on spot (GEOTOT1_SEAL.md §7): [2, Q] in 200 chunks of equal modelled cost, single-thread
# processes, at most P at a time; cost checks at the first wave and at 25 / 50 / 75% (stop above 1.25x).
# Usage: run_geotot1_spot.sh Q P OUT_DIR
Q=$1; P=$2; O=$3
cd ~/tmp/claude/specarith/geotot1 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
mkdir -p $O/parts
echo "$(date -Is) [CC specarith] geotot1 enum Q=$Q P=$P: start" >> ~/claude-work.log
$PY - "$Q" > $O/chunks.txt <<'PYEOF'
import math, sys
Q = int(float(sys.argv[1])); mu = 12 * math.log(2) / math.pi ** 2; c = 1.0
w = lambda q: (q - 1) * (mu * math.log(q) + c)
tot = sum(w(q) for q in range(2, Q + 1)); n = 200; acc, lo, k = 0.0, 2, 0
for q in range(2, Q + 1):
    acc += w(q)
    if acc >= tot * (k + 1) / n or q == Q:
        print(k, lo, q, f"{acc:.6g}"); lo = q + 1; k += 1
PYEOF
date +%s > $O/t0
# model: 6.06 ns per Euclid step x 2.3 (spot) — per-chunk model seconds = steps * 6.06e-9 * 2.3
export NUMBA_NUM_THREADS=1
awk '{print $1, $2, $3}' $O/chunks.txt | xargs -P $P -n 3 sh -c 'nice -n 10 '$PY' geotot1.py enum $1 $2 '$O'/parts/part_$(printf %03d $0).npz > '$O'/parts/log_$0.txt 2>&1; echo $0 $? $(date +%s) >> '$O'/done.txt' &
XP=$!
check() {   # $1 = label, $2 = chunks done to wait for; cost = Σ chunk CPU / Σ chunk model over finished chunks
  while [ $(cat $O/done.txt 2>/dev/null | wc -l) -lt $2 ]; do sleep 30; done
  $PY - $O $1 <<'PYEOF'
import sys, math
O, lab = sys.argv[1], sys.argv[2]
mu = 12 * math.log(2) / math.pi ** 2
ch = {int(l.split()[0]): (int(l.split()[1]), int(l.split()[2])) for l in open(f"{O}/chunks.txt")}
done = [int(l.split()[0]) for l in open(f"{O}/done.txt")]
model = sum(sum((q - 1) * (mu * math.log(q) + 1.0) for q in range(ch[k][0], ch[k][1] + 1)) for k in done) * 6.06e-9 * 2.3
cpu = sum(float(open(f"{O}/parts/part_{k:03d}.npz.cpu").read()) for k in done)
print(f"{lab}: {len(done)} chunks, cpu/model = {cpu / model:.3f}", flush=True)
sys.exit(3 if cpu > 1.25 * model else 0)
PYEOF
}
for spec in "first 1" "25 50" "50 100" "75 150"; do
  set -- $spec
  check $1 $2 >> $O/checks.txt || { echo "cost above 1.25x at $1" > $O/STOPPED; kill $XP; exit 3; }
done
wait $XP
echo "$(date -Is) [CC specarith] geotot1 enum: chunks done" >> ~/claude-work.log
date -Is > $O/ENUM_DONE

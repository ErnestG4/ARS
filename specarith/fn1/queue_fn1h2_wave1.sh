#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1-h2 archive, TOOLKIT §9.H stratified first wave (FN1H2_SEAL.md §8), timing only, before the bulk.
# Cases: Cornacchia type 1 (D ≡ 1 mod 4: 4p form) at the smallest / median / largest |D| (−15, −115, −427) and type 0
# (D ≡ 0 mod 4: p form; −20, −52, −232), each at k ∈ {1, 100, 199}: 18 tasks, one pueue task each, in
# specarith-filler through pq-fill. The segments are kept as part of the archives. Model 61.2 s CPU per task.
# The bulk is queued separately (queue_fn1h2_bulk.sh) only if the wave's CPU total ≤ 1.25 × its model.
#   bash queue_fn1h2_wave1.sh
set -euo pipefail
ROOT=/mnt/data/fn1h2; CODE=~/tmp/claude/specarith/fn1; Q=$ROOT/pq; PQ=~/.local/bin/pueue
mountpoint -q /mnt/data || { echo "REFUSED: /mnt/data is not a mount point"; exit 2; }
[ ! -e $Q/wave1_ids.txt ] || { echo "REFUSED: wave 1 already queued"; exit 1; }
mkdir -p $Q $ROOT/logs
ids=""
for D in -15 -115 -427 -20 -52 -232; do for k in 1 100 199; do
  f=$Q/w1_D${D#-}_k$k; echo "$D $k" > $f
  ids="$ids $($PQ add -p -g specarith-filler -w $CODE -l specarith:fn1h2-arch-w1-D${D#-}-k$k -- pq-fill --no-viz archive-generation fn1h2-arch-w1 2 bash $CODE/run_fn1h2_chunk.sh $f)"
done; done
echo "$ids" > $Q/wave1_ids.txt
echo "$(date -Is) [CC specarith] fn1h2 archive §9.H first wave queued (specarith-filler): pueue$ids" >> ~/claude-work.log
echo "wave1:$ids"

#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1-h2 archive bulk (FN1H2_SEAL.md §8), queued only after the §9.H first wave's projection is OK
# (fn1h2_costs.py wave1). The 3,582 remaining segments, ordered by k then field, in chunks of CHUNK (default 20),
# split at the half point: first-half chunks → mid check (--after all) → second-half chunks (--after mid) → final
# check + manifests. All in specarith-filler through pq-fill (CPUWeight=idle), unique job names, labels specarith:<job>.
#   bash queue_fn1h2_bulk.sh [CHUNK]
set -euo pipefail
CHUNK=${1:-20}
ROOT=/mnt/data/fn1h2; CODE=~/tmp/claude/specarith/fn1; Q=$ROOT/pq; PQ=~/.local/bin/pueue
PY=~/miniforge3/envs/ph6c/bin/python
mountpoint -q /mnt/data || { echo "REFUSED: /mnt/data is not a mount point"; exit 2; }
[ ! -e $Q/bulk_ids.txt ] || { echo "REFUSED: bulk already queued"; exit 1; }
[ ! -e $ROOT/STOPPED ] || { echo "REFUSED: STOPPED exists"; exit 1; }
$PY $CODE/fn1h2_costs.py $ROOT wave1 | tee $ROOT/cost_wave1.txt | tail -1 | grep -qx OK || { echo "REFUSED: wave-1 projection"; exit 1; }
for k in $(seq 0 199); do for D in -15 -20 -24 -35 -40 -51 -52 -88 -91 -115 -123 -148 -187 -232 -235 -267 -403 -427; do
  [ -e $ROOT/archive_2e10_D${D#-}/seg_$(printf %04d $k).npy ] || echo "$D $k"; done; done > $Q/remaining.txt
NJ=$(wc -l < $Q/remaining.txt); HALF=$((NJ / 2))
head -n $HALF $Q/remaining.txt | split -l $CHUNK -d -a 3 - $Q/b1_
tail -n +$((HALF + 1)) $Q/remaining.txt | split -l $CHUNK -d -a 3 - $Q/b2_
add() { $PQ add -p -g specarith-filler -w $CODE "$@"; }
B1=""
for f in $Q/b1_*; do n=$(basename $f)
  B1="$B1 $(add -l specarith:fn1h2-arch-$n -- pq-fill --no-viz archive-generation fn1h2-arch-$n 2 bash $CODE/run_fn1h2_chunk.sh $f)"; done
MID=$(add -l specarith:fn1h2-arch-midcheck --after $B1 -- pq-fill --no-viz archive-check fn1h2-arch-midcheck 2 bash $CODE/run_fn1h2_check.sh mid)
B2=""
for f in $Q/b2_*; do n=$(basename $f)
  B2="$B2 $(add -l specarith:fn1h2-arch-$n --after $MID -- pq-fill --no-viz archive-generation fn1h2-arch-$n 2 bash $CODE/run_fn1h2_chunk.sh $f)"; done
FIN=$(add -l specarith:fn1h2-arch-final --after $B2 -- pq-fill --no-viz archive-manifest fn1h2-arch-final 16 bash $CODE/run_fn1h2_check.sh final)
{ echo "b1:$B1"; echo "mid $MID"; echo "b2:$B2"; echo "final $FIN"; } > $Q/bulk_ids.txt
echo "remaining $NJ; chunks b1 $(ls $Q/b1_* | wc -l), b2 $(ls $Q/b2_* | wc -l); mid $MID final $FIN"
echo "$(date -Is) [CC specarith] fn1h2 archive bulk queued (specarith-filler): $NJ segments, mid $MID, final $FIN" >> ~/claude-work.log

#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1 stage-2 archive: move the remaining segments from the direct xargs launcher (run_fn1_archive2_spot.sh, stopped by
# PID at no task boundary; tasks are atomic and skip existing segments) into the shared pueue daemon on spot
# (~/pll-fabric-queue/tools/queue/README.md): own group specarith-filler, every task through pq-fill (CPUWeight=idle,
# memory cap), labels specarith:<job>. Seconds-long; run once, after no fn1_archive.py task process remains.
#   remaining = jobs2_order.txt lines whose segment file does not exist, kept in the launcher's order and split at
#   the launcher's half point (first half / second half); chunks of CHUNK lines (default 20, ≈ 17 min);
#   first-half chunks → mid check (--after all of them) → second-half chunks (--after the mid check) → final check +
#   manifests (--after all second-half chunks).
#   bash queue_fn1_archive2_pueue.sh [PARALLEL] [CHUNK]
set -euo pipefail
PAR=${1:-24}; CHUNK=${2:-20}
ROOT=/mnt/data/fn1; CODE=~/tmp/claude/specarith/fn1; Q=$ROOT/pq2
PQ=~/.local/bin/pueue
mountpoint -q /mnt/data || { echo "REFUSED: /mnt/data is not a mount point"; exit 2; }
[ ! -e $ROOT/STOPPED2 ] || { echo "REFUSED: STOPPED2 exists"; exit 1; }
[ ! -e $Q ] || { echo "REFUSED: $Q exists (already queued?)"; exit 1; }
mkdir -p $Q
NJ=$(wc -l < $ROOT/jobs2_order.txt); HALF=$((NJ / 2))
awk -v H=$HALF -v R=$ROOT '{f=sprintf("%s/archive_1e11_D%d/seg_%04d.npy", R, -$1, $2); if ((getline x < f) < 0) print $1, $2, (NR<=H?1:2); close(f)}' $ROOT/jobs2_order.txt > $Q/remaining.txt
awk '$3==1{print $1, $2}' $Q/remaining.txt | split -l $CHUNK -d -a 3 - $Q/h1_
awk '$3==2{print $1, $2}' $Q/remaining.txt | split -l $CHUNK -d -a 3 - $Q/h2_
$PQ group | grep -q '^Group "specarith-filler"' || $PQ group add specarith-filler -p "$PAR"
$PQ parallel -g specarith-filler "$PAR"
add() { $PQ add -p -g specarith-filler -w $CODE "$@"; }
H1=""
for f in $Q/h1_*; do [ -e "$f" ] || continue; n=$(basename $f)
  H1="$H1 $(add -l specarith:fn1-arch2-$n -- pq-fill --no-viz archive-generation fn1-arch2-$n 2 bash $CODE/run_fn1_archive2_chunk.sh $f)"; done
MID=$(add -l specarith:fn1-arch2-midcheck ${H1:+--after $H1} -- pq-fill --no-viz archive-check fn1-arch2-midcheck 2 bash $CODE/run_fn1_archive2_check.sh mid)
H2=""
for f in $Q/h2_*; do n=$(basename $f)
  H2="$H2 $(add -l specarith:fn1-arch2-$n --after $MID -- pq-fill --no-viz archive-generation fn1-arch2-$n 2 bash $CODE/run_fn1_archive2_chunk.sh $f)"; done
FIN=$(add -l specarith:fn1-arch2-final --after $H2 -- pq-fill --no-viz archive-manifest fn1-arch2-final 16 bash $CODE/run_fn1_archive2_check.sh final)
echo "h1 ids:$H1" > $Q/ids.txt; echo "mid $MID" >> $Q/ids.txt; echo "h2 ids:$H2" >> $Q/ids.txt; echo "final $FIN" >> $Q/ids.txt
echo "remaining $(wc -l < $Q/remaining.txt) (h1 $(awk '$3==1' $Q/remaining.txt | wc -l), h2 $(awk '$3==2' $Q/remaining.txt | wc -l)); chunks h1 $(ls $Q/h1_* 2>/dev/null | wc -l), h2 $(ls $Q/h2_* | wc -l); mid $MID final $FIN"
echo "$(date -Is) [CC specarith] fn1 archive2 moved to pueue group specarith-filler (-p $PAR): $(wc -l < $Q/remaining.txt) segments, mid $MID, final $FIN" >> ~/claude-work.log

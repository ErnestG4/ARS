#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1 stage-2 archive, pueue continuation: the launcher's stop rules and final step, as pueue tasks.
#   bash run_fn1_archive2_check.sh mid     cost rule after the first half (mid_run2.txt); any failure → STOPPED2, exit 1
#   bash run_fn1_archive2_check.sh final   failures → STOPPED2; cost rule (final_ratio2.txt); manifests over all 1010
#                                          segments (summary2.exit); ALL_DONE2
# A failing pueue task makes its dependents DependencyFailed, so a stop here stops the rest of the queue.
set -u
CODE=~/tmp/claude/specarith/fn1; ROOT=/mnt/data/fn1; LG=$ROOT/logs2
PY=~/miniforge3/envs/ph6c/bin/python
export OMP_NUM_THREADS=1
cd $CODE || exit 1
mountpoint -q /mnt/data || { echo "REFUSED: /mnt/data is not a mount point" > $ROOT/STOPPED2; exit 2; }
if [ "$1" = mid ]; then
  $PY fn1_archive2_costs.py $ROOT check > $ROOT/mid_run2.txt
  if grep -q EXCEEDS $ROOT/mid_run2.txt || [ -s $LG/failed.txt ]; then echo "mid-run over the per-job cost model or a task failed" > $ROOT/STOPPED2; exit 1; fi
  exit 0
fi
[ -s $LG/failed.txt ] && { echo "task failures" > $ROOT/STOPPED2; exit 1; }
$PY fn1_archive2_costs.py $ROOT check > $ROOT/final_ratio2.txt
: > $ROOT/summary2.exit
for D in -7 -8 -11 -19 -43 -67 -163; do
  MANIFEST_PROCS=${MANIFEST_PROCS:-24} $PY fn1_archive.py manifest $D $ROOT/archive_1e11_D${D#-} 1.01e11 > $LG/manifest_D${D#-}.log 2>&1
  echo "D=$D exit=$?" >> $ROOT/summary2.exit
done
date -Is > $ROOT/ALL_DONE2
echo "$(date -Is) [CC specarith] fn1 stage-2 archives to 1.01e11: done (pueue)" >> ~/claude-work.log

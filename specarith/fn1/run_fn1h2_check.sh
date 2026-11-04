#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1-h2 archive cost checks (FN1H2_SEAL.md §8). mid / q3: cost rule; on EXCEEDS write $ROOT/STOPPED (later chunks
# skip their segments) and exit 1. final: cost rule, then the 18 manifests (hashes, counts, integrity; no statistic)
# and the count report (fn1h2_counts.py, −148 explicit). Rule: COSTMODE (default price: the approved seal price,
# rebased 2026-11-04 by Will; check = the original first-wave rule).
#   bash run_fn1h2_check.sh mid|q3|final
set -u
CODE=~/tmp/claude/specarith/fn1; ROOT=/mnt/data/fn1h2; PY=~/miniforge3/envs/ph6c/bin/python
cd $CODE || exit 1
mountpoint -q /mnt/data || { echo "REFUSED: /mnt/data not mounted"; exit 2; }
if ! $PY fn1h2_costs.py $ROOT ${COSTMODE:-price} > $ROOT/cost_$1.txt 2>&1; then
  cat $ROOT/cost_$1.txt; date -Is > $ROOT/STOPPED
  echo "$(date -Is) [CC specarith] fn1h2 archive $1 check EXCEEDS: STOPPED written" >> ~/claude-work.log; exit 1
fi
cat $ROOT/cost_$1.txt
echo "$(date -Is) [CC specarith] fn1h2 archive $1 check: $(tail -2 $ROOT/cost_$1.txt | head -1)" >> ~/claude-work.log
[ "$1" = final ] || exit 0
[ -s $ROOT/logs/failed.txt ] && { echo "failed segments present"; exit 1; }
rc=0
for D in -15 -20 -24 -35 -40 -51 -52 -88 -91 -115 -123 -148 -187 -232 -235 -267 -403 -427; do
  MANIFEST_PROCS=8 $PY fn1h2_archive.py manifest $D $ROOT/archive_2e10_D${D#-} 2e10 >> $ROOT/manifests.log 2>&1 || rc=1
done
$PY fn1h2_counts.py $ROOT $ROOT/COUNTS.json > $ROOT/counts.log 2>&1 || rc=1
date -Is > $ROOT/ALL_DONE
echo "$(date -Is) [CC specarith] fn1h2 archive manifests written (rc $rc)" >> ~/claude-work.log
exit $rc

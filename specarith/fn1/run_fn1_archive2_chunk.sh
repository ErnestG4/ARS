#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1 stage-2 archive, pueue continuation: one chunk. Runs the "D k" lines of JOBFILE in order with the unchanged
# fn1_archive.py task (it skips segments that already exist; it writes atomically), logging exactly as the xargs phase
# (logs2/tasks_D*.log, done.txt, failed.txt), plus CPU seconds per task in logs2/cpu_D*.log ("k user sys wall").
# Queued by queue_fn1_archive2_pueue.sh inside pq-fill (CPUWeight=idle, memory cap). Exit 1 if any task failed.
#   bash run_fn1_archive2_chunk.sh JOBFILE
set -u
CODE=~/tmp/claude/specarith/fn1; ROOT=/mnt/data/fn1; LG=$ROOT/logs2
PY=~/miniforge3/envs/ph6c/bin/python
export OMP_NUM_THREADS=1
cd $CODE || exit 1
rc=0
while read -r D k; do
  [ -n "${D:-}" ] || continue
  if ! mountpoint -q /mnt/data; then echo "$D $k" >> $LG/failed.txt; rc=1; continue; fi
  t=$(mktemp ~/tmp/claude/specarith/fn1/cpu.XXXXXX)
  if /usr/bin/time -o "$t" -f "%U %S %e" $PY fn1_archive.py task $D $k $ROOT/archive_1e11_D${D#-} >> $LG/tasks_D${D#-}.log 2>&1; then
    echo "$D $k" >> $LG/done.txt
    echo "$k $(tail -1 "$t")" >> $LG/cpu_D${D#-}.log
  else
    echo "$D $k" >> $LG/failed.txt; rc=1
  fi
  rm -f "$t"
done < "$1"
exit $rc

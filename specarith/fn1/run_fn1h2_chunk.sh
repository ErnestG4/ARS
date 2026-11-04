#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1-h2 archive (FN1H2_SEAL.md §3, §8): one chunk of "D k" lines, run in order with fn1h2_archive.py task (skips
# existing segments, writes atomically). Generation only: no statistic. CPU seconds per task → logs/cpu_D*.log
# ("k user sys wall"); done.txt / failed.txt. Queued inside pq-fill (CPUWeight=idle, memory cap). Exit 1 if any failed.
#   bash run_fn1h2_chunk.sh JOBFILE
set -u
CODE=~/tmp/claude/specarith/fn1; ROOT=/mnt/data/fn1h2; LG=$ROOT/logs
PY=~/miniforge3/envs/ph6c/bin/python
export OMP_NUM_THREADS=1
cd $CODE || exit 1
mkdir -p $LG
rc=0
while read -r D k; do
  [ -n "${D:-}" ] || continue
  if ! mountpoint -q /mnt/data; then echo "$D $k" >> $LG/failed.txt; rc=1; continue; fi
  [ ! -e $ROOT/STOPPED ] || { echo "$D $k" >> $LG/skipped_stopped.txt; continue; }
  out=$ROOT/archive_2e10_D${D#-}; mkdir -p $out
  t=$(mktemp ~/tmp/claude/specarith/fn1/cpu.XXXXXX)
  if /usr/bin/time -o "$t" -f "%U %S %e" $PY fn1h2_archive.py task $D $k $out >> $LG/tasks_D${D#-}.log 2>&1; then
    echo "$D $k" >> $LG/done.txt
    echo "$k $(tail -1 "$t")" >> $LG/cpu_D${D#-}.log
  else
    echo "$D $k" >> $LG/failed.txt; rc=1
  fi
  rm -f "$t"
done < "$1"
exit $rc

#!/bin/bash
# Sequential job queue (one heavy job at a time after the 2026-09-25 10:59 WSL crash). Honours STOP.
cd "$(dirname "$0")"
PY=/home/combust/fmexplorer/bin/python3
while read -r line; do
  [ -z "$line" ] && continue; [[ "$line" == \#* ]] && continue
  [ -e STOP ] && { echo "$(date +%T) STOP present, queue halted"; exit 3; }
  name=${line%%|*}; cmd=${line#*|}
  echo "$(date +%T) START $name"
  bash -c "$cmd" > "logs/$name.log" 2>&1; rc=$?
  echo "$(date +%T) END $name rc=$rc"
done < "$1"

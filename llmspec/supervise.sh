#!/bin/bash
# Run queue files in order. If a queue halts because memwatch wrote STOP (content "memwatch"), wait until the host's
# free commit is back above 8 GB, clear that STOP and re-run the same queue (every job is resumable). A STOP with any
# other content (e.g. Will's `touch STOP`) is respected: the supervisor exits.
cd "$(dirname "$0")"
for q in "$@"; do
  while true; do
    ./queue.sh "$q"
    if [ -e STOP ]; then
      if [ "$(cat STOP 2>/dev/null)" = "memwatch" ]; then
        echo "$(date +%T) supervisor: memwatch STOP; waiting for host commit > 8 GB"
        while true; do
          h=$(timeout 15 powershell.exe -NoProfile -Command '$o=Get-CimInstance Win32_OperatingSystem; "{0:N1}" -f ($o.FreeVirtualMemory/1MB)' 2>/dev/null | tr -d '\r ')
          [ -n "$h" ] && awk -v h="$h" 'BEGIN{exit !(h > 8.0)}' && break
          sleep 60
        done
        rm -f STOP; echo "$(date +%T) supervisor: commit ${h}G, resuming $q"; continue
      fi
      echo "$(date +%T) supervisor: manual STOP present, exiting"; exit 3
    fi
    grep -q "rc=[1-9]" "logs/$(basename "$q" .txt).log" 2>/dev/null && echo "$(date +%T) supervisor: $q had a failing job (see log)"
    break
  done
done
echo "$(date +%T) supervisor: all queues done"

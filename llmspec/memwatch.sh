#!/bin/bash
# Memory/GPU/host-disk watchdog: one line per 5 s, so a future crash leaves evidence.
while true; do
  echo "$(date +%T) $(free -m | awk '/Mem/{print "used="$3"M avail="$7"M"}') gpu=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)M C_free=$(df -BG --output=avail /mnt/c | tail -1 | tr -d ' ') top=$(ps -eo rss,comm --sort=-rss | awk 'NR==2{print $2":"int($1/1024)"M"}')"
  sleep 5
done

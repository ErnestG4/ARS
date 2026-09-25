#!/bin/bash
# Memory/GPU watchdog: one line per 30 s, so a future crash leaves evidence.
while true; do
  echo "$(date +%T) $(free -m | awk '/Mem/{print "used="$3"M avail="$7"M"}') $(free -m | awk '/Swap/{print "swap="$3"M"}') gpu=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)M top=$(ps -eo rss,comm --sort=-rss | awk 'NR==2{print $2":"int($1/1024)"M"}')"
  sleep 30
done

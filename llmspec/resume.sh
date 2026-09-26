#!/bin/bash
# One-command resume after a reboot / WSL restart: watchdog + the whole remaining pipeline, detached.
# Every stage skips finished work (DONE markers, per-layer npz, per-type witness, per-pair motion, per-condition G2).
cd "$(dirname "$0")"
if [ -e STOP ]; then echo "STOP present (content: '$(cat STOP)'); remove it first if you want to resume"; exit 1; fi
if ps -eo args | grep -q "[s]upervise.sh"; then echo "already running"; exit 0; fi
setsid nohup ./memwatch.sh >> logs/memwatch.log 2>&1 < /dev/null &
setsid nohup ./supervise.sh queue4.txt queue5.txt queue6.txt >> logs/supervisor.log 2>&1 < /dev/null &
sleep 2
echo "resumed: $(ps -eo pid,args | grep -E '[m]emwatch.sh|[s]upervise.sh' | awk '{print $1, $3}' | tr '\n' ' ')"

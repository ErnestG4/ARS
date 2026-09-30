#!/usr/bin/env bash
# Start a fresh queue_runner after PID $1 exits, unless llmspec/STOP exists (finished arms are skipped; B-G1 re-checked).
cd "$(dirname "$0")/.."
while kill -0 "$1" 2>/dev/null; do sleep 60; done
[ -e STOP ] && { echo "$(date -Is) chain: STOP present, not starting" >> armb/queue_runner.log; exit 3; }
echo "$(date -Is) chain: starting fresh queue_runner after PID $1" >> armb/queue_runner.log
exec /home/combust/fmexplorer/bin/python3 armb/queue_runner.py

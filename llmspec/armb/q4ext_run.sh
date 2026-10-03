#!/usr/bin/env bash
# Q4EXT descriptive extraction runner (Q4EXT_PREREG.md §2): waits for the divisor extraction chain to finish, re-checks
# GPU_STATUS: FREE and no trainer, then q4ext_extract.py extract (sealed B4 extractor, stops extended) and dw0, then
# q4ext_descriptive.py. STOP-aware (b4_extract honours llmspec/STOP), resumable. Log: armb/q4ext_run.log.
set -u
cd "$(dirname "$0")/.."
PY=/home/combust/fmexplorer/bin/python3
while [ -f divisor/chain_extract.log ] && ! grep -qE "EXTRACT_ALL_DONE|NOT extracting" divisor/chain_extract.log; do sleep 30; done
if [ "$(grep -c 'GPU_STATUS: FREE' NOTES.md)" -lt 1 ] || ps -eo args | grep -q '^/home/combust/fmexplorer/bin/python3 train.py'; then
  echo "$(date -Is) GPU not free; NOT running"; exit 2; fi
echo "$(date -Is) Q4EXT extraction start"
$PY armb/q4ext_extract.py extract A0 M0s1 M0s3; rc=$?; echo "$(date -Is) extract rc=$rc"
[ $rc -ne 0 ] && exit $rc
$PY armb/q4ext_extract.py dw0 A0 M0s1 M0s3; rc=$?; echo "$(date -Is) dw0 rc=$rc"
OMP_NUM_THREADS=4 $PY armb/q4ext_descriptive.py; echo "$(date -Is) descriptive rc=$?"
echo "$(date -Is) Q4EXT_RUN_DONE"

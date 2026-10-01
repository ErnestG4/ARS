#!/usr/bin/env bash
# Q4EXT_PREREG.md queue: waits for the A0r scoring run, then A0 -> 10000, M0s1 -> 10000, M0s3 -> 3000. STOP-aware, resumable.
cd "$(dirname "$0")" || exit 1
PY=/home/combust/fmexplorer/bin/python3
SP=$(cat a0r_score.pid 2>/dev/null)
while [ -n "$SP" ] && kill -0 "$SP" 2>/dev/null; do sleep 60; done
for spec in "A0 --stop 10000" "M0s1 --stop 10000" "M0s3"; do
  set -- $spec; arm=$1
  [ -f ../STOP ] && { echo "$(date -Is) STOP present; queue halted before $arm"; exit 2; }
  echo "$(date -Is) === start $spec"
  $PY train.py $spec >> train_${arm}_ext.log 2>&1
  rc=$?; echo "$(date -Is) === $arm exited $rc"
  [ $rc -ne 0 ] && { echo "halting queue"; exit $rc; }
done
echo "$(date -Is) === EXT QUEUE DONE"

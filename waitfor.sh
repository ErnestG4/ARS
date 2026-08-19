#!/usr/bin/env bash
# waitfor.sh — wait on a PROCESS, never on an artifact.
#
# Why this exists: on 2026-08-18 a background job died at its own timeout
# without writing its output file, and a waiter of the form
#
#     until [ -f out.json ]; do sleep 20; done
#
# spun for 7h44m on a file that would never appear.  Two status reports were
# written during that window claiming the job was "still running".  Waiting on
# an ARTIFACT means a dead process is indistinguishable from a slow one — which
# is exactly the banked `verify_liveness_not_last_line` lesson, violated by the
# person who banked it.
#
# Usage:
#   ./waitfor.sh <PID> [deadline_seconds] [artifact]
#
#   PID       the job's process id (`cmd & echo $!`) — NOT a pattern
#   deadline  hard cap; default 3600.  Exceeding it is REPORTED, not silent.
#   artifact  optional expected output; its absence at exit is REPORTED.
#
# Exit codes:  0 finished and artifact present (or none expected)
#              3 process died WITHOUT producing the artifact   <-- the case
#                that cost the night
#              4 deadline exceeded while still running
set -u
PATTERN="${1:?usage: waitfor.sh <PID> [deadline_s] [artifact]   # PID, not a pattern}"
DEADLINE="${2:-3600}"
ARTIFACT="${3:-}"

# WAIT ON A PID, NOT A PATTERN. First version used `pgrep -f "$PATTERN"`, which
# matches on the full command line — and this script's own argv, AND the shell
# wrapper that invoked it, both contain the pattern. So a DEAD job looked alive
# until the deadline: the exact failure this script exists to prevent, rebuilt
# inside the fix, and found only by red-pathing it. Excluding $$ and $PPID was
# not enough (the harness wrapper is neither). A PID cannot self-match.
#   PATTERN is now a PID.  Get it with:  cmd & echo $!
alive() { kill -0 "$PATTERN" 2>/dev/null; }

start=$(date +%s)
if ! alive; then
  echo "waitfor: PID $PATTERN is not alive — it never started, or it is"
  echo "         already gone. NOT waiting."
  [ -n "$ARTIFACT" ] && [ -f "$ARTIFACT" ] && { echo "         artifact present: $ARTIFACT"; exit 0; }
  exit 3
fi

while alive; do
  now=$(date +%s); el=$((now - start))
  if [ "$el" -ge "$DEADLINE" ]; then
    echo "waitfor: DEADLINE ${DEADLINE}s exceeded, '$PATTERN' still running after ${el}s."
    echo "         Not killing it. Decide explicitly."
    exit 4
  fi
  sleep 10
done

el=$(( $(date +%s) - start ))
if [ -n "$ARTIFACT" ] && [ ! -f "$ARTIFACT" ]; then
  echo "waitfor: process '$PATTERN' EXITED after ${el}s WITHOUT producing $ARTIFACT."
  echo "         Treat as failure — a missing artifact after exit is a dead job,"
  echo "         not a slow one."
  exit 3
fi
echo "waitfor: '$PATTERN' finished after ${el}s${ARTIFACT:+ (artifact present)}."
exit 0

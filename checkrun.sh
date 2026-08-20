#!/usr/bin/env bash
# checkrun.sh — run a checker and emit a MACHINE-WRITTEN pass/fail record.
#
# WHY: three exit-code misreads in one session, the last of which put a false
# "verify_bridge green" claim into a commit message. Twice the cause was reading
# $? after a PIPE (`cmd | tail` reports tail's status, not cmd's). "Read the exit
# code more carefully" is a docstring-grade fix for a bug with a measured rate —
# and this session's own epitaph is that rules you merely consult do not hold.
#
#   ./checkrun.sh <checker> [args...]
#
# Prints the checker's output, then a line NO HUMAN TYPED:
#     CHECKRUN <path> EXIT=<n> <PASS|FAIL>
# Paste that line into the commit message instead of asserting green. Never
# pipes; captures the real status.
set -u
CHECKER="${1:?usage: checkrun.sh <checker> [args...]}"; shift || true
OUT=$(mktemp)
if [[ "$CHECKER" == *.py ]]; then
  /home/combust/fmexplorer/bin/python3 "$CHECKER" "$@" >"$OUT" 2>&1
else
  "$CHECKER" "$@" >"$OUT" 2>&1
fi
RC=$?                       # captured BEFORE anything else touches $?
cat "$OUT"; rm -f "$OUT"
if [ "$RC" -eq 0 ]; then VERDICT=PASS; else VERDICT=FAIL; fi
echo "CHECKRUN $CHECKER EXIT=$RC $VERDICT"
exit "$RC"

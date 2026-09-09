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
LINE="CHECKRUN $CHECKER EXIT=$RC $VERDICT"
echo "$LINE"
# ALSO record it where the commit-msg hook can VERIFY it. Added 2026-09-09 after
# a commit message carried "CHECKRUN verify_all.py EXIT=0 PASS" while the board
# was red: the line had been TYPED, not pasted, because `checkrun ... | grep ...
# && git commit` tested grep's status instead of the checker's -- an exit code
# read through a pipe, the exact defect this script exists to prevent. The hook
# could not catch it, because it checked that a CHECKRUN line was PRESENT and
# self-consistent, never that it had actually been produced by a run.
printf '%s\t%s\n' "$(date +%s)" "$LINE" >> "$(dirname "$0")/.checkrun_log"
exit "$RC"

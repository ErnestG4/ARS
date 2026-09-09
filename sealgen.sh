#!/usr/bin/env bash
# sealgen.sh — commit a generator BEFORE it produces output, then run it.
#
# WHY: twice in two days a generator and its output landed in the same commit
# (3b501fe: rounding convention + dedup result; 8ba9d52: verdict mapping + sweep
# table). Both times the rule inside the generator was written before the run —
# and both times the commit graph could not show it, so the honest report was
# "declared, not sealed". Commit order is the evidence, not recollection, and
# recollection is exactly what post-hoc rationalisation feels like from inside.
#
#   ./sealgen.sh <generator.py> "<commit message>" [-- args...]
#
# Commits the generator ALONE (refusing if its outputs are already staged), then
# runs it. The output is committed separately, afterwards, by you.
set -u
GEN="${1:?usage: sealgen.sh <generator.py> \"<msg>\" [-- args...]}"
MSG="${2:?commit message required}"
shift 2; [ "${1:-}" = "--" ] && shift || true

if ! git diff --cached --quiet -- . 2>/dev/null; then
  STAGED=$(git diff --cached --name-only | grep -v "^${GEN}$" || true)
  if [ -n "$STAGED" ]; then
    echo "REFUSED: files other than the generator are staged:"; echo "$STAGED"
    echo "Commit the generator ALONE so the commit graph proves it preceded its output."
    exit 2
  fi
fi
git add "$GEN" || exit 1
git commit -q -m "$MSG" || exit 1
echo "SEALED GENERATOR: $(git rev-parse --short HEAD)  $GEN"
echo "-- running --"
/home/combust/fmexplorer/bin/python3 "$GEN" "$@"
RC=$?
SEALLINE="CHECKRUN $GEN EXIT=$RC $([ $RC -eq 0 ] && echo PASS || echo FAIL)"
echo "$SEALLINE"
# Log it where the commit-msg hook can verify it, exactly as checkrun.sh does.
# Added 2026-09-09, minutes after the provenance hook went in and immediately
# REFUSED a legitimate sealgen line: sealgen emits its own machine record, and a
# guard that trusts only one of two producers turns honest work into a forgery.
# Found by the guard rejecting honest work, which is the good direction.
printf '%s\t%s\n' "$(date +%s)" "$SEALLINE" >> "$(dirname "$0")/.checkrun_log"
echo "Now commit the OUTPUT separately; the graph will show generator-then-result."
exit $RC

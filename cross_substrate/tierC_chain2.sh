#!/usr/bin/env bash
# Tier C, second leg: the two expensive population producers.
# Waits for the arithmetic runner to exit, then runs them SEQUENTIALLY.
#
# population_strat needs its bank MOVED ASIDE first: with the bank in place its
# resume logic marks every task done and opens the file in "a" mode, so the run
# silently does nothing and the file keeps its stale axis. quasiperiodic_operators
# truncates immediately instead, so it needs no such handling.
set -u
ROOT=/home/combust/fmexplorer/criticality_tool
PY=/home/combust/fmexplorer/bin/python3
BASE=$HOME/fmexplorer/coordinate_baselines_2026-07-31_tierC
COORD=$ROOT/cross_substrate/coordinates
LOG=/tmp/tierC_run
ASIDE=/tmp/tierC_aside
mkdir -p $LOG $ASIDE
cd $ROOT || exit 1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

echo "=== leg 2 waiting for runner pid ${1:-none} ==="
if [ -n "${1:-}" ]; then while kill -0 "$1" 2>/dev/null; do sleep 60; done; fi
while pgrep -f "population_fingerprint.py --run --all" >/dev/null; do sleep 60; done
echo "=== leg 2 starting $(date) ==="

gate () {  # gate <stem> <restore-from-aside?>
  if $PY cross_substrate/verify_brody_repair.py "$1" --baseline "$BASE" > "$LOG/$1.gate" 2>&1; then
    grep -E "^GATE|median repaired|outside \[0,1\]|repaired railed" "$LOG/$1.gate" | sed 's/^/      /'
    return 0
  fi
  echo "    !!! GATE FAILED for $1 — restoring"
  grep -E "^GATE|^rows|UNEXPECTED|differ" "$LOG/$1.gate" | head -8
  cp "$BASE/$1.jsonl" "$COORD/$1.jsonl"
  return 1
}

echo ""
echo "--- [quasiperiodic_operators] $(date +%H:%M:%S)"
$PY -m cross_substrate.quasiperiodic_operators --sweep --workers 6 > $LOG/qpo.log 2>&1
if [ $? -ne 0 ]; then
  echo "!!! qpo producer failed — restoring"; cp $BASE/quasiperiodic-operators.jsonl $COORD/
else
  gate quasiperiodic-operators
fi

echo ""
echo "--- [population_strat] $(date +%H:%M:%S)  (bank moved aside first)"
mv $COORD/population-strat.jsonl $ASIDE/population-strat.jsonl 2>/dev/null
$PY -m cross_substrate.population_strat --run --all --workers 6 > $LOG/popstrat.log 2>&1
if [ $? -ne 0 ]; then
  echo "!!! population_strat producer failed — restoring"
  cp $BASE/population-strat.jsonl $COORD/population-strat.jsonl
else
  gate population-strat
fi

echo ""
echo "=== leg 2 complete $(date) ==="

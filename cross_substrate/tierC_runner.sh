#!/usr/bin/env bash
# Tier C sequential runner: re-run each producer, gate its output, stop on failure.
#
# Sequential BY DESIGN. This box has 15GB RAM and two concurrent ports have
# already OOM-crashed one run; and a producer that fails its gate must not be
# followed by another that overwrites more of the store before anyone looks.
#
# On gate FAIL: restore that producer's files from the baseline and HALT.
# Producers are ordered cheapest-first so the gate discipline is proven before
# core-hours are spent.
set -u

ROOT=/home/combust/fmexplorer/criticality_tool
PY=/home/combust/fmexplorer/bin/python3
BASE=$HOME/fmexplorer/coordinate_baselines_2026-07-31_tierC
COORD=$ROOT/cross_substrate/coordinates
LOG=/tmp/tierC_run
mkdir -p $LOG
cd $ROOT || exit 1

export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

# name | command | space-separated output file stems
JOBS=(
  "am_reextract|-m cross_substrate.am_reextract --agg --cells all|am"
  "brocot_approximability|-m cross_substrate.brocot_approximability --run|brocot-approximability"
  "mackey_glass|-m cross_substrate.mackey_glass_run|mackey-glass"
  "lorenz_logistic|-m cross_substrate.lorenz_logistic_run|lorenz logistic"
  "dynamical_breadth|-m cross_substrate.dynamical_breadth --sweep --workers 2|dynamical-breadth"
  "sturmian|-m cross_substrate.sturmian_run|sturmian"
  "cf_discriminator|-m cross_substrate.cf_discriminator --run --workers 2|cf-discriminator"
  "fibonacci_lambda|-m cross_substrate.fibonacci_lambda_run --sweep --workers 2|fibonacci-lambda"
  "lambda_star_nconv|-m cross_substrate.lambda_star_nconv --run --workers 2|lambda-star-nconv"
  "am_confluence|-m cross_substrate.am_confluence --sweep --workers 2|am-confluence"
  "theta_class|-m cross_substrate.theta_class_correspondence --run --workers 2|am-confluence-theta fibonacci-lambda-theta"
  "liouville_nconv|-m cross_substrate.liouville_nconv --run --workers 2|liouville-nconv"
  "lambda_star_classes|-m cross_substrate.lambda_star_classes --run --workers 2|lambda-star-classes"
)

echo "=== TIER C RUNNER started $(date) ==="
for job in "${JOBS[@]}"; do
  name="${job%%|*}"; rest="${job#*|}"
  cmd="${rest%%|*}"; files="${rest##*|}"

  echo ""
  echo "--- [$name] $(date +%H:%M:%S) : $PY $cmd"
  $PY $cmd > "$LOG/$name.log" 2>&1
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "!!! [$name] PRODUCER EXITED $rc — restoring and halting"
    for f in $files; do cp "$BASE/$f.jsonl" "$COORD/$f.jsonl"; done
    echo "=== HALTED at $name (producer error) ==="
    exit 1
  fi

  ok=1
  for f in $files; do
    echo "    gate: $f"
    if ! $PY cross_substrate/verify_brody_repair.py "$f" --baseline "$BASE" \
         > "$LOG/$name.$f.gate" 2>&1; then
      ok=0
      echo "    !!! GATE FAILED for $f"
      grep -E "^GATE|^rows|UNEXPECTED|differ" "$LOG/$name.$f.gate" | head -8
    else
      grep -E "^GATE|median repaired|outside \[0,1\]" "$LOG/$name.$f.gate" | sed 's/^/      /'
    fi
  done

  if [ $ok -ne 1 ]; then
    echo "!!! [$name] restoring $files from baseline and halting"
    for f in $files; do cp "$BASE/$f.jsonl" "$COORD/$f.jsonl"; done
    echo "=== HALTED at $name (gate failure) ==="
    exit 1
  fi
  echo "    [$name] OK"
done

echo ""
echo "=== TIER C RUNNER complete $(date) ==="

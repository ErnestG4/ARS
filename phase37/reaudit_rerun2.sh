#!/usr/bin/env bash
# phase37/reaudit_rerun2.sh — Set 1 re-run #2. Re-run every port so each regenerates its coordinate file
# WITH the rate-robust local-irregularity axes (I.12_cv2 + I.13_lv, added to axes.py) — the fix for the
# CV-16 slow-rate/epoch-gap artifact. Sequential (network-safe), logged, per-port timeout, continue-on-fail.
# ibl at --workers 4 (was 8 → BrokenProcessPool crash). Auto-runs the CV2-primary summary at the end.
set -u
PY=$HOME/fmexplorer/bin/python3
CS=$HOME/fmexplorer/criticality_tool/cross_substrate
LOG=$HOME/fmexplorer/criticality_tool/phase37/reaudit_logs2
mkdir -p "$LOG"
cd "$CS" || exit 1

run_port () {
  local name="$1"; shift
  local to="$1"; shift
  echo "=== $(date +%H:%M:%S)  $name  ($*) ===" | tee -a "$LOG/_master.log"
  timeout "$to" $PY "$CS/$name.py" "$@" > "$LOG/$name.log" 2>&1
  echo "    -> exit $? ($(wc -l < "$LOG/$name.log") lines)" | tee -a "$LOG/_master.log"
}

# fast local first (validation/landscape context)
run_port ret1_port            600  --run --workers 8
run_port calibration_anchors  600  --run
run_port lorenz_logistic_run  600  --run
run_port mackey_glass_run     600  --run
run_port dynamical_breadth    900  --sweep --workers 4
# biological arc: V1 → IBL → hippocampus
run_port allen_v1_burst       7200 --run --workers 10
run_port ibl_port            12000 --run --all --workers 4    # workers 4 (8 crashed BrokenProcessPool)
run_port buzsaki_port        14400 --run --all --workers 8
run_port hc3_port            14400 --run --workers 6
run_port dual_region_port    14400 --run --workers 8
run_port allen_hpf           10800 --run --all --workers 10

echo "=== $(date +%H:%M:%S)  ALL PORTS DONE ===" | tee -a "$LOG/_master.log"
$PY $HOME/fmexplorer/criticality_tool/phase37/reaudit_summary.py > "$LOG/_summary.log" 2>&1
echo "summary -> $LOG/_summary.log" | tee -a "$LOG/_master.log"

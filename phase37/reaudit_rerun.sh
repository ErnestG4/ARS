#!/usr/bin/env bash
# phase37/reaudit_rerun.sh — Set 1 launcher. Re-run substrate ports sequentially so each regenerates its
# coordinate file WITH the new clustering axes (I.10_cv + I.11_mass03, added to cross_substrate/axes.py).
# Sequential (not parallel) to avoid network contention on the streaming substrates ([[parallel_curl_corruption]]).
# Each port: logged, per-port timeout, continue-on-failure. Coordinates backed up to
# coordinates_backup_pre_twoaxis.tgz (restore if any port truncates its file on failure).
set -u
PY=/home/combust/fmexplorer/bin/python3
CS=/home/combust/fmexplorer/criticality_tool/cross_substrate
LOG=/home/combust/fmexplorer/criticality_tool/phase37/reaudit_logs
mkdir -p "$LOG"
cd "$CS" || exit 1

# port  args  timeout(s)   — ordered: fast/local landscape first, then the bio arc (retina done already)
run_port () {
  local name="$1"; shift
  local to="$1"; shift
  echo "=== $(date +%H:%M:%S)  $name  ($*) ===" | tee -a "$LOG/_master.log"
  timeout "$to" $PY "$CS/$name.py" "$@" > "$LOG/$name.log" 2>&1
  local rc=$?
  echo "    -> exit $rc  ($(wc -l < "$LOG/$name.log") log lines)" | tee -a "$LOG/_master.log"
}

# --- fast local landscape (calibrators + dynamical + arithmetic) ---
run_port calibration_anchors  600  --run
run_port lorenz_logistic_run  600  --run
run_port mackey_glass_run     600  --run
run_port dynamical_breadth    900  --sweep   # NB: takes --sweep/--probe, not --run (fixed post-launch)

# --- the biological arc: V1 → IBL → hippocampus (streaming/local-cache; heavier) ---
run_port allen_v1_burst       7200 --run --workers 10        # V1 burst+OSI (Allen, local cache)
run_port ibl_port            10800 --run --all --workers 8   # IBL (DANDI stream)
run_port buzsaki_port        14400 --run --all --workers 8   # CA1 (CRCNS/DANDI stream)
run_port hc3_port            14400 --run --workers 6         # EC/CA3/CA1/DG (CRCNS stream)
run_port dual_region_port    14400 --run --workers 8         # MEC (DANDI stream)
run_port allen_hpf           10800 --run --all --workers 10  # Allen hippocampal formation (local cache)

echo "=== $(date +%H:%M:%S)  ALL PORTS DONE ===" | tee -a "$LOG/_master.log"
# auto-run the two-axis summary once ports finish
$PY /home/combust/fmexplorer/criticality_tool/phase37/reaudit_summary.py > "$LOG/_summary.log" 2>&1
echo "summary written to $LOG/_summary.log" | tee -a "$LOG/_master.log"

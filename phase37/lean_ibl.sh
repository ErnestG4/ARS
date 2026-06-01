#!/usr/bin/env bash
# Lean ibl re-run: non-visual sub-*.nwb only (skips the 2+GB vis-* sessions whose >1M-event pooled reads
# wedged the wave at 30+ min/session and aren't CV2-relevant). Recovers ibl per-cell CV2. Run AFTER the
# hippocampal arc + summary complete, then re-run reaudit_summary.py to fold ibl back in.
PY=/home/combust/fmexplorer/bin/python3
cd /home/combust/fmexplorer/criticality_tool/cross_substrate
timeout 5400 "$PY" ibl_port.py --run --workers 4 --glob "/home/combust/fmexplorer/ibl_cache/sub-*.nwb" \
  > /home/combust/fmexplorer/criticality_tool/phase37/reaudit_logs2/ibl_lean.log 2>&1
echo "lean ibl exit $?"
"$PY" /home/combust/fmexplorer/criticality_tool/phase37/reaudit_summary.py \
  > /home/combust/fmexplorer/criticality_tool/phase37/reaudit_logs2/_summary_final.log 2>&1
echo "summary re-run with ibl folded in -> _summary_final.log"

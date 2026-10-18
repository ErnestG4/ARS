#!/usr/bin/env bash
# Round 53 pre-seal record: each F4/F5 stand-in (CUE_1000 spacings from char) placed at its file's geometry with exact θ,
# written in the Platt format (synth), then decoded by the read's path and compared with its own sequence (pipeline).
# One process per file, nice 10. Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_followup_standins_spot.sh
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
OUT=results/followup_dryrun_synth
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) replications: stand-ins synth + pipeline identity, 7 procs, nice 10" >> ~/claude-work.log
ls "$OUT"/*.npy | xargs -n1 basename | sed 's/\.npy$//' | xargs -P 7 -I{} sh -c 'nice -n 10 '"$PY"' followup_sealread.py synth '"$OUT"' {} > '"$OUT"'/logs/{}.log 2>&1 && nice -n 10 '"$PY"' followup_sealread.py pipeline '"$OUT"' {} >> '"$OUT"'/logs/{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/{}.exit'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] route (a) replications: stand-ins: done" >> ~/claude-work.log

#!/usr/bin/env bash
# Route (a) Phase 2 bins check (descriptive; seen data only; no F3 file). 3 bins at a time on char's 4 cores.
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/tmp/claude/venv/bin/python
OUT=results/ph2bins
mkdir -p $OUT
echo "$(date -Iseconds) [CC specarith] route (a) Phase 2 bins check P1-P6 (descriptive, 3 procs)" >> ~/claude-work.log
printf '%s\n' P1 P2 P3 P4 P5 P6 | xargs -P 3 -I{} sh -c "f=\$(PY=$PY nice -n 10 $PY -c 'import route_a_ph2bins as M; print(M.PLATT[\"{}\"][0])'); nice -n 10 $PY route_a_ph2bins.py {} ../ph2/data/platt/\$f $OUT/{}.json > $OUT/{}.log 2>&1; echo exit=\$? > $OUT/{}.exit"
date -Iseconds > $OUT/ALL_DONE
echo "$(date -Iseconds) [CC specarith] route (a) Phase 2 bins check: done" >> ~/claude-work.log

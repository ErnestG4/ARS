#!/usr/bin/env bash
# Route (a) READ of F3 (round 47 order: seal 563cf804 / tag route-a-seal → OpenTimestamps stamp 485b7d20 → this).
# Under the pinned interpreter (spot, ph6c): read run1, then read run2 in a separate process, then compare (bit-identical
# or VOID; only compare prints the result). Every refusal in route_a_sealread.read() applies before any decode.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_route_a_read_spot.sh
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=results/read
mkdir -p "$O"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) F3 read: run1, run2, compare" >> ~/claude-work.log
for r in run1 run2; do
  date -Is > "$O/$r.start"
  nice -n 10 $PY route_a_sealread.py read $r > "$O/$r.log" 2>&1; echo "exit=$?" > "$O/$r.exit"
done
nice -n 10 $PY route_a_sealread.py compare > "$O/compare.log" 2>&1; echo "exit=$?" > "$O/compare.exit"
echo "$(date -Is) [CC specarith] route (a) F3 read: done" >> ~/claude-work.log

#!/usr/bin/env bash
# R₂ pre-read, after G0b: waits for results/g0b/ALL_DONE (a file, not a process name), then red-path reachability, the
# dry run (5 bins + the (achieved) witness in parallel, then merge). Each step writes its own outputs; nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph2r2/run_post_g0b_spot.sh
set -u
D=~/tmp/claude/specarith/ph2r2
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
G=results/g0b
OUT=results/post
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
while [ ! -f "$G/ALL_DONE" ]; do sleep 60; done
if ! grep -q "exit=0" "$G/exits/merge.txt"; then echo "G0b merge failed" > "$OUT/ABORTED"; exit 1; fi
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ph2r2 post-G0b: red paths + dry run, nice 10" >> ~/claude-work.log
nice -n 10 $PY redpaths_r2.py "$G" "$OUT" > "$OUT/logs/redpaths.log" 2>&1; echo "exit=$?" > "$OUT/exits/redpaths.txt"
printf '%s\n' R1 R2 R3 R4 R5 witness | xargs -P 6 -L 1 sh -c 'nice -n 10 '"$PY"' dryrun_r2.py '"$G"' '"$OUT"' "$0" > '"$OUT"'/logs/dry_$0.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/dry_$0.txt'
nice -n 10 $PY dryrun_r2.py "$G" "$OUT" merge > "$OUT/logs/dry_merge.log" 2>&1; echo "exit=$?" > "$OUT/exits/dry_merge.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph2r2 post-G0b: done" >> ~/claude-work.log

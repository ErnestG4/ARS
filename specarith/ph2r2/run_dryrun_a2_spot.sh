#!/usr/bin/env bash
# R₂ dry run under amendment A2 (achieved rule judges precision only) + A3 (drift-removed A1 series): 5 bins + the
# four-point witness in parallel, then merge. Red paths are unaffected by A2 and stay in results/post. nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph2r2/run_dryrun_a2_spot.sh
set -u
D=~/tmp/claude/specarith/ph2r2
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
G=results/g0b
OUT=results/dry_a2
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE" "$OUT"/exits/*.txt
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ph2r2 dry run A2/A3: 5 bins + witness, nice 10" >> ~/claude-work.log
printf '%s\n' R1 R2 R3 R4 R5 witness | xargs -P 6 -L 1 sh -c 'nice -n 10 '"$PY"' dryrun_r2.py '"$G"' '"$OUT"' "$0" > '"$OUT"'/logs/dry_$0.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/dry_$0.txt'
nice -n 10 $PY dryrun_r2.py "$G" "$OUT" merge > "$OUT/logs/dry_merge.log" 2>&1; echo "exit=$?" > "$OUT/exits/dry_merge.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph2r2 dry run A2/A3: done" >> ~/claude-work.log

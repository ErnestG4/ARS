#!/usr/bin/env bash
# CONTINGENCY (not in the sealed scope): chi_-4 zeros on [20000, 40000], so Will can choose G2's height in the morning
# (review B2: with the corrected band, log 9 enters G2's resolvable set only near T ~ 3-4e4). Pure data acquisition.
# 40 chunks of width 500 at realprecision 38 + one realprecision-57 check window [39900, 40000]; 20 in parallel, nice 10.
set -u
D=~/tmp/claude/specarith
OUT=$D/chi4_ext
PY=~/miniforge3/envs/specarith/bin/python
mkdir -p "$OUT"
rm -f "$OUT/ALL_DONE"
{ for a in $(seq 20000 500 39500); do echo "$a $((a + 500)) 38"; done; echo "39900 40000 57"; } > "$OUT/jobs.txt"
echo "$(date -Is) [CC specarith] chi4 zeros CONTINGENCY [20000,40000]: $(wc -l < "$OUT/jobs.txt") jobs, nice 10" >> ~/claude-work.log
xargs -P 20 -L 1 sh -c 'nice -n 10 '"$PY"' -I '"$D"'/chi4_zeros.py chunk "$0" "$1" '"$OUT"' "$2" > '"$OUT"'/log_$0_$1_p$2.txt 2>&1; echo "$0 $1 $2 exit=$?" >> '"$OUT"'/exits.txt' < "$OUT/jobs.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] chi4 contingency: all jobs exited" >> ~/claude-work.log

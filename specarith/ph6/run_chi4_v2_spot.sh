#!/usr/bin/env bash
# chi_-4 zeros, recipe v2 (divz = 64; see chi4_zeros_v2.py for why). Usage inside tmux `claude`:
#   bash ~/tmp/claude/specarith/run_chi4_v2_spot.sh T_MAX N_CHUNKS NPAR OUTNAME
# Writes ~/tmp/claude/specarith/OUTNAME/: chunks at realprecision 38 + the p57 check windows [0,1000] and [T_MAX-100,T_MAX].
set -u
T_MAX=$1; N=$2; NPAR=$3; NAME=$4
D=~/tmp/claude/specarith
OUT=$D/$NAME
PY=~/miniforge3/envs/specarith/bin/python
mkdir -p "$OUT"
rm -f "$OUT/ALL_DONE" "$OUT/exits.txt"
{ $PY "$D/chi4_zeros_v2.py" plan "$T_MAX" "$N" | awk '{print $1, $2, 38, 64}'
  echo "0 1000 57 64"; echo "$((T_MAX - 100)) $T_MAX 57 64"; } > "$OUT/jobs.txt"
# longest jobs first (low chunks are widest; p57 windows last)
sort -k3,3n -k1,1n "$OUT/jobs.txt" -o "$OUT/jobs.txt"
echo "$(date -Is) [CC specarith] chi4 v2 (divz 64) T_MAX=$T_MAX: $(wc -l < "$OUT/jobs.txt") jobs, $NPAR parallel, nice 10" >> ~/claude-work.log
xargs -P "$NPAR" -L 1 sh -c 'nice -n 10 '"$PY"' '"$D"'/chi4_zeros_v2.py chunk "$0" "$1" '"$OUT"' "$2" "$3" > '"$OUT"'/log_$0_$1_p$2.txt 2>&1; echo "$0 $1 $2 exit=$?" >> '"$OUT"'/exits.txt' < "$OUT/jobs.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] chi4 v2 $NAME: all jobs exited" >> ~/claude-work.log

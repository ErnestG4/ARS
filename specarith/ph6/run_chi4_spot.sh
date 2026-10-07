#!/usr/bin/env bash
# Launch the chi_-4 zero chunks (seal §9.1) on spot: 20 chunks at realprecision 38 + 2 check windows at 57.
# Run inside tmux session `claude`:  bash ~/tmp/claude/specarith/run_chi4_spot.sh
# Each job writes its own files (no shared paths); a DONE marker is written when all have exited.
set -u
D=~/tmp/claude/specarith
OUT=$D/chi4
PY=~/miniforge3/envs/specarith/bin/python
mkdir -p "$OUT"
rm -f "$OUT/ALL_DONE"
{
  $PY -I "$D/chi4_zeros.py" plan | awk '{print $1, $2, 38}'
  echo "0 1000 57"
  echo "19900 20000 57"
} > "$OUT/jobs.txt"
echo "$(date -Is) [CC specarith] chi4 zeros: $(wc -l < "$OUT/jobs.txt") PARI jobs, nice 10, out $OUT" >> ~/claude-work.log
xargs -P 22 -L 1 sh -c 'nice -n 10 '"$PY"' -I '"$D"'/chi4_zeros.py chunk "$0" "$1" '"$OUT"' "$2" > '"$OUT"'/log_$0_$1_p$2.txt 2>&1; echo "$0 $1 $2 exit=$?" >> '"$OUT"'/exits.txt' < "$OUT/jobs.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] chi4 zeros: all jobs exited" >> ~/claude-work.log

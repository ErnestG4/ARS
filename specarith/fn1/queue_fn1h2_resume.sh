#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1-h2 archive, second half after the midpoint stop (Will, 2026-11-04: relaunch approved at 24 tasks; cost check
# rebased to the approved price). Preconditions checked here: no generator process, no *.part* files, every existing
# segment listed in done.txt. The stop record STOPPED is kept as STOPPED_mid_<time>. The second half's chunk files
# (pq/b2_*, written at bulk time) list only the segments missing after the first half; the chunk runner also skips any
# segment file that exists. b2 chunks split in two: first 45 → q3 check (price rule) → last 45 → final check +
# manifests + count report. specarith-filler, pq-fill, unique job names.
#   bash queue_fn1h2_resume.sh
set -euo pipefail
ROOT=/mnt/data/fn1h2; CODE=~/tmp/claude/specarith/fn1; Q=$ROOT/pq; PQ=~/.local/bin/pueue
mountpoint -q /mnt/data || { echo "REFUSED: /mnt/data is not a mount point"; exit 2; }
[ ! -e $Q/resume_ids.txt ] || { echo "REFUSED: already resumed"; exit 1; }
[ -z "$(find $ROOT -name '*.part*' | head -1)" ] || { echo "REFUSED: partial files present"; exit 1; }
if ps -u "$USER" -o args | grep -q "[f]n1h2_archive.py task"; then echo "REFUSED: a generator task is running"; exit 1; fi
[ "$(ls $ROOT/archive_2e10_D*/seg_*.npy | wc -l)" = "$(wc -l < $ROOT/logs/done.txt)" ] || { echo "REFUSED: files != done.txt"; exit 1; }
[ -e $ROOT/STOPPED ] && mv $ROOT/STOPPED $ROOT/STOPPED_mid_$(date +%Y%m%dT%H%M%S)
add() { $PQ add -p -g specarith-filler -w $CODE "$@"; }
files=($Q/b2_*); n=${#files[@]}; h=$((n / 2))
A=""; for f in "${files[@]:0:$h}"; do b=$(basename $f)
  A="$A $(add -l specarith:fn1h2-arch-r-$b -- pq-fill --no-viz archive-generation fn1h2-arch-r-$b 2 bash $CODE/run_fn1h2_chunk.sh $f)"; done
Q3=$(add -l specarith:fn1h2-arch-q3check --after $A -- pq-fill --no-viz archive-check fn1h2-arch-q3check 2 bash $CODE/run_fn1h2_check.sh q3)
B=""; for f in "${files[@]:$h}"; do b=$(basename $f)
  B="$B $(add -l specarith:fn1h2-arch-r-$b --after $Q3 -- pq-fill --no-viz archive-generation fn1h2-arch-r-$b 2 bash $CODE/run_fn1h2_chunk.sh $f)"; done
FIN=$(add -l specarith:fn1h2-arch-final2 --after $B -- pq-fill --no-viz archive-manifest fn1h2-arch-final2 16 bash $CODE/run_fn1h2_check.sh final)
{ echo "a:$A"; echo "q3 $Q3"; echo "b:$B"; echo "final $FIN"; } > $Q/resume_ids.txt
echo "resumed: chunks $n ($h + $((n - h))), q3 $Q3, final $FIN"
echo "$(date -Is) [CC specarith] fn1h2 archive second half relaunched (Will 11-04; price-based cost rule): $n chunks, q3 $Q3, final $FIN" >> ~/claude-work.log

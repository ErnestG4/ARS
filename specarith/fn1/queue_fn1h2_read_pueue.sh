#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1-h2 sealed double read: read 1, read 2 (--after read 1), cmp (--after read 2), in specarith-scored (parallel 1)
# through pq-scored, labels specarith:fn1h2-read-*. Run once, after the stamp's Bitcoin attestation is verified on two
# explorers and the VERIFY record is copied to the read dir.
set -euo pipefail
CODE=~/tmp/claude/specarith/fn1; O=$CODE/h2_read; PQ=~/.local/bin/pueue
[ -s $O/FN1H2_SEAL_STAMP_VERIFY.json ] || { echo "REFUSED: no VERIFY record in $O"; exit 1; }
[ ! -e $O/ids.txt ] || { echo "REFUSED: already queued ($O/ids.txt)"; exit 1; }
$PQ parallel -g specarith-scored 1
add() { $PQ add -p -g specarith-scored -o 10 -w $CODE "$@"; }
R1=$(add -l specarith:fn1h2-read-1 -- pq-scored --no-viz sealed-read fn1h2-read-1 40 bash $CODE/run_fn1h2_read_one.sh 1)
R2=$(add -l specarith:fn1h2-read-2 --after $R1 -- pq-scored --no-viz sealed-read fn1h2-read-2 40 bash $CODE/run_fn1h2_read_one.sh 2)
CM=$(add -l specarith:fn1h2-read-cmp --after $R2 -- bash $CODE/run_fn1h2_read_cmp.sh)
echo "read1 $R1 read2 $R2 cmp $CM" | tee $O/ids.txt
echo "$(date -Is) [CC specarith] fn1h2 sealed double read queued: pueue $R1, $R2, cmp $CM (specarith-scored)" >> ~/claude-work.log

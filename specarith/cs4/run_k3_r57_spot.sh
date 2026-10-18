#!/usr/bin/env bash
# Corrected (B) L rule: followup_k3 terms at L = 4, 5, 6 at the F3 heights (K3_LS), 30 jobs, 30 procs, nice 10.
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
OUT=results/followup_k3_r57
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 K3_LS=4.0,5.0,6.0
echo "$(date -Is) [CC specarith] corrected (B) L rule: k3 terms at L = 4, 5, 6 (30 procs)" >> ~/claude-work.log
seq 0 29 | xargs -P 30 -I{} sh -c 'nice -n 10 '"$PY"' followup_k3.py run {} 30 '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/c{}.exit'
nice -n 10 $PY followup_k3.py merge $OUT > $OUT/merge.log 2>&1; echo "exit=$?" > $OUT/merge.exit
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] corrected (B) L rule: k3 terms: done" >> ~/claude-work.log

#!/usr/bin/env bash
# Corrected (B) (round 58): CUE_N known-answer slope at L* under round 53's rule (b2_cuen.py). STAGE = pilot (400
# batches per N) or run (main, from plan.json; EXTEND = B2CUEN_EXTEND for the declared 25% extensions). NCH procs,
# nice 10. Restartable. Data-free.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_b2_cuen_spot.sh STAGE [NCH] [EXTEND]
set -u
STAGE=$1
NCH=${2:-48}
export B2CUEN_EXTEND=${3:-0}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
OUT=results/b2_cuen
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE_$STAGE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] corrected (B) CUE_N slope $STAGE (extend $B2CUEN_EXTEND): $NCH procs, nice 10" >> ~/claude-work.log
seq 0 $((NCH - 1)) | xargs -P "$NCH" -I{} sh -c 'nice -n 10 '"$PY"' b2_cuen.py '"$STAGE"' {} '"$NCH"' '"$OUT"' > '"$OUT"'/logs/'"$STAGE"'_c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/'"$STAGE"'_c{}.exit'
date -Is > "$OUT/ALL_DONE_$STAGE"
echo "$(date -Is) [CC specarith] corrected (B) CUE_N slope $STAGE: done" >> ~/claude-work.log

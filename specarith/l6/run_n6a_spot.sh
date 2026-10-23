#!/usr/bin/env bash
# n = 6 stage (a) on spot (N6_STAGE_A.md): check, then C(kΔ) in NCHUNK chunks, then the summary. nice 10, one BLAS
# thread each. Run inside tmux `claude`:  bash ~/tmp/claude/specarith/l6/run_n6a_spot.sh [NCHUNK]
set -u
NCHUNK=${1:-28}
cd ~/tmp/claude/specarith/l6 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=results/n6a; LG=$O/logs
mkdir -p $O $LG
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY O LG NCHUNK
echo "$(date -Is) [CC specarith] n6 stage (a): exact U(N) W_B ($NCHUNK chunks)" >> ~/claude-work.log
nice -n 10 $PY n6a_trace.py check $O/N6A_CHECK.json > $O/check.log 2>&1; echo "exit=$?" > $O/check.exit
grep -q "exit=0" $O/check.exit || { echo "check not passed" > $O/STOPPED; exit 1; }
seq 0 $((NCHUNK - 1)) | xargs -P "$NCHUNK" -I{} sh -c 'j=$(printf %03d {}); [ -f "$O/C_$j.npz" ] || nice -n 10 $PY n6a_trace.py chunk {} $NCHUNK $O > $LG/chunk_$j.log 2>&1; echo "exit=$?" > $LG/chunk_$j.exit'
grep -L "exit=0" $LG/*.exit > $O/failures.txt
[ -s $O/failures.txt ] && { echo "chunk failures" > $O/STOPPED; exit 1; }
nice -n 10 $PY n6a_trace.py summary $O > $O/summary.log 2>&1; echo "exit=$?" > $O/summary.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] n6 stage (a): done" >> ~/claude-work.log

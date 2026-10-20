#!/usr/bin/env bash
# L6 long baseline, step 0 (L6_BASELINE_DESIGN.md §2, round 66): cbe.py red paths V1–V4 (its own selftest, CPU), V5
# (N = 10⁴ against dense eigvals, 8 BLAS threads), V6/V7 (N = 10⁵ certification, red paths, residual, timing). Three
# processes in parallel, nice 10. Run inside tmux `claude`:  bash ~/tmp/claude/specarith/l6/run_l6_step0_spot.sh
set -u
cd ~/tmp/claude/specarith/l6 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
D=results/step0
mkdir -p $D
rm -f $D/ALL_DONE
echo "$(date -Is) [CC specarith] L6 step 0 (cbe red paths V1-V7)" >> ~/claude-work.log
( OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 10 $PY l6_base.py step0 selftest $D/selftest.json > $D/selftest.log 2>&1; echo "exit=$?" > $D/selftest.exit ) &
( OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 nice -n 10 $PY l6_base.py step0 v5 $D/v5.json > $D/v5.log 2>&1; echo "exit=$?" > $D/v5.exit ) &
( OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 10 $PY l6_base.py step0 v67 $D/v67.json > $D/v67.log 2>&1; echo "exit=$?" > $D/v67.exit ) &
wait
date -Is > $D/ALL_DONE
echo "$(date -Is) [CC specarith] L6 step 0: done" >> ~/claude-work.log

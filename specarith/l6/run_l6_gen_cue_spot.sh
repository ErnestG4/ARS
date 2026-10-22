#!/usr/bin/env bash
# L6 restart (design §12): the 50 CUE sequences with the active-set, checkpointed solver, started while
# step0 activeset_full is still running; then the full pipeline (run_l6_base_spot.sh), whose step-0 gate requires
# activeset_full's exit 0 before gate 1 or any statistic. If activeset_full fails, these sequences are not used.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/l6/run_l6_gen_cue_spot.sh [NPROC] [NPROC_PIPELINE]
set -u
NPROC=${1:-25}
NPROC2=${2:-28}
cd ~/tmp/claude/specarith/l6 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
GEN=results/base/gen; LG=results/base/logs
mkdir -p $GEN $LG
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY GEN LG
echo "$(date -Is) [CC specarith] L6 §12 restart: 50 CUE, active-set + checkpoints ($NPROC procs)" >> ~/claude-work.log
seq 0 49 | xargs -P "$NPROC" -I{} sh -c 'r=$(printf %03d {}); [ -f "$GEN/cue_$r.npy" ] || nice -n 10 $PY l6_base.py gen cue {} $GEN > $LG/gen_cue_{}.log 2>&1; echo "exit=$?" > $LG/gen_cue_{}.exit'
echo "$(date -Is) [CC specarith] L6 §12 restart: CUE generation pass ended; waiting for step-0 activeset_full" >> ~/claude-work.log
while [ ! -f results/step0/activeset_full.exit ]; do sleep 60; done
exec bash run_l6_base_spot.sh "$NPROC2"

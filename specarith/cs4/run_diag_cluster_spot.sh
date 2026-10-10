#!/usr/bin/env bash
# diag_cluster.py on spot: 5 cases at ℓ = 16.4972 (pairs already done), 5 procs, nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_diag_cluster_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/diag_cluster
mkdir -p "$OUT"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] diag_cluster: 5 procs, 50-digit ref at the clustered grid corner, nice 10" >> ~/claude-work.log
seq 0 4 | xargs -P 5 -I{} sh -c 'nice -n 10 '"$PY"' diag_cluster.py 16.4972 results/gs_zeta {} '"$OUT"' > '"$OUT"'/c{}.log 2>&1; echo "exit=$?" >> '"$OUT"'/c{}.log'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] diag_cluster: done" >> ~/claude-work.log

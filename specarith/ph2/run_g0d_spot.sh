#!/usr/bin/env bash
# Pre-read G0d on spot (seal §5 + A1): every (bin, N) config of `preread.py geometry`, R=200 reps in chunks of 25
# (`preread.py g0d_jobs`; the first 100 reps of each config carry the moving-block bootstrap, B=200 per block length),
# then `preread.py g0d_merge`. One process per chunk, own output file; nice 10, 1 thread each, 36 at a time
# (bootstrap chunks first). Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph2/run_g0d_spot.sh
set -u
D=~/tmp/claude/specarith/ph2
PY=~/miniforge3/envs/specarith/bin/python
cd "$D"
mkdir -p results/g0d/logs results/g0d/exits
rm -f results/g0d/ALL_DONE
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
$PY preread.py g0d_jobs | sort -k3,3n -s > results/g0d/jobs.txt
echo "$(date -Is) [CC specarith] ph2 G0d chunked: $(wc -l < results/g0d/jobs.txt) jobs, 36 parallel, nice 10" >> ~/claude-work.log
xargs -P 36 -L 1 sh -c 'nice -n 10 '"$PY"' preread.py g0d "$0" "$1" "$2" "$3" 100 200 > results/g0d/logs/$0_N$1_r$2.log 2>&1; echo "exit=$?" > results/g0d/exits/$0_N$1_r$2.txt' < results/g0d/jobs.txt
nice -n 10 $PY preread.py g0d_merge > results/g0d/logs/merge.log 2>&1; echo "merge exit=$?" > results/g0d/exits/merge.txt
date -Is > results/g0d/ALL_DONE
echo "$(date -Is) [CC specarith] ph2 G0d chunked: all jobs exited, merged" >> ~/claude-work.log

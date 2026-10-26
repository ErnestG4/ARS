#!/usr/bin/env bash
# RQ1 round 88 checks on spot (synthetic data and primes outside both archives; nothing is read from the archives):
#   regen  (version drift): 12 ℤ[√2] segments regenerated, sha256 against the manifest
#   precision: float θ against mpmath (50 digits) and unit shifts, primes in [1.01e11, 1.01e11 + 2e6)
#   readcheck: READ_ESTIMATOR_CHECK rerun in the pinned ph6c env
#   memprobe: the read's peak RSS at the 1e11 matched N (synthetic: unsorted θ, in-place sort, one var_stream pass)
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/rq1/run_rq1_r88_checks_spot.sh
set -u
cd ~/tmp/claude/specarith/rq1 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=r88; mkdir -p $O/regen
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PY O
echo "$(date -Is) [CC specarith] rq1 r88 checks: start" >> ~/claude-work.log
$PY rq1_regen_check.py list | xargs -P 12 -L 1 sh -c 'nice -n 10 $PY rq1_regen_check.py task $0 $O/regen >> $O/regen.log 2>&1 || echo "$0" >> $O/regen_failed.txt' &
{ nice -n 10 $PY rq1_precision.py $O/PRECISION.json > $O/precision.log 2>&1; echo "exit=$?" >> $O/precision.log; } &
{ nice -n 10 $PY rq1_read_check.py $O/READ_ESTIMATOR_CHECK.json > $O/readcheck.log 2>&1; echo "exit=$?" >> $O/readcheck.log; } &
wait
nice -n 10 $PY rq1_regen_check.py check $O/regen archive/MANIFEST.json $O/REGEN_CHECK.json > $O/regen_check.log 2>&1; echo "exit=$?" >> $O/regen_check.log
systemd-run --user --scope -q -p MemoryMax=40G -p MemorySwapMax=0 nice -n 10 $PY - > $O/memprobe.log 2>&1 <<'PY'
import resource, time, numpy as np, rq1_read as Q
N = 2 * 2059026114
t = time.time()
th = np.random.default_rng(0).random(N)
th.sort()
v = Q.var_stream(th, 21213)
print(dict(N=N, peak_rss_GB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 20, wall_s=time.time() - t,
           R=v / (N / 21213)))
PY
echo "exit=$?" >> $O/memprobe.log
date -Is > $O/CHECKS_DONE
echo "$(date -Is) [CC specarith] rq1 r88 checks: done" >> ~/claude-work.log

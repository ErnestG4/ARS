#!/usr/bin/env bash
# RQ1 round 89 B2 rule confirmation on spot (rq1_witness.py; synthetic only, nothing is read from the archives).
# Runs only if witness/SELECTION.json (rq1_witness.py select, on the round-88 replicates) has a chosen k.
# 200 fresh tasks (seed base 8889; the same sets, N and planted parameters as round 88), NPROC at a time, each under
# a per-process memory cap; then rq1_witness.py confirm → witness_confirm/CONFIRM.json.
# Cost model as the round-88 witness: 370 (null) / 350 (planted) local core-s per task × 2.3 → about 46 spot core-h
# (the round-88 first wave measured 0.597×). First-wave and mid-run checks as there (stop at > 1.25×).
# Copy the round-89 rq1_read.py / rq1_witness.py to spot only after the round-88 witness has finished (its tasks
# import both modules when they start).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/rq1/run_rq1_witness_confirm_spot.sh [NPROC]
set -u
NPROC=${1:-3}
cd ~/tmp/claude/specarith/rq1 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=witness_confirm; LG=$O/logs; SEL=witness/SELECTION.json
$PY -c "import json, sys; sys.exit(0 if json.load(open('$SEL'))['chosen_k'] is not None else 3)" || { echo "no k selected (B2 UNPOWERED): nothing to confirm"; exit 3; }
mkdir -p $O $LG
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PY O LG
RUN='systemd-run --user --scope -q -p MemoryMax=36G -p MemorySwapMax=0 nice -n 10 $PY rq1_witness.py task $0 $1 $O 8889 >> $LG/tasks.log 2>&1 || echo "$0 $1" >> $LG/failed.txt'
echo "$(date -Is) [CC specarith] rq1 r89 confirmation: 200 tasks ($NPROC procs, 36G cap each)" >> ~/claude-work.log
$PY rq1_witness.py jobs > $O/jobs.txt
ratio() {
$PY - "$O" "$1" <<'PY'
import glob, json, os, sys
o, n = sys.argv[1], int(sys.argv[2])
model = {"null": 370 * 2.3, "planted": 350 * 2.3}
rs = [json.load(open(p)) for p in sorted(glob.glob(o + "/*_[0-9][0-9][0-9].json"), key=os.path.getmtime)[:n]]
r = sum(x["cpu_s"] for x in rs) / sum(model[x["arm"]] for x in rs)
print(f"{len(rs)} tasks, measured cpu/model = {r:.3f}")
print("OK" if r <= 1.25 else "EXCEEDS")
PY
}
head -n "$NPROC" $O/jobs.txt | xargs -P "$NPROC" -L 1 sh -c "$RUN"
ratio "$NPROC" > $O/first_wave.txt
if grep -q EXCEEDS $O/first_wave.txt || [ -s $LG/failed.txt ]; then
  echo "first wave over the cost model by > 25% or a task failed" > $O/STOPPED; exit 1
fi
sed -n "$((NPROC + 1)),100p" $O/jobs.txt | xargs -P "$NPROC" -L 1 sh -c "$RUN"
ratio 100 > $O/mid_run.txt
if grep -q EXCEEDS $O/mid_run.txt || [ -s $LG/failed.txt ]; then
  echo "mid-run over the cost model by > 25% or a task failed" > $O/STOPPED; exit 1
fi
tail -n +101 $O/jobs.txt | xargs -P "$NPROC" -L 1 sh -c "$RUN"
[ -s $LG/failed.txt ] && { echo "task failures" > $O/STOPPED; exit 1; }
nice -n 10 $PY rq1_witness.py confirm $O $SEL $O/CONFIRM.json > $O/confirm.log 2>&1; echo "exit=$?" > $O/confirm.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] rq1 r89 confirmation: done" >> ~/claude-work.log

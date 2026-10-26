#!/usr/bin/env bash
# RQ1 round 88 B2 witness on spot (rq1_witness.py; synthetic only, nothing is read from the archives).
# 200 tasks (null and planted, 100 each, interleaved), NPROC at a time, each under a per-process memory cap.
# Cost model (N6-2_PLAN.md §10 form): local core-s per task ≈ 370 (null) / 350 (planted), measured at the 1e10 matched
# size and scaled by N; spot factor 2.3 (the archive class; this class is uncalibrated, so the first wave calibrates it).
# First-wave rule (round 84): if the first NPROC tasks' CPU exceeds the model by more than 25%, STOPPED is written
# and nothing more runs. Mid-run check (round 88 note): the same ratio after 100 tasks (mid_run.txt), same stop.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/rq1/run_rq1_witness_spot.sh [NPROC]
set -u
NPROC=${1:-3}
cd ~/tmp/claude/specarith/rq1 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=witness; LG=$O/logs
mkdir -p $O $LG
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PY O LG
RUN='systemd-run --user --scope -q -p MemoryMax=36G -p MemorySwapMax=0 nice -n 10 $PY rq1_witness.py task $0 $1 $O >> $LG/tasks.log 2>&1 || echo "$0 $1" >> $LG/failed.txt'
echo "$(date -Is) [CC specarith] rq1 r88 witness: 200 tasks ($NPROC procs, 36G cap each)" >> ~/claude-work.log
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
nice -n 10 $PY rq1_witness.py summary $O $O/WITNESS.json > $O/summary.log 2>&1; echo "exit=$?" > $O/summary.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] rq1 r88 witness: done" >> ~/claude-work.log

#!/usr/bin/env bash
# RQ1 (round 86) on spot: the Z[i] angle archive to X = 1.01e11 (1,010 segments of 1e8; the extra 1e9 so N can be matched to Z[sqrt2] at 1e11). First-wave rule (round 84): the
# first NPROC tasks run alone; if their mean wall time exceeds the cost model by more than 25%, STOPPED is written and
# nothing more runs. Then the rest, then the manifest (hashes + integrity; no statistic).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/rq1/run_rq1_archive_zi_spot.sh [NPROC]
set -u
NPROC=${1:-28}
cd ~/tmp/claude/specarith/rq1 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=archive_zi; LG=$O/logs
mkdir -p $O $LG
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 PY O LG
echo "$(date -Is) [CC specarith] rq1 ZI archive: 1010 segments ($NPROC procs)" >> ~/claude-work.log
$PY rq1_archive.py jobs 1.01e11 zi > $O/jobs.txt
head -n "$NPROC" $O/jobs.txt | xargs -P "$NPROC" -L 1 sh -c 'nice -n 10 $PY rq1_archive.py task $0 $O zi >> $LG/tasks.log 2>&1 || echo "$0" >> $LG/failed.txt'
$PY - "$O" "$NPROC" > $O/first_wave.txt <<'PY'
import sys
o, n = sys.argv[1], int(sys.argv[2])
pred = {int(l.split()[0]): float(l.split()[1]) for l in open(o + "/jobs.txt")}
meas = {}
for l in open(o + "/logs/tasks.log"):
    k, rows, s = l.split()
    meas[int(k)] = float(s)
ks = sorted(meas)[:n]
r = sum(meas[k] for k in ks) / sum(pred[k] for k in ks)
print(f"first wave: {len(ks)} tasks, measured/model = {r:.3f}")
print("OK" if r <= 1.25 else "EXCEEDS")
PY
if grep -q EXCEEDS $O/first_wave.txt || [ -s $LG/failed.txt ]; then
  echo "first wave over the cost model by > 25% or a task failed" > $O/STOPPED; exit 1
fi
tail -n +"$((NPROC + 1))" $O/jobs.txt | xargs -P "$NPROC" -L 1 sh -c 'nice -n 10 $PY rq1_archive.py task $0 $O zi >> $LG/tasks.log 2>&1 || echo "$0" >> $LG/failed.txt'
[ -s $LG/failed.txt ] && { echo "task failures" > $O/STOPPED; exit 1; }
nice -n 10 $PY rq1_archive.py manifest $O 1.01e11 zi > $O/summary.log 2>&1; echo "exit=$?" > $O/summary.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] rq1 ZI archive: done" >> ~/claude-work.log

#!/usr/bin/env bash
# RQ1-c (round 95): the ℤ[ω] angle archive to 1.01·10¹² (10,100 segments of 10⁸) on /mnt/data, queued after ℤ[i]: it
# waits for /mnt/data/rq1/archive_1e12_zi/ALL_DONE and does nothing if that run wrote STOPPED or its summary failed.
# rq1_zw.py: split rule p ≡ 1 (mod 3), p = u² + 3v²; θ = (arg π mod π/3)/(π/3), mirror 1 − θ. Generation, integrity and
# hashes only; no statistic. Mount guard, free-space check, first-wave and running-ratio checks (½, ¾; stop above 1.25×)
# as run_rq1_archive_1e12_spot.sh. Cost model ≈ 234 spot core-h, ≈ 8.4 h at 28 processes.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/rq1/run_rq1_archive_zw_spot.sh [NPROC]
set -u
NPROC=${1:-28}
CODE=~/tmp/claude/specarith/rq1
ZI=/mnt/data/rq1/archive_1e12_zi
O=/mnt/data/rq1/archive_1e12_zw; LG=$O/logs
PY=~/miniforge3/envs/ph6c/bin/python
while [ ! -f $ZI/ALL_DONE ]; do
  [ -f $ZI/STOPPED ] && { echo "Z[i] run STOPPED; Z[omega] not started"; exit 1; }
  sleep 600
done
grep -qx "exit=0" $ZI/summary.exit || { echo "Z[i] manifest did not exit 0; Z[omega] not started"; exit 1; }
mountpoint -q /mnt/data || { echo "REFUSED: /mnt/data is not a mount point"; exit 2; }
FREE_GB=$(df -BG --output=avail /mnt/data | tail -1 | tr -dc 0-9)
[ "$FREE_GB" -gt 173 ] || { echo "not enough space on /mnt/data: ${FREE_GB} GB free, 153 + 20 needed"; exit 1; }
cd $CODE || exit 1
mkdir -p $O $LG
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 PY O LG
RUN='mountpoint -q /mnt/data && nice -n 10 $PY rq1_zw.py task $0 $O >> $LG/tasks.log 2>&1 || echo "$0" >> $LG/failed.txt'
ratio() {
$PY - "$1" "$2" <<'PY'
import sys
o, n = sys.argv[1], int(sys.argv[2])
pred = {int(l.split()[0]): float(l.split()[1]) for l in open(o + "/jobs.txt")}
m = [(int(l.split()[0]), float(l.split()[2])) for l in open(o + "/logs/tasks.log")][:n]
r = sum(s for _, s in m) / sum(pred[k] for k, _ in m)
print(f"{len(m)} tasks, measured/model = {r:.3f}")
print("OK" if r <= 1.25 else "EXCEEDS")
PY
}
echo "$(date -Is) [CC specarith] rq1 1e12 archive zw: start ($NPROC procs, $O)" >> ~/claude-work.log
$PY rq1_zw.py jobs 1.01e12 > $O/jobs.txt
NJ=$(wc -l < $O/jobs.txt); HALF=$((NJ / 2)); Q3=$((NJ * 3 / 4))
head -n "$NPROC" $O/jobs.txt | cut -d' ' -f1 | xargs -P "$NPROC" -n 1 sh -c "$RUN"
ratio $O $NPROC > $O/first_wave.txt
if grep -q EXCEEDS $O/first_wave.txt || [ -s $LG/failed.txt ]; then echo "first wave over the cost model or a task failed" > $O/STOPPED; exit 1; fi
sed -n "$((NPROC + 1)),${HALF}p" $O/jobs.txt | cut -d' ' -f1 | xargs -P "$NPROC" -n 1 sh -c "$RUN"
ratio $O $HALF > $O/mid_run.txt
if grep -q EXCEEDS $O/mid_run.txt || [ -s $LG/failed.txt ]; then echo "mid-run over the cost model or a task failed" > $O/STOPPED; exit 1; fi
sed -n "$((HALF + 1)),${Q3}p" $O/jobs.txt | cut -d' ' -f1 | xargs -P "$NPROC" -n 1 sh -c "$RUN"
ratio $O $Q3 > $O/q3_run.txt
if grep -q EXCEEDS $O/q3_run.txt || [ -s $LG/failed.txt ]; then echo "three-quarter check over the cost model or a task failed" > $O/STOPPED; exit 1; fi
tail -n +"$((Q3 + 1))" $O/jobs.txt | cut -d' ' -f1 | xargs -P "$NPROC" -n 1 sh -c "$RUN"
[ -s $LG/failed.txt ] && { echo "task failures" > $O/STOPPED; exit 1; }
ratio $O $NJ > $O/final_ratio.txt
mountpoint -q /mnt/data || { echo "REFUSED at manifest: /mnt/data is not a mount point" > $O/STOPPED; exit 2; }
MANIFEST_PROCS=$NPROC nice -n 10 $PY rq1_zw.py manifest $O 1.01e12 > $O/summary.log 2>&1; echo "exit=$?" > $O/summary.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] rq1 1e12 archive zw: done" >> ~/claude-work.log

#!/usr/bin/env bash
# RQ1-c sealed read on spot (RQ1C_SEAL.md §5). Launch ONLY after the seal's OpenTimestamps receipt is Bitcoin-attested
# and verified on two explorers (verify_rq1c_stamp.py exit 0, VERIFY JSON committed), and after a load check.
# VOID conditions (any one; nothing is read): the mount guard fails; sha256sum -c rq1c_read_pins.sha256 fails (code,
# JSONs, manifests, segment list); sha256sum -c rq1c_archive_segments.sha256 fails (all 30,200 segments); the two reads'
# JSONs differ (cmp).
# Reads: read1 then read2, separate processes, each under a 80 GB memory cap, READ_THREADS=16, nice. Cost: rq1c_read.py
# compares cumulative CPU with the model after every stage (≈ 28.2 spot core-h per read) and writes STOPPED above 1.25×.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/rq1/run_rq1c_read_spot.sh
set -u
cd ~/tmp/claude/specarith/rq1 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=rq1c_read_out; mkdir -p $O
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1 READ_THREADS=16
echo "$(date -Is) [CC specarith] rq1c sealed read: pre-read checks" >> ~/claude-work.log
mountpoint -q /mnt/data || { echo "VOID (mount guard): /mnt/data not mounted" > $O/STOPPED; exit 1; }
sha256sum -c rq1c_read_pins.sha256 > $O/pins_check.txt 2>&1; echo "exit=$?" >> $O/pins_check.txt
grep -qx "exit=0" $O/pins_check.txt || { echo "VOID (hash): rq1c_read_pins.sha256" > $O/STOPPED; exit 1; }
for f in zs2 zi zw; do
  grep "archive_1e12_$f/" rq1c_archive_segments.sha256 > $O/seg_$f.sha256
  ( nice -n 10 sha256sum -c $O/seg_$f.sha256 > $O/segments_check_$f.txt 2>&1; echo "exit=$?" >> $O/segments_check_$f.txt ) &
done
wait
for f in zs2 zi zw; do
  grep -qx "exit=0" $O/segments_check_$f.txt || { echo "VOID (hash): archive segments $f" > $O/STOPPED; exit 1; }
done
A="/mnt/data/rq1/archive_1e12_zs2 /mnt/data/rq1/archive_1e12_zi /mnt/data/rq1/archive_1e12_zw rq1c_wit/P1_SELECTION.json rq1c_wit/P1_CONFIRM.json"
for i in 1 2; do
  echo "$(date -Is) [CC specarith] rq1c sealed read: read$i" >> ~/claude-work.log
  t0=$(date +%s)
  mountpoint -q /mnt/data || { echo "VOID (mount guard) before read$i" > $O/STOPPED; exit 1; }
  systemd-run --user --scope -q -p MemoryMax=80G -p MemorySwapMax=0 nice -n 10 $PY rq1c_read.py read $A \
    $O/read$i.json > $O/read$i.log 2>&1
  echo "exit=$?" >> $O/read$i.log
  echo "read$i wall $(( $(date +%s) - t0 )) s" >> $O/timing.txt
  [ -f $O/STOPPED ] && exit 1
  grep -qx "exit=0" $O/read$i.log || { echo "read$i failed" > $O/STOPPED; exit 1; }
done
cmp $O/read1.json $O/read2.json > $O/cmp.txt 2>&1; echo "exit=$?" >> $O/cmp.txt
sha256sum $O/read1.json $O/read2.json >> $O/cmp.txt
grep -qx "exit=0" $O/cmp.txt || echo "VOID (cmp): read1 and read2 differ" > $O/STOPPED
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] rq1c sealed read: done" >> ~/claude-work.log

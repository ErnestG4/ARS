#!/bin/bash
# RQ1-c read-code checks (rq1c_read.py @ 9fb9262c): zw34d, then repro. Mount guard; nice; log.
cd ~/tmp/claude/specarith/rq1 || exit 1
mountpoint -q /mnt/data || { echo "no /mnt/data" > rq1c_read/STOPPED; exit 2; }
PY=~/miniforge3/envs/ph6c/bin/python
echo "$(date -Is) [CC specarith] rq1c read checks: start" >> ~/claude-work.log
nice -n 10 $PY rq1c_read.py zw34d rq1c_read/ZW34D_CHECK.json /mnt/data/rq1/archive_1e12_zw > rq1c_read/zw34d.log 2>&1; echo "zw34d exit=$?" >> rq1c_read/status.txt
READ_THREADS=16 nice -n 10 $PY rq1c_read.py repro /mnt/data/rq1/archive_1e12_zs2 /mnt/data/rq1/archive_1e12_zi rq1c_read/REPRO.json > rq1c_read/repro.log 2>&1; echo "repro exit=$?" >> rq1c_read/status.txt
date -Is > rq1c_read/ALL_DONE
echo "$(date -Is) [CC specarith] rq1c read checks: done" >> ~/claude-work.log

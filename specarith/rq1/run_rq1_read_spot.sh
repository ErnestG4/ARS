#!/usr/bin/env bash
# RQ1 sealed read on spot (RQ1_SEAL.md order steps 4-5; round 91). Launch ONLY after the seal's OpenTimestamps receipt is
# Bitcoin-attested and verified on two explorers (verify_rq1_stamp.py exit 0, VERIFY JSON committed).
# Step 4: sha256sum -c read_pins.sha256 (code, JSONs, manifests, heuristic file, segment list), then
#         sha256sum -c archive_segments.sha256 (all 2,010 segment files). Any mismatch: VOID (hash), no read.
# Step 5: read1 then read2, separate processes, each under a 40 GB cap, single-threaded, pinned env; then cmp.
# Cost model (seal §6): ≈ 1.4 spot core-h per read (≈ 83 min), the 10¹⁰ part ≈ 1/10 of it (≈ 8.3 min). First-wave rule:
# if read1's 10¹⁰ rows take more than 1.25 × 8.3 min, read1 is stopped, STOPPED written, and nothing more runs.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/rq1/run_rq1_read_spot.sh   (an argument: another base dir, for the dry run)
set -u
cd "${1:-$HOME/tmp/claude/specarith/rq1}" || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=read_out; mkdir -p $O
rm -f $O/ALL_DONE $O/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1
echo "$(date -Is) [CC specarith] rq1 sealed read: pre-read checks" >> ~/claude-work.log
sha256sum -c read_pins.sha256 > $O/pins_check.txt 2>&1; echo "exit=$?" >> $O/pins_check.txt
grep -qx "exit=0" $O/pins_check.txt || { echo "VOID (hash): read_pins.sha256" > $O/STOPPED; exit 1; }
nice -n 10 sha256sum -c archive_segments.sha256 > $O/segments_check.txt 2>&1; echo "exit=$?" >> $O/segments_check.txt
grep -qx "exit=0" $O/segments_check.txt || { echo "VOID (hash): archive segments" > $O/STOPPED; exit 1; }
LIMIT=$((83 * 60 / 10 * 125 / 100))
for i in 1 2; do
  echo "$(date -Is) [CC specarith] rq1 sealed read: read$i" >> ~/claude-work.log
  t0=$(date +%s)
  systemd-run --user --scope -q -p MemoryMax=40G -p MemorySwapMax=0 nice -n 10 $PY rq1_read.py archive archive_zi \
    witness/SELECTION.json witness_confirm/CONFIRM.json $O/read$i.json > $O/read$i.log 2>&1 &
  pid=$!
  if [ $i = 1 ]; then
    while kill -0 $pid 2>/dev/null && ! grep -q "^10000000000 " $O/read1.log; do sleep 10; done
    el=$(( $(date +%s) - t0 ))
    echo "read1 1e10 rows after ${el} s; limit ${LIMIT} s" > $O/first_wave.txt
    if [ $el -gt $LIMIT ]; then kill $pid; echo "first X over the cost model by > 25%" > $O/STOPPED; exit 1; fi
  fi
  wait $pid; echo "exit=$?" >> $O/read$i.log
  echo "read$i wall $(( $(date +%s) - t0 )) s" >> $O/timing.txt
  grep -qx "exit=0" $O/read$i.log || { echo "read$i failed" > $O/STOPPED; exit 1; }
done
cmp $O/read1.json $O/read2.json > $O/cmp.txt 2>&1; echo "exit=$?" >> $O/cmp.txt
sha256sum $O/read1.json $O/read2.json >> $O/cmp.txt
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] rq1 sealed read: done" >> ~/claude-work.log

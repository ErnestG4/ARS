#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1 stage-2 SEALED READ, one of two (FN1_STAGE2_SEAL.md; Will 2026-11-02: "stamp → Bitcoin attestation verified on
# two explorers → sequential double read through the queue → cmp → verdicts (not viewed before the cmp)").
# Queued by queue_fn1_read2_pueue.sh in group specarith-scored (parallel 1) through pq-scored; read 2 runs after read 1.
# Guards (any failure: exit nonzero, no read):
#  - the stamp verification record (timestamps/FN1_STAGE2_SEAL_STAMP_2026-11-02_VERIFY.json, copied to the read dir)
#    has every check true, including a Bitcoin attestation verified on both explorers;
#  - sha256 of the read code, the pins and the imported modules equal the sealed values below;
#  - /mnt/data is mounted; MemAvailable ≥ 60 GB (the read peaks near 43 GB); the output does not exist yet.
# The read prints only "done"; its JSON is not opened before the cmp.
#   bash run_fn1_read2_one.sh N        (N = 1 or 2)
set -u
N=$1
CODE=~/tmp/claude/specarith/fn1; O=~/tmp/claude/specarith/fn1/stage2_read
PY=~/miniforge3/envs/ph6c/bin/python
export OMP_NUM_THREADS=1
cd $CODE || exit 1
mkdir -p $O
st() { echo "read$N $1" >> $O/status.txt; }
[ -e $O/READ$N.json ] && { st "REFUSED output exists"; exit 1; }
mountpoint -q /mnt/data || { st "REFUSED mount"; exit 2; }
$PY -I -c 'import json,sys; v=json.load(open(sys.argv[1])); c=v["checks"]; sys.exit(0 if c and all(c.values()) and v["attestations"] and all(a["verified"] for a in v["attestations"]) else 1)' $O/FN1_STAGE2_SEAL_STAMP_2026-11-02_VERIFY.json || { st "REFUSED attestation not verified"; exit 1; }
sha256sum -c --quiet - <<SUMS || { st "REFUSED sealed hash mismatch"; exit 1; }
92f9db78fa9e709b2beb64ce56d2b69d37fb316687f6fa12628b68d6fe50f9a8  fn1_read2.py
c511e4a4549c14ca0913753d8d32b0822b5840714d9311a17e060a9a74b404ce  fn1_pins2.json
585a673c9dd0d3e23f0cc69ebb43006f046c91110810688a98223baae85d75e1  fn1_archive.py
0e328302e974660ed3abd1316cac04aae1483cd1def13546952677bd845bc856  rq1_read.py
98dd15825933b137bfea99b5f622c725634987d2a8a977efaece2957748366d1  rq1_zw.py
7764c23ef64c1f53efb1fb12bd1152d93f8956745cf623d40af93e108e7d1a0c  rq1_angles.py
eca8eb958945500cee44faedf1229d8aebd9f88b35c23ab92ccf624eed175cc0  rq1_archive.py
SUMS
MA=$(awk '/MemAvailable/{print int($2/1048576)}' /proc/meminfo)
[ "$MA" -ge 60 ] || { st "REFUSED MemAvailable ${MA} GB < 60"; exit 1; }
echo "$(date -Is) [CC specarith] fn1 stage-2 sealed read $N start (MemAvailable ${MA} GB)" >> ~/claude-work.log
$PY fn1_read2.py read fn1_pins2.json $O/READ$N.json > $O/read$N.log 2>&1; rc=$?
st "rc $rc"
echo "$(date -Is) [CC specarith] fn1 stage-2 sealed read $N end rc $rc" >> ~/claude-work.log
exit $rc

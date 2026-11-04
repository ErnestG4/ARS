#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1-h2 SEALED READ, one of two (FN1H2_SEAL.md §10; Will 2026-11-04: "tag, timestamp, Bitcoin attestation verified on
# two explorers, the sequential double read through the queue, cmp, and only then the verdicts").
# Queued by queue_fn1h2_read_pueue.sh in specarith-scored (parallel 1) through pq-scored; read 2 runs after read 1.
# Guards (any failure: exit nonzero, no read):
#  - the stamp verification record (copied to the read dir) has every check true and a Bitcoin attestation verified
#    on both explorers;
#  - sha256 of the pins file equals the sealed value below, and every code file's sha256 equals the pins file's
#    "code" block (checked here, before Python imports anything);
#  - /mnt/data mounted; MemAvailable ≥ 30 GB (the D2 (b) run peaked near 11 GB); the output does not exist yet.
# The read prints only "done"; its JSON is not opened before the cmp.
#   bash run_fn1h2_read_one.sh N        (N = 1 or 2)
set -u
N=$1
CODE=~/tmp/claude/specarith/fn1; O=$CODE/h2_read
PY=~/miniforge3/envs/ph6c/bin/python
PINS_SHA=e591fc3f370880be8b6fd780d6fc3d533989dbe1d53d8f3e49dcec2fa90bce96
export OMP_NUM_THREADS=1
cd $CODE || exit 1
mkdir -p $O
st() { echo "read$N $1" >> $O/status.txt; }
[ -e $O/READ$N.json ] && { st "REFUSED output exists"; exit 1; }
mountpoint -q /mnt/data || { st "REFUSED mount"; exit 2; }
$PY -I -c 'import json,sys; v=json.load(open(sys.argv[1])); c=v["checks"]; sys.exit(0 if c and all(c.values()) and v["attestations"] and all(a["verified"] for a in v["attestations"]) else 1)' $O/FN1H2_SEAL_STAMP_VERIFY.json || { st "REFUSED attestation not verified"; exit 1; }
echo "$PINS_SHA  fn1h2_pins.json" | sha256sum -c --quiet - || { st "REFUSED pins hash"; exit 1; }
$PY -I -c 'import json,sys; [print(v + "  " + k) for k, v in json.load(open("fn1h2_pins.json"))["code"].items()]' | sha256sum -c --quiet - || { st "REFUSED code hash"; exit 1; }
MA=$(awk '/MemAvailable/{print int($2/1048576)}' /proc/meminfo)
[ "$MA" -ge 30 ] || { st "REFUSED MemAvailable ${MA} GB < 30"; exit 1; }
echo "$(date -Is) [CC specarith] fn1h2 sealed read $N start (MemAvailable ${MA} GB)" >> ~/claude-work.log
READ_THREADS=8 $PY fn1h2_read.py read fn1h2_pins.json $O/READ$N.json > $O/read$N.log 2>&1; rc=$?
st "rc $rc"
echo "$(date -Is) [CC specarith] fn1h2 sealed read $N end rc $rc" >> ~/claude-work.log
exit $rc

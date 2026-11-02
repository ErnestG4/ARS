#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1 stage-2 §9.F rehearsal REPEAT on the final code (Will 2026-11-02 §2.4: option B), sequential, on spot:
#  pins (dry + red) → dry read ×2 on window [n(1e9), n(1e10)) with the stage-1 synthetic w = 2 archives → cmp →
#  red: prefix guard (one altered stage-1 sha) must raise, no output → red: altered manifest pin must raise, no output →
#  (no drysynth: the array path is unchanged since dry2; its memory and timing stand).
set -u
cd ~/tmp/claude/specarith/fn1 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=~/tmp/claude/specarith/fn1/dry3; mkdir -p $O; : > $O/status.txt
mountpoint -q /mnt/data || { echo "mount missing" >> $O/status.txt; exit 2; }
echo "$(date -Is) [CC specarith] fn1 stage-2 dry rehearsal repeat (dry3) start" >> ~/claude-work.log
$PY fn1_make_pins2.py dry fn1_pins.json dry10_pins.json specarith/fn1/dry3/PINS2_DRY.json specarith/fn1/dry3/PINS2_DRY_RED.json > $O/pins.log 2>&1; echo "pins $?" >> $O/status.txt
$PY - <<'PY' >> $O/status.txt 2>&1
import json
p = json.load(open("/home/combust/tmp/claude/specarith/fn1/dry3/PINS2_DRY.json"))
p["archives"]["zi"]["manifest_sha256"] = "0" * 64
json.dump(p, open("/home/combust/tmp/claude/specarith/fn1/dry3/PINS2_DRY_REDPIN.json", "w"))
print("redpin made 0")
PY
for i in 1 2; do nice -n 10 $PY fn1_read2.py dry $O/PINS2_DRY.json $O/D$i.json 1e9 1e10 > $O/d$i.log 2>&1; echo "d$i $?" >> $O/status.txt; done
cmp $O/D1.json $O/D2.json > $O/cmp.txt 2>&1; echo "cmp $?" >> $O/status.txt
nice -n 10 $PY fn1_read2.py dry $O/PINS2_DRY_RED.json $O/RED_PREFIX.json 1e9 1e10 > $O/red_prefix.log 2>&1; echo "red_prefix $?" >> $O/status.txt
[ -e $O/RED_PREFIX.json ] && echo "red_prefix_output_exists" >> $O/status.txt
nice -n 10 $PY fn1_read2.py dry $O/PINS2_DRY_REDPIN.json $O/RED_PIN.json 1e9 1e10 > $O/red_pin.log 2>&1; echo "red_pin $?" >> $O/status.txt
[ -e $O/RED_PIN.json ] && echo "red_pin_output_exists" >> $O/status.txt
echo DONE >> $O/status.txt
echo "$(date -Is) [CC specarith] fn1 stage-2 dry rehearsal repeat (dry3) done" >> ~/claude-work.log

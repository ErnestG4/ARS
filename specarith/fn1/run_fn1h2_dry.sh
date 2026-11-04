#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1-h2 §9.F dry double read (D2 (c)), the whole read pipeline at X_DRY = 2·10⁹ (≈ 0.4 core-h, against ≈ 3 at X*).
# h = 2 sets: the synthetic fixtures (/mnt/data/fn1h2_dry, fn1h2_fixtures.py); h = 1: the real seen archives cut at
# X_DRY. Step refs writes the dry references at X_DRY (fn1h2_read.py refs); the pins file then pins them, the committed
# (★) predictions and controls; each dry read recomputes the references and checks them bit for bit, as the read will
# against the committed D2 (b) file. Each read is its own process and pueue task. Red paths (must fail, no output):
#   red-pin:  the -7 manifest pin zeroed in a copy of the pins file → AssertionError ('manifest pin', …);
#   red-refs: the refs pin's sha256 zeroed → AssertionError ('refs pin', …) — raised only after the references are
#             recomputed (the comparison needs them), so it costs one reference pass.
#   bash run_fn1h2_dry.sh refs | pins | one N | cmp | red-pin | red-refs
set -u
CODE=~/tmp/claude/specarith/fn1; OUT=${DRYOUT:-~/tmp/claude/specarith/fn1/h2dry}; PY=~/miniforge3/envs/ph6c/bin/python
PINS=$OUT/fn1h2_pins_dry.json; XD=2e9; LEAD=~/tmp/claude/specarith/fn1/lead
cd $CODE || exit 1
mkdir -p $OUT
case "$1" in
  refs) READ_THREADS=8 $PY fn1h2_read.py refs fn1_pins2.json $OUT/DRY_REFS.json $XD > $OUT/refs.log 2>&1 ;;
  pins) $PY fn1h2_make_pins.py dry $OUT/DRY_REFS.json $LEAD/FN1H2_PRED.json $LEAD/FN1H2_CONTROLS.json /mnt/data/fn1h2_dry $PINS ;;
  one) READ_THREADS=8 $PY fn1h2_read.py dry $PINS $OUT/DRY$2.json $XD > $OUT/dry$2.log 2>&1; rc=$?; echo "rc $rc" >> $OUT/dry$2.log; exit $rc ;;
  cmp) cmp $OUT/DRY1.json $OUT/DRY2.json > $OUT/cmp.txt 2>&1; rc=$?; sha256sum $OUT/DRY1.json $OUT/DRY2.json >> $OUT/cmp.txt; echo "cmp rc $rc" >> $OUT/cmp.txt; exit $rc ;;
  red-pin) $PY -c "import json; p=json.load(open('$PINS')); p['archives']['-7']['manifest_sha256']='0'*64; json.dump(p, open('$OUT/pins_redpin.json','w'))"
           $PY fn1h2_read.py dry $OUT/pins_redpin.json $OUT/RED_PIN.json $XD > $OUT/red_pin.log 2>&1; rc=$?
           echo "rc $rc; output exists: $([ -e $OUT/RED_PIN.json ] && echo yes || echo no)" >> $OUT/red_pin.log
           [ $rc -ne 0 ] && [ ! -e $OUT/RED_PIN.json ] && grep -q "manifest pin" $OUT/red_pin.log ;;
  red-refs) $PY -c "import json; p=json.load(open('$PINS')); p['refs']['sha256']='0'*64; json.dump(p, open('$OUT/pins_redrefs.json','w'))"
           READ_THREADS=8 $PY fn1h2_read.py dry $OUT/pins_redrefs.json $OUT/RED_REFS.json $XD > $OUT/red_refs.log 2>&1; rc=$?
           echo "rc $rc; output exists: $([ -e $OUT/RED_REFS.json ] && echo yes || echo no)" >> $OUT/red_refs.log
           [ $rc -ne 0 ] && [ ! -e $OUT/RED_REFS.json ] && grep -q "refs pin" $OUT/red_refs.log ;;
esac

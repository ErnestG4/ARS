#!/usr/bin/env bash
# Wait for a spot run dir (relative to ~/tmp/claude/specarith/cs4); print its state. Status 0 iff no STOPPED marker,
# every failure list is empty and the summary reported exit=0; nonzero only on a failure.
O=~/tmp/claude/specarith/cs4/$1
while ! ssh -o ConnectTimeout=20 spot "test -f $O/ALL_DONE -o -f $O/STOPPED" 2>/dev/null; do sleep 900; done
ssh spot "cd $O && cat STOPPED 2>/dev/null; cat summary.exit 2>/dev/null; cat summary.log 2>/dev/null; cat logs/failed*.txt 2>/dev/null; ls *.json | wc -l"
ssh spot "cd $O && test ! -f STOPPED && ! cat logs/failed*.txt 2>/dev/null | grep -q . && grep -qx 'exit=0' summary.exit"

#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# FN1-h2 sealed double read: cmp of READ1.json and READ2.json (queued after read 2). Exit 0 iff byte-identical.
# Verdicts are opened only after this.
set -u
O=~/tmp/claude/specarith/fn1/h2_read
cmp $O/READ1.json $O/READ2.json > $O/cmp.txt 2>&1; rc=$?
echo "cmp $rc" >> $O/status.txt
sha256sum $O/READ1.json $O/READ2.json >> $O/status.txt
exit $rc

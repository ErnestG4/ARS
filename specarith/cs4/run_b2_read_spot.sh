#!/usr/bin/env bash
# Round 61/62: the corrected (B)'s sealed read on the fresh F6 files: run1, run2 (separate processes), then compare.
# The read refuses unless seals/CORRECTED_B_SEAL.json pins this code, interpreter and inputs; md5s are checked before decode.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_b2_read_spot.sh
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
D=results/b2_read
mkdir -p $D
rm -f $D/ALL_DONE
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] corrected (B): sealed read run1/run2/compare" >> ~/claude-work.log
{ nice -n 10 $PY b2_sealread.py read run1 && nice -n 10 $PY b2_sealread.py read run2; } > $D/read.log 2>&1
echo "exit=$?" > $D/read.exit
nice -n 10 $PY b2_sealread.py compare > $D/compare.log 2>&1
echo "exit=$?" > $D/compare.exit
date -Is > $D/ALL_DONE
echo "$(date -Is) [CC specarith] corrected (B): sealed read: done" >> ~/claude-work.log

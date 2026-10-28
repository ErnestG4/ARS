#!/bin/bash
# GEO-TOT2 enumeration on spot (GEOTOT2_SEAL.md §2, §8): the 5,805 q of results/PLAN_1e8.json, one process, 20 numba
# threads, nice; cost checks inside geotot2.py enum (stop above 1.25x). Outputs hashed; nothing displayed.
# Usage: run_geotot2_spot.sh OUT_DIR
O=$1
cd ~/tmp/claude/specarith/geotot2 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
mkdir -p $O
echo "$(date -Is) [CC specarith] geotot2 enum: start" >> ~/claude-work.log
NUMBA_NUM_THREADS=20 nice -n 10 $PY geotot2.py enum PLAN_1e8.json $O/GEOTOT2_1e8.npz > $O/enum.log 2>&1
echo $? > $O/exit
sha256sum $O/GEOTOT2_1e8.npz > $O/HASH 2>/dev/null
echo "$(date -Is) [CC specarith] geotot2 enum: exit $(cat $O/exit)" >> ~/claude-work.log
date -Is > $O/ENUM_DONE

#!/usr/bin/env bash
# Phase 6.1 read under PH6_SEAL_6.1 (tag ph6.1-seal): every candidate through tests61.py read (hash-checked).
set -u
cd "$(dirname "$0")"
mkdir -p results/read61
for c in C1a C1b C2 C4 C3a C3b BBM Sierra_mirror; do
  OMP_NUM_THREADS=1 /home/combust/fmexplorer/bin/python3 tests61.py read "$c" >> results/read61/read.log 2>&1
  echo "$c exit=$?" >> results/read61/exits.txt
done
date -Is > results/read61/ALL_DONE

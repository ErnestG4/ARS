#!/usr/bin/env bash
# Phase 2 real run under PH2_SEAL_2.1 (tag ph2-seal-2.1): every sealed bin, unfold (exact θ) then gates. run.py refuses
# unless code and data hashes match seals/PH2_SEAL_2.1.json. One process per bin, own output files; nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph2/run_real_spot.sh
set -u
D=~/tmp/claude/specarith/ph2
PY=~/miniforge3/envs/specarith/bin/python
cd "$D"
mkdir -p results/run/logs results/run/exits
rm -f results/run/ALL_DONE
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PH2_ZEROS6="$D/data/odlyzko_zeros6.txt"
sha256sum ph2lib.py preread.py run.py seals/PH2_SEAL_2.1.json > results/run/code_sha256_run.txt
echo "$(date -Is) [CC specarith] ph2 REAL run under PH2_SEAL_2.1: 11 bins, nice 10" >> ~/claude-work.log
printf '%s\n' A B P1 P2 P3 P4 P5 P6 H1 H2 H3 |
  xargs -P 11 -L 1 sh -c 'nice -n 10 '"$PY"' run.py unfold "$0" > results/run/logs/$0.log 2>&1 && nice -n 10 '"$PY"' run.py gates "$0" >> results/run/logs/$0.log 2>&1; echo "exit=$?" > results/run/exits/$0.txt'
date -Is > results/run/ALL_DONE
echo "$(date -Is) [CC specarith] ph2 REAL run: all bins exited" >> ~/claude-work.log

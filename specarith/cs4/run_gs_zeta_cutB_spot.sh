#!/usr/bin/env bash
# Twenty-fifth round: prime cutoff 10⁶ at ℓ = 15.7502, every node pair (gs_zeta_cutB.py), 48 procs, nice 10, then the
# summary against the stored 3·10⁵ values.  Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_gs_zeta_cutB_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
OUT=results/gs_zeta_cutB
NP=48
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] gs_zeta_cutB: pmax 1e6, $NP procs, nice 10" >> ~/claude-work.log
seq 0 $((NP - 1)) |
  xargs -P $NP -I{} sh -c 'nice -n 10 '"$PY"' gs_zeta_cutB.py pairs 1000000 {} '"$NP"' '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" >> '"$OUT"'/logs/c{}.log'
nice -n 10 "$PY" gs_zeta_cutB.py summary 1000000 "$OUT" results/gs_zeta > "$OUT/summary.txt" 2>&1
echo "exit=$?" >> "$OUT/summary.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] gs_zeta_cutB: done" >> ~/claude-work.log

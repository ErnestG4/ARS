#!/usr/bin/env bash
# Diagnostic D (round 55; DIAG_D_DESIGN.md d2506082): decode (16 files, in parallel with the CUE null: 4 F5 files x 9
# chunks), then the scale tables, then the declared reading. nice 10. Run inside tmux `claude`.
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=results/diag_d
mkdir -p $O/seq $O/scales $O/null $O/logs
rm -f $O/ALL_DONE
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] Diagnostic D (round 55): decode 16 files + CUE null (36 procs), nice 10" >> ~/claude-work.log
F5="zeros_36146000.dat zeros_244046000.dat zeros_2377646000.dat zeros_10643246000.dat"
F4="zeros_252446000.dat zeros_2369246000.dat zeros_10634846000.dat"
F3="zeros_15146000.dat zeros_25646000.dat zeros_248246000.dat zeros_2373446000.dat zeros_10639046000.dat"
JOBS=""
for f in $F5; do JOBS="$JOBS F5:$f SI:$f"; done
for f in $F4; do JOBS="$JOBS F4:$f"; done
for f in $F3; do JOBS="$JOBS F3:$f"; done
( for j in $JOBS; do echo $j; done | xargs -P 16 -I{} sh -c 'S=$(echo {} | cut -d: -f1); F=$(echo {} | cut -d: -f2); nice -n 10 '"$PY"' diag_d.py decode $S $F '"$O"'/seq > '"$O"'/logs/decode_${S}_${F}.log 2>&1; echo "exit=$?" > '"$O"'/logs/decode_${S}_${F}.exit' ) &
DEC=$!
( for f in $F5; do for c in 0 1 2 3 4 5 6 7 8; do echo "$f:$c"; done; done | xargs -P 36 -I{} sh -c 'F=$(echo {} | cut -d: -f1); C=$(echo {} | cut -d: -f2); nice -n 10 '"$PY"' diag_d.py null $F '"$O"'/null $C 9 > '"$O"'/logs/null_${F}_$C.log 2>&1; echo "exit=$?" > '"$O"'/logs/null_${F}_$C.exit' ) &
NUL=$!
wait $DEC
i=0
for npy in $O/seq/*.npy; do
  b=$(basename $npy .npy); case $b in F5_*) idx=$i;; F4_*) idx=$((10+i));; F3_*) idx=$((20+i));; SI_*) idx=$((30+i));; esac; i=$((i+1))
  nice -n 10 $PY diag_d.py scales $npy $O/scales/$b.json $idx > $O/logs/scales_$b.log 2>&1; echo "exit=$?" > $O/logs/scales_$b.exit &
done
wait
wait $NUL
nice -n 10 $PY diag_d.py read > $O/read.log 2>&1; echo "exit=$?" > $O/read.exit
date -Is > $O/ALL_DONE
echo "$(date -Is) [CC specarith] Diagnostic D (round 55): done" >> ~/claude-work.log

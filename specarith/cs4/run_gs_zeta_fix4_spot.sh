#!/usr/bin/env bash
# Stage 2 prediction RECOMPUTED with the J13 sign fix (CS08_ERRATUM.md §4; Will, 2026-10-12: "recompute the Stage 2
# prediction with the fix and compare it with the sealed values"). Same code path as the sealed prediction
# (run_gs_zeta_spot.sh pairs + merge, run_gs_zeta_ext_spot.sh, gs_zeta_B.py), same heights, grids and cutoff, with the
# corrected cs4lib/cs4fast. Output to results/gs_zeta_fix4; the sealed results/gs_zeta is NOT touched.
# ρ₃ (I₃) is copied from the sealed run: n = 3 uses only J11 and J12, which the fix does not touch (check_ratios_j.py).
# 40 procs (16 cores stay with the U-family generation), nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_gs_zeta_fix4_spot.sh
set -u
D=~/tmp/claude/specarith/cs4
PY=~/miniforge3/envs/ph6c/bin/python
cd "$D"
SEALED=results/gs_zeta
OUT=results/gs_zeta_fix4
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE"
ELLS="15.7502 16.4972 17.2491 19.5003 21.75"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] gs_zeta_fix4: Stage 2 prediction recompute with the J13 fix, 40 procs, nice 10" >> ~/claude-work.log
for L in $ELLS; do
  mkdir -p "$OUT/L$L"
  cp -r "$SEALED/L$L/rho3" "$OUT/L$L/"
done
for L in $ELLS; do for c in $(seq 0 41); do echo "$L $c"; done; done | xargs -P 40 -L 1 sh -c 'nice -n 10 '"$PY"' gs_zeta.py pairs "$0" "$1" 42 '"$OUT"' > '"$OUT"'/logs/pr_$0_$1.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/pr_$0_$1.txt'
for L in $ELLS; do
  nice -n 10 $PY gs_zeta.py merge "$L" "$OUT" > "$OUT/logs/merge_$L.log" 2>&1; echo "exit=$?" > "$OUT/exits/merge_$L.txt"
done
for L in $ELLS; do for c in $(seq 0 7); do echo "$L $c"; done; done | xargs -P 40 -L 1 sh -c 'nice -n 10 '"$PY"' gs_zeta_ext.py pairs "$0" "$1" 8 '"$OUT"' > '"$OUT"'/logs/ext_$0_$1.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/ext_$0_$1.txt'
nice -n 10 $PY gs_zeta_B.py "$OUT" > "$OUT/logs/B.log" 2>&1; echo "exit=$?" > "$OUT/exits/B.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] gs_zeta_fix4: done" >> ~/claude-work.log

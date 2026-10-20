#!/usr/bin/env bash
# L6 long baseline (L6_BASELINE_DESIGN.md, round 66), after step 0 has passed: generation → gate 1 (stop on failure) →
# block statistics (50 CUE + 25 stitched sequences), the concatenation variant and the five pair windows → gate 2 →
# compare. nice 10, NPROC parallel jobs, one BLAS thread each. Restartable per sequence (existing outputs are kept).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/l6/run_l6_base_spot.sh [NPROC]
set -u
NPROC=${1:-48}
cd ~/tmp/claude/specarith/l6 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
R=results/base
GEN=$R/gen; ST=$R/stats; PR=$R/pair; LG=$R/logs
mkdir -p $GEN $ST $PR $LG
rm -f $R/ALL_DONE $R/STOPPED
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY GEN ST PR LG
# step 0 (design §2, §10): V1-V5 and the round-68 targeted V7 check replace the original V6/V7 verdict
for s in selftest v5 v7check; do grep -q "exit=0" results/step0/$s.exit 2>/dev/null || { echo "step 0 $s not passed" > $R/STOPPED; exit 1; }; done
echo "$(date -Is) [CC specarith] L6 baseline: generation ($NPROC procs)" >> ~/claude-work.log
{ for r in $(seq 0 49); do echo "cue $r"; done; for r in $(seq 0 9); do echo "cse $r"; echo "poisson $r"; done
  for r in $(seq 0 24); do echo "stitched $r"; done; } |
  xargs -P "$NPROC" -L 1 sh -c '[ -f "$GEN/$0_$(printf %03d $1).npy" ] || nice -n 10 $PY l6_base.py gen $0 $1 $GEN > $LG/gen_$0_$1.log 2>&1; echo "exit=$?" > $LG/gen_$0_$1.exit'
grep -L "exit=0" $LG/gen_*.exit > $R/gen_failures.txt
[ -s $R/gen_failures.txt ] && { echo "generation failures" > $R/STOPPED; exit 1; }
nice -n 10 $PY l6_base.py gate1 $GEN $R/gate1.json > $LG/gate1.log 2>&1; echo "exit=$?" > $R/gate1.exit
grep -q "exit=0" $R/gate1.exit || { echo "gate 1 not passed" > $R/STOPPED; exit 1; }
echo "$(date -Is) [CC specarith] L6 baseline: gate 1 passed; statistics" >> ~/claude-work.log
{ for r in $(seq 0 49); do echo "stats cue $r"; done; for r in $(seq 0 24); do echo "stats stitched $r"; done
  echo "concat x x"; for w in 0 1 2 3 4; do echo "pair $w x"; done; } |
  xargs -P "$NPROC" -L 1 sh -c '
    case $0 in
      stats)  [ -f "$ST/stats_$1_$(printf %03d $2).json" ] || nice -n 10 $PY l6_base.py stats $1 $2 $GEN $ST > $LG/stats_$1_$2.log 2>&1; echo "exit=$?" > $LG/stats_$1_$2.exit ;;
      concat) [ -f "$ST/concat.json" ] || nice -n 10 $PY l6_base.py concat $GEN $ST > $LG/concat.log 2>&1; echo "exit=$?" > $LG/concat.exit ;;
      pair)   [ -f "$PR/pair_0$1.json" ] || nice -n 10 $PY l6_base.py pair $1 $GEN $PR > $LG/pair_$1.log 2>&1; echo "exit=$?" > $LG/pair_$1.exit ;;
    esac'
grep -L "exit=0" $LG/stats_*.exit $LG/concat.exit $LG/pair_*.exit > $R/stats_failures.txt
[ -s $R/stats_failures.txt ] && { echo "statistics failures" > $R/STOPPED; exit 1; }
nice -n 10 $PY l6_base.py gate2 $ST $R/gate2.json > $LG/gate2.log 2>&1; echo "exit=$?" > $R/gate2.exit
grep -q "exit=0" $R/gate2.exit || { echo "gate 2 not passed" > $R/STOPPED; exit 1; }
nice -n 10 $PY l6_base.py compare $ST $PR $R/compare.json > $LG/compare.log 2>&1; echo "exit=$?" > $R/compare.exit
date -Is > $R/ALL_DONE
echo "$(date -Is) [CC specarith] L6 baseline: done" >> ~/claude-work.log

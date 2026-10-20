#!/usr/bin/env bash
# Phase 6 near-miss check (NEARMISS_RULE.md, round 67; post hoc, descriptive): six spectra in parallel (C1a C1b C2 C4,
# the ζ-zeros positive control, the GUE negative control), then the summary. nice 10, one BLAS thread each.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph6nm/run_nearmiss_spot.sh
set -u
cd ~/tmp/claude/specarith/ph6nm || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
D=results/nearmiss
mkdir -p $D/logs
rm -f $D/ALL_DONE
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY D ZEROS6=$HOME/tmp/claude/specarith/ph6nm/data/odlyzko_zeros6.txt
echo "$(date -Is) [CC specarith] Phase 6 near-miss check (6 spectra)" >> ~/claude-work.log
printf '%s\n' C1a C1b C2 C4 zeros gue | xargs -P 6 -I{} sh -c 'nice -n 10 $PY nearmiss.py one {} $D > $D/logs/{}.log 2>&1; echo "exit=$?" > $D/logs/{}.exit'
nice -n 10 $PY nearmiss.py summary $D > $D/logs/summary.log 2>&1; echo "exit=$?" > $D/logs/summary.exit
date -Is > $D/ALL_DONE
echo "$(date -Is) [CC specarith] Phase 6 near-miss check: done" >> ~/claude-work.log

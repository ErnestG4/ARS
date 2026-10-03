#!/usr/bin/env bash
# Divisor Harmonics v0 -- CPU analysis on spot (brief §8: nulls and bootstraps on spot's CPUs). numpy only.
# 1. rsync the extracted activations + the sealed scripts to spot:~/llmspec_div/ (sequential, size-verified by rsync)
# 2. run divisor_spectrum.py per tag inside tmux 'claude' (nice), logging to ~/claude-work.log per the box rules
# 3. results come back with `./run_spectrum_spot.sh pull`
# Usage: ./run_spectrum_spot.sh push | run | pull | status
set -u
cd "$(dirname "$0")/.."
R=~/llmspec_div
case "${1:-status}" in
push)
  ssh spot "mkdir -p $R/acts $R/results $R/divisor"
  rsync -a divisor/templates.py divisor/divisor_spectrum.py spot:$R/divisor/
  for f in results/divisor/acts/*.npz; do rsync -a --partial "$f" spot:$R/acts/ || { echo "rsync failed $f"; exit 1; }; done
  ssh spot "ls -la $R/acts | tail -n +2 | wc -l; du -sh $R/acts" ;;
run)
  ssh spot "tmux new -d -s claude 2>/dev/null; tmux send-keys -t claude 'echo \"\$(date -Is) llmspec divisor: spectrum run start\" >> ~/claude-work.log; cd $R && for f in acts/*.npz; do t=\$(basename \$f .npz); [ -f results/\${t}_last_primary.json ] && continue; OMP_NUM_THREADS=8 nice -n 10 python3 divisor/divisor_spectrum.py \$f --out results/\${t}_last_primary.json 2>&1 | tail -n 9 | tee -a spectrum.log; done; for f in acts/pythia-*.npz; do t=\$(basename \$f .npz); OMP_NUM_THREADS=8 nice -n 10 python3 divisor/divisor_spectrum.py \$f --read first --out results/\${t}_first_primary.json 2>&1 | tail -n 3 | tee -a spectrum.log; OMP_NUM_THREADS=8 nice -n 10 python3 divisor/divisor_spectrum.py \$f --layers all --out results/\${t}_last_all.json 2>&1 | tail -n 2 | tee -a spectrum.log; done; echo SPECTRUM_ALL_DONE | tee -a spectrum.log; echo \"\$(date -Is) llmspec divisor: spectrum run done\" >> ~/claude-work.log' Enter" ;;
pull)
  mkdir -p results/divisor && rsync -a spot:$R/results/ results/divisor/ && rsync -a spot:$R/spectrum.log results/divisor/spot_spectrum.log && ls results/divisor/*.json | wc -l ;;
status)
  ssh spot "tail -n 5 $R/spectrum.log 2>/dev/null; ls $R/results 2>/dev/null | wc -l" ;;
esac

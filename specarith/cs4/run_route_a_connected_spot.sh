#!/usr/bin/env bash
# Route (a) connected-term sensitivities (forty-eighth round): positivity of ρ_n at μ_k = 1 ± 0.02 at every quadrature
# point (route_a_connected.py run), NCH chunks, nice 10. Data-free. Restartable (chunks skip jobs already done).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_route_a_connected_spot.sh [NCH]
set -u
NCH=${1:-32}
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
OUT=results/connected
mkdir -p "$OUT/logs"
rm -f "$OUT/ALL_DONE"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) connected-term positivity: $NCH procs, nice 10" >> ~/claude-work.log
seq 0 $((NCH - 1)) | xargs -P "$NCH" -I{} sh -c 'nice -n 10 '"$PY"' route_a_connected.py run {} '"$NCH"' '"$OUT"' > '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/logs/c{}.exit'
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] route (a) connected-term positivity: done" >> ~/claude-work.log

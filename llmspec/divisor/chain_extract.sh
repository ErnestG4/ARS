#!/usr/bin/env bash
# Divisor Harmonics v0 -- GPU extraction chain. Waits for the ext_queue to exit, re-checks GPU_STATUS: FREE and that no
# train.py is running, then extracts the three final Pythia checkpoints and the 23 A0 checkpoints (minutes). Detached,
# resumable (skips tags whose .npz exists). Never preempts the queue.
set -u
cd "$(dirname "$0")/.."
PY=/home/combust/fmexplorer/bin/python3
Q=$(ps -eo pid,args | grep '[b]ash ./ext_queue.sh' | awk '{print $1}' | head -1)
[ -n "$Q" ] && { echo "$(date -Is) waiting for ext_queue pid $Q"; while kill -0 "$Q" 2>/dev/null; do sleep 60; done; }
sleep 30
if [ "$(grep -c 'GPU_STATUS: FREE' NOTES.md)" -lt 1 ] || ps -eo args | grep -q '^/home/combust/fmexplorer/bin/python3 train.py'; then
  echo "$(date -Is) GPU not free (flag or train.py); NOT extracting"; exit 2; fi
echo "$(date -Is) ext_queue done, GPU free: extracting"
run() { tag=$1; shift; [ -f results/divisor/acts/$tag.npz ] && { echo "skip $tag"; return; }
        $PY divisor/divisor_extract.py --tag "$tag" "$@" || echo "EXTRACT FAILED $tag"; }
run pythia-70m  --model EleutherAI/pythia-70m  --revision step143000
run pythia-410m --model EleutherAI/pythia-410m --revision step143000
run pythia-1.4b --model EleutherAI/pythia-1.4b --revision step143000
for f in /home/combust/llmspec_div/A0/step*.pt; do s=$(basename $f .pt); run A0_$s --ckpt $f; done
echo "$(date -Is) EXTRACT_ALL_DONE"

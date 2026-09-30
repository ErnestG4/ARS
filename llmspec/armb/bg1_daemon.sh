#!/bin/bash
# B-G1 scoring daemon (runs on spot inside tmux `claude`; ARMB_PREREG.md §3.6). Scores each A0 checkpoint at the shared
# steps once its sha256-verified .ok marker exists, in step order, appending to bg1/bg1_verdicts.jsonl (bg1_score.py a0).
# Exits when every step in STEPS has a verdict, or when ~/llmspec_armb/bg1/DAEMON_STOP exists. Polite: nice/ionice, 16 threads.
cd ~/llmspec_armb/code/llmspec/armb || exit 1
export BG1_DIR=~/llmspec_armb/bg1 BG1_TMP=~/tmp/claude HF_HOME=~/tmp/claude/hf OMP_NUM_THREADS=16 MKL_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16
PY=~/miniforge3/envs/llmspec/bin/python
STEPS="0 1 2 4 8 16 32 64 128 256 512 1000 2000 3000"
V=~/llmspec_armb/bg1/bg1_verdicts.jsonl; LOG=~/llmspec_armb/bg1_daemon.log
echo "=== $(date -Is) daemon start" >> $LOG
while true; do
  [ -e ~/llmspec_armb/bg1/DAEMON_STOP ] && { echo "=== $(date -Is) DAEMON_STOP" >> $LOG; exit 0; }
  pending=0
  for s in $STEPS; do
    grep -q "^{\"step\": $s," $V 2>/dev/null && continue
    pending=1
    f=$(printf "%s/step%05d.pt" ~/llmspec_armb/ckpt/A0 $s)
    [ -e "$f.ok" ] || break                      # strict step order: wait for the next checkpoint in sequence
    nice -n 19 ionice -c3 $PY -B -u bg1_score.py a0 "$f" $s >> $LOG 2>&1 || echo "=== $(date -Is) scorer rc=$? at step $s" >> $LOG
  done
  [ $pending = 0 ] && { echo "=== $(date -Is) all steps scored" >> $LOG; exit 0; }
  sleep 30
done

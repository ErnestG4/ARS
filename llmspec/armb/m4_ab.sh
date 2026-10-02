#!/usr/bin/env bash
# M4 hook A/B (Will's preconditions, 2026-10-01): halt A0, run 100 steps from the SAME resume.pt twice (hook off / on),
# compare, then relaunch the extension queue whatever the outcome. Log: armb/m4_ab.log.
cd "$(dirname "$0")" || exit 1
PY=/home/combust/fmexplorer/bin/python3
echo "$(date -Is) === M4 A/B start"
echo "m4 A/B" > ../STOP
T=$(ps -eo pid,args | grep '[t]rain.py A0 --stop 10000' | awk '{print $1}')
for i in $(seq 1 90); do kill -0 $T 2>/dev/null || break; sleep 2; done
kill -0 $T 2>/dev/null && { echo "trainer did not stop"; exit 2; }
sleep 3; rm -f ../STOP; rm -rf staging/A0_test; mkdir -p staging/A0_test staging/_m4ab
S=$($PY -c "import torch; print(torch.load('staging/A0/resume.pt', map_location='cpu', weights_only=False)['step'])")
STOP=$((S+100)); echo "$(date -Is) resume step $S, A/B to $STOP"
cp staging/A0/resume.pt staging/_m4ab/start.pt
# run A: hook off
cp staging/_m4ab/start.pt staging/A0_test/resume.pt; rm -f staging/A0_test/trainlog.jsonl
$PY train.py A0 --test --stop $STOP > train_A0_test.log 2>&1; echo "$(date -Is) run A exit $?"
cp staging/A0_test/resume.pt staging/_m4ab/ab_off.pt; cp staging/A0_test/trainlog.jsonl staging/_m4ab/trainlog_off.jsonl
# run B: hook on, sample GPU memory every 10 s
rm -rf staging/A0_test; mkdir -p staging/A0_test; cp staging/_m4ab/start.pt staging/A0_test/resume.pt
( while true; do nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits >> staging/_m4ab/gpu_mem_on.txt; sleep 10; done ) & MON=$!
LLMSPEC_M4=1 $PY train.py A0 --test --stop $STOP > train_A0_test.log 2>&1; echo "$(date -Is) run B exit $?"
kill $MON 2>/dev/null
cp staging/A0_test/resume.pt staging/_m4ab/ab_on.pt; cp staging/A0_test/trainlog.jsonl staging/_m4ab/trainlog_on.jsonl; cp staging/A0_test/m4_gram.jsonl staging/_m4ab/ 2>/dev/null
$PY m4_ab_compare.py; echo "$(date -Is) compare exit $?"
rm -rf staging/A0_test
echo "$(date -Is) relaunching ext_queue"; setsid nohup ./ext_queue.sh > ext_queue.log 2>&1 < /dev/null &
echo "$(date -Is) === M4 A/B done"

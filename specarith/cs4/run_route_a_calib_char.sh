#!/usr/bin/env bash
# Route (a) GUE calibration on char (fortieth round): two calibration processes sharing the GPU (replicates 0-99, 100-199)
# and one process for the full-size pipeline-identity checks (five files in turn). nice 10; resumable (re-run).
set -u
cd ~/tmp/claude/specarith/cs4
PY=~/tmp/claude/venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] route (a) GUE calibration: R 0-199 (2 procs) + pipeline-identity checks (1 proc)" >> ~/claude-work.log
nice -n 10 $PY route_a_calib.py run 0 100 results/calib/calib_A.jsonl > results/calib/calib_A.log 2>&1 &
A=$!
nice -n 10 $PY route_a_calib.py run 100 200 results/calib/calib_B.jsonl > results/calib/calib_B.log 2>&1 &
B=$!
for f in zeros_15146000.dat zeros_25646000.dat zeros_248246000.dat zeros_2373446000.dat zeros_10639046000.dat; do
  [ -f results/calib/pipeline_$f.json ] && continue
  n=$($PY -c "import route_a_read as R; print(int(round(R.spacing_count(\"$f\"))))")
  nice -n 10 $PY route_a_read.py pipeline $f $n results/calib/pipeline_$f.json ~/tmp/claude/synthetic_$f > results/calib/pipeline_$f.log 2>&1
  echo "exit=$?" > results/calib/pipeline_$f.exit
done
wait $A; echo "exit=$?" > results/calib/calib_A.exit
wait $B; echo "exit=$?" > results/calib/calib_B.exit
date -Is > results/calib/ALL_DONE
echo "$(date -Is) [CC specarith] route (a) GUE calibration: done" >> ~/claude-work.log

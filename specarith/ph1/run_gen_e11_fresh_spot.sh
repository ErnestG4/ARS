#!/usr/bin/env bash
# Phase 1 P5(ii): zeros of the E₁₁ even twists over the FRESH range d ∈ (4·10⁵, X′] (X′ declared in the seal before
# generation; thirty-third round). GENERATION ONLY. 30 chunks on 30 workers (memory: ~3.0 GB peak per worker, so 30 ≈ 90 GB
# of spot's 117 GB). Checkpointed per twist (gen_twists_e11.run): re-running this script resumes every chunk; a power
# cut costs only the twists in progress. A memory guard stops the workers by PID if MemAvailable < 15 GB. nice 10.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/ph1/run_gen_e11_fresh_spot.sh XPRIME [P]
set -u
X=$1
P=${2:-30}
D=~/tmp/claude/specarith/ph1
PY=~/miniforge3/envs/specarith/bin/python
cd "$D"
OUT=results/zeros_e11_fresh
mkdir -p "$OUT/logs" "$OUT/exits"
rm -f "$OUT/ALL_DONE" "$OUT"/exits/c*.txt
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ph1 E11 fresh-range zeros d in (4e5, $X]: 30 chunks, $P procs, nice 10 (checkpointed per twist)" >> ~/claude-work.log
(
  while [ ! -f "$OUT/ALL_DONE" ]; do
    avail=$(awk '/MemAvailable/ {print int($2/1048576)}' /proc/meminfo)
    if [ "$avail" -lt 15 ]; then
      W=$(ps -u combust -o pid=,args= | awk '/gen_twists_e11.py run 400000/ && !/awk/ && !/sh -c/ {print $1}')
      echo "$(date -Is) [CC specarith] E11 fresh memguard: MemAvailable ${avail} GB < 15; stopping workers $W (resumable)" >> ~/claude-work.log
      kill $W
      break
    fi
    sleep 10
  done
) &
GUARD=$!
seq 0 29 | xargs -P "$P" -I{} sh -c 'nice -n 10 '"$PY"' gen_twists_e11.py run 400000 '"$X"' {} 30 '"$OUT"' >> '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" > '"$OUT"'/exits/c{}.txt'
kill $GUARD 2>/dev/null
ok=$(cat "$OUT"/exits/c*.txt 2>/dev/null | grep -c "^exit=0$")
if [ "$ok" -ne 30 ]; then
  echo "$(date -Is) [CC specarith] ph1 E11 fresh-range: only $ok/30 chunks exited 0; NOT merged (re-run this script to resume)" >> ~/claude-work.log
  exit 1
fi
nice -n 10 $PY gen_twists_e11.py merge "$OUT" fresh > "$OUT/logs/merge.log" 2>&1; echo "exit=$?" > "$OUT/exits/merge.txt"
date -Is > "$OUT/ALL_DONE"
echo "$(date -Is) [CC specarith] ph1 E11 fresh-range zeros: done" >> ~/claude-work.log

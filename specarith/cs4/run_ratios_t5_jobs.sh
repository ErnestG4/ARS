#!/usr/bin/env bash
# ζ T₅ (ratios_t5.py zeta) for an EXPLICIT list of job indices (chunk i of 54 = job i), so the 54 jobs can be split
# between machines without overlap (2026-10-12: spot and the second box char@10.0.0.31). Checkpointed and restartable
# (finished jobs are skipped; a job resumes from results/ratios_t5/ckpt/jobNN.json if its key and code hash match).
# No merge here: the per-job t5_cNN.jsonl files are collected into one directory and merged there.
#   PY=<python> bash run_ratios_t5_jobs.sh TAG P JOB [JOB ...]      (run inside tmux `claude`; nice 10)
set -u
TAG=$1
P=$2
shift 2
D=~/tmp/claude/specarith/cs4
PY=${PY:-~/miniforge3/envs/ph6c/bin/python}
cd "$D"
OUT=results/ratios_t5
mkdir -p "$OUT/logs" "$OUT/ckpt"
rm -f "$OUT/DONE_$TAG"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
echo "$(date -Is) [CC specarith] ratios_t5 jobs [$TAG]: $* ($P procs, nice 10)" >> ~/claude-work.log
printf '%s\n' "$@" | xargs -P "$P" -I{} sh -c 'nice -n 10 '"$PY"' ratios_t5.py zeta {} 54 '"$OUT"' >> '"$OUT"'/logs/c{}.log 2>&1; echo "exit=$?" >> '"$OUT"'/logs/c{}.log'
date -Is > "$OUT/DONE_$TAG"
echo "$(date -Is) [CC specarith] ratios_t5 jobs [$TAG]: done" >> ~/claude-work.log

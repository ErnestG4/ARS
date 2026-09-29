#!/usr/bin/env bash
# B4 chain (sealed code, B4 amendment 2 bde3656): refs -> 70M witness -> every arm -> analysis. STOP-aware; resumable
# (every stage skips finished outputs). Logs to armb/b4_run.log; the analysis runs under checkrun.
cd "$(dirname "$0")/.."
PY=/home/combust/fmexplorer/bin/python3
log(){ echo "$(date -Is) $*" >> armb/b4_run.log; }
step(){ [ -e STOP ] && { log "STOP present: $(cat STOP)"; exit 3; }; log "start: $*"; "$@" >> armb/b4_run.log 2>&1; rc=$?; log "exit rc=$rc: $*"; [ $rc -eq 0 ] || exit $rc; }
step $PY armb/b4_extract.py refs
[ -e results/stage3_witness_pythia-70m.json ] || step env LLMSPEC_MODEL=pythia-70m $PY stage3_witness.py
for a in A0 A1 A2 M0s1 M0s2; do step $PY armb/b4_extract.py arm $a; done
step ../checkrun.sh armb/b4_analyze.py all
log "B4 chain complete"

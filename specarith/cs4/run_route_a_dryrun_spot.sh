#!/usr/bin/env bash
# Route (a) dry run (rounds 43-45), under the interpreter the seal pins (spot, ph6c): dry-run seal pinning the stand-ins'
# md5s, read() twice in separate processes, then compare (bit-identical or VOID) and the dry-run expectations.
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_route_a_dryrun_spot.sh
set -u
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
S=results/dryrun_synth
echo "$(date -Is) [CC specarith] route (a) dry run: prepare + read x2 + record" >> ~/claude-work.log
nice -n 10 $PY route_a_sealread.py dryrun_prepare $S > results/dryrun_prepare.log 2>&1 || exit 1
for r in run1 run2; do
  nice -n 10 $PY route_a_sealread.py dryrun_read $r $S > results/dryrun_$r.log 2>&1; echo "exit=$?" > results/dryrun_$r.exit
done
nice -n 10 $PY route_a_sealread.py dryrun_record $S > results/dryrun.log 2>&1; echo "exit=$?" > results/dryrun.exit
echo "$(date -Is) [CC specarith] route (a) dry run: done" >> ~/claude-work.log

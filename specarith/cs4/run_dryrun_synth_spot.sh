#!/usr/bin/env bash
# Route (a) dry run: place the five CUE stand-ins at F3 geometry (Platt format), then read() them under a dry-run seal.
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
D=results/dryrun_synth
echo "$(date -Is) [CC specarith] route (a) dry run: synth 5 stand-ins (5 procs)" >> ~/claude-work.log
printf "%s\n" zeros_15146000.dat zeros_25646000.dat zeros_248246000.dat zeros_2373446000.dat zeros_10639046000.dat | xargs -P 5 -I{} sh -c "nice -n 10 $PY route_a_sealread.py synth $D {} > $D/{}.synth.log 2>&1; echo exit=\$? > $D/{}.synth.exit"
echo "$(date -Is) [CC specarith] route (a) dry run: read (5 procs)" >> ~/claude-work.log
nice -n 10 $PY route_a_sealread.py dryrun $D > results/dryrun.log 2>&1; echo exit=$? > results/dryrun.exit
echo "$(date -Is) [CC specarith] route (a) dry run: done" >> ~/claude-work.log

#!/usr/bin/env bash
# jobs.sh -- structural fix for the repeated pgrep self-match (Will, 2026-10-03): every long job writes a pid file at
# launch; every check reads that file and verifies the binary through /proc/<pid>/exe. Never pgrep -f.
#
#   ./jobs.sh launch <name> <cmd...>   detached (setsid nohup), log jobs/<name>.log, pid file jobs/<name>.pid,
#                                      jobs/<name>.exe = realpath of the launched binary (resolved after start)
#   ./jobs.sh alive <name>             exit 0 iff the pid is alive AND /proc/<pid>/exe resolves to the recorded binary
#   ./jobs.sh wait <name> [secs]       poll alive every <secs> (default 60) until it dies; prints the log tail
#   ./jobs.sh status                   one line per pid file
#   ./jobs.sh any-trainer              exit 0 iff any live pid whose /proc/<pid>/exe is the venv python has
#                                      'train.py' in /proc/<pid>/cmdline (GPU-trainer check for chains)
set -u
cd "$(dirname "$0")"; J=jobs; mkdir -p $J
PY=/home/combust/fmexplorer/bin/python3
case "${1:-status}" in
launch)
  name=$2; shift 2
  setsid nohup "$@" > $J/$name.log 2>&1 &
  pid=$!; echo $pid > $J/$name.pid; sleep 1
  readlink -f /proc/$pid/exe > $J/$name.exe 2>/dev/null || echo "?" > $J/$name.exe
  echo "launched $name pid $pid exe $(cat $J/$name.exe)" ;;
alive)
  name=$2; pid=$(cat $J/$name.pid 2>/dev/null) || exit 1; [ -d /proc/$pid ] || exit 1
  exe=$(readlink -f /proc/$pid/exe 2>/dev/null); want=$(cat $J/$name.exe 2>/dev/null)
  [ -n "$exe" ] && [ "$exe" = "$want" ] ;;
wait)
  name=$2; s=${3:-60}; while ./jobs.sh alive $name; do sleep $s; done
  echo "$name ended $(date -Is)"; tail -3 $J/$name.log 2>/dev/null | cut -c1-120 ;;
any-trainer)
  for p in /proc/[0-9]*; do pid=${p#/proc/}
    [ "$(readlink -f $p/exe 2>/dev/null)" = "$(readlink -f $PY)" ] || continue
    tr '\0' ' ' < $p/cmdline 2>/dev/null | grep -q ' train.py' && { echo "trainer pid $pid"; exit 0; }
  done; exit 1 ;;
status)
  for f in $J/*.pid; do [ -e "$f" ] || continue; n=$(basename $f .pid)
    if ./jobs.sh alive $n; then echo "$n: ALIVE pid $(cat $f)"; else echo "$n: dead"; fi; done ;;
esac

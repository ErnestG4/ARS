#!/usr/bin/env bash
# Round 80: bit-identity of pilot chunks that both runners computed (the later write replaced the earlier copy, so each
# is recomputed in the same environment into a separate dir and compared field by field, wall_s excluded).
# Run inside tmux `claude`:  bash ~/tmp/claude/specarith/cs4/run_n6c_dupcheck_spot.sh NPROC CHUNK...
set -u
NPROC=$1; shift
cd ~/tmp/claude/specarith/cs4 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python
O=results/n6c/pilot_dupcheck; mkdir -p $O
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PY O
echo "$(date -Is) [CC specarith] n6c pilot dupcheck: $# chunks ($NPROC procs)" >> ~/claude-work.log
printf "%s\n" "$@" | xargs -P "$NPROC" -I{} sh -c 'nice -n 10 $PY n6c_conn.py task zeta 15.75 100 6.0 8 {} $O >> $O/tasks.log 2>&1 || echo {} >> $O/failed.txt'
$PY - "$O" "$@" > $O/compare.log 2>&1 <<'PY'
import json, sys
o, chunks = sys.argv[1], sys.argv[2:]
same = 0
for c in chunks:
    f = "t_zeta_15.75_100_6.0_8_%04d.json" % int(c)
    a, b = json.load(open("results/n6c/pilot/" + f)), json.load(open(o + "/" + f))
    a.pop("wall_s"); b.pop("wall_s")
    eq = a == b
    same += eq
    print(c, "bit-identical" if eq else "DIFFERS", "" if eq else {k: (a[k], b[k]) for k in a if a[k] != b[k]})
print(f"{same}/{len(chunks)} bit-identical")
PY
echo "exit=$?" > $O/compare.exit
date -Is > $O/ALL_DONE

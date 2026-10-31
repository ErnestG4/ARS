#!/bin/bash
# GEO1 Peter seal: the fresh range on spot (GEO1_PETER_SEAL.md §8). The operator load-checks before launch (PLL work and
# ARSv2 share spot). pari: t = 1,000,001 … 3,000,000 in 200 chunks of 10⁴, NP processes (default 16); cost checks at the
# first chunk and at 25 / 50 / 75 % (model 6.0 ms per t; stop above 1.25×). hind: the 200 sealed samples in 20 chunks
# (qfbclassno + CF period parity). merge, hashes. Nothing here computes a statistic. Usage: run_peter_fresh_spot.sh OUT [NP]
O=$1
NP=${2:-16}
cd ~/tmp/claude/specarith/geo1 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python            # numpy (merge, cost checks)
PP=~/miniforge3/envs/specarith/bin/python       # cypari2 (pari, hind)
mkdir -p $O/pari $O/hind
echo "$(date -Is) [CC specarith] geo1 peter fresh: start (NP=$NP)" >> ~/claude-work.log
for k in $(seq 0 199); do echo $k $((1000001 + k * 10000)) $((1000000 + (k + 1) * 10000)); done > $O/pari/chunks.txt
xargs -P $NP -n 3 sh -c 'nice -n 10 '$PP' geo1.py pari $1 $2 '$O'/pari/part_$(printf %03d $0).npz > '$O'/pari/log_$0.txt 2>&1; echo $0 $? >> '$O'/pari/done.txt' < $O/pari/chunks.txt &
XP=$!
check() {
  while [ $(cat $O/pari/done.txt 2>/dev/null | wc -l) -lt $2 ]; do sleep 20; done
  $PY - $O $1 <<'PYEOF'
import sys
O, lab = sys.argv[1], sys.argv[2]
ch = {int(l.split()[0]): (int(l.split()[1]), int(l.split()[2])) for l in open(f"{O}/pari/chunks.txt")}
done = [int(l.split()[0]) for l in open(f"{O}/pari/done.txt")]
model = sum(ch[k][1] - ch[k][0] + 1 for k in done) * 6.0e-3
cpu = sum(float(open(f"{O}/pari/part_{k:03d}.npz.cpu").read()) for k in done)
print(f"{lab}: {len(done)} chunks, cpu/model = {cpu / model:.3f}", flush=True)
sys.exit(3 if cpu > 1.25 * model else 0)
PYEOF
}
for spec in "first 1" "25 50" "50 100" "75 150"; do
  set -- $spec
  check $1 $2 >> $O/pari/checks.txt || { echo "pari cost above 1.25x at $1" > $O/STOPPED; kill $XP; exit 3; }
done
wait $XP
awk '$2 != 0' $O/pari/done.txt | grep -q . && { echo "a pari chunk failed" > $O/STOPPED; exit 1; }
for k in $(seq 0 19); do echo $k $((k * 10)) $(((k + 1) * 10)); done > $O/hind/chunks.txt
xargs -P $NP -n 3 sh -c 'nice -n 10 '$PP' geo1_peter_seal.py hind HSAMPLE.json $1 $2 '$O'/hind/hind_$(printf %02d $0).json > '$O'/hind/log_$0.txt 2>&1; echo $0 $? >> '$O'/hind/done.txt' < $O/hind/chunks.txt
awk '$2 != 0' $O/hind/done.txt | grep -q . && { echo "a hind chunk failed" > $O/STOPPED; exit 1; }
$PY geo1.py merge $O/fresh_3e6.npz $O/pari/part_*.npz || { echo "merge failed" > $O/STOPPED; exit 1; }
sha256sum $O/fresh_3e6.npz $O/hind/hind_*.json > $O/HASHES.txt
echo "$(date -Is) [CC specarith] geo1 peter fresh: done" >> ~/claude-work.log
date -Is > $O/ALL_DONE

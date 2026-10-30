#!/bin/bash
# GEO1 Step 1 on spot (GEO1_STEP1_PLAN.md §2–§3). Load check by the operator before launch (ARSv2 shares spot).
# words (T_w = 3e4, 20 numba threads; cost checks inside), forms (t ≤ 40), list (t = 6), pari (t ≤ 1e6 in 100 chunks,
# 20 processes; cost checks at the first chunk and at 25 / 50 / 75%: model 5.2 ms per t, stop above 1.25x), merge,
# then the gates twice in separate processes and cmp. Usage: run_geo1_spot.sh OUT_DIR
O=$1
cd ~/tmp/claude/specarith/geo1 || exit 1
PY=~/miniforge3/envs/ph6c/bin/python            # numba, mpmath (words, forms, list, merge, gates)
PP=~/miniforge3/envs/specarith/bin/python       # cypari2 (pari route)
mkdir -p $O/pari
echo "$(date -Is) [CC specarith] geo1 step1: start" >> ~/claude-work.log
NUMBA_NUM_THREADS=20 nice -n 10 $PY geo1.py words 3e4 $O/words_3e4.npz > $O/words.log 2>&1 || { echo "words failed" > $O/STOPPED; exit 1; }
nice -n 10 $PY geo1.py forms 40 $O/forms_40.json > $O/forms.log 2>&1 || { echo "forms failed" > $O/STOPPED; exit 1; }
nice -n 10 $PY geo1.py list 6 $O/list_t6.json > $O/list.log 2>&1 || { echo "list failed" > $O/STOPPED; exit 1; }
for k in $(seq 0 99); do echo $k $((3 + k * 10000)) $(( k == 99 ? 1000000 : 2 + (k + 1) * 10000 )); done > $O/pari/chunks.txt
xargs -P 20 -n 3 sh -c 'nice -n 10 '$PP' geo1.py pari $1 $2 '$O'/pari/part_$(printf %03d $0).npz > '$O'/pari/log_$0.txt 2>&1; echo $0 $? >> '$O'/pari/done.txt' < $O/pari/chunks.txt &
XP=$!
check() {
  while [ $(cat $O/pari/done.txt 2>/dev/null | wc -l) -lt $2 ]; do sleep 20; done
  $PY - $O $1 <<'PYEOF'
import sys
O, lab = sys.argv[1], sys.argv[2]
ch = {int(l.split()[0]): (int(l.split()[1]), int(l.split()[2])) for l in open(f"{O}/pari/chunks.txt")}
done = [int(l.split()[0]) for l in open(f"{O}/pari/done.txt")]
model = sum(ch[k][1] - ch[k][0] + 1 for k in done) * 5.2e-3
cpu = sum(float(open(f"{O}/pari/part_{k:03d}.npz.cpu").read()) for k in done)
print(f"{lab}: {len(done)} chunks, cpu/model = {cpu / model:.3f}", flush=True)
sys.exit(3 if cpu > 1.25 * model else 0)
PYEOF
}
for spec in "first 1" "25 25" "50 50" "75 75"; do
  set -- $spec
  check $1 $2 >> $O/pari/checks.txt || { echo "pari cost above 1.25x at $1" > $O/STOPPED; kill $XP; exit 3; }
done
wait $XP
awk '$2 != 0' $O/pari/done.txt | grep -q . && { echo "a pari chunk failed" > $O/STOPPED; exit 1; }
$PY geo1.py merge $O/pari_1e6.npz $O/pari/part_*.npz || { echo "merge failed" > $O/STOPPED; exit 1; }
sha256sum $O/words_3e4.npz $O/pari_1e6.npz $O/forms_40.json $O/list_t6.json > $O/HASHES.txt
for i in 1 2; do
  $PY geo1_analyze.py $O/words_3e4.npz $O/pari_1e6.npz $O/forms_40.json $O/list_t6.json $O/GATES$i.json > $O/gates$i.log 2>&1
done
cmp $O/GATES1.json $O/GATES2.json > $O/cmp.txt 2>&1; echo "exit=$?" >> $O/cmp.txt
echo "$(date -Is) [CC specarith] geo1 step1: done" >> ~/claude-work.log
date -Is > $O/ALL_DONE

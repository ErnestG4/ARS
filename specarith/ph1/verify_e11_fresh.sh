#!/usr/bin/env bash
# Verify the E11 fresh range on spot against the pinned manifest: 30 chunk exits + merge exit are 0, every chunk file's
# sha256 equals the manifest's, and the d set is exactly gen_twists_e11.items(4e5, 1.1e6). Exit 0 only if all hold.
set -u
M=$(cat specarith/ph1/results/zeros_e11_fresh_MANIFEST.json)
ssh -o BatchMode=yes spot "cd ~/tmp/claude/specarith/ph1 && MANIFEST='$M' ~/miniforge3/envs/specarith/bin/python -c '
import json, glob, hashlib, os, sys, gen_twists_e11 as G
m = json.loads(os.environ[\"MANIFEST\"])[\"fresh\"]
D = \"results/zeros_e11_fresh\"
ex = [open(f).read().strip() for f in sorted(glob.glob(D + \"/exits/c*.txt\"))] + [open(D + \"/exits/merge.txt\").read().strip()]
files = sorted(glob.glob(D + \"/e11_*.jsonl\"))
sh = {os.path.basename(f): hashlib.sha256(open(f, \"rb\").read()).hexdigest() for f in files}
ds = sorted(json.loads(l)[\"d\"] for f in files for l in open(f))
ok = dict(exits=len(ex) == 31 and all(e == \"exit=0\" for e in ex), sha=sh == m[\"files\"],
          dset=ds == sorted(G.items(400000, 1100000)), n_L=len(ds) == m[\"n_L\"] == 12917)
print(ok)
sys.exit(0 if all(ok.values()) else 1)
'"

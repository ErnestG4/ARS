"""GEO-TOT1 re-enumeration check (GEOTOT1_SEAL.md §8): 4 chunks, chosen by numpy default_rng(20261027).choice(200, 4,
replace=False), enumerated again; every array must equal the merged first run's slice (np.array_equal).

  python geotot1_reenum.py ENUM_DIR MERGED_NPZ OUT_DIR OUT_JSON
"""
import json
import os
import subprocess
import sys

import numpy as np

from geotot1 import KEYS

SEED = 20261027


def main(enum_dir, merged, out_dir, out):
    ch = {int(l.split()[0]): (int(l.split()[1]), int(l.split()[2])) for l in open(f"{enum_dir}/chunks.txt")}
    pick = sorted(int(k) for k in np.random.default_rng(SEED).choice(len(ch), 4, replace=False))
    os.makedirs(out_dir, exist_ok=True)
    env = dict(os.environ, NUMBA_NUM_THREADS="1")
    procs = [subprocess.Popen(["nice", "-n", "10", sys.executable, "geotot1.py", "enum", str(ch[k][0]), str(ch[k][1]),
                               f"{out_dir}/re_{k:03d}.npz"], env=env) for k in pick]
    rc = [p.wait() for p in procs]
    d = np.load(merged)
    res = {}
    for k in pick:
        r = np.load(f"{out_dir}/re_{k:03d}.npz")
        i0, i1 = ch[k][0] - 2, ch[k][1] - 2 + 1
        res[f"{k:03d}"] = dict(q=list(ch[k]), equal={key: bool(np.array_equal(r[key], d[key][i0:i1]))
                                                       for key in ("q",) + KEYS})
    ok = all(c == 0 for c in rc) and all(all(v["equal"].values()) for v in res.values())
    json.dump(dict(seed=SEED, chunks=pick, exit=rc, results=res, PASS=ok), open(out, "w"), indent=1)
    print("chunks", pick, "PASS", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))

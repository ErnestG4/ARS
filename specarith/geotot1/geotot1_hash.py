"""GEO-TOT1 output hashes (GEOTOT1_SEAL.md §7–8), written before any statistic of q > 2000 is computed or displayed.

  python geotot1_hash.py ENUM_DIR MERGED_NPZ Q OUT_JSON

Lists the sha256 of every part file and of the merged file, and a sha256 of each merged array's bytes (with dtype and
shape: .npz bytes carry zip timestamps, so a re-enumeration is compared on the arrays). Asserts that the merged q column is
exactly 2 … Q and that every chunk exited 0. Also the total chunk CPU against the cost model. Prints no array content.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

from geotot1 import KEYS


def fsha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main(enum_dir, merged, Q, out):
    ch = {int(l.split()[0]): (int(l.split()[1]), int(l.split()[2])) for l in open(f"{enum_dir}/chunks.txt")}
    done = {int(l.split()[0]): int(l.split()[1]) for l in open(f"{enum_dir}/done.txt")}
    assert sorted(done) == sorted(ch) and all(v == 0 for v in done.values())
    parts = {f"part_{k:03d}.npz": fsha(f"{enum_dir}/parts/part_{k:03d}.npz") for k in sorted(ch)}
    d = np.load(merged)
    assert np.array_equal(d["q"], np.arange(2, Q + 1, dtype=np.int64))
    arrays = {k: dict(dtype=str(d[k].dtype), shape=list(d[k].shape),
                      sha256=hashlib.sha256(np.ascontiguousarray(d[k]).tobytes()).hexdigest()) for k in ("q",) + KEYS}
    mu = 12 * math.log(2) / math.pi ** 2
    model = sum((q - 1) * (mu * math.log(q) + 1.0) for q in range(2, Q + 1)) * 6.06e-9 * 2.3
    cpu = sum(float(open(f"{enum_dir}/parts/part_{k:03d}.npz.cpu").read()) for k in ch)
    res = dict(Q=Q, n_chunks=len(ch), chunks={f"{k:03d}": list(ch[k]) for k in sorted(ch)}, part_sha256=parts,
               merged=os.path.basename(merged), merged_sha256=fsha(merged), merged_bytes=os.path.getsize(merged),
               array_sha256=arrays, cpu_core_h=cpu / 3600, model_core_h=model / 3600, cost_ratio=cpu / model,
               checks=open(f"{enum_dir}/checks.txt").read().splitlines())
    json.dump(res, open(out, "w"), indent=1)
    print(f"{len(parts)} parts, merged {res['merged_bytes']} bytes sha256 {res['merged_sha256']}; "
          f"cpu {res['cpu_core_h']:.2f} core-h = {res['cost_ratio']:.3f}x model")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], int(float(sys.argv[3])), sys.argv[4]))

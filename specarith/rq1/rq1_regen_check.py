"""RQ1 version-drift check (round 88): regenerate ℤ[√2] archive segments with the current code and compare their
sha256 with the manifest. Segments 0 and 999, plus 10 drawn by a seeded RNG from 1…998. Only file hashes are compared;
no angle is read from the archive.

  python rq1_regen_check.py list                     the segment list
  python rq1_regen_check.py task K OUT_DIR           regenerate segment K into OUT_DIR (rq1_archive.task)
  python rq1_regen_check.py check OUT_DIR MANIFEST OUT_JSON
"""
import hashlib
import json
import os
import sys

import numpy as np

import rq1_archive as A


def segments():
    rng = np.random.default_rng(8803)
    return [0, 999] + sorted(int(k) for k in rng.choice(np.arange(1, 999), 10, replace=False))


def check(out_dir, manifest, out):
    man = {s["k"]: s["sha256"] for s in json.load(open(manifest))["segments"]}
    rows = []
    for k in segments():
        h = hashlib.sha256(open(os.path.join(out_dir, f"seg_{k:04d}.npy"), "rb").read()).hexdigest()
        rows.append(dict(k=k, sha256=h, manifest=man[k], identical=h == man[k]))
    res = dict(seed=8803, segments=rows, all_identical=all(r["identical"] for r in rows),
               rq1_angles_sha256=hashlib.sha256(open("rq1_angles.py", "rb").read()).hexdigest(),
               rq1_archive_sha256=hashlib.sha256(open("rq1_archive.py", "rb").read()).hexdigest())
    json.dump(res, open(out, "w"), indent=1)
    print([r["k"] for r in rows], "all identical:", res["all_identical"])
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "list":
        print("\n".join(map(str, segments())))
    elif sys.argv[1] == "task":
        sys.exit(A.task(int(sys.argv[2]), sys.argv[3]))
    else:
        sys.exit(check(sys.argv[2], sys.argv[3], sys.argv[4]))

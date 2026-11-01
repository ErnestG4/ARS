"""FN1 §9.F rehearsal: synthetic stand-in archives for the seven w = 2 fields, in the real archive format (int32 rows in
segments, MANIFEST.json with per-segment sha256). The rows are seeded random (x, y) pairs, not split primes, so the
dry read exercises the loader, the θ map, the sort, var_stream, the rank test, the verdict path and the cmp without
touching any fresh field data. The real ℤ[√2], ℤ[i] and ℤ[ω] archives are read at the dry X (already-seen prefixes).

  python fn1_dry_archives.py OUT_ROOT N_ROWS
"""
import hashlib
import json
import os
import sys

import numpy as np

FIELDS = [-7, -8, -11, -19, -43, -67, -163]
SEGROWS = 10 ** 7


def main(root, n_rows):
    out = {}
    for i, D in enumerate(FIELDS):
        d = os.path.join(root, f"dry_D{-D}")
        os.makedirs(d, exist_ok=True)
        rng = np.random.default_rng([20261115, i])
        segs, got, k = [], 0, 0
        while got < n_rows:
            m = min(SEGROWS, n_rows - got)
            rows = rng.integers(1, 10 ** 5, size=(m, 2)).astype(np.int32)
            path = os.path.join(d, f"seg_{k:04d}.npy")
            np.save(path, rows)
            segs.append(dict(k=k, rows=int(m), sha256=hashlib.sha256(open(path, "rb").read()).hexdigest()))
            got += m
            k += 1
        json.dump(dict(label="FN1 DRY-RUN synthetic stand-in (random rows, not primes)", D=D, rows=got, segments=segs),
                  open(os.path.join(d, "MANIFEST.json"), "w"), indent=1)
        out[str(D)] = d
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], int(float(sys.argv[2]))))

# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1-h2 §9.F fixtures: synthetic stand-ins for the 18 h = 2 archives, for the dry double read only. No primes, no
arithmetic data: each segment k = 0 … 199 (hi = (k + 1)·10⁸) holds ROWS_PER_SEG seeded random int32 (x, y) pairs in
[1, 30000] (seed 20261104 + 1000·|D| + k), in the archive's format, with a MANIFEST.json of the archive's shape
(sha256 per segment). The fixture is 1/10 of the real principal count per segment (≈ 1.1·10⁵ rows), so the dry read's
h = 2 part runs at ≈ 1/10 of the real load; the h = 1 part runs at full size on the real (seen) h = 1 archives.

  python fn1h2_fixtures.py OUT_ROOT     → OUT_ROOT/archive_D{|D|}/seg_KKKK.npy + MANIFEST.json
"""
import hashlib, json, os, sys

import numpy as np

import fn1h2_archive as H

ROWS_PER_SEG = 110_000


def main(root):
    for D in H.FIELDS:
        d = os.path.join(root, f"archive_D{-D}")
        os.makedirs(d, exist_ok=True)
        segs = []
        for k in range(200):
            rng = np.random.default_rng(20261104 + 1000 * (-D) + k)
            xy = rng.integers(1, 30001, size=(ROWS_PER_SEG, 2)).astype(np.int32)
            p = os.path.join(d, f"seg_{k:04d}.npy")
            np.save(p, xy)
            segs.append(dict(k=k, lo=k * 10 ** 8, hi=(k + 1) * 10 ** 8, rows=ROWS_PER_SEG,
                             sha256=hashlib.sha256(open(p, "rb").read()).hexdigest(), integrity=True))
        json.dump(dict(label=f"FN1-h2 SYNTHETIC FIXTURE D = {D} (dry run only; random rows, not primes)", D=D,
                       X=2 * 10 ** 10, segment=10 ** 8, rows=200 * ROWS_PER_SEG, segments=segs, fixture=True),
                  open(os.path.join(d, "MANIFEST.json"), "w"), indent=1)
        print(D, "done", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

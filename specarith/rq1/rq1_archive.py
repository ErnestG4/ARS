"""RQ1 Step 2 archive (round 85): ℤ[√2] reduced generators for every split prime p < X, in 1e8-wide p-segments.
Generation, integrity and hashing only; no statistic of the angles is computed here.

  python rq1_archive.py jobs X [FIELD]                segment list (k, lo, hi) and the cost-model prediction per task
  python rq1_archive.py task K OUT_DIR [FIELD]        segment k → OUT_DIR/seg_KKKK.npy (int32 rows)
  python rq1_archive.py manifest OUT_DIR X [FIELD]    per-segment sha256 + row counts + integrity → OUT_DIR/MANIFEST.json
FIELD = zs2 (ℤ[√2], default) or zi (ℤ[i], round 86; Cornacchia pairs (u, v), 0 < u < v, u² + v² = p).

Cost model (N6-2_PLAN.md §10 form): local µs per split prime t(p) ≈ 9 (p ~ 1e7), 20 (1e10), 22 (1e11) — log-linear
interpolation; spot factor 2.3 for this task class at 28 processes (round 87 recalibration; 4.1 overpredicted by 1/0.56); split primes in [lo, hi) ≈ (hi − lo)/(2 ln mid).
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

import rq1_angles as R

SEG = 10 ** 8
SPOT = 2.3                                        # archive task class, recalibrated in round 87 (was 4.1: measured 0.56× on the ℤ[√2] run)


ZI_FACTOR = 0.82                                 # ℤ[i] µs per prime ÷ ℤ[√2] (measured locally: 16.5 vs 20.2 µs at 1e10, 17.2 vs 22.3 at 1e11)


def t_local_us(p, field="zs2"):
    pts = [(7.0, 9.0), (10.0, 20.0), (11.0, 22.3)]
    x = math.log10(max(p, 1e7))
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1:
            return (y0 + (y1 - y0) * (x - x0) / (x1 - x0)) * (ZI_FACTOR if field == "zi" else 1.0)
    return pts[-1][1] * (ZI_FACTOR if field == "zi" else 1.0)


def jobs(X, field="zs2"):
    out = []
    for k in range(int(X // SEG)):
        lo, hi = k * SEG, (k + 1) * SEG
        mid = (lo + hi) / 2
        n = (hi - max(lo, 3)) / (2 * math.log(mid))
        out.append((k, lo, hi, n * t_local_us(mid, field) * 1e-6 * SPOT))
    return out


def task(k, out_dir, field="zs2"):
    path = os.path.join(out_dir, f"seg_{k:04d}.npy")
    if os.path.exists(path):
        return 0
    t = time.time()
    ab = (R.gen_segment_zi if field == "zi" else R.gen_segment)(k * SEG, (k + 1) * SEG)
    tmp = f"{path}.{os.getpid()}.part.npy"
    np.save(tmp, ab)
    os.replace(tmp, path)
    print(k, len(ab), round(time.time() - t, 1), flush=True)
    return 0


def manifest(out_dir, X, field="zs2"):
    segs, total, h_all = [], 0, hashlib.sha256()
    for k, lo, hi, _ in jobs(X, field):
        path = os.path.join(out_dir, f"seg_{k:04d}.npy")
        raw = open(path, "rb").read()
        h = hashlib.sha256(raw).hexdigest()
        h_all.update(bytes.fromhex(h))
        ab = np.load(path)
        a, b = ab[:, 0].astype(np.int64), ab[:, 1].astype(np.int64)
        if field == "zi":
            p = a * a + b * b
            ref = R.primes_in(max(lo, 2), hi)
            ref = ref[ref % 4 == 1]
            ok = bool(np.array_equal(p, ref) and np.all(a > 0) and np.all(b > a))
        else:
            p = np.abs(a * a - 2 * b * b)
            ref = R.primes_in(max(lo, 2), hi)
            ref = ref[(ref % 8 == 1) | (ref % 8 == 7)]
            ok = bool(np.array_equal(p, ref) and np.all(a > 0) and np.all(b >= 0))   # norms = the split primes, in order
        segs.append(dict(k=k, lo=lo, hi=hi, rows=int(len(ab)), sha256=h, integrity=ok))
        total += len(ab)
    m = dict(label=f"RQ1 angle archive ({field}); generation + integrity + hashes only, no statistic", field=field,
             X=X, segment=SEG, rows=total, segments=segs, all_integrity=all(s["integrity"] for s in segs),
             sha256_of_segment_hashes=h_all.hexdigest(),
             X_1e10_rows=int(sum(s["rows"] for s in segs if s["hi"] <= 10 ** 10)))
    json.dump(m, open(os.path.join(out_dir, "MANIFEST.json"), "w"), indent=1)
    print(total, m["all_integrity"], m["sha256_of_segment_hashes"])
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "jobs":
        for j in jobs(int(float(sys.argv[2])), *(sys.argv[3:4] or ["zs2"])):
            print(j[0], f"{j[3]:.0f}")
        sys.exit(0)
    if sys.argv[1] == "task":
        sys.exit(task(int(sys.argv[2]), sys.argv[3], *(sys.argv[4:5] or ["zs2"])))
    if sys.argv[1] == "manifest":
        sys.exit(manifest(sys.argv[2], int(float(sys.argv[3])), *(sys.argv[4:5] or ["zs2"])))

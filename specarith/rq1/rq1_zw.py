"""RQ1-c (round 95): the ℤ[ω] angle archive (ω = e^{2πi/3}). New module, so the running ℤ[√2] / ℤ[i] archive code is not
touched. Generation, integrity and hashes only; no statistic of the angles is computed here.

Split rule: p ≡ 1 (mod 3). Each such p is u² + 3v² with u, v > 0, uniquely (class number 1 of ℤ[√−3]); π = u + v√−3
lies in ℤ[ω] (√−3 = 1 + 2ω) and has norm p. Inert p ≡ 2 (mod 3) and the ramified prime (√−3) are excluded, as in the
ℤ[√2] and ℤ[i] archives (N = prime ideals above split primes).
θ map: θ(π) = (arg π mod π/3)/(π/3) ∈ [0, 1) (34d's convention θ ∈ [0, π/3), normalised). The six unit multiples of π
(sixth roots of unity) leave θ unchanged; the conjugate ideal π̄ sits at 1 − θ (the mirror). The archive stores
(u, v) as int32 rows; θ = (atan2(√3·v, u) mod π/3)/(π/3) per row, plus the mirror 1 − θ.
Cornacchia for u² + 3v² = p: r₀² ≡ −3 (mod p) with p/2 < r₀ < p; Euclid on (p, r₀) until r < √p; u = r,
v = √((p − u²)/3), asserted.

  python rq1_zw.py jobs X                       segment list (k, model seconds)
  python rq1_zw.py task K OUT_DIR               segment k → OUT_DIR/seg_KKKK.npy
  python rq1_zw.py manifest OUT_DIR X           per-segment sha256, rows, integrity → OUT_DIR/MANIFEST.json
Cost model: rq1_archive.py's ℤ[i] curve (N6-2_PLAN §10) × 16.2/19.2, the ℤ[ω] / ℤ[i] ratio of local µs per prime
measured at 1.011·10¹² (outside both archives), with the ℤ[i] class's spot factor 2.8 (the same Cornacchia structure).
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

import rq1_angles as R
import rq1_archive as A

SEG = 10 ** 8
SPOT = 2.8
ZW_OVER_ZI = 16.2 / 19.2                            # µs per prime at 1.011e12, ℤ[ω] / ℤ[i], both measured locally (round 95)


def gen_segment_zw(lo, hi):
    ps = R.primes_in(lo, hi)
    ps = ps[ps % 3 == 1]
    out = np.empty((len(ps), 2), np.int32)
    for i, p in enumerate(ps.tolist()):
        r = R.sqrt_mod(p - 3, p)                      # r² ≡ −3 (mod p)
        if 2 * r < p:
            r = p - r
        a, b = p, r
        lim = math.isqrt(p)
        while b > lim:
            a, b = b, a % b
        u = b
        t = p - u * u
        if t % 3:
            raise ArithmeticError(("cornacchia mod 3", p, u))
        v = math.isqrt(t // 3)
        if u * u + 3 * v * v != p or u <= 0 or v <= 0:
            raise ArithmeticError(("cornacchia", p, u, v))
        out[i] = u, v
    return out


def thetas_zw(uv):
    u, v = uv[:, 0].astype(np.float64), uv[:, 1].astype(np.float64)
    ang = np.arctan2(math.sqrt(3.0) * v, u)          # ∈ (0, π/2)
    return np.mod(ang, math.pi / 3) / (math.pi / 3)


def jobs(X):
    out = []
    for k in range(int(X // SEG)):
        lo, hi = k * SEG, (k + 1) * SEG
        n = (hi - max(lo, 3)) / (2 * math.log((lo + hi) / 2))
        out.append((k, n * A.t_local_us((lo + hi) / 2, "zi") * ZW_OVER_ZI * 1e-6 * SPOT))
    return out


def task(k, out_dir):
    path = os.path.join(out_dir, f"seg_{k:04d}.npy")
    if os.path.exists(path):
        return 0
    t = time.time()
    uv = gen_segment_zw(k * SEG, (k + 1) * SEG)
    tmp = f"{path}.{os.getpid()}.part.npy"
    np.save(tmp, uv)
    os.replace(tmp, path)
    print(k, len(uv), round(time.time() - t, 1), flush=True)
    return 0


def _check(args):
    out_dir, k = args
    lo, hi = k * SEG, (k + 1) * SEG
    path = os.path.join(out_dir, f"seg_{k:04d}.npy")
    raw = open(path, "rb").read()
    uv = np.load(path)
    u, v = uv[:, 0].astype(np.int64), uv[:, 1].astype(np.int64)
    ref = R.primes_in(max(lo, 2), hi)
    ref = ref[ref % 3 == 1]
    ok = bool(np.array_equal(u * u + 3 * v * v, ref) and np.all(u > 0) and np.all(v > 0))
    return dict(k=k, lo=lo, hi=hi, rows=int(len(uv)), sha256=hashlib.sha256(raw).hexdigest(), integrity=ok)


def manifest(out_dir, X):
    from multiprocessing import Pool
    args = [(out_dir, k) for k, _ in jobs(X)]
    nproc = int(os.environ.get("MANIFEST_PROCS", "1"))
    if nproc > 1:
        with Pool(nproc) as pool:
            segs = pool.map(_check, args, chunksize=8)
    else:
        segs = [_check(a) for a in args]
    h_all = hashlib.sha256()
    for s in segs:
        h_all.update(bytes.fromhex(s["sha256"]))
    m = dict(label="RQ1 angle archive (zw); generation + integrity + hashes only, no statistic", field="zw", X=X,
             segment=SEG, rows=sum(s["rows"] for s in segs), segments=segs,
             all_integrity=all(s["integrity"] for s in segs), sha256_of_segment_hashes=h_all.hexdigest(),
             X_1e10_rows=int(sum(s["rows"] for s in segs if s["hi"] <= 10 ** 10)),
             X_1e11_rows=int(sum(s["rows"] for s in segs if s["hi"] <= 10 ** 11)),
             X_1e12_rows=int(sum(s["rows"] for s in segs if s["hi"] <= 10 ** 12)))
    json.dump(m, open(os.path.join(out_dir, "MANIFEST.json"), "w"), indent=1)
    print(m["rows"], m["all_integrity"], m["sha256_of_segment_hashes"])
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "jobs":
        for k, s in jobs(int(float(sys.argv[2]))):
            print(k, f"{s:.0f}")
    elif sys.argv[1] == "task":
        sys.exit(task(int(sys.argv[2]), sys.argv[3]))
    else:
        sys.exit(manifest(sys.argv[2], int(float(sys.argv[3]))))

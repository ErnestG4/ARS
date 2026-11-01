"""FN1 (field ladder; Will, 2026-10-31, staged 10¹⁰ first): prime-angle archives for the seven w = 2 class-number-1
imaginary quadratic fields D ∈ {−7, −8, −11, −19, −43, −67, −163}. Generation, integrity and hashes only: no statistic
of the angles is computed here (FN1_STEP0.md §3).

Split primes: p with (D/p) = +1. For D = −q (q ≡ 3 mod 4 prime), (D/p) = (p/q) for odd p ≠ q; p = 2 splits iff
D ≡ 1 (mod 8) (only D = −7 here). For D = −8, p splits iff p ≡ 1, 3 (mod 8). Ramified and inert primes are excluded.
Rows (int32): D ≡ 1 (mod 4): (x, y), x, y > 0, x² + |D| y² = 4p, π = (x + y√D)/2;
              D = −8:        (x, y), x, y > 0, x² + 2 y² = p,     π = x + y√−2.
θ = (arg π mod π)/π = atan2(y√|D|, x)/π (or atan2(y√2, x)/π) ∈ (0, ½); the conjugate ideal sits at 1 − θ (mirror).
Cornacchia: r² ≡ D (mod p) by Tonelli–Shanks (rq1_angles.sqrt_mod); for 4p, r of the parity of D, Euclid on (2p, r)
until r ≤ 2√p; for p (D = −8), r > p/2, Euclid on (p, r) until r < √p. Every row is asserted.

  python fn1_archive.py selftest                 Cornacchia against brute force (p < 2·10⁵), split rule against Euler's
                                                 criterion (p < 10⁶), the hand case θ(D = −7, p = 2), and the LMFDB
                                                 weight-3 a_p (p ≤ 47) from the generated rows
  python fn1_archive.py jobs D X                 segment list (k, model seconds)
  python fn1_archive.py task D K OUT_DIR         segment k → OUT_DIR/seg_KKKK.npy
  python fn1_archive.py manifest D OUT_DIR X     per-segment sha256, rows, integrity → OUT_DIR/MANIFEST.json
Cost model: rq1_zw.py's (the ℤ[i] curve × 16.2/19.2, spot factor 2.8): the same Tonelli + Euclid structure per split
prime.
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

try:
    import rq1_angles as R
    import rq1_archive as A
except ImportError:                                   # repo layout; on spot the two modules are copied alongside
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rq1"))
    import rq1_angles as R
    import rq1_archive as A

FIELDS = [-7, -8, -11, -19, -43, -67, -163]
SEG = 10 ** 8
SPOT = 2.8
W2_OVER_ZI = 16.2 / 19.2
LMFDB_AP = {                                          # LMFDB_WEIGHT3_CM.md (p = 2 … 47)
    -7: [-3, 0, 0, -7, -6, 0, 0, 0, 18, -54, 0, -38, 0, 58, 0],
    -8: [-2, -2, 0, 0, 14, 0, 2, -34, 0, 0, 0, 0, -46, 14, 0],
    -11: [0, -5, -1, 0, -11, 0, 0, 0, 35, 0, -37, -25, 0, 0, 50],
    -19: [0, 0, -9, -5, 3, 0, 15, -19, -30, 0, 0, 0, 0, -85, 75],
    -43: [0, 0, 0, 0, -21, -17, -9, 0, 3, 0, 19, 0, 39, -43, -78],
    -67: [0, 0, 0, 0, 0, 0, -33, -29, -21, -9, 0, 7, 0, 0, 27],
    -163: [0] * 12 + [-81, -77, -69]}


def split_mask(ps, D):
    if D == -8:
        return (ps % 8 == 1) | (ps % 8 == 3)
    q = -D
    qr = np.zeros(q, bool)
    qr[(np.arange(1, q) ** 2) % q] = True
    m = qr[ps % q] & (ps % 2 == 1) & (ps != q)
    if D % 8 == 1:
        m |= ps == 2
    return m


def cornacchia(p, D):
    if D == -8:
        r = R.sqrt_mod((p - 2) % p, p) if p > 2 else 0          # r² ≡ −2 (mod p)
        if 2 * r < p:
            r = p - r
        a, b = p, r
        lim = math.isqrt(p)
        while b > lim:
            a, b = b, a % b
        x = b
        t = p - x * x
        y = math.isqrt(t // 2)
        if t % 2 or x * x + 2 * y * y != p or x <= 0 or y <= 0:
            raise ArithmeticError(("cornacchia -8", p))
        return x, y
    q = -D
    if p == 2:                                                   # D ≡ 1 (mod 8): 8 = x² + q y²
        y = 1
        x = math.isqrt(8 - q)
        if x * x + q != 8:
            raise ArithmeticError(("cornacchia p=2", D))
        return x, y
    r = R.sqrt_mod(D % p, p)
    if (r - D) % 2:
        r = p - r
    a, b = 2 * p, r
    lim = math.isqrt(4 * p)
    while b > lim:
        a, b = b, a % b
    x = b
    t = 4 * p - x * x
    y = math.isqrt(t // q)
    if t % q or x * x + q * y * y != 4 * p or x <= 0 or y <= 0:
        raise ArithmeticError(("cornacchia", D, p))
    return x, y


def gen_segment(D, lo, hi):
    ps = R.primes_in(lo, hi)
    ps = ps[split_mask(ps, D)]
    out = np.empty((len(ps), 2), np.int32)
    for i, p in enumerate(ps.tolist()):
        out[i] = cornacchia(p, D)
    return out


def thetas(D, xy):
    x, y = xy[:, 0].astype(np.float64), xy[:, 1].astype(np.float64)
    s = math.sqrt(2.0) if D == -8 else math.sqrt(-D)
    return np.arctan2(s * y, x) / math.pi


def norm_of(D, xy):
    x, y = xy[:, 0].astype(np.int64), xy[:, 1].astype(np.int64)
    return x * x + 2 * y * y if D == -8 else (x * x - D * y * y) // 4


def selftest():
    ok = True
    for D in FIELDS:
        q = -D
        ps = R.primes_in(2, 2 * 10 ** 5)
        sp = ps[split_mask(ps, D)]
        for p in sp.tolist()[:3000]:                               # Cornacchia against brute force
            x, y = cornacchia(p, D)
            if D == -8:
                bf = [(a, b) for b in range(1, math.isqrt(p // 2) + 1) for a in [math.isqrt(p - 2 * b * b)]
                      if a > 0 and a * a + 2 * b * b == p]
            else:
                bf = [(a, b) for b in range(1, math.isqrt(4 * p // q) + 1) for a in [math.isqrt(4 * p - q * b * b)]
                      if a > 0 and a * a + q * b * b == 4 * p]
            ok &= bf == [(x, y)]
        big = R.primes_in(2, 10 ** 6)                              # split rule against Euler's criterion
        eu = np.array([(p == 2 and D % 8 == 1) or (p != 2 and p % q != 0 and pow(D % p, (p - 1) // 2, p) == 1)
                       for p in big.tolist()])
        ok &= bool(np.array_equal(eu, split_mask(big, D)))
        pr = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]   # a_p from the generated rows
        seg = gen_segment(D, 2, 48)
        N = norm_of(D, seg)
        x, y = seg[:, 0].astype(np.int64), seg[:, 1].astype(np.int64)
        two_re = 2 * (x * x - 2 * y * y) if D == -8 else (x * x + D * y * y) // 2
        mine = {int(p): int(a) for p, a in zip(N, two_re)}
        ram = {-8: (2, -2)}.get(D, (q, D))
        for p, a in zip(pr, LMFDB_AP[D]):
            exp = mine.get(p, ram[1] if p == ram[0] else 0)
            ok &= exp == a
        print(D, "Cornacchia/brute, split rule, LMFDB a_p:", ok, flush=True)
    th = thetas(-7, np.array([[1, 1]]))[0]
    ok &= abs(th - math.atan2(math.sqrt(7), 1) / math.pi) < 1e-15 and abs(th - 0.38497) < 1e-4
    print("theta(-7, p=2)", th, "SELFTEST_PASS", ok)
    return 0 if ok else 1


def jobs(D, X):
    out = []
    for k in range(int(X // SEG)):
        lo, hi = k * SEG, (k + 1) * SEG
        n = (hi - max(lo, 3)) / (2 * math.log((lo + hi) / 2))
        out.append((k, n * A.t_local_us((lo + hi) / 2, "zi") * W2_OVER_ZI * 1e-6 * SPOT))
    return out


def task(D, k, out_dir):
    path = os.path.join(out_dir, f"seg_{k:04d}.npy")
    if os.path.exists(path):
        return 0
    t = time.time()
    xy = gen_segment(D, k * SEG, (k + 1) * SEG)
    tmp = f"{path}.{os.getpid()}.part.npy"
    np.save(tmp, xy)
    os.replace(tmp, path)
    print(k, len(xy), round(time.time() - t, 1), flush=True)
    return 0


def _check(args):
    D, out_dir, k = args
    lo, hi = k * SEG, (k + 1) * SEG
    path = os.path.join(out_dir, f"seg_{k:04d}.npy")
    raw = open(path, "rb").read()
    xy = np.load(path)
    ref = R.primes_in(max(lo, 2), hi)
    ref = ref[split_mask(ref, D)]
    ok = bool(np.array_equal(norm_of(D, xy), ref) and np.all(xy > 0))
    if D != -8:
        x, y = xy[:, 0].astype(np.int64), xy[:, 1].astype(np.int64)
        ok &= bool(np.all(x * x - D * y * y == 4 * ref))
    return dict(k=k, lo=lo, hi=hi, rows=int(len(xy)), sha256=hashlib.sha256(raw).hexdigest(), integrity=ok)


def manifest(D, out_dir, X):
    from multiprocessing import Pool
    args = [(D, out_dir, k) for k, _ in jobs(D, X)]
    nproc = int(os.environ.get("MANIFEST_PROCS", "1"))
    if nproc > 1:
        with Pool(nproc) as pool:
            segs = pool.map(_check, args, chunksize=2)
    else:
        segs = [_check(a) for a in args]
    h_all = hashlib.sha256()
    for s in segs:
        h_all.update(bytes.fromhex(s["sha256"]))
    m = dict(label=f"FN1 angle archive D = {D}; generation + integrity + hashes only, no statistic", D=D, X=X,
             segment=SEG, rows=sum(s["rows"] for s in segs), segments=segs,
             all_integrity=all(s["integrity"] for s in segs), sha256_of_segment_hashes=h_all.hexdigest(),
             X_1e10_rows=int(sum(s["rows"] for s in segs if s["hi"] <= 10 ** 10)))
    json.dump(m, open(os.path.join(out_dir, "MANIFEST.json"), "w"), indent=1)
    print(m["rows"], m["all_integrity"], m["sha256_of_segment_hashes"])
    return 0 if m["all_integrity"] else 1


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "selftest":
        sys.exit(selftest())
    D = int(sys.argv[2])
    if c == "jobs":
        for k, s in jobs(D, int(float(sys.argv[3]))):
            print(k, f"{s:.0f}")
    elif c == "task":
        sys.exit(task(D, int(sys.argv[3]), sys.argv[4]))
    else:
        sys.exit(manifest(D, sys.argv[3], int(float(sys.argv[4]))))

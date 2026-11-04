# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1-h2 (FN1H2_SEAL.md §3; Will, 2026-11-03): principal-prime angle archives for the 18 class-number-2 imaginary
quadratic fields (lead/FN1_L17_PREREQS.md (a)). Generation, integrity, counts and hashes only: no statistic of the
angles is computed here (the stage-2 archive rule). Structure follows fn1_archive.py.

Split primes: p ∤ D with χ_D(p) = +1, χ_D the Kronecker symbol (D/·), periodic mod |D| for fundamental D (table built
by `kronecker` on the residues). Principal: every |D| here has exactly two prime factors, so Cl = the genus group and a
split p has principal prime factors iff the genus character χ_{q*}(p) = +1, q the odd prime factor used below,
q* = (−1)^((q−1)/2)·q (periodic mod q). Non-principal split primes, ramified and inert primes are excluded.
Rows (int32), x, y > 0:
  D ≡ 1 (mod 4): x² + |D| y² = 4p, α = (x + y√D)/2 (principal form x² + xy + ((1 + |D|)/4) y²);
  D ≡ 0 (mod 4): x² + m y² = p, m = |D|/4, α = x + y√−m.
θ = (arg α mod π)/π = atan2(y√|D|, x)/π, or atan2(y√m, x)/π, ∈ (0, ½); the conjugate ideal sits at 1 − θ (mirror).
Cornacchia as fn1_archive.cornacchia, with |D| (or m) composite; it is asserted to succeed on every principal split
prime and every row is checked. For −15 the primes above 2 split but are non-principal (8 = x² + 15y² has no solution)
and drop out through the genus test.

  python fn1h2_archive.py selftest               brute-force principal-form representability (p < 2·10⁵) against
                                                 split ∧ genus, Cornacchia against brute force, the split rule against
                                                 Euler's criterion (p < 10⁶), the D = −7 / −8 / −11 h = 1 rows of
                                                 fn1_archive (no genus factor) reproduced, density check, hand cases
  python fn1h2_archive.py jobs D X               segment list (k, model seconds)
  python fn1h2_archive.py task D K OUT_DIR       segment k → OUT_DIR/seg_KKKK.npy
  python fn1h2_archive.py manifest D OUT_DIR X   per-segment sha256, rows, integrity → OUT_DIR/MANIFEST.json
Cost model (FN1H2_SEAL.md §8, priced before any h = 2 compute): 51 s CPU per 10⁸ segment (FN1's measured, flat in k;
an upper bound since only half the split primes reach Cornacchia) × 1.2 queue contention = 61.2 s per segment,
3,600 segments ≈ 61 core-h. The §9.H first wave (queue_fn1h2_wave1.sh) measures it before the bulk.
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    import rq1_angles as R
    import fn1_archive as FA
except ImportError:                                   # repo layout; on spot the modules are copied alongside
    sys.path.insert(0, os.path.join(HERE, "..", "rq1"))
    sys.path.insert(0, HERE)
    import rq1_angles as R
    import fn1_archive as FA

FIELDS = [-15, -20, -24, -35, -40, -51, -52, -88, -91, -115, -123, -148, -187, -232, -235, -267, -403, -427]
PRIMARY = [-35, -40, -51, -52, -88, -91, -115, -123, -148]
SEG = 10 ** 8


def kronecker(a, n):
    """Kronecker symbol (a/n), n ≥ 1."""
    if n == 0:
        return 1 if abs(a) == 1 else 0
    res = 1
    while n % 2 == 0:
        n //= 2
        if a % 2 == 0:
            return 0
        if a % 8 in (3, 5):
            res = -res
    a %= n
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                res = -res
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            res = -res
        a %= n
    return res if n == 1 else 0


def genus_q(D):
    """The odd prime q | D whose genus character χ_{q*} is used (the smallest odd prime factor)."""
    m = -D
    f = 3
    while f <= m:
        if m % f == 0:
            return f
        f += 2
    raise ValueError(D)


def masks(ps, D):
    """(split, principal) boolean masks for primes ps."""
    q = -D
    tab = np.array([kronecker(D, r) for r in range(q)], np.int8)
    split = (tab[ps % q] == 1) & (q % ps != 0)
    g = genus_q(D)
    gs = g if g % 4 == 1 else -g
    gtab = np.array([kronecker(gs, r) for r in range(g)], np.int8)
    princ = split & (gtab[ps % g] == 1)
    # p = 2 (odd D only; splits iff D ≡ 1 mod 8): its genus value is the Kronecker symbol (q*/2)
    two = ps == 2
    if two.any():
        princ[two] = split[two] & (kronecker(gs, 2) == 1)
    return split, princ


def cornacchia(p, D):
    q = -D
    if q % 4 == 0:
        m = q // 4
        r = R.sqrt_mod((-m) % p, p) if p > 2 else 0
        if 2 * r < p:
            r = p - r
        a, b = p, r
        lim = math.isqrt(p)
        while b > lim:
            a, b = b, a % b
        x = b
        t = p - x * x
        y = math.isqrt(t // m)
        if t % m or x * x + m * y * y != p or x <= 0 or y <= 0:
            raise ArithmeticError(("cornacchia 4m", D, p))
        return x, y
    if p == 2:
        raise ArithmeticError(("p = 2 principal", D))  # never reached: no D here has a principal prime above 2
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
    ps = ps[masks(ps, D)[1]]
    out = np.empty((len(ps), 2), np.int32)
    for i, p in enumerate(ps.tolist()):
        out[i] = cornacchia(p, D)
    return out


def thetas(D, xy):
    x, y = xy[:, 0].astype(np.float64), xy[:, 1].astype(np.float64)
    s = math.sqrt(-D / 4) if (-D) % 4 == 0 else math.sqrt(-D)
    return np.arctan2(s * y, x) / math.pi


def norm_of(D, xy):
    x, y = xy[:, 0].astype(np.int64), xy[:, 1].astype(np.int64)
    return x * x + (-D // 4) * y * y if (-D) % 4 == 0 else (x * x - D * y * y) // 4


def brute_principal(p, D):
    """All (x, y), x, y > 0, of the principal-form equation (brute force)."""
    q = -D
    if q % 4 == 0:
        m = q // 4
        return [(a, b) for b in range(1, math.isqrt(p // m) + 1) for a in [math.isqrt(p - m * b * b)]
                if a > 0 and a * a + m * b * b == p]
    return [(a, b) for b in range(1, math.isqrt(4 * p // q) + 1) for a in [math.isqrt(4 * p - q * b * b)]
            if a > 0 and a * a + q * b * b == 4 * p]


def selftest():
    ok = True
    small = R.primes_in(2, 2 * 10 ** 5)
    big = R.primes_in(2, 10 ** 6)
    for D in FIELDS:
        q = -D
        sp, pr = masks(small, D)
        rep = np.array([len(brute_principal(p, D)) > 0 for p in small.tolist()])
        a = bool(np.array_equal(rep, pr))                              # representable ⇔ split ∧ genus
        bad = 0
        for p in small[pr].tolist()[:3000]:                           # Cornacchia = the unique brute-force solution
            bad += brute_principal(p, D) != [cornacchia(p, D)]
        b = bad == 0
        eu = np.array([(p == 2 and D % 8 == 1) or (p != 2 and q % p != 0 and pow(D % p, (p - 1) // 2, p) == 1)
                       for p in big.tolist()])
        c = bool(np.array_equal(eu, masks(big, D)[0]))                # split rule against Euler's criterion
        dens = pr.sum() / len(small)                                   # Chebotarev: 1/4
        d = abs(dens - 0.25) < 0.01
        seg = gen_segment(D, 2, 2 * 10 ** 4)
        e = bool(np.array_equal(norm_of(D, seg), small[pr & (small < 2 * 10 ** 4)]))
        th = thetas(D, seg)
        f = bool(np.all((th > 0) & (th < 0.5)))
        print(D, "genus=repr", a, "cornacchia", b, "split/Euler", c, f"density {dens:.4f}", d, "norms", e,
              "theta in (0, 1/2)", f, flush=True)
        ok &= a and b and c and d and e and f
    # h = 1 fields: no genus factor, so every split prime is principal and the rows must equal fn1_archive's
    for D in (-7, -11, -19):
        ps = R.primes_in(2, 10 ** 5)
        mine = ps[(np.array([kronecker(D, int(p)) for p in ps.tolist()]) == 1) & (ps != -D)]
        theirs = FA.gen_segment(D, 2, 10 ** 5)
        mine_xy = np.array([cornacchia(int(p), D) if p != 2 else FA.cornacchia(2, D) for p in mine.tolist()], np.int32)
        g = bool(np.array_equal(mine_xy, theirs))
        print("h = 1 cross-check", D, g, flush=True)
        ok &= g
    # hand cases
    hc = [(-15, 19, (4, 2)), (-20, 29, (3, 2)), (-20, 3, None), (-24, 7, (1, 1)), (-15, 2, None), (-40, 11, (1, 1))]
    for D, p, xy in hc:
        sp, pr = masks(np.array([p]), D)
        h = (xy is None and not pr[0]) or (xy is not None and pr[0] and cornacchia(p, D) == xy)
        print("hand", D, p, xy, h)
        ok &= h
    th = thetas(-20, np.array([[3, 2]]))[0]
    ok &= abs(th - math.atan2(2 * math.sqrt(5), 3) / math.pi) < 1e-15
    print("SELFTEST_PASS", ok)
    return 0 if ok else 1


MODEL_S = 51.0 * 1.2


def jobs(D, X):
    return [(k, MODEL_S) for k in range(int(X // SEG))]


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
    sp, pr = masks(ref, D)
    ok = bool(np.array_equal(norm_of(D, xy), ref[pr]) and np.all(xy > 0))
    if (-D) % 4:
        x, y = xy[:, 0].astype(np.int64), xy[:, 1].astype(np.int64)
        ok &= bool(np.all(x * x - D * y * y == 4 * ref[pr]))
    return dict(k=k, lo=lo, hi=hi, rows=int(len(xy)), split_count=int(sp.sum()), sha256=hashlib.sha256(raw).hexdigest(),
                integrity=ok)


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
    m = dict(label=f"FN1-h2 principal-prime angle archive D = {D}; generation + integrity + counts + hashes only, "
                   f"no statistic", D=D, X=X, segment=SEG, rows=sum(s["rows"] for s in segs),
             split_count=sum(s["split_count"] for s in segs), segments=segs,
             all_integrity=all(s["integrity"] for s in segs), sha256_of_segment_hashes=h_all.hexdigest())
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

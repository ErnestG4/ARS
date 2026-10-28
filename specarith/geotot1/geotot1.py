"""GEO-TOT1 (brief 2026-10-27): bounded-dwell keys a/q, per q. Exact integer arithmetic (numba int64).

For every q in [2, Q] and every a in [1, q − 1] with gcd(a, q) = 1: the continued fraction a/q = [0; a_1, …, a_k] in the
canonical form (a_k ≥ 2 for q ≥ 2), its length L = k, depth S = a_1 + … + a_k, and the maximum M = max a_i.
Membership in E_N (all partial quotients ≤ N), under two conventions:
  canon ("last ≥ 2"): M ≤ N.
  alt   (either form; [..., a_k] = [..., a_k − 1, 1]): max(a_1, …, a_{k−1}, a_k − 1, 1) ≤ N.
Per q (all int64): phi; cnt_canon[N], cnt_alt[N] for N = 2 … 6; S_sum; L_sum; L_sq_sum; L_hist[0 … 47];
S_hist and M_hist on log2 bins (bin j holds 2^j ≤ x < 2^(j+1), j = 0 … 39). q = 1 is not enumerated (no key with
0 < a < q); the Farey count adds 0/1 and 1/1 as 1 + Σ φ(q).
Per-q work is independent; q is split over workers by a fixed partition, so outputs do not depend on the worker count.

  python geotot1.py enum Q0 Q1 OUT_NPZ          q in [Q0, Q1] → OUT_NPZ
  python geotot1.py merge OUT_NPZ PART …        concatenate parts (q ascending; asserts contiguity)
"""
import sys

import numpy as np
from numba import njit, prange

NS = (2, 3, 4, 5, 6)
LH, SH = 48, 40


@njit(cache=False)
def one_q(q, cnt_c, cnt_a, Lh, Sh, Mh):
    phi = 0
    S_sum = 0
    L_sum = 0
    L_sq = 0
    for a in range(1, q):
        x, y = q, a
        k = 0
        S = 0
        M = 0
        Mpre = 0             # max over a_1 … a_{k−1}
        last = 0
        while y != 0:
            t = x // y
            r = x - t * y
            x, y = y, r
            if k > 0 and last > Mpre:
                Mpre = last
            last = t
            k += 1
            S += t
            if t > M:
                M = t
        # x is gcd(q, a); the first quotient is q // a (a/q = [0; q//a, …])
        if x != 1:
            continue
        phi += 1
        S_sum += S
        L_sum += k
        L_sq += k * k
        Lh[min(k, LH - 1)] += 1
        j = 0
        v = S
        while v > 1:
            v >>= 1
            j += 1
        Sh[min(j, SH - 1)] += 1
        j = 0
        v = M
        while v > 1:
            v >>= 1
            j += 1
        Mh[min(j, SH - 1)] += 1
        malt = Mpre
        if last - 1 > malt:
            malt = last - 1
        if malt < 1:
            malt = 1
        for i in range(5):
            N = i + 2
            if M <= N:
                cnt_c[i] += 1
            if malt <= N:
                cnt_a[i] += 1
    return phi, S_sum, L_sum, L_sq


@njit(cache=False, parallel=True)
def enum(q0, q1):
    n = q1 - q0 + 1
    phi = np.zeros(n, np.int64)
    S_sum = np.zeros(n, np.int64)
    L_sum = np.zeros(n, np.int64)
    L_sq = np.zeros(n, np.int64)
    cnt_c = np.zeros((n, 5), np.int64)
    cnt_a = np.zeros((n, 5), np.int64)
    Lh = np.zeros((n, LH), np.int64)
    Sh = np.zeros((n, SH), np.int64)
    Mh = np.zeros((n, SH), np.int64)
    for i in prange(n):
        p, s, l1, l2 = one_q(q0 + i, cnt_c[i], cnt_a[i], Lh[i], Sh[i], Mh[i])
        phi[i] = p
        S_sum[i] = s
        L_sum[i] = l1
        L_sq[i] = l2
    return phi, S_sum, L_sum, L_sq, cnt_c, cnt_a, Lh, Sh, Mh


KEYS = ("phi", "S_sum", "L_sum", "L_sq", "cnt_canon", "cnt_alt", "L_hist", "S_hist", "M_hist")


def run(q0, q1, out):
    import time
    arrs = enum(q0, q1)
    np.savez(out, q=np.arange(q0, q1 + 1, dtype=np.int64), **dict(zip(KEYS, arrs)))
    open(out + ".cpu", "w").write(f"{time.process_time():.3f}\n")     # sidecar, so the .npz bytes stay deterministic
    return 0


def merge(out, parts):
    ds = [np.load(p) for p in parts]
    ds.sort(key=lambda d: int(d["q"][0]))
    for a, b in zip(ds, ds[1:]):
        assert int(b["q"][0]) == int(a["q"][-1]) + 1
    np.savez(out, **{k: np.concatenate([d[k] for d in ds]) for k in ("q",) + KEYS})
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "enum":
        sys.exit(run(int(float(sys.argv[2])), int(float(sys.argv[3])), sys.argv[4]))
    sys.exit(merge(sys.argv[2], sys.argv[3:]))

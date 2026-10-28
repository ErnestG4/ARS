"""GEO-TOT1 prime-power lead, seen-range check (POST HOC, 2026-10-28): reproduces the Step 0 agent's table for the 103
prime squares p², 317 ≤ p ≤ 997, from data/GEOTOT1_perq.parquet. Excess = c_N·q/φ(q) at p² minus the mean of the 4
nearest primes; fold = the number of distinct canonical E_N keys of p² produced by Niederreiter's folding of the keys of
p (if a/p = [b₁…b_s], then [b₁, …, b_{s−1}, b_s + 1, b_s − 1, b_{s−1}, …, b₁] has denominator p²), on the same scale.

  python geotot1_pp_seen.py
"""
import math
from fractions import Fraction

import numpy as np
import pyarrow.parquet as pq

from geotot1_analyze import DELTA


def cf(a, r):
    out = []
    while a:
        k = r // a
        out.append(k)
        r, a = a, r - k * a
    return out


def canon_max(w):
    w = list(w)
    if len(w) > 1 and w[-1] == 1:
        w = w[:-2] + [w[-2] + 1]
    return max(w)


def num(w):
    x = Fraction(0)
    for b in reversed(w):
        x = 1 / (b + x)
    return x


def main():
    t = pq.read_table("data/GEOTOT1_perq.parquet", columns=["q", "phi", "type", "E3_canon", "E4_canon", "E5_canon"]).to_pandas()
    q, phi, typ = t.q.values, t.phi.values, t.type.astype(str).values
    primes = q[typ == "prime"]
    ps = [p for p in range(317, 998) if all(p % d for d in range(2, int(p ** .5) + 1))]
    res = {N: [] for N in (3, 4, 5)}
    for p in ps:
        Q = p * p
        i = Q - 2
        near = primes[np.argsort(np.abs(primes - Q))[:4]]
        folded = {3: set(), 4: set(), 5: set()}
        for a in range(1, p):
            b = cf(a, p)
            w = b[:-1] + [b[-1] + 1, b[-1] - 1] + b[:-1][::-1]
            m = canon_max(w)
            for N in (3, 4, 5):
                if m <= N:
                    folded[N].add(num(w).numerator)
        for N in (3, 4, 5):
            e = 2 * DELTA[N] - 1
            cq = lambda j: t[f"E{N}_canon"].values[j] / q[j] ** e * q[j] / phi[j]
            ex = cq(i) - np.mean([cq(int(x) - 2) for x in near])
            res[N].append((ex, len(folded[N]) / Q ** e * Q / phi[i]))
    for N in (3, 4, 5):
        a = np.array(res[N])
        d = a[:, 0] - a[:, 1]
        se = lambda v: v.std(ddof=1) / len(v) ** .5
        print(N, f"excess {a[:, 0].mean():.4f} ± {se(a[:, 0]):.4f}  fold {a[:, 1].mean():.4f}  "
                 f"diff {d.mean():+.4f} ± {se(d):.4f}  n={len(a)}")


if __name__ == "__main__":
    main()

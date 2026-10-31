"""Peter (2002) multiplicity correlations: the zero-parameter prediction γ(r) (GEO1_STEP0B_PETER.md; the theorem block
of arXiv math/0104234 v1, read verbatim).

γ(r) + 1 = ∏_p (1 + Σ_{b ≥ 1} A_r(p^b)), with
  odd p:  A_r(p)   = (p·S_r(p) − 1)/(p² − 1)²,  S_r(p) = Σ_{n mod p} ((n² − 4)((n + r)² − 4) / p)  (Legendre symbol)
          A_r(p^b) = [2p^b(1 − 1/p) if r ≡ 0 (p^b); −2p^{b−1} if r ≢ 0 (p^b), ≡ 0 (p^{b−1});
                      (−1/p)^b p^b(1 − 1/p) if r ≡ ±4 (p^b); −(−1/p)^b p^{b−1} if r ≢ ±4 (p^b), ≡ ±4 (p^{b−1}); 0]
                     / ((p² − 1)² p^{3b−4}),  b ≥ 2
  p = 2:  A_r(2) = ±1/9 (r even / odd); A_r(4) = (1/18)·{1: r ≡ 0 (4); −1: r ≡ 2 (4); 0: r odd}; A_r(8) = A_r(32) = 0;
          A_r(16) = (1/144)·{1: r ≡ 0 (16); −1: r ≡ 8 (16); 0: r ≢ 0 (8)};
          A_r(2^b) = (1/(9·2^{2b−4}))·{2: r ≡ 0; −2: r ≡ 2^{b−1}; 1: r ≡ ±(4 + 2^{b−2}); −1: r ≡ ±(4 + 2^{b−2} + 2^{b−1});
                     0 otherwise} (mod 2^b), b ≥ 6.
Primes p ≤ P are multiplied exactly; the tail is bounded by Σ_{p > P} |A_r(p) + …| ≤ Σ_{p>P} (p·|S_r(p)| + 1)/(p² − 1)²
with |S_r(p)| ≤ p (reported as tail_bound).

Independent check (`check`): for q = p^B, the local factor 1 + Σ_{b ≤ B} A_r(p^b) against (1/q) Σ_{n mod q} δ(n) δ(n + r),
δ(n) = q·#{M ∈ SL(2, ℤ/q): tr M ≡ n} / |SL(2, ℤ/q)| (the trace distribution's density; counted, not from the formulas).

  python geo1_peter.py predict P OUT_JSON R1 R2 …
  python geo1_peter.py check OUT_JSON
"""
import json
import math
import sys

import numpy as np

try:
    from numba import njit
except ImportError:
    def njit(*a, **k):
        return (lambda f: f) if not (len(a) == 1 and callable(a[0])) else a[0]


def primes_upto(P):
    s = np.ones(P + 1, bool)
    s[:2] = False
    for i in range(2, int(P ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.flatnonzero(s)


@njit(cache=False)
def legendre_sum(p, r):
    chi = np.zeros(p, np.int64)                         # chi[x] = (x / p)
    for x in range(1, p):
        chi[(x * x) % p] = 1
    for x in range(1, p):
        if chi[x] == 0:
            chi[x] = -1
    s = 0
    for n in range(p):
        v = ((n * n - 4) % p) * (((n + r) * (n + r) - 4) % p) % p
        s += chi[v]
    return s


def leg_m1(p):
    return 1 if p % 4 == 1 else -1                       # (−1/p)


def A_odd(p, b, r, S=None):
    if b == 1:
        return (p * S - 1) / (p * p - 1) ** 2
    pb, pb1 = p ** b, p ** (b - 1)
    den = (p * p - 1) ** 2 * float(p) ** (3 * b - 4)
    e = leg_m1(p) ** b
    if r % pb == 0:
        num = 2 * pb * (1 - 1 / p)
    elif r % pb1 == 0:
        num = -2 * pb1
    elif (r - 4) % pb == 0 or (r + 4) % pb == 0:
        num = e * pb * (1 - 1 / p)
    elif (r - 4) % pb1 == 0 or (r + 4) % pb1 == 0:
        num = -e * pb1
    else:
        num = 0.0
    return num / den


def A_two(b, r):
    if b == 1:
        return (1 if r % 2 == 0 else -1) / 9
    if b == 2:
        return 0.0 if r % 2 else (1 if r % 4 == 0 else -1) / 18
    if b in (3, 5):
        return 0.0
    if b == 4:
        if r % 16 == 0:
            return 1 / 144
        if r % 16 == 8:
            return -1 / 144
        return 0.0
    m = 2 ** b
    rr = r % m
    a1 = (4 + 2 ** (b - 2)) % m
    a2 = (4 + 2 ** (b - 2) + 2 ** (b - 1)) % m
    if rr == 0:
        v = 2
    elif rr == 2 ** (b - 1):
        v = -2
    elif rr in (a1, (-a1) % m):
        v = 1
    elif rr in (a2, (-a2) % m):
        v = -1
    else:
        v = 0
    return v / (9 * 2.0 ** (2 * b - 4))


def local_factor(p, r, bmax=80):
    if p == 2:
        tot = 1.0
        for b in range(1, bmax):
            tot += A_two(b, r)
        return tot
    S = legendre_sum(p, r)
    tot = 1 + A_odd(p, 1, r, S)
    for b in range(2, bmax):                       # b ≥ 2 terms vanish unless r ≡ 0 or ±4 (mod p^{b−1})
        pb1 = p ** (b - 1)
        if r % pb1 and (r - 4) % pb1 and (r + 4) % pb1:
            break
        term = A_odd(p, b, r, S)
        tot += term
        if abs(term) < 1e-22:
            break
    return tot


def gamma_pred(r, P):
    lp = 0.0
    tail = 0.0
    for p in primes_upto(P):
        f = local_factor(int(p), r)
        lp += math.log(f)
    tail = 1.1 / (P * math.log(P))                         # Σ_{p > P} (p² + 1)/(p² − 1)² ≲ 1/(P ln P) (|S_r(p)| ≤ p)
    return math.exp(lp) - 1, tail


def predict(P, out, rs):
    res = {}
    for r in rs:
        g, tail = gamma_pred(r, P)
        res[str(r)] = dict(gamma=g, log_tail_bound=tail)
        print(r, f"{g:.6f}", f"tail bound on log(1+γ) {tail:.1e}", flush=True)
    g0 = res["0"]["gamma"] if "0" in res else gamma_pred(0, P)[0]
    for r in rs:
        res[str(r)]["ratio_to_gamma0"] = res[str(r)]["gamma"] / g0
    json.dump(dict(P=P, gamma=res), open(out, "w"), indent=1)
    return 0


def trace_density(q):
    """δ(n) for n mod q from SL(2, ℤ/q) counted by trace."""
    N = np.zeros(q, np.int64)                                  # N[m] = #{(b, c) mod q: bc ≡ m}
    b = np.arange(q)
    for c in range(q):
        np.add.at(N, (b * c) % q, 1)
    cnt = np.zeros(q, np.int64)
    for a in range(q):
        for d in range(q):
            cnt[(a + d) % q] += N[(a * d - 1) % q]
    tot = cnt.sum()
    return q * cnt / tot


def check(out):
    res = []
    for p, B in ((2, 7), (3, 4), (5, 3), (7, 2), (11, 2)):
        q = p ** B
        dlt = trace_density(q)
        for r in range(0, 25):
            direct = float(np.mean(dlt * np.roll(dlt, -r)))
            S = legendre_sum(p, r) if p > 2 else 0
            formula = 1 + sum((A_two(b, r) if p == 2 else A_odd(p, b, r, S)) for b in range(1, B + 1))
            res.append(dict(p=p, B=B, r=r, direct=direct, formula=formula, diff=direct - formula))
    mx = max(abs(x["diff"]) for x in res)
    json.dump(dict(max_abs_diff=mx, rows=res), open(out, "w"), indent=1)
    print("max |direct - formula| =", mx)
    return 0 if mx < 1e-12 else 1


if __name__ == "__main__":
    if sys.argv[1] == "predict":
        sys.exit(predict(int(float(sys.argv[2])), sys.argv[3], [int(x) for x in sys.argv[4:]]))
    sys.exit(check(sys.argv[2]))

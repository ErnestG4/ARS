"""Comb arc G2: the ZZ[i] Hardy-Littlewood singular series, computed to
certified precision.  COMMITTED GENERATOR of comb/singular_series_banked.json
(TOOLKIT §9 committed-generator rule).

Form (L1-anchored): Gross-Smith [GrSm, Rocky Mountain J. Math.] conjecture as
stated in Kuperberg-Rodgers-Roditty-Gershon, arXiv:2001.09513 (Ramanujan J. 58,
2022), display defining
    S(eta) = prod_p (1 - nu_eta(p)/Np) / (1 - 1/Np)^2 ,
    nu = 2 if eta not in p, 1 if eta in p     (membership, NOT valuation),
product over ALL prime ideals of O_K.  Archived source: comb/lit/ (grep
"mathfrak{S}(\\eta):=").  K = Q(i) is explicitly instantiated in KRR's
numerical section (their figure captioned K = Q(i)).

Site-level form used by the arc (checkerboard support absorbs the ramified
(1+i) factor, which equals 2 for every even-norm offset):
    S'(h) = C'_G * prod_{pi odd, pi | h} (q-1)/(q-2),   q = N(pi),
    C'_G  = prod_{pi odd} (1 - 2/q)/(1 - 1/q)^2 .
Relation: S_GS(h) = 2 * S'(h); the estimator's occupancy normalization
rho = 2*lambda supplies the same factor on the measurement side.

Tail bound for the truncated C'_G product over primes with q > Q:
|log factor(q)| = |log(1-2/q) - 2 log(1-1/q)| <= 1/q^2 + 4/q^3 <= 2/q^2 for
q >= 8.  Sum over ZZ[i] primes with q > Q:
  split p=1 mod 4: two factors at q=p  -> sum <= 2 * sum_{p>Q} 2/p^2
  inert p=3 mod 4: one factor at q=p^2 -> negligible (sum 2/p^4)
Using pi(t) <= 1.3 t/ln t:  sum_{p>Q} 2/p^2 <= 2.6/(Q ln Q).  Total bound
B(Q) = 2*2.6/(Q ln Q) + 4/(3 Q^{3/2}) (inert, crude).  Reported in the JSON.
"""

import json
import math
import sys
import numpy as np

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool")
from phase34d.gaussian_primes import sieve_primes, split_p_as_sum_of_two_squares

Q_CUT = 10_000_000

# shells: N(h) -> mandatory/secondary per the sealed brief
MANDATORY_SHELLS = [2, 4, 8, 16, 32, 10, 20, 40, 18, 26, 50]
SECONDARY_SHELLS = [34, 36, 64, 80, 90, 100]


def cprime_g(qcut=Q_CUT):
    """Truncated product + rigorous-ish tail bound (see module docstring)."""
    primes = sieve_primes(qcut)
    logC = 0.0
    for p in primes:
        p = int(p)
        if p == 2:
            continue
        if p % 4 == 1:
            q = float(p)
            logC += 2.0 * (np.log1p(-2.0 / q) - 2.0 * np.log1p(-1.0 / q))
        else:
            q = float(p) * float(p)
            if q <= qcut * qcut:   # include ALL inert primes p <= qcut (q=p^2)
                logC += (np.log1p(-2.0 / q) - 2.0 * np.log1p(-1.0 / q))
    tail = 2 * 2.6 / (qcut * np.log(qcut)) + 4.0 / (3.0 * qcut ** 1.5)
    return float(np.exp(logC)), float(tail)


# ── ZZ[i] arithmetic for offset classification ──────────────────────────────

def zi_divides(pi, h):
    """Does the Gaussian integer pi divide h?  (a+bi | c+di in ZZ[i])."""
    a, b = pi
    c, d = h
    n = a * a + b * b
    # h / pi = (h * conj(pi)) / N(pi); divisibility <=> both components = 0 mod n
    re = c * a + d * b
    im = d * a - c * b
    return re % n == 0 and im % n == 0


def offsets_of_norm(N):
    """All h = (c,d) with c^2 + d^2 = N."""
    out = []
    r = math.isqrt(N)
    for c in range(-r, r + 1):
        d2 = N - c * c
        if d2 < 0:
            continue
        d = math.isqrt(d2)
        if d * d == d2:
            out.append((c, d))
            if d != 0:
                out.append((c, -d))
    return sorted(set(out))


def classify_offset(h):
    """Distinct odd primes pi of ZZ[i] dividing h, as a sorted tuple of
    (q, multiplicity-of-distinct-primes-at-that-q).  Membership only —
    valuation does not enter (L1-verified rule)."""
    c, d = h
    N = c * c + d * d
    facs = []
    M = N
    while M % 2 == 0:          # strip the ramified part FIRST — an even residual
        M //= 2                # would hide odd primes from the M>1 check below
    p = 3
    odd_rat = set()
    while p * p <= M:
        while M % p == 0:
            odd_rat.add(p)
            M //= p
        p += 2
    if M > 1:
        odd_rat.add(M)
    for p in sorted(odd_rat):
        if p % 4 == 3:
            # inert: p | h  <=>  p | N(h) (since p | h*hbar and p is real prime)
            if zi_divides((p, 0), h):
                facs.append((p * p, 1))
        else:
            a, b = split_p_as_sum_of_two_squares(p)
            cnt = int(zi_divides((a, b), h)) + int(zi_divides((a, -b), h))
            if cnt:
                facs.append((p, cnt))
    return tuple(facs)


def shell_classes(N):
    """Partition the norm-N shell into offset classes by divisor pattern."""
    classes = {}
    for h in offsets_of_norm(N):
        key = classify_offset(h)
        classes.setdefault(key, []).append(h)
    return classes


def s_prime(key, C):
    v = C
    for q, cnt in key:
        v *= ((q - 1.0) / (q - 2.0)) ** cnt
    return v


HAND_TABLE = {  # brief §2 table, independently verified by Will at review —
    # executable check, not a comment (a lost divisor factor MUST fail here;
    # this assertion caught exactly that bug on first run: even residuals hid
    # the odd prime for N in {10, 20, 26, 34})
    "N2": 1.0, "N4": 1.0, "N8": 1.0, "N16": 1.0, "N32": 1.0,
    "N10_q5m1": 4/3, "N20_q5m1": 4/3, "N40_q5m1": 4/3,
    "N18_q9m1": 8/7, "N26_q13m1": 12/11, "N34_q17m1": 16/15,
    "N50_q5m1": 4/3, "N50_q5m2": (4/3)**2,
    "N100_q5m1": 4/3, "N100_q5m2": (4/3)**2,
}


def main():
    C, tail = cprime_g()
    print(f"C'_G = {C:.8f}  (relative tail bound {tail:.2e}, Q={Q_CUT:.0e})", flush=True)
    table = {}
    for N in MANDATORY_SHELLS + SECONDARY_SHELLS:
        for key, offs in sorted(shell_classes(N).items()):
            cid = f"N{N}" + ("" if not key else "_" + "x".join(f"q{q}m{m}" for q, m in key))
            table[cid] = dict(shell=N, divisor_key=list(key), n_offsets=len(offs),
                              offsets=offs, S_prime_pred=float(s_prime(key, C)),
                              mandatory=bool(N in MANDATORY_SHELLS))
            print(f"  {cid}: {len(offs)} offsets, pred S' = {table[cid]['S_prime_pred']:.6f}")
    # executable hand-table gate: every HAND_TABLE cid must exist with the
    # exact predicted ratio; every produced mandatory cid at a hand shell must
    # be IN the hand table (no unexpected class splits)
    for cid, ratio in HAND_TABLE.items():
        assert cid in table, f"HAND TABLE FAIL: expected class {cid} missing"
        got = table[cid]["S_prime_pred"] / C
        assert abs(got - ratio) < 1e-12, f"HAND TABLE FAIL {cid}: {got} != {ratio}"
    for cid, row in table.items():
        if row["shell"] in (2, 4, 8, 16, 32, 10, 20, 40, 18, 26, 34, 50, 100):
            assert cid in HAND_TABLE, f"HAND TABLE FAIL: unexpected class {cid}"
    print("HAND TABLE CHECK: PASS", flush=True)
    out = dict(C_prime_G=C, tail_bound_rel=tail, Q_cut=Q_CUT,
               anchor="Gross-Smith via KRR arXiv:2001.09513 (Ramanujan J. 58, 2022); "
                      "source archived comb/lit/; S_GS(h) = 2*S'(h)",
               classes=table)
    with open("/home/combust/fmexplorer/criticality_tool/comb/singular_series_banked.json", "w") as f:
        json.dump(out, f, indent=1)
    print("BANKED", flush=True)


if __name__ == "__main__":
    main()

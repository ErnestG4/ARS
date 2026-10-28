"""GEO-TOT1 analysis: seen-range check, gates, witness and the sealed read (GEOTOT1_SEAL.md; criteria there).

Estimator (per-q law). Bins: 10 per decade, bin j = {q : 10^(j/10) ≤ q < 10^((j+1)/10)}. Per bin: x = mean ln q over its
integers, y = ln(Σ count / #q) (the bin's mean count per q; bin totals only, no per-q logs). OLS slope of y on x over
the bins inside the window. Seen range: bins 23 … 32 (q ∈ [200, 1995]); fit window [Q/10, Q): bins 10·log10 Q − 10 …
10·log10 Q − 1. SE: the OLS residual SE (descriptive).
Cumulative: C(Q′) = Σ_{q ≤ Q′} count(q) at Q′ = ⌈10^(j/10)⌉ − 1 for the window's 11 bin edges; OLS slope of ln C on ln Q′.
Surrogate: per q and length L, Binomial(L_hist[q, L], P_N^L) with P_N = 1 − log₂(1 + 1/(N + 1)) (i.i.d. Gauss–Kuzmin
digits, all ≤ N), numpy default_rng(SEED); the same slope estimator.

  python geotot1_analyze.py seen OUT_JSON                     q ≤ 2000, computed here (seen range)
  python geotot1_analyze.py gates NPZ Q OUT_JSON
  python geotot1_analyze.py witness NPZ Q OUT_JSON
  python geotot1_analyze.py read NPZ Q OUT_JSON
"""
import json
import math
import sys
from fractions import Fraction

import numpy as np

DELTA = {2: 0.5312805, 3: 0.7056609, 4: 0.7889455, 5: 0.8368294}     # replaced by the Step 0 values at sealing
TOL = 0.03
MU = 12 * math.log(2) / math.pi ** 2
KAPPA = 0.516                                                         # replaced by the Step 0 value at sealing
SEED = 20261027
ZETA3_OVER_ZETA4 = 1.2020569031595942853997 / (math.pi ** 4 / 90)
N_SEALED = (3, 4, 5)


def load(npz):
    d = np.load(npz)
    return {k: d[k] for k in d.files}


def bins(j0, j1):
    return [(j, math.ceil(10 ** (j / 10)), math.ceil(10 ** ((j + 1) / 10))) for j in range(j0, j1)]


def window(Q):
    k = round(10 * math.log10(Q))
    assert 10 ** (k / 10) == Q or abs(10 ** (k / 10) - Q) < 1e-6 * Q
    return k - 10, k


def slope(q, cnt, j0, j1):
    xs, ys = [], []
    for j, lo, hi in bins(j0, j1):
        m = (q >= lo) & (q < hi)
        xs.append(float(np.mean(np.log(q[m]))))
        ys.append(math.log(float(cnt[m].sum()) / int(m.sum())))
    X = np.vstack([np.ones(len(xs)), xs]).T
    c = np.linalg.lstsq(X, np.array(ys), rcond=None)[0]
    e = np.array(ys) - X @ c
    se = math.sqrt(float(e @ e) / (len(xs) - 2) * np.linalg.inv(X.T @ X)[1, 1])
    return float(c[1]), se


def cum_slope(q, cnt, j0, j1):
    C = np.cumsum(cnt)
    Qs = [math.ceil(10 ** (j / 10)) - 1 for j in range(j0, j1 + 1)]
    idx = [int(np.searchsorted(q, Qp)) for Qp in Qs]
    assert all(q[i] == Qp for i, Qp in zip(idx, Qs))
    return float(np.polyfit(np.log(Qs), np.log([C[i] for i in idx]), 1)[0])


def theory_surrogate(N):
    lp = math.log(1 - math.log2(1 + 1 / (N + 1)))
    return 1 + MU * lp + 0.5 * KAPPA * lp * lp


def seen(out):
    import geotot1 as G
    arrs = dict(zip(G.KEYS, G.enum(2, 2000)))
    q = np.arange(2, 2001)
    res = dict(label="GEO-TOT1 seen range q <= 2000 (browser preview range)", per_q={}, cumulative={}, surrogate={})
    for conv, key in (("canon", "cnt_canon"), ("alt", "cnt_alt")):
        res["per_q"][conv] = {}
        for N in N_SEALED:
            s, se = slope(q, arrs[key][:, N - 2], 23, 33)
            res["per_q"][conv][N] = dict(slope=s, SE=se, target=2 * DELTA[N] - 1, miss=s - (2 * DELTA[N] - 1))
        res["exceptions"] = res.get("exceptions", {})
        res["exceptions"][conv] = {N: [int(x) for x in q[arrs[key][:, N - 2] == 0]] for N in (3, 4, 5, 6)}
    for N in N_SEALED:
        res["cumulative"][N] = dict(slope=cum_slope(q, arrs["cnt_canon"][:, N - 2], 23, 32), target=2 * DELTA[N])
        L = np.arange(arrs["L_hist"].shape[1])
        P = 1 - math.log2(1 + 1 / (N + 1))
        E = (arrs["L_hist"] * P ** L).sum(1)
        res["surrogate"][N] = dict(expectation_slope=slope(q, E, 23, 33)[0], theory=theory_surrogate(N),
                                   theory_no_var=1 + MU * math.log(P))
    i = 360 - 2
    res["mean_depth_360"] = dict(sum_pq=float(arrs["S_sum"][i] / arrs["phi"][i]),
                                 stern_brocot=float(arrs["S_sum"][i] / arrs["phi"][i] - 1),
                                 yao_knuth_leading=6 / math.pi ** 2 * math.log(360) ** 2)
    res["seen_range_supports_tol"] = bool(all(abs(v["miss"]) <= TOL for v in res["per_q"]["canon"].values()))
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print(json.dumps(res, sort_keys=True)[:3000])
    return 0


def phi_sieve(Q):
    """Independent totient (linear sieve, numpy)."""
    phi = np.arange(Q + 1, dtype=np.int64)
    for p in range(2, Q + 1):
        if phi[p] == p:
            phi[p::p] -= phi[p::p] // p
    return phi


def brute_has_key(q, N):
    for a in range(1, q):
        if math.gcd(a, q) != 1:
            continue
        x, y, ok = q, a, True
        while y:
            t, (x, y) = x // y, (y, x % y)
            if t > N:
                ok = False
                break
        if ok:
            return True
    return False


def gates(npz, Q, out):
    d = load(npz)
    q = d["q"]
    assert int(q[0]) == 2 and int(q[-1]) == Q
    j0, j1 = window(Q)
    res = {}
    phi = phi_sieve(Q)
    res["farey"] = dict(length_enum=int(1 + d["phi"].sum()) + 1, length_sieve=int(1 + phi[1:].sum()),
                        per_q_equal=bool(np.array_equal(d["phi"], phi[2:])))
    # Farey F_Q = 1 + Σ_{q=1}^{Q} φ(q); the enumeration starts at q = 2, so add φ(1) = 1
    res["farey"]["GATE"] = bool(res["farey"]["per_q_equal"] and res["farey"]["length_enum"] == res["farey"]["length_sieve"])
    s = math.fsum([1.0] + [float(Fraction(int(p), int(qq) ** 4)) for p, qq in zip(d["phi"], q)])
    tail = 1 / (2 * Q * Q)
    res["ford"] = dict(sum=s, target=ZETA3_OVER_ZETA4, diff=s - ZETA3_OVER_ZETA4, tail_bound=tail,
                       GATE=bool(abs(s - ZETA3_OVER_ZETA4) <= tail + 1e-14))
    ex4 = [int(x) for x in q[(d["cnt_canon"][:, 2] == 0) & (q <= 2000)]]
    res["bound4_le_2000"] = dict(exceptions=ex4, GATE=ex4 == [6, 54, 150],
                                 all_exceptions_to_Q=[int(x) for x in q[d["cnt_canon"][:, 2] == 0]])
    ex5 = [int(x) for x in q[d["cnt_canon"][:, 3] == 0]]
    res["bound5"] = dict(exceptions=ex5, brute_reproduced=[int(x) for x in ex5 if not brute_has_key(int(x), 5)],
                         GATE=len(ex5) == 0)
    res["cumulative"] = {}
    for N in N_SEALED:
        sl = cum_slope(q, d["cnt_canon"][:, N - 2], j0, j1)
        res["cumulative"][N] = dict(slope=sl, target=2 * DELTA[N], miss=sl - 2 * DELTA[N], GATE=bool(abs(sl - 2 * DELTA[N]) <= TOL))
    res["ALL_GATES"] = bool(res["farey"]["GATE"] and res["ford"]["GATE"] and res["bound4_le_2000"]["GATE"]
                            and res["bound5"]["GATE"] and all(v["GATE"] for v in res["cumulative"].values()))
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print("ALL_GATES", res["ALL_GATES"])
    return 0


def witness(npz, Q, out):
    d = load(npz)
    q = d["q"]
    j0, j1 = window(Q)
    rng = np.random.default_rng(SEED)
    L = np.arange(d["L_hist"].shape[1])
    res = {}
    for N in N_SEALED:
        P = 1 - math.log2(1 + 1 / (N + 1))
        sur = rng.binomial(d["L_hist"], P ** L).sum(1)
        s, se = slope(q, sur, j0, j1)
        own = theory_surrogate(N)
        expect = slope(q, (d["L_hist"] * P ** L).sum(1), j0, j1)[0]
        res[str(N)] = dict(slope=s, SE=se, own_theory=own, own_expectation=expect, target_2delta_minus_1=2 * DELTA[N] - 1,
                      recovers_own=bool(abs(s - own) <= TOL), fails_2delta=bool(abs(s - (2 * DELTA[N] - 1)) > TOL))
        res[str(N)]["OK"] = bool(res[str(N)]["recovers_own"] and res[str(N)]["fails_2delta"])
    res["WITNESS_OK"] = bool(all(res[str(N)]["OK"] for N in N_SEALED))
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print("WITNESS_OK", res["WITNESS_OK"])
    return 0


def arith_type(qq):
    f, n, p = {}, qq, 2
    while p * p <= n:
        while n % p == 0:
            f[p] = f.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    if len(f) == 1:
        return "prime" if list(f.values())[0] == 1 else "prime_power"
    return "smooth" if max(f) <= 100 else "other"            # smooth: every prime factor ≤ 100


def read(npz, Q, out):
    d = load(npz)
    q = d["q"]
    j0, j1 = window(Q)
    res = dict(Q=Q, window=[math.ceil(10 ** (j0 / 10)), math.ceil(10 ** (j1 / 10)) - 1], tol=TOL, per_q={})
    for N in N_SEALED:
        s, se = slope(q, d["cnt_canon"][:, N - 2], j0, j1)
        tgt = 2 * DELTA[N] - 1
        res["per_q"][N] = dict(slope=s, SE=se, target=tgt, miss=s - tgt, verdict="PASS" if abs(s - tgt) <= TOL else "FAIL",
                               slope_alt=slope(q, d["cnt_alt"][:, N - 2], j0, j1)[0])
    res["ordering_slopes_increase_with_N"] = bool(res["per_q"][3]["slope"] < res["per_q"][4]["slope"] < res["per_q"][5]["slope"])
    res["verdict"] = "PASS" if all(v["verdict"] == "PASS" for v in res["per_q"].values()) else "FAIL"
    # descriptive: c_N(q) by arithmetic type, in the window
    m = (q >= res["window"][0]) & (q <= res["window"][1])
    types = np.array([arith_type(int(x)) for x in q[m]])
    res["c_N_by_type"] = {}
    for N in N_SEALED:
        c = d["cnt_canon"][m, N - 2] / q[m].astype(float) ** (2 * DELTA[N] - 1)
        res["c_N_by_type"][N] = {t: dict(n=int((types == t).sum()), mean=float(c[types == t].mean()),
                                         sd=float(c[types == t].std(ddof=1))) for t in sorted(set(types))}
    res["bound4_exceptions_to_Q"] = [int(x) for x in q[d["cnt_canon"][:, 2] == 0]]
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print("verdict", res["verdict"])
    return 0


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "seen":
        sys.exit(seen(sys.argv[2]))
    f = {"gates": gates, "witness": witness, "read": read}[c]
    sys.exit(f(sys.argv[2], int(float(sys.argv[3])), sys.argv[4]))

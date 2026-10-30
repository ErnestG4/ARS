"""GEO1 Step 1 (Will, 2026-10-27 brief; go 2026-10-30): closed geodesics of the modular surface as SL(2,ℤ) hyperbolic
conjugacy classes, by trace t ≥ 3 (length ℓ = 2 arccosh(t/2)). Plan, gates and tolerances: GEO1_STEP1_PLAN.md.

Three independent routes to the number of classes of trace t:
  words  every class contains exactly one "reduced" positive matrix per R-run of its cyclic R/L word:
         M = (a b; c d), a, b, c, d ≥ 1, a + d = t, ad − bc = 1, a ≥ b ≥ d, a ≥ c ≥ d (word starts with R, ends with L).
         Each is decomposed into its run vector (r₁, l₁, …, r_m, l_m) (the regular continued-fraction digits of the
         cutting sequence); a class is counted once, at the matrix whose run vector is the least of its even rotations;
         it is primitive iff that vector has no shorter even period. Per t: all classes, primitive classes, and the
         pooled digit histogram over primitive classes.
  pari   g_all(t) = Σ_u h⁺(d), d = (t² − 4)/u² ≡ 0, 1 (mod 4), with h⁺(d) = h(d)·(2 if N(ε_d) = +1 else 1);
         h(d) from PARI quadclassunit (the class number of the order of discriminant d; GRH-conditional for large d),
         N(ε_d) from quadunitnorm. g_prim(t) = g_all(t) − Σ_{k ≥ 2, V_k(t′) = t} g_prim(t′) (powers of primitive classes;
         V_k the trace of the k-th power).
  forms  (t ≤ 40) every positive matrix with c ≤ t maps to the primitive form (c, d − a, −b)/u, u = gcd; classes are
         the distinct (u, least reduced form of the Gauss ρ-cycle), with exact integer arithmetic. Independent of both.

  python geo1.py words T OUT_NPZ                  t = 3 … T (numba, threads); 10 cost-balanced sub-calls, cost checks
  python geo1.py pari T0 T1 OUT_NPZ               t = T0 … T1 (one process; run many in parallel)
  python geo1.py forms TMAX OUT_JSON              t = 3 … TMAX
  python geo1.py list T OUT_JSON                  canonical run vectors of every class of trace T (words route)
  python geo1.py merge OUT_NPZ PART …              concatenate pari parts (t ascending, contiguous)
"""
import json
import math
import sys
import time

import numpy as np

try:
    from numba import njit, prange
except ImportError:                 # the pari route runs in spot's `specarith` env (cypari2, no numba)
    def njit(*a, **k):
        return (lambda f: f) if not (len(a) == 1 and callable(a[0])) else a[0]
    prange = range

K = 64                      # digit histogram bins 1 … K; bin K + 1 collects digits > K
MAXR = 256                  # run-vector buffer (runs per word); asserted


@njit(cache=False)
def isqrt(n):
    r = int(math.sqrt(n))
    while r * r > n:
        r -= 1
    while (r + 1) * (r + 1) <= n:
        r += 1
    return r


@njit(cache=False)
def runs_of(a, b, c, d, buf):
    """Run lengths of the R/L word of a positive matrix in SL(2,ℤ) (alternating, first run R). Returns the count."""
    m = 0
    while not (a == 1 and b == 0 and c == 0 and d == 1):
        if a >= c and b >= d:                               # R^k
            k = a // c if c > 0 else 1 << 62
            if d > 0:
                k = min(k, b // d)
            a, b = a - k * c, b - k * d
            if m % 2 == 0:
                buf[m] = k
                m += 1
            else:                                           # an R after an R-run cannot happen; keep alternation
                buf[m - 1] += k
        else:                                               # L^k
            k = c // a if a > 0 else 1 << 62
            if b > 0:
                k = min(k, d // b)
            c, d = c - k * a, d - k * b
            if m % 2 == 1:
                buf[m] = k
                m += 1
            else:
                buf[m] = 0                                  # (never for a word starting with R)
                buf[m + 1] = k
                m += 2
    return m


@njit(cache=False)
def canon(buf, m):
    """(is the vector the least of its even rotations, is it primitive)."""
    for j in range(2, m, 2):
        cmp = 0
        for i in range(m):
            x, y = buf[(i + j) % m], buf[i]
            if x != y:
                cmp = -1 if x < y else 1
                break
        if cmp < 0:
            return False, False
        if cmp == 0:
            return True, False                              # periodic with period j < m: not primitive
    return True, True


@njit(cache=False)
def scan_t(t, hist):
    """Classes of trace t by the words route. Returns (reduced matrices, classes, primitive classes, Σ runs over
    primitive, Σ letters over primitive); fills hist[k] with digit counts over primitive classes."""
    buf = np.zeros(MAXR, np.int64)
    nred = nall = nprim = sruns = slet = 0
    for dd in range(1, t // 2 + 1):
        a = t - dd
        n = a * dd - 1
        if n < 1:
            continue
        r = isqrt(n)
        for b in range(dd, r + 1):
            if n % b != 0:
                continue
            c = n // b
            for sw in range(2):
                bb, cc = (b, c) if sw == 0 else (c, b)
                if sw == 1 and b == c:
                    break
                if bb > a or cc > a or bb < dd or cc < dd:
                    continue
                nred += 1
                m = runs_of(a, bb, cc, dd, buf)
                ok, prim = canon(buf, m)
                if not ok:
                    continue
                nall += 1
                if prim:
                    nprim += 1
                    sruns += m
                    for i in range(m):
                        hist[min(buf[i], K + 1)] += 1
                        slet += buf[i]
    return nred, nall, nprim, sruns, slet


@njit(cache=False, parallel=True)
def scan_list(ts, out, hist):
    for i in prange(len(ts)):
        r = scan_t(ts[i], hist[i])
        for j in range(5):
            out[i, j] = r[j]


def words(T, out):
    ts_all = np.arange(3, T + 1, dtype=np.int64)
    cost = (ts_all.astype(float) ** 2)
    edges = np.searchsorted(np.cumsum(cost), np.linspace(0, cost.sum(), 11)[1:-1])
    groups = np.split(np.arange(len(ts_all)), edges)
    out_all = np.zeros((len(ts_all), 5), np.int64)
    hist_all = np.zeros((len(ts_all), K + 2), np.int64)
    scan_list(np.array([3, 4], np.int64), np.zeros((2, 5), np.int64), np.zeros((2, K + 2), np.int64))   # compile
    model = lambda ts: float(np.sum(ts.astype(float) ** 2)) * 0.071 * 1.2e-9 * 2.3   # core-s on spot (plan §5)
    t0 = time.process_time()
    done = []
    for gi, g in enumerate(groups):
        if gi in (1, 3, 5, 8) and model(ts_all[np.concatenate(done)]) >= 60:      # not meaningful below a minute
            r = (time.process_time() - t0) / model(ts_all[np.concatenate(done)])
            print(f"after {gi} of 10 groups: cpu/model = {r:.3f}", flush=True)
            if r > 1.25:
                open(out + ".STOPPED", "w").write(f"cost {r:.3f}x at group {gi}\n")
                return 3
        rng = np.random.default_rng(gi)
        perm = rng.permutation(g)
        o = np.zeros((len(perm), 5), np.int64)
        h = np.zeros((len(perm), K + 2), np.int64)
        scan_list(ts_all[perm], o, h)
        out_all[perm], hist_all[perm] = o, h
        done.append(g)
    cpu = time.process_time() - t0
    np.savez(out, t=ts_all, nred=out_all[:, 0], nall=out_all[:, 1], nprim=out_all[:, 2], sruns=out_all[:, 3],
             slet=out_all[:, 4], hist=hist_all)
    open(out + ".cpu", "w").write(f"{cpu:.3f} {cpu / model(ts_all):.4f}\n")
    print(f"done: cpu {cpu / 3600:.3f} core-h = {cpu / model(ts_all):.3f}x model", flush=True)
    return 0


def list_t(T, out):
    """Canonical run vectors of every class of trace T (words route), for the R²L² gate and inspection."""
    buf = np.zeros(MAXR, np.int64)
    res = []
    for dd in range(1, T // 2 + 1):
        a = T - dd
        n = a * dd - 1
        for b in range(1, n + 1):
            if n % b:
                continue
            c = n // b
            if b > a or c > a or b < dd or c < dd:
                continue
            m = runs_of(a, b, c, dd, buf)
            ok, prim = canon(buf, m)
            if ok:
                res.append(dict(matrix=[a, b, c, dd], runs=[int(x) for x in buf[:m]], primitive=bool(prim)))
    json.dump(dict(t=T, classes=res), open(out, "w"), indent=1)
    print(T, len(res), [r["runs"] for r in res])
    return 0


# ---------------- pari route ----------------
def V(k, t):
    a, b = 2, t
    for _ in range(k - 1):
        a, b = b, t * b - a
    return b if k >= 1 else 2


def pari(T0, T1, out):
    import cypari2
    P = cypari2.Pari()
    P.allocatemem(10 ** 9)
    rows = []
    g_all = np.zeros(T1 - T0 + 1, np.int64)
    g_wide = np.zeros(T1 - T0 + 1, np.int64)
    t0 = time.process_time()
    for t in range(T0, T1 + 1):
        n = t * t - 4
        fac = P.factor(n)
        ps, es = [int(x) for x in fac[0]], [int(x) for x in fac[1]]
        us = [1]
        for p, e in zip(ps, es):
            us = [u * p ** j for u in us for j in range(e // 2 + 1)]
        for u in sorted(us):
            d = n // (u * u)
            if d % 4 not in (0, 1):
                continue
            h = int(P(f"quadclassunit({d})[1]"))
            nu = int(P(f"quadunitnorm({d})"))
            hp = h * (2 if nu == 1 else 1)
            g_all[t - T0] += hp
            g_wide[t - T0] += h
            rows.append((t, u, d, h, nu))
    cpu = time.process_time() - t0
    rows = np.array(rows, np.int64).reshape(-1, 5)
    np.savez(out, t=np.arange(T0, T1 + 1, dtype=np.int64), g_all=g_all, g_wide=g_wide, rows=rows)
    open(out + ".cpu", "w").write(f"{cpu:.3f}\n")
    return 0


def g_prim_from_all(t, g_all):
    """g_prim(t) = g_all(t) − Σ_{k ≥ 2} Σ_{t′ ≥ 3: V_k(t′) = t} g_prim(t′), for t = 3 … T (t[i] = i + 3)."""
    T = int(t[-1])
    gp = g_all.astype(np.int64).copy()
    for tp in range(3, T + 1):
        k = 2
        while True:
            v = V(k, tp)
            if v > T:
                break
            gp[v - 3] -= gp[tp - 3]
            k += 1
    return gp


# ---------------- forms route (independent, small t) ----------------
def _reduced(A, B, C, D, s):
    return 0 < B <= s and s - B < 2 * abs(A) <= s + B


def _rho(A, B, C, D, s):
    c2 = 2 * abs(C)
    # B* ≡ −B (mod 2|C|), chosen in (√D − 2|C|, √D) if |C| < √D, else in (−|C|, |C|] (Buchmann–Vollmer normalisation)
    if abs(C) <= s:
        lo = s - c2 + 1                                      # B* > √D − 2|C|  ⇔ B* ≥ s − 2|C| + 1
        Bs = lo + ((-B - lo) % c2)
    else:
        lo = -abs(C) + 1
        Bs = lo + ((-B - lo) % c2)
    Cs = (Bs * Bs - D) // (4 * C)
    return C, Bs, Cs


def _cycle_min(A, B, C):
    D = B * B - 4 * A * C
    s = math.isqrt(D)
    seen = 0
    while not _reduced(A, B, C, D, s):
        A, B, C = _rho(A, B, C, D, s)
        seen += 1
        assert seen < 10 ** 5
    start = (A, B, C)
    best = start
    cur = _rho(A, B, C, D, s)
    n = 1
    while cur != start:
        assert _reduced(*cur, D, s)
        best = min(best, cur)
        cur = _rho(*cur, D, s)
        n += 1
        assert n < 10 ** 6
    return best


def forms(TMAX, out):
    res = {}
    for t in range(3, TMAX + 1):
        cls = set()
        for a in range(1, t):
            dd = t - a
            n = a * dd - 1
            for c in range(1, t + 1):
                if n % c:
                    continue
                b = n // c
                A, B, C = c, dd - a, -b
                u = math.gcd(math.gcd(abs(A), abs(B)), abs(C))
                A, B, C = A // u, B // u, C // u
                cls.add((u, _cycle_min(A, B, C)))
        res[t] = len(cls)
    json.dump(dict(TMAX=TMAX, classes={str(t): v for t, v in res.items()}), open(out, "w"), indent=1)
    print(res)
    return 0


def merge(out, parts):
    ds = sorted((np.load(x) for x in parts), key=lambda d: int(d["t"][0]))
    for x, y in zip(ds, ds[1:]):
        assert int(y["t"][0]) == int(x["t"][-1]) + 1
    np.savez(out, **{k: np.concatenate([d[k] for d in ds]) for k in ("t", "g_all", "g_wide", "rows")})
    return 0


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "words":
        sys.exit(words(int(float(sys.argv[2])), sys.argv[3]))
    if m == "pari":
        sys.exit(pari(int(float(sys.argv[2])), int(float(sys.argv[3])), sys.argv[4]))
    if m == "forms":
        sys.exit(forms(int(sys.argv[2]), sys.argv[3]))
    if m == "list":
        sys.exit(list_t(int(sys.argv[2]), sys.argv[3]))
    if m == "merge":
        sys.exit(merge(sys.argv[2], sys.argv[3:]))

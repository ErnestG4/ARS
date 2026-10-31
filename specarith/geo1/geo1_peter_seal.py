"""GEO1 Peter-correlation seal (Will's brief 2026-10-30; T₂ = 3·10⁶ and D23 on the 4090, 2026-10-31). Design, criteria
and their justification: GEO1_PETER_SEAL.md. Fresh range: traces 10⁶ < t ≤ 3·10⁶ (never computed before the seal).

Statistics on the fresh window n ∈ [T₁ + 1, T₂ − 120] (the same n for every lag; α̃(n) = g_prim(n) log n / n − 1):
  γ̂(r) = (1/N) Σ_n α̃(n) α̃(n + r) for the 23 committed lags, primary ratio γ̂(r)/γ̂(0) (r ≠ 0), secondary γ̂(0) and the
  raw γ̂(r). Predictions: Peter's Euler product (results/peter/PRED.json, p ≤ 10⁵, tail bound included).
Tolerance per statistic: |dev trend at the fresh window| + Z_B·SE + tail, SE = max(dev block-jackknife SE projected to
  the fresh N, generator SD at the fresh N); Z_B = Φ⁻¹(1 − 0.05/90) (Bonferroni, 45 statistics, two-sided).
Planted generator (witness, D23): α(n) = δ_P(n + s) ξ(n), δ_P = Π_{p ≤ 997} δ_{p^B}(n mod p^B) (SL(2, ℤ/p^B) trace
  densities; B = 7, 4, 3, 2, 2, 2 for p = 2 … 13, else 1), independent uniform shifts s per prime power, ξ i.i.d. from
  the dev residual pool α/δ_P on n ∈ [316228, 10⁶) normalised to mean 1. Exact planted values: γ(r) = Π_q mean(δ_q δ_q(·+r))
  − 1 (r ≠ 0), γ(0) = Π_q mean(δ_q²)·E[ξ²] − 1. Matched-marginal independent-lag null: ξ i.i.d. from the dev α pool.

  python geo1_peter_seal.py tables-check OUT_JSON
  python geo1_peter_seal.py hsample SEED NS T1 T2 OUT_JSON
  python geo1_peter_seal.py cfcheck OUT_JSON                      (cypari2: CF unit-norm parity against quadunitnorm)
  python geo1_peter_seal.py hind HSAMPLE_JSON I0 I1 OUT_JSON      (cypari2: qfbclassno + CF parity, independent)
  python geo1_peter_seal.py calibrate DEV_NPZ PRED_JSON DEV_JSON GEN_SD_JSON OUT_JSON
  python geo1_peter_seal.py finalize TOL_JSON D23_JSON D23N_JSON PRED_JSON OUT_JSON
  python geo1_peter_seal.py read DEV_NPZ FRESH_NPZ PARAMS_JSON HSAMPLE_JSON HIND_JSON OUT_JSON
  python geo1_peter_seal.py dryparams PARAMS_JSON DEV_NPZ T1 T2 OUT_DIR   (§9.F: split the dev range into dev/"fresh")
"""
import hashlib
import json
import math
import statistics
import sys
import time

import numpy as np

from geo1 import g_prim_from_all
from geo1_peter import primes_upto, trace_density, local_factor

T1, T2 = 10 ** 6, 3 * 10 ** 6
RMAX = 120
BLOCK = 10 ** 4
NSTAT = 45
Z_B = statistics.NormalDist().inv_cdf(1 - 0.05 / (2 * NSTAT))
PGEN = 997
BPOW = {2: 7, 3: 4, 5: 3, 7: 2, 11: 2, 13: 2}
POOL = (316228, 10 ** 6)                 # dev n range of the generator pools (k = 22, 23 quarter-decades)
CAL_K = (21, 22, 23)                     # dev quarter-decade windows for the projected block-jackknife SE
DEV_SHA = "c72380f922ab16bb84c6f905ee2b1246b78d3b46b8e847540c88fb2f589b3258"
SEEDS = dict(shuffle=20261101, null=20261102, planted=20261103)
POWER_MIN = 0.80


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def dump(obj, path):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
        f.write("\n")


# ---------------- local densities and the planted generator ----------------
def legendre_vec(p, x):
    sq = np.zeros(p, np.int64)
    sq[(np.arange(1, p) ** 2) % p] = 1
    chi = np.where(sq == 1, 1, -1)
    chi[0] = 0
    return chi[x % p]


def tables(P=PGEN, drop=()):
    """[(q, δ_q)] for p ≤ P: counted SL(2, ℤ/q) trace densities for q = p^B, B > 1; closed form (p² + p χ(n² − 4))/(p² − 1)
    for B = 1 (checked against counts in tables-check)."""
    out = []
    for p in primes_upto(P):
        p = int(p)
        if p in drop:
            continue
        B = BPOW.get(p, 1)
        if B > 1:
            tab = trace_density(p ** B)
        else:
            n = np.arange(p)
            tab = (p * p + p * legendre_vec(p, n * n - 4)) / (p * p - 1)
        out.append((p ** B, np.asarray(tab, np.float64)))
    return out


def delta(n0, L, tabs, shifts=None):
    i = np.arange(n0, n0 + L, dtype=np.int64)
    d = np.ones(L)
    for k, (q, tab) in enumerate(tabs):
        s = 0 if shifts is None else int(shifts[k])
        d *= tab[(i + s) % q]
    return d


def planted_exact(lags, tabs, m2):
    g = {}
    for r in lags:
        f = 1.0
        for q, tab in tabs:
            f *= float(np.mean(tab * np.roll(tab, -(r % q))))
        g[r] = f * (m2 if r == 0 else 1.0) - 1.0
    return g


def tables_check(out):
    res = []
    for p in primes_upto(47)[1:]:
        p = int(p)
        n = np.arange(p)
        closed = (p * p + p * legendre_vec(p, n * n - 4)) / (p * p - 1)
        res.append(dict(p=p, max_abs_diff=float(np.max(np.abs(closed - trace_density(p))))))
    tabs = tables()
    means = [abs(float(t.mean()) - 1) for _, t in tabs]
    mx = max(r["max_abs_diff"] for r in res)
    dump(dict(closed_form_vs_counts=res, max_abs_diff=mx, n_tables=len(tabs), max_abs_mean_minus_1=max(means),
              min_density=float(min(t.min() for _, t in tabs))), out)
    print("closed form vs counts, p ≤ 47: max diff", mx, "| tables", len(tabs), "| max |mean − 1|", max(means),
          "| min density", min(t.min() for _, t in tabs))
    return 0 if mx < 1e-12 and max(means) < 1e-12 else 1


# ---------------- data ----------------
def alpha_tilde(dev_npz, fresh_npz=None):
    d = np.load(dev_npz)
    t, g = d["t"].astype(np.int64), d["g_all"].astype(np.int64)
    if fresh_npz is not None:
        f = np.load(fresh_npz)
        assert int(f["t"][0]) == int(t[-1]) + 1
        t = np.concatenate([t, f["t"].astype(np.int64)])
        g = np.concatenate([g, f["g_all"].astype(np.int64)])
    assert int(t[0]) == 3 and np.all(np.diff(t) == 1)
    gp = g_prim_from_all(t, g).astype(np.float64)
    return gp * np.log(t) / t - 1.0


def pools(dev_npz):
    """Residual pool α/δ_P and α pool on dev n ∈ POOL, each normalised to mean 1."""
    a = alpha_tilde(dev_npz) + 1.0
    lo, hi = POOL
    al = a[lo - 3:hi - 3]
    res = al / delta(lo, hi - lo, tables())
    return res / res.mean(), al / al.mean()


def window_stats(a, n_lo, n_hi, lags):
    """γ̂(r) on n ∈ [n_lo, n_hi] (same n for every lag), ratios, block-jackknife SEs (blocks of 10⁴)."""
    i0, i1 = n_lo - 3, n_hi - 3 + 1
    N = i1 - i0
    assert i1 - 1 + max(lags) < len(a)
    nb = N // BLOCK
    S, Sb, g = {}, {}, {}
    for r in lags:
        y = a[i0:i1] * a[i0 + r:i1 + r]
        S[r] = float(np.sum(y))
        g[r] = S[r] / N
        yb = y[:nb * BLOCK]
        Sb[r] = yb.reshape(nb, BLOCK).sum(1)
    tot = {r: float(np.sum(Sb[r])) for r in lags}
    m = nb * BLOCK - BLOCK

    def jk(th):
        return float(math.sqrt((nb - 1) / nb * np.sum((th - th.mean()) ** 2)))
    loo = {r: (tot[r] - Sb[r]) / m for r in lags}
    se = {r: jk(loo[r]) for r in lags}
    ratio = {r: g[r] / g[0] for r in lags if r}
    se_ratio = {r: jk(loo[r] / loo[0]) for r in lags if r}
    return dict(N=N, n_blocks=nb, gamma=g, ratio=ratio, se_gamma=se, se_ratio=se_ratio)


def stat_vector(st, lags):
    """Order: ratio r ≠ 0 (primary, 22), γ(0), raw γ(r ≠ 0) (secondary, 23)."""
    nz = [r for r in lags if r]
    return [st["ratio"][r] for r in nz] + [st["gamma"][0]] + [st["gamma"][r] for r in nz]


def stat_names(lags):
    nz = [r for r in lags if r]
    return [f"ratio_{r}" for r in nz] + ["gamma_0"] + [f"gamma_{r}" for r in nz]


def pred_vector(pred, lags):
    g = {r: pred["gamma"][str(r)]["gamma"] for r in lags}
    return stat_vector(dict(gamma=g, ratio={r: g[r] / g[0] for r in lags if r}), lags)


def lags_of(pred):
    return sorted(int(r) for r in pred["gamma"])


# ---------------- class-number inputs ----------------
def hsample(seed, ns, t1, t2, out):
    """Seeded (t, u) sample from the fresh range: t uniform; u = 1 or (half the time, when one exists) a uniform valid
    u > 1 with u² | t² − 4 and (t² − 4)/u² ≡ 0, 1 (mod 4). Uses nothing but t."""
    rng = np.random.default_rng(seed)
    rows = []
    ts = []
    while len(ts) < ns:
        t = int(rng.integers(t1 + 1, t2 + 1))
        if t not in ts:
            ts.append(t)
    for t in ts:
        n = t * t - 4
        us = _valid_u(t)
        u = 1
        if us and rng.random() < 0.5:
            u = int(us[int(rng.integers(len(us)))])
        rows.append(dict(t=t, u=u, d=n // (u * u)))
    dump(dict(seed=seed, T1=t1, T2=t2, rows=rows), out)
    print(len(rows), "samples;", sum(r["u"] > 1 for r in rows), "with u > 1")
    return 0


def _factor(m):
    f, p = {}, 2
    while p * p <= m:
        while m % p == 0:
            f[p] = f.get(p, 0) + 1
            m //= p
        p += 1 if p == 2 else 2
    if m > 1:
        f[m] = f.get(m, 0) + 1
    return f


def _valid_u(t):
    f = _factor(t - 2)
    for p, e in _factor(t + 2).items():
        f[p] = f.get(p, 0) + e
    us = [1]
    for p, e in f.items():
        us = [u * p ** j for u in us for j in range(e // 2 + 1)]
    n = t * t - 4
    return sorted(u for u in us if u > 1 and (n // (u * u)) % 4 in (0, 1))


def unit_norm_cf(d):
    """N(ε) of the order of discriminant d > 0 (non-square) from the parity of the period of the regular continued
    fraction of the reduced ω = (b + √d)/2, b the largest integer < √d with b ≡ d (mod 2): N(ε) = (−1)^period."""
    s = math.isqrt(d)
    assert s * s != d
    b = s if (s - d) % 2 == 0 else s - 1
    P, Q = b, 2
    k = 0
    while True:
        a = (P + s) // Q
        P = a * Q - P
        assert (d - P * P) % Q == 0
        Q = (d - P * P) // Q
        k += 1
        if P == b and Q == 2:
            return -1 if k % 2 else 1


def cfcheck(out):
    import cypari2
    Pa = cypari2.Pari()
    Pa.allocatemem(10 ** 9)
    rng = np.random.default_rng(20261104)
    ds = [d for d in range(5, 20001) if d % 4 in (0, 1) and math.isqrt(d) ** 2 != d]
    big = [int(x) for x in rng.integers(10 ** 8, 10 ** 11, size=400)]
    ds += [d for d in big if d % 4 in (0, 1) and math.isqrt(d) ** 2 != d]
    bad = sum(unit_norm_cf(d) != int(Pa(f"quadunitnorm({d})")) for d in ds)
    nneg = sum(unit_norm_cf(d) == -1 for d in ds)
    dump(dict(n=len(ds), mismatches=bad, n_norm_minus1=nneg), out)
    print(len(ds), "discriminants; mismatches", bad, "; norm −1:", nneg)
    return 0 if bad == 0 else 1


def hind(hs_json, i0, i1, out):
    """Independent route: h(d) from PARI qfbclassno (analytic class number formula, O(√d)), N(ε) from unit_norm_cf.
    The production route used quadclassunit (subexponential, GRH-conditional) and quadunitnorm."""
    import cypari2
    Pa = cypari2.Pari()
    Pa.allocatemem(2 * 10 ** 9)
    rows = json.load(open(hs_json))["rows"][i0:i1]
    res = []
    for r in rows:
        d = int(r["d"])
        res.append(dict(t=r["t"], u=r["u"], d=d, h=int(Pa(f"qfbclassno({d})")), nu=unit_norm_cf(d)))
    dump(dict(rows=res), out)
    return 0


def hcompare(fresh, hs_json, hind_jsons):
    """Programmatic comparison; returns counts only."""
    rows = fresh["rows"]
    key = {(int(r[0]), int(r[1])): (int(r[3]), int(r[4])) for r in rows}
    samp = json.load(open(hs_json))["rows"]
    ind = {}
    for j in hind_jsons:
        for r in json.load(open(j))["rows"]:
            ind[(int(r["t"]), int(r["u"]))] = (int(r["h"]), int(r["nu"]))
    n = len(samp)
    miss = sum((r["t"], r["u"]) not in key or (r["t"], r["u"]) not in ind for r in samp)
    mh = sum(key.get((r["t"], r["u"]), (None,))[0] == ind.get((r["t"], r["u"]), (-1,))[0] for r in samp)
    mn = sum(key.get((r["t"], r["u"]), (None, None))[1] == ind.get((r["t"], r["u"]), (-1, -1))[1] for r in samp)
    return dict(n=n, missing=miss, match_h=mh, match_nu=mn, all_match=(miss == 0 and mh == n and mn == n))


# ---------------- calibration (dev range only) ----------------
def fresh_mean_log(t1, t2):
    return float(np.log(np.arange(t1 + 1, t2 - RMAX + 1, dtype=np.float64)).mean())


def calibrate(dev_npz, pred_json, dev_json, gensd_json, out, t1=T1, t2=T2):
    assert sha(dev_npz) == DEV_SHA
    pred = json.load(open(pred_json))
    dev = json.load(open(dev_json))
    gsd = json.load(open(gensd_json))
    lags = lags_of(pred)
    names = stat_names(lags)
    NF = (t2 - RMAX) - (t1 + 1) + 1
    a = alpha_tilde(dev_npz)
    # projected block-jackknife SE: max over the CAL_K windows of SE·√N, divided by √N_F
    cal = []
    for k in CAL_K:
        lo, hi = int(round(10 ** (k / 4))), int(round(10 ** ((k + 1) / 4)))
        st = window_stats(a, lo, min(hi - 1, 10 ** 6 - RMAX), lags)
        se = [st["se_ratio"][r] for r in lags if r] + [st["se_gamma"][0]] + [st["se_gamma"][r] for r in lags if r]
        cal.append(dict(k=k, lo=lo, N=st["N"], n_blocks=st["n_blocks"], se=se,
                        se_sqrtN=[x * math.sqrt(st["N"]) for x in se]))
    proj = [max(c["se_sqrtN"][j] for c in cal) / math.sqrt(NF) for j in range(len(names))]
    # trend: the committed dev OLS (unweighted, diff on log of the window's geometric centre), at the fresh mean log n
    xF = fresh_mean_log(t1, t2)
    pv = pred_vector(pred, lags)
    nz = [r for r in lags if r]
    dd = dev["disjoint"]
    xs = np.array([math.log(math.sqrt(d["lo"] * d["hi"])) for d in dd["0"]])
    trend = []
    for r in nz:                                                          # ratio
        y = np.array(dev["ratio"][str(r)]["disjoint"]) - dev["ratio"][str(r)]["pred"]
        trend.append(float(np.polyval(np.polyfit(xs, y, 1), xF)))
    for r in [0] + nz:                                                     # raw γ
        y = np.array([d["diff"] for d in dd[str(r)]])
        trend.append(float(np.polyval(np.polyfit(xs, y, 1), xF)))
    # Euler-product truncation: |log(1+γ) tail| ≤ τ  ⇒  |Δγ| ≤ (1 + γ)(e^τ − 1); ratio by propagation
    g = {r: pred["gamma"][str(r)]["gamma"] for r in lags}
    tg = {r: (1 + g[r]) * math.expm1(pred["gamma"][str(r)]["log_tail_bound"]) for r in lags}
    tail = [(tg[r] + abs(g[r] / g[0]) * tg[0]) / abs(g[0]) for r in nz] + [tg[0]] + [tg[r] for r in nz]
    gen = gsd["sd_fresh"]
    gen_dev = gsd["sd_dev23"]
    se_used = [max(p, q) for p, q in zip(proj, gen)]
    tol_se = [Z_B * s for s in se_used]
    tol = [abs(tr) + ts + ta for tr, ts, ta in zip(trend, tol_se, tail)]
    real_dev23 = cal[-1]["se"]
    res = dict(T1=t1, T2=t2, RMAX=RMAX, N_fresh=NF, fresh_mean_log_n=xF, Z_B=Z_B, lags=lags, names=names, pred=pv,
               trend=trend, se_block_proj=proj, gen_sd=gen, se_used=se_used, tail=tail, tol_se_only=tol_se, tol=tol,
               cal_windows=cal, dev_sha256=DEV_SHA,
               generator_vs_real_at_dev23=dict(gen_sd=gen_dev, real_block_jk_se=real_dev23,
                                               ratio_gen_over_real=[x / y for x, y in zip(gen_dev, real_dev23)]))
    dump(res, out)
    print(f"Z_B {Z_B:.3f}  N_F {NF}  mean log n {xF:.4f}")
    print(f"{'stat':>10} {'pred':>9} {'trend':>9} {'SEproj':>8} {'genSD':>8} {'tol':>8}  gen/real@dev23")
    for j, nm in enumerate(names):
        print(f"{nm:>10} {pv[j]:9.5f} {trend[j]:+9.2e} {proj[j]:8.2e} {gen[j]:8.2e} {tol[j]:8.2e}  "
              f"{res['generator_vs_real_at_dev23']['ratio_gen_over_real'][j]:.2f}")
    return 0


# ---------------- finalize: powers, UNPOWERED flags, D23 gate ----------------
def finalize(tol_json, d23_json, d23n_json, pred_json, out):
    tol = json.load(open(tol_json))
    d23 = json.load(open(d23_json))
    d23n = json.load(open(d23n_json))
    pred = json.load(open(pred_json))
    lags = tol["lags"]
    nz = [r for r in lags if r]
    names = tol["names"]
    nd = statistics.NormalDist()

    def pw(delta, t, s):
        return nd.cdf((abs(delta) - t) / s) + nd.cdf((-abs(delta) - t) / s)
    # descriptive structure resolution: Peter's product against the product without prime p
    g = {r: pred["gamma"][str(r)]["gamma"] for r in lags}
    resol = {}
    for p in (2, 3, 5, 7, 11):
        gm = {r: (1 + g[r]) / local_factor(p, r) - 1 for r in lags}
        alt = stat_vector(dict(gamma=gm, ratio={r: gm[r] / gm[0] for r in nz}), lags)
        resol[str(p)] = [pw(tol["pred"][j] - alt[j], tol["tol"][j], tol["se_used"][j]) for j in range(len(names))]
    gate_power = []
    for j, nm in enumerate(names):
        if nm == "gamma_0":
            gate_power.append(dict(alternative="Euler product without p = 3 (normal approximation)",
                                   power=resol["3"][j]))
        else:
            gate_power.append(dict(alternative="matched-marginal independent-lag null (simulated)",
                                   power=d23["null"]["fail_rate_per_stat"][j]))
    powered = [x["power"] >= POWER_MIN for x in gate_power]
    gate = dict(d23_primary_se_only=d23["planted"]["pass_rate"]["primary_se_only"],
                d23_secondary_se_only=d23["planted"]["pass_rate"]["secondary_se_only"],
                d23_joint_se_only=d23["planted"]["pass_rate"]["joint_se_only"],
                null_primary_fail_rate=d23["null"]["family_fail_rate"]["primary"],
                noise_matched_c=d23n["noise_c"],
                d23n_primary_full=d23n["planted"]["pass_rate"]["primary_full"],
                d23n_secondary_full=d23n["planted"]["pass_rate"]["secondary_full"],
                d23n_joint_full=d23n["planted"]["pass_rate"]["joint_full"],
                d23n_se_only_reported=dict(primary=d23n["planted"]["pass_rate"]["primary_se_only"],
                                           secondary=d23n["planted"]["pass_rate"]["secondary_se_only"],
                                           joint=d23n["planted"]["pass_rate"]["joint_se_only"]))
    gate["ok"] = (min(gate["d23_primary_se_only"], gate["d23_secondary_se_only"], gate["d23_joint_se_only"],
                      gate["d23n_primary_full"], gate["d23n_secondary_full"], gate["d23n_joint_full"]) >= 0.95
                  and gate["null_primary_fail_rate"] >= 0.95)
    res = dict(tol)
    res.update(gate_power=gate_power, powered=powered, power_min=POWER_MIN, structure_resolution=resol,
               d23=dict(planted=d23["planted"]["pass_rate"], null=d23["null"]["family_fail_rate"],
                        drop3=d23["drop3"]["family_fail_rate"], R=d23["R"]),
               seal_gate=gate, seeds=SEEDS, pool=list(POOL), PGEN=PGEN, BPOW={str(k): v for k, v in BPOW.items()},
               primary=[n for n in names if n.startswith("ratio_")],
               secondary=[n for n in names if not n.startswith("ratio_")])
    dump(res, out)
    print("gate:", gate)
    print("UNPOWERED:", [n for n, p in zip(names, powered) if not p] or "none")
    print(f"{'stat':>10} {'power':>6} " + " ".join(f"p={p:>2}" for p in resol))
    for j, nm in enumerate(names):
        print(f"{nm:>10} {gate_power[j]['power']:6.3f} " + " ".join(f"{resol[p][j]:5.2f}" for p in resol))
    return 0 if gate["ok"] else 2


# ---------------- read ----------------
def verdict(vec, ref, P, idx):
    out = [abs(vec[j] - ref[j]) <= P["tol"][j] for j in idx]
    return "PASS" if all(out) else "FAIL"


def family_idx(P, fam):
    return [j for j, n in enumerate(P["names"]) if n in P[fam] and P["powered"][j]]


def series_planted(L, tabs, pool, rng):
    shifts = [int(rng.integers(q)) for q, _ in tabs]
    return delta(0, L, tabs, shifts) * pool[rng.integers(len(pool), size=L)] - 1.0


def read(dev_npz, fresh_npz, params_json, hs_json, hind_glob, out):
    t0 = time.time()
    P = json.load(open(params_json))
    lags, names = P["lags"], P["names"]
    t1, t2 = P["T1"], P["T2"]
    res = dict(params_sha256=sha(params_json), dev_sha256=sha(dev_npz), fresh_sha256=sha(fresh_npz),
               hsample_sha256=sha(hs_json))
    fresh = np.load(fresh_npz)
    tf = fresh["t"]
    cov = bool(int(tf[0]) == t1 + 1 and int(tf[-1]) == t2 and np.all(np.diff(tf) == 1) and np.all(fresh["g_all"] > 0))
    hj = sorted(hind_glob.split(","))
    hc = hcompare(fresh, hs_json, hj)
    inputs_ok = res["dev_sha256"] == P["dev_sha256"] and cov and hc["all_match"]
    res.update(inputs=dict(dev_hash_ok=res["dev_sha256"] == P["dev_sha256"], coverage_ok=cov, class_number_check=hc,
                           ok=inputs_ok))
    if not cov:                                   # no statistics without the full contiguous fresh range
        res["verdict"] = dict(primary="VOID (inputs)", secondary="VOID (inputs)", overall="VOID (inputs)")
        dump(res, out)
        open(out + ".timing", "w").write(f"wall_s {time.time() - t0:.1f}\n")
        print("verdict:", res["verdict"])
        return 0
    a = alpha_tilde(dev_npz, fresh_npz)
    lo, hi = t1 + 1, t2 - RMAX
    st = window_stats(a, lo, hi, lags)
    vec = stat_vector(st, lags)
    pr, pi = family_idx(P, "primary"), family_idx(P, "secondary")
    within = [abs(vec[j] - P["pred"][j]) <= P["tol"][j] for j in range(len(names))]
    res["stats"] = {n: dict(value=vec[j], pred=P["pred"][j], diff=vec[j] - P["pred"][j], tol=P["tol"][j],
                            within=within[j], powered=P["powered"][j]) for j, n in enumerate(names)}
    res["block_jackknife_se"] = dict(gamma={str(r): st["se_gamma"][r] for r in lags},
                                     ratio={str(r): st["se_ratio"][r] for r in lags if r}, n_blocks=st["n_blocks"])
    # witnesses (fresh-window length, same statistic code)
    L = st["N"] + RMAX
    seg = a[lo - 3:lo - 3 + L]
    rs = np.random.default_rng(P["seeds"]["shuffle"])
    w_sh = stat_vector(window_stats(np.concatenate([np.zeros(lo - 3), rs.permutation(seg)]), lo, hi, lags), lags)
    tabs = tables(P["PGEN"])
    pool_src = P.get("pool_dev_npz", dev_npz)                 # the dry run's split 'dev' part lacks the pool range
    res["pool_source_sha256_ok"] = sha(pool_src) == DEV_SHA
    resp, alp = pools(pool_src)
    rn = np.random.default_rng(P["seeds"]["null"])
    w_nu = stat_vector(window_stats(np.concatenate([np.zeros(lo - 3), alp[rn.integers(len(alp), size=L)] - 1.0]),
                                    lo, hi, lags), lags)
    rp = np.random.default_rng(P["seeds"]["planted"])
    xp = series_planted(L, tabs, resp, rp)
    ex = planted_exact(lags, tabs, float(np.mean(resp ** 2)))
    pex = stat_vector(dict(gamma=ex, ratio={r: ex[r] / ex[0] for r in lags if r}), lags)
    w_pl = stat_vector(window_stats(np.concatenate([np.zeros(lo - 3), xp]), lo, hi, lags), lags)
    wit = dict(shuffled_t=dict(primary=verdict(w_sh, P["pred"], P, pr), secondary=verdict(w_sh, P["pred"], P, pi),
                               must="FAIL"),
               matched_marginal_null=dict(primary=verdict(w_nu, P["pred"], P, pr),
                                          secondary=verdict(w_nu, P["pred"], P, pi), must="FAIL"),
               planted=dict(primary=verdict(w_pl, pex, P, pr), secondary=verdict(w_pl, pex, P, pi), must="PASS"))
    wit_ok = (wit["shuffled_t"]["primary"] == "FAIL" and wit["matched_marginal_null"]["primary"] == "FAIL"
              and wit["planted"]["primary"] == "PASS" and wit["planted"]["secondary"] == "PASS")
    res["witnesses"] = dict(wit, ok=wit_ok)
    prim = verdict(vec, P["pred"], P, pr)
    sec = verdict(vec, P["pred"], P, pi)
    inputs_ok = inputs_ok and res["pool_source_sha256_ok"]
    res["inputs"]["ok"] = inputs_ok
    if not inputs_ok:
        v = "VOID (inputs)"
    elif not wit_ok:
        v = "VOID (witness)"
    else:
        v = prim
    res["verdict"] = dict(primary=prim if inputs_ok and wit_ok else v, secondary=sec if inputs_ok and wit_ok else v,
                          overall=v, unpowered=[n for j, n in enumerate(names) if not P["powered"][j]])
    dump(res, out)
    open(out + ".timing", "w").write(f"wall_s {time.time() - t0:.1f}\n")
    print("verdict:", res["verdict"])
    return 0


def dryparams(params_json, dev_npz, t1, t2, odir):
    """§9.F dry run: split the dev data at t1 into a 'dev' part (t ≤ t1) and a 'fresh' part (t1, t2]; params copy with
    T1, T2 and the split's hashes. Verdicts from a dry run mean nothing; it exercises the read and its cmp."""
    import os
    P = json.load(open(params_json))
    d = np.load(dev_npz)
    t = d["t"]
    m = t <= t1
    rows = d["rows"]
    np.savez(os.path.join(odir, "dry_dev.npz"), t=t[m], g_all=d["g_all"][m], g_wide=d["g_wide"][m],
             rows=rows[rows[:, 0] <= t1])
    mf = (t > t1) & (t <= t2)
    np.savez(os.path.join(odir, "dry_fresh.npz"), t=t[mf], g_all=d["g_all"][mf], g_wide=d["g_wide"][mf],
             rows=rows[(rows[:, 0] > t1) & (rows[:, 0] <= t2)])
    P.update(T1=t1, T2=t2, dev_sha256=sha(os.path.join(odir, "dry_dev.npz")), pool_dev_npz=dev_npz, dry_run=True)
    dump(P, os.path.join(odir, "dry_params.json"))
    return 0


if __name__ == "__main__":
    m, A = sys.argv[1], sys.argv[2:]
    if m == "tables-check":
        sys.exit(tables_check(A[0]))
    if m == "hsample":
        sys.exit(hsample(int(A[0]), int(A[1]), int(float(A[2])), int(float(A[3])), A[4]))
    if m == "cfcheck":
        sys.exit(cfcheck(A[0]))
    if m == "hind":
        sys.exit(hind(A[0], int(A[1]), int(A[2]), A[3]))
    if m == "calibrate":
        sys.exit(calibrate(*A[:5]))
    if m == "finalize":
        sys.exit(finalize(*A[:5]))
    if m == "read":
        sys.exit(read(*A[:6]))
    if m == "dryparams":
        sys.exit(dryparams(A[0], A[1], int(float(A[2])), int(float(A[3])), A[4]))
    sys.exit(f"unknown mode {m}")

"""GEO1 bridge-kit A2: evaluate the derived window-average error E_rms(L) (GEO1_BRIDGE_A2_DERIVATION.md §2–§3).

E²(L) = c₀ [Σ_{2≤q≤Q} W(q) T(q, L) + (M_total − Σ_{q≤Q} W(q) φ(q))/L]. Here:
  - W(q) = Π_{p^k∥q} w(p^k), with w the flat per-frequency weight at exact denominator p^k;
  - T(q, L) = Σ_{d | rad q} μ(d) F(q/d, L) and F(e, L) = (e/L²)(s(m+1)² + (e−s)m²), L = me + s;
  - c₀ = 1 for α̃ and (1 + γ(r))² for y_r = α̃(n) α̃(n+r).
Weights:
  - p ≤ 13: exact DFTs of the counted SL(2, ℤ/p^B) trace densities (BPOW), grouped by exact denominator;
  - 13 < p ≤ PEX: Parseval masses of the closed-form δ_p (α) or g_p = δ_p(n) δ_p(n+r) (y), divided by p − 1;
  - p > PEX: Var(δ_p) (α) or 2·Var(δ_p) (y; p ∤ r) over p − 1.

  python geo1_peter_spec.py planted OUT_JSON           check 1: flat approximation on the planted witness (§3)
  python geo1_peter_spec.py predict PRED_JSON OUT_JSON  the zero-parameter prediction for α̃ and the 23 lags
  python geo1_peter_spec.py compare DEV_NPZ FRESH_NPZ PREDICT_JSON RATE_JSON OUT_JSON   descriptive, read ranges only

Check 1 criterion (fixed in the derivation, before running): within 25% at every L in [10³, 10⁵], slope within 0.05.
Check 2: M_total for α̃ equals Peter's γ(0) to 1%; for the planted series, its exact second moment to 1%.
"""
import json
import math
import sys

import numpy as np
from numba import njit

import geo1_peter_seal as S
from geo1_peter import primes_upto, trace_density

BPOW = S.BPOW
PEX = 10 ** 5
Q = 2 * 10 ** 7
FRESH = (10 ** 6 + 1, 3 * 10 ** 6 - 120)
SPAN = FRESH[1] - FRESH[0] + 1
LS = np.unique(np.round(np.logspace(2, math.log10(SPAN / 8), 25)).astype(np.int64))
SEED = 20261109


@njit(cache=False)
def spf_sieve(n):
    s = np.zeros(n + 1, np.int32)
    for i in range(2, n + 1):
        if s[i] == 0:
            for j in range(i, n + 1, i):
                if s[j] == 0:
                    s[j] = i
    return s


@njit(cache=False)
def spec_sum(Qmax, spf, wp, small, Ls):
    nL = Ls.shape[0]
    acc = np.zeros(nL)
    massq = 0.0
    ps = np.zeros(16, np.int64)
    for q in range(2, Qmax + 1):
        x = q
        W = 1.0
        phi = 1.0
        w = 0
        while x > 1:
            p = spf[x]
            k = 0
            while x % p == 0:
                x //= p
                k += 1
            if p <= 13:
                if k >= small.shape[1]:
                    W = 0.0
                    break
                W *= small[p, k]
            else:
                if k > 1:
                    W = 0.0
                    break
                W *= wp[p]
            phi *= (p - 1.0) * p ** (k - 1.0)
            ps[w] = p
            w += 1
            if W == 0.0:
                break
        if W == 0.0:
            continue
        massq += W * phi
        for li in range(nL):
            L = Ls[li]
            T = 0.0
            for mask in range(1 << w):
                d = 1
                sg = 1.0
                for j in range(w):
                    if mask >> j & 1:
                        d *= ps[j]
                        sg = -sg
                e = q // d
                m = L // e
                s = L - m * e
                T += sg * e * (s * (m + 1.0) ** 2 + (e - s) * float(m) * m) / (float(L) * L)
            acc[li] += W * T
    return acc, massq


@njit(cache=False)
def parseval_masses(primes, r, mode):
    """mass_p = mean(g²)/mean(g)² − 1 over n mod p; g = δ_p (mode 0) or δ_p(n) δ_p(n + r) (mode 1)."""
    out = np.zeros(primes.shape[0])
    for i in range(primes.shape[0]):
        p = primes[i]
        sq = np.zeros(p, np.int8)
        for x in range(1, p):
            sq[(x * x) % p] = 1
        dl = np.empty(p)
        for n in range(p):
            v = (n * n - 4) % p
            chi = 0 if v == 0 else (1 if sq[v] == 1 else -1)
            dl[n] = (p * p + p * chi) / (p * p - 1.0)
        m1 = 0.0
        m2 = 0.0
        for n in range(p):
            g = dl[n] if mode == 0 else dl[n] * dl[(n + r) % p]
            m1 += g
            m2 += g * g
        m1 /= p
        m2 /= p
        out[i] = m2 / (m1 * m1) - 1.0
    return out


def small_weights(tabs_small, r, mode):
    """small[p, k] = flat weight at exact denominator p^k (k ≥ 1) from the DFT of the table (δ or g); small[p, 0] = 1."""
    small = np.zeros((14, 8))
    small[:, 0] = 1.0
    for q, tab in tabs_small:
        p = min(pp for pp in (2, 3, 5, 7, 11, 13) if q % pp == 0)
        B = round(math.log(q, p))
        g = tab if mode == 0 else tab * np.roll(tab, -(r % q))
        G = np.fft.fft(g) / q
        pw = np.abs(G / G[0]) ** 2
        a = np.arange(q)
        v = np.zeros(q, int)
        aa = a.copy()
        for _ in range(B):
            nz = (aa % p == 0) & (aa > 0)
            v[nz] += 1
            aa = np.where(nz, aa // p, aa)
        v[0] = B
        for k in range(1, B + 1):
            sel = (B - v) == k
            small[p, k] = pw[sel].sum() / (p ** k - p ** (k - 1))
    return small


def var_delta(p):
    return (p * p / (p * p - 1.0) ** 2) * ((p - 2.0) / p - 1.0 / p ** 2)


def weights(r, mode, pmax_planted=None):
    """(small, wp, M_total) for α̃ (mode 0) or y_r (mode 1); pmax_planted truncates to the planted primes."""
    tabs = S.tables(997 if pmax_planted else S.PGEN)
    small = small_weights([t for t in tabs if t[0] in [p ** BPOW[p] for p in BPOW]], r, mode)
    wp = np.zeros(Q + 1)
    top = pmax_planted or PEX
    pr = primes_upto(top).astype(np.int64)
    pr = pr[pr > 13]
    ms = parseval_masses(pr, r, mode)
    wp[pr] = ms / (pr - 1.0)
    logM = sum(math.log1p(sum(small[p, k] * (p ** k - p ** (k - 1)) for k in range(1, 8))) for p in BPOW)
    logM += float(np.sum(np.log1p(ms)))
    if not pmax_planted:
        big = primes_upto(Q).astype(np.int64)
        big = big[big > PEX]
        c = 1.0 if mode == 0 else 2.0
        mb = c * np.array([var_delta(float(p)) for p in big])
        wp[big] = mb / (big - 1.0)
        logM += float(np.sum(np.log1p(mb)))
        logM += c / (Q * math.log(Q))                      # primes above Q (Σ c/p²)
    return small, wp, math.expm1(logM)


_SPF = None


def predict_curve(r, mode, c0, pmax_planted=None):
    global _SPF
    if _SPF is None:
        _SPF = spf_sieve(Q)
    small, wp, Mt = weights(r, mode, pmax_planted)
    acc, mq = spec_sum(Q, _SPF, wp, small, LS)
    E2 = c0 * (acc + (Mt - mq) / LS)
    return np.sqrt(E2), Mt, mq


def slope(L, E, lo=1e3, hi=1e5):
    m = (L >= lo) & (L <= hi)
    return float(np.polyfit(np.log(L[m]), np.log(E[m]), 1)[0])


def measure(a, rs, lo=FRESH[0]):
    """E_rms(L) on disjoint windows tiling [lo, lo + SPAN): for α̃ itself (key 'alpha') and y_r against mean_ref."""
    out = {}
    series = {"alpha": a}
    for r in rs:
        series[r] = a[: len(a) - r] * a[r:]
    for key, y in series.items():
        cs = np.concatenate([[0.0], np.cumsum(y)])
        ref = 0.0 if key == "alpha" else None
        rows = []
        for L in LS:
            k = SPAN // L
            st = lo - 3 + np.arange(k) * L
            out_w = (cs[st + L] - cs[st]) / L
            rows.append(out_w)
        out[key] = rows
    return out


def planted(out):
    tabs = S.tables(997)
    rng = np.random.default_rng(SEED)
    shifts = [int(rng.integers(q)) for q, _ in tabs]
    n_all = 3 * 10 ** 6 - 2
    a = S.delta(0, n_all, tabs, shifts) - 1.0
    rs = [0, 1, 2, 4]
    ex = S.planted_exact(rs, tabs, 1.0)
    meas = measure(a, rs)
    res = dict(L=LS.tolist(), rows={})
    ok_all = True
    for key in ["alpha"] + rs:
        mean_ref = 0.0 if key == "alpha" else ex[key]
        E_meas = np.array([math.sqrt(np.mean((w - mean_ref) ** 2)) for w in meas[key]])
        mode = 0 if key == "alpha" else 1
        c0 = 1.0 if key == "alpha" else (1 + ex[key]) ** 2
        E_pred, Mt, mq = predict_curve(0 if key == "alpha" else key, mode, c0, pmax_planted=997)
        exact_m2 = float(np.prod([np.mean(t ** 2) for _, t in tabs]) - 1) if key == "alpha" else \
            float(np.prod([np.mean((t * np.roll(t, -(key % q))) ** 2) / np.mean(t * np.roll(t, -(key % q))) ** 2
                           for q, t in tabs]) - 1)
        m = (LS >= 1e3) & (LS <= 1e5)
        ratio = E_meas / E_pred
        s_meas, s_pred = slope(LS, E_meas), slope(LS, E_pred)
        ok = bool(np.all(np.abs(ratio[m] - 1) <= 0.25) and abs(s_meas - s_pred) <= 0.05
                  and abs(Mt / exact_m2 - 1) <= 0.01)
        ok_all &= ok
        res["rows"][str(key)] = dict(E_meas=E_meas.tolist(), E_pred=E_pred.tolist(), ratio=ratio.tolist(),
                                     slope_meas=s_meas, slope_pred=s_pred, M_total=Mt, M_exact=exact_m2,
                                     mass_q_le_Q=mq, max_abs_ratio_dev_1e3_1e5=float(np.max(np.abs(ratio[m] - 1))),
                                     ok=ok)
        print(key, f"slope meas {s_meas:.3f} pred {s_pred:.3f}; ratio meas/pred on [1e3,1e5] "
                   f"{ratio[m].min():.3f}–{ratio[m].max():.3f}; M_total {Mt:.5f} exact {exact_m2:.5f}; ok {ok}",
              flush=True)
    res["CHECK1_PASS"] = bool(ok_all)
    json.dump(res, open(out, "w"), indent=1)
    print("CHECK1_PASS", ok_all)
    return 0


def predict(pred_json, out):
    pred = json.load(open(pred_json))
    lags = S.lags_of(pred)
    g = {r: pred["gamma"][str(r)]["gamma"] for r in lags}
    res = dict(L=LS.tolist(), Q=Q, PEX=PEX, rows={})
    E, Mt, mq = predict_curve(0, 0, 1.0)
    res["rows"]["alpha"] = dict(E_pred=E.tolist(), slope_pred=slope(LS, E), M_total=Mt, gamma0_peter=g[0],
                                check2_ok=bool(abs(Mt / g[0] - 1) <= 0.01))
    print("alpha", f"slope {slope(LS, E):.3f}; M_total {Mt:.5f} vs Peter gamma(0) {g[0]:.5f}", flush=True)
    for r in lags:
        E, Mt, mq = predict_curve(r, 1, (1 + g[r]) ** 2)
        res["rows"][str(r)] = dict(E_pred=E.tolist(), slope_pred=slope(LS, E), M_total_normalised=Mt)
        print(r, f"slope {slope(LS, E):.3f}; E(1e4) {np.interp(1e4, LS, E):.3e}", flush=True)
    json.dump(res, open(out, "w"), indent=1)
    return 0


def compare(dev_npz, fresh_npz, predict_json, rate_json, out):
    P = json.load(open(predict_json))
    R = json.load(open(rate_json))
    a = S.alpha_tilde(dev_npz, fresh_npz)
    meas = measure(a, [])
    res = dict(L=LS.tolist(), rows={})
    E_meas = np.array([math.sqrt(np.mean(w ** 2)) for w in meas["alpha"]])
    E_pred = np.array(P["rows"]["alpha"]["E_pred"])
    res["rows"]["alpha"] = dict(E_meas=E_meas.tolist(), ratio=(E_meas / E_pred).tolist(),
                                slope_meas=slope(LS, E_meas), slope_pred=slope(LS, E_pred))
    for r in R["lags"]:
        row = R["data"]["disjoint_fresh"][str(r)]
        assert row["L"] == LS.tolist()
        Em = np.array(row["rms_gamma"])
        Ep = np.array(P["rows"][str(r)]["E_pred"])
        res["rows"][str(r)] = dict(ratio=(Em / Ep).tolist(), slope_meas=slope(LS, Em), slope_pred=slope(LS, Ep))
    m = (LS >= 1e3) & (LS <= 1e5)
    for k, v in res["rows"].items():
        rr = np.array(v["ratio"])[m]
        print(k, f"slope meas {v['slope_meas']:.3f} pred {v['slope_pred']:.3f}; meas/pred on [1e3,1e5] "
                 f"{rr.min():.2f}–{rr.max():.2f} (median {np.median(rr):.2f})")
    json.dump(res, open(out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    m, A = sys.argv[1], sys.argv[2:]
    if m == "planted":
        sys.exit(planted(A[0]))
    if m == "predict":
        sys.exit(predict(A[0], A[1]))
    sys.exit(compare(*A[:5]))

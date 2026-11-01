"""GEO1 bridge-kit A1 (Will, 2026-10-31; descriptive, not a seal; the Peter seal is already read): how the residual
γ̂ − γ_Peter shrinks with the averaging length.

  python geo1_peter_rate.py DEV_NPZ FRESH_NPZ PRED_JSON OUT_DIR

Data: α̃(n) for 3 ≤ n ≤ 3·10⁶ (the development range and the read fresh range); the 23 sealed lags; prediction PRED.json.
For each lag, the raw γ(r) and the ratio γ(r)/γ(0), two schemes.

(1) Nested windows [3, N] (Peter's definition).
  - 48 log-spaced N from 10³ to 3·10⁶ − 120.
  - E(N) = |residual| pointwise, plus the running maximum of |residual| over N′ ≥ N (an envelope, less sensitive to
    sign changes).
  - Caveat, stated before running: a cumulative average from n = 3 carries its start-up transient as O(1/N) whatever
    the averaging class, so a −1 slope here is not evidence by itself.

(2) Disjoint windows of length L, tiling a range far from the origin: the fresh range [10⁶ + 1, 3·10⁶ − 120], and as a
    check the development range [10⁵, 10⁶ − 120].
  - 25 log-spaced L from 10² up to the range / 8 (at least 8 windows).
  - E_rms(L) = the RMS over windows of the residual, plus the maximum over windows.
  - This is the scheme that bears on the block jackknife.

Fits (OLS, on log E):
  (a) log E = c − a·log L;
  (b) with a log correction, log E = c − a·log L + b·log log L, with b free;
  - fit ranges: L or N in [10³, the upper end of each scheme];
  - reported per lag, plus the median and range over lags.

Witnesses (the same code, at the fresh-range length):
  - i.i.d. α drawn from the development α pool, where the expected exponent is ½;
  - the planted local-density product δ_P(n + s) of the Peter seal (p ≤ 997, random shifts, no noise), which is
    limit-periodic, so the expected exponent is about 1.
  - Each witness's residual is taken against its own exact γ.
  - If the fitter cannot separate them, the A1 fits mean nothing.

Implication for the jackknife (descriptive): with E_rms(L) measured, the block jackknife (blocks of 10⁴, N_F windows)
estimates SE ≈ E_rms(10⁴)·√(10⁴/N_F). Its ratio to the actual E_rms(N_F) is reported, together with the ratio expected
if E ∝ L^(−a).
"""
import json
import math
import os
import sys

import numpy as np

import geo1_peter_seal as S

LAGS_FROM_PRED = True
T1, T2, RMAX = 10 ** 6, 3 * 10 ** 6, 120
DEV_RANGE = (10 ** 5, 10 ** 6 - RMAX)
FRESH_RANGE = (T1 + 1, T2 - RMAX)
SEED = 20261108


def products(a, lags, nmax):
    """y_r[i] = α̃(n) α̃(n + r) for n = 3 … nmax (index i = n − 3)."""
    m = nmax - 3 + 1
    return {r: a[:m] * a[r:r + m] for r in lags}


def ols(x, y):
    X = np.vstack([np.ones_like(x), x]).T
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ c
    se = math.sqrt(float(e @ e) / max(len(x) - 2, 1) * np.linalg.inv(X.T @ X)[1, 1])
    return float(c[1]), se


def fit_logcorr(x, y):
    X = np.vstack([np.ones_like(x), x, np.log(x)]).T            # x = log L
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(c[1]), float(c[2])


def fits(Ls, E, lo=1e3):
    Ls, E = np.asarray(Ls, float), np.asarray(E, float)
    ok = (Ls >= lo) & (E > 0) & np.isfinite(E)
    x, y = np.log(Ls[ok]), np.log(E[ok])
    s, se = ols(x, y)
    a2, b2 = fit_logcorr(x, y)
    return dict(slope=s, slope_se=se, logcorr_slope=a2, logcorr_b=b2, n=int(ok.sum()))


def nested(Y, pv, Ns):
    """Residuals of the nested averages; Y = {r: y_r}, pv = {r: (γ_pred, ratio_pred)}."""
    out = {}
    cs = {r: np.cumsum(y) for r, y in Y.items()}
    for r in Y:
        g = np.array([cs[r][N - 3] / (N - 2) for N in Ns])
        g0 = np.array([cs[0][N - 3] / (N - 2) for N in Ns])
        res_g = np.abs(g - pv[r][0])
        res = dict(gamma=res_g)
        if r:
            res["ratio"] = np.abs(g / g0 - pv[r][1])
        out[r] = res
    return out


def envelope(E):
    return np.array([np.max(E[i:]) for i in range(len(E))])


def disjoint(Y, pv, rng_, Ls):
    lo, hi = rng_
    out = {}
    cs = {r: np.concatenate([[0.0], np.cumsum(y)]) for r, y in Y.items()}
    for r in Y:
        rows = dict(gamma=[], ratio=[], gamma_max=[], ratio_max=[], n_windows=[])
        for L in Ls:
            k = (hi - lo + 1) // L
            st = lo - 3 + np.arange(k) * L
            g = (cs[r][st + L] - cs[r][st]) / L
            g0 = (cs[0][st + L] - cs[0][st]) / L
            d = g - pv[r][0]
            rows["gamma"].append(float(np.sqrt(np.mean(d * d))))
            rows["gamma_max"].append(float(np.max(np.abs(d))))
            rows["n_windows"].append(int(k))
            if r:
                dr = g / g0 - pv[r][1]
                rows["ratio"].append(float(np.sqrt(np.mean(dr * dr))))
                rows["ratio_max"].append(float(np.max(np.abs(dr))))
        out[r] = rows
    return out


def analyse(a, lags, pv, label):
    Y = products(a, lags, T2 - RMAX)
    Ns = np.unique(np.round(np.logspace(3, math.log10(T2 - RMAX), 48)).astype(int))
    ne = nested(Y, pv, Ns)
    res = dict(label=label, nested={}, disjoint_fresh={}, disjoint_dev={})
    for r in lags:
        e = ne[r]
        res["nested"][str(r)] = {k: dict(pointwise=fits(Ns, v), envelope=fits(Ns, envelope(v)))
                                 for k, v in e.items()}
    for key, rg in (("disjoint_fresh", FRESH_RANGE), ("disjoint_dev", DEV_RANGE)):
        span = rg[1] - rg[0] + 1
        Ls = np.unique(np.round(np.logspace(2, math.log10(span / 8), 25)).astype(int))
        dj = disjoint(Y, pv, rg, Ls)
        for r in lags:
            row = dict(L=Ls.tolist(), n_windows=dj[r]["n_windows"], rms_gamma=dj[r]["gamma"],
                       max_gamma=dj[r]["gamma_max"], fit_rms_gamma=fits(Ls, dj[r]["gamma"]),
                       fit_max_gamma=fits(Ls, dj[r]["gamma_max"]))
            if r:
                row.update(rms_ratio=dj[r]["ratio"], max_ratio=dj[r]["ratio_max"],
                           fit_rms_ratio=fits(Ls, dj[r]["ratio"]), fit_max_ratio=fits(Ls, dj[r]["ratio_max"]))
            res[key][str(r)] = row
    del Y
    return res


def summary(res, lags):
    def med(vals):
        v = np.array(vals)
        return dict(median=float(np.median(v)), min=float(v.min()), max=float(v.max()))
    nz = [r for r in lags if r]
    s = {}
    for k in ("gamma", "ratio"):
        rs = lags if k == "gamma" else nz
        s[f"nested_pointwise_{k}"] = med([res["nested"][str(r)][k]["pointwise"]["slope"] for r in rs])
        s[f"nested_envelope_{k}"] = med([res["nested"][str(r)][k]["envelope"]["slope"] for r in rs])
        for sch in ("disjoint_fresh", "disjoint_dev"):
            s[f"{sch}_rms_{k}"] = med([res[sch][str(r)][f"fit_rms_{k}"]["slope"] for r in rs])
            s[f"{sch}_rms_{k}_logcorr_slope"] = med([res[sch][str(r)][f"fit_rms_{k}"]["logcorr_slope"] for r in rs])
            s[f"{sch}_rms_{k}_logcorr_b"] = med([res[sch][str(r)][f"fit_rms_{k}"]["logcorr_b"] for r in rs])
            s[f"{sch}_max_{k}"] = med([res[sch][str(r)][f"fit_max_{k}"]["slope"] for r in rs])
    return s


def main(dev_npz, fresh_npz, pred_json, odir):
    os.makedirs(odir, exist_ok=True)
    pred = json.load(open(pred_json))
    lags = S.lags_of(pred)
    g = {r: pred["gamma"][str(r)]["gamma"] for r in lags}
    pv = {r: (g[r], g[r] / g[0]) for r in lags}
    a = S.alpha_tilde(dev_npz, fresh_npz)
    assert len(a) == T2 - 2
    out = dict(lags=lags, data=analyse(a, lags, pv, "GEO1 alpha (dev + fresh)"))
    out["data_summary"] = summary(out["data"], lags)
    # witnesses: r ∈ {0, 1, 2, 4}
    wl = [0, 1, 2, 4]
    rng = np.random.default_rng(SEED)
    resp, alp = S.pools(dev_npz)
    n_all = len(a)
    a_iid = alp[rng.integers(len(alp), size=n_all)] - 1.0
    pv_iid = {r: (float(np.mean((alp - 1) ** 2)) if r == 0 else 0.0, 0.0) for r in wl}
    tabs = S.tables()
    shifts = [int(rng.integers(q)) for q, _ in tabs]
    a_per = S.delta(0, n_all, tabs, shifts) - 1.0
    ex = S.planted_exact(wl, tabs, 1.0)
    pv_per = {r: (ex[r], ex[r] / ex[0]) for r in wl}
    w = {}
    for name, aw, pw in (("iid", a_iid, pv_iid), ("periodic_planted", a_per, pv_per)):
        rw = analyse(aw, wl, pw, name)
        w[name] = dict(summary=summary(rw, wl), detail=rw)
    out["witnesses"] = w
    json.dump(out, open(os.path.join(odir, "RATE.json"), "w"), indent=1, sort_keys=True)
    # jackknife implication (fresh range, raw gamma, per lag)
    jk = []
    for r in lags:
        row = out["data"]["disjoint_fresh"][str(r)]
        L, E = np.array(row["L"]), np.array(row["rms_gamma"])
        e4 = float(np.exp(np.interp(math.log(1e4), np.log(L), np.log(E))))
        NF = FRESH_RANGE[1] - FRESH_RANGE[0] + 1
        se_jk = e4 * math.sqrt(1e4 / NF)
        a_fit = -row["fit_rms_gamma"]["slope"]
        e_full = e4 * (NF / 1e4) ** (-a_fit)
        jk.append(dict(r=r, E_rms_1e4=e4, jackknife_SE_implied=se_jk, E_full_extrapolated=e_full,
                       ratio=se_jk / e_full))
    json.dump(jk, open(os.path.join(odir, "JK_IMPLICATION.json"), "w"), indent=1)
    print(json.dumps(out["data_summary"], indent=1))
    for name in w:
        print(name, json.dumps({k: round(v["median"], 3) for k, v in w[name]["summary"].items()
                                if "rms" in k and "logcorr" not in k}))
    print("jackknife SE / extrapolated true error (median over lags):", np.median([x["ratio"] for x in jk]))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:5]))

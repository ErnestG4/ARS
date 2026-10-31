"""GEO1 Step 2 additions (Will, 2026-10-30; descriptive, no verdicts).

  python geo1_step2b.py WORDS_NPZ PARI_NPZ OUT_DIR

1. PGT remainder rate: OLS slope of log|Π(T)/Li(x) − 1| on log x, x = ε(T)², T ∈ [10³, 10⁶] (80 log-spaced T), against
   −1/2 (square-root remainder: relative x^{−1/2} up to logs) and the proven bound's relative exponent (x^{θ}/Li(x)).
   Also the slope of the running maximum of |·| over the remaining range (an envelope less sensitive to sign changes).
2. Gauss–Kuzmin convergence: TV from Gauss–Kuzmin per band of t (4 bands per decade, t ≥ 100) and the OLS slope of
   log TV on log t; each band's TV against the multinomial sampling floor (median TV of 200 seeded multinomial draws
   with the band's digit count from the Gauss–Kuzmin law).
3. Length-spectrum figure redrawn at uniform density in ℓ (40,000 ℓ values drawn uniformly, mapped to the nearest
   trace), so the t = 3,000 sampling switch of the first version is not read as structure.
"""
import json
import math
import os
import sys

import mpmath as mp
import numpy as np

from geo1 import K, g_prim_from_all
from geo1_analyze import gk, tv
from geo1_step2 import SERIES, INK, INK2, SURF, ell, style

SEED = 20261031


def ols(x, y):
    X = np.vstack([np.ones_like(x), x]).T
    c, res, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ c
    se = math.sqrt(float(e @ e) / (len(x) - 2) * np.linalg.inv(X.T @ X)[1, 1])
    return float(c[1]), se


def main(wnpz, pnpz, odir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "figure.facecolor": SURF, "savefig.facecolor": SURF, "text.color": INK})
    w, p = np.load(wnpz), np.load(pnpz)
    t = p["t"].astype(np.int64)
    gp = g_prim_from_all(t, p["g_all"])
    cum = np.cumsum(gp.astype(float))
    res = {}
    # 1
    mp.mp.dps = 30
    Ts = np.unique(np.round(np.logspace(3, 6, 80)).astype(int))
    lx, lr = [], []
    for T in Ts:
        e = (T + math.sqrt(T * T - 4)) / 2
        x = e * e
        r = float(cum[T - 3]) / float(mp.li(x) - mp.li(2)) - 1
        lx.append(math.log(x))
        lr.append(math.log(abs(r)) if r != 0 else float("nan"))
    lx, lr = np.array(lx), np.array(lr)
    ok = np.isfinite(lr)
    s, se = ols(lx[ok], lr[ok])
    env = np.array([np.nanmax(lr[i:]) for i in range(len(lr))])
    s_env, se_env = ols(lx, env)
    res["PGT"] = dict(T_range=[1000, 1000000], n_T=int(ok.sum()), slope_abs_rel=s, SE=se, slope_running_max=s_env,
                      SE_running_max=se_env, sqrt_remainder_reference=-0.5,
                      note="relative remainder x^(theta-1) up to log factors; theta = 1/2 conjectured")
    # 2
    tw = w["t"]
    H = w["hist"][:, 1:].astype(float)
    pg = gk(K)
    rng = np.random.default_rng(SEED)
    bands = []
    for j in range(8, 18):                       # 10^(j/4): 100 … 3·10⁴
        a, b = 10 ** (j / 4), 10 ** ((j + 1) / 4)
        m = (tw >= a) & (tw < b)
        if m.sum() == 0:
            continue
        hh = H[m].sum(0)
        n = int(hh.sum())
        floor = float(np.median([tv(rng.multinomial(n, pg / pg.sum()) / n, pg) for _ in range(200)]))
        bands.append(dict(t_lo=a, t_hi=min(b, float(tw[-1])), t_geomean=float(np.exp(np.log(tw[m]).mean())), digits=n,
                          TV=tv(hh / n, pg), multinomial_floor_median=floor))
    lt = np.log([x["t_geomean"] for x in bands])
    lv = np.log([x["TV"] for x in bands])
    s2, se2 = ols(lt, lv)
    res["GK"] = dict(bands=bands, slope_logTV_logt=s2, SE=se2)
    # 3
    L = ell(t)
    lu = rng.uniform(L[0], L[-1], 40000)
    tt = np.unique(np.clip(np.round(2 * np.cosh(lu / 2)).astype(np.int64), 3, int(t[-1])))
    fig, ax = plt.subplots(figsize=(8.5, 4.6), constrained_layout=True)
    style(ax)
    ax.scatter(L[tt - 3], gp[tt - 3], s=1.2, color=SERIES[0], alpha=0.35, lw=0, rasterized=True,
               label=f"g_prim(t), {len(tt):,} traces at uniform density in ℓ")
    xx = np.linspace(L[0], L[-1], 400)
    ax.plot(xx, 2 * np.exp(xx / 2) / xx, "--", color=INK, lw=1.2, label="2e^{ℓ/2}/ℓ (Bolte 1993; Bogomolny 2003)")
    ax.set_yscale("log")
    ax.set_xlabel("length ℓ = 2 arccosh(t/2)")
    ax.set_ylabel("multiplicity: primitive oriented classes of trace t")
    ax.set_title("Length spectrum of the modular surface, t ≤ 10⁶ (uniform sampling in ℓ)", color=INK)
    ax.legend(fontsize=8, frameon=False, labelcolor=INK2, loc="upper left")
    fig.savefig(os.path.join(odir, "geo1_length_spectrum.png"), dpi=150, metadata={"Software": None})
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    style(axs[0])
    axs[0].plot(np.exp(lx), np.exp(lr), "o", color=SERIES[1], ms=3, label="|Π(T)/Li(x) − 1|")
    axs[0].plot(np.exp(lx), np.exp(env), "-", color=SERIES[1], lw=1.5, label="running maximum (envelope)")
    x0 = np.exp(lx)
    for slope, ls, lab in ((-0.5, "--", "slope −1/2 (square-root remainder)"),):
        axs[0].plot(x0, np.exp(env[0]) * (x0 / x0[0]) ** slope, ls, color=INK, lw=1.2, label=lab)
    axs[0].set_xscale("log")
    axs[0].set_yscale("log")
    axs[0].set_xlabel("x = ε(T)²")
    axs[0].set_ylabel("relative difference")
    axs[0].legend(fontsize=8, frameon=False, labelcolor=INK2)
    axs[0].set_title(f"PGT remainder: slope {s:.3f} ± {se:.3f} (envelope {s_env:.3f})", color=INK)
    style(axs[1])
    axs[1].plot([x["t_geomean"] for x in bands], [x["TV"] for x in bands], "-o", color=SERIES[0], lw=2, ms=4,
                label="TV from Gauss–Kuzmin")
    axs[1].plot([x["t_geomean"] for x in bands], [x["multinomial_floor_median"] for x in bands], ":", color=SERIES[1],
                lw=1.5, label="multinomial sampling floor (same digit count)")
    axs[1].set_xscale("log")
    axs[1].set_yscale("log")
    axs[1].set_xlabel("trace band (geometric mean t)")
    axs[1].set_ylabel("total variation")
    axs[1].legend(fontsize=8, frameon=False, labelcolor=INK2)
    axs[1].set_title(f"Digit law by band: slope {s2:.2f} ± {se2:.2f}", color=INK)
    fig.savefig(os.path.join(odir, "geo1_rates.png"), dpi=150, metadata={"Software": None})
    json.dump(res, open(os.path.join(odir, "STEP2B.json"), "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "bands"} for k, v in res.items()}, indent=1))
    for b in bands:
        print(f"{b['t_geomean']:9.0f} digits {b['digits']:>11,} TV {b['TV']:.2e} floor {b['multinomial_floor_median']:.2e}")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))

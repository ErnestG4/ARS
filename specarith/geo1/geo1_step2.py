"""GEO1 Step 2 (descriptive; no verdicts): the modular surface's length spectrum from the Step 1 data (hashed; gates
passed, GEO1_STEP1_RESULTS.md).

  python geo1_step2.py WORDS_NPZ PARI_NPZ OUT_DIR

Not computed on purpose: multiplicity fluctuations and correlations (Peter 2002's γ(r)), the candidate sealable
prediction of GEO1_STEP0.md, so that no fluctuation statistic of t ≤ 10⁶ is seen before a seal is designed.

Outputs (OUT_DIR): STEP2.json (summary numbers), length_spectrum.csv.gz (t, ℓ, g_all, g_prim for t ≤ 10⁶) and four
figures:
  geo1_length_spectrum.png    g_prim against ℓ = 2 arccosh(t/2), bin means, and the mean law 2e^{ℓ/2}/ℓ
  geo1_multiplicity_growth.png bin means of g_prim(t)/(t/log t), and Π(T)/Li(ε(T)²) − 1 (the prime geodesic theorem)
  geo1_partial_quotients.png   pooled digit frequencies over primitive classes against Gauss–Kuzmin; TV by t band
  geo1_mean_period.png         mean even period length against Pollicott's (6 log 2/π²)·ℓ, cumulative and per band
"""
import gzip
import json
import math
import os
import sys

import mpmath as mp
import numpy as np

from geo1 import K, g_prim_from_all
from geo1_analyze import gk, tv

SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"
POLL = 6 * math.log(2) / math.pi ** 2


def ell(t):
    t = np.asarray(t, float)
    return 2 * np.arccosh(t / 2)


def style(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(True, color=GRID, lw=0.6)
    ax.xaxis.label.set_color(INK2)
    ax.yaxis.label.set_color(INK2)


def bands(t, lo=3, per_decade=10):
    j0 = math.floor(per_decade * math.log10(max(lo, 3)))
    j1 = math.ceil(per_decade * math.log10(t[-1] + 1))
    out = []
    for j in range(j0, j1):
        a, b = 10 ** (j / per_decade), 10 ** ((j + 1) / per_decade)
        m = (t >= a) & (t < b)
        if m.sum() >= 1:
            out.append(m)
    return out


def main(wnpz, pnpz, odir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "figure.facecolor": SURF, "savefig.facecolor": SURF, "text.color": INK})
    os.makedirs(odir, exist_ok=True)
    w, p = np.load(wnpz), np.load(pnpz)
    t = p["t"].astype(np.int64)
    gall = p["g_all"].astype(np.int64)
    gp = g_prim_from_all(t, gall)
    L = ell(t)
    res = {}

    # table
    with gzip.open(os.path.join(odir, "length_spectrum.csv.gz"), "wt") as f:
        f.write("t,ell,g_all,g_prim\n")
        for a, b, c, d in zip(t, L, gall, gp):
            f.write(f"{a},{b:.12f},{c},{d}\n")

    # 1. length spectrum
    fig, ax = plt.subplots(figsize=(8.5, 4.6), constrained_layout=True)
    style(ax)
    rng = np.random.default_rng(20261030)
    sub = np.sort(np.concatenate([np.arange(min(3000, len(t))), rng.choice(np.arange(3000, len(t)), 60000, replace=False)]))
    ax.scatter(L[sub], gp[sub], s=0.5, color=SERIES[0], alpha=0.12, lw=0, rasterized=True, label="g_prim(t), each trace (subsample)")
    bx = [float(L[m].mean()) for m in bands(t)]
    by = [float(gp[m].mean()) for m in bands(t)]
    ax.plot(bx, by, "-o", color=SERIES[0], lw=2, ms=3, label="band mean (10 bands per decade of t)")
    xx = np.linspace(L[0], L[-1], 400)
    ax.plot(xx, 2 * np.exp(xx / 2) / xx, "--", color=INK, lw=1.2, label="2e^{ℓ/2}/ℓ (Bolte 1993; Bogomolny 2003)")
    ax.set_yscale("log")
    ax.set_xlabel("length ℓ = 2 arccosh(t/2)")
    ax.set_ylabel("multiplicity: primitive oriented classes of trace t")
    ax.set_title("Length spectrum of the modular surface, t ≤ 10⁶ (each trace is one length)", color=INK)
    ax.legend(fontsize=8, frameon=False, labelcolor=INK2, loc="upper left")
    fig.savefig(os.path.join(odir, "geo1_length_spectrum.png"), dpi=150, metadata={"Software": None})

    # 2. multiplicity growth
    ratio = gp / (t / np.log(t))
    bt = [float(np.exp(np.log(t[m]).mean())) for m in bands(t, lo=10)]
    br = [float(ratio[m].mean()) for m in bands(t, lo=10)]
    cum = np.cumsum(gp.astype(float))
    Ts = np.unique(np.round(np.logspace(1, 6, 60)).astype(int))
    mp.mp.dps = 30
    rel = []
    for T in Ts:
        x = (T + math.sqrt(T * T - 4)) / 2
        rel.append(float(cum[T - 3]) / float(mp.li(x * x) - mp.li(2)) - 1)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    style(axs[0])
    axs[0].plot(bt, br, "-o", color=SERIES[0], lw=2, ms=3, label="band mean of g_prim(t) / (t / log t)")
    axs[0].axhline(1, color=INK, lw=1.2, ls="--", label="mean law t / log t (= d/dt Li(t²))")
    axs[0].set_xscale("log")
    axs[0].set_xlabel("trace t")
    axs[0].set_ylabel("multiplicity / mean law")
    axs[0].legend(fontsize=8, frameon=False, labelcolor=INK2)
    axs[0].set_title("Mean multiplicity against t / log t", color=INK)
    style(axs[1])
    rr = np.array(rel)
    axs[1].plot(Ts, np.abs(rr), "-o", color=SERIES[1], lw=2, ms=3, label="|Π(T) / Li(ε(T)²) − 1|")
    for T, r in zip(Ts, rr):
        if r < 0:
            axs[1].plot([T], [abs(r)], "o", ms=5, mfc=SURF, mec=SERIES[1])
    axs[1].plot(Ts, Ts.astype(float) ** -0.6 * np.log(Ts.astype(float) ** 2), ":", color=INK, lw=1.2,
                label="G3 tolerance x^(−3/5) ln x²")
    axs[1].set_xscale("log")
    axs[1].set_yscale("log")
    axs[1].set_xlabel("T (largest trace)")
    axs[1].set_ylabel("relative difference (open markers: negative)")
    axs[1].legend(fontsize=8, frameon=False, labelcolor=INK2)
    axs[1].set_title("Prime geodesic theorem: primitive count against Li(x²)", color=INK)
    fig.savefig(os.path.join(odir, "geo1_multiplicity_growth.png"), dpi=150, metadata={"Software": None})
    res["mean_multiplicity_ratio_by_decade"] = {f"1e{d}-1e{d+1}": float(ratio[(t >= 10 ** d) & (t < 10 ** (d + 1))].mean())
                                                for d in range(1, 6)}
    res["Pi_over_Li_minus_1"] = {str(int(T)): r for T, r in zip(Ts, rel) if T in (100, 1000, 10000, 100000, 1000000)}

    # 3. partial quotients (words, t ≤ 3e4)
    tw = w["t"]
    H = w["hist"][:, 1:].astype(float)
    p_gk = gk(K)
    f_all = H.sum(0) / H.sum()
    bnds = [(10 ** a, 10 ** b) for a, b in ((0.5, 1.5), (1.5, 2.5), (2.5, 3.5), (3.5, 4.0), (4.0, 4.48))]
    tvb = []
    for a, b in bnds:
        m = (tw >= a) & (tw < b)
        hh = H[m].sum(0)
        tvb.append((float(np.exp(np.log(tw[m]).mean())), tv(hh / hh.sum(), p_gk), int(hh.sum())))
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
    style(axs[0])
    k = np.arange(1, K + 1)
    axs[0].plot(k, p_gk[:K], "-", color=INK, lw=1.2, label="Gauss–Kuzmin −log₂(1 − 1/(k+1)²)")
    axs[0].plot(k, f_all[:K], "o", color=SERIES[0], ms=3.5, label=f"pooled digits, primitive classes, t ≤ 3·10⁴ ({int(H.sum()):,})")
    axs[0].plot(k[:30], 2.0 ** -k[:30], ":", color=SERIES[1], lw=1.5, label="geometric 2^−k (random words, the witness)")
    axs[0].set_xscale("log")
    axs[0].set_yscale("log")
    axs[0].set_xlabel("partial quotient k")
    axs[0].set_ylabel("frequency")
    axs[0].legend(fontsize=8, frameon=False, labelcolor=INK2)
    axs[0].set_title("Partial quotients over closed geodesics (Pollicott 1986)", color=INK)
    style(axs[1])
    axs[1].plot([x[0] for x in tvb], [x[1] for x in tvb], "-o", color=SERIES[0], lw=2, ms=4)
    axs[1].set_xscale("log")
    axs[1].set_yscale("log")
    axs[1].set_xlabel("trace band (geometric mean t)")
    axs[1].set_ylabel("total variation from Gauss–Kuzmin")
    axs[1].set_title("Digit law by trace band", color=INK)
    fig.savefig(os.path.join(odir, "geo1_partial_quotients.png"), dpi=150, metadata={"Software": None})
    res["GK_TV_by_band"] = [dict(t_geomean=a, TV=b, digits=c) for a, b, c in tvb]
    res["GK_pooled_TV"] = tv(f_all, p_gk)

    # 4. mean even period
    sr, npm = w["sruns"].astype(float), w["nprim"].astype(float)
    Lw = ell(tw)
    cumr = np.cumsum(sr) / np.cumsum(npm)
    fig, ax = plt.subplots(figsize=(8.5, 4.4), constrained_layout=True)
    style(ax)
    ax.plot(Lw, cumr, "-", color=SERIES[0], lw=2, label="cumulative: Σ period / Σ classes over t ≤ T, at ℓ(T)")
    bm = bands(tw, lo=3)
    ax.plot([float(Lw[m].mean()) for m in bm], [float(sr[m].sum() / npm[m].sum()) for m in bm], "o", color=SERIES[1],
            ms=3.5, label="per band of t")
    ax.plot(Lw, POLL * Lw, "--", color=INK, lw=1.2, label="(6 log 2/π²)·ℓ (Pollicott 1986 Prop. 3(i))")
    ax.set_xlabel("length ℓ")
    ax.set_ylabel("mean even period length (runs of the R/L word)")
    ax.legend(fontsize=8, frameon=False, labelcolor=INK2)
    ax.set_title("Mean continued-fraction period over primitive closed geodesics, t ≤ 3·10⁴", color=INK)
    fig.savefig(os.path.join(odir, "geo1_mean_period.png"), dpi=150, metadata={"Software": None})
    res["mean_period_cumulative_at_T"] = {str(T): dict(ell=float(ell(T)), mean=float(cumr[T - 3]),
                                                       pollicott=float(POLL * ell(T)), ratio=float(cumr[T - 3] / (POLL * ell(T))))
                                          for T in (100, 1000, 10000, 30000)}
    json.dump(res, open(os.path.join(odir, "STEP2.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(res, indent=1)[:2500])
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))

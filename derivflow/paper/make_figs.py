#!/usr/bin/env python3
"""Paper figures. Palette: dataviz reference instance, slots 1-2 (validated: CVD 24.5, NV 33.6).
iid = blue #2a78d6, GUE = orange #eb6834; n encoded as lightness steps within hue (sequential =
magnitude). Thin marks, direct labels, recessive grid, no top/right spines. Static print form.
"""
import json, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb

sys.path.insert(0, "derivflow")

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED = "#0b0b0b", "#52514e"
GRID = "#e6e5e2"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.grid": True,
    "figure.dpi": 150, "savefig.bbox": "tight"})


def shade(hex_color, f):
    """f in [0,1]: 0 = light tint, 1 = full hue (light -> dark = increasing n)."""
    r, g, b = to_rgb(hex_color)
    return tuple(1 - (1 - c) * (0.35 + 0.65 * f) for c in (r, g, b))


dense = json.load(open("derivflow/science_dense_grid.json"))
s3 = json.load(open("derivflow/step3_scale_law.json"))
seal = json.load(open("derivflow/seals/SCALE_LAW_SEAL.json"))
step2 = json.load(open("derivflow/step2_env_decomposition.json"))

NS = [1024, 2048, 4096, 16384]
HUE = {"iid": BLUE, "gue": ORANGE}
LABEL = {"iid": "iid Uniform[−1,1]", "gue": "GUE eigenvalues"}


def curve(sc, n):
    src = dense["data"][sc].get(str(n)) if n != 16384 else s3["data"].get(sc)
    if src is None:
        return None
    ks = sorted(int(k) for k in src)
    return (np.array(ks, float),
            np.array([src[str(k)]["mean"] for k in ks]),
            np.array([src[str(k)]["sigma_mean"] for k in ks]))


def f3(k, la, tau, beta):
    return 10 ** la * np.exp(-((k / tau) ** beta))


# ---------- Figure 1: relaxation curves ----------
fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=True)
for ax, sc in zip(axes, ["iid", "gue"]):
    for i, n in enumerate(NS):
        c = curve(sc, n)
        if c is None:
            continue
        ks, m, sm = c
        col = shade(HUE[sc], i / (len(NS) - 1))
        ax.fill_between(ks, m - sm, m + sm, color=col, alpha=0.25, lw=0)
        ax.plot(ks, m, "-", color=col, lw=1.4)
    ax.annotate("n = 1024, 2048, 4096, 16384\n(curves coincide — the scale result)",
                (0.55, 0.8), xycoords="axes fraction", fontsize=7, color=MUTED)
    p = dense["fits"]["primary"][sc]["4096"]
    lad = p["ladder"][p["selected"]]["params"]
    kk = np.geomspace(1, 24, 80)
    ax.plot(kk, f3(kk, *lad), "--", color=INK, lw=0.9)
    ax.set_ylim(3e-5, 1.2)
    ax.annotate("F3 fit (n=4096)", (kk[8], f3(kk[8], *lad)), textcoords="offset points",
                xytext=(5, 5), fontsize=7, color=INK)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("derivative count k")
    ax.set_title(LABEL[sc], fontsize=9, color=HUE[sc], loc="left")
    ax.axhline(1e-2, color=MUTED, lw=0.6, ls=":")
axes[0].set_ylabel(r"$1-\langle \tilde r\rangle$")
axes[0].annotate(r"$k^*$ level $10^{-2}$", (1.1, 1.15e-2), fontsize=7, color=MUTED)
fig.suptitle("Stretched-exponential crystallization under repeated differentiation",
             fontsize=10, x=0.02, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig("derivflow/paper/figs/fig1_relaxation.png")
fig.savefig("derivflow/paper/figs/fig1_relaxation.pdf")
plt.close(fig)

# ---------- Figure 2: k*(n) with sealed predictions ----------
fig, ax = plt.subplots(figsize=(4.6, 3.2))
for sc in ["iid", "gue"]:
    ns_a = [1024, 2048, 4096]
    ka = [dense["kstar_table"][sc][str(n)]["kstar"] for n in ns_a]
    ea = [dense["kstar_table"][sc][str(n)]["err"] for n in ns_a]
    adj = s3["adjudication"][sc]
    ns_all = ns_a + [16384]
    ka_all = ka + [adj["kstar_16384"]]
    ea_all = ea + [adj["sigma_m"]]
    col = HUE[sc]
    pred = seal["predictions_rederived_from_repo"]["iid" if sc == "iid" else "gue_if_time"]
    s_eff = adj["sigma_eff"]
    ax.fill_between([12000, 22000], pred["H_flat"] - 3 * s_eff, pred["H_flat"] + 3 * s_eff,
                    color=col, alpha=0.13, lw=0)
    ax.hlines(pred["H_flat"], 12000, 22000, color=col, lw=0.8, ls="-")
    ax.hlines(pred["H_log"], 12000, 22000, color=col, lw=0.8, ls="--")
    ax.errorbar(ns_all, ka_all, yerr=ea_all, fmt="o", color=col, ms=4,
                elinewidth=1.1, capsize=2, lw=0)
    lab = ("SCALE-FLAT (sealed)" if sc == "iid" else "SCALE-FLAT (confirmatory)")
    ax.annotate(f"{LABEL[sc]}\n{lab}", (ns_all[-1], ka_all[-1]),
                textcoords="offset points", xytext=(-4, 10 if sc == "iid" else 12),
                fontsize=7, color=col, ha="right")
    ax.annotate("H_log", (21000, pred["H_log"]), textcoords="offset points",
                xytext=(2, -2), fontsize=6.5, color=col)
ax.set_xscale("log")
ax.set_xticks([1024, 2048, 4096, 16384], ["1024", "2048", "4096", "16384"])
ax.set_ylim(5.5, 13.2)
ax.set_xlabel("degree n"); ax.set_ylabel(r"$k^*(n)$")
ax.set_title("Crystallization scale: flat across 16× in n\n(bands: sealed flat prediction ±3σ_eff; dashed: proportional-log)",
             fontsize=8.5, loc="left")
fig.savefig("derivflow/paper/figs/fig2_kstar.png")
fig.savefig("derivflow/paper/figs/fig2_kstar.pdf")
plt.close(fig)

# ---------- Figure 3: environment-conditioned decomposition ----------
have_2b = False
try:
    step2b = json.load(open("derivflow/step2b_isoconfig.json"))
    have_2b = True
except FileNotFoundError:
    pass
ncols = 2 if have_2b else 1
fig, axes = plt.subplots(1, ncols, figsize=(3.6 * ncols, 3.1), sharey=True, squeeze=False)
panels = [("Step 2: seed conditioning (k=0)", step2)] + \
         ([("Step 2b: mid-flow conditioning (k=2)", step2b)] if have_2b else [])
for ax, (title, d) in zip(axes[0], panels):
    ks = sorted(int(k) for k in d["per_bin"])
    for b in range(5):
        m = np.array([d["per_bin"][str(k)][b]["mean"] for k in ks])
        col = shade(BLUE, b / 4)
        ax.plot(ks, m, "-", color=col, lw=1.2)
        if b == 0:
            ax.annotate("Q1 (largest gaps): F2, slow", (ks[0], m[0]),
                        textcoords="offset points", xytext=(6, 6), fontsize=7, color=col)
        if b == 4:
            others = "/".join(sorted(set(d["selected_forms"][1:])))
            ax.annotate(f"Q2–Q5: {others}", (ks[0], m[0]), textcoords="offset points",
                        xytext=(6, -13), fontsize=7, color=col)
    ma = np.array([d["aggregate"][str(k)]["mean"] for k in ks])
    ax.plot(ks, ma, "--", color=INK, lw=1.0)
    ax.annotate("aggregate", (ks[1], ma[1]), textcoords="offset points",
                xytext=(4, 4), fontsize=7, color=INK)
    forms = d["selected_forms"]
    ax.set_title(f"{title}\nforms: {'/'.join(forms)} → {d['ladder_outcome']}",
                 fontsize=8, loc="left")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("k")
axes[0][0].set_ylabel(r"$1-\langle \tilde r\rangle$ (per environment quintile)")
fig.suptitle("Does environment conditioning decompose the stretch?", fontsize=10,
             x=0.02, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig("derivflow/paper/figs/fig3_bins.png")
fig.savefig("derivflow/paper/figs/fig3_bins.pdf")
plt.close(fig)

# ---------- Figure 4: two-scale schematic (real mini-flow) ----------
from track0_harness import diff_step
rng = np.random.default_rng(7)
n = 1024
seed = np.sort(rng.uniform(-1, 1, n))
r = seed.copy()
snap = {0: seed.copy()}
for k in range(1, 11):
    r = diff_step(r)
    snap[k] = r.copy()
fig, (top, bot) = plt.subplots(2, 1, figsize=(6.2, 3.4),
                               gridspec_kw={"height_ratios": [1.2, 1]})
for k, f, lab in [(0, 0.35, "k = 0 (seed)"), (10, 1.0, "k = 10")]:
    top.hist(snap[k], bins=48, density=True, histtype="step",
             color=shade(BLUE, f), lw=1.4)
top.annotate("global density: k=0 and k=10 indistinguishable\n(ANP: frozen through k = o(n/log n))",
             (0.02, 0.72), xycoords="axes fraction", fontsize=8, color=INK)
top.set_ylabel("density"); top.set_xlim(-1.05, 1.05)
top.set_yticks([])
top.legend(["k = 0 (seed)", "k = 10"], fontsize=7, frameon=False, loc="lower center")
w = 0.05
for y, k, f in [(1, 0, 0.35), (0, 10, 1.0)]:
    pts = snap[k][(snap[k] > -w) & (snap[k] < w)]
    bot.eventplot(pts, lineoffsets=y, linelengths=0.6, colors=[shade(BLUE, f)], lw=1.2)
bot.set_yticks([1, 0], ["k = 0", "k = 10"])
bot.set_xlim(-w, w)
bot.set_xlabel("central window (zoom ×20)")
bot.annotate("local spacings: rough → crystalline by k ≈ 10", (0.02, 0.45),
             xycoords="axes fraction", fontsize=8, color=INK)
bot.grid(False)
fig.suptitle("Two scales: frozen global measure, crystallizing local spacings (n = 1024, one seed)",
             fontsize=10, x=0.02, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.94))
fig.savefig("derivflow/paper/figs/fig4_twoscale.png")
fig.savefig("derivflow/paper/figs/fig4_twoscale.pdf")
plt.close(fig)
print("figures written", "with 2b panel" if have_2b else "(2b panel pending)")

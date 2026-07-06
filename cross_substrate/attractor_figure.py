"""
cross_substrate/attractor_figure.py — summary figure for the EC(MEC)-vs-CA3 attractor arc.

4 panels: (A) per-cell ks_gue by region, both substrates (shows the substrate offset = bridge fail +
within-substrate region structure); (B) burst_frac by region (MEC<<CA1 large effect); (C) population
corr-eig Brody q by region (pillar-1 holds, all GUE-like); (D) the CA1/DG bridge: 000638 vs Allen ks_gue.
Read-only on banked coordinates. Out: figures/P_ec_ca3_attractor.png.
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
FIGS = os.path.join(_HERE, "figures")
os.makedirs(FIGS, exist_ok=True)


def load(name):
    p = os.path.join(COORD, name)
    if not os.path.exists(p):
        return []
    return [json.loads(line) for line in open(p) if line.strip()]


dr = load("dr-port-cell.jsonl"); al = load("allen-hpf-cell.jsonl")
drp = load("dr-port-pop.jsonl"); alp = load("allen-hpf-pop.jsonl")

COL = {"MEC": "#d62728", "CA3": "#1f77b4", "CA1": "#2ca02c", "DG": "#ff7f0e"}


def vals(cells, region, axkey, ct="excitatory"):
    out = []
    for c in cells:
        if c.get("region") != region or (ct and c.get("cell_type") != ct):
            continue
        v = c.get("axes_computed", {}).get(axkey)
        if v is not None and np.isfinite(v):
            out.append(v)
    return np.array(out)


def burst(cells, region, ct="excitatory"):
    out = []
    for c in cells:
        if c.get("region") != region or (ct and c.get("cell_type") != ct):
            continue
        v = (c.get("burst") or {}).get("burst_frac")
        if v is not None and np.isfinite(v):
            out.append(v)
    return np.array(out)


fig, axes = plt.subplots(2, 2, figsize=(13, 9))

# A: ks_gue distributions by region, both substrates
ax = axes[0, 0]
groups = [("MEC", dr), ("CA1(000638)", dr, "CA1"), ("DG(000638)", dr, "DG"),
          ("CA3", al), ("CA1(Allen)", al, "CA1"), ("DG(Allen)", al, "DG")]
data, labels, colors = [], [], []
for g in groups:
    reg = g[2] if len(g) == 3 else g[0]
    src = g[1]
    v = vals(src, reg, "I.5q_ks_gue_med")
    data.append(v); labels.append(f"{g[0]}\nn={v.size}")
    colors.append(COL.get(reg, "#999"))
bp = ax.boxplot(data, labels=labels, patch_artist=True, showfliers=False)
for patch, c in zip(bp["boxes"], colors):
    patch.set_facecolor(c); patch.set_alpha(0.55)
ax.axvspan(0.5, 3.5, color="#d62728", alpha=0.04)
ax.axvspan(3.5, 6.5, color="#1f77b4", alpha=0.04)
ax.set_ylabel("per-cell ks_gue (I.5q)  — lower = more GUE-like")
ax.set_title("(A) Per-cell NNS by region (excitatory)\n"
             "left=000638 (track task ~0.5Hz)  right=Allen (spontaneous ~3Hz)", fontsize=10)
ax.tick_params(axis="x", labelsize=8)

# B: burst_frac by region
ax = axes[0, 1]
data, labels, colors = [], [], []
for g in groups:
    reg = g[2] if len(g) == 3 else g[0]
    v = burst(g[1], reg)
    data.append(v); labels.append(f"{g[0]}\nn={v.size}"); colors.append(COL.get(reg, "#999"))
bp = ax.boxplot(data, labels=labels, patch_artist=True, showfliers=False)
for patch, c in zip(bp["boxes"], colors):
    patch.set_facecolor(c); patch.set_alpha(0.55)
ax.set_ylabel("burst fraction  P(ISI < 10 ms)")
ax.set_title("(B) Burst structure: MEC ≪ CA1 (δ=−0.55 LARGE, within-000638)", fontsize=10)
ax.tick_params(axis="x", labelsize=8)

# C: population corr-eig Brody q by region/substrate (pillar-1)
ax = axes[1, 0]
def popq(pop, region, agg="corr-eig"):
    out = []
    for r in pop:
        if r.get("region") == region and r.get("aggregation") == agg and r.get("cell_type") == "all":
            v = r["axes_computed"].get("I.8_brody_q")
            if v is not None and np.isfinite(v):
                out.append(v)
    return np.array(out)
labels = ["MEC", "CA1\n(000638)", "DG\n(000638)", "CA3", "CA1\n(Allen)", "DG\n(Allen)"]
srcreg = [(drp, "MEC"), (drp, "CA1"), (drp, "DG"), (alp, "CA3"), (alp, "CA1"), (alp, "DG")]
for i, (src, reg) in enumerate(srcreg):
    q = popq(src, reg)
    if q.size:
        ax.scatter([i] * q.size, q, c=COL.get(reg, "#999"), s=40, alpha=0.7, edgecolor="k", linewidth=0.3)
        ax.scatter([i], [np.median(q)], c="k", marker="_", s=400)
ax.axhline(1.0, ls="--", c="green", alpha=0.6, label="GUE (q=1)")
ax.axhline(0.0, ls="--", c="gray", alpha=0.6, label="Poisson (q=0)")
ax.set_xticks(range(6)); ax.set_xticklabels(labels, fontsize=8)
ax.set_ylabel("population corr-eig Brody q")
ax.set_title("(C) Pillar-1: corr-eig stays GUE-like in ALL regions/substrates", fontsize=10)
ax.legend(fontsize=8)

# D: the bridge — CA1/DG ks_gue 000638 vs Allen
ax = axes[1, 1]
pos = 0; ticks, tlab = [], []
for reg in ("CA1", "DG"):
    d_dr = vals(dr, reg, "I.5q_ks_gue_med"); d_al = vals(al, reg, "I.5q_ks_gue_med")
    ax.boxplot([d_dr, d_al], positions=[pos, pos + 1], widths=0.7, patch_artist=True, showfliers=False)
    ticks += [pos, pos + 1]; tlab += [f"{reg}\n000638", f"{reg}\nAllen"]
    pos += 3
ax.set_xticks(ticks); ax.set_xticklabels(tlab, fontsize=8)
ax.set_ylabel("ks_gue (I.5q)")
ax.set_title("(D) BRIDGE FAILS: shared CA1/DG differ across substrates\n"
             "(δ≈−0.9 LARGE) ⇒ cross-substrate MEC-vs-CA3 confounded", fontsize=10)

fig.suptitle("EC(MEC continuous-attractor) vs CA3(discrete-attractor) — ARS fingerprint comparison "
             "(progress log, NOT validated)", fontsize=12, y=0.995)
fig.tight_layout(rect=[0, 0, 1, 0.97])
out = os.path.join(FIGS, "P_ec_ca3_attractor.png")
fig.savefig(out, dpi=130)
print("wrote", out)

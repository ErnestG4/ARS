"""Panel C figure — V7 triangle re-drawn three ways + Stern-Brocot turtle-path/tessellation.
Reads panel_C.json (clean Floquet C). Top row: C vs {Lagrange, K, mean-digit}, each with Spearman rho.
Bottom: RL turtle-paths (R^a1 L^a2 R^a3...) per member, colored by C — the geometric 'tessellation' face
(balanced RLRL=gold vs clustered RRLL=silver), showing how CF-word geometry relates to the dimension.
"""
import json, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

rows = [r for r in json.load(open("panel_C.json")) if r["C"] is not None]
C = np.array([r["C"] for r in rows])
cmin, cmax = C.min(), C.max()
norm = plt.Normalize(cmin, cmax)
cmap = plt.cm.viridis

fig = plt.figure(figsize=(15, 9))
gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.1], hspace=0.32, wspace=0.28)

AXES = [("lagrange", "Lagrange constant Λ  (approximability)"),
        ("K", "K = liminf geomean of partial quotients  (Panel A / Liu–Wen)"),
        ("meandig", "mean partial quotient  (digit content / Thread-1)")]
for j, (key, lbl) in enumerate(AXES):
    ax = fig.add_subplot(gs[0, j])
    x = np.array([r[key] for r in rows])
    sr = spearmanr(x, C)
    order = np.argsort(x)
    ax.plot(x[order], C[order], "-", color="0.75", lw=1, zorder=1)   # the 'polyline'
    ax.scatter(x, C, c=C, cmap=cmap, norm=norm, s=80, edgecolor="k", zorder=3)
    for r in rows:
        ax.annotate(r["name"], (r[key], r["C"]), fontsize=6, xytext=(4, 3),
                    textcoords="offset points")
    ax.set_xlabel(lbl, fontsize=9)
    if j == 0:
        ax.set_ylabel("DEGT dimension constant C", fontsize=10)
    ax.set_title(f"C vs {key}\nSpearman ρ = {sr.correlation:+.3f}  (p={sr.pvalue:.3f})",
                 fontsize=10, fontweight="bold")
    ax.grid(alpha=0.2)

# ---- bottom: RL turtle-path tessellation ----
def rl_word(period, n=26):
    s, mv = "", "R"
    for d in period * 20:
        s += mv * d; mv = "L" if mv == "R" else "R"
        if len(s) >= n:
            break
    return s[:n]

def turtle(word, step=1.0, dtheta=math.radians(28)):
    x, y, th = [0.0], [0.0], 0.0
    for ch in word:
        th += dtheta if ch == "L" else -dtheta
        x.append(x[-1] + step * math.cos(th)); y.append(y[-1] + step * math.sin(th))
    return np.array(x), np.array(y)

axb = fig.add_subplot(gs[1, :])
# vertical offset each path into its own lane (sorted by C) so labels don't collide
order = sorted(range(len(rows)), key=lambda i: rows[i]["C"])
for lane, i in enumerate(order):
    r = rows[i]
    wx, wy = turtle(rl_word(r["period"]))
    off = lane * 3.0
    col = cmap(norm(r["C"]))
    axb.plot(wx, wy + off, "-", color=col, lw=2.0, alpha=0.95)
    axb.plot(wx[0], wy[0] + off, "s", color=col, ms=5, markeredgecolor="k", mew=0.4)
    axb.annotate(f"{r['name']}  C={r['C']:.3f}", (wx[0], wy[0] + off), fontsize=6.5,
                 ha="right", va="center", xytext=(-6, 0), textcoords="offset points")
axb.set_aspect("equal")
axb.set_yticks([])
axb.set_title("Stern-Brocot RL turtle-paths (R^a₁ L^a₂ R^a₃ …), colored by DEGT dimension C  "
              "— balanced RLRL=gold, clustered runs=silver/bronze", fontsize=10, fontweight="bold")
axb.grid(alpha=0.15)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
fig.colorbar(sm, ax=axb, label="C", fraction=0.025, pad=0.01)

fig.suptitle("Panel C — V7 C-polyline re-drawn three ways + turtle-path tessellation "
             "(which functional controls the dimension?)", fontsize=12, fontweight="bold")
fig.savefig("panel_C_threeways.png", dpi=130, bbox_inches="tight")
print("wrote panel_C_threeways.png")

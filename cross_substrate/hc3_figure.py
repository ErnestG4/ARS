"""
cross_substrate/hc3_figure.py — the de-confounded EC-vs-CA3 result on CRCNS hc-3.
(A) ks_gue vs burst_frac: EC + CA3 fall on ONE curve (ρ≈0.8) -> the region difference is position along the
    intrinsic burst axis, not a separate NNS class. (B) per-region ks_gue & burst_frac boxes (EC<CA3 both).
(C) pillar-2 spatial_info↔ks_gue in EC + CA3. Out: figures/P_hc3_ec_ca3_deconfound.png.
"""
import json, os
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__)); COORD = os.path.join(_HERE, "coordinates")
load = lambda n: [json.loads(l) for l in open(os.path.join(COORD, n)) if l.strip()]
cells = load("hc3-port-cell.jsonl"); pf = load("hc3-placefields.jsonl")
COL = {"EC": "#d62728", "CA3": "#1f77b4", "DG": "#ff7f0e"}

def cv(region, axkey="I.5q_ks_gue_med", ct="excitatory"):
    return np.array([c["axes_computed"][axkey] for c in cells if c["region"] == region
                     and c["cell_type"] == ct and c["axes_computed"].get(axkey) is not None], float)
def bv(region, key="burst_frac", ct="excitatory"):
    return np.array([(c["burst"] or {}).get(key) for c in cells if c["region"] == region
                     and c["cell_type"] == ct and (c["burst"] or {}).get(key) is not None], float)

fig, ax = plt.subplots(1, 3, figsize=(16, 5))

# A: ks_gue vs burst, EC+CA3 one curve
for r in ("EC", "CA3"):
    bvals, kvals = [], []
    for c in cells:
        if c["region"] == r and c["cell_type"] == "excitatory":
            b = (c["burst"] or {}).get("burst_frac"); k = c["axes_computed"].get("I.5q_ks_gue_med")
            if b is not None and k is not None and np.isfinite(b) and np.isfinite(k):
                bvals.append(b); kvals.append(k)
    ax[0].scatter(bvals, kvals, s=28, c=COL[r], alpha=0.6, edgecolor="k", linewidth=0.2,
                  label=f"{r} (n={len(bvals)})")
# pooled trend
allb = [(c["burst"] or {}).get("burst_frac") for c in cells if c["region"] in ("EC", "CA3") and c["cell_type"] == "excitatory"]
allk = [c["axes_computed"].get("I.5q_ks_gue_med") for c in cells if c["region"] in ("EC", "CA3") and c["cell_type"] == "excitatory"]
m = [(b, k) for b, k in zip(allb, allk) if b is not None and k is not None and np.isfinite(b) and np.isfinite(k)]
bb = np.array([x[0] for x in m]); kk = np.array([x[1] for x in m])
rho, p = stats.spearmanr(bb, kk)
xs = np.linspace(bb.min(), bb.max(), 50); cf = np.polyfit(bb, kk, 1)
ax[0].plot(xs, np.polyval(cf, xs), "k--", lw=1.5, alpha=0.7)
ax[0].set_xlabel("burst fraction P(ISI<10ms)"); ax[0].set_ylabel("ks_gue (I.5q)")
ax[0].set_title(f"(A) EC+CA3 on ONE burst axis: ρ={rho:+.2f}\nregion gap = position along burst, not separate NNS class")
ax[0].legend()

# B: boxes
data = [cv("EC"), cv("CA3"), bv("EC"), bv("CA3")]
labs = ["EC\nks_gue", "CA3\nks_gue", "EC\nburst", "CA3\nburst"]
bp = ax[1].boxplot(data, tick_labels=labs, patch_artist=True, showfliers=False)
for patch, c in zip(bp["boxes"], [COL["EC"], COL["CA3"], COL["EC"], COL["CA3"]]):
    patch.set_facecolor(c); patch.set_alpha(0.55)
ax[1].set_title("(B) EC < CA3 in both ks_gue (more GUE) and burst\n(rate-matched δ: ks_gue −0.53, burst −0.82, LARGE)")

# C: pillar-2 spatial_info vs ks_gue
for r in ("EC", "CA3"):
    rr = [x for x in pf if x["region"] == r and x.get("cell_type", x.get("celltype")) == "excitatory"]
    x = np.array([z["spatial_info_bits_per_spike"] for z in rr], float)
    y = np.array([z["ks_gue_med"] for z in rr], float)
    mm = np.isfinite(x) & np.isfinite(y); x, y = x[mm], y[mm]
    ax[2].scatter(x, y, s=26, c=COL[r], alpha=0.6, edgecolor="k", linewidth=0.2, label=f"{r} n={x.size}")
    if x.size >= 8:
        rh, pp = stats.spearmanr(x, y)
        cf2 = np.polyfit(x, y, 1); xs2 = np.linspace(x.min(), x.max(), 30)
        ax[2].plot(xs2, np.polyval(cf2, xs2), c=COL[r], lw=1.5)
ax[2].set_xscale("symlog", linthresh=0.05)
ax[2].set_xlabel("Skaggs spatial info (bits/spike)"); ax[2].set_ylabel("ks_gue (I.5q)")
ax[2].set_title("(C) Pillar-2: spatial-quality↔class holds in EC & CA3\n(EC ρ=+0.39, CA3 ρ=+0.25)")
ax[2].legend()

fig.suptitle("De-confounded EC-vs-CA3 within ONE dataset (CRCNS hc-3): large raw difference = intrinsic burst "
             "axis, not attractor topology (progress log, NOT validated)", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(os.path.join(_HERE, "figures", "P_hc3_ec_ca3_deconfound.png"), dpi=130)
print("wrote figures/P_hc3_ec_ca3_deconfound.png")

"""Arm A (bulk self-similarity) -- PREDICTION FIGURE, drawn 2026-10-01 BEFORE any arm-A code or data (Will: 'draw the
decision regions for each panel before writing any code'). Nothing here is measured; every curve is a hypothesis.

Scale axis: octave bands of the bulk by singular-value index, [2^j, 2^(j+1)) counted from the spike edge (32 for d = 2048),
so j = 0..5 spans 32..2048 (1.8 decades). Every panel is TRAINED / CALIBRATOR (co-adapted random bulk), so the calibrator
is the line at 1 and the 'reservoir' prediction is flatness.
Panels: (A) input-projection profile ||v_k^T X||^2; (B) output-matched cost (output-side curvature); (C) raw size-matched
cost = A x B; (D) smoothness: dispersion across random k-subspaces, CV^2 vs k.
Three hypotheses: SELF-SIMILAR (Will: power law across octaves, no knee), RESERVOIR (flat = calibrator), HEAD-SCALE KNEE
(CC: flat on the head-nested side until the band crosses d_head, then a step; the residual side is where an exponent could
survive). Decision regions: 'flat' = within the band noise epsilon (placeholder 0.10 in log10 until the calibrator's
replicate spread is measured); 'power law' needs >= MIN_OCTAVES = 4 (1.2 decades; placeholder, sealed later) with a
likelihood-ratio preference over broken/cutoff; a knee is a broken power law whose break is at a declared scale.
Output: seals/armA_predictions.png (committed; not a plot of data).
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
OUT = Path(__file__).resolve().parent / "seals" / "armA_predictions.png"
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
C_SS, C_RES, C_KNEE, C_CAL = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"   # fixed categorical order 1,2,3; calibrator = gray
EPS, MIN_OCT = 0.10, 4
j = np.arange(6); kmid = 32 * 2.0 ** (j + 0.5); dhead = 128
ss_in = 10 ** (0.18 * (j - 2.5))              # self-similar: input-side power law (data-imprinted)
ss_out = 10 ** (0.08 * (j - 2.5))             # ... and a weaker one on the output side
res = np.ones(6)                               # reservoir: identical to the calibrator everywhere
knee_in = np.where(kmid < dhead, 1.0, 10 ** (0.12 * (j - 1.5)))   # CC: flat below the head scale, exponent above (input side)
knee_out = np.where(kmid < dhead, 1.35, 1.0)                        # CC: step at the head scale on the head-nested side
fig, ax = plt.subplots(2, 2, figsize=(11, 8.2), facecolor=SURF)
fig.suptitle("Arm A — predicted curves and decision regions (drawn before any code or data; nothing measured)",
             color=INK, fontsize=12, x=0.02, ha="left", y=0.985)
def frame(a, title, ylab):
    a.set_facecolor(SURF); a.set_title(title, color=INK, fontsize=10.5, loc="left")
    a.set_ylabel(ylab, color=INK2, fontsize=9); a.tick_params(colors=INK2, labelsize=8.5)
    for s in a.spines.values(): s.set_color(GRID)
    a.grid(True, color=GRID, lw=0.8); a.set_axisbelow(True)
def octave_axis(a):
    a.set_xticks(j); a.set_xticklabels([f"{32*2**i}–{32*2**(i+1)}" for i in j], fontsize=7.5, rotation=25, ha="right")
    a.set_xlabel("bulk octave by singular-value index (from the spike edge, d = 2048)", color=INK2, fontsize=9)
    a.axhspan(-EPS, EPS, color="#f0efec", zorder=0); a.axhline(0, color=C_CAL, lw=2, ls="--")
    a.axvline(np.log2(dhead / 32) - 0.5, color=INK2, lw=0.8, ls=":")
    a.text(np.log2(dhead / 32) - 0.42, a.get_ylim()[1] - 0.06, "d_head", color=INK2, fontsize=8, va="top")
def panel(a, title, ylab, curves):
    frame(a, title, ylab)
    ends = sorted([(float(np.log10(y[-1])), lab, c) for y, c, lab in curves])
    pos = [e[0] for e in ends]
    for i in range(1, len(pos)):                      # push labels apart by >= 0.07 in data units
        pos[i] = max(pos[i], pos[i - 1] + 0.07)
    for y, c, lab in curves:
        a.plot(j, np.log10(y), color=c, lw=2, marker="o", ms=5, markerfacecolor=SURF, markeredgewidth=2)
    for (yv, lab, c), yp in zip(ends, pos):
        a.annotate(lab, (j[-1], yv), xytext=(8, (yp - yv) * 120), textcoords="offset points", color=INK, fontsize=8.5, va="center")
    a.set_xlim(-0.5, 7.4); a.set_ylim(-0.5, 0.7); octave_axis(a)
    a.text(0.0, -0.36, f"shaded: 'flat' (|log10 ratio| < {EPS}, placeholder). A power-law call needs ≥ {MIN_OCT} octaves (LR test).",
           transform=a.transAxes, color=INK2, fontsize=7.5)
panel(ax[0, 0], "A. input-projection profile ‖vₖᵀX‖² (trained / calibrator)", "log10 ratio",
      [(ss_in, C_SS, "self-similar"), (res, C_RES, "reservoir"), (knee_in, C_KNEE, "head-scale knee (CC)")])
panel(ax[0, 1], "B. output-matched cost (output-side curvature, trained / calibrator)", "log10 ratio",
      [(ss_out, C_SS, "self-similar"), (res, C_RES, "reservoir"), (knee_out, C_KNEE, "head-scale knee (CC)")])
panel(ax[1, 0], "C. raw size-matched cost = A × B (trained / calibrator)", "log10 ratio",
      [(ss_in * ss_out, C_SS, "self-similar"), (res, C_RES, "reservoir"), (knee_in * knee_out, C_KNEE, "head-scale knee (CC)")])
# D: smoothness -- dispersion across random k-subspaces
a = ax[1, 1]; frame(a, "D. smoothness: dispersion of cost across random k-subspaces", "log10 CV² of cost")
k = 2.0 ** np.arange(3, 11)
a.plot(np.log2(k), np.log10(2.0 / k), color=C_SS, lw=2, marker="o", ms=5, markerfacecolor=SURF, markeredgewidth=2)
a.annotate("smooth, distributed: CV² ∝ 1/k", (np.log2(k[-1]), np.log10(2.0 / k[-1])), xytext=(-150, 10), textcoords="offset points", color=INK, fontsize=8.5)
lumpy = 0.6 * (1 + 0.5 * np.sin(np.arange(8) * 1.7)) / k ** 0.3
a.plot(np.log2(k), np.log10(lumpy), color=C_RES, lw=2, marker="o", ms=5, markerfacecolor=SURF, markeredgewidth=2)
a.annotate("concentrated: high, lumpy, slope > −1", (np.log2(k[-1]), np.log10(lumpy[-1])), xytext=(-170, 8), textcoords="offset points", color=INK, fontsize=8.5)
a.fill_between(np.log2(k), np.log10(2.0 / k) - 0.15, np.log10(2.0 / k) + 0.15, color="#f0efec", zorder=0)
a.set_xticks(np.log2(k)); a.set_xticklabels([str(int(x)) for x in k], fontsize=8)
a.set_xlabel("random-subspace dimension k (log2 axis)", color=INK2, fontsize=9)
a.text(0.0, -0.36, "shaded: slope −1 ± 0.15 (placeholder) = 'smooth'. Both hypotheses predict smooth.",
       transform=a.transAxes, color=INK2, fontsize=7.5)
fig.text(0.02, 0.012, "Reading: A flat & B flat → reservoir.  A or B a power law over ≥ 4 octaves → self-similar on that side.\n"
         "A break at d_head on the head-nested side → characteristic scale (CC).  D tests smoothness, not self-similarity.",
         color=INK2, fontsize=8.5, va="bottom")
fig.set_size_inches(11, 9.2); fig.tight_layout(rect=(0, 0.05, 1, 0.97), h_pad=3.0); OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT, dpi=150, facecolor=SURF); print("wrote", OUT)

"""Q4EXT descriptive tables + plots (Q4EXT_PREREG.md §2; committed before the extraction runs). DESCRIPTIVE ONLY: no
verdict changes. Reads the B4 bank (cache/armb/<arm>/step*/L*.npz: fp64 singular values) and the DW0 pass
(cache/armb/<arm>/DW0_*.npz) written by q4ext_extract.py.

Per arm (A0, M0s1, M0s3; A1, M0s2 as context where banked), per matrix type, per grid step:
  stable rank sr = sum(sigma^2)/sigma_1^2 (layer mean), sigma_1 (layer mean), ||W_t - W_0||_F / ||W_0||_F (layer mean, DW0 steps),
  the applied-LR integral (q1_models.cum), with the step-3000 values marked in the plots; the Q/K stable-rank trajectory.
M0s3 vs M0s1 on the shared grid <= 3000: ONE draw of the Muon-side spread -- per cell (step, layer, type) |sr_M0s3 - sr_M0s1| /
mean, summarised (median, IQR, fraction > 10 %), reported BESIDE Q4's "123/368 cells" (never a cell count re-read).
Output: results/armb_q4ext_descriptive.json, plots/armb_q4ext_*.png.
"""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
TYPES = ["Q", "K", "V", "O", "MLP_IN", "MLP_OUT"]; NL = 6
ARMS = ["A0", "M0s1", "M0s3", "A1", "M0s2"]
CACHE = ROOT / "cache" / "armb"


def banked_steps(arm):
    return sorted(int(p.name[4:]) for p in (CACHE / arm).glob("step*") if (p / "DONE").exists())


def sr_sigma1(arm, t):
    sr = {M: [] for M in TYPES}; s1 = {M: [] for M in TYPES}
    for L in range(NL):
        z = np.load(CACHE / arm / f"step{t:05d}" / f"L{L:02d}.npz")
        for M in TYPES:
            s = z[f"sig_{M}"]; sr[M].append(float((s ** 2).sum() / s[0] ** 2)); s1[M].append(float(s[0]))
    return {M: float(np.mean(v)) for M, v in sr.items()}, {M: float(np.mean(v)) for M, v in s1.items()}, sr


def dw0(arm):
    out = {}
    for fp in sorted((CACHE / arm).glob("DW0_*.npz")):
        t = int(fp.stem[4:]); z = np.load(fp); out[t] = {}
        for M in TYPES:
            d = np.mean([float(z[f"L{L:02d}_{M}_dw0_fro"]) for L in range(NL)])
            w = np.mean([float(z[f"L{L:02d}_{M}_w_fro"]) for L in range(NL)])
            out[t][M] = {"dw0_fro": d, "w_fro": w}
    return out


def lr_integral(arm, steps):
    import q1_models as QM
    W = {"A0": 1430, "A1": 2860, "A2": 715, "M0s1": 1430, "M0s2": 1430, "M0s3": 1430}[arm]
    C = QM._CX.get(arm) if arm in QM._CX else QM.cum(W, 12000)
    return {t: float(C[min(t, len(C) - 1)]) for t in steps}


def main():
    res = {"doc": __doc__.strip().splitlines()[0], "arms": {}}
    series = {}
    for arm in ARMS:
        if not (CACHE / arm).exists():
            continue
        steps = banked_steps(arm); rows = {}; per_layer = {}
        for t in steps:
            sr, s1, srl = sr_sigma1(arm, t); rows[t] = {"sr": sr, "sigma1": s1}; per_layer[t] = srl
        d0 = dw0(arm)
        res["arms"][arm] = {"n_steps": len(steps), "max_step": max(steps) if steps else None,
                            "at_3000": rows.get(3000), "at_max": rows.get(max(steps)) if steps else None,
                            "dw0_steps": sorted(d0), "lr_integral": lr_integral(arm, steps[-1:] + [3000] if steps else [])}
        series[arm] = (steps, rows, d0, per_layer)
        print(f"{arm}: {len(steps)} steps banked to {max(steps) if steps else None}; dw0 at {len(d0)} steps")
    # Muon-side spread: M0s3 vs M0s1 on the shared grid <= 3000 (one draw)
    if "M0s1" in series and "M0s3" in series:
        s1, r1, _, p1 = series["M0s1"]; s3, r3, _, p3 = series["M0s3"]
        shared = sorted(set(s1) & set(s3)); rel = []
        for t in shared:
            for M in TYPES:
                for L in range(NL):
                    a, b = p1[t][M][L], p3[t][M][L]; rel.append(abs(a - b) / (0.5 * (a + b)))
        rel = np.array(rel)
        res["muon_spread_one_draw"] = {"shared_steps": len(shared), "cells": int(rel.size),
                                       "median_rel": float(np.median(rel)), "iqr": [float(np.quantile(rel, .25)), float(np.quantile(rel, .75))],
                                       "frac_gt_10pct": float(np.mean(rel > 0.10)),
                                       "note": "ONE pair -> one draw of the Muon-side spread; beside Q4's AdamW seed SD (123/368 cells), not a cell count"}
        print("Muon spread (M0s3 vs M0s1, sr per cell):", {k: v for k, v in res["muon_spread_one_draw"].items() if k != "note"})
    (ROOT / "results").mkdir(exist_ok=True)
    json.dump(res, open(ROOT / "results" / "armb_q4ext_descriptive.json", "w"), indent=1)
    # plots
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    except ImportError:
        print("no matplotlib; tables only"); return
    (ROOT / "plots").mkdir(exist_ok=True)
    for metric, title in (("sr", "stable rank (layer mean)"), ("sigma1", "sigma_1 (layer mean)")):
        fig, axes = plt.subplots(2, 3, figsize=(13, 6.5))
        for ax, M in zip(axes.ravel(), TYPES):
            for arm, (steps, rows, _, _) in series.items():
                ax.plot(steps, [rows[t][metric][M] for t in steps], lw=1, label=arm)
            ax.axvline(3000, color="0.6", ls="--", lw=0.8); ax.set_xscale("symlog", linthresh=100); ax.set_title(M); ax.set_xlabel("step")
        axes[0, 0].legend(fontsize=7); fig.suptitle(f"Q4EXT descriptive: {title}; dashed = step 3000 (Q4's endpoint)")
        fig.tight_layout(); fig.savefig(ROOT / "plots" / f"armb_q4ext_{metric}.png", dpi=120); plt.close(fig)
    fig, axes = plt.subplots(2, 3, figsize=(13, 6.5))
    for ax, M in zip(axes.ravel(), TYPES):
        for arm, (steps, rows, d0, _) in series.items():
            ts = sorted(d0)
            if ts: ax.plot(ts, [d0[t][M]["dw0_fro"] / d0[0][M]["w_fro"] if 0 in d0 else d0[t][M]["dw0_fro"] for t in ts], "o-", ms=2, lw=1, label=arm)
        ax.axvline(3000, color="0.6", ls="--", lw=0.8); ax.set_xscale("symlog", linthresh=100); ax.set_title(f"{M}: ||W_t - W_0||_F / ||W_0||_F")
    axes[0, 0].legend(fontsize=7); fig.tight_layout(); fig.savefig(ROOT / "plots" / "armb_q4ext_dw0.png", dpi=120); plt.close(fig)
    print("WROTE results/armb_q4ext_descriptive.json + plots/armb_q4ext_{sr,sigma1,dw0}.png")


if __name__ == "__main__":
    main()

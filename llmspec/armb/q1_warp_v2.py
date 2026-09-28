"""Q1 E4 warp-and-compare licence, VERSION 2 (Will's sign-off 2026-09-28, pre-data; supersedes the v1 licence cells for
Q1). Sealed by the commit that adds it, BEFORE it runs and before B4 reads any arm. Synthetic only; runs on spot.

Why v2: the v1 HALFWAY confuser (shift dW/2) EQUALS the LR_INT map once both warmups have ended (cumulative LR differs by
lr0*dW/2), so it tested E4 against a copy of one hypothesis (A2 median |HALFWAY - LR_INT| = 0 steps; A1 71 vs >= 644
between real models). HALFWAY is RETIRED.
Estimator E4 itself is UNCHANGED (q1_warp.decide: affine height scaling, SSE over the window common to the three model
maps, NO_SIMPLE_ANCHOR via c_fit, SUPPORTED via the margin r*). Grids and windows come from grids.arm_grid (A2 dense,
B1a-A8): A1 [1450, 3000] on its standard grid, A2 [300, 2275] on its dense grid.
CONFUSERS per arm (truths that are none of the three models):
  MID_SL  tau = (tau_STEP + tau_LR_INT) / 2        midpoint between adjacent model maps
  MID_LW  tau = (tau_LR_INT + tau_WARMUP) / 2      midpoint between adjacent model maps
  STRETCH tau = 1.3 t                              easy extra
  OVERSHOOT tau = t - 1.5 (W_X - W_0)              easy extra
Truth classes cycle STEP, WARMUP, LR_INT, MID_SL, MID_LW, STRETCH, OVERSHOOT; 700 draws per cell (100 per class); shapes,
noise levels / types, amplitude changes and seeds' construction as q1_warp v1.
LICENCE per (arm, noise level, noise type):
  r* = the smallest value in {1.0, 1.1, 1.25, 1.5, 2.0} with every wrong-model rate <= 5% AND every confuser assigned to
       any SINGLE model <= 20%;
  E4 LICENSED (model verdicts) iff at r* every true-model rate >= 80%.
  NO_SIMPLE_ANCHOR LICENSED iff, at r*, NO_SIMPLE_ANCHOR fires on BOTH midpoint confusers at >= 80% (reported with its
  rate on the true models, which c_fit holds near 1%).
VERDICT WORDING (sealed): a SUPPORTED(X) from a licensed cell is reported as "X-driven" ONLY if NO_SIMPLE_ANCHOR is also
licensed for that cell; otherwise as "the closest of the three models is X" (a midpoint truth could not be told apart).
Output: results/armb_q1_warp_licence_v2.json.
"""
import json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import q1_warp as W  # noqa: E402
import q1_licence as QL  # noqa: E402
from grids import arm_grid  # noqa: E402

OUT = ROOT / "results" / "armb_q1_warp_licence_v2.json"
CONFUSERS = ["MID_SL", "MID_LW", "STRETCH", "OVERSHOOT"]
CLASSES = W.MODELS + CONFUSERS
DRAWS, SEED = 700, 20261004


def tau2(t, X, m):
    t = np.asarray(t, float)
    if m in W.MODELS:
        return W.tau(t, X, m)
    if m == "MID_SL":
        return (W.tau(t, X, "STEP") + W.tau(t, X, "LR_INT")) / 2
    if m == "MID_LW":
        return (W.tau(t, X, "LR_INT") + W.tau(t, X, "WARMUP")) / 2
    if m == "STRETCH":
        return 1.3 * t
    if m == "OVERSHOOT":
        from q1_models import ARMS, W0
        return t - 1.5 * (ARMS[X] - W0)
    raise ValueError(m)


def window_armgrid(X):
    g = np.array(arm_grid(X), float); ok = (g >= 300) & (g <= W.STOP[X])
    for m in W.MODELS:
        tm = W.tau(g, X, m); ok &= (tm >= 0) & (tm <= W.STOP["A0"])
    return g[ok]


W.window = window_armgrid                          # decide() reads the window through W.window (arm grids, A2 dense)


def main():
    rng = np.random.default_rng(SEED)
    res = json.loads(OUT.read_text()) if OUT.exists() else {"doc": __doc__, "cells": {}}
    g0 = QL.grid(W.STOP["A0"]); names = [n for n, _ in W.base_curves(g0)]
    for X in ("A1", "A2"):
        gX = np.array(arm_grid(X), float)
        for s in (0.005, 0.01, 0.02, 0.05):
            for ar in (False, True):
                key = f"{X}_s{s}_{'ar' if ar else 'iid'}"
                if key in res["cells"]:
                    continue
                recs = []
                for d in range(DRAWS):
                    name = names[rng.integers(len(names))]; truth = CLASSES[d % len(CLASSES)]
                    b = [0.8, 1.0, 1.25][rng.integers(3)]; a = rng.normal(0, 5)
                    y0 = W.gen_curve(name, g0) * (1 + QL.noise(rng, len(g0), 1, s, ar)[0])
                    clean = a + b * W.gen_curve(name, np.clip(tau2(gX, X, truth), 0, None))
                    yX = clean * (1 + QL.noise(rng, len(gX), 1, s, ar)[0])
                    _, sse, fr = W.decide(g0, y0, gX, yX, X, 1.0, None); recs.append((truth, sse, fr))
                c_fit = float(np.quantile([fr for m, _, fr in recs if m in W.MODELS], 0.99)); table = {}
                for r in W.R_GRID:
                    conf = {m: {} for m in CLASSES}
                    for truth, sse, fr in recs:
                        o = sorted(sse, key=sse.get)
                        dec = "NO_SIMPLE_ANCHOR" if fr > c_fit else (o[0] if sse[o[1]] / max(sse[o[0]], 1e-300) >= r else "INCONCLUSIVE")
                        conf[truth][dec] = conf[truth].get(dec, 0) + 1
                    conf = {m: {k: v / sum(cc.values()) for k, v in cc.items()} for m, cc in conf.items()}
                    table[str(r)] = {"confusion": conf,
                                     "max_offdiag": max(conf[m].get(o, 0) for m in W.MODELS for o in W.MODELS if o != m),
                                     "confuser_to_single_model": {c: max(conf[c].get(o, 0) for o in W.MODELS) for c in CONFUSERS},
                                     "min_diag": min(conf[m].get(m, 0) for m in W.MODELS),
                                     "nsa_on_midpoints": {c: conf[c].get("NO_SIMPLE_ANCHOR", 0) for c in ("MID_SL", "MID_LW")},
                                     "nsa_on_true_models": max(conf[m].get("NO_SIMPLE_ANCHOR", 0) for m in W.MODELS)}
                ok = [r for r in W.R_GRID if table[str(r)]["max_offdiag"] <= 0.05 and max(table[str(r)]["confuser_to_single_model"].values()) <= 0.20]
                rs = ok[0] if ok else None
                lic = bool(rs is not None and table[str(rs)]["min_diag"] >= 0.80)
                nsa = bool(rs is not None and min(table[str(rs)]["nsa_on_midpoints"].values()) >= 0.80)
                res["cells"][key] = {"c_fit": c_fit, "table": table, "r_star": rs, "LICENSED": lic, "NSA_LICENSED": nsa,
                                     "wording": ("X-driven" if (lic and nsa) else ("closest of the three models is X" if lic else None))}
                OUT.write_text(json.dumps(res, indent=1))
                t = table[str(rs or 1.0)]
                print(key, "LICENSED", lic, "NSA", nsa, "r*", rs, f"diag {t['min_diag']:.2f} offdiag {t['max_offdiag']:.3f}",
                      "conf->model", {c: round(v, 2) for c, v in t["confuser_to_single_model"].items()},
                      "nsa@mid", {c: round(v, 2) for c, v in t["nsa_on_midpoints"].items()}, flush=True)


if __name__ == "__main__":
    main()

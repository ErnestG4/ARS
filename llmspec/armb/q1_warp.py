"""Q1 estimator E4, WARP-AND-COMPARE (Will 09-27: approved in this form only; the pure-shift version is NOT approved),
and its confusion-matrix licence. ARMB_PREREG_B1B.md Q1; sealed with it. Synthetic only until sealed.

Time maps tau_m: arm-X step -> A0 step, from the sealed LR function (q1_models.py):
  STEP    tau(t) = t
  WARMUP  tau(t) = t - (W_X - W_0)
  LR_INT  tau(t) = Lambda_0^{-1}(Lambda_X(t))        (cumulative applied LR matched)
Comparison window (common to the three maps, so every model is scored on the same arm-X points): arm-X grid steps t
with 300 <= t <= stop_X and 0 <= tau_m(t) <= stop_A0 for every m. With stop_A0 = 3000: A1 -> [1430, 3000]; A2 -> [300, 2285].
Prediction under m: yhat_m(t) = a + b * y_A0(tau_m(t)), y_A0 interpolated linearly in log(step + 16) on A0's grid,
(a, b) by least squares ("scale the heights before comparing"). Fit: SSE_m over the window.
Decision per (arm, metric):
  best = argmin SSE; margin = SSE_second / SSE_best.
  NO SIMPLE ANCHOR  iff SSE_best / (n * s^2) > c_fit, s = pooled relative noise x level (measured on A0 and X about
                    their own Savitzky-Golay smooths), c_fit = the licence's 99th percentile of that ratio under the true model
  SUPPORTED(best)   iff margin >= r*   (r* fixed by the licence, below)
  INCONCLUSIVE      otherwise
Licence (per arm, per noise level sigma in {0.5, 1, 2, 5}%, i.i.d. and AR(1) phi 0.5; 500 draws per cell):
  A0 curves from the q1_licence shape families (kinked / smooth minima, plateaus; depth 15% and 40%; every family
  member with t0 >= 1000, i.e. t0 in {1500, 2200}); the arm-X curve is generated under a TRUE model m* in {STEP, WARMUP, LR_INT, HALFWAY}
  (HALFWAY: tau(t) = t - (W_X - W_0)/2, matching no model), with an amplitude change b* in {0.8, 1.0, 1.25} and offset;
  independent noise on A0 and X.
  Confusion matrix P(decision | m*). r* = the smallest value in {1.0, 1.1, 1.25, 1.5, 2.0} for which every
  off-diagonal entry (wrong model SUPPORTED) <= 5% and HALFWAY -> any single model SUPPORTED <= 20%; E4 is LICENSED for
  that (arm, sigma, noise type) iff at that r* every diagonal entry (true model SUPPORTED) >= 80%.
Output: results/armb_q1_warp_licence.json.
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.signal import savgol_filter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import q1_models as QM  # noqa: E402
import q1_licence as QL  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "armb_q1_warp_licence.json"
STOP = {"A0": 3000, "A1": 5000, "A2": 3000}
MODELS = ["STEP", "WARMUP", "LR_INT"]
R_GRID = [1.0, 1.1, 1.25, 1.5, 2.0]
DRAWS, SEED = 500, 20260929
_C0 = QM._C0


def tau(t, X, m):
    t = np.asarray(t, float)
    if m == "STEP":
        return t
    if m == "WARMUP":
        return t - (QM.ARMS[X] - QM.W0)
    if m == "HALFWAY":
        return t - (QM.ARMS[X] - QM.W0) / 2
    lam = np.interp(t, np.arange(len(QM._CX[X])), QM._CX[X])          # LR_INT
    return np.interp(lam, _C0, np.arange(len(_C0)))


def window(X):
    g = QL.grid(STOP[X])
    ok = (g >= 300) & (g <= STOP[X])
    for m in MODELS:
        tm = tau(g, X, m); ok &= (tm >= 0) & (tm <= STOP["A0"])
    return g[ok]


def interp0(g0, y0, tq):
    return np.interp(np.log(tq + 16), np.log(g0 + 16), y0)


def fit_sse(g0, y0, tX, yX, X, m):
    p = interp0(g0, y0, tau(tX, X, m)); A = np.vstack([np.ones_like(p), p]).T
    c, *_ = np.linalg.lstsq(A, yX, rcond=None)
    return float(((yX - A @ c) ** 2).sum())


def noise_level(y):
    sm = savgol_filter(y, 9, 2); return float(np.std((y - sm) / sm, ddof=1))


def decide(g0, y0, gX, yX, X, r_star, c_fit):
    w = np.isin(gX, window(X)); tX, yw = gX[w], yX[w]
    sse = {m: fit_sse(g0, y0, tX, yw, X, m) for m in MODELS}
    order = sorted(sse, key=sse.get); best, second = order[0], order[1]
    s = np.sqrt((noise_level(y0) ** 2 + noise_level(yX) ** 2) / 2) * float(np.mean(yw))
    fit_ratio = sse[best] / (len(yw) * s ** 2)
    if c_fit is not None and fit_ratio > c_fit:
        return "NO_SIMPLE_ANCHOR", sse, fit_ratio
    margin = sse[second] / max(sse[best], 1e-300)
    return (best if margin >= r_star else "INCONCLUSIVE"), sse, fit_ratio


def base_curves(g):
    out = []
    for kind, name, f, t0, plat in QL.shapes(g, STOP["A0"]):
        if kind in ("b", "c") and (t0 is None or t0 >= 1000) and "_d0.05_" not in name:
            out.append((name, t0))
    return out


_GD = np.arange(0, 6001, 5, dtype=float)
_SHAPES = {nm: ff for _, nm, ff, _, _ in QL.shapes(_GD, 6000)}


def gen_curve(name, t, stop_ref=6000):
    """Evaluate the named A0 shape at arbitrary steps t (q1_licence shape formulas on a dense 5-step grid)."""
    return np.interp(t, _GD, _SHAPES[name])


def main():
    rng = np.random.default_rng(SEED)
    res = json.loads(OUT.read_text()) if OUT.exists() else {"doc": __doc__, "cells": {}}
    g0 = QL.grid(STOP["A0"])
    names = [n for n, _ in base_curves(g0)]
    for X in ("A1", "A2"):
        gX = QL.grid(STOP[X])
        for s in (0.005, 0.01, 0.02, 0.05):
            for ar in (False, True):
                key = f"{X}_s{s}_{'ar' if ar else 'iid'}"
                if key in res["cells"]:
                    continue
                recs = []                                      # (m*, sse dict, fit_ratio)
                for d in range(DRAWS):
                    name = names[rng.integers(len(names))]; mstar = ["STEP", "WARMUP", "LR_INT", "HALFWAY"][d % 4]
                    b = [0.8, 1.0, 1.25][rng.integers(3)]; a = rng.normal(0, 5)
                    y0 = gen_curve(name, g0, 6000) * (1 + QL.noise(rng, len(g0), 1, s, ar)[0])
                    tX = tau(gX, X, mstar)
                    clean = a + b * gen_curve(name, np.clip(tX, 0, None), 6000)
                    yX = clean * (1 + QL.noise(rng, len(gX), 1, s, ar)[0])
                    _, sse, fr = decide(g0, y0, gX, yX, X, 1.0, None)
                    recs.append((mstar, sse, fr))
                c_fit = float(np.quantile([fr for m, _, fr in recs if m != "HALFWAY"], 0.99))
                table = {}
                for r in R_GRID:
                    conf = {m: {} for m in MODELS + ["HALFWAY"]}
                    for mstar, sse, fr in recs:
                        order = sorted(sse, key=sse.get)
                        dec = ("NO_SIMPLE_ANCHOR" if fr > c_fit else
                               (order[0] if sse[order[1]] / max(sse[order[0]], 1e-300) >= r else "INCONCLUSIVE"))
                        conf[mstar][dec] = conf[mstar].get(dec, 0) + 1
                    conf = {m: {k: v / sum(c.values()) for k, v in c.items()} for m, c in conf.items()}
                    off = max(conf[m].get(o, 0) for m in MODELS for o in MODELS if o != m)
                    half = max(conf["HALFWAY"].get(o, 0) for o in MODELS)
                    diag = min(conf[m].get(m, 0) for m in MODELS)
                    table[str(r)] = {"confusion": conf, "max_offdiag": off, "halfway_to_single_model": half, "min_diag": diag}
                ok_r = [r for r in R_GRID if table[str(r)]["max_offdiag"] <= 0.05 and table[str(r)]["halfway_to_single_model"] <= 0.20]
                r_star = ok_r[0] if ok_r else None
                lic = bool(r_star is not None and table[str(r_star)]["min_diag"] >= 0.80)
                res["cells"][key] = {"c_fit": c_fit, "table": table, "r_star": r_star, "LICENSED": lic}
                OUT.write_text(json.dumps(res, indent=1))
                t = table[str(r_star)] if r_star else None
                print(key, "r*", r_star, "LICENSED", lic, "" if t is None else
                      f"min_diag {t['min_diag']:.2f} offdiag {t['max_offdiag']:.3f} halfway {t['halfway_to_single_model']:.2f}", flush=True)


if __name__ == "__main__":
    main()

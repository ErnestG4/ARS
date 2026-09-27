"""Q2 crossing-time localisation licence (ARMB_PREREG_B1B.md Q2; sealed with it). Synthetic only.

Event time = the first grid step at which a trajectory crosses its threshold. Estimator X1: Savitzky-Golay smooth
(window 5, order 2, on the grid index) and take the first grid step whose smoothed value is past the threshold and
stays past it for the next 3 grid points; if it never does, "not crossed".
Synthetic trajectories on A0's grid (stop 3000): sigmoids in u = log(t + 16), rising (head fractions, induction score) or
falling (stable rank, loss), plus an asymmetric Gompertz variant; crossing time tc in {300, 512, 800, 1200, 1800};
width w in {0.1, 0.3, 0.6} (log units); threshold = the level the clean curve has at tc.
Noise: (i) additive on a 0-1 fraction scale, sd in {0.01, 0.03, 0.07} (0.07 ~ binomial sd at p = 0.5 over 48 heads);
(ii) relative, sd in {0.5, 1, 2, 5}%. i.i.d. and AR(1) phi 0.5. 500 draws per cell.
Output per (noise kind, level, type): e_x = the 95% quantile of |t_hat - tc| over all shapes, and the worst-shape
value; the miss rate ("not crossed" although the clean curve crosses). At analysis, the noise of each event trajectory
is measured about its own smooth (a noise measurement, not the effect); the next-higher licence row gives e_x, and the
Q2 ordering rule uses [t +- e_x]. Output: results/armb_q2_licence.json.
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.signal import savgol_filter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import q1_licence as QL  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "armb_q2_licence.json"
DRAWS, SEED = 500, 20260930


def curves(g):
    u = np.log(g + 16); out = []
    for tc in (300, 512, 800, 1200, 1800):
        uc = np.log(tc + 16)
        for w in (0.1, 0.3, 0.6):
            s = 1 / (1 + np.exp(-(u - uc) / w))
            gz = np.exp(-np.exp(-(u - uc) / w) * np.log(2))           # Gompertz, = 0.5 at uc
            for nm, f in (("sig", s), ("gomp", gz)):
                out.append((f"{nm}_tc{tc}_w{w}_rise", f, tc, +1))
                out.append((f"{nm}_tc{tc}_w{w}_fall", 1 - f, tc, -1))
    return out


def x1(y, g, thr, sgn):
    sm = savgol_filter(y, 5, 2, axis=-1)
    past = (sm - thr) * sgn >= 0
    ok = past.copy()
    for k in range(1, 4):
        ok[..., :-k] &= past[..., k:]
    ok[..., -3:] = False
    idx = np.where(ok.any(-1), ok.argmax(-1), -1)
    return np.where(idx >= 0, g[np.clip(idx, 0, None)], np.nan)


def main():
    rng = np.random.default_rng(SEED); g = QL.grid(3000)
    res = {"doc": __doc__, "cells": {}}
    for kind, levels in (("abs", (0.01, 0.03, 0.07)), ("rel", (0.005, 0.01, 0.02, 0.05))):
        for s in levels:
            for ar in (False, True):
                errs, worst, miss = [], {}, []
                for name, f, tc, sgn in curves(g):
                    base = 0.1 + 0.8 * f if kind == "abs" else 20 + 80 * f
                    thr = float(np.interp(np.log(tc + 16), np.log(g + 16), base))
                    e = QL.noise(rng, len(g), DRAWS, s, ar)
                    y = base[None, :] + e if kind == "abs" else base[None, :] * (1 + e)
                    th = x1(y, g, thr, sgn); m = np.isnan(th)
                    miss.append(float(m.mean())); err = np.abs(th[~m] - tc)
                    errs.extend(err.tolist()); worst[name] = float(np.quantile(err, 0.95)) if len(err) else float("nan")
                key = f"{kind}_{s}_{'ar' if ar else 'iid'}"
                res["cells"][key] = {"e_x_95_all": float(np.quantile(errs, 0.95)),
                                     "e_x_95_worst_shape": float(np.nanmax(list(worst.values()))),
                                     "worst_shape": max(worst, key=lambda k: -1 if np.isnan(worst[k]) else worst[k]),
                                     "max_miss_rate": max(miss)}
                print(key, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res["cells"][key].items()}, flush=True)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()

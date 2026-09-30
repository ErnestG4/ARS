"""Q1 turning-point estimator licence (ARMB_PREREG_B1B.md, Q1; sealed with it). Known answer, synthetic only -- runs
BEFORE any arm data exists.

Grids: the sealed checkpoint grid (B1a §2) truncated at 3000 (A1/A2/M0) and at 5000 (A0).
Shapes (value vs step t; all positive; R = range):
  (a) NO turning point, monotone decreasing: exponential F + A e^{-t/tau} (tau 300 / 800 / 2000), power law
      F + A (1 + t/tau)^-alpha (tau 100, alpha 0.5 / 1), logistic F + A / (1 + e^{(t - c)/w}) (c 800 / 2000, w 200)
  (b) planted minimum at t0 [two sub-families: KINKED (zero slope left, positive slope right: the shape an LR kink at
      warmup end would make) and SMOOTH (zero slope on both sides, rise d*R*(1 - exp(-((u-u0)/lam)^2)) in u = log(t+16))] in {800, 1500, 2200, 2900} (2900 only on the 5000 grid is interior with margin; on the 3000
      grid t0 = 2900 is skipped), rebound depth d in {5%, 15%, 40%} of R, asymmetric: quadratic fall in log-step to t0,
      rise d*R*(1 - e^{-(t - t0)/kappa}) with kappa in {300, 1000}
  (c) plateau-then-rise: flat minimum of width w in {200, 600} centred at t0 in {1500, 2200}, rise as in (b), d = 15%
Noise: multiplicative, relative SD s in {0.5%, 1%, 2%, 5%}; i.i.d. and AR(1) with phi = 0.5. 400 draws per cell.
Estimators (interior window: t in [300, stop - 250]):
  E1: Savitzky-Golay smoothing on the grid index (window 9, order 2); t* = argmin of the smoothed curve; residual
      bootstrap (B = 200, i.i.d. resampling of residuals about the smooth); TURNING POINT iff >= 95% of bootstrap
      replicates have their argmin inside the interior window AND the smoothed rise from the argmin to the last point
      > 0; CI = 5-95% quantiles of the bootstrap argmins.
  E2: E1's argmin, refined by a quadratic fit in log-step over +-6 grid points; TURNING POINT iff curvature > 0 with
      t-stat > 3 AND the vertex inside the fit window AND inside the interior window; CI by the same residual bootstrap.
  E3 (added pre-seal after the smoke showed E1's kink bias): asymmetric parabola in log-step, y = m + aL (u-v)^2 left of
      the vertex v and m + aR (u-v)^2 right of it, fitted by profile least squares over v (60 candidates) on +-12 grid
      points around E1's argmin; TURNING POINT iff aL, aR both > 0 with t > 3 AND t* inside the interior window; CI =
      5-95% quantiles of v over a 100-replicate residual bootstrap about the fitted model.
Licence per (grid, noise level, noise type), per estimator (rev 2, after Will's 09-27 review): false TP on (a) <= 5%;
detection on (b) >= 80% at d >= 15%; e(sigma) = the WORST-SHAPE 98.75% quantile of |t_hat - t0| over detected (b)/(c)
draws at d >= 15% (plateau: distance to the plateau). e(sigma) feeds the sealed decidability rule; the median error and the
bootstrap-CI coverage are REPORTED only (no longer criteria). 1000 draws per cell. Output: results/armb_q1_licence.json.
"""
import json, os, sys
from pathlib import Path
import numpy as np
from scipy.signal import savgol_filter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "armb_q1_licence.json"
DRAWS, BOOT, SEED = 1000, 200, 20260928


def grid(stop):
    g = set(range(0, 501, 10)) | {1, 2, 4, 8, 16, 32, 64, 128, 256, 512} | set(range(500, min(stop, 3000) + 1, 25))
    if stop > 3000:
        g |= set(range(3000, stop + 1, 100))
    return np.array(sorted(x for x in g if x <= stop), float)


def interval_at(g, t0):
    i = np.searchsorted(g, t0)
    return float(g[min(i, len(g) - 1)] - g[max(i - 1, 0)])


def shapes(g, stop):
    t = g; A, F = 100.0, 20.0
    out = []
    for tau in (300, 800, 2000):
        out.append(("a", f"exp{tau}", F + A * np.exp(-t / tau), None, None))
    for alpha in (0.5, 1.0):
        out.append(("a", f"pow{alpha}", F + A * (1 + t / 100) ** -alpha, None, None))
    for c in (800, 2000):
        out.append(("a", f"logi{c}", F + A / (1 + np.exp((t - c) / 200)), None, None))
    lt = np.log(t + 16)
    for t0 in (800, 1500, 2200, 2900):
        if t0 > stop - 400:
            continue
        for d in (0.05, 0.15, 0.40):
            for kap in (300, 1000):
                fall = F + A * ((np.log(t0 + 16) - lt) / np.log(t0 + 16)) ** 2
                rise = F + d * A * (1 - np.exp(-(t - t0) / kap))
                out.append(("b", f"t{t0}_d{d}_k{kap}", np.where(t < t0, fall, rise), t0, None))
                lam = np.log((t0 + kap + 16) / (t0 + 16)); u0 = np.log(t0 + 16)
                rise_s = F + d * A * (1 - np.exp(-((lt - u0) / lam) ** 2))           # zero slope at t0 on both sides
                out.append(("b", f"smooth_t{t0}_d{d}_k{kap}", np.where(t < t0, fall, rise_s), t0, None))
    for t0 in (1500, 2200):
        for w in (200, 600):
            if t0 + w / 2 > stop - 400:
                continue
            lo, hi = t0 - w / 2, t0 + w / 2
            fall = F + A * ((np.log(lo + 16) - lt) / np.log(lo + 16)) ** 2
            rise = F + 0.15 * A * (1 - np.exp(-(t - hi) / 300))
            out.append(("c", f"plat{t0}_w{w}", np.where(t < lo, fall, np.where(t <= hi, F, rise)), t0, (lo, hi)))
    return out


def noise(rng, n, draws, s, ar):
    e = rng.standard_normal((draws, n))
    if ar:
        for i in range(1, n):
            e[:, i] = 0.5 * e[:, i - 1] + np.sqrt(1 - 0.25) * e[:, i]
    return s * e


def estimate(y, g, stop, rng):
    """y: (draws, n). Returns per draw: (tp_E1, tstar_E1, ci_E1, tp_E2, tstar_E2, ci_E2)."""
    n = y.shape[1]; inside = (g >= 300) & (g <= stop - 250)
    sm = savgol_filter(y, 9, 2, axis=1); res = y - sm
    out = []
    for k in range(y.shape[0]):
        bi = rng.integers(0, n, (BOOT, n))
        yb = sm[k] + res[k][bi]; smb = savgol_filter(yb, 9, 2, axis=1)
        am = smb.argmin(1); rise = smb[:, -1] - smb[np.arange(BOOT), am]
        ok = inside[am] & (rise > 0)
        tp1 = ok.mean() >= 0.95; a0 = int(sm[k].argmin()); t1 = g[a0]
        ci1 = (np.quantile(g[am], 0.05), np.quantile(g[am], 0.95))
        # E2: quadratic in log-step around a0
        lo, hi = max(a0 - 6, 0), min(a0 + 7, n); x = np.log(g[lo:hi] + 16); yy = y[k, lo:hi]
        tp2, t2, ci2 = False, np.nan, (np.nan, np.nan)
        if hi - lo >= 5:
            X = np.vstack([x ** 2, x, np.ones_like(x)]).T
            coef, *_ = np.linalg.lstsq(X, yy, rcond=None)
            r = yy - X @ coef; dof = max(len(x) - 3, 1)
            cov = (r @ r / dof) * np.linalg.pinv(X.T @ X)
            tcurv = coef[0] / np.sqrt(max(cov[0, 0], 1e-300))
            if coef[0] > 0:
                v = -coef[1] / (2 * coef[0]); t2 = float(np.exp(v) - 16)
                tp2 = bool(tcurv > 3 and x[0] <= v <= x[-1] and 300 <= t2 <= stop - 250)
                Yb = (X @ coef)[None, :] + r[rng.integers(0, len(r), (BOOT, len(r)))]
                CB = Yb @ np.linalg.pinv(X).T                                  # (BOOT, 3) least-squares refits
                good = CB[:, 0] > 0
                if good.any():
                    vb = np.exp(-CB[good, 1] / (2 * CB[good, 0])) - 16
                    ci2 = (float(np.quantile(vb, 0.05)), float(np.quantile(vb, 0.95)))
        tp3, t3, ci3 = e3(y[k], g, stop, a0, rng)
        out.append((tp1, t1, ci1, tp2, t2, ci2, tp3, t3, ci3))
    return out


def _asym_batch(x, Y, vs):
    """Profile LS of y = m + aL (x-v)^2 [x<v] + aR (x-v)^2 [x>=v] for every candidate v and every row of Y at once.
    Fits with aL < 0 or aR < 0 are excluded. Returns (best v index per row, coefficients (rows, 3), sse per row, X)."""
    L = np.where(x[None, :] < vs[:, None], (x[None, :] - vs[:, None]) ** 2, 0.0)       # (V, m)
    R = np.where(x[None, :] >= vs[:, None], (x[None, :] - vs[:, None]) ** 2, 0.0)
    X = np.stack([np.ones_like(L), L, R], axis=2)                                    # (V, m, 3)
    P = np.linalg.pinv(X)                                                            # (V, 3, m)
    C = np.einsum("vkm,bm->bvk", P, Y)                                               # (B, V, 3)
    fit = np.einsum("vmk,bvk->bvm", X, C)
    sse = ((Y[:, None, :] - fit) ** 2).sum(-1)                                       # (B, V)
    sse = np.where((C[..., 1] >= 0) & (C[..., 2] >= 0), sse, np.inf)
    iv = sse.argmin(1)
    return iv, C[np.arange(len(Y)), iv], sse[np.arange(len(Y)), iv], X


def e3(y, g, stop, a0, rng, K=12):
    n = len(g); lo, hi = max(a0 - K, 0), min(a0 + K + 1, n)
    x = np.log(g[lo:hi] + 16); yy = y[lo:hi]
    if hi - lo < 7:
        return False, np.nan, (np.nan, np.nan)
    vs = np.linspace(x[1], x[-2], 60)
    iv, C, sse, X = _asym_batch(x, yy[None, :], vs)
    if not np.isfinite(sse[0]):
        return False, np.nan, (np.nan, np.nan)
    Xv = X[iv[0]]; c = C[0]; yhat = Xv @ c; r = yy - yhat
    cov = (sse[0] / max(len(x) - 4, 1)) * np.linalg.pinv(Xv.T @ Xv)
    tL, tR = c[1] / np.sqrt(max(cov[1, 1], 1e-300)), c[2] / np.sqrt(max(cov[2, 2], 1e-300))
    t3 = float(np.exp(vs[iv[0]]) - 16)
    tp = bool(tL > 3 and tR > 3 and 300 <= t3 <= stop - 250)
    Yb = yhat[None, :] + r[rng.integers(0, len(r), (100, len(r)))]
    ivb, _, sseb, _ = _asym_batch(x, Yb, vs)
    vb = np.exp(vs[ivb[np.isfinite(sseb)]]) - 16
    ci = (float(np.quantile(vb, 0.05)), float(np.quantile(vb, 0.95))) if len(vb) else (np.nan, np.nan)
    return tp, t3, ci


def main():
    rng = np.random.default_rng(SEED)
    res = json.loads(OUT.read_text()) if OUT.exists() else {"doc": __doc__, "cells": {}}
    for stop in (3000, 5000):
        g = grid(stop)
        for s in (0.005, 0.01, 0.02, 0.05):
            for ar in (False, True):
                key = f"stop{stop}_s{s}_{'ar' if ar else 'iid'}"
                if key in res["cells"]:
                    continue
                cell = {}
                for kind, name, f, t0, plat in shapes(g, stop):
                    y = f[None, :] * (1 + noise(rng, len(g), DRAWS, s, ar))
                    est = estimate(y, g, stop, rng)
                    rec = {}
                    for j, E in ((0, "E1"), (3, "E2"), (6, "E3")):
                        tp = np.array([e[j] for e in est]); ts = np.array([e[j + 1] for e in est], float)
                        ci = np.array([e[j + 2] for e in est], float)
                        r = {"tp_rate": float(tp.mean())}
                        if kind != "a" and tp.any():
                            tol = max(interval_at(g, t0), 0.05 * t0)
                            if kind == "b":
                                err = ts[tp] - t0; cov = ((ci[tp, 0] <= t0) & (t0 <= ci[tp, 1]))
                                r.update({"med_err": float(np.median(err)), "tol": tol, "loc_ok": bool(abs(np.median(err)) <= tol),
                                          "err9875": float(np.quantile(np.abs(err), 0.9875))})
                            else:
                                lo, hi = plat; gi = interval_at(g, t0)
                                dist = np.maximum(0, np.maximum(lo - ts[tp], ts[tp] - hi))
                                cov = (ci[tp, 0] <= hi) & (ci[tp, 1] >= lo)
                                r.update({"med_dist_to_plateau": float(np.median(dist)), "tol": gi, "loc_ok": bool(np.median(dist) <= gi),
                                          "err9875": float(np.quantile(dist, 0.9875))})
                            r["ci_coverage"] = float(cov.mean())
                        rec[E] = r
                    cell[f"{kind}:{name}"] = rec
                lic = {}
                for E in ("E1", "E2", "E3"):
                    fa = max(v[E]["tp_rate"] for k, v in cell.items() if k.startswith("a:"))
                    det = min(v[E]["tp_rate"] for k, v in cell.items() if k.startswith("b:") and "_d0.05_" not in k)
                    errs = [v[E].get("err9875") for k, v in cell.items() if (k.startswith("b:") or k.startswith("c:")) and "_d0.05_" not in k]
                    e_sig = (max(errs) if errs and all(x is not None for x in errs) else None)
                    lic[E] = {"max_false_tp": fa, "min_detection_d>=15%": det, "e_sigma_9875_worst_shape": e_sig,
                              "LICENSED": bool(fa <= 0.05 and det >= 0.80 and e_sig is not None)}
                res["cells"][key] = {"shapes": cell, "licence": lic}
                OUT.write_text(json.dumps(res, indent=1))
                print(key, {E: (round(v["max_false_tp"], 3), round(v["min_detection_d>=15%"], 3), v["e_sigma_9875_worst_shape"], v["LICENSED"]) for E, v in lic.items()}, flush=True)


if __name__ == "__main__":
    main()

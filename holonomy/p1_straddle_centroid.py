"""Locate the straddle peak properly: more seeds, narrowed grid, CENTROID.
COMMITTED GENERATOR of holonomy/p1_straddle_centroid.json.  DIAGNOSTIC.

p1_straddle_law.py returned UNDERPOWERED_FOR_LOCATION: only deg 5's peak was
resolved above its own row's runner-up (6.8 sem), while deg 9 and 13 argmaxes
sat 0.4 and 1.5 sem above theirs -- argmaxes over noise, not located peaks.
Its own diagnosis was "more seeds, not a wider grid", so:

  * SEEDS 24 -> 200 (sem falls ~2.9x; a real separation grows as sqrt(N) in sem
    units, so a 0.4-sem margin becomes ~1.2 and a 1.5-sem one becomes ~4.3).
  * Grid narrowed to the elevated region, since the wings are already flat.
  * ARGMAX replaced by a CENTROID of the elevation. An argmax throws away every
    point except one and has no error bar; the centroid uses the whole profile,
    so it is far better powered for the quantity actually claimed -- WHERE the
    elevation sits. Baseline-subtracted (median of the row) and clipped at zero
    so only genuine elevation contributes, with a bootstrap CI over seeds.

PREDICTION, COMMITTED BEFORE THE RUN: centroids near 4.0 (deg 9) and 6.0
(deg 13), i.e. tracking (deg-1)/2, with CIs that exclude each other. If the two
CIs OVERLAP, the peak does not demonstrably move between these degrees and the
straddle law stays unproven regardless of where the argmaxes fell.
"""
import json, sys, warnings
import numpy as np

warnings.filterwarnings("ignore")
ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")
from transitions import (gen_gue_unfolded, make_trend_maps, p1_apply,   # noqa: E402
                         sigma2_at)
import predict_p1 as PP                                                 # noqa: E402

N_FULL, N_W, A, L = 1200, 600, 0.25, 10.0
SEEDS, N_MAT = 200, 2048
DIALS = [2.0, 3.0, 4.0, 6.0, 8.0, 10.0]
DEGS = [9, 13]


def predict(dial, deg):
    ell = N_W / dial
    u = np.linspace(0.0, float(N_FULL), 48001)
    x_of_u, _ = make_trend_maps(A, ell, u_hi=float(N_FULL))
    x = x_of_u(u)
    lo, hi = (N_FULL - N_W) / 2.0, (N_FULL + N_W) / 2.0
    w = (u >= lo) & (u <= hi)
    cA, cB = np.polyfit(x, u, deg), np.polyfit(x[w], u[w] - lo, deg)
    return float(PP.spurious_var(np.polyval(cA, x[w]), u[w], L)
                 - PP.spurious_var(np.polyval(cB, x[w]), u[w], L))


def centroid(res):
    """Baseline-subtracted, zero-clipped centroid over DIALS."""
    e = np.clip(np.abs(res) - np.median(np.abs(res)), 0.0, None)
    return float(np.sum(np.asarray(DIALS) * e) / np.sum(e)) if e.sum() > 0 else np.nan


def main():
    spectra = {}
    for s in range(SEEDS):
        ua = gen_gue_unfolded(N_MAT, s)
        lo = (len(ua) - N_FULL) // 2
        spectra[s] = ua[lo:lo + N_FULL] - ua[lo]
    print(f"{SEEDS} seeds cached\n")
    rng = np.random.default_rng(11)
    out = dict(seeds=SEEDS, dials=DIALS, degs=DEGS, a=A, L=L,
               prediction="centroids near 4.0 (deg 9) and 6.0 (deg 13), CIs disjoint",
               grid={})
    for deg in DEGS:
        per_seed, preds = [], []
        for dial in DIALS:
            ell = N_W / dial
            x_of_u, _ = make_trend_maps(A, ell, u_hi=float(N_FULL))
            p = predict(dial, deg); preds.append(p)
            col = []
            for s in range(SEEDS):
                x = x_of_u(spectra[s])
                sA = sigma2_at(p1_apply(x, "unfold_then_window", deg, N_W), [L])[0]
                sB = sigma2_at(p1_apply(x, "window_then_unfold", deg, N_W), [L])[0]
                col.append(sA - sB - p)
            per_seed.append(col)
        M = np.asarray(per_seed, float)                     # dials x seeds
        mean_res = np.nanmean(M, axis=1)
        sem = np.nanstd(M, axis=1, ddof=1) / np.sqrt(M.shape[1])
        c = centroid(mean_res)
        boots = []
        for _ in range(2000):
            idx = rng.integers(0, M.shape[1], M.shape[1])
            boots.append(centroid(np.nanmean(M[:, idx], axis=1)))
        boots = np.asarray([b for b in boots if np.isfinite(b)])
        lo, hi = np.percentile(boots, [2.5, 97.5])
        out["grid"][str(deg)] = dict(
            residuals=mean_res.tolist(), sems=sem.tolist(), predicted=preds,
            centroid=c, ci95=[float(lo), float(hi)], target=(deg - 1) / 2.0)
        print(f"deg {deg:>2}  " + " ".join(f"{v:+.4f}" for v in mean_res))
        print(f"        sem " + " ".join(f"{v:.4f}" for v in sem))
        print(f"        centroid {c:.2f}  95% CI [{lo:.2f}, {hi:.2f}]  "
              f"predicted {(deg-1)/2.0:.1f}\n", flush=True)

    a, b = out["grid"]["9"], out["grid"]["13"]
    disjoint = bool(a["ci95"][1] < b["ci95"][0] or b["ci95"][1] < a["ci95"][0])
    hits = sum(1 for g in (a, b) if g["ci95"][0] <= g["target"] <= g["ci95"][1])
    out["cis_disjoint"], out["n_targets_in_ci"] = disjoint, hits
    out["verdict"] = (
        f"STRADDLE_LAW_SUPPORTED — centroids {a['centroid']:.2f} and "
        f"{b['centroid']:.2f} are disjoint at 95% and {hits}/2 contain their "
        "(deg-1)/2 target; the elevation demonstrably MOVES with degree"
        if disjoint and hits >= 1 else
        f"NOT_DEMONSTRATED — centroids {a['centroid']:.2f} [{a['ci95'][0]:.2f},"
        f"{a['ci95'][1]:.2f}] and {b['centroid']:.2f} [{b['ci95'][0]:.2f},"
        f"{b['ci95'][1]:.2f}] {'overlap' if not disjoint else 'are disjoint but miss their targets'}"
        "; the peak does not demonstrably track (deg-1)/2")
    print(f"VERDICT: {out['verdict']}")
    json.dump(out, open(f"{ROOT}/holonomy/p1_straddle_centroid.json", "w"), indent=1)


if __name__ == "__main__":
    main()

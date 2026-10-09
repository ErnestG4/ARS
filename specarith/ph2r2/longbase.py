"""R₂ §3 follow-up (Will, 2026-10-09): a long sine-kernel baseline for the shrinking error bars. Exploratory and
descriptive; the confirmatory test is a later seal on fresh heights.

Question: the zeros' drift-removed bootstrap SD of the pair sum falls with block length (0.59–0.75 of its 100-level value
at 10,000 levels; PH2R2_FINDINGS §3). Independent CUE_250 blocks cannot carry correlation beyond 250 levels. Does a
single long GUE (sine-kernel) sequence, run through the identical drift-removed bootstrap, also shrink?

Baseline: Dumitriu–Edelman GUE tridiagonal (β = 2) of size n_mat = ⌈1.06·L⌉, all eigenvalues by LAPACK sterf (as
ph6/bands61.py), central L kept (≈ 94% of the spectrum), unfolded by the exact semicircle count n_mat·F(x) with
R² = 8·n_mat (trace identity: E tr H² = 2n² for this normalisation), then mapped onto ζ heights of bin NAME by
t = N̄⁻¹(N̄(t₀) + u) — the G0b map — as ONE window of L levels. The zeros: bin NAME's Platt file cut into consecutive
disjoint windows of L levels from t₀, each one window. Both go through the same code: g0b.contributions (primary f,
bin δ) → r2run.drift_removed → g0b.boot_sd_sum at 100 / 1,000 / 10,000 levels (B = 400), raw and drift-removed.

Comparison rule (declared before any baseline number exists): per bin and window length L, growth g = SD(10,000)/SD(100),
drift-removed. Baseline g_B = mean over GUE seeds ± SE; zeros g_Z = mean over the bin's windows ± SE.
  - The zeros' shrinkage is DISTINGUISHED from the sine-kernel baseline in a bin iff g_Z < g_B − 3·√(SE_B² + SE_Z²).
  - "Candidate finding" (Will's wording) iff distinguished in ≥ 4 of 5 bins at L = 10⁶.
  - Flatness of the baseline is reported (|g_B − 1| with SE) but the decision is the difference at matched L, because
    the moving-block estimator's own finite-n behaviour is shared by both arms.
Sanity per GUE sequence: unfolded count residual, mean spacing, ⟨r̃⟩ (large-N GUE 0.5996).

  python longbase.py gue SEED L OUT         (spot; one sequence, mapped into all five bins)
  python longbase.py zeros NAME L OUT       (local; the bin's Platt file — read is done, so decoding is allowed)
  python longbase.py merge OUT
"""
import glob
import json
import math
import os
import sys

import numpy as np
from scipy.linalg import eigh_tridiagonal

import g0b as G
import r2prep as P
import r2run as RR

PRIMARY = (0.5, 0.3)
SEED0 = 20261010


def growth_record(levels, name):
    g = P.geometry(name)
    u, w = PRIMARY
    c = G.contributions(levels, u, w, g["delta"])
    cd = RR.drift_removed(c, levels, name, u, w)
    rng = np.random.default_rng(SEED0 + int(name[1:]))
    raw = {str(b): G.boot_sd_sum(c, b, rng) for b in G.BOOT_LEVELS}
    dr = {str(b): G.boot_sd_sum(cd, b, rng) for b in G.BOOT_LEVELS}
    return dict(n=int(len(levels)), boot_sd_raw=raw, boot_sd_drift_removed=dr,
                growth_raw=[raw[str(b)] / raw["100"] for b in G.BOOT_LEVELS],
                growth_drift_removed=[dr[str(b)] / dr["100"] for b in G.BOOT_LEVELS])


def semicircle_count(x, n, R):
    x = np.clip(x, -R, R)
    return n * (0.5 + (x * np.sqrt(R * R - x * x) + R * R * np.arcsin(x / R)) / (math.pi * R * R))


def gue(seed, L, out):
    n = int(math.ceil(1.06 * L))
    rng = np.random.default_rng(SEED0 * 1000 + seed)
    d = math.sqrt(2.0) * rng.standard_normal(n)
    b = np.sqrt(rng.chisquare(2 * np.arange(n - 1, 0, -1)))
    ev = np.sort(eigh_tridiagonal(d, b, eigvals_only=True, lapack_driver="sterf"))
    i0 = (n - L) // 2
    x = ev[i0:i0 + L]
    R = math.sqrt(8.0 * n)
    u = semicircle_count(x, n, R)
    resid = (u - (i0 + 0.5 + np.arange(L)))                 # unfolded count vs index: O(1) if the unfolding is right
    s = np.diff(u)
    rt = float((np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])).mean())
    rec = dict(seed=seed, L=L, n_mat=n, sanity=dict(count_resid_mean=float(resid.mean()), count_resid_sd=float(resid.std()),
                                                    count_resid_drift=float(resid[-1000:].mean() - resid[:1000].mean()),
                                                    mean_spacing=float(s.mean()), rtilde=rt), bins={})
    u = u - u[0]
    for name in P.BINS:
        g = P.geometry(name)
        t = G.nbar_inv(float(P.nbar(g["t0"])) + 0.5 + u, g["tc"])
        rec["bins"][name] = growth_record(t, name)
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, f"gue_L{L}_s{seed:03d}.json"), "w"), indent=1)
    print("gue", seed, L, rec["sanity"], {k: [round(x, 3) for x in v["growth_drift_removed"]] for k, v in rec["bins"].items()},
          flush=True)


def zeros(name, L, out):
    lev = RR.read_platt_heights(os.path.join(RR.HERE, "data", "platt", RR.PLATT[name]))
    recs = []
    for k in range(len(lev) // L):
        recs.append(dict(window=k, **growth_record(lev[k * L:(k + 1) * L], name)))
    os.makedirs(out, exist_ok=True)
    json.dump(recs, open(os.path.join(out, f"zeros_{name}_L{L}.json"), "w"), indent=1)
    print("zeros", name, L, len(recs), "windows; drift-removed growth at 10,000:",
          [round(r["growth_drift_removed"][-1], 3) for r in recs], flush=True)


def ms(v):
    v = np.asarray(v, float)
    return float(v.mean()), float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else float("nan")


def merge(out):
    res = {}
    for L in sorted({int(f.split("_L")[1].split("_")[0].split(".")[0]) for f in glob.glob(os.path.join(out, "*_L*.json"))}):
        G_ = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(out, f"gue_L{L}_s*.json")))]
        rowL = dict(n_gue_seeds=len(G_), gue_sanity=[g["sanity"] for g in G_], bins={})
        for name in P.BINS:
            zf = os.path.join(out, f"zeros_{name}_L{L}.json")
            if not G_ or not os.path.exists(zf):
                continue
            Z = json.load(open(zf))
            gB = ms([g["bins"][name]["growth_drift_removed"][-1] for g in G_])
            gZ = ms([z["growth_drift_removed"][-1] for z in Z])
            gBr = ms([g["bins"][name]["growth_raw"][-1] for g in G_])
            gZr = ms([z["growth_raw"][-1] for z in Z])
            thr = gB[0] - 3 * math.sqrt(gB[1] ** 2 + gZ[1] ** 2)
            rowL["bins"][name] = dict(gue_drift_removed=gB, zeros_drift_removed=gZ, gue_raw=gBr, zeros_raw=gZr,
                                      n_zero_windows=len(Z), threshold=thr, DISTINGUISHED=bool(gZ[0] < thr),
                                      separation_in_combined_se=(gB[0] - gZ[0]) / math.sqrt(gB[1] ** 2 + gZ[1] ** 2))
        nd = sum(v["DISTINGUISHED"] for v in rowL["bins"].values())
        rowL["n_distinguished"] = nd
        rowL["CANDIDATE_FINDING"] = bool(L == 1_000_000 and nd >= 4)
        res[str(L)] = rowL
        for name, v in rowL["bins"].items():
            print(L, name, "GUE %.3f±%.3f  zeros %.3f±%.3f (%d windows)  sep %.1f SE  %s" % (
                *v["gue_drift_removed"], *v["zeros_drift_removed"], v["n_zero_windows"], v["separation_in_combined_se"],
                "DISTINGUISHED" if v["DISTINGUISHED"] else "-"))
        print(L, "distinguished in", nd, "of", len(rowL["bins"]), "| candidate finding:", rowL["CANDIDATE_FINDING"])
    json.dump(res, open(os.path.join(out, "longbase_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "gue":
        gue(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == "zeros":
        zeros(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    elif cmd == "merge":
        merge(sys.argv[1 + 1])

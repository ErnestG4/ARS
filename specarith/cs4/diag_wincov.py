"""Stage 2 seal condition (twenty-third round), estimator side: the PREDICTED covariance between tapered windows at
the estimator's spacing. ph2s2/tapered.py takes the sample variance of S(c; b) over centres 3b apart, centred on the
file mean, so with n windows
  E[s²] = V(b) − (2/(n(n−1))) Σ_{k≥1} (n − k) Cov(3bk) + b²·s²_c(μ(ℓ_c)),
and v̂ = s²/b. Cov(R) = ∫ (W⋆W)(r − R) C(r) dr, i.e. Cov(R)/b = (1/√2) ∫_ℝ exp(−π(r − R)²/2b²) C(r) dr, from the same
stored per-pair C as v(b) (gs_zeta.py pairs: c_short = full C × χ-part on r < 20, c_non = non-oscillating C on the
long grid r = 5 … 4.8·10⁴; the ℓ-oscillating long part is dropped as in the prediction, amendment 7).
Only lags whose Gaussian lies inside the stored grid to 5 standard deviations (R + 5b/√π ≤ 4.8·10⁴) are used: C is
almost periodic with RMS ~0.05 and no decay (diag_wincov_edge.py), so a Gaussian cut at the grid end stops cancelling
(a cut at 1.75σ gave a spurious ρ = −0.22). Nothing is extrapolated; b = 10⁴ has no usable lag.

  python diag_wincov.py ELL OUT       (reads results/gs_zeta/L{ELL}/pairs/*.npz and gs_zeta_L{ELL}.json)
"""
import json
import math
import os
import sys

import numpy as np
from scipy.special import erf

import gs_unitary as G
import gs_zeta as Z

KMAX = 200
# F2 files' height ranges (ph2r2/FRESH_SETS_F1_F3.md), for the window count n per rung
T_RANGE = {"15.7502": (42_446_000, 44_546_000), "16.4972": (90_746_000, 92_846_000), "17.2491": (193_646_000, 195_746_000),
           "19.5003": (1_848_446_000, 1_850_546_000), "21.75": (17_541_746_000, 17_543_846_000)}


def nbar(t):
    return t / (2 * math.pi) * math.log(t / (2 * math.pi * math.e)) + 7 / 8


def n_windows(ell, b):
    """As ph2s2/tapered.py: centres arange(lo + 4σ, hi − 4σ, 3b), σ = b/√(2π), over the file's unfolded range."""
    t0, t1 = T_RANGE[ell]
    lo, hi = nbar(t0), nbar(t1)
    sig = b / math.sqrt(2 * math.pi)
    return len(np.arange(lo + 4 * sig, hi - 4 * sig, 3 * b))


def main(ell, out):
    d = os.path.join("results", "gs_zeta", f"L{ell}", "pairs")
    rs, rl = Z.short_grid(), Z.long_grid()
    cs_, cl_ = G.chi(rs), 1 - G.chi(rl)
    Cs, Cl = np.zeros(len(rs)), np.zeros(len(rl))
    for (i, j) in Z.PAIRS:
        z = np.load(os.path.join(d, f"p{i:02d}_{j:02d}.npz"))
        wgt = 4 * Z.DW[i] * Z.FD[i] * Z.DW[j] * Z.FD[j] * (1 if i == j else 2)
        Cs += wgt * cs_ * z["c_short"]
        Cl += wgt * cl_ * z["c_non"]
    res = json.load(open(os.path.join("results", "gs_zeta", f"gs_zeta_L{ell}.json")))
    v = res["v"]
    rmax = rl[-1]
    out_d = {}
    for b in Z.LADDER:
        g = lambda x: np.exp(-math.pi * x ** 2 / (2 * b * b))
        s = b / math.sqrt(math.pi)
        i4 = Z.DR_S * np.sum(2 * g(rs) * Cs) + Z.DR_L * np.sum(2 * g(rl) * Cl)
        check = i4 - (res["I4_short"][str(b)] + res["I4_long"][str(b)])
        lags = []
        for k in range(1, KMAX + 1):
            R = 3 * b * k
            if R + 5 * s > rmax:                 # only lags whose Gaussian lies wholly inside the stored grid: C is
                break                            # almost periodic (RMS ~0.05, no decay), so a cut Gaussian leaks
            cov = (Z.DR_S * np.sum((g(rs - R) + g(rs + R)) * Cs) + Z.DR_L * np.sum((g(rl - R) + g(rl + R)) * Cl)) / math.sqrt(2)
            inside = 0.5 * (1 + erf((rmax - R) / (s * math.sqrt(2))))
            lags.append(dict(k=k, R=R, cov_over_b=float(cov), rho=float(cov / v[str(b)]), mass_inside=float(inside)))
        n = n_windows(ell, b)
        rho = np.array([L["rho"] for L in lags])
        ks = np.arange(1, len(rho) + 1)
        part = np.cumsum((1 - ks / n) * rho)              # Σ_{k ≤ K} (1 − k/n) ρ_k
        # E[s²]/V = 1 − (2/(n − 1)) Σ_{k=1}^{n−1} (1 − k/n) ρ_k  (centring); lags beyond K_avail are not available
        out_d[b] = dict(v=v[str(b)], i4_recheck=float(check), n_windows=n, lags=lags, partial_sums=part.tolist(),
                        centring_partial=float(-2 / (n - 1) * part[-1]) if len(part) else None,
                        diff_factor=float(1 - rho[0]) if len(rho) else None)
        Ks = [K for K in (1, 2, 4, 8, 16, 32, 64, 128, 200) if K <= len(part)]
        print("ℓ=%s b=%5d n=%5d K_avail=%3d  I4 recheck %+.1e  ρ_1..4 %s | Σ_{k≤K}(1−k/n)ρ_k: %s | centring(K_avail) %s"
              % (ell, b, n, len(part), check, " ".join("%+.4f" % x for x in rho[:4]),
                 " ".join("K%d:%+.3f" % (K, part[K - 1]) for K in Ks),
                 "%+.1e" % out_d[b]["centring_partial"] if len(part) else "-"), flush=True)
    os.makedirs(out, exist_ok=True)
    json.dump(out_d, open(os.path.join(out, f"wincov_L{ell}.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

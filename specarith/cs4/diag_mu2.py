"""Stage 2 seal condition (Will, twenty-third round): the height-dependence of the two-point MEAN of the tapered
statistic across each F2 file. With x unfolded by the exact N̄ (unit density), E S(c; b) = b·μ(ℓ_c),
  μ(ℓ) = ∫ F(d) ρ₂(d; ℓ) dd = 2 ∫₀^{U_MAX} F ρ₂,
ρ₂ from CS08 (cs4fast.FastZeta.R2, prime cutoff 3·10⁵), F the primary bump (0.5, 0.3), U_MAX = 3 as in ph2s2/tapered.py.
Windows spread over the file add b²·Var_c μ(ℓ_c) to the window-sum variance, i.e. b·Var_c μ to v(b).

Per F2 file: μ at 64 stratified ℓ (midpoints, weights ∝ ℓe^ℓ = zero density in ℓ) across the file's ℓ range, a weighted
quadratic fit in ℓ (the smooth part) and its residual (any oscillating part), and two dense pockets at the file
midpoint (16 ℓ spaced 1e-6 and 16 spaced 1e-4) so an oscillation faster than the 64-point grid cannot hide by aliasing.
  (i)  smooth:      T_s(b) = b·Var_w μ_fit / v(b)
  (ii) oscillating: T_o(b) = b·Var_w (μ − μ_fit) / v(b), and b·(pocket spread)²/v(b)
v(b) from results/gs_zeta/gs_zeta_L{ELL}.json.

  python diag_mu2.py FILE_IDX OUT       one F2 file (0..4) -> OUT/mu2_F2_{idx}.json
  python diag_mu2.py summary OUT
"""
import glob
import json
import math
import os
import sys

import numpy as np

import cs4fast as F
import gs_zeta as Z

U, W, U_MAX = 0.5, 0.3, 3.0
# F2 files (ph2r2/FRESH_SETS_F1_F3.md): ℓ range and the mean ℓ used by gs_zeta
FILES = ((15.7259, 15.7742, 15.7502), (16.4857, 16.5086, 16.4972), (17.2437, 17.2545, 17.2491),
         (19.4997, 19.5009, 19.5003), (21.7500, 21.7501, 21.75))
NG = 80
XG, WG = np.polynomial.legendre.leggauss(NG)
DG, DWG = 0.5 * U_MAX * (XG + 1), 0.5 * U_MAX * WG


def Fb(d):
    return np.exp(-(d - U) ** 2 / (2 * W * W)) + np.exp(-(d + U) ** 2 / (2 * W * W))


def mu(ell):
    fz = F.FastZeta(Z.tval(ell), pmax=Z.PMAX)
    r2 = np.array([fz.R2(float(d)).real for d in DG])
    return 2 * float(np.sum(DWG * Fb(DG) * r2))


def grid(lo, hi, n=64):
    ells = np.array([lo + (k + 0.5) * (hi - lo) / n for k in range(n)])
    w = ells * np.exp(ells)
    return ells, w / w.sum()


def run(idx, out):
    lo, hi, ell0 = FILES[idx]
    ells, w = grid(lo, hi)
    mid = 0.5 * (lo + hi)
    p6 = mid + 1e-6 * (np.arange(16) - 7.5)
    p4 = mid + 1e-4 * (np.arange(16) - 7.5) if hi - lo > 2e-3 else None
    res = dict(file=idx, ell_range=[lo, hi], ell0=ell0, ells=ells.tolist(), w=w.tolist(),
               mu=[mu(l) for l in ells], pocket6=dict(ells=p6.tolist(), mu=[mu(l) for l in p6]))
    if p4 is not None:
        res["pocket4"] = dict(ells=p4.tolist(), mu=[mu(l) for l in p4])
    res["mu_ell0"] = mu(ell0)
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, f"mu2_F2_{idx}.json"), "w"), indent=1)
    print(idx, "done", flush=True)


def wvar(x, w):
    m = np.dot(w, x)
    return float(np.dot(w, (x - m) ** 2))


def summary(out):
    rows = {}
    for f in sorted(glob.glob(os.path.join(out, "mu2_F2_*.json"))):
        r = json.load(open(f))
        ells, w, m = np.array(r["ells"]), np.array(r["w"]), np.array(r["mu"])
        v = json.load(open(os.path.join(os.path.dirname(out.rstrip("/")), "gs_zeta", f"gs_zeta_L{r['ell0']}.json")))["v"]
        u = ells - r["ell0"]
        X = np.vander(u, 3)
        sw = np.sqrt(w)
        beta = np.linalg.lstsq(X * sw[:, None], m * sw, rcond=None)[0]
        fit = X @ beta
        res = m - fit
        sp6 = float(np.ptp(r["pocket6"]["mu"]))
        sp4 = float(np.ptp(r["pocket4"]["mu"])) if "pocket4" in r else None
        out_r = dict(ell0=r["ell0"], mu_ell0=r["mu_ell0"], mu_wavg=float(np.dot(w, m)), dmu_dell=float(beta[1]),
                     d2mu=float(2 * beta[0]), resid_rms=math.sqrt(float(np.dot(w, res ** 2))),
                     resid_max=float(np.abs(res).max()), pocket6_spread=sp6, pocket4_spread=sp4,
                     var_smooth=wvar(fit, w), var_resid=wvar(res, w))
        for b in Z.LADDER:
            vb = v[str(b)]
            out_r[f"T_smooth_b{b}"] = b * out_r["var_smooth"] / vb
            out_r[f"T_osc_b{b}"] = b * out_r["var_resid"] / vb
            out_r[f"T_pocket_b{b}"] = b * max(sp6, sp4 or 0.0) ** 2 / vb
        rows[r["ell0"]] = out_r
        print("ℓ=%-8s μ=%.9f dμ/dℓ=%+.3e d²μ=%+.2e | resid rms %.1e max %.1e | pockets %.1e %s | b=1e4: T_s %.1e  T_o %.1e"
              " T_pocket %.1e" % (r["ell0"], out_r["mu_wavg"], out_r["dmu_dell"], out_r["d2mu"], out_r["resid_rms"],
                                  out_r["resid_max"], sp6, "%.1e" % sp4 if sp4 is not None else "-",
                                  out_r["T_smooth_b10000"], out_r["T_osc_b10000"], out_r["T_pocket_b10000"]))
    json.dump(rows, open(os.path.join(out, "summary.json"), "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "summary":
        summary(sys.argv[2])
    else:
        run(int(sys.argv[1]), sys.argv[2])

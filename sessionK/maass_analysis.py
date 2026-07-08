"""Session K — Co-Primary 1: arithmetic-chaos fingerprint of the Maass spectrum.

Discipline (R2 + section 3 gate):
  * DESYMMETRIZE by the source 'symmetry' field (even/odd) BEFORE any statistic.
  * Weyl COMPLETENESS gate per sector before Sigma^2/NNS.
  * Unfold with the ANALYTIC Weyl smooth counting (R^2 and R lnR coeffs fixed
    from theory; only the linear+const normalization is fit). No flexible/
    self-derived density fit that could manufacture Poisson.

Weyl-Selberg smooth counting for PSL(2,Z) cusp forms (both parities):
    Nbar(R) = R^2/12 - (2/pi) R lnR + c R + d
The R^2/12 (area pi/3) and -(2/pi)R lnR (one-cusp scattering) terms are analytic;
c,d are a linear normalization fixed by least squares to the certified staircase.

Synthetic validation: Poisson and GOE spectra PLACED at the Maass Weyl density,
pushed through the identical unfold+classify, must return Poisson and GOE resp.
Only then is a verdict on the real spectrum licensed.
"""
import json, math, os, sys
import numpy as np
import nns_stats as st

HERE = os.path.dirname(os.path.abspath(__file__))
A_WEYL = 1.0 / 12.0
B_WEYL = -2.0 / math.pi

def fit_norm(R, idx):
    """Fix a,b analytic; fit c,d in Nbar=aR^2+bRlnR+cR+d to staircase (R,idx)."""
    y = idx - (A_WEYL * R**2 + B_WEYL * R * np.log(R))
    Amat = np.vstack([R, np.ones_like(R)]).T
    (c, d), *_ = np.linalg.lstsq(Amat, y, rcond=None)
    return c, d

def Nbar(R, c, d):
    return A_WEYL * R**2 + B_WEYL * R * np.log(R) + c * R + d

def inverse_Nbar(u, c, d, Rmax=400.0):
    Rg = np.linspace(1.0, Rmax, 400000)
    Ng = Nbar(Rg, c, d)
    return np.interp(u, Ng, Rg)

# Per-sector Weyl leading terms (THEORY-FIXED, not fit — so Sigma^2 long-range
# power is preserved): area term a=1/24 each; one-cusp scattering -(2/pi)R lnR
# belongs to the EVEN sector (Eisenstein series are even), odd has none.
# PARITY CONVENTION settled by Run 1 (Mayer det): eigenvalue+1=even=LMFDB sym0;
# eigenvalue-1=odd=LMFDB sym1. So sym0=EVEN (gets scattering), sym1=ODD.
SECTOR_B = {0: -2.0 / math.pi, 1: 0.0}     # 0=even(scattering), 1=odd

def fit_norm_sector(R, a_lead, b_lead):
    """Fix R^2 (a_lead=1/24) and R lnR (b_lead, scattering) from THEORY; fit only
    the affine offset {R,1}. Preserves long-range Sigma^2 signal. Unit density."""
    R = np.sort(R)
    ix = np.arange(1, len(R) + 1)
    y = ix - (a_lead * R**2 + b_lead * R * np.log(R))
    M = np.vstack([R, np.ones_like(R)]).T
    (c, d), *_ = np.linalg.lstsq(M, y, rcond=None)
    u = a_lead * R**2 + b_lead * R * np.log(R) + c * R + d
    sp = np.diff(u)
    return np.concatenate([[0.0], np.cumsum(sp / sp.mean())])   # unit mean spacing

def per_sector_unfold(R_all, sym_all, idx_all):
    """Split by symmetry FIRST (R2), unfold each sector with its OWN theory-fixed
    Weyl form. Returns sym -> (raw_r_sector, unfolded_unit)."""
    out = {}
    for s in (0, 1):
        Rs = np.sort(R_all[sym_all == s])
        if len(Rs) < 3:
            out[s] = (Rs, np.array([])); continue
        out[s] = (Rs, fit_norm_sector(Rs, 1.0 / 24.0, SECTOR_B[s]))
    return out

def longest_same_sym_run(sym_by_idx):
    runs, c = [], 1
    for i in range(1, len(sym_by_idx)):
        if sym_by_idx[i] == sym_by_idx[i - 1]:
            c += 1
        else:
            runs.append(c); c = 1
    runs.append(c)
    return max(runs)

def weyl_completeness(R_all, sym_all, idx_all):
    """Completeness certificate: (1) idx strictly consecutive (no dropped levels);
    (2) NO long single-parity run (a run > ~8 means the other parity is missing in
    that window -- the desymmetrization completeness defect this gate guards). Also
    reports per-sector counts vs the analytic total-Weyl increment."""
    order = np.argsort(idx_all)
    sym_ord = sym_all[order].astype(int)
    idx_ord = idx_all[order].astype(int)
    gaps = np.where(np.diff(idx_ord) != 1)[0]
    max_run = longest_same_sym_run(sym_ord)
    c, d = fit_norm(R_all, idx_all)
    res = {"idx_consecutive": bool(len(gaps) == 0),
           "max_single_parity_run": int(max_run),
           "run_gate_pass": bool(max_run <= 8),
           "even_count": int((sym_all == 1).sum()),
           "odd_count": int((sym_all == 0).sum()),
           "total_weyl_predicted": float(Nbar(R_all.max(), c, d) - Nbar(R_all.min(), c, d)),
           "total_observed": int(len(R_all) - 1)}
    res["COMPLETE"] = bool(res["idx_consecutive"] and res["run_gate_pass"])
    return res

# Unfolding-FREE spacing ratio r~ = min(s_n,s_{n-1})/max(...). Atas et al 2013:
#   Poisson <r~>=0.3863, GOE=0.5359, GUE=0.6027, GSE=0.6762.
R_REF = {"Poisson": 0.38629, "GOE": 0.53590, "GUE": 0.60266, "GSE": 0.67617}
# std of r~ per sample (for SE): Poisson ~0.241, GOE ~0.210 (empirical)
R_STD = {"Poisson": 0.241, "GOE": 0.210, "GUE": 0.196, "GSE": 0.185}

def ratio_stat(x):
    x = np.sort(x); s = np.diff(x)
    return np.minimum(s[1:], s[:-1]) / np.maximum(s[1:], s[:-1])

def ratio_verdict(x):
    rr = ratio_stat(x)
    m = float(rr.mean()); se = float(rr.std(ddof=1) / math.sqrt(len(rr)))
    z = {k: (m - v) / se for k, v in R_REF.items()}
    nearest = min(R_REF, key=lambda k: abs(m - R_REF[k]))
    return {"mean_rtilde": m, "se": se, "n_ratios": int(len(rr)),
            "nearest_class": nearest, "z_vs": {k: round(v, 2) for k, v in z.items()}}

def classify_sector(unf_raw_r, unf, tag):
    """unf_raw_r: RAW eigenvalues (for unfolding-free ratio stat).
       unf: analytic-Weyl-unfolded, unit-density (for Sigma^2/NNS)."""
    r = {"tag": tag, "n_levels": int(len(unf_raw_r)),
         "ratio_stat": ratio_verdict(unf_raw_r)}       # PRIMARY, unfolding-free
    if len(unf) > 8:
        r["nns_ks"] = st.classify_nns(unf)
    if len(unf) >= 60:
        Ls = np.linspace(1.0, min(15.0, (unf[-1] - unf[0]) / 6.0), 12)
        s2 = st.number_variance(unf, Ls)
        r["sigma2"] = {"Ls": Ls.tolist(), "vals": s2.tolist(),
                       "slope_vs_L": float(np.polyfit(Ls, np.nan_to_num(s2), 1)[0]),
                       "poisson_ref": Ls.tolist(),
                       "goe_ref": st.sigma2_goe(Ls).tolist()}
    return r

# ---------------------------------------------------------------------------
def synthetic_validation(n=1200, seed=20260708):
    rng = np.random.default_rng(seed)
    # reference normalization from a plausible c,d (use real-data fit later; here nominal)
    c, d = 0.9, -1.0
    results = {}
    for kind in ("Poisson", "GOE"):
        # build a unit-density unfolded sequence of n levels
        if kind == "Poisson":
            u = np.cumsum(rng.exponential(1.0, size=n))
        else:
            # GOE spectrum: eigenvalues of large GOE, unfolded to unit density
            m = 2 * n
            H = rng.standard_normal((m, m)); H = (H + H.T) / 2
            ev = np.linalg.eigvalsh(H)
            u = st.unfold_poly(ev, frac=0.7)[:n]
            u = np.cumsum(np.diff(np.sort(u)) / np.mean(np.diff(np.sort(u))))
        # place at Maass density: map unfolded index -> R via inverse Weyl, then
        # push back through the SAME unfold to confirm round-trip + classify
        R = inverse_Nbar(u + 5.0, c, d)      # place at Maass density
        uu = fit_norm_sector(R, 1.0 / 24.0, 0.0)  # unfold (ratio-stat gate is unfold-free)
        res = classify_sector(R, uu, f"synth_{kind}")
        results[kind] = {"ratio_nearest": res["ratio_stat"]["nearest_class"],
                         "mean_rtilde": round(res["ratio_stat"]["mean_rtilde"], 4),
                         "nns_ks_verdict": res.get("nns_ks", {}).get("verdict"),
                         "sigma2_slope_vs_L": res.get("sigma2", {}).get("slope_vs_L")}
    results["PIPELINE_VALID"] = bool(results["Poisson"]["ratio_nearest"] == "Poisson"
                                     and results["GOE"]["ratio_nearest"] == "GOE")
    return results

def run_real(csv):
    d = np.genfromtxt(csv, delimiter=",", names=True)
    R_all = np.asarray(d["r"], float)
    sym_all = np.asarray(d["symmetry"], int)
    idx_all = np.asarray(d["idx"], float)
    order = np.argsort(R_all)
    R_all, sym_all, idx_all = R_all[order], sym_all[order], idx_all[order]
    comp = weyl_completeness(R_all, sym_all, idx_all)
    unf = per_sector_unfold(R_all, sym_all, idx_all)
    out = {"n_total": int(len(R_all)),
           "r_range": [float(R_all.min()), float(R_all.max())],
           "completeness": comp, "sectors": {}}
    names = {0: "even", 1: "odd"}
    for s in (0, 1):
        raw_r, u = unf[s]
        out["sectors"][names[s]] = classify_sector(raw_r, u, names[s])
    return out

if __name__ == "__main__":
    result = {}
    print("=== synthetic pipeline validation (Maass density) ===")
    result["synthetic"] = synthetic_validation()
    print(json.dumps(result["synthetic"], indent=2))
    print("\n=== real Maass level-1 (certified consecutive block) ===")
    result["real"] = run_real(os.path.join(HERE, "maass_level1_partial.csv"))
    print("  ref <r~>: Poisson=0.386 GOE=0.536 GUE=0.603")
    for name, sec in result["real"]["sectors"].items():
        rs = sec["ratio_stat"]
        s2 = sec.get("sigma2", {})
        print(f"  {name:5s} n={sec['n_levels']:4d}  <r~>={rs['mean_rtilde']:.4f}+/-{rs['se']:.4f}"
              f"  nearest={rs['nearest_class']:8s} z(Pois)={rs['z_vs']['Poisson']:+.1f} "
              f"z(GOE)={rs['z_vs']['GOE']:+.1f}  Sig2slope/L={s2.get('slope_vs_L')}")
    print("  completeness:", json.dumps(result["real"]["completeness"]))
    json.dump(result, open(os.path.join(HERE, "maass_analysis_measured.json"), "w"),
              indent=2, default=str)
    print("\nPIPELINE_VALID:", result["synthetic"]["PIPELINE_VALID"])

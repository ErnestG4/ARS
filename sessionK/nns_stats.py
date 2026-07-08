"""Session K shared statistics: number variance Sigma^2(L), spectral rigidity
Delta_3(L), analytic references (Poisson/GOE/GUE/GSE), and a blind class
classifier that can REFUSE ('not an ensemble')."""
import math
import numpy as np

EULER_GAMMA = 0.5772156649015329

# ---- analytic long-range references (large-L asymptotics) -------------------
def sigma2_poisson(L):
    return np.asarray(L, float)

def sigma2_gue(L):
    L = np.asarray(L, float)
    return (1.0 / math.pi**2) * (np.log(2 * math.pi * L) + EULER_GAMMA + 1.0)

def sigma2_goe(L):
    L = np.asarray(L, float)
    return (2.0 / math.pi**2) * (np.log(2 * math.pi * L) + EULER_GAMMA + 1.0 - math.pi**2 / 8.0)

def sigma2_gse(L):
    L = np.asarray(L, float)
    return (1.0 / (2 * math.pi**2)) * (np.log(4 * math.pi * L) + EULER_GAMMA + 1.0 + math.pi**2 / 8.0)

def delta3_poisson(L):
    return np.asarray(L, float) / 15.0

def delta3_gue(L):
    L = np.asarray(L, float)
    return (1.0 / (2 * math.pi**2)) * (np.log(2 * math.pi * L) + EULER_GAMMA - 5.0/4.0 - math.pi**2/8.0)

def delta3_goe(L):
    L = np.asarray(L, float)
    return (1.0 / math.pi**2) * (np.log(2 * math.pi * L) + EULER_GAMMA - 5.0/4.0 - math.pi**2/8.0)

def delta3_gse(L):
    L = np.asarray(L, float)
    return (1.0 / (4 * math.pi**2)) * (np.log(4 * math.pi * L) + EULER_GAMMA - 5.0/4.0 + math.pi**2/8.0)

# ---- estimators on an unfolded spectrum (mean spacing 1) --------------------
def number_variance(unf, Ls, n_origins=400):
    """Sigma^2(L): variance of count in windows of width L, averaged over origins."""
    unf = np.sort(np.asarray(unf, float))
    lo, hi = unf[0], unf[-1]
    out = np.full(len(Ls), np.nan)
    for i, L in enumerate(Ls):
        if hi - lo < 3 * L:
            continue
        origins = np.linspace(lo, hi - L, n_origins)
        counts = np.array([np.searchsorted(unf, o + L) - np.searchsorted(unf, o)
                           for o in origins], float)
        out[i] = counts.var(ddof=1)
    return out

def delta3(unf, Ls, n_origins=200):
    """Dyson-Mehta spectral rigidity: min over (a,b) of mean-square deviation of
    the staircase N(x) from a+bx over a window of width L, averaged over origins."""
    unf = np.sort(np.asarray(unf, float))
    lo, hi = unf[0], unf[-1]
    out = np.full(len(Ls), np.nan)
    for i, L in enumerate(Ls):
        if hi - lo < 3 * L:
            continue
        origins = np.linspace(lo, hi - L, n_origins)
        vals = []
        for o in origins:
            # staircase over [o, o+L]; least-squares line fit; mean-square residual
            idx0 = np.searchsorted(unf, o)
            idx1 = np.searchsorted(unf, o + L)
            pts = unf[idx0:idx1]
            # N(x) = number of levels <= x within window, x in [o,o+L]
            # analytic least squares of step function vs a+b x on [o,o+L]
            xs = np.linspace(o, o + L, 400)
            Nx = np.searchsorted(unf, xs, side="right") - idx0
            A = np.vstack([np.ones_like(xs), xs - o]).T
            coef, *_ = np.linalg.lstsq(A, Nx, rcond=None)
            resid = Nx - A @ coef
            vals.append(np.mean(resid**2))
        out[i] = np.mean(vals)
    return out

REFS = {
    "Poisson": (sigma2_poisson, delta3_poisson),
    "GOE": (sigma2_goe, delta3_goe),
    "GUE": (sigma2_gue, delta3_gue),
    "GSE": (sigma2_gse, delta3_gse),
}

def unfold_poly(eigs, deg=12, frac=0.7):
    """Standard RMT local unfolding: smooth polynomial fit of the staircase.
    Returns the bulk-unfolded spectrum (mean spacing ~1)."""
    lam = np.sort(np.asarray(eigs, float))
    n = len(lam)
    idx = np.arange(1, n + 1)
    lo = int(n * (1 - frac) / 2); hi = n - lo
    lam_b, idx_b = lam[lo:hi], idx[lo:hi]
    c = np.polyfit(lam_b, idx_b, deg)
    return np.polyval(c, lam_b)

# ---- short-range NNS surmise CDFs (do NOT saturate; robust GUE/GOE marker) --
def _nns_pdf(name, s):
    s = np.asarray(s, float)
    if name == "Poisson":
        return np.exp(-s)
    if name == "GOE":
        return (math.pi / 2) * s * np.exp(-math.pi * s**2 / 4)
    if name == "GUE":
        return (32 / math.pi**2) * s**2 * np.exp(-4 * s**2 / math.pi)
    if name == "GSE":
        return (2**18 / (3**6 * math.pi**3)) * s**4 * np.exp(-64 * s**2 / (9 * math.pi))
    raise ValueError(name)

def _surmise_cdf(name, sgrid):
    pdf = _nns_pdf(name, sgrid)
    cdf = np.concatenate([[0.0], np.cumsum((pdf[1:] + pdf[:-1]) / 2 * np.diff(sgrid))])
    return cdf / cdf[-1]

def classify_nns(unf, classes=("Poisson", "GOE", "GUE", "GSE")):
    """KS distance of the empirical spacing CDF to each surmise. Short-range;
    immune to the long-range (Berry) saturation that biases Sigma^2 on zeta."""
    s = np.diff(np.sort(np.asarray(unf, float)))
    s = s[np.isfinite(s)]
    s = s / s.mean()
    ss = np.sort(s)
    emp = np.arange(1, len(ss) + 1) / len(ss)
    sgrid = np.linspace(0, max(6.0, ss[-1]), 4000)
    ks = {}
    for name in classes:
        cdf = _surmise_cdf(name, sgrid)
        theo = np.interp(ss, sgrid, cdf)
        ks[name] = float(np.max(np.abs(emp - theo)))
    best = min(ks, key=ks.get)
    return {"verdict": best, "ks": ks, "n_spacings": int(len(s))}

def build_empirical_refs(generators, Ls, n_real=6):
    """generators: dict name -> callable()->unfolded spectrum. Returns
    name -> {'sigma2': mean curve, 'delta3': mean curve} over n_real draws."""
    refs = {}
    for name, gen in generators.items():
        s2s, d3s = [], []
        for _ in range(n_real):
            u = gen()
            s2s.append(number_variance(u, Ls))
            d3s.append(delta3(u, Ls))
        refs[name] = {"sigma2": np.nanmean(s2s, axis=0),
                      "delta3": np.nanmean(d3s, axis=0)}
    return refs

def classify_empirical(unf, refs, Ls, refuse_min_levels=200):
    """Classify a spectrum against empirical reference curves (same estimator)."""
    unf = np.sort(np.asarray(unf, float))
    n = len(unf)
    mean_sp = float(np.mean(np.diff(unf)))
    if n < refuse_min_levels:
        return {"verdict": "REFUSE", "reason": f"only {n} levels (<{refuse_min_levels})"}
    if not (0.7 < mean_sp < 1.4):
        return {"verdict": "REFUSE",
                "reason": f"mean spacing {mean_sp:.3f} not ~1: not a unit-density point process"}
    s2 = number_variance(unf, Ls)
    d3 = delta3(unf, Ls)
    ok = np.isfinite(s2) & np.isfinite(d3)
    scores = {}
    for name, r in refs.items():
        m = ok & np.isfinite(r["sigma2"]) & np.isfinite(r["delta3"])
        r2 = float(np.sqrt(np.nanmean((s2[m] - r["sigma2"][m])**2)))
        r3 = float(np.sqrt(np.nanmean((d3[m] - r["delta3"][m])**2)))
        scores[name] = {"rms_sigma2": r2, "rms_delta3": r3, "combined": r2 + r3}
    best = min(scores, key=lambda k: scores[k]["combined"])
    return {"verdict": best, "scores": scores, "n_levels": n, "mean_spacing": mean_sp,
            "sigma2": s2[ok].tolist(), "delta3": d3[ok].tolist(), "Ls": Ls[ok].tolist()}

def classify(unf, Lmax=None, refuse_min_levels=200):
    """Blind classifier. Returns dict with best class or REFUSE.
    Decision on Sigma^2 shape: linear (Poisson) vs logarithmic (RMT) and which RMT."""
    unf = np.sort(np.asarray(unf, float))
    n = len(unf)
    span = unf[-1] - unf[0]
    # refusal conditions: too few levels, or density not ~unit (not unfolded to a line)
    mean_sp = np.mean(np.diff(unf))
    if n < refuse_min_levels:
        return {"verdict": "REFUSE", "reason": f"only {n} levels (<{refuse_min_levels})"}
    if not (0.7 < mean_sp < 1.4):
        return {"verdict": "REFUSE",
                "reason": f"mean spacing {mean_sp:.3f} not ~1: not a unit-density point process"}
    if Lmax is None:
        Lmax = min(20.0, span / 6.0)
    Ls = np.linspace(1.0, Lmax, 14)
    s2 = number_variance(unf, Ls)
    d3 = delta3(unf, Ls)
    ok = np.isfinite(s2)
    Lf, s2f = Ls[ok], s2[ok]
    # score each reference by RMS on Sigma^2 and Delta_3
    scores = {}
    d3f = d3[ok]
    for name, (fs2, fd3) in REFS.items():
        r2 = np.sqrt(np.nanmean((s2f - fs2(Lf))**2))
        r3 = np.sqrt(np.nanmean((d3f - fd3(Lf))**2))
        scores[name] = {"rms_sigma2": float(r2), "rms_delta3": float(r3),
                        "combined": float(r2 + r3)}
    best = min(scores, key=lambda k: scores[k]["combined"])
    # linear-vs-log discriminant on Sigma^2
    b_lin = np.polyfit(Lf, s2f, 1)[0]                 # slope vs L
    b_log = np.polyfit(np.log(Lf), s2f, 1)[0]         # slope vs ln L
    return {"verdict": best, "scores": scores,
            "sigma2_slope_vs_L": float(b_lin),
            "sigma2_slope_vs_lnL": float(b_log),
            "Ls": Lf.tolist(), "sigma2": s2f.tolist(), "delta3": d3f.tolist(),
            "n_levels": int(n), "mean_spacing": float(mean_sp)}

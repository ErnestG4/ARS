"""Stage 3 local statistics -- ONE implementation used by the witnesses and the real data (STAGE3_PREREG.md).

Input: a list of spectra (singular values, any order). Per spectrum, lambda = sigma^2 sorted ascending, and
bands are taken by rank quantile q = i/n: LOWER [0.01, 0.10), BULK [0.10, 0.90), UPPER [0.90, 0.99).
  <r~>   primary: mean min(r, 1/r) over consecutive raw-lambda spacing ratios whose three levels lie in the band
         (no unfolding).
  q      secondary: Brody q (repaired fitter) on kde(4)-unfolded spacings. Each spectrum is unfolded WHOLE
         (stage2_g7.unfold "kde", c = 4); spacings whose left level lies in the band are kept; the pool is
         renormalised per spectrum to unit mean in-band. local(5) is reported alongside. A pool with > 0.1%
         non-positive spacings is REFUSED (q = None, flagged).
  Sigma^2(L), Delta_3(L), L in {1, 2, 5, 10}: BULK only, on in-band levels from a SEPARATE long-range
         unfolding kde(32) (renormalised to mean spacing 1), per spectrum (sessionK.nns_stats), then averaged over
         spectra. PRE-DATA AMENDMENT (2026-09-25, before any real Stage 3 statistic): kde(4) absorbs fluctuations
         on scales >~ 4 spacings (known answers: Poisson Sigma^2(10) = 1.2 instead of 10, Wishart 0.46 instead of
         0.91). kde(32) gives Wishart 0.87-0.88 (GOE 0.91) on both shapes, but Poisson reads ~27% low at L = 10
         (7.3). Delta_3 is insensitive to the unfolding (Poisson 0.65 vs 0.667; Wishart 0.23 vs 0.226). See
         verify_s3stats.py.
Pooling rule: spacings are formed within each spectrum; raw eigenvalues are NEVER pooled across spectra.
"""
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from cross_substrate.axes import I8_brody_q_unbounded  # noqa: E402
from sessionK.nns_stats import number_variance, delta3  # noqa: E402
import stage2_g7 as G  # noqa: E402

BANDS = {"lower": (0.01, 0.10), "bulk": (0.10, 0.90), "upper": (0.90, 0.99)}
LS = [1, 2, 5, 10]
LR_C = 32          # long-range unfolding bandwidth (x local spacing); see docstring
NONPOS_MAX = 1e-3
EST = "s3stats-v1.1"


def band_idx(n, band):
    lo, hi = BANDS[band]
    return int(np.ceil(lo * n)), int(np.ceil(hi * n))      # levels [a, b) in ascending order


def spectrum_parts(sig, band):
    lam = np.sort(np.asarray(sig, dtype=np.float64) ** 2)
    n = len(lam)
    a, b = band_idx(n, band)
    raw = np.diff(lam[a:b])
    r = raw[1:] / raw[:-1]
    rt = np.minimum(r, 1 / r) if np.all(raw > 0) else np.full(len(r), np.nan)
    out = {"rt": rt}
    for meth, par in (("kde", 4), ("local", 5)):
        if meth == "local":
            s_all = np.diff(lam)
            cs = np.concatenate([[0], np.cumsum(s_all)])
            idx = np.arange(len(s_all))
            l0 = np.maximum(idx - par, 0); h0 = np.minimum(idx + par + 1, len(s_all))
            s_all = s_all / ((cs[h0] - cs[l0]) / (h0 - l0))
            s = s_all[a:b - 1]
            u = None
        else:
            u = G.unfold(lam, meth, par)
            s = np.diff(u)[a:b - 1]
        m = s[s > 0].mean() if np.any(s > 0) else np.nan
        out[meth] = s / m
        if meth == "kde" and band == "bulk":
            ul = G.unfold(lam, "kde", LR_C)[a:b]
            lv = ul / np.diff(ul).mean()
            out["sigma2"] = number_variance(lv - lv[0], LS)
            out["delta3"] = delta3(lv - lv[0], LS)
    return out


def local_stats(spectra, band):
    parts = [spectrum_parts(s, band) for s in spectra]
    rt = np.concatenate([p["rt"] for p in parts])
    res = {"band": band, "n_spectra": len(parts), "rt": float(np.nanmean(rt)) if np.isfinite(rt).any() else None,
           "rt_nan_frac": float(np.isnan(rt).mean()), "n_ratios": int(len(rt)), "estimator_version": EST}
    for meth in ("kde", "local"):
        s = np.concatenate([p[meth] for p in parts])
        nonpos = float((s <= 0).mean())
        res[f"nonpos_{meth}"] = nonpos
        res[f"q_{meth}"] = None if nonpos > NONPOS_MAX else I8_brody_q_unbounded(s[s > 0])
        res[f"n_sp_{meth}"] = int(len(s))
    if band == "bulk":
        res["sigma2"] = np.nanmean([p["sigma2"] for p in parts], axis=0).tolist()
        res["delta3"] = np.nanmean([p["delta3"] for p in parts], axis=0).tolist()
    return res

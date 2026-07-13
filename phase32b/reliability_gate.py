"""
reliability_gate.py — the ceiling arm of TOOLKIT §9.

Admissibility gate for any ORTHOGONAL / INDEPENDENT_AXES verdict resting on an
empirical per-unit axis.

Attenuation:  r_obs = r_true * sqrt(rho_R * rho_B)   =>   R^2(R,B) <= rho(R)

Therefore a low observed R^2 is NOT evidence of a novel axis -- it is the
expected reading of an unreliable one.  For threshold tau and observed R2_obs,
true orthogonality requires

    rho(R) > R2_obs / tau

Below that the verdict is INDETERMINATE.  Disattenuation (R2_true = R2_obs/rho)
divides by a small, imprecise rho; it can KILL orthogonality but can never
CERTIFY subsumption.  Bank INDETERMINATE flat and repair the instrument.

Usage (Phase 32b p7_mean_z, the exhibit):
    python3 reliability_gate.py

Requires the MAIN venv: $HOME/fmexplorer/bin/python3
"""

import itertools

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

R2_ORTHOGONAL_CEIL = 0.20  # NOTE: Phase 27 used 0.3. Neither named a scale. See TOOLKIT §9.


def split_half_reliability(per_window, robust=True):
    """Spearman-Brown reliability of the k-window mean.

    per_window : (n_units, k) array of per-window estimates, already
                 within-group centred/scaled if the downstream regression was.
    robust     : rank-based (Spearman). Mandatory when the estimator has heavy
                 tails -- e.g. a z-score against few surrogates.

    Returns (rho_k, rbar, pairwise).
    """
    k = per_window.shape[1]
    corr = (lambda a, b: spearmanr(a, b).statistic) if robust else (
        lambda a, b: np.corrcoef(a, b)[0, 1])
    pairwise = [corr(per_window[:, i], per_window[:, j])
                for i, j in itertools.combinations(range(k), 2)]
    rbar = float(np.mean(pairwise))
    rho_k = k * rbar / (1 + (k - 1) * rbar) if rbar > 0 else float("nan")
    return rho_k, rbar, pairwise


def gate(r2_obs, rho, tau=R2_ORTHOGONAL_CEIL):
    """Return (verdict, rho_required). Never emits SUBSUMED -- see module docstring."""
    rho_required = r2_obs / tau
    if not np.isfinite(rho) or rho <= 0:
        return "INDETERMINATE (reliability not established)", rho_required
    if rho > rho_required:
        return "ORTHOGONAL (admissible)", rho_required
    # R2_true = r2_obs/rho clears tau across the plausible band -> orthogonality dies.
    # It does NOT follow that R is subsumed: the point estimate is unstable.
    return "INDETERMINATE (ORTHOGONAL fails; subsumption NOT certified)", rho_required


def noise_vs_nonstationarity(per_window, event_counts, n_quartiles=4):
    """Discriminate estimator noise from genuine within-unit nonstationarity.

    Estimator noise  => split-half rho rises monotonically with event count.
    Nonstationarity  => rho flat in event count.
    Returns (rhos_by_quartile, trend).
    """
    odd = per_window[:, ::2].mean(1)
    even = per_window[:, 1::2].mean(1)
    q = pd.qcut(pd.Series(event_counts), n_quartiles, labels=False).values
    rhos = [spearmanr(odd[q == i], even[q == i]).statistic for i in range(n_quartiles)]
    return rhos, spearmanr(range(n_quartiles), rhos).statistic


def rho_band(d, W):
    """rho is ITSELF imprecise. Report the band across defensible centering frames;
    a verdict that flips inside the band is INDETERMINATE, not the frame you liked."""
    g = d.groupby("session_id")[W]
    zc = lambda x: (x - x.mean()) / x.std(ddof=1)
    frames = {
        "raw pooled, Pearson": (d[W].values, False),
        "raw pooled, Spearman": (d[W].values, True),
        "within-session z, Pearson": (g.transform(zc).values, False),
        "within-session rank->z, Spearman": (g.rank().groupby(d.session_id).transform(zc).values, True),
        "within-session rank, Spearman": (g.rank().values, True),
    }
    return {nm: split_half_reliability(M, robust=r)[0] for nm, (M, r) in frames.items()}


if __name__ == "__main__":
    df = pd.read_parquet("../data/phase32b_results/per_cell_decomposition_merged.parquet")
    d = df[(df.p7_status == "OK") & (df.p7_n_windows_used == 5)]
    W = [f"z_w{i}" for i in range(5)]

    band = rho_band(d, W)
    for nm, r in band.items():
        print(f"  rho[{nm:34s}] = {r:.4f}")
    lo, hi = min(band.values()), max(band.values())
    print(f"\nrho band = [{lo:.3f}, {hi:.3f}]   <- denominator uncertainty, not a point")

    for r2_obs, name in [(0.113, "FA-nmo"), (0.054, "raw props")]:
        need = r2_obs / R2_ORTHOGONAL_CEIL
        v_lo, v_hi = gate(r2_obs, lo)[0], gate(r2_obs, hi)[0]
        stable = v_lo == v_hi
        print(f"\n  R2_obs={r2_obs:.3f} vs {name:10s}: need rho>{need:.3f}")
        print(f"    across band -> {v_lo if stable else 'FRAME-DEPENDENT => INDETERMINATE'}")
        if stable and "fails" in v_lo.lower():
            print(f"    R2_true in [{r2_obs/hi:.3f}, {r2_obs/lo:.3f}] -- clears tau everywhere (kill robust),")
            print(f"    but spans the SUBSUMED floor (0.50) -- subsumption NOT certifiable. Bank INDETERMINATE flat.")

    ranked = d.groupby("session_id")[W].rank().values
    rhos, trend = noise_vs_nonstationarity(ranked, d[[f"n_w{i}" for i in range(5)]].min(1).values)
    print(f"\nsplit-half rho by event quartile: {np.round(rhos, 3)}")
    print(f"trend = {trend:+.3f}   (+1 => estimator noise; ~0 => nonstationarity)")
    print("=> repair the instrument (more surrogates), do not divide by a small rho.")

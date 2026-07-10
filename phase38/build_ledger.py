"""
Phase 38 — build the reliability ledger from banked per-window axes.

Emits one row per (axis x baseline x cohort): rho, CI, frame band, R^2_obs,
rho_required, verdict.  Verdicts, in the only directions the evidence supports:

  ADMISSIBLE-ORTHOGONAL  rho_CI_lower > R2_obs/tau
  INDETERMINATE          rho fails the gate anywhere in its CI / frame band  (default)
  SUBSUMED-CERTIFIED     only if R2_obs / rho_CI_upper >= 0.50 across the whole CI

Disattenuation raises the lower bound; it cannot certify the upper (TOOLKIT §9).

B4 (cohort invariance): rho rises monotonically with event count, so trimming inflates
it.  rho is reported on the cohort its R^2 was measured on; if the axis cohort is
trimmed, R^2 is RE-MEASURED on the trimmed cohort and the gate recomputed.  Both
ledgers bank; a verdict differing between them is INDETERMINATE.
"""

import itertools
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

TAU = 0.20          # declared: applies to the DISATTENUATED (true) scale
TAU_SENS = 0.30     # Phase 27's value, carried as a sensitivity row
SUBSUMED_FLOOR = 0.50
OUT = Path(ROOT_DIR) / "data" / "phase38_results"

AXES = {
    "p7_mean_z":  [f"z_w{i}" for i in range(5)],
    "rep_med":    [f"rep_med_w{i}" for i in range(5)],
    "ks_gue_med": [f"ks_gue_med_w{i}" for i in range(5)],
}
FA_NMO = [f"fa_nmo_fa_loading_{i}" for i in range(8)]
FA_DRIFT = [f"fa_drift_fa_loading_{i}" for i in range(8)]
RAW = ["mean_rate", "osi", "dsi", "f1_f0_pref"]
BASELINES = {"FA-nmo": FA_NMO, "FA-drift": FA_DRIFT, "raw props": RAW}


def _rho5(M):
    k = M.shape[1]
    pr = [spearmanr(M[:, i], M[:, j]).statistic for i, j in itertools.combinations(range(k), 2)]
    rb = float(np.mean(pr))
    return (k * rb / (1 + (k - 1) * rb)) if rb > 0 else 0.0


def rho_frames(sub, cols):
    """rho band across defensible centering frames. A verdict that flips inside the
    band is INDETERMINATE, not the frame you liked."""
    g = sub.groupby("session_id")[cols]
    zc = lambda x: (x - x.mean()) / x.std(ddof=1)
    frames = {
        "raw pooled": sub[cols].values,
        "within-session z": g.transform(zc).values,
        "within-session rank": g.rank().values,
    }
    return {k: _rho5(v) for k, v in frames.items()}


def rho_ci(sub, cols, n_boot=2000, seed=5):
    M = sub[cols].values
    odd, even = M[:, ::2].mean(1), M[:, 1::2].mean(1)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n_boot):
        i = rng.integers(0, len(odd), len(odd))
        r = spearmanr(odd[i], even[i]).statistic
        bs.append(2 * r / (1 + r) if r > 0 else 0.0)   # Spearman-Brown on the half
    r0 = spearmanr(odd, even).statistic
    point = 2 * r0 / (1 + r0) if r0 > 0 else 0.0
    return point, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def r2(sub, target, preds):
    s = sub[["session_id", target] + preds].dropna()
    if len(s) < len(preds) + 5:
        return np.nan, 0
    zc = lambda x: (x - x.mean()) / x.std(ddof=1)
    y = s.groupby("session_id")[target].transform(zc).values
    X = s.groupby("session_id")[preds].transform(zc).values
    X = np.c_[np.ones(len(X)), X]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(1 - ((y - X @ beta) ** 2).sum() / ((y - y.mean()) ** 2).sum()), len(s)


def verdict(r2_obs, rho_lo, rho_hi, band, tau=TAU):
    """Four states, not three. A high-rho axis whose R2_true clears tau is NOT
    'indeterminate' -- it is reliably measured and simply not orthogonal. Collapsing
    that into INDETERMINATE (which means 'the instrument cannot see') would launder a
    real negative result into an unknown one."""
    if not np.isfinite(r2_obs) or r2_obs <= 0:
        return "INDETERMINATE (no R2)"
    need = r2_obs / tau
    band_lo, band_hi = min(band.values()), max(band.values())

    # Reliability is established (CI and band both high) -> the R2_true reading is trusted.
    reliable = rho_lo > 0.50 and band_lo > 0.50
    if rho_lo > need and band_lo > need:
        return "ADMISSIBLE-ORTHOGONAL"
    if reliable:
        # r2_true bounded by the rho CI; both ends inform the label.
        t_lo, t_hi = r2_obs / rho_hi, r2_obs / rho_lo
        if t_lo >= SUBSUMED_FLOOR:
            return "SUBSUMED-CERTIFIED"          # clears the floor across the whole CI
        if t_lo > tau:
            return "NOT-ORTHOGONAL (subsumption not certified)"
        return "INDETERMINATE (straddles tau)"
    return "INDETERMINATE (reliability below gate)"


def main():
    axes = pd.read_parquet(OUT / "per_cell_windowed_axes.parquet")
    banked = pd.read_parquet(Path(ROOT_DIR) / "data/phase32b_results/per_cell_decomposition_merged.parquet")
    keep = [c for c in banked.columns if c.startswith(("fa_nmo_", "fa_drift_"))] + \
           RAW + ["session_id", "unit_id"]
    df = axes.merge(banked[keep], on=["session_id", "unit_id"], how="left")

    # Regression targets must be the SAME aggregates the banked R^2 used:
    #   p7_mean_z  = mean of the per-window z (now @ 100 independent surrogates)
    #   rep_med / ks_gue_med = FULL-TRAIN estimates (frozen unfold, no decimation)
    # rho is estimated from the 5 windows via Spearman-Brown at k=5, i.e. the
    # reliability of a 5-window mean. That is the right proxy for the full-train
    # estimate only because both consume the same total data. Stated, not assumed.
    df["p7_mean_z"] = df[AXES["p7_mean_z"]].mean(axis=1)
    df["rep_med"] = df["rep_med_full"]
    df["ks_gue_med"] = df["ks_gue_med_full"]

    full = df[df.status == "OK"]
    print(f"full cohort (B4 reference) n={len(full)}   status counts:\n{df.status.value_counts().to_string()}\n")

    rows = []
    for axis, cols in AXES.items():
        sub_all = full.dropna(subset=cols)
        cohorts = {"full": sub_all}
        # trimmed cohort: cells that would survive a naive windowed-power cut
        trimmed = sub_all[sub_all[[f"n_w{i}" for i in range(5)]].min(1) >= 150]
        if len(trimmed) < len(sub_all):
            cohorts["trimmed(min_n>=150)"] = trimmed

        for cname, sub in cohorts.items():
            if len(sub) < 30:
                continue
            band = rho_frames(sub, cols)
            pt, lo, hi = rho_ci(sub, cols)
            for bname, preds in BASELINES.items():
                R2, n = r2(sub, axis, preds)
                v = verdict(R2, lo, hi, band)
                rows.append(dict(axis=axis, baseline=bname, cohort=cname, n=n,
                                 rho=pt, rho_ci_lo=lo, rho_ci_hi=hi,
                                 rho_band_lo=min(band.values()), rho_band_hi=max(band.values()),
                                 r2_obs=R2, rho_required=R2 / TAU if np.isfinite(R2) else np.nan,
                                 verdict=v))

    led = pd.DataFrame(rows)
    led.to_parquet(OUT / "reliability_ledger.parquet", index=False)

    pd.set_option("display.width", 200)
    print(led.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    # B4 check: does any verdict differ between cohorts?
    print("\n--- B4 cohort-invariance check ---")
    for (a, b), g in led.groupby(["axis", "baseline"]):
        if g.cohort.nunique() > 1 and g.verdict.nunique() > 1:
            print(f"  *** {a} ~ {b}: verdict DIFFERS across cohorts -> INDETERMINATE ***")
            print(g[["cohort", "n", "rho", "r2_obs", "verdict"]].to_string(index=False))
    print("\n--- axes with NO admissible orthogonality verdict ---")
    for a in AXES:
        sub = led[led.axis == a]
        if not (sub.verdict == "ADMISSIBLE-ORTHOGONAL").any():
            print(f"  {a}: no ADMISSIBLE-ORTHOGONAL row -> carries NO orthogonality verdict")
    print(f"\n-> data/phase38_results/reliability_ledger.parquet")


if __name__ == "__main__":
    main()

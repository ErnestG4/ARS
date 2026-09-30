"""Change-point null calibration (STAGE3_FINDINGS open item; rule declared here before running, 2026-09-26 06:10).
The BIC binary segmentation in stage3_analyze.changepoints flagged >= 1 change in 270/337 Pythia-1.4B series. Smooth
curvature in log-step may produce breaks by itself.
Null family (no change point by construction), sampled at the 25 schedule steps >= 1, x = log10(step):
  sigmoid(x; centre c, width w), c ~ U(1, 4.5), w ~ U(0.2, 1.5); saturating 1 - exp(-(x/a)^b), a ~ U(1, 4), b ~ U(1, 4);
  and pure linear. Each is scaled to the observed series' range, with Gaussian noise at the observed series' noise level
  (the residual SD after a 2nd-order local smoother; the median over series is used).
RULE: change points are LICENSED only if the false-change-point rate (>= 1 change flagged on a null) is <= 5% for the
matched null. Otherwise every change point is descriptive only -- as currently labelled -- and the label is now
calibrated rather than asserted.
"""
import json
from pathlib import Path
import numpy as np, pandas as pd
import stage3_analyze as A
ROOT = Path(__file__).resolve().parent
df = pd.read_parquet(ROOT / "results" / "stage3_long.parquet")
agg = df[(df.step >= 1) & (df.band.isin(["all", "bulk"]))].groupby(["matrix", "band", "metric", "step"]).value.mean().reset_index()
noise, ranges = [], []
for _, g in agg.groupby(["matrix", "band", "metric"]):
    g = g.sort_values("step")
    if len(g) < 8:
        continue
    y = g.value.values; x = np.log10(g.step.values)
    rng_ = y.max() - y.min()
    if rng_ <= 0:
        continue
    res = []
    for i in range(1, len(y) - 1):                         # 2nd-order local smoother residual (leave-one-out)
        res.append(y[i] - (y[i - 1] + y[i + 1]) / 2)
    noise.append(np.std(res) / rng_ / np.sqrt(1.5)); ranges.append(rng_)
sig_rel = float(np.median(noise))
x = np.log10(np.array(sorted(s for s in set(df.step) if s >= 1), float))
rng = np.random.default_rng(0)
out = {"doc": __doc__, "noise_rel_median": sig_rel, "n_series": len(noise), "rates": {}}
for fam in ("sigmoid", "saturating", "linear"):
    for nl in (0.5, 1.0, 2.0):
        hits = 0; N = 400
        for _ in range(N):
            if fam == "sigmoid":
                c, w = rng.uniform(1, 4.5), rng.uniform(0.2, 1.5); y = 1 / (1 + np.exp(-(x - c) / w))
            elif fam == "saturating":
                a, b = rng.uniform(1, 4), rng.uniform(1, 4); y = 1 - np.exp(-(x / a) ** b)
            else:
                y = x / x.max()
            y = (y - y.min()) / max(y.max() - y.min(), 1e-12) + nl * sig_rel * rng.standard_normal(len(x))
            cps, _ = A.changepoints(x, y)
            hits += len(cps) > 0
        out["rates"][f"{fam}_noise{nl}x"] = hits / N
        print(f"{fam:10s} noise {nl}x median: false-CP rate {hits / N:.3f}", flush=True)
worst = max(out["rates"].values())
out["LICENSED"] = bool(worst <= 0.05)
print("median relative noise", round(sig_rel, 4), "| worst false-CP rate", worst, "| LICENSED:", out["LICENSED"])
(ROOT / "results" / "stage3_cp_null.json").write_text(json.dumps(out, indent=1))

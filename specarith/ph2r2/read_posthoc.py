"""R₂ read — post-hoc descriptive checks (written after the read; nothing here is a verdict).
1. Pooled μ̂ (inverse-variance, surrogate SDs; bins are disjoint, so independent).
2. Is the agreement with μ = 1 finer than the resolution? χ² of (μ̂ − 1) over the 5 bins under two SD choices: the
   sealed surrogate SD (independent CUE_250 blocks) and the zeros' own drift-removed 10,000-level bootstrap SD.
3. Block-length growth ranges: zeros (drift-removed) vs the dry-run surrogates (drift-removed).

  python read_posthoc.py  ->  results/read/POSTHOC.md
"""
import json
import math
import os

import numpy as np
from scipy import stats

import r2prep as P

HERE = os.path.dirname(os.path.abspath(__file__))
seal = json.load(open(os.path.join(HERE, "seals", "PH2R2_SEAL_1.0.json")))
M = {n: json.load(open(os.path.join(HERE, "results", "read", f"{n}.json"))) for n in P.BINS}
mu = np.array([M[n]["mu"] for n in P.BINS])
sd_s = np.array([M[n]["sd_surrogate"] for n in P.BINS])
sd_z = np.array([M[n]["boot_sd_drift_removed"]["10000"] for n in P.BINS])
out = ["# R₂ read — post-hoc descriptive checks (not verdicts)", ""]
w = 1 / sd_s ** 2
pooled, se = float(np.sum(w * mu) / np.sum(w)), float(1 / math.sqrt(np.sum(w)))
out += [f"- **Pooled μ̂** (inverse-variance, surrogate SDs): {pooled:.4f} ± {se:.4f} (1 SD); "
        f"μ = 0 excluded by {pooled / se:.0f} SD; |μ̂ − 1| = {abs(pooled - 1) / se:.2f} SD.", ""]
for tag, sd in (("sealed surrogate SD", sd_s), ("zeros' own drift-removed 10,000-level bootstrap SD", sd_z)):
    z = (mu - 1) / sd
    chi2 = float(np.sum(z ** 2))
    out.append(f"- (μ̂ − 1)/SD with the {tag}: {', '.join(f'{x:+.2f}' for x in z)}; χ²₅ = {chi2:.2f}, "
               f"P(χ²₅ ≤ this) = {stats.chi2.cdf(chi2, 5):.3f}")
gz = [M[n]["A1_growth_drift_removed"][-1] for n in P.BINS]
gs = [seal["bins"][n]["A1_dryrun_surrogate_growth_drift_removed"][-1] for n in P.BINS]
out += ["", f"- Drift-removed growth at 10,000 levels: zeros {min(gz):.2f}–{max(gz):.2f} "
        f"({', '.join(f'{x:.2f}' for x in gz)}); dry-run surrogates {min(gs):.2f}–{max(gs):.2f} "
        f"({', '.join(f'{x:.2f}' for x in gs)}).", ""]
open(os.path.join(HERE, "results", "read", "POSTHOC.md"), "w").write("\n".join(out))
print("\n".join(out))

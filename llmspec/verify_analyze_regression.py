"""G3 refactor regression, analysis half: stage3_analyze (model-general) run on {step0, step143000} with
STAGE3_TAG=_regress must reproduce the banked full-run values (results/stage3_long.parquet) exactly for every metric
that does not depend on other revisions (subspace overlaps, change points and motion are excluded). Exit 1 on any
mismatch. --redpath: compare step0 regress rows against step143000 banked rows; they must mismatch."""
import sys
import numpy as np, pandas as pd
new = pd.read_parquet("results/stage3_long_regress.parquet")
ref = pd.read_parquet("results/stage3_long.parquet")
excl = new.metric.str.contains("overlap|dW_") | (new.matrix == "MODEL") & new.metric.str.contains("___")
new = new[~excl]
key = ["step", "layer", "matrix", "head", "band", "metric"]
if "--redpath" in sys.argv:
    new = new[new.step == 0].assign(step=143000)
m = new.merge(ref, on=key, how="left", suffixes=("_new", "_ref"))
missing = int(m.value_ref.isna().sum())
bad = m[m.value_ref.notna() & (m.value_new != m.value_ref)]
print(f"rows compared: {len(m) - missing}; missing in ref: {missing}; exact mismatches: {len(bad)}"
      + (" [REDPATH]" if "--redpath" in sys.argv else ""))
if len(bad):
    print(bad.groupby("metric").size().sort_values(ascending=False).head(8).to_string())
fail = bool(len(bad) or missing)
sys.exit((0 if fail else 1) if "--redpath" in sys.argv else (1 if fail else 0))

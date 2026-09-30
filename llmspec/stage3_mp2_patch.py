"""Add mp_fit_v2's square-matrix lowest-10% KS (mp2_lower10_ks) to an existing stage3_long parquet, calling the SAME
stage3_analyze.mp_fit_v2 used by the analysis. Needed once: the 2026-09-25 full run had imported stage3_analyze before
mp2_lower10_ks existed (its v1 counterpart uses the collapsed v1 scale and is DEGENERATE for trained Q/K)."""
import os, json
from pathlib import Path
import numpy as np, pandas as pd
import stage3_analyze as A
ROOT = Path(__file__).resolve().parent
TAG = os.environ.get("STAGE3_TAG", "")
fp = ROOT / "results" / f"stage3_long{TAG}.parquet"
df = pd.read_parquet(fp)
if "mp2_lower10_ks" in set(df.metric):
    print("already patched"); raise SystemExit
wit = json.loads((ROOT / "results" / "stage3_witness.json").read_text())
rows = []
for rev in sorted(set(df.step)):
    d = ROOT / "cache" / "s3" / A.MODEL / f"step{rev}"
    for l in range(24):
        z = np.load(d / f"L{l:02d}.npz")
        for M in ("Q", "K", "V", "O"):
            m, n = A.FULL[M]
            r = A.mp_fit_v2(z[f"sig_{M}"], m, n, wit["types"][M]["tau_plus"], wit["types"][M]["tau_minus"])
            rows.append((A.MODEL, "base", int(rev), l, M, -1, "all", "mp2_lower10_ks", r["mp2_lower10_ks"], "mp_fit_v2"))
new = pd.concat([df, pd.DataFrame(rows, columns=df.columns)], ignore_index=True)
tmp = fp.with_suffix(".tmp.parquet"); new.to_parquet(tmp); os.replace(tmp, fp)
print("added", len(rows), "rows")

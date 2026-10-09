"""R₂ read report (written before the read): per-bin table from results/read/<bin>.json and the seal JSON.
Verdict (A2), μ̂ and CI, achieved vs target half-width, 0 ∈ CI (descriptive), zero count vs N̄, and A1/A3's block-length
growth three ways (raw; surrogate-relative = raw ÷ the G0b surrogates' mean growth; drift-removed).

  python read_report.py  ->  results/read/READ_REPORT.md
"""
import json
import os

import r2prep as P

HERE = os.path.dirname(os.path.abspath(__file__))
seal = json.load(open(os.path.join(HERE, "seals", "PH2R2_SEAL_1.0.json")))
f3 = lambda xs: " → ".join(f"{x:.2f}" for x in xs)
rows, grow = [], []
for name in P.BINS:
    m = json.load(open(os.path.join(HERE, "results", "read", f"{name}.json")))
    b = seal["bins"][name]
    g = P.geometry(name)
    zero_in = m["ci"][0] <= 0 <= m["ci"][1]
    rows.append(f"| {name} | {g['L_c']:.2f} | {m['n']:,} ({m['n'] / g['n_zeros']:.6f} of N̄) | {m['mu']:.4f} | "
                f"[{m['ci'][0]:.4f}, {m['ci'][1]:.4f}] | {m['halfwidth']:.4f} / {b['target_halfwidth']:.4f} | "
                f"{'yes' if zero_in else 'no'} | **{m['verdict']}** |")
    grow.append(f"| {name} | {f3(m['A1_growth'])} | {f3(b['A1_surrogate_growth'])} | "
                f"{f3(m['A1_growth_surrogate_relative'])} | {f3(m['A1_growth_drift_removed'])} | "
                f"{f3(b['A1_dryrun_surrogate_growth_drift_removed'])} |")
out = ["# R₂ read — μ̂ per fresh bin (PH2R2_SEAL_1.0, amendments A1–A3)", "",
       f"Primary test function (u, w) = {tuple(seal['primary'])}; CI = μ̂ ± 1.96·max(SD_surrogate, widest bootstrap SD).",
       "Verdict (A2): NOT RESOLVABLE (achieved) iff the CI contains both 0 and 1 or its half-width > 0.5; else PASS iff "
       "1 ∈ CI, else FAIL.", "",
       "| bin | log(t/2π) | zeros | μ̂ | 95% CI | half-width achieved / target | 0 ∈ CI | G1 |",
       "|---|---|---|---|---|---|---|---|", *rows, "",
       "## Block-length growth of the bootstrap SD (A1/A3; descriptive, 100 → 1,000 → 10,000 levels)",
       "| bin | raw | G0b surrogate mean (raw) | surrogate-relative | drift-removed | dry-run surrogate, drift-removed |",
       "|---|---|---|---|---|---|", *grow, ""]
open(os.path.join(HERE, "results", "read", "READ_REPORT.md"), "w").write("\n".join(out))
print("\n".join(out))

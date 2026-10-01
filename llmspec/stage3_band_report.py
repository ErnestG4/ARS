"""Report the pre-registered LOWER/UPPER-band <r~> descriptives (STAGE3_PREREG.md: 'The same tolerances are reported for
LOWER and UPPER bands, labelled descriptive (not sealed)'). They were banked in every stage3_long*.parquet
(metric rt_minus_witness, band lower/upper) but never reported; this is the reporting fix (2026-10-01).
Output: results/stage3_band_rt.json and a markdown table on stdout (final checkpoint, per matrix type, per run)."""
import json, glob, pandas as pd
from pathlib import Path
runs = {"pythia-1.4b": "results/stage3_long.parquet", "pythia-1b": "results/stage3_long_pythia-1b.parquet",
        "pythia-410m": "results/stage3_long_pythia-410m.parquet"}
runs.update({f"pythia-410m-seed{s}": f"results/stage3_long_pythia-410m-seed{s}.parquet" for s in range(1, 10)})
out, rows = {}, []
for run, f in runs.items():
    if not Path(f).exists(): continue
    d = pd.read_parquet(f); m = d[d.metric == "rt_minus_witness"]
    last = int(m.step.max()); out[run] = {"final_step": last, "bands": {}}
    for band in ["lower", "bulk", "upper"]:
        b = m[(m.band == band)]
        traj = b.pivot_table(index="matrix", columns="step", values="value")
        out[run]["bands"][band] = {mt: {str(int(s)): float(v) for s, v in traj.loc[mt].items()} for mt in traj.index}
    fin = m[m.step == last].pivot_table(index="matrix", columns="band", values="value")
    for mt in fin.index: rows.append((run, mt, fin.loc[mt, "lower"], fin.loc[mt, "bulk"], fin.loc[mt, "upper"]))
Path("results/stage3_band_rt.json").write_text(json.dumps(out, indent=0))
t = pd.DataFrame(rows, columns=["run", "matrix", "lower", "bulk", "upper"])
print("| run | matrix | lower | bulk | upper |\n|---|---|---|---|---|")
for _, r in t.iterrows():
    if abs(r.upper) > 0.010 or abs(r.lower) > 0.010 or r.run in ("pythia-1.4b",) and r.matrix.startswith("head_Q"):
        print(f"| {r.run} | {r.matrix} | {r.lower:+.3f} | {r.bulk:+.3f} | {r.upper:+.3f} |")
print("\nupper-band head_Q/head_K at final step, all runs:")
print(t[t.matrix.isin(["head_Q", "head_K"])].pivot_table(index="run", columns="matrix", values="upper").round(3).to_string())
print("\ncells with |lower|>0.010:", int((t.lower.abs() > 0.010).sum()), " |upper|>0.010:", int((t.upper.abs() > 0.010).sum()), " of", len(t))

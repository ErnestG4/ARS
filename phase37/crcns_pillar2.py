"""
phase37/crcns_pillar2.py — publication-grade re-derivation of CRCNS pillar-2 (selectivity <-> spectral
class) + the supporting descriptors, with bootstrap 95% CIs and burst-controlled partials.

Substrates (CRCNS):
  pvc-11  anesthetized macaque V1 (Kohn)        — H1: OSI <-> ks_gue
  hc-3    Mizuseki/Buzsaki rat hippocampus       — spatial-info <-> ks_gue (per region)
  ret-1   mouse RGC retina (white-noise)         — RF-SNR <-> ks_gue (banked NULL = axis-mismatch)

ks_gue = KS distance to the GUE Wigner surmise (LOW = GUE-like/repulsive, HIGH = away-from-GUE/clustered).
Pillar-2 sign convention reported explicitly. Burst-controlled partial = the defensible figure (rules out
the intrinsic burst tautology, per the intrinsic-vs-extrinsic / pillar2-burst-control discipline).
All correlations Spearman; CIs = 2000-resample cell bootstrap (seeded). NOT from the overnight wave.
"""
import json, numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata
ROOT = "$HOME/fmexplorer/criticality_tool"
RNG = np.random.default_rng(20260601)


def _partial_rank(x, y, *covs):
    """Partial Spearman of x,y controlling >=1 covariates: rank all, residualize rank(x),rank(y) on the
    rank(covariate) design (with intercept) via least squares, correlate the residuals."""
    rx, ry = rankdata(x).astype(float), rankdata(y).astype(float)
    Z = np.column_stack([np.ones(len(x))] + [rankdata(c).astype(float) for c in covs])
    ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]
    ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1])


def boot_ci(fn, *arrs, n=2000):
    m = len(arrs[0]); vals = []
    for _ in range(n):
        idx = RNG.integers(0, m, m)
        try: vals.append(fn(*[a[idx] for a in arrs]))
        except Exception: pass
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def report(name, x, y, covs=None, cov_names="", sign_note=""):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rho, p = spearmanr(x, y); lo, hi = boot_ci(lambda a, b: spearmanr(a, b)[0], x, y)
    out = dict(test=name, n=len(x), rho=round(float(rho), 3), ci=[round(lo, 3), round(hi, 3)], p=float(p))
    line = f"  {name:40s} n={len(x):4d}  rho={rho:+.3f}  95%CI[{lo:+.3f},{hi:+.3f}]  p={p:.1e}"
    if covs:
        covs = [np.asarray(c, float) for c in covs]
        pr = _partial_rank(x, y, *covs)
        plo, phi = boot_ci(lambda *a: _partial_rank(a[0], a[1], *a[2:]), x, y, *covs)
        out.update(partial_rho=round(float(pr), 3), partial_ci=[round(plo, 3), round(phi, 3)], controlled_for=cov_names)
        line += f"\n    -> partial rho={pr:+.3f}  95%CI[{plo:+.3f},{phi:+.3f}]  (controlling {cov_names})"
    if sign_note: line += f"\n    [{sign_note}]"
    print(line); return out


def load_jsonl(f): return [json.loads(l) for l in open(f"{ROOT}/cross_substrate/coordinates/{f}.jsonl")]
results = {}

print("="*78); print("pvc-11  (CRCNS, anesthetized macaque V1, Kohn) — H1: OSI <-> ks_gue"); print("="*78)
# pvc-11 tables are BOTH in phase22a_results (phase24's h1_classifications is the ALLEN one, big-int unit_id).
# Join on (recording, unit_id) — unit_id repeats across recordings/monkeys, so unit_id alone over-joins.
fn = pd.read_parquet(f"{ROOT}/data/phase22a_results/h1_functional.parquet")
cl = pd.read_parquet(f"{ROOT}/data/phase22a_results/h1_classifications.parquet")
grat = fn[fn.subset == "gratings"][["recording", "unit_id", "osi", "mean_rate"]].dropna()
m = grat.merge(cl[["recording", "unit_id", "ks_gue_med"]].dropna(), on=["recording", "unit_id"])
results["pvc11_H1"] = report("OSI vs ks_gue (drifting gratings)", m.osi.values, m.ks_gue_med.values,
    covs=[m.mean_rate.values], cov_names="rate",
    sign_note="RAW is rate-CONFOUNDED; banked phase27 method-B (rate-matched) rho=+0.298, SUBSTRATE-SYSTEMATIC (Allen -0.22). Use rate-controlled.")

print("="*78); print("hc-3  (CRCNS, Mizuseki/Buzsaki rat hippocampus) — spatial-info <-> ks_gue"); print("="*78)
pc = {(d["session"], d["ele"], d["clu"]): (d["burst"]["burst_frac"], d["axes_computed"].get("I.5_ks_gue"),
       d.get("region"), d.get("rate_hz"))
      for d in load_jsonl("hc3-port-cell") if d["axes_computed"].get("I.5_ks_gue") is not None}
rows = []
for d in load_jsonl("hc3-placefields"):
    k = (d["session"], d["ele"], d["clu"])
    if k in pc and d.get("spatial_info_bits_per_spike") is not None and pc[k][3] is not None:
        bf, ks, reg, rt = pc[k]; rows.append((d["spatial_info_bits_per_spike"], ks, bf, reg, rt))
SI = np.array([r[0] for r in rows]); KS = np.array([r[1] for r in rows]); BF = np.array([r[2] for r in rows])
REG = np.array([r[3] for r in rows]); RT = np.array([r[4] for r in rows])
results["hc3_pillar2_all"] = report("spatial-info vs ks_gue (all regions)", SI, KS, [RT, BF], "rate+burst",
    sign_note="positive = spatially-selective place cells AWAY from GUE (clustered)")
for rg in ("CA1", "CA3", "EC", "DG"):
    msk = REG == rg
    if msk.sum() >= 15:
        results[f"hc3_pillar2_{rg}"] = report(f"  spatial-info vs ks_gue [{rg}]", SI[msk], KS[msk], [RT[msk], BF[msk]], "rate+burst")

print("="*78); print("ret-1  (CRCNS, mouse RGC retina, white-noise) — RF-SNR <-> ks_gue"); print("="*78)
r1 = {(d["recording"], d["cell"]): (d["burst"]["burst_frac"], d["axes_computed"].get("I.5_ks_gue"), d.get("rate_hz"))
      for d in load_jsonl("ret1-cell") if d["axes_computed"].get("I.5_ks_gue") is not None}
rf = {(d["recording"], d["cell"]): d["rf_snr"] for d in load_jsonl("ret1-rf")}
keys = [k for k in r1 if k in rf and r1[k][2] is not None]
RFv = np.array([rf[k] for k in keys]); KSv = np.array([r1[k][1] for k in keys])
BFv = np.array([r1[k][0] for k in keys]); RTv = np.array([r1[k][2] for k in keys])
results["ret1_pillar2"] = report("RF-SNR vs ks_gue", RFv, KSv, [RTv, BFv], "rate+burst",
    sign_note="banked NULL = axis-mismatch (RF-SNR not the selectivity axis under white-noise; needs DSI/motion)")

json.dump(results, open(f"{ROOT}/phase37/crcns_pillar2_results.json", "w"), indent=1)
print(f"\nWrote {ROOT}/phase37/crcns_pillar2_results.json")

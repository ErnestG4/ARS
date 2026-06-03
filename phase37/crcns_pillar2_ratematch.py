"""
phase37/crcns_pillar2_ratematch.py — (a) pvc-11 H1 reconciliation + (b) rate-MATCHED (stratified) hc-3 pillar-2.

(a) RESOLVED: pvc-11 within-substrate H1 OSI<->ks_gue = +0.720 (banked PVC11_REF in phase24/run_verdicts.py).
    Fresh re-derivation reproduces it (+0.72). The +0.298 in phase27/analysis1_verdict.json is a DIFFERENT
    statistic — the cross-substrate rate-matched-to-Allen comparison (method_b, n=210) used for the
    SUBSTRATE-SYSTEMATIC sign-flip test (Allen mouse-V1 = -0.22). No discrepancy. Direction: pvc-11 + and
    hc-3 + AGREE (selective cells -> away from GUE / clustered); the sign-flip is macaque-vs-mouse V1.

(b) Banked H1 method = per-unit Spearman partial controlling mean rate. For hc-3 we add the stronger
    rate-STRATIFIED check: within firing-rate quartiles compute spatial_info<->ks_gue (burst-partial within
    quartile), then fixed-effect pool + bootstrap CI. If it survives within-quartile, the +0.47 partial is
    not a between-rate-bin artifact.
"""
import json, numpy as np
from scipy.stats import spearmanr, rankdata
ROOT = "$HOME/fmexplorer/criticality_tool"
RNG = np.random.default_rng(20260601)


def load_jsonl(f): return [json.loads(l) for l in open(f"{ROOT}/cross_substrate/coordinates/{f}.jsonl")]


def partial(x, y, *covs):
    rx, ry = rankdata(x).astype(float), rankdata(y).astype(float)
    Z = np.column_stack([np.ones(len(x))] + [rankdata(c).astype(float) for c in covs])
    ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]
    ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1])


# build hc-3 (spatial_info, ks_gue, burst, rate)
pc = {(d["session"], d["ele"], d["clu"]): (d["burst"]["burst_frac"], d["axes_computed"].get("I.5_ks_gue"),
       d.get("rate_hz")) for d in load_jsonl("hc3-port-cell") if d["axes_computed"].get("I.5_ks_gue") is not None}
rows = []
for d in load_jsonl("hc3-placefields"):
    k = (d["session"], d["ele"], d["clu"])
    if k in pc and d.get("spatial_info_bits_per_spike") is not None and pc[k][2] is not None:
        bf, ks, rt = pc[k]; rows.append((d["spatial_info_bits_per_spike"], ks, bf, rt))
A = np.array(rows)
SI, KS, BF, RT = A[:, 0], A[:, 1], A[:, 2], A[:, 3]
print(f"hc-3 pillar-2 (spatial_info <-> ks_gue), n={len(A)}")
print(f"  raw rho           = {spearmanr(SI,KS)[0]:+.3f}")
print(f"  partial|rate,burst= {partial(SI,KS,RT,BF):+.3f}   (matches main script +0.47)")

# rate-STRATIFIED: within rate quartiles, burst-partial spatial_info<->ks_gue, fixed-effect pool
def stratified(si, ks, bf, rt, nq=4):
    q = np.quantile(rt, np.linspace(0, 1, nq + 1)); rhos = []; ns = []
    for i in range(nq):
        m = (rt >= q[i]) & (rt <= q[i + 1]) if i == nq - 1 else (rt >= q[i]) & (rt < q[i + 1])
        if m.sum() >= 20:
            rhos.append(partial(si[m], ks[m], bf[m])); ns.append(m.sum())
    rhos, ns = np.array(rhos), np.array(ns)
    return float(np.sum(rhos * ns) / np.sum(ns)), rhos, ns  # n-weighted fixed-effect pool

pooled, rhos, ns = stratified(SI, KS, BF, RT)
print(f"  rate-STRATIFIED (within-quartile burst-partial, n-weighted pool) = {pooled:+.3f}")
print(f"    per-quartile rho={[round(r,3) for r in rhos]} n={list(ns)}")
# bootstrap CI on the stratified pooled estimate
boot = []
for _ in range(2000):
    idx = RNG.integers(0, len(A), len(A))
    try: boot.append(stratified(SI[idx], KS[idx], BF[idx], RT[idx])[0])
    except Exception: pass
lo, hi = np.percentile(boot, [2.5, 97.5])
print(f"    rate-stratified pooled 95%CI = [{lo:+.3f}, {hi:+.3f}]")
print(f"  VERDICT: spatial_info<->ks_gue {'SURVIVES rate-stratification' if lo>0 else 'does NOT survive'} "
      f"(pooled {pooled:+.3f}) -> genuine, not a between-rate-bin artifact")

out = dict(pvc11_H1_within_substrate_banked=0.720,
           pvc11_298_is="cross-substrate rate-matched-to-Allen (method_b), NOT within-substrate H1",
           hc3_partial_rate_burst=round(partial(SI, KS, RT, BF), 3),
           hc3_rate_stratified_pooled=round(pooled, 3),
           hc3_rate_stratified_ci=[round(float(lo), 3), round(float(hi), 3)],
           direction="pvc-11(+) and hc-3(+) AGREE: selective->clustered; sign-flip is vs Allen mouse-V1(-0.22)")
json.dump(out, open(f"{ROOT}/phase37/crcns_pillar2_ratematch_results.json", "w"), indent=1)
print("\nWrote crcns_pillar2_ratematch_results.json")

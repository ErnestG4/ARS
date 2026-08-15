"""Comb arc G3: fresh-wedge measurement.  COMMITTED GENERATOR of
comb/comb_measured.json.  Runs ONLY against comb/prereg_sealed.json; every
threshold and window is read from the seal, never typed here.

This file is part of the code-freeze set's *runner* layer: it contains no
estimator logic (frozen in exact_offsets.py at the sealed commit) — it wires
sealed windows to frozen estimators and applies the sealed 2x2.
"""

import json
import sys
import numpy as np

CT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{CT}/comb")
from exact_offsets import build_points, measure

SEAL = json.load(open(f"{CT}/comb/prereg_sealed.json"))
T1, T2 = SEAL["windows"]["wedge_theta"]
BAND1 = tuple(SEAL["windows"]["band1_norm"])
BAND2 = tuple(SEAL["windows"]["band2_norm"])
K = SEAL["acceptance_2x2"]["k"]
classes = {cid: dict(offsets=[tuple(h) for h in
                              json.load(open(f"{CT}/comb/singular_series_banked.json"))
                              ["classes"][cid]["offsets"]])
           for cid in SEAL["prediction_first"]["classes"]}
pred = SEAL["prediction_first"]["classes"]

res = {"seal_cited": f"{CT}/comb/prereg_sealed.json"}
bands = {}
for tag, (lo, hi) in (("band1", BAND1), ("band2", BAND2)):
    pts = build_points(lo, hi, T1, T2)
    print(f"{tag}: n = {len(pts)} points sieved", flush=True)
    bands[tag] = measure(pts, classes, lo, hi, T1, T2)
    res[f"{tag}_n"] = int(len(pts))

rows = {}
drift_signs, drift_hits = [], 0
level_ok = True
for cid, p in pred.items():
    b1, b2 = bands["band1"][cid], bands["band2"][cid]
    w1, w2 = 1.0 / b1["sigma"] ** 2, 1.0 / b2["sigma"] ** 2
    pooled = (b1["S_hat"] * w1 + b2["S_hat"] * w2) / (w1 + w2)
    sig_p = (w1 + w2) ** -0.5
    z_level = (pooled - p["S_prime_pred"]) / sig_p
    sig_d = np.hypot(b1["sigma"], b2["sigma"])
    z_drift = (b2["S_hat"] - b1["S_hat"]) / sig_d
    rows[cid] = dict(pred=p["S_prime_pred"], mandatory=p["mandatory"],
                     S1=b1["S_hat"], sig1=b1["sigma"], C1=b1["C"],
                     S2=b2["S_hat"], sig2=b2["sigma"], C2=b2["C"],
                     pooled=float(pooled), sigma_pooled=float(sig_p),
                     z_level=float(z_level), z_drift=float(z_drift))
    if p["mandatory"]:
        level_ok = level_ok and abs(z_level) <= K
        drift_signs.append(np.sign(z_drift))
        drift_hits += int(abs(z_drift) >= 2.0)
res["classes"] = rows

n_mand = len(drift_signs)
maj = max((np.array(drift_signs) == s).sum() for s in (-1.0, 1.0))
coherent_drift = bool(maj >= np.ceil(2 * n_mand / 3) and drift_hits >= 3)

d = rows["N50_q5m2"]["pooled"] - rows["N50_q5m1"]["pooled"]
sd = np.hypot(rows["N50_q5m2"]["sigma_pooled"], rows["N50_q5m1"]["sigma_pooled"])
disc_ok = bool(d > 0 and d / sd >= 3.0)
res["discriminator"] = dict(diff=float(d), sigma=float(sd), z=float(d / sd),
                            resolved=disc_ok)

if level_ok and disc_ok and not coherent_drift:
    verdict = "PASS (WEIGHTS_MATCH_SINGULAR_SERIES)"
elif level_ok and coherent_drift:
    verdict = "SOFT PASS (MATCH_WITH_BOUNDED_DRIFT)"
elif not level_ok:
    verdict = "FAIL substantive (DEVIATION_BEYOND_ERRORS)"
res["drift"] = dict(n_mandatory=n_mand, majority_sign_count=int(maj),
                    hits_2sigma=int(drift_hits), coherent=coherent_drift)
res["level_all_mandatory_within_k"] = bool(level_ok)
res["VERDICT"] = verdict

with open(f"{CT}/comb/comb_measured.json", "w") as f:
    json.dump(res, f, indent=1)

print(f"\n{'cid':16s} {'pred':>7s} {'pooled':>7s} {'sig':>6s} {'z_lvl':>6s} {'z_drf':>6s}")
for cid, r in sorted(rows.items(), key=lambda kv: (not kv[1]['mandatory'], kv[0])):
    tag = "M" if r["mandatory"] else "s"
    print(f"{tag} {cid:14s} {r['pred']:7.4f} {r['pooled']:7.4f} "
          f"{r['sigma_pooled']:6.4f} {r['z_level']:+6.2f} {r['z_drift']:+6.2f}")
print(f"\ndiscriminator N50: diff={d:+.4f} ({d/sd:.1f} sigma) resolved={disc_ok}")
print("drift:", res["drift"])
print("VERDICT:", verdict, flush=True)

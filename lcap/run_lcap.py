"""L-policy measurement (L1 + L3).  COMMITTED GENERATOR of
lcap/lcap_measured.json.  ORDER ENFORCED IN CODE (Will's condition 1):
the zoo gate must record PASS, the power cell runs first, and ZETA IS LAST."""

import hashlib
import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (f"{ROOT}/rigidgate", f"{ROOT}/lcap"):
    if p not in sys.path:
        sys.path.insert(0, p)

SEAL = json.load(open(f"{ROOT}/lcap/prereg_sealed.json"))
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/lcap/{f}", "rb").read()
    assert hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha, \
        f"FREEZE VIOLATION {f}"

zoo = json.load(open(f"{ROOT}/lcap/zoo_measured.json"))
assert zoo["PASS"], "ORDER VIOLATION: zeta may not be evaluated before the " \
                    "zoo gate passes (Will's condition 1)"

import gate_probe as G                                          # noqa: E402
from proposed_rule import rigid_cell, deployed_cell             # noqa: E402

POL = json.load(open(f"{ROOT}/lcap/policy.json"))
K = SEAL["condition_3_power_decides"]["k"]
DEG, SEEDS = 6, 24
OUT = dict(seal_cited="lcap/prereg_sealed.json", order="zoo -> power -> "
           "banked rows -> zeta LAST")

# ── L3 POWER (runs BEFORE zeta, so its threshold cannot be tuned to it) ────
print("L3 power at capped L (substrate-independent; runs before zeta)",
      flush=True)
power = {}
for tag in ("zeta_first_2000", "gue_n343", "gue_n2000"):
    L = POL["policy"][tag]["L_judge"]
    n = 2000 if tag != "gue_n343" else 343
    gue_b, _ = G.bands(n, L, SEEDS, DEG)
    sd = gue_b["sigma2"]["sd"]
    mdd = K * sd
    power[tag] = dict(L_judge=L, n=n, band_mean=float(gue_b["sigma2"]["mean"]),
                      band_sd=float(sd), MDD=float(mdd))
    print(f"  {tag:18s} L={L:5.2f} band {gue_b['sigma2']['mean']:.4f}"
          f"+-{sd:.4f} -> MDD(k={K}) = {mdd:.4f}", flush=True)
OUT["L3_power"] = power

# ── L1 banked rows, zeta LAST ──────────────────────────────────────────────
print("L1 banked rows (reported, not applied)", flush=True)
rows = {}

br = dict(n=343, L_deployed=6.86, sigma2=0.635, gue_mean=0.576, z_rep=0.49)
band_br = dict(mean=br["gue_mean"], sd=(br["sigma2"] - br["gue_mean"]) / br["z_rep"])
Lj_br = POL["policy"]["gue_n343"]["L_judge"]
dep_br, z_br = deployed_cell(br["sigma2"], band_br)
prop_br, _ = rigid_cell(br["sigma2"], band_br)
rows["brocot_golden"] = dict(L_deployed=br["L_deployed"], L_judge=Lj_br,
                             moved_by_policy=bool(br["L_deployed"] > Lj_br),
                             z=float(z_br), deployed=dep_br, proposed=prop_br,
                             note="6.86 < 8.0 cap — the policy does not move "
                                  "this row")
print(f"  brocot_golden: L 6.86 vs cap {Lj_br} -> unmoved; z={z_br:+.2f} "
      f"{dep_br} / {prop_br}", flush=True)

# ---- ZETA, LAST ----
print("L1 ZETA (last, per Will's condition 1)", flush=True)
z_raw = np.load(f"{ROOT}/zeros_2000.npy")
zn = (z_raw / (2 * np.pi)) * np.log(
    np.maximum(z_raw / (2 * np.pi * np.e), 1.0)) + 7.0 / 8.0
Lj = POL["policy"]["zeta_first_2000"]["L_judge"]
gue_b, pois_b = G.bands(2000, Lj, SEEDS, DEG)
band = gue_b["sigma2"]
s2 = G.sigma2(zn, Lj, DEG)
dep, z = deployed_cell(s2, band)
prop, _ = rigid_cell(s2, band)
effect = abs(s2 - band["mean"])
mdd = power["zeta_first_2000"]["MDD"]
resolvable = bool(effect > mdd)
lens = {f"deg{d}": dict(sigma2=float(G.sigma2(zn, Lj, d)),
                        z=float((G.sigma2(zn, Lj, d) - band["mean"])
                                / band["sd"]))
        for d in (3, 6, 10, 15)}
halt = bool(z >= 0.0)
rows["zeta_first_2000"] = dict(
    L_deployed=50.0, L_judge=Lj, binding="validity (Berry ln(T/2pi)=5.99)",
    sigma2=float(s2), band_mean=float(band["mean"]), band_sd=float(band["sd"]),
    z=float(z), z_at_deployed_L=-2.33, deployed=dep, proposed=prop,
    effect_size=float(effect), MDD=float(mdd), resolvable=resolvable,
    lens_sweep=lens,
    sealed_prediction_sign_held=bool(z < 0.0),
    halt=halt)
print(f"  zeta: L {50.0} -> {Lj:.2f} | Sigma2={s2:.4f} band "
      f"{band['mean']:.4f}+-{band['sd']:.4f} -> z={z:+.2f} "
      f"(was {-2.33:+.2f} at L=50)", flush=True)
print(f"  effect {effect:.4f} vs MDD {mdd:.4f} -> resolvable={resolvable}; "
      f"deployed={dep} proposed={prop}", flush=True)
print(f"  lens sweep: " + "  ".join(
    f"{k}:z={v['z']:+.2f}" for k, v in lens.items()), flush=True)
OUT["L1_rows"] = rows

# ── verdict ────────────────────────────────────────────────────────────────
if halt:
    verdict = "HALT_INCONSISTENT"
elif prop == "RIGID_GUE" and not resolvable:
    verdict = "UNDER_RESOLVED"
else:
    verdict = "L_POLICY_FIXED"
OUT["verdict"] = dict(
    primary=verdict,
    zeta_reads=prop,
    sign_precommitment_held=bool(z < 0.0),
    magnitude_counter_expectation_held=bool(abs(z) > 2.33),
    zoo_gate="PASS", discrimination_L=POL["discrimination_L"])
json.dump(OUT, open(f"{ROOT}/lcap/lcap_measured.json", "w"), indent=1)
print(f"VERDICT: {verdict} | zeta reads {prop} under the policy | "
      f"sign pre-commitment held={z < 0.0}", flush=True)

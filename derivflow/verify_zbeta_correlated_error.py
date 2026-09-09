"""Re-derive the correlated-error repair from its committed artifacts.

What this protects, in order:
  1. The RECOVERY IDENTITY. The cell's whole standing rests on the re-run flows
     being the sealed flows: p1_mismatches must be 0, the recovered independent
     fit parameters must equal science_dense_grid.json's banked shape_params to
     double precision, and the recomputed z must equal the banked shape_z. If a
     later edit breaks that, every number here is about a different instrument.
  2. The BARS re-derive from the artifact's own stored quantities.
  3. THE MISS IS PRESERVED. C4 missed: the bootstrap and the GLS sweep do not
     agree to 25%. A later artifact in which C4 reads MET without the underlying
     numbers moving would mean the disagreement was tuned away, and the cell's
     own seal says that disagreement is why no single z is quotable alone.
  4. The DECISION IS INVARIANT: every treatment in the artifact -- bootstrap,
     all four GLS shrinkages, the sealed recomputation, and the conservative
     convention -- clears the sealed 5-sigma bar. That, not any single z, is
     what the cell actually established.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
bad = []
d = json.load(open(os.path.join(HERE, "zbeta_correlated_error.json")))
bank = json.load(open(os.path.join(HERE, "science_dense_grid.json")))

# 1. recovery identity
if d["p1_mismatches"] != 0:
    bad.append(f"p1_mismatches = {d['p1_mismatches']}, not 0 — the recovered "
               "flows are no longer the sealed flows")
for sc in ("iid", "gue"):
    got = d["indep"][sc]["params"]
    want = bank["adjudication"]["shape_params"][sc]
    if len(got) != len(want) or any(g != w for g, w in zip(got, want)):
        bad.append(f"{sc}: recovered fit params != banked shape_params")
if d["z"]["sealed_recomputed"] != bank["adjudication"]["shape_z"]["param2"]:
    bad.append("z.sealed_recomputed != banked shape_z.param2 — the recovered "
               "pipeline no longer reproduces the sealed adjudication")

# 2. bars re-derive from stored quantities
PR = "sealed_fixed"
se_b = {sc: d["bootstrap"][PR][sc]["se_beta"] for sc in ("iid", "gue")}
se_i = {sc: d["indep"][sc]["se_beta"] for sc in ("iid", "gue")}
dp = abs(d["indep"]["iid"]["params"][2] - d["indep"]["gue"]["params"][2])
rec = {
    "sigma_boot(beta_GUE) / sigma_indep(beta_GUE)": se_b["gue"] / se_i["gue"],
    "z_boot(beta)": dp / (se_b["iid"] ** 2 + se_b["gue"] ** 2) ** 0.5,
    "max |z_gls - z_boot| / z_boot over the shrinkage sweep":
        max(abs(z - d["z"]["bootstrap"]) / d["z"]["bootstrap"]
            for z in d["z"]["gls_sweep"]),
    "median |pearson r| over fit-window k-pairs, GUE": d["correlation"]["gue"]["value"],
    "recovered-vs-banked mismatches (80 numbers)": float(d["p1_mismatches"]),
}
for name, want in rec.items():
    got = d["bars"][name]["value"]
    if abs(got - want) > 1e-9 * max(abs(want), 1.0):
        bad.append(f"bar '{name}': banked {got!r}, re-derived {want!r}")
if abs(d["ratios"]["gue"] - se_b["gue"] / se_i["gue"]) > 1e-12:
    bad.append("ratios.gue does not re-derive from the stored SEs")

# 3. the miss is preserved
c4 = d["bars"]["max |z_gls - z_boot| / z_boot over the shrinkage sweep"]
if c4["met"]:
    bad.append("C4 now reads MET. It MISSED (0.349 vs 0.25) and that miss is the "
               "reason this cell reports a RANGE rather than a number; a MET here "
               "without the numbers moving would be the disagreement tuned away")
c2 = d["bars"]["sigma_boot(beta_GUE) / sigma_indep(beta_GUE)"]
if not c2["met"]:
    bad.append("C2 now reads MISSED — the tightening result has changed sign")

# 4. the decision is invariant across every treatment
zs = ([d["z"]["bootstrap"], d["z"]["sealed_recomputed"],
       d["z"]["conservative_convention"]] + list(d["z"]["gls_sweep"]))
below = [z for z in zs if z < 5.0]
if below:
    bad.append(f"a treatment falls below the sealed 5-sigma bar: {below} — the "
               "decision is no longer invariant and the headline changes")
if d["verdict"] != "SHAPE_Z_SURVIVES_THE_CORRELATED_ERROR_MODEL":
    bad.append(f"verdict is {d['verdict']!r}")

print(f"  recovery: {d['p1_mismatches']} of 80 mismatched; sealed z re-derived "
      f"{d['z']['sealed_recomputed']:.6f}")
print(f"  sigma ratios (boot/indep): gue {d['ratios']['gue']:.4f} (tightens), "
      f"iid {d['ratios']['iid']:.4f} (loosens)")
print(f"  z(beta) across treatments: {min(zs):.3f} - {max(zs):.3f}; "
      f"{len(zs) - len(below)} of {len(zs)} clear the 5.0 bar"
      + ("" if not below else f"  <-- {len(below)} BELOW"))
print(f"  C4 stands MISSED at {c4['value']:.4f} vs {c4['thresh']} — the range, "
      f"not a point value, is what this cell licenses")

if bad:
    print("VERIFY_ZBETA_CORRELATED_ERROR: FAIL")
    for b in bad:
        print("  *", b)
    sys.exit(1)
print("VERIFY_ZBETA_CORRELATED_ERROR: PASS — recovery identity holds, bars "
      "re-derive, the C4 miss is preserved, and the decision is invariant across "
      "all seven treatments")

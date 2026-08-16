"""RIGID_GUE arc measurement (cells R1-R5).  COMMITTED GENERATOR of
rigidgate/gate_measured.json.  Post-seal; every threshold from the seal."""

import hashlib
import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/rigidgate")

SEAL = json.load(open(f"{ROOT}/rigidgate/prereg_sealed.json"))
for f, sha in SEAL["code_freeze_blob_shas"].items():
    d = open(f"{ROOT}/rigidgate/{f}", "rb").read()
    assert hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest() == sha, \
        f"FREEZE VIOLATION {f}"

import gate_probe as G                                          # noqa: E402
from proposed_rule import rigid_cell, deployed_cell             # noqa: E402

DEG = SEAL["lens_deg"]
NS = SEAL["band_seeds"]
CONFIGS = {k: tuple(v) for k, v in SEAL["configs"].items()}
OUT = dict(seal_cited="rigidgate/prereg_sealed.json")


def zeta_unfolded():
    z = np.load(f"{ROOT}/zeros_2000.npy")
    return (z / (2 * np.pi)) * np.log(np.maximum(z / (2 * np.pi * np.e),
                                                 1.0)) + 7.0 / 8.0


# ── R1 band validity vs analytic ────────────────────────────────────────────
print("R1 band validity", flush=True)
r1 = {}
for name, (n, L) in CONFIGS.items():
    gue_b, _ = G.bands(n, L, NS, DEG)
    gm = gue_b["sigma2"]["mean"]
    an = G.sigma2_gue_analytic(L)
    ren = G.decoy_sample("renewal", n, L, 40, 5_000, DEG)
    ran = G.sigma2_renewal_analytic(L)
    r1[name] = dict(gue_measured=float(gm), gue_analytic=float(an),
                    gue_rel_dev=float(abs(gm - an) / an),
                    renewal_measured=float(ren.mean()),
                    renewal_analytic=float(ran),
                    renewal_rel_dev=float(abs(ren.mean() - ran) / ran))
    print(f"  {name}: GUE {gm:.4f} vs {an:.4f} ({r1[name]['gue_rel_dev']:.1%}) "
          f"| renewal {ren.mean():.3f} vs {ran:.3f} "
          f"({r1[name]['renewal_rel_dev']:.1%})", flush=True)
r1_pass = all(v["gue_rel_dev"] <= SEAL["r1_band_tolerance"]
              and v["renewal_rel_dev"] <= SEAL["r1_band_tolerance"]
              for v in r1.values())
OUT["R1"] = dict(rows=r1, PASS=bool(r1_pass))

# ── R2 error rates on the calibrated decoy family ───────────────────────────
print("R2 error rates", flush=True)
r2 = {}
for name, (n, L) in CONFIGS.items():
    gue_b, _ = G.bands(n, L, NS, DEG)
    b = G.gue_boundary(gue_b, SEAL["mult"])
    ren = G.decoy_sample("renewal", n, L, SEAL["r2_draws"]["renewal"],
                         51_000, DEG)
    g = G.gue_sample(n, L, SEAL["r2_draws"]["gue"], 52_000, DEG)
    p = np.array([G.sigma2(G.poisson_positions(
        n, np.random.default_rng(53_000 + k)), L, DEG)
        for k in range(SEAL["r2_draws"]["poisson"])])
    sd = ren.std(ddof=1)
    r2[name] = dict(
        boundary=float(b),
        renewal_mean=float(ren.mean()), renewal_sd=float(sd),
        renewal_min=float(ren.min()), renewal_n=int(ren.size),
        margin_sigma=float((ren.mean() - b) / sd),
        false_rigid_rate=float(np.mean(ren <= b)),
        gue_rigid_rate=float(np.mean(g <= b)),
        poisson_rigid_rate=float(np.mean(p <= b)))
    print(f"  {name}: renewal {ren.mean():.2f}+-{sd:.2f} vs boundary "
          f"{b:.3f} -> margin {r2[name]['margin_sigma']:.1f}sigma, "
          f"false-RIGID {r2[name]['false_rigid_rate']:.3f}", flush=True)
OUT["R2"] = dict(rows=r2,
                 PASS=bool(all(v["false_rigid_rate"] <= 0.01
                               for v in r2.values())))

# ── R3 adversarial marginal-exact family + hyper-rigid calibrators ──────────
print("R3 adversarial battery", flush=True)
n, L = CONFIGS["C-zeta"]
gue_b, _ = G.bands(n, L, NS, DEG)
band = gue_b["sigma2"]
b = G.gue_boundary(gue_b, SEAL["mult"])
fgrid = {}
for f in SEAL["r3_family"]["antithetic_f_grid"]:
    vals = G.decoy_sample("antithetic", n, L,
                          SEAL["r3_family"]["draws_per_f"], 61_000, DEG, f=f)
    fgrid[str(f)] = dict(mean=float(vals.mean()), sd=float(vals.std(ddof=1)),
                         rigid_rate=float(np.mean(vals <= b)))
    print(f"  antithetic f={f}: Sigma2 {vals.mean():.3f} "
          f"RIGID-rate {fgrid[str(f)]['rigid_rate']:.2f}", flush=True)
# bisect f* where the family crosses the boundary
lo, hi = 0.0, 1.0
for _ in range(12):
    mid = 0.5 * (lo + hi)
    v = G.decoy_sample("antithetic", n, L, 8, 62_000, DEG, f=mid).mean()
    if v <= b:
        lo = mid
    else:
        hi = mid
fstar = lo
# NNS identity: same seed, renewal vs antithetic -> identical KS
rng_a = np.random.default_rng(63_000)
s = G.wigner_spacings(n, rng_a)
ks_ren = G.ks_gue_of(np.cumsum(s))
ks_anti = G.ks_gue_of(np.cumsum(G.antithetic_order(s.copy())))
extras = {}
for tag, pos in (("clock", np.arange(n, dtype=float)),
                 ("jitter_clock_0.1",
                  np.sort(np.arange(n) + np.random.default_rng(7).normal(
                      0, 0.1, n))),
                 ("cumulant", G.cumulant_decoy(
                     n, np.random.default_rng(64_000)))):
    v = G.sigma2(pos, L, DEG)
    dep, z = deployed_cell(v, band, SEAL["mult"])
    prop, _ = rigid_cell(v, band, SEAL["mult"])
    extras[tag] = dict(sigma2=float(v), z=float(z), deployed=dep,
                       proposed=prop, ks_gue=G.ks_gue_of(pos))
    print(f"  {tag}: Sigma2={v:.4f} z={z:+.2f} deployed={dep} "
          f"proposed={prop}", flush=True)
OUT["R3"] = dict(f_grid=fgrid, f_star=float(fstar),
                 nns_identity=dict(ks_renewal=ks_ren, ks_antithetic=ks_anti,
                                   identical=bool(ks_ren == ks_anti)),
                 extras=extras, boundary=float(b), config="C-zeta")
print(f"  f* = {fstar:.4f}; NNS-KS renewal {ks_ren:.6f} vs antithetic "
      f"{ks_anti:.6f} identical={ks_ren == ks_anti}", flush=True)

# ── R4 materiality on banked rows (REPORTED, NOT APPLIED) ───────────────────
print("R4 banked-row materiality (reported, not applied)", flush=True)
r4 = {}
br = SEAL["r4_banked_rows"]["brocot_golden"]
band_br = dict(mean=br["gue_mean"], sd=br["sd_reconstructed"])
dep_br, z_br = deployed_cell(br["sigma2"], band_br, SEAL["mult"])
prop_br, _ = rigid_cell(br["sigma2"], band_br, SEAL["mult"])
r4["brocot_golden"] = dict(z=float(z_br), deployed=dep_br, proposed=prop_br,
                           moves=bool(dep_br != prop_br))
zn = zeta_unfolded()
gue_z, _ = G.bands(2000, 40.0, NS, DEG)
bz = gue_z["sigma2"]
v_zeta = G.sigma2(zn, 40.0, DEG)
dep_z, z_z = deployed_cell(v_zeta, bz, SEAL["mult"])
prop_z, _ = rigid_cell(v_zeta, bz, SEAL["mult"])
lens = {}
for deg in (3, 6, 10, 15):
    vv = G.sigma2(zn, 40.0, deg)
    lens[f"deg{deg}"] = dict(sigma2=float(vv),
                             z=float((vv - bz["mean"]) / bz["sd"]),
                             proposed=rigid_cell(vv, bz, SEAL["mult"])[0])
r4["zeta_first_2000"] = dict(sigma2=float(v_zeta), z=float(z_z),
                             deployed=dep_z, proposed=prop_z,
                             moves=bool(dep_z != prop_z), lens_sweep=lens)
for k, v in r4.items():
    print(f"  {k}: z={v['z']:+.2f} deployed={v['deployed']} "
          f"proposed={v['proposed']} MOVES={v['moves']}", flush=True)
OUT["R4"] = r4

# ── R5 proposed-rule validation battery (both arms must move correctly) ─────
print("R5 proposed-rule battery", flush=True)
bat = {}
cases = {
    "gue": G.gue_positions(n, np.random.default_rng(71_000)),
    "poisson": G.poisson_positions(n, np.random.default_rng(72_000)),
    "renewal": G.DECOYS["renewal"](n, np.random.default_rng(73_000)),
    "antithetic_fstar": G.antithetic_renewal(n, fstar,
                                             np.random.default_rng(74_000)),
    "clock": np.arange(n, dtype=float),
    "jitter_clock": np.sort(np.arange(n)
                            + np.random.default_rng(7).normal(0, 0.1, n)),
    "zeta": zn,
}
for tag, pos in cases.items():
    v = G.sigma2(pos, L, DEG)
    dep, z = deployed_cell(v, band, SEAL["mult"])
    prop, _ = rigid_cell(v, band, SEAL["mult"])
    bat[tag] = dict(sigma2=float(v), z=float(z), deployed=dep, proposed=prop)
    print(f"  {tag}: z={z:+.2f} deployed={dep} proposed={prop}", flush=True)
bat["brocot"] = dict(sigma2=br["sigma2"], z=float(z_br), deployed=dep_br,
                     proposed=prop_br)
# sensitivity/specificity: both arms, measured
keep_ok = bat["gue"]["proposed"] == "RIGID_GUE"
reject_ok = all(bat[t]["proposed"] != "RIGID_GUE"
                for t in ("clock", "jitter_clock", "antithetic_fstar"))
OUT["R5"] = dict(battery=bat, keeps_gue=bool(keep_ok),
                 rejects_hyper_spoofs=bool(reject_ok),
                 no_specificity_cost=bool(
                     OUT["R2"]["rows"]["C-zeta"]["gue_rigid_rate"] >= 0.95))

# ── verdict ─────────────────────────────────────────────────────────────────
hole = any(v["deployed"] == "RIGID_GUE" for v in
           list(OUT["R3"]["extras"].values())) or \
    OUT["R3"]["f_grid"]["0.0"]["rigid_rate"] > 0
if OUT["R1"]["PASS"] and OUT["R2"]["PASS"] and hole:
    verdict = "GATE_BOUNDED"
elif OUT["R1"]["PASS"] and OUT["R2"]["PASS"]:
    verdict = "GATE_SOUND"
else:
    verdict = "GATE_DEFECTIVE"
OUT["verdict"] = dict(
    primary=verdict,
    hole_demonstrated=bool(hole),
    scope="RIGID_GUE as deployed means 'not floppier than GUE', not "
          "'consistent with GUE'.",
    fix_validated=bool(keep_ok and reject_ok))
json.dump(OUT, open(f"{ROOT}/rigidgate/gate_measured.json", "w"), indent=1)
print(f"VERDICT: {verdict} | hole={hole} | fix keeps GUE={keep_ok} "
      f"rejects spoofs={reject_ok}", flush=True)

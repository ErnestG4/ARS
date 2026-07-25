"""
ARS-RH Phase 5 — height attribution of the low-gamma rigidity excess, and re-derivation
(or deletion) of P1's corroboration line.

Seal: seals/PHASE5_SEAL.json, committed pre-run (b5ac6fb). Opens LOOK_REGISTER R-010.
§0: nothing here estimates Lambda; nothing bears on RH.
§0d: Sigma^2 and <r~> are different families -> two witnesses ON THE ATTRIBUTION QUESTION,
     NOT two independent witnesses (one block read twice).

Gates run before any zeta reading:
  G1 separation  -- the N=500 bracket must be tight enough to resolve the effect
  G2 powered falsifier -- a DESIGNED heterogeneous synthetic the decomposition must localize
"""
from __future__ import annotations
import json, math, os
import numpy as np
from taskB_falpha import (rvm_N, exact_N, exact_N_inv, sigma2, gue_unit, poisson_unit,
                          superrigid_unit, HERE, ROOT)

RNG = np.random.default_rng(20260726)
p = lambda *a: print(*a, flush=True)
Ls = np.array([1, 2, 4, 8], float)
B = 20
OUT = {"anti_claim": "height attribution of an instrument reading; NOT about RH",
       "seal": "seals/PHASE5_SEAL.json"}


def mean_rtilde(x):
    s = np.diff(np.sort(x)); s = s[s > 0]
    r = np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])
    return float(r.mean())


def on_backbone(unit_levels, t_lo):
    """Impose unit-density levels on zeta's EXACT-theta density backbone starting at t_lo."""
    return exact_N_inv(float(exact_N(np.array([t_lo]))[0]) + unit_levels)


def bracket(kind, n, t_lo, B=B):
    """Curvature-matched band for a sub-block: kind fluctuations on ITS OWN backbone."""
    gen = {"GUE": gue_unit, "Poisson": poisson_unit, "superrigid": superrigid_unit}[kind]
    s2, rt = [], []
    for _ in range(B):
        raw = on_backbone(gen(n), t_lo)
        s2.append(sigma2(rvm_N(raw), Ls))
        rt.append(mean_rtilde(raw))
    s2 = np.array(s2)
    return {"s2_mean": s2.mean(0), "s2_sd": s2.std(0),
            "rt_mean": float(np.mean(rt)), "rt_sd": float(np.std(rt))}


z6 = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
blk = z6[:2000]

p("=== ARS-RH Phase 5 — height attribution ===")
p("seal: seals/PHASE5_SEAL.json (committed pre-run)\n")

# =============================================================== G1 separation gate
p("[G1] separation gate — is the N=500 bracket tight enough to resolve the effect?")
g1 = bracket("GUE", 500, float(blk[0]))
sd1 = float(g1["s2_sd"][0])
full_gap = 0.3433 - 0.3112     # full-block curved-GUE mean minus zeta, at L=1 (Task B D5)
p(f"  curved-GUE band at N=500, L=1: mean {g1['s2_mean'][0]:.4f}  sd {sd1:.4f}")
p(f"  full-block gap to match: {full_gap:.4f}  ->  {full_gap/sd1:.2f} sigma per sub-block")
G1 = sd1 < 0.016
p(f"  G1 (sd < 0.016 and gap >= 2 sigma): {'PASS' if G1 else 'FAIL'}\n")
OUT["G1"] = {"band_sd_L1_N500": sd1, "full_block_gap": full_gap,
             "sigma_per_subblock": full_gap / sd1, "pass": bool(G1)}
if not G1:
    json.dump(OUT, open(os.path.join(HERE, "phase5_attribution_measured.json"), "w"), indent=2, default=float)
    raise SystemExit("G1 FAILED — compute-blocked, no zeta reading")

# =============================================================== G2 powered falsifier
p("[G2] powered falsifier — a DESIGNED heterogeneous synthetic the decomposition must localize")
p("     construction: sub-block 1 super-rigid, sub-blocks 2-4 GUE, on zeta's exact-theta backbone")


def build_designed():
    """500 super-rigid levels then 1500 GUE levels, concatenated in UNIT density, then imposed."""
    u1 = superrigid_unit(500)
    u2 = gue_unit(1500)
    u = np.concatenate([u1, u1[-1] + 1.0 + u2])
    return on_backbone(u, float(blk[0]))


def decompose(raw, nsub=4):
    """Per sub-block: Sigma^2 and <r~> against a bracket built on that sub-block's own backbone."""
    raw = np.sort(raw)
    n = len(raw) // nsub
    rows = []
    for i in range(nsub):
        sb = raw[i * n:(i + 1) * n]
        bd = bracket("GUE", len(sb), float(sb[0]))
        s2 = sigma2(rvm_N(sb), Ls)
        rt = mean_rtilde(sb)
        rows.append({"i": i, "gamma_lo": float(sb[0]), "gamma_mid": float(sb[len(sb) // 2]),
                     "gamma_hi": float(sb[-1]), "n": len(sb),
                     "sigma2": s2.tolist(), "band_mean": bd["s2_mean"].tolist(),
                     "band_sd": bd["s2_sd"].tolist(),
                     "dev_over_sd": ((s2 - bd["s2_mean"]) / bd["s2_sd"]).tolist(),
                     "rtilde": rt, "rt_null_mean": bd["rt_mean"], "rt_null_sd": bd["rt_sd"],
                     "rt_dev_over_sd": (rt - bd["rt_mean"]) / bd["rt_sd"]})
    return rows


des = decompose(build_designed())
p(f"  {'sub':>4s} {'gamma_mid':>10s} {'Sig2 dev/sd @L=1':>17s} {'@L=8':>8s}")
for r in des:
    p(f"  {r['i']+1:>4d} {r['gamma_mid']:>10.1f} {r['dev_over_sd'][0]:>17.2f} {r['dev_over_sd'][3]:>8.2f}")
G2 = des[0]["dev_over_sd"][0] < -3.0 and all(abs(r["dev_over_sd"][0]) < 2.0 for r in des[1:])
p(f"  G2 (sub-1 < -3 sigma, sub-2..4 within +/-2 sigma): {'PASS' if G2 else 'FAIL'}\n")
OUT["G2"] = {"rows": des, "pass": bool(G2)}
if not G2:
    json.dump(OUT, open(os.path.join(HERE, "phase5_attribution_measured.json"), "w"), indent=2, default=float)
    raise SystemExit("G2 FAILED — the decomposition cannot localize a KNOWN localized signal; halt")

# =============================================================== zeta, 4 x 500
p("[Z] zeta zeros6[:2000], 4 x 500 sub-blocks — WHICH HEIGHT OWNS THE EXCESS?")
zrows = decompose(blk, 4)
p(f"  {'sub':>4s} {'gamma range':>20s} {'gmid':>8s} | " +
  " ".join(f"{'S2@L=%d'%L:>8s}" for L in Ls.astype(int)) + " | " + f"{'<r~> dev':>9s}")
for r in zrows:
    p(f"  {r['i']+1:>4d} {r['gamma_lo']:>8.1f}-{r['gamma_hi']:<11.1f} {r['gamma_mid']:>8.1f} | " +
      " ".join(f"{v:>8.2f}" for v in r["dev_over_sd"]) + " | " + f"{r['rt_dev_over_sd']:>+9.2f}")
p("  (Sigma^2 dev in sd units, negative = MORE rigid than curvature-matched GUE)")
p("  (<r~> dev in sd units, positive = MORE rigid than matched-density GUE null)")
OUT["zeta_4x500"] = zrows

# =============================================================== resolution check 8 x 250
p("\n[R] resolution check — 8 x 250")
zr8 = decompose(blk, 8)
p(f"  {'sub':>4s} {'gmid':>9s} {'S2@L=1':>9s} {'S2@L=4':>9s} {'<r~> dev':>10s}")
for r in zr8:
    p(f"  {r['i']+1:>4d} {r['gamma_mid']:>9.1f} {r['dev_over_sd'][0]:>9.2f} "
      f"{r['dev_over_sd'][2]:>9.2f} {r['rt_dev_over_sd']:>+10.2f}")
OUT["zeta_8x250"] = zr8

# =============================================================== verdict
s2dev = np.array([r["dev_over_sd"][0] for r in zrows])
rtdev = np.array([r["rt_dev_over_sd"] for r in zrows])
gm = np.array([r["gamma_mid"] for r in zrows])
s2_mono = bool(np.all(np.diff(np.abs(s2dev)) < 0))
rt_mono = bool(np.all(np.diff(rtdev) < 0))
H_bottom_s2 = bool(s2dev[0] <= -4.0 and abs(s2dev[-1]) < 2.0)
H_bottom_rt = bool(rtdev[0] >= 2.0 and rtdev[-1] < 1.0)
H_null = bool(np.all(np.abs(s2dev) < 2.0))
H_flat = bool(np.std(s2dev) < 1.0 and not H_null)
p("\n[V] sealed-outcome scoring")
p(f"  Sigma^2 dev@L=1 by sub-block: " + " ".join("%+.2f" % v for v in s2dev))
p(f"  <r~>    dev      by sub-block: " + " ".join("%+.2f" % v for v in rtdev))
p(f"  H_bottom (Sigma^2): {H_bottom_s2}   monotone |dev|: {s2_mono}")
p(f"  H_bottom (<r~>)   : {H_bottom_rt}   monotone dev  : {rt_mono}")
p(f"  H_flat: {H_flat}    H_null: {H_null}")
split = bool(H_bottom_s2 != H_bottom_rt)
p(f"  H_split (families disagree on attribution): {split}")
OUT["verdict"] = {"sigma2_dev_L1": s2dev.tolist(), "rtilde_dev": rtdev.tolist(),
                  "gamma_mids": gm.tolist(), "H_bottom_sigma2": H_bottom_s2,
                  "H_bottom_rtilde": H_bottom_rt, "H_flat": H_flat, "H_null": H_null,
                  "H_split": split, "sigma2_monotone": s2_mono, "rtilde_monotone": rt_mono}

json.dump(OUT, open(os.path.join(HERE, "phase5_attribution_measured.json"), "w"), indent=2, default=float)
p("\nwrote phase5_attribution_measured.json")

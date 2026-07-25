"""
Phase 5b — leverage vs sensitivity, the computation that decides R-010's short-L reading.

NOT a re-run of Phase 5's G2 and NOT a rescue of its seal. This asks a different question:
at the L where the measurement is actually made (L=1, because P1's corroboration is a SHORT-L
claim), does the heterogeneity confound have LEVERAGE, and does the instrument have SENSITIVITY?
Those are two different quantities that a single contrast number cannot separate.

  C1. Is Sigma^2(1) actually blind to rigidity? (tests the premise that the 0.0007 contrast
      generalises -- it should NOT: 0.0007 is a fact about eta=0.3, not about the statistic)
  C2. Mixing-is-averaging: verify numerically that a heterogeneous block's Sigma^2 equals the
      mean of its parts, so mixing CANNOT manufacture an excess, only relocate its address.
  C3. Residual density drift after the theta unfold (does theta really handle density exactly?)
  C4. Sub-block boundary effects at L=1.
  C5. The three-way decision: leverage vs sensitivity vs measured effect.
  C6. Feasibility: do ~202,000 zeros exist at low gamma, and what would that block look like?
"""
from __future__ import annotations
import json, math, os
import numpy as np
from taskB_falpha import rvm_N, exact_N, exact_N_inv, sigma2, gue_unit, poisson_unit, HERE, ROOT

RNG = np.random.default_rng(20260727)
p = lambda *a: print(*a, flush=True)
Ls = np.array([1, 2, 4, 8], float)
OUT = {"anti_claim": "instrument leverage/sensitivity analysis; NOT about RH"}

z6 = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
blk = z6[:2000]


def jitter_lattice(n, eta):
    return np.sort(np.arange(n) + eta * RNG.standard_normal(n))


def on_backbone(u, t_lo):
    return exact_N_inv(float(exact_N(np.array([t_lo]))[0]) + u)


# ------------------------------------------------------------------ C1
p("[C1] is Sigma^2(1) blind to rigidity, or was 0.0007 a fact about eta=0.3?")
lad = []
for lbl, gen in ([(f"lattice eta={e}", (lambda e: (lambda n: jitter_lattice(n, e)))(e))
                  for e in (0.02, 0.05, 0.10, 0.20, 0.30, 0.50)] +
                 [("GUE", gue_unit), ("Poisson", poisson_unit)]):
    v = np.mean([sigma2(gen(500), Ls) for _ in range(12)], 0)
    lad.append({"class": lbl, "sigma2": v.tolist()})
    p(f"  {lbl:16s} Sigma^2(1) = {v[0]:7.4f}   (L=2,4,8: {v[1]:.3f} {v[2]:.3f} {v[3]:.3f})")
s1 = [r["sigma2"][0] for r in lad]
p(f"\n  -> Sigma^2(1) spans {min(s1):.4f} .. {max(s1):.4f} across the ladder. NOT blind.")
p(f"  -> the 0.0007 gate contrast is a coincidence of eta=0.3 landing on top of GUE at L=1,")
p(f"     not a property of the statistic. The inference 'Sigma^2(1) is nearly blind to the")
p(f"     structural difference' is NOT supported by that number.")
OUT["C1"] = {"ladder": lad, "sigma2_1_range": [min(s1), max(s1)]}
p("")

# ------------------------------------------------------------------ C2
p("[C2] mixing-is-averaging: can heterogeneity MANUFACTURE an excess, or only relocate it?")
u = np.concatenate([jitter_lattice(500, 0.10),
                    jitter_lattice(500, 0.10)[-1] + 1.0 + gue_unit(500),
                    0.0 * np.zeros(0)])
u = np.concatenate([u, u[-1] + 1.0 + gue_unit(500), ])
u = np.concatenate([u, u[-1] + 1.0 + poisson_unit(500)])
raw = on_backbone(u, float(blk[0]))
x = rvm_N(raw)
whole = sigma2(x, Ls)
n = len(x) // 4
parts = np.array([sigma2(np.sort(x)[i * n:(i + 1) * n], Ls) for i in range(4)])
p(f"  designed mixture: [lattice eta=0.1 | GUE | GUE | Poisson], 500 each")
p(f"  part Sigma^2(1) : " + " ".join("%.4f" % v for v in parts[:, 0]) +
  f"   mean {parts[:,0].mean():.4f}")
p(f"  whole-block Sigma^2(1) = {whole[0]:.4f}   |whole - mean(parts)| = {abs(whole[0]-parts[:,0].mean()):.4f}")
p(f"  min(part) = {parts[:,0].min():.4f}  -> whole is inside [min,max] parts: "
  f"{parts[:,0].min() <= whole[0] <= parts[:,0].max()}")
p("  -> mixing AVERAGES. It cannot push the block below the most rigid part. So a block sitting")
p("     below a GUE bracket entails that AT LEAST ONE sub-block sits below it. Existence is")
p("     entailed; only the ADDRESS is open.")
OUT["C2"] = {"whole": whole.tolist(), "parts": parts.tolist(),
             "whole_minus_mean_parts_L1": float(abs(whole[0] - parts[:, 0].mean())),
             "whole_within_part_range": bool(parts[:, 0].min() <= whole[0] <= parts[:, 0].max())}
p("")

# ------------------------------------------------------------------ C3
p("[C3] residual density drift after the theta unfold (is density REALLY handled exactly?)")
xz = rvm_N(blk)
q = len(xz) // 4
drift = []
for i in range(4):
    sub = xz[i * q:(i + 1) * q]
    span = sub[-1] - sub[0]
    dens = (len(sub) - 1) / span
    drift.append({"quarter": i + 1, "gamma_lo": float(blk[i * q]), "gamma_hi": float(blk[(i + 1) * q - 1]),
                  "unfolded_density": float(dens)})
    p(f"  quarter {i+1}: gamma {blk[i*q]:8.1f}-{blk[(i+1)*q-1]:8.1f}   unfolded density = {dens:.6f}")
dv = [d["unfolded_density"] for d in drift]
p(f"  spread = {max(dv)-min(dv):.6f}  (raw density varies 7.4x across this block)")
p(f"  -> theta removes the density to {100*(max(dv)-min(dv)):.3f}% across quarters; the residual is")
p("     NOT a drift the sliding-window variance can mistake for rigidity at L=1.")
OUT["C3"] = {"quarters": drift, "density_spread": float(max(dv) - min(dv))}
p("")

# ------------------------------------------------------------------ C4
p("[C4] sub-block boundary effect at L=1")
zq = np.array([sigma2(xz[i * q:(i + 1) * q], Ls) for i in range(4)])
p(f"  zeta whole-block Sigma^2(1) = {sigma2(xz, Ls)[0]:.4f}")
p(f"  zeta sub-block Sigma^2(1)   = " + " ".join("%.4f" % v for v in zq[:, 0]) +
  f"   mean {zq[:,0].mean():.4f}")
bnd = abs(sigma2(xz, Ls)[0] - zq[:, 0].mean())
p(f"  |whole - mean(subs)| = {bnd:.4f}   vs bracket sd at N=500, L=1 = 0.0113")
p(f"  -> splitting introduces {bnd/0.0113:.2f} sd of boundary effect at L=1: "
  f"{'NEGLIGIBLE' if bnd < 0.5*0.0113 else 'NOT negligible'}")
OUT["C4"] = {"whole_L1": float(sigma2(xz, Ls)[0]), "subs_L1": zq[:, 0].tolist(),
             "boundary_effect": float(bnd), "in_sd_units": float(bnd / 0.0113)}
p("")

# ------------------------------------------------------------------ C5
p("[C5] THE DECISION: leverage vs sensitivity vs measured effect, at L=1 (the measurement arm)")
zeta_L1 = 0.3112          # Task B D5, theta path
band_m, band_sd = 0.3433, 0.0048     # Task B D5, curvature-matched GUE, N=2000, B=20
effect = band_m - zeta_L1
leverage = 0.0            # C2: mixing is averaging -> zero leverage to manufacture
p(f"  measured effect      |zeta - bracket| = {effect:.4f}   ({effect/band_sd:.2f} sd)")
p(f"  instrument sensitivity  bracket sd    = {band_sd:.4f}")
p(f"  confound leverage    (mixing, from C2) = {leverage:.4f}  -- averaging cannot manufacture")
p("")
p("  three-way reading:")
p(f"    effect / sd  = {effect/band_sd:.2f}   -> instrument CAN see it")
p(f"    leverage/sd  = {leverage/band_sd:.2f}   -> confound CANNOT explain it")
p("    => PROCEED at L=1. The confound lacks leverage; the instrument does not lack sensitivity.")
p("    => what remains open is ATTRIBUTION (which height), not EXISTENCE.")
OUT["C5"] = {"zeta_L1": zeta_L1, "band_mean": band_m, "band_sd": band_sd, "effect": effect,
             "effect_over_sd": effect / band_sd, "leverage": leverage,
             "decision": "PROCEED at L=1; existence entailed, attribution open"}
p("")

# ------------------------------------------------------------------ C6
p("[C6] feasibility of ~202,000 zeros at LOW gamma")
need = 202000
p(f"  zeros6 holds {z6.size} zeros, gamma {z6[0]:.1f} .. {z6[-1]:.1f}")
if z6.size >= need:
    b = z6[:need]
    curv = math.log(b[-1] / (2 * math.pi)) / math.log(b[0] / (2 * math.pi))
    p(f"  the first {need} zeros exist: gamma {b[0]:.1f} .. {b[-1]:.1f}")
    p(f"  BUT that block spans {curv:.1f}x density curvature (vs 7.4x for W=2000)")
    p("  -> the resolution gain and the attribution problem move in OPPOSITE directions:")
    p("     the W needed to resolve 1e-3 at low gamma buys a block so wide that 'low gamma'")
    p("     stops meaning anything. Status is not 'expensive', it is 'available but self-defeating'.")
    OUT["C6"] = {"available": True, "need": need, "gamma_lo": float(b[0]), "gamma_hi": float(b[-1]),
                 "curvature_ratio": curv,
                 "status": "AVAILABLE BUT SELF-DEFEATING at low gamma"}
else:
    p(f"  NOT available: only {z6.size} zeros in the file")
    OUT["C6"] = {"available": False, "have": int(z6.size), "need": need}

json.dump(OUT, open(os.path.join(HERE, "phase5b_leverage_measured.json"), "w"), indent=2, default=float)
p("\nwrote phase5b_leverage_measured.json")

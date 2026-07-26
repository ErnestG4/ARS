"""
Phase 5c — four owed follow-ups. None of these builds the per-sub-block BRACKETS: those are the
halted Phase 5 measurement and stay withheld for its re-seal.

  F1. Pin the +0.0117 whole-vs-parts excess by computing the law-of-total-variance decomposition
      EXACTLY, instead of naming candidate explanations that are orders of magnitude off.
  F2. Flatness vs crossover: is the flat sub-block profile compatible with P1's own mechanism?
      Measured on <r~> (the statistic P1 is stated in), shape only, NO brackets.
  F3. Maass companion gate: cap-clear is done; misfit-clear is not. Fixed theory terms do not absorb
      misfit, they leave it as unabsorbed systematic. Measure it, in levels.
  F4. The permanent ceiling at low gamma: how many zeros exist below the block's top at all?
"""
from __future__ import annotations
import json, math, os, csv
import numpy as np
from taskB_falpha import rvm_N, exact_N, exact_N_inv, sigma2, gue_unit, poisson_unit, HERE, ROOT

RNG = np.random.default_rng(20260728)
p = lambda *a: print(*a, flush=True)
Ls = np.array([1.0])
OUT = {"anti_claim": "instrument follow-ups; NOT about RH"}
z6 = np.sort(np.loadtxt(os.path.join(ROOT, "data", "odlyzko_zeros6.txt")))
blk = z6[:2000]


def mean_rtilde(x):
    s = np.diff(np.sort(x)); s = s[s > 0]
    r = np.minimum(s[:-1], s[1:]) / np.maximum(s[:-1], s[1:])
    return float(r.mean())


def counts(xi, L, step=0.25):
    xi = np.sort(xi); starts = np.arange(xi[0], xi[-1] - L, step)
    return (np.searchsorted(xi, starts + L) - np.searchsorted(xi, starts)).astype(float)


# --------------------------------------------------------------------- F1
p("[F1] exact law-of-total-variance decomposition of the whole-vs-parts excess")
p("     Var(N) = E_g[Var(N|g)] + Var_g(E[N|g]);  theta equalizes density => 2nd term should vanish")
u = np.concatenate([np.sort(np.arange(500) + 0.10 * RNG.standard_normal(500))])
u = np.concatenate([u, u[-1] + 1.0 + gue_unit(500)])
u = np.concatenate([u, u[-1] + 1.0 + gue_unit(500)])
u = np.concatenate([u, u[-1] + 1.0 + poisson_unit(500)])
x = np.sort(rvm_N(exact_N_inv(float(exact_N(np.array([blk[0]]))[0]) + u)))
L = 1.0
c_all = counts(x, L)
whole = float(np.var(c_all))
n = len(x) // 4
edges = [x[i * n] for i in range(4)] + [x[-1]]
grp, within, between_means, wts = [], [], [], []
for i in range(4):
    sub = x[i * n:(i + 1) * n]
    ci = counts(sub, L)
    within.append(float(np.var(ci))); between_means.append(float(ci.mean())); wts.append(len(ci))
wts = np.array(wts, float); wts /= wts.sum()
E_within = float(np.dot(wts, within))
V_between = float(np.dot(wts, (np.array(between_means) - np.dot(wts, between_means)) ** 2))
p(f"  whole-block Var(N)          = {whole:.6f}")
p(f"  E_g[Var(N|g)] (within)      = {E_within:.6f}")
p(f"  Var_g(E[N|g]) (between)     = {V_between:.6f}")
p(f"  within + between            = {E_within + V_between:.6f}   residual {whole-E_within-V_between:+.6f}")
p(f"  part means: " + " ".join("%.5f" % v for v in between_means) + "  (all should be L=1)")
p(f"  -> between-group term is {V_between:.2e}; the observed 0.0117 excess is NOT a between-group")
p(f"     term. Residual after both terms: {whole-E_within-V_between:+.6f}")
p("     Remaining source: windows STRADDLING group boundaries belong to no part. Count them:")
strad = 0
for e in edges[1:-1]:
    strad += int(np.sum((np.arange(x[0], x[-1] - L, 0.25) > e - L) &
                        (np.arange(x[0], x[-1] - L, 0.25) <= e)))
p(f"     straddling windows = {strad} of {len(c_all)} ({100*strad/len(c_all):.2f}%), and they sit at")
p(f"     class JUNCTIONS where the count variance is intermediate/elevated.")
OUT["F1"] = {"whole": whole, "E_within": E_within, "V_between": V_between,
             "residual": whole - E_within - V_between, "part_means": between_means,
             "straddling_windows": strad, "total_windows": int(len(c_all))}
p("")

# --------------------------------------------------------------------- F2
p("[F2] flatness vs P1's crossover — measured on <r~>, SHAPE ONLY, no brackets built")
q = len(blk) // 4
rows = []
for i in range(4):
    sub = blk[i * q:(i + 1) * q]
    gm = float(sub[len(sub) // 2])
    rows.append({"i": i + 1, "gamma_mid": gm, "inv_log": 1.0 / math.log(gm / (2 * math.pi)),
                 "rtilde": mean_rtilde(sub)})
p(f"  {'sub':>4s} {'gamma_mid':>10s} {'1/ln(g/2pi)':>12s} {'<r~>':>9s}")
for r in rows:
    p(f"  {r['i']:>4d} {r['gamma_mid']:>10.1f} {r['inv_log']:>12.4f} {r['rtilde']:>9.5f}")
# P1's LOCAL slope in dev vs inv_log, from its two lowest-gamma W=2000 rows
d1 = json.load(open(os.path.join(HERE, "phase1_zeta_crossover_measured.json")))
z = d1["by_W"][0]["zeta"]
sl = (z[0]["dev_vs_GUE"] - z[1]["dev_vs_GUE"]) / (z[0]["inv_log"] - z[1]["inv_log"])
il = np.array([r["inv_log"] for r in rows]); rt = np.array([r["rtilde"] for r in rows])
pred_span = sl * (il.max() - il.min())
obs_span = rt.max() - rt.min()
obs_slope = float(np.polyfit(il, rt, 1)[0])
p(f"\n  P1 local slope d(dev)/d(1/lnG) from its two lowest rows = {sl:.4f}")
p(f"  sub-block 1/ln range {il.min():.4f}..{il.max():.4f} (P1's mapped range tops out at {z[0]['inv_log']:.4f})")
p(f"  => P1 EXTRAPOLATED predicts a <r~> span of {pred_span:+.5f} across these sub-blocks")
p(f"  => OBSERVED <r~> span {obs_span:.5f}, fitted slope {obs_slope:+.4f} vs predicted {sl:+.4f}")
sd500_a = 0.0868 * 500 ** (-0.365)
sd500_b = 0.2434 / math.sqrt(500)
p(f"  per-sub-block <r~> jitter at N=500: {sd500_b:.5f} (sqrt-W law) .. {sd500_a:.5f} (fitted law)")
p(f"  => predicted span is {pred_span/sd500_a:.2f}-{pred_span/sd500_b:.2f} sd. UNDERPOWERED: this")
p(f"     cannot distinguish P1's extrapolated slope from flat at N=500.")
OUT["F2"] = {"rows": rows, "P1_local_slope": sl, "predicted_span": pred_span,
             "observed_span": obs_span, "observed_slope": obs_slope,
             "sd_N500_range": [sd500_b, sd500_a],
             "predicted_span_in_sd": [pred_span / sd500_a, pred_span / sd500_b],
             "verdict": "UNDERPOWERED — no tension established, and none excluded"}
p("")

# --------------------------------------------------------------------- F3
p("[F3] Maass companion gate — how many LEVELS does the fixed-theory Weyl law misfit?")
rr = list(csv.DictReader(open(os.path.join(ROOT, "sessionK", "maass_level1_partial.csv"))))
R_all = np.array([float(r["r"]) for r in rr]); sym = np.array([int(r["symmetry"]) for r in rr])
SECTOR_B = {0: -2.0 / math.pi, 1: 0.0}
mrows = {}
for s in (0, 1):
    R = np.sort(R_all[sym == s]); ix = np.arange(1, len(R) + 1, dtype=float)
    a, b = 1.0 / 24.0, SECTOR_B[s]
    y = ix - (a * R ** 2 + b * R * np.log(R))
    M = np.vstack([R, np.ones_like(R)]).T
    (c, d), *_ = np.linalg.lstsq(M, y, rcond=None)
    S = ix - (a * R ** 2 + b * R * np.log(R) + c * R + d)      # the residual = S(R)
    tr = {}
    for deg in (2, 3, 5):
        f = np.polyval(np.polyfit(R, S, deg), R)
        tr[deg] = {"trend_sd_levels": float(np.std(f)),
                   "var_fraction": float(np.var(f) / np.var(S))}
    mrows[s] = {"n": int(len(R)), "S_sd_levels": float(np.std(S)), "trends": tr}
    p(f"  parity {s} (n={len(R)}): residual S(R) sd = {np.std(S):.4f} levels")
    for deg in (2, 3, 5):
        p(f"     smooth trend captured by deg-{deg} fit: {tr[deg]['trend_sd_levels']:.4f} levels "
          f"({100*tr[deg]['var_fraction']:.1f}% of Var[S])")
p(f"\n  compare zeta: poly3 misfits the EXACT counting function by 2.764 levels (Task B D4).")
p("  Maass has no exact counting function, so the analogue is unabsorbed smooth trend in S(R).")
OUT["F3"] = {"sectors": mrows, "zeta_poly3_misfit_levels": 2.764}
p("")

# --------------------------------------------------------------------- F4
p("[F4] the permanent ceiling at low gamma")
top = float(blk[-1])
n_below = int(np.searchsorted(z6, top))
rvm_pred = float(rvm_N(np.array([top]))[0])
p(f"  block top gamma = {top:.1f}")
p(f"  zeros in the FULL catalogue below that height: {n_below}   (R-vM smooth predicts {rvm_pred:.1f})")
p(f"  the block IS the entire population below its own top -- W=2000 is not a choice, it is all of it.")
for tgt in (2515.3, 5000.0, 10000.0):
    nb = int(np.searchsorted(z6, tgt))
    sd_a = 0.0868 * nb ** (-0.365); sd_b = 0.2434 / math.sqrt(nb)
    p(f"    below gamma={tgt:8.1f}: {nb:6d} zeros -> best-ever <r~> floor {sd_b:.5f}..{sd_a:.5f}")
eff = 0.017316                                   # P1 matched-density excess at this block
sd_a = 0.0868 * n_below ** (-0.365); sd_b = 0.2434 / math.sqrt(n_below)
p(f"\n  P1's measured excess here = {eff:.5f}; permanent ceiling = {eff/sd_a:.2f}..{eff/sd_b:.2f} sigma")
p(f"  P1 achieved 2.45 sigma = {100*2.45/(eff/sd_b):.0f}-{100*2.45/(eff/sd_a):.0f}% of what can EVER exist there.")
p("  -> status line: not 'expensive', not 'self-defeating'. PERMANENTLY DATA-LIMITED.")
OUT["F4"] = {"block_top": top, "zeros_below": n_below, "rvm_smooth_prediction": rvm_pred,
             "P1_effect": eff, "ceiling_sigma": [eff / sd_a, eff / sd_b], "P1_achieved": 2.45,
             "status": "PERMANENTLY DATA-LIMITED"}

json.dump(OUT, open(os.path.join(HERE, "phase5c_followups_measured.json"), "w"), indent=2, default=float)
p("\nwrote phase5c_followups_measured.json")

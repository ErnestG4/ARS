# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 post-hoc lead, descriptive (Will 2026-11-02): correlation of the 1e10 residuals of R against C_F with
L'/L(1, chi_D), at beta 0.55, 0.45, 0.40.  Nine fields; no verdict.

Residuals, two definitions (the brief says "R against the C_F rank fit"; both reported):
  lin : R - (a + b C_F), OLS at each beta;
  rank: rank(R) - rank(C_F).
Correlations: Pearson r and Spearman rho with L'/L, two-sided exact permutation p over all 9! orderings.
Also: corr(L'/L, C_F) itself, and the same correlations with -7 removed (n = 8, 8! orderings).
"""
import json, sys, itertools
import numpy as np

read = json.load(open(sys.argv[1]))
lp = json.load(open(sys.argv[2]))
F = sorted(lp, key=lambda k: lp[k]["C_F"])

def ranks(x):
    r = np.empty(len(x)); r[np.argsort(x, kind="stable")] = np.arange(len(x)); return r

def perm_p(x, y, kind):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if kind == "spearman":
        x, y = ranks(x), ranks(y)
    xc = x - x.mean(); yc = y - y.mean()
    obs = xc @ yc / np.sqrt((xc @ xc) * (yc @ yc))
    P = np.array(list(itertools.permutations(range(len(y)))))
    yp = yc[P]
    st = yp @ xc / np.sqrt((xc @ xc) * (yc @ yc))
    return float(obs), float(np.mean(np.abs(st) >= abs(obs) - 1e-12))

def block(fields):
    C = np.array([lp[k]["C_F"] for k in fields]); L = np.array([lp[k]["LpL1"] for k in fields])
    o = {"fields": fields, "corr_LpL_vs_C": dict(zip(("pearson", "p"), perm_p(C, L, "pearson"))),
         "spearman_LpL_vs_C": dict(zip(("rho", "p"), perm_p(C, L, "spearman")))}
    for b in ("0.55", "0.45", "0.40"):
        bk = b if b in read["R"]["-7"] else str(float(b))
        R = np.array([read["R"][k][bk] for k in fields])
        A = np.vstack([np.ones_like(C), C]).T
        coef, *_ = np.linalg.lstsq(A, R, rcond=None)
        lin = R - A @ coef
        rk = ranks(R) - ranks(C)
        o[b] = {"ols_a_b": coef.tolist(),
                "resid_lin": dict(zip(fields, lin.tolist())),
                "resid_rank": dict(zip(fields, rk.tolist())),
                "lin_pearson": dict(zip(("r", "p"), perm_p(L, lin, "pearson"))),
                "lin_spearman": dict(zip(("rho", "p"), perm_p(L, lin, "spearman"))),
                "rank_pearson": dict(zip(("r", "p"), perm_p(L, rk, "pearson"))),
                "rank_spearman": dict(zip(("rho", "p"), perm_p(L, rk, "spearman")))}
    return o

out = {"label": "FN1 post-hoc lead, descriptive (no verdict): 1e10 residuals vs L'/L(1,chi_D)",
       "read_sha256_note": "input READ1.json sha256 47c19dd2...", "all9": block(F),
       "without_-7": block([k for k in F if k != "-7"])}
json.dump(out, open(sys.argv[3], "w"), indent=1, sort_keys=True)
for nm in ("all9", "without_-7"):
    o = out[nm]
    print(nm, "corr(L'/L, C_F): r %.3f p %.4f; rho %.3f p %.4f" % (o["corr_LpL_vs_C"]["pearson"], o["corr_LpL_vs_C"]["p"],
          o["spearman_LpL_vs_C"]["rho"], o["spearman_LpL_vs_C"]["p"]))
    for b in ("0.55", "0.45", "0.40"):
        x = o[b]
        print("  beta", b, "lin: r %+.3f (p %.3f) rho %+.3f (p %.3f) | rank: r %+.3f (p %.3f) rho %+.3f (p %.3f)" % (
            x["lin_pearson"]["r"], x["lin_pearson"]["p"], x["lin_spearman"]["rho"], x["lin_spearman"]["p"],
            x["rank_pearson"]["r"], x["rank_pearson"]["p"], x["rank_spearman"]["rho"], x["rank_spearman"]["p"]))
    if nm == "all9":
        print("  lin resid 0.55:", {k: round(v, 4) for k, v in o["0.55"]["resid_lin"].items()})

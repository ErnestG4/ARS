# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 POST-HOC lead (Will 2026-11-02), item 3: what sign and form Chen et al.'s C_Phi,L piece predicts for the
imaginary quadratic fields, extended from RQ1-b's three-field generalisation (rq1/RQ1B_STEP0.md §2, UNVERIFIED).

Source: Chen, Kim, Lichtman, Miller, Shubina, Sweitzer, Waxman, Winsor, Yang, arXiv:1901.07386 (PDF sha256
920b212b...9162), Conjecture 1.2 (lambda < 1/2): Var/(C_f X^(1-lambda)) = C_Phi (2 lambda log X) - K_Phi,
K_Phi = C_Phi,zeta - C_Phi,L - A'_Phi + 2 pi^2 PhiT(1/2)^2 + C_Phi (log(4 pi^2) - C_F + 2)   [RQ1-b's C_F form].
Field-dependent part of Var/(<psi> log X), in units of 1/log X:  P_F = C_F + (C_Phi,L(D) + A'_Phi(D)) / C_Phi.

(9.26) C_Phi,L = 2 pi i int_(eps') PhiT(1/2+b)PhiT(1/2-b) (L'/L(1+2b)+L'/L(1-2b)) db. For Phi = 1_(0,1], PhiT = 1/s,
the weight on b = it is 1/(1/4+t^2), the Poisson kernel of Re s > 1 at s = 2 (after s = 1+2it), and L'/L(s,chi) is
holomorphic, of log growth, -> 0 as Re s -> oo, so  C_Phi,L = -8 pi^2 L'/L(2, chi)   (sign as printed in 9.26).
Checks: (a) against RQ1-b's independent contour values (results/RQ1B_CONSTANTS.json: zi, zs2, zw) within their tail
bounds; (b) a direct contour on RQ1-b's grid for D = -7 and -11.
Sign note: Appendix A's Mathematica cell for C_Phi,L carries -2 pi i (i NIntegrate) = the NEGATIVE of (9.26) while its
C_Phi,zeta cell carries +2 pi i; RQ1-b used (9.26). Both signs are reported for the residual correlation.
A'_Phi(D): RQ1-b's integrand with F's inert primes (chi_D(p) = -1, p < 1e5). Our statistic excludes inert primes
(Chen's includes them at theta = 0), so P_F is also reported without A'.
"""
import json, math, sys
import numpy as np
import mpmath as mp
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from fn1_lprime import kron  # noqa: E402

FIELDS = {"-7": (-7, 2), "-8": (-8, 2), "-11": (-11, 2), "zi": (-4, 4), "-19": (-19, 2), "zw": (-3, 6),
          "-43": (-43, 2), "-67": (-67, 2), "-163": (-163, 2), "zs2": (8, None)}
CPHI = 4 * math.pi ** 2
mp.mp.dps = 20

def chi_list(D):
    q = abs(D); return [0] + [kron(D, a) for a in range(1, q)]   # mpmath.dirichlet indexes chi[n mod q]

def lpl(s, chi):
    return mp.dirichlet(s, chi, derivative=1) / mp.dirichlet(s, chi)

# RQ1-b grid (identical construction)
EPS, H = 0.1, 0.05
def grid(T):
    TT = np.arange(-T, T + H / 2, H); WS = np.ones(len(TT)); WS[1:-1:2] = 4; WS[2:-1:2] = 2; WS *= H / 3
    B = EPS + 1j * TT; return TT, WS, B, 1 / ((0.5 + B) * (0.5 - B))

def contour_CL(D, T):
    TT, WS, B, PP = grid(T); chi = chi_list(D)
    v = np.array([complex(lpl(1 + 2 * complex(b), chi) + lpl(1 - 2 * complex(b), chi)) for b in B])
    return (2j * math.pi * 1j * np.sum(WS * PP * v)).real, 2 * math.pi * 2 * max(abs(v[0]), abs(v[-1])) / T

def primes(n):
    s = bytearray([1]) * (n + 1); s[:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
PR = primes(100000)
TT, WS, B, PP = grid(200.0)

def A_prime(D):
    p = np.array([q for q in PR if kron(D, q) == -1], np.float64)[:, None]; b = B[None, :]; lp = np.log(p)
    num = (np.exp((2 + 8 * b) * lp) + p ** 2 - 2 * np.exp(4 * b * lp)) * lp
    den = np.exp((2 + 8 * b) * lp) + p ** 2 - np.exp(4 * b * lp) - np.exp((4 + 4 * b) * lp)
    return (-4j * math.pi * 1j * np.sum(WS * PP * (num / den).sum(0))).real, int(p.shape[0])

rq1b = json.load(open(sys.argv[1]))["fields"]
read = json.load(open(sys.argv[2]))
res = {"label": "FN1 POST-HOC: Chen et al. C_Phi,L (and A'_Phi) generalised to the nine fields; UNVERIFIED generalisation",
       "fields": {}, "checks": {}}
for k, (D, w) in FIELDS.items():
    v2 = lpl(2, chi_list(D)).real
    CL = float(-8 * mp.pi ** 2 * v2); AP, nin = A_prime(D)
    Cf = math.log(abs(D) * (w / 2) ** 2) if w else rq1b["zs2"]["C_F"]
    res["fields"][k] = dict(D=D, LpL2=float(v2), C_PhiL=CL, A_prime=AP, inert_primes_used=nin, C_F=Cf,
                            P_full=Cf + (CL + AP) / CPHI, P_noA=Cf + CL / CPHI, Lterm=CL / CPHI, Aterm=AP / CPHI)
for k in ("zi", "zs2", "zw"):
    d = abs(res["fields"][k]["C_PhiL"] - rq1b[k]["C_Phi_L"]); tb = rq1b[k]["tail_bounds"]["C_Phi_L"]
    da = abs(res["fields"][k]["A_prime"] - rq1b[k]["A_prime"])
    res["checks"]["rq1b_" + k] = dict(poisson=res["fields"][k]["C_PhiL"], rq1b_contour=rq1b[k]["C_Phi_L"], absdiff=d,
                                      tail_bound=tb, ok=bool(d <= tb), A_prime_absdiff=da, A_ok=bool(da < 1e-9))
    assert d <= tb and da < 1e-9, res["checks"]["rq1b_" + k]
for k in ("-7", "-11"):
    c, tb = contour_CL(FIELDS[k][0], 100.0); d = abs(c - res["fields"][k]["C_PhiL"])
    res["checks"]["contour_" + k] = dict(contour_T100=c, poisson=res["fields"][k]["C_PhiL"], absdiff=d, tail_bound=tb, ok=bool(d <= tb))
    assert d <= tb, res["checks"]["contour_" + k]

# residual correlations, nine imaginary fields (descriptive; exact permutation p, two-sided)
import itertools
F9 = ["-7", "-8", "-11", "zi", "-19", "zw", "-43", "-67", "-163"]
P = np.array(list(itertools.permutations(range(9))))
def corr_p(x, y):
    x = np.asarray(x) - np.mean(x); y = np.asarray(y) - np.mean(y)
    d = math.sqrt((x @ x) * (y @ y)); r = (x @ y) / d; st = (y[P] @ x) / d
    return float(r), float(np.mean(np.abs(st) >= abs(r) - 1e-12))
logX = math.log(1e10)
C = np.array([res["fields"][k]["C_F"] for k in F9])
for b in ("0.55", "0.45", "0.4"):
    R = np.array([read["R"][k][b] for k in F9]); A = np.vstack([np.ones(9), C]).T
    coef = np.linalg.lstsq(A, R, rcond=None)[0]; resid = R - A @ coef
    o = dict(ols_slope_per_C=float(coef[1]), chen_slope_1_over_logX=1 / logX,
             lambda_chen=math.log(read["K"][b]) / logX)
    for nm, key in (("Lterm_as_9.26", "Lterm"), ("Lterm_plus_A", None)):
        pred = np.array([res["fields"][k]["Lterm"] + (res["fields"][k]["Aterm"] if key is None else 0) for k in F9])
        r, p = corr_p(pred, resid)
        o[nm] = dict(r=r, p=p, pred_over_logX=dict(zip(F9, (pred / logX).tolist())))
        o[nm + "_appendix_sign"] = dict(r=-r if key else corr_p(-np.array([res["fields"][k]["Lterm"] for k in F9]) + np.array([res["fields"][k]["Aterm"] for k in F9]), resid)[0], p=p if key else None)
    o["resid"] = dict(zip(F9, resid.tolist()))
    for nm in ("P_full", "P_noA"):
        Pp = np.array([res["fields"][k][nm] for k in F9]); A2 = np.vstack([np.ones(9), Pp]).T
        c2 = np.linalg.lstsq(A2, R, rcond=None)[0]; r2 = R - A2 @ c2
        o["fit_" + nm] = dict(slope=float(c2[1]), resid_SD=float(r2.std(ddof=2)))
    o["fit_C_F"] = dict(slope=float(coef[1]), resid_SD=float(resid.std(ddof=2)))
    res["beta_" + b] = o
json.dump(res, open(sys.argv[3], "w"), indent=1, sort_keys=True)
for k, v in res["fields"].items():
    print("%5s L'/L(2)=%+.5f C_PhiL=%+8.3f A'=%+7.3f  Lterm=%+.4f Aterm=%+.4f  C_F=%.3f P_full=%.3f P_noA=%.3f" % (
        k, v["LpL2"], v["C_PhiL"], v["A_prime"], v["Lterm"], v["Aterm"], v["C_F"], v["P_full"], v["P_noA"]))
for k, v in res["checks"].items(): print(k, {a: (round(x, 5) if isinstance(x, float) else x) for a, x in v.items()})
for b in ("0.55", "0.45", "0.4"):
    o = res["beta_" + b]
    print("beta", b, "lambda_chen %.3f" % o["lambda_chen"], "OLS slope/C %.4f (1/logX %.4f)" % (o["ols_slope_per_C"], 1 / logX),
          "| r(resid, Lterm) %+.3f p %.3f | r(resid, L+A) %+.3f p %.3f | resid SD: C_F %.4f P_noA %.4f P_full %.4f" % (
          o["Lterm_as_9.26"]["r"], o["Lterm_as_9.26"]["p"], o["Lterm_plus_A"]["r"], o["Lterm_plus_A"]["p"],
          o["fit_C_F"]["resid_SD"], o["fit_P_noA"]["resid_SD"], o["fit_P_full"]["resid_SD"]))

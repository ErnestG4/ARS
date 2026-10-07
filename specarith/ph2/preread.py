"""Phase 2 pre-read (seal PH2_SEAL_2.1 §3–§7): everything that is decided before any Phase-2 zero is read.

  python preread.py g0a          constants and the published (E, N_eff, α, ᾱ) values          -> results/g0a.json
  python preread.py g0b          exact CUE_N (Fredholm) vs Haar draws; BFM appendix values     -> results/g0b.json
  python preread.py g0c          expansion remainder vs exact CUE_N; truncation allowances      -> results/g0c.json

No zero data are read here (g0d, which unfolds CUE surrogates with the exact θ, is separate).
"""
import json
import math
import os
import sys
import time

import numpy as np

import ph2lib as P

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
TWO_PI = 2 * math.pi

# ---------------------------------------------------------------- sealed bins (§3), heights before any data
# (name, kind, log(E/2π) lower, upper); P bins from the pinned files' height ranges, H bins from the table indices.
def _L(E):
    return math.log(E / TWO_PI)


BINS = [
    ("A", "zeros6", 9.4, 10.5),
    ("B", "zeros6", 11.0, 12.1),
    ("P1", "platt", _L(2_546_000), _L(4_646_000)),
    ("P2", "platt", _L(19_346_000), _L(21_446_000)),
    ("P3", "platt", _L(151_646_000), _L(153_746_000)),
    ("P4", "platt", _L(1_119_746_000), _L(1_121_846_000)),
    ("P5", "platt", _L(8_284_946_000), _L(8_287_046_000)),
    ("P6", "platt", _L(30_404_246_000), _L(30_406_346_000)),
    ("H1", "zeros3", 24.48, 24.48),
    ("H2", "zeros4", 44.58, 44.58),
    ("H3", "zeros5", 46.83, 46.83),
]
NEFF_DEN = math.sqrt(12 * P.LAMBDA)


def neff_of_L(L):
    return L / NEFF_DEN


def abar_of_L(L):
    return 1 + 2 * P.Q_CONST / (P.LAMBDA * L)


def dump(name, obj):
    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, name), "w") as f:
        json.dump(obj, f, indent=1, default=float)
    print("wrote", os.path.join(RES, name))


# ---------------------------------------------------------------- G0a
BFM_LAMBDA = "1.57315 10713 24955".replace(" ", "")
BFM_Q = "2.31584 63849 58803".replace(" ", "")
BBLM_PUBLISHED = [  # (E, N_eff, α) as printed in BBLM p. 7 (agent-verified digits in lit/bblm_bk.md)
    (2.5041178e15, 7.7376, 1.0438),
    (1.30664344e22, 11.2976, 1.0300),
]
BFM_P18 = dict(E=1.30664344e22, N="11.29759090", alpha="1.0299900807", abar="1.0599801615")


def g0a():
    k = P.constants(dps=30)
    rows = []
    for E, Np, ap in BBLM_PUBLISHED:
        L = math.log(E / TWO_PI)
        N = neff_of_L(L)
        a = 1 + P.Q_CONST / P.LAMBDA / L
        rows.append(dict(E=E, N_eff=N, alpha=a, N_pub=Np, alpha_pub=ap,
                         ok=bool(abs(N - Np) < 0.6e-4 and abs(a - ap) < 0.6e-4)))
    L = math.log(BFM_P18["E"] / TWO_PI)
    N, a, ab = neff_of_L(L), 1 + P.Q_CONST / P.LAMBDA / L, abar_of_L(L)
    bfm = dict(N=N, alpha=a, abar=ab, pub=BFM_P18,
               ok=bool(abs(N - float(BFM_P18["N"])) < 1e-8 and abs(a - float(BFM_P18["alpha"])) < 1e-10
                       and abs(ab - float(BFM_P18["abar"])) < 1e-10))
    lam_ok = k["Lambda_str"].startswith(BFM_LAMBDA[:15])
    q_ok = k["Q_str"].startswith(BFM_Q[:15])
    out = dict(constants=k, Lambda_bfm=BFM_LAMBDA, Q_bfm=BFM_Q, Lambda_ok=lam_ok, Q_ok=q_ok,
               lib_constants_ok=bool(abs(k["Lambda"] - P.LAMBDA) < 1e-15 and abs(k["Q"] - P.Q_CONST) < 1e-15),
               bblm=rows, bfm_p18=bfm)
    out["PASS"] = bool(lam_ok and q_ok and out["lib_constants_ok"] and all(r["ok"] for r in rows) and bfm["ok"])
    print(json.dumps(out, indent=1, default=float))
    dump("g0a.json", out)


# ---------------------------------------------------------------- G0b
def g0b(n_spacings=2_000_000, seed=20261007):
    det1, om1 = P.fredholm_values(1.0, m=40, abars=(1.0,))
    app = dict(det1=det1, det1_bfm=0.170217421379185, om1=om1[0], om1_bfm=-0.075241982465122)
    app["ok"] = bool(abs(det1 - app["det1_bfm"]) < 1e-12 and abs(om1[0] - app["om1_bfm"]) < 1e-12)
    rng = np.random.default_rng(seed)
    rows = []
    for N in (3, 5, 8, 11):
        S = N - 0.02 if N < 6 else 6.0
        pN, _, EN = P.spacing_tables(S=S, N=N, abars=())
        sp = P.cue_spacings(N, n_spacings // N, rng).ravel()
        # exact CDF F(s) = 1 + E'(s) (E = gap probability, E' = −(1 − F)); KS against it
        g = np.linspace(0, S, 20001)
        Ec = np.polynomial.chebyshev  # noqa: F841  (EN is the Chebyshev E; differentiate numerically on a fine grid)
        Eg = EN(g)
        dE = np.gradient(Eg, g)
        F = 1 + dE
        xs = np.sort(sp[sp <= S])
        Fe = np.interp(xs, g, F)
        n = len(sp)
        emp_hi = np.arange(1, len(xs) + 1) / n
        emp_lo = np.arange(0, len(xs)) / n
        ks = float(max(np.max(np.abs(emp_hi - Fe)), np.max(np.abs(emp_lo - Fe))))
        # matrices are independent; spacings within a matrix are not (sum constraint), so the i.i.d. KS band is
        # approximate: report it and the 99% band, and the mean-spacing check
        band95 = 1.358 / math.sqrt(n)
        ss = np.linspace(0, S, 4001)
        mean_exact = float(np.trapezoid(ss * pN(ss), ss))
        rows.append(dict(N=N, n=n, KS=ks, KS95=band95, KS_ok=bool(ks < 1.628 / math.sqrt(n)),
                         mean_exact=mean_exact, mean_draw=float(sp.mean()),
                         norm_exact=float(np.trapezoid(pN(ss), ss))))
        print(rows[-1], flush=True)
    out = dict(appendix=app, cue=rows, PASS=bool(app["ok"] and all(r["KS_ok"] for r in rows)))
    print(json.dumps(out, indent=1, default=float))
    dump("g0b.json", out)


# ---------------------------------------------------------------- G0c and the PRIMARY truncation allowance (§6)
def g0c():
    t = time.time()
    M = P.Model()
    W = P.WindowFit(M)
    sc = W.sc
    # (1) expansion remainder at integer N: R_N(s) = p_N − (p0 + p1/N²) on the window, and the c* it implies
    integer = []
    gs = np.linspace(0.0, sc, 2001)
    p0g, r2g = M.p0(gs), M.r2s[0](gs)
    for N in range(2, 21):
        pN, _, _ = P.spacing_tables(S=sc + 0.05 if N > 2 else 1.98, N=N, abars=())
        if N == 2:          # CUE_2 spacings live on [0, 2]; window [0, 1.98] check only
            g2 = gs[gs <= 1.98]
            rem = pN(g2) - p0g[:len(g2)] - r2g[:len(g2)] / N ** 2
        else:
            rem = pN(gs) - p0g - r2g / N ** 2
        cst = W.expected_c(pN, N)
        integer.append(dict(N=N, max_abs_remainder=float(np.max(np.abs(rem))),
                            N4_max_abs_remainder=float(N ** 4 * np.max(np.abs(rem))),
                            max_abs_leading=float(np.max(np.abs(r2g)) / N ** 2),
                            c_star=cst, kappa_star=P.kappa_from_c(cst)))
        print(integer[-1], flush=True)
    # (2) per bin: shifts of the PRIMARY fit against (i) the exact CUE_N law continued to real N (the kernel formula
    # BFM 1.8 at real N; checked against the integer values above) and (ii) the SECONDARY family at that height
    abars = np.round(np.arange(1.0, 1.4001, 0.01), 4)
    Ms = P.Model(abar_grid=abars)
    bins = []
    for name, kind, L0, L1 in BINS:
        rows = []
        for L in sorted({L0, 0.5 * (L0 + L1), L1}):
            N, ab = neff_of_L(L), abar_of_L(L)
            pN, _, _ = P.spacing_tables(S=sc + 0.05, N=N, abars=())
            c_i = W.expected_c(pN, N)
            p_sec = lambda s, ab=ab, N=N: Ms.eval(s, np.full(np.shape(s), ab))[0] + Ms.eval(s, np.full(np.shape(s), ab))[1] / N ** 2
            c_ii = W.expected_c(p_sec, N)
            k_i, k_ii = P.kappa_from_c(c_i), P.kappa_from_c(c_ii)
            rows.append(dict(L=L, N_eff=N, abar=ab, c_exact=c_i, kappa_exact=k_i, c_secondary=c_ii,
                             kappa_secondary=k_ii, shift_exact=k_i - 1, shift_secondary=k_ii - 1))
        worst = max(rows, key=lambda r: abs(r["shift_exact"]) + abs(r["shift_secondary"]))
        bins.append(dict(bin=name, kind=kind, L=[L0, L1], rows=rows,
                         allowance_sum=abs(worst["shift_exact"]) + abs(worst["shift_secondary"]),
                         allowance_max=max(abs(worst["shift_exact"]), abs(worst["shift_secondary"]))))
        print(name, [(round(r["N_eff"], 3), round(r["shift_exact"], 5), round(r["shift_secondary"], 5)) for r in rows],
              "allowance(sum) %.5f" % bins[-1]["allowance_sum"], flush=True)
    out = dict(window=sc, integer_N=integer, bins=bins, seconds=time.time() - t)
    dump("g0c.json", out)


if __name__ == "__main__":
    {"g0a": g0a, "g0b": g0b, "g0c": g0c}[sys.argv[1]]()

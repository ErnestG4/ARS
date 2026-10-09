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
    Ms = P.Model(abar_grid=P.SECONDARY_ABAR_GRID)
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


# ---------------------------------------------------------------- bin geometry before data (sizes, N_eff profile)
def nbar_float(T):
    """Riemann–von Mangoldt smooth count θ(T)/π + 1 (asymptotic θ to O(T⁻³)); float, for design arithmetic only."""
    T = np.asarray(T, dtype=float)
    th = T / 2 * np.log(T / TWO_PI) - T / 2 - math.pi / 8 + 1 / (48 * T) + 7 / (5760 * T ** 3)
    return th / math.pi + 1


def nbar_inv(x, T0):
    T = np.full(np.shape(x), float(T0))
    for _ in range(60):
        T = T - (nbar_float(T) - x) / (np.log(T / TWO_PI) / TWO_PI)
    return T


H_COUNT = 10_000   # zeros3/4/5 hold 10⁴ zeros each


def bin_geometry(name, n_profile=None):
    """(n_spacings, N_eff per spacing [length n or n_profile], ᾱ per spacing) for a sealed bin, from heights only."""
    _, kind, L0, L1 = next(b for b in BINS if b[0] == name)
    if kind in ("zeros3", "zeros4", "zeros5"):
        n = H_COUNT - 1
        m = n if n_profile is None else n_profile
        L = np.full(m, L0)
    else:
        T0, T1 = TWO_PI * math.exp(L0), TWO_PI * math.exp(L1)
        x0, x1 = float(nbar_float(T0)), float(nbar_float(T1))
        n = int(round(x1 - x0)) - 1
        m = n if n_profile is None else n_profile
        x = x0 + (np.arange(m) + 0.5) * (x1 - x0) / m
        L = np.log(nbar_inv(x, T0) / TWO_PI)
    return n, neff_of_L(L), abar_of_L(L)


# ---------------------------------------------------------------- G0d: the estimator on CUE_N surrogates (§5, A1)
BLOCK_FACTORS = (10, 30, 100)       # A1: L_b = factor × ⌈N_eff⌉ levels
Z95 = 1.959963984540054


def _ci_cover(c_hat, sd, target):
    return bool(c_hat - Z95 * sd <= target <= c_hat + Z95 * sd)


CHUNK = 25   # reps per job; a chunk's RNG seed is (bin, N, first rep) so the run is reproducible chunk by chunk


def _g0d_setup(name, N):
    n, Neff, ab = bin_geometry(name)
    Mp, Ms = P.Model(), P.Model(abar_grid=P.SECONDARY_ABAR_GRID)
    return n, Neff, ab, P.WindowFit(Mp), P.WindowFit(Ms)


def g0d(name, N, r0=0, r1=CHUNK, RB=100, B=200):
    """Reps r0 … r1−1 of the G0d surrogate run for (bin, N). Surrogates: concatenated CUE_N blocks (integer N), length =
    the bin's spacing count, each spacing carrying the bin's N_eff (and ᾱ) profile; both arms fitted; reps r < RB also
    get the A1 moving-block bootstrap SD (B replicates) at each declared block length. Writes a chunk file."""
    N, t0 = int(N), time.time()
    n, Neff, ab, Wp, Ws = _g0d_setup(name, N)
    seed = (1000003 * N + sum(map(ord, name))) * 1000 + r0
    rng = np.random.default_rng(seed)
    Lb = [f * int(math.ceil(float(np.median(Neff)))) for f in BLOCK_FACTORS]
    reps = []
    for r in range(r0, r1):
        sp = P.cue_spacings(N, int(math.ceil(n / N)), rng).ravel()[:n]
        rec = dict(rep=r, mean_s=float(sp.mean()))
        for arm, W, abar in (("prim", Wp, None), ("sec", Ws, ab)):
            prep = W.prepare(sp, Neff, abar)
            c, flag = W.fit(prep)
            rec[arm] = dict(c=c, flag=flag)
            if r < RB:
                rec[arm]["boot_sd"], rec[arm]["boot_refit"] = {}, 0
                for Lblk in Lb:
                    bs, nref = P.block_bootstrap_c_series(W, prep, c, Lblk, B, rng)
                    rec[arm]["boot_sd"][str(Lblk)] = float(np.std(bs, ddof=1))
                    rec[arm]["boot_refit"] += nref
        reps.append(rec)
        print(f"{name} N={N} rep {r} c_prim={rec['prim']['c']:.5f} c_sec={rec['sec']['c']:.5f} "
              f"{time.time() - t0:.0f}s", flush=True)
    os.makedirs(os.path.join(RES, "g0d", "chunks"), exist_ok=True)
    with open(os.path.join(RES, "g0d", "chunks", f"{name}_N{N}_r{r0:03d}.json"), "w") as f:
        json.dump(dict(bin=name, N=N, n=n, r0=r0, r1=r1, RB=RB, B=B, seed=seed, block_lengths=Lb, reps=reps,
                       seconds=time.time() - t0), f, default=float)


def g0d_merge(name, N):
    """Summary of all chunks of (bin, N): bias vs the known answer, CUE-calibrated split-half coverage, bootstrap SD
    ratio and coverage per block length, widest, and the wider of CUE and bootstrap (§6)."""
    import glob
    N = int(N)
    ch = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(RES, "g0d", "chunks", f"{name}_N{N}_r*.json")))]
    reps = sorted([r for c in ch for r in c["reps"]], key=lambda r: r["rep"])
    n, Neff, ab, Wp, Ws = _g0d_setup(name, N)
    q = np.linspace(0.025, 0.975, 20)
    Nq, Aq = np.quantile(Neff, q), np.quantile(ab, q)
    pN, _, _ = P.spacing_tables(S=P.S_C + 0.05 if N > 2 else 2.0, N=N, abars=())   # CUE_2 lives on [0, 2]
    cstar = dict(prim=Wp.expected_c(pN, Nq), sec=Ws.expected_c(pN, Nq, abar=Aq))
    Lb = ch[0]["block_lengths"]
    out = dict(bin=name, N=N, n=n, R=len(reps), reps_complete=[r["rep"] for r in reps] == list(range(len(reps))),
               RB=sum("boot_sd" in r["prim"] for r in reps), B=ch[0]["B"], seeds=[c["seed"] for c in ch],
               block_lengths=Lb, Neff_median=float(np.median(Neff)), Neff_range=[float(Neff.min()), float(Neff.max())],
               kappa_true_median=N / float(np.median(Neff)), cpu_seconds=sum(c["seconds"] for c in ch))
    for arm in ("prim", "sec"):
        cst = cstar[arm]
        c = np.array([x[arm]["c"] for x in reps])
        sd = float(np.std(c, ddof=1))
        sd_even = float(np.std(c[0::2], ddof=1))
        a = dict(c_star=cst, kappa_star=P.kappa_from_c(cst), c_mean=float(c.mean()), c_sd=sd,
                 bias_in_sd=(float(c.mean()) - cst) / sd if sd > 0 else None,
                 bias_se_in_sd=1 / math.sqrt(len(c)),
                 kappa_sd_rel=sd / (2 * cst) if cst > 0 else None,
                 cover_cue_split=float(np.mean([_ci_cover(ci, sd_even, cst) for ci in c[1::2]])),
                 flags={f: int(sum(x[arm]["flag"] == f for x in reps)) for f in ("interior", "at_lo", "at_hi")})
        rb = [x for x in reps if "boot_sd" in x[arm]]
        a["boot_refit_total"] = int(sum(x[arm]["boot_refit"] for x in rb))
        a["boot"] = {}
        for Lblk in Lb:
            sds = np.array([x[arm]["boot_sd"][str(Lblk)] for x in rb])
            a["boot"][str(Lblk)] = dict(sd_mean=float(sds.mean()), sd_ratio_to_cue=float(sds.mean()) / sd,
                                        cover=float(np.mean([_ci_cover(x[arm]["c"], x[arm]["boot_sd"][str(Lblk)], cst)
                                                             for x in rb])))
        widest = [max(x[arm]["boot_sd"].values()) for x in rb]
        a["boot"]["widest"] = dict(cover=float(np.mean([_ci_cover(x[arm]["c"], w, cst) for x, w in zip(rb, widest)])))
        a["wider_of_cue_and_boot"] = dict(cover=float(np.mean([_ci_cover(x[arm]["c"], max(w, sd), cst)
                                                               for x, w in zip(rb, widest)])))
        out[arm] = a
    out["mean_spacing"] = float(np.mean([x["mean_s"] for x in reps]))
    dump(os.path.join("g0d", f"{name}_N{N}.json"), out)


REPRESENTATION = {   # how each source stores γ (decimal digits after the point of the stored value)
    "zeros6": 9, "platt": None, "zeros3": 9, "zeros4": 9, "zeros5": 9}


def g0d_chain(n_levels=3000, seed=7):
    """The unfolding chain end to end (§5 G0d 'mapped onto ζ's density by N̄⁻¹ and unfolded back with the exact θ'):
    CUE_N levels x (unit mean spacing) are placed at N̄(T_bin) + x, mapped to heights γ = N̄⁻¹(·) in mpmath, stored in the
    source's representation (decimal rounding; Platt: the nearest t0 + Z·2⁻¹⁰¹), and unfolded back with
    ph2lib.unfolded_spacings. Reports max |Δs| per bin and the θ cost per zero."""
    import mpmath as mp
    rng = np.random.default_rng(seed)
    rows = []
    for name, kind, L0, L1 in BINS:
        N = max(2, round(neff_of_L(L0)))
        x = np.cumsum(P.cue_spacings(N, n_levels // N + 1, rng).ravel()[:n_levels])
        s_true = np.diff(x)
        with mp.workdps(50):
            T0 = TWO_PI * mp.exp(mp.mpf(L0))
            base = mp.siegeltheta(T0) / mp.pi + 1
            g = T0
            gam = []
            for xi in x:
                target = base + mp.mpf(float(xi))
                for _ in range(50):
                    step = (mp.siegeltheta(g) / mp.pi + 1 - target) / (mp.log(g / (2 * mp.pi)) / (2 * mp.pi))
                    g -= step
                    if abs(step) < mp.mpf(10) ** -40:
                        break
                gam.append(+g)
            digits = REPRESENTATION[kind]
            if digits is None:
                eps = mp.mpf(2) ** -101
                t0 = mp.floor(gam[0])
                stored = [t0 + mp.nint((v - t0) / eps) * eps for v in gam]
            else:
                q = mp.mpf(10) ** -digits
                stored = [mp.nint(v / q) * q for v in gam]
        t = time.time()
        s_back = P.unfolded_spacings(stored, dps=45)
        dt = (time.time() - t) / len(stored)
        err = float(np.max(np.abs(s_back - s_true)))
        rows.append(dict(bin=name, kind=kind, N=N, n=n_levels, max_abs_ds=err, theta_seconds_per_zero=dt,
                         mean_s_back=float(s_back.mean()), mean_s_true=float(s_true.mean())))
        print(rows[-1], flush=True)
    dump("g0d_chain.json", dict(rows=rows, PASS=bool(all(r["max_abs_ds"] < 1e-6 for r in rows))))


def reach():
    """§7 red paths, deterministic part (pre-data): κ* each arm would read under the wrong construction, per bin, with
    the SECONDARY law (ᾱ, κ = 1) standing in for the zeros' p(s). Reachability = shift vs the bin's half-width (summary).
      RP-misprint: unfolding with log(E/2πe): s' = s(L−1)/L, mean spacing (L−1)/L.
      RP-mix: SECONDARY family fitted with BBLM's α = (1 + ᾱ)/2 in place of ᾱ.
      RP-Λ: BBLM's printed 1.57314 → N_eff ratio √(Λ/Λ_BBLM) (declared UNREACHABLE; the ratio is reported)."""
    Mp, Ms = P.Model(), P.Model(abar_grid=P.SECONDARY_ABAR_GRID)
    Wp, Ws = P.WindowFit(Mp), P.WindowFit(Ms)
    rows = []
    for name, kind, L0, L1 in BINS:
        n, Neff, ab = bin_geometry(name, n_profile=2001)
        q = np.linspace(0.025, 0.975, 20)
        Nq, Aq = np.quantile(Neff, q), np.quantile(ab, q)
        L = float(np.median(Neff) * NEFF_DEN)
        Nm, am = float(np.median(Neff)), float(np.median(ab))
        truth = lambda s: Ms.eval(s, np.full(np.shape(s), am))[0] + Ms.eval(s, np.full(np.shape(s), am))[1] / Nm ** 2
        lam = L / (L - 1)
        mis = lambda s: lam * truth(np.minimum(lam * np.asarray(s), Ms.S))
        r = dict(bin=name, L=L, N_eff=Nm, abar=am)
        for arm, W, A in (("prim", Wp, None), ("sec", Ws, Aq)):
            c0 = W.expected_c(truth, Nq, abar=A)
            c1 = W.expected_c(mis, Nq, abar=A)
            r[arm] = dict(kappa_truth=P.kappa_from_c(c0), kappa_misprint=P.kappa_from_c(c1))
        c_mix = Ws.expected_c(truth, Nq, abar=(1 + Aq) / 2)
        r["sec"]["kappa_mix_alpha"] = P.kappa_from_c(c_mix)
        r["misprint_mean_spacing"] = (L - 1) / L
        r["rp_lambda_neff_ratio"] = math.sqrt(P.LAMBDA / 1.57314)
        rows.append(r)
        print(name, json.dumps(r, default=float), flush=True)
    dump("reach.json", dict(rows=rows))


FLOOR = 0.20                 # §4 resolution floor (±20%)
POWER_REQUIRED = 0.80        # A8 (PA7): a red-path check is scored only where its pre-read power reaches this
MEAN_SPACING_BAND = 10.0     # §2 check: |mean spacing − 1| ≤ MEAN_SPACING_BAND / n (|S(t)| ≤ 4 at both ends, +1)


def summary(only=None):
    """Per-bin pre-data decisions (§3–§7) from g0c.json, g0d/*.json, reach.json, geometry.json:
    SD_pred(κ̂) per arm = the G0d CUE-calibrated SD interpolated (log-linear in N) to the bin's median N_eff, times
    max(1, widest-bootstrap/CUE ratio) — the 'wider of' rule of §6 as it will apply; h_bin = min(3·SD_pred, 0.20);
    PRIMARY allowance under both PA2 options; NOT RESOLVABLE per §4; red-path reachability (shift > 1.96·SD_pred)."""
    from statistics import NormalDist
    Phi = NormalDist().cdf
    g0c = {b["bin"]: b for b in json.load(open(os.path.join(RES, "g0c.json")))["bins"]}
    reach_ = {r["bin"]: r for r in json.load(open(os.path.join(RES, "reach.json")))["rows"]}
    geo = {r["bin"]: r for r in json.load(open(os.path.join(RES, "geometry.json")))["bins"]}
    rows = []
    for name in (only or [b[0] for b in BINS]):
        Nm = geo[name]["Neff"][1]
        cfg = [json.load(open(os.path.join(RES, "g0d", f"{name}_N{N}.json"))) for b, N in g0d_configs() if b == name]
        r = dict(bin=name, N_eff=Nm, n=geo[name]["n_spacings"], mean_spacing_band=MEAN_SPACING_BAND / geo[name]["n_spacings"])
        for arm in ("prim", "sec"):
            pts = []
            for d in cfg:
                a = d[arm]
                ratio = max([1.0] + [v["sd_ratio_to_cue"] for k, v in a["boot"].items() if k != "widest"])
                pts.append((d["N"], a["kappa_sd_rel"], ratio, a["wider_of_cue_and_boot"]["cover"], a["cover_cue_split"],
                            a["bias_in_sd"], a["c_sd"]))

            def interp(j):          # log-linear in N between the two integer-N surrogates, to the bin's median N_eff
                if len(pts) == 2 and pts[0][0] != pts[1][0]:
                    (N0, v0), (N1, v1) = (pts[0][0], pts[0][j]), (pts[1][0], pts[1][j])
                    return math.exp(math.log(v0) + (math.log(v1) - math.log(v0)) * (Nm - N0) / (N1 - N0))
                return pts[0][j]

            sd_cue, sd_c_cue = interp(1), interp(6)
            ratio = max(p[2] for p in pts)
            sd = sd_cue * ratio
            r[arm] = dict(sd_cue=sd_cue, sd_c_cue=sd_c_cue, boot_ratio=ratio, sd_pred=sd, h_bin=min(3 * sd, FLOOR),
                          g0d_cover_wider=[p[3] for p in pts], g0d_cover_cue_split=[p[4] for p in pts],
                          g0d_bias_in_sd=[p[5] for p in pts],
                          power_excludes_inf=bool(Z95 * 2 * sd < 1),        # c = 1 ± 1.96·SD_c, SD_c ≈ 2·SD_κ
                          ci_halfwidth=Z95 * sd)
        al_sum, al_max = g0c[name]["allowance_sum"], g0c[name]["allowance_max"]
        for tag, al in (("sum", al_sum), ("max", al_max)):
            w = r["prim"]["ci_halfwidth"] + al
            r["prim"][f"widened_halfwidth_{tag}"] = w
            r["prim"][f"NOT_RESOLVABLE_{tag}"] = bool(w > FLOOR or not r["prim"]["power_excludes_inf"])
        r["sec"]["RESOLVABLE_at_floor"] = bool(r["sec"]["ci_halfwidth"] <= FLOOR and r["sec"]["power_excludes_inf"])
        rc = reach_[name]
        mix = rc["sec"]["kappa_mix_alpha"] - rc["sec"]["kappa_truth"]
        # A8 (PA7): a red-path check is REQUIRED only where its pre-read power ≥ POWER_REQUIRED
        pw_mix = Phi(abs(mix) / r["sec"]["sd_pred"] - Z95)
        r["rp_mix"] = dict(shift=mix, reachable=bool(abs(mix) > Z95 * r["sec"]["sd_pred"]), power=pw_mix,
                           required=bool(pw_mix >= POWER_REQUIRED and r["sec"]["RESOLVABLE_at_floor"]))

        def pw_kappa(k_mis, k_truth, sd, allow):     # misprint κ̂ arm: shift beyond the (widened) CI half-width
            if not math.isfinite(k_mis):
                return 1.0
            return Phi((abs(k_mis - k_truth) - allow) / sd - Z95)

        d_mean = 1 - rc["misprint_mean_spacing"]
        n_b = geo[name]["n_spacings"]
        pw_mean = Phi((d_mean - r["mean_spacing_band"]) * n_b / 2)    # mean of zeros: σ ≈ 2/n (S at both ends)
        # an arm that is NOT RESOLVABLE (its CI reaches N = ∞) cannot see any κ̂ shift: power undefined (None)
        pw_np = (None if r["prim"]["NOT_RESOLVABLE_max"] else
                 pw_kappa(rc["prim"]["kappa_misprint"], rc["prim"]["kappa_truth"], r["prim"]["sd_pred"],
                          g0c[name]["allowance_max"]))
        pw_ns = (None if not r["sec"]["RESOLVABLE_at_floor"] else
                 pw_kappa(rc["sec"]["kappa_misprint"], rc["sec"]["kappa_truth"], r["sec"]["sd_pred"], 0.0))
        r["rp_misprint"] = dict(kappa_prim=rc["prim"]["kappa_misprint"], kappa_sec=rc["sec"]["kappa_misprint"],
                                mean_spacing=rc["misprint_mean_spacing"],
                                reachable_mean=bool(d_mean > r["mean_spacing_band"]),
                                power=dict(mean=pw_mean, N_prim=pw_np, N_sec=pw_ns),
                                required=dict(mean=bool(pw_mean >= POWER_REQUIRED),
                                              N_prim=bool(pw_np is not None and pw_np >= POWER_REQUIRED),
                                              N_sec=bool(pw_ns is not None and pw_ns >= POWER_REQUIRED)))
        r["rp_ninf"] = dict(reachable_prim=r["prim"]["power_excludes_inf"], reachable_sec=r["sec"]["power_excludes_inf"])
        r["rp_lambda"] = dict(neff_ratio=rc["rp_lambda_neff_ratio"], status="INAPPLICABLE (unreachable, declared)")
        rows.append(r)
        print(f"{name:3} N_eff {Nm:6.3f} n {r['n']:>9,}  SDκ prim {r['prim']['sd_pred']:.4f} sec {r['sec']['sd_pred']:.4f}"
              f"  h_bin {r['prim']['h_bin']:.3f}/{r['sec']['h_bin']:.3f}  widened(sum/max) "
              f"{r['prim']['widened_halfwidth_sum']:.3f}/{r['prim']['widened_halfwidth_max']:.3f}"
              f"  PRIM NR(sum/max) {r['prim']['NOT_RESOLVABLE_sum']}/{r['prim']['NOT_RESOLVABLE_max']}"
              f"  SEC ok {r['sec']['RESOLVABLE_at_floor']}  mix {mix:+.4f} reach {r['rp_mix']['reachable']}", flush=True)
    dump("summary.json", dict(rows=rows, floor=FLOOR, mean_spacing_band_numerator=MEAN_SPACING_BAND))
    f = lambda x: f"{x:.4f}"
    md = ["| bin | N_eff | n | SD κ̂ prim (CUE×boot) | SD κ̂ sec | h_bin prim/sec | allowance sum/max | widened ½-width sum/max |"
          " PRIMARY NR sum/max | SECONDARY resolvable | RP-mix shift (reach, power) | G0d cover (wider) prim/sec |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        p, s = r["prim"], r["sec"]
        md.append(f"| {r['bin']} | {r['N_eff']:.3f} | {r['n']:,} | {f(p['sd_cue'])}×{p['boot_ratio']:.2f} = {f(p['sd_pred'])} |"
                  f" {f(s['sd_pred'])} | {p['h_bin']:.3f}/{s['h_bin']:.3f} |"
                  f" {g0c[r['bin']]['allowance_sum']:.3f}/{g0c[r['bin']]['allowance_max']:.3f} |"
                  f" {p['widened_halfwidth_sum']:.3f}/{p['widened_halfwidth_max']:.3f} |"
                  f" {'NR' if p['NOT_RESOLVABLE_sum'] else 'ok'}/{'NR' if p['NOT_RESOLVABLE_max'] else 'ok'} |"
                  f" {'yes' if s['RESOLVABLE_at_floor'] else 'NO'} |"
                  f" {r['rp_mix']['shift']:+.4f} ({'yes' if r['rp_mix']['reachable'] else 'no'}, {r['rp_mix']['power']:.2f}) |"
                  f" {'/'.join(f'{c:.2f}' for c in p['g0d_cover_wider'])} · {'/'.join(f'{c:.2f}' for c in s['g0d_cover_wider'])} |")
    open(os.path.join(RES, "summary.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


def g0d_configs():
    """The (bin, N) pairs: integer N on both sides of the bin's median N_eff (N ≥ 2)."""
    out = []
    for name, *_ in BINS:
        _, Neff, _ = bin_geometry(name, n_profile=2001)
        m = float(np.median(Neff))
        for N in sorted({max(2, math.floor(m)), math.ceil(m)}):
            out.append((name, N))
    return out


def geometry():
    rows = []
    for name, kind, L0, L1 in BINS:
        n, Neff, ab = bin_geometry(name, n_profile=20001)
        rows.append(dict(bin=name, kind=kind, L=[L0, L1], n_spacings=n,
                         Neff=[float(Neff.min()), float(np.median(Neff)), float(Neff.max())],
                         abar=[float(ab.min()), float(ab.max())]))
        print(rows[-1])
    print("G0d configs:", g0d_configs())
    dump("geometry.json", dict(bins=rows, g0d_configs=g0d_configs()))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "g0d":
        g0d(sys.argv[2], int(sys.argv[3]), *[int(a) for a in sys.argv[4:]])
    elif cmd == "g0d_merge":
        for b, nn in (g0d_configs() if len(sys.argv) == 2 else [(sys.argv[2], int(sys.argv[3]))]):
            g0d_merge(b, nn)
    elif cmd == "g0d_jobs":            # one line per chunk job: bin N r0 r1
        for b, nn in g0d_configs():
            for r0 in range(0, 200, CHUNK):
                print(b, nn, r0, r0 + CHUNK)
    else:
        {"g0a": g0a, "g0b": g0b, "g0c": g0c, "geometry": geometry, "g0d_chain": g0d_chain, "reach": reach, "summary": lambda: summary(sys.argv[2].split(",") if len(sys.argv) > 2 else None)}[cmd]()

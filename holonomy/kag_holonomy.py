"""Holonomy pilot KAG + witness battery (brief §2, §6) — the legal debugging
window.  COMMITTED GENERATOR of holonomy/kag_measured.json.

A. Commutation nulls, NON-VACUOUS: non-identity transitions that provably
   commute analytically, run through each dialect's full plumbing; exact
   commutation within the fp tolerance candidate.  Identity runs retained
   as labeled smoke tests only.
B. Red demos (witness-must-fail, delta-DETECTION): deliberately
   order-sensitive constructions; the dialed detector must fire.
C. Correctness-leg two-sided witness: rules correctly where one ordering is
   more biased BY DESIGN (P2, G=4.30, prediction says A worse), and returns
   indistinguishable on the symmetric construction (G=1.0).
D. P3 data section: R2 equivalence test (bit-identical keep-mask), A3 sign
   scalars, red demo A (suppressor-broken retained-mass z — labeled
   DETECTION_IN_PRINCIPLE), red demo B (spatially-modulated injected delta
   at the UNMODIFIED F path — the stronger witness), and the Q8 timing
   pilot for n_draws.
"""

import json
import sys
import time

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")

from transitions import (gen_trended_set, p1_apply, sigma2_at,             # noqa: E402
                         sample_inhom_poisson, p2_apply, k_inhom_marks,
                         fit_lambda_strips, thin_pre, equivalence_thin)

FP_TOL = 1e-12           # candidate sealed tolerance (relative); §9 Q3
RES = {}


def rel(a, b):
    return abs(a - b) / max(abs(a), abs(b), 1e-300)


# ── A. commutation nulls ─────────────────────────────────────────────────────

def null_1d():
    st = gen_trended_set(seed=0, N=2048, n_keep=1200, a=0.25, ell=600.0)
    x = st["x"] + 1.0                                  # positive support
    def stat(y):
        return float(sigma2_at(p1_apply(y, "unfold_then_window", 5, 600),
                               [20.0])[0])
    outs = {}
    # two dilations (commute exactly as maps)
    outs["dilations"] = rel(stat(0.7 * (1.3 * x)), stat(1.3 * (0.7 * x)))
    # two power maps (commute exactly as maps on positive support)
    outs["powers"] = rel(stat((x ** 1.1) ** 0.9), stat((x ** 0.9) ** 1.1))
    outs["identity_smoke"] = rel(stat(x.copy()), stat(x.copy()))
    return outs


def null_2d():
    pts, meta = sample_inhom_poisson(seed=1, beta=np.log(2.074) / 10.0,
                                     n_target=3000)
    dom = (0.0, meta["Lx"], 0.0, meta["Ly"])
    m0 = np.ones(len(pts))
    f = 1.0 + 0.3 * np.sin(pts[:, 0])
    g = 1.0 + 0.2 * np.cos(pts[:, 1])
    def stat(marks):
        return k_inhom_marks(pts, marks, dom, [1.0])[1.0]
    outs = {"marks": rel(stat((m0 * f) * g), stat((m0 * g) * f)),
            "identity_smoke": rel(stat(m0 * 1.0), stat(m0 * 1.0))}
    return outs


def null_survey_dialect():
    sys.path.insert(0, f"{ROOT}/survey")
    from estimators import cells_F
    rng = np.random.default_rng(7)
    xy_d = rng.uniform(0, 5, size=(20000, 2))
    w_d = np.exp(rng.normal(0, 0.1, 20000))
    xy_r = rng.uniform(0, 5, size=(100000, 2))
    w_r = np.ones(100000)
    f1 = 1.0 + 0.2 * np.sin(xy_d[:, 0])
    f2 = 1.0 + 0.1 * np.cos(xy_d[:, 1])
    def stat(w):
        return cells_F(xy_d, w, xy_r, w_r, 0.5, (0, 5, 0, 5))["F"]
    return {"weights": rel(stat((w_d * f1) * f2), stat((w_d * f2) * f1)),
            "identity_smoke": rel(stat(w_d * 1.0), stat(w_d * 1.0))}


# ── B. red demos (delta-detection must fire) ─────────────────────────────────

def red_p1():
    """Nonlinear rescale vs ABSOLUTE-coordinate window cut: the cut selects
    a different quantile of the process depending on whether the rescale
    has already happened (0.5 vs ~0.707), and hands Σ² a strongly
    non-uniform density either way — order-sensitive by design.
    (First construction — rank-window vs renormalise — was INERT: rank
    selection is invariant under monotone maps, so only a scale factor
    survived and Σ²(L) barely moves.  Replaced in the KAG debug window,
    2026-08-15; the inert version is retained here as the record.)"""
    deltas = []
    for seed in range(6):
        st = gen_trended_set(seed=100 + seed, N=2048, n_keep=1200,
                             a=0.25, ell=600.0)
        x = np.sort(st["x"])
        span = float(x[-1])
        def sq(y):
            return y * y / span
        def cut(y):
            return y[y < span / 2.0]
        sA = float(sigma2_at(cut(sq(x)), [20.0])[0])
        sB = float(sigma2_at(sq(cut(x)), [20.0])[0])
        deltas.append(sA - sB)
    d = np.array(deltas)
    sem = d.std(ddof=1) / np.sqrt(len(d))
    fired = bool(abs(d.mean()) > 3 * sem and abs(d.mean()) > 1e3 * FP_TOL)
    return dict(mean=float(d.mean()), sem=float(sem), fired=fired)


def red_p2():
    """Reweight-by-lambda-hat vs keep-left-half-domain."""
    deltas = []
    for seed in range(6):
        pts, meta = sample_inhom_poisson(seed=200 + seed,
                                         beta=np.log(4.30) / 10.0,
                                         n_target=3000)
        dom = (0.0, 10.0, 0.0, 10.0)
        def kw(p, marks, d):
            return k_inhom_marks(p, marks, d, [1.0])[1.0]
        # order 1: reweight on full, then cut to left half
        lam = fit_lambda_strips(pts, dom, 10)
        mfull = lam(pts[:, 0])
        mhalf = pts[:, 0] < 5.0
        k1 = kw(pts[mhalf], mfull[mhalf], (0, 5, 0, 10))
        # order 2: cut, then reweight on the half
        ph = pts[mhalf]
        lam2 = fit_lambda_strips(ph, (0, 5, 0, 10), 10)
        k2 = kw(ph, lam2(ph[:, 0]), (0, 5, 0, 10))
        deltas.append(k1 - k2)
    d = np.array(deltas)
    sem = d.std(ddof=1) / np.sqrt(len(d))
    fired = bool(abs(d.mean()) > 3 * sem and abs(d.mean()) > 1e3 * FP_TOL)
    return dict(mean=float(d.mean()), sem=float(sem), fired=fired)


# ── C. correctness-leg two-sided witness ─────────────────────────────────────

def leg_two_sided():
    def biases(G, seeds):
        bA, bB = [], []
        beta = 0.0 if G == 1.0 else np.log(G) / 10.0
        for s in seeds:
            pts, meta = sample_inhom_poisson(seed=300 + s, beta=beta,
                                             n_target=3000)
            dom = (0.0, 10.0, 0.0, 10.0)
            for order, acc in (("reweight_then_edge", bA),
                               ("edge_then_reweight", bB)):
                pe, marks, d2 = p2_apply(pts, dom, order, rmax=1.0)
                K = k_inhom_marks(pe, marks, d2, [1.0])[1.0]
                acc.append(abs(K - np.pi))
        return np.array(bA), np.array(bB)

    seeds = range(8)
    # separated half: G=4.30, prediction says A more biased
    bA, bB = biases(4.30, seeds)
    diff = bA - bB
    sem = diff.std(ddof=1) / np.sqrt(len(diff))
    sep = dict(mean_bias_A=float(bA.mean()), mean_bias_B=float(bB.mean()),
               diff=float(diff.mean()), sem=float(sem),
               ruled_correctly=bool(diff.mean() > 3 * sem))
    # null half: G=1.0, must be indistinguishable
    bA0, bB0 = biases(1.0, seeds)
    d0 = bA0 - bB0
    sem0 = d0.std(ddof=1) / np.sqrt(len(d0))
    nul = dict(diff=float(d0.mean()), sem=float(sem0),
               indistinguishable=bool(abs(d0.mean()) <= 3 * sem0))
    return dict(separated=sep, null=nul,
                PASS=bool(sep["ruled_correctly"] and nul["indistinguishable"]))


# ── D. P3 data section ───────────────────────────────────────────────────────

def p3_section():
    from p3_common import load_all, prep_null_tiles, pooled_F
    print("  [P3] loading survey objects (read-only)...", flush=True)
    scal, kag, nulls, tiles = load_all()
    ntiles = prep_null_tiles(nulls, tiles)
    del nulls
    # the two orderings' scalar rates from the banked scalars (mechanism)
    p_wt = scal["W_data"] / scal["W_kag"]
    p_tw = scal["N_data"] / scal["N_kag"]
    sign_pred = int(np.sign(p_wt - p_tw))
    out = dict(scalars=scal, p_weight_then_thin=float(p_wt),
               p_thin_then_weight=float(p_tw),
               predicted_sign_retained_diff=sign_pred,
               predicted_abs_count_diff=float(abs(p_wt - p_tw) * scal["N_kag"]))
    # R2 equivalence test (bit-identical vs frozen thin_to_data)
    same, nkept = equivalence_thin(kag, scal["W_data"], seed=42)
    out["equivalence_thin"] = dict(bit_identical=bool(same), n_kept=nkept)
    # red demo A: suppressor-broken retained-mass z (DETECTION_IN_PRINCIPLE)
    rng = np.random.default_rng(1000)
    u = rng.uniform(size=scal["N_kag"])
    W_A = float(kag["w"][u < p_wt].sum())
    W_inj = float(kag["w"][u < p_wt * 1.01].sum())     # injected 1% offset
    sig_W = float(np.sqrt((kag["w"] ** 2 * p_wt * (1 - p_wt)).sum()))
    z_inj = (W_inj - W_A) / sig_W
    W_B = float(kag["w"][u < p_tw].sum())
    z_real = (W_B - W_A) / sig_W
    out["red_A_detection_in_principle"] = dict(
        z_injected_1pct=float(z_inj), fired=bool(abs(z_inj) > 5.0),
        z_real_amplitude=float(z_real),
        note="retained-mass z = the F statistic minus its self-"
             "normalisation; tests a modified estimator (labeled)")
    # red demo B: spatial injected delta at the UNMODIFIED F path
    L_RED = 0.5
    DELTA_INJ = 0.05
    ra0 = float(kag["ra"].min())
    mod = 1.0 + DELTA_INJ * np.sin(2 * np.pi * (kag["ra"] - ra0) / 20.0)
    dF, t0 = [], time.time()
    for dr in range(8):
        u = np.random.default_rng(2000 + dr).uniform(size=scal["N_kag"])
        thin_A = thin_pre(kag, p_wt, u)
        thin_Bp = {k: v[u < np.clip(p_tw * mod, 0, 1)] for k, v in kag.items()}
        FA, _ = pooled_F(thin_A, ntiles, tiles, [L_RED])
        FB, _ = pooled_F(thin_Bp, ntiles, tiles, [L_RED])
        dF.append(FB[L_RED] - FA[L_RED])
        print(f"    [redB] draw {dr}: dF={dF[-1]:+.4f}", flush=True)
    t_draw = (time.time() - t0) / 8.0
    d = np.array(dF)
    sem = d.std(ddof=1) / np.sqrt(len(d))
    out["red_B_unmodified_path"] = dict(
        delta_inj=DELTA_INJ, L=L_RED, mean_dF=float(d.mean()),
        sem=float(sem), fired=bool(abs(d.mean()) > 3 * sem))
    # Q8 timing pilot -> n_draws proposal (both orderings, 2 sealed L)
    out["timing"] = dict(t_per_draw_pair_sec=float(t_draw),
                         n_draws_proposed=32)
    return out


def main():
    print("A. commutation nulls", flush=True)
    RES["null_1d"] = null_1d()
    RES["null_2d"] = null_2d()
    RES["null_survey"] = null_survey_dialect()
    worst = max(v for d in (RES["null_1d"], RES["null_2d"],
                            RES["null_survey"])
                for k, v in d.items() if k != "identity_smoke")
    RES["fp_headroom"] = dict(worst_rel_delta=float(worst),
                              tol_candidate=FP_TOL,
                              within=bool(worst <= FP_TOL))
    print(f"  worst non-identity rel delta = {worst:.3e} "
          f"(tol {FP_TOL:.0e})", flush=True)
    print("B. red demos", flush=True)
    RES["red_p1"] = red_p1()
    RES["red_p2"] = red_p2()
    print(f"  P1 red fired={RES['red_p1']['fired']} "
          f"P2 red fired={RES['red_p2']['fired']}", flush=True)
    print("C. correctness-leg two-sided witness", flush=True)
    RES["leg_witness"] = leg_two_sided()
    print(f"  separated ruled_correctly="
          f"{RES['leg_witness']['separated']['ruled_correctly']} "
          f"null indistinguishable="
          f"{RES['leg_witness']['null']['indistinguishable']}", flush=True)
    print("D. P3 data section", flush=True)
    RES["p3"] = p3_section()
    p3 = RES["p3"]
    print(f"  equivalence bit_identical="
          f"{p3['equivalence_thin']['bit_identical']} "
          f"redA fired={p3['red_A_detection_in_principle']['fired']} "
          f"redB fired={p3['red_B_unmodified_path']['fired']}", flush=True)
    RES["PASS"] = bool(
        RES["fp_headroom"]["within"] and RES["red_p1"]["fired"]
        and RES["red_p2"]["fired"] and RES["leg_witness"]["PASS"]
        and p3["equivalence_thin"]["bit_identical"]
        and p3["red_A_detection_in_principle"]["fired"]
        and p3["red_B_unmodified_path"]["fired"])
    json.dump(RES, open(f"{ROOT}/holonomy/kag_measured.json", "w"), indent=1)
    print(f"KAG PASS={RES['PASS']}", flush=True)
    sys.exit(0 if RES["PASS"] else 1)


if __name__ == "__main__":
    main()

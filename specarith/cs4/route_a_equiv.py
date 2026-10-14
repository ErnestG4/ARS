"""Route (a) pre-read item (thirtieth/thirty-seventh rounds; DESCRIPTIVE, answers lead L2): Phase 2's CUE(N_eff)
families expressed as an equivalent μ. For each F3 file (at its zero-weighted mean height E, as the prediction), the
equivalent μ of a spacing law p_true is the infinite-sample limit of the route (a) estimator on the window when the
zeros follow p_true:
    μ* solves  ∫_w p_true(s) ρ(s)/(1 + μρ(s)) ds / ∫_w p_true  =  φ/(1 + μφ)        (ρ = Δp/p_sine, φ = ∫Δp/∫p_sine),
i.e. the maximiser of E_true[ℓ(μ)] (route_a_read.MuFit, the read's own fitter). Families (Phase 2's notation,
N_eff = log(E/2π)/√(12Λ), ᾱ = BFM 4.5, r2 = BFM 1.13):
    BBLM      p0 + r2(ᾱ = 1)/N_eff²                 (CUE(N_eff), first order: Phase 2's PRIMARY at κ = 1)
    BFM_abar  p0 + r2(ᾱ)/N_eff²                     (Phase 2's SECONDARY at κ = 1)
    fit_prim  p0 + ĉ_prim·r2(1)/N_eff²              (Phase 2's fitted PRIMARY, ĉ = 1/κ̂², κ̂ interpolated linearly in
    fit_sec   p0 + ĉ_sec·r2(ᾱ)/N_eff²                log(E/2π) between the sealed P bins bracketing the file; seen data)
    cue_exact the exact CUE_N spacing law at real N = N_eff (all orders; ph2lib Fredholm with the CUE_N kernel)
and, for reference, the prediction itself (μ = 1) and the sine kernel (μ = 0), which the estimator must return.

  python route_a_equiv.py [OUT.json]
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
import ph2lib  # noqa: E402
import route_a_read as RR  # noqa: E402

PH2_RUN = os.path.join(HERE, "..", "ph2", "results", "run")
P_BINS = ["P1", "P2", "P3", "P4", "P5", "P6"]


def expected_mu(fit, p_true, n=40001):
    g = np.linspace(0, fit.sc, n)[1:]
    w = np.full(len(g), fit.sc / (n - 1))
    w[-1] *= 0.5
    wt = np.maximum(p_true(g), 0) * w
    W = float(wt.sum())
    gg = np.maximum(g, RR.S_TINY)
    rho = RR.cheb_interp(fit.dp_nodes, gg) / RR.p_sine()(gg)
    phi = fit.FD / fit.F0
    score = lambda m: float(np.sum(wt * rho / (1 + m * rho))) / W - phi / (1 + m * phi)
    lo, hi = fit.c_range()
    if score(lo) <= 0:
        return lo
    if score(hi) >= 0:
        return hi
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if score(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def noncentrality(fit, p_true, mu, n_spacings, nb=RR.GOF_BINS):
    """The GoF χ²'s noncentrality at the read's size if the zeros followed p_true and μ̂ = μ*: n_window·Σ_j (P_j − Q_j)²/Q_j
    (P = p_true's window-conditional bin probabilities, Q = p_μ*'s); compare with the CUE-calibrated χ² threshold."""
    Q, edges = fit.bin_probs(mu, nb)
    P = []
    for a, b in zip(edges[:-1], edges[1:]):
        g = np.linspace(a, b, 2001)
        P.append(float(np.trapezoid(np.maximum(p_true(g), 0), g)))
    gw = np.linspace(0, fit.sc, 20001)
    frac = float(np.trapezoid(np.maximum(p_true(gw), 0), gw))
    P = np.array(P) / sum(P)
    return float(n_spacings * frac * np.sum((P - Q) ** 2 / Q))


def bins():
    sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
    import preread as PR
    out = []
    for b in P_BINS:
        d = json.load(open(os.path.join(PH2_RUN, f"{b}.json")))
        L0, L1 = next((x[2], x[3]) for x in PR.BINS if x[0] == b)
        out.append(dict(bin=b, ell=0.5 * (L0 + L1), c_prim=float(d["prim"]["c"]), c_sec=float(d["sec"]["c"]),
                        kappa_prim=float(d["prim"]["kappa"]), kappa_sec=float(d["sec"]["kappa"])))
    return out


def interp_kappa(B, ell, key):
    x = [b["ell"] for b in B]
    y = [b[key] for b in B]
    return float(np.interp(ell, x, y))


def main(out=None):
    pred = json.load(open(RR.PRED))
    B = bins()
    p0 = RR.p_sine()
    res = dict(bins=B, files={})
    _, nf = RR.weights()
    for f in RR.F3:
        fit = RR.MuFit.for_file(f, pred)
        E = pred["files"][f]["t_mean"]
        ell = math.log(E / (2 * math.pi))
        N = float(ph2lib.n_eff(E))
        ab = float(ph2lib.alpha_bar(E))
        _, r2s, _ = ph2lib.spacing_tables(S=6.0, M=160, m=40, abars=(1.0, ab))
        r2_1, r2_ab = r2s
        kp, ks = interp_kappa(B, ell, "kappa_prim"), interp_kappa(B, ell, "kappa_sec")
        cue_N = ph2lib.spacing_tables(S=6.0, M=160, m=40, abars=(), N=N)[0]
        fam = {
            "sine (μ = 0 check)": p0,
            "prediction (μ = 1 check)": lambda s: fit.density(s, 1.0),
            "BBLM: CUE(N_eff) first order": lambda s: p0(s) + r2_1(s) / N ** 2,
            "BFM_abar: SECONDARY form, kappa = 1": lambda s: p0(s) + r2_ab(s) / N ** 2,
            "fit_prim: Phase 2 PRIMARY fitted (interp.)": lambda s: p0(s) + r2_1(s) / (kp * N) ** 2,
            "fit_sec: Phase 2 SECONDARY fitted (interp.)": lambda s: p0(s) + r2_ab(s) / (ks * N) ** 2,
            "cue_exact: CUE_N at N = N_eff": cue_N,
        }
        row = dict(t_mean=E, ell=ell, N_eff=N, abar=ab, kappa_prim_interp=kp, kappa_sec_interp=ks, n_f=nf[f], mu={},
                   gof_noncentrality={})
        for name, p in fam.items():
            m = expected_mu(fit, p)
            row["mu"][name] = m
            row["gof_noncentrality"][name] = noncentrality(fit, p, m, nf[f])
        res["files"][f] = row
        print(f"{f}: ℓ {ell:.3f} N_eff {N:.3f} ᾱ {ab:.4f} κ̂ prim/sec {kp:.3f}/{ks:.3f}", flush=True)
        for name, v in row["mu"].items():
            print(f"    {name:48s} μ* = {v:+.4f}   GoF noncentrality at n_f: {row['gof_noncentrality'][name]:.3g}", flush=True)
    if out:
        json.dump(res, open(out, "w"), indent=1)
    return res


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

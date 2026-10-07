"""Phase 6 pre-read computations (seal PH6_SEAL_6.0.md §9). Computes NO gate statistic.

What it may touch: level POSITIONS for the tolerance terms eps_data / eps_float (non-oscillatory sums of w and |w'|), the
30,000th zero's height (G0-c's E_hi), and synthetic null spectra. It never forms S(tau), C(tau) or c_n from ζ, χ₋₄ or
Maass data.

Usage:  python -I preread.py tables OUTDIR ZEROS1 MAASS_CSV [CHI4_ZEROS]   # configs, RHS + tolerances, reachability
        python -I preread.py nulls  OUTDIR CONFIG_NAME N_GUE N_POISSON NPROC  # calibration draws, bands, known answers
        python -I preread.py design OUTDIR                                   # resolvable sets from the bands
"""
import json
import math
import os
import sys
import time

import numpy as np

import ph6lib as L

ID_GRID = 0.5 + 0.001 * np.arange(4001)
ALPHA = 0.01
CALIB_SEEDS = {"gue": 1000, "poisson": 2000}       # seal §7: calibration = the first 100 seeds of each family


def load_zeros(path):
    return np.loadtxt(path, dtype=np.float64)


def load_maass(path):
    import csv
    rows = list(csv.DictReader(open(path)))
    r = np.array([float(x["r"]) for x in rows])
    s = np.array([int(x["symmetry"]) for x in rows])
    return r[s == 0], r[s == 1]              # sym0 = even, sym1 = odd (DATA_MANIFEST; SESSION_K continuation Run 1)


def configs(zeros1):
    g30000 = float(zeros1[29999])
    return {
        "G0": L.rule_config(0.0, float(zeros1[-1])),
        "G0s_a": L.fixed_config(10.0, 4.0),
        "G0s_b": L.fixed_config(40.0, 3.0),
        "G0s_c": L.fixed_config(150.0, 10.0),
        "G0c": L.rule_config(0.0, g30000),
        "G1": L.rule_config(0.0, 98.76496727),
        "G2": L.rule_config(0.0, 20000.0),
    }


def cfg_json(c):
    return dict(T0=c.T0, sigma=c.sigma, E_lo=c.E_lo, E_hi=c.E_hi)


def zeta_density(t):
    return math.log(max(t, 7.0) / (2 * math.pi)) / (2 * math.pi)


def chi_density(t):
    return math.log(max(t, 2.0) * 4 / (2 * math.pi)) / (2 * math.pi)


def tables(outdir, zeros1_path, maass_path, chi_path=None):
    t_start = time.time()
    z = load_zeros(zeros1_path)
    r_even, r_odd = load_maass(maass_path)
    C = configs(z)
    out = {"configs": {k: cfg_json(v) for k, v in C.items()}, "gates": {}, "reachability": {}}
    import classes
    _, ls = classes.pari_counts(30, 30)
    ch = {t: ls[("h", t)] / 2 for (k, t) in ls if k == "h"}
    cg = {t: ls[("g", t)] for (k, t) in ls if k == "g"}

    def save(name, taus, rhs_total, eps_parts, extra=None):
        eps = L.tolerance(*eps_parts)
        np.savez_compressed(os.path.join(outdir, f"rhs_{name}.npz"), taus=taus, rhs=rhs_total, eps=eps,
                            **{f"eps_{i}": p for i, p in enumerate(eps_parts)})
        out["gates"][name] = dict(n_tau=int(len(taus)), eps_min=float(np.min(eps)), eps_max=float(np.max(eps)),
                                  **(extra or {}))
        print(name, out["gates"][name], flush=True)

    def reach(name, rp, removed, eps, note=""):
        m = np.abs(removed) / (2 * eps)
        out["reachability"][f"{name}:{rp}"] = dict(max_ratio=float(np.max(m)),
                                                    status="REACHABLE" if np.max(m) > 1 else "INAPPLICABLE", note=note)
        print("  reach", name, rp, out["reachability"][f"{name}:{rp}"], flush=True)

    # ---- zeta gates: G0, G0-s (three), G0-c
    for name, zsub, delta in (("G0", z, 3e-9), ("G0s_a", z, 3e-9), ("G0s_b", z, 3e-9), ("G0s_c", z, 3e-9),
                              ("G0c", z[:30000], 3e-9)):
        cfg = C[name]
        taus = np.concatenate([ID_GRID, L.local_grid(cfg)])          # seal §4 (review m5: G0-s too)
        R = L.rhs_dirichlet(cfg, taus, 1, None, 0)
        e_rhs = R["err"]                                               # derived bounds (review M4)
        parts = (L.eps_data_zero(cfg, zsub, taus, delta), L.eps_float_zero(cfg, zsub, taus),
                 np.full(len(taus), L.eps_trunc(cfg, zeta_density(cfg.E_hi) + 1)), e_rhs)
        save(name, taus, R["total"], parts, dict(config=cfg_json(cfg), n_levels=int(len(zsub))))
        eps = L.tolerance(*parts)
        # red paths (seal §8), magnitudes from the RHS only
        if name in ("G0", "G0c"):
            lam = L.mangoldt_upto(100000)
            # RP1: drop all k >= 2 prime-power terms = the prime sum restricted to non-primes
            nonprime = lambda n: np.where([(lam[k] > 0 and round(math.exp(lam[k])) != k) for k in n], 1.0, 0.0)
            R_np = L.prime_sum_dirichlet(cfg, taus, chi=nonprime)[0]
            reach(name, "RP1_drop_k>=2", R_np, eps)
            reach(name, "RP2_flip_prime_sign", 2 * R["prime"], eps)
            reach(name, "RP3_shift_100delta", taus * 100 * delta * np.abs(R["total"]), eps,
                  "first-order estimate tau*100*delta*|RHS|")
        if name.startswith("G0s"):
            reach(name, "RP13_drop_gamma", R["gamma"], eps)
            reach(name, "RP14_drop_pole", R["pole"], eps)
            # RP15: Re psi(1/4 + iu/2) replaced by the pinned asymptotic ph6lib.psi_asymptotic (review m1)
            u = np.arange(cfg.T0 - 13 * cfg.sigma, cfg.T0 + 13 * cfg.sigma, 0.025)
            f = L.w(cfg, u) * (np.real(L.digamma(0.25 + 0.5j * u)) - L.psi_asymptotic(u))
            dg = np.array([L.trapezoid_integral(np.exp(1j * t * u) * f, u) for t in taus]) / (2 * math.pi)
            reach(name, "RP15_asymptotic_psi", dg, eps)
            mirror_upper = np.full(len(taus), float(np.sum(L.w(cfg, -z))))
            reach(name, "RP16_drop_mirror(upper bound)", mirror_upper, eps,
                  "upper bound sum w(-gamma); if INAPPLICABLE here it is INAPPLICABLE")

    # ---- G1 per sector
    cfg = C["G1"]
    I = L.selberg_integrals(cfg, ID_GRID)
    RS = {}
    for sector, rl in (("even", r_even), ("odd", r_odd)):
        Rs = L.rhs_selberg(cfg, ID_GRID, sector, ch, cg, integrals=I)
        RS[sector] = Rs
        wsum = L.w(cfg, rl) + L.w(cfg, -rl)
        wp = (np.abs(rl - cfg.T0) * L.w(cfg, rl) + np.abs(-rl - cfg.T0) * L.w(cfg, -rl)) / cfg.sigma ** 2
        d_eff = 5e-9 + 2.0 ** -53 * float(np.max(rl))
        e_data = d_eff * (ID_GRID * wsum.sum() + wp.sum())
        e_float = 2.0 ** -51 * (ID_GRID * (wsum * rl).sum() + wsum.sum()) + 2 * 2.0 ** -53 * wsum.sum()
        e_trunc = np.full(len(ID_GRID), L.eps_trunc(cfg, cfg.E_hi / 6.0 + 1))
        terms = [Rs[k] for k in ("ident", "elliptic", "hyperbolic", "glide", "g0", "psi", "prime") if k in Rs]
        e_rhs = Rs["err"] + 8 * L.EPS64 * sum(np.abs(t) for t in terms)
        parts = (e_data, e_float, e_trunc, e_rhs)
        save(f"G1_{sector}", ID_GRID, Rs["total"], parts, dict(config=cfg_json(cfg), n_levels=int(len(rl))))
        eps = L.tolerance(*parts)
        reach(f"G1_{sector}", "RP5_elliptic_x2", Rs["elliptic"], eps)
        reach(f"G1_{sector}", "RP6_drop_R", Rs["glide"], eps)
        if sector == "even":
            reach("G1_even", "RP8_drop_scattering", Rs["prime"] - 2 * I["psi_one"][0] / (4 * math.pi), eps,
                  "even-only continuous-spectrum terms: prime lines 2 Lambda(n)/n g(2 log n) and -(2/4pi) int h psi(1+ir)")
        # RP9: hyperbolic classes taken from the glide discriminants (t^2+4 <-> t^2-4)
        wrong = L.selberg_class_terms(cfg, ID_GRID, {t: cg.get(t, 0.0) for t in ch}, "h")
        reach(f"G1_{sector}", "RP9_wrong_discriminant", wrong - Rs["hyperbolic"], eps)
    eps_even = L.tolerance(*[np.load(os.path.join(outdir, "rhs_G1_even.npz"))[f"eps_{i}"] for i in range(4)])
    reach("G1", "RP7_swap_parity", RS["even"]["total"] - RS["odd"]["total"], eps_even,
          "RHS(even) - RHS(odd); swapping labels moves the LHS by this much")

    # ---- G2 (needs the chi zeros for eps_data / eps_float; RHS and reachability need only the config)
    cfg = C["G2"]
    taus = np.concatenate([ID_GRID, L.local_grid(cfg)])
    R = L.rhs_dirichlet(cfg, taus, 4, L.chi4, 1)
    out["gates"]["G2_rhs_only"] = dict(config=cfg_json(cfg))
    if chi_path:
        zc = np.array([float(x) for x in open(chi_path).read().split()])
        check = json.load(open(chi_path.replace(".txt", ".accuracy.json")))
        delta = float(check["delta"])
        e_rhs = R["err"]
        parts = (L.eps_data_zero(cfg, zc, taus, delta), L.eps_float_zero(cfg, zc, taus),
                 np.full(len(taus), L.eps_trunc(cfg, chi_density(cfg.E_hi) + 1)), e_rhs)
        save("G2", taus, R["total"], parts, dict(config=cfg_json(cfg), n_levels=int(len(zc)), delta=delta))
        eps = L.tolerance(*parts)
        R1 = L.rhs_dirichlet(cfg, taus, 4, None, 1)
        reach("G2", "RP10_chi_equiv_1", R1["prime"] - R["prime"], eps)
        R0 = L.rhs_dirichlet(cfg, taus, 4, L.chi4, 0)
        reach("G2", "RP11_wrong_parity_a0", R0["gamma"] - R["gamma"], eps)

    # ---- G4 pickets at G0's configuration (synthetic; Layer A tolerance is float + RHS only)
    cfg = C["G0"]
    taus = np.concatenate([ID_GRID, L.local_grid(cfg)])
    for label, lam in (("confusable", math.log(2)), ("incommensurate", 1.2345)):
        lev = L.picket_levels(cfg, lam)
        rhs, smooth = L.rhs_picket(cfg, taus, lam)
        ws = L.w(cfg, lev)
        e_float = 2.0 ** -51 * (taus * (ws * np.abs(lev)).sum() + ws.sum()) + 2 * 2.0 ** -53 * ws.sum()
        kk = np.arange(-60, 61)
        e_rhs = 8 * L.EPS64 * (lam / (2 * math.pi)) * cfg.sigma * math.sqrt(2 * math.pi) * \
            np.array([np.sum(np.exp(-(cfg.sigma ** 2) * (t - kk * lam) ** 2 / 2) * (cfg.T0 * abs(t) + 8)) for t in taus])
        parts = (np.zeros(len(taus)), e_float, np.zeros(len(taus)), e_rhs)
        save(f"G4_{label}", taus, rhs, parts, dict(config=cfg_json(cfg), lam=lam, n_levels=int(len(lev))))
        eps = L.tolerance(*parts)
        reach(f"G4_{label}", "RP12_brief_v1_bc", (np.exp(taus / 2) - 1) * np.abs(rhs), eps,
              "brief-v1 BC: eigenvalues E_n - i/2 multiply the picket sum by e^{tau/2}")
    out["reachability"]["G0:RP4_plant_log6"] = dict(max_ratio=2.0, status="REACHABLE",
                                                    note="by construction: a planted line of 2 B_6 at log 6")

    out["wall_s"] = round(time.time() - t_start, 1)
    with open(os.path.join(outdir, "preread_tables.json"), "w") as f:
        json.dump(out, f, indent=1)


# ------------------------------------------------------------------ nulls
def _one_draw(args):
    kind, seed, cfgd, target = args
    cfg = L.Config(**cfgd)
    rng = np.random.default_rng(seed)
    nbar = L.nbar_zeta if target == "zeta" else L.nbar_chi
    lev = L.null_levels(kind, nbar, cfg.E_hi, rng)
    lev = lev[lev <= cfg.E_hi]                 # the null list is "complete" to E_hi, as the target's list is
    taus = L.local_grid(cfg)
    S, M = L.zero_sums(cfg, lev, taus)
    s = np.diff(lev)
    u = nbar(lev)
    su = np.diff(u)
    rt = float((np.minimum(su[:-1], su[1:]) / np.maximum(su[:-1], su[1:])).mean())
    return kind, seed, S + M, rt, len(lev)


def nulls(outdir, name, n_gue, n_poi, nproc):
    from multiprocessing import Pool
    tab = json.load(open(os.path.join(outdir, "preread_tables.json")))
    cfgd = tab["configs"][name]
    cfg = L.Config(**cfgd)
    target = "chi" if name == "G2" else "zeta"
    taus = L.local_grid(cfg)
    q, chi, a = (4, L.chi4, 1) if target == "chi" else (1, None, 0)
    Sm = L.rhs_dirichlet(cfg, taus, q, chi, a)["smooth"]
    jobs = [("gue", CALIB_SEEDS["gue"] + i, cfgd, target) for i in range(n_gue)] + \
           [("poisson", CALIB_SEEDS["poisson"] + i, cfgd, target) for i in range(n_poi)]
    t0 = time.time()
    with Pool(nproc) as pool:
        res = pool.map(_one_draw, jobs, chunksize=1)
    out = {}
    for kind in ("gue", "poisson"):
        rows = [r for r in res if r[0] == kind]
        rvals = np.array([(r[2] - Sm) / cfg.norm for r in rows])
        cs = np.array([L.readout(cfg, taus, rv) for rv in rvals])
        B, s = L.band(cs, ALPHA)
        # null known answer (seal §7): GUE pointwise variance (tau/2pi) sigma sqrt(pi) -> normalised tau sqrt(pi)/sigma;
        # Poisson sum w^2 = int rho w^2; propagated through the joint least squares with the matching covariance.
        pred = predicted_s(cfg, kind, target)
        ratio = (s / pred)
        np.savez_compressed(os.path.join(outdir, f"nulls_{name}_{kind}.npz"), c=cs, B=B, s=s, pred=pred,
                            seeds=np.array([r[1] for r in rows]), rtilde=np.array([r[3] for r in rows]),
                            nlev=np.array([r[4] for r in rows]))
        out[kind] = dict(n_draws=len(rows), s_over_pred_min=float(ratio.min()), s_over_pred_max=float(ratio.max()),
                         known_answer_20pct="PASS" if np.all(np.abs(ratio - 1) <= 0.2) else "FAIL",
                         rtilde_mean=float(np.mean([r[3] for r in rows])),
                         B_at_log2=float(B[0]), B_at_log90=float(B[-1]))
        print(name, kind, out[kind], flush=True)
    out["wall_s"] = round(time.time() - t0, 1)
    with open(os.path.join(outdir, f"nulls_{name}.json"), "w") as f:
        json.dump(out, f, indent=1)


def predicted_s(cfg, kind, target):
    """Predicted s_n for the joint-LS coefficient under a Gaussian-process null with the window's covariance.
    Pointwise: GUE Var S(tau) = (tau/2pi) sigma sqrt(pi) (form factor K(t)=t integrated over the window; the density
    cancels), Poisson Var S = int rho(E) w(E)^2 dE. Covariance between grid points tau_j, tau_k: that variance times
    exp(-sigma^2 (tau_j - tau_k)^2/4) exp(i (tau_j - tau_k) T0) (the transform of w^2)."""
    ns = L.LINE_NS
    taus = L.local_grid(cfg)
    ln = np.log(ns.astype(float))
    d = taus[:, None] - ln[None, :]
    A = np.exp(-(cfg.sigma ** 2) * d ** 2 / 2) * np.exp(1j * d * cfg.T0)
    P = np.linalg.pinv(A)                                                   # (n_lines, n_tau)
    if kind == "gue":
        var = taus / (2 * math.pi) * cfg.sigma * math.sqrt(math.pi)
    else:
        E = np.linspace(max(1.0, cfg.T0 - 12 * cfg.sigma), cfg.T0 + 12 * cfg.sigma, 20001)
        dens = np.log(E * (4 if target == "chi" else 1) / (2 * math.pi)) / (2 * math.pi)
        var = np.full(len(taus), np.trapezoid(dens * L.w(cfg, E) ** 2, E))
    var = var / cfg.norm ** 2
    dt = taus[:, None] - taus[None, :]
    Cov = np.sqrt(np.outer(var, var)) * np.exp(-(cfg.sigma ** 2) * dt ** 2 / 4) * np.exp(1j * dt * cfg.T0)
    return np.sqrt(np.real(np.einsum("ij,jk,ik->i", P, Cov, P.conj())))


ARSRH_RTILDE_BAND = (0.5952, 0.6065)    # arsrh Phase 1 matched-window (W = 10,000) tridiagonal GUE 95% band (PHASE1_FINDINGS)


def known_answers(outdir):
    """Seal §7 null known answers from the saved calibration draws, evaluated two ways (review M1):
    (literal) the sealed pointwise formula, mean |c_n|^2 within 20% for every n;
    (LS) the least-squares-propagated prediction P Cov P^H (ph6 preread.predicted_s), with the pooled median ratio
    and the per-n spread reported. Plus the <r~> check against the arsrh Phase-1 band (review M2)."""
    tab = json.load(open(os.path.join(outdir, "preread_tables.json")))
    res = {}
    for name in ("G0", "G0c", "G2"):
        cfg = L.Config(**tab["configs"][name])
        target = "chi" if name == "G2" else "zeta"
        q = 4 if target == "chi" else 1
        for kind in ("gue", "poisson"):
            p = os.path.join(outdir, f"nulls_{name}_{kind}.npz")
            if not os.path.exists(p):
                continue
            d = np.load(p)
            mc2 = np.mean(np.abs(d["c"]) ** 2, axis=0)
            E = np.linspace(max(1.0, cfg.T0 - 12 * cfg.sigma), cfg.T0 + 12 * cfg.sigma, 20001)
            dens = np.log(E * q / (2 * math.pi)) / (2 * math.pi)
            sumw2 = np.trapezoid(dens * L.w(cfg, E) ** 2, E)
            tauH = math.log(cfg.T0 / (2 * math.pi))                      # literal sealed tau_H (review m12)
            ns = L.LINE_NS.astype(float)
            lit = sumw2 * (np.minimum(np.log(ns) / tauH, 1.0) if kind == "gue" else 1.0) / cfg.norm ** 2
            r_lit = mc2 / lit
            r_ls = mc2 / d["pred"] ** 2
            res[f"{name}_{kind}"] = dict(
                literal_ratio_median=float(np.median(r_lit)), literal_n_outside_20pct=int(np.sum(np.abs(r_lit - 1) > 0.2)),
                literal_verdict="PASS" if np.all(np.abs(r_lit - 1) <= 0.2) else "FAIL",
                ls_ratio_median=float(np.median(r_ls)), ls_ratio_min=float(np.min(r_ls)), ls_ratio_max=float(np.max(r_ls)),
                ls_n_outside_20pct=int(np.sum(np.abs(r_ls - 1) > 0.2)),
                rtilde_mean=float(np.mean(d["rtilde"])),
                rtilde_in_arsrh_band=bool(ARSRH_RTILDE_BAND[0] <= np.mean(d["rtilde"]) <= ARSRH_RTILDE_BAND[1])
                if kind == "gue" else None)
            print(name, kind, res[f"{name}_{kind}"])
    with open(os.path.join(outdir, "null_known_answers.json"), "w") as f:
        json.dump(res, f, indent=1)


def design(outdir):
    rows = {}
    for name, wkind in (("G0", "zeta"), ("G0c", "zeta"), ("G2", "chi4")):
        p = os.path.join(outdir, f"nulls_{name}_gue.npz")
        if not os.path.exists(p):
            continue
        B = np.load(p)["B"]
        a = L.weights(wkind)
        pp = L.is_prime_power()
        R = L.LINE_NS[pp & (a != 0) & (np.abs(a) >= 2 * B)]
        nz = int(np.sum(pp & (a != 0)))
        M_w = {m for m in L.T3_MIN_SET if a[list(L.LINE_NS).index(m)] != 0}       # proposed A3
        rows[name] = dict(weights=wkind, R=R.tolist(), size=f"{len(R)}/{nz}",
                          contains_M_w=bool(M_w <= set(R.tolist())), M_w=sorted(M_w))
        if name == "G0c":
            d = np.abs(L.weights("zeta") - L.weights("chi4")) / B
            rows[name]["RP17_reach_ratio"] = float(np.max(d))
        print(name, rows[name])
    with open(os.path.join(outdir, "design_table.json"), "w") as f:
        json.dump(rows, f, indent=1)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "tables":
        tables(*sys.argv[2:5], sys.argv[5] if len(sys.argv) > 5 else None)
    elif mode == "nulls":
        nulls(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]))
    elif mode == "design":
        design(sys.argv[2])
    elif mode == "known":
        known_answers(sys.argv[2])
    else:
        raise SystemExit(mode)

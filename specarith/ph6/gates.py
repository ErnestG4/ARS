"""Phase 6 gate runner (seal PH6_SEAL_6.0.md §5, §6, §8). Refuses to run unless seals/PH6_SEAL_6.0.json exists and
every file it pins has the pinned sha256.

Usage:  python gates.py run  PREREAD_DIR OUTDIR ZEROS1 MAASS_CSV CHI4_ZEROS    # the sealed gate run (after the seal)
        python gates.py dry  OUTDIR ZEROS1                                     # dry run: disclosed pilot only (§11)

The dry run touches only what the disclosed pilot already touched (ζ zeros with γ <= 144 at T0 = 60, sigma = 6) plus
synthetic spectra (pickets and nulls at a small non-gate configuration). It exercises the code paths; it is not a gate.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np
from scipy.stats import binom

import ph6lib as L

HERE = os.path.dirname(os.path.abspath(__file__))
SEAL_JSON = os.path.join(HERE, "seals", "PH6_SEAL_6.0.json")
ALPHA = 0.01
HELDOUT_SEEDS = {"gue": 1100, "poisson": 2100}          # seal §7: the second 100 seeds of each family
PICKETS = {"confusable": math.log(2), "incommensurate": 1.2345}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check_seal():
    if not os.path.exists(SEAL_JSON):
        raise SystemExit("REFUSED: seals/PH6_SEAL_6.0.json does not exist (the seal commit has not been made)")
    seal = json.load(open(SEAL_JSON))
    bad = [p for p, h in seal["files"].items() if sha256(p) != h]
    if bad:
        raise SystemExit(f"REFUSED: pinned files changed since the seal: {bad}")
    return seal


# ------------------------------------------------------------------ Layer A
def layer_a(lhs, rhs, eps):
    ratio = np.abs(lhs - rhs) / eps
    return dict(verdict="PASS" if np.max(ratio) <= 1 else "FAIL", max_ratio=float(np.max(ratio)),
                tau_at_max=None)


def red_path(name, lhs, rhs_mod, eps, reach_status):
    """A red path must FAIL. Returns FIRED (it failed, as required), DID_NOT_FIRE, or INAPPLICABLE."""
    if reach_status == "INAPPLICABLE":
        return dict(red_path=name, result="INAPPLICABLE")
    m = float(np.max(np.abs(lhs - rhs_mod) / eps))
    return dict(red_path=name, result="FIRED" if m > 1 else "DID_NOT_FIRE", max_ratio=m)


# ------------------------------------------------------------------ Layer B
def layer_b(cfg, taus_local, S_plus_M, smooth):
    r = (S_plus_M - smooth) / cfg.norm
    return L.readout(cfg, taus_local, r)


def nonprime_power_chi(n):
    lam = L.mangoldt_upto(int(np.max(n)))
    return np.array([1.0 if (lam[k] > 0 and round(math.exp(lam[k])) != k) else 0.0 for k in np.asarray(n)])


def zeta_like_gate(name, cfg, zeros, pre, reach, q=1, chi=None, a=0, delta=3e-9, layer_b_band=None):
    """Layer A + red paths (+ Layer B readout when a band is given) for a ζ or χ₋₄ gate."""
    taus, rhs, eps = pre["taus"], pre["rhs"], pre["eps"]
    S, M = L.zero_sums(cfg, zeros, taus)
    lhs = S + M
    R = L.rhs_dirichlet(cfg, taus, q, chi, a)
    assert np.allclose(R["total"], rhs, rtol=0, atol=1e-9 * np.max(np.abs(rhs))), "RHS differs from the pre-read"
    res = dict(gate=name, layer_a=layer_a(lhs, rhs, eps), red_paths=[])
    st = lambda rp: reach.get(f"{name}:{rp}", {}).get("status", "REACHABLE")
    if q == 1 and name in ("G0", "G0c"):
        Pnp = L.prime_sum_dirichlet(cfg, taus, chi=nonprime_power_chi)[0]
        res["red_paths"].append(red_path("RP1_drop_k>=2", lhs, rhs + Pnp, eps, st("RP1_drop_k>=2")))
        res["red_paths"].append(red_path("RP2_flip_prime_sign", lhs, rhs + 2 * R["prime"], eps, st("RP2_flip_prime_sign")))
        S3, M3 = L.zero_sums(cfg, zeros + 100 * delta, taus)
        res["red_paths"].append(red_path("RP3_shift_100delta", S3 + M3, rhs, eps, st("RP3_shift_100delta")))
    if name.startswith("G0s"):
        res["red_paths"].append(red_path("RP13_drop_gamma", lhs, rhs - R["gamma"], eps, st("RP13_drop_gamma")))
        res["red_paths"].append(red_path("RP14_drop_pole", lhs, rhs - R["pole"], eps, st("RP14_drop_pole")))
        u = np.arange(cfg.T0 - 13 * cfg.sigma, cfg.T0 + 13 * cfg.sigma, 0.05)
        f = L.w(cfg, u) * np.log(np.maximum(np.abs(u), 1e-300) / 2)
        asym = np.array([L.trapezoid_integral(np.exp(1j * t * u) * f, u) for t in taus]) / (2 * math.pi)
        res["red_paths"].append(red_path("RP15_asymptotic_psi", lhs, rhs - R["gamma"] + asym, eps,
                                         st("RP15_asymptotic_psi")))
        res["red_paths"].append(red_path("RP16_drop_mirror", S, rhs, eps,
                                         st("RP16_drop_mirror(upper bound)")))
    if q == 4:
        R1 = L.rhs_dirichlet(cfg, taus, 4, None, 1)
        res["red_paths"].append(red_path("RP10_chi_equiv_1", lhs, R1["total"], eps, st("RP10_chi_equiv_1")))
        R0 = L.rhs_dirichlet(cfg, taus, 4, chi, 0)
        res["red_paths"].append(red_path("RP11_wrong_parity_a0", lhs, R0["total"], eps, st("RP11_wrong_parity_a0")))
    if layer_b_band is not None:
        loc = L.local_grid(cfg)
        Sl, Ml = L.zero_sums(cfg, zeros, loc)
        sm = L.rhs_dirichlet(cfg, loc, q, chi, a)["smooth"]
        c = layer_b(cfg, loc, Sl + Ml, sm)
        B = layer_b_band
        own = "zeta" if q == 1 else "chi4"
        other = "chi4" if q == 1 else "zeta"
        v_own = L.t3_verdict(c, L.weights(own), B)
        v_other = L.t3_verdict(c, L.weights(other), B)
        res["layer_b"] = dict(own_weights=own, verdict_own=v_own, other_weights=other, verdict_other=v_other,
                              c_first=[[int(n), float(np.real(x)), float(np.imag(x))] for n, x in zip(L.LINE_NS[:8], c[:8])])
        if q == 1 and name == "G0":
            # RP4: plant a line of 2 B at log 6 in r(tau): SILENCE must flag
            i6 = list(L.LINE_NS).index(6)
            d = loc - math.log(6)
            plant = 2 * B[i6] * np.exp(-(cfg.sigma ** 2) * d ** 2 / 2) * np.exp(1j * d * cfg.T0)
            c4 = L.readout(cfg, loc, (Sl + Ml - sm) / cfg.norm + plant)
            v4 = L.t3_verdict(c4, L.weights("zeta"), B)
            res["red_paths"].append(dict(red_path="RP4_plant_log6", result="FIRED" if 6 in
                                         v4[1].get("failed_arms", {}).get("SILENCE", []) else "DID_NOT_FIRE"))
        if name == "G0c":
            res["red_paths"].append(dict(red_path="RP17_read_vs_chi4", result="FIRED" if v_other[0] == "FAIL"
                                         else "DID_NOT_FIRE"))
            R = set(v_own[1].get("R", []))
            res["g0c_checks"] = dict(M_in_R=set(L.T3_MIN_SET) <= R, R_size=len(R), R_size_in_22_30=22 <= len(R) <= 30)
    return res


def maass_gate(cfg, r_even, r_odd, pre_even, pre_odd, reach, classdata):
    ch, cg = classdata
    out = {}
    taus = pre_even["taus"]
    I = L.selberg_integrals(cfg, taus)
    lhs = {"even": L.maass_sector_sum(cfg, r_even, taus, True), "odd": L.maass_sector_sum(cfg, r_odd, taus, False)}
    pre = {"even": pre_even, "odd": pre_odd}
    for sector in ("even", "odd"):
        Rs = L.rhs_selberg(cfg, taus, sector, ch, cg, integrals=I)
        assert np.allclose(Rs["total"], pre[sector]["rhs"], rtol=0, atol=1e-9 * np.max(np.abs(Rs["total"])))
        eps = pre[sector]["eps"]
        st = lambda rp: reach.get(f"G1_{sector}:{rp}", {}).get("status", "REACHABLE")
        res = dict(gate=f"G1_{sector}", layer_a=layer_a(lhs[sector], Rs["total"], eps), red_paths=[])
        res["red_paths"].append(red_path("RP5_elliptic_x2", lhs[sector], Rs["total"] + Rs["elliptic"], eps,
                                         st("RP5_elliptic_x2")))
        res["red_paths"].append(red_path("RP6_drop_R", lhs[sector], Rs["total"] - Rs["glide"], eps, st("RP6_drop_R")))
        other = "odd" if sector == "even" else "even"
        res["red_paths"].append(red_path("RP7_swap_parity", lhs[other], Rs["total"], eps,
                                         reach.get("G1:RP7_swap_parity", {}).get("status", "REACHABLE")))
        if sector == "even":
            res["red_paths"].append(red_path("RP8_drop_scattering", lhs[sector],
                                             Rs["total"] - Rs["prime"] + 2 * I["psi_one"][0] / (4 * math.pi), eps,
                                             st("RP8_drop_scattering")))
        wrong = L.selberg_class_terms(cfg, taus, {t: cg.get(t, 0.0) for t in ch}, "h")
        res["red_paths"].append(red_path("RP9_wrong_discriminant", lhs[sector], Rs["total"] - Rs["hyperbolic"] + wrong,
                                         eps, st("RP9_wrong_discriminant")))
        out[sector] = res
    e_sum = pre_even["eps"] + pre_odd["eps"]
    out["G1a_sum_implied"] = layer_a(lhs["even"] + lhs["odd"], pre_even["rhs"] + pre_odd["rhs"], e_sum)
    out["G1b_difference_implied"] = layer_a(lhs["even"] - lhs["odd"], pre_even["rhs"] - pre_odd["rhs"], e_sum)
    return out


def null_gate(name, cfg, target, bands):
    """G3 / G3-c on held-out draws (seal §8): silence vs zero weights within alpha + binomial 99% allowance (each family
    against its own band); vs zeta weights T3 = FAIL or NOT RESOLVABLE in 100% of draws; positive control (GUE + planted
    zeta lines) T3 = PASS in >= 95% of draws."""
    loc = L.local_grid(cfg)
    q, chi, a = (4, L.chi4, 1) if target == "chi" else (1, None, 0)
    sm = L.rhs_dirichlet(cfg, loc, q, chi, a)["smooth"]
    nbar = L.nbar_chi if target == "chi" else L.nbar_zeta
    aw = L.weights("zeta")
    d = loc[:, None] - np.log(L.LINE_NS.astype(float))[None, :]
    templ = np.exp(-(cfg.sigma ** 2) * d ** 2 / 2) * np.exp(1j * d * cfg.T0)
    res = dict(gate=name)
    for kind in ("gue", "poisson"):
        B = bands[kind]
        n_exceed, n_zeta_reject, n_pos_pass, n = 0, 0, 0, 100
        for i in range(n):
            rng = np.random.default_rng(HELDOUT_SEEDS[kind] + i)
            lev = L.null_levels(kind, nbar, cfg.E_hi, rng)
            lev = lev[lev <= cfg.E_hi]
            S, M = L.zero_sums(cfg, lev, loc)
            r = (S + M - sm) / cfg.norm
            c = L.readout(cfg, loc, r)
            v0 = L.t3_verdict(c, L.weights("zero"), B)
            n_exceed += v0[0] == "FAIL"
            vz = L.t3_verdict(c, aw, bands["gue"])
            n_zeta_reject += vz[0] in ("FAIL", "NOT RESOLVABLE")
            if kind == "gue":
                cp = L.readout(cfg, loc, r + templ @ aw)
                n_pos_pass += L.t3_verdict(cp, aw, bands["gue"])[0] == "PASS"
        allow = int(binom.ppf(0.99, n, ALPHA))
        res[kind] = dict(silence_exceed=n_exceed, allowance=allow, silence="PASS" if n_exceed <= allow else "FAIL",
                         zeta_rejected=n_zeta_reject, zeta_rejection="PASS" if n_zeta_reject == n else "FAIL")
        if kind == "gue":
            res[kind].update(positive_control_pass=n_pos_pass,
                             positive_control="PASS" if n_pos_pass >= 95 else "FAIL")
    return res


def picket_gate(cfg, B):
    out = {}
    loc = L.local_grid(cfg)
    taus = np.concatenate([0.5 + 0.001 * np.arange(4001), loc])
    for label, lam in PICKETS.items():
        lev = L.picket_levels(cfg, lam)
        lhs = L.picket_sum(cfg, lev, taus)
        rhs, smooth = L.rhs_picket(cfg, taus, lam)
        ws = L.w(cfg, lev)
        eps = L.tolerance(L.EPS64 * (taus * (ws * np.abs(lev)).sum() + ws.sum() * (math.log2(len(lev)) + 4)),
                          1e-12 * np.maximum(1.0, np.abs(rhs)))
        res = dict(layer_a=layer_a(lhs, rhs, eps))
        lhs12 = lhs * np.exp(taus / 2)                     # RP12: brief-v1 BC, eigenvalues E_n - i/2
        res["RP12_brief_v1_bc"] = red_path("RP12", lhs12, rhs, eps, "REACHABLE")
        ll = L.picket_sum(cfg, lev, loc)
        sm = L.rhs_picket(cfg, loc, lam)[1]
        c = L.readout(cfg, loc, (ll - sm) / cfg.norm)
        res["vs_zeta"] = L.t3_verdict(c, L.weights("zeta"), B)
        res["vs_zero"] = L.t3_verdict(c, L.weights("zero"), B)
        res["c_at"] = {int(n): [float(np.real(c[i])), float(np.imag(c[i]))] for i, n in enumerate(L.LINE_NS)
                       if n in (2, 3, 4, 5, 7, 8, 16, 32, 64)}
        if label == "confusable":
            fires = [int(n) for i, n in enumerate(L.LINE_NS) if abs(c[i]) > B[i]]
            res["position_fires_at"] = fires
            res["expected_fires"] = [2, 4, 8, 16, 32, 64]
            res["silent_at_3_5_7"] = all(abs(c[list(L.LINE_NS).index(n)]) <= B[list(L.LINE_NS).index(n)] for n in (3, 5, 7))
        out[label] = res
    return out


def main_run(pre_dir, outdir, zeros1_path, maass_path, chi_path):
    seal = check_seal()
    import classes
    from preread import load_maass
    tab = json.load(open(os.path.join(pre_dir, "preread_tables.json")))
    reach = tab["reachability"]
    C = {k: L.Config(**v) for k, v in tab["configs"].items()}
    z = np.loadtxt(zeros1_path)
    rE, rO = load_maass(maass_path)
    zc = np.array([float(x) for x in open(chi_path).read().split()])
    pre = lambda n: np.load(os.path.join(pre_dir, f"rhs_{n}.npz"))
    band = lambda n, k: np.load(os.path.join(pre_dir, f"nulls_{n}_{k}.npz"))["B"]
    _, ls = classes.pari_counts(30, 30)
    ch = {t: ls[("h", t)] / 2 for (k, t) in ls if k == "h"}
    cg = {t: ls[("g", t)] for (k, t) in ls if k == "g"}
    results = dict(seal_commit=seal.get("commit"), gates={})
    results["gates"]["G0"] = zeta_like_gate("G0", C["G0"], z, pre("G0"), reach, layer_b_band=band("G0", "gue"))
    for s in ("G0s_a", "G0s_b", "G0s_c"):
        results["gates"][s] = zeta_like_gate(s, C[s], z, pre(s), reach)
    results["gates"]["G0c"] = zeta_like_gate("G0c", C["G0c"], z[:30000], pre("G0c"), reach,
                                             layer_b_band=band("G0c", "gue"))
    results["gates"]["G1"] = maass_gate(C["G1"], rE, rO, pre("G1_even"), pre("G1_odd"), reach, (ch, cg))
    delta = json.load(open(chi_path.replace(".txt", ".accuracy.json")))["delta"]
    results["gates"]["G2"] = zeta_like_gate("G2", C["G2"], zc, pre("G2"), reach, q=4, chi=L.chi4, a=1, delta=delta,
                                            layer_b_band=band("G2", "gue"))
    results["gates"]["G3"] = null_gate("G3", C["G0"], "zeta", {k: band("G0", k) for k in ("gue", "poisson")})
    results["gates"]["G3c"] = null_gate("G3c", C["G0c"], "zeta", {k: band("G0c", k) for k in ("gue", "poisson")})
    results["gates"]["G4"] = picket_gate(C["G0"], band("G0", "gue"))
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "gate_results.json"), "w") as f:
        json.dump(results, f, indent=1, default=str)
    print(json.dumps(results, indent=1, default=str)[:20000])


def main_dry(outdir, zeros1_path):
    """Dry run (seal §11): the disclosed pilot configuration only, plus synthetic spectra. Not a gate."""
    os.makedirs(outdir, exist_ok=True)
    z = np.loadtxt(zeros1_path)
    z = z[z <= 144.0]                                    # exactly the pilot's zeros (EF §9: 50 zeros <= 144)
    cfg = L.fixed_config(60.0, 6.0)
    taus = 0.5 + 0.001 * np.arange(4001)
    R = L.rhs_dirichlet(cfg, taus, 1, None, 0)
    eps = L.tolerance(L.eps_data_zero(cfg, z, taus, 3e-9), L.eps_float_zero(cfg, z, taus),
                      np.full(len(taus), L.eps_trunc(cfg, 1.0)), R["err"] + 1e-12 * np.maximum(1, np.abs(R["total"])))
    pre = dict(taus=taus, rhs=R["total"], eps=eps)
    out = dict(pilot_zeta=zeta_like_gate("G0s_pilot", cfg, z, pre, {}))
    # synthetic: pickets and a small null configuration (not gate configurations)
    cfg_s = L.rule_config(0.0, 3000.0)
    loc = L.local_grid(cfg_s)
    cs = []
    for i in range(20):
        lev = L.null_levels("gue", L.nbar_zeta, cfg_s.E_hi, np.random.default_rng(99000 + i))
        lev = lev[lev <= cfg_s.E_hi]
        S, M = L.zero_sums(cfg_s, lev, loc)
        cs.append(L.readout(cfg_s, loc, (S + M - L.rhs_dirichlet(cfg_s, loc, 1, None, 0)["smooth"]) / cfg_s.norm))
    B, s = L.band(np.array(cs))
    out["synthetic_band_small"] = dict(B_log2=float(B[0]), B_log90=float(B[-1]))
    out["synthetic_pickets_small"] = picket_gate(cfg_s, B)
    with open(os.path.join(outdir, "dry_run.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(json.dumps(out, indent=1, default=str)[:6000])


if __name__ == "__main__":
    if sys.argv[1] == "run":
        main_run(*sys.argv[2:7])
    elif sys.argv[1] == "dry":
        main_dry(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(sys.argv[1])

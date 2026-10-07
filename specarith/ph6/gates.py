"""Phase 6 gate runner (seal PH6_SEAL_6.0.md §5, §6, §8). Refuses to run unless seals/PH6_SEAL_6.0.json exists and
every file it pins has the pinned sha256.

Usage:  python gates.py run  PREREAD_DIR OUTDIR ZEROS1 MAASS_CSV CHI4_ZEROS    # the sealed gate run (after the seal)
        python gates.py dry  OUTDIR ZEROS1                                     # dry run: disclosed pilot only (§11)

The dry run touches only what the disclosed pilot already touched (ζ zeros with γ <= 144 at T0 = 60, sigma = 6) plus
synthetic spectra (pickets and nulls at a small non-gate configuration). It exercises the code paths; it is not a gate.

Gate statistics use compensated summation (ph6lib exact=True; seal §5.1). Red-path reachability is read from the
pre-read and FAILS CLOSED: a missing entry stops the run (review M7). Layer B rulings live in rulings.py (review M6).
"""
import hashlib
import json
import math
import os
import sys

import numpy as np
from scipy.stats import binom

import ph6lib as L
import rulings

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


class Reach:
    """Fail-closed reachability lookup (review M7)."""

    def __init__(self, table):
        self.table = table

    def status(self, key):
        if key not in self.table:
            raise KeyError(f"no reachability entry for {key}: the pre-read must declare every red path")
        return self.table[key]["status"]


# ------------------------------------------------------------------ Layer A
def layer_a(lhs, rhs, eps, taus=None):
    assert np.all(eps > 0), "non-positive tolerance"
    ratio = np.abs(lhs - rhs) / eps
    i = int(np.argmax(ratio))
    return dict(verdict="PASS" if ratio[i] <= 1 else "FAIL", max_ratio=float(ratio[i]),
                tau_at_max=None if taus is None else float(taus[i]))


def red_path(name, lhs, rhs_mod, eps, status):
    """A red path must FAIL. Returns FIRED (it failed, as required), DID_NOT_FIRE, or INAPPLICABLE."""
    if status == "INAPPLICABLE":
        return dict(red_path=name, result="INAPPLICABLE")
    assert np.all(eps > 0), "non-positive tolerance"
    m = float(np.max(np.abs(lhs - rhs_mod) / eps))
    return dict(red_path=name, result="FIRED" if m > 1 else "DID_NOT_FIRE", max_ratio=m)


def nonprime_power_chi(n):
    lam = L.mangoldt_upto(int(np.max(n)))
    return np.array([1.0 if (lam[k] > 0 and round(math.exp(lam[k])) != k) else 0.0 for k in np.asarray(n)])


def zeta_like_gate(name, cfg, zeros, pre, reach, q=1, chi=None, a=0, delta=3e-9, band=None):
    """Layer A + red paths (+ Layer B readout and ruling when a band is given) for a ζ or χ₋₄ gate."""
    taus, rhs, eps = pre["taus"], pre["rhs"], pre["eps"]
    S, M = L.zero_sums(cfg, zeros, taus, exact=True)
    lhs = S + M
    R = L.rhs_dirichlet(cfg, taus, q, chi, a)
    assert np.max(np.abs(R["total"] - rhs) / eps) <= 1e-3, "RHS differs from the pre-read"   # review v2 N13
    res = dict(gate=name, layer_a=layer_a(lhs, rhs, eps, taus), red_paths=[])
    st = lambda rp: reach.status(f"{name}:{rp}")
    if q == 1 and name in ("G0", "G0c"):
        Pnp = L.prime_sum_dirichlet(cfg, taus, chi=nonprime_power_chi)[0]
        res["red_paths"].append(red_path("RP1_drop_k>=2", lhs, rhs + Pnp, eps, st("RP1_drop_k>=2")))
        res["red_paths"].append(red_path("RP2_flip_prime_sign", lhs, rhs + 2 * R["prime"], eps,
                                         st("RP2_flip_prime_sign")))
        S3, M3 = L.zero_sums(cfg, zeros + 100 * delta, taus, exact=True)
        res["red_paths"].append(red_path("RP3_shift_100delta", S3 + M3, rhs, eps, st("RP3_shift_100delta")))
    if name.startswith("G0s"):
        res["red_paths"].append(red_path("RP13_drop_gamma", lhs, rhs - R["gamma"], eps, st("RP13_drop_gamma")))
        res["red_paths"].append(red_path("RP14_drop_pole", lhs, rhs - R["pole"], eps, st("RP14_drop_pole")))
        u = np.arange(cfg.T0 - 13 * cfg.sigma, cfg.T0 + 13 * cfg.sigma, 0.025)
        f = L.w(cfg, u) * (np.real(L.digamma(0.25 + 0.5j * u)) - L.psi_asymptotic(u))
        dg = np.array([L.trapezoid_integral(np.exp(1j * t * u) * f, u) for t in taus]) / (2 * math.pi)
        res["red_paths"].append(red_path("RP15_asymptotic_psi", lhs, rhs - dg, eps, st("RP15_asymptotic_psi")))
        res["red_paths"].append(red_path("RP16_drop_mirror", S, rhs, eps, st("RP16_drop_mirror(upper bound)")))
    if q == 4:
        R1 = L.rhs_dirichlet(cfg, taus, 4, None, 1)
        res["red_paths"].append(red_path("RP10_chi_equiv_1", lhs, R1["total"], eps, st("RP10_chi_equiv_1")))
        R0 = L.rhs_dirichlet(cfg, taus, 4, chi, 0)
        res["red_paths"].append(red_path("RP11_wrong_parity_a0", lhs, R0["total"], eps, st("RP11_wrong_parity_a0")))
    if band is not None:
        loc = L.local_grid(cfg)
        Sl, Ml = L.zero_sums(cfg, zeros, loc, exact=True)
        sm = L.rhs_dirichlet(cfg, loc, q, chi, a)["smooth"]
        c = L.readout(cfg, loc, (Sl + Ml - sm) / cfg.norm)
        own, other = ("zeta", "chi4") if q == 1 else ("chi4", "zeta")
        v_own = L.t3_verdict(c, L.weights(own), band)
        v_other = L.t3_verdict(c, L.weights(other), band)
        if q == 1 and name == "G0c":
            ruling = rulings.g0c_layer_b(v_own, v_other)
        elif q == 1:
            ruling = rulings.g0_layer_b(v_own, v_other)
        else:
            ruling = rulings.g2_layer_b(c, band, v_own, v_other)
        res["layer_b"] = dict(verdict=ruling[0], reasons=ruling[1], own_weights=own, verdict_own=v_own,
                              other_weights=other, verdict_other=v_other,
                              c=[[int(n), float(np.real(x)), float(np.imag(x))] for n, x in zip(L.LINE_NS, c)],
                              B=band.tolist())
        if q == 1 and name == "G0":
            i6 = list(L.LINE_NS).index(6)
            d = loc - math.log(6)
            plant = 2 * band[i6] * np.exp(-(cfg.sigma ** 2) * d ** 2 / 2) * np.exp(1j * d * cfg.T0)
            c4 = L.readout(cfg, loc, (Sl + Ml - sm) / cfg.norm + plant)
            v4 = L.t3_verdict(c4, L.weights("zeta"), band)
            if reach.status("G0:RP4_plant_log6") == "INAPPLICABLE":
                res["red_paths"].append(dict(red_path="RP4_plant_log6", result="INAPPLICABLE"))
            else:
                res["red_paths"].append(dict(red_path="RP4_plant_log6", result="FIRED" if 6 in
                                             v4[1].get("failed_arms", {}).get("SILENCE", []) else "DID_NOT_FIRE"))
        if name == "G0c":
            if reach.status("G0c:RP17_read_vs_chi4") == "INAPPLICABLE":
                res["red_paths"].append(dict(red_path="RP17_read_vs_chi4", result="INAPPLICABLE"))
            else:
                res["red_paths"].append(dict(red_path="RP17_read_vs_chi4",
                                             result="FIRED" if v_other[0] == "FAIL" else "DID_NOT_FIRE"))
    return res


def maass_gate(cfg, r_even, r_odd, pre_even, pre_odd, reach, classdata):
    ch, cg = classdata
    out = {}
    taus = pre_even["taus"]
    I = L.selberg_integrals(cfg, taus)
    lhs = {"even": L.maass_sector_sum(cfg, r_even, taus, True), "odd": L.maass_sector_sum(cfg, r_odd, taus, False)}
    # RP7: labels swapped -- each sector's identity read on the other sector's levels (with h(i/2) where the even
    # identity requires it)
    swapped = {"even": L.maass_sector_sum(cfg, r_odd, taus, True), "odd": L.maass_sector_sum(cfg, r_even, taus, False)}
    pre = {"even": pre_even, "odd": pre_odd}
    for sector in ("even", "odd"):
        Rs = L.rhs_selberg(cfg, taus, sector, ch, cg, integrals=I)
        eps = pre[sector]["eps"]
        assert np.max(np.abs(Rs["total"] - pre[sector]["rhs"]) / eps) <= 1e-3, "RHS differs from the pre-read"
        st = lambda rp: reach.status(f"G1_{sector}:{rp}")
        res = dict(gate=f"G1_{sector}", layer_a=layer_a(lhs[sector], pre[sector]["rhs"], eps, taus), red_paths=[])
        res["red_paths"].append(red_path("RP5_elliptic_x2", lhs[sector], Rs["total"] + Rs["elliptic"], eps,
                                         st("RP5_elliptic_x2")))
        res["red_paths"].append(red_path("RP6_drop_R", lhs[sector], Rs["total"] - Rs["glide"], eps, st("RP6_drop_R")))
        res["red_paths"].append(red_path("RP7_swap_parity", swapped[sector], Rs["total"], eps,
                                         reach.status("G1:RP7_swap_parity")))
        if sector == "even":
            res["red_paths"].append(red_path("RP8_drop_scattering", lhs[sector],
                                             Rs["total"] - Rs["prime"] + 2 * I["psi_one"][0] / (4 * math.pi), eps,
                                             st("RP8_drop_scattering")))
        wrong = L.selberg_class_terms(cfg, taus, {t: cg.get(t, 0.0) for t in ch}, "h")
        res["red_paths"].append(red_path("RP9_wrong_discriminant", lhs[sector], Rs["total"] - Rs["hyperbolic"] + wrong,
                                         eps, st("RP9_wrong_discriminant")))
        out[sector] = res
    e_sum = pre_even["eps"] + pre_odd["eps"]
    out["G1a_sum_implied"] = layer_a(lhs["even"] + lhs["odd"], pre_even["rhs"] + pre_odd["rhs"], e_sum, taus)
    out["G1b_difference_implied"] = layer_a(lhs["even"] - lhs["odd"], pre_even["rhs"] - pre_odd["rhs"], e_sum, taus)
    return out


def null_gate(name, cfg, target, bands, families=("gue", "poisson"), zeta_reject=("FAIL", "NOT RESOLVABLE")):
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
    for kind in families:
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
            n_zeta_reject += vz[0] in zeta_reject
            if kind == "gue":
                cp = L.readout(cfg, loc, r + templ @ aw)
                n_pos_pass += L.t3_verdict(cp, aw, bands["gue"])[0] == "PASS"
        allow = int(binom.ppf(0.99, n, ALPHA))
        res[kind] = dict(silence_exceed=n_exceed, allowance=allow, silence="PASS" if n_exceed <= allow else "FAIL",
                         zeta_rejected=n_zeta_reject, zeta_rejection="PASS" if n_zeta_reject == n else "FAIL")
        if kind == "gue":
            res[kind].update(positive_control_pass=n_pos_pass,
                             positive_control="PASS" if n_pos_pass >= 95 else "FAIL")
        res[kind]["ruling"] = rulings.g3_null(res[kind], kind)
    res["verdict"] = "PASS" if all(res[k]["ruling"][0] == "PASS" for k in families) else "FAIL"
    return res


def picket_gate(cfg, B, pre=None, reach=None):
    out = {}
    loc = L.local_grid(cfg)
    for label, lam in PICKETS.items():
        lev = L.picket_levels(cfg, lam)
        if pre is not None:
            taus, rhs, eps = pre[label]["taus"], pre[label]["rhs"], pre[label]["eps"]
        else:                                                 # dry run: tolerance built inline
            taus = np.concatenate([0.5 + 0.001 * np.arange(4001), loc])
            rhs, _ = L.rhs_picket(cfg, taus, lam)
            eps = L.tolerance(*L.picket_tolerance(cfg, taus, lam, lev, rhs))
        ws = L.w(cfg, lev)
        keep = ws > 1e-300
        lhs = np.empty(len(taus), dtype=np.complex128)
        for i in range(0, len(taus), 16):
            lhs[i:i + 16] = L._fsum_rows(np.multiply.outer(taus[i:i + 16], lev[keep]), ws[keep])
        res = dict(layer_a=layer_a(lhs, rhs, eps, taus))
        st = "REACHABLE" if reach is None else reach.status(f"G4_{label}:RP12_brief_v1_bc")
        res["RP12_brief_v1_bc"] = red_path("RP12", lhs * np.exp(taus / 2), rhs, eps, st)
        ll = L.picket_sum(cfg, lev, loc)
        sm = L.rhs_picket(cfg, loc, lam)[1]
        c = L.readout(cfg, loc, (ll - sm) / cfg.norm)
        v_zeta = L.t3_verdict(c, L.weights("zeta"), B)
        v_zero = L.t3_verdict(c, L.weights("zero"), B)
        res["vs_zeta"], res["vs_zero"] = v_zeta, v_zero
        res["c_at"] = {int(n): [float(np.real(c[i])), float(np.imag(c[i]))] for i, n in enumerate(L.LINE_NS)
                       if n in (2, 3, 4, 5, 7, 8, 16, 32, 64)}
        res["layer_b"] = rulings.g4_confusable(c, B, v_zeta, lam) if label == "confusable" \
            else rulings.g4_incommensurate(v_zero, v_zeta)
        out[label] = res
    return out


def main_run(pre_dir, outdir, zeros1_path, maass_path, chi_path):
    seal = check_seal()
    import classes
    from preread import load_maass
    tab = json.load(open(os.path.join(pre_dir, "preread_tables.json")))
    reach = Reach(tab["reachability"])
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
    results["gates"]["G0"] = zeta_like_gate("G0", C["G0"], z, pre("G0"), reach, band=band("G0", "gue"))
    for s in ("G0s_a", "G0s_b", "G0s_c"):
        results["gates"][s] = zeta_like_gate(s, C[s], z, pre(s), reach)
    results["gates"]["G0c"] = zeta_like_gate("G0c", C["G0c"], z[:30000], pre("G0c"), reach, band=band("G0c", "gue"))
    results["gates"]["G1"] = maass_gate(C["G1"], rE, rO, pre("G1_even"), pre("G1_odd"), reach, (ch, cg))
    delta = json.load(open(chi_path.replace(".txt", ".accuracy.json")))["delta"]
    results["gates"]["G2"] = zeta_like_gate("G2", C["G2"], zc, pre("G2"), reach, q=4, chi=L.chi4, a=1, delta=delta,
                                            band=band("G2", "gue"))
    results["gates"]["G3"] = null_gate("G3", C["G0"], "zeta", {k: band("G0", k) for k in ("gue", "poisson")})
    # seal §8 G3-c row: held-out GUE only; vs zeta weights T3 = FAIL (not NOT RESOLVABLE) in 100% (review v2 N5b)
    results["gates"]["G3c"] = null_gate("G3c", C["G0c"], "zeta", {k: band("G0c", k) for k in ("gue", "poisson")},
                                        families=("gue",), zeta_reject=("FAIL",))
    results["gates"]["G4"] = picket_gate(C["G0"], band("G0", "gue"),
                                         pre={lab: pre(f"G4_{lab}") for lab in PICKETS}, reach=reach)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "gate_results.json"), "w") as f:
        json.dump(results, f, indent=1, default=str)
    print(json.dumps(results, indent=1, default=str)[:20000])


def main_dry(outdir, zeros1_path):
    """Dry run (seal §11): the disclosed pilot configuration only, plus synthetic spectra. Not a gate. Reachability for
    the pilot window is computed inline from the RHS, by the pre-read's rule."""
    os.makedirs(outdir, exist_ok=True)
    z = np.loadtxt(zeros1_path)
    z = z[z <= 144.0]                                    # exactly the pilot's zeros (EF §9: 50 zeros <= 144)
    cfg = L.fixed_config(60.0, 6.0)
    taus = np.concatenate([0.5 + 0.001 * np.arange(4001), L.local_grid(cfg)])
    R = L.rhs_dirichlet(cfg, taus, 1, None, 0)
    eps = L.tolerance(L.eps_data_zero(cfg, z, taus, 3e-9), L.eps_float_zero(cfg, z, taus),
                      np.full(len(taus), L.eps_trunc(cfg, 1.0)), R["err"])
    u = np.arange(cfg.T0 - 13 * cfg.sigma, cfg.T0 + 13 * cfg.sigma, 0.025)
    f = L.w(cfg, u) * (np.real(L.digamma(0.25 + 0.5j * u)) - L.psi_asymptotic(u))
    dg = np.array([L.trapezoid_integral(np.exp(1j * t * u) * f, u) for t in taus]) / (2 * math.pi)
    st = lambda x: "REACHABLE" if np.max(np.abs(x) / (2 * eps)) > 1 else "INAPPLICABLE"
    reach = Reach({"G0s_pilot:RP13_drop_gamma": {"status": st(R["gamma"])},
                   "G0s_pilot:RP14_drop_pole": {"status": st(R["pole"])},
                   "G0s_pilot:RP15_asymptotic_psi": {"status": st(dg)},
                   "G0s_pilot:RP16_drop_mirror(upper bound)": {"status": st(np.full(len(taus), np.sum(L.w(cfg, -z))))}})
    out = dict(pilot_zeta=zeta_like_gate("G0s_pilot", cfg, z, dict(taus=taus, rhs=R["total"], eps=eps), reach))
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
    print(json.dumps(out, indent=1, default=str)[:4000])


if __name__ == "__main__":
    if sys.argv[1] == "run":
        main_run(*sys.argv[2:7])
    elif sys.argv[1] == "dry":
        main_dry(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(sys.argv[1])

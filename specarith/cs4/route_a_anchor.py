"""Route (a) R₂-anchored attribution bound and cut-model validity (forty-fifth round, Will, 2026-10-14). Data-free.

(1) μ₂ family. κ₂ → κ₂^sine + μ₂(κ₂^ζ − κ₂^sine) wherever κ₂ appears (inside ρ₂…ρ₅), with κ₃…κ₅ held at ζ's (CS) values;
μ₂ = 1 is the prediction. Only partitions with a pair block change, so
    ρ_n(μ₂) − ρ_n^ζ = Σ_{π ∋ a 2-block} [Π_B κ_B(μ₂) − Π_B κ_B^ζ],
which needs ζ's κ₂ (n ≤ 4) and κ₃ (n = 5) only. The changes are integrated with the prediction's quadratures (T₂–T₄:
route_a_zeta.term_points, primes ≤ 3·10⁵; T₅: ratios_t5.t5_points, primes ≤ 1000, at EVERY node) and added to the tagged
Δp; μ*(μ₂) is the read's estimator limit (route_a_equiv.expected_mu). ∂μ*/∂μ₂ by the symmetric difference at ±0.01,
linearity checked with the one-sided slopes and the ±0.02 difference. B₂ = |∂μ*/∂μ₂|·(|1.003 − 1| + 2 × 0.006), with
R₂'s own μ̂ = 1.003 ± 0.006 (round 43) at R₂'s heights, under the assumption that μ is a height-independent amplitude.

(2) Validity of the cut models (route_a_cumul, C2–C4): the minimum over each quadrature grid of ρ_n^{Ck} for every cut
model with k < n, n = 3, 4, 5 (primes ≤ 1000 for n = 4, 5; ≤ 3·10⁵ for n = 3), and of p^{Ck}(s) on the window grid
(1801 points, from route_a_cumul.json). Declared before the cut results were seen: the decomposition is VALID only if
every cut model is positive everywhere (ρ_n ≥ −1e-12, the absolute noise floor of the quadrature values; p > 0) AND the
pooled increments decay, |C3 − C2| > |C4 − C3| > |C5 − C4|; otherwise it is reported as "not a valid decomposition at
N_eff ≈ 3.4" and not used for weights (round 45). The sign pattern of the increments is reported either way.

  python route_a_anchor.py selftest
  python route_a_anchor.py run CHUNK NCHUNKS OUT_DIR
  python route_a_anchor.py merge OUT_DIR       → results/route_a_anchor.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cs4fast as F  # noqa: E402
import route_a_cumul as RC  # noqa: E402
import route_a_zeta as RZ  # noqa: E402

MU2 = (0.98, 0.99, 1.01, 1.02)
R2_MU, R2_SE = 1.003, 0.006


def mu2_change(ds, zeta_rho):
    """{μ₂: ρ_n(μ₂) − ρ_n^ζ} at the points ds (n arrays)."""
    n = len(ds)
    kz = max(2, n - 2)
    rs = {S: RZ.sine_rho([ds[i] for i in sorted(S)]) for S in RC.subsets(n, 2)}
    rz = {S: np.real(zeta_rho([ds[i] for i in sorted(S)])) for S in RC.subsets(n, kz)}
    ks, kzc = RC.cumulants(rs), RC.cumulants(rz)
    parts = [p for p in RC.partitions(range(n)) if any(len(B) == 2 for B in p)]
    out = {}
    for m in MU2:
        tot = 0.0
        for p in parts:
            a, b = 1.0, 1.0
            for B in p:
                if len(B) == 1:
                    continue
                S = frozenset(B)
                kzS = kzc[S]
                a = a * (ks[S] + m * (kzS - ks[S]) if len(B) == 2 else kzS)
                b = b * kzS
            tot = tot + (a - b)
        out[m] = tot
    return out


def cut_minima(ds, zeta_rho):
    """min over the points of ρ_n^{Ck} for the cut models k < n (C2..C4)."""
    n = len(ds)
    rhos, _ = RC.model_rhos(ds, zeta_rho, min(4, n - 1))
    return {str(k): float(np.min(rhos[k])) for k in RC.MODELS if k < n and k in rhos}


def selftest():
    """Known answer: the pair-block-only difference equals the full reassembly over ALL partitions with κ₂ scaled and
    κ₃…κ_n from the 'ζ' process, on CUE_N (N = 4, 10) as 'ζ', n = 3, 4, 5; and it vanishes identically at μ₂ = 1."""
    rng = np.random.default_rng(45)
    worst = 0.0
    for N in (4, 10):
        for n in (3, 4, 5):
            ds = [np.sort(rng.uniform(0, 1.8, (6, n)), axis=1)[:, i] for i in range(n)]
            zr = lambda xs: RZ.sine_rho(xs, N)
            got = mu2_change(ds, zr)
            rs = {S: RZ.sine_rho([ds[i] for i in sorted(S)]) for S in RC.subsets(n, n)}
            rz = {S: zr([ds[i] for i in sorted(S)]) for S in RC.subsets(n, n)}
            ks, kzc = RC.cumulants(rs), RC.cumulants(rz)
            base = RC.assemble(kzc, n)
            for m in MU2:
                mixed = {S: (ks[S] + m * (kzc[S] - ks[S]) if len(S) == 2 else kzc[S]) for S in kzc}
                worst = max(worst, float(np.max(np.abs((RC.assemble(mixed, n) - base) - got[m]))))
            one = {S: kzc[S] for S in kzc}
            worst = max(worst, float(np.max(np.abs(RC.assemble(one, n) - base))))
    ok = worst < 1e-12
    print(f"μ₂ algebra vs full reassembly (CUE_4, CUE_10; n = 3, 4, 5; μ₂ ∈ {MU2}): {worst:.1e} → {'PASS' if ok else 'FAIL'}")
    return ok


def jobs():
    return [(f, part, float(s)) for f in RZ.F3 for s in RZ.NODES[1:] for part in ("n3", "n4", "n5")]


def run_one(job):
    f, part, s = job
    t = RZ.height(f, "mean")
    out = dict(file=f, part=part, s=s)
    if part in ("n3", "n4"):
        ds, w, c = RZ.term_points(s, RZ.M_QUAD)["T3" if part == "n3" else "T4"]
        Zm = F.FastZeta(t, pmax=RZ.PMAX_MAIN)
        ch = mu2_change(ds, lambda xs: RZ.rho(Zm, xs))
        out["dT"] = {str(m): float(c * np.sum(w * v)) for m, v in ch.items()}
        Zv = Zm if part == "n3" else F.FastZeta(t, pmax=RC.PMAX_N5)
        out["min_rho_cut"] = cut_minima(ds, lambda xs: RZ.rho(Zv, xs))
    else:
        Z = F.FastZeta(t, pmax=RC.PMAX_N5)
        pts = __import__("ratios_t5").t5_points(s)
        ds = [np.array([p[0][i] for p in pts]) for i in range(5)]
        w = np.array([p[1] for p in pts])
        ch = mu2_change(ds, lambda xs: RZ.rho(Z, xs))
        out["dT"] = {str(m): float(-np.sum(w * v) / 6) for m, v in ch.items()}
        out["min_rho_cut"] = cut_minima(ds, lambda xs: RZ.rho(Z, xs))
    out["min_rho_sine"] = float(np.min(RZ.sine_rho(ds)))
    print(json.dumps(out), flush=True)
    return out


def run(chunk, nchunks, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"anchor_c{chunk:02d}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["file"], r["part"], r["s"]) for r in map(json.loads, open(path))}
    J = sorted(jobs(), key=lambda j: {"n5": 0, "n4": 1, "n3": 2}[j[1]])
    for i, j in enumerate(J):
        if i % nchunks != chunk or j in done:
            continue
        r = run_one(j)
        with open(path, "a") as fh:
            fh.write(json.dumps(r) + "\n")


def merge(out_dir):
    import route_a_equiv as EQ
    import route_a_read as RR
    import route_a_split as SP
    rows = {}
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("anchor_c") and fn.endswith(".jsonl"):
            for r in map(json.loads, open(os.path.join(out_dir, fn))):
                rows.setdefault((r["file"], r["part"], r["s"]), r)
    missing = set(jobs()) - set(rows)
    if missing:
        raise SystemExit(f"merge: {len(missing)} jobs missing")
    pred = json.load(open(RR.PRED))
    w, _ = RR.weights()
    res = dict(round="forty-fifth", definition=__doc__.split("\n\n")[0], files={})
    for f in RR.F3:
        full = np.array(pred["files"][f]["dp_nodes"])
        D = SP.term_deltas(f)
        fit = RR.MuFit(full)
        mus = {}
        for m in (1.0,) + MU2:
            dp = full.copy()
            if m != 1.0:
                dp += (m - 1) * D["T2"]                                   # n = 2: ρ₂ − ρ₂^ζ = (μ₂ − 1)(ρ₂^ζ − ρ₂^sine)
                for i, s in enumerate(RZ.NODES[1:], start=1):
                    s = float(s)
                    dp[i] += (-rows[(f, "n3", s)]["dT"][str(m)] + rows[(f, "n4", s)]["dT"][str(m)]
                              + rows[(f, "n5", s)]["dT"][str(m)])
            p = (lambda dn: (lambda s: RR.p_sine()(np.maximum(np.asarray(s, float), RR.S_TINY))
                             + RR.cheb_interp(dn, np.maximum(np.asarray(s, float), RR.S_TINY))))(dp)
            mus[m] = EQ.expected_mu(fit, p)
        d01 = (mus[1.01] - mus[0.99]) / 0.02
        d02 = (mus[1.02] - mus[0.98]) / 0.04
        up, dn = (mus[1.01] - mus[1.0]) / 0.01, (mus[1.0] - mus[0.99]) / 0.01
        mins = {}
        for part in ("n3", "n4", "n5"):
            for s in RZ.NODES[1:]:
                for k, v in rows[(f, part, float(s))]["min_rho_cut"].items():
                    key = f"rho{part[1]}_C{k}"
                    mins[key] = min(mins.get(key, np.inf), v)
        res["files"][f] = dict(mu_star={str(m): v for m, v in mus.items()}, dmu_dmu2=d01, dmu_dmu2_pm002=d02,
                               slope_up=up, slope_down=dn, min_rho_cut=mins)
        print(f"{f}: ∂μ*/∂μ₂ {d01:+.5f} (±0.02: {d02:+.5f}; one-sided {up:+.5f} / {dn:+.5f})  min ρ cut: "
              + "  ".join(f"{k} {v:+.2e}" for k, v in sorted(mins.items())), flush=True)
    d = float(sum(w[f] * res["files"][f]["dmu_dmu2"] for f in RR.F3))
    d2 = float(sum(w[f] * res["files"][f]["dmu_dmu2_pm002"] for f in RR.F3))
    lin = max(abs(res["files"][f]["slope_up"] - res["files"][f]["slope_down"]) / abs(res["files"][f]["dmu_dmu2"])
              for f in RR.F3)
    B2 = abs(d) * (abs(R2_MU - 1) + 2 * R2_SE)
    res.update(weights=w, dmu_dmu2_pool=d, dmu_dmu2_pool_pm002=d2, linearity_max_rel=lin, R2=dict(mu=R2_MU, se=R2_SE),
               B2=B2, assumption="mu is a height-independent amplitude (R2 measured at its own heights)")
    cut = os.path.join(HERE, "results", "route_a_cumul.json")
    if os.path.exists(cut):
        cu = json.load(open(cut))
        grid = np.linspace(0, RR.S_MAX, 1801)
        ps = RR.p_sine()(np.maximum(grid, RR.S_TINY))
        min_p = {k: min(float(np.min(ps + RR.cheb_interp(np.array(cu["files"][f]["dp_nodes"][k]), np.maximum(grid, RR.S_TINY))))
                        for f in RR.F3) for k in ("2", "3", "4", "5")}
        min_rho = {}
        for f in RR.F3:
            for key, v in res["files"][f]["min_rho_cut"].items():
                min_rho[key] = min(min_rho.get(key, np.inf), v)
        inc = list(cu["increments"].values())
        decays = abs(inc[1]) > abs(inc[2]) > abs(inc[3])
        positive = all(v >= -1e-12 for v in min_rho.values()) and all(min_p[k] > 0 for k in ("2", "3", "4"))
        signs = "".join("+" if x > 0 else "-" for x in inc)
        res["cut_validity"] = dict(min_rho=min_rho, min_p=min_p, increments=cu["increments"], sign_pattern=signs,
                                   decays=bool(decays), positive=bool(positive), valid=bool(decays and positive),
                                   reading=("valid decomposition" if decays and positive else
                                            "not a valid decomposition at N_eff ≈ 3.4; not used for weights"))
        print(f"cut validity: positive {positive} (min ρ: " + ", ".join(f"{k} {v:+.2e}" for k, v in sorted(min_rho.items()))
              + "; min p: " + ", ".join(f"C{k} {v:+.3e}" for k, v in min_p.items()) + f"); increments {signs}, decay "
              f"{decays} → {res['cut_validity']['reading']}")
    print(f"pooled ∂μ*/∂μ₂ = {d:+.5f} (±0.02: {d2:+.5f}); linearity: max |up − down|/slope = {lin:.2e};  "
          f"B₂ = {abs(d):.5f} × ({abs(R2_MU - 1):.3f} + 2 × {R2_SE}) = {B2:.5f}")
    json.dump(res, open(os.path.join(HERE, "results", "route_a_anchor.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "selftest":
        sys.exit(0 if selftest() else 1)
    elif cmd == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == "merge":
        sys.exit(merge(sys.argv[2]))

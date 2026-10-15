"""Route (a) connected-term sensitivities (forty-eighth round, Will, 2026-10-15). POST HOC, data-free, labelled as derived.

μ_k family, k = 3, 4: κ_k → κ_k^sine + μ_k(κ_k^ζ − κ_k^sine) wherever κ_k appears (inside ρ_k…ρ₅), every other κ_j at ζ's
(CS) values; μ_k = 1 is the prediction. For n ≤ 5 a partition holds at most one block of size ≥ 3, so ρ_n(μ_k) is exactly
linear in μ_k, and every partition with a k-block has its other blocks of size < k, at ζ's values in both of the cuts
C_k and C_{k−1} of route_a_cumul. Hence, exactly,
    ρ_n(μ_k) − ρ_n^ζ = (μ_k − 1)(ρ_n^{C_k} − ρ_n^{C_{k−1}}),
and the node changes come from the committed cumulant-cut rows (results/cumul/, the prediction's quadratures; T₃/T₄ at
primes ≤ 3·10⁵, T₅ at primes ≤ 1000), added at EVERY node as B₂'s μ₂ family was (route_a_anchor: no skip). The value
with the prediction's skip rule (no T₃/T₄ change where |T_n^sine| < RZ.SKIP, route_a_cumul.merge) is reported as a
sensitivity: the skip rule assumes |ρ_n/ρ_n^sine| ≤ 100 there, which holds for ζ but not for a κ_k-scaled model.
μ*(μ_k) is the read's estimator limit (route_a_equiv.expected_mu) at μ_k ∈ {0.98, 0.99, 1.01, 1.02}; ∂μ*/∂μ_k by the
symmetric ±0.01 difference, linearity by the one-sided slopes and ±0.02 (the B₂ method). Positivity at μ_k = 1 ± 0.02: ρ_n at
every quadrature point (this file's run: n = 3 at primes ≤ 3·10⁵, n = 4, 5 at ≤ 1000, as the round-45 validity check;
ρ₅^ζ from ratios_t5.Model, as the n = 5 presence check) and
p(s) on the 1801-point window grid; the μ₂ family of B₂ is checked at the same points (descriptive). The n = 5 jobs also
record ζ's full T₅ change at every node (primes ≤ 1000), which the follow-up's NNN candidate needs (FOLLOWUP_SELECTION_RULE). Implied constraint: |μ_k − 1| ≤ (|μ̃ − 1| + 2·SE_pool)/|∂μ*/∂μ_k| with the read's
μ̃_pool and SE_pool (results/read/, 798065dc).

  python route_a_connected.py selftest
  python route_a_connected.py run CHUNK NCHUNKS OUT_DIR     (positivity at the quadrature points; spot)
  python route_a_connected.py merge OUT_DIR                → results/route_a_connected.json
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

KS = (3, 4)
MUK = (0.98, 0.99, 1.01, 1.02)


def scaled_change(kz, ks, k, m, n):
    """Full reassembly with κ_k scaled by m (others at 'ζ') minus the 'ζ' reassembly."""
    mixed = {S: (ks[S] + m * (kz[S] - ks[S]) if len(S) == k else kz[S]) for S in kz}
    return RC.assemble(mixed, n) - RC.assemble(kz, n)


def selftest():
    """Known answer for the identity above on CUE_N (N = 4, 10) as 'ζ', n = 3, 4, 5, k = 3, 4, m ∈ MUK: the full
    reassembly with κ_k scaled equals (m − 1)(ρ^{C_k} − ρ^{C_{k−1}}) from route_a_cumul.model_rhos."""
    rng = np.random.default_rng(48)
    worst = 0.0
    for N in (4, 10):
        for n in (3, 4, 5):
            ds = [np.sort(rng.uniform(0, 1.8, (6, n)), axis=1)[:, i] for i in range(n)]
            zr = lambda xs: RZ.sine_rho(xs, N)
            rs = {S: RZ.sine_rho([ds[i] for i in sorted(S)]) for S in RC.subsets(n, n)}
            rz = {S: zr([ds[i] for i in sorted(S)]) for S in RC.subsets(n, n)}
            ks, kz = RC.cumulants(rs), RC.cumulants(rz)
            rhos, _ = RC.model_rhos(ds, zr, n - 1)
            rhos[n] = rz[frozenset(range(n))]
            for k in KS:
                if k > n:
                    continue
                diff = rhos[k] - rhos[k - 1]
                for m in MUK:
                    worst = max(worst, float(np.max(np.abs(scaled_change(kz, ks, k, m, n) - (m - 1) * diff))))
    ok = worst < 1e-12
    print(f"κ_k scaling = (μ_k − 1)(C_k − C_(k−1)) (CUE_4, CUE_10; n = 3, 4, 5; k = 3, 4): {worst:.1e} → "
          f"{'PASS' if ok else 'FAIL'}")
    return ok


def jobs():
    return [(f, part, float(s)) for f in RZ.F3 for s in RZ.NODES[1:] for part in ("n3", "n4", "n5")]


def run_one(job):
    """min over the quadrature points of ρ_n(μ_k) at μ_k = 1 ± 0.02 (k = 3, 4 with k ≤ n), and of ρ_n^ζ itself."""
    f, part, s = job
    t = RZ.height(f, "mean")
    n = int(part[1])
    Z = F.FastZeta(t, pmax=RZ.PMAX_MAIN if part == "n3" else RC.PMAX_N5)
    if part in ("n3", "n4"):
        ds, _, _ = RZ.term_points(s, RZ.M_QUAD)["T3" if part == "n3" else "T4"]
    else:
        pts = __import__("ratios_t5").t5_points(s)
        ds = [np.array([p[0][i] for p in pts]) for i in range(5)]
        w5 = np.array([p[1] for p in pts])
    rhos, rz = RC.model_rhos(ds, lambda xs: RZ.rho(Z, xs), n - 1)
    if n == 5:                                   # FastZeta's R_n stops at n = 4; ρ₅^ζ from ratios_t5.Model (as presence)
        import math
        import ratios_t5 as T
        rz_full = np.real(T.Model("zeta", math.log(t / (2 * math.pi)), pmax=RC.PMAX_N5).rho(ds))
    else:
        rz_full = np.real(RZ.rho(Z, ds))
    rhos[n] = rz_full
    out = dict(file=f, part=part, s=s, points=int(len(ds[0])), min_rho_zeta=float(np.min(rz_full)), min_rho={})
    if n == 5:   # ζ's full T₅ change at this node (route_a_cumul's T₅ convention), for the follow-up's NNN candidate
        out["T5_sine"] = float(-np.sum(w5 * rhos["sine"]) / 6)
        out["dT5_zeta"] = float(-np.sum(w5 * (rz_full - rhos["sine"])) / 6)
    for k in KS:
        if k > n:
            continue
        diff = rhos[k] - rhos[k - 1]
        for m in (0.98, 1.02):
            out["min_rho"][f"k{k}_{m}"] = float(np.min(rz_full + (m - 1) * diff))
    import route_a_anchor as RA                                   # descriptive: B₂'s μ₂ family at the same points
    ch = RA.mu2_change(ds, lambda xs: RZ.rho(Z, xs))
    for m in (0.98, 1.02):
        out["min_rho"][f"k2_{m}"] = float(np.min(rz_full + ch[m]))
    print(json.dumps(out), flush=True)
    return out


def run(chunk, nchunks, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"conn_c{chunk:02d}.jsonl")
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


def cut_rows():
    rows = {}
    d = os.path.join(HERE, "results", "cumul")
    for fn in sorted(os.listdir(d)):
        if fn.startswith("cumul_c") and fn.endswith(".jsonl"):
            for r in map(json.loads, open(os.path.join(d, fn))):
                rows.setdefault((r["file"], r["part"], r["s"]), r)
    return rows


def node_derivative(rows, f, k, skip=True):
    """∂Δp/∂μ_k at the nodes (s = 0 first, 0): −∂T₃ + ∂T₄ + ∂T₅ (Δp = Δ₂ − Δ₃ + Δ₄ + Δ₅), from C_k − C_{k−1}."""
    out = [0.0]
    for s in RZ.NODES[1:]:
        s = float(s)
        r3, r4, r5 = rows[(f, "n3", s)], rows[(f, "n4", s)], rows[(f, "n5", s)]
        g = lambda r: r["dT"][str(k)] - r["dT"][str(k - 1)]                      # noqa: E731
        d3 = 0.0 if (skip and abs(r3["T_sine"]) < RZ.SKIP) else g(r3)
        d4 = 0.0 if (skip and abs(r4["T_sine"]) < RZ.SKIP) else g(r4)
        out.append(-d3 + d4 + g(r5))
    return np.array(out)


def merge(out_dir):
    import route_a_equiv as EQ
    import route_a_read as RR
    pos = {}
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("conn_c") and fn.endswith(".jsonl"):
            for r in map(json.loads, open(os.path.join(out_dir, fn))):
                pos.setdefault((r["file"], r["part"], r["s"]), r)
    missing = set(jobs()) - set(pos)
    if missing:
        raise SystemExit(f"merge: {len(missing)} positivity jobs missing")
    rows = cut_rows()
    pred = json.load(open(RR.PRED))
    w, _ = RR.weights()
    rd = json.load(open(os.path.join(HERE, "results", "read", "run1", "ROUTE_A_READ.json")))["result"]
    margin = abs(rd["mu_pool"] - 1) + 2 * rd["se_pool"]
    grid = np.linspace(0, RR.S_MAX, 1801)
    gg = np.maximum(grid, RR.S_TINY)
    ps = RR.p_sine()(gg)
    res = dict(round="forty-eighth", label="POST HOC, data-free, derived", definition=__doc__.split("\n\n")[0],
               read=dict(mu_pool=rd["mu_pool"], se_pool=rd["se_pool"], margin=margin), weights=w, k={})
    for k in KS:
        per = {}
        for f in RR.F3:
            full = np.array(pred["files"][f]["dp_nodes"])
            fit = RR.MuFit(full)
            out = {}
            for skip in (False, True):
                D = node_derivative(rows, f, k, skip)
                mus = {1.0: EQ.expected_mu(fit, (lambda dn: (lambda s: RR.p_sine()(np.maximum(np.asarray(s, float), RR.S_TINY))
                                                                 + RR.cheb_interp(dn, np.maximum(np.asarray(s, float), RR.S_TINY))))(full))}
                minp = {}
                for m in MUK:
                    dp = full + (m - 1) * D
                    p = (lambda dn: (lambda s: RR.p_sine()(np.maximum(np.asarray(s, float), RR.S_TINY))
                                     + RR.cheb_interp(dn, np.maximum(np.asarray(s, float), RR.S_TINY))))(dp)
                    mus[m] = EQ.expected_mu(fit, p)
                    minp[str(m)] = float(np.min(ps + RR.cheb_interp(dp, gg)))
                out["skip" if skip else "every_node"] = dict(
                    mu_star={str(m): v for m, v in mus.items()}, d01=(mus[1.01] - mus[0.99]) / 0.02,
                    d02=(mus[1.02] - mus[0.98]) / 0.04, up=(mus[1.01] - mus[1.0]) / 0.01,
                    down=(mus[1.0] - mus[0.99]) / 0.01, min_p=minp, max_abs_node_derivative=float(np.max(np.abs(D))))
            mr = {}
            for part in ("n3", "n4", "n5"):
                if int(part[1]) < k:
                    continue
                for s in RZ.NODES[1:]:
                    r = pos[(f, part, float(s))]
                    for m in ("0.98", "1.02"):
                        key = f"rho{part[1]}_{m}"
                        mr[key] = min(mr.get(key, np.inf), r["min_rho"][f"k{k}_{m}"])
                    mr[f"rho{part[1]}_zeta"] = min(mr.get(f"rho{part[1]}_zeta", np.inf), r["min_rho_zeta"])
            out["min_rho"] = mr
            per[f] = out
            o = out["every_node"]
            print(f"k = {k} {f}: ∂μ*/∂μ_{k} {o['d01']:+.5f} (±0.02 {o['d02']:+.5f}; one-sided {o['up']:+.5f} / "
                  f"{o['down']:+.5f}; skip rule {out['skip']['d01']:+.5f})  min p {min(o['min_p'].values()):+.2e}  "
                  f"min ρ: " + ", ".join(f"{a} {b:+.2e}" for a, b in sorted(mr.items())), flush=True)
        d = float(sum(w[f] * per[f]["every_node"]["d01"] for f in RR.F3))
        d2 = float(sum(w[f] * per[f]["every_node"]["d02"] for f in RR.F3))
        dn = float(sum(w[f] * per[f]["skip"]["d01"] for f in RR.F3))
        lin = max(abs(per[f]["every_node"]["up"] - per[f]["every_node"]["down"]) / abs(per[f]["every_node"]["d01"])
                  for f in RR.F3)
        rho_min = {}
        for f in RR.F3:
            for key, v in per[f]["min_rho"].items():
                rho_min[key] = min(rho_min.get(key, np.inf), v)
        p_min = min(min(per[f]["every_node"]["min_p"].values()) for f in RR.F3)
        positive = all(v >= -1e-12 for key, v in rho_min.items() if not key.endswith("zeta")) and p_min > 0
        res["k"][str(k)] = dict(files=per, dmu_dmuk_pool=d, dmu_dmuk_pool_pm002=d2, dmu_dmuk_pool_skip_rule=dn,
                                constraint_skip_rule=margin / abs(dn),
                                linearity_max_rel=lin, min_rho_pm002=rho_min, min_p_pm002=p_min,
                                positive_at_pm002=bool(positive), constraint_abs_muk_minus_1_le=margin / abs(d))
        print(f"k = {k}: pooled ∂μ*/∂μ_{k} = {d:+.5f} (±0.02 {d2:+.5f}; skip rule {dn:+.5f}); linearity {lin:.2e}; "
              f"positive at ±0.02: {positive} (min p {p_min:+.2e}); constraint |μ_{k} − 1| ≤ {margin:.5f}/{abs(d):.5f} = "
              f"{margin / abs(d):.4f}", flush=True)
    mu2 = {}
    for r in pos.values():
        for m in ("0.98", "1.02"):
            key = f"rho{r['part'][1]}_{m}"
            mu2[key] = min(mu2.get(key, np.inf), r["min_rho"][f"k2_{m}"])
    res["mu2_family_min_rho_pm002"] = dict(min_rho=mu2, positive=bool(all(v >= -1e-12 for v in mu2.values())),
                                           note="descriptive (round 48 asked for k = 3, 4); B2's family at the same points")
    print("μ₂ family (B₂), min ρ at ±0.02: " + ", ".join(f"{a} {b:+.2e}" for a, b in sorted(mu2.items())), flush=True)
    json.dump(res, open(os.path.join(HERE, "results", "route_a_connected.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "selftest":
        sys.exit(0 if selftest() else 1)
    elif cmd == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == "merge":
        sys.exit(merge(sys.argv[2]))

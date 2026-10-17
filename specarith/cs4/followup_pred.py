"""Predictions for the two route (a) replications (rounds 50–51, FOLLOWUP_REPLICATION_RULES.md). Data-free: no F4 or F5
file is downloaded, and heights come from the declared ranges only (../ph2r2/FRESH_SETS_F4_F5.md).

(A) at F4: the next-nearest-neighbour law on s ≤ S_A = 1.6 (b3fa4824).
  Δp⁽²⁾ = ΔT₃ − 2ΔT₄ + 3ΔT₅ with ΔT₅ = −T₅^sine (the primary end of the T₅ bracket, rules §3), at each file's
  zero-weighted mean height, on Chebyshev–Lobatto nodes of [0, S_A] (M_A = 24, as route (a)). ζ's T₃/T₄ come from
  FastZeta at primes ≤ 3·10⁵ (route (a)'s quadrature, order M_QUAD); route (a)'s skip rule (|T_n^sine| < SKIP → ΔT_n = 0)
  is applied at job time and at merge. Checks, mirroring route (a)'s prediction:
  - positivity of the μ = 1 density on the fitted bins (≥ S_RES);
  - prime cutoff 3·10⁵ → 10⁶, quadrature M_QUAD → M_QUAD + 4, the T₅ bracket's other end (ΔT₅ = 0), and the n = 6 bound
    (4·T6_CAP·|T₆^sine|), each as δμ through followup_fit's estimator limit (n = 6 by route (a)'s check-(c) construction);
  - the file average: Simpson over (t0, mean, t1) at the lowest file, scaled to the others by Var ℓ (as route (a));
  - interpolation: the half-grid interpolant against the odd nodes;
  - ∂μ*/∂μ re-measured at the F4 heights (expected counts at μ′ = 0.99, 1.01).
(B) at F5: the third cumulant of the count at L = 3 (b3fa4824).
  κ₃^sine(3) and Δκ₃(3) = 3ΔF₂ + ΔF₃ at each file's zero-weighted mean height (followup_k3.terms, triangle order 48),
  with the same cutoff, quadrature (32 → 48) and file-average checks as relative changes of Δκ₃ (μ units).
δμ_sys of each prediction is the w_f-pooled sum of its δμ contributions (conservative; route (a) used the file-average
term alone).

  python followup_pred.py run CHUNK NCHUNKS OUT_DIR       (spot)
  python followup_pred.py merge OUT_DIR                   → results/followup_pred_A.json, results/followup_pred_B.json
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route_a_zeta as RZ  # noqa: E402

F4 = {"zeros_252446000.dat": (252_446_000, 254_546_000),
      "zeros_2369246000.dat": (2_369_246_000, 2_371_346_000),
      "zeros_10634846000.dat": (10_634_846_000, 10_636_946_000)}
F5 = {"zeros_36146000.dat": (36_146_000, 38_246_000),
      "zeros_244046000.dat": (244_046_000, 246_146_000),
      "zeros_2377646000.dat": (2_377_646_000, 2_379_746_000),
      "zeros_10643246000.dat": (10_643_246_000, 10_645_346_000)}
S_A, L_B = 1.6, 3.0
M_A = 24
NODES_A = 0.5 * S_A * (1 - np.cos(np.pi * np.arange(M_A + 1) / M_A))
M_B = (32, 48)
PM, PM_HI, MQ = RZ.PMAX_MAIN, RZ.PMAX_CHECK, RZ.M_QUAD


def height(S, f, which="mean"):
    t0, t1 = S[f]
    return {"mean": RZ.zero_weighted_t(t0, t1), "t0": float(t0), "t1": float(t1)}[which]


def lowest(S):
    return min(S, key=lambda k: S[k][0])


def sine_T(part, s, m=MQ):
    ds, w, c = RZ.term_points(s, m)[part]
    return float(c * np.sum(w * RZ.sine_rho(ds)))


def jobs():
    J = []
    for f in F4:
        for s in map(float, NODES_A[1:]):
            for part in ("T3", "T4"):
                if abs(sine_T(part, s)) < RZ.SKIP:
                    continue
                J += [("A", f, "mean", PM, MQ, part, s), ("A", f, "mean", PM_HI, MQ, part, s),
                      ("A", f, "mean", PM, MQ + 4, part, s)]
                if f == lowest(F4):
                    J += [("A", f, "t0", PM, MQ, part, s), ("A", f, "t1", PM, MQ, part, s)]
    for f in F5:
        for pm in (PM, PM_HI):
            for m in M_B:
                J.append(("B", f, "mean", pm, m, "k3", L_B))
        if f == lowest(F5):
            J += [("B", f, "t0", PM, M_B[1], "k3", L_B), ("B", f, "t1", PM, M_B[1], "k3", L_B)]
    return J


def run_one(job):
    import cs4fast as Fz
    obs, f, which, pm, m, part, s = job
    t = height(F4 if obs == "A" else F5, f, which)
    Z = Fz.FastZeta(t, pmax=pm)
    out = dict(obs=obs, file=f, which=which, pmax=pm, m=m, part=part, s=s, t=t)
    if obs == "A":
        ds, w, c = RZ.term_points(s, m)[part]
        rs = RZ.sine_rho(ds)
        out.update(T_sine=float(c * np.sum(w * rs)), dT=float(c * np.sum(w * (np.real(RZ.rho(Z, ds)) - rs))))
    else:
        import followup_k3 as K
        out.update(K.terms(Z, s, m))
    return out


def key(r):
    return (r["obs"], r["file"], r["which"], r["pmax"], r["m"], r["part"], r["s"])


def run(chunk, nchunks, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"pred_c{chunk:02d}.jsonl")
    done = {key(r) for r in map(json.loads, open(path))} if os.path.exists(path) else set()
    J = sorted(jobs(), key=lambda j: (j[0] == "A" and j[5] == "T4", j[3] == PM_HI), reverse=True)
    for i, j in enumerate(J):
        if i % nchunks != chunk or j in done:
            continue
        r = run_one(j)
        with open(path, "a") as fh:
            fh.write(json.dumps(r) + "\n")
        print(json.dumps(r), flush=True)


# ------------------------------------------------------------------ merge
def bary(vals, nodes, s):
    w = (-1.0) ** np.arange(len(nodes))
    w[0] *= 0.5
    w[-1] *= 0.5
    s = np.atleast_1d(np.asarray(s, float))
    D = s[:, None] - nodes[None, :]
    hit = np.isclose(D, 0, atol=1e-14)
    D[hit] = 1.0
    K = w / D
    out = (K @ np.asarray(vals)) / K.sum(1)
    r, c = np.nonzero(hit)
    out[r] = np.asarray(vals)[c]
    return out


def counts(S):
    import mpmath as mp
    n = {}
    for f, (t0, t1) in S.items():
        with mp.workdps(30):
            n[f] = float((mp.siegeltheta(t1) - mp.siegeltheta(t0)) / mp.pi)
    tot = sum(n.values())
    return {f: n[f] / tot for f in S}, n


def var_ell(t0, t1, n=4001):
    t = np.linspace(t0, t1, n)
    ell = np.log(t / (2 * math.pi))
    m = np.sum(ell * ell) / np.sum(ell)
    return float(np.sum(ell * (ell - m) ** 2) / np.sum(ell))


def merge(out_dir):
    import followup_fit as FF
    import followup_nnn as N
    import ratios_t5 as T
    import route_a_read as RR
    rows = {}
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("pred_c") and fn.endswith(".jsonl"):
            for r in map(json.loads, open(os.path.join(out_dir, fn))):
                rows.setdefault(key(r), r)
    missing = set(jobs()) - set(rows)
    if missing:
        raise SystemExit(f"merge: {len(missing)} jobs missing")
    p2, _ = N.p2_sine()
    c = FF.CENTRES
    sr = max(FF.s_res(p2(c)), RR.S_TINY)
    sel = (c >= sr) & (c < S_A - 1e-12)
    cb, p0 = c[sel], p2(c[sel])
    wbin = np.full(len(cb), FF.HB)
    T5s = [0.0]
    for s in NODES_A[1:]:                                   # as followup_nnn.merge
        pts = T.t5_points(float(s))
        ds = [np.array([p[0][i] for p in pts]) for i in range(5)]
        T5s.append(float(np.sum(np.array([p[1] for p in pts]) * RZ.sine_rho(ds)) / 6))
    T5s = np.array(T5s)
    T6 = np.array([0.0] + [abs(RZ.T6_det(float(s))) for s in NODES_A[1:]])
    trunc6 = 4 * RZ.T6_CAP * T6

    def dp_series(f, which, pm, m, t5="zero"):
        out = [0.0]
        for s in map(float, NODES_A[1:]):
            d = {}
            for part in ("T3", "T4"):
                r = rows.get(("A", f, which, pm, m, part, s))
                d[part] = 0.0 if r is None else r["dT"]          # absent = skipped at job time (|T^sine| < SKIP)
            out.append(d["T3"] - 2 * d["T4"])
        out = np.array(out)
        return out - 3 * T5s if t5 == "zero" else out

    def mustar(model, truth):
        """Estimator limit of the fixed fit with model Δp on expected counts from truth Δp (μ = 1)."""
        D, Dt = bary(model, NODES_A, cb), bary(truth, NODES_A, cb)
        mu, why = FF.fit_A(FF.expected(p0, Dt, 1.0), p0, D, wbin)
        if why:
            raise SystemExit(f"estimator limit failed: {why}")
        return mu

    wA, nA = counts(F4)
    resA = dict(round="fifty-first", observable="A: next-nearest-neighbour spacing law", window=S_A, S_RES=sr,
                nodes=NODES_A.tolist(), pmax=PM, pmax_check=PM_HI, m_quad=MQ, T5_sine=T5s.tolist(),
                trunc6_bound=trunc6.tolist(), weights=wA, n_f=nA, files={})
    f0 = lowest(F4)
    fav0 = None
    for f in [f0] + [g for g in F4 if g != f0]:
        dp = dp_series(f, "mean", PM, MQ)
        D = bary(dp, NODES_A, cb)
        P1 = p0 + D
        lim = {m: FF.fit_A(FF.expected(p0, D, m), p0, D, wbin)[0] for m in (0.99, 1.01)}
        slope = (lim[1.01] - lim[0.99]) / 0.02
        dmu = dict(cutoff=abs(mustar(dp, dp_series(f, "mean", PM_HI, MQ)) - 1) / slope,
                   quad=abs(mustar(dp, dp_series(f, "mean", PM, MQ + 4)) - 1) / slope,
                   T5_bracket=abs(mustar(dp, dp_series(f, "mean", PM, MQ, t5="sine")) - 1) / slope,
                   trunc6=float(np.sum(bary(trunc6, NODES_A, cb) * np.abs(D)) / np.sum(D * D)) / slope)
        if f == f0:
            e0, e1 = dp_series(f, "t0", PM, MQ), dp_series(f, "t1", PM, MQ)
            fav0 = abs(mustar(dp, (e0 + 4 * dp + e1) / 6) - 1) / slope
            v0 = var_ell(*F4[f0])
        dmu["file_average"] = fav0 * var_ell(*F4[f]) / v0
        half = float(np.max(np.abs(bary(dp[::2], NODES_A[::2], NODES_A[1::2]) - dp[1::2])))
        resA["files"][f] = dict(t_mean=height(F4, f), ell_mean=RZ.ell_of(height(F4, f)), dp_nodes=dp.tolist(),
                                dmustar_dmu=slope, dmu=dmu, interp_half_grid_max_abs=half,
                                min_p_mu1=float(P1.min()), max_abs_dp=float(np.max(np.abs(dp))),
                                positive=bool(P1.min() > 0))
        print(f"(A) {f}: ℓ̄ {resA['files'][f]['ell_mean']:.4f}  max|Δp⁽²⁾| {np.max(np.abs(dp)):.3e}  min p(μ=1) "
              f"{P1.min():.2e}  ∂μ*/∂μ {slope:.5f}  δμ " + ", ".join(f"{k} {v:.1e}" for k, v in dmu.items())
              + f"  half-grid {half:.1e}", flush=True)
    resA["delta_mu_sys"] = float(sum(wA[f] * sum(resA["files"][f]["dmu"].values()) for f in F4))
    resA["TAGGABLE"] = bool(all(v["positive"] for v in resA["files"].values())
                            and all(abs(v["dmustar_dmu"] - 1) < 1e-3 for v in resA["files"].values()))
    print(f"(A) δμ_sys {resA['delta_mu_sys']:.2e}; TAGGABLE {resA['TAGGABLE']}", flush=True)

    wB, nB = counts(F5)
    resB = dict(round="fifty-first", observable="B: third cumulant of the count", L=L_B, pmax=PM, pmax_check=PM_HI,
                m_tri=M_B, weights=wB, n_f=nB, files={})
    f0 = lowest(F5)
    g = lambda f, which, pm, m: rows[("B", f, which, pm, m, "k3", L_B)]                         # noqa: E731
    dk = lambda r: 3 * r["dF2"] + r["dF3"]                                                      # noqa: E731
    r0 = g(f0, "mean", PM, M_B[1])
    favB = abs((dk(g(f0, "t0", PM, M_B[1])) + 4 * dk(r0) + dk(g(f0, "t1", PM, M_B[1]))) / 6 - dk(r0)) / abs(dk(r0))
    v0 = var_ell(*F5[f0])
    for f in F5:
        r = g(f, "mean", PM, M_B[1])
        d = dk(r)
        dmu = dict(cutoff=abs(dk(g(f, "mean", PM_HI, M_B[1])) - d) / abs(d),
                   quad=abs(dk(g(f, "mean", PM, M_B[0])) - d) / abs(d),
                   file_average=favB * var_ell(*F5[f]) / v0)
        resB["files"][f] = dict(t_mean=height(F5, f), ell_mean=RZ.ell_of(height(F5, f)), dF2=r["dF2"], dF3=r["dF3"],
                                dkappa3=d, kappa3_sine=L_B + 3 * r["F2_sine"] + r["F3_sine"], dmu=dmu)
        print(f"(B) {f}: ℓ̄ {resB['files'][f]['ell_mean']:.4f}  Δκ₃ {d:+.4e} (3ΔF₂ {3 * r['dF2']:+.3e}, ΔF₃ "
              f"{r['dF3']:+.3e})  κ₃^sine {resB['files'][f]['kappa3_sine']:.6f}  δμ "
              + ", ".join(f"{k} {v:.1e}" for k, v in dmu.items()), flush=True)
    resB["delta_mu_sys"] = float(sum(wB[f] * sum(resB["files"][f]["dmu"].values()) for f in F5))
    resB["TAGGABLE"] = bool(all(abs(v["dkappa3"]) > 0 for v in resB["files"].values()))
    print(f"(B) δμ_sys {resB['delta_mu_sys']:.2e}; TAGGABLE {resB['TAGGABLE']}", flush=True)
    for name, res in (("A", resA), ("B", resB)):
        json.dump(res, open(os.path.join(HERE, "results", f"followup_pred_{name}.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == "merge":
        sys.exit(merge(sys.argv[2]))
    elif cmd == "count":
        J = jobs()
        print(len(J), {k: sum(1 for j in J if (j[0], j[5], j[3]) == k) for k in {(j[0], j[5], j[3]) for j in J}})

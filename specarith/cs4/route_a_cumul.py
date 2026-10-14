"""Route (a) cumulant cut (forty-fourth round, Will, 2026-10-14): data-free; no zero data is read.

Cumulants (connected correlations) κ_j, defined by ρ_n(X) = Σ_{set partitions π of X} Π_{B∈π} κ_{|B|}(X_B), κ₁ = 1.
Models (round 44): Ck takes κ_j from ζ for j ≤ k and from the sine kernel for j > k,
    C2: κ₂ from ζ;  C3: κ₂, κ₃;  C4: κ₂–κ₄;  C5: everything from ζ (= the tagged n ≤ 5 prediction: the gate).
Each model's ρ_n^{Ck} is reassembled from its cumulants, and its spacing law is built exactly as the prediction's:
    Δp^{Ck} = ΔT₂ − ΔT₃ + ΔT₄ + ΔT₅,   ΔT_n = T_n[ρ_n^{Ck}] − T_n[ρ_n^sine],
with route_a_zeta's T₂–T₄ quadrature (term_points, m = 16; primes ≤ 3·10⁵, FastZeta) and ratios_t5's T₅ quadrature
(t5_points, m = 6; primes ≤ 1000, the cutoff of the stored Δ₅). C5 is the prediction exactly: its own n-point terms
keep the prediction's small-s skip (ΔT_n = 0 where |T_n^sine| < 1e-8) and its n = 5 term only at the edge nodes. For the
cut models the cut pieces are computed at EVERY node, without the skip: the 2026-10-14 smoke test showed a cut model's
n = 5 term at s = 1.8 is ~200 × T₅^sine (the cut breaks the cancellation among cumulant products that makes ρ₅ small), so
the prediction's grounds for dropping it (|ρ₅^ζ/ρ₅^sine| ≤ 100) do not hold for the cuts. An n = 6 probe of the cut models
at s = 1.8 (lowest file) shows whether their series in n decays.
ζ cumulants come from ζ's ρ_j on every subset by Möbius inversion; sine cumulants from the sine-kernel determinants.
For C5 the n ≤ 4 terms are RECOMPUTED here (ρ₃^ζ, ρ₄^ζ at every quadrature point); the n = 5 term of C5 is the stored Δ₅
(ratios_t5.Model; recomputing it is the multi-hour job of the thirty-sixth round), so C5 − C4 at n = 5 is the κ₅
increment Δ₅ − ΔT₅^{C4}. The lower-order ζ correlations inside the n = 5 term come from FastZeta at primes ≤ 1000;
`agree` checks FastZeta against ratios_t5.Model there pointwise, so that κ₅'s increment does not absorb a difference
between the two constructions.

  python route_a_cumul.py algebra                       known answer: cumulant algebra on CUE_N (cycle formula, reassembly)
  python route_a_cumul.py run CHUNK NCHUNKS OUT_DIR     node jobs (spot), one JSON line per job, restartable
  python route_a_cumul.py presence OUT.json             ρ₅^ζ − ρ₅^sine at a few T₅ quadrature points; FastZeta vs Model
  python route_a_cumul.py merge OUT_DIR [PRESENCE.json] → results/route_a_cumul.json
"""
import itertools
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cs4fast as F  # noqa: E402
import route_a_zeta as RZ  # noqa: E402

PMAX_N5 = 1000
MODELS = (2, 3, 4, 5)
BAND = 0.016


# ---------------------------------------------------------------- set partitions and cumulant algebra
def partitions(items):
    items = list(items)
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for p in partitions(rest):
        yield [[first]] + p
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]


def cumulants(rho):
    """rho: {frozenset S (|S| ≥ 2): array}. Returns κ on the same subsets by Möbius inversion (κ of a singleton = 1)."""
    kap = {}
    for S in sorted(rho, key=len):
        tot = rho[S].copy()
        for p in partitions(sorted(S)):
            if len(p) == 1:
                continue
            term = np.ones_like(tot)
            for B in p:
                if len(B) >= 2:
                    term = term * kap[frozenset(B)]
            tot = tot - term
        kap[S] = tot
    return kap


def assemble(kap, n):
    """ρ_n on the full set {0..n−1} from cumulants on its subsets."""
    out = None
    for p in partitions(range(n)):
        term = 1.0
        for B in p:
            if len(B) >= 2:
                term = term * kap[frozenset(B)]
        out = term if out is None else out + term
    return out


def subsets(n, kmax):
    return [frozenset(c) for j in range(2, kmax + 1) for c in itertools.combinations(range(n), j)]


def model_rhos(ds, zeta_rho, kz):
    """ρ_n^{Ck} for every k in MODELS with k < n (k ≥ n: ρ_n^ζ, handled by the caller), and ρ_n^sine.
    ds: n point arrays; zeta_rho(list of arrays) → ζ's ρ_j at those points; kz = the largest j whose ζ ρ_j is needed."""
    n = len(ds)
    rs = {S: RZ.sine_rho([ds[i] for i in sorted(S)]) for S in subsets(n, n)}
    rz = {S: np.real(zeta_rho([ds[i] for i in sorted(S)])) for S in subsets(n, kz)}
    ks, kzc = cumulants(rs), cumulants(rz)
    out = {"sine": rs[frozenset(range(n))]}
    for k in MODELS:
        if k >= n or k > kz:
            continue
        mixed = {S: (kzc[S] if len(S) <= k else ks[S]) for S in ks}
        out[k] = assemble(mixed, n)
    return out, rz


# ---------------------------------------------------------------- known answer: CUE_N (determinantal, cycle formula)
def algebra():
    """Known answers for the partition algebra: on CUE_N (determinantal) the Möbius cumulants equal the cycle formula
    (−1)^{n−1} Σ_{cyclic orders} Π K_N, and reassembly returns ρ_n; with ζ's ρ replaced by the sine kernel's own, every
    cut Ck must return the sine kernel exactly (the cut is then the identity)."""
    rng = np.random.default_rng(44)
    worst_cyc, worst_re, worst_id = 0.0, 0.0, 0.0
    for N in (4, 10):
        for n in (2, 3, 4, 5):
            D = np.sort(rng.uniform(0, 1.8, n))
            ds = [np.array([x]) for x in D]
            X = D[:, None] - D[None, :]
            off = np.abs(X) > 1e-15
            K = np.ones_like(X)
            K[off] = np.sin(np.pi * X[off]) / (N * np.sin(np.pi * X[off] / N))
            rho = {S: RZ.sine_rho([ds[i] for i in sorted(S)], N) for S in subsets(n, n)}
            kap = cumulants(rho)
            full = frozenset(range(n))
            cyc = 0.0
            for perm in itertools.permutations(range(1, n)):
                order = (0,) + perm
                prod = 1.0
                for a, b in zip(order, order[1:] + (0,)):
                    prod *= K[a, b]
                cyc += prod
            cyc *= (-1) ** (n - 1)
            worst_cyc = max(worst_cyc, abs(float(kap[full][0]) - cyc))
            worst_re = max(worst_re, abs(float(assemble(kap, n)[0]) - float(rho[full][0])))
            out, _ = model_rhos(ds, lambda xs: RZ.sine_rho(xs), n)
            for k in MODELS:
                if k in out:
                    worst_id = max(worst_id, abs(float(out[k][0]) - float(out["sine"][0])))
    ok = worst_cyc < 1e-12 and worst_re < 1e-12 and worst_id < 1e-12
    print(f"cumulants vs cycle formula (CUE_4, CUE_10; n = 2..5): {worst_cyc:.1e};  reassembly: {worst_re:.1e};  "
          f"identity cut (ζ := sine): {worst_id:.1e}  → {'PASS' if ok else 'FAIL'}")
    return ok


# ---------------------------------------------------------------- node jobs
def edge_nodes(f):
    t5 = json.load(open(os.path.join(HERE, "results", "ratios_t5.json")))
    return {float(k): v for k, v in t5["files"][f]["delta5"].items()}


def jobs():
    J = []
    for f in RZ.F3:
        for s in RZ.NODES[1:]:
            J += [(f, "n3", float(s)), (f, "n4", float(s))]
        J += [(f, "n5", float(s)) for s in RZ.NODES[1:]]
    f0 = min(RZ.F3, key=lambda k: RZ.F3[k][0])
    J += [(f0, "n6", 1.8)]
    return J


def t6_points(s, m=6):
    axes = [RZ.gl(m + 2 * k, s) for k in range(4)]
    Y = np.meshgrid(*[a[0] for a in axes], indexing="ij")
    W = np.einsum("i,j,k,l->ijkl", *[a[1] for a in axes]).ravel()
    return [np.zeros(W.size)] + [y.ravel() for y in Y] + [np.full(W.size, s)], W


def run_one(job):
    f, part, s = job
    t = RZ.height(f, "mean")
    out = dict(file=f, part=part, s=s, t=t)
    if part in ("n3", "n4"):
        Z = F.FastZeta(t, pmax=RZ.PMAX_MAIN)
        ds, w, c = RZ.term_points(s, RZ.M_QUAD)["T3" if part == "n3" else "T4"]
        n = len(ds)
        rhos, rz = model_rhos(ds, lambda xs: RZ.rho(Z, xs), n)
        full = frozenset(range(n))
        rhos[n] = rz[full]                          # C_n and above: ζ's own ρ_n
        Ts = float(c * np.sum(w * rhos["sine"]))
        out["T_sine"] = Ts
        out["dT"] = {str(k): float(c * np.sum(w * (rhos[min(k, n)] - rhos["sine"]))) for k in MODELS}
    elif part == "n6":
        Z = F.FastZeta(t, pmax=PMAX_N5)
        ds, w = t6_points(s)
        rhos, _ = model_rhos(ds, lambda xs: RZ.rho(Z, xs), 4)
        out["T_sine"] = float(np.sum(w * rhos["sine"]) / 24)
        out["dT"] = {str(k): float(np.sum(w * (rhos[k] - rhos["sine"])) / 24) for k in (2, 3, 4)}
    else:
        Z = F.FastZeta(t, pmax=PMAX_N5)
        pts = __import__("ratios_t5").t5_points(s)
        ds = [np.array([p[0][i] for p in pts]) for i in range(5)]
        w = np.array([p[1] for p in pts])
        rhos, _ = model_rhos(ds, lambda xs: RZ.rho(Z, xs), 4)
        out["T_sine"] = float(-np.sum(w * rhos["sine"]) / 6)
        out["dT"] = {str(k): float(-np.sum(w * (rhos[k] - rhos["sine"])) / 6) for k in (2, 3, 4)}
    print(json.dumps(out), flush=True)
    return out


def run(chunk, nchunks, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"cumul_c{chunk:02d}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["file"], r["part"], r["s"]) for r in map(json.loads, open(path))}
    # cost-balanced order: the n4 jobs (ρ₄ at 3·10⁵ primes) first, round-robin over chunks
    J = sorted(jobs(), key=lambda j: {"n6": 0, "n4": 1, "n5": 2, "n3": 3}[j[1]])
    for i, j in enumerate(J):
        if i % nchunks != chunk or j in done:
            continue
        r = run_one(j)
        with open(path, "a") as fh:
            fh.write(json.dumps(r) + "\n")


# ---------------------------------------------------------------- presence check (n = 5) and FastZeta vs Model
def presence(out):
    import ratios_t5 as T
    f = min(RZ.F3, key=lambda k: RZ.F3[k][0])
    t = RZ.height(f, "mean")
    ell = math.log(t / (2 * math.pi))
    M = T.Model("zeta", ell, pmax=PMAX_N5)
    Z = F.FastZeta(t, pmax=PMAX_N5)
    pts = T.t5_points(1.8)
    w = np.array([p[1] for p in pts])
    rs = np.array([RZ.sine_rho([np.array([x]) for x in p[0]])[0] for p in pts])
    pick = list(np.argsort(-np.abs(w * rs))[:4]) + [int(np.argmin(np.abs(w * rs)))]
    rows = []
    for i in pick:
        x = pts[i][0]
        r5z = float(np.real(M.rho([np.array([v]) for v in x]))[0])
        quad = [np.array([v]) for v in x[:4]]
        r4m = float(np.real(M.rho(quad))[0])
        r4f = float(np.real(RZ.rho(Z, quad))[0])
        rows.append(dict(point=list(x), weight=float(w[i]), rho5_zeta=r5z, rho5_sine=float(rs[i]),
                         diff=r5z - float(rs[i]), rho4_model=r4m, rho4_fastzeta=r4f, rho4_rel=abs(r4m - r4f) / abs(r4m)))
        print(f"x = {np.round(x, 4)}  ρ₅^ζ {r5z:.4e}  ρ₅^sine {rs[i]:.4e}  diff {r5z - rs[i]:+.4e}   ρ₄(0,y₁,y₂,y₃): Model "
              f"{r4m:.10e} FastZeta {r4f:.10e} rel {abs(r4m - r4f) / abs(r4m):.1e}", flush=True)
    res = dict(file=f, s=1.8, pmax=PMAX_N5, points=rows, agree_max_rel=max(r["rho4_rel"] for r in rows))
    json.dump(res, open(out, "w"), indent=1)
    return res


# ---------------------------------------------------------------- merge
def merge(out_dir, presence_json=None):
    import route_a_equiv as EQ
    import route_a_read as RR
    import route_a_split as SP
    rows = {}
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("cumul_c") and fn.endswith(".jsonl"):
            for r in map(json.loads, open(os.path.join(out_dir, fn))):
                rows.setdefault((r["file"], r["part"], r["s"]), r)
    need = set(jobs())
    missing = need - set(rows)
    if missing:
        raise SystemExit(f"merge: {len(missing)} jobs missing")
    pred = json.load(open(RR.PRED))
    split = json.load(open(os.path.join(HERE, "results", "route_a_split.json")))
    w, nf = RR.weights()
    res = dict(round="forty-fourth", definition=__doc__.split("\n\n")[0], files={}, band=BAND)
    worst_recon = 0.0
    for f in RR.F3:
        v = pred["files"][f]
        D = SP.term_deltas(f)                                    # stored ΔT₂, −ΔT₃, +ΔT₄ (skip rule applied)
        d5 = np.array(v["check_c"]["delta5_included"])
        e5 = edge_nodes(f)
        dp = {k: np.zeros(len(RZ.NODES)) for k in MODELS}
        chk = {"T3": [0.0], "T4": [0.0]}
        for i, s in enumerate(RZ.NODES[1:], start=1):
            s = float(s)
            r3, r4 = rows[(f, "n3", s)], rows[(f, "n4", s)]
            skip3 = abs(r3["T_sine"]) < RZ.SKIP
            skip4 = abs(r4["T_sine"]) < RZ.SKIP
            r5 = rows[(f, "n5", s)]
            for k in MODELS:
                dT3 = 0.0 if (k >= 3 and skip3) else r3["dT"][str(k)]
                dT4 = 0.0 if (k >= 4 and skip4) else r4["dT"][str(k)]
                dT5 = e5.get(s, 0.0) if k == 5 else r5["dT"][str(k)]
                dp[k][i] = D["T2"][i] - dT3 + dT4 + dT5
            chk["T3"].append(-(0.0 if skip3 else r3["dT"]["5"]))
            chk["T4"].append(0.0 if skip4 else r4["dT"]["5"])
        recon = max(float(np.max(np.abs(np.array(chk["T3"]) - D["T3"]))), float(np.max(np.abs(np.array(chk["T4"]) - D["T4"]))),
                    float(np.max(np.abs(dp[5] - np.array(v["dp_nodes"])))))
        worst_recon = max(worst_recon, recon)
        fit = RR.MuFit(v["dp_nodes"])
        mu = {}
        for k in MODELS:
            p = (lambda dn: (lambda s: RR.p_sine()(np.maximum(np.asarray(s, float), RR.S_TINY))
                             + RR.cheb_interp(dn, np.maximum(np.asarray(s, float), RR.S_TINY))))(dp[k])
            mu[k] = EQ.expected_mu(fit, p)
        n5_nodes = {str(float(s)): dict(sine_T5=rows[(f, "n5", float(s))]["T_sine"],
                                        dT5_C2=rows[(f, "n5", float(s))]["dT"]["2"], dT5_C3=rows[(f, "n5", float(s))]["dT"]["3"],
                                        dT5_C4=rows[(f, "n5", float(s))]["dT"]["4"], dT5_C5=e5.get(float(s), 0.0))
                    for s in RZ.NODES[1:]}
        res["files"][f] = dict(recompute_vs_stored_max_abs=recon, mu_star={str(k): mu[k] for k in MODELS},
                               dp_nodes={str(k): dp[k].tolist() for k in MODELS}, n5_nodes=n5_nodes,
                               block_n5_increment=split["files"][f]["mu_star"]["n_le_5_full"]
                               - split["files"][f]["mu_star"]["n_le_4"],
                               trunc_dmu_bound=v["check_c"]["dmu_trunc_worst_sign"])
        print(f"{f}: recompute {recon:.1e}  μ* " + "  ".join(f"C{k} {mu[k]:.6f}" for k in MODELS), flush=True)
    pool = {k: float(sum(w[f] * res["files"][f]["mu_star"][str(k)] for f in RR.F3)) for k in MODELS}
    eqv = json.load(open(os.path.join(HERE, "results", "route_a_equiv.json")))["files"]
    c5_vs_eq = max(abs(res["files"][f]["mu_star"]["5"] - eqv[f]["mu"]["prediction (μ = 1 check)"]) for f in RR.F3)
    inc = {"C2 (pair, from sine)": pool[2], "C3 - C2 (connected 3-point)": pool[3] - pool[2],
           "C4 - C3 (connected 4-point)": pool[4] - pool[3], "C5 - C4 (connected 5-point)": pool[5] - pool[4]}
    blk5 = float(sum(w[f] * res["files"][f]["block_n5_increment"] for f in RR.F3))
    trunc = float(sum(w[f] * res["files"][f]["trunc_dmu_bound"] for f in RR.F3))
    gate = bool(worst_recon <= 1e-10 and c5_vs_eq <= 1e-9 and abs(pool[5] - 1) <= 1e-4)
    res.update(weights=w, mu_star_pool={str(k): pool[k] for k in MODELS}, increments=inc,
               increments_over_band={k: abs(x) / BAND for k, x in inc.items()},
               block_n5_increment_pool=blk5, trunc_dmu_bound_pool=trunc,
               gate=dict(recompute_vs_stored_max_abs=worst_recon, C5_vs_committed_equiv=c5_vs_eq,
                         C5_pool=pool[5], PASS=gate))
    f0 = min(RZ.F3, key=lambda k: RZ.F3[k][0])
    r6, r5e = rows[(f0, "n6", 1.8)], rows[(f0, "n5", 1.8)]
    res["n6_probe"] = dict(file=f0, s=1.8, T6_sine=r6["T_sine"], dT6={k: r6["dT"][k] for k in ("2", "3", "4")},
                           dT5={k: r5e["dT"][k] for k in ("2", "3", "4")}, dT5_C5=edge_nodes(f0)[1.8])
    print(f"  n = 6 probe ({f0}, s = 1.8): T₆^sine {r6['T_sine']:.3e};  cut models ΔT₅ / ΔT₆: " + "  ".join(
        f"C{k} {r5e['dT'][k]:+.3e} / {r6['dT'][k]:+.3e}" for k in ("2", "3", "4")))
    if presence_json and os.path.exists(presence_json):
        res["presence"] = json.load(open(presence_json))
    print(f"gate (n ≤ 4 recomputed = stored ≤ 1e-10; C5 = committed equiv check ≤ 1e-9; |C5_pool − 1| ≤ 1e-4): "
          f"{'PASS' if gate else 'FAIL'} ({worst_recon:.1e}, {c5_vs_eq:.1e}, {pool[5]:.8f})")
    for k, x in inc.items():
        print(f"  {k:30s} {x:+.6f}   = {abs(x) / BAND:.3f} × band (0.016)")
    print(f"  n = 5 block increment (pooled, full precision): {blk5:+.17e};  κ₅ increment {pool[5] - pool[4]:+.17e}")
    print(f"  truncation bound (pooled δμ, n ≥ 6 and n = 5 below the edge): {trunc:.3e}")
    json.dump(res, open(os.path.join(HERE, "results", "route_a_cumul.json"), "w"), indent=1)
    return 0 if gate else 1


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "algebra":
        sys.exit(0 if algebra() else 1)
    elif cmd == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == "presence":
        presence(sys.argv[2])
    elif cmd == "merge":
        sys.exit(merge(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None))

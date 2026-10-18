"""(B)'s ∂μ*/∂μ, part 2 (FOLLOWUP_REPLICATION_RULES.md §2, round 50): a known-answer slope of the k-statistic on CUE_N.
Data-free.

For N ∈ NS and L ∈ LS:
- exact κ₃^{CUE_N}(L) = L + 3F₂ + F₃, with followup_k3's construction and quadrature, and ρ_n from the exact CUE_N
  kernel sin(πx)/(N sin(πx/N)) at unit density (route_a_zeta.sine_rho(·, N));
- the k-statistic k₃ = W²m₃/((W − 1)(W − 2)) of the counts in the disjoint windows [jL, (j + 1)L), j < ⌊N/L⌋, of Haar
  U(N) matrices (cbe.haar_phases; unfolded x = Nθ/2π; Haar is rotation invariant, so fixed window positions suffice),
  one k₃ per batch of B_MAT matrices.
The slope per L is the weighted least-squares fit of the batch-mean k₃ on exact κ₃ across N, with weights from the
batches' SEs. Seeds [20261016, ROUND, N, batch] (ROUND = 50, 51 for the round-51 L = 3 rerun, 53 for round 53's run to
SE(slope) ≤ 0.005 with ALLOC_53 batches per N), disjoint from every earlier use.

  python followup_cuen.py exact                       (table of exact κ₃^{CUE_N} − κ₃^sine)
  python followup_cuen.py run CHUNK NCHUNKS OUT_DIR   (spot)
  python followup_cuen.py merge OUT_DIR               → results/followup_cuen.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cbe  # noqa: E402
import route_a_zeta as RZ  # noqa: E402

NS = (8, 12, 16, 24, 32)
LS = (0.5, 1.0, 1.5, 2.0, 3.0)
M_TRI, M_F2 = 48, 96
B_MAT = 20_000
N_BATCH = int(os.environ.get("CUEN_BATCHES", "2000"))
ROUND = int(os.environ.get("CUEN_ROUND", "50"))           # seed tag; round 51 rerun: 51, 4000 batches
OUT_JSON = "followup_cuen.json" if ROUND == 50 else f"followup_cuen_r{ROUND}.json"
# Round 53 (FOLLOWUP_REPLICATION_RULES.md, round-53 addendum): batches per N chosen to minimise CPU cost for a planned
# SE(slope at L = 3) of 0.0045 from round 51's per-batch spreads and per-N batch times, with a 4000-batch floor at
# every N (keeps the linearity χ²); extension k ≥ 1 (CUEN_EXTEND) adds 25% per step at N = 8 and 24, until SE ≤ 0.005.
ALLOC_53 = {8: 188_000, 12: 4000, 16: 4000, 24: 27_000, 32: 4000}
EXTEND = int(os.environ.get("CUEN_EXTEND", "0"))
SE_TARGET_53 = 0.005


def n_batch(N):
    if ROUND != 53:
        return N_BATCH
    b = ALLOC_53[N]
    return b + (EXTEND * b) // 4 if N in (8, 24) else b


def gl(m, a, b):
    x, w = np.polynomial.legendre.leggauss(m)
    return 0.5 * (b - a) * x + 0.5 * (b + a), 0.5 * (b - a) * w


def kappa3_exact(L, N=None, m=M_TRI):
    """κ₃(L) = L + 3F₂ + F₃ (followup_k3.terms with the CUE_N kernel; N = None is the sine kernel)."""
    rho = lambda xs: RZ.sine_rho(xs, N)                                                 # noqa: E731
    u, wu = gl(M_F2, 0.0, L)
    f2 = 2 * np.sum(wu * (L - u) * (rho([np.zeros_like(u), u]) - 1))
    a, wa = gl(m, 0.0, 1.0)
    b, wb = gl(m, 0.0, 1.0)
    A, B = np.meshgrid(a, b, indexing="ij")
    W = (np.outer(wa, wb) * L * L * (1 - A)).ravel()
    U, V = (L * A).ravel(), (L * (1 - A) * B).ravel()
    z0 = np.zeros_like(U)
    kc = rho([z0, U, U + V]) - rho([z0, U]) - rho([z0, U + V]) - rho([z0, V]) + 2
    f3 = 6 * np.sum(W * (L - U - V) * kc)
    return float(L + 3 * f2 + f3)


def exact_table():
    out = {}
    for L in LS:
        ks = kappa3_exact(L)
        out[str(L)] = dict(sine=ks, quad_err_sine=abs(ks - kappa3_exact(L, m=M_TRI + 16)),
                           cue={str(N): kappa3_exact(L, N) for N in NS})
        print(f"L = {L}: κ₃^sine {ks:.6f}; κ₃^CUE_N − sine: "
              + ", ".join(f"N={N} {out[str(L)]['cue'][str(N)] - ks:+.3e}" for N in NS), flush=True)
    return out


def k3_batch(th, N):
    x = th * N / (2 * np.pi)
    res = {}
    k = th.shape[0]
    for L in LS:
        nw = int(N // L)
        j = (x // L).astype(np.int64)
        ok = j < nw
        per = np.zeros((k, nw), np.int64)
        rows = np.broadcast_to(np.arange(k)[:, None], j.shape)
        np.add.at(per, (rows[ok], j[ok]), 1)
        v = per.ravel().astype(float)
        W = v.size
        m3 = np.mean((v - v.mean()) ** 3)
        res[str(L)] = float(W * W * m3 / ((W - 1) * (W - 2)))
    return res


def jobs():
    return [(N, c) for N in NS for c in range(n_batch(N))]


def run(chunk, nchunks, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"cuen_c{chunk:02d}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["N"], r["batch"]) for r in map(json.loads, open(path))}
    for i, (N, c) in enumerate(jobs()):
        if i % nchunks != chunk or (N, c) in done:
            continue
        rng = np.random.default_rng([20261016, ROUND, N, c])
        th = cbe.haar_phases(rng, B_MAT, N)
        r = dict(N=N, batch=c, n_mat=B_MAT, seed_round=ROUND, k3=k3_batch(th, N))
        with open(path, "a") as fh:
            fh.write(json.dumps(r) + "\n")


def merge(out_dir):
    rows = {}
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("cuen_c") and fn.endswith(".jsonl"):
            for r in map(json.loads, open(os.path.join(out_dir, fn))):
                rows.setdefault((r["N"], r["batch"]), r)
    missing = set(jobs()) - set(rows)
    if missing:
        raise SystemExit(f"merge: {len(missing)} jobs missing")
    ex = exact_table()
    res = dict(round="fiftieth" if ROUND == 50 else f"round {ROUND} rerun", seed_round=ROUND, NS=NS, B_MAT=B_MAT,
               N_BATCH=N_BATCH if ROUND != 53 else {str(N): n_batch(N) for N in NS}, extend=EXTEND, exact=ex, L={})
    for L in LS:
        x, y, se = [], [], []
        for N in NS:
            v = np.array([rows[(N, c)]["k3"][str(L)] for c in range(n_batch(N))])
            x.append(ex[str(L)]["cue"][str(N)])
            y.append(float(v.mean()))
            se.append(float(v.std(ddof=1) / np.sqrt(len(v))))
        x, y, se = map(np.array, (x, y, se))
        w = 1 / se ** 2
        X = np.stack([np.ones_like(x), x], 1)
        cov = np.linalg.inv(X.T @ (w[:, None] * X))
        beta = cov @ (X.T @ (w * y))
        chi2 = float(np.sum(w * (y - X @ beta) ** 2))
        from scipy.stats import chi2 as C2
        pval = float(C2.sf(chi2, len(NS) - 2))
        res["L"][str(L)] = dict(kappa3_exact=x.tolist(), k3_mean=y.tolist(), k3_se=se.tolist(),
                                z_exact=((y - x) / se).tolist(), slope=float(beta[1]), slope_se=float(np.sqrt(cov[1, 1])),
                                intercept=float(beta[0]), chi2=chi2, dof=len(NS) - 2, p=pval)
        print(f"L = {L}: slope {beta[1]:.4f} ± {np.sqrt(cov[1, 1]):.4f} (χ² {chi2:.2f} on {len(NS) - 2}, p {pval:.3f}); "
              f"z(mean k₃ − exact) " + ", ".join(f"{z:+.2f}" for z in (y - x) / se), flush=True)
    if ROUND == 53:
        r = res["L"]["3.0"]
        done = r["slope_se"] <= SE_TARGET_53
        divide = done and abs(r["slope"] - 1) > 2 * r["slope_se"]
        res["round53"] = dict(se_target=SE_TARGET_53, se_reached=done,
                              decision=None if not done else ("divide the slope out" if divide else "slope = 1"),
                              g=None if not done else (r["slope"] if divide else 1.0),
                              dmu_sys_add=None if not done else r["slope_se"],
                              next=None if done else f"extend: CUEN_EXTEND={EXTEND + 1}")
        print(f"round 53: SE(slope) {r['slope_se']:.5f} (target ≤ {SE_TARGET_53}): "
              + (f"reached; |slope − 1| = {abs(r['slope'] - 1):.5f} vs 2·SE {2 * r['slope_se']:.5f} → "
                 f"{res['round53']['decision']}, g = {res['round53']['g']}, δμ_sys += {r['slope_se']:.5f}" if done
                 else f"NOT reached → {res['round53']['next']}"), flush=True)
    json.dump(res, open(os.path.join(HERE, "results", OUT_JSON), "w"), indent=1)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "exact":
        exact_table()
    elif cmd == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == "merge":
        sys.exit(merge(sys.argv[2]))

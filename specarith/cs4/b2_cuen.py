"""Corrected (B): ∂μ*/∂μ at L* through the offset-averaged estimator (CORRECTED_B_DESIGN.md §4), under round 53's rule:
CUE_N known-answer slope with SE(slope) ≤ 0.005; divide the slope out only if |slope − 1| > 2·SE; its SE in δμ_sys
either way. Data-free.

For N ∈ NS: per batch, B_MAT Haar U(N) matrices (cbe.haar_phases), each its own piece of span N, through b2_est.Acc at
L* (k̄₃ over 32 offsets); the slope is the WLS slope of the batch-mean k̄₃ on the exact κ₃^{CUE_N}(L*)
(followup_cuen.kappa3_exact). Batches per N: a pilot of PILOT batches per N (seeds [20261018, 59, N, c]), then the
cost-minimising allocation for a planned SE of 0.0045 with a floor of FLOOR batches per N (round 53's method, from the
pilot's per-batch spreads and per-batch times), then the main run (seeds [20261018, 60, N, c]); if SE(slope) > 0.005,
the two allocated-heavy N are extended by 25% per step (EXTEND) until it is ≤ 0.005. The pilot is not pooled with the
main run.

  python b2_cuen.py pilot CHUNK NCHUNKS OUT_DIR
  python b2_cuen.py plan OUT_DIR                   → OUT_DIR/plan.json
  python b2_cuen.py run CHUNK NCHUNKS OUT_DIR      (main run, reads plan.json; B2CUEN_EXTEND=k for extensions)
  python b2_cuen.py merge OUT_DIR                  → results/b2_cuen.json (slope, SE, χ², the round-53 decision)
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b2_est as E  # noqa: E402
import b2_pred as BP  # noqa: E402

NS = (8, 12, 16, 24, 32)
B_MAT, PILOT, FLOOR = 20_000, 400, 4000
SE_PLAN, SE_TARGET = 0.0045, 0.005
EXTEND = int(os.environ.get("B2CUEN_EXTEND", "0"))


def batch(N, seed, L):
    import cbe
    t = time.time()
    rng = np.random.default_rng(seed)
    th = cbe.haar_phases(rng, B_MAT, N)
    x = np.sort(np.mod(th, 2 * np.pi), axis=1) * N / (2 * np.pi)
    a = E.Acc(L, B_MAT * N, segs=(B_MAT * N,))
    a.add_block(x, float(N), np.arange(B_MAT) * N)
    return float(a.k3_offsets().mean()), time.time() - t


def _run(jobs, chunk, nchunks, path, tag):
    L = BP.L_star()
    done = {(r["N"], r["batch"]) for r in map(json.loads, open(path))} if os.path.exists(path) else set()
    for i, (N, c) in enumerate(jobs):
        if i % nchunks != chunk or (N, c) in done:
            continue
        k3, dt = batch(N, [20261018, tag, N, c], L)
        with open(path, "a") as fh:
            fh.write(json.dumps(dict(N=N, batch=c, k3bar=k3, t=round(dt, 3), L=L)) + "\n")


def pilot(chunk, nchunks, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    _run([(N, c) for N in NS for c in range(PILOT)], chunk, nchunks, os.path.join(out_dir, f"pilot_c{chunk:02d}.jsonl"), 59)


def _rows(out_dir, prefix):
    rows = {}
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith(prefix):
            for r in map(json.loads, open(os.path.join(out_dir, fn))):
                rows[(r["N"], r["batch"])] = r
    return rows


def _slope_se(x, sd, n):
    w = n / sd ** 2
    X = np.stack([np.ones_like(x), x], 1)
    return float(np.sqrt(np.linalg.inv(X.T @ (w[:, None] * X))[1, 1]))


def plan(out_dir):
    import followup_cuen as C
    L = BP.L_star()
    rows = _rows(out_dir, "pilot_c")
    x = np.array([C.kappa3_exact(L, N) for N in NS])
    sd = np.array([np.std([rows[(N, c)]["k3bar"] for c in range(PILOT)], ddof=1) for N in NS])
    tm = np.array([np.median([rows[(N, c)]["t"] for c in range(PILOT)]) for N in NS])
    best = None
    grid = [FLOOR * k for k in range(1, 151)]
    for i in range(len(NS)):                        # two heavy N on top of the floor (round 53's shape), searched
        for j in range(i + 1, len(NS)):
            for a in grid:
                for b in grid:
                    n = np.full(len(NS), float(FLOOR))
                    n[i], n[j] = a, b
                    if _slope_se(x, sd, n) <= SE_PLAN:
                        cost = float(np.sum(n * tm))
                        if best is None or cost < best[0]:
                            best = (cost, n.astype(int).tolist(), (NS[i], NS[j]))
                        break
    if best is None:
        raise SystemExit("plan: no allocation reaches the planned SE within the grid")
    p = dict(L=L, kappa3_exact=x.tolist(), pilot_sd=sd.tolist(), pilot_t=tm.tolist(), alloc=dict(zip(map(str, NS), best[1])),
             heavy=best[2], cost_cpu_h=best[0] / 3600, se_plan=SE_PLAN)
    json.dump(p, open(os.path.join(out_dir, "plan.json"), "w"), indent=1)
    print(p, flush=True)


def _alloc(out_dir):
    p = json.load(open(os.path.join(out_dir, "plan.json")))
    a = {int(k): v for k, v in p["alloc"].items()}
    for N in p["heavy"]:
        a[N] += EXTEND * a[N] // 4
    return a


def run(chunk, nchunks, out_dir):
    a = _alloc(out_dir)
    _run([(N, c) for N in NS for c in range(a[N])], chunk, nchunks, os.path.join(out_dir, f"main_c{chunk:02d}.jsonl"), 60)


def merge(out_dir):
    import followup_cuen as C
    from scipy.stats import chi2 as C2
    L = BP.L_star()
    a = _alloc(out_dir)
    rows = _rows(out_dir, "main_c")
    missing = [(N, c) for N in NS for c in range(a[N]) if (N, c) not in rows]
    if missing:
        raise SystemExit(f"merge: {len(missing)} batches missing")
    x = np.array([C.kappa3_exact(L, N) for N in NS])
    y = np.array([np.mean([rows[(N, c)]["k3bar"] for c in range(a[N])]) for N in NS])
    se = np.array([np.std([rows[(N, c)]["k3bar"] for c in range(a[N])], ddof=1) / np.sqrt(a[N]) for N in NS])
    w = 1 / se ** 2
    X = np.stack([np.ones_like(x), x], 1)
    cov = np.linalg.inv(X.T @ (w[:, None] * X))
    beta = cov @ (X.T @ (w * y))
    chi2 = float(np.sum(w * (y - X @ beta) ** 2))
    slope, sse = float(beta[1]), float(np.sqrt(cov[1, 1]))
    reached = sse <= SE_TARGET
    divide = reached and abs(slope - 1) > 2 * sse
    res = dict(L=L, NS=NS, batches={str(N): a[N] for N in NS}, extend=EXTEND, kappa3_exact=x.tolist(), k3_mean=y.tolist(),
               k3_se=se.tolist(), slope=slope, slope_se=sse, chi2=chi2, dof=len(NS) - 2, p=float(C2.sf(chi2, len(NS) - 2)),
               rule=dict(se_target=SE_TARGET, se_reached=bool(reached),
                         decision=None if not reached else ("divide the slope out" if divide else "slope = 1"),
                         g=None if not reached else (slope if divide else 1.0), dmu_sys_add=None if not reached else sse,
                         next=None if reached else f"extend: B2CUEN_EXTEND={EXTEND + 1}"))
    json.dump(res, open(os.path.join(HERE, "results", "b2_cuen.json"), "w"), indent=1)
    print(f"L* = {L}: slope {slope:.4f} ± {sse:.4f} (χ² {chi2:.2f} on {len(NS) - 2}); " + (
        f"{res['rule']['decision']}, g = {res['rule']['g']}, δμ_sys += {sse:.5f}" if reached else res["rule"]["next"]))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "pilot":
        pilot(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == "plan":
        plan(sys.argv[2])
    elif cmd == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif cmd == "merge":
        sys.exit(merge(sys.argv[2]))

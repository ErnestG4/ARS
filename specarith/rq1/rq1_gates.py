"""RQ1 Step 1 gates and witnesses (round 85). Criteria are declared here, before running; outputs go to results/GATES.json.

G0  estimator exactness: var_exact equals the brute pair formula Σ_{i,j} max(0, w − d_ij) − (Nw)² to 1e-9 relative,
    on 20 random point sets (N = 200–2,000) × K ∈ {2, 5, 17, 64, 300}.
G1  uniform i.i.d.: E[Var] = (N/K)(1 − 1/K) exactly (binomial; the window-centre average of a Binomial(N, 1/K) count).
    N = 2,000, M = 4,000 replicates (seed 85), K ∈ {4, 16, 64, 256}; PASS iff |mean − binomial| ≤ 3·SE at every K.
G2  CUE: the exact arc number variance V(w) = Σ_{m≠0} sin²(πmw)/(πm)²·min(|m|, N), in closed form
    2Σ_{m=1}^{N} sin²(πmw)/(π²m) + 2N[w(1 − w)/2 − Σ_{m=1}^{N} sin²(πmw)/(π²m²)].
    Haar CUE_N (QR of complex Ginibre with phase fix; Mezzadri 2007), N = 100, M = 4,000 (seed 851),
    K ∈ {2, 5, 10, 25, 50}; PASS iff |mean − V| ≤ 3·SE at every K.
G3  ℤ[i] against Rudnick–Waxman's published numerics: RW Figure 1 (x ≈ 10⁸; 46 points (β, Var/E) recovered exactly
    from the PDF's vector paths, results/RW_FIG1_POINTS.json, PDF sha256 864ede1b…a720). Ours: RW's convention (all
    prime ideals of norm ≤ x, inert at θ = 0, (1 + i) at ½), RW's estimator (eq. 1.2, window centre averaged, computed
    exactly), x = 10⁸, K = round(N^β) at their 46 β. Declared tolerance: |ours − theirs| ≤ 0.03 at every β ≥ 0.5,
    and median |ours − theirs| ≤ 0.05 over β < 0.5 (few windows; their exact x and K-rounding are not stated).
    §9.E: the same at x = 10⁷, reported with the 10⁷ → 10⁸ change, before the comparison is read.
W   witnesses on a ℤ[√2] archive segment (p < 10⁷), each must be FLAGGED by `audit`: (i) inert primes added (rows
    (p, 0), p ≡ ±3 mod 8, p² ≤ 10⁷): a spike at θ = 0; (ii) conjugate ideals added as a second row per split p:
    a repeated p. The clean segment must pass `audit`.

  python rq1_gates.py OUT_JSON
"""
import json
import math
import sys
import time

import numpy as np

import rq1_angles as R


def audit(ab, X):
    """Archive checks: every row a split prime p ≤ X with |a² − 2b²| = p, each p once, θ ∈ (0, ½], no θ = 0."""
    th, p = R.thetas_from_ab(ab)
    issues = []
    if np.any(th < 1e-12):
        issues.append(f"spike at θ = 0: {int(np.sum(th < 1e-12))} rows")
    if np.any(th > 0.5 + 1e-12):
        issues.append(f"θ > ½: {int(np.sum(th > 0.5 + 1e-12))} rows")
    u, c = np.unique(p, return_counts=True)
    if np.any(c > 1):
        issues.append(f"repeated p: {int(np.sum(c > 1))}")
    if not set(np.unique(p % 8).tolist()) <= {1, 7}:
        issues.append("non-split p")
    ref = R.primes_in(2, X + 1)
    ref = ref[(ref % 8 == 1) | (ref % 8 == 7)]
    if not np.array_equal(np.sort(u), ref):
        issues.append(f"split-prime set mismatch ({len(u)} vs {len(ref)})")
    return issues


def cue_phases(n, rng):
    z = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / math.sqrt(2)
    q, r = np.linalg.qr(z)
    q = q * (np.diag(r) / np.abs(np.diag(r)))
    return np.mod(np.angle(np.linalg.eigvals(q)) / (2 * math.pi), 1.0)


def cue_var(n, w):
    m = np.arange(1, n + 1)
    s2 = np.sin(math.pi * m * w) ** 2
    return float(2 * np.sum(s2 / (math.pi ** 2 * m)) + 2 * n * (w * (1 - w) / 2 - np.sum(s2 / (math.pi ** 2 * m ** 2))))


def main(out):
    res = {}
    t0 = time.time()
    rng = np.random.default_rng(850)
    worst = 0.0
    for i in range(20):
        th = rng.random(int(rng.integers(200, 2001)))
        for K in (2, 5, 17, 64, 300):
            a, b = R.var_exact(th, K), R.var_pairs(th, K)
            worst = max(worst, abs(a - b) / max(abs(b), 1e-300))
    res["G0"] = dict(max_rel=worst, PASS=bool(worst <= 1e-9))
    print("G0", res["G0"], flush=True)

    rng = np.random.default_rng(85)
    N, M = 2000, 4000
    rows, ok = {}, True
    for K in (4, 16, 64, 256):
        v = np.array([R.var_exact(rng.random(N), K) for _ in range(M)])
        exp = N / K * (1 - 1 / K)
        se = v.std(ddof=1) / math.sqrt(M)
        rows[K] = dict(mean=float(v.mean()), binomial=exp, se=float(se), z=float((v.mean() - exp) / se))
        ok &= abs(v.mean() - exp) <= 3 * se
    res["G1"] = dict(N=N, M=M, K=rows, PASS=bool(ok))
    print("G1", res["G1"], flush=True)

    rng = np.random.default_rng(851)
    n, M = 100, 4000
    Ks = (2, 5, 10, 25, 50)
    acc = {K: [] for K in Ks}
    for _ in range(M):
        ph = cue_phases(n, rng)
        for K in Ks:
            acc[K].append(R.var_exact(ph, K))
    rows, ok = {}, True
    for K in Ks:
        v = np.array(acc[K])
        exp = cue_var(n, 1 / K)
        se = v.std(ddof=1) / math.sqrt(M)
        rows[K] = dict(mean=float(v.mean()), exact=exp, se=float(se), z=float((v.mean() - exp) / se))
        ok &= abs(v.mean() - exp) <= 3 * se
    res["G2"] = dict(N=n, M=M, K=rows, PASS=bool(ok))
    print("G2", res["G2"], flush=True)

    pts = json.load(open("results/RW_FIG1_POINTS.json"))
    g3 = {}
    for x in (10 ** 7, 10 ** 8):
        th = R.gaussian_thetas(x)
        Nn = len(th)
        rr = []
        for beta, theirs in pts:
            K = max(1, int(round(Nn ** beta)))
            rr.append(dict(beta=beta, K=K, ours=R.var_exact(th, K) / (Nn / K), theirs=theirs))
        g3[str(x)] = dict(N=Nn, rows=rr)
        print("G3 x", x, "N", Nn, flush=True)
    r8, r7 = g3[str(10 ** 8)]["rows"], g3[str(10 ** 7)]["rows"]
    hi = [abs(r["ours"] - r["theirs"]) for r in r8 if r["beta"] >= 0.5]
    lo = [abs(r["ours"] - r["theirs"]) for r in r8 if r["beta"] < 0.5]
    res["G3"] = dict(x_values=g3, max_abs_dev_beta_ge_half=max(hi), median_abs_dev_beta_lt_half=float(np.median(lo)),
                     change_1e7_to_1e8_max=max(abs(a["ours"] - b["ours"]) for a, b in zip(r7, r8)),
                     PASS=bool(max(hi) <= 0.03 and np.median(lo) <= 0.05))
    print("G3", {k: v for k, v in res["G3"].items() if k != "x_values"}, flush=True)

    X = 10 ** 7
    ab = R.gen_segment(2, X)
    clean = audit(ab, X)
    inert = np.array([[p, 0] for p in R.primes_in(3, math.isqrt(X) + 1).tolist() if p % 8 in (3, 5)], np.int32)
    w1 = audit(np.concatenate([ab, inert]), X)
    th, p = R.thetas_from_ab(ab)
    conj = []
    for (a, b), pp in zip(ab.tolist(), p.tolist()):
        c = (a - 2 * b, a - b)                                    # π′·ε, θ → 1 − θ
        conj.append((abs(c[0]), abs(c[1])) if c[0] * c[1] >= 0 else (c[0], c[1]))
    w2 = audit(np.concatenate([ab, np.array(conj, np.int32)]), X)
    res["W"] = dict(clean_issues=clean, inert_witness_issues=w1, conjugate_witness_issues=w2,
                    PASS=bool(not clean and any("θ = 0" in s for s in w1) and any("repeated p" in s for s in w2)))
    print("W", res["W"], flush=True)

    res["ALL_PASS"] = bool(all(res[g]["PASS"] for g in ("G0", "G1", "G2", "G3", "W")))
    res["wall_s"] = round(time.time() - t0, 1)
    json.dump(res, open(out, "w"), indent=1)
    print("ALL_PASS", res["ALL_PASS"], res["wall_s"], "s")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

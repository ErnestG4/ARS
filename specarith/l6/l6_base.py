"""L6 long CUE baseline (L6_BASELINE_DESIGN.md, approved round 66). Step 0 here; generation, gates and comparisons are
added in later commits, each before it runs.

Step 0 (design §2) — cbe.py's red paths before any baseline sequence is drawn (spot, CPU, gpu = False):
  python l6_base.py step0 selftest OUT.json    V1–V4 exactly as cbe.py's own selftest (incl. V4's red path)
  python l6_base.py step0 v5 OUT.json          N = 10⁴: Prüfer roots against dense CMV eigvals, max |Δθ|·N/2π ≤ 1e-8
  python l6_base.py step0 v67 OUT.json         N = 10⁵ (β = 2): certify() passes on a real draw; red paths: one root
                                               duplicated, two roots swapped, one root deleted (count check) — each must be
                                               refused; V7: every accepted root's residual |ψ_{N−1}(θ) − c_m| < F_ACCEPT,
                                               reported with its maximum; wall time of one N = 10⁵ draw recorded.
Seeds: [20261020, 65, 900 + k] (step 0 only; disjoint from the baseline's [20261020, 65, r], r < 50).

Generation (design §1, §3 witnesses; spot, CPU), one sequence per call, unfolded positions x in [0, N) saved as .npy:
  python l6_base.py gen KIND R OUT_DIR
    cue       β = 2 CMV, N = 10⁵, seeds [20261020, 65, R]        R = 0..49   (the baseline)
    cse       β = 4 CMV, N = 10⁵, seeds [20261020, 65, 600 + R]  R = 0..9    (gate-1 witness ii)
    stitched  100 independent CUE_1000 (CMV, β = 2) laid end to end (the calibration's construction), N = 10⁵,
              seeds [20261020, 65, 700 + R]                       R = 0..24   (gate-1 witness i, gate-2 witness)
    poisson   N = 10⁵ exponential spacings, seeds [20261020, 65, 800 + R]  R = 0..9  (gate-1 witness iii)
  x = θ·N/2π sorted (CMV); stitched: matrix j's x + 1000·j; poisson: cumulative sums rescaled to [0, N).

Gate 1 (design §3): Σ²(L) for L in L_GRID, per sequence the variance over disjoint windows [u + jL, u + (j+1)L) inside
[0, N) at 32 offsets u = kL/32, averaged over offsets; mean over sequences, SE = SD/√R. Exact CUE_N:
  Σ²_N(L) = (2/π²)·[Σ_{m=1}^{N} sin²(πmL/N)/m + (N/2)·(ψ′(N+1) − Σ_{m>N} cos(mx)/m²)],  x = 2πL/N,
  with Σ_{m≥1} cos(mx)/m² = π²/6 − πx/2 + x²/4 on [0, 2π] (exact; no truncation).
  The CUE passes iff |z| ≤ 3 at every L and Σ z² ≤ χ²₁₀(0.99). Each witness must FAIL the same criterion (stitched at
  some L ≥ 500; CSE at some L ≤ 10; Poisson anywhere); a witness that passes stops the work.
  python l6_base.py gate1 GEN_DIR OUT.json

Block statistics (design §4; the zeros' read code, unchanged), for every F3 / F4 / F6 file's geometry:
  route (a)      route_a_read.fit_file(MuFit.for_file(f), spacings, rng, BLOCK_LENS)         se[G], μ units
  (A)            followup_read.fit_file_A(ModelA(file), seq_A(spacings), rng)                 se[G], μ units
  corrected (B)  b2_read.fit(pred_f, b2_est.zeros_stats(x, L*, rng))   (primary)              se[G], μ units
                 b2_est.Acc pieces of 10⁵ levels, as cue_stats          (concatenation variant)
  spacings = np.diff(x) within one sequence (the seam spacing is never formed).
  python l6_base.py stats KIND R GEN_DIR OUT_DIR       per sequence  → OUT_DIR/stats_KIND_RRR.json
  python l6_base.py concat GEN_DIR OUT_DIR             the 50 CUE sequences concatenated (seams every 10⁵) → concat.json
  Var(G) at a file's geometry = SE(G)² · n_used / n_file (n = spacings for route (a) and (A), levels for (B)).
  Seeds: the bootstrap rng [20261020, 66, test, file index, KIND seed, R] (concat: R = 999).

Pair cross-check (round 66): ph2r2/longbase.growth_record on the CMV baseline, mapped onto each R₂ bin as in v2; five
  windows of 10⁶ levels, each 10 consecutive CUE sequences (seams every 10⁵), arm 3 (DE GUE was arm 1, zeros arm 2).
  python l6_base.py pair W GEN_DIR OUT_DIR             W = 0..4 → pair_WW.json

Gate 2 (design §3): halves A (even R) and B (odd R) of the 50 CUE sequences; per test and G, the file-averaged
  log(Var_A/Var_B) with an SE from the per-sequence spread; |z| ≤ 3 at every (test, G). Witness: CUE half A against
  the 25 stitched sequences must give |z| > 3 at some G ≥ 1000 for at least one test.
Compare (round 66): per test, file and G: stitched/long (the CUE_1000 calibration's declared mean bootstrap SE²
  over the long baseline's Var), zeros/long (the read records' SE² over the long baseline's Var), for the primary and
  the concatenation variant; and the pair cross-check, CMV against the 10⁶ DE GUE, per bin.
  python l6_base.py gate2 STATS_DIR OUT.json
  python l6_base.py compare STATS_DIR PAIR_DIR OUT.json
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "cs4"))
import cbe  # noqa: E402

V5_TOL = 1e-8


def env():
    import scipy
    return dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__)


def step0_selftest(out):
    t = time.time()
    res = cbe.selftest(gpu=False)
    res["wall_s"] = round(time.time() - t, 1)
    res["env"] = env()
    json.dump(res, open(out, "w"), indent=1, default=float)
    return 0 if res["PASS"] else 1


def step0_v5(out, N=10_000):
    rng = np.random.default_rng([20261020, 65, 905])
    a = cbe.verblunsky(rng, 1, N, 2.0)
    t = time.time()
    th, it = cbe.roots_np(a)
    t_pr = time.time() - t
    t = time.time()
    ref = cbe.dense_phases(a[0])
    t_d = time.time() - t
    dd = np.angle(np.exp(1j * (th[0] - ref))) * N / cbe.TWO_PI
    worst = float(np.abs(dd).max())
    res = dict(N=N, max_abs_unfolded_diff=worst, tol=V5_TOL, iters=int(it), t_prufer_s=round(t_pr, 1),
               t_dense_s=round(t_d, 1), PASS=bool(worst <= V5_TOL), env=env())
    json.dump(res, open(out, "w"), indent=1)
    print(res, flush=True)
    return 0 if res["PASS"] else 1


def refused(th):
    try:
        cbe.certify(th)
        return False
    except RuntimeError:
        return True


def step0_v67(out, N=100_000):
    rng = np.random.default_rng([20261020, 65, 967])
    a = cbe.verblunsky(rng, 1, N, 2.0)
    t = time.time()
    th, it = cbe.roots_np(a)
    wall = time.time() - t
    ok_real = not refused(th) and th.shape == (1, N)
    dup = th.copy()
    dup[0, N // 2] = dup[0, N // 2 - 1]
    swp = th.copy()
    swp[0, [N // 3, N // 3 + 1]] = swp[0, [N // 3 + 1, N // 3]]
    dele = np.delete(th, N // 4, axis=1)
    red = dict(duplicated=refused(dup), swapped=refused(swp), deleted_count_check=dele.shape[1] != N)
    c0, _ = cbe.targets(a)
    c = c0[:, None] + cbe.TWO_PI * np.arange(N)[None, :]
    phi, _ = cbe.phi_np(a, th)
    resid = np.abs(N * th - c + phi)
    sp = cbe.spacings(th)
    res = dict(N=N, iters=int(it), wall_s=round(wall, 1), certify_real=bool(ok_real), red_paths=red,
               V6_PASS=bool(ok_real and all(red.values())), max_residual=float(resid.max()),
               F_ACCEPT=cbe.F_ACCEPT, V7_PASS=bool(resid.max() < cbe.F_ACCEPT),
               psi_headroom_ulp=float(np.spacing(cbe.TWO_PI * N)), min_spacing=float(sp.min()),
               mean_spacing=float(sp.mean()), env=env())
    res["PASS"] = res["V6_PASS"] and res["V7_PASS"]
    json.dump(res, open(out, "w"), indent=1)
    print(res, flush=True)
    return 0 if res["PASS"] else 1


# ---------------------------------------------------------------- V7 diagnostic and amendment (design §9, round 67)
def _root_table(a, th):
    N = a.shape[1]
    c0, _ = cbe.targets(a)
    c = c0[:, None] + cbe.TWO_PI * np.arange(N)[None, :]
    phi, dp = cbe.phi_np(a, th)
    f = np.abs(N * th - c + phi)[0]
    ulp = np.spacing(np.abs(th[0]))
    return f, dp[0], ulp


def step0_v7diag(out, N=10_000):
    rng = np.random.default_rng([20261020, 65, 905])                       # V5's draw
    a = cbe.verblunsky(rng, 1, N, 2.0)
    th, it = cbe.roots_np(a)
    ref = cbe.dense_phases(a[0])
    dist = np.abs(np.angle(np.exp(1j * (th[0] - ref)))) * N / cbe.TWO_PI
    f, dp, ulp = _root_table(a, th)
    floor = dp * ulp
    ver = dist <= V5_TOL
    over = ver & (f > cbe.F_ACCEPT)
    res = dict(N=N, iters=int(it), n_roots=N, n_verified=int(ver.sum()), n_unverified=int((~ver).sum()),
               max_dist_unfolded=float(dist.max()), F_ACCEPT=cbe.F_ACCEPT,
               n_verified_over_F_ACCEPT=int(over.sum()), max_residual_verified=float(f[ver].max()),
               residual_quantiles={q: float(np.quantile(f, q)) for q in (0.5, 0.9, 0.99, 0.999, 1.0)},
               psi_prime_quantiles={q: float(np.quantile(dp, q)) for q in (0.5, 0.9, 0.99, 0.999, 1.0)},
               floor_of_over=[float(x) for x in floor[over][:50]], residual_of_over=[float(x) for x in f[over][:50]],
               env=env())
    if res["n_unverified"]:
        res["reading"] = "unverified roots: a sampler-accuracy finding; neither branch (design §9)"
        K = None
    elif over.any():
        need = (f[over] - cbe.F_ACCEPT) / floor[over]
        K = float(2.0 ** max(0, math.ceil(math.log2(max(need.max(), 1.0)))))
        res["reading"] = "V7 miscalibrated: verified roots exceed F_ACCEPT; amended threshold F_ACCEPT + K psi' ulp"
    else:
        K = None
        res["reading"] = "every verified root passes V7: the N = 1e5 failure is real; DE fallback (design §9)"
    res["K"] = K
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("n_verified", "n_unverified", "n_verified_over_F_ACCEPT",
                                          "max_residual_verified", "K", "reading")}), flush=True)
    return 0


def step0_v7amended(diag_json, out, N=100_000):
    K = json.load(open(diag_json))["K"]
    if K is None:
        raise SystemExit("v7amended: the diagnostic did not call for an amendment (design §9)")
    rng = np.random.default_rng([20261020, 65, 967])                       # the step-0 V6/V7 draw
    a = cbe.verblunsky(rng, 1, N, 2.0)
    t = time.time()
    th, it = cbe.roots_np(a)
    wall = time.time() - t
    f, dp, ulp = _root_table(a, th)
    thr = cbe.F_ACCEPT + K * dp * ulp
    bad = f > thr
    base = os.path.splitext(out)[0]
    np.save(base + "_theta.npy", th[0])
    np.save(base + "_psi_prime.npy", dp)
    res = dict(N=N, K=K, iters=int(it), wall_s=round(wall, 1), max_residual=float(f.max()),
               n_over_F_ACCEPT=int((f > cbe.F_ACCEPT).sum()), n_fail_amended=int(bad.sum()),
               max_residual_over_threshold=float((f / thr).max()), V7_amended_PASS=bool(not bad.any()), env=env())
    json.dump(res, open(out, "w"), indent=1)
    print(res, flush=True)
    return 0 if res["V7_amended_PASS"] else 1


# ---------------------------------------------------------------- V7 targeted check at N = 10⁵ (design §10, round 68)
MP_DPS = 40


def step0_v7check(out, N=100_000):
    rng = np.random.default_rng([20261020, 65, 967])                       # the step-0 V6/V7 draw
    a = cbe.verblunsky(rng, 1, N, 2.0)
    t = time.time()
    th, it = cbe.roots_np(a)
    wall = time.time() - t
    f, dp, ulp = _root_table(a, th)
    base = os.path.splitext(out)[0]
    np.save(base + "_alpha.npy", a[0])
    np.save(base + "_theta.npy", th[0])
    np.save(base + "_psi_prime.npy", dp)
    np.save(base + "_residual.npy", f)
    json.dump(dict(N=N, iters=int(it), wall_s=round(wall, 1)), open(base + "_solve.json", "w"), indent=1)
    return v7check_refine(out)


def _phi_mp(a, theta):
    import mpmath as mp
    z = mp.expj(theta)
    b = z
    phi = mp.mpf(0)
    for k in range(len(a) - 1):
        w = 1 - a[k] * b
        aw = abs(w) ** 2
        phi -= 2 * mp.arg(w)
        b = z * b * mp.conj(w) ** 2 / aw
    return phi


def _refine_one(args):
    import mpmath as mp
    alpha_path, c0s, m, th = args
    mp.mp.dps = MP_DPS
    a = [mp.mpc(complex(x)) for x in np.load(alpha_path)]
    N = len(a)
    cm = mp.mpf(c0s) + 2 * mp.pi * m
    fm = lambda x: N * x - cm + _phi_mp(a, x)                               # noqa: E731
    u = float(np.spacing(abs(th)))
    h, lo, hi = 64 * u, None, None
    while h <= 2 ** 20 * u:
        l_, r_ = mp.mpf(th) - h, mp.mpf(th) + h
        if fm(l_) < 0 < fm(r_):
            lo, hi = l_, r_
            break
        h *= 2
    if lo is None:
        return dict(m=int(m), c_ok=False, reason="no sign change within 2^20 ulp")
    while hi - lo > mp.mpf("1e-30"):
        mid = (lo + hi) / 2
        if fm(mid) < 0:
            lo = mid
        else:
            hi = mid
    tm = (lo + hi) / 2
    d = float(abs(tm - mp.mpf(th)) * N / (2 * mp.pi))
    return dict(m=int(m), theta_mp=mp.nstr(tm, 35), dist_spacings=d, c_ok=bool(d <= 1e-6))


def v7check_refine(out, nproc=48):
    import mpmath as mp
    from multiprocessing import Pool
    base = os.path.splitext(out)[0]
    a = np.load(base + "_alpha.npy")[None, :]
    th = np.load(base + "_theta.npy")
    dp = np.load(base + "_psi_prime.npy")
    f = np.load(base + "_residual.npy")
    N = a.shape[1]
    flag = np.where(f > cbe.F_ACCEPT)[0]
    ulp = np.spacing(np.abs(th))
    ca = f[flag] <= cbe.BRACKET_ULPS * dp[flag] * ulp[flag] + 1e-6                      # (a)
    lo_, hi_ = th[flag].copy(), th[flag].copy()
    for _ in range(cbe.BRACKET_ULPS):
        lo_, hi_ = np.nextafter(lo_, -np.inf), np.nextafter(hi_, np.inf)
    c0, _ = cbe.targets(a)
    c = c0[0] + cbe.TWO_PI * flag
    fl = (N * lo_ - c) + cbe.phi_np(a, lo_[None, :])[0][0]
    fh = (N * hi_ - c) + cbe.phi_np(a, hi_[None, :])[0][0]
    cb = (fl < 0) & (fh > 0)                                                               # (b)
    mp.mp.dps = MP_DPS
    am = [mp.mpc(complex(x)) for x in a[0]]
    p0 = _phi_mp(am, mp.mpf(0))
    tt = -mp.arg(am[-1])
    d0 = tt - p0
    c0m = p0 + (d0 - 2 * mp.pi * mp.floor(d0 / (2 * mp.pi)))
    if c0m <= p0:
        c0m += 2 * mp.pi
    jobs = [(base + "_alpha.npy", mp.nstr(c0m, 45), int(m), float(th[m])) for m in flag]
    with Pool(min(nproc, max(1, len(jobs)))) as pool:
        cc = pool.map(_refine_one, jobs, chunksize=1) if jobs else []                       # (c)
    rows = [dict(m=int(m), residual=float(f[m]), psi_prime=float(dp[m]), floor=float(dp[m] * ulp[m]),
                 a_ok=bool(x), b_ok=bool(y), **{k: v for k, v in z.items() if k != "m"})
            for m, x, y, z in zip(flag, ca, cb, cc)]
    all_b_c = all(r["b_ok"] and r["c_ok"] for r in rows)
    all_a = all(r["a_ok"] for r in rows)
    K = 1.0
    need = [(r["residual"] - cbe.F_ACCEPT) / r["floor"] for r in rows if r["c_ok"]]
    if need and max(need) > K:
        K = float(2.0 ** math.ceil(math.log2(max(need))))
    amended = f <= cbe.F_ACCEPT + K * dp * ulp
    if not all_b_c:
        reading = "a flagged root fails (b) or (c): Dumitriu-Edelman fallback via a design addendum (design §10)"
    elif not all_a:
        reading = "(a) fails while (b) and (c) hold: not covered by round 68; to Will (design §10)"
    else:
        reading = "(a), (b), (c) hold for every flagged root: V7 miscalibrated; §9 amendment applies; generate CMV"
    res = dict(N=N, n_flagged=int(len(flag)), c0_float=float(c0[0]), c0_mp=mp.nstr(c0m, 20),
               n_a=int(sum(r["a_ok"] for r in rows)), n_b=int(sum(r["b_ok"] for r in rows)),
               n_c=int(sum(r["c_ok"] for r in rows)),
               max_dist_spacings=max([r.get("dist_spacings", float("inf")) for r in rows], default=0.0),
               K=K, K_raised_beyond_committed=bool(K > 1.0), amended_V7_pass=bool(amended.all()),
               n_fail_amended=int((~amended).sum()), reading=reading, PASS=bool(all_b_c and all_a and amended.all()),
               flagged=rows, env=env())
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("flagged", "env")}), flush=True)
    return 0 if res["PASS"] else 1


def step0_v7a_bracket(out):
    """Round 69's post-hoc amendment to (a), on the saved v7check arrays (design §11): the slope across the bracket.
    f = N·θ − c_m + φ(θ) is strictly increasing (f′ = ψ′ > 0). For a flagged root θ, the edge θ_e is BRACKET_ULPS
    representable doubles from θ on the root's side (up if f(θ) < 0, down if f(θ) > 0), s_br = |f(θ_e) − f(θ)|/|θ_e − θ|,
    and (a′) holds iff |f(θ)| ≤ BRACKET_ULPS·s_br·ulp(θ) + 1e-6. The v7check record itself is not modified."""
    base = os.path.join(os.path.dirname(out), "v7check")
    a = np.load(base + "_alpha.npy")[None, :]
    th = np.load(base + "_theta.npy")
    f_saved = np.load(base + "_residual.npy")
    dp = np.load(base + "_psi_prime.npy")
    N = a.shape[1]
    flag = np.where(f_saved > cbe.F_ACCEPT)[0]
    c0, _ = cbe.targets(a)
    c = c0[0] + cbe.TWO_PI * flag
    ks = np.arange(-cbe.BRACKET_ULPS, cbe.BRACKET_ULPS + 1)
    grid = np.empty((len(flag), len(ks)))
    grid[:, cbe.BRACKET_ULPS] = th[flag]
    for j in range(1, cbe.BRACKET_ULPS + 1):
        grid[:, cbe.BRACKET_ULPS + j] = np.nextafter(grid[:, cbe.BRACKET_ULPS + j - 1], np.inf)
        grid[:, cbe.BRACKET_ULPS - j] = np.nextafter(grid[:, cbe.BRACKET_ULPS - j + 1], -np.inf)
    fg = (N * grid - c[:, None]) + cbe.phi_np(a, grid.reshape(1, -1))[0][0].reshape(grid.shape)
    ulp = np.spacing(np.abs(th[flag]))
    rows = []
    for i, m in enumerate(flag):
        f0 = fg[i, cbe.BRACKET_ULPS]
        e = -1 if f0 < 0 else 0                                                   # root side: up if f(θ) < 0
        te, fe = grid[i, e], fg[i, e]
        s_br = abs(fe - f0) / abs(te - grid[i, cbe.BRACKET_ULPS])
        bound = cbe.BRACKET_ULPS * s_br * ulp[i] + 1e-6
        s_sym = (fg[i, -1] - fg[i, 0]) / (grid[i, -1] - grid[i, 0])               # descriptive: symmetric secant
        rows.append(dict(m=int(m), f_theta=float(f0), f_saved=float(f_saved[m]),
                         f_steps=[float(x) for x in fg[i]], monotone=bool(np.all(np.diff(fg[i]) > 0)),
                         slope_bracket=float(s_br), psi_prime=float(dp[m]), slope_over_psi_prime=float(s_br / dp[m]),
                         bound_a_amended=float(bound), a_amended_ok=bool(abs(f0) <= bound),
                         bound_a_original=float(cbe.BRACKET_ULPS * dp[m] * ulp[i] + 1e-6),
                         a_original_ok=bool(abs(f0) <= cbe.BRACKET_ULPS * dp[m] * ulp[i] + 1e-6),
                         bound_symmetric_secant=float(cbe.BRACKET_ULPS * s_sym * ulp[i] + 1e-6),
                         symmetric_secant_ok=bool(abs(f0) <= cbe.BRACKET_ULPS * s_sym * ulp[i] + 1e-6)))
    res = dict(N=N, n_flagged=len(rows), n_a_amended=sum(r["a_amended_ok"] for r in rows),
               n_a_original=sum(r["a_original_ok"] for r in rows),
               n_symmetric_secant=sum(r["symmetric_secant_ok"] for r in rows),
               n_monotone=sum(r["monotone"] for r in rows),
               max_abs_f_minus_saved=float(max(abs(abs(r["f_theta"]) - r["f_saved"]) for r in rows)),
               PASS=bool(rows and all(r["a_amended_ok"] for r in rows)), rows=rows,
               label="post-hoc amendment to (a), round 69 (design §11); descriptive record", env=env())
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("rows", "env")}), flush=True)
    return 0 if res["PASS"] else 1


# ---------------------------------------------------------------- generation
N_SEQ = 100_000
SEED_BASE = {"cue": 0, "cse": 600, "stitched": 700, "poisson": 800}
L_GRID = (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000)
NU = 32


def gen(kind, r, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    rng = np.random.default_rng([20261020, 65, SEED_BASE[kind] + r])
    t = time.time()
    meta = dict(kind=kind, r=r, seed=[20261020, 65, SEED_BASE[kind] + r], N=N_SEQ)
    if kind in ("cue", "cse"):
        th, it = cbe.sample(rng, 1, N_SEQ, 2.0 if kind == "cue" else 4.0)          # roots_np certifies
        x = np.sort(th[0]) * N_SEQ / cbe.TWO_PI
        meta["iters"] = int(it)
    elif kind == "stitched":
        th, it = cbe.sample(rng, N_SEQ // 1000, 1000, 2.0)
        x = (np.sort(th, axis=1) * 1000 / cbe.TWO_PI + 1000.0 * np.arange(N_SEQ // 1000)[:, None]).ravel()
        meta["iters"] = int(it)
    elif kind == "poisson":
        c = np.cumsum(rng.exponential(1.0, N_SEQ + 1))
        x = c[:-1] * N_SEQ / c[-1]
    else:
        raise SystemExit(f"gen: unknown kind {kind}")
    assert len(x) == N_SEQ and np.all(np.diff(x) > 0) and 0 <= x[0] and x[-1] < N_SEQ
    meta.update(wall_s=round(time.time() - t, 1), env=env())
    p = os.path.join(out_dir, f"{kind}_{r:03d}.npy")                          # per-sequence checkpoint: the .npy
    json.dump(meta, open(os.path.join(out_dir, f"{kind}_{r:03d}.json"), "w"), indent=1)
    np.save(p[:-4] + ".part.npy", x)                                          # appears last and whole (os.replace)
    os.replace(p[:-4] + ".part.npy", p)
    print(meta, flush=True)
    return 0


# ---------------------------------------------------------------- gate 1: Σ²(L)
def sigma2_exact(L, N=N_SEQ):
    from scipy.special import polygamma
    m = np.arange(1, N + 1, dtype=float)
    x = cbe.TWO_PI * L / N
    s1 = float(np.sum(np.sin(math.pi * m * L / N) ** 2 / m))
    clausen_all = math.pi ** 2 / 6 - math.pi * x / 2 + x * x / 4
    tail_cos = clausen_all - float(np.sum(np.cos(m * x) / m ** 2))
    tail = 0.5 * N * (float(polygamma(1, N + 1)) - tail_cos)
    return 2 / math.pi ** 2 * (s1 + tail)


def sigma2_sine(L):
    from scipy.special import sici
    si, ci = sici(2 * math.pi * L)
    return float((math.log(2 * math.pi * L) + np.euler_gamma + 1 - math.cos(2 * math.pi * L) - ci) / math.pi ** 2
                 + L * (1 - 2 * si / math.pi))


def sigma2_seq(x, L, N=N_SEQ):
    v = []
    for k in range(NU):
        u = k * L / NU
        W = int((N - u) // L)
        j = np.floor((x - u) / L).astype(np.int64)
        c = np.bincount(j[(x >= u) & (j < W)], minlength=W)
        v.append(c.var(ddof=1))
    return float(np.mean(v))


def gate1(gen_dir, out):
    import glob
    from scipy.stats import chi2
    res = dict(L=list(L_GRID), exact_cue=[sigma2_exact(L) for L in L_GRID], sine=[sigma2_sine(L) for L in L_GRID],
               chi2_99=float(chi2.ppf(0.99, len(L_GRID))), kinds={})
    ex = np.array(res["exact_cue"])
    for kind in ("cue", "stitched", "cse", "poisson"):
        paths = sorted(glob.glob(os.path.join(gen_dir, f"{kind}_*.npy")))
        if not paths:
            continue
        S = np.array([[sigma2_seq(np.load(p), L) for L in L_GRID] for p in paths])
        m, se = S.mean(0), S.std(0, ddof=1) / math.sqrt(len(S))
        z = (m - ex) / se
        ok = bool(np.all(np.abs(z) <= 3) and np.sum(z ** 2) <= res["chi2_99"])
        res["kinds"][kind] = dict(R=len(S), mean=m.tolist(), se=se.tolist(), z=z.tolist(), sum_z2=float(np.sum(z ** 2)),
                                  passes_criterion=ok)
    k = res["kinds"]
    L = np.array(L_GRID)
    wit = dict(stitched_fails_at_L_ge_500=bool(np.any(np.abs(np.array(k["stitched"]["z"]))[L >= 500] > 3)),
               cse_fails_at_L_le_10=bool(np.any(np.abs(np.array(k["cse"]["z"]))[L <= 10] > 3)),
               poisson_fails=not k["poisson"]["passes_criterion"])
    res.update(cue_passes=k["cue"]["passes_criterion"], witnesses=wit,
               GATE1=bool(k["cue"]["passes_criterion"] and all(wit.values())),
               exact_vs_sine_max_rel=float(np.max(np.abs(ex - np.array(res["sine"])) / np.array(res["sine"]))))
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({kk: res[kk] for kk in ("cue_passes", "witnesses", "GATE1", "exact_vs_sine_max_rel")}), flush=True)
    return 0 if res["GATE1"] else 1


# ---------------------------------------------------------------- block statistics (the zeros' read code)
CS4 = os.path.join(HERE, "..", "cs4")
R2D = os.path.join(HERE, "..", "ph2r2")
TESTS = ("route_a", "A", "B2")
KIND_SEED = {"cue": 0, "stitched": 700}


def _cs4():
    sys.path.insert(0, CS4)
    sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
    import route_a_read as RA
    import followup_read as FR
    import b2_read as BR
    import b2_est as E
    import b2_pred as BP
    return RA, FR, BR, E, BP


def _setup():
    RA, FR, BR, E, BP = _cs4()
    pa = json.load(open(os.path.join(CS4, os.path.relpath(RA.PRED, CS4))))
    pf = json.load(open(os.path.join(CS4, os.path.relpath(FR.PRED["A"], CS4))))
    pb = json.load(open(BR.PRED))
    fits = {f: RA.MuFit.for_file(f, pa) for f in RA.F3}
    models = {f: FR.ModelA(pf["files"][f]["dp_nodes"], pf["n_f"][f]) for f in FR.FILES["A"]}
    return RA, FR, BR, E, BP, fits, models, pb


def _stats_one(x_or_pieces, kind_seed, r, S, concat=False):
    RA, FR, BR, E, BP, fits, models, pb = S
    if concat:
        X = x_or_pieces                                   # (R, N) positions, each piece in [0, N)
        sp = np.concatenate([np.diff(x) for x in X])
    else:
        x = x_or_pieces
        sp = np.diff(x)
    out = {}
    for ti, (test, files) in enumerate((("route_a", list(RA.F3)), ("A", list(FR.FILES["A"])), ("B2", list(BR.FILES)))):
        out[test] = {}
        for fi, f in enumerate(files):
            rng = np.random.default_rng([20261020, 66, ti, fi, kind_seed, r])
            if test == "route_a":
                res = RA.fit_file(fits[f], sp, rng, RA.BLOCK_LENS, gof=False)
                se, n = {str(k): v for k, v in res["se"].items()}, res["n"]
            elif test == "A":
                res = FR.fit_file_A(models[f], FR.seq_A(sp), rng)
                se, n = res.get("se"), res["n"]
            else:
                L = BP.L_star()
                if concat:
                    a = E.Acc(L, X.shape[0] * X.shape[1], E.SEGS)
                    a.add_block(X, float(X.shape[1]), np.arange(X.shape[0]) * float(X.shape[1]))
                    raw = a.result(rng, BR.B_BOOT)
                    n = int(X.size)
                else:
                    raw = E.zeros_stats(x, L, rng, n_boot=BR.B_BOOT)
                    n = int(len(x))
                se = {str(k): v for k, v in BR.fit(pb["files"][f], raw)["se"].items()}
            out[test][f] = dict(se=se, n=int(n), fail=res.get("fail") if test != "B2" else None)
    return out


def stats(kind, r, gen_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    S = _setup()
    x = np.load(os.path.join(gen_dir, f"{kind}_{r:03d}.npy"))
    t = time.time()
    rec = dict(kind=kind, r=r, stats=_stats_one(x, KIND_SEED[kind], r, S), wall_s=None, env=env())
    rec["wall_s"] = round(time.time() - t, 1)
    json.dump(rec, open(os.path.join(out_dir, f"stats_{kind}_{r:03d}.json"), "w"), indent=1)
    print(kind, r, rec["wall_s"], "s", flush=True)
    return 0


def concat(gen_dir, out_dir, R=50):
    os.makedirs(out_dir, exist_ok=True)
    S = _setup()
    X = np.stack([np.load(os.path.join(gen_dir, f"cue_{r:03d}.npy")) for r in range(R)])
    t = time.time()
    rec = dict(kind="cue_concat", R=R, stats=_stats_one(X, 0, 999, S, concat=True), env=env())
    rec["wall_s"] = round(time.time() - t, 1)
    json.dump(rec, open(os.path.join(out_dir, "concat.json"), "w"), indent=1)
    print("concat", rec["wall_s"], "s", flush=True)
    return 0


def pair(w, gen_dir, out_dir, per=10):
    sys.path.insert(0, R2D)
    import g0b as G0
    import r2prep as RP
    import longbase as LB
    os.makedirs(out_dir, exist_ok=True)
    X = [np.load(os.path.join(gen_dir, f"cue_{r:03d}.npy")) for r in range(w * per, (w + 1) * per)]
    u = np.concatenate([x - x[0] + N_SEQ * i for i, x in enumerate(X)])
    rec = dict(window=w, n=int(len(u)), sequences=list(range(w * per, (w + 1) * per)), bins={}, env=env())
    for name in RP.BINS:
        g = RP.geometry(name)
        t = G0.nbar_inv(float(RP.nbar(g["t0"])) + 0.5 + u, g["tc"])
        rec["bins"][name] = LB.growth_record(t, name, 3, w)
    json.dump(rec, open(os.path.join(out_dir, f"pair_{w:02d}.json"), "w"), indent=1)
    print("pair", w, {k: round(v["growth_drift_removed"][-1], 3) for k, v in rec["bins"].items()}, flush=True)
    return 0


def _var_table(recs, test):
    """{file: {G: array over sequences of SE²·n_used}} (Var at unit level count)."""
    out = {}
    for rec in recs:
        for f, v in rec["stats"][test].items():
            if v["se"] is None:
                continue
            for G, se in v["se"].items():
                if se is not None:
                    out.setdefault(f, {}).setdefault(G, []).append(se * se * v["n"])
    return {f: {G: np.array(a) for G, a in d.items()} for f, d in out.items()}


def _load(stats_dir, kind):
    import glob
    return [json.load(open(p)) for p in sorted(glob.glob(os.path.join(stats_dir, f"stats_{kind}_*.json")))]


def _logratio(VA, VB):
    """File-averaged log(mean A / mean B) per G with a delta-method SE (files share sequences: averaged, not pooled)."""
    out = {}
    for G in sorted({G for f in VA for G in VA[f]}, key=int):
        lr, se2 = [], []
        for f in VA:
            a, b = VA[f][G], VB[f][G]
            lr.append(math.log(a.mean() / b.mean()))
            se2.append((a.std(ddof=1) / a.mean()) ** 2 / len(a) + (b.std(ddof=1) / b.mean()) ** 2 / len(b))
        lr, se = float(np.mean(lr)), float(math.sqrt(np.mean(se2)))
        out[G] = dict(log_ratio=lr, ratio=math.exp(lr), se=se, z=lr / se)
    return out


def gate2(stats_dir, out):
    cue = _load(stats_dir, "cue")
    st = _load(stats_dir, "stitched")
    A = [r for r in cue if r["r"] % 2 == 0]
    B = [r for r in cue if r["r"] % 2 == 1]
    res = dict(n_A=len(A), n_B=len(B), n_stitched=len(st), tests={}, witness={})
    ok, wit = True, False
    for test in TESTS:
        h = _logratio(_var_table(A, test), _var_table(B, test))
        w = _logratio(_var_table(A, test), _var_table(st, test))
        res["tests"][test] = h
        res["witness"][test] = w
        ok &= all(abs(v["z"]) <= 3 for v in h.values())
        wit |= any(abs(v["z"]) > 3 for G, v in w.items() if int(G) >= 1000)
    res.update(halves_agree=bool(ok), stitched_witness_fires=bool(wit), GATE2=bool(ok and wit))
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: res[k] for k in ("halves_agree", "stitched_witness_fires", "GATE2")}), flush=True)
    return 0 if res["GATE2"] else 1


def compare(stats_dir, pair_dir, out):
    import glob
    RA, FR, BR, E, BP = _cs4()
    reads = {"route_a": os.path.join(CS4, "results/read/run1/ROUTE_A_READ.json"),
             "A": os.path.join(CS4, "results/followup_read/A/run1/FOLLOWUP_READ.json"),
             "B2": os.path.join(CS4, "results/b2_read/run1/B2_READ.json")}
    cals = {"route_a": os.path.join(CS4, "results/calib/route_a_calib_declared.json"),
            "A": os.path.join(CS4, "results/calib/followup_calib_A_declared.json"),
            "B2": os.path.join(CS4, "results/calib/b2_calib_declared.json")}
    cue = _load(stats_dir, "cue")
    cc = json.load(open(os.path.join(stats_dir, "concat.json")))
    res = dict(tests={}, pair={})
    for test in TESTS:
        rd = json.load(open(reads[test]))["records"]
        cal = json.load(open(cals[test]))["files"]
        V = _var_table(cue, test)
        Vc = _var_table([cc], test)
        res["tests"][test] = {}
        for f in V:
            nz = rd[f]["n_zeros"] if test == "B2" else rd[f]["n"]       # levels for (B); spacings / seq for the others
            row = {}
            for G in sorted(V[f], key=int):
                vl = V[f][G].mean() / nz
                vl_se = V[f][G].std(ddof=1) / math.sqrt(len(V[f][G])) / nz
                vc = Vc[f][G][0] / nz
                vz = rd[f]["se"][G] ** 2
                vs = cal[f]["se_boot_mean"][G] ** 2
                row[G] = dict(var_long=vl, var_long_rel_se=vl_se / vl, var_long_concat=vc, var_zeros=vz,
                              var_stitched_cal=vs, stitched_over_long=vs / vl, zeros_over_long=vz / vl,
                              stitched_over_long_concat=vs / vc, zeros_over_long_concat=vz / vc,
                              zeros_over_stitched=vz / vs, concat_vs_primary=vc / vl)
            res["tests"][test][f] = row
    lb = json.load(open(os.path.join(R2D, "results", "longbase_v2", "longbase_summary.json")))["1000000"]["bins"]
    P_ = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(pair_dir, "pair_*.json")))]
    for name in lb:
        v = np.array([p["bins"][name]["growth_drift_removed"][-1] for p in P_])
        m, se = float(v.mean()), float(v.std(ddof=1) / math.sqrt(len(v)))
        dm, dse = lb[name]["gue_drift_removed"]
        res["pair"][name] = dict(cmv=[m, se], de_gue=[dm, dse], cmv_over_de=m / dm,
                                 diff_in_combined_se=(m - dm) / math.sqrt(se ** 2 + dse ** 2), n_cmv_windows=len(v))
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res["pair"], indent=1), flush=True)
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "step0":
        if sys.argv[2] == "v7amended":
            sys.exit(step0_v7amended(sys.argv[3], sys.argv[4]))
        if sys.argv[2] == "v7check":
            sys.exit(step0_v7check(sys.argv[3]))
        if sys.argv[2] == "v7check_refine":
            sys.exit(v7check_refine(sys.argv[3]))
        if sys.argv[2] == "v7a_bracket":
            sys.exit(step0_v7a_bracket(sys.argv[3]))
        sys.exit({"selftest": step0_selftest, "v5": step0_v5, "v67": step0_v67, "v7diag": step0_v7diag}[sys.argv[2]](
            sys.argv[3]))
    elif sys.argv[1] == "gen":
        sys.exit(gen(sys.argv[2], int(sys.argv[3]), sys.argv[4]))
    elif sys.argv[1] == "gate1":
        sys.exit(gate1(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "stats":
        sys.exit(stats(sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]))
    elif sys.argv[1] == "concat":
        sys.exit(concat(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "pair":
        sys.exit(pair(int(sys.argv[2]), sys.argv[3], sys.argv[4]))
    elif sys.argv[1] == "gate2":
        sys.exit(gate2(sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == "compare":
        sys.exit(compare(sys.argv[2], sys.argv[3], sys.argv[4]))

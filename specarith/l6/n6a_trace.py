"""n = 6 stage (a), round 74 (N6_STAGE_A.md): the exact U(N) block variance of corrected (B)'s estimator, data-free.

CUE_N in unfolded units is determinantal with K(x, y) = sin(π(x − y)) / (N sin(π(x − y)/N)). For windows A = [0, L) and
B = [r, r + L), the joint generating function of the counts is a Fredholm determinant,
  F(z, w) = E[z^{n_A} w^{n_B}] = det(I − K·g),  g = 1 − z on A∖B, 1 − w on B∖A, 1 − zw on A∩B,
discretised by Gauss–Legendre on each sub-interval (Bornemann). The joint factorial moments f_ab = ∂_z^a ∂_w^b F at (1, 1)
come from the Taylor coefficients of F(1 + s, 1 + t) on |s| = |t| = 0.75 (2-D DFT; well conditioned, unlike the pmf), and
C(r) = Cov(ψ(n_A), ψ(n_B)) = Σ c_a c_b (f_ab − f_a f_b), with ψ(n) = (n − m)³ − 3σ²(n − m) (the k₃ influence function)
written in the falling-factorial basis. The estimator's
offsets sit on a grid of step Δ = L/NU, so (κ₃ units)
  W(G) = Δ·[C(0) + 2 Σ_{k ≥ 1} (1 − kΔ/G) C(kΔ)],
the target of b2_est's segment bootstrap (SE²·n) and of the round-73 global-mean estimator.

  python n6a_trace.py check OUT.json             pmf/κ₃ known answers and node convergence
  python n6a_trace.py chunk J NCHUNK OUT_DIR      C(kΔ) for the k of chunk J
  python n6a_trace.py summary OUT_DIR             → OUT_DIR/N6A_SUMMARY.json (prediction vs the L6 long baseline)
"""
import glob
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
N = 100_000
L = 4.0
NU = 32
DELTA = L / NU
GMAX = 10_000
K_MAX = int(round(GMAX / DELTA))                 # 80,000
M = 24                                           # DFT size: counts 0..23 (P(n ≥ 24) in 4 units is ~0)
NODES_PER_WINDOW = 24
GS = (300, 1000, 3000, 10000)


def kernel(x, y):
    s = x[:, None] - y[None, :]
    with np.errstate(invalid="ignore", divide="ignore"):
        k = np.sin(np.pi * s) / (N * np.sin(np.pi * s / N))
    k[s == 0] = 1.0
    return k


def _gl(a, b, n):
    t, w = np.polynomial.legendre.leggauss(n)
    return 0.5 * (b - a) * t + 0.5 * (a + b), 0.5 * (b - a) * w


def _nodes(r, npw):
    """Nodes, weights and region code (0 = A only, 1 = B only, 2 = both) for A = [0, L), B = [r, r + L), r ≥ 0."""
    parts = []
    if r >= L:
        parts = [(0.0, L, 0), (r, r + L, 1)]
    elif r == 0:
        parts = [(0.0, L, 2)]
    else:
        parts = [(0.0, r, 0), (r, L, 2), (L, r + L, 1)]
    xs, ws, cs = [], [], []
    for a, b, c in parts:
        n = max(8, int(math.ceil(npw * (b - a) / L)))
        x, w = _gl(a, b, n)
        xs.append(x), ws.append(w), cs.append(np.full(n, c))
    return np.concatenate(xs), np.concatenate(ws), np.concatenate(cs)


RHO = 0.75                                       # Taylor-coefficient circle |s| = |t| = RHO around z = w = 1
MT = 16                                          # DFT size for the coefficients (orders 0..15; F's are ~0 beyond)


def _fact_coeffs(r, npw=NODES_PER_WINDOW, rho=RHO):
    """Taylor coefficients c[i, j] of G(s, t) = F(1 + s, 1 + t) = det(I − K g), g = −s on A∖B, −t on B∖A, −(s + t + st)
    on A∩B; the joint factorial moments are f_ij = i! j! c[i, j]."""
    x, w, c = _nodes(r, npw)
    sw = np.sqrt(w)
    Kw = sw[:, None] * kernel(x, x) * sw[None, :]
    om = rho * np.exp(2j * np.pi * np.arange(MT) / MT)
    S, T = np.meshgrid(om, om, indexing="ij")
    g = np.where(c[None, None, :] == 0, (-S)[..., None],
                 np.where(c[None, None, :] == 1, (-T)[..., None], (-(S + T + S * T))[..., None]))
    D = np.eye(len(x))[None, None] - Kw[None, None] * g[:, :, None, :]
    Fv = np.linalg.det(D)
    cf = np.fft.fft2(Fv) / MT ** 2
    i = np.arange(MT)
    return (cf / rho ** (i[:, None] + i[None, :])).real


def _fm(cf, amax=3):
    fac = np.array([math.factorial(a) for a in range(amax + 1)], float)
    return cf[:amax + 1, :amax + 1] * fac[:, None] * fac[None, :]


def single_moments(npw=NODES_PER_WINDOW, rho=RHO):
    """Factorial moments f_a = E[(n)_a] of one window, a = 0..3, from the t = 0 column of a disjoint pair."""
    f = _fm(_fact_coeffs(10.0 * L, npw, rho))
    return f[:, 0]


def moments(f):
    m = f[1]
    s2 = f[2] + f[1] - f[1] ** 2
    k3 = f[3] + 3 * f[2] + f[1] - 3 * m * (f[2] + f[1]) + 2 * m ** 3
    return float(m), float(s2), float(k3)


def psi_coeffs(f):
    """ψ(n) = (n − m)³ − 3σ²(n − m) in the falling-factorial basis: coefficients of (n)_1, (n)_2, (n)_3."""
    m, s2, _ = moments(f)
    return np.array([0.0, 1 - 3 * m + 3 * m * m - 3 * s2, 3 - 3 * m, 1.0])


def _conn_coeffs_disjoint(r, npw=NODES_PER_WINDOW, rho=RHO):
    """r ≥ L: Taylor coefficients of the connected part F − F_A F_B = F_A F_B (e^X − 1), with
    X = log det(I − Q⁻¹ K_BA g_A P⁻¹ K_AB g_B) (Schur complement; P = I − K_AA g_A, Q = I − K_BB g_B) summed as
    Σ log1p(−λ) over the small eigenvalues, so nothing cancels at long range."""
    xa, wa = _gl(0.0, L, npw)
    xb, wb = _gl(r, r + L, npw)
    sa, sb = np.sqrt(wa), np.sqrt(wb)
    Kaa = sa[:, None] * kernel(xa, xa) * sa[None, :]
    Kbb = sb[:, None] * kernel(xb, xb) * sb[None, :]
    Kab = sa[:, None] * kernel(xa, xb) * sb[None, :]
    Kba = Kab.T
    om = rho * np.exp(2j * np.pi * np.arange(MT) / MT)
    I = np.eye(npw)
    P = I[None] + Kaa[None] * om[:, None, None]            # g_A = −s, so I − K g_A = I + s K
    Q = I[None] + Kbb[None] * om[:, None, None]
    FA = np.linalg.det(P)                                    # F_A(1 + s) on the circle (= F_B by translation)
    FB = np.linalg.det(Q)
    PinvKab = np.linalg.solve(P, np.broadcast_to(Kab, P.shape))       # (MT, m, m): P(s)⁻¹ K_AB
    QinvKba = np.linalg.solve(Q, np.broadcast_to(Kba, Q.shape))       # Q(t)⁻¹ K_BA
    H = np.empty((MT, MT), complex)
    for b in range(MT):                                      # t index
        for a in range(MT):                                  # s index
            Mx = QinvKba[b] @ (PinvKab[a] * (-om[b])) * (-om[a])        # Q⁻¹ K_BA g_A P⁻¹ K_AB g_B (g = −s, −t)
            lam = np.linalg.eigvals(Mx)
            X = np.sum(np.log1p(-lam))
            H[a, b] = FA[a] * FB[b] * np.expm1(X)
    cf = np.fft.fft2(H) / MT ** 2
    i = np.arange(MT)
    return (cf / rho ** (i[:, None] + i[None, :])).real


def cov_r(r, f1, cpsi, npw=NODES_PER_WINDOW, rho=RHO):
    """C(r) = Σ_{a,b ≥ 1} c_a c_b (f_ab − f_a f_b); the connected part is taken directly for disjoint windows."""
    if r >= L:
        conn = _fm(_conn_coeffs_disjoint(r, npw, rho))
        return float(cpsi @ conn @ cpsi), 0.0
    f = _fm(_fact_coeffs(r, npw, rho))
    conn = f - np.outer(f1, f1)
    return float(cpsi @ conn @ cpsi), float(np.abs(f[:, 0] - f1).max())


def check(out):
    f1 = single_moments()
    m, s2, k3 = moments(f1)
    f1b = single_moments(36, 0.5)
    cpsi = psi_coeffs(f1)
    rows = []
    for r in (0.0, 0.5, 2.0, 3.875, 4.0, 4.125, 7.3, 100.0, 5000.0):
        c24, marg = cov_r(r, f1, cpsi)
        c36, _ = cov_r(r, f1, cpsi, 36)
        c_rho, _ = cov_r(r, f1, cpsi, NODES_PER_WINDOW, 0.5)
        rows.append(dict(r=r, C=c24, C_36nodes=c36, C_rho05=c_rho, abs_diff_nodes=abs(c24 - c36),
                         abs_diff_rho=abs(c24 - c_rho), max_marginal_err=marg))
    tol = 1e-11                                  # per point; bounds W error by tol·K_MAX·2Δ ≈ 2e-7 (≈ 3e-6 relative)
    res = dict(N=N, L=L, mean=m, var=s2, kappa3=k3, kappa3_sine_pred=0.0037028835622399114,
               kappa3_diff=abs(k3 - 0.0037028835622399114), single_36_rho05_vs=float(np.abs(f1b - f1).max()), conv=rows,
               PASS=bool(abs(m - L) < 1e-10 and abs(k3 - 0.0037028835622399114) < 1e-8
                         and max(max(r["abs_diff_nodes"], r["abs_diff_rho"]) for r in rows) < tol
                         and max(r["max_marginal_err"] for r in rows) < 1e-10), tol=tol)
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "conv"}), flush=True)
    for r in rows:
        print(r, flush=True)
    return 0 if res["PASS"] else 1


def chunk(j, nchunk, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    f1 = single_moments()
    cpsi = psi_coeffs(f1)
    ks = np.arange(j, K_MAX + 1, nchunk)
    t = time.time()
    C = np.array([cov_r(k * DELTA, f1, cpsi)[0] for k in ks])
    np.savez(os.path.join(out_dir, f"C_{j:03d}.npz"), k=ks, C=C)
    print(j, len(ks), round(time.time() - t, 1), flush=True)
    return 0


def summary(out_dir):
    sys.path.insert(0, HERE)
    import l6_base as B
    k = np.concatenate([np.load(f)["k"] for f in sorted(glob.glob(os.path.join(out_dir, "C_*.npz")))])
    C = np.concatenate([np.load(f)["C"] for f in sorted(glob.glob(os.path.join(out_dir, "C_*.npz")))])
    o = np.argsort(k)
    k, C = k[o], C[o]
    assert np.array_equal(k, np.arange(K_MAX + 1)), "missing C(kΔ) points"
    W = {}
    for G in GS:
        kk = np.arange(1, int(round(G / DELTA)))
        W[str(G)] = float(DELTA * (C[0] + 2 * np.sum((1 - kk * DELTA / G) * C[kk])))
    pb = json.load(open(os.path.join(B.CS4, "results", "b2_pred.json")))["files"]
    cue = B._load(os.path.join(HERE, "results", "base", "stats"), "cue")
    V = B._var_table(cue, "B2")
    r73 = json.load(open(os.path.join(HERE, "results", "r73", "R73_SUMMARY.json")))["tests"]["B2"]
    rows = {}
    for f in V:
        d2 = pb[f]["dkappa3"] ** 2
        row = {}
        for G in GS:
            ns = int(math.floor(1e5 / G)) + 1
            ns_eff = 1e5 / G
            w = V[f][str(G)] * d2
            wb = float(w.mean()) * ns_eff / (ns_eff - 1)
            wb_se = float(w.std(ddof=1) / math.sqrt(len(w))) * ns_eff / (ns_eff - 1)
            wg, wg_se = r73[f][str(G)]["W_glob"] * d2, r73[f][str(G)]["W_glob_se"] * d2
            pred = W[str(G)]
            row[str(G)] = dict(W_pred=pred, W_boot_raw=float(w.mean()), W_boot_corr=wb, W_boot_corr_se=wb_se,
                               z_boot=(wb - pred) / wb_se, ratio_boot=wb / pred,
                               W_glob=wg, W_glob_se=wg_se, z_glob=(wg - pred) / wg_se, ratio_glob=wg / pred,
                               primary="boot" if G <= 1000 else "glob", nseg=ns)
        rows[f] = row
    prim = [abs(r[str(G)]["z_boot" if G <= 1000 else "z_glob"]) for r in rows.values() for G in GS]
    res = dict(W_pred=W, C0=float(C[0]), C_at=dict((str(r), float(C[int(round(r / DELTA))])) for r in (1, 4, 10, 100, 1000)),
               files=rows, max_abs_z_primary=float(max(prim)), AGREES=bool(max(prim) <= 3),
               label="round 74 stage (a); data-free U(N) prediction vs the L6 long CUE baseline (N6_STAGE_A.md)")
    json.dump(res, open(os.path.join(out_dir, "N6A_SUMMARY.json"), "w"), indent=1)
    print("W_pred (kappa3 units):", {G: f"{v:.6e}" for G, v in W.items()})
    for f, r in rows.items():
        print(f[:18], " | ".join(f"G{G}: boot {r[str(G)]['ratio_boot']:.3f} (z {r[str(G)]['z_boot']:+.1f}) "
                                 f"glob {r[str(G)]['ratio_glob']:.3f} (z {r[str(G)]['z_glob']:+.1f})" for G in GS))
    print("AGREES:", res["AGREES"], "max |z| primary", round(res["max_abs_z_primary"], 2))
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "check":
        sys.exit(check(sys.argv[2]))
    if sys.argv[1] == "chunk":
        sys.exit(chunk(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]))
    if sys.argv[1] == "summary":
        sys.exit(summary(sys.argv[2]))

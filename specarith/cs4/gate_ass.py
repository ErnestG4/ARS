"""Gate G-ass (Will, nineteenth round, item 2): the variance-assembly machinery reproduces Aguirre–Soshnikov–Sumpter's
EXACT finite-N CUE variance of a pair statistic, before any block or taper geometry enters.

Statistic: S_N = Σ_{i≠j} f(θ_i − θ_j) on CUE_N, f(θ) = F(Nθ/2π) periodised, F the R₂ family bump (u = 0.5, w = 0.3;
unit mean spacing): F(d) = exp(−(d−u)²/2w²) + exp(−(d+u)²/2w²).
Known answer: ASS (RMTA 10 (2021) 2150035; arXiv 1912.07110, Prop. 4.1, β = 2), with f̂(k) = (1/2π)∫f e^{−ikθ}
= F̃(k/N)/N, F̃(ν) = 2√(2π)·w·exp(−2π²w²ν²)·cos(2πνu):
  Var = 4[Σ_{1≤s≤N−1} s² f̂(s)² + (N² − N) Σ_{s≥N} f̂(s)²]
        − 4[Σ_{s,t≥1; 1≤|s−t|≤N−1; max(s,t)≥N} (N − |s−t|) f̂(s)f̂(t) + Σ_{1≤s,t≤N−1; s+t≥N+1} (s + t − N) f̂(s)f̂(t)].
Assembly (ASS eqs. 4.0–4.3, translation-reduced; d in unit-spacing units on a circle of length N; ρ_n = R_{N,n}/N^n):
  Var = 2N∫f²(x)ρ₂(0,x)dx + 4N∫∫f(x)f(y)ρ₃(0,−x,−x−y)dxdy + N∫∫∫f(x)f(y)[ρ₄(0,−x,r,r−y) − ρ₂(0,x)ρ₂(0,y)]dr dx dy.
ρ_n is supplied by the CUE determinant here; G-a(i) showed CS08's transcribed U(N) correlations equal it pointwise
to 1e-22, and a subsample of the 4-point integrand is recomputed from the transcription (cs4lib.RMT) as a check.
Pass: |assembly − ASS| ≤ 1e-6 · ASS for N ∈ {10, 20, 50}.

  python gate_ass.py  ->  results/gate_ass.json
"""
import json
import math
import os

import mpmath as mp
import numpy as np

import cs4lib as C

HERE = os.path.dirname(os.path.abspath(__file__))
U, W = 0.5, 0.3
XMAX = 2.8                       # F(±2.8) ~ e^{−29}: negligible support cut
TOL = 1e-6


def F(d):
    return np.exp(-(d - U) ** 2 / (2 * W * W)) + np.exp(-(d + U) ** 2 / (2 * W * W))


def Ft(nu):
    return 2 * math.sqrt(2 * math.pi) * W * np.exp(-2 * math.pi ** 2 * W * W * nu ** 2) * np.cos(2 * math.pi * nu * U)


def var_ass(N, kmax_factor=12):
    K = kmax_factor * N
    fh = lambda s: Ft(np.asarray(s, float) / N) / N
    s = np.arange(1, K + 1)
    f = fh(s)
    v = 4 * (np.sum((s[:N - 1] ** 2) * f[:N - 1] ** 2) + (N * N - N) * np.sum(f[N - 1:] ** 2))
    S, T = np.meshgrid(s, s, indexing="ij")
    FF = np.outer(f, f)
    d = np.abs(S - T)
    m1 = (d >= 1) & (d <= N - 1) & (np.maximum(S, T) >= N)
    m2 = (S <= N - 1) & (T <= N - 1) & (S + T >= N + 1)
    v -= 4 * (np.sum(((N - d) * FF)[m1]) + np.sum(((S + T - N) * FF)[m2]))
    return float(v)


def kernel(D, N):
    out = np.ones_like(D)
    nz = np.abs(D) > 1e-14
    out[nz] = np.sin(np.pi * D[nz]) / (N * np.sin(np.pi * D[nz] / N))
    return out


def rho(points, N):
    """det[K(d_i − d_j)] for arrays of points: points shape (..., n)."""
    D = points[..., :, None] - points[..., None, :]
    return np.linalg.det(kernel(D, N))


def gl(a, b, m):
    x, w = np.polynomial.legendre.leggauss(m)
    return 0.5 * (b - a) * (x + 1) + a, 0.5 * (b - a) * w


def composite(a, b, panels, m):
    xs, ws = [], []
    edges = np.linspace(a, b, panels + 1)
    for lo, hi in zip(edges[:-1], edges[1:]):
        x, w = gl(lo, hi, m)
        xs.append(x)
        ws.append(w)
    return np.concatenate(xs), np.concatenate(ws)


def var_assembly(N, mx=64, r_per_unit=8, m=8):
    x, wx = composite(-XMAX, XMAX, 8, mx // 8)
    fx = F(x)
    # 2-point
    p2 = rho(np.stack([np.zeros_like(x), x], -1), N)
    T2 = 2 * N * np.sum(wx * fx ** 2 * p2)
    # 3-point
    X, Y = np.meshgrid(x, x, indexing="ij")
    p3 = rho(np.stack([np.zeros_like(X), -X, -X - Y], -1), N)
    T3 = 4 * N * np.sum(np.outer(wx * fx, wx * fx) * p3)
    # 4-point connected, r over the circle [0, N)
    r, wr = composite(0.0, float(N), N, r_per_unit)
    acc = 0.0
    for i in range(len(x)):
        R_, Yg = np.meshgrid(r, x, indexing="ij")
        pts = np.stack([np.zeros_like(R_), np.full_like(R_, -x[i]), R_, R_ - Yg], -1)
        c = rho(pts, N) - p2[i] * p2[None, :]
        acc += wx[i] * fx[i] * np.sum(wr[:, None] * (wx * fx)[None, :] * c)
    T4 = N * acc
    return float(T2 + T3 + T4), dict(T2=float(T2), T3=float(T3), T4c=float(T4))


def transcription_spotcheck(N, n_pts=6, seed=3):
    """The 4-point integrand from CS08's transcribed U(N) correlations (cs4lib.RMT) equals the determinant's."""
    rng = np.random.default_rng(seed)
    R = C.RMT(N)
    worst = 0.0
    for _ in range(n_pts):
        xx, yy, rr = rng.uniform(-XMAX, XMAX), rng.uniform(-XMAX, XMAX), rng.uniform(0, N)
        d = [0.0, -xx, rr, rr - yy]
        got = float(mp.re(R.R([mp.mpf(2 * math.pi * v / N) for v in d]))) / N ** 4
        ref = float(rho(np.array(d), N))
        worst = max(worst, abs(got - ref) / max(abs(ref), 1e-12))
    return worst


def main():
    rows = []
    for N in (10, 20, 50):
        exact = var_ass(N)
        asm, parts = var_assembly(N)
        asm2, _ = var_assembly(N, mx=96, r_per_unit=12)
        sc = transcription_spotcheck(N)
        rel = abs(asm2 - exact) / abs(exact)
        rows.append(dict(N=N, ass_exact=exact, assembly=asm2, assembly_coarse=asm, quad_change=abs(asm2 - asm) / abs(exact),
                         rel_err=rel, parts=parts, var_over_N=asm2 / N, transcription_spotcheck_rel=sc, PASS=rel <= TOL and sc <= 1e-8))
        print(f"N={N}: ASS exact {exact:.10f}  assembly {asm2:.10f}  rel {rel:.2e}  (quad change {rows[-1]['quad_change']:.1e};"
              f" transcription spot-check {sc:.1e})  Var/N {asm2 / N:.6f}")
    out = dict(PASS=all(r["PASS"] for r in rows), tol=TOL, f=dict(u=U, w=W), rows=rows)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "gate_ass.json"), "w"), indent=1)
    print("G-ass", "PASS" if out["PASS"] else "FAIL")


if __name__ == "__main__":
    main()

"""Stage 2 G-s, U(N) step (ii) (G_S_DESIGN.md §5.1): small-N exact CUE_N Monte Carlo of the tapered statistic's
variance against the assembly's prediction with the CUE_N kernel — the taper geometry (midpoint weights, (W⋆W)(r),
the 3-point overlap factor) tested end to end on a known process. (G-ass tested the assembly with W ≡ 1.)

Statistic (as ph2s2/tapered.py, on the circle of circumference N in unit spacings x = Nθ/2π):
  S(c; b) = Σ_{i≠j} F(δ_ij) · W_b(m_ij − c),   δ_ij the min-image difference, m_ij = x_i + δ_ij/2,
W_b(y) = exp(−πy²/b²) with y the min-image distance. 4.8b ≤ N/2, so wrap-around terms are < e^{−36}.

Prediction: gs_unitary's assembly with K_N(x) = sin(πx)/(N sin(πx/N)) in place of the sine kernel, r over [0, N/2].
MC: Haar CUE_N by QR of a complex Ginibre matrix (phase-corrected), 4 centres per matrix (spaced N/4, random offset);
V = pooled sample variance over matrices; SE from the per-matrix contributions.
Pass: |V_MC − V_pred| ≤ 3·SE at every b. Red paths (reported as z-scores, must be ≫ 3 to show the MC can fire):
the 3-point term with factor 2 instead of 4; the 4-point term dropped (C ≡ 0); the pair-midpoint overlap (W⋆W)(r)
with W_b's width instead of √2·b (overlap_as_W). Descriptive: the sine kernel in place of K_N (an O(1/N²) change).

  python gs_cue_mc.py pred N OUT                 predicted V(b), b ∈ BS
  python gs_cue_mc.py mc N NMAT SEED OUT          one MC chunk
  python gs_cue_mc.py merge N OUT                 verdict
"""
import glob
import json
import math
import os
import sys

import numpy as np

import gs_unitary as G

BS = (10, 20, 40)


def kern(N):
    def K(x):
        x = np.asarray(x, float)
        s = np.sin(np.pi * x / N)
        small = np.abs(s) < 1e-14
        return np.where(small, 1.0, np.sin(np.pi * x) / (N * np.where(small, 1.0, s)))
    return K


def det4k(K, d1, d2, r):
    a, f = K(d1), K(d2)
    b, c = K(r - d2 / 2 + d1 / 2), K(r + d2 / 2 + d1 / 2)
    d, e = K(r - d2 / 2 - d1 / 2), K(r + d2 / 2 - d1 / 2)
    return (1 - a * a - b * b - c * c - d * d - e * e - f * f
            + a * a * f * f + b * b * e * e + c * c * d * d
            + 2 * (a * d * b + a * e * c + b * f * c + d * f * e)
            - 2 * (a * d * f * c + a * e * f * b + b * d * e * c))


def predict(N, b, K=None, f3=4.0, with4=True, dr=0.2, ww_k=1.0):
    K = K or kern(N)
    DN, DW, FD = G.DN, G.DW, G.FD
    rho2 = lambda d: 1 - K(d) ** 2
    I2 = 2 * float(np.sum(DW * FD ** 2 * rho2(DN)))
    x, w = G.gl(-G.DMAX, G.DMAX, 2 * G.ND)
    A, E = x[:, None], x[None, :]
    p, q, s = K(A), K(E), K(E - A)
    I3 = float(np.sum(np.outer(w * G.F(x), w * G.F(x)) * (1 - p * p - q * q - s * s + 2 * p * q * s)
                      * np.exp(-math.pi * (E - A) ** 2 / (8 * b * b))))
    I4 = 0.0
    if with4:
        r = np.arange(0.0, min(4.8 * b, N / 2) + dr, dr)
        D1, D2 = DN[:, None, None], DN[None, :, None]
        c = np.einsum("ij,ijk->k", G.WD, det4k(K, D1, D2, r[None, None, :]) - rho2(D1) * rho2(D2))
        wt = (b / math.sqrt(2)) * np.exp(-ww_k * math.pi * r ** 2 / (2 * b * b)) * c
        I4 = dr * (wt[0] + 2 * np.sum(wt[1:]))
    return 2 * (b / math.sqrt(2)) * I2 + f3 * (b / math.sqrt(2)) * I3 + I4


def haar_phases(N, rng):
    Z = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / math.sqrt(2)
    Q, R = np.linalg.qr(Z)
    d = np.diagonal(R)
    Q = Q * (d / np.abs(d))
    return np.sort(np.mod(np.angle(np.linalg.eigvals(Q)), 2 * np.pi))


def stat(x, N, centres, b):
    """S(c; b) for each centre (x sorted on [0, N))."""
    n = len(x)
    xx = np.concatenate([x, x + N])
    out = np.zeros(len(centres))
    for k in range(1, 12):                               # pairs within 2.8 spacings: k ≤ 11 is ample at N ≤ 1000
        dlt = xx[k:k + n] - x
        m = dlt <= G.DMAX
        if not m.any():
            break
        mid = np.mod(x[m] + dlt[m] / 2, N)
        wF = 2 * G.F(dlt[m])                             # both orders of the unordered pair
        for j, c in enumerate(centres):
            y = np.abs(mid - c)
            y = np.minimum(y, N - y)
            out[j] += np.sum(wF * np.exp(-math.pi * y * y / (b * b)))
    return out


def mc(N, nmat, seed, out):
    rng = np.random.default_rng(seed)
    S = {b: np.empty((nmat, 4)) for b in BS}
    for i in range(nmat):
        x = haar_phases(N, rng) * N / (2 * np.pi)
        c0 = rng.uniform(0, N)
        cs = np.mod(c0 + np.arange(4) * N / 4, N)
        for b in BS:
            S[b][i] = stat(x, N, cs, b)
    os.makedirs(out, exist_ok=True)
    np.savez(os.path.join(out, f"mc_N{N}_s{seed}.npz"), **{f"b{b}": S[b] for b in BS})


def merge(N, out):
    pred = json.load(open(os.path.join(out, f"pred_N{N}.json")))
    files = sorted(glob.glob(os.path.join(out, f"mc_N{N}_s*.npz")))
    rows, ok = [], True
    for b in BS:
        S = np.concatenate([np.load(f)[f"b{b}"] for f in files])
        mu = S.mean()
        q = ((S - mu) ** 2).mean(axis=1)
        n = S.size
        V = q.mean() * n / (n - 1)
        se = q.std(ddof=1) / math.sqrt(len(q))
        p = pred[str(b)]
        z = (V - p["V"]) / se
        zr = {k: (V - v) / se for k, v in p["red"].items()}
        ok &= abs(z) <= 3
        rows.append(dict(b=b, n_mat=len(q), V_mc=V, se=se, V_pred=p["V"], z=z, z_red=zr, mean_mc=mu,
                         V_sine=p["descriptive"]["sine_kernel"], z_sine=(V - p["descriptive"]["sine_kernel"]) / se))
        print(f"N={N} b={b}: V_mc {V:.5f} ± {se:.5f}  V_pred {p['V']:.5f}  z {z:+.2f}   red z: "
              + ", ".join(f"{k} {v:+.1f}" for k, v in zr.items()), flush=True)
    for r in rows:
        ok &= all(abs(v) > 3 for v in r["z_red"].values())
    json.dump(dict(N=N, rows=rows, PASS=bool(ok)), open(os.path.join(out, f"gs_cue_mc_N{N}.json"), "w"), indent=1)
    print("G-s U(N) (ii) CUE_N MC:", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    cmd, N = sys.argv[1], int(sys.argv[2])
    if cmd == "pred":
        out = sys.argv[3]
        res = {}
        for b in BS:
            res[str(b)] = dict(V=predict(N, b), red=dict(three_pt_x2=predict(N, b, f3=2.0), no_four_pt=predict(N, b, with4=False),
                                                          overlap_as_W=predict(N, b, ww_k=2.0)),
                               descriptive=dict(sine_kernel=predict(N, b, K=G.sinc)))
            print(b, res[str(b)], flush=True)
        os.makedirs(out, exist_ok=True)
        json.dump(res, open(os.path.join(out, f"pred_N{N}.json"), "w"), indent=1)
    elif cmd == "mc":
        mc(N, int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        merge(N, sys.argv[3])

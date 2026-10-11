"""Stage 2 G-s, ζ step (G_S_DESIGN.md §2, §3, §6): the predicted v(b) = V(b)/b of the tapered statistic for the
Riemann zeros at height ℓ = log(t/2π), from CS08's n ≤ 4 correlations, computed directly at every rung of the ladder
(no functional form; twenty-first round). Same assembly as the sine-kernel step (gs_unitary.py, which reproduces the
measured long-GUE v(b) on the whole ladder):

  v(b) = √2·I₂ + 2√2·I₃(b) + (1/√2)·I₄(b),   I₄(b) = ∫ exp(−πr²/2b²) C(r) dr,
  C(r) = 4 Σ_{d₁,d₂ ≥ 0 nodes} w w F F [ρ₄c(d₁, d₂, r)]   (ρ₄ even in each in-pair offset; C(r; d₁, d₂) is even in r and
         symmetric in (d₁, d₂) because CS08's R₄ is even under x → −x: J* is symmetric in its two arguments).

Split (G_S_DESIGN §3): short range, the full connected function × χ on r = (k + ½)·0.1 < 20 (midpoint rule, exact for
the even, band-limited, smoothly cut integrand); long range, the non-oscillating part × (1 − χ) on r = 5 + 0.5k up to
4.8·10⁴ (trapezoid; the integrand vanishes identically for r ≤ 10). Evaluator: cs4lr.LongRangeZeta (validated against
cs4fastc, itself against the 50-digit reference). Prime cutoff 3·10⁵ (twenty-first round: ≥ 3·10⁵).
In-pair quadrature: Gauss–Jacobi with weight d² (ρ₄c ∝ d² as d → 0), 16 nodes on [0, 2.4]; smallest node 0.051
(sine kernel: 6e-6 relative to the 40-node reference; gs_dquad_test2.py). v1 used Gauss–Legendre, whose node at
d = 0.008 lost the signal to cancellation between pieces (5% imaginary residue in the test pair).
Noise bound: each pair also stores ∫ weight·|Im ρ₄c| (the result must be real), summed into an error bound on v(b).
The ℓ-oscillating long-range part dropped by the split is evaluated for two node pairs per height (osc check).
I₃: ρ₃(0, a, e) from cs4lib.Zeta (mp ζ; numpy prime sums), product Gauss–Legendre 40 × 42 nodes on [−2.4, 2.4]
(different orders so that a ≠ e and neither is 0 at any node: no coincident points).

  python gs_zeta.py pairs ELL CHUNK NCHUNKS OUT     four-point integrals for the node pairs of this chunk
  python gs_zeta.py rho3 ELL CHUNK NCHUNKS OUT      ρ₃ at the I₃ nodes of this chunk
  python gs_zeta.py merge ELL OUT                   v(b), g, positivity -> OUT/gs_zeta_L{ELL}.json
"""
import glob
import json
import math
import os
import sys
import time

import numpy as np
from scipy.special import roots_jacobi

import gs_unitary as G

DMAX, ND = 2.4, 16
LADDER = (100, 300, 1000, 3000, 10_000)
PMAX = 300_000
DR_S, NS = 0.1, 200
DR_L, R_LO = 0.5, 5.0
def gj(dmax, n):
    x, w = roots_jacobi(n, 0.0, 2.0)                 # weight (1 + x)² on [−1, 1]
    return 0.5 * dmax * (1 + x), 0.5 * dmax * w / (1 + x) ** 2


DN, DW = gj(DMAX, ND)
FD = G.F(DN)
PAIRS = [(i, j) for i in range(ND) for j in range(i, ND)]
OSC_PAIRS = ((5, 5), (2, 8))
NA, NE = 40, 42


def short_grid():
    return (np.arange(NS) + 0.5) * DR_S


def long_grid():
    n = int(math.ceil((4.8 * max(LADDER) - R_LO) / DR_L)) + 1
    n += n % 2
    return R_LO + DR_L * np.arange(n)


def gb(r, b):
    return np.exp(-math.pi * r ** 2 / (2 * b * b))


def tval(ell):
    return 2 * math.pi * math.exp(ell)


def pairs(ell, chunk, nchunks, out):
    import cs4lr as LR
    lr = LR.LongRangeZeta(tval(ell), pmax=PMAX)
    rs, rl = short_grid(), long_grid()
    cs_, cl_ = G.chi(rs), 1 - G.chi(rl)
    d = os.path.join(out, f"L{ell}", "pairs")
    os.makedirs(d, exist_ok=True)
    for k, (i, j) in enumerate(PAIRS):
        if k % nchunks != chunk:
            continue
        fn = os.path.join(d, f"p{i:02d}_{j:02d}.npz")
        if os.path.exists(fn):
            continue
        t0 = time.time()
        d1, d2 = DN[i], DN[j]
        o, n = lr.connected(d1, d2, rs)
        full = o + n
        tail_s = max(lr.diag.values())
        _, nl = lr.connected(d1, d2, rl, nonosc_only=True)
        tail_l = max(lr.diag.values())
        res = dict(short=np.array([2 * DR_S * np.sum(cs_ * gb(rs, b) * full.real) for b in LADDER]),
                   long=np.array([2 * DR_L * np.sum(cl_ * gb(rl, b) * nl.real) for b in LADDER]),
                   imag_max=np.array([np.abs(full.imag).max(), np.abs(nl.imag).max()]),
                   short_absim=np.array([2 * DR_S * np.sum(cs_ * gb(rs, b) * np.abs(full.imag)) for b in LADDER]),
                   long_absim=np.array([2 * DR_L * np.sum(cl_ * gb(rl, b) * np.abs(nl.imag)) for b in LADDER]),
                   tail=np.array([tail_s, tail_l]), c_short=full.real, c_non=nl.real)
        if (i, j) in OSC_PAIRS:
            ol, _ = lr.connected(d1, d2, rl)
            res["osc_long"] = np.array([2 * DR_L * np.sum(cl_ * gb(rl, b) * ol.real) for b in LADDER])
        res["secs"] = np.array([time.time() - t0])
        np.savez(fn, **res)
        print(ell, i, j, "short", res["short"][0], "long", res["long"][[0, -1]], "%.0fs" % res["secs"][0], flush=True)


def i3_nodes():
    a, wa = G.gl(-DMAX, DMAX, NA)
    e, we = G.gl(-DMAX, DMAX, NE)
    return a, wa, e, we


def rho3(ell, chunk, nchunks, out):
    import mpmath as mp
    import cs4lib as C
    Z = C.Zeta(tval(ell), pmax=PMAX)
    sg = 2 * math.pi / Z.L
    a, _, e, _ = i3_nodes()
    d = os.path.join(out, f"L{ell}", "rho3")
    os.makedirs(d, exist_ok=True)
    rows = []
    for ia in range(NA):
        if ia % nchunks != chunk:
            continue
        for ie in range(NE):
            v = Z.R([mp.mpf(0), mp.mpf(a[ia] * sg), mp.mpf(e[ie] * sg)]) / mp.mpf(Z.L) ** 3
            rows.append((ia, ie, float(mp.re(v)), float(mp.im(v))))
        print(ell, "rho3 row", ia, flush=True)
    np.save(os.path.join(d, f"c{chunk:03d}.npy"), np.array(rows))


def merge(ell, out):
    import cs4fast as F
    d = os.path.join(out, f"L{ell}")
    fz = F.FastZeta(tval(ell), pmax=PMAX)
    rho2 = np.array([fz.R2(x).real for x in DN])
    I2 = 2 * float(np.sum(DW * FD ** 2 * rho2))
    rows3 = np.concatenate([np.load(f) for f in sorted(glob.glob(os.path.join(d, "rho3", "c*.npy")))])
    assert len(rows3) == NA * NE, len(rows3)
    a, wa, e, we = i3_nodes()
    R3 = np.zeros((NA, NE))
    R3[rows3[:, 0].astype(int), rows3[:, 1].astype(int)] = rows3[:, 2]
    WW = np.outer(wa * G.F(a), we * G.F(e))
    A_, E_ = a[:, None], e[None, :]
    I3 = {b: float(np.sum(WW * R3 * np.exp(-math.pi * (E_ - A_) ** 2 / (8 * b * b)))) for b in LADDER}
    short, long_, osc, tails, imag = np.zeros(len(LADDER)), np.zeros(len(LADDER)), {}, [], []
    noise = np.zeros(len(LADDER))
    n_found = 0
    for (i, j) in PAIRS:
        z = np.load(os.path.join(d, "pairs", f"p{i:02d}_{j:02d}.npz"))
        wgt = 4 * DW[i] * FD[i] * DW[j] * FD[j] * (1 if i == j else 2)
        short += wgt * z["short"]
        long_ += wgt * z["long"]
        noise += abs(wgt) * (z["short_absim"] + z["long_absim"])
        tails.append(z["tail"].max())
        imag.append(z["imag_max"].max())
        if "osc_long" in z:
            osc[f"{i},{j}"] = dict(osc_long=z["osc_long"].tolist(), long=z["long"].tolist())
        n_found += 1
    I4 = short + long_
    v = {b: math.sqrt(2) * I2 + 2 * math.sqrt(2) * I3[b] + I4[k] / math.sqrt(2) for k, b in enumerate(LADDER)}
    res = dict(ell=ell, pmax=PMAX, I2=I2, I3=I3, I4_short=dict(zip(LADDER, short.tolist())),
               I4_long=dict(zip(LADDER, long_.tolist())), v=v, g=math.sqrt(v[10_000] / v[100]),
               positivity=all(x > 0 for x in v.values()), osc_check=osc,
               v_noise_bound=dict(zip(LADDER, (noise / math.sqrt(2)).tolist())), max_fourier_tail=float(max(tails)),
               max_imag=float(max(imag)), rho3_max_imag=float(np.abs(rows3[:, 3]).max()), n_pairs=n_found)
    json.dump(res, open(os.path.join(out, f"gs_zeta_L{ell}.json"), "w"), indent=1)
    print(f"ℓ = {ell}: " + "  ".join(f"v({b}) {v[b]:.6f}" for b in LADDER) + f"   g {res['g']:.4f}  positivity "
          f"{'PASS' if res['positivity'] else 'FAIL'}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "pairs":
        pairs(float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    elif cmd == "rho3":
        rho3(float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        merge(float(sys.argv[2]), sys.argv[3])

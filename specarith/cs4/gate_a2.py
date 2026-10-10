"""Gate G-a(ii) (combined plan §2; route (a) milestone 1, part 2): the CUE_N gap probability from the transcribed n ≤ 4
correlations, E_4(s) = 1 − s + Σ_{n=2..4} ((−1)^n/n!) ∫_{[0,s]^n} ρ_n, against the exact Fredholm determinant
det(I − K_s) with K = sin(πd)/(N sin(πd/N)) (ph2/ph2lib.fredholm_values, Phase 2's G0b-verified machinery).

Units: unit mean spacing, d = N·x/(2π); ρ_n(d) = R_{N,n}(2πd/N)/N^n (= det[K(d_i − d_j)] by G-a(i)).
Quadrature: tensor Gauss–Legendre with a different even node count per axis (10, 12, 14, 16, so no node is shared
between axes and the J* poles at coincident points are never hit), and a +4-nodes rerun for the quadrature error.
Pass criteria:
  N ≤ 4: the series terminates (ρ_n = 0 for n > N), so |E_4 − det| ≤ 1e-9 + quadrature error.
  N ≥ 5: |E_4 − det| ≤ 1.5·|S_5| + 1e-9, with S_5 = (1/5!)∫ρ_5 computed from the determinant (the first omitted term),
         and for N = 50 at s ≤ 2 also ≤ 5e-6 (the sine-kernel truncation bound, SCOPE_CS_SPACING §1).

  python gate_a2.py [PROCS]  ->  results/gate_a2.json
"""
import itertools
import json
import math
import os
import sys
from multiprocessing import Pool

import mpmath as mp
import numpy as np

import cs4lib as C

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
import ph2lib  # noqa: E402

NS = (2, 3, 4, 10, 50)
SS = (0.5, 1.0, 1.5, 2.0)


def gl(m, s):
    x, w = np.polynomial.legendre.leggauss(m)
    return 0.5 * s * (x + 1), 0.5 * s * w


def S_n_transcribed(N, n, s, base):
    R = C.RMT(N)
    axes = [gl(base + 2 * k, s) for k in range(n)]
    tot = mp.mpf(0)
    for combo in itertools.product(*[range(len(a[0])) for a in axes]):
        d = [axes[k][0][i] for k, i in enumerate(combo)]
        w = math.prod(axes[k][1][i] for k, i in enumerate(combo))
        tot += w * mp.re(R.R([mp.mpf(2 * math.pi * di / N) for di in d])) / mp.mpf(N) ** n
    return float(tot) / math.factorial(n)


def S_n_det(N, n, s, m=10):
    """(1/n!)∫ det[K(d_i − d_j)] by tensor GL (numpy), for the first omitted term S_5."""
    x, w = gl(m, s)
    tot = 0.0
    for combo in itertools.product(range(m), repeat=n):
        d = x[list(combo)]
        D = d[:, None] - d[None, :]
        K = np.ones_like(D)
        nz = np.abs(D) > 1e-15
        K[nz] = np.sin(np.pi * D[nz]) / (N * np.sin(np.pi * D[nz] / N))
        tot += np.prod(w[list(combo)]) * np.linalg.det(K)
    return tot / math.factorial(n)


def one(job):
    N, s = job
    out = dict(N=N, s=s)
    for base, tag in ((10, "q"), (14, "q4")):
        Sn = {n: S_n_transcribed(N, n, s, base) for n in (2, 3, 4)}
        out[tag] = dict(S=Sn, E4=1 - s + Sn[2] - Sn[3] + Sn[4])
    out["fredholm"] = float(ph2lib.fredholm_values(s, m=40, N=N)[0])
    out["S5_det"] = S_n_det(N, 5, s) if N >= 5 else 0.0
    out["diff"] = out["q4"]["E4"] - out["fredholm"]
    out["quad_err"] = abs(out["q4"]["E4"] - out["q"]["E4"])
    lim = (1e-9 + out["quad_err"]) if N <= 4 else (1.5 * abs(out["S5_det"]) + 1e-9 + out["quad_err"])
    if N == 50 and s <= 2.0:
        lim = min(lim, 5e-6)
    out["limit"] = lim
    out["PASS"] = bool(abs(out["diff"]) <= lim)
    print(N, s, "E4 %.12f  det %.12f  diff %.2e  S5 %.2e  quad %.1e  %s" % (
        out["q4"]["E4"], out["fredholm"], out["diff"], out["S5_det"], out["quad_err"], "PASS" if out["PASS"] else "FAIL"),
        flush=True)
    return out


def main(procs=8):
    with Pool(procs) as p:
        rows = p.map(one, [(N, s) for N in NS for s in SS], chunksize=1)
    out = dict(PASS=all(r["PASS"] for r in rows), rows=rows)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "gate_a2.json"), "w"), indent=1)
    print("G-a(ii)", "PASS" if out["PASS"] else "FAIL")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)

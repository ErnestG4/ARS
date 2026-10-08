"""C2 level build (PH6_SEAL 6.1 §1–§2): Berry–Keating 2011 with α = 0, η = 1/2π, levels E_n (BK units) and
t_n = 2π E_n (eq. 5.3). Φ(E) from c2_fast.phase (validated against scipy DOP853). Levels: Φ(E) = α + 2πm.

  python c2_build.py RES OUT PROCS      RES 1: rtol 1e-11, 3 samples per mean spacing; RES 2: rtol 1e-12, 6 samples

Φ is unwrapped as Φ = 2π E(log E − 1) + R(E) with R continuous (BK11 eq. 1.6 supplies the semiclassical part; R is
bounded and slow on the sample grid — checked: |ΔR| between samples is asserted < π/2). Each level is located by
interpolating R between samples and refined by secant on Φ itself.
"""
import cmath
import hashlib
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

import c2_fast as F

T_MAX = 26_600.0                       # same range as C1 (t up to ~2.66·10⁴: ≥ 3·10⁴ levels)
E_MAX = T_MAX / (2 * math.pi)
ALPHA = 0.0


def _phi_chunk(args):
    Es, rtol = args
    return [F.phase(E, rtol=rtol)[0] for E in Es]


def _sc(E):
    return 2 * math.pi * E * (math.log(E) - 1) if E > 0 else 0.0


def build(res, procs):
    rtol = {1: 1e-11, 2: 1e-12}[res]
    mult = {1: 1, 2: 2}[res]
    # Φ(E) is a staircase (BK11 §3 (iv): rises concentrated near α = π); measured local/mean rate ratio r ≈ 10 at
    # E ≈ 12, 2.6 at 50, 1.5 at 200. Envelope r(E) = max(2, 40/√E); local step = 1/(4·r·mult·log E) so the mean step is
    # ≤ π/(2·mult)·(1/r) and the largest local step ≈ π/2 / mult.
    Es = [0.0]
    while Es[-1] < E_MAX + 1:
        E = Es[-1]
        if E < 3:
            Es.append(E + 0.005 / mult)
        else:
            r = max(2.0, 40.0 / math.sqrt(E))
            Es.append(E + 1 / (4 * r * mult * math.log(E)))
    Es = np.array(Es[1:])

    def phases(xs):
        chunks = np.array_split(np.asarray(xs), max(1, min(len(xs), procs * 16)))
        with Pool(procs) as pool:
            return np.concatenate([np.array(c) for c in pool.map(_phi_chunk, [(c, rtol) for c in chunks if len(c)])])

    phi = phases(Es)
    # Φ is increasing (checked on fine samples: min local rate > 0); unwrap with every step taken in [0, 2π) and
    # refine any interval whose step is ≥ π (ambiguous under aliasing) by inserting midpoints, up to 8 rounds
    refined = 0
    for _ in range(8):
        d = np.mod(np.diff(phi), 2 * math.pi)
        bad = np.nonzero(d >= math.pi)[0]
        if len(bad) == 0:
            break
        mids = 0.5 * (Es[bad] + Es[bad + 1])
        pm = phases(mids)
        Es = np.insert(Es, bad + 1, mids)
        phi = np.insert(phi, bad + 1, pm)
        refined += len(bad)
    d = np.mod(np.diff(phi), 2 * math.pi)
    assert d.max() < math.pi, f"unresolved ambiguous steps remain: max step {d.max():.3f}"
    Phi = phi[0] + np.concatenate([[0.0], np.cumsum(d)])
    sc = np.array([_sc(E) for E in Es])
    R = Phi - sc
    dR = np.abs(np.diff(R))
    m_lo = math.ceil((Phi[0] - ALPHA) / (2 * math.pi))
    m_hi = math.floor((Phi[-1] - ALPHA) / (2 * math.pi))
    targets = ALPHA + 2 * math.pi * np.arange(m_lo, m_hi + 1)
    idx = np.searchsorted(Phi, targets) - 1
    jobs = [(Es[i], Es[i + 1], Phi[i], Phi[i + 1], tg, rtol) for i, tg in zip(idx, targets)]
    with Pool(procs) as pool:
        levels = np.array(pool.map(_refine, jobs, chunksize=64))
    return np.sort(levels), dict(n_samples=int(len(Es)), refined_midpoints=int(refined), max_step=float(d.max()),
                                 R_range=[float(R.min()), float(R.max())], max_dR=float(dR.max()), m_range=[m_lo, m_hi])


def _refine(job):
    a, b, pa, pb, tgt, rtol = job

    # continuous branch around the bracket: unwrap relative to the linear interpolation of the samples
    def g(E):
        lin = pa + (pb - pa) * (E - a) / (b - a)
        v = F.phase(E, rtol=rtol)[0]
        v = v + 2 * math.pi * round((lin - v) / (2 * math.pi))
        return v - tgt

    fa, fb = pa - tgt, pb - tgt
    for _ in range(60):
        m = (a * fb - b * fa) / (fb - fa) if fb != fa else 0.5 * (a + b)
        if not (a < m < b):
            m = 0.5 * (a + b)
        fm = g(m)
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
        if b - a < 1e-11 * max(1.0, a) or abs(fm) < 1e-10:
            return m
    return 0.5 * (a + b)


if __name__ == "__main__":
    res, out, procs = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
    t = time.time()
    E_lev, info = build(res, procs)
    t_lev = 2 * math.pi * E_lev
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, f"C2_res{res}.npy")
    np.save(p, t_lev)
    meta = dict(id="C2", res=res, n=int(len(t_lev)), t_min=float(t_lev[0]), t_max=float(t_lev[-1]),
                sha256=hashlib.sha256(open(p, "rb").read()).hexdigest(),
                params=dict(alpha=ALPHA, eta="1/2pi", identification="t = 2 pi E (BK11 eq. 5.3)", T_MAX=T_MAX,
                            rtol={1: 1e-11, 2: 1e-12}[res], seconds=time.time() - t, **info))
    json.dump(meta, open(os.path.join(out, f"C2_res{res}.json"), "w"), indent=1)
    print(json.dumps(meta), flush=True)

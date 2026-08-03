"""Khinchin Landscape — grid-offset audit (finding, spec sec 3.2).

The spec offsets the sample grid by xi = 1/phi:  alpha_i = (i + (sqrt5-1)/2)/N.
Every such alpha_i satisfies an integer quadratic (2*N*alpha - 2i + 1)^2 = 5, i.e.
EVERY column is a quadratic irrational in Q(sqrt5) -- eventually-periodic CF, the
measure-zero exceptional set, not a generic point. This script measures whether
that bites at the depths we actually render, against matched alternatives.

    python3 grid_audit.py            # production params: D=2048, B=8192
"""
import math
import multiprocessing as mp
import os
import sys

import numpy as np

import kcore as kc

N_COLS = 8192
D = 2048
B = 8192
NGRID = 65536          # the production N whose lattice geometry we mimic


def _offsets(B):
    import mpmath
    mpmath.mp.dps = int(B * 0.302) + 40
    two_B = mpmath.mpf(2) ** B
    return {
        'golden_phi':  (math.isqrt(5 << (2 * B)) - (1 << B)) // 2,
        'pi_m3':       int(mpmath.floor((mpmath.pi - 3) * two_B)),
        'cbrt2_m1':    int(mpmath.floor((mpmath.cbrt(2) - 1) * two_B)),
        'ln2':         int(mpmath.floor(mpmath.log(2) * two_B)),
    }


_S = {}


def _init(mode, xi, seed):
    _S.update(mode=mode, xi=xi, seed=seed, Q=NGRID << B, one=1 << B,
              limit=kc.horizon_limit(B))


def _col(i):
    if _S['mode'] == 'jitter':
        # stratified: one uniform random real inside cell i, seeded & reproducible
        rng = np.random.default_rng((_S['seed'], i))
        frac = 0
        for _ in range(B // 32):
            frac = (frac << 32) | int(rng.integers(0, 1 << 32))
        P, Q = (i << B) + (frac % (1 << B)), _S['Q']
    elif _S['mode'] == 'random':
        rng = np.random.default_rng((_S['seed'], i))
        frac = 0
        for _ in range(B // 32):
            frac = (frac << 32) | int(rng.integers(0, 1 << 32))
        P, Q = max(1, frac % _S['one']), _S['one']
    else:
        P, Q = (i << B) + _S['xi'], _S['Q']
    quots, reason = kc.cf_quotients(P, Q, D, _S['limit'])
    v = np.full(D, np.nan, dtype=np.float32)
    v[:len(quots)] = [kc.ilog2(a) for a in quots]
    return v


def measure(name, mode, xi, seed=20260803, workers=22):
    cols = np.linspace(0, NGRID - 1, N_COLS).astype(int)
    with mp.Pool(workers, initializer=_init, initargs=(mode, xi, seed)) as pool:
        M = np.array(pool.map(_col, cols.tolist(), chunksize=32)).T
    S = np.nancumsum(np.nan_to_num(M, nan=0.0), axis=0) / np.arange(1, D + 1)[:, None]
    out = {'name': name}
    for n in (512, 2048):
        s = S[n - 1]
        rng = np.random.default_rng(7)
        bs = np.array([s[rng.integers(0, len(s), len(s))].mean() for _ in range(600)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        out[n] = dict(mean=float(s.mean()), lo=float(lo), hi=float(hi),
                      medK=float(2 ** np.median(s)),
                      covers=bool(lo <= kc.LOG2_K0 <= hi),
                      relK=float((2 ** np.median(s) - kc.KHINCHIN_K0) / kc.KHINCHIN_K0))
    out['drift'] = [float(np.nanmean(M[n - 1])) for n in (16, 128, 512, 1024, 2048)]
    return out


def main():
    offs = _offsets(B)
    cands = [('golden_phi (spec)', 'lattice', offs['golden_phi']),
             ('pi_m3 offset', 'lattice', offs['pi_m3']),
             ('cbrt2_m1 offset', 'lattice', offs['cbrt2_m1']),
             ('ln2 offset', 'lattice', offs['ln2']),
             ('stratified jitter', 'jitter', 0),
             ('random reals', 'random', 0)]
    print(f'grid-offset audit: {N_COLS} columns, D={D}, B={B}, lattice N={NGRID}')
    print(f'GK target log2 K0 = {kc.LOG2_K0:.6f}\n')
    print(f'{"candidate":22s} {"medK@512":>9s} {"medK@2048":>10s} {"rel@2048":>9s} '
          f'{"CI@2048 covers K0":>18s}   E[log2 a] at n=16,128,512,1024,2048')
    rows = []
    for name, mode, xi in cands:
        r = measure(name, mode, xi)
        rows.append(r)
        d = ' '.join(f'{v:.3f}' for v in r['drift'])
        print(f'{name:22s} {r[512]["medK"]:9.4f} {r[2048]["medK"]:10.4f} '
              f'{r[2048]["relK"]*100:+8.2f}% {str(r[2048]["covers"]):>18s}   {d}', flush=True)
    import json
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'validation'),
                exist_ok=True)
    json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'validation', 'grid_offset_audit.json'), 'w'),
              indent=2)
    return rows


if __name__ == '__main__':
    main()

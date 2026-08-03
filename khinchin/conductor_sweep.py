"""Is the golden-grid bias conductor-dependent (arithmetic) or a finite-size effect?

Review reproduced both original numbers and reconciled them via N: the golden-grid
columns are the surds (2i-1+sqrt5)/2N, whose map to sqrt5 has determinant 2N, not
+-1 -- so Serret does not apply, they are NOT tail-equivalent to phi, and each N
selects a different family of orders of conductor ~2N in Q(sqrt5), with its own
period-quotient statistics. Sketch-grade, not certified.

That sketch makes a falsifiable prediction this script tests. A finite-size effect
must vary SMOOTHLY with N: adjacent N=4094..4098 would agree. An arithmetic effect
need not: adjacent N can differ by more than the sampling error.

    python3 conductor_sweep.py
"""
import json
import math
import multiprocessing as mp
import os

import numpy as np

import kcore as kc

B, D = 2048, 512
HERE = os.path.dirname(os.path.abspath(__file__))
DEPTHS = (200, 512)

NEIGHBOURS = [4094, 4095, 4096, 4097, 4098]
SPREAD = [3072, 4093, 4096, 6144,          # the four review reported
          2048, 3067, 4000, 4620, 5000, 6151, 8192]

_S = {}


def _init(xi, Q, lim):
    _S.update(xi=xi, Q=Q, lim=lim)


def _col(i):
    q, _ = kc.cf_quotients((i << B) + _S['xi'], _S['Q'], D, _S['lim'])
    v = np.full(D, np.nan, dtype=np.float64)
    v[:len(q)] = [kc.ilog2(a) for a in q]
    return v


def measure(N, kind, workers=22):
    xi, Q = kc.grid_numerators(N, B, kind)
    with mp.Pool(workers, initializer=_init, initargs=(xi, Q, kc.horizon_limit(B))) as pool:
        M = np.array(pool.map(_col, range(N), chunksize=64)).T
    S = np.nancumsum(M, 0) / np.arange(1, D + 1)[:, None]
    out = {}
    for d in DEPTHS:
        s = S[d - 1]
        med = 2 ** np.median(s)
        # SE of the median of a roughly-normal sample
        se_log2 = 1.2533 * s.std() / math.sqrt(len(s))
        out[d] = dict(medK=float(med),
                      pct=float((med - kc.KHINCHIN_K0) / kc.KHINCHIN_K0 * 100),
                      se_pct=float(se_log2 * math.log(2) * 100))
    return out


def factor(n):
    f, d = {}, 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return '·'.join(f'{p}^{e}' if e > 1 else f'{p}' for p, e in sorted(f.items()))


def run(Ns, title):
    print(f'\n=== {title} ===')
    print(f'{"N":>6} {"factorisation":>16} | {"golden d200":>12} {"golden d512":>12} '
          f'| {"pi d200":>9} {"pi d512":>9} | {"SE d512":>8}')
    rows = []
    for N in Ns:
        g, p = measure(N, 'golden_phi'), measure(N, 'pi_m3')
        rows.append(dict(N=N, factorisation=factor(N), golden=g, pi=p))
        print(f'{N:6d} {factor(N):>16} | {g[200]["pct"]:+11.2f}% {g[512]["pct"]:+11.2f}% '
              f'| {p[200]["pct"]:+8.2f}% {p[512]["pct"]:+8.2f}% | {g[512]["se_pct"]:7.2f}%',
              flush=True)
    return rows


def main():
    out = {'config': dict(B=B, D=D, depths=list(DEPTHS))}
    out['neighbours'] = run(NEIGHBOURS, 'DISCRIMINATOR: adjacent N (finite-size would agree)')
    out['spread'] = run(SPREAD, 'SPREAD: N of differing factorisation')

    g = [r['golden'][512]['pct'] for r in out['neighbours']]
    se = max(r['golden'][512]['se_pct'] for r in out['neighbours'])
    out['verdict'] = dict(
        neighbour_range_pct=max(g) - min(g), typical_se_pct=se,
        smooth_finite_size_excluded=bool((max(g) - min(g)) > 4 * se))
    json.dump(out, open(os.path.join(HERE, 'validation', 'conductor_sweep.json'), 'w'),
              indent=2, default=float)
    print(f'\nAdjacent-N spread at depth 512: {max(g)-min(g):.2f}% against a typical '
          f'median SE of {se:.2f}%.')
    print('A smooth finite-size effect is EXCLUDED.' if out['verdict']['smooth_finite_size_excluded']
          else 'Adjacent N agree within noise: finite-size NOT excluded.')
    return out


if __name__ == '__main__':
    main()

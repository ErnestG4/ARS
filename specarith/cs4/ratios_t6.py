"""n = 6 stage (c), round 74/75 (l6/N6_STAGE_C_BOUND.md): the ratios-definition 6-point function, i.e. ratios_t5.Model,
whose construction is general in n, at n = 6, and its U(N) pointwise gate against det[S(x_i − x_j)] (the n = 6 form of
`ratios_t5 ugate`). No ζ value is read before this gate passes.

  python ratios_t6.py ugate OUT.json [NPTS]    U(N), N = 10 and 50: ρ₆ by the construction vs the determinant, NPTS
                                               configurations each: spread over [0, 6), near-coincident, and 3 + 3 at
                                               r = 5 and 9 (N = 50 only for r = 9)
  python ratios_t6.py timing                   wall time of one batched ρ₆ evaluation (U and ζ at PMAX 100)
"""
import json
import math
import sys
import time

import numpy as np

import ratios_t5 as T5
import route_a_zeta as RA

GATE_ABS, GATE_REL = 1e-12, 1e-6          # pointwise; the configurations keep |ρ₆| ≳ 1e-3, so the relative part
                                           # decides (round 75: the first version's [0, 2.4] points had ρ₆ ~ 1e-11 under
                                           # an absolute 1e-9 and could not fail; stopped before any result)


def configs(rng, n_pts, near=False, r=None):
    """6 points with ρ₆ of order 0.01–1: spread over [0, 6) (spacings ~1), or, with r, the stage's 3 + 3 geometry (three
    in [0, 4), three in [r, r + 4)). near: one near-coincident pair (1e-3 apart) per configuration."""
    if r is None:
        d = np.sort(rng.uniform(0, 6.0, (n_pts, 6)), axis=1)
    else:
        d = np.concatenate([np.sort(rng.uniform(0, 4, (n_pts, 3)), axis=1),
                            r + np.sort(rng.uniform(0, 4, (n_pts, 3)), axis=1)], axis=1)
    if near:
        k = rng.integers(0, 2, n_pts)
        d[np.arange(n_pts), k + 1] = d[np.arange(n_pts), k] + 1e-3
        d = np.sort(d, axis=1)
    return [d[:, j] for j in range(6)]


def ugate(out, npts=8):
    rng = np.random.default_rng([20261022, 75, 6])
    rows = []
    for N in (10, 50):
        M = T5.Model("U", N)
        for near, r in ((False, None), (True, None), (False, 5.0), (False, 9.0)):
            if r is not None and r + 4 > N / 2:
                continue
            ds = configs(rng, npts, near, r)
            t = time.time()
            mine = np.real(M.rho(ds))
            wall = time.time() - t
            det = RA.sine_rho(ds, N)
            diff = np.abs(mine - det)
            ok = bool(np.all(diff <= GATE_ABS + GATE_REL * np.abs(det)))
            rows.append(dict(N=N, near=near, r=r, n=npts, max_rel_diff=float((diff / np.abs(det)).max()), max_abs_diff=float(diff.max()), max_abs_det=float(np.abs(det).max()),
                             min_abs_det=float(np.abs(det).min()),
                              wall_s=round(wall, 1), PASS=ok))
            print(rows[-1], flush=True)
    res = dict(rows=rows, tol=dict(abs=GATE_ABS, rel=GATE_REL), PASS=all(r["PASS"] for r in rows))
    json.dump(res, open(out, "w"), indent=1)
    print("n = 6 U(N) pointwise gate:", "PASS" if res["PASS"] else "FAIL", flush=True)
    return 0 if res["PASS"] else 1


def largen(out):
    """Diagnostic for stage (b) G-b1 (not a gate): the construction's ρ₆ in the 3 + 3 geometry against the determinant at
    large N and separated clusters (r = 20, 100, 1000), N = 10³, 10⁴, 10⁵. Reports the relative difference; decides
    which N the U(N) gate can use without the jets' large-L cancellations dominating."""
    rng = np.random.default_rng([20261022, 75, 7])
    rows = []
    for N in (1000, 10_000, 100_000):
        M = T5.Model("U", N)
        for r in (20.0, 100.0, 1000.0):
            if r + 4 > N / 2:
                continue
            ds = configs(rng, 4, False, r)
            mine = np.real(M.rho(ds))
            det = RA.sine_rho(ds, N)
            rows.append(dict(N=N, r=r, max_rel_diff=float((np.abs(mine - det) / np.abs(det)).max()),
                             min_abs_det=float(np.abs(det).min())))
            print(rows[-1], flush=True)
    json.dump(dict(rows=rows), open(out, "w"), indent=1)
    return 0


def timing():
    rng = np.random.default_rng(1)
    ds = configs(rng, 4)
    for kind, kw in (("U", dict(L=50)), ("zeta", dict(L=RA.ell_of(4.77e7), pmax=100))):
        M = T5.Model(kind, kw["L"], pmax=kw.get("pmax"))
        t = time.time()
        v = M.rho(ds)
        print(kind, "4 configurations:", round(time.time() - t, 1), "s", np.real(v)[:2], flush=True)
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "ugate":
        sys.exit(ugate(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8))
    if sys.argv[1] == "largen":
        sys.exit(largen(sys.argv[2]))
    if sys.argv[1] == "timing":
        sys.exit(timing())

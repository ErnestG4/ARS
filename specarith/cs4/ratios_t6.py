"""n = 6 stage (c), round 74/75 (l6/N6_STAGE_C_BOUND.md): the ratios-definition 6-point function, i.e. ratios_t5.Model,
whose construction is general in n, at n = 6, and its U(N) pointwise gate against det[S(x_i − x_j)] (the n = 6 form of
`ratios_t5 ugate`). No ζ value is read before this gate passes.

  python ratios_t6.py ugate OUT.json [NPTS]    U(N), N = 10 and 50: ρ₆ by the construction vs the determinant, NPTS
                                               configurations each: spread over [0, 6), near-coincident, and 3 + 3 at
                                               r = 5 and 9 (N = 50 only for r = 9)
  python ratios_t6.py threshold OUT.json        round 76: double vs high-precision path at min separation = DELTA_TH
  python ratios_t6.py ugate OUT.json 8 PROCS    round 76 re-run: the gate unchanged, evaluated through rho_auto
  python ratios_t6.py timing                   wall time of one batched ρ₆ evaluation (U and ζ at PMAX 100)
"""
import json
import math
import sys
import time

import numpy as np

import ratios_hp as HP
import ratios_t5 as T5
import route_a_zeta as RA

GATE_ABS, GATE_REL = 1e-12, 1e-6          # pointwise; the configurations keep |ρ₆| ≳ 1e-3, so the relative part
                                           # decides (round 75: the first version's [0, 2.4] points had ρ₆ ~ 1e-11 under
                                           # an absolute 1e-9 and could not fail; stopped before any result)


# ---------------------------------------------------------------- round 76: the high-precision path and the guard
def min_sep(ds):
    D = np.stack([np.atleast_1d(np.asarray(d, float)) for d in ds], -1)
    X = np.abs(D[..., :, None] - D[..., None, :]) + np.eye(D.shape[-1]) * 1e300
    return X.min(axis=(-1, -2))


def guard(ds):
    """Refuse double-precision evaluation of any configuration below the declared threshold (round 76)."""
    m = min_sep(ds)
    if np.any(m < HP.DELTA_TH):
        raise RuntimeError(f"ratios_t6.guard: {int(np.sum(m < HP.DELTA_TH))} configuration(s) below DELTA_TH = "
                           f"{HP.DELTA_TH} (min separation {float(m.min()):.3g}); double evaluation refused")


def _hp_one(job):
    kind, L, pmax, d = job
    return complex(HP.ModelMP(kind, L, pmax).rho(list(d)))


def rho_auto(model, ds, procs=1):
    """ρ_n by the construction: double (ratios_t5.Model, guarded) at or above DELTA_TH, mpmath below."""
    D = np.stack([np.atleast_1d(np.asarray(d, float)) for d in ds], -1)
    low = min_sep(ds) < HP.DELTA_TH
    out = np.empty(D.shape[0], complex)
    if np.any(~low):
        hi = [D[~low, j] for j in range(D.shape[1])]
        guard(hi)
        out[~low] = model.rho(hi)
    if np.any(low):
        jobs = [(model.kind, float(model.L), getattr(model, "pmax", None), D[i]) for i in np.where(low)[0]]
        if procs > 1:
            from multiprocessing import Pool
            with Pool(min(procs, len(jobs))) as pool:
                vals = pool.map(_hp_one, jobs, chunksize=1)
        else:
            vals = [_hp_one(j) for j in jobs]
        out[low] = vals
    return out, low


def threshold_check(out, procs=8):
    """Path agreement at the threshold (declared before running): configurations whose smallest separation is exactly
    DELTA_TH, evaluated by both paths, must agree to 1e-12 + 1e-7·|hp| (10× tighter than the gate). U(N) at N = 10 and
    50, 4 configurations each."""
    rng = np.random.default_rng([20261023, 76, 1])
    rows = []
    for N in (10, 50):
        M = T5.Model("U", N)
        d = np.sort(rng.uniform(0, 6.0, (4, 6)), axis=1)
        for i in range(4):                                           # widen every gap to ≥ 0.3, then set one to DELTA_TH
            g = np.maximum(np.diff(d[i]), 0.3)
            k = rng.integers(0, 5)
            g[k] = HP.DELTA_TH
            d[i] = np.concatenate([[d[i, 0]], d[i, 0] + np.cumsum(g)])
        ds = [d[:, j] for j in range(6)]
        dbl = np.real(M.rho(ds))
        from multiprocessing import Pool
        with Pool(min(procs, 4)) as pool:
            hp = np.real(np.array(pool.map(_hp_one, [("U", N, None, d[i]) for i in range(4)], chunksize=1)))
        diff = np.abs(dbl - hp)
        ok = bool(np.all(diff <= 1e-12 + 1e-7 * np.abs(hp)))
        rows.append(dict(N=N, min_sep=min_sep(ds).tolist(), double=dbl.tolist(), hp=hp.tolist(),
                         max_abs_diff=float(diff.max()), max_rel_diff=float((diff / np.abs(hp)).max()), PASS=ok))
        print(rows[-1], flush=True)
    res = dict(DELTA_TH=HP.DELTA_TH, DPS=HP.DPS, rows=rows, PASS=all(r["PASS"] for r in rows))
    json.dump(res, open(out, "w"), indent=1)
    print("threshold path agreement:", "PASS" if res["PASS"] else "FAIL", flush=True)
    return 0 if res["PASS"] else 1


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


def ugate(out, npts=8, procs=1):
    rng = np.random.default_rng([20261022, 75, 6])
    rows = []
    for N in (10, 50):
        M = T5.Model("U", N)
        for near, r in ((False, None), (True, None), (False, 5.0), (False, 9.0)):
            if r is not None and r + 4 > N / 2:
                continue
            ds = configs(rng, npts, near, r)
            t = time.time()
            mine, low = rho_auto(M, ds, procs)
            mine = np.real(mine)
            wall = time.time() - t
            det = RA.sine_rho(ds, N)
            diff = np.abs(mine - det)
            ok = bool(np.all(diff <= GATE_ABS + GATE_REL * np.abs(det)))
            rows.append(dict(N=N, near=near, r=r, n=npts, n_high_precision=int(low.sum()), max_rel_diff=float((diff / np.abs(det)).max()), max_abs_diff=float(diff.max()), max_abs_det=float(np.abs(det).max()),
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
        sys.exit(ugate(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8, int(sys.argv[4]) if len(sys.argv) > 4 else 1))
    if sys.argv[1] == "threshold":
        sys.exit(threshold_check(sys.argv[2]))
    if sys.argv[1] == "largen":
        sys.exit(largen(sys.argv[2]))
    if sys.argv[1] == "timing":
        sys.exit(timing())

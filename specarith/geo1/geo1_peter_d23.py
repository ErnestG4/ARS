"""GEO1 Peter seal: generator SDs, D23 and witness powers on the GPU (Will, 2026-10-31: "D23 on the 4090"). CuPy.
Generators as in geo1_peter_seal.py (planted Euler-product series with random per-prime-power shifts and i.i.d. residual
noise; matched-marginal independent-lag null; planted without the p = 3 factor). Each replicate is a fresh-window-length
series; the statistics are the seal's 45 (ratio r ≠ 0; γ(0); raw γ(r ≠ 0)).

  python geo1_peter_d23.py sd  DEV_NPZ PRED_JSON OUT_JSON            R = 500 planted replicates at the fresh N and at
                                                                       the dev k = 23 window's N (generator calibration)
  python geo1_peter_d23.py d23 DEV_NPZ PRED_JSON TOL_JSON OUT_JSON    R = 2000 each: planted (pass rates against the
                                                                       exact planted values; SE-only and full tolerance),
                                                                       null and planted-without-3 (fail rates)
  python geo1_peter_d23.py d23n DEV_NPZ PRED_JSON TOL_JSON OUT_JSON   the same with noise-matched planted noise
                                                                       ξ' = 1 + c(ξ − 1), c = 1/median(generator SD /
                                                                       real block-jackknife SE at the dev k = 23 window)

Addition before the seal (2026-10-31, after the sd and d23 runs): the as-built generator is smoother than the real data
(generator SD / real block-jackknife SE 0.30–0.84 at the dev k = 23 window), so its D23 is optimistic. d23n is the stress
variant; seal gate fixed before it runs: d23 SE-only rates ≥ 0.95 AND d23n full-tolerance rates ≥ 0.95 (all families);
d23n SE-only rates reported.
"""
import json
import sys
import time

import cupy as cp
import numpy as np

import geo1_peter_seal as S

KER = cp.RawKernel(r'''
extern "C" __global__ void gen(const double* tab, const int* off, const int* q, const int* sh, const int np_,
                               const double* pool, const int* idx, double* x, const int L) {
  int i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i >= L) return;
  double v = pool[idx[i]];
  for (int k = 0; k < np_; k++) v *= tab[off[k] + (i + sh[k]) % q[k]];
  x[i] = v - 1.0;
}''', "gen")
SEED_SD, SEED_D23 = 20261105, 20261106
R_SD, R_D23 = 500, 2000
N_DEV23 = (10 ** 6 - S.RMAX) - int(round(10 ** (23 / 4))) + 1


class Gen:
    def __init__(self, tabs, pool):
        self.qs = np.array([q for q, _ in tabs], np.int64)
        self.np_ = len(tabs)
        cat = np.concatenate([t for _, t in tabs]) if tabs else np.zeros(1)
        off = np.concatenate([[0], np.cumsum(self.qs)[:-1]]).astype(np.int32) if tabs else np.zeros(1, np.int32)
        self.tab, self.off = cp.asarray(cat), cp.asarray(off)
        self.q = cp.asarray(self.qs.astype(np.int32) if tabs else np.ones(1, np.int32))
        self.pool = cp.asarray(pool)
        self.M = len(pool)

    def series(self, L, rng, rs, x):
        sh = rng.integers(0, self.qs).astype(np.int32) if self.np_ else np.zeros(1, np.int32)
        idx = rs.randint(0, self.M, size=L, dtype=cp.int32)
        KER(((L + 255) // 256,), (256,), (self.tab, self.off, self.q, cp.asarray(sh), np.int32(self.np_), self.pool,
                                         idx, x, np.int32(L)))


def replicate_stats(gen, R, N, lags, seed):
    rng = np.random.default_rng(seed)
    rs = cp.random.RandomState(seed)
    L = N + S.RMAX
    x = cp.empty(L, cp.float64)
    out = np.empty((R, S.NSTAT))
    for i in range(R):
        gen.series(L, rng, rs, x)
        g = (cp.stack([x[:N] @ x[r:r + N] for r in lags]) / N).get()
        gd = dict(zip(lags, g.tolist()))
        out[i] = S.stat_vector(dict(gamma=gd, ratio={r: gd[r] / gd[0] for r in lags if r}), lags)
    return out


def setup(dev_npz, pred_json):
    pred = json.load(open(pred_json))
    lags = S.lags_of(pred)
    resp, alp = S.pools(dev_npz)
    return pred, lags, resp, alp


def sd(dev_npz, pred_json, out):
    t0 = time.time()
    pred, lags, resp, alp = setup(dev_npz, pred_json)
    g = Gen(S.tables(), resp)
    NF = (S.T2 - S.RMAX) - (S.T1 + 1) + 1
    a = replicate_stats(g, R_SD, NF, lags, SEED_SD)
    b = replicate_stats(g, R_SD, N_DEV23, lags, SEED_SD + 1)
    ex = S.planted_exact(lags, S.tables(), float(np.mean(resp ** 2)))
    exv = S.stat_vector(dict(gamma=ex, ratio={r: ex[r] / ex[0] for r in lags if r}), lags)
    res = dict(R=R_SD, seeds=[SEED_SD, SEED_SD + 1], N_fresh=NF, N_dev23=N_DEV23, names=S.stat_names(lags),
               sd_fresh=a.std(0, ddof=1).tolist(), sd_dev23=b.std(0, ddof=1).tolist(), planted_exact=exv,
               bias_over_sd_fresh=((a.mean(0) - exv) / a.std(0, ddof=1)).tolist(),
               resid_pool_var=float(resp.var()), alpha_pool_var=float(alp.var()), pool_size=len(resp))
    S.dump(res, out)
    open(out + ".timing", "w").write(f"wall_s {time.time() - t0:.1f}\n")
    print("resid pool var", res["resid_pool_var"], "alpha pool var", res["alpha_pool_var"])
    for j, n in enumerate(res["names"]):
        print(f"{n:>10} exact {exv[j]:9.5f} sd_fresh {res['sd_fresh'][j]:.2e} sd_dev23 {res['sd_dev23'][j]:.2e} "
              f"bias/sd {res['bias_over_sd_fresh'][j]:+.2f}")
    return 0


def d23(dev_npz, pred_json, tol_json, out, noise_matched=False):
    t0 = time.time()
    pred, lags, resp, alp = setup(dev_npz, pred_json)
    T = json.load(open(tol_json))
    c = 1.0
    if noise_matched:
        c = 1.0 / float(np.median(T["generator_vs_real_at_dev23"]["ratio_gen_over_real"]))
        resp = 1.0 + c * (resp - 1.0)
        seed_off = 10
    else:
        seed_off = 0
    tol, tse, pv = np.array(T["tol"]), np.array(T["tol_se_only"]), np.array(T["pred"])
    NF = T["N_fresh"]
    tabs = S.tables()
    ex = S.planted_exact(lags, tabs, float(np.mean(resp ** 2)))
    exv = np.array(S.stat_vector(dict(gamma=ex, ratio={r: ex[r] / ex[0] for r in lags if r}), lags))
    tabs3 = [x for x in tabs if x[0] != 81]
    ex3 = S.planted_exact(lags, tabs3, float(np.mean(resp ** 2)))
    exv3 = S.stat_vector(dict(gamma=ex3, ratio={r: ex3[r] / ex3[0] for r in lags if r}), lags)
    P = slice(0, 22)
    Q = slice(22, 45)
    pl = replicate_stats(Gen(tabs, resp), R_D23, NF, lags, SEED_D23 + seed_off)
    nu = replicate_stats(Gen([], alp), R_D23, NF, lags, SEED_D23 + seed_off + 1)
    d3 = replicate_stats(Gen(tabs3, resp), R_D23, NF, lags, SEED_D23 + seed_off + 2)
    sd_dev = replicate_stats(Gen(tabs, resp), R_SD, N_DEV23, lags, SEED_D23 + seed_off + 3).std(0, ddof=1) \
        if noise_matched else None

    def rates(x, ref, t):
        ok = np.abs(x - ref) <= t
        return ok, dict(primary=float(ok[:, P].all(1).mean()), secondary=float(ok[:, Q].all(1).mean()),
                        joint=float(ok.all(1).mean()))
    ok_se, r_se = rates(pl, exv, tse)
    ok_f, r_f = rates(pl, exv, tol)
    nok, _ = rates(nu, pv, tol)
    dok, _ = rates(d3, exv, tol)
    res = dict(R=R_D23, seeds=[SEED_D23 + seed_off + k for k in range(4 if noise_matched else 3)], names=T["names"],
               N_fresh=NF, tol_sha256=S.sha(tol_json), noise_c=c,
               sd_dev23_over_real=None if sd_dev is None else
               (sd_dev / np.array(T["generator_vs_real_at_dev23"]["real_block_jk_se"])).tolist(),
               planted=dict(exact=exv.tolist(),
                            pass_rate={**{k + "_se_only": v for k, v in r_se.items()},
                                       **{k + "_full": v for k, v in r_f.items()}},
                            pass_rate_per_stat_se_only=ok_se.mean(0).tolist(),
                            max_abs_z=float(np.max(np.abs(pl - exv) / pl.std(0, ddof=1)))),
               null=dict(fail_rate_per_stat=(1 - nok.mean(0)).tolist(),
                         family_fail_rate=dict(primary=float((~nok[:, P]).any(1).mean()),
                                               secondary=float((~nok[:, Q]).any(1).mean())),
                         mean_stat=nu.mean(0).tolist()),
               drop3=dict(exact=exv3, fail_rate_per_stat=(1 - dok.mean(0)).tolist(),
                          family_fail_rate=dict(primary=float((~dok[:, P]).any(1).mean()),
                                                secondary=float((~dok[:, Q]).any(1).mean()))))
    S.dump(res, out)
    open(out + ".timing", "w").write(f"wall_s {time.time() - t0:.1f}\n")
    print("planted pass rates:", res["planted"]["pass_rate"])
    print("null family fail rates:", res["null"]["family_fail_rate"], "| drop-3:", res["drop3"]["family_fail_rate"])
    for j, n in enumerate(T["names"]):
        print(f"{n:>10} planted pass {ok_se.mean(0)[j]:.4f}  null fail {1 - nok.mean(0)[j]:.3f}  "
              f"drop3 fail {1 - dok.mean(0)[j]:.3f}")
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "sd":
        sys.exit(sd(*sys.argv[2:5]))
    sys.exit(d23(*sys.argv[2:6], noise_matched=sys.argv[1] == "d23n"))

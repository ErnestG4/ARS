"""Route (a) read: the estimator, its error bar, the goodness-of-fit red path and the decision rule, as code
(fortieth round). Nothing here reads an F3 file unless `read` is called, which needs the sealed seal (fails closed).

Model (route_a_zeta.json, tagged `route-a-prediction`): on the window s ≤ S_MAX = 1.8,
    p_μ(s) = p_sine(s) + μ·Δp_f(s),
p_sine = Phase 2's Fredholm table (ph2lib.spacing_tables), Δp_f = the barycentric interpolant through file f's 25
Chebyshev–Lobatto values (route_a_zeta.cheb_interp, the declared interpolant), at f's zero-weighted mean height.

Estimator (per file): conditional maximum likelihood on the window (Phase 2's WindowFit, PA1):
    ℓ(μ) = Σ_{s_k ≤ S_MAX} [log(1 + μ ρ_k) − log(1 + μ φ)],   ρ_k = Δp(s_k)/p_sine(s_k),   φ = ∫Δp / ∫p_sine (window),
with p_sine and Δp evaluated at max(s, S_TINY) (Δp/p_sine is flat below 0.01 to 1e-4 relative; P(s < S_TINY) ≈ 1.4e-7).
Error bar: moving-block bootstrap of μ̂ (Phase 2's series form), block length BLOCK spacings, B_BOOT replicates.

Goodness of fit (fortieth round red path): binned χ² of the in-window spacings against p_μ̂ (conditional on the
window), GOF_BINS equal bins on [0, S_MAX]; per-file threshold from the CUE calibration (GOF_THRESHOLD). A file over
its threshold reads MODEL MISFIT.

Rule (fortieth round draft; Stage 2 analogue):
    weights w_f ∝ n_f, the pre-data spacing count N̄(t1) − N̄(t0) of the declared height range (exact θ);
    μ̂_pool = Σ w_f μ̂_f,  SE_pool = (Σ w_f² SE_f²)^{1/2}  (files are disjoint height ranges: independent);
    RESOLVABLE  iff 2·SE_pool ≤ 0.25;
    PASS        iff RESOLVABLE and |μ̂_pool − 1| ≤ 2·SE_pool + δμ_sys and at least 4 of 5 files have |μ̂_f − 1| ≤ 3·SE_f;
    FAIL        iff RESOLVABLE and not PASS;   MODEL MISFIT reported beside the verdict for any file over its GoF threshold;
    always reported: μ̂_pool ± 2·SE_pool (and per file).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
import ph2lib  # noqa: E402

PRED = os.path.join(HERE, "results", "route_a_zeta.json")
S_MAX = 1.8
S_TINY = 0.005
DMU_SYS = 2e-4                 # thirty-eighth round
RESOLVE_2SE = 0.25             # fortieth round
K_POOL, K_FILE, MIN_FILES = 2.0, 3.0, 4
GOF_BINS = 36                  # width 0.05
BLOCK = None                   # declared from the CUE calibration (route_a_calib.py), before any real-zero check
B_BOOT = 200
GOF_THRESHOLD = None           # per file, declared from the CUE calibration
F3 = {"zeros_15146000.dat": (15_146_000, 17_246_000),
      "zeros_25646000.dat": (25_646_000, 27_746_000),
      "zeros_248246000.dat": (248_246_000, 250_346_000),
      "zeros_2373446000.dat": (2_373_446_000, 2_375_546_000),
      "zeros_10639046000.dat": (10_639_046_000, 10_641_146_000)}

_PSINE = None


def p_sine():
    global _PSINE
    if _PSINE is None:
        _PSINE = ph2lib.spacing_tables(S=6.0, M=160, m=40, abars=())[0]
    return _PSINE


def cheb_interp(vals, s):
    import route_a_zeta
    return route_a_zeta.cheb_interp(vals, s)


def spacing_count(f):
    """Pre-data n_f = N̄(t1) − N̄(t0), N̄(t) = θ(t)/π + 1 (exact θ, mpmath)."""
    import mpmath as mp
    t0, t1 = F3[f]
    with mp.workdps(30):
        return float((mp.siegeltheta(t1) - mp.siegeltheta(t0)) / mp.pi)


def weights():
    n = {f: spacing_count(f) for f in F3}
    tot = sum(n.values())
    return {f: n[f] / tot for f in F3}, n


class MuFit(ph2lib.WindowFit):
    """ph2lib.WindowFit with c ↔ μ, a_k ↔ Δp, p0 ↔ p_sine (single model, no N_eff): fit/loglik/compress and the series
    bootstrap are inherited unchanged."""

    def __init__(self, dp_nodes, sc=S_MAX):
        self.sc = sc
        self.dp_nodes = np.asarray(dp_nodes, float)
        g, w = ph2lib._window_grid(sc)
        ps = p_sine()
        self.F0 = float(np.sum(w * ps(g)))
        self.FD = float(np.sum(w * cheb_interp(self.dp_nodes, g)))
        gg = g[g >= S_TINY]
        rho = cheb_interp(self.dp_nodes, gg) / ps(gg)
        self._lo = float(np.max(-1 / rho[rho > 0])) * (1 - 1e-9) if (rho > 0).any() else -1e6
        self._hi = float(np.min(-1 / rho[rho < 0])) * (1 - 1e-9) if (rho < 0).any() else 1e6
        self.model = None

    @classmethod
    def for_file(cls, f, pred=None):
        pred = json.load(open(PRED)) if pred is None else pred
        return cls(pred["files"][f]["dp_nodes"])

    def c_range(self, Neff_min=None, abars=None):
        return self._lo, self._hi

    def density(self, s, mu):
        s = np.maximum(np.asarray(s, float), S_TINY)
        return p_sine()(s) + mu * cheb_interp(self.dp_nodes, s)

    def prepare(self, s, Neff=None, abar=None):
        s = np.asarray(s, dtype=float)
        inw = s <= self.sc
        si = np.maximum(s[inw], S_TINY)
        rho = np.zeros(s.shape)
        rho[inw] = cheb_interp(self.dp_nodes, si) / p_sine()(si)
        phi = np.zeros(s.shape)
        phi[inw] = self.FD / self.F0
        return dict(inw=inw, s=s, Neff=np.ones(1), rho=rho, phi=phi, Nmin=1.0, abars=None)

    def bin_probs(self, mu, nb=GOF_BINS):
        """Window-conditional bin probabilities of p_μ (fine trapezoid per bin)."""
        edges = np.linspace(0, self.sc, nb + 1)
        P = []
        for a, b in zip(edges[:-1], edges[1:]):
            g = np.linspace(a, b, 2001)
            P.append(float(np.trapezoid(self.density(g, mu), g)))
        P = np.array(P)
        return P / P.sum(), edges

    def gof(self, s, mu, nb=GOF_BINS):
        s = np.asarray(s, float)
        sw = s[s <= self.sc]
        P, edges = self.bin_probs(mu, nb)
        O = np.histogram(sw, bins=edges)[0].astype(float)
        E = len(sw) * P
        return float(np.sum((O - E) ** 2 / E))


def fit_file(fitter, s, rng, block_lens, n_boot=B_BOOT, gof=True):
    """μ̂, flag, bootstrap SE per block length, χ² (GoF), in-window count."""
    prep = fitter.prepare(s)
    mu, flag = fitter.fit(prep)
    se = {}
    for L in block_lens:
        reps, nref = ph2lib.block_bootstrap_c_series(fitter, prep, mu, int(L), n_boot, rng)
        se[int(L)] = float(np.std(reps, ddof=1))
    out = dict(mu=float(mu), flag=flag, se=se, n=int(len(s)), n_window=int(prep["inw"].sum()))
    if gof:
        out["chi2"] = fitter.gof(s, mu)
    return out


def rule(per_file, w, block=None, gof_threshold=None):
    """The fortieth-round decision rule on per-file results {f: {mu, se[block]}} with weights w (pre-data)."""
    block = BLOCK if block is None else block
    files = list(w)
    mu = np.array([per_file[f]["mu"] for f in files])
    se = np.array([per_file[f]["se"][block] if isinstance(per_file[f]["se"], dict) else per_file[f]["se"]
                   for f in files])
    W = np.array([w[f] for f in files])
    mp_, sp = float(np.sum(W * mu)), float(math.sqrt(np.sum(W ** 2 * se ** 2)))
    resolvable = 2 * sp <= RESOLVE_2SE
    within = int(np.sum(np.abs(mu - 1) <= K_FILE * se))
    pool_ok = abs(mp_ - 1) <= K_POOL * sp + DMU_SYS
    verdict = "UNRESOLVED" if not resolvable else ("PASS" if pool_ok and within >= MIN_FILES else "FAIL")
    misfit = []
    if gof_threshold is not None:
        misfit = [f for f in files if per_file[f].get("chi2", 0.0) > gof_threshold[f]]
    return dict(verdict=verdict, mu_pool=mp_, se_pool=sp, ci95=[mp_ - 2 * sp, mp_ + 2 * sp], resolvable=resolvable,
                pool_within=pool_ok, files_within_3se=within, model_misfit=misfit)


# ---------------------------------------------------------------- the F3 decoding path (identical for synthetic files)
def spacings_from_platt(path, dps=45):
    """Decode a Platt-format file and unfold with exact θ (Phase 2's path: read_platt_file → platt_to_mpf →
    unfolded_spacings). Returns float64 spacings."""
    pairs, _ = ph2lib.read_platt_file(path)
    g = ph2lib.platt_to_mpf(pairs, dps=dps)
    return ph2lib.unfolded_spacings(g, dps=dps - 5)


def write_platt(path, zeros_mp, block=10_000, first_index=1):
    """Write zeros (mpf, increasing) in the LMFDB Platt format read by ph2lib.read_platt_file: uint64 block count; per
    block 'ddQQ' (t0, t1, N(t0), N(t1)) then 13-byte cumulative deltas Z (γ = t0 + Z·2^-101), t0 an integer below the
    block's first zero. Values are rounded to the 2^-101 grid, as in the real files."""
    import struct
    import mpmath as mp
    n = len(zeros_mp)
    nb = (n + block - 1) // block
    with mp.workdps(60), open(path, "wb") as fh:
        fh.write(struct.pack("<Q", nb))
        for b in range(nb):
            zs = zeros_mp[b * block:(b + 1) * block]
            t0 = int(mp.floor(zs[0]))
            t1 = int(mp.floor(zs[-1])) + 1
            fh.write(struct.pack("<ddQQ", float(t0), float(t1), first_index - 1 + b * block,
                                 first_index - 1 + b * block + len(zs)))
            prev = 0
            for z in zs:
                Z = int(mp.nint((z - t0) * mp.mpf(2) ** 101))
                d = Z - prev
                prev = Z
                fh.write(struct.pack("<QIB", d & (2 ** 64 - 1), (d >> 64) & (2 ** 32 - 1), d >> 96))


# ---------------------------------------------------------------- pipeline identity (fortieth round): CUE → file density → back
def place(t0, s, x0=0.5, dps=50):
    """Heights γ_k with N̄(γ_k) = N̄(t0) + x_k, x_0 = x0, x_{k+1} = x_k + s_k summed EXACTLY in mpf (a float64 cumulative
    sum would put ~1e-9 into the round trip at 7·10⁶ levels); exact θ; Newton from a first-order predictor."""
    import mpmath as mp
    out = []
    with mp.workdps(dps):
        two_pi = 2 * mp.pi
        base = mp.siegeltheta(mp.mpf(t0)) / mp.pi + 1
        tol = mp.mpf(10) ** -34                     # far below the files' 2^-101 ≈ 4e-31 grid
        x = mp.mpf(x0)
        g = mp.mpf(t0)
        dx = x
        for k in range(len(s) + 1):
            if k:
                dx = mp.mpf(float(s[k - 1]))
                x += dx
            target = base + x
            g = g + dx * two_pi / mp.log(g / two_pi)             # predictor
            for _ in range(60):
                step = (mp.siegeltheta(g) / mp.pi + 1 - target) / (mp.log(g / two_pi) / two_pi)
                g -= step
                if abs(step) < tol:
                    break
            else:
                raise RuntimeError("place: Newton did not converge")
            out.append(+g)
    return out


def pipeline_check(f, s, path, fitter=None):
    """CUE spacings s placed at file f's height (first level at N̄(t0) + 0.5), written in the Platt format at the 2^-101
    grid, decoded and unfolded by spacings_from_platt (the read's path). Returns the round-trip spacing error and μ̂ both
    ways (same fitter, same window)."""
    fitter = MuFit.for_file(f) if fitter is None else fitter
    g = place(F3[f][0], s)
    write_platt(path, g)
    del g
    back = spacings_from_platt(path)
    err = float(np.max(np.abs(back - s)))
    mu_direct = fitter.fit(fitter.prepare(s))[0]
    mu_back = fitter.fit(fitter.prepare(back))[0]
    return dict(file=f, n=len(s), max_abs_spacing_err=err, mu_direct=float(mu_direct), mu_back=float(mu_back),
                dmu=float(mu_back - mu_direct), chi2_direct=fitter.gof(s, mu_direct), chi2_back=fitter.gof(back, mu_back))


# ---------------------------------------------------------------- known answers (i.i.d. draws; correlations are the CUE calibration's job)
def draw_iid(fitter, mu, n, rng, grid=200001):
    """n i.i.d. spacings from the window-conditional p_μ (inverse CDF on a fine grid)."""
    g = np.linspace(0, fitter.sc, grid)
    p = np.maximum(fitter.density(g, mu), 0)
    p[0] = 0.0
    cdf = np.concatenate([[0], np.cumsum(0.5 * (p[1:] + p[:-1]) * np.diff(g))])
    cdf /= cdf[-1]
    return np.interp(rng.uniform(size=n), cdf, g)


def selftest(n=2_000_000, seed=40):
    rng = np.random.default_rng(seed)
    pred = json.load(open(PRED))
    out = {}
    for f in (list(F3)[0], list(F3)[-1]):
        fit = MuFit.for_file(f, pred)
        rows = []
        for mu in (0.0, 0.5, 1.0, 2.0):
            s = draw_iid(fit, mu, n, rng)
            r = fit_file(fit, s, rng, block_lens=(1,), n_boot=100)
            r["true"] = mu
            r["z"] = (r["mu"] - mu) / r["se"][1]
            rows.append(r)
            print(f, f"μ={mu}: μ̂ {r['mu']:+.4f} ± {r['se'][1]:.4f}  z {r['z']:+.2f}  χ² {r['chi2']:.1f}  ({fit.c_range()})", flush=True)
        # red path: Poisson spacings must be flagged by the GoF (χ² far above its i.i.d. scale ≈ GOF_BINS − 2)
        sp = rng.exponential(size=n)
        rp = fit_file(fit, sp, rng, block_lens=(1,), n_boot=20)
        print(f, f"Poisson: μ̂ {rp['mu']:+.4f} flag {rp['flag']}  χ² {rp['chi2']:.3g}", flush=True)
        out[f] = dict(rows=rows, poisson=rp)
    ok = all(abs(r["z"]) < 4 for v in out.values() for r in v["rows"]) and \
        all(v["poisson"]["chi2"] > 100 * GOF_BINS for v in out.values()) and \
        all(r["chi2"] < 3 * GOF_BINS for v in out.values() for r in v["rows"])
    out["PASS"] = bool(ok)
    print("SELFTEST", "PASS" if ok else "FAIL")
    return out


if __name__ == "__main__":
    if sys.argv[1] == "selftest":
        res = selftest()
        if len(sys.argv) > 2:
            json.dump(res, open(sys.argv[2], "w"), indent=1)
    elif sys.argv[1] == "pipeline":          # pipeline FILE N_SPACINGS OUT.json PLATT_PATH   (GPU sampler on char)
        import cbe
        f, n = sys.argv[2], int(sys.argv[3])
        rng = np.random.default_rng([20261013, 99, list(F3).index(f)])
        need = -(-n // 1000)
        sp = np.concatenate([cbe.spacings(cbe.sample(rng, min(2000, need - k), 1000, 2.0, gpu=True)[0]).ravel()
                             for k in range(0, need, 2000)])[:n]
        res = pipeline_check(f, sp, sys.argv[5])
        os.remove(sys.argv[5])
        print(res)
        json.dump(res, open(sys.argv[4], "w"), indent=1)
    elif sys.argv[1] == "weights":
        w, n = weights()
        for f in F3:
            print(f, f"n_f {n[f]:.1f}  w {w[f]:.5f}")

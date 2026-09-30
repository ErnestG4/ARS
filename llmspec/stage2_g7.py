"""Stage 2 -- G7 multi-peak calibrator (brief v1.1 §5 G7). Witness-must-fail for peaked densities.

PRE-REGISTRATION (frozen by commit before any local statistic touches a real peaked spectrum):

Targets. Per-spectrum target densities = Gaussian mixtures fitted (EM, K by BIC over 1..6) to real per-head
  x = sigma/median over x >= 0.1 (near-zero/dead-row cluster excluded, as it is excluded from local stats),
  for every head of the substrate/matrix that Stage 1 selects (--targets). N per spectrum = d_head; the number
  of spectra pooled = number of real heads. A UNIMODAL control family (single Gaussian fitted to each head)
  runs alongside: the instrument must pass on it too.

Synthetic classes, each defined in unfolded coordinates on a circle of N levels (mean spacing 1, no edges),
  then mapped per spectrum through the inverse CDF of that spectrum's target:
  (a) POISSON: N i.i.d. uniform.
  (b) BETA1: COE(N) eigenphases (exactly uniform density; beta=1 local statistics). Secondary (b'): real
      Wishart 128 x 2048 eigenvalues unfolded by the MP CDF (the brief's construction; finite-N edge effects).
  (c) CLUSTERED: Neyman-Scott on the circle, parents Poisson(rate 1/mu), Poisson(mu) offspring, Gaussian
      displacement sd_c; strengths (mu, sd_c) in {(2, 0.1), (4, 0.3)}.
  (d) BETA2: CUE(N) eigenphases.

Pipeline (NO access to the true density): sort x -> unfold with method U -> spacings -> drop spacings whose
  left level is in the first/last 5% of the spectrum -> per-spectrum unit-mean renorm -> pool over spectra.
  Statistics on the pool: Brody q (cross_substrate.axes.I8_brody_q_unbounded, the repaired fitter) and
  <r~> (mean min(r,1/r) of consecutive raw-x spacing ratios, no unfolding; and on unfolded spacings).
  ORACLE = same data unfolded with the true target CDF (reference, not a candidate).
  Methods (every setting that may be used on real data must pass):
    poly(k):   LSQ Chebyshev fit of the staircase i vs x_i, degree k in {3, 5, 7, 9, 12, 15, 20}
    spline(m): LSQ cubic spline of the staircase, interior knots at every m-th level (adapts to peaks),
               m in {4, 6, 8, 12, 16, 24, 32}
    kde(c):    staircase smoothed by Gaussian-CDF kernels, per-level bandwidth b_j = c * local spacing
               (x_{j+5} - x_{j-5}) / 10, c in {1, 1.5, 2, 3, 4, 6, 8}
    local(w):  s_i / mean(s_{i-w..i+w}), w in {2, 3, 4, 5, 6, 8}
  A NON-MONOTONE unfolding is not an unfolding: a setting whose unfolded spacings are non-positive in more
  than 0.1% of spacings (any class, any family) FAILS; non-positive spacings are never silently dropped
  from <r~>, and the Brody fit sees only s > 0 only for settings that already pass this rule.
  EXCLUDED by design: unfolding with a fitted Gaussian mixture -- the targets ARE Gaussian mixtures, so
  it would pass by sharing the generator's model family and would not transfer to real spectra.
  (Candidate set widened 2026-09-25 after a SYNTHETIC-target dry run only -- no real target seen -- in
  which polynomial unfolding went non-monotone and every setting failed beta=1 on narrow peaks.)

Pass criteria per (method setting, target family), R = 20 replicate pools, compared on the replicate MEAN:
  (a) |q - q_oracle| <= 0.10    (b) |q - q_oracle| <= 0.10    (d) |q - q_oracle| <= 0.10
  (c) q < 0 in >= 19/20 replicates AND |q - q_oracle| <= 0.15 (strength recovered, sign read)
  <r~>: |r - r_oracle| <= 0.01 for every class, separately for raw-x and unfolded <r~> (a failing <r~> is
  reported as <r~> NOT LICENSED on peaked spectra, independent of q).
  Tolerance rationale: 0.10 = 10% of the Poisson-GOE gap in q; the pooled SE of q at ~3e4 spacings is ~0.01.
A setting PASSES iff all classes pass on both the peaked and the unimodal-control families.
Bandwidth rule for real data: within each method family, the passing setting at the centre of the longest
  contiguous passing run (ties -> the less smoothing one). If no setting of any family passes: local
  statistics on peaked spectra are NOT LICENSED; report density-level results only (peak count, positions,
  widths over time).
"""
import json, sys, time, warnings
from pathlib import Path
import numpy as np
from scipy.special import ndtr
from scipy.stats import norm

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from cross_substrate.axes import I8_brody_q_unbounded  # noqa: E402

EDGE = 0.05
warnings.filterwarnings("ignore", message="The fit may be poorly conditioned")  # conditioning is judged by the pass rule, not a warning
POLY = [3, 5, 7, 9, 12, 15, 20]
SPLM = [4, 6, 8, 12, 16, 24, 32]
KDEC = [1, 1.5, 2, 3, 4, 6, 8]
LOCW = [2, 3, 4, 5, 6, 8]
NONPOS_MAX = 1e-3
NS = [(2, 0.1), (4, 0.3)]


# ---------------- targets ----------------
class Mixture:
    def __init__(self, w, mu, sd):
        self.w, self.mu, self.sd = map(np.asarray, (w, mu, sd))
        lo = (self.mu - 8 * self.sd).min(); hi = (self.mu + 8 * self.sd).max()
        self.g = np.linspace(lo, hi, 20001)
        c = (self.w[None] * ndtr((self.g[:, None] - self.mu[None]) / self.sd[None])).sum(1)
        self.c = (c - c[0]) / (c[-1] - c[0])

    def cdf(self, x):
        return np.interp(x, self.g, self.c)

    def icdf(self, u):
        return np.interp(u, self.c, self.g)


def fit_mixture(x, kmax=6, seed=0):
    from sklearn.mixture import GaussianMixture
    x = np.asarray(x)[:, None]
    best = None
    for k in range(1, kmax + 1):
        if k > len(x) // 8:
            break
        gm = GaussianMixture(k, n_init=3, random_state=seed).fit(x)
        b = gm.bic(x)
        if best is None or b < best[0]:
            best = (b, gm)
    gm = best[1]
    return Mixture(gm.weights_, gm.means_[:, 0], np.sqrt(gm.covariances_.reshape(-1)))


def fit_unimodal(x):
    x = np.asarray(x)
    return Mixture([1.0], [x.mean()], [x.std(ddof=1)])


# ---------------- classes (unfolded coords on a circle of length N) ----------------
def cue_phases(N, rng, beta):
    Z = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2)
    Q, R = np.linalg.qr(Z)
    Q = Q * (np.diag(R) / np.abs(np.diag(R)))
    U = Q if beta == 2 else Q.T @ Q          # COE = U^T U for U Haar-CUE
    th = np.sort(np.angle(np.linalg.eigvals(U)) % (2 * np.pi))
    return th / (2 * np.pi)                  # in [0,1)


def neyman_scott(N, rng, mu, sd):
    while True:
        npar = rng.poisson(N / mu)
        par = rng.uniform(0, N, npar)
        kids = rng.poisson(mu, npar)
        pts = np.concatenate([p + sd * rng.standard_normal(k) for p, k in zip(par, kids)]) if npar else np.array([])
        pts = np.sort(pts % N)
        if len(pts) >= 0.8 * N:
            return pts / N


def wishart_mp(N, rng, n=2048):
    W = rng.standard_normal((N, n)) / np.sqrt(n)
    ev = np.linalg.eigvalsh(W @ W.T)
    c = N / n
    a, b = (1 - np.sqrt(c)) ** 2, (1 + np.sqrt(c)) ** 2
    g = np.linspace(a, b, 20001)
    f = np.sqrt(np.clip((b - g) * (g - a), 0, None)) / (2 * np.pi * c * g)
    F = np.concatenate([[0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(g))]); F /= F[-1]
    return np.sort(np.clip(np.interp(ev, g, F), 0, 1 - 1e-12))


def draw(cls, N, rng):
    if cls == "poisson":
        return np.sort(rng.uniform(0, 1, N))
    if cls == "beta1":
        return cue_phases(N, rng, 1)
    if cls == "beta2":
        return cue_phases(N, rng, 2)
    if cls == "beta1_wishart":
        return wishart_mp(N, rng)
    if cls.startswith("ns"):
        mu, sd = NS[int(cls[2])]
        return neyman_scott(N, rng, mu, sd)
    raise ValueError(cls)


# ---------------- unfolding ----------------
def unfold(x, method, par, target=None):
    x = np.sort(x); n = len(x); i = np.arange(n) + 0.5
    if method == "oracle":
        return target.cdf(x) * n
    if method == "poly":
        return np.polynomial.Chebyshev.fit(x, i, par)(x)
    if method == "spline":
        from scipy.interpolate import LSQUnivariateSpline
        t = x[par:n - par:par]
        t = t[(t > x[0]) & (t < x[-1])]
        return LSQUnivariateSpline(x, i, t, k=3)(x)
    if method == "kde":
        k = 5
        j = np.arange(n)
        loc = (x[np.minimum(j + k, n - 1)] - x[np.maximum(j - k, 0)]) / (np.minimum(j + k, n - 1) - np.maximum(j - k, 0))
        b = np.maximum(par * loc, 1e-300)
        return ndtr((x[:, None] - x[None, :]) / b[None, :]).sum(1)
    raise ValueError(method)


def spacings(x, method, par, target=None):
    x = np.sort(x); n = len(x)
    if method == "local":
        s = np.diff(x)
        w = par
        cs = np.concatenate([[0], np.cumsum(s)])
        idx = np.arange(len(s))
        lo = np.maximum(idx - w, 0); hi = np.minimum(idx + w + 1, len(s))
        s = s / ((cs[hi] - cs[lo]) / (hi - lo))
    else:
        s = np.diff(unfold(x, method, par, target))
    keep = (np.arange(len(s)) >= int(EDGE * n)) & (np.arange(len(s)) < n - 1 - int(EDGE * n))
    s = s[keep]
    return s / s.mean()


def rtilde(s):
    s = np.asarray(s)
    r = s[1:] / s[:-1]
    return np.minimum(r, 1 / r)


def settings():
    return ([("poly", k) for k in POLY] + [("spline", m) for m in SPLM] + [("kde", c) for c in KDEC]
            + [("local", w) for w in LOCW])


# ---------------- one replicate pool ----------------
def replicate(targets, cls, N, rng):
    out = {("oracle", 0): [], **{st: [] for st in settings()}}
    r_raw, r_unf = [], {st: [] for st in list(out)}
    for T in targets:
        u = draw(cls, N, rng)
        x = np.sort(T.icdf(u))
        if np.any(np.diff(x) <= 0):
            x = np.sort(x + 1e-15 * rng.standard_normal(len(x)))
        r_raw.append(rtilde(np.diff(x)[int(EDGE * len(x)):len(x) - 1 - int(EDGE * len(x))]))
        for st in out:
            s = spacings(x, st[0], st[1], T)
            out[st].append(s)
            r_unf[st].append(rtilde(s) if np.all(s > 0) else np.full(max(len(s) - 1, 0), np.nan))
    res = {}
    for st in out:
        s = np.concatenate(out[st])
        bad = int((s <= 0).sum())
        rr = np.concatenate(r_unf[st])
        res[f"{st[0]}:{st[1]}"] = {"q": I8_brody_q_unbounded(s[s > 0]),
                                   "r_unf": float(np.nanmean(rr)) if np.isfinite(rr).any() else float("nan"),
                                   "n": int(len(s)), "nonpos": bad}
    res["raw_r"] = float(np.concatenate(r_raw).mean())
    return res


def evaluate(targets, N, R, seed, classes):
    rng = np.random.default_rng(seed)
    tab = {}
    for cls in classes:
        reps = [replicate(targets, cls, N, rng) for _ in range(R)]
        tab[cls] = reps
        print(f"  {cls}: oracle q={np.mean([r['oracle:0']['q'] for r in reps]):.3f}", flush=True)
    return tab


def judge(tab):
    out = {}
    classes = list(tab)
    for st in ["%s:%s" % s for s in settings()]:
        v = {}
        ok_all = True
        for cls in classes:
            reps = tab[cls]
            q = np.array([r[st]["q"] for r in reps]); qo = np.array([r["oracle:0"]["q"] for r in reps])
            ru = np.mean([r[st]["r_unf"] for r in reps]); ro = np.mean([r["oracle:0"]["r_unf"] for r in reps])
            rr = np.mean([r["raw_r"] for r in reps])
            dq = float(q.mean() - qo.mean())
            nonpos_frac = sum(r[st]["nonpos"] for r in reps) / sum(r[st]["n"] for r in reps)
            if cls.startswith("ns"):
                okq = bool((q < 0).sum() >= 19 * len(q) / 20 and abs(dq) <= 0.15)
            else:
                okq = abs(dq) <= 0.10
            okq = bool(okq and nonpos_frac <= NONPOS_MAX)
            v[cls] = {"q": float(q.mean()), "q_oracle": float(qo.mean()), "dq": dq, "q_sd": float(q.std()),
                      "pass_q": okq, "r_unf": float(ru), "r_oracle": float(ro), "r_raw": float(rr),
                      "pass_r_unf": bool(np.isfinite(ru) and abs(ru - ro) <= 0.01), "pass_r_raw": abs(rr - ro) <= 0.01,
                      "nonpos_frac": float(nonpos_frac)}
            ok_all &= okq
        out[st] = {"pass_q_all": ok_all, "classes": v}
    return out


def pick(passing):
    """centre of the longest contiguous passing run per family (ties -> less smoothing: lower c / w / m;
    for poly, MORE degree = less smoothing, so ties -> higher k)."""
    rule = {}
    for fam, grid in (("poly", POLY), ("spline", SPLM), ("kde", KDEC), ("local", LOCW)):
        flags = [passing.get(f"{fam}:{p}", False) for p in grid]
        best, cur = [], []
        for p, f in zip(grid, flags):
            cur = cur + [p] if f else []
            if len(cur) > len(best) or (len(cur) == len(best) and cur and fam == "poly"):
                best = list(cur)
        if best:
            mid = (len(best) - 1) / 2
            rule[fam] = best[int(np.ceil(mid))] if fam == "poly" else best[int(np.floor(mid))]
            rule[fam + "_run"] = best
        else:
            rule[fam] = None
    return rule


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", required=True, help="npz with per-head x arrays (key 'x', object array) or 'synthetic'")
    ap.add_argument("--N", type=int, default=128)
    ap.add_argument("--R", type=int, default=20)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=20260925)
    ap.add_argument("--classes", default="poisson,beta1,ns0,ns1,beta2,beta1_wishart")
    a = ap.parse_args()
    classes = a.classes.split(",")
    if a.targets == "synthetic":
        rng = np.random.default_rng(1)
        xs = []
        for _ in range(64):
            k = rng.integers(2, 4)
            mu = np.sort(rng.uniform(0.6, 2.0, k)); sd = rng.uniform(0.02, 0.1, k); w = rng.dirichlet(np.ones(k) * 3)
            comp = rng.choice(k, 128, p=w)
            xs.append(mu[comp] + sd[comp] * rng.standard_normal(128))
    else:
        z = np.load(a.targets, allow_pickle=True)
        xs = list(z["x"])
    t = time.time()
    peaked = [fit_mixture(x) for x in xs]
    uni = [fit_unimodal(x) for x in xs]
    kk = [len(m.w) for m in peaked]
    print(f"targets: {len(xs)} spectra, mixture K distribution {np.bincount(kk).tolist()} ({time.time()-t:.0f}s)", flush=True)
    res = {"prereg": __doc__, "n_spectra": len(xs), "N": a.N, "R": a.R, "K_counts": np.bincount(kk).tolist(),
           "families": {}}
    for fam, T in (("peaked", peaked), ("unimodal_control", uni)):
        print(fam, flush=True)
        tab = evaluate(T, a.N, a.R, a.seed + (0 if fam == "peaked" else 1), classes)
        res["families"][fam] = judge(tab)
    passing = {st: all(res["families"][f][st]["pass_q_all"] for f in res["families"]) for st in res["families"]["peaked"]}
    res["passing"] = passing
    res["bandwidth_rule"] = pick(passing)
    res["licensed_q"] = any(passing.values())
    # raw-x <r~> does not depend on the unfolding setting: read it off any one setting
    st0 = next(iter(res["families"]["peaked"]))
    res["r_raw_licensed"] = all(res["families"][f][st0]["classes"][c]["pass_r_raw"]
                                for f in res["families"] for c in classes)
    res["r_unf_licensed"] = {st: all(res["families"][f][st]["classes"][c]["pass_r_unf"]
                                     for f in res["families"] for c in classes) for st in res["families"]["peaked"]}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=1, default=float))
    print("passing:", {k: v for k, v in passing.items() if v}, "rule:", res["bandwidth_rule"],
          "r_raw_licensed:", res["r_raw_licensed"], flush=True)


if __name__ == "__main__":
    main()

"""derivflow/modes — shared machinery for the M0–M6 arc (BRIEF.md).

READ-ONLY on everything outside derivflow/modes/. Imports the certified production
instrument verbatim and adds only the new ARMS (NOUNFOLD, POPREF, RM1), the new
SEEDS (LATTICE, LATTICE_WAVE, QLATTICE) and the interlacing witness (M6).

Production statistic (M0.2): track0_harness.rtilde on np.diff(u[bulk_idx(m)]),
bulk_idx selecting the central ceil(BULK_FRACTION*m) roots BY INDEX.
Production reference (M0.5): track0_iid_scaling.reference_cdf — per-gap 3-point
Gauss quadrature of the Stieltjes-inverted density at height eps_k
(eps_k = Delta_s*sqrt(0.25 + 16(n-k)/(kn)), Poisson-kernel smoothing), Richardson
primary 2F(eps)-F(2eps), raw eps / raw 2eps as the two band arms. It exposes
unfolded POSITIONS (F_at * m), not only gaps.
"""
import hashlib
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DF = os.path.dirname(HERE)
ROOT = os.path.dirname(DF)
for p in (ROOT, DF):
    if p not in sys.path:
        sys.path.insert(0, p)

from track0_harness import diff_step, bulk_idx, rtilde, sigma2, BULK_FRACTION, GateFail  # noqa: E402,F401
from track0_iid_scaling import reference_cdf, F_uniform, eps_rule_v15                   # noqa: E402
import track0_iid_scaling as TIS                                                        # noqa: E402
from free_conv import F_empirical, F_semicircle                                         # noqa: E402
from science_rate_question import (gue_seed, MASTER_SEED, KSTAR_LEVEL, FIT_WINDOW_MIN,  # noqa: E402
                                   fit_ladder, kstar, f3, LN10)
from science_dense import K_DENSE                                                       # noqa: E402
from spacings import Unfolding, Spacings                                                # noqa: E402

WINDOW_TAG = f"bulk-{BULK_FRACTION:.2f}"
GUE_DE_SEMICIRCLE_SIGMA = 1.0     # F_semicircle(1.0): support [-2, 2]; verified in M0 (manifest)
SEAL_CHILDREN = {                 # RATE_QUESTION_SEAL / SCALE_LAW_SEAL rng_protocol
    ("iid", 1024): 0, ("iid", 2048): 16, ("iid", 4096): 32, ("iid", 16384): 96,
    ("gue", 1024): 48, ("gue", 2048): 64, ("gue", 4096): 80, ("gue", 16384): 112,
}
R_SEAL = 16


# ---------------------------------------------------------------- seeds
def seal_children(n_children=128):
    return np.random.SeedSequence(MASTER_SEED).spawn(n_children)


def seed_iid_uniform(child, n):
    return np.sort(np.random.default_rng(child).uniform(-1.0, 1.0, n))


def seed_gue_de(child, n):
    return gue_seed(n, np.random.default_rng(child))


def seed_lattice(n):
    return np.linspace(-1.0, 1.0, n)


def seed_lattice_wave(n, qw, A, phi):
    """LATTICE + A*h*sin(qw*j + phi), h = 2/(n-1), j = 0..n-1 (BRIEF §1)."""
    h = 2.0 / (n - 1)
    j = np.arange(n)
    return seed_lattice(n) + A * h * np.sin(qw * j + phi)


def cdf_semicircle(x, sigma):
    """CDF of sc(sigma), support [-2 sigma, 2 sigma]."""
    y = np.clip(x / (2.0 * sigma), -1.0, 1.0)
    return 0.5 + (y * np.sqrt(1.0 - y * y) + np.arcsin(y)) / np.pi


def seed_qlattice_semicircle(n_k, t_flow, sigma=GUE_DE_SEMICIRCLE_SIGMA):
    """x_j = F^{-1}((j+1/2)/n_k), F = CDF of sc(sigma) evolved to t_flow: sc(sigma*sqrt(1-t))."""
    sig = sigma * np.sqrt(1.0 - t_flow)
    targets = (np.arange(n_k) + 0.5) / n_k
    lo, hi = np.full(n_k, -2.0 * sig), np.full(n_k, 2.0 * sig)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        below = cdf_semicircle(mid, sig) < targets
        lo = np.where(below, mid, lo)
        hi = np.where(below, hi, mid)
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------- flow
def flow(seed, k_list, on_k):
    """Run diff_step to max(k_list); call on_k(k, roots) at each banked k."""
    r = seed.copy()
    for k in range(1, max(k_list) + 1):
        r = diff_step(r)
        if k in k_list:
            on_k(k, r)
    return r


# ---------------------------------------------------------------- arms
def eps_over_delta(n, k):
    return float(np.sqrt(0.25 + 16.0 * (n - k) / (k * n)))


def tag(reference, arm, n, k):
    e = 0.0 if arm in ("nounfold", "rm1") else eps_over_delta(n, k) * (2.0 if arm == "raw-2eps" else 1.0)
    return Unfolding(reference=reference, arm=arm, eps_over_delta=e, window=WINDOW_TAG)


def prod_positions(F_seed_emp, r, n, k):
    """Production arms on flowed roots r: unfolded positions for primary/eps/2eps."""
    m = n - k
    F_at, diag = reference_cdf(F_seed_emp, r, k / n, m)
    return {"PROD_PRIMARY": F_at * m,
            "PROD_BW1": diag["F_at_eps_raw"] * m,
            "PROD_BW2": diag["F_at_2eps"] * m}, {kk: v for kk, v in diag.items()
                                                 if kk not in ("F_at_eps_raw", "F_at_2eps")}


def popref_positions(F_analytic, r, n, k):
    """POPREF: the production reference with the ANALYTIC seed transform in place of atoms.
    Same eps_k rule, same quadrature, same Richardson pairing — only F_seed differs."""
    m = n - k
    F_at, diag = reference_cdf(F_analytic, r, k / n, m)
    return F_at * m, {kk: v for kk, v in diag.items() if kk not in ("F_at_eps_raw", "F_at_2eps")}


def rm1_positions(r):
    """Each raw gap divided by the mean of raw gaps at offsets -1,0,+1 (truncated at ends)."""
    g = np.diff(r)
    s = np.empty_like(g)
    s[1:-1] = g[1:-1] / ((g[:-2] + g[1:-1] + g[2:]) / 3.0)
    s[0] = g[0] / ((g[0] + g[1]) / 2.0)
    s[-1] = g[-1] / ((g[-2] + g[-1]) / 2.0)
    return np.concatenate([[0.0], np.cumsum(s)])


ARM_REF = {"PROD_PRIMARY": ("empirical-seed", "richardson"),
           "PROD_BW1": ("empirical-seed", "raw-eps"),
           "PROD_BW2": ("empirical-seed", "raw-2eps"),
           "NOUNFOLD": ("none", "nounfold"),
           "RM1": ("none", "rm1")}


def omr(positions, n, k, arm, reference=None, substrate=""):
    """1 - <rtilde> over the bulk window, exactly as production: rtilde(np.diff(u[bulk_idx(m)])).
    Returns (float, Tagged)."""
    m = n - k
    if reference is None:
        reference, armname = ARM_REF[arm]
    else:
        armname = "richardson"
    t = tag(reference, armname, n, k)
    sp = Spacings.from_positions(np.asarray(positions)[bulk_idx(m)], t, substrate)
    tg = sp.rtilde_distance()
    v = float(tg)
    # cross-check against the production function on the same gaps
    assert abs(v - (1.0 - rtilde(sp.values))) <= 1e-15 * max(1.0, abs(v))
    return v, tg


# ---------------------------------------------------------------- M6 interlacing witness
def interlacing_D(seed, r):
    """D = sup_x |F_r(x) - F_seed(x)|, empirical CDFs each normalised by its own degree."""
    n0, n1 = len(seed), len(r)
    xs = np.concatenate([seed, r])
    F0 = np.searchsorted(seed, xs, side="right") / n0
    F1 = np.searchsorted(r, xs, side="right") / n1
    F0m = np.searchsorted(seed, xs, side="left") / n0
    F1m = np.searchsorted(r, xs, side="left") / n1
    return float(max(np.max(np.abs(F1 - F0)), np.max(np.abs(F1m - F0m))))


def interlacing_bounds(n, k):
    """(sharp theorem bound k/n, BRIEF bound 2k/(n-k)).

    Rolle interlacing: the j-th root of p^(k) lies in (r_j, r_{j+k}), so the count
    c_k(x) of p^(k)-roots <= x satisfies c_0 - k <= c_k <= min(c_0, n-k). Then
    D = |c_k/(n-k) - c_0/n| <= k/n, attained e.g. at c_0 = c_k = n-k. The BRIEF's
    2k/(n-k) is implied (looser by > 2x) but is NOT reachable by its own red path:
    moving one root changes D by at most 1/(n-k), and k/n + 1/(n-k) < 2k/(n-k)
    for every k >= 1, n > 2k. So the witness checks the sharp bound and REPORTS both."""
    return k / n, 2.0 * k / (n - k)


# ---------------------------------------------------------------- fits / k* / tail
def kstar_interp(ks, means, level=KSTAR_LEVEL):
    """Method (b): monotone log-linear interpolation of the ensemble mean across the
    first crossing of `level`. Returns None if no crossing."""
    ks = np.asarray(ks, float); y = np.log(np.asarray(means, float))
    yl = np.log(level)
    for i in range(len(ks) - 1):
        if (y[i] - yl) * (y[i + 1] - yl) <= 0 and y[i] != y[i + 1]:
            t = (yl - y[i]) / (y[i + 1] - y[i])
            return float(np.exp(np.log(ks[i]) + t * (np.log(ks[i + 1]) - np.log(ks[i]))))
    return None


def kstar_fit(ks, means, sig, rng):
    """Method (a): the production F3 ladder + kstar() (MVN covariance draws)."""
    ks = np.asarray(ks, float)
    win = means > FIT_WINDOW_MIN
    if win.sum() < 4:
        return {"selected": None, "kstar": None, "err": None, "fit_window_k": ks[win].tolist()}
    sel, fits = fit_ladder(ks[win], np.asarray(means)[win], np.asarray(sig)[win])
    out = {"selected": sel, "fit_window_k": ks[win].tolist(), "ladder": fits}
    if "params" in fits[sel]:
        k0, kerr = kstar(sel, np.array(fits[sel]["params"]), np.array(fits[sel]["cov"]), rng)
        out.update(kstar=k0, err=kerr, params=fits[sel]["params"],
                   chi2=fits[sel]["chi2"], dof=fits[sel]["dof"])
    else:
        out.update(kstar=None, err=None)
    return out


def p_tail(ks, means, kmin=16, kmax=None):
    """-(OLS slope of ln mean-omr against ln k) over kmin <= k <= kmax."""
    ks = np.asarray(ks, float); means = np.asarray(means, float)
    sel = (ks >= kmin) & (ks <= (kmax if kmax else ks.max())) & (means > 0)
    if sel.sum() < 3:
        return None
    x, y = np.log(ks[sel]), np.log(means[sel])
    return float(-np.polyfit(x, y, 1)[0]), int(sel.sum())


def bootstrap_curve_stats(curves, ks, rng, n_boot=200, kmin_tail=16, kmax_tail=None):
    """Replicate bootstrap of {k*_fit, k*_interp, p_tail}. curves: (R, len(ks))."""
    R = curves.shape[0]
    out = {"kstar_fit": [], "kstar_interp": [], "p_tail": []}
    for _ in range(n_boot):
        idx = rng.integers(0, R, R)
        c = curves[idx]
        m, s = c.mean(axis=0), c.std(axis=0, ddof=1) / np.sqrt(R)
        kf = kstar_fit(ks, m, s, rng)
        out["kstar_fit"].append(kf["kstar"])
        out["kstar_interp"].append(kstar_interp(ks, m))
        pt = p_tail(ks, m, kmin_tail, kmax_tail)
        out["p_tail"].append(pt[0] if pt else None)
    res = {}
    for key, vals in out.items():
        v = np.array([x for x in vals if x is not None], float)
        res[key] = {"n_ok": int(v.size), "n_boot": n_boot,
                    "sd": (float(v.std(ddof=1)) if v.size > 2 else None),
                    "q16": (float(np.quantile(v, 0.16)) if v.size else None),
                    "q84": (float(np.quantile(v, 0.84)) if v.size else None)}
    return res


def curve_summary(curves, ks, rng, tail_kmin=16, tail_kmax=None, n_boot=200):
    """Everything BRIEF M3 banks per (class, n, arm) from per-replicate curves."""
    curves = np.asarray(curves, float)
    R = curves.shape[0]
    mean = curves.mean(axis=0)
    sig = curves.std(axis=0, ddof=1) / np.sqrt(R)
    kf = kstar_fit(ks, mean, sig, rng)
    ki = kstar_interp(ks, mean)
    pt = p_tail(ks, mean, tail_kmin, tail_kmax)
    boot = bootstrap_curve_stats(curves, ks, rng, n_boot, tail_kmin, tail_kmax)
    return {"k_grid": list(map(int, ks)), "replicates": R,
            "per_replicate": curves.tolist(),
            "mean": mean.tolist(), "sigma_mean": sig.tolist(),
            "kstar_fit": {"method": "(a) production F3 ladder + kstar() MVN draws",
                          "value": kf.get("kstar"), "err_covariance": kf.get("err"),
                          "err_bootstrap": boot["kstar_fit"]["sd"],
                          "selected": kf.get("selected"), "fit_window_k": kf.get("fit_window_k"),
                          "params": kf.get("params"), "chi2": kf.get("chi2"), "dof": kf.get("dof")},
            "kstar_interp": {"method": "(b) monotone log-linear interpolation of the ensemble mean",
                             "value": ki, "err_bootstrap": boot["kstar_interp"]["sd"]},
            "p_tail": {"value": (pt[0] if pt else None), "n_points": (pt[1] if pt else 0),
                       "k_range": [tail_kmin, tail_kmax if tail_kmax else int(max(ks))],
                       "err_bootstrap": boot["p_tail"]["sd"],
                       "report_only": bool((tail_kmax if tail_kmax else max(ks)) < 48)},
            "bootstrap": boot,
            "error_models": "covariance (kstar_fit.err_covariance, MVN parameter draws) AND "
                            "replicate bootstrap (err_bootstrap, n_boot resamples of the "
                            f"{R} replicates); both always reported (errormodel.py fork)"}


# ---------------------------------------------------------------- hashing / banking
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_array(a):
    return hashlib.sha256(np.ascontiguousarray(a, dtype=np.float64).tobytes()).hexdigest()

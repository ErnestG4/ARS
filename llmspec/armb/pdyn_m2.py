"""M2 -- parametric BULK statistics of a time series of spectra (eigenvalue-only, gauge-free).

Input: spectra (T, n) -- one matrix's levels at checkpoints t_0 < ... < t_{T-1} (singular values or eigenvalues, any
order within a row), times (T,) in training steps; spacing may be uneven.

Pipeline (every parameter is a declared argument of analyse(); defaults in PARAMS):
  1. STRIP outliers BEFORE unfolding: the top_k largest levels of each checkpoint are removed (Will 2026-10-01: strip
     before unfolding), leaving n_eff = n - top_k levels per checkpoint.
  2. UNFOLD each checkpoint against ITS OWN smoothed integrated density: Gaussian-CDF kernel smoothing of the staircase
     with per-level bandwidth b_j = kde_c * local spacing (x_{j+5} - x_{j-5}) / 10 -- the IDENTICAL formula to
     stage2_g7.unfold("kde", c) used by s3stats. This removes the collective drift (Frobenius growth, spike,
     lower-decile shape) so that only the RELATIVE motion of levels is read as velocity (PARAMETRIC_DYNAMICS_PLAN
     §3, warning 11). DEFAULT kde_c = 32 (the s3stats long-range setting), NOT the Stage 3 kde(4): measured against
     the oracle (fixed semicircle CDF) on a beta = 1 series of 3001 per-step checkpoints, per-checkpoint kde
     unfolding injects velocity noise var(v_kde - v_oracle)/var(v_oracle) = 13% at c = 4, 8% at 8, 4-5% at 16,
     2% at 32, and inflates median |k| from the exact 0.577 to 0.651 / 0.624 / 0.604 / 0.594 (compare_oracle;
     verify_pdyn). A non-monotone unfolding is refused (> nonpos_max non-positive spacings -> RuntimeError).
  3. BAND: keep unfolded levels of rank quantile [band[0], band[1]) of the n_eff levels (edge margin); per checkpoint the
     in-band levels are CENTRED on the band mean (one common-mode translation removed), and ONE time-averaged factor
     (nb-1)/mean_t(span) sets unit mean spacing (Delta = 1). Rejected (2026-10-01): pinning the end levels per
     checkpoint (froze two levels' motion) and a per-checkpoint slope/span rescaling (a random dilation of ~4e-4 per
     checkpoint, i.e. ~0.1 spacing at the band edge, comparable to x_step). The relative sd of the span is reported
     (unfold.span_rel_sd) as the dilation that a per-checkpoint rescale WOULD have injected. Levels are tracked by sorted index
     within the band -- deliberate: eigenvalue-only, no vectors; for beta >= 1 levels do not cross so sorted index IS
     the adiabatic label; for an uncorrelated (Poisson) walk crossings appear as kinks, which is part of what
     distinguishes it.
  4. WINDOWS: statistics are computed per declared time window [a, b) (default [0, 500) and [500, 3001): the real grid
     changes cadence at step 500) and NEVER pooled across windows unless pool=True (Will 2026-10-01).
  5. VELOCITY v_i(t_{k+1/2}) = (e_i(t_{k+1}) - e_i(t_k)) / (t_{k+1} - t_k) at interval midpoints (uneven spacing is
     exact here). Time is rescaled by the RMS velocity: x = t * sqrt(<v^2>_i) / Delta with Delta = 1, where <v^2>_i
     is the LOCAL mean square velocity of the window (time-mean v^2 per level, cubic least-squares fit against band
     index, v2_deg = 3): after unfolding, <v^2> varies across the band as the local density squared, and a band-mean scale
     biases k by rho_i^2/<rho^2> (found on the MP-shaped singular-value density: mean |k| 1.15 instead of 1 at
     per-step cadence; fixed 2026-10-01). x_step = dt * v_rms (band mean) is the mean level displacement per
     interval in spacings. Reported: skew, excess kurtosis, KS distance vs a Gaussian with the sample mean/sd, n.
  6. VELOCITY AUTOCORRELATION C(x) = <v(x') v(x'+x)> / <v^2> over all pairs of intervals of the same level, binned in
     rescaled lag x (bin width xbin up to xmax); also C by lag index (C_lag[j], used by the shuffle check). The
     Simons-Altshuler reference curve is NOT a remembered formula: pdyn_calib produces it from a beta = 1 draw and
     verify_pdyn compares two independent draws.
  7. CURVATURE K_i(t_k) = d^2 e_i / dt^2 by the three-point uneven-grid second difference at interior checkpoints:
       K = 2 [ (e_{k+1} - e_k)/dt_k - (e_k - e_{k-1})/dt_{k-1} ] / (dt_k + dt_{k-1}).
     Dimensionless curvature  k = Delta * K / (pi * beta * <v^2>)   with Delta = 1 and <v^2> the window's measured
     mean square velocity. Zakrzewski-Delande form  P_beta(k) = C_beta (1 + k^2)^{-(beta+2)/2},
       C_1 = 1/2,  C_2 = 2/pi,  C_4 = 8/(3 pi)   (C_beta = Gamma(nu)/(sqrt(pi) Gamma(nu - 1/2)), nu = (beta+2)/2).
     SOURCE VERIFICATION (2026-10-01; the 1993 paper is paywalled): Fyodorov, arXiv:1108.0950 (Acta Phys. Pol. A 120,
     100 (2012)), read from ar5iv. His eqs (4), (6): lambda_m(t) = lambda_m + t v_m + t^2 C_m, C_m = sum_{n != m}
     |W_mn|^2 / (lambda_m - lambda_n), so C = K/2; eq (7): C_typ = pi rho(mu) y_typ, y_typ = Tr W^2 / N, with rho the
     unit-normalised density; eq (40): the Zakrzewski-Delande GUE distribution P(c) = (2/pi) kappa^3 /
     [(c - c_0)^2 + kappa^2]^2 for c = C/C_typ, kappa = pi rho y = 1, c_0 = x y / 2 (the smooth global-curvature
     offset, which per-checkpoint unfolding removes). For GUE, <v^2> = <|W_mm|^2> = y_typ/N and the mean spacing is
     Delta = 1/(N rho), hence  pi*beta*<v^2>/Delta = 2 pi rho y_typ = 2 C_typ  and  k = K/(2 C_typ) = C/C_typ = c:
     Fyodorov's eq (40) IS  P(k) = (2/pi)(1+k^2)^{-2}  with  k = Delta K / (pi beta <v^2>), beta = 2.  For beta = 1
     the same scale follows from the small-spacing tail (GOE p(s) ~ (pi^2/6) s/Delta^2, K ~ 2 W_mn^2 / s,
     <v^2> = <W_mm^2> = 2 <W_mn^2> for real Haar vectors): P(K) -> gamma^2/(2 K^3) with gamma = pi <v^2>/Delta, i.e.
     C_1 = 1/2 and the same k. von Oppen's PRL 73, 798 (1994) abstract states the same scaling, k = K/(pi beta rho
     <(dE/dlambda)^2>) with rho = 1/Delta (APS page returned 403; the statement is from the search engine's rendering
     of the abstract). RESULT: the addendum's memory version k = Delta*K/(pi*beta*<v^2>), P ~ (1+k^2)^{-(beta+2)/2}
     MATCHES the sources; the normalisation constants above are the exact ones; the calibrator (verify_pdyn (a))
     checks numerically that a beta = 1 draw gives the free-scale fit gamma_hat ~ 1 and nu_hat ~ 3/2.
     Fitted: nu_hat by maximum likelihood in the family C_nu (1+k^2)^{-nu} with the scale FIXED at the ZD value
     (the prediction has no free scale), optionally truncated to |k| < k_cut (the finite-difference curvature cannot
     resolve the tail beyond |k| ~ 1/(pi x_step); the truncated likelihood is normalised on the window); and (nu, gamma)
     with a free scale as a diagnostic. Also KS distance to P_beta, tail fractions P(|k| > 1, 2, 5), mean |k| (exactly
     1 for beta = 1 under this scaling, 2/pi for beta = 2), median |k| (exactly 1/sqrt(3) = 0.5774 for beta = 1; a
     beta = 2 process read with the beta = 1 scale has k doubled: median 0.879, mean 4/pi), skew / excess kurtosis of
     k (ZD: infinite; a Gaussian curvature law -- the literal DBM -- gives ~0), the k median/mean.
     At finite cadence the finite-difference curvature is the velocity CHANGE over ~2 x_step, not the instantaneous
     curvature: the tail beyond |k| ~ 1/(pi x_step) is lost and the body broadens, so the analytic ZD law is
     recovered only as x_step -> 0 (per-step sampling in the cadence study); at the real cadence every curvature
     statistic is compared with the beta = 1 calibrator at the SAME cadence and x_step, never with the formula.
  8. Per-window results are dicts; save() writes an npz (curves) + json (scalars). CLI: python pdyn_m2.py in.npz out
     where in.npz has 'spectra' (T, n) and 'times' (T,).
"""
import sys, json
from pathlib import Path
import numpy as np
from scipy.special import ndtr, gammaln, hyp2f1
from scipy import optimize, integrate, stats

PARAMS = dict(top_k=16, band=(0.10, 0.90), kde_c=32.0, beta=1, nonpos_max=1e-3, xbin=0.1, xmax=3.0, max_lag=12,
              min_pairs=10, v2_deg=3, k_cut="auto", windows=((0, 500), (500, 3001)), pool=False)
EST = "pdyn_m2-v1"


# ---------------------------------------------------------------- unfolding
def kde_unfold(x, c):
    """stage2_g7.unfold('kde', c) verbatim: staircase smoothed by Gaussian CDFs with adaptive per-level bandwidth."""
    x = np.sort(np.asarray(x, dtype=np.float64)); n = len(x); k = 5
    j = np.arange(n)
    loc = (x[np.minimum(j + k, n - 1)] - x[np.maximum(j - k, 0)]) / (np.minimum(j + k, n - 1) - np.maximum(j - k, 0))
    b = np.maximum(c * loc, 1e-300)
    return ndtr((x[:, None] - x[None, :]) / b[None, :]).sum(1)


def unfold_series(spectra, top_k, band, kde_c, nonpos_max, cdf=None):
    """(T, n) raw levels -> (T, nb) unfolded in-band levels at unit mean spacing. cdf: an ORACLE unfolding (a fixed
    CDF of the stripped spectrum, synthetic checks only) used in place of the per-checkpoint kde."""
    S = np.asarray(spectra, dtype=np.float64)
    T, n = S.shape
    S = np.sort(S, axis=1)[:, :n - top_k] if top_k > 0 else np.sort(S, axis=1)        # strip top-K BEFORE unfolding
    n_eff = S.shape[1]
    a, b = int(np.ceil(band[0] * n_eff)), int(np.ceil(band[1] * n_eff))
    E = np.empty((T, b - a)); nonpos = 0; tot = 0; spans = np.empty(T)
    for t in range(T):
        u = kde_unfold(S[t], kde_c) if cdf is None else cdf(S[t]) * n_eff
        d = np.diff(u); nonpos += int((d <= 0).sum()); tot += len(d)
        e = u[a:b]
        E[t] = e - e.mean()                                  # centre only (one common-mode translation per checkpoint)
        spans[t] = e[-1] - e[0]
    E *= (b - a - 1) / spans.mean()                          # ONE time-averaged scale -> unit mean spacing, no per-checkpoint dilation
    if nonpos > nonpos_max * tot:
        raise RuntimeError(f"non-monotone unfolding: {nonpos}/{tot} non-positive spacings (kde_c={kde_c})")
    return E, dict(n=n, n_eff=n_eff, nb=b - a, band_idx=(a, b), nonpos_frac=nonpos / max(tot, 1),
                   span_rel_sd=float(spans.std() / spans.mean()))


# ---------------------------------------------------------------- kinematics
def velocities(E, t):
    dt = np.diff(t)
    return np.diff(E, axis=0) / dt[:, None], 0.5 * (t[1:] + t[:-1]), dt


def curvatures(E, t):
    dt = np.diff(t)
    v = np.diff(E, axis=0) / dt[:, None]
    K = 2.0 * (v[1:] - v[:-1]) / (dt[1:] + dt[:-1])[:, None]
    return K, t[1:-1]


def velocity_stats(v):
    z = v.ravel(); z = (z - z.mean()) / z.std()
    return dict(n=int(z.size), skew=float(stats.skew(z)), ex_kurt=float(stats.kurtosis(z)),
                ks_gauss=float(stats.kstest(z, "norm").statistic))


def local_v2(v, deg):
    """Position-dependent mean square velocity: time-mean of v^2 per level, then a degree-`deg` least-squares
    polynomial fit against band index IN LINEAR SPACE (unbiased for the mean; deg = 0 -> the band mean), floored at
    0.1 x the band mean. After unfolding, <v^2> varies across the band as the local density squared, so the ZD scale
    and the SA time rescaling are LOCAL: k_i = K_i / (pi beta <v^2>_i), x_i = t sqrt(<v^2>_i). Rejected variants
    (2026-10-01): a 33-level moving average (25% noise when the window holds ~1 correlation time, scattering the
    curvature scale by +-20% between seeds) and a fit in log space (with ~1 independent time sample per level the
    per-level mean is ~chi^2_1 and E[log chi^2_1] = -1.27 biases exp(fit) low by up to 0.28; C_lag[1] read > 1)."""
    m = (v * v).mean(axis=0); i = np.linspace(-1, 1, len(m))
    if deg <= 0: return np.full(len(m), m.mean())
    f = np.polynomial.Polynomial.fit(i, m, deg)(i)
    return np.maximum(f, 0.1 * m.mean())


def autocorr(v, tmid, v2loc, xbin, xmax, max_lag, min_pairs):
    """C(x) = <v(t) v(t+lag)>_i / <v^2>_i binned in the LOCAL rescaled lag x = |dt| sqrt(<v^2>_i), and C_lag by index
    lag; same-level pairs only. Bins with fewer than min_pairs (level, time-pair) samples are NaN."""
    T1, nb = v.shape
    vr = np.sqrt(v2loc)
    edges = np.arange(0, xmax + xbin, xbin); nbin = len(edges) - 1
    acc = np.zeros(nbin); cnt = np.zeros(nbin, int)
    L = min(max_lag, T1 - 1); Clag = np.zeros(L + 1); Clag[0] = 1.0; xlag = np.zeros(L + 1)
    for j in range(1, T1):
        dtj = (tmid[j:] - tmid[:-j])                      # (T1-j,)
        c = (v[j:] * v[:-j]) / v2loc[None, :]             # (T1-j, nb)
        x = dtj[:, None] * vr[None, :]
        idx = np.digitize(x.ravel(), edges) - 1; ok = (idx >= 0) & (idx < nbin)
        acc += np.bincount(idx[ok], weights=c.ravel()[ok], minlength=nbin); cnt += np.bincount(idx[ok], minlength=nbin)
        if j <= L:
            Clag[j] = c.mean(); xlag[j] = x.mean()
    Cx = np.where(cnt >= min_pairs, acc / np.maximum(cnt, 1), np.nan)
    return dict(x=0.5 * (edges[1:] + edges[:-1]), C=Cx, n_pairs=cnt, C_lag=Clag, x_lag=xlag)


# ---------------------------------------------------------------- Zakrzewski-Delande fits
def zd_logC(nu):
    return gammaln(nu) - 0.5 * np.log(np.pi) - gammaln(nu - 0.5)


def zd_pdf(k, beta=1, gamma=1.0):
    nu = (beta + 2) / 2
    return np.exp(zd_logC(nu)) / gamma * (1 + (k / gamma) ** 2) ** (-nu)


def zd_cdf(k, beta=1, gamma=1.0):
    """int_0^k (1+u^2)^{-nu} du = k 2F1(1/2, nu; 3/2; -k^2) (vectorised, exact)."""
    nu = (beta + 2) / 2
    z = np.atleast_1d(np.asarray(k, float)) / gamma
    return 0.5 + np.exp(zd_logC(nu)) * z * hyp2f1(0.5, nu, 1.5, -z ** 2)


def hill_tail(k, k0):
    """Pareto MLE on |k| > k0: P(|k| > x) ~ x^{-alpha}; density exponent -(alpha+1); ZD: alpha = beta + 1
    (equivalently nu = (alpha + 1)/2). Returns (alpha_hat, se, n_tail)."""
    a = np.abs(np.asarray(k, float).ravel()); a = a[a > k0]
    if len(a) < 10: return float("nan"), float("nan"), int(len(a))
    al = len(a) / np.log(a / k0).sum()
    return float(al), float(al / np.sqrt(len(a))), int(len(a))


def _trunc_mass(nu, gamma, k_cut):
    return 2 * integrate.quad(lambda u: np.exp(zd_logC(nu)) / gamma * (1 + (u / gamma) ** 2) ** (-nu), 0, k_cut)[0]


def fit_nu(k, k_cut=None, free_scale=False):
    """MLE of nu in C_nu (1+(k/gamma)^2)^{-nu}; gamma fixed at 1 (ZD scale) unless free_scale; optional truncation
    |k| < k_cut (likelihood renormalised on the window). Returns (nu_hat, gamma_hat, se_nu, n_used)."""
    k = np.asarray(k, float).ravel()
    if k_cut is not None:
        k = k[np.abs(k) < k_cut]
    n = len(k)

    def nll(p):
        nu = p[0]; g = p[1] if free_scale else 1.0
        if nu <= 0.55 or g <= 1e-6: return 1e30
        ll = zd_logC(nu) - np.log(g) - nu * np.log1p((k / g) ** 2)
        s = ll.sum()
        if k_cut is not None:
            s -= n * np.log(_trunc_mass(nu, g, k_cut))
        return -s
    p0 = [1.5, 1.0] if free_scale else [1.5]
    r = optimize.minimize(nll, p0, method="Nelder-Mead", options=dict(xatol=1e-5, fatol=1e-6, maxiter=2000))
    nu = float(r.x[0]); g = float(r.x[1]) if free_scale else 1.0
    h = 1e-3
    f0 = nll(r.x); fp = nll(r.x + np.eye(len(r.x))[0] * h); fm = nll(r.x - np.eye(len(r.x))[0] * h)
    d2 = (fp - 2 * f0 + fm) / h ** 2
    se = float(1 / np.sqrt(d2)) if d2 > 0 else float("nan")
    return nu, g, se, n


def curvature_stats(K, v2loc, beta, k_cut=None):
    k = (K / (np.pi * beta * v2loc[None, :])).ravel()
    nu_f, _, se_f, n = fit_nu(k)
    nu_g, g_g, se_g, _ = fit_nu(k, free_scale=True)
    out = dict(n=int(n), k_mean=float(k.mean()), k_median=float(np.median(k)), abs_k_mean=float(np.abs(k).mean()),
               abs_k_median=float(np.median(np.abs(k))), k_skew=float(stats.skew(k)), k_ex_kurt=float(stats.kurtosis(k)),
               tail_gt1=float((np.abs(k) > 1).mean()), tail_gt2=float((np.abs(k) > 2).mean()),
               tail_gt5=float((np.abs(k) > 5).mean()), nu_fixed=nu_f, nu_fixed_se=se_f, nu_free=nu_g, gamma_free=g_g,
               nu_free_se=se_g, ks_zd=float(stats.kstest(k, lambda x: zd_cdf(x, beta)).statistic))
    for k0 in (1.0, 2.0):
        al, se, nt = hill_tail(k, k0)
        out[f"hill_alpha_k0_{k0:g}"] = al; out[f"hill_alpha_se_k0_{k0:g}"] = se; out[f"hill_n_k0_{k0:g}"] = nt
    if k_cut is not None:
        nu_t, _, se_t, n_t = fit_nu(k, k_cut=k_cut)
        out.update(k_cut=float(k_cut), nu_trunc=nu_t, nu_trunc_se=se_t, n_trunc=int(n_t))
    hist, edges = np.histogram(k, bins=np.linspace(-8, 8, 81), density=True)
    out["hist"] = hist; out["hist_edges"] = edges
    return out, k


# ---------------------------------------------------------------- driver
def analyse_window(E, t, beta, xbin, xmax, max_lag, k_cut, min_pairs, v2_deg):
    v, tmid, dt = velocities(E, t)
    v2loc = local_v2(v, v2_deg)
    v2 = float((v * v).mean()); vrms = np.sqrt(v2)
    K, tK = curvatures(E, t)
    if k_cut == "auto":
        k_cut = 1.0 / (np.pi * float((dt * vrms).max()))        # FD resolution of the curvature tail (declared)
    cs, k = curvature_stats(K, v2loc, beta, k_cut)
    return dict(T=int(len(t)), t0=float(t[0]), t1=float(t[-1]), v2=v2, vrms=vrms, x_step=dt * vrms,
                x_step_mean=float((dt * vrms).mean()), x_step_max=float((dt * vrms).max()),
                v2_local_min=float(v2loc.min()), v2_local_max=float(v2loc.max()), v2_local=v2loc,
                velocity=velocity_stats(v), autocorr=autocorr(v, tmid, v2loc, xbin, xmax, max_lag, min_pairs),
                curvature=cs, k_samples=k)


def analyse(spectra, times, **kw):
    p = dict(PARAMS); p.update(kw)
    times = np.asarray(times, float)
    order = np.argsort(times); times = times[order]; spectra = np.asarray(spectra)[order]
    E, info = unfold_series(spectra, p["top_k"], p["band"], p["kde_c"], p["nonpos_max"])
    out = dict(params={k: (list(v) if isinstance(v, tuple) else v) for k, v in p.items()}, unfold=info, est=EST, windows={})
    wins = [tuple(w) for w in p["windows"]]
    if p["pool"]:
        wins = [(float(times[0]), float(times[-1]) + 1)]
    for a, b in wins:
        m = (times >= a) & (times < b)
        if m.sum() < 4:
            out["windows"][f"[{a},{b})"] = dict(status="INAPPLICABLE", T=int(m.sum()))
            continue
        out["windows"][f"[{a},{b})"] = analyse_window(E[m], times[m], p["beta"], p["xbin"], p["xmax"], p["max_lag"], p["k_cut"],
                                                       p["min_pairs"], p["v2_deg"])
    out["unfolded"] = E; out["times"] = times
    return out


def compare_oracle(spectra, times, cdf, **kw):
    """Synthetic checks only: per-checkpoint kde unfolding vs the ORACLE fixed CDF of the same stripped spectrum.
    Returns the velocity-field correlation, the variance ratio, and the kde-induced velocity noise fraction
    var(v_kde - v_oracle)/var(v_oracle), plus median |k| under both, per window."""
    p = dict(PARAMS); p.update(kw)
    times = np.asarray(times, float); order = np.argsort(times); times = times[order]; spectra = np.asarray(spectra)[order]
    Ek, _ = unfold_series(spectra, p["top_k"], p["band"], p["kde_c"], p["nonpos_max"])
    Eo, _ = unfold_series(spectra, p["top_k"], p["band"], p["kde_c"], p["nonpos_max"], cdf=cdf)
    out = {}
    for a, b in [tuple(x) for x in p["windows"]]:
        m = (times >= a) & (times < b)
        if m.sum() < 4: continue
        vk, _, _ = velocities(Ek[m], times[m]); vo, _, _ = velocities(Eo[m], times[m])
        rk = analyse_window(Ek[m], times[m], p["beta"], p["xbin"], p["xmax"], p["max_lag"], None, p["min_pairs"], p["v2_deg"])
        ro = analyse_window(Eo[m], times[m], p["beta"], p["xbin"], p["xmax"], p["max_lag"], None, p["min_pairs"], p["v2_deg"])
        out[f"[{a},{b})"] = dict(corr=float(np.corrcoef(vk.ravel(), vo.ravel())[0, 1]), var_ratio=float(vk.var() / vo.var()),
                                noise_frac=float(((vk - vo) ** 2).mean() / (vo ** 2).mean()),
                                med_k_kde=rk["curvature"]["abs_k_median"], med_k_oracle=ro["curvature"]["abs_k_median"],
                                nu_fixed_kde=rk["curvature"]["nu_fixed"], nu_fixed_oracle=ro["curvature"]["nu_fixed"],
                                C_lag1_kde=float(rk["autocorr"]["C_lag"][1]), C_lag1_oracle=float(ro["autocorr"]["C_lag"][1]),
                                x_step=rk["x_step_mean"])
    return out


def _scalars(d):
    if isinstance(d, dict):
        return {k: _scalars(v) for k, v in d.items() if not isinstance(v, np.ndarray)}
    if isinstance(d, (np.floating, np.integer)):
        return d.item()
    return d


def save(res, out):
    out = Path(out)
    json.dump(_scalars(res), open(out.with_suffix(".json"), "w"), indent=1)
    arrs = {"unfolded": res["unfolded"], "times": res["times"]}
    for w, r in res["windows"].items():
        if "autocorr" in r:
            for key in ("x", "C", "n_pairs", "C_lag", "x_lag"):
                arrs[f"{w}/autocorr/{key}"] = r["autocorr"][key]
            arrs[f"{w}/k_samples"] = r["k_samples"]; arrs[f"{w}/x_step"] = r["x_step"]; arrs[f"{w}/v2_local"] = r["v2_local"]
            arrs[f"{w}/hist"] = r["curvature"]["hist"]; arrs[f"{w}/hist_edges"] = r["curvature"]["hist_edges"]
    np.savez_compressed(out.with_suffix(".npz"), **arrs)


def summary_lines(res):
    L = []
    for w, r in res["windows"].items():
        if r.get("status"):
            L.append(f"{w}: {r['status']} (T={r['T']})"); continue
        vs, cs = r["velocity"], r["curvature"]
        L.append(f"{w}: T={r['T']} vrms={r['vrms']:.4g} x_step mean/max={r['x_step_mean']:.3f}/{r['x_step_max']:.3f} | "
                 f"v: skew={vs['skew']:+.3f} exkurt={vs['ex_kurt']:+.3f} KS={vs['ks_gauss']:.3f} | "
                 f"C_lag1={r['autocorr']['C_lag'][1]:+.3f} | k: <|k|>={cs['abs_k_mean']:.3f} med|k|={cs['abs_k_median']:.3f} "
                 f"exkurt={cs['k_ex_kurt']:.1f} nu_fixed={cs['nu_fixed']:.3f}"
                 f"±{cs['nu_fixed_se']:.3f} nu_free={cs['nu_free']:.3f} gamma={cs['gamma_free']:.3f} KS_ZD={cs['ks_zd']:.3f} "
                 f"P(|k|>2)={cs['tail_gt2']:.4f} hill_a(k0=1)={cs['hill_alpha_k0_1']:.2f}±{cs['hill_alpha_se_k0_1']:.2f}"
                 + (f" nu_trunc(|k|<{cs['k_cut']:.2f})={cs['nu_trunc']:.3f}±{cs['nu_trunc_se']:.3f}" if "nu_trunc" in cs else ""))
    return L


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--top-k", type=int, default=PARAMS["top_k"]); ap.add_argument("--kde-c", type=float, default=PARAMS["kde_c"])
    ap.add_argument("--beta", type=int, default=PARAMS["beta"]); ap.add_argument("--band", type=float, nargs=2, default=PARAMS["band"])
    ap.add_argument("--windows", type=float, nargs="+", help="flat list a0 b0 a1 b1 ...")
    ap.add_argument("--pool", action="store_true"); ap.add_argument("--k-cut", default="auto", help="float, auto, or none")
    a = ap.parse_args()
    z = np.load(a.inp)
    kc = None if a.k_cut == "none" else ("auto" if a.k_cut == "auto" else float(a.k_cut))
    kw = dict(top_k=a.top_k, kde_c=a.kde_c, beta=a.beta, band=tuple(a.band), pool=a.pool, k_cut=kc)
    if a.windows:
        kw["windows"] = tuple(zip(a.windows[::2], a.windows[1::2]))
    res = analyse(z["spectra"], z["times"], **kw)
    save(res, a.out)
    print("\n".join(summary_lines(res)))

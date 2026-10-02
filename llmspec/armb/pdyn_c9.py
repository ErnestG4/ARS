"""Attribution controls for the phase-1 P2 C(x) failure (PDYN_FINDINGS §4, candidates 1 and 2): C9 (beta = 1 motion plus
the REAL slow density drift) and the C1-driver (beta = 1 motion with an optimiser-like velocity time scale), each read
through the IDENTICAL sealed pipeline (pdyn_m2.analyse with PARAMS: top-16 stripped, kde(32), band [0.10, 0.90),
local <v^2> cubic) at the real cadence (the bank's W2 grid, every 25 steps over [500, 3000]) with vrms matched to the
real window (XSTEP_MATCH_TOL = 5 %, as the phase-1 runner). CPU only. Reads ONLY sig_<M> and rms_<M> of the bank
(never ipr_* / pt_* / U32 / V32) and the phase-1 parts (results/armb_pdyn_phase1/<arm>/parts/) for the real and C1
C(x) curves, the matched C1 tau and seeds (the C1 draws are regenerated bit-identically from (seed, tau, grid)).

C9 -- CONSTRUCTION (declared; the unfolding is untouched):
  1. Real slow component. For the window's T checkpoints, strip the top-16 of the real spectrum (as the pipeline does),
     sort ascending, L(k, t) = log sigma_(k)(t), k = 0..n_eff-1. Smooth in TIME with a Gaussian kernel of sd sigma_t
     steps (default 200: 2.3x the measured velocity decorrelation time of ~85 steps, PDYN_FINDINGS §2, so the beta = 1
     motion averages out while the lr-schedule-scale deformation is kept), then in RANK with a Gaussian kernel of sd
     h ranks (variants: 'smooth' h = 32 = the unfolding's own bandwidth; 'fine' h = 8; 'raw' h = 0), both kernels
     edge-normalised. Result Lslow(k, t): the real spectrum's slow log-quantile time course.
  2. Warp. A C1 draw (pdyn_calib.smooth_rect at the real shape, the phase-1 seed and tau) is stripped of its own top-16,
     each level is mapped to its POOLED quantile u = F_syn(sigma) (the time-mean empirical CDF of the stationary
     synthetic bulk, so a level's beta = 1 wandering becomes a wandering in u), and placed at the real slow quantile
     function of that checkpoint: sigma_C9_(k)(t) = exp(Lslow(u_k(t) n_eff - 1/2, t)) (linear interpolation in rank).
     Sixteen dummy outliers above the bulk are prepended so the pipeline's top-16 strip removes exactly them. The C9
     spectrum therefore has the real slow density (||W||_F, band edges, log-moments, the whole quantile function) at
     every checkpoint and the synthetic's beta = 1 relative motion in quantile (= unfolded) coordinates.
  3. 'zero' = the same warp with the time-MEAN Lslow (a fixed map, no drift): must read as C1 within noise (verify (i)).
     'scale' = the time-mean shape times the real ||W||_F(t) time course (a pure dilation): the unfolding is
     dilation-invariant (kde bandwidth = c x local spacing), so this must be C1 to rounding.
     'null' = Lslow extracted (same h, sigma_t) from an INDEPENDENT C1 draw that was itself warped by the time-mean real
     map: carries the extraction's residual (the motion that the time smoothing does not remove) but no real drift;
     the matched variant is read against it.
     'planted' = the 'zero' map plus a deterministic rank-structured drift delta log sigma = A x spacing_log(k) x
     sin(2 pi k / lambda) x (t - t_mid)/span with lambda = 24 ranks (below the kde bandwidth, so the unfolding cannot
     remove it) and amplitude A spacings end-to-end (verify (ii): the control CAN fire).
  4. vrms matching: the drift adds velocity, so tau is re-solved from vrms^2 = (v_c1 tau_c1 / tau)^2 + v_drift^2
     after the first pass (<= 3 passes), then the C9 draw is regenerated with the same seed.
  Drift diagnostics per matrix (reported): ||W||_F, band edges (10 % / 90 % index), log-moments of the band at the
  start/end of W2; edge motion in units of the time-mean spacing; and the part of the slow deformation that SURVIVES
  the unfolding: unfold exp(Lslow) alone (no motion) with the sealed unfolding -> rms displacement of the index-tracked
  unfolded levels over the window (spacings) and its velocity rms relative to the real vrms.

C1-DRIVER -- CONSTRUCTION (declared): W(t) = W(0) + int_0^t M(s) ds, W(0) iid N(0, 1) at the real shape, M an iid
  Ornstein-Uhlenbeck (momentum) matrix process with time constant tau_v steps and stationary entry variance s_M^2:
  dM = -M/tau_v dt + s_M sqrt(2/tau_v) dB. Exact joint Gaussian step over each (uneven) interval:
  M' = e^{-a} M + xi_M, W' = W + tau_v (1 - e^{-a}) M + xi_W, a = dt/tau_v, Var xi_M = s^2 (1 - e^{-2a}),
  Var xi_W = 2 s^2 tau_v^2 [a - 2(1 - e^{-a}) + (1 - e^{-2a})/2], Cov = s^2 tau_v [2(1 - e^{-a}) - (1 - e^{-2a})]
  (series for a < 1e-2). The matrix velocity decorrelates in tau_v (Adam beta_1 = 0.9 -> ~10 steps, Muon momentum 0.95
  -> ~20). After every step W is projected back to its initial Frobenius norm (a weight-decay-like pure dilation,
  EXACTLY invisible to the sealed unfolding -- kde bandwidth = c x local spacing -- which keeps vrms stationary over
  the window; without it the entry variance grows by 2 s^2 tau_v t, a 40 % dilation at tau_v = 80 that halves the
  per-spacing velocity across W2). Limits: tau_v = 0 is the literal DBM (white increments; phase-0 known answer: no SA
  structure; verify (iii) checks it against pdyn_calib.dbm_sym(rect) at the same x_step); tau_v = 'c1' = the matched C1
  tau of the matrix (the smooth GP's own velocity correlation time, ~400-600 steps) is the C1-like reference the OU
  driver is read against (verify (iii-b)). tau_v = inf (constant velocity W(0) + t M(0)) is NOT a Simons-Altshuler
  limit at n = 512: 44 spacings of travel over W2 means t M(0) dominates W(0) (measured dev 26; kept out of the sweep).
  s_M is matched to the real vrms (vrms is proportional to s_M; <= 3 passes, same seed).

COMPARISON (the runner's, pdyn_phase1.verdict_p2): dev_Cx = max over bins x <= 2 with >= min_pairs (10) on both
  curves of |C_ctl(x) - C_ref(x)| / 0.15, dev_Clag = max_{j <= 6} |C_lag| difference / 0.10 (TOL = the declared
  calibrator spread), against the REAL curve and against the phase-1 C1 seed-mean curve -- both REPORTED as the runner
  computes them. Measured on the first unit: the runner's dev_Cx is set by the sparse bins x < 0.3 (63-400 pairs: the
  band-edge levels with small local <v^2>), e.g. the same C1 draw warped by a FIXED map differs from itself by 0.14
  there and by 0.008 on C_lag[1..6]. The WORDS below are therefore taken on dev_Clag and on dev_Cx_dense = the same
  statistic restricted to bins with >= DENSE_PAIRS (1000) pairs on both curves (declared here, before the full run):
  REPRODUCES  : max(dev_Clag, dev_Cx_dense vs real) <= 1
  STAYS AT C1 : else, max(dev_Clag, dev_Cx_dense vs C1) <= 1
  OVERSHOOTS  : else, the control's dip depth (min C over DENSE bins, 0.3 <= x <= 2) is shallower than the real one by
                more than 0.15, or its C_lag[1] exceeds the real C_lag[1] by more than 0.10
  PARTIAL     : else, every dense bin of the control lies between C1 and the real curve within 0.15
  OFF-CURVE   : otherwise.
  Also reported per control: velocity skew / excess kurtosis / KS, median |k| (PROVISIONAL at bank cadence), C_lag[1],
  C_lag[2], dip depth and position, measured vrms / target.

CLI: python pdyn_c9.py [--arms A0 M0s1] [--layers 0 2 5] [--types Q K O MLP_OUT] [--taus 5 10 20 40 80]
     [--variants smooth fine raw] [--planted-amp 50] [--out results/armb_pdyn_c9] [--workers 5] [--nseed 2]
     (--taus accepts '0' = literal DBM, 'c1' = the matrix's matched C1 tau, 'inf' = constant velocity)
Outputs: <out>/<arm>/L<LL>_<M>.json (+ .npz curves), <out>/summary.json, <out>/table.csv, <out>/table.md; resumable
per unit (the unit json is the resume unit; --force recomputes).
"""
import os, sys


def _early_threads():
    argv = sys.argv; w = 1
    for i, a in enumerate(argv):
        if a == "--workers" and i + 1 < len(argv): w = int(argv[i + 1])
        elif a.startswith("--workers="): w = int(a.split("=", 1)[1])
    if w > 1 or "--blas-threads" in argv:
        nt = "1"
        if "--blas-threads" in argv: nt = argv[argv.index("--blas-threads") + 1]
        for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[k] = nt


_early_threads()
import argparse, json, time, math, traceback, warnings  # noqa: E402
from pathlib import Path  # noqa: E402
from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402
import numpy as np  # noqa: E402
from scipy.linalg import svd  # noqa: E402

HERE = Path(__file__).resolve().parent
LLMSPEC = HERE.parent
sys.path.insert(0, str(HERE))
import pdyn_m2 as M2, pdyn_calib as C  # noqa: E402

EST = "pdyn_c9-v1"
TYPES = ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT")
WINDOWS = {"W1": (0.0, 500.0), "W2": (500.0, 3001.0)}
ALLOWED_PREFIXES = ("sig_", "rms_")                                   # the ONLY bank keys this module reads
TOP_K = M2.PARAMS["top_k"]
TOL = dict(C_lag=0.10, Cx=0.15, n_lag=6, x_max=2.0)                  # pdyn_phase1.TOL (C(x) part)
XSTEP_MATCH_TOL = 0.05
MIN_PAIRS = M2.PARAMS["min_pairs"]
DENSE_PAIRS = 1000                                                    # bins that carry the word (declared; see docstring)
VARIANTS = dict(smooth=dict(h=32.0, sigma_t=200.0), fine=dict(h=8.0, sigma_t=200.0), raw=dict(h=0.0, sigma_t=200.0))
PLANTED_LAMBDA = 24.0
DIP_RANGE = (0.3, 2.0)
PHASE1 = LLMSPEC / "results" / "armb_pdyn_phase1"
DEFAULT_OUT = LLMSPEC / "results" / "armb_pdyn_c9"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ====================================================================== bank access (sig / rms only)
def _get(z, key):
    if not key.startswith(ALLOWED_PREFIXES):
        raise PermissionError(f"key {key!r} is not in the allowed set {ALLOWED_PREFIXES}")
    return z[key]


def load_real(bank, arm, layer, M, window="W2"):
    """Steps from the phase-1 part json (the bank steps the runner used), restricted to the window; sig (T, n) and
    rms (T,). Shape from the part json."""
    pj = PHASE1 / arm / "parts" / f"L{layer:02d}_{M}.json"
    part = json.load(open(pj))
    a, b = WINDOWS[window]
    steps = [int(s) for s in part["steps"] if a <= s < b]
    sig, rms = [], []
    for s in steps:
        with np.load(Path(bank) / arm / f"step{s:05d}" / f"L{layer:02d}.npz") as z:
            sig.append(np.asarray(_get(z, f"sig_{M}"), np.float64)); rms.append(float(_get(z, f"rms_{M}")))
    return dict(sig=np.array(sig), rms=np.array(rms), times=np.array(steps, float), shape=tuple(int(x) for x in part["shape"]),
                n=int(part["n_levels"]), part=part)


def phase1_curves(arm, layer, M, window="W2"):
    """The real C(x) and the C1 seed-mean curve exactly as verdict_p2 read them, plus the C1 match (seeds, tau)."""
    pj = PHASE1 / arm / "parts" / f"L{layer:02d}_{M}.json"; pn = pj.with_suffix(".npz")
    part = json.load(open(pj)); z = np.load(pn)
    W = part["windows"][window]; ctl = W["controls"]; c1 = [s for s in ctl["families"]["c1"] if s.get("status") == "OK"]
    x = z[f"{window}/Cx_x"]
    Cs = [z[f"{window}/c1/Cx_C"]]; ns = [z[f"{window}/c1/Cx_n"]]
    for sd in range(1, len(c1)):
        if f"{window}/c1/Cx_C_s{sd}" in z: Cs.append(z[f"{window}/c1/Cx_C_s{sd}"]); ns.append(z[f"{window}/c1/Cx_n_s{sd}"])
    L = TOL["n_lag"]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        c1_mean = np.nanmean(np.array(Cs), axis=0)
    return dict(x=x, real=dict(C=z[f"{window}/Cx_C"], n=z[f"{window}/Cx_n"], C_lag=np.array(W["m2"]["C_lag"][:L + 1]), scalars=W["m2"]),
                c1=dict(C=c1_mean, n=np.min(np.array(ns), axis=0), C_lag=np.mean([s["C_lag"][:L + 1] for s in c1], axis=0),
                        seeds=c1, dt_ref=ctl["dt_ref"], v_target=ctl["v_target"]))


def c1_seed(layer, M, sd, window="W2"):
    """pdyn_phase1's seed formula (bit-identical regeneration of the phase-1 C1 draws)."""
    return 100000 * (sd + 1) + 1000 * layer + 10 * TYPES.index(M) + list(("W1", "W2", "W3")).index(window)


# ====================================================================== M2 single-window wrapper (runner's)
def m2_single(S, t, **kw):
    t = np.asarray(t, float)
    res = M2.analyse(S, t, windows=((float(t[0]), float(t[-1]) + 1.0),), **kw)
    return next(iter(res["windows"].values())), res


def scalars(r):
    if r.get("status"): return dict(status=r["status"], T=r["T"])
    cs = {k: v for k, v in r["curvature"].items() if not isinstance(v, np.ndarray)}
    return dict(status="OK", T=r["T"], vrms=r["vrms"], x_step_mean=r["x_step_mean"], velocity=r["velocity"],
                C_lag=[float(v) for v in r["autocorr"]["C_lag"]], x_lag=[float(v) for v in r["autocorr"]["x_lag"]],
                abs_k_median=cs["abs_k_median"], nu_fixed=cs["nu_fixed"], n_k=int(cs["n"]))


# ====================================================================== real slow component
def gauss_smooth(Y, coord, sd, axis):
    """Edge-normalised Gaussian kernel smoothing of Y along `axis` at coordinates `coord` (sd in coordinate units);
    sd <= 0 -> identity."""
    if sd <= 0: return np.array(Y, float)
    c = np.asarray(coord, float)
    Wt = np.exp(-0.5 * ((c[:, None] - c[None, :]) / sd) ** 2); Wt /= Wt.sum(1, keepdims=True)
    Y = np.asarray(Y, float)
    return np.tensordot(Wt, Y, axes=([1], [axis])) if axis == 0 else np.tensordot(Y, Wt, axes=([axis], [1]))


def strip_sort(S, top_k=TOP_K):
    S = np.sort(np.asarray(S, float), axis=1)
    return S[:, :S.shape[1] - top_k] if top_k > 0 else S


def slow_component(S_stripped, times, h, sigma_t):
    """Lslow (T, n_eff): log sigma per rank smoothed in time (sd sigma_t steps) then in rank (sd h ranks)."""
    LS = np.log(S_stripped)
    LT = gauss_smooth(LS, times, sigma_t, axis=0)
    return gauss_smooth(LT, np.arange(LS.shape[1], dtype=float), h, axis=1)


def pooled_quantile(S_stripped):
    """u = F_syn(sigma): the time-mean empirical CDF of the stationary synthetic bulk (pooled, mid-rank convention)."""
    pool = np.sort(S_stripped.ravel()); N = len(pool)
    def F(x):
        lo = np.searchsorted(pool, x, side="left"); hi = np.searchsorted(pool, x, side="right")
        return (0.5 * (lo + hi)) / N
    return F


def warp(S_syn, Lslow, F=None, top_k=TOP_K):
    """Map the synthetic bulk (top_k stripped) through u = F_syn(sigma) onto the slow quantile function of each
    checkpoint; prepend top_k dummy outliers above the bulk. Lslow may be (T, n_eff) or (n_eff,) (fixed map)."""
    Sb = strip_sort(S_syn, top_k); T, n_eff = Sb.shape
    if Lslow.ndim == 1: Lslow = np.broadcast_to(Lslow, (T, n_eff))
    assert Lslow.shape == (T, n_eff), (Lslow.shape, (T, n_eff))
    F = F or pooled_quantile(Sb)
    ranks = np.arange(n_eff, dtype=float)
    out = np.empty((T, n_eff + top_k))
    for t in range(T):
        u = np.clip(F(Sb[t]) * n_eff - 0.5, 0.0, n_eff - 1.0)
        bulk = np.exp(np.interp(u, ranks, Lslow[t]))
        out[t, :n_eff] = bulk
        out[t, n_eff:] = bulk.max() * (2.0 + np.arange(top_k))
    return out


def planted_field(n_eff, times, Lmean, amp, lam=PLANTED_LAMBDA):
    """delta log sigma (T, n_eff) = amp x local log-spacing x sin(2 pi k / lam) x (t - t_mid)/span: a rank-periodic
    deformation below the kde bandwidth, amp spacings end-to-end."""
    k = np.arange(n_eff, dtype=float)
    loc = np.gradient(Lmean)                                           # d log sigma per rank = local spacing in log units
    tt = (times - 0.5 * (times[0] + times[-1])) / (times[-1] - times[0])
    return amp * loc[None, :] * np.sin(2 * np.pi * k / lam)[None, :] * tt[:, None]


def drift_diagnostics(real, Lslow, times, h_label):
    """Drift magnitudes of the real window and the part of the slow deformation that survives the sealed unfolding."""
    S = strip_sort(real["sig"]); T, n_eff = S.shape
    a, b = int(np.ceil(M2.PARAMS["band"][0] * n_eff)), int(np.ceil(M2.PARAMS["band"][1] * n_eff))
    fro = np.sqrt((real["sig"] ** 2).sum(1)); lo = S[:, a]; hi = S[:, b - 1]
    sp = (hi - lo) / (b - a - 1); spm = float(sp.mean())
    band = np.log(S[:, a:b]); lm, lsd = band.mean(1), band.std(1)
    Ls = np.exp(Lslow)                                                 # the slow spectrum alone (no motion)
    E_slow, _ = M2.unfold_series(np.concatenate([Ls, Ls.max(1, keepdims=True) * (2 + np.arange(TOP_K))[None, :]], 1),
                                 M2.PARAMS["top_k"], M2.PARAMS["band"], M2.PARAMS["kde_c"], 1.0)
    d_slow = E_slow - E_slow.mean(0)
    v_slow = np.diff(E_slow, axis=0) / np.diff(times)[:, None]
    return dict(variant=h_label, T=int(T), n_eff=int(n_eff), band=[a, b],
                fro_start=float(fro[0]), fro_end=float(fro[-1]), fro_rel_change=float(fro[-1] / fro[0] - 1),
                edge10_start=float(lo[0]), edge10_end=float(lo[-1]), edge10_move_spacings=float((lo[-1] - lo[0]) / spm),
                edge90_start=float(hi[0]), edge90_end=float(hi[-1]), edge90_move_spacings=float((hi[-1] - hi[0]) / spm),
                spacing_mean=spm, spacing_rel_change=float(sp[-1] / sp[0] - 1),
                logmean_start=float(lm[0]), logmean_end=float(lm[-1]), logsd_start=float(lsd[0]), logsd_end=float(lsd[-1]),
                logsd_rel_change=float(lsd[-1] / lsd[0] - 1),
                unfolded_slow_drift_rms=float(np.sqrt((d_slow ** 2).mean())), unfolded_slow_drift_max=float(np.abs(d_slow).max()),
                unfolded_slow_vrms=float(np.sqrt((v_slow ** 2).mean())), unfolded_slow_vrms_over_real=float(np.sqrt((v_slow ** 2).mean()) / real["vrms"]))


# ====================================================================== families
def gen_c1(m, n, times, tau, seed):
    m, n = max(m, n), min(m, n)                                        # pdyn_phase1.gen_family convention
    return C.smooth_rect(m, n, times, tau, 1, seed)


def _ou_coefs(a):
    """(VarM, VarW, Cov) per unit s^2 and tau_v = 1 (multiply VarW by tau_v^2 and Cov by tau_v)."""
    if a < 1e-2:
        vm = 2 * a - 2 * a ** 2 + 4 * a ** 3 / 3 - 2 * a ** 4 / 3
        vw = 2 * (a ** 3 / 3 - a ** 4 / 4 + 7 * a ** 5 / 60)
        cv = a ** 2 - a ** 3 + 7 * a ** 4 / 12
    else:
        e1, e2 = -np.expm1(-a), -np.expm1(-2 * a)
        vm = e2; vw = 2 * (a - 2 * e1 + e2 / 2); cv = 2 * e1 - e2
    return vm, vw, cv


def gen_driver(m, n, times, tau_v, sM, seed, project_norm=True):
    """W(0) + integrated OU momentum (module docstring). tau_v = 0 -> literal DBM (increments sM sqrt(dt) z);
    tau_v = inf -> constant velocity W(0) + t M(0). project_norm: rescale W to its initial Frobenius norm after each
    step (pure dilation, invisible to the unfolding; keeps the per-spacing velocity stationary)."""
    m, n = max(m, n), min(m, n)
    rng = np.random.default_rng(seed)
    t = np.asarray(times, float)
    W = rng.standard_normal((m, n)); Mo = rng.standard_normal((m, n)) * sM
    F0 = np.linalg.norm(W)
    out = [svd(W, compute_uv=False)]
    for i in range(1, len(t)):
        dt = t[i] - t[i - 1]
        if tau_v == 0:
            W = W + sM * math.sqrt(dt) * rng.standard_normal((m, n))
        elif not np.isfinite(tau_v):
            W = W + dt * Mo
        else:
            a = dt / tau_v; vm, vw, cv = _ou_coefs(a)
            vw *= tau_v ** 2; cv *= tau_v
            z1 = rng.standard_normal((m, n)); z2 = rng.standard_normal((m, n))
            sw = math.sqrt(vw); xi_W = sM * sw * z1
            xi_M = sM * ((cv / sw) * z1 + math.sqrt(max(vm - cv ** 2 / vw, 0.0)) * z2)
            W = W + tau_v * (-math.expm1(-a)) * Mo + xi_W
            Mo = math.exp(-a) * Mo + xi_M
        if project_norm: W *= F0 / np.linalg.norm(W)
        out.append(svd(W, compute_uv=False))
    return np.array(out)


def match_scale(make, v_target, p0, passes=3, mode="prop", extra=None):
    """make(p) -> spectra; iterate p so the measured band vrms matches v_target within XSTEP_MATCH_TOL.
    mode 'prop': vrms proportional to p (driver s_M; C1 1/tau handled by the caller via 'inv').
    mode 'inv' : vrms proportional to 1/p plus an additive drift variance (C9): vrms^2 = A/p^2 + B."""
    p = float(p0); hist = []; S = r = res = None
    for it in range(1, passes + 1):
        S = make(p); r, res = m2_single(S, extra)
        v1 = float(r["vrms"]) if "vrms" in r else float("nan"); hist.append((p, v1))
        if not np.isfinite(v1) or v1 <= 0 or abs(v1 / v_target - 1) < XSTEP_MATCH_TOL: break
        if mode == "prop":
            p *= v_target / v1
        else:
            if len(hist) >= 2:                                         # two-point solve of v^2 = A/p^2 + B
                (pa, va), (pb, vb) = hist[-2], hist[-1]
                A_ = (va ** 2 - vb ** 2) / (1 / pa ** 2 - 1 / pb ** 2); B_ = va ** 2 - A_ / pa ** 2
                tgt = v_target ** 2 - B_
                p = math.sqrt(A_ / tgt) if (A_ > 0 and tgt > 0) else p * v1 / v_target
            else:
                p *= v1 / v_target
    return S, r, res, dict(p=float(p), passes=it, vrms_measured=v1, v_target=float(v_target),
                           matched=bool(np.isfinite(v1) and abs(v1 / v_target - 1) < XSTEP_MATCH_TOL), history=hist)


# ====================================================================== comparison
def dev_curves(Ca, na, Cb, nb, x, Clag_a, Clag_b, min_pairs=MIN_PAIRS):
    ok = (x <= TOL["x_max"]) & (na >= min_pairs) & (nb >= min_pairs) & np.isfinite(Ca) & np.isfinite(Cb)
    d_cx = float(np.max(np.abs(Ca[ok] - Cb[ok])) / TOL["Cx"]) if ok.any() else float("nan")
    L = min(TOL["n_lag"], len(Clag_a) - 1, len(Clag_b) - 1)
    d_lag = float(np.max(np.abs(np.asarray(Clag_a[1:L + 1]) - np.asarray(Clag_b[1:L + 1]))) / TOL["C_lag"]) if L >= 1 else 0.0
    return d_cx, d_lag, ok


def dip(C, n, x, min_pairs=DENSE_PAIRS):
    """Dip depth and position: the minimum of C over DIP_RANGE on DENSE bins (>= DENSE_PAIRS pairs; a 10-pair bin set
    the minimum on the verifier's planted A = 50 series, 2026-10-02)."""
    ok = (x >= DIP_RANGE[0]) & (x <= DIP_RANGE[1]) & (n >= min_pairs) & np.isfinite(C)
    if not ok.any(): return float("nan"), float("nan")
    i = np.argmin(np.where(ok, C, np.inf)); return float(C[i]), float(x[i])


def compare(ctl_C, ctl_n, ctl_lag, curves):
    x = curves["x"]; R, C1 = curves["real"], curves["c1"]
    dr_cx, dr_lag, okr = dev_curves(ctl_C, ctl_n, R["C"], R["n"], x, ctl_lag, R["C_lag"])
    dc_cx, dc_lag, okc = dev_curves(ctl_C, ctl_n, C1["C"], C1["n"], x, ctl_lag, C1["C_lag"])
    dr_dense, _, okrd = dev_curves(ctl_C, ctl_n, R["C"], R["n"], x, ctl_lag, R["C_lag"], DENSE_PAIRS)
    dc_dense, _, okcd = dev_curves(ctl_C, ctl_n, C1["C"], C1["n"], x, ctl_lag, C1["C_lag"], DENSE_PAIRS)
    d_ctl, x_ctl = dip(ctl_C, ctl_n, x); d_real, _ = dip(R["C"], R["n"], x); d_c1, _ = dip(C1["C"], C1["n"], x)
    if max(dr_dense, dr_lag) <= 1: word = "REPRODUCES"
    elif max(dc_dense, dc_lag) <= 1: word = "STAYS AT C1"
    elif (d_ctl - d_real > TOL["Cx"]) or (ctl_lag[1] - R["C_lag"][1] > TOL["C_lag"]): word = "OVERSHOOTS"
    else:
        ok = okrd & okcd
        lo_ = np.minimum(R["C"], C1["C"]) - TOL["Cx"]; hi_ = np.maximum(R["C"], C1["C"]) + TOL["Cx"]
        word = "PARTIAL" if bool(np.all((ctl_C[ok] >= lo_[ok]) & (ctl_C[ok] <= hi_[ok]))) else "OFF-CURVE"
    return dict(word=word, dev_Cx_real=dr_cx, dev_Clag_real=dr_lag, dev_Cx_c1=dc_cx, dev_Clag_c1=dc_lag,
                dev_Cx_dense_real=dr_dense, dev_Cx_dense_c1=dc_dense, n_dense_bins=int((okrd & okcd).sum()),
                C_lag1=float(ctl_lag[1]), C_lag2=float(ctl_lag[2]), dip=d_ctl, dip_x=x_ctl, dip_real=d_real, dip_c1=d_c1,
                real_C_lag1=float(R["C_lag"][1]), real_C_lag2=float(R["C_lag"][2]), c1_C_lag1=float(C1["C_lag"][1]), c1_C_lag2=float(C1["C_lag"][2]))


def record(name, r, res, match, curves, arrays, extra=None):
    sc = scalars(r)
    if sc["status"] != "OK":
        return dict(name=name, status=sc["status"], match=match)
    cmp_ = compare(r["autocorr"]["C"], r["autocorr"]["n_pairs"].astype(float), np.array(sc["C_lag"]), curves)
    arrays[f"{name}/Cx_C"] = r["autocorr"]["C"]; arrays[f"{name}/Cx_n"] = r["autocorr"]["n_pairs"].astype(float)
    out = dict(name=name, status="OK", match=match, scalars=sc, compare=cmp_, span_rel_sd=float(res["unfold"]["span_rel_sd"]))
    if extra: out.update(extra)
    return out


# ====================================================================== the unit
def analyse_unit(bank, arm, layer, M, taus, variants, planted_amps, nseed, out_json, out_npz, window="W2"):
    t0 = time.time()
    real = load_real(bank, arm, layer, M, window); curves = phase1_curves(arm, layer, M, window)
    tw = real["times"]; m, n = real["shape"]
    v_target = float(curves["c1"]["v_target"]); real["vrms"] = v_target
    c1seeds = curves["c1"]["seeds"]
    tau_c1 = [float(s["match"]["tau"]) for s in c1seeds]
    seeds = [c1_seed(layer, M, sd, window) for sd in range(len(c1seeds))][:nseed]
    out = dict(est=EST, arm=arm, layer=layer, type=M, window=window, shape=[m, n], T=int(len(tw)), v_target=v_target,
               x_step_real=float(curves["real"]["scalars"]["x_step_mean"]), real=dict(C_lag=[float(v) for v in curves["real"]["C_lag"]],
               velocity=curves["real"]["scalars"]["velocity"], abs_k_median=curves["real"]["scalars"]["curvature"]["abs_k_median"]),
               c1=dict(C_lag=[float(v) for v in curves["c1"]["C_lag"]], tau=tau_c1, seeds=seeds,
                       velocity={k: float(np.mean([s["velocity"][k] for s in c1seeds])) for k in ("skew", "ex_kurt", "ks_gauss")},
                       abs_k_median=float(np.mean([s["curvature"]["abs_k_median"] for s in c1seeds]))),
               drift={}, controls=[], errors=[])
    arrays = {"x": curves["x"], "real/Cx_C": curves["real"]["C"], "real/Cx_n": curves["real"]["n"], "c1/Cx_C": curves["c1"]["C"], "c1/Cx_n": curves["c1"]["n"]}
    S_real = strip_sort(real["sig"]); n_eff = S_real.shape[1]
    # stationarity of the real velocity over the window (sealed unfolding; band rms velocity per half)
    E_real, _ = M2.unfold_series(real["sig"], M2.PARAMS["top_k"], M2.PARAMS["band"], M2.PARAMS["kde_c"], M2.PARAMS["nonpos_max"])
    v_real = np.diff(E_real, axis=0) / np.diff(tw)[:, None]; hm = len(v_real) // 2
    out["real"]["vrms_halves"] = [float(np.sqrt((v_real[:hm] ** 2).mean())), float(np.sqrt((v_real[hm:] ** 2).mean()))]

    # --- regenerate the phase-1 C1 draws (bit-identical: same seed, tau, grid) and re-read them here (self-check)
    C1draws = {}
    for sd, seed in enumerate(seeds):
        S = gen_c1(m, n, tw, tau_c1[sd], seed); r, res = m2_single(S, tw)
        C1draws[sd] = (S, r)
        ok = abs(float(r["vrms"]) - float(c1seeds[sd]["match"]["vrms_measured"])) < 1e-9
        out["controls"].append(record(f"c1_regen_s{sd}", r, res, dict(tau=tau_c1[sd], seed=seed, bit_identical_vrms=ok), curves, arrays))
    S0, r0 = C1draws[0]

    # --- C9
    for var in variants:
        h, st = VARIANTS[var]["h"], VARIANTS[var]["sigma_t"]
        try:
            Lslow = slow_component(S_real, tw, h, st)
            out["drift"][var] = drift_diagnostics(real, Lslow, tw, var)
            Lmean = Lslow.mean(0)
            # zero drift (fixed time-mean map), same tau -> must be C1 within noise
            r, res = m2_single(warp(S0, Lmean), tw)
            out["controls"].append(record(f"c9_{var}_zero", r, res, dict(tau=tau_c1[0], seed=seeds[0], h=h, sigma_t=st), curves, arrays,
                                          extra=dict(vs_same_seed_c1=_same_seed_dev(r, r0))))
            if var == variants[0]:
                # pure dilation: time-mean shape x real ||W||_F(t) -> dilation-invariant unfolding -> C1 to rounding
                fro = np.sqrt((real["sig"] ** 2).sum(1)); Lscale = Lmean[None, :] + np.log(fro / np.exp(np.log(fro).mean()))[:, None]
                r, res = m2_single(warp(S0, Lscale), tw)
                out["controls"].append(record("c9_scale_only", r, res, dict(tau=tau_c1[0], seed=seeds[0]), curves, arrays,
                                              extra=dict(vs_same_seed_c1=_same_seed_dev(r, r0))))
            # matched (the real slow drift), tau re-solved, each seed
            for sd, seed in enumerate(seeds):
                mk = lambda tau, _seed=seed: warp(gen_c1(m, n, tw, tau, _seed), Lslow)
                S, r, res, match = match_scale(mk, v_target, tau_c1[sd], mode="inv", extra=tw)
                match.update(tau=match.pop("p"), seed=seed, h=h, sigma_t=st)
                out["controls"].append(record(f"c9_{var}_matched_s{sd}", r, res, match, curves, arrays))
            # null: slow component extracted from an independent C1 draw warped by the time-mean real map
            S_ind = warp(gen_c1(m, n, tw, tau_c1[0], seeds[0] + 777), Lmean)
            Lnull = slow_component(strip_sort(S_ind), tw, h, st)
            out["drift"][var + "_null"] = drift_diagnostics(dict(sig=S_ind, vrms=v_target), Lnull, tw, var + "_null")
            mk = lambda tau: warp(gen_c1(m, n, tw, tau, seeds[0]), Lnull)
            S, r, res, match = match_scale(mk, v_target, tau_c1[0], mode="inv", extra=tw)
            match.update(tau=match.pop("p"), seed=seeds[0], h=h, sigma_t=st)
            out["controls"].append(record(f"c9_{var}_null", r, res, match, curves, arrays))
        except Exception as e:
            out["errors"].append(f"c9_{var}: {type(e).__name__}: {e}\n{traceback.format_exc()}")
    # planted drift on the zero map (the control CAN fire)
    for amp in planted_amps:
        try:
            Lmean = slow_component(S_real, tw, VARIANTS[variants[0]]["h"], VARIANTS[variants[0]]["sigma_t"]).mean(0)
            Lpl = Lmean[None, :] + planted_field(n_eff, tw, Lmean, amp)
            mk = lambda tau: warp(gen_c1(m, n, tw, tau, seeds[0]), Lpl)
            S, r, res, match = match_scale(mk, v_target, tau_c1[0], mode="inv", extra=tw)
            match.update(tau=match.pop("p"), seed=seeds[0], amp=amp, lam=PLANTED_LAMBDA)
            out["controls"].append(record(f"c9_planted_A{amp:g}", r, res, match, curves, arrays))
        except Exception as e:
            out["errors"].append(f"planted A{amp}: {type(e).__name__}: {e}\n{traceback.format_exc()}")

    # --- C1-driver
    for tau_tok in taus:
        tau_v = tau_c1[0] if tau_tok == "c1" else float(tau_tok)
        tlabel = "c1" if tau_tok == "c1" else ("inf" if not np.isfinite(tau_v) else f"{tau_v:g}")
        try:
            # initial s_M: level velocity ~ s_M in sigma units; spacing of W(0)'s bulk from one SVD
            s0 = svd(np.random.default_rng(seeds[0]).standard_normal((max(m, n), min(m, n))), compute_uv=False)
            s0 = np.sort(s0)[:len(s0) - TOP_K]; a_, b_ = int(np.ceil(0.1 * len(s0))), int(np.ceil(0.9 * len(s0)))
            Delta = (s0[b_ - 1] - s0[a_]) / (b_ - a_ - 1)
            sM0 = v_target * Delta
            if tau_v == 0: sM0 = v_target * Delta / math.sqrt(float(np.median(np.diff(tw))))     # DBM: displacement sM sqrt(dt)
            sM = sM0
            for sd, seed in enumerate(seeds):
                if sd == 0:
                    mk = lambda s, _seed=seed: gen_driver(m, n, tw, tau_v, s, _seed)
                    S, r, res, match = match_scale(mk, v_target, sM0, mode="prop", extra=tw)
                    sM = match["p"]
                else:
                    S = gen_driver(m, n, tw, tau_v, sM, seed); r, res = m2_single(S, tw)
                    v1 = float(r["vrms"]); match = dict(p=sM, passes=0, vrms_measured=v1, v_target=v_target, matched=bool(abs(v1 / v_target - 1) < XSTEP_MATCH_TOL), history=[])
                match.update(sM=match.pop("p"), tau_v=(float(tau_v) if np.isfinite(tau_v) else "inf"), tau_label=tlabel, seed=seed)
                out["controls"].append(record(f"driver_tau{tlabel}_s{sd}", r, res, match, curves, arrays))
        except Exception as e:
            out["errors"].append(f"driver tau_v={tau_tok}: {type(e).__name__}: {e}\n{traceback.format_exc()}")

    out["runtime_s"] = time.time() - t0
    out_json.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_npz, **{k: np.asarray(v) for k, v in arrays.items()})
    json.dump(out, open(out_json, "w"), indent=1, default=_jsonable)
    return out


def _same_seed_dev(r, r0):
    """Same-seed difference between a warped and the unwarped C1 draw (the warp's own footprint)."""
    x = r["autocorr"]["x"]; d_cx, d_lag, _ = dev_curves(r["autocorr"]["C"], r["autocorr"]["n_pairs"], r0["autocorr"]["C"], r0["autocorr"]["n_pairs"], x,
                                                     r["autocorr"]["C_lag"], r0["autocorr"]["C_lag"])
    d_dense, _, _ = dev_curves(r["autocorr"]["C"], r["autocorr"]["n_pairs"], r0["autocorr"]["C"], r0["autocorr"]["n_pairs"], x,
                               r["autocorr"]["C_lag"], r0["autocorr"]["C_lag"], DENSE_PAIRS)
    return dict(max_dCx_x_le_2=d_cx * TOL["Cx"], max_dCx_dense=d_dense * TOL["Cx"], max_dClag_1_6=d_lag * TOL["C_lag"], d_abs_k_median=float(r["curvature"]["abs_k_median"] - r0["curvature"]["abs_k_median"]),
                d_vrms_rel=float(r["vrms"] / r0["vrms"] - 1))


def _jsonable(o):
    if isinstance(o, (np.floating, np.integer)): return o.item()
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, (np.bool_,)): return bool(o)
    if isinstance(o, float) and not np.isfinite(o): return None
    raise TypeError(type(o))


def reword_unit(oj):
    """Recompute every control's comparison (words) from the stored curves under the current compare()."""
    oj = Path(oj); u = json.load(open(oj)); z = np.load(oj.with_suffix(".npz"))
    L = TOL["n_lag"]
    curves = dict(x=z["x"], real=dict(C=z["real/Cx_C"], n=z["real/Cx_n"], C_lag=np.array(u["real"]["C_lag"][:L + 1])),
                  c1=dict(C=z["c1/Cx_C"], n=z["c1/Cx_n"], C_lag=np.array(u["c1"]["C_lag"][:L + 1])))
    for c in u["controls"]:
        if c.get("status") != "OK": continue
        c["compare"] = compare(z[f"{c['name']}/Cx_C"], z[f"{c['name']}/Cx_n"], np.array(c["scalars"]["C_lag"]), curves)
    u["reworded"] = EST
    json.dump(u, open(oj, "w"), indent=1, default=_jsonable)
    return u


def _worker(args):
    bank, arm, layer, M, taus, variants, amps, nseed, oj, on = args
    try:
        return (arm, layer, M, analyse_unit(bank, arm, layer, M, taus, variants, amps, nseed, Path(oj), Path(on)), None)
    except Exception as e:
        return (arm, layer, M, None, f"{type(e).__name__}: {e}\n{traceback.format_exc()}")


# ====================================================================== tables
def table_rows(units):
    rows = []
    for u in units:
        base = dict(arm=u["arm"], layer=u["layer"], type=u["type"], x_step=u["x_step_real"], real_C_lag1=u["real"]["C_lag"][1], real_C_lag2=u["real"]["C_lag"][2],
                    c1_C_lag1=u["c1"]["C_lag"][1], c1_C_lag2=u["c1"]["C_lag"][2], real_kmed=u["real"]["abs_k_median"], c1_kmed=u["c1"]["abs_k_median"])
        for c in u["controls"]:
            if c.get("status") != "OK": rows.append(dict(base, control=c["name"], word=c.get("status"))); continue
            sc, cp, mt = c["scalars"], c["compare"], c["match"]
            rows.append(dict(base, control=c["name"], word=cp["word"], dev_Cx_real=cp["dev_Cx_real"], dev_Clag_real=cp["dev_Clag_real"], dev_Cx_c1=cp["dev_Cx_c1"],
                             dev_Clag_c1=cp["dev_Clag_c1"], dev_Cx_dense_real=cp["dev_Cx_dense_real"], dev_Cx_dense_c1=cp["dev_Cx_dense_c1"], C_lag1=cp["C_lag1"], C_lag2=cp["C_lag2"], dip=cp["dip"], dip_x=cp["dip_x"], dip_real=cp["dip_real"], dip_c1=cp["dip_c1"],
                             v_skew=sc["velocity"]["skew"], v_exkurt=sc["velocity"]["ex_kurt"], v_ks=sc["velocity"]["ks_gauss"], kmed=sc["abs_k_median"],
                             vrms_ratio=(mt.get("vrms_measured", float("nan")) / mt.get("v_target", 1.0)) if mt.get("v_target") else float("nan"),
                             matched=mt.get("matched"), tau=mt.get("tau"), tau_v=mt.get("tau_v"), sM=mt.get("sM")))
    return rows


def write_tables(out, units):
    import csv
    rows = table_rows(units)
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("arm", "layer", "type", "control", "word"), k))
    with open(out / "table.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); [w.writerow(r) for r in rows]
    # markdown: one row per (matrix, control) with the headline numbers
    L = ["| arm | L | type | x_step | control | word | C_lag1 (real / C1 / ctl) | C_lag2 (real / C1 / ctl) | dip (real / C1 / ctl) | dev_Clag real / C1 | dev_Cx_dense real / C1 | dev_Cx(runner) real / C1 | v skew / exkurt / KS | med\\|k\\| (real / C1 / ctl) | vrms/target |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    f3 = lambda v: "nan" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:+.3f}"
    f2 = lambda v: "nan" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.2f}"
    for r in rows:
        if "C_lag1" not in r: L.append(f"| {r['arm']} | {r['layer']} | {r['type']} | {r['x_step']:.2f} | {r['control']} | {r['word']} | | | | | | | | | |"); continue
        L.append(f"| {r['arm']} | {r['layer']} | {r['type']} | {r['x_step']:.2f} | {r['control']} | {r['word']} | {f3(r['real_C_lag1'])} / {f3(r['c1_C_lag1'])} / {f3(r['C_lag1'])} "
                 f"| {f3(r['real_C_lag2'])} / {f3(r['c1_C_lag2'])} / {f3(r['C_lag2'])} | {f3(r['dip_real'])} / {f3(r['dip_c1'])} / {f3(r['dip'])} "
                 f"| {f2(r['dev_Clag_real'])} / {f2(r['dev_Clag_c1'])} | {f2(r['dev_Cx_dense_real'])} / {f2(r['dev_Cx_dense_c1'])} | {f2(r['dev_Cx_real'])} / {f2(r['dev_Cx_c1'])} "
                 f"| {f3(r['v_skew'])} / {f3(r['v_exkurt'])} / {r['v_ks']:.3f} | {r['real_kmed']:.3f} / {r['c1_kmed']:.3f} / {r['kmed']:.3f} | {f2(r['vrms_ratio'])} |")
    (out / "table.md").write_text("\n".join(L) + "\n")
    return rows


def summarise(out, units, taus, variants):
    rows = table_rows(units)
    def count(prefix):
        rs = [r for r in rows if r["control"].startswith(prefix) and "word" in r]
        words = {}
        for r in rs: words[r["word"]] = words.get(r["word"], 0) + 1
        return dict(n=len(rs), words=words,
                    C_lag1_mean=float(np.nanmean([r.get("C_lag1", np.nan) for r in rs])) if rs else None,
                    C_lag2_mean=float(np.nanmean([r.get("C_lag2", np.nan) for r in rs])) if rs else None,
                    dev_Clag_real_median=float(np.nanmedian([r.get("dev_Clag_real", np.nan) for r in rs])) if rs else None,
                    dev_Clag_c1_median=float(np.nanmedian([r.get("dev_Clag_c1", np.nan) for r in rs])) if rs else None,
                    dev_Cx_dense_real_median=float(np.nanmedian([r.get("dev_Cx_dense_real", np.nan) for r in rs])) if rs else None,
                    dev_Cx_dense_c1_median=float(np.nanmedian([r.get("dev_Cx_dense_c1", np.nan) for r in rs])) if rs else None,
                    dev_Cx_real_median=float(np.nanmedian([r.get("dev_Cx_real", np.nan) for r in rs])) if rs else None,
                    dev_Cx_c1_median=float(np.nanmedian([r.get("dev_Cx_c1", np.nan) for r in rs])) if rs else None,
                    kmed_mean=float(np.nanmean([r.get("kmed", np.nan) for r in rs])) if rs else None)
    groups = {}
    for var in variants:
        for kind in ("zero", "matched", "null"): groups[f"c9_{var}_{kind}"] = count(f"c9_{var}_{kind}")
    groups["c9_scale_only"] = count("c9_scale_only"); groups["c9_planted"] = count("c9_planted")
    for tau_v in taus:
        lab = "c1" if tau_v == "c1" else ("inf" if not np.isfinite(tau_v) else f"{tau_v:g}")
        groups[f"driver_tau{lab}"] = count(f"driver_tau{lab}_")
    per_arm = {}
    for arm in sorted({u["arm"] for u in units}):
        per_arm[arm] = {g: {} for g in groups}
        for g in groups:
            rs = [r for r in rows if r["arm"] == arm and r["control"].startswith(g + ("_" if not g.startswith("c9_planted") and not g.startswith("c9_scale") else "")) and "word" in r]
            for r in rs: per_arm[arm][g][r["word"]] = per_arm[arm][g].get(r["word"], 0) + 1
    drift = {f"{u['arm']}/L{u['layer']:02d}_{u['type']}": u["drift"] for u in units}
    S = dict(est=EST, n_units=len(units), units=[f"{u['arm']}/L{u['layer']:02d}_{u['type']}" for u in units], groups=groups, per_arm=per_arm, drift=drift,
             errors={f"{u['arm']}/L{u['layer']:02d}_{u['type']}": u["errors"] for u in units if u["errors"]},
             real_x_step={f"{u['arm']}/L{u['layer']:02d}_{u['type']}": u["x_step_real"] for u in units})
    json.dump(S, open(out / "summary.json", "w"), indent=1, default=_jsonable)
    return S


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bank", default=str(LLMSPEC / "cache" / "armb")); ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--arms", nargs="+", default=["A0", "M0s1"]); ap.add_argument("--layers", type=int, nargs="+", default=[0, 2, 5])
    ap.add_argument("--types", nargs="+", default=["Q", "K", "O", "MLP_OUT"])
    ap.add_argument("--taus", nargs="+", default=["0", "2", "5", "10", "20", "40", "80", "c1"], help="driver tau_v in steps; '0' = literal DBM, 'c1' = matched C1 tau, 'inf' = constant velocity")
    ap.add_argument("--variants", nargs="+", default=["smooth", "fine", "raw"], choices=list(VARIANTS))
    ap.add_argument("--planted-amp", type=float, nargs="*", default=[50.0]); ap.add_argument("--nseed", type=int, default=2)
    ap.add_argument("--workers", type=int, default=5); ap.add_argument("--blas-threads", default=None); ap.add_argument("--force", action="store_true")
    ap.add_argument("--reword", action="store_true", help="recompute the words of every stored unit from its curves (no spectra regenerated)")
    A = ap.parse_args(argv)
    taus = [t if t == "c1" else (float("inf") if t == "inf" else float(t)) for t in A.taus]
    out = Path(A.out); out.mkdir(parents=True, exist_ok=True)
    jobs, units = [], []
    for arm in A.arms:
        for L in A.layers:
            for M in A.types:
                oj = out / arm / f"L{L:02d}_{M}.json"; on = oj.with_suffix(".npz")
                if oj.exists() and not A.force:
                    u = reword_unit(oj) if A.reword else json.load(open(oj))
                    if u.get("est") == EST and not u.get("errors"): units.append(u); continue
                jobs.append((A.bank, arm, L, M, taus, A.variants, A.planted_amp, A.nseed, str(oj), str(on)))
    log(f"{len(units)} units resumed, {len(jobs)} to compute; workers {A.workers}; taus {taus}; variants {A.variants}")
    T0 = time.time(); errors = []
    if jobs:
        if A.workers > 1:
            with ProcessPoolExecutor(max_workers=A.workers) as ex:
                for fut in as_completed([ex.submit(_worker, j) for j in jobs]):
                    arm, L, M, u, err = fut.result()
                    if err: errors.append((arm, L, M, err)); log(f"ERROR {arm} L{L} {M}: {err.splitlines()[0]}"); continue
                    units.append(u); log(f"done {arm} L{L} {M} ({u['runtime_s']:.0f}s; errors {len(u['errors'])}) [{time.time() - T0:.0f}s]")
        else:
            for j in jobs:
                arm, L, M, u, err = _worker(j)
                if err: errors.append((arm, L, M, err)); log(f"ERROR {arm} L{L} {M}: {err}"); continue
                units.append(u); log(f"done {arm} L{L} {M} ({u['runtime_s']:.0f}s; errors {len(u['errors'])}) [{time.time() - T0:.0f}s]")
    units.sort(key=lambda u: (A.arms.index(u["arm"]) if u["arm"] in A.arms else 99, u["layer"], TYPES.index(u["type"])))
    write_tables(out, units); S = summarise(out, units, taus, A.variants)
    for g, d in S["groups"].items():
        if d["n"]: log(f"  {g:22s} n={d['n']:3d} words={d['words']} C_lag1={d['C_lag1_mean']:+.3f} C_lag2={d['C_lag2_mean']:+.3f} dev_Clag real/C1 med={d['dev_Clag_real_median']:.2f}/{d['dev_Clag_c1_median']:.2f} "
                      f"dev_Cx_dense real/C1 med={d['dev_Cx_dense_real_median']:.2f}/{d['dev_Cx_dense_c1_median']:.2f} med|k| mean={d['kmed_mean']:.3f}")
    if errors or S["errors"]: log("ERRORS:", errors, S["errors"])
    log(f"wrote {out} ({time.time() - T0:.0f}s)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

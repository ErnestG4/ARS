"""Phase-1 runner for PDYN_PREREG.md (parametric spectral dynamics, AdamW vs Muon) over the banked Arm B extraction.

Reads, per arm / layer / matrix type, ONLY the keys sig_<M> (fp64 singular values, descending), U32_<M> / V32_<M>
(top-32 vectors; the top-16 are used, M3 only) and rms_<M> of cache/armb/<arm>/stepNNNNN/LNN.npz. The held-out
bulk-vector keys (ipr_*, pt_*) are never touched (split-sample rule, PDYN_PREREG §1); the loader refuses any other key.
The matrix shape is (rows of U32, rows of V32): Q/K/V/O 512x512, MLP_IN 2048x512, MLP_OUT 512x2048; ||W||_F from the
spectrum equals rms*sqrt(mn) on the bank (checked on one file, 4 decimals).

Windows (PDYN_PREREG §1): W1 = [0,500) (warmup, 10-step cadence), W2 = [500,3000] (25-step), W3 = (3000, ...]
(extension, every 100; DESCRIPTIVE only). Never pooled. Steps = the step directories present in the bank with a DONE
marker; the declared grid (grids.arm_grid; A0r uses A0's) is reported against them (missing / extra).

Measurements (§2; estimator settings fixed by phase 0 and asserted equal to pdyn_m2.PARAMS / pdyn_m3.PARAMS):
  M1  sigma_1, sigma_16, sigma_median, ||W||_F = sqrt(sum sigma^2), rms, per checkpoint.
  M2  pdyn_m2.analyse: top-16 stripped BEFORE unfolding, kde(32), band [0.10,0.90), local <v^2> cubic; velocity
      skew / excess kurtosis / KS, C(x), C_lag, curvature |k| statistics and ZD fits -- per window.
  M3  pdyn_m3.analyse on the top-16 (sig[:17] so the last lower gap exists): gap_mult 2, overlap_min 0.5; events
      assigned to windows by t_min; ambiguous (step, level) fraction per window; C8 = all vs unambiguous.
  M5  effective rank exp(H(sigma^2/sum)), stable rank sum sigma^2 / sigma_1^2, top-16 mass fraction, MP fit at the
      MEDIAN-matched scale (stage3_analyze.mp_fit_v2 convention; the fixed-point v1 collapses on trained Q/K) with
      its full-spectrum KS; upper outliers = sigma > tau_plus * E_plus; WITHDRAWN where KS > the Stage-3 witness 95th
      percentile (results/stage3_witness_pythia-70m.json, per type, same shapes; --mp-witness; if absent the flag is
      None and the KS is reported for the findings step); HTSR alpha = Pareto MLE on the ESD with Clauset min-KS xmin
      over the top half (n_tail >= 50) -- labelled FRAGILE, only to be read beside its ESD.
  M6  events per checkpoint interval (all layers and types pooled) over the trainlog's loss and lr
      (armb/staging/<arm>/trainlog.jsonl: step, loss, lr only); absent trainlog -> M6 skipped with a note.

Controls (§4), through the identical code path, computed per (arm, layer, type, window) BEFORE the real reading in
the output ordering:
  C1  smooth beta=1 Gaussian-process family (pdyn_calib.smooth_rect at the REAL shape -- the real objects are singular
      values of a non-symmetric W, so the rectangular analogue is used for every type, square included), on the
      window's own checkpoint grid (same cadence), tau set so the MEASURED x_step matches the real window's x_step
      within 5% (x_step is exactly proportional to 1/tau for this family; iterated on a 16-checkpoint stub, <= 3
      passes), --nseed seeds (default 2, as the verify (a) two-draw comparison).
  C2  beta=2 (complex W, pdyn_calib.smooth_rect beta=2; PDYN_PIPELINE_NOTES §2 flags a +13% scale excess for the
      complex RECTANGULAR family, unexplained) and the Poisson walk (pdyn_calib.poisson_walk, n = the real number of
      levels), both x_step-matched the same way; these are the WITNESSES that must read NOT beta=1 at the real n.
  C3  shuffled checkpoint order of the real series (pdyn_calib.shuffle) -> C_lag[1..3] with the exact iid prediction.
  C4  fp32 round-trip. The bank holds no W, so two floors are reported: (a) the SPECTRUM of the window's middle
      checkpoint rounded to fp32 and back, re-unfolded -> displacement rms vs the per-step displacement rms;
      (b) pdyn_calib.roundtrip_floor on a synthetic matrix of the real shape at the real entry rms (matrix-level).
  C5  pdyn_calib.sign_flips (joint and independent) on the M3 inputs -> every metric array bit-identical (must be True).
  C8  ambiguous fractions and the unambiguous-only ("excluded") re-estimate of event counts / rates and of P5 / P6.

Verdict words (§3), applied MECHANICALLY by verdict():
  P2 per matrix and window, against C1 at the SAME cadence and matched x_step:
     - NOT RESOLVABLE if the curvature sample count n_k = (T-2) x band levels < 1000 (beta=2 discrimination size,
       PDYN_PIPELINE_NOTES §4; Poisson needs 500), or if the witnesses are not separated from C1 at this n (every beta=2
       seed must read S > thr_hi and every Poisson seed S < thr_lo, S = median |k|, thr = midpoints of the seed means),
       or if the unfolding was refused / a window is INAPPLICABLE (< 4 checkpoints).
     - velocity component: |skew - mean_C1| <= 0.25, |exkurt - mean_C1| <= 0.5, KS - mean_C1 <= 0.03 (the verify (a)
       tolerances = the declared calibrator spread, set from the measured two-draw agreement, PDYN_PIPELINE_NOTES §4).
     - C(x) component: max_j<=6 |C_lag - mean_C1| <= 0.10 and max over bins with >= min_pairs on both |C(x<=2) - C1| <= 0.15.
     - curvature component (ALWAYS tagged PROVISIONAL, cadence): thr_lo < S < thr_hi -> HOLDS else FAILS.
     - word = FAILS if any component FAILS, else HOLDS; tags carry PROVISIONAL (curvature).
     Arm level (per window): per-matrix tables are reported, not counted; the arm word is the MAJORITY of per-matrix
     component words (each component must have a HOLDS majority among resolvable matrices; > half NOT RESOLVABLE -> NOT
     RESOLVABLE). Primary endpoints: P2 on W2 for A0 (AdamW) and M0s1 (Muon).
  P3 (M5, W2, step-matched): per matrix, median over steps of (Muon - AdamW) effective rank, read against the floor
     median |A0 - A0r| at the same steps (one draw): majority of matrices above the floor -> HOLDS; majority <= 0 ->
     FAILS ("Muon <= AdamW"); else NOT RESOLVABLE. "Fewer/weaker outliers": top-16 mass fraction (weaker; majority
     lower -> HOLDS) and upper-outlier counts only where neither side is WITHDRAWN. Primary pair A0 vs M0s1; A1/A2 vs
     M0s2 DESCRIPTIVE; "across seeds" reported as a qualifier.
  P5 (PROVISIONAL): rate = events per step per interval; Spearman(rate, lr) > 0 with p < 0.05 AND event intervals
     carry larger |delta loss| than a shuffled-time null (events redrawn uniformly in time, 2000 draws, p < 0.05)
     -> HOLDS; either fails -> FAILS; fewer than 20 events or no trainlog -> NOT RESOLVABLE. Declared, untuned.
  P6 (PROVISIONAL, DESCRIPTIVE): inter-event CV and <r~> with a uniform-time null at the same n; no class word below
     n = 50 events (declared).
  P1 is read on the existing <r~>/q (ARMB_FINDINGS §6), not computed here; P4 is phase 2 only. W3 and M5 context are
  DESCRIPTIVE.
--flip-threshold inverts the per-matrix curvature acceptance region (verify_pdyn_phase1.py --redpath only; recorded).

Outputs: <out>/<arm>/{m1,m2,m3,m5,m6,controls}.json, <out>/<arm>/parts/ (per (layer, type) json+npz; the resume unit),
<out>/long_*.parquet (+ .csv), <out>/summary.json, <out>/figs/*.png.
--fake builds a synthetic bank from the sealed calibrators (same keys / shapes / grid structure, 2 layers, a planted
avoided crossing in type O of layer 0, arms FAKE_C1 (beta=1), FAKE_B2 (beta=2), FAKE_PO (Poisson), FAKE_SHORT (beta=1,
5 checkpoints)) and runs end-to-end; never on cache/armb.
"""
import os, sys


def _early_threads():
    """One BLAS thread per worker process when --workers > 1 (must be set before numpy is imported; inherited by
    the forked workers); --blas-threads overrides."""
    argv = sys.argv; w = 1; nt = None
    for i, a in enumerate(argv):
        if a == "--workers" and i + 1 < len(argv): w = int(argv[i + 1])
        elif a.startswith("--workers="): w = int(a.split("=", 1)[1])
        elif a == "--blas-threads" and i + 1 < len(argv): nt = argv[i + 1]
    if nt is None and w > 1: nt = "1"
    if nt is not None:
        for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[k] = str(nt)


_early_threads()
import argparse, json, time, hashlib, math, traceback  # noqa: E402
from pathlib import Path  # noqa: E402
from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402
from scipy.linalg import svd  # noqa: E402

HERE = Path(__file__).resolve().parent
LLMSPEC = HERE.parent
sys.path.insert(0, str(HERE))
import pdyn_m2 as M2, pdyn_m3 as M3, pdyn_calib as C  # noqa: E402

EST = "pdyn_phase1-v1"
TYPES = ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT")
ALLOWED_PREFIXES = ("sig_", "U32_", "V32_", "rms_")                    # the ONLY bank keys this runner reads
WINDOWS = {"W1": (0.0, 500.0), "W2": (500.0, 3001.0), "W3": (3001.0, 1e9)}
GRID_ARM = {"A0r": "A0"}
TOP_K = 16
M2_KW = dict(top_k=16, kde_c=32.0, band=(0.10, 0.90), v2_deg=3)        # PDYN_PREREG §2; asserted == pdyn_m2.PARAMS
M3_KW = dict(K=16, gap_mult=2.0, overlap_min=0.5)                      # PDYN_PREREG §2; asserted == pdyn_m3.PARAMS
for _k, _v in M2_KW.items(): assert M2.PARAMS[_k] == _v, (_k, M2.PARAMS[_k], _v)
for _k, _v in M3_KW.items(): assert M3.PARAMS[_k] == _v, (_k, M3.PARAMS[_k], _v)
DISCRIM_N = dict(beta2=1000, poisson=500)                              # PDYN_PIPELINE_NOTES §4 (curvature samples)
TOL = dict(skew=0.25, ex_kurt=0.5, ks_gauss=0.03, C_lag=0.10, Cx=0.15, n_lag=6, x_max=2.0)   # verify_pdyn (a)
XSTEP_MATCH_TOL = 0.05
N_SHUFFLE = 3                                                          # C3 permutations averaged
NB_REF = 397                                                           # band levels of a real 512-level spectrum (n_eff 496, [50,447)); tolerances scale by sqrt(NB_REF/nb) below it
P5_MIN_EVENTS = 20
P6_MIN_EVENTS_CLASS = 50
N_NULL = 2000
SUBSAMPLE = 20000
DEFAULT_WITNESS = LLMSPEC / "results" / "stage3_witness_pythia-70m.json"
P3_PAIRS = dict(primary=("A0", "M0s1"), floor=("A0", "A0r"), descriptive=[("A1", "M0s2"), ("A2", "M0s2")])
OPTIMIZER = {"A0": "AdamW", "A0r": "AdamW", "A1": "AdamW", "A2": "AdamW", "M0s1": "Muon", "M0s2": "Muon", "M0s3": "Muon"}
FAKE_ARMS = ("FAKE_C1", "FAKE_B2", "FAKE_PO", "FAKE_SHORT")


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ====================================================================== bank access
def bank_steps(bank, arm, n_layers):
    d = Path(bank) / arm
    out = []
    for p in sorted(d.glob("step*")):
        if not p.is_dir() or not p.name[4:].isdigit(): continue
        if not (p / "DONE").exists(): continue
        if all((p / f"L{L:02d}.npz").exists() for L in range(n_layers)):
            out.append(int(p.name[4:]))
    return out


def declared_grid(arm):
    try:
        import grids
        return [int(x) for x in grids.arm_grid(GRID_ARM.get(arm, arm))]
    except Exception:
        return None


def _get(z, key):
    if not key.startswith(ALLOWED_PREFIXES):
        raise PermissionError(f"key {key!r} is not in the allowed set {ALLOWED_PREFIXES} (held-out keys are never read)")
    return z[key]


def load_series(bank, arm, steps, layer, M, K=TOP_K):
    """One (layer, type) series: sig (T, n) fp64 descending, U (T, d_out, K) / V (T, d_in, K) fp64, rms (T,)."""
    sig, U, V, rms = [], [], [], []
    for s in steps:
        with np.load(Path(bank) / arm / f"step{s:05d}" / f"L{layer:02d}.npz") as z:
            sg = np.asarray(_get(z, f"sig_{M}"), np.float64)
            if np.any(np.diff(sg) > 1e-9 * max(1.0, abs(sg[0]))):
                raise ValueError(f"{arm} step {s} L{layer} {M}: sig not descending (bank convention assumed)")
            sig.append(sg)
            U.append(np.asarray(_get(z, f"U32_{M}"))[:, :K].astype(np.float64))
            V.append(np.asarray(_get(z, f"V32_{M}"))[:, :K].astype(np.float64))
            rms.append(float(_get(z, f"rms_{M}")))
    sig = np.array(sig)
    return dict(sig=sig, U=U, V=V, rms=np.array(rms), shape=(U[0].shape[0], V[0].shape[0]), n=sig.shape[1])


def read_trainlog(path):
    """step, loss, lr only (truncated last line tolerated)."""
    path = Path(path)
    if not path.exists(): return None
    st, lo, lr = [], [], []
    with open(path) as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "step" in d and "loss" in d:
                st.append(int(d["step"])); lo.append(float(d["loss"])); lr.append(float(d.get("lr", np.nan)))
    if not st: return None
    o = np.argsort(st)
    return dict(step=np.array(st)[o], loss=np.array(lo)[o], lr=np.array(lr)[o])


# ====================================================================== M5 helpers
_MP_CACHE = {}


def mp_cdf(c):
    if c not in _MP_CACHE:
        a, b = (1 - np.sqrt(c)) ** 2, (1 + np.sqrt(c)) ** 2
        g = np.linspace(a, b, 40001)
        f = np.sqrt(np.clip((b - g) * (g - a), 0, None)) / (2 * np.pi * c * g + 1e-300)
        F = np.concatenate([[0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(g))]); F /= F[-1]
        _MP_CACHE[c] = (g, F)
    return _MP_CACHE[c]


def mp_fit(sig, m, n, tau_plus):
    """Median-matched MP scale (stage3_analyze.mp_fit_v2 convention), full-spectrum KS, upper outliers."""
    nmax, nmin = max(m, n), min(m, n)
    g, F = mp_cdf(nmin / nmax)
    med_x = float(np.interp(0.5, F, g))
    s = float(np.median(sig)) / math.sqrt(nmax * med_x)
    Ep = s * (math.sqrt(m) + math.sqrt(n))
    x = np.sort(sig ** 2 / (nmax * s * s)); N = len(x); Fx = np.interp(x, g, F); i = np.arange(1, N + 1)
    ks = float(max((i / N - Fx).max(), (Fx - (i - 1) / N).max()))
    return dict(mp_scale=s, mp_ks=ks, n_upper_outliers=int((sig > tau_plus * Ep).sum()), sigma_max_over_Eplus=float(sig.max() / Ep))


def htsr_alpha(sig, kmin=50):
    """Pareto MLE on the ESD lambda = sigma^2 (descending) with Clauset min-KS x_min over the top half. FRAGILE."""
    lam = np.sort(sig ** 2)[::-1]; lam = lam[lam > 0]; n = len(lam)
    if n < 2 * kmin: return dict(htsr_alpha=float("nan"), htsr_xmin=float("nan"), htsr_ks=float("nan"), htsr_ntail=0)
    logs = np.log(lam); cs = np.cumsum(logs); best = None
    for k in range(kmin, n // 2 + 1):
        xmin = lam[k - 1]; denom = cs[k - 1] - k * math.log(xmin)
        if denom <= 0: continue
        a = 1 + k / denom
        tail = lam[:k][::-1]; Fm = 1 - (tail / xmin) ** (-(a - 1)); i = np.arange(1, k + 1)
        D = max((i / k - Fm).max(), (Fm - (i - 1) / k).max())
        if best is None or D < best[0]: best = (D, a, xmin, k)
    if best is None: return dict(htsr_alpha=float("nan"), htsr_xmin=float("nan"), htsr_ks=float("nan"), htsr_ntail=0)
    return dict(htsr_alpha=float(best[1]), htsr_xmin=float(best[2]), htsr_ks=float(best[0]), htsr_ntail=int(best[3]))


def m5_series(sig, m, n, mp_ref):
    tau_plus = float(mp_ref["tau_plus"]) if mp_ref and mp_ref.get("tau_plus") else 1.0
    ks95 = float(mp_ref["ks95"]) if mp_ref and mp_ref.get("ks95") else None
    rows = []
    for s in sig:
        s2 = s ** 2; tot = s2.sum(); p = s2 / tot; p = p[p > 0]
        r = dict(eff_rank=float(np.exp(-(p * np.log(p)).sum())), stable_rank=float(tot / s2[0]),
                 top16_mass=float(s2[:TOP_K].sum() / tot), sigma1_over_median=float(s[0] / np.median(s)))
        r.update(mp_fit(s, m, n, tau_plus)); r.update(htsr_alpha(s))
        r["mp_withdrawn"] = (r["mp_ks"] > ks95) if ks95 is not None else None
        rows.append(r)
    cols = {k: np.array([r[k] for r in rows], dtype=(object if k == "mp_withdrawn" else float)) for k in rows[0]}
    return cols, dict(tau_plus=tau_plus, ks95=ks95, mp_scale_convention="median-matched (stage3 mp_fit_v2)")


# ====================================================================== controls
def window_mask(times, w):
    a, b = WINDOWS[w]; return (times >= a) & (times < b)


def _std_vel(E, t):
    v, _, _ = M2.velocities(E, t); z = v.ravel(); return (z - z.mean()) / z.std()


def m2_single(S, t, **kw):
    """pdyn_m2.analyse on one window covering the whole series; returns the window dict (or INAPPLICABLE) with the
    standardised velocity sample attached as "_v_std" (figures only)."""
    t = np.asarray(t, float)
    res = M2.analyse(S, t, windows=((float(t[0]), float(t[-1]) + 1.0),), **kw)
    r = next(iter(res["windows"].values()))
    if not r.get("status"):
        r["_v_std"] = _std_vel(res["unfolded"], res["times"])
    return r


def gen_family(fam, m, n, times, tau, amp, seed):
    m, n = max(m, n), min(m, n)                       # singular values are transpose-invariant; the tall SVD is ~2x faster
    if fam == "c1": return C.smooth_rect(m, n, times, tau, 1, seed)
    if fam == "b2": return C.smooth_rect(m, n, times, tau, 2, seed)
    if fam == "po": return C.poisson_walk(n, times, tau, amp, seed)
    raise ValueError(fam)


def matched_family(fam, m, n, times_w, v_target, seed, dt_ref):
    """Generate `fam` on the window's own grid with the MEASURED band-mean RMS velocity (spacings per step) within
    XSTEP_MATCH_TOL of v_target (the real window's vrms, so x_step = dt * vrms matches at every interval): vrms is
    exactly proportional to 1/tau (smooth GP, dt << tau) or to amp (Poisson), so the same-seed draw is regenerated
    with the corrected scale (<= 3 passes on the full grid; a 16-checkpoint stub was rejected: the log steps of W1
    give the stub a different dt distribution and x_step_mean, 2026-10-02)."""
    tau = C.tau_for_xstep(n, v_target * dt_ref, dt_ref, beta=2 if fam == "b2" else 1)
    amp = v_target * tau
    v1 = float("nan"); it = 0; S = None; r = None
    for it in range(1, 4):
        S = gen_family(fam, m, n, times_w, tau, amp, seed)
        r = m2_single(S, times_w)
        v1 = float(r["vrms"]) if "vrms" in r else float("nan")
        if not np.isfinite(v1) or v1 <= 0: break
        if abs(v1 / v_target - 1) < XSTEP_MATCH_TOL: break
        if fam == "po": amp *= v_target / v1
        else: tau *= v1 / v_target
    return S, r, dict(tau=float(tau), amp=float(amp) if fam == "po" else None, passes=it, vrms_measured=v1, v_target=float(v_target),
                      matched=bool(np.isfinite(v1) and abs(v1 / v_target - 1) < XSTEP_MATCH_TOL))


def _sub(a, rng, k=SUBSAMPLE):
    a = np.asarray(a).ravel()
    return a if a.size <= k else a[rng.choice(a.size, k, replace=False)]


def win_scalars(r):
    """Scalar export of a pdyn_m2 window dict (no arrays), with C_lag kept (short) and the x grid of C(x)."""
    if r.get("status"): return dict(status=r["status"], T=r["T"])
    cs = {k: v for k, v in r["curvature"].items() if not isinstance(v, np.ndarray)}
    return dict(status="OK", T=r["T"], t0=r["t0"], t1=r["t1"], vrms=r["vrms"], v2=r["v2"], x_step_mean=r["x_step_mean"],
                x_step_max=r["x_step_max"], velocity=r["velocity"], C_lag=[float(x) for x in r["autocorr"]["C_lag"]],
                x_lag=[float(x) for x in r["autocorr"]["x_lag"]], curvature=cs, n_k=int(cs["n"]))


# ====================================================================== the work unit: (arm, layer, type)
def analyse_unit(bank, arm, steps, layer, M, windows, nseed, mp_ref, part_json, part_npz, signature):
    t_unit = time.time()
    rng = np.random.default_rng(int(hashlib.sha256(f"{arm}/{layer}/{M}".encode()).hexdigest()[:8], 16))   # deterministic subsampling
    D = load_series(bank, arm, steps, layer, M)
    sig, U, V, rms, (m, n) = D["sig"], D["U"], D["V"], D["rms"], D["shape"]
    times = np.array(steps, float)
    arrays = dict(steps=times)
    out = dict(est=EST, arm=arm, layer=layer, type=M, shape=[m, n], n_levels=int(D["n"]), steps=[int(s) for s in steps],
               signature=signature, windows={}, controls={}, notes=[])
    # ---- M1
    fro = np.sqrt((sig ** 2).sum(1))
    arrays.update(sigma1=sig[:, 0], sigma16=sig[:, TOP_K - 1], sigma_median=np.median(sig, 1), fro=fro, rms=rms, fro_from_rms=rms * math.sqrt(m * n))
    out["m1"] = dict(fro_vs_rms_max_rel_dev=float(np.max(np.abs(fro / (rms * math.sqrt(m * n)) - 1))))
    # ---- M5
    m5, m5meta = m5_series(sig, m, n, mp_ref)
    for k, v in m5.items():
        arrays[f"m5/{k}"] = v.astype(float) if k != "mp_withdrawn" else np.array([-1 if x is None else int(x) for x in v], float)
    out["m5"] = dict(meta=m5meta, withdrawn_frac=(float(np.mean([bool(x) for x in m5["mp_withdrawn"]])) if m5meta["ks95"] is not None else None),
                     W2_median=None)
    # ---- M2 on the real series (all requested windows)
    wins = tuple(WINDOWS[w] for w in windows)
    try:
        r2 = M2.analyse(sig, times, windows=wins)
        out["unfold"] = r2["unfold"]; m2_ok = True
    except RuntimeError as e:                                     # non-monotone unfolding refused
        out["notes"].append(f"M2 unfolding refused: {e}"); r2 = None; m2_ok = False
    # ---- M3 on the whole series (steps across the window boundary belong to the window of their midpoint)
    r3 = M3.analyse(sig[:, :TOP_K + 1], U, V, times, **M3_KW)
    flagged = ~r3["accepted"]; tmid = 0.5 * (times[1:] + times[:-1])
    for e in r3["events"]:
        e["window"] = next((w for w in windows if WINDOWS[w][0] <= e["t_min"] < WINDOWS[w][1]), None)
    out["m3"] = dict(ambiguous_frac=r3["ambiguous_frac"], mean_quality=r3["mean_quality"], total_swaps=r3["total_swaps"],
                     n_events=r3["n_events"], n_events_ambiguous=r3["n_events_ambiguous"], events=r3["events"])
    arrays["m3/delta"] = r3["delta"]; arrays["m3/swaps"] = r3["swaps"].astype(float); arrays["m3/quality_mean"] = r3["quality"].mean(1)
    # ---- C5 sign flips (bit identity)
    c5 = {}
    for joint in (True, False):
        U2, V2 = C.sign_flips(U, V, seed=11 + int(joint), joint=joint)
        r3b = M3.analyse(sig[:, :TOP_K + 1], U2, V2, times, **M3_KW)
        a0, a1 = M3.metric_arrays(r3), M3.metric_arrays(r3b)
        c5["joint" if joint else "independent"] = bool(all(np.array_equal(a0[k], a1[k]) for k in a0))
    out["controls"]["C5"] = dict(bit_identical=c5, pass_=all(c5.values()))
    # ---- per-window: real M2 scalars, C1/C2 matched, C3, C4, C8, verdict inputs
    for w in windows:
        a, b = WINDOWS[w]; mw = window_mask(times, w); tw = times[mw]
        W = dict(name=w, T=int(mw.sum()), nb=(int(r2["unfold"]["nb"]) if m2_ok else None))
        key = f"[{a},{b})"
        rw = r2["windows"][key] if (m2_ok and key in r2["windows"]) else None
        if rw is None or rw.get("status"):
            W["m2"] = dict(status=("UNFOLD_REFUSED" if not m2_ok else rw.get("status", "INAPPLICABLE")), T=W["T"])
        else:
            W["m2"] = win_scalars(rw)
            arrays[f"{w}/v_std"] = _sub(_std_vel(r2["unfolded"][mw], tw), rng)
            arrays[f"{w}/k_abs"] = _sub(np.abs(rw["k_samples"]), rng)
            arrays[f"{w}/Cx_x"] = rw["autocorr"]["x"]; arrays[f"{w}/Cx_C"] = rw["autocorr"]["C"]; arrays[f"{w}/Cx_n"] = rw["autocorr"]["n_pairs"].astype(float)
            arrays[f"{w}/hist"] = rw["curvature"]["hist"]; arrays[f"{w}/hist_edges"] = rw["curvature"]["hist_edges"]
        # M3 per window (C8)
        ev_w = [e for e in r3["events"] if e["window"] == w]
        fl_w = flagged[(tmid >= a) & (tmid < b)]
        span = float(tw[-1] - tw[0]) if len(tw) > 1 else float("nan")
        n_all, n_ok = len(ev_w), sum(not e["ambiguous"] for e in ev_w)
        W["m3"] = dict(n_events=n_all, n_events_unambiguous=n_ok, ambiguous_step_level_frac=(float(fl_w.mean()) if fl_w.size else float("nan")),
                       event_ambiguous_frac=(float(1 - n_ok / n_all) if n_all else float("nan")), span=span,
                       rate_all_per_step=(n_all / span if span > 0 else float("nan")), rate_unambiguous_per_step=(n_ok / span if span > 0 else float("nan")))
        # M5 per window (medians)
        if mw.sum():
            W["m5"] = {k: float(np.nanmedian(m5[k][mw].astype(float))) for k in ("eff_rank", "stable_rank", "top16_mass", "mp_ks", "n_upper_outliers", "sigma1_over_median", "htsr_alpha")}
            W["m5"]["withdrawn_frac"] = (float(np.mean([bool(x) for x in m5["mp_withdrawn"][mw]])) if m5meta["ks95"] is not None else None)
        # controls C1 / C2 / C3 / C4 (only where the real M2 window is applicable)
        ctl = dict(status="SKIPPED (real window inapplicable)")
        if W["m2"]["status"] == "OK" and len(tw) >= 4:
            ctl = dict(status="OK", x_target=W["m2"]["x_step_mean"], v_target=W["m2"]["vrms"], dt_ref=float(np.median(np.diff(tw))), families={})
            dt_ref = ctl["dt_ref"]
            for fam in ("c1", "b2", "po"):
                seeds = []
                for sd in range(nseed):
                    seed = 100000 * (sd + 1) + 1000 * layer + 10 * TYPES.index(M) + list(WINDOWS).index(w)
                    try:
                        S, r, meta = matched_family(fam, m, n, tw, ctl["v_target"], seed, dt_ref)
                        rec = win_scalars(r); rec["match"] = meta
                        if rec["status"] == "OK":
                            if sd == 0:
                                arrays[f"{w}/{fam}/v_std"] = _sub(r["_v_std"], rng); arrays[f"{w}/{fam}/k_abs"] = _sub(np.abs(r["k_samples"]), rng)
                                arrays[f"{w}/{fam}/Cx_C"] = r["autocorr"]["C"]; arrays[f"{w}/{fam}/Cx_n"] = r["autocorr"]["n_pairs"].astype(float)
                                arrays[f"{w}/{fam}/hist"] = r["curvature"]["hist"]
                            else:
                                arrays[f"{w}/{fam}/Cx_C_s{sd}"] = r["autocorr"]["C"]; arrays[f"{w}/{fam}/Cx_n_s{sd}"] = r["autocorr"]["n_pairs"].astype(float)
                    except Exception as e:
                        rec = dict(status=f"ERROR {type(e).__name__}: {e}")
                    seeds.append(rec)
                ctl["families"][fam] = seeds
            # C3 shuffle of the real series (window only)
            try:
                cl, cx = [], []
                for ps in range(N_SHUFFLE):
                    rsh = m2_single(C.shuffle(sig[mw], seed=3 + layer + 97 * ps), tw)
                    cl.append(rsh["autocorr"]["C_lag"][:4]); cx.append(rsh["autocorr"]["C"])
                cl = np.mean(cl, axis=0)
                dts = np.diff(tw)
                pred = -(np.sum(1 / (dts[1:] * dts[:-1])) / (len(dts) - 1)) / (np.sum(2 / dts ** 2) / len(dts))
                ctl["C3"] = dict(C_lag=[float(x) for x in cl], exact_lag1=float(pred), n_permutations=N_SHUFFLE,
                                 collapsed=bool(abs(cl[1] - pred) < 0.1 and np.max(np.abs(cl[2:4])) < 0.1),
                                 note="single-permutation noise is large when the window spans few correlation times (W1)")
                arrays[f"{w}/c3/Cx_C"] = np.nanmean(np.array(cx), axis=0)
            except Exception as e:
                ctl["C3"] = dict(status=f"ERROR {type(e).__name__}: {e}")
            # C4 (a) spectrum round-trip of the window's middle checkpoint
            try:
                j = int(np.where(mw)[0][len(tw) // 2])
                S32 = sig.copy(); S32[j] = sig[j].astype(np.float32).astype(np.float64)
                E0, _ = M2.unfold_series(sig, M2.PARAMS["top_k"], M2.PARAMS["band"], M2.PARAMS["kde_c"], M2.PARAMS["nonpos_max"])
                E1, _ = M2.unfold_series(S32, M2.PARAMS["top_k"], M2.PARAMS["band"], M2.PARAMS["kde_c"], M2.PARAMS["nonpos_max"])
                d_rt = float(np.sqrt(np.mean((E1[j] - E0[j]) ** 2)))
                d_step = float(np.sqrt(np.mean(np.diff(E0[mw], axis=0) ** 2)))
                ctl["C4_spectrum"] = dict(checkpoint=int(times[j]), unfolded_rms=d_rt, step_rms=d_step, ratio_to_step=(d_rt / d_step if d_step > 0 else float("nan")))
            except Exception as e:
                ctl["C4_spectrum"] = dict(status=f"ERROR {type(e).__name__}: {e}")
            # C4 (b) matrix-level synthetic floor at the real rms and shape (W2 only; one per unit)
            if w == "W2" or ("W2" not in windows and w == windows[0]):
                try:
                    tau = ctl["families"]["c1"][0]["match"]["tau"] if ctl["families"]["c1"][0].get("match") else C.tau_for_xstep(n, ctl["x_target"], dt_ref)
                    fl = C.roundtrip_floor(m, n, tw[:min(12, len(tw))], tau, M2.PARAMS["top_k"], M2.PARAMS["band"], M2.PARAMS["kde_c"], seed=layer, scale=float(np.median(rms)))
                    ctl["C4_matrix"] = dict(entry_rms=float(np.median(rms)), step_rms=fl["step_rms"], fp32=fl["fp32"], bf16_comparison_only=fl["bf16"])
                except Exception as e:
                    ctl["C4_matrix"] = dict(status=f"ERROR {type(e).__name__}: {e}")
        W["controls"] = ctl
        out["windows"][w] = W
    out["runtime_s"] = time.time() - t_unit
    part_json.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(part_npz, **{k: np.asarray(v) for k, v in arrays.items()})
    json.dump(out, open(part_json, "w"), indent=1, default=_jsonable)
    return out


def _jsonable(o):
    if isinstance(o, (np.floating, np.integer)): return o.item()
    if isinstance(o, np.bool_): return bool(o)
    if isinstance(o, np.ndarray): return o.tolist()
    if isinstance(o, Path): return str(o)
    raise TypeError(str(type(o)))


# ====================================================================== verdicts
def _zsep(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 2 or len(b) < 2: return float("nan")
    d = math.sqrt(a.var(ddof=1) + b.var(ddof=1))
    return float(abs(a.mean() - b.mean()) / d) if d > 0 else float("inf")


def _ok_fams(ctl, fam):
    return [s for s in ctl.get("families", {}).get(fam, []) if s.get("status") == "OK"]


def verdict_p2(W, arrays, flip=False):
    """P2 for one (matrix, window): see the module docstring. Returns dict(word, tags, components, n_k, reason)."""
    m2, ctl = W["m2"], W["controls"]
    tags = ["PROVISIONAL (curvature at bank cadence)"]
    if m2["status"] != "OK":
        return dict(word="NOT RESOLVABLE", tags=tags, reason=f"M2 {m2['status']}", n_k=0, components={})
    n_k = m2["n_k"]
    if n_k < DISCRIM_N["beta2"]:
        return dict(word="NOT RESOLVABLE", tags=tags, reason=f"n_k={n_k} < {DISCRIM_N['beta2']} (beta=2 discrimination size)", n_k=n_k, components={})
    c1, b2, po = _ok_fams(ctl, "c1"), _ok_fams(ctl, "b2"), _ok_fams(ctl, "po")
    if not c1 or not b2 or not po:
        return dict(word="NOT RESOLVABLE", tags=tags, reason="calibrators missing", n_k=n_k, components={})
    nb = int(W.get("nb") or NB_REF); ts = math.sqrt(max(1.0, NB_REF / nb))      # declared tolerance scale (1 on the real bank)
    # --- velocity
    vr = m2["velocity"]; mean = lambda L, f: float(np.mean([f(s) for s in L]))
    dev_v = dict(skew=abs(vr["skew"] - mean(c1, lambda s: s["velocity"]["skew"])) / (TOL["skew"] * ts),
                 ex_kurt=abs(vr["ex_kurt"] - mean(c1, lambda s: s["velocity"]["ex_kurt"])) / (TOL["ex_kurt"] * ts),
                 ks_gauss=(vr["ks_gauss"] - mean(c1, lambda s: s["velocity"]["ks_gauss"])) / (TOL["ks_gauss"] * ts))
    vel_word = "HOLDS" if max(dev_v.values()) <= 1 else "FAILS"
    # --- C(x)
    L = min(TOL["n_lag"], len(m2["C_lag"]) - 1, min(len(s["C_lag"]) for s in c1) - 1)
    clag_c1 = np.mean([s["C_lag"][1:L + 1] for s in c1], axis=0)
    dev_clag = float(np.max(np.abs(np.array(m2["C_lag"][1:L + 1]) - clag_c1)) / (TOL["C_lag"] * ts)) if L >= 1 else 0.0
    dev_cx = 0.0
    w = W["name"]
    if f"{w}/Cx_C" in arrays and f"{w}/c1/Cx_C" in arrays:
        x = arrays[f"{w}/Cx_x"]; Cr = arrays[f"{w}/Cx_C"]; nr = arrays[f"{w}/Cx_n"]
        Cs = [arrays[f"{w}/c1/Cx_C"]]; ns = [arrays[f"{w}/c1/Cx_n"]]
        for sd in range(1, len(c1)):
            if f"{w}/c1/Cx_C_s{sd}" in arrays: Cs.append(arrays[f"{w}/c1/Cx_C_s{sd}"]); ns.append(arrays[f"{w}/c1/Cx_n_s{sd}"])
        Cc = np.nanmean(np.array(Cs), axis=0); nc = np.min(np.array(ns), axis=0)
        ok = (x <= TOL["x_max"]) & (nr >= M2.PARAMS["min_pairs"]) & (nc >= M2.PARAMS["min_pairs"]) & np.isfinite(Cr) & np.isfinite(Cc)
        dev_cx = float(np.max(np.abs(Cr[ok] - Cc[ok])) / (TOL["Cx"] * ts)) if ok.any() else 0.0
    cx_word = "HOLDS" if max(dev_clag, dev_cx) <= 1 else "FAILS"
    # --- curvature (PROVISIONAL)
    S = m2["curvature"]["abs_k_median"]
    S1 = [s["curvature"]["abs_k_median"] for s in c1]; S2 = [s["curvature"]["abs_k_median"] for s in b2]; Sp = [s["curvature"]["abs_k_median"] for s in po]
    thr_lo, thr_hi = (np.mean(Sp) + np.mean(S1)) / 2, (np.mean(S1) + np.mean(S2)) / 2
    witnesses_ok = bool(min(S2) > thr_hi and max(Sp) < thr_lo and max(S1) < thr_hi and min(S1) > thr_lo)
    in_band = bool(thr_lo < S < thr_hi)
    if flip: in_band = not in_band
    curv = dict(S=S, S_c1=S1, S_b2=S2, S_po=Sp, thr_lo=float(thr_lo), thr_hi=float(thr_hi), z_c1_b2=_zsep(S1, S2), z_c1_po=_zsep(S1, Sp),
                witnesses_separated=witnesses_ok, flipped=bool(flip), PROVISIONAL=True,
                x_step_real=m2["x_step_mean"], x_step_c1=float(np.mean([s["x_step_mean"] for s in c1])))
    comps = dict(velocity=dict(word=vel_word, dev=dev_v), Cx=dict(word=cx_word, dev_C_lag=dev_clag, dev_Cx=dev_cx, n_lag=L), curvature=curv, tolerance_scale=ts, nb=nb)
    if not witnesses_ok:
        curv["word"] = "NOT RESOLVABLE"
        return dict(word="NOT RESOLVABLE", tags=tags, reason="witnesses (beta=2 / Poisson) not separated from C1 at this n through the identical unfolding", n_k=n_k, components=comps)
    curv["word"] = "HOLDS" if in_band else "FAILS"
    word = "FAILS" if "FAILS" in (vel_word, cx_word, curv["word"]) else "HOLDS"
    return dict(word=word, tags=tags, reason="", n_k=n_k, components=comps)


def _descriptive(w, v):
    """W3 (the extension range) is DESCRIPTIVE only (PDYN_PREREG §1): the mechanical word is kept in parentheses."""
    if w == "W3" and v.get("word") and not str(v["word"]).startswith("DESCRIPTIVE"):
        v["word"] = f"DESCRIPTIVE ({v['word']})"; v["tags"] = list(v.get("tags", [])) + ["DESCRIPTIVE (W3)"]
    return v


def aggregate_p2(per_matrix):
    """Arm-level word per window from the per-matrix words: majority rule per component (see docstring)."""
    words = [v["word"] for v in per_matrix]
    n = len(words); n_nr = words.count("NOT RESOLVABLE")
    out = dict(n_matrices=n, n_not_resolvable=n_nr, n_holds=words.count("HOLDS"), n_fails=words.count("FAILS"),
               tags=["PROVISIONAL (curvature at bank cadence)"])
    if n == 0 or n_nr > n / 2:
        out["word"] = "NOT RESOLVABLE"; out["reason"] = f"{n_nr}/{n} matrices NOT RESOLVABLE"; return out
    res = [v for v in per_matrix if v["word"] != "NOT RESOLVABLE"]
    comp = {}
    for c in ("velocity", "Cx", "curvature"):
        ws = [v["components"][c]["word"] for v in res]
        comp[c] = dict(frac_holds=ws.count("HOLDS") / len(ws), word=("HOLDS" if ws.count("HOLDS") > len(ws) / 2 else "FAILS"))
    out["components"] = comp
    out["word"] = "HOLDS" if all(c["word"] == "HOLDS" for c in comp.values()) else "FAILS"
    out["frac_matrices_fails"] = words.count("FAILS") / n
    return out


def verdict_p3(m5a, m5b, floor_pair, window="W2"):
    """m5x: dict (layer, type) -> dict(steps, eff_rank, top16_mass, n_upper_outliers, mp_withdrawn). a = AdamW, b = Muon."""
    rows = []
    for key in sorted(set(m5a) & set(m5b)):
        A, B = m5a[key], m5b[key]
        a0, b0 = WINDOWS[window]
        common = np.intersect1d(A["steps"], B["steps"]); common = common[(common >= a0) & (common < b0)]
        if len(common) == 0: continue
        ia = np.searchsorted(A["steps"], common); ib = np.searchsorted(B["steps"], common)
        d_eff = float(np.median(B["eff_rank"][ib] - A["eff_rank"][ia])); d_top = float(np.median(B["top16_mass"][ib] - A["top16_mass"][ia]))
        fl = 0.0
        if floor_pair is not None and key in floor_pair[0] and key in floor_pair[1]:
            F0, F1 = floor_pair[0][key], floor_pair[1][key]
            cf = np.intersect1d(np.intersect1d(F0["steps"], F1["steps"]), common)
            if len(cf): fl = float(np.median(np.abs(F1["eff_rank"][np.searchsorted(F1["steps"], cf)] - F0["eff_rank"][np.searchsorted(F0["steps"], cf)])))
        wd = (A["mp_withdrawn"][ia] != 1) & (B["mp_withdrawn"][ib] != 1) & (A["mp_withdrawn"][ia] != -1)
        d_out = float(np.median(B["n_upper_outliers"][ib][wd] - A["n_upper_outliers"][ia][wd])) if wd.any() else float("nan")
        rows.append(dict(layer=key[0], type=key[1], n_steps=int(len(common)), d_eff_rank=d_eff, floor=fl, d_top16_mass=d_top, d_n_outliers=d_out, n_steps_mp_valid=int(wd.sum())))
    if not rows: return dict(word="NOT RESOLVABLE", reason="no common matrices/steps", rows=rows)
    n = len(rows)
    n_hi = sum(r["d_eff_rank"] > r["floor"] for r in rows); n_le = sum(r["d_eff_rank"] <= 0 for r in rows)
    eff = "HOLDS" if n_hi > n / 2 else ("FAILS" if n_le > n / 2 else "NOT RESOLVABLE")
    n_weak = sum(r["d_top16_mass"] < 0 for r in rows)
    weak = "HOLDS" if n_weak > n / 2 else "FAILS"
    outl = [r["d_n_outliers"] for r in rows if np.isfinite(r["d_n_outliers"])]
    fewer = ("WITHDRAWN (MP fit fails on both sides at every matched step)" if not outl else
             ("HOLDS" if sum(x < 0 for x in outl) > len(outl) / 2 else ("FAILS" if sum(x >= 0 for x in outl) > len(outl) / 2 else "NOT RESOLVABLE")))
    word = "HOLDS" if (eff == "HOLDS" and weak == "HOLDS") else ("FAILS" if eff == "FAILS" else "NOT RESOLVABLE")
    return dict(word=word, components=dict(effective_rank=dict(word=eff, n_above_floor=n_hi, n_muon_le_adamw=n_le, n=n),
                                           weaker_outliers_top16_mass=dict(word=weak, n_lower=n_weak, n=n),
                                           fewer_outliers_mp=dict(word=fewer, n_matrices_mp_valid=len(outl))),
                floor_source=("A0 vs A0r, same steps (one draw)" if floor_pair is not None else "NONE (floor = 0)"), rows=rows, window=window)


def verdict_p5(event_times, intervals, tl, rng):
    """event_times: sorted array (one event set); intervals: dict(t0, t1, lr_mean, dloss) arrays; tl: trainlog or None."""
    tags = ["PROVISIONAL (bank cadence)"]
    n = len(event_times)
    if tl is None: return dict(word="NOT RESOLVABLE", tags=tags, reason="no trainlog (loss / lr unavailable)", n_events=n)
    if n < P5_MIN_EVENTS: return dict(word="NOT RESOLVABLE", tags=tags, reason=f"n_events={n} < {P5_MIN_EVENTS}", n_events=n)
    t0, t1 = intervals["t0"], intervals["t1"]; dt = t1 - t0
    counts = np.array([((event_times >= a) & (event_times < b)).sum() for a, b in zip(t0, t1)], float)
    rate = counts / dt
    ok = np.isfinite(intervals["lr_mean"]) & np.isfinite(intervals["dloss"])
    rho, p_rho = stats.spearmanr(rate[ok], intervals["lr_mean"][ok]) if ok.sum() >= 5 else (float("nan"), float("nan"))
    obs = float(np.sum(counts[ok] * np.abs(intervals["dloss"][ok])) / max(counts[ok].sum(), 1))
    pw = dt[ok] / dt[ok].sum(); m = int(counts[ok].sum()); null = np.empty(N_NULL)
    for i in range(N_NULL):
        c = rng.multinomial(m, pw); null[i] = np.sum(c * np.abs(intervals["dloss"][ok])) / max(m, 1)
    p_cl = float((null >= obs).mean()); z_cl = float((obs - null.mean()) / null.std()) if null.std() > 0 else float("nan")
    rate_ok = bool(np.isfinite(rho) and rho > 0 and p_rho < 0.05); clus_ok = bool(p_cl < 0.05)
    word = "HOLDS" if (rate_ok and clus_ok) else "FAILS"
    return dict(word=word, tags=tags, n_events=n, spearman_rate_lr=dict(rho=float(rho), p=float(p_rho), passes=rate_ok),
                clustering_vs_shuffled_time=dict(mean_abs_dloss_at_events=obs, null_mean=float(null.mean()), null_sd=float(null.std()), z=z_cl, p=p_cl, passes=clus_ok, n_null=N_NULL),
                falsifier=("flat rate" if not rate_ok else "") + (" / no clustering" if not clus_ok else ""))


def _rtilde(s):
    s = np.asarray(s, float); s = s[s > 0]
    if len(s) < 2: return float("nan")
    return float(np.mean(np.minimum(s[1:], s[:-1]) / np.maximum(s[1:], s[:-1])))


def verdict_p6(event_times, span, rng):
    tags = ["PROVISIONAL (bank cadence)", "DESCRIPTIVE (no prediction)"]
    n = len(event_times)
    out = dict(word="DESCRIPTIVE", tags=tags, n_events=n, class_word=f"none (n < {P6_MIN_EVENTS_CLASS})" if n < P6_MIN_EVENTS_CLASS else "see statistics; ARS calibrated classification deferred")
    if n < 3: out["reason"] = "n < 3"; return out
    s = np.diff(np.sort(event_times))
    out.update(cv=float(np.std(s) / np.mean(s)) if np.mean(s) > 0 else float("nan"), r_tilde=_rtilde(s), r_tilde_poisson=2 * math.log(2) - 1, r_tilde_goe=0.5307)
    null = np.array([_rtilde(np.diff(np.sort(rng.uniform(span[0], span[1], n)))) for _ in range(500)])
    out["r_tilde_uniform_null"] = dict(mean=float(np.nanmean(null)), sd=float(np.nanstd(null)), z=float((out["r_tilde"] - np.nanmean(null)) / np.nanstd(null)) if np.nanstd(null) > 0 else float("nan"))
    out["note"] = "event times are refined vertices on a 10/25/100-step grid; interval statistics inherit the grid"
    return out


def verdict(prediction, *a, **kw):
    """Single mechanical entry point for the PDYN_PREREG §3 words."""
    if prediction == "P1": return dict(word="NOT COMPUTED HERE", note="read on the existing <r~>/q (ARMB_FINDINGS §6)")
    if prediction == "P2": return verdict_p2(*a, **kw)
    if prediction == "P3": return verdict_p3(*a, **kw)
    if prediction == "P4": return dict(word="NOT READ", note="phase 2 only (M4 trajectory Gram)")
    if prediction == "P5": return verdict_p5(*a, **kw)
    if prediction == "P6": return verdict_p6(*a, **kw)
    raise ValueError(prediction)


# ====================================================================== assembly per arm
def intervals_from(steps, tl):
    t = np.array(steps, float); t0, t1 = t[:-1], t[1:]
    lr_mean = np.full(len(t0), np.nan); dloss = np.full(len(t0), np.nan); loss_mean = np.full(len(t0), np.nan)
    if tl is not None:
        sm = np.convolve(tl["loss"], np.ones(10) / 10, mode="same")
        for i, (a, b) in enumerate(zip(t0, t1)):
            m = (tl["step"] > a) & (tl["step"] <= b)
            if m.any():
                lr_mean[i] = np.nanmean(tl["lr"][m]); loss_mean[i] = np.mean(tl["loss"][m])
                ia, ib = np.searchsorted(tl["step"], a), np.searchsorted(tl["step"], b)
                dloss[i] = sm[min(ib, len(sm) - 1)] - sm[min(ia, len(sm) - 1)]
    return dict(t0=t0, t1=t1, lr_mean=lr_mean, dloss=dloss, loss_mean=loss_mean)


def assemble_arm(out, arm, steps, layers, windows, tl, flip):
    parts = {}
    for L in layers:
        for M in TYPES:
            pj = out / arm / "parts" / f"L{L:02d}_{M}.json"
            if pj.exists():
                parts[(L, M)] = (json.load(open(pj)), dict(np.load(pj.with_suffix(".npz"))))
    rng = np.random.default_rng(20261002)
    # ---- controls (FIRST in the output ordering), then m1..m6
    controls = dict(order_note="controls precede the real reading (PDYN_PREREG §4)", C5={}, per_matrix={})
    for (L, M), (P, A) in parts.items():
        controls["C5"][f"L{L:02d}_{M}"] = P["controls"]["C5"]
        controls["per_matrix"][f"L{L:02d}_{M}"] = {w: P["windows"][w]["controls"] for w in P["windows"]}
    controls["C5_all_bit_identical"] = all(v["pass_"] for v in controls["C5"].values()) if controls["C5"] else None
    c3 = [P["windows"][w]["controls"].get("C3", {}).get("collapsed") for (P, A) in parts.values() for w in P["windows"] if P["windows"][w]["controls"].get("status") == "OK"]
    controls["C3_collapsed_frac"] = float(np.mean([bool(x) for x in c3 if x is not None])) if c3 else None
    c4 = [P["windows"][w]["controls"].get("C4_spectrum", {}).get("ratio_to_step") for (P, A) in parts.values() for w in P["windows"] if P["windows"][w]["controls"].get("status") == "OK"]
    controls["C4_spectrum_ratio_median"] = float(np.nanmedian([x for x in c4 if x is not None])) if c4 else None
    c4m = [P["windows"][w]["controls"]["C4_matrix"]["fp32"]["ratio_to_step"] for (P, A) in parts.values() for w in P["windows"] if "C4_matrix" in P["windows"][w]["controls"] and "fp32" in P["windows"][w]["controls"]["C4_matrix"]]
    controls["C4_matrix_fp32_ratio_median"] = float(np.median(c4m)) if c4m else None
    c8 = {w: dict(n_all=int(sum(P["windows"][w]["m3"]["n_events"] for (P, A) in parts.values())),
                  n_unambiguous=int(sum(P["windows"][w]["m3"]["n_events_unambiguous"] for (P, A) in parts.values())),
                  ambiguous_step_level_frac_median=float(np.nanmedian([P["windows"][w]["m3"]["ambiguous_step_level_frac"] for (P, A) in parts.values()])) if parts else None) for w in windows}
    controls["C8"] = c8
    json.dump(controls, open(out / arm / "controls.json", "w"), indent=1, default=_jsonable)
    # ---- m1
    m1 = {f"L{L:02d}_{M}": dict(steps=A["steps"].tolist(), sigma1=A["sigma1"].tolist(), sigma16=A["sigma16"].tolist(), sigma_median=A["sigma_median"].tolist(),
                                fro=A["fro"].tolist(), rms=A["rms"].tolist(), fro_vs_rms_max_rel_dev=P["m1"]["fro_vs_rms_max_rel_dev"]) for (L, M), (P, A) in parts.items()}
    json.dump(m1, open(out / arm / "m1.json", "w"), indent=1)
    # ---- m2 (+ verdicts per matrix / window)
    m2 = dict(per_matrix={}, verdict_p2={}, x_step={})
    per_win = {w: [] for w in windows}
    for (L, M), (P, A) in parts.items():
        key = f"L{L:02d}_{M}"; m2["per_matrix"][key] = {w: P["windows"][w]["m2"] for w in P["windows"]}
        m2["per_matrix"][key]["unfold"] = P.get("unfold"); m2["per_matrix"][key]["notes"] = P["notes"]
        for w in windows:
            if w not in P["windows"]: continue
            v = verdict("P2", P["windows"][w], A, flip=flip); v["layer"] = L; v["type"] = M
            m2["verdict_p2"].setdefault(w, {})[key] = v; per_win[w].append(v)
    for w in windows:
        xs = {M: [P["windows"][w]["m2"].get("x_step_mean") for (L2, M2_), (P, A) in parts.items() if M2_ == M and P["windows"].get(w, {}).get("m2", {}).get("status") == "OK"] for M in TYPES}
        m2["x_step"][w] = {M: (float(np.median(v)) if v else None) for M, v in xs.items()}
    m2["arm_verdict_p2"] = {w: _descriptive(w, aggregate_p2(per_win[w])) for w in windows}
    m2["per_type_verdict_p2"] = {w: {M: _descriptive(w, aggregate_p2([v for v in per_win[w] if v["type"] == M])) for M in TYPES} for w in windows}
    for w in windows:
        for v in m2["verdict_p2"].get(w, {}).values(): _descriptive(w, v)
    m2["flip_threshold"] = bool(flip)
    json.dump(m2, open(out / arm / "m2.json", "w"), indent=1, default=_jsonable)
    # ---- m3 (+ P5 / P6 per window, all vs unambiguous = C8)
    intervals = intervals_from(steps, tl)
    m3 = dict(per_matrix={f"L{L:02d}_{M}": dict(ambiguous_frac=P["m3"]["ambiguous_frac"], mean_quality=P["m3"]["mean_quality"], total_swaps=P["m3"]["total_swaps"],
                                                n_events=P["m3"]["n_events"], n_events_ambiguous=P["m3"]["n_events_ambiguous"], windows={w: P["windows"][w]["m3"] for w in P["windows"]})
                          for (L, M), (P, A) in parts.items()},
              events=[dict(layer=L, type=M, **e) for (L, M), (P, A) in parts.items() for e in P["m3"]["events"]], verdict_p5={}, verdict_p6={})
    for w in windows:
        a, b = WINDOWS[w]; tw = [s for s in steps if a <= s < b]
        span = (float(tw[0]), float(tw[-1])) if len(tw) > 1 else (a, a)
        ev_all = np.sort([e["t_min"] for e in m3["events"] if e["window"] == w]); ev_ok = np.sort([e["t_min"] for e in m3["events"] if e["window"] == w and not e["ambiguous"]])
        mi = (intervals["t0"] >= a) & (intervals["t1"] <= b + 1e-9)
        iv = {k: v[mi] for k, v in intervals.items()}
        m3["verdict_p5"][w] = dict(all_events=_descriptive(w, verdict("P5", ev_all, iv, tl, rng)), unambiguous_only=_descriptive(w, verdict("P5", ev_ok, iv, tl, rng)))
        m3["verdict_p5"][w]["stable_when_ambiguous_excluded"] = m3["verdict_p5"][w]["all_events"]["word"] == m3["verdict_p5"][w]["unambiguous_only"]["word"]
        m3["verdict_p6"][w] = dict(all_events=verdict("P6", ev_all, span, rng), unambiguous_only=verdict("P6", ev_ok, span, rng))
    json.dump(m3, open(out / arm / "m3.json", "w"), indent=1, default=_jsonable)
    # ---- m5
    m5 = dict(meta=next(iter(parts.values()))[0]["m5"]["meta"] if parts else None, per_matrix={})
    for (L, M), (P, A) in parts.items():
        m5["per_matrix"][f"L{L:02d}_{M}"] = dict(steps=A["steps"].tolist(), **{k[3:]: A[k].tolist() for k in A if k.startswith("m5/")},
                                                 windows={w: P["windows"][w].get("m5") for w in P["windows"]}, withdrawn_frac=P["m5"]["withdrawn_frac"],
                                                 htsr_label="FRAGILE: read only beside its ESD plot")
    json.dump(m5, open(out / arm / "m5.json", "w"), indent=1, default=_jsonable)
    # ---- m6
    if tl is None:
        m6 = dict(status="SKIPPED", note=f"trainlog absent for {arm}; M6 (event rates over loss / lr) not computed")
    else:
        ev_all = np.array([e["t_min"] for e in m3["events"]]); ev_ok = np.array([e["t_min"] for e in m3["events"] if not e["ambiguous"]])
        m6 = dict(status="OK", t0=intervals["t0"].tolist(), t1=intervals["t1"].tolist(), loss_mean=intervals["loss_mean"].tolist(), dloss=intervals["dloss"].tolist(),
                  lr_mean=intervals["lr_mean"].tolist(),
                  n_events_all=[int(((ev_all >= a) & (ev_all < b)).sum()) for a, b in zip(intervals["t0"], intervals["t1"])],
                  n_events_unambiguous=[int(((ev_ok >= a) & (ev_ok < b)).sum()) for a, b in zip(intervals["t0"], intervals["t1"])],
                  trainlog_steps=int(len(tl["step"])), trainlog_last_step=int(tl["step"][-1]))
    json.dump(m6, open(out / arm / "m6.json", "w"), indent=1, default=_jsonable)
    return dict(parts=parts, controls=controls, m1=m1, m2=m2, m3=m3, m5=m5, m6=m6, intervals=intervals, tl=tl)


# ====================================================================== long tables
def long_tables(out, arms_data, windows):
    import pandas as pd
    r15, r2, r3, rc = [], [], [], []
    for arm, D in arms_data.items():
        for (L, M), (P, A) in D["parts"].items():
            steps = A["steps"]
            for i, s in enumerate(steps):
                w = next((w for w in windows if WINDOWS[w][0] <= s < WINDOWS[w][1]), None)
                row = dict(arm=arm, layer=L, type=M, window=w, step=int(s), sigma1=A["sigma1"][i], sigma16=A["sigma16"][i], sigma_median=A["sigma_median"][i], fro=A["fro"][i], rms=A["rms"][i])
                for k in A:
                    if k.startswith("m5/"): row[k[3:]] = A[k][i]
                r15.append(row)
            for w in P["windows"]:
                m2 = P["windows"][w]["m2"]
                row = dict(arm=arm, layer=L, type=M, window=w, status=m2["status"], T=m2["T"])
                if m2["status"] == "OK":
                    row.update(x_step_mean=m2["x_step_mean"], vrms=m2["vrms"], n_k=m2["n_k"], **{f"v_{k}": v for k, v in m2["velocity"].items()},
                               C_lag1=m2["C_lag"][1] if len(m2["C_lag"]) > 1 else np.nan, **{f"k_{k}": v for k, v in m2["curvature"].items() if k != "n"})
                    v = D["m2"]["verdict_p2"].get(w, {}).get(f"L{L:02d}_{M}", {}); row["p2_word"] = v.get("word")
                    for c in ("velocity", "Cx", "curvature"):
                        if c in v.get("components", {}): row[f"p2_{c}"] = v["components"][c].get("word")
                row.update(**{f"m3_{k}": v for k, v in P["windows"][w]["m3"].items()})
                r2.append(row)
                ctl = P["windows"][w]["controls"]
                if ctl.get("status") == "OK":
                    for fam, seeds in ctl["families"].items():
                        for sd, rec in enumerate(seeds):
                            if rec.get("status") != "OK": rc.append(dict(arm=arm, layer=L, type=M, window=w, family=fam, seed=sd, status=rec.get("status"))); continue
                            rc.append(dict(arm=arm, layer=L, type=M, window=w, family=fam, seed=sd, status="OK", x_step_mean=rec["x_step_mean"], v_target=rec["match"]["v_target"], matched=rec["match"]["matched"],
                                           tau=rec["match"]["tau"], passes=rec["match"]["passes"], **{f"v_{k}": v for k, v in rec["velocity"].items()},
                                           C_lag1=rec["C_lag"][1] if len(rec["C_lag"]) > 1 else np.nan, abs_k_median=rec["curvature"]["abs_k_median"], nu_fixed=rec["curvature"]["nu_fixed"]))
                    if "C3" in ctl and "C_lag" in ctl["C3"]:
                        rc.append(dict(arm=arm, layer=L, type=M, window=w, family="c3_shuffle", seed=0, status="OK", C_lag1=ctl["C3"]["C_lag"][1], exact_lag1=ctl["C3"]["exact_lag1"], collapsed=ctl["C3"]["collapsed"]))
            for e in P["m3"]["events"]:
                r3.append(dict(arm=arm, layer=L, type=M, window=e["window"], step=e["t_min"], **{k: v for k, v in e.items() if k != "window"}))
    for name, rows in (("long_m1m5", r15), ("long_m2", r2), ("long_m3_events", r3), ("long_controls", rc)):
        df = pd.DataFrame(rows)
        try:
            df.to_parquet(out / f"{name}.parquet", index=False)
        except Exception as e:
            log(f"parquet failed for {name}: {e}; csv only")
        df.to_csv(out / f"{name}.csv", index=False)


# ====================================================================== figures
def figures_arm(out, arm, D, windows):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    figs = out / "figs"; figs.mkdir(exist_ok=True)
    parts = D["parts"]
    for w in windows:
        for M in TYPES:
            keys = [(L, M2_) for (L, M2_) in parts if M2_ == M and f"{w}/v_std" in parts[(L, M2_)][1]]
            if not keys: continue
            vr = np.concatenate([parts[k][1][f"{w}/v_std"] for k in keys])
            vc = np.concatenate([parts[k][1][f"{w}/c1/v_std"] for k in keys if f"{w}/c1/v_std" in parts[k][1]]) if any(f"{w}/c1/v_std" in parts[k][1] for k in keys) else None
            fig, ax = plt.subplots(figsize=(6, 4))
            bins = np.linspace(-6, 6, 97)
            ax.hist(vr, bins=bins, density=True, histtype="step", color="C0", label=f"{arm} {M} (layers pooled, standardised; n={vr.size})")
            if vc is not None: ax.hist(vc, bins=bins, density=True, histtype="step", color="C1", label="C1 beta=1, same cadence, matched x_step")
            ax.plot(bins, stats.norm.pdf(bins), "k--", lw=1, label="Gaussian")
            ax.set_yscale("log"); ax.set_ylim(1e-5, 1); ax.set_xlabel("velocity / sd"); ax.set_ylabel("density"); ax.legend(fontsize=7)
            ax.set_title(f"M2 velocity distribution -- {arm} {M} -- window {w} {WINDOWS[w][0]:.0f}..{min(WINDOWS[w][1], 1e5):.0f}")
            fig.tight_layout(); fig.savefig(figs / f"{arm}_{w}_{M}_vhist.png", dpi=110); plt.close(fig)
            # C(x)
            fig, ax = plt.subplots(figsize=(6, 4))
            x = parts[keys[0]][1][f"{w}/Cx_x"]
            for lab, kk, col in (("trained", "Cx_C", "C0"), ("C1 beta=1", "c1/Cx_C", "C1"), ("C2 beta=2", "b2/Cx_C", "C2"), ("C2 Poisson", "po/Cx_C", "C3"), ("C3 shuffled", "c3/Cx_C", "C7")):
                cs = [parts[k][1][f"{w}/{kk}"] for k in keys if f"{w}/{kk}" in parts[k][1]]
                if cs: ax.plot(x, np.nanmean(np.array(cs), axis=0), marker="o", ms=3, color=col, label=f"{lab} (layer mean)")
            ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("rescaled lag x"); ax.set_ylabel("C(x)"); ax.legend(fontsize=7)
            ax.set_title(f"M2 velocity autocorrelation C(x) -- {arm} {M} -- window {w}")
            fig.tight_layout(); fig.savefig(figs / f"{arm}_{w}_{M}_Cx.png", dpi=110); plt.close(fig)
            # |k|
            fig, ax = plt.subplots(figsize=(6, 4))
            kb = np.logspace(-3, 2, 61)
            for lab, kk, col in (("trained", "k_abs", "C0"), ("C1 beta=1 same cadence", "c1/k_abs", "C1"), ("C2 beta=2", "b2/k_abs", "C2"), ("C2 Poisson", "po/k_abs", "C3")):
                ks = [parts[k][1][f"{w}/{kk}"] for k in keys if f"{w}/{kk}" in parts[k][1]]
                if ks:
                    kk_ = np.concatenate(ks); ax.hist(kk_, bins=kb, density=True, histtype="step", color=col, label=f"{lab} (median {np.median(kk_):.3f})")
            ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("|k| (ZD scale, beta=1)"); ax.set_ylabel("density"); ax.legend(fontsize=7)
            ax.set_title(f"M2 curvature |k| (PROVISIONAL) -- {arm} {M} -- window {w}")
            fig.tight_layout(); fig.savefig(figs / f"{arm}_{w}_{M}_kabs.png", dpi=110); plt.close(fig)
    # M3 raster over loss / lr
    fig, ax = plt.subplots(figsize=(9, 5))
    rows = sorted(parts); ylab = []
    for i, (L, M) in enumerate(rows):
        ev = parts[(L, M)][0]["m3"]["events"]
        ta = [e["t_min"] for e in ev if not e["ambiguous"]]; tb = [e["t_min"] for e in ev if e["ambiguous"]]
        ax.scatter(ta, [i] * len(ta), marker="|", color="C0", s=60, label="event (unambiguous)" if i == 0 else None)
        ax.scatter(tb, [i] * len(tb), marker="|", color="C3", s=60, label="event (ambiguous, C8)" if i == 0 else None)
        ylab.append(f"L{L}{M}")
    ax.set_yticks(range(len(rows))); ax.set_yticklabels(ylab, fontsize=6)
    tl = D["tl"]
    if tl is not None and len(rows):
        lo = tl["loss"]; lo = (lo - lo.min()) / max(lo.max() - lo.min(), 1e-12) * (len(rows) - 1)
        lr = tl["lr"]; lr = (lr - np.nanmin(lr)) / max(np.nanmax(lr) - np.nanmin(lr), 1e-12) * (len(rows) - 1)
        ax.plot(tl["step"], lo, color="k", lw=0.8, alpha=0.7, label="loss (scaled to axis)"); ax.plot(tl["step"], lr, color="C2", lw=0.8, alpha=0.8, label="lr (scaled to axis)")
    for w in windows:
        ax.axvline(WINDOWS[w][0], color="grey", ls=":", lw=0.8)
    ax.set_xlabel("training step"); ax.set_ylabel("(layer, type)"); ax.legend(fontsize=7, loc="upper right")
    ax.set_title(f"M3 avoided-crossing events (PROVISIONAL) over loss / lr -- {arm} -- windows {' '.join(windows)}")
    fig.tight_layout(); fig.savefig(figs / f"{arm}_m3_raster.png", dpi=110); plt.close(fig)


def figures_summary(out, arms_data, windows):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    figs = out / "figs"; figs.mkdir(exist_ok=True)
    for stat in ("eff_rank", "stable_rank", "top16_mass"):
        for M in TYPES:
            fig, ax = plt.subplots(figsize=(7, 4)); any_ = False
            for arm, D in arms_data.items():
                ser = [(A["steps"], A[f"m5/{stat}"]) for (L, M2_), (P, A) in D["parts"].items() if M2_ == M]
                if not ser: continue
                steps = ser[0][0]; med = np.nanmedian(np.array([s[1] for s in ser]), axis=0)
                opt = OPTIMIZER.get(arm, "?")
                ax.plot(steps, med, ls=("--" if opt == "Muon" else "-"), label=f"{arm} ({opt}), median over layers"); any_ = True
            if not any_: plt.close(fig); continue
            for w in windows: ax.axvline(WINDOWS[w][0], color="grey", ls=":", lw=0.8)
            ax.set_xlabel("training step"); ax.set_ylabel(stat); ax.legend(fontsize=7)
            ax.set_title(f"M5 {stat} -- {M} -- AdamW (solid) vs Muon (dashed) -- windows {' '.join(windows)} (DESCRIPTIVE)")
            fig.tight_layout(); fig.savefig(figs / f"m5_{stat}_{M}.png", dpi=110); plt.close(fig)


# ====================================================================== fake bank
def _fake_arm_spec(arm):
    times_full = C.real_grid(3000)
    return {"FAKE_C1": ("c1", times_full), "FAKE_B2": ("b2", times_full), "FAKE_PO": ("po", times_full),
            "FAKE_SHORT": ("c1", np.arange(500, 601, 25, dtype=float))}[arm]


def build_fake_bank(root, arms=FAKE_ARMS, n=256, xstep=0.1, seed=0, workers=1):
    """Builds the requested fake arms (one process per arm when workers > 1); the manifest accumulates."""
    root = Path(root); root.mkdir(parents=True, exist_ok=True)
    mf = root / "FAKE_MANIFEST.json"
    manifest = json.load(open(mf)) if mf.exists() else dict(n=n, xstep=xstep, arms={}, planted=dict(type="O", layer=0, t0=1500.0, coupling=0.05, slope=1e-3))
    todo = [a for a in arms if a not in manifest["arms"]]
    if todo:
        jobs = [(str(root), a, n, xstep, seed + 17 * FAKE_ARMS.index(a)) for a in todo]
        if workers > 1 and len(jobs) > 1:
            with ProcessPoolExecutor(max_workers=min(workers, len(jobs))) as ex:
                res = list(ex.map(_build_fake_arm, jobs))
        else:
            res = [_build_fake_arm(j) for j in jobs]
        for a, r in zip(todo, res): manifest["arms"][a] = r
        if res and res[0].get("planted_truth"): manifest["planted"].update(res[0]["planted_truth"])
        json.dump(manifest, open(mf, "w"), indent=1)
    return manifest


def _build_fake_arm(args):
    root, arm, n, xstep, seed = args
    fam, times = _fake_arm_spec(arm)
    return _build_fake_arm_impl(Path(root), arm, fam, times, n, xstep, seed)


def _build_fake_arm_impl(root, arm, fam, times, n=256, xstep=0.1, seed=0):
    """Synthetic bank from the sealed calibrators: same keys / shapes / grid structure as cache/armb; 2 layers; types
    Q/K/V/O n x n, MLP_IN 4n x n, MLP_OUT n x 4n; entries rms 0.02. FAKE_C1 beta=1 smooth GP (pdyn_calib.kl_factor),
    FAKE_B2 beta=2 (complex W; U32/V32 = orthonormalised real parts, PLACEHOLDERS: M3 is not under test there),
    FAKE_PO Poisson walk (static random frames), FAKE_SHORT = beta=1 on 5 checkpoints 500..600. A planted avoided
    crossing (pdyn_calib.planted_crossing, t0 = 1500, 2c = 0.1) replaces the top-16 of type O, layer 0, in every arm.
    Fake trainlogs under <root>/_staging/<arm>/trainlog.jsonl."""
    rng = np.random.default_rng(seed)
    shapes = {"Q": (n, n), "K": (n, n), "V": (n, n), "O": (n, n), "MLP_IN": (4 * n, n), "MLP_OUT": (n, 4 * n)}
    scale = 0.02; tau = C.tau_for_xstep(n, xstep, 10.0); tau2 = C.tau_for_xstep(n, xstep, 10.0, beta=2)
    planted_truth = {}
    if True:
        T = len(times); L_ = C.kl_factor(times, tau if fam != "b2" else tau2)
        for layer in range(2):
            store = {}
            for M, (m, nn) in shapes.items():
                sseed = int(rng.integers(2 ** 31))
                if fam in ("c1", "b2"):
                    r = L_.shape[1]; g = np.random.default_rng(sseed)
                    if fam == "c1": G = g.standard_normal((r, m * nn))
                    else: G = (g.standard_normal((r, m * nn)) + 1j * g.standard_normal((r, m * nn))) / np.sqrt(2)
                    sig, U, V = [], [], []
                    for t in range(T):
                        W = (L_[t] @ G).reshape(m, nn) * scale
                        u, s, vh = svd(W, full_matrices=False)
                        if fam == "b2":
                            u = np.linalg.qr(u[:, :32].real)[0]; v = np.linalg.qr(vh[:32].conj().T.real)[0]
                        else:
                            u = u[:, :32]; v = vh[:32].T
                        sig.append(s); U.append(u.astype(np.float32)); V.append(v.astype(np.float32))
                    sig = np.array(sig)
                else:
                    lev = C.poisson_walk(nn, times, tau, xstep * tau / 10.0, seed=sseed)        # unit mean density, in spacings
                    lev = np.sort(lev, axis=1)[:, ::-1]
                    sig = (lev - lev.min() + 5.0) * scale * 0.05 + scale                              # positive, descending
                    g = np.random.default_rng(sseed)
                    u0 = np.linalg.qr(g.standard_normal((m, 32)))[0].astype(np.float32); v0 = np.linalg.qr(g.standard_normal((nn, 32)))[0].astype(np.float32)
                    U = [u0] * T; V = [v0] * T
                if M == "O" and layer == 0 and T >= 5:
                    ps, pU, pV, truth = C.planted_crossing(times, K=16, d_out=m, d_in=nn, t0=1500.0, slope=1e-3, coupling=0.05, s0=float(sig.max()) + 10.0, seed=sseed)
                    for t in range(T):
                        sig[t, :16] = ps[t]; U[t] = U[t].copy(); V[t] = V[t].copy()
                        U[t][:, :16] = pU[t].astype(np.float32); V[t][:, :16] = pV[t].astype(np.float32)
                    planted_truth = dict(truth_t_min=truth["t_min"], truth_g_min=truth["g_min"])
                store[M] = (sig, U, V, float(np.sqrt((sig[0] ** 2).sum()) / math.sqrt(m * nn)))
            for t, s in enumerate(times):
                d = root / arm / f"step{int(s):05d}"; d.mkdir(parents=True, exist_ok=True)
                out = {}
                for M in TYPES:
                    sig, U, V, _ = store[M]
                    out[f"sig_{M}"] = sig[t]; out[f"U32_{M}"] = U[t]; out[f"V32_{M}"] = V[t]
                    out[f"rms_{M}"] = np.array(float(np.sqrt((sig[t] ** 2).sum()) / math.sqrt(np.prod(shapes[M]))))
                np.savez(d / f"L{layer:02d}.npz", **out)
                if layer == 1: (d / "DONE").write_text(json.dumps({"est": "fake-" + EST}))
        # trainlog
        st = root / "_staging" / arm; st.mkdir(parents=True, exist_ok=True)
        with open(st / "trainlog.jsonl", "w") as f:
            for s in range(1, int(times[-1]) + 1):
                lr = 1e-3 * s / 500 if s < 500 else 1e-4 + 0.5 * (1e-3 - 1e-4) * (1 + math.cos(math.pi * (s - 500) / 2500))
                loss = 3 + 8 * math.exp(-s / 300) + 0.5 / (1 + math.exp((s - 1500) / 50)) + 0.02 * rng.standard_normal()
                f.write(json.dumps({"step": s, "loss": loss, "lr": lr}) + "\n")
        log(f"fake bank: {arm} ({fam}) {T} checkpoints x 2 layers written (n={n})")
    return dict(family=fam, T=T, steps=[int(x) for x in times], tau=tau, tau2=tau2, planted_truth=planted_truth)


# ====================================================================== main
def _worker(args):
    try:
        return analyse_unit(*args)
    except Exception as e:
        return dict(error=f"{type(e).__name__}: {e}", trace=traceback.format_exc(), arm=args[1], layer=args[3], type=args[4])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bank", default=str(LLMSPEC / "cache" / "armb"))
    ap.add_argument("--arms", nargs="+", default=["A0", "A1", "A2", "M0s1", "M0s2", "A0r"])
    ap.add_argument("--out", default=str(LLMSPEC / "results" / "armb_pdyn_phase1"))
    ap.add_argument("--layers", type=int, nargs="*", default=None, help="default: all layers present (6 on the real bank)")
    ap.add_argument("--types", nargs="*", default=list(TYPES))
    ap.add_argument("--windows", nargs="+", default=["W1", "W2", "W3"], choices=list(WINDOWS))
    ap.add_argument("--workers", type=int, default=1); ap.add_argument("--blas-threads", default=None)
    ap.add_argument("--nseed", type=int, default=2, help="calibrator seeds per family (C1, beta=2, Poisson)")
    ap.add_argument("--staging", default=str(HERE / "staging"), help="dir with <arm>/trainlog.jsonl")
    ap.add_argument("--mp-witness", default=str(DEFAULT_WITNESS), help="Stage-3 witness json (ks95 / tau_plus per type); 'none' to leave the WITHDRAWN flag unset")
    ap.add_argument("--fake", action="store_true", help="build a fake bank under <out>/fake_bank from the sealed calibrators and run on it")
    ap.add_argument("--fake-n", type=int, default=256)
    ap.add_argument("--flip-threshold", action="store_true", help="RED PATH ONLY: invert the P2 curvature acceptance region")
    ap.add_argument("--verdict-only", action="store_true", help="skip analysis; re-assemble verdicts / tables / figures from existing parts")
    ap.add_argument("--no-figs", action="store_true")
    A = ap.parse_args(argv)
    T0 = time.time()
    out = Path(A.out); out.mkdir(parents=True, exist_ok=True)
    bank = Path(A.bank); staging = Path(A.staging); arms = list(A.arms)
    if A.fake:
        bank = out / "fake_bank"; staging = bank / "_staging"; arms = list(FAKE_ARMS) if A.arms == ap.get_default("arms") else arms
        log(f"fake bank under {bank} (n={A.fake_n}); building missing arms of {arms}")
        build_fake_bank(bank, arms=arms, n=A.fake_n, workers=A.workers)
    if str(bank.resolve()).endswith("cache/armb") and A.fake:
        raise SystemExit("refusing: --fake must not point at the real bank")
    mp_ref = None
    if A.mp_witness and A.mp_witness.lower() != "none" and Path(A.mp_witness).exists():
        wj = json.load(open(A.mp_witness)); mp_ref = {M: wj["types"][M] for M in TYPES if M in wj.get("types", {})}
        log(f"MP witness thresholds from {A.mp_witness}: " + ", ".join(f"{M} ks95={mp_ref[M]['ks95']:.4f} tau+={mp_ref[M]['tau_plus']:.4f} shape={mp_ref[M].get('shape')}" for M in mp_ref))
    else:
        log("no MP witness: WITHDRAWN flag left unset (KS reported)")
    types = [M for M in TYPES if M in A.types]
    summary = dict(est=EST, m2_est=M2.EST, m3_est=M3.EST, params=dict(m2=M2_KW, m3=M3_KW, discrimination_n=DISCRIM_N, tolerances=TOL, nseed=A.nseed, windows={w: list(WINDOWS[w]) for w in A.windows},
                   p5_min_events=P5_MIN_EVENTS, p6_min_events_class=P6_MIN_EVENTS_CLASS, mp_witness=(A.mp_witness if mp_ref else None)),
                   bank=str(bank), fake=bool(A.fake), flip_threshold=bool(A.flip_threshold), arms={}, primary_endpoints={}, runtime_s=None, skipped_parts=0, computed_parts=0, errors=[])
    arms_data = {}
    jobs = []; arm_steps = {}; arm_layers = {}
    for arm in arms:
        n_layers_probe = 0
        d0 = sorted((bank / arm).glob("step*"))
        if not d0: log(f"{arm}: no step directories under {bank / arm}; skipped"); summary["arms"][arm] = dict(status="ABSENT"); continue
        while (d0[0] / f"L{n_layers_probe:02d}.npz").exists(): n_layers_probe += 1
        layers = A.layers if A.layers is not None else list(range(n_layers_probe))
        steps = bank_steps(bank, arm, max(layers) + 1 if layers else 1)
        grid = declared_grid(arm)
        info = dict(status="OK", n_checkpoints=len(steps), first=steps[0] if steps else None, last=steps[-1] if steps else None, layers=layers,
                    grid_declared=(len(grid) if grid else None), grid_missing_from_bank=([s for s in grid if s not in set(steps)] if grid else None),
                    bank_steps_not_in_grid=([s for s in steps if s not in set(grid)] if grid else None),
                    checkpoints_per_window={w: int(sum(1 for s in steps if WINDOWS[w][0] <= s < WINDOWS[w][1])) for w in A.windows},
                    trainlog=str(staging / arm / "trainlog.jsonl"), trainlog_present=(staging / arm / "trainlog.jsonl").exists())
        summary["arms"][arm] = info; arm_steps[arm] = steps; arm_layers[arm] = layers
        log(f"{arm}: {len(steps)} checkpoints ({steps[0]}..{steps[-1]}), layers {layers}, per window {info['checkpoints_per_window']}, grid missing {len(info['grid_missing_from_bank'] or [])}, trainlog {info['trainlog_present']}")
        sig_src = dict(est=[EST, M2.EST, M3.EST], m2=M2_KW, m3=M3_KW, steps=steps, nseed=A.nseed, windows=A.windows)
        signature = hashlib.sha256(json.dumps(sig_src, sort_keys=True, default=str).encode()).hexdigest()[:16]
        for L in layers:
            for M in types:
                pj = out / arm / "parts" / f"L{L:02d}_{M}.json"
                if pj.exists() and pj.with_suffix(".npz").exists():
                    try:
                        if json.load(open(pj)).get("signature") == signature:
                            summary["skipped_parts"] += 1; continue
                    except Exception:
                        pass
                if A.verdict_only: continue
                jobs.append((str(bank), arm, steps, L, M, A.windows, A.nseed, (mp_ref or {}).get(M), pj, pj.with_suffix(".npz"), signature))
    log(f"{len(jobs)} units to compute, {summary['skipped_parts']} resumed from parts; workers={A.workers}")
    t_units = time.time(); done = 0
    if jobs:
        if A.workers > 1:
            with ProcessPoolExecutor(max_workers=A.workers) as ex:
                for fut in as_completed([ex.submit(_worker, j) for j in jobs]):
                    r = fut.result(); done += 1
                    if "error" in r: summary["errors"].append(r); log(f"ERROR {r['arm']} L{r['layer']} {r['type']}: {r['error']}")
                    elif done % 6 == 0 or done == len(jobs): log(f"  {done}/{len(jobs)} units ({time.time() - t_units:.0f}s) last: {r['arm']} L{r['layer']} {r['type']} {r['runtime_s']:.1f}s")
        else:
            for j in jobs:
                r = _worker(j); done += 1
                if "error" in r: summary["errors"].append(r); log(f"ERROR {r['arm']} L{r['layer']} {r['type']}: {r['error']}")
                else: log(f"  {done}/{len(jobs)} {r['arm']} L{r['layer']} {r['type']} {r['runtime_s']:.1f}s")
    summary["computed_parts"] = done; summary["unit_runtime_s"] = time.time() - t_units
    # ---- assembly
    for arm in arm_steps:
        tl = read_trainlog(staging / arm / "trainlog.jsonl")
        D = assemble_arm(out, arm, arm_steps[arm], arm_layers[arm], A.windows, tl, A.flip_threshold)
        arms_data[arm] = D
        S = summary["arms"][arm]
        S["P1"] = verdict("P1"); S["P4"] = verdict("P4")
        S["P2"] = D["m2"]["arm_verdict_p2"]; S["P2_per_type"] = {w: {M: v["word"] for M, v in D["m2"]["per_type_verdict_p2"][w].items()} for w in A.windows}
        S["x_step_median_per_type"] = D["m2"]["x_step"]
        S["P5"] = {w: dict(word=D["m3"]["verdict_p5"][w]["all_events"]["word"], tags=D["m3"]["verdict_p5"][w]["all_events"]["tags"], n_events=D["m3"]["verdict_p5"][w]["all_events"]["n_events"],
                           unambiguous_only_word=D["m3"]["verdict_p5"][w]["unambiguous_only"]["word"], stable_when_ambiguous_excluded=D["m3"]["verdict_p5"][w]["stable_when_ambiguous_excluded"],
                           detail=D["m3"]["verdict_p5"][w]["all_events"]) for w in A.windows}
        S["P6"] = {w: D["m3"]["verdict_p6"][w]["all_events"] for w in A.windows}
        S["controls"] = dict(C5_all_bit_identical=D["controls"]["C5_all_bit_identical"], C3_collapsed_frac=D["controls"]["C3_collapsed_frac"],
                             C4_spectrum_ratio_median=D["controls"]["C4_spectrum_ratio_median"], C4_matrix_fp32_ratio_median=D["controls"]["C4_matrix_fp32_ratio_median"], C8=D["controls"]["C8"])
        S["M6"] = D["m6"]["status"] if D["m6"].get("status") else "OK"
        S["W3"] = "DESCRIPTIVE" if "W3" in A.windows else None
        if not A.no_figs:
            try: figures_arm(out, arm, D, A.windows)
            except Exception as e: summary["errors"].append(dict(arm=arm, error=f"figures: {type(e).__name__}: {e}")); log(f"figures failed for {arm}: {e}")
        log(f"{arm}: P2 " + ", ".join(f"{w}={S['P2'][w]['word']}" for w in A.windows) + " | P5 " + ", ".join(f"{w}={S['P5'][w]['word']}" for w in A.windows)
            + f" | C5 {S['controls']['C5_all_bit_identical']} C3 {S['controls']['C3_collapsed_frac']} | events {S['controls']['C8']}")
    # ---- P3 pairs
    def m5map(arm):
        if arm not in arms_data: return None
        return {(L, M): dict(steps=A_["steps"], eff_rank=A_["m5/eff_rank"], top16_mass=A_["m5/top16_mass"], n_upper_outliers=A_["m5/n_upper_outliers"], mp_withdrawn=A_["m5/mp_withdrawn"])
                for (L, M), (P, A_) in arms_data[arm]["parts"].items()}
    pairs = dict(P3_PAIRS)
    if A.fake: pairs = dict(primary=("FAKE_C1", "FAKE_B2"), floor=None, descriptive=[("FAKE_C1", "FAKE_PO")])
    p3 = {}
    fl = None
    if pairs.get("floor") and all(m5map(x) for x in pairs["floor"]): fl = (m5map(pairs["floor"][0]), m5map(pairs["floor"][1]))
    a, b = pairs["primary"]
    if m5map(a) and m5map(b):
        p3["primary"] = dict(pair=[a, b], **verdict("P3", m5map(a), m5map(b), fl))
    else:
        p3["primary"] = dict(pair=[a, b], word="NOT RESOLVABLE", reason="arm(s) absent")
    p3["descriptive"] = []
    for a, b in pairs.get("descriptive", []):
        if m5map(a) and m5map(b):
            v = verdict("P3", m5map(a), m5map(b), fl); v["word"] = f"DESCRIPTIVE ({v['word']})"; v["pair"] = [a, b]; p3["descriptive"].append(v)
    words = [p3["primary"].get("word")] + [v["word"] for v in p3["descriptive"]]
    p3["across_seeds"] = ("all pairs Muon <= AdamW" if words and all("FAILS" in str(w) for w in words) else ("all pairs HOLD" if words and all("HOLDS" in str(w) for w in words) else "mixed / unresolved"))
    summary["P3"] = p3
    summary["primary_endpoints"] = dict(
        P2_W2={arm: (summary["arms"][arm]["P2"]["W2"]["word"] if "W2" in summary["arms"].get(arm, {}).get("P2", {}) else "ABSENT") for arm in (("FAKE_C1", "FAKE_B2", "FAKE_PO", "FAKE_SHORT") if A.fake else ("A0", "M0s1"))},
        P3_primary=p3["primary"].get("word"), P3_descriptive=[(v["pair"], v["word"]) for v in p3["descriptive"]],
        note="P2 primary = velocity Gaussianity + C(x) on W2 for A0 (AdamW) and M0s1 (Muon); curvature PROVISIONAL; P5/P6 PROVISIONAL; W3 / M5 DESCRIPTIVE")
    # ---- tables + summary figures
    try:
        long_tables(out, arms_data, A.windows)
    except Exception as e:
        summary["errors"].append(dict(error=f"long tables: {type(e).__name__}: {e}")); log(f"long tables failed: {e}")
    if not A.no_figs and arms_data:
        try: figures_summary(out, arms_data, A.windows)
        except Exception as e: summary["errors"].append(dict(error=f"summary figures: {type(e).__name__}: {e}")); log(f"summary figures failed: {e}")
    summary["runtime_s"] = time.time() - T0
    json.dump(summary, open(out / "summary.json", "w"), indent=1, default=_jsonable)
    log(f"summary -> {out / 'summary.json'}; runtime {summary['runtime_s']:.0f}s ({summary['computed_parts']} computed, {summary['skipped_parts']} resumed; {len(summary['errors'])} errors)")
    print("PRIMARY ENDPOINTS: " + json.dumps(summary["primary_endpoints"], default=_jsonable))
    return summary


if __name__ == "__main__":
    main()

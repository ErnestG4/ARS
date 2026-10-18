"""The two route (a) replications' read: estimators, error bars, goodness of fit and decision rule, as code (round 52
draft; FOLLOWUP_REPLICATION_RULES.md §5–6). Mirrors route_a_read.py. Nothing here reads an F4/F5 file; the sealed read
(a separate file, built after the seals) is the only path that will.

Data → per-file sequences (the same code for zeros and for the CUE calibration replicates):
  (A) the bin index ⌊s⁽²⁾/1e-4⌋ (capped at 30,000) of each next-nearest-neighbour spacing s⁽²⁾_k = s_k + s_{k+1}, in order.
      Zeros: consecutive unfolded spacings of the file (Phase 2's decode and exact-θ unfolding). CUE: followup_calsamp.
  (B) the counts in the disjoint windows [jL, (j + 1)L), L = 3, of the unfolded positions x_k = N̄(γ_k) − N̄(t0)
      (exact θ, differences in extended precision), j < ⌊x_last/L⌋, in order. CUE: followup_calsamp (per matrix).
Model and estimator, per file f:
  (A) p_μ = p⁽²⁾_sine + μ·Δp⁽²⁾_f on the bins of [S_RES, S_A) (followup_fit §1: resolved bins, S_A = 1.6), Δp⁽²⁾_f the
      barycentric interpolant through the tagged prediction's 25 Chebyshev–Lobatto values (followup_pred_A.json, as its
      merge); μ̂ by followup_fit.fit_A (binned conditional ML; a fit at its bound, non-finite or with density ≤ 0 is a
      FAILURE, never a value).
  (B) μ̂ = (k₃ − κ₃^sine)/Δκ₃,f, k₃ = W²m₃/((W − 1)(W − 2)) of the W counts, κ₃^sine and Δκ₃,f from followup_pred_B.json.
Error bars: moving-block bootstrap, B_BOOT replicates, at each block length (A: BLOCK_LENS_A spacings, solved by
Phase 2's series form, ph2lib.block_bootstrap_c_series, whose score is exactly the binned one; B: BLOCK_LENS_B windows,
the same unfolded lengths, exact from block sums of N, N², N³).
Goodness of fit, (A) only: binned χ² against p_μ̂ conditional on the window, GOF_BINS_A groups of the 1e-4 bins with
equal sine-kernel probability (the window starts where p⁽²⁾ ~ s⁷ is tiny, so equal widths would leave near-empty bins;
accepted in round 53 as a pre-data deviation from route (a)). Count floor (round 53): each group's pre-data expected
count per file, E_g = n_f·Σ_{k∈g} p_{μ=1}(k)·1e-4 (n_f the file's pre-data count, p_{μ=1} the tagged prediction), must
be ≥ GOF_MIN_E = 5; while any group falls short, the group with the smallest E_g is merged with whichever adjacent group
has the smaller E_g (a tie goes to the lower-s neighbour), and E is recomputed. The groups are fixed per file before
any data; the thresholds T_f come from the calibration only.

Calibration (declared before the seal; FOLLOWUP_REPLICATION_RULES.md §5 step 2): per file, R = 200 CUE_1000 replicates
at the file's pre-data size through the identical estimator: bias b_f (replicate mean of μ̂), SD_f, BLOCK (the shortest
block length whose bootstrap-SE/SD ratio, geometric mean over the files, is ≥ 0.95; none → the longest), and for (A)
the GoF threshold T_f (the (1 − α₁) quantile of a scaled χ², α₁ = 1 − 0.99^{1/n_files}).

Rule, per observable (route (a)'s, with the measured ∂μ*/∂μ = g_f in place of 1, rules §2):
  μ̃_f = (μ̂_f − b_f)/g_f;  SE_f = max(SD_f, SE_boot,f(L) for L ≥ BLOCK), widened by SD_f/√R, then divided by g_f;
  μ̃_pool = Σ w_f μ̃_f,  SE_pool = (Σ w_f² SE_f²)^½,  w_f ∝ n_f (pre-data, exact θ);
  precedence:
  FIT FAILURE   iff any file's fit failed (a failure is never a value; reported with its reason);
  MODEL MISFIT  (A only) iff χ²_f > T_f in at least 2 files;
  UNRESOLVED    iff 2·SE_pool > 0.25;
  PASS          iff |μ̃_pool − 1| ≤ 2·SE_pool + δμ_sys, all files but one have |μ̃_f − 1| ≤ 3·SE_f, and (A) all files
                but one pass the GoF;
  FAIL          otherwise.
g_f: (A) the prediction's estimator-limit slope per file (followup_pred_A.json); (B) the exact linear limit (1) times
the CUE_N known-answer slope at L = 3 by round 53's rule (G_B_53: the run to SE(slope) ≤ 0.005; the slope is divided out
only if |slope − 1| > 2·SE, else 1; its SE is added to (B)'s δμ_sys either way).

  python followup_read.py selftest                          known answers and red paths (small; spot)
  python followup_read.py calib_fit SAMP_DIR OUT_DIR CHUNK NCHUNKS   fits on followup_calsamp's sequences (spot)
  python followup_read.py declare OUT_DIR [A|B|AB]          → results/calib/followup_calib_{A,B}_declared.json
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
import followup_fit as FF  # noqa: E402
import followup_nnn as N  # noqa: E402
import followup_pred as P  # noqa: E402
import ph2lib  # noqa: E402
import route_a_read as RR  # noqa: E402

PRED = {"A": os.path.join(HERE, "results", "followup_pred_A.json"),
        "B": os.path.join(HERE, "results", "followup_pred_B.json")}
FILES = {"A": P.F4, "B": P.F5}
SET = {"A": 4, "B": 5}
L_B = P.L_B
BLOCK_LENS = {"A": (300, 1000, 3000, 10000), "B": (100, 333, 1000, 3333)}   # B: windows of 3 = the same unfolded lengths
B_BOOT = 200
BLOCK_SE_RATIO = 0.95
GOF_BINS_A = 30
GOF_MIN_E = 5.0                                                              # round 53
GOF_FAMILYWISE = 0.01
RESOLVE_2SE = 0.25
K_POOL, K_FILE = 2.0, 3.0
MISFIT_FILES = 2
R_CAL = 200
CALIB = {o: os.path.join(HERE, "results", "calib", f"followup_calib_{o}_declared.json") for o in "AB"}
CUEN = (os.path.join(HERE, "results", "followup_cuen.json"), os.path.join(HERE, "results", "followup_cuen_r51.json"))
CUEN_53 = os.path.join(HERE, "results", "followup_cuen_r53.json")
SHIFTS = (0.90, 0.94, 0.96, 0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.06, 1.10)


def G_B_53():
    """Round 53's slope rule: g and the δμ_sys addition from the run to SE(slope) ≤ 0.005 (followup_cuen.py, ROUND 53).
    Fails closed if the run has not reached the target."""
    r = json.load(open(CUEN_53))
    d = r["round53"]
    if not d["se_reached"]:
        raise RuntimeError(f"G_B_53: SE(slope) target not reached ({d['next']})")
    return dict(g=d["g"], dmu_sys_add=d["dmu_sys_add"], decision=d["decision"], slope=r["L"]["3.0"]["slope"],
                slope_se=r["L"]["3.0"]["slope_se"], chi2=r["L"]["3.0"]["chi2"], p=r["L"]["3.0"]["p"],
                batches=r["N_BATCH"], extend=r["extend"])


def G_B(L="3.0"):
    """The CUE_N known-answer slope at L: each run, and their inverse-variance pool (value, se)."""
    runs = [json.load(open(p))["L"][L] for p in CUEN]
    w = [1 / r["slope_se"] ** 2 for r in runs]
    pool = sum(wi * r["slope"] for wi, r in zip(w, runs)) / sum(w)
    return dict(runs=[dict(slope=r["slope"], se=r["slope_se"], chi2=r["chi2"], p=r.get("p")) for r in runs],   # r50 has no p
                pool=pool, pool_se=sum(w) ** -0.5)


# ------------------------------------------------------------------ sequences from data
def seq_A(spacings):
    s2 = spacings[:-1] + spacings[1:]
    return np.minimum((s2 / FF.HB).astype(np.int64), FF.NBIN).astype(np.uint16)


def seq_B(x):
    """Window counts from unfolded positions x (relative to N̄(t0), increasing, ≥ 0)."""
    W = int(math.floor(x[-1] / L_B))
    j = np.floor(np.asarray(x) / L_B).astype(np.int64)
    c = np.bincount(j[j < W], minlength=W)
    assert c.max() < 256
    return c.astype(np.uint8)


def unfold(gammas_mp, t0, dps=40):
    """Unfolded spacings and positions x_k = N̄(γ_k) − N̄(t0) (exact θ; differences taken at dps, then float64)."""
    import mpmath as mp
    with mp.workdps(dps):
        base = mp.siegeltheta(mp.mpf(t0)) / mp.pi + 1
        xs = ph2lib.nbar_exact(gammas_mp)
        s = np.array([float(xs[i + 1] - xs[i]) for i in range(len(xs) - 1)])
        x = np.array([float(v - base) for v in xs])
    return s, x


# ------------------------------------------------------------------ (A)
class ModelA:
    """The binned model on the window for one file's tagged Δp⁽²⁾ nodes; the series-bootstrap fitter interface."""

    def __init__(self, dp_nodes, n_f=None):
        p2, _ = N.p2_sine()
        c = FF.CENTRES
        sr = max(FF.s_res(p2(c)), RR.S_TINY)
        k = np.nonzero((c >= sr) & (c < P.S_A - 1e-12))[0]
        assert np.all(np.diff(k) == 1)
        self.k0, self.K, self.S_RES = int(k[0]), len(k), sr
        self.c = c[k]
        self.p0 = p2(self.c)
        self.dp = P.bary(np.asarray(dp_nodes, float), P.NODES_A, self.c)
        self.wbin = np.full(self.K, FF.HB)
        self.rho_bin = self.dp / self.p0
        self.phi = float(np.sum(self.dp) / np.sum(self.p0))
        cum = np.concatenate([[0.0], np.cumsum(self.p0)[:-1]]) / np.sum(self.p0)
        self.group = np.minimum((cum * GOF_BINS_A).astype(np.int64), GOF_BINS_A - 1)
        self.merges, self.E_pre = [], None
        if n_f is not None:
            self._count_floor(float(n_f))
        self.n_groups = int(self.group.max()) + 1

    def _count_floor(self, n_f):
        """Round 53: merge adjacent groups until every pre-data expected count n_f·P_{μ=1}(group) is ≥ GOF_MIN_E."""
        q = (self.p0 + self.dp) * FF.HB
        g = self.group.copy()
        while True:
            E = n_f * np.bincount(g, weights=q)
            j = int(np.argmin(E))
            if E[j] >= GOF_MIN_E:
                break
            nb = [k for k in (j - 1, j + 1) if 0 <= k < len(E)]
            k = min(nb, key=lambda k: (E[k], k))
            lo, hi = min(j, k), max(j, k)
            g[g == hi] = lo
            g[g > hi] -= 1
            self.merges.append([lo, hi, float(E[j])])
        self.group, self.E_pre = g, E.tolist()

    def hist(self, pos, weights=None):
        ok = (pos >= 0) & (pos < self.K)
        return np.bincount(pos[ok], weights=None if weights is None else weights[ok], minlength=self.K).astype(float)

    def prepare(self, seq):
        pos = seq.astype(np.int64) - self.k0
        inw = (pos >= 0) & (pos < self.K)
        rho = np.zeros(len(pos))
        rho[inw] = self.rho_bin[pos[inw]]
        return dict(inw=inw, rho=rho, phi=self.phi, pos=pos)

    def fit(self, prep, weights=None):
        mu, why = FF.fit_A(self.hist(prep["pos"], weights), self.p0, self.dp, self.wbin)
        return (np.nan, why) if why else (mu, "interior")

    def gof(self, h, mu):
        q = self.p0 + mu * self.dp
        ng = int(self.group.max()) + 1
        O = np.bincount(self.group, weights=h, minlength=ng)
        E = h.sum() * np.bincount(self.group, weights=q, minlength=ng) / q.sum()
        return float(np.sum((O - E) ** 2 / E))


def fit_file_A(model, seq, rng, block_lens=BLOCK_LENS["A"], n_boot=B_BOOT):
    prep = model.prepare(seq)
    h = model.hist(prep["pos"])
    mu, why = FF.fit_A(h, model.p0, model.dp, model.wbin)
    out = dict(n=int(len(seq)), n_window=int(h.sum()))
    if why:
        return dict(out, mu=None, fail=why)
    se, refit, bfail = {}, {}, {}
    for L in block_lens:
        reps, nref = ph2lib.block_bootstrap_c_series(model, prep, mu, int(L), n_boot, rng)
        bad = int(np.sum(~np.isfinite(reps)))
        se[str(L)] = float(np.std(reps[np.isfinite(reps)], ddof=1)) if bad == 0 else None
        refit[str(L)], bfail[str(L)] = int(nref), bad
    return dict(out, mu=float(mu), fail=None, se=se, boot_refit=refit, boot_fail=bfail, chi2=model.gof(h, mu))


# ------------------------------------------------------------------ (B)
def k3(c):
    c = np.asarray(c, float)
    W = len(c)
    m = c.mean()
    return float(W * W * np.mean((c - m) ** 3) / ((W - 1) * (W - 2)))


def boot_k3(c, L, n_boot, rng):
    """Moving-block bootstrap of k₃ (starts uniform on [0, W − L], ⌈W/L⌉ blocks, the last cut to length W), exact from
    block sums of d, d², d³ (d = c − round(mean), integers, so the sums are exact in float64)."""
    d = np.asarray(c, np.int64) - int(round(float(np.mean(c))))
    W = len(d)
    C = [np.concatenate([[0], np.cumsum(d ** p)]).astype(float) for p in (1, 2, 3)]
    nb = int(math.ceil(W / L))
    last = W - (nb - 1) * L
    starts = rng.integers(0, W - L + 1, (n_boot, nb))
    lens = np.full(nb, L)
    lens[-1] = last
    S1, S2, S3 = ((Cp[starts + lens] - Cp[starts]).sum(axis=1) for Cp in C)
    m1, m2, m3 = S1 / W, S2 / W, S3 / W
    cm3 = m3 - 3 * m1 * m2 + 2 * m1 ** 3
    return W * W * cm3 / ((W - 1) * (W - 2))


def fit_file_B(t, seq, rng, block_lens=BLOCK_LENS["B"], n_boot=B_BOOT):
    """t: the tagged prediction's row for the file (kappa3_sine, dkappa3)."""
    ks = k3(seq)
    mu = (ks - t["kappa3_sine"]) / t["dkappa3"]
    se = {str(L): float(np.std((boot_k3(seq, int(L), n_boot, rng) - t["kappa3_sine"]) / t["dkappa3"], ddof=1))
          for L in block_lens}
    return dict(n=int(len(seq)), W=int(len(seq)), k3=ks, mu=float(mu), fail=None, se=se)


# ------------------------------------------------------------------ the rule
def weights(obs):
    return P.counts(FILES[obs])


def g_files(obs, pred, gb=None):
    if obs == "A":
        return {f: pred["files"][f]["dmustar_dmu"] for f in FILES["A"]}
    gb = G_B_53()["g"] if gb is None else gb                  # round 53's rule
    return {f: 1.0 * gb for f in FILES["B"]}                 # the exact linear limit is 1 (rules §2)


def dmu_sys(obs, pred):
    """The declared δμ_sys: the prediction's own; for (B) plus round 53's slope SE."""
    return pred["delta_mu_sys"] + (G_B_53()["dmu_sys_add"] if obs == "B" else 0.0)


def file_se(r, c, block):
    boot = [v for k, v in r["se"].items() if int(k) >= block]
    if not boot or any(v is None for v in boot):
        raise RuntimeError("followup_read.file_se: no complete bootstrap SE at L ≥ BLOCK")
    s = max([c["sd"]] + boot)
    return math.sqrt(s ** 2 + c["sd"] ** 2 / c["R"])


def rule(obs, per_file, w, cal, dmu_sys, g):
    files = list(w)
    fails = {f: per_file[f]["fail"] for f in files if per_file[f].get("fail")}
    if fails:
        return dict(verdict="FIT FAILURE", failures=fails)
    block = int(cal["block"])
    C = cal["files"]
    G = np.array([g[f] for f in files])
    mu = (np.array([per_file[f]["mu"] - C[f]["bias"] for f in files])) / G
    se = np.array([file_se(per_file[f], C[f], block) for f in files]) / G
    W = np.array([w[f] for f in files])
    mp_, sp = float(np.sum(W * mu)), float(math.sqrt(np.sum(W ** 2 * se ** 2)))
    resolvable = 2 * sp <= RESOLVE_2SE
    within = int(np.sum(np.abs(mu - 1) <= K_FILE * se))
    pool_ok = abs(mp_ - 1) <= K_POOL * sp + dmu_sys
    misfit = [f for f in files if obs == "A" and per_file[f]["chi2"] > C[f]["T"]]
    need = len(files) - 1
    if obs == "A" and len(misfit) >= MISFIT_FILES:
        verdict = "MODEL MISFIT"
    elif not resolvable:
        verdict = "UNRESOLVED"
    elif pool_ok and within >= need and len(files) - len(misfit) >= need:
        verdict = "PASS"
    else:
        verdict = "FAIL"
    return dict(verdict=verdict, mu_pool=mp_, se_pool=sp, band=K_POOL * sp + dmu_sys, ci95=[mp_ - 2 * sp, mp_ + 2 * sp],
                resolvable=resolvable, pool_within=pool_ok, files_within_3se=within, files_needed=need,
                misfit_files=misfit, mu_file=dict(zip(files, mu.tolist())), se_file=dict(zip(files, se.tolist())))


# ------------------------------------------------------------------ calibration
def calib_fit(samp_dir, out_dir, chunk, nchunks):
    """Fit every calibration sequence (followup_calsamp) with the tagged predictions; append + fsync per row."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"fit_c{chunk:02d}.jsonl")
    done = set()
    if os.path.exists(path):
        done = {(r["rep"], r["file"]) for r in map(json.loads, open(path))}
    pred = {o: json.load(open(PRED[o])) for o in "AB"}
    models = {f: ModelA(pred["A"]["files"][f]["dp_nodes"], pred["A"]["n_f"][f]) for f in FILES["A"]}
    rows = sorted((r for fn in sorted(os.listdir(samp_dir)) if fn.startswith("samp_")
                   for r in map(json.loads, open(os.path.join(samp_dir, fn)))), key=lambda r: (r["rep"], r["set"], r["i"]))
    for j, r in enumerate(rows):
        if j % nchunks != chunk or (r["rep"], r["file"]) in done:
            continue
        seq = np.load(os.path.join(samp_dir, r["seq"]))
        assert len(seq) == r["len"]
        rng = np.random.default_rng([20261017, 52, 1, SET[r["obs"]], r["i"], r["rep"]])
        if r["obs"] == "A":
            res = fit_file_A(models[r["file"]], seq, rng)
        else:
            res = fit_file_B(pred["B"]["files"][r["file"]], seq, rng)
        res.update(rep=r["rep"], file=r["file"], obs=r["obs"])
        with open(path, "a") as fh:
            fh.write(json.dumps(res) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        print(f"rep {r['rep']} {r['obs']} {r['file']}: μ̂ {res['mu']}" + (f" FAIL {res['fail']}" if res["fail"] else ""),
              flush=True)


def scaled_chi2_quantile(x, q):
    from scipy.stats import chi2
    m, v = float(np.mean(x)), float(np.var(x, ddof=1))
    a, nu = v / (2 * m), 2 * m * m / v
    return float(a * chi2.ppf(q, nu)), a, nu


def declare_one(obs, rows, pred, dmu_sys_options):
    files = list(FILES[obs])
    reps = sorted({rep for rep, _ in rows})
    joint = [r for r in reps if all((r, f) in rows for f in files)]
    fails = [dict(rep=r, file=f, why=rows[(r, f)]["fail"]) for r in joint for f in files if rows[(r, f)]["fail"]]
    bfail = sum(v for r in joint for f in files if obs == "A" and rows[(r, f)]["fail"] is None
                for v in rows[(r, f)]["boot_fail"].values())
    if bfail:
        raise RuntimeError(f"declare ({obs}): {bfail} bootstrap replicate fits failed — a calibration defect, to Will")
    good = [r for r in joint if all(not rows[(r, f)]["fail"] for f in files)]
    sd = {f: float(np.std([rows[(r, f)]["mu"] for r in good], ddof=1)) for f in files}
    BL = BLOCK_LENS[obs]
    se_mean = {f: {L: float(np.mean([rows[(r, f)]["se"][str(L)] for r in good])) for L in BL} for f in files}
    ratio = {L: float(np.exp(np.mean([np.log(se_mean[f][L] / sd[f]) for f in files]))) for L in BL}
    ok = [L for L in BL if ratio[L] >= BLOCK_SE_RATIO]
    a1 = 1 - (1 - GOF_FAMILYWISE) ** (1 / len(files))
    cal = dict(observable=obs, block=min(ok) if ok else max(BL), block_fallback=not ok, se_over_sd_geomean=ratio,
               R=len(good), R_complete=len(joint), fit_failures=fails, boot_failures=bfail, files={})
    for f in files:
        mu = np.array([rows[(r, f)]["mu"] for r in good])
        c = dict(bias=float(mu.mean()), bias_z=float(mu.mean() / (sd[f] / math.sqrt(len(mu)))), sd=sd[f], R=len(mu),
                 se_boot_mean=se_mean[f])
        if obs == "A":
            chi = np.array([rows[(r, f)]["chi2"] for r in good])
            T, a, nu = scaled_chi2_quantile(chi, 1 - a1)
            c.update(T=T, chi2_scale=a, chi2_dof=nu, chi2_mean=float(chi.mean()),
                     chi2_emp_q99=float(np.percentile(chi, 99)), chi2_fit_q99=scaled_chi2_quantile(chi, 0.99)[0])
        cal["files"][f] = c
    if obs == "A":
        cal.update(alpha_per_file=a1, familywise=GOF_FAMILYWISE)
        nflag = np.array([sum(rows[(r, f)]["chi2"] > cal["files"][f]["T"] for f in files) for r in good])
        cal["empirical_familywise_misfit"] = float(np.mean(nflag >= 1))
        cal["empirical_model_misfit_verdict"] = float(np.mean(nflag >= MISFIT_FILES))
    w, _ = weights(obs)
    oc = {}
    for name, (dmu_sys, gsel) in dmu_sys_options.items():
        g = g_files(obs, pred, gsel)

        def verdicts(mu_true):
            return [rule(obs, {f: dict(rows[(r, f)], mu=rows[(r, f)]["mu"] + mu_true * g[f]) for f in files},
                         w, cal, dmu_sys, g)["verdict"] for r in good]
        curve = {}
        for m in (0.0,) + SHIFTS:
            v = verdicts(m)
            curve[f"{m:.2f}"] = {k: v.count(k) for k in sorted(set(v))}
        n = len(good)
        oc[name] = dict(dmu_sys=dmu_sys, g=g, false_fail=1 - curve["1.00"].get("PASS", 0) / n,
                        power_mu0=curve["0.00"].get("FAIL", 0) / n, verdicts=curve)
    cal["operating_characteristics"] = oc
    return cal


def declare(out_dir, which="AB"):
    rows = {"A": {}, "B": {}}
    for fn in sorted(os.listdir(out_dir)):
        if fn.startswith("fit_c"):
            for r in map(json.loads, open(os.path.join(out_dir, fn))):
                rows[r["obs"]][(r["rep"], r["file"])] = r
    pred = {o: json.load(open(PRED[o])) for o in "AB"}
    out = {}
    for o in which:
        opts = {"declared": (dmu_sys(o, pred[o]), None)}
        cal = declare_one(o, rows[o], pred[o], opts)
        if o == "A":
            cal["gof_groups"] = {f: dict(n_groups=m.n_groups, merges=m.merges, E_pre_min=min(m.E_pre))
                                 for f, m in ((f, ModelA(pred["A"]["files"][f]["dp_nodes"], pred["A"]["n_f"][f]))
                                              for f in FILES["A"])}
            print(f"(A) GoF groups: {cal['gof_groups']}", flush=True)
        else:
            cal["G_B_round53"] = G_B_53()
            cal["G_B_rounds50_51"] = G_B()
        os.makedirs(os.path.dirname(CALIB[o]), exist_ok=True)
        json.dump(cal, open(CALIB[o], "w"), indent=1, sort_keys=True)
        out[o] = cal
        print(f"({o}) R {cal['R']} (complete {cal['R_complete']}), fit failures {len(cal['fit_failures'])}, BLOCK "
              f"{cal['block']} (SE/SD {cal['se_over_sd_geomean']})", flush=True)
        for f, c in cal["files"].items():
            print(f"  {f}: b {c['bias']:+.5f} (z {c['bias_z']:+.2f})  SD {c['sd']:.5f}"
                  + (f"  T {c['T']:.1f}" if o == "A" else ""), flush=True)
        for k, v in cal["operating_characteristics"].items():
            print(f"  [{k}] δμ_sys {v['dmu_sys']:.2e}: false FAIL (μ = 1) {v['false_fail']:.3f}, power (μ = 0) "
                  f"{v['power_mu0']:.3f}; " + ", ".join(f"μ {m}: PASS {c.get('PASS', 0)}" for m, c in v["verdicts"].items()),
                  flush=True)
    return out


# ------------------------------------------------------------------ known answers and red paths
def draw_iid_A(model, mu, n, rng):
    """n i.i.d. bin indices from p_μ on the window, plus a fraction outside it with the sine kernel's probability."""
    p2, _ = N.p2_sine()
    pin = float(np.sum(model.p0) * FF.HB)
    q = (model.p0 + mu * model.dp)
    q = q / q.sum()
    n_in = rng.binomial(n, pin)
    seq = np.concatenate([model.k0 + rng.choice(model.K, n_in, p=q),
                          np.full(n - n_in, FF.NBIN)])                              # outside: a bin past the window
    return rng.permutation(seq).astype(np.uint16)


def selftest():
    rng = np.random.default_rng([20261017, 52, 99])
    ok = True
    # (A) known answers with a stand-in Δp⁽²⁾ (followup_nnn's primary F3 nodes at the lowest file, interpolated to S_A's
    # nodes); i.i.d. draws, so the bootstrap at block 1 must cover
    nnn = json.load(open(os.path.join(HERE, "results", "followup_nnn.json")))
    f3 = next(iter(RR.F3))
    dpn = N.nn_interp(nnn["files"][f3][FF.MODEL]["dp_nodes"], P.NODES_A)
    m = ModelA(dpn)
    for mu in (0.0, 0.5, 1.0):                         # inside the stand-in's positivity range
        seq = draw_iid_A(m, mu, 3_000_000, rng)
        r = fit_file_A(m, seq, rng, block_lens=(1, 300), n_boot=100)
        z = (r["mu"] - mu) / r["se"]["1"]
        g = abs(z) < 4 and r["chi2"] < 3 * GOF_BINS_A and abs(r["se"]["300"] / r["se"]["1"] - 1) < 0.3
        ok &= g
        print(f"(A) green μ = {mu}: μ̂ {r['mu']:+.4f} ± {r['se']['1']:.4f} (block 300: {r['se']['300']:.4f}) z {z:+.2f} "
              f"χ² {r['chi2']:.1f} refits {r['boot_refit']} → {'PASS' if g else 'FAIL'}", flush=True)
    # round 53 count floor: at a real file size nothing merges; at a tiny n_f the rule must merge until E ≥ 5 everywhere
    big, tiny = ModelA(dpn, n_f=5_853_282), ModelA(dpn, n_f=1_000)
    g = (not big.merges and big.n_groups == GOF_BINS_A and min(big.E_pre) >= GOF_MIN_E
         and len(tiny.merges) > 0 and min(tiny.E_pre) >= GOF_MIN_E and tiny.n_groups < GOF_BINS_A
         and np.all(np.diff(tiny.group) >= 0) and np.all(np.diff(tiny.group) <= 1))
    ok &= g
    print(f"(A) count floor: n_f 5.85e6 → {big.n_groups} groups, min E {min(big.E_pre):.0f}, merges {len(big.merges)}; "
          f"red n_f 1000 → {tiny.n_groups} groups, min E {min(tiny.E_pre):.2f}, merges {len(tiny.merges)} "
          f"(contiguous) → {'PASS' if g else 'FAIL'}")
    # series bootstrap = exact multiplicity refits (same starts)
    seq = draw_iid_A(m, 1.0, 400_000, rng)
    prep = m.prepare(seq)
    mu0 = m.fit(prep)[0]
    r1 = np.random.default_rng(5)
    ser, _ = ph2lib.block_bootstrap_c_series(m, prep, mu0, 1000, 20, r1)
    r2 = np.random.default_rng(5)
    n = len(seq)
    nb = int(math.ceil(n / 1000))
    st = r2.integers(0, n - 1000 + 1, (20, nb))
    last = n - (nb - 1) * 1000
    ex = []
    for b in range(20):
        idx = np.concatenate([(st[b][:-1, None] + np.arange(1000)[None, :]).ravel(), st[b][-1] + np.arange(last)])
        ex.append(m.fit(prep, weights=np.bincount(idx, minlength=n).astype(float))[0])
    d = float(np.max(np.abs(ser - np.array(ex))))
    g = d < 1e-6
    ok &= g
    print(f"(A) series bootstrap vs exact refits (20 replicates, block 1000): max |diff| {d:.1e} → {'PASS' if g else 'FAIL'}")
    # red (A): Poisson-like NNN (sum of two exponentials) must be flagged by the GoF
    s = rng.exponential(size=3_000_001)
    r = fit_file_A(m, seq_A(s), rng, block_lens=(1,), n_boot=20)
    red = r["mu"] is None or r["chi2"] > 100 * GOF_BINS_A
    ok &= red
    print(f"(A) red: Poisson spacings → μ̂ {r['mu']} ({r.get('fail')}) χ² {r.get('chi2')} → "
          f"{'PASS (flagged)' if red else 'FAIL (not flagged)'}")
    # (B) k₃ on Poisson counts (κ₃ = λ) and the bootstrap's exactness
    c = rng.poisson(3.0, 2_000_000)
    kk = k3(c)
    bs = boot_k3(c, 1, 200, rng)
    zb = (kk - 3.0) / np.std(bs, ddof=1)
    g = abs(zb) < 4
    ok &= g
    print(f"(B) green: Poisson(3) counts → k₃ {kk:.4f} (κ₃ = 3), z {zb:+.2f} → {'PASS' if g else 'FAIL'}")
    rr = np.random.default_rng(7)
    b1 = boot_k3(c[:10_000], 37, 5, rr)
    rr = np.random.default_rng(7)
    W = 10_000
    nb = int(math.ceil(W / 37))
    st = rr.integers(0, W - 37 + 1, (5, nb))
    last = W - (nb - 1) * 37
    b2 = [k3(np.concatenate([c[:W][(st[b][:-1, None] + np.arange(37)[None, :]).ravel()], c[:W][st[b][-1] + np.arange(last)]]))
          for b in range(5)]
    d = float(np.max(np.abs(b1 - np.array(b2))))
    g = d < 1e-10
    ok &= g
    print(f"(B) block-sum bootstrap vs materialised resamples: max |diff| {d:.1e} → {'PASS' if g else 'FAIL'}")
    # (B) window counts from positions: a uniform grid of spacing 1 gives exactly 3 per window
    x = 0.5 + np.arange(30_000, dtype=float)
    cc = seq_B(x)
    g = bool(np.all(cc == 3)) and len(cc) == int((x[-1]) // 3)
    ok &= g
    print(f"(B) seq_B on a unit grid: {len(cc)} windows, counts {set(cc.tolist())} → {'PASS' if g else 'FAIL'}")
    ok &= rule_selftest()
    print("SELFTEST", "PASS" if ok else "FAIL")
    return ok


def rule_selftest():
    """Every verdict of rule() fires on constructed input, for both observables, and the precedence holds."""
    ok = True
    for obs in "AB":
        files = list(FILES[obs])
        nf = len(files)
        w = {f: 1 / nf for f in files}
        BL = BLOCK_LENS[obs]
        cal = dict(block=BL[1], files={f: dict(bias=0.01, sd=0.02, R=200, T=60.0) for f in files})
        g = {f: 1.0 for f in files}

        def pf(mu, se=0.02, chi2=40.0, mis=0, fail=None, gg=1.0):
            return {f: dict(mu=mu * gg + 0.01, se={str(L): (0.5 * se if L == BL[0] else se) for L in BL},
                            chi2=(99.0 if i < mis else chi2), fail=(fail if i == 0 else None)) for i, f in enumerate(files)}
        cases = [("PASS", pf(1.0), g), ("FAIL", pf(0.97), g), ("FAIL", pf(0.0), g), ("UNRESOLVED", pf(1.0, se=0.4), g),
                 ("FIT FAILURE", pf(1.0, fail="at the bound"), g),
                 ("PASS", pf(1.0, gg=0.9), {f: 0.9 for f in files}),                        # g scales μ̃
                 ("FAIL", pf(1.0, gg=0.9), g)]
        if obs == "A":
            cases += [("PASS", pf(1.0, mis=1), g), ("MODEL MISFIT", pf(1.0, mis=2), g),
                      ("MODEL MISFIT", pf(0.0, se=0.4, mis=nf), g), ("FIT FAILURE", pf(1.0, mis=nf, fail="x"), g)]
        else:
            cases += [("PASS", pf(1.0, mis=nf), g)]                                         # no GoF for (B)
        # per-file condition (SE_f = 0.02 at the floor, 3·SE_f = 0.06), pool kept inside its band: one file out passes,
        # two files out do not
        x = pf(1.0)
        x[files[0]]["mu"] += 0.07
        x[files[1]]["mu"] -= 0.05
        cases.append(("PASS", x, g))
        x = pf(1.0)
        x[files[0]]["mu"] += 0.07
        x[files[1]]["mu"] -= 0.07
        cases.append(("FAIL", x, g))
        out = [(want, rule(obs, x, w, cal, 2e-4, gg)["verdict"]) for want, x, gg in cases]
        r = rule(obs, pf(1.0, se=0.001), w, cal, 2e-4, g)
        se_ok = abs(r["se_file"][files[0]] - math.sqrt(0.02 ** 2 + 0.02 ** 2 / 200)) < 1e-12
        good = all(a == b for a, b in out) and abs(r["mu_pool"] - 1.0) < 1e-12 and se_ok
        ok &= good
        print(f"({obs}) RULE {out} se floor {se_ok} → {'PASS' if good else 'FAIL'}")
    return ok


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "selftest":
        sys.exit(0 if selftest() else 1)
    elif cmd == "ruletest":
        sys.exit(0 if rule_selftest() else 1)
    elif cmd == "calib_fit":
        calib_fit(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    elif cmd == "declare":
        declare(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "AB")

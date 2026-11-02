# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 read (FN1_STAGE2_SEAL.md): R_F on the fresh slice (10¹⁰, 10¹¹] for the nine class-number-1 imaginary
quadratic fields and ℤ[√2]; rank tests against C_F; the −7 displacement prediction.

  python fn1_read2.py read     PINS2 OUT              the read: rows [n(1e10), n(1e11)) of every field
  python fn1_read2.py dry      PINS2 OUT X_LO X_HI    §9.F rehearsal: w = 2 fields from the pins file's "dry" block
                                                      (synthetic rows), window [n(X_LO), n(X_HI)) in place of 10¹⁰…10¹¹
  python fn1_read2.py drysynth OUT N_HALF             full-size memory / timing check: synthetic θ (seeded uniform),
                                                      N_HALF rows; no archive, no statistic of any data

Window. n_lo, n_hi = the ℤ[√2] split-prime counts below X_LO, X_HI (rq1_read.n_below), as stage 1. Each field
contributes its own rows [n_lo, n_hi) in prime order; θ and 1 − θ; N = 2 (n_hi − n_lo); K = round(N^β).
R(β) = var_stream(θ, K)/(N/K), exact (rq1_read.var_stream), β ∈ {0.55, 0.40, 0.45}.
Integrity. Every manifest sha256 against PINS2; every loaded segment sha256 against its manifest. Prefix guard: for
each w = 2 field the pinned stage-1 manifest (sha256 in PINS2) must list exactly the same (k, rows, sha256) as the
first segments of the stage-2 manifest. A mismatch raises (no output). Mount guard on /mnt/data.

Primary (β 0.55) and secondaries (β 0.45, 0.40): Spearman rank test of R against C_F over the nine fields; exact
one-sided p over 9!; PASS iff p < 0.01 and ρ > 0 (Σd² ≤ 26). Exact ties → VOID (ties).
Read-time noise (all three β). For each field the slice rows are split into M = 8 contiguous prime-order segments;
R_seg at K_seg = round((2·(n_f // 8))^β); relSD = SD/mean × √(K_seg/K) (stage-1 §3a, raw), pooled RMS over the nine
fields; also per-field linear-detrended relSD (ddof 2) pooled the same way.
- Primary rule (Will 2026-11-02: raw, as stage 1): power at the raw β 0.55 ratio from R = b C + σ ε with
  b = B055, σ = ratio × SE055 (stage-1-derived constants below), 200,000 seeded simulations. Power < 0.80 → a primary
  FAIL reads "FAIL (UNPOWERED at the read-time noise)".
- Secondaries β 0.45 / 0.40: DECLARED ONE-WAY in advance (Will 2026-11-02 rulings, TOOLKIT §9.J as clarified): the
  same rank test with B045 / B040, SE045 / SE040; a PASS is informative, a FAIL is not and always reads
  "FAIL (one-way arm: FAIL not informative)". Their power at the read-time raw ratio is reported (descriptive).
−7 prediction (β 0.55), DECLARED ONE-WAY, flat null (Will 2026-11-02 rulings, superseding option B's local slope):
T = min(R_−7 − R_−8, R_−7 − R_−11). PASS iff T > m. An exact equality R_−7 = R_−8 or R_−7 = R_−11 → VOID (ties).
A FAIL is not informative and always reads "FAIL (one-way arm: FAIL not informative)".
- Rule noise: σ_rel = √(det² + DRIFT_SD²), det = the read-time pooled detrended relSD at β 0.55, DRIFT_SD = 0.012458
  (the slope-noise-corrected stage-1 drift spread, committed). σ = σ_rel × mean_F R_F(0.55).
- m = the 95th percentile (numpy linear quantile) of T under a FLAT null (b_null = 0): R_F = a + σ ε, 200,000 draws,
  seed SEED_M7. The false-PASS rate is 0.05 under the flat null and ≤ 0.05 under any C-dependence that is monotone
  non-decreasing at −7, −8, −11 (it lowers T pointwise); checked on an independent seed (SEED_M7 + 2) and reported.
- Reported too (descriptive, no verdict): the power under persistence P(T + DELTA7 > m) (seed SEED_M7 + 1); the
  read-time b_global and b_local (−8, −11, ℤ[i], −19); the plain two-neighbour hit; and the margin and power under
  the raw noise alone, the detrended noise alone, the local slope (option B as first ruled) and the global slope.
Descriptive: ρ against log|D|; fresh-only 7 (exact over 7!); ℤ[√2] placement at 0.40 / 0.45; pairs; OLS residuals on
C_F per β, and their Pearson r with the stage-1 residuals (pinned stage-1 read); Chen-form P_F fit (constants below).
Output: JSON, sorted keys, no timings (sidecar OUT.timing); stdout prints only "done".
"""
import hashlib
import itertools
import json
import math
import os
import resource
import sys
import time

import numpy as np

try:
    import rq1_read as Q
except ImportError:                                   # repo layout; on spot the rq1 modules are copied alongside
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rq1"))
    import rq1_read as Q
import rq1_zw as Z
import fn1_archive as FA

X10, X11 = 10 ** 10, 10 ** 11
BETAS = [0.55, 0.40, 0.45]
FIELDS = ["-7", "-8", "-11", "zi", "-19", "zw", "-43", "-67", "-163"]
W2 = ["-7", "-8", "-11", "-19", "-43", "-67", "-163"]
C = dict(zip(FIELDS, [math.log(7), math.log(8), math.log(11), math.log(16), math.log(19), math.log(27),
                      math.log(43), math.log(67), math.log(163)]))
LOGD = dict(zip(FIELDS, [math.log(7), math.log(8), math.log(11), math.log(4), math.log(19), math.log(3),
                         math.log(43), math.log(67), math.log(163)]))
ALPHA = 0.01
FRESH = W2
M_SEG = 8
C_SE = 0.6271633049515984
# ---- constants committed before the read (FN1_STAGE2_SEAL.md §3; sources: stage-1 READ1.json sha256 47c19dd2…,
#      lead/SEGNOISE_BETAS.json, lead/FN1_STAGE2_CONSTANTS.json), written by fn1_stage2_constants.py and frozen here:
CONST = {
 "B": {
  "0.4": 0.013169587753083384,
  "0.45": 0.013885567804458532,
  "0.55": 0.04550657297146217
 },
 "DELTA7": 0.03518989655270044,
 "DRIFT_SD": 0.012457967508111512,
 "P_full": {
  "-11": 2.2097896370665207,
  "-163": 4.011084636085667,
  "-19": 2.4382042355586235,
  "-43": 2.9020374959605113,
  "-67": 3.2341797463491213,
  "-7": 1.985709842433647,
  "-8": 2.1561439138284135,
  "zi": 2.535468434346986,
  "zw": 2.7545130997928577
 },
 "P_noA": {
  "-11": 2.398490803205579,
  "-163": 4.265746474994277,
  "-19": 2.678387652926035,
  "-43": 3.15548820037336,
  "-67": 3.4885536212360666,
  "-7": 2.051569174366095,
  "-8": 2.170157159104636,
  "zi": 2.594458153504011,
  "zw": 2.950539269844647
 },
 "SE": {
  "0.4": 0.011991381642377912,
  "0.45": 0.008000700533594972,
  "0.55": 0.00342234884863943
 },
 "STAGE1_RESID": {
  "0.4": {
   "-11": -0.005293890376653287,
   "-163": 0.012015611247067515,
   "-19": 0.004036102264163399,
   "-43": 0.017977597092310615,
   "-67": -0.031806600616262615,
   "-7": -0.0055643279717930705,
   "-8": 0.010307120283098437,
   "zi": -0.001202570249151269,
   "zw": -0.00046904167278150055
  },
  "0.45": {
   "-11": 0.01107383937334816,
   "-163": 0.02194289412711914,
   "-19": -0.005871786585304739,
   "-43": 0.007035753461336114,
   "-67": -0.03251906211579547,
   "-7": 0.00386327801608477,
   "-8": 0.0010329525977201826,
   "zi": -0.00225797674291639,
   "zw": -0.004299892131592986
  },
  "0.55": {
   "-11": -0.004731995297765912,
   "-163": 0.02920897214188456,
   "-19": -0.025399887860556247,
   "-43": -0.010719979509868471,
   "-67": -0.008061338484413372,
   "-7": 0.03518989655270044,
   "-8": 0.009167665266229252,
   "zi": -0.010092424191414762,
   "zw": -0.014560908616799928
  }
 }
}   # frozen from lead/FN1_STAGE2_CONSTANTS.json; DRIFT_SD = the slope-noise-corrected spread (seal §3a)
SEED_PRIMARY, SEED_M7 = 20261121, 20261122
NSIM = 200_000


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def theta_fn(field):
    if field in ("zs2", "zi"):
        return lambda rows: Q.field_thetas(rows, field)
    if field == "zw":
        return Z.thetas_zw
    D = int(field)
    return lambda rows: FA.thetas(D, rows)


def check_prefix(stage1_manifest, stage1_sha, stage2_man):
    assert sha_file(stage1_manifest) == stage1_sha, ("stage-1 manifest pin", stage1_manifest)
    s1 = json.load(open(stage1_manifest))["segments"]
    s2 = stage2_man["segments"][: len(s1)]
    key = lambda s: (s["k"], s["rows"], s["sha256"])
    assert [key(s) for s in s1] == [key(s) for s in s2], ("prefix guard", stage1_manifest)


def load_window(d, field, lo, hi, pinned_sha, prefix=None):
    """Rows [lo, hi) of the field's prime-ordered list: θ and the mirror, sorted; plus the unsorted half (prime
    order) for the segment-noise estimate."""
    mp = os.path.join(d, "MANIFEST.json")
    assert sha_file(mp) == pinned_sha, ("manifest pin", d)
    man = json.load(open(mp))
    if prefix is not None:
        check_prefix(prefix[0], prefix[1], man)
    n = hi - lo
    th = np.empty(2 * n, np.float64)
    f = theta_fn(field)
    pos, got = 0, 0                                          # pos: global row index at the start of segment s
    for s in man["segments"]:
        if got >= n:
            break
        a, b = pos, pos + s["rows"]
        pos = b
        if b <= lo:
            continue
        path = os.path.join(d, f"seg_{s['k']:04d}.npy")
        assert hashlib.sha256(open(path, "rb").read()).hexdigest() == s["sha256"], path
        rows = np.load(path)
        assert len(rows) == s["rows"], ("segment rows", path)
        rows = rows[max(lo - a, 0): min(hi, b) - a]
        t1 = f(rows)
        th[got:got + len(rows)] = t1
        th[n + got:n + got + len(rows)] = np.mod(1.0 - t1, 1.0)
        got += len(rows)
    assert got == n, ("rows", d, got, n)
    half = th[:n].copy()
    th.sort()
    return th, half


def seg_noise(half, n, K, beta):
    ns = n // M_SEG
    Ks = int(round((2 * ns) ** beta))
    r = []
    for i in range(M_SEG):
        s = half[i * ns:(i + 1) * ns]
        t = np.concatenate([s, np.mod(1.0 - s, 1.0)])
        t.sort()
        r.append(float(Q.var_stream(t, Ks) / (2 * ns / Ks)))
    r = np.array(r)
    x = np.arange(M_SEG)
    fit = np.polyfit(x, r, 1)
    det = r - np.polyval(fit, x)
    sc = math.sqrt(Ks / K)
    return dict(K_seg=Ks, R_seg=r.tolist(), relSD_full=float(r.std(ddof=1) / r.mean() * sc),
                relSD_full_detrended=float(det.std(ddof=2) / r.mean() * sc),
                drift_total_rel=float(fit[0] * (M_SEG - 1) / r.mean()))


def exact_null_counts(n=9):
    r0 = np.arange(n)
    d2 = [int(((np.array(p) - r0) ** 2).sum()) for p in itertools.permutations(range(n))]
    return np.bincount(np.array(d2))


def d2_crit(counts):
    return max(d for d in range(len(counts)) if counts[: d + 1].sum() / counts.sum() < ALPHA)


def power_at(ratio, b, se, counts, seed):
    C_arr = np.array([C[f] for f in FIELDS])
    rng = np.random.default_rng(seed)
    sim = b * C_arr[None, :] + ratio * se * rng.standard_normal((NSIM, 9))
    return float((((sim.argsort(1).argsort(1) - np.arange(9)) ** 2).sum(1) <= d2_crit(counts)).mean())


def rank_test(Rvals, keyC, counts, fields=None):
    fields = FIELDS if fields is None else fields
    m = len(fields)
    vals = [Rvals[f] for f in fields]
    if len(set(vals)) < len(vals):
        return dict(verdict="VOID (ties)")
    rk_R = np.argsort(np.argsort(vals))
    rk_C = np.argsort(np.argsort([keyC[f] for f in fields]))
    d2 = int(((rk_R - rk_C) ** 2).sum())
    rho = 1 - 6 * d2 / (m * (m * m - 1))
    p = float(counts[: d2 + 1].sum() / counts.sum())
    return dict(sum_d2=d2, rho=rho, p_exact=p, verdict="PASS" if (p < ALPHA and rho > 0) else "FAIL",
                ranks_R=dict(zip(fields, rk_R.tolist())))


def ols(R, key):
    x = np.array([key[f] for f in FIELDS])
    y = np.array([R[f] for f in FIELDS])
    A = np.vstack([np.ones(9), x]).T
    coef = np.linalg.lstsq(A, y, rcond=None)[0]
    return coef, dict(zip(FIELDS, (y - A @ coef).tolist()))


_DRAWS = {}


def m7_draws(seed):
    """Seeded standard-normal draws (NSIM, 3) for (−7, −8, −11); cached, so every call with a seed sees the same draws."""
    if seed not in _DRAWS:
        _DRAWS[seed] = np.random.default_rng(seed).standard_normal((NSIM, 3))
    return _DRAWS[seed]


def m7_T(b, sigma, delta, seed):
    """T = min(R_−7 − R_−8, R_−7 − R_−11) under R = b C + σ ε (+ delta on −7)."""
    e = m7_draws(seed) * sigma
    r7 = b * C["-7"] + delta + e[:, 0]
    return np.minimum(r7 - (b * C["-8"] + e[:, 1]), r7 - (b * C["-11"] + e[:, 2]))


def m7_margin(b, sigma, seed=None):
    return float(np.quantile(m7_T(b, sigma, 0.0, SEED_M7 if seed is None else seed), 0.95))


def m7_power(b, sigma, m, delta, seed=None):
    return float((m7_T(b, sigma, delta, SEED_M7 + 1 if seed is None else seed) > m).mean())


def m7_rates(b, sigma, delta, seed):
    """P(R_−7 > R_−8 and R_−7 > R_−11): the plain two-neighbour hit rate (descriptive)."""
    return float((m7_T(b, sigma, delta, seed) > 0).mean())


LOCAL4 = ["-8", "-11", "zi", "-19"]


def slopes(R55):
    coef, _ = ols(R55, C)
    b_global = float(coef[1])
    x = np.array([C[f] for f in LOCAL4]); y = np.array([R55[f] for f in LOCAL4])
    b_local_raw = float(np.polyfit(x, y, 1)[0])
    b_local = max(0.0, b_local_raw)
    return b_global, b_local_raw, b_local, min(b_global, b_local)


ONE_WAY_FAIL = "FAIL (one-way arm: FAIL not informative)"
UNPOWERED = "FAIL (UNPOWERED at the read-time noise)"


def minus7(R55, det_rel, raw_rel):
    if R55["-7"] == R55["-8"] or R55["-7"] == R55["-11"]:
        return dict(verdict="VOID (ties)")
    b_global, b_local_raw, b_local, b_optB = slopes(R55)
    Rbar = float(np.mean([R55[f] for f in FIELDS]))
    s_rule = math.sqrt(det_rel ** 2 + CONST["DRIFT_SD"] ** 2) * Rbar
    T = min(R55["-7"] - R55["-8"], R55["-7"] - R55["-11"])
    m = m7_margin(0.0, s_rule)
    desc = {}
    for nm, bb, ss in (("raw_noise_only", 0.0, raw_rel * Rbar), ("detrended_noise_only", 0.0, det_rel * Rbar),
                       ("local_slope_optionB", b_optB, s_rule), ("global_slope", b_global, s_rule)):
        mm = m7_margin(bb, ss)
        desc[nm] = dict(slope=bb, sigma=ss, margin=mm, power_persist=m7_power(bb, ss, mm, CONST["DELTA7"]),
                        T_above_margin=bool(T > mm))
    out = dict(R_m7=R55["-7"], R_m8=R55["-8"], R_m11=R55["-11"], T=T, b_null=0.0, b_global=b_global,
               b_local_raw=b_local_raw, b_local=b_local, Rbar=Rbar, det_rel=det_rel, drift_sd=CONST["DRIFT_SD"],
               raw_rel=raw_rel, sigma_rel_rule=s_rule / Rbar, sigma_rule=s_rule, margin=m,
               power_persist_descriptive=m7_power(0.0, s_rule, m, CONST["DELTA7"]),
               false_pass_check=float((m7_T(0.0, s_rule, 0.0, SEED_M7 + 2) > m).mean()),
               two_neighbour_hit_descriptive=bool(T > 0), one_way=True, descriptive=desc)
    out["verdict"] = "PASS" if T > m else ONE_WAY_FAIL
    return out


def verdict_labels(v055, v045, v040, primary_fail_informative, zs2_between, v_m7):
    """The sealed verdict lattice: primary two-way (FAIL informative iff the read-time power ≥ 0.80); β 0.45, β 0.40
    and −7 one-way (a FAIL is never informative); ℤ[√2] placement plain."""
    one = lambda v: ONE_WAY_FAIL if v == "FAIL" else v
    return dict(primary_beta055=UNPOWERED if (v055 == "FAIL" and not primary_fail_informative) else v055,
                secondary_beta045=one(v045), secondary_beta040=one(v040),
                zs2_placement_beta055="PASS" if zs2_between else "FAIL", minus7_beta055=v_m7)


def run(pins_json, out, X_LO, X_HI, dry):
    t0 = time.time()
    assert all(v is not None for v in (CONST["DRIFT_SD"], CONST["DELTA7"], CONST["P_noA"], CONST["STAGE1_RESID"])) \
        and all(CONST["B"].values()) and all(CONST["SE"].values()), "constants not frozen"
    pins = json.load(open(pins_json))
    assert os.path.ismount("/mnt/data"), "mount guard: /mnt/data is not mounted"
    arch = dict(pins["archives"])
    stage1 = dict(pins["stage1_manifests"])
    if dry:
        arch.update(pins["dry"]["archives"])
        stage1.update(pins["dry"]["stage1_manifests"])
    lo, hi = Q.n_below(arch["zs2"]["dir"], X_LO), Q.n_below(arch["zs2"]["dir"], X_HI)
    n = hi - lo
    N = 2 * n
    Ks = {b: int(round(N ** b)) for b in BETAS}
    res = dict(label="FN1 stage-2 read (fresh slice)" + (" (DRY RUN: synthetic w = 2 rows, not the sealed data)" if dry else ""),
               X_LO=X_LO, X_HI=X_HI, n_lo=lo, n_hi=hi, n=n, N=N, K={str(b): k for b, k in Ks.items()},
               pins_sha256=sha_file(pins_json), R={}, prefix_guard="checked (raises on mismatch)")
    noise = {str(b): {} for b in BETAS}
    for field in FIELDS + ["zs2"]:
        pre = (stage1[field]["path"], stage1[field]["sha256"]) if field in W2 else None
        th, half = load_window(arch[field]["dir"], field, lo, hi, arch[field]["manifest_sha256"], pre)
        res["R"][field] = {str(b): float(Q.var_stream(th, Ks[b]) / (N / Ks[b])) for b in BETAS}
        del th
        if field in FIELDS:
            for b in BETAS:
                noise[str(b)][field] = seg_noise(half, n, Ks[b], b)
        del half
    counts, counts7 = exact_null_counts(), exact_null_counts(7)
    rtn = {}
    for b in BETAS:
        sb = str(b)
        pooled = math.sqrt(float(np.mean([noise[sb][f]["relSD_full"] ** 2 for f in FIELDS])))
        pooled_d = math.sqrt(float(np.mean([noise[sb][f]["relSD_full_detrended"] ** 2 for f in FIELDS])))
        model = math.sqrt(2 / (C_SE * Ks[b]))
        pw = power_at(pooled / model, CONST["B"][sb], CONST["SE"][sb], counts, SEED_PRIMARY + int(b * 100))
        rtn[sb] = dict(M=M_SEG, per_field=noise[sb], pooled_relSD_full=pooled, noise_ratio_to_sealed_model=pooled / model,
                       pooled_relSD_full_detrended=pooled_d, noise_ratio_detrended=pooled_d / model,
                       power_at_read_noise=pw, fail_informative=bool(pw >= 0.80))
    res["read_time_noise"] = rtn
    tests = {}
    for b in BETAS:
        sb = str(b)
        Rb = {f: res["R"][f][sb] for f in FIELDS}
        coef, resid = ols(Rb, C)
        s1 = CONST["STAGE1_RESID"][sb]
        r_s12 = float(np.corrcoef([s1[f] for f in FIELDS], [resid[f] for f in FIELDS])[0, 1])
        fitP = {}
        for nm in ("P_noA", "P_full"):
            cP, rP = ols(Rb, CONST[nm])
            fitP[nm] = dict(slope=float(cP[1]), resid_SD=float(np.std(list(rP.values()), ddof=2)))
        tests[sb] = dict(rank_test_C=rank_test(Rb, C, counts), rank_test_logD_descriptive=rank_test(Rb, LOGD, counts),
                         fresh_only_7_descriptive_unpowered=rank_test(Rb, C, counts7, FRESH),
                         zs2_between_m67_m163=bool(Rb["-67"] < res["R"]["zs2"][sb] < Rb["-163"]),
                         pairs={"-7/-8": dict(dR=Rb["-8"] - Rb["-7"], dC=C["-8"] - C["-7"]),
                                "zi/-19": dict(dR=Rb["-19"] - Rb["zi"], dC=C["-19"] - C["zi"])},
                         ols_C=dict(a=float(coef[0]), b=float(coef[1]), resid=resid,
                                    resid_SD=float(np.std(list(resid.values()), ddof=2)),
                                    pearson_with_stage1_resid=r_s12),
                         chen_form_fit_descriptive=fitP)
    R55 = {f: res["R"][f]["0.55"] for f in FIELDS}
    tests["minus7_beta055"] = minus7(R55, rtn["0.55"]["pooled_relSD_full_detrended"], rtn["0.55"]["pooled_relSD_full"])
    res["tests"] = tests

    res["verdict"] = verdict_labels(tests["0.55"]["rank_test_C"]["verdict"], tests["0.45"]["rank_test_C"]["verdict"],
                                    tests["0.4"]["rank_test_C"]["verdict"], rtn["0.55"]["fail_informative"],
                                    tests["0.55"]["zs2_between_m67_m163"], tests["minus7_beta055"]["verdict"])
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    ru = resource.getrusage(resource.RUSAGE_SELF)
    open(out + ".timing", "w").write(f"wall_s {time.time() - t0:.1f}\ncpu_s {time.process_time():.1f}\n"
                                     f"maxrss_GB {ru.ru_maxrss / 1e6:.1f}\n")
    print("done")
    return 0


def drysynth(out, n):
    """Full-size memory / timing check of the read's array path on synthetic θ (no data, no statistic of data)."""
    t0 = time.time()
    rng = np.random.default_rng(20261123)
    th = np.empty(2 * n, np.float64)
    step = 50_000_000
    for i in range(0, n, step):
        m = min(step, n - i)
        t1 = rng.random(m)
        th[i:i + m] = t1
        th[n + i:n + i + m] = np.mod(1.0 - t1, 1.0)
    half = th[:n].copy()
    th.sort()
    N = 2 * n
    Ks = {b: int(round(N ** b)) for b in BETAS}
    R = {str(b): float(Q.var_stream(th, Ks[b]) / (N / Ks[b])) for b in BETAS}
    del th
    sn = {str(b): seg_noise(half, n, Ks[b], b) for b in BETAS}
    ru = resource.getrusage(resource.RUSAGE_SELF)
    json.dump(dict(label="FN1 stage-2 drysynth (synthetic uniform θ; memory/timing only)", n=n, N=N, R_uniform=R,
                   seg_ratio_055=sn["0.55"]["relSD_full"] / math.sqrt(2 / (C_SE * Ks[0.55]))), open(out, "w"),
              indent=1, sort_keys=True)
    open(out + ".timing", "w").write(f"wall_s {time.time() - t0:.1f}\ncpu_s {time.process_time():.1f}\n"
                                     f"maxrss_GB {ru.ru_maxrss / 1e6:.1f}\n")
    print("done")
    return 0


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "read":
        sys.exit(run(sys.argv[2], sys.argv[3], X10, X11, False))
    if m == "dry":
        sys.exit(run(sys.argv[2], sys.argv[3], int(float(sys.argv[4])), int(float(sys.argv[5])), True))
    if m == "drysynth":
        sys.exit(drysynth(sys.argv[2], int(sys.argv[3])))
    sys.exit("unknown mode")

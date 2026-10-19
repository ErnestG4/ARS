"""Corrected (B): the read's estimator, error bars, calibration declaration and rule, as code (CORRECTED_B_DESIGN.md
§1, §4; rounds 57–58). Nothing here reads an F6 file; the sealed read (b2_sealread.py) is the only path that will.

Per F6 file f: x = N̄(γ) − N̄(t₀) (exact θ, followup_read.unfold, as the sealed (B)); b2_est.zeros_stats at L* (32
offsets, joint-offset segment bootstrap at 300/1000/3000/10000 units, B = 200) → k̄₃ and SE_boot(G);
μ̂_f = (k̄₃ − κ₃^sine,f)/Δκ₃,f (results/b2_pred.json), SE_boot,f(G) in μ units = SE_boot(k̄₃; G)/|Δκ₃,f|.

Calibration (declared before the seal): b2_calsamp's R = 200 CUE_1000 replicates per F6 file through the same estimator:
bias b_f (replicate mean of μ̂), SD_f, BLOCK = the shortest segment length whose SE_boot/SD (geometric mean over files)
is ≥ 0.95 (none → the longest); operating characteristics under the rule with the calibration replicates shifted by
μ·g (false FAIL at μ = 1, power at μ = 0, and the PASS curve).

Rule: route (a)'s, the rule code of the sealed (B) (followup_read.rule, observable B; one code path):
  μ̃_f = (μ̂_f − b_f)/g;  SE_f = max(SD_f, SE_boot,f(G) for G ≥ BLOCK), widened by SD_f/√R, then divided by g;
  μ̃_pool = Σ w_f μ̃_f, SE_pool = (Σ w_f² SE_f²)^½, w_f ∝ n_f (pre-data, exact θ);
  FIT FAILURE (a non-finite estimate) > UNRESOLVED (2·SE_pool > 0.25) > PASS (|μ̃_pool − 1| ≤ 2·SE_pool + δμ_sys and all
  files but one within 3·SE_f) > FAIL.
g and δμ_sys: g = the CUE_N known-answer slope at L* under round 53's rule (b2_cuen.json; divided out only if
|slope − 1| > 2·SE; fails closed if SE ≤ 0.005 was not reached); δμ_sys = the prediction's (b2_pred.json) + SE(slope).
The test stands alone (round 58): no joint reading, no family-wise rate.

  python b2_read.py selftest               known answers, the G1b red path and the rule's verdicts (small)
  python b2_read.py declare SAMP_DIR       → results/calib/b2_calib_declared.json
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "ph2"))
import b2_est as E  # noqa: E402
import b2_pred as BP  # noqa: E402
import followup_pred as P  # noqa: E402
import followup_read as FR  # noqa: E402

PRED = os.path.join(HERE, "results", "b2_pred.json")
CUEN = os.path.join(HERE, "results", "b2_cuen.json")
CALIB = os.path.join(HERE, "results", "calib", "b2_calib_declared.json")
FILES = BP.F6
SEGS = E.SEGS
B_BOOT = 200
BLOCK_SE_RATIO = 0.95
SHIFTS = FR.SHIFTS


def weights():
    return P.counts(FILES)


def G():
    """Round 53's rule at L*: g and the δμ_sys addition (fails closed if the slope run has not reached SE ≤ 0.005)."""
    r = json.load(open(CUEN))
    d = r["rule"]
    if not d["se_reached"]:
        raise RuntimeError(f"b2_read.G: SE(slope) target not reached ({d['next']})")
    if r["L"] != BP.L_star():
        raise RuntimeError("b2_read.G: the slope run's L is not L*")
    return dict(g=d["g"], dmu_sys_add=d["dmu_sys_add"], decision=d["decision"], slope=r["slope"], slope_se=r["slope_se"],
                chi2=r["chi2"], p=r["p"], batches=r["batches"], extend=r["extend"])


def g_files(gb=None):
    gb = G()["g"] if gb is None else gb
    return {f: 1.0 * gb for f in FILES}                      # κ₃ is exactly linear in μ: the limit slope is 1


def dmu_sys(pred):
    return pred["delta_mu_sys"] + G()["dmu_sys_add"]


def fit(t, res):
    """t: the prediction's row for the file; res: b2_est.Acc.result(). The per-file record the rule reads."""
    k = res["k3bar"]
    mu = (k - t["kappa3_sine"]) / t["dkappa3"]
    se = {G_: v / abs(t["dkappa3"]) for G_, v in res["se_boot"].items()}
    ok = math.isfinite(mu) and all(math.isfinite(v) and v > 0 for v in se.values())
    return dict(k3bar=k, mu=float(mu) if ok else None, se=se, n_windows=res["n_windows"],
                fail=None if ok else "non-finite estimate or bootstrap SE")


def rule(per_file, cal, dmu, g):
    w, _ = weights()
    return FR.rule("B", per_file, w, cal, dmu, g)


# ------------------------------------------------------------------ declaration
def load_samp(samp_dir):
    rows = {}
    for fn in sorted(os.listdir(samp_dir)):
        if fn.startswith("b2cal_") and fn.endswith(".jsonl"):
            for r in map(json.loads, open(os.path.join(samp_dir, fn))):
                rows.setdefault((r["rep"], r["file"]), r)
    return rows


def declare_cal(rows, pred, dmu, g):
    files = list(FILES)
    L = BP.L_star()
    reps = sorted({rep for rep, _ in rows})
    joint = [r for r in reps if all((r, f) in rows for f in files)]
    if any(rows[(r, f)]["L"] != L for r in joint for f in files):
        raise RuntimeError("declare: a calibration row is not at L*")
    fits = {(r, f): fit(pred["files"][f], rows[(r, f)]) for r in joint for f in files}
    fails = [dict(rep=r, file=f, why=fits[(r, f)]["fail"]) for r in joint for f in files if fits[(r, f)]["fail"]]
    good = [r for r in joint if all(not fits[(r, f)]["fail"] for f in files)]
    sd = {f: float(np.std([fits[(r, f)]["mu"] for r in good], ddof=1)) for f in files}
    se_mean = {f: {G_: float(np.mean([fits[(r, f)]["se"][str(G_)] for r in good])) for G_ in SEGS} for f in files}
    ratio = {G_: float(np.exp(np.mean([np.log(se_mean[f][G_] / sd[f]) for f in files]))) for G_ in SEGS}
    ok = [G_ for G_ in SEGS if ratio[G_] >= BLOCK_SE_RATIO]
    cal = dict(observable="corrected (B)", L=L, block=min(ok) if ok else max(SEGS), block_fallback=not ok,
               se_over_sd_geomean={str(k): v for k, v in ratio.items()}, R=len(good), R_complete=len(joint),
               fit_failures=fails, files={})
    for f in files:
        mu = np.array([fits[(r, f)]["mu"] for r in good])
        cal["files"][f] = dict(bias=float(mu.mean()), bias_z=float(mu.mean() / (sd[f] / math.sqrt(len(mu)))), sd=sd[f],
                               R=len(mu), se_boot_mean={str(k): v for k, v in se_mean[f].items()},
                               n_windows_mean=float(np.mean([rows[(r, f)]["n_windows"] for r in good])))
    curve = {}
    for m in (0.0,) + SHIFTS:
        v = [rule({f: dict(fits[(r, f)], mu=fits[(r, f)]["mu"] + m * g[f]) for f in files}, cal, dmu, g)["verdict"]
             for r in good]
        curve[f"{m:.2f}"] = {k: v.count(k) for k in sorted(set(v))}
    n = len(good)
    cal["operating_characteristics"] = dict(dmu_sys=dmu, g=g, false_fail=1 - curve["1.00"].get("PASS", 0) / n,
                                            power_mu0=curve["0.00"].get("FAIL", 0) / n, verdicts=curve)
    return cal


def declare(samp_dir):
    pred = json.load(open(PRED))
    if pred["L"] != BP.L_star():
        raise SystemExit("REFUSED: the prediction's L is not L*")
    rows = load_samp(samp_dir)
    cal = declare_cal(rows, pred, dmu_sys(pred), g_files())
    cal["G_round53_at_Lstar"] = G()
    os.makedirs(os.path.dirname(CALIB), exist_ok=True)
    json.dump(cal, open(CALIB, "w"), indent=1, sort_keys=True)
    print(f"corrected (B) at L* = {cal['L']}: R {cal['R']} (complete {cal['R_complete']}), failures "
          f"{len(cal['fit_failures'])}, BLOCK {cal['block']} (SE/SD {cal['se_over_sd_geomean']})", flush=True)
    for f, c in cal["files"].items():
        print(f"  {f}: b {c['bias']:+.5f} (z {c['bias_z']:+.2f})  SD {c['sd']:.5f}", flush=True)
    oc = cal["operating_characteristics"]
    print(f"  δμ_sys {oc['dmu_sys']:.2e}, g {next(iter(oc['g'].values())):.4f}: false FAIL (μ = 1) "
          f"{oc['false_fail']:.3f}, power (μ = 0) {oc['power_mu0']:.3f}; "
          + ", ".join(f"μ {m}: PASS {c.get('PASS', 0)}" for m, c in oc["verdicts"].items()), flush=True)
    return cal


# ------------------------------------------------------------------ known answers and red paths
def g1b_redpath(L, n=200_000, n_shift=8, seed=(20261018, 58, 99), sigma=0.3):
    """ENGINE_V2_SPEC G1b on the read's estimator: a jittered lattice x_k = k + σ·N(0, 1) read with the grid anchored at
    the first point, after shifting the data by n_shift uniform origins in [0, 1). The offset-averaged k̄₃ must move by
    at most 1 SE_boot (G = 1000) across origins; the single-offset k₃ (the sealed (B)'s grid) must move by more than
    3 SE_boot (the witness, so the check can fail)."""
    rng = np.random.default_rng(list(seed))
    x0 = np.sort(np.arange(n) + sigma * rng.standard_normal(n))
    shifts = np.concatenate([[0.0], rng.uniform(0, 1, n_shift)])
    avg, one, se = [], [], []
    for s in shifts:
        x = x0 + s
        x = x[x >= 0]
        a = E.Acc(L, x[-1])
        a.add_block(x[None, :], float(x[-1]), [0.0])
        r = a.result(np.random.default_rng(list(seed) + [1]), n_boot=100)
        avg.append(r["k3bar"])
        one.append(r["k3_u"][0])
        se.append(r["se_boot"]["1000"])
    se0 = se[0]
    d_avg = float(np.max(np.abs(np.array(avg) - avg[0])) / se0)
    d_one = float(np.max(np.abs(np.array(one) - one[0])) / se0)
    return dict(L=L, n=n, sigma=sigma, shifts=shifts.tolist(), se_boot=se0, max_shift_avg_SE=d_avg,
                max_shift_single_SE=d_one, ok=d_avg <= 1.0 and d_one > 3.0)


def selftest():
    ok = True
    L = BP.L_star()
    rng = np.random.default_rng([20261018, 58, 98])
    # Poisson: κ₃ = L for the count of a unit-rate Poisson process in any window
    x = np.cumsum(rng.exponential(size=2_000_000))
    r = E.zeros_stats(x, L, rng, n_boot=100)
    z = (r["k3bar"] - L) / r["se_boot"]["1000"]
    g = abs(z) < 4
    ok &= g
    print(f"Poisson: k̄₃ {r['k3bar']:.4f} (κ₃ = {L}), z {z:+.2f} → {'PASS' if g else 'FAIL'}", flush=True)
    # per-offset k₃ equals the direct k-statistic of the counts at that offset
    x = np.cumsum(rng.exponential(size=50_000))
    r = E.zeros_stats(x, L, rng, n_boot=10)
    d = 0.0
    for q in (0, 7, 31):
        u = q * L / E.NU
        nw = int((x[-1] - u) // L)
        c = np.bincount(np.floor((x[x >= u] - u) / L).astype(int), minlength=nw)[:nw]
        d = max(d, abs(r["k3_u"][q] - FR.k3(c)))
    g = d < 1e-9
    ok &= g
    print(f"per-offset k₃ vs direct: max |diff| {d:.1e} → {'PASS' if g else 'FAIL'}", flush=True)
    # μ units and the record
    t = dict(kappa3_sine=0.1, dkappa3=-0.02)
    rec = fit(t, dict(k3bar=0.08, se_boot={"300": 0.002, "1000": 0.004}, n_windows=10.0))
    g = abs(rec["mu"] - 1.0) < 1e-12 and abs(rec["se"]["1000"] - 0.2) < 1e-12 and rec["fail"] is None
    rec2 = fit(t, dict(k3bar=float("nan"), se_boot={"300": 0.002}, n_windows=10.0))
    g &= rec2["fail"] is not None and rec2["mu"] is None
    ok &= g
    print(f"μ units (k̄₃ 0.08 → μ̂ 1, SE 0.004 → 0.2) and a non-finite estimate → FIT FAILURE record → "
          f"{'PASS' if g else 'FAIL'}", flush=True)
    # G1b red path at L*
    gb = g1b_redpath(L)
    ok &= gb["ok"]
    print(f"G1b red path (jittered lattice, L = {L}): offset average moves ≤ {gb['max_shift_avg_SE']:.2f} SE, single "
          f"offset {gb['max_shift_single_SE']:.2f} SE → {'PASS' if gb['ok'] else 'FAIL'}", flush=True)
    # the rule (one code path with the sealed (B)): every verdict fires
    g = FR.rule_selftest()
    ok &= g
    print("SELFTEST", "PASS" if ok else "FAIL", flush=True)
    return ok, gb


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "selftest":
        sys.exit(0 if selftest()[0] else 1)
    elif cmd == "declare":
        declare(sys.argv[2])

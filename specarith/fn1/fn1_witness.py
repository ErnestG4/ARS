"""FN1 stage-1 witnesses (FN1_SEAL.md §5): the read's own rank_test on synthetic nine-field ladders, and a check of the
parametric power machinery (fn1_power.py) on sets whose truth is known (TOOLKIT §9.G).

Sets: mirror-symmetrised mixtures, n = 10⁶ half-points: a lattice fraction ρ_F plus i.i.d. points, so R_F ≈ 1 − ρ_F.
N = 2·10⁶, K = round(N^0.55). Arms, 200 replicates each (seeds [20261112, arm, rep]):
  null      ρ_F = 0.20 for all nine fields               → false PASS rate (should be about α; exact test)
  planted_h ρ_F = 0.20 − 0.040·(C_F − mean C)             → PASS rate
  planted_l ρ_F = 0.20 − 0.015·(C_F − mean C)             → PASS rate
  shuffled  planted_h's R with C permuted by a fixed derangement (its own ρ with the identity is −0.10) → PASS rate
Calibration: per planted arm, the parametric power at that arm's mean R ladder and the null arm's replicate SD of R
(σ), by fn1_power's method; measured and parametric PASS rates compared.
Criteria (declared before running):
  - null false PASS ≤ 6/200 (α = 0.01; binomial 99.5% bound);
  - shuffled PASS ≤ 6/200;
  - planted_h PASS ≥ 180/200;
  - |measured − parametric| ≤ 3·√(p(1−p)/200) + 0.02 for both planted arms.
WITNESS_PASS iff all four hold.

  python fn1_witness.py OUT_JSON [NPROC]
  python fn1_witness.py extra OUT_JSON [NPROC]
  python fn1_witness.py curve OUT_JSON [NPROC]

Will's pre-stamp conditions (2026-11-01).
- **(a) is not met.** planted_x's slope (0.080) was chosen as twice planted_h's, after planted_h failed. It was not set
  from FN1's target effect size, so planted_x does not replace planted_h as the must-pass witness.
- **(b) is met.** The sealed SE model's predicted power at planted_h's slope (0.040) is 0.718 (model σ 0.0264 at the
  witness K = 2921), against the measured 0.76, so the model does not overstate power.
- planted_h stays in the seal as a power-curve point, together with its bar error.

Curve run, declared before it runs:
- *Arms.* null (slope 0): 1000 replicates, new seeds (arm index 4). New slopes: 0.010 (index 5), 0.025 (6), 0.060 (7)
  and target (8), 200 replicates each. The earlier arms (0.015, 0.040, 0.080) are reused as curve points.
- *Must-pass slope (target).* Set from FN1's target effect size: FN1's seen b/σ at (10¹⁰, β 0.55) is
  0.04119/0.006120 = 6.731 per unit C. That times the witness's sealed-model σ (0.0264) gives slope = 0.1777.
- *Criteria:*
  - null PASS count in [1, 19] of 1000 (exact p < 0.01 has size 0.0086);
  - target PASS ≥ 180/200;
  - every curve point within 3·√(p(1 − p)/R) + 0.02 of the sealed-model parametric power.
  - The measured-σ parametric power is reported alongside.

Supplementary arm, added after the first run (2026-10-31; labelled, it does not replace a failed criterion).
- What failed: planted_h passed 0.76 < 0.90. The parametric power at its slope (0.040) is 0.75, and the measurement
  matched it (calib_h holds). So the criterion was set above what that slope can deliver: a witness-design error.
- planted_x: slope 0.080, 200 replicates (seed arm index 3). Declared before it runs: PASS ≥ 180/200, and
  |measured − parametric| within the same tolerance.
- Will decides whether it stands in for planted_h.
"""
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

try:
    import rq1_read as Q
except ImportError:                                   # repo layout; on spot the rq1 modules are copied alongside
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "rq1"))
    import rq1_read as Q
import rq1_witness as W
import fn1_read as FR

N_HALF = 10 ** 6
BETA = 0.55
REPS = 200
CMEAN = float(np.mean(list(FR.C.values())))
DERANGE = [4, 7, 0, 8, 1, 6, 2, 3, 5]
ARMS = ["null", "planted_h", "planted_l", "planted_x", "null_big", "s010", "s025", "s060", "target"]
TARGET = 6.731 * 0.0264                                  # FN1 b/σ at the primary cell × the witness's sealed-model σ


def gen_mix(n, rho, rng):
    m = int(round(rho * n))
    buf = np.empty(2 * n)
    Q.sorted_uniform(n - m, rng, out=buf[n:2 * n - m], scale=0.5)
    W.merge_lattice(buf[n:2 * n - m], m, buf[:n])
    W.mirror_into(buf, n)
    return buf


def one(args):
    arm, rep = args
    rng = np.random.default_rng([20261112, ARMS.index(arm), rep])
    slope = {"null": 0.0, "planted_h": 0.040, "planted_l": 0.015, "planted_x": 0.080, "null_big": 0.0, "s010": 0.010,
             "s025": 0.025, "s060": 0.060, "target": TARGET}[arm]
    N = 2 * N_HALF
    K = int(round(N ** BETA))
    R = {}
    for f in FR.FIELDS:
        th = gen_mix(N_HALF, 0.20 - slope * (FR.C[f] - CMEAN), rng)
        R[f] = float(Q.var_stream(th, K) / (N / K))
    return arm, rep, R


def main(out, nproc=8):
    counts = FR.exact_null_counts()
    rows = {"null": [], "planted_h": [], "planted_l": []}
    with ProcessPoolExecutor(nproc) as ex:
        for arm, rep, R in ex.map(one, [(a, r) for a in rows for r in range(REPS)]):
            rows[arm].append(R)
    res = dict(N=2 * N_HALF, beta=BETA, reps=REPS, arms={})
    perm_C = {f: FR.C[FR.FIELDS[DERANGE[i]]] for i, f in enumerate(FR.FIELDS)}
    rate = {}
    for arm, lst in rows.items():
        v = [FR.rank_test(R, FR.C, counts)["verdict"] for R in lst]
        rate[arm] = sum(x == "PASS" for x in v) / REPS
    rate["shuffled"] = sum(FR.rank_test(R, perm_C, counts)["verdict"] == "PASS" for R in rows["planted_h"]) / REPS
    sig = float(np.mean([np.std([R[f] for R in rows["null"]], ddof=1) for f in FR.FIELDS]))
    rng = np.random.default_rng(20261113)
    d2_crit = max(d for d in range(len(counts)) if counts[: d + 1].sum() / counts.sum() < 0.01)
    para = {}
    for arm in ("planted_h", "planted_l"):
        mu = np.array([np.mean([R[f] for R in rows[arm]]) for f in FR.FIELDS])
        sim = mu[None, :] + sig * rng.standard_normal((100000, 9))
        d2 = ((sim.argsort(1).argsort(1) - np.arange(9)) ** 2).sum(1)
        para[arm] = float((d2 <= d2_crit).mean())
    tol = {a: 3 * math.sqrt(para[a] * (1 - para[a]) / REPS) + 0.02 for a in para}
    ok = dict(null=rate["null"] <= 6 / REPS, shuffled=rate["shuffled"] <= 6 / REPS, planted_h=rate["planted_h"] >= 0.9,
              calib_h=abs(rate["planted_h"] - para["planted_h"]) <= tol["planted_h"],
              calib_l=abs(rate["planted_l"] - para["planted_l"]) <= tol["planted_l"])
    res.update(pass_rates=rate, sigma_null_replicates=sig, parametric_power=para, calib_tolerance=tol, checks=ok,
               WITNESS_PASS=all(ok.values()), derangement=DERANGE)
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print(json.dumps(dict(pass_rates=rate, parametric=para, sigma=sig, checks=ok), indent=1))
    return 0


def extra(out, nproc=8):
    counts = FR.exact_null_counts()
    with ProcessPoolExecutor(nproc) as ex:
        rows = [R for _, _, R in ex.map(one, [("planted_x", r) for r in range(REPS)])]
    base = json.load(open(out.replace("_EXTRA", "")))
    sig = base["sigma_null_replicates"]
    rate = sum(FR.rank_test(R, FR.C, counts)["verdict"] == "PASS" for R in rows) / REPS
    d2_crit = max(d for d in range(len(counts)) if counts[: d + 1].sum() / counts.sum() < 0.01)
    mu = np.array([np.mean([R[f] for R in rows]) for f in FR.FIELDS])
    sim = mu[None, :] + sig * np.random.default_rng(20261114).standard_normal((100000, 9))
    para = float((((sim.argsort(1).argsort(1) - np.arange(9)) ** 2).sum(1) <= d2_crit).mean())
    tol = 3 * math.sqrt(para * (1 - para) / REPS) + 0.02
    res = dict(label="supplementary arm planted_x (slope 0.080), added after planted_h missed its 0.90 bar", rate=rate,
               parametric=para, tol=tol, checks=dict(pass_ge_090=rate >= 0.9, calib=abs(rate - para) <= tol))
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print(json.dumps(res, indent=1))
    return 0


def model_power(slope, sig, counts, rng):
    C = np.array([FR.C[f] for f in FR.FIELDS])
    d2c = max(d for d in range(len(counts)) if counts[: d + 1].sum() / counts.sum() < 0.01)
    sim = slope * C[None, :] + sig * rng.standard_normal((200000, 9))
    return float((((sim.argsort(1).argsort(1) - np.arange(9)) ** 2).sum(1) <= d2c).mean())


def curve(out, nproc=8):
    counts = FR.exact_null_counts()
    K = int(round((2 * N_HALF) ** BETA))
    sig_model = 0.80 * math.sqrt(2 / (0.6271633049515984 * K))
    base = json.load(open(out.replace("_CURVE", "")))
    sig_meas = base["sigma_null_replicates"]
    runs = {"null_big": 1000, "s010": REPS, "s025": REPS, "s060": REPS, "target": REPS}
    rates = {}
    with ProcessPoolExecutor(nproc) as ex:
        for arm, R in runs.items():
            rows = [x for _, _, x in ex.map(one, [(arm, r) for r in range(R)])]
            rates[arm] = (sum(FR.rank_test(x, FR.C, counts)["verdict"] == "PASS" for x in rows), R)
    rates["planted_l(0.015)"] = (round(base["pass_rates"]["planted_l"] * REPS), REPS)
    rates["planted_h(0.040)"] = (round(base["pass_rates"]["planted_h"] * REPS), REPS)
    ex2 = json.load(open(out.replace("_CURVE", "_EXTRA")))
    rates["planted_x(0.080)"] = (round(ex2["rate"] * REPS), REPS)
    slopes = {"null_big": 0.0, "s010": 0.010, "planted_l(0.015)": 0.015, "s025": 0.025, "planted_h(0.040)": 0.040,
              "s060": 0.060, "planted_x(0.080)": 0.080, "target": TARGET}
    rng = np.random.default_rng(20261116)
    pts = []
    for k in sorted(slopes, key=slopes.get):
        c, R = rates[k]
        pm, pmeas = model_power(slopes[k], sig_model, counts, rng), model_power(slopes[k], sig_meas, counts, rng)
        tol = 3 * math.sqrt(max(pm * (1 - pm), 1e-4) / R) + 0.02
        pts.append(dict(arm=k, slope=slopes[k], passes=c, reps=R, rate=c / R, model_power=pm,
                        measured_sigma_power=pmeas, tol=tol, within=bool(abs(c / R - pm) <= tol)))
        print(f"{k:18s} slope {slopes[k]:.4f}  {c:4d}/{R:<4d} = {c / R:.3f}   sealed-model {pm:.3f}  "
              f"measured-sigma {pmeas:.3f}  within {abs(c / R - pm) <= tol}")
    nb = rates["null_big"][0]
    ok = dict(null_about_alpha=1 <= nb <= 19, target_must_pass=rates["target"][0] >= 180,
              curve_within=all(p["within"] for p in pts if p["slope"] > 0))
    json.dump(dict(witness_K=K, sigma_model=sig_model, sigma_measured=sig_meas, target_slope=TARGET, points=pts,
                   checks=ok, CURVE_PASS=all(ok.values())), open(out, "w"), indent=1, sort_keys=True)
    print(ok)
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "curve":
        sys.exit(curve(sys.argv[2], *(int(x) for x in sys.argv[3:4])))
    if sys.argv[1] == "extra":
        sys.exit(extra(sys.argv[2], *(int(x) for x in sys.argv[3:4])))
    sys.exit(main(sys.argv[1], *(int(x) for x in sys.argv[2:3])))

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


def gen_mix(n, rho, rng):
    m = int(round(rho * n))
    buf = np.empty(2 * n)
    Q.sorted_uniform(n - m, rng, out=buf[n:2 * n - m], scale=0.5)
    W.merge_lattice(buf[n:2 * n - m], m, buf[:n])
    W.mirror_into(buf, n)
    return buf


def one(args):
    arm, rep = args
    rng = np.random.default_rng([20261112, ["null", "planted_h", "planted_l", "planted_x"].index(arm), rep])
    slope = {"null": 0.0, "planted_h": 0.040, "planted_l": 0.015, "planted_x": 0.080}[arm]
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


if __name__ == "__main__":
    if sys.argv[1] == "extra":
        sys.exit(extra(sys.argv[2], *(int(x) for x in sys.argv[3:4])))
    sys.exit(main(sys.argv[1], *(int(x) for x in sys.argv[2:3])))

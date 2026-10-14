"""Route (a) pre-read: the GUE calibration (fortieth round). Every replicate is a full-size CUE_1000 sample for each F3
file (n_f spacings, the pre-data count; consecutive matrices concatenated), fitted exactly as the read will fit the
zeros (route_a_read.MuFit, the same model and window); expected μ̂ ≈ 0. Recorded per (replicate, file): μ̂, the
moving-block bootstrap SE at each candidate block length, χ² (GoF), and timing. Checkpointed per (replicate, file):
append + fsync; a restart skips the done keys; a torn last line is dropped. Seeds are (file index, replicate).

  python route_a_calib.py run R0 R1 OUT.jsonl [BETA]     replicates R0..R1−1 (BETA = 2 is CUE; other β = red paths)
  python route_a_calib.py summary OUT.jsonl [...]        bias, spread, SE coverage per block length, χ² null quantiles
  python route_a_calib.py declare DECL.json OUT.jsonl [...]   the forty-first-round declaration (route_a_read docstring):
        BLOCK, per-file bias b_f, spread SD_f, R_f, GoF threshold T_f (scaled χ², 1% family-wise), the empirical
        family-wise misfit rate, and the rule's operating characteristics on the joint replicates:
        false-fail  = P(verdict ≠ PASS) with every μ̂_f shifted by +1 (round 40's assumption: μ = 1 correlations ≈ μ = 0),
        power       = P(verdict = FAIL) unshifted (truth μ = 0),
        and, descriptive only, P(verdict ≠ PASS) under per-file shifts to Phase 2's fitted-SECONDARY equivalent μ*
        (route_a_equiv.json; μ-condition only, its χ² misfit is not simulated).
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cbe  # noqa: E402
import route_a_read as RR  # noqa: E402

N_MAT = 1000                       # fortieth round: N ≥ 10³ per block
BLOCK_LENS = RR.BLOCK_LENS
CHUNK = 2000                       # matrices per GPU call


def cue_spacings(rng, n, beta=2.0, gpu=True):
    """n consecutive spacings from independent CβE_1000 matrices (Killip–Nenciu sampler), concatenated."""
    need = -(-n // N_MAT)
    out = []
    while need > 0:
        k = min(CHUNK, need)
        th, _ = cbe.sample(rng, k, N_MAT, beta, gpu=gpu)
        out.append(cbe.spacings(th).ravel())
        need -= k
    return np.concatenate(out)[:n]


def done_keys(path):
    keys, good = set(), []
    if os.path.exists(path):
        lines = open(path).read().split("\n")
        for ln in lines:
            if not ln.strip():
                continue
            try:
                r = json.loads(ln)
            except json.JSONDecodeError:          # torn last line
                continue
            keys.add((r["rep"], r["file"], r["beta"]))
            good.append(ln)
        with open(path, "w") as fh:               # rewrite without a torn line
            fh.write("".join(x + "\n" for x in good))
    return keys


def run(r0, r1, out, beta=2.0):
    pred = json.load(open(RR.PRED))
    _, n = RR.weights()
    fits = {f: RR.MuFit.for_file(f, pred) for f in RR.F3}
    done = done_keys(out)
    files = list(RR.F3)
    for rep in range(r0, r1):
        for i, f in enumerate(files):
            if (rep, f, beta) in done:
                continue
            t = time.time()
            rng = np.random.default_rng([20261013, i, rep, int(round(beta * 1000))])
            s = cue_spacings(rng, int(round(n[f])), beta)
            t1 = time.time()
            res = RR.fit_file(fits[f], s, rng, BLOCK_LENS)
            res.update(rep=rep, file=f, beta=beta, t_sample=round(t1 - t, 1), t_fit=round(time.time() - t1, 1))
            with open(out, "a") as fh:
                fh.write(json.dumps(res) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            print(f"rep {rep} {f}: μ̂ {res['mu']:+.4f} SE(1000) {res['se'][1000]:.4f} χ² {res['chi2']:.1f} "
                  f"({res['t_sample']}+{res['t_fit']} s)", flush=True)


def load(paths, beta=2.0):
    rows = {}
    for p in paths:
        for ln in open(p):
            if ln.strip():
                r = json.loads(ln)
                if r["beta"] == beta:
                    rows[(r["rep"], r["file"])] = r
    return rows


def summary(paths):
    rows = load(paths)
    files = list(RR.F3)
    out = {}
    for f in files:
        R = [r for (rep, ff), r in sorted(rows.items()) if ff == f]
        mu = np.array([r["mu"] for r in R])
        sd = float(mu.std(ddof=1))
        se = {L: float(np.mean([r["se"][str(L)] if str(L) in r["se"] else r["se"][L] for r in R])) for L in BLOCK_LENS}
        chi = np.array([r["chi2"] for r in R])
        out[f] = dict(n_rep=len(R), mu_mean=float(mu.mean()), mu_mean_se=sd / math.sqrt(len(R)), mu_sd=sd,
                      se_mean=se, se_over_sd={L: se[L] / sd for L in BLOCK_LENS},
                      chi2_mean=float(chi.mean()), chi2_var=float(chi.var(ddof=1)),
                      chi2_q=dict(zip(("50", "90", "99", "max"), map(float, np.percentile(chi, [50, 90, 99, 100])))))
        v = out[f]
        print(f"{f}: R={v['n_rep']}  μ̂ mean {v['mu_mean']:+.5f} ± {v['mu_mean_se']:.5f}  SD {sd:.5f}  "
              + "  ".join(f"SE{L}/SD {v['se_over_sd'][L]:.3f}" for L in BLOCK_LENS)
              + f"  χ² mean {v['chi2_mean']:.1f} var {v['chi2_var']:.1f} q99 {v['chi2_q']['99']:.1f}", flush=True)
    return out


def scaled_chi2_quantile(x, q):
    """q-quantile of a·χ²_ν with a, ν matched to the sample mean and variance of x."""
    from scipy.stats import chi2
    m, v = float(np.mean(x)), float(np.var(x, ddof=1))
    a, nu = v / (2 * m), 2 * m * m / v
    return float(a * chi2.ppf(q, nu)), a, nu


def declare(out, paths, equiv=os.path.join(HERE, "results", "route_a_equiv.json")):
    rows = load(paths)
    files = list(RR.F3)
    reps = sorted({rep for rep, _ in rows})
    joint = [r for r in reps if all((r, f) in rows for f in files)]
    if len(joint) != len(reps):
        raise RuntimeError(f"declare: {len(reps) - len(joint)} replicates incomplete")
    sd = {f: float(np.std([rows[(r, f)]["mu"] for r in joint], ddof=1)) for f in files}
    se_mean = {f: {L: float(np.mean([rows[(r, f)]["se"][str(L)] for r in joint])) for L in BLOCK_LENS} for f in files}
    ratio = {L: float(np.exp(np.mean([np.log(se_mean[f][L] / sd[f]) for f in files]))) for L in BLOCK_LENS}
    ok = [L for L in BLOCK_LENS if ratio[L] >= RR.BLOCK_SE_RATIO]
    block = min(ok) if ok else max(BLOCK_LENS)            # declared fallback; SE_f ≥ SD_f holds regardless
    a1 = 1 - (1 - RR.GOF_FAMILYWISE) ** (1 / len(files))
    cal = dict(block=block, block_fallback=not ok, se_over_sd_geomean=ratio, alpha_per_file=a1,
               familywise=RR.GOF_FAMILYWISE, R=len(joint), files={})
    for f in files:
        mu = np.array([rows[(r, f)]["mu"] for r in joint])
        chi = np.array([rows[(r, f)]["chi2"] for r in joint])
        T, a, nu = scaled_chi2_quantile(chi, 1 - a1)
        cal["files"][f] = dict(bias=float(mu.mean()), bias_z=float(mu.mean() / (sd[f] / math.sqrt(len(mu)))),
                               sd=sd[f], R=len(mu), se_boot_mean=se_mean[f], T=T, chi2_scale=a, chi2_dof=nu,
                               chi2_mean=float(chi.mean()), chi2_emp_q90=float(np.percentile(chi, 90)),
                               chi2_fit_q90=scaled_chi2_quantile(chi, 0.90)[0],
                               chi2_emp_q99=float(np.percentile(chi, 99)),
                               chi2_fit_q99=scaled_chi2_quantile(chi, 0.99)[0])
    w, _ = RR.weights()
    nflag = np.array([sum(rows[(r, f)]["chi2"] > cal["files"][f]["T"] for f in files) for r in joint])
    cal["empirical_familywise_misfit"] = float(np.mean(nflag >= 1))
    cal["empirical_model_misfit_verdict"] = float(np.mean(nflag >= RR.MISFIT_FILES))
    mustar = {}
    if os.path.exists(equiv):
        E = json.load(open(equiv))["files"]
        mustar = {f: E[f]["mu"]["fit_sec: Phase 2 SECONDARY fitted (interp.)"] for f in files}

    def verdicts(shift):
        out = []
        for r in joint:
            pf = {f: dict(rows[(r, f)], mu=rows[(r, f)]["mu"] + shift[f]) for f in files}
            out.append(RR.rule(pf, w, cal)["verdict"])
        return out

    v1 = verdicts({f: 1.0 for f in files})
    v0 = verdicts({f: 0.0 for f in files})
    oc = dict(false_fail=float(np.mean([v != "PASS" for v in v1])), verdicts_mu1={v: v1.count(v) for v in set(v1)},
              power_mu0=float(np.mean([v == "FAIL" for v in v0])), verdicts_mu0={v: v0.count(v) for v in set(v0)})
    if mustar:
        vs = verdicts(mustar)
        oc["descriptive_not_pass_at_fit_sec_mustar"] = float(np.mean([v != "PASS" for v in vs]))
        oc["fit_sec_mustar"] = mustar
    cal["operating_characteristics"] = oc
    json.dump(cal, open(out, "w"), indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in cal.items() if k != "files"}, indent=1))
    for f in files:
        c = cal["files"][f]
        print(f"{f}: b {c['bias']:+.5f} (z {c['bias_z']:+.2f})  SD {c['sd']:.5f}  T {c['T']:.1f}  "
              f"q90 emp/fit {c['chi2_emp_q90']:.1f}/{c['chi2_fit_q90']:.1f}  q99 {c['chi2_emp_q99']:.1f}/{c['chi2_fit_q99']:.1f}")
    return cal


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], float(sys.argv[5]) if len(sys.argv) > 5 else 2.0)
    elif sys.argv[1] == "summary":
        summary(sys.argv[2:])
    elif sys.argv[1] == "declare":
        declare(sys.argv[2], sys.argv[3:])

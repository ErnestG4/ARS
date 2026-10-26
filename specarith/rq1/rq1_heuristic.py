"""RQ1 seal (B) amendments (round 86): the B2 heuristic offset, the SE at each β, and B1's basis. No archive data used.

Heuristic (RW §5 form, field entering only through the analytic-conductor constant C_F, log q_F(k) = 2 log|k| + C_F):
    R_F(K, X) = K · Σ_{k≠0} sin²(πk/K)/(πk)² · min(1, (2 log|k| + C_F)/L),   L = log X (variant: L = log N)
C_ℤ[√2] = log(8π²/log²ε) = 4.6214, C_ℤ[i] = log 16 = 2.7726. B2 offset = R_ℤ[√2] − R_ℤ[i] at matched N and β.

SE model: the sliding-window estimator's relative SD is sqrt(2/(c·K)); c is calibrated by Monte Carlo on uniform
i.i.d. (Poisson-like) and CUE (rigid) points, and the smaller c (larger SE) is used. SE_diff = sqrt(SE_√2² + SE_i²)
(independent fields). β is "powered" for B2 iff heuristic offset ≥ 2·SE_diff.

Round 88: both archives are mirror-symmetric (each split prime gives θ and 1 − θ), so c is recalibrated on
symmetrised sets (n/2 points plus their mirrors at 1 − θ, Poisson and CUE_{n/2}), and c_used is the smallest
symmetrised c. The unsymmetrised calibration is kept in the output for comparison. N is the archives' matched N
(2 × the ℤ[√2] manifest row count at each X; row counts only, no angle), so K matches the read exactly.

  python rq1_heuristic.py OUT_JSON [--mirror]
"""
import json
import math
import sys

import numpy as np

import rq1_angles as R

LOGEPS = math.log(1 + math.sqrt(2))
C = {"zs2": math.log(8 * math.pi ** 2 / LOGEPS ** 2), "zi": math.log(16.0)}
BETAS = [0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90]
XS = {"1e10": 1e10, "1e11": 1e11}


def n_ideals(X):
    """≈ number of prime ideals above split primes with norm ≤ X (both ideals): li(X) to leading order."""
    from mpmath import li
    return float(li(X)) - float(li(2))


def R_heur(K, L, Cf):
    """K·Σ_{k≠0} w_k f_k with Σ_{k≠0} w_k = (1/K)(1 − 1/K) and f_k = 1 beyond k* = exp((L − C_F)/2): only k ≤ k*
    needs an explicit sum, R = (1 − 1/K) + 2K·Σ_{1≤k≤k*} w_k (f_k − 1)."""
    kstar = int(math.exp((L - Cf) / 2)) + 1
    k = np.arange(1, kstar + 1, dtype=np.float64)
    w = np.sin(math.pi * k / K) ** 2 / (math.pi * k) ** 2
    f = np.minimum(1.0, (2 * np.log(k) + Cf) / L)
    return (1 - 1 / K) + 2 * K * float(np.sum(w * (f - 1)))


N_MATCHED = {"1e10": 2 * 227524967, "1e11": 2 * 2059026114}     # 2 × ℤ[√2] manifest rows ≤ X (round 88)


def cue_phases(rng, n):
    z = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / math.sqrt(2)
    q, r = np.linalg.qr(z)
    q = q * (np.diag(r) / np.abs(np.diag(r)))
    return np.mod(np.angle(np.linalg.eigvals(q)) / (2 * math.pi), 1.0)


def calib_c(rng, mirror=False):
    """mirror: draw n/2 points and add their mirrors 1 − θ (the archives' structure)."""
    out = {}
    for name, n, Ks, M in (("poisson", 20000, (20, 50, 200), 400), ("cue", 400, (8, 20, 50), 300)):
        res = {}
        for K in Ks:
            vals = []
            for _ in range(M):
                m = n // 2 if mirror else n
                th = rng.random(m) if name == "poisson" else cue_phases(rng, m)
                if mirror:
                    th = np.concatenate([th, np.mod(1.0 - th, 1.0)])
                vals.append(R.var_exact(th, K) / (n / K))
            vals = np.array(vals)
            rel = vals.std(ddof=1) / vals.mean()
            res[K] = dict(mean=float(vals.mean()), rel_sd=float(rel), c=float(2 / (K * rel ** 2)))
        out[name] = res
    return out


def main(out, mirror=False):
    rng = np.random.default_rng(8686)
    cal = calib_c(rng)
    res = dict(C=C, c_calibration=cal, rows={})
    if mirror:
        cal_m = calib_c(np.random.default_rng(8888), mirror=True)
        res["c_calibration_mirror"] = cal_m
        c_use = min(v["c"] for d in cal_m.values() for v in d.values())
    else:
        c_use = min(v["c"] for d in cal.values() for v in d.values())
    res["c_used"] = c_use
    for xl, X in XS.items():
        N = N_MATCHED[xl] if mirror else n_ideals(X)
        rows = []
        for b in BETAS:
            K = int(round(N ** b))
            r = {}
            for lname, L in (("logX", math.log(X)), ("logN", math.log(N))):
                rs2, ri = R_heur(K, L, C["zs2"]), R_heur(K, L, C["zi"])
                r[lname] = dict(R_zs2=rs2, R_zi=ri, offset=rs2 - ri)
            se = lambda Rv: Rv * math.sqrt(2 / (c_use * K))
            sed = math.sqrt(se(r["logX"]["R_zs2"]) ** 2 + se(r["logX"]["R_zi"]) ** 2)
            off = min(r["logX"]["offset"], r["logN"]["offset"])
            rows.append(dict(beta=b, K=K, heuristic=r, SE_diff=sed, offset_over_SE=off / sed,
                             B2_powered=bool(b <= 0.45 and off >= 2 * sed)))
        res["rows"][xl] = dict(N=N, rows=rows)
    json.dump(res, open(out, "w"), indent=1)
    for xl, d in res["rows"].items():
        print(xl, "N %.3e" % d["N"])
        for r in d["rows"]:
            h = r["heuristic"]
            print("  β %.2f K %10d  R√2 %.3f Ri %.3f off(logX) %+.3f off(logN) %+.3f SEdiff %.3f off/SE %.1f %s" % (
                r["beta"], r["K"], h["logX"]["R_zs2"], h["logX"]["R_zi"], h["logX"]["offset"], h["logN"]["offset"],
                r["SE_diff"], r["offset_over_SE"], "powered" if r["B2_powered"] else ""))
    for key in ("c_calibration", "c_calibration_mirror"):
        if key in res:
            print(key, {k: {K: (round(v["mean"], 3), round(v["c"], 2)) for K, v in d.items()} for k, d in res[key].items()})
    print("used", round(c_use, 3))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], "--mirror" in sys.argv[2:]))

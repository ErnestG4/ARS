"""RQ1-c witnesses for P1, P3 and P4 (round 97). Synthetic only; reduced N = 10⁹ (allowed: block-SE check PASS, cb40744d),
except P4's 10¹⁰ sets at the actual 10¹⁰ matched N. K values are the read's: K = round(N_X^β) at each X's matched N
(N₁₂ = 2·1.880·10¹⁰ until the ℤ[√2] 10¹² manifest gives the row count). Every set is mirror-symmetric (n on [0, ½] plus
mirrors). Estimator: rq1_read.var_stream. CRITERIA (declared here, committed before running):

P1 (B2 T rule at the 10¹² cells β 0.40, 0.45). NULL: two i.i.d. sets. PLANTED: the round-88 recipe at the 10¹² matched
  N: ρ_zi = 1 − (largest heuristic R_zi over the two cells and both L), ρ_zs2 = ρ_zi − ΔR, ΔR = the smallest heuristic
  offset (min of L = log X, log N) over the two cells. Selection on 100 + 100 (seed base 9800): SE check and s_c as
  round 89 (ratio > 1.2 → s = ratio, cells < 2 dropped), t = 2·RMS(T_null); bars null false PASS ≤ 5, planted PASS
  ≥ 90. Confirmation on 100 + 100 fresh (9801) at the frozen t, same bars.
P3 (crossover location in [0.51, 0.54]). Residual r(β) = R_A(K) − R_B(aK) on β = 0.45, …, 0.65 (step 0.01), the first
  ≤ 0 → > 0 sign change located by linear interpolation; PASS iff it lies in [0.51, 0.54]; no crossing → FAIL.
  A: jittered lattice σ_A; B: two-scale jittered lattice (half the points at σ₁, half at σ₂) with a·σ₁ = σ_A e^{−s},
  a·σ₂ = σ_A e^{+s}: r changes sign once, at the inflection of f(log x) placed at β*; s sets the slope so that the
  model resolution SE_r/|slope| equals 0.0029 (the expected 10¹² value, RQ1C_POWER.json). Arms (100 each, seed 9810):
  IN (β* = 0.525) must PASS ≥ 90; LOW (β* = 0.50) and HIGH (β* = 0.555) must FAIL ≥ 90 each; NULL (two flat mixtures,
  R 0.80 and 0.85, no crossing) must FAIL ≥ 90.
P4 (ordering R_ℤ√2 > R_ℤω > R_ℤi at β = 0.55 at 10¹⁰, 10¹¹, 10¹²). Three mixture sets per X. NULL: equal R (the
  ℤ[i] level); PLANTED: R_I, R_I + 0.283·D, R_I + D with D = 0.0761, 0.0640, 0.0598 (data at 10¹⁰, 10¹¹; the 1/log X
  law at 10¹²) and R_I = 0.790, 0.817, 0.82. 100 + 100 (seed 9820): null false PASS ≤ 5, planted PASS ≥ 90.
A witness that fails its bars: report and stop (no automatic redesign).

  python rq1c_witness.py jobs P                       (P = p1sel, p1conf, p3, p4)
  python rq1c_witness.py task P ARM REP OUT_DIR
  python rq1c_witness.py summary P OUT_DIR OUT_JSON [SELECTION_JSON]
"""
import json
import math
import os
import sys
import time

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.stats import norm

import rq1_heuristic as H
import rq1_read as Q
import rq1_witness as W

N_RED = 10 ** 9
N12 = 2 * 1.880e10
N10, N11 = 2 * 227524967, 2 * 2059026114
A = math.pi / (math.sqrt(2) * math.log(1 + math.sqrt(2)))
P3_GRID = [round(0.45 + 0.01 * i, 2) for i in range(21)]
P3_STAR = {"in": 0.525, "low": 0.50, "high": 0.555}
P3_RES = 0.0029
P4_X = {"1e10": (N10, 0.0761, 0.790), "1e11": (N11, 0.0640, 0.817), "1e12": (N12, 0.0598, 0.82)}
FRAC = 0.283
NREP = 100


def K_of(N, b):
    return int(round(N ** b))


# ---- set generators (mirror-symmetric, sorted, length 2n) ----
def _mix(n, rho, rng):
    m = int(round(rho * n))
    buf = np.empty(2 * n)
    if m:
        Q.sorted_uniform(n - m, rng, out=buf[n:2 * n - m], scale=0.5)
        W.merge_lattice(buf[n:2 * n - m], m, buf[:n])
    else:
        Q.sorted_uniform(n, rng, out=buf[:n], scale=0.5)
    W.mirror_into(buf, n)
    return buf


def jit(n, sig1, sig2, rng):
    """Jittered lattice; lattice point j gets σ₁ (j even) or σ₂ (j odd), so R = ½f(Kσ₁) + ½f(Kσ₂) exactly (random labels
    would add the labels' own variance: tested at N = 10⁹, B came out 2–3% above that), folded into [0, ½]."""
    buf = np.empty(2 * n)
    x = buf[:n]
    x[:] = (np.arange(n) + 0.5) / (2 * n)
    s = np.where(np.arange(n) % 2 == 0, sig1, sig2) if sig1 != sig2 else sig1
    x += s * rng.standard_normal(n)
    np.abs(x, out=x)
    np.minimum(x, 1.0 - x, out=x)
    x.sort()
    W.mirror_into(buf, n)
    return buf


def R_of(th, K):
    return Q.var_stream(th, float(K)) / (len(th) / K)


# ---- the exact jittered-lattice R(Kσ) and the P3 calibration ----
def f_jit(x):
    """R of a dense jittered lattice at Kσ = x: x·∫ p(1 − p) du, p(u) = Φ(1/(2x) − u) − Φ(−1/(2x) − u)."""
    h = 0.5 / x
    g = lambda u: (lambda p: p * (1 - p))(norm.cdf(h - u) - norm.cdf(-h - u))
    return x * quad(g, -h - 12, h + 12, limit=400)[0]


def p3_params(beta_star):
    """σ_A, σ₁, σ₂ (absolute θ units): crossing at β*, model resolution P3_RES."""
    lnN = math.log(N12)
    # inflection of f in ln x
    d2 = lambda y: (f_jit(math.exp(y + 1e-3)) - 2 * f_jit(math.exp(y)) + f_jit(math.exp(y - 1e-3))) / 1e-6
    y0 = brentq(d2, -2.0, 2.0)
    K = K_of(N12, beta_star)
    sA = math.exp(y0) / K

    def resid(b, s):
        x = K_of(N12, b) * sA
        return f_jit(x) - 0.5 * (f_jit(x * math.exp(-s)) + f_jit(x * math.exp(s)))

    def resolution(s):
        slope = (resid(beta_star + 0.005, s) - resid(beta_star - 0.005, s)) / 0.01
        RA = f_jit(K * sA)
        se = math.hypot(RA * math.sqrt(2 / (Q.C_SE * K)), RA * math.sqrt(2 / (Q.C_SE * A * K)))
        return se / slope
    s = brentq(lambda s: resolution(s) - P3_RES, 0.05, 3.0)
    return dict(beta_star=beta_star, y_inflection=y0, sigma_A=sA, sigma_1=sA * math.exp(-s) / A,
                sigma_2=sA * math.exp(s) / A, s=s, R_A_at_star=f_jit(K * sA), resolution=resolution(s), lnN12=lnN)


def p1_params():
    rows = []
    for b in (0.40, 0.45):
        K = K_of(N12, b)
        r = {}
        for nm, L in (("logX", math.log(1e12)), ("logN", math.log(N12))):
            rs2, rzi = H.R_heur(K, L, H.C["zs2"]), H.R_heur(K, L, H.C["zi"])
            r[nm] = dict(R_zs2=rs2, R_zi=rzi, offset=rs2 - rzi)
        rows.append((b, K, r))
    dR = min(min(v["offset"] for v in r.values()) for _, _, r in rows)
    rzi = max(max(v["R_zi"] for v in r.values()) for _, _, r in rows)
    return dict(rho_zi=1 - rzi, rho_zs2=1 - rzi - dR, dR=dR, cells=[(b, K) for b, K, _ in rows])


# ---- tasks ----
def task(P, arm, rep, out_dir):
    path = os.path.join(out_dir, f"{arm}_{rep:03d}.json")
    if os.path.exists(path):
        return 0
    t0 = time.time()
    n = N_RED // 2
    res = dict(P=P, arm=arm, rep=rep)
    if P in ("p1sel", "p1conf"):
        rng = np.random.default_rng([9800 if P == "p1sel" else 9801, 0 if arm == "null" else 1, rep])
        pp = p1_params()
        res["sets"] = {}
        for f in ("zs2", "zi"):
            rho = 0.0 if arm == "null" else pp["rho_zs2" if f == "zs2" else "rho_zi"]
            th = _mix(n, rho, rng)
            res["sets"][f] = {str(b): dict(K=K, R=R_of(th, K)) for b, K in pp["cells"]}
            del th
    elif P == "p3":
        rng = np.random.default_rng([9810, ["in", "low", "high", "null"].index(arm), rep])
        if arm == "null":
            thA, thB = _mix(n, 0.20, rng), None
        else:
            pp = p3_params(P3_STAR[arm])
            thA = jit(n, pp["sigma_A"], pp["sigma_A"], rng)
        RA = [R_of(thA, K_of(N12, b)) for b in P3_GRID]
        del thA
        thB = _mix(n, 0.15, rng) if arm == "null" else jit(n, pp["sigma_1"], pp["sigma_2"], rng)
        RB = [R_of(thB, A * K_of(N12, b)) for b in P3_GRID]
        res.update(RA=RA, RB=RB, resid=[a - b for a, b in zip(RA, RB)])
    elif P == "p4":
        rng = np.random.default_rng([9820, 0 if arm == "null" else 1, rep])
        res["X"] = {}
        for xl, (N, D, RI) in P4_X.items():
            nn = min(N, N_RED) // 2
            K = K_of(N, 0.55)
            lv = {"I": RI, "W": RI if arm == "null" else RI + FRAC * D, "A": RI if arm == "null" else RI + D}
            out = {}
            for k, R in lv.items():
                th = _mix(nn, 1 - R, rng)
                out[k] = R_of(th, K)
                del th
            res["X"][xl] = dict(K=K, R=out)
    res["cpu_s"] = time.process_time()
    res["wall_s"] = time.time() - t0
    tmp = path + f".{os.getpid()}.part"
    json.dump(res, open(tmp, "w"))
    os.replace(tmp, path)
    print(P, arm, rep, round(res["cpu_s"], 1), flush=True)
    return 0


def jobs(P):
    arms = {"p1sel": ["null", "planted"], "p1conf": ["null", "planted"], "p3": ["in", "low", "high", "null"],
            "p4": ["null", "planted"]}[P]
    for r in range(NREP):
        for a in arms:
            print(a, r)


# ---- summaries ----
def p3_locate(resid):
    for i in range(len(P3_GRID) - 1):
        if resid[i] <= 0 < resid[i + 1]:
            return P3_GRID[i] + (P3_GRID[i + 1] - P3_GRID[i]) * (-resid[i]) / (resid[i + 1] - resid[i])
    return None


def p1_TD(rep, cells, scale):
    D, SE = {}, {}
    for b, K in cells:
        a, c = rep["sets"]["zs2"][str(b)]["R"], rep["sets"]["zi"][str(b)]["R"]
        D[b], SE[b] = a - c, Q.se_diff(a, c, K)
    T = sum(D[b] / (scale[b] * SE[b]) for b, _ in cells)
    guard = all(D[b] >= -2 * scale[b] * SE[b] for b, _ in cells)
    return T, guard, D, SE


def summary(P, out_dir, out, sel=None):
    load = lambda arm: [json.load(open(os.path.join(out_dir, f"{arm}_{r:03d}.json"))) for r in range(NREP)]
    res = dict(P=P, reps=NREP)
    if P in ("p1sel", "p1conf"):
        pp = p1_params()
        cells = pp["cells"]
        nul, pla = load("null"), load("planted")
        if P == "p1sel":
            ratios = {}
            for b, K in cells:
                r = 0.0
                for reps in (nul, pla):
                    d = [p1_TD(x, cells, {c: 1.0 for c, _ in cells}) for x in reps]
                    Dv = np.array([q[2][b] for q in d])
                    r = max(r, Dv.std(ddof=1) / np.mean([q[3][b] for q in d]))
                ratios[b] = float(r)
            trig = any(v > 1.2 for v in ratios.values())
            scale = {b: (ratios[b] if trig else 1.0) for b, _ in cells}
            Tn = np.array([p1_TD(x, cells, scale)[0] for x in nul])
            t = float(2 * math.sqrt((Tn ** 2).mean()))
            res.update(params=pp, se_ratio=ratios, se_check_triggered=trig, scale=scale, t=t,
                       T_null_mean=float(Tn.mean()), T_null_sd_centred=float(Tn.std(ddof=1)))
        else:
            s = json.load(open(sel))
            t, scale = s["t"], {float(k): v for k, v in s["scale"].items()}
            res.update(t=t, scale=scale, selection_file=sel)
        cnt = lambda reps: int(sum((lambda T, g, *_: T > t and g)(*p1_TD(x, cells, scale)) for x in reps))
        res.update(null_false_pass=cnt(nul), planted_pass=cnt(pla))
        res["OK"] = bool(res["null_false_pass"] <= 5 and res["planted_pass"] >= 90)
    elif P == "p3":
        arms = {}
        for arm in ("in", "low", "high", "null"):
            locs = [p3_locate(x["resid"]) for x in load(arm)]
            pas = [l is not None and 0.51 <= l <= 0.54 for l in locs]
            good = sum(pas) if arm == "in" else len(pas) - sum(pas)
            fl = [l for l in locs if l is not None]
            arms[arm] = dict(pass_count=int(sum(pas)), correct=int(good), ok=bool(good >= 90),
                             loc_mean=float(np.mean(fl)) if fl else None, loc_sd=float(np.std(fl, ddof=1)) if len(fl) > 1 else None,
                             no_crossing=int(sum(l is None for l in locs)),
                             params=None if arm == "null" else p3_params(P3_STAR[arm]))
        res.update(arms=arms, OK=bool(all(v["ok"] for v in arms.values())))
    elif P == "p4":
        def ok(x):
            return all(v["R"]["A"] > v["R"]["W"] > v["R"]["I"] for v in x["X"].values())
        nul, pla = load("null"), load("planted")
        res.update(null_false_pass=int(sum(ok(x) for x in nul)), planted_pass=int(sum(ok(x) for x in pla)))
        res["OK"] = bool(res["null_false_pass"] <= 5 and res["planted_pass"] >= 90)
    res["cpu_core_h"] = float(sum(x["cpu_s"] for arm in os.listdir(out_dir) if arm.endswith(".json") and arm[0] != "S"
                                  for x in [json.load(open(os.path.join(out_dir, arm)))]) / 3600)
    json.dump(res, open(out, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k not in ("arms", "params")}, default=str))
    if P == "p3":
        for a, v in res["arms"].items():
            print(a, v["correct"], v["loc_mean"], v["loc_sd"], v["no_crossing"])
    return 0


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "jobs":
        jobs(sys.argv[2])
    elif c == "task":
        sys.exit(task(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]))
    elif c == "summary":
        sys.exit(summary(sys.argv[2], sys.argv[3], sys.argv[4], *(sys.argv[5:6])))
    elif c == "params":
        print(json.dumps(dict(p1=p1_params(), p3={k: p3_params(v) for k, v in P3_STAR.items()}), indent=1))

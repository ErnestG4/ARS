"""GEO-CM1 analysis, exactly as GEOCM1_SEAL.md §§3–5 and geocm1.py's gate tolerances (committed before any result).

  python geocm1_analyze.py gates RESULTS_DIR OUT_JSON       golden, silver, cusp, K = 0.5 witness, quintic (descriptive)
  python geocm1_analyze.py read RESULTS_DIR OUT_JSON        a = 1 … 10: per-a estimates and the sealed clauses (after
                                                            the seal's attestation; a ≥ 3 files exist only then)
Per path: levels with 10 ≤ q (all levels for the K = 0.5 witness); a level counts only while both precisions' widths
agree to ≤ 10⁻⁶ relative and the saddle-node Newton edges agree with bisection to ≤ 10⁻³ of the width.
f_n = ln(w_n/w_{n+1}) / (2 ln(q_{n+1}/q_n)); δ_n = w_n/w_{n+1}. Estimate = Aitken on the last three; SE = |Aitken(last
three) − Aitken(the three before)| (≥ 4 values). Gates: golden / silver within 3·SE and within 6·10⁻⁴ (f absolute, |δ|
relative). Cusp: f_N for N = 24 … 199, least-squares f_N = f∞ + c₁x + c₂x², x = 1/ln N, gate |f∞ − 1.5| ≤ 0.02.
K = 0.5 must-fail: f_n increasing at each of the last three steps and the last f_n > 3. Quintic: |f̂ − 1.0822| > 5·SE,
descriptive. Read: SUPPORT / CONTRADICT / UNPOWERED at ±2·SE (pairs: SE_d = √(SE_a² + SE_{a+1}²)); f(∞): weighted
the f(∞) clause is replaced by the h_a clause (re-gate), UNPOWERED because the cusp form was not validated on fresh N;
h_a reported descriptively.
"""
import json
import math
import os
import sys

import numpy as np

LIT = {"a1": (1.0822, 2.833612), "a2": (1.0874, 6.79924)}


def aitken(s):
    s1, s2, s3 = s[-3:]
    den = (s3 - s2) - (s2 - s1)
    return s3 if den == 0 else s3 - (s3 - s2) ** 2 / den


def est(seq):
    if len(seq) < 3:
        return None, None
    a = aitken(seq)
    se = abs(a - aitken(seq[:-1])) if len(seq) >= 4 else None
    return a, se


def levels(d, qmin=10):
    runs = d["runs"]
    keys = sorted(runs, key=int)
    ref = runs[keys[0]]
    out, stop = [], None
    for i, lv in enumerate(ref):
        if lv["q"] < qmin:
            continue
        w = float(lv["w"])
        ok_n = lv["newton_agree_rel"] is not None and lv["newton_agree_rel"] <= 1e-3
        ok_p = all(abs(float(runs[k][i]["w"]) / w - 1) <= 1e-6 for k in keys[1:]) if len(keys) > 1 else True
        if not (ok_n and ok_p):
            stop = dict(q=lv["q"], newton_ok=ok_n, precision_ok=ok_p)
            break
        out.append((lv["q"], w, lv["fixes"], lv["edge_tol_rel"]))
    return out, stop


def path_stats(d, qmin=10):
    lv, stop = levels(d, qmin)
    f = [math.log(lv[i][1] / lv[i + 1][1]) / (2 * math.log(lv[i + 1][0] / lv[i][0])) for i in range(len(lv) - 1)]
    dl = [lv[i][1] / lv[i + 1][1] for i in range(len(lv) - 1)]
    fh, fse = est(f)
    dh, dse = est(dl)
    return dict(levels=[dict(q=q, w=w, fixes=fx, edge_tol_rel=et) for q, w, fx, et in lv], stopped_at=stop,
                f_n=f, delta_n=dl, f_hat=fh, f_SE=fse, delta_hat=dh, delta_SE=dse,
                bracket_fixes=int(sum(x[2] for x in lv)))


def load(dirn, name):
    p = os.path.join(dirn, f"GATE_{name}.json")
    if not os.path.exists(p):
        p = os.path.join(dirn, f"READ_{name}.json")
    return json.load(open(p))


def gates(dirn, out):
    res = {}
    for a in ("a1", "a2"):
        s = path_stats(load(dirn, a))
        fl, dlit = LIT[a]
        ok_f = s["f_SE"] is not None and abs(s["f_hat"] - fl) <= 3 * s["f_SE"] and abs(s["f_hat"] - fl) <= 6e-4
        ok_d = s["delta_SE"] is not None and abs(s["delta_hat"] - dlit) <= 3 * s["delta_SE"] and abs(s["delta_hat"] / dlit - 1) <= 6e-4
        s.update(literature=dict(f=fl, delta=dlit), gate_f=bool(ok_f), gate_delta=bool(ok_d), GATE=bool(ok_f and ok_d))
        res[a] = s
    c = load(dirn, "cusp")
    lv, stop = levels(c, qmin=2)
    w = {q: wv for q, wv, _, _ in lv}
    fN = {N: math.log(w[N] / w[N + 1]) / (2 * math.log((N + 1) / N)) for N in range(2, 200) if N in w and N + 1 in w}
    Ns = [N for N in fN if N >= 24]
    X = np.array([[1, 1 / math.log(N), 1 / math.log(N) ** 2] for N in Ns])
    y = np.array([fN[N] for N in Ns])
    coef, res_, _, _ = np.linalg.lstsq(X, y, rcond=None)
    dof = len(Ns) - 3
    s2 = float(np.sum((X @ coef - y) ** 2) / dof) if dof > 0 else float("nan")
    cov = s2 * np.linalg.inv(X.T @ X)
    res["cusp"] = dict(f_N={str(k): v for k, v in fN.items()}, fit_N=[min(Ns), max(Ns)], f_inf=float(coef[0]),
                       f_inf_SE=float(math.sqrt(cov[0, 0])), c1=float(coef[1]), c2=float(coef[2]), stopped_at=stop,
                       GATE=bool(abs(coef[0] - 1.5) <= 0.02), bracket_fixes=int(sum(x[2] for x in lv)))
    s = path_stats(load(dirn, "sub05"), qmin=1)
    f = s["f_n"]
    must_fail = len(f) >= 4 and all(f[-i] > f[-i - 1] for i in (1, 2, 3)) and f[-1] > 3
    s.update(must_fail_condition_met=bool(must_fail), WITNESS_OK=bool(must_fail))
    res["sub05"] = s
    s = path_stats(load(dirn, "quintic"))
    s.update(differs_by_5SE=bool(s["f_SE"] is not None and abs(s["f_hat"] - 1.0822) > 5 * s["f_SE"]))
    res["quintic"] = s
    res["ALL_GATES"] = bool(res["a1"]["GATE"] and res["a2"]["GATE"] and res["cusp"]["GATE"] and res["sub05"]["WITNESS_OK"])
    json.dump(res, open(out, "w"), indent=1)
    for k in ("a1", "a2"):
        r = res[k]
        print(k, "f", r["f_hat"], "+-", r["f_SE"], "delta", r["delta_hat"], "+-", r["delta_SE"], "GATE", r["GATE"], "fixes", r["bracket_fixes"], "stopped", r["stopped_at"])
    print("cusp f_inf", res["cusp"]["f_inf"], "+-", res["cusp"]["f_inf_SE"], "GATE", res["cusp"]["GATE"])
    print("sub05 f_n", [round(x, 3) for x in res["sub05"]["f_n"]], "witness OK", res["sub05"]["WITNESS_OK"])
    print("quintic f", res["quintic"]["f_hat"], "+-", res["quintic"]["f_SE"], "differs by > 5 SE", res["quintic"]["differs_by_5SE"])
    print("ALL_GATES", res["ALL_GATES"])
    return 0


def read(dirn, out):
    g = json.load(open(os.path.join(dirn, "GATES.json")))
    per = {}
    for a in range(1, 11):
        s = path_stats(load(dirn, f"a{a}"))
        s["lambda"] = (a + math.sqrt(a * a + 4)) / 2
        per[a] = s
    def judge(val, se, bound):
        if se is None:
            return "UNPOWERED"
        return "SUPPORT" if val + 2 * se < bound else ("CONTRADICT" if val - 2 * se > bound else "UNPOWERED")
    mono = {}
    for a in range(1, 10):
        x, y = per[a], per[a + 1]
        if x["f_hat"] is None or y["f_hat"] is None or x["f_SE"] is None or y["f_SE"] is None:
            mono[f"{a}-{a+1}"] = "UNPOWERED"
            continue
        d, sd = y["f_hat"] - x["f_hat"], math.hypot(x["f_SE"], y["f_SE"])
        mono[f"{a}-{a+1}"] = "SUPPORT" if d > 2 * sd else ("CONTRADICT" if d < -2 * sd else "UNPOWERED")
    below = {a: judge(per[a]["f_hat"], per[a]["f_SE"], 1.5) if per[a]["f_hat"] is not None else "UNPOWERED" for a in per}
    agg = lambda v: "FAIL" if "CONTRADICT" in v.values() else ("PASS" if all(x == "SUPPORT" for x in v.values()) else "PASS on SUPPORT, UNPOWERED on the rest")
    # h_a clause (re-gate): h_a = ln(δ_{a+1}/δ_a) / (2 ln(λ_{a+1}/λ_a)), prediction h_a → 1.5 via h∞ + c₁/λ + c₂/λ²
    # (λ the pair's geometric mean). The cusp-form validation on fresh N failed (§10), so as specified the form family
    # does not count: the clause is UNPOWERED; h_a are reported descriptively.
    h = {}
    for a in range(1, 10):
        x, y = per[a], per[a + 1]
        if x["delta_hat"] and y["delta_hat"]:
            h[f"{a}-{a+1}"] = dict(h=math.log(y["delta_hat"] / x["delta_hat"]) / (2 * math.log(y["lambda"] / x["lambda"])),
                                   lambda_gm=math.sqrt(x["lambda"] * y["lambda"]))
    P3 = dict(status="UNPOWERED", reason="cusp form not validated on fresh N (seal section 10)", h_a=h)
    res = dict(per_a={a: per[a] for a in per}, P1_monotonic=dict(pairs=mono, verdict=agg(mono)),
               P2_below_1p5=dict(per_a=below, verdict=agg(below)), P3_h_a=P3,
               bronze=dict(delta=per[3]["delta_hat"], delta_SE=per[3]["delta_SE"], f=per[3]["f_hat"], f_SE=per[3]["f_SE"]))
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit({"gates": gates, "read": read}[sys.argv[1]](sys.argv[2], sys.argv[3]))

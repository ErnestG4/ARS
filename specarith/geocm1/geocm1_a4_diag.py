"""GEO-CM1 a = 4 SE diagnostic (Will, 2026-10-28; POST HOC, labelled): on the existing per-level values of the sealed
read (results/READ1), find the level driving SE(|δ_4|) = 2.3·10⁻⁵ and check it. Nothing here changes a sealed verdict.

  python geocm1_a4_diag.py OUT_JSON

1. Per path a = 3, 4, 5: δ_n, the differences and their ratios (the geometric-correction check behind Aitken), every
   Aitken triple, the SE as sealed, and leave-one-level-out estimates of |δ| and f.
2. Per a = 4 level: bracket fixes, Newton agreement, 30/50-digit width agreement, edge tolerance (from the JSON).
3. Global-extremum check per a = 3, 4, 5 level (new, double precision): at Ω = edge ∓ ε·w (ε = 0.05) the maximum of
   G = Fᵠ(x) − x − p over a grid of 256q points, refined around its best 8 points, must be < 0 below the lower edge and
   > 0 above it (and the minimum likewise at the upper edge). A tracked local extremum that is not global would fail.
4. The a = 4 bracket contents: level n's bracket is the gap between the tongues of the previous two convergents; the
   intermediate fractions (k p_{n−1} + p_{n−2}) / (k q_{n−1} + q_{n−2}), k = 1 … 3, lie in it. Listed with whether
   their denominators are Fibonacci numbers, and the distance (in Ω, in units of the level's width) from the a = 4
   edges to the golden-path limit Ω_1 (the a = 1 path's last level).
5. P1 pairs (3,4) and (4,5): the sealed comparison, and the same with SE(4) inflated by 10× and 100×.
"""
import json
import math
import sys

import numpy as np
from numba import njit, prange

from geocm1_analyze import aitken, est, levels

TWO_PI = 2 * math.pi
A1 = -1 / TWO_PI


@njit(parallel=True, cache=False)
def gvals(Om, q, p, M):
    v = np.empty(M)
    for i in prange(M):
        x0 = i / M
        x = x0
        for _ in range(q):
            x = x + Om + A1 * math.sin(TWO_PI * x)
        v[i] = x - x0 - p
    return v


@njit(cache=False)
def g1(x0, Om, q, p):
    x = x0
    for _ in range(q):
        x = x + Om + A1 * math.sin(TWO_PI * x)
    return x - x0 - p


def ext(Om, q, p, kind, M):
    v = gvals(Om, q, p, M)
    s = 1.0 if kind == "max" else -1.0
    best = s * v.max() if kind == "max" else s * v.min()
    idx = np.argsort(-s * v)[:8]
    for i in idx:                                   # golden-section refine on ±1 grid cell
        a, b = (i - 1) / M, (i + 1) / M
        g = (math.sqrt(5) - 1) / 2
        for _ in range(60):
            c, d = b - g * (b - a), a + g * (b - a)
            if s * g1(c, Om, q, p) > s * g1(d, Om, q, p):
                b = d
            else:
                a = c
        best = max(best, s * g1((a + b) / 2, Om, q, p))
    return s * best


def fib(n):
    a, b = 1, 1
    while b < n:
        a, b = b, a + b
    return b == n or n == 1


def main(out):
    res = dict(label="POST HOC diagnostic (Will, 2026-10-28) on the sealed read's existing per-level values", paths={})
    per = {}
    for a in (1, 3, 4, 5):
        d = json.load(open(f"results/READ1/{'GATE' if a < 3 else 'READ'}_a{a}.json"))
        lv, stop = levels(d)
        q = [x[0] for x in lv]
        w = [x[1] for x in lv]
        dl = [w[i] / w[i + 1] for i in range(len(w) - 1)]
        f = [math.log(w[i] / w[i + 1]) / (2 * math.log(q[i + 1] / q[i])) for i in range(len(w) - 1)]
        diffs = [dl[i + 1] - dl[i] for i in range(len(dl) - 1)]
        loo = {}
        for k in range(len(w)):
            ww, qq = w[:k] + w[k + 1:], q[:k] + q[k + 1:]
            if k not in (0, len(w) - 1):
                continue                             # only an end level can be dropped without breaking consecutiveness
            dd = [ww[i] / ww[i + 1] for i in range(len(ww) - 1)]
            ff = [math.log(ww[i] / ww[i + 1]) / (2 * math.log(qq[i + 1] / qq[i])) for i in range(len(ww) - 1)]
            loo[f"drop_q{q[k]}"] = dict(delta=est(dd), f=est(ff))
        per[a] = dict(q=q, w=w, runs=d["runs"])
        res["paths"][f"a{a}"] = dict(q=q, delta_n=dl, diffs=diffs,
                                     diff_ratios=[diffs[i + 1] / diffs[i] for i in range(len(diffs) - 1)],
                                     aitken_triples_delta=[aitken(dl[i:i + 3]) for i in range(len(dl) - 2)],
                                     aitken_triples_f=[aitken(f[i:i + 3]) for i in range(len(f) - 2)],
                                     sealed_delta=est(dl), sealed_f=est(f), leave_one_out=loo, stopped=stop)
    # 2. a = 4 per-level integrity
    r30, r50 = per[4]["runs"]["30"], per[4]["runs"]["50"]
    res["a4_levels"] = [dict(p=x["p"], q=x["q"], fixes=[x["fixes"], y["fixes"]], newton_agree_rel=x["newton_agree_rel"],
                             prec_rel=abs(float(x["w"]) / float(y["w"]) - 1), edge_tol_rel=x["edge_tol_rel"],
                             lo=x["lo"], hi=x["hi"]) for x, y in zip(r30, r50)]
    # 3. global-extremum check (double precision)
    eps = 0.05
    gx = {}
    for a in (3, 4, 5):
        d = json.load(open(f"results/READ1/READ_a{a}.json"))
        for lv in d["runs"]["50"]:
            p, q = lv["p"], lv["q"]
            lo, hi, w = float(lv["lo"]), float(lv["hi"]), float(lv["w"])
            M = 256 * q
            c = dict(below_lo_max=ext(lo - eps * w, q, p, "max", M), above_lo_max=ext(lo + eps * w, q, p, "max", M),
                     below_hi_min=ext(hi - eps * w, q, p, "min", M), above_hi_min=ext(hi + eps * w, q, p, "min", M))
            c["ok"] = c["below_lo_max"] < 0 < c["above_lo_max"] and c["below_hi_min"] < 0 < c["above_hi_min"]
            gx[f"a{a}_q{q}"] = c
            print(f"a{a} q={q} ok={c['ok']} " + " ".join(f"{k}={v:+.2e}" for k, v in c.items() if k != "ok"), flush=True)
    res["global_extremum_check"] = dict(eps=eps, grid="256q + golden refine of the best 8", levels=gx,
                                        all_ok=all(v["ok"] for v in gx.values()))
    # 4. bracket contents for a = 4, and distance to the golden-path limit
    conv = [(0, 1), (1, 4)]
    while conv[-1][1] < 6000:
        conv.append((4 * conv[-1][0] + conv[-2][0], 4 * conv[-1][1] + conv[-2][1]))
    om1 = float(json.load(open("results/READ1/GATE_a1.json"))["runs"]["50"][-1]["lo"])
    br = []
    for n in range(2, len(conv)):
        (p2, q2), (p1, q1), (p, q) = conv[n - 2], conv[n - 1], conv[n]
        inter = [(k * p1 + p2, k * q1 + q2) for k in (1, 2, 3)]
        lv = next((x for x in r50 if x["q"] == q), None)
        br.append(dict(level=f"{p}/{q}", q_is_half_fib=fib(2 * q), parents=[f"{p2}/{q2}", f"{p1}/{q1}"],
                       intermediates=[dict(frac=f"{a}/{b}", fib_denominator=fib(b)) for a, b in inter],
                       dist_to_golden_limit_in_widths=(abs(float(lv["lo"]) - om1) / float(lv["w"])) if lv else None))
    res["a4_brackets"] = dict(golden_limit_Omega=om1, levels=br)
    # 5. P1 pairs
    pf = {a: res["paths"][f"a{a}"]["sealed_f"] for a in (3, 4, 5)}
    p1 = {}
    for x, y in ((3, 4), (4, 5)):
        dlt = pf[y][0] - pf[x][0]
        for inf in (1, 10, 100):
            s = math.hypot(pf[x][1] * (inf if x == 4 else 1), pf[y][1] * (inf if y == 4 else 1))
            p1[f"{x}-{y}_SE4x{inf}"] = dict(diff=dlt, sd=s, z=dlt / s, verdict="SUPPORT" if dlt > 2 * s else "not SUPPORT")
    res["P1_pairs"] = p1
    json.dump(res, open(out, "w"), indent=1)
    for k, v in p1.items():
        print(k, f"diff {v['diff']:.6f} sd {v['sd']:.2e} z {v['z']:.0f} {v['verdict']}")
    print("global extremum all ok:", res["global_extremum_check"]["all_ok"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

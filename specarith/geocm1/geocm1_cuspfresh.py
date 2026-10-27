"""GEO-CM1 re-gate (post hoc, labelled): cusp-form validation on fresh N.
  predict: fit f_N = f∞ + b/N + c/N² on the seen N = 24 … 199 (results/GATES.json); predictions with SE for the declared
           fresh subset FRESH, SE_pred² = xᵀ Cov x + s² (s² the fit's residual variance) → results/CUSP_PREDICTIONS.json
  compute: the fresh tongues 1/N and 1/(N + 1) at 30 and 50 digits (geocm1.tongue), bracketed by 0/1's upper edge and
           the lower edge of the already-computed 1/199 tongue → results/CUSP_FRESH.json
  judge:   VALIDATED iff every fresh f_N lies within its ±2·SE_pred band and the fit's f∞ is 1.5 ± 0.002.
"""
import json
import math
import sys

import mpmath as mp
import numpy as np

import geocm1 as G

FRESH = [220, 250, 300, 400, 500, 650, 800, 1000]


def predict(out):
    g = json.load(open("results/GATES.json"))
    f = {int(k): v for k, v in g["cusp"]["f_N"].items()}
    Ns = [N for N in sorted(f) if 24 <= N <= 199]
    X = np.array([[1, 1 / N, 1 / N ** 2] for N in Ns])
    y = np.array([f[N] for N in Ns])
    c = np.linalg.lstsq(X, y, rcond=None)[0]
    s2 = float(np.sum((X @ c - y) ** 2) / (len(Ns) - 3))
    cov = s2 * np.linalg.inv(X.T @ X)
    pr = {}
    for N in FRESH:
        x = np.array([1, 1 / N, 1 / N ** 2])
        pr[str(N)] = dict(pred=float(x @ c), SE=float(math.sqrt(x @ cov @ x + s2)))
    res = dict(fit_N=[Ns[0], Ns[-1]], f_inf=float(c[0]), f_inf_SE=float(math.sqrt(cov[0, 0])), b=float(c[1]),
               c=float(c[2]), resid_sd=math.sqrt(s2), predictions=pr, fit_recovers_1p5=bool(abs(c[0] - 1.5) <= 0.002))
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps(res, indent=1))


def compute(out):
    gc = json.load(open("results/GATE_cusp.json"))
    res = dict(fresh=FRESH, runs={})
    A1, A2 = G.params("cusp")
    for dps in G.DIGITS:
        mp.mp.dps = dps
        z_hi, _, _ = G.edge(mp.mpf(0), mp.mpf(1), 1, 0, A1, A2, "min", mp.mpf(10) ** -25)
        lv199 = [l for l in gc["runs"][str(dps)] if l["q"] == 199][0]
        hi = mp.mpf(lv199["lo"])
        w = {}
        for N in sorted(set(FRESH + [n + 1 for n in FRESH])):
            t = G.tongue(1, N, z_hi, hi, A1, A2, None)
            w[str(N)] = dict(w=mp.nstr(t["w"], dps), fixes=t["fixes"], newton_agree_rel=t["newton_agree_rel"])
            print(dps, N, mp.nstr(t["w"], 12), t["fixes"], t["newton_agree_rel"], flush=True)
        res["runs"][str(dps)] = w
    json.dump(res, open(out, "w"), indent=1)


def judge(pred_path, fresh_path, out):
    P = json.load(open(pred_path))
    F = json.load(open(fresh_path))
    r30, r50 = F["runs"]["30"], F["runs"]["50"]
    rows, ok = {}, P["fit_recovers_1p5"]
    for N in FRESH:
        agree = abs(float(r30[str(N)]["w"]) / float(r50[str(N)]["w"]) - 1) <= 1e-6
        fN = math.log(float(r50[str(N)]["w"]) / float(r50[str(N + 1)]["w"])) / (2 * math.log((N + 1) / N))
        p = P["predictions"][str(N)]
        inb = abs(fN - p["pred"]) <= 2 * p["SE"]
        rows[str(N)] = dict(f_N=fN, pred=p["pred"], SE=p["SE"], z=(fN - p["pred"]) / p["SE"], in_band=inb, precisions_agree=agree)
        ok &= inb and agree
    res = dict(rows=rows, f_inf=P["f_inf"], fit_recovers_1p5=P["fit_recovers_1p5"], VALIDATED=bool(ok))
    json.dump(res, open(out, "w"), indent=1)
    for N, r in rows.items():
        print(N, f"f_N {r['f_N']:.6f} pred {r['pred']:.6f} SE {r['SE']:.1e} z {r['z']:+.2f}", r["in_band"], r["precisions_agree"])
    print("VALIDATED", ok)


if __name__ == "__main__":
    {"predict": predict, "compute": compute, "judge": judge}[sys.argv[1]](*sys.argv[2:])

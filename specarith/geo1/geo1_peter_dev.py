"""GEO1 Peter-correlation seal: development range t ≤ 10⁶ (Will: "the convergence trend on t ≤ 10⁶ (the development
range) plus the statistical SE"). Seen data; the fresh range for the seal is t > 10⁶.

  python geo1_peter_dev.py PARI_NPZ PRED_JSON OUT_JSON

α(n) = g_prim(n) log n / n, α̃ = α − 1 (Peter's definitions). For each lag r of PRED_JSON:
  - windows W = [a, b) of n (with n + r ≤ 10⁶): γ̂_W(r) = mean over n ∈ W of α̃(n) α̃(n + r); the windows are the nested
    [3, N) for N = 10⁴, 3·10⁴, 10⁵, 3·10⁵, 10⁶ − r and the disjoint quarter-decades [10^(k/4), 10^((k+1)/4)), k = 16 … 23;
  - the ratio γ̂(r)/γ̂(0) on the same windows;
  - block SE on each disjoint window: blocks of 10⁴ consecutive n, SE = SD(block means)/√(number of blocks);
  - z = (γ̂ − γ_pred)/SE per disjoint window, and the trend: OLS of (γ̂ − γ_pred) on log n over the disjoint windows.
"""
import json
import math
import sys

import numpy as np

from geo1 import g_prim_from_all

BLOCK = 10 ** 4


def main(pnpz, pjson, out):
    p = np.load(pnpz)
    t = p["t"].astype(np.int64)
    gp = g_prim_from_all(t, p["g_all"]).astype(np.float64)
    a = gp * np.log(t) / t - 1.0                        # α̃(n), n = t
    pred = json.load(open(pjson))["gamma"]
    lags = sorted(int(r) for r in pred)
    T = int(t[-1])
    res = dict(alpha_mean_all=float(a.mean() + 1), lags=lags, nested={}, disjoint={})
    nested = [10 ** 4, 3 * 10 ** 4, 10 ** 5, 3 * 10 ** 5, T]
    disj = [(int(round(10 ** (k / 4))), int(round(10 ** ((k + 1) / 4)))) for k in range(16, 24)]
    for r in lags:
        y = a[: len(a) - r] * a[r:]                        # y[i] = α̃(t_i) α̃(t_i + r), t_i = i + 3
        nn = {}
        for N in nested:
            m = min(N - 3, len(y))
            nn[str(N)] = float(y[:m].mean())
        res["nested"][str(r)] = nn
        dd = []
        for lo, hi in disj:
            i0, i1 = lo - 3, min(hi - 3, len(y))
            seg = y[i0:i1]
            nb = len(seg) // BLOCK
            bm = seg[: nb * BLOCK].reshape(nb, BLOCK).mean(1) if nb >= 2 else None
            se = float(bm.std(ddof=1) / math.sqrt(nb)) if bm is not None else None
            g = float(seg.mean())
            dd.append(dict(lo=lo, hi=hi, n=len(seg), gamma_hat=g, SE_block=se, pred=pred[str(r)]["gamma"],
                           diff=g - pred[str(r)]["gamma"], z=(g - pred[str(r)]["gamma"]) / se if se else None))
        res["disjoint"][str(r)] = dd
        x = np.array([math.log(math.sqrt(d["lo"] * d["hi"])) for d in dd])
        yy = np.array([d["diff"] for d in dd])
        c = np.polyfit(x, yy, 1)
        res["disjoint"][str(r) + "_trend"] = dict(slope_per_log_n=float(c[0]), at_1e6=float(np.polyval(c, math.log(1e6))),
                                                   at_1e7=float(np.polyval(c, math.log(1e7))))
    # ratios
    rat = {}
    for r in lags:
        rat[str(r)] = dict(pred=pred[str(r)]["gamma"] / pred["0"]["gamma"],
                           nested={N: res["nested"][str(r)][N] / res["nested"]["0"][N] for N in res["nested"]["0"]},
                           disjoint=[d["gamma_hat"] / d0["gamma_hat"] for d, d0 in zip(res["disjoint"][str(r)],
                                                                                    res["disjoint"]["0"])])
    res["ratio"] = rat
    json.dump(res, open(out, "w"), indent=1)
    print(f"mean alpha over t <= {T}: {res['alpha_mean_all']:.6f}")
    print(" r     pred   nested 1e4 ... 1e6                         last disjoint z   trend@1e6")
    for r in lags:
        nn = res["nested"][str(r)]
        last = res["disjoint"][str(r)][-1]
        print(f"{r:3d} {pred[str(r)]['gamma']:8.4f}  " + " ".join(f"{nn[k]:8.4f}" for k in nn) +
              f"   z_last {last['z']:+6.2f} SE {last['SE_block']:.4f}  trend@1e6 {res['disjoint'][str(r) + '_trend']['at_1e6']:+.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))

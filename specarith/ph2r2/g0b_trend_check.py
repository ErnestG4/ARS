"""G0b post-hoc diagnostic (2026-10-09, after the official merge; descriptive, not a seal input).
Does the deterministic density drift across a bin explain the bootstrap SD growth at 10,000-level blocks?
E[c](t) = per-level expected ordered-pair contribution under the sine kernel at the bin's fixed delta; a linear trend
of total range D over n levels adds Var = n*B*D^2/12 to the MBB variance of the sum (B << n)."""
import json, math, sys
import numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import r2prep as P
HERE = __import__('os').path.dirname(__import__('os').path.abspath(__file__))
S = json.load(open(HERE + '/results/g0b/g0b_summary.json'))
x, wx = np.polynomial.legendre.leggauss(2001)
for n in P.BINS:
    g = P.geometry(n)
    for u, w in ((0.5, 0.3), (0.5, 0.15), (2.0, 0.3)):
        def Ec(t):
            rho = math.log(t / P.TWO_PI) / P.TWO_PI
            rmax = P.U_MAX * g["delta"]
            r = 0.5 * rmax * (x + 1); wr = 0.5 * rmax * wx
            s = rho * r
            R2 = rho * (1 - np.sinc(s) ** 2)          # pair density per level at distance r (sine kernel)
            return 2 * np.sum(P.f_raw(r, u, w, g["delta"]) * R2 * wr)
        D = Ec(g["t1"]) - Ec(g["t0"])
        rec = json.load(open(sorted(__import__('glob').glob(HERE + f'/results/g0b/g0b_{n}_r*.json'))[0]))[0]
        k = f"{u}_{w}"
        nlev = rec["nblocks"] * 250
        lot = abs(rec[k]["LOT"])
        sd = S[n][k]["sd_mu"]
        out = []
        for B in (100, 1000, 10000):
            trend_sd_mu = D * math.sqrt(nlev * B / 12) / lot
            pred_ratio = math.sqrt(sd ** 2 + trend_sd_mu ** 2) / sd
            out.append((B, round(trend_sd_mu / sd, 3), round(pred_ratio, 3), round(S[n][k]["boot_sd_over_sd"][str(B)], 3)))
        print(n, k, f"Ec0={Ec(g['t0']):.5f} D/Ec={D/Ec(g['t0']):+.4f}", "(B, trend/sd, predicted ratio, observed ratio):", out)

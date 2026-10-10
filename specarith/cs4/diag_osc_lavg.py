"""Reads the ℓ-averaging diagnostic (run_diag_osc_lavg_spot.sh): pair (5,5)'s dropped ℓ-oscillating long-range part and
its kept non-oscillating part, Δr = 0.1, at the 5 Gauss–Legendre nodes across the F2 15.75 file's ℓ range, and their
zero-weighted averages (weights ∝ GL·ℓe^ℓ), as fractions of the production v(b) at ℓ = 15.7502.

  python diag_osc_lavg.py RESULTS_DIR [dense]      (RESULTS_DIR holds diag_osc_lavg/, diag_osc_lavg64/, gs_zeta/)

"dense": the 64 stratified midpoints of run_diag_osc_lavg64_spot.sh (weights ∝ ℓe^ℓ), with the standard error of the
stratified mean (treating the ℓ samples as dephased, i.e. independent) beside it.
"""
import json
import math
import os
import sys

import numpy as np

import gs_zeta as Z

ELLS = (15.728166, 15.737046, 15.750050, 15.763054, 15.771934)
WTS = (0.115725, 0.236002, 0.284413, 0.242620, 0.121239)


def dense_nodes():
    a, b = 15.7259, 15.7742
    ells = [float("%.7f" % (a + (k + 0.5) * (b - a) / 64)) for k in range(64)]
    w = np.array([l * math.exp(l) for l in ells])
    return ells, (w / w.sum()).tolist()


def main(rd, dense=False):
    ells, wts, sub = (*dense_nodes(), "diag_osc_lavg64") if dense else (ELLS, WTS, "diag_osc_lavg")
    # diag_osc_alias.py names its output by repr(float(ELL)), as here
    rows = [json.load(open(os.path.join(rd, sub, f"alias_L{ell}_5_5_full.json"))) for ell in ells]
    v = json.load(open(os.path.join(rd, "gs_zeta", "gs_zeta_L15.7502.json")))["v"]
    w = 4 * (Z.DW[5] * Z.FD[5]) ** 2 / math.sqrt(2)          # pair (5,5)'s weight in v(b)
    out = {}
    for b in Z.LADDER:
        osc = np.array([r[f"osc_fine_b{b}"] for r in rows])
        non = np.array([r[f"non_fine_b{b}"] for r in rows])
        avg_o, avg_n = float(np.dot(wts, osc)), float(np.dot(wts, non))
        se_o = float(osc.std(ddof=1) / math.sqrt(len(osc)))
        out[b] = dict(osc_by_ell=osc.tolist(), osc_avg=avg_o, non_by_ell=non.tolist(), non_avg=avg_n,
                      osc_avg_over_v=w * abs(avg_o) / v[str(b)], osc_max_over_v=w * np.abs(osc).max() / v[str(b)],
                      non_spread_over_v=w * (non.max() - non.min()) / v[str(b)], osc_avg_se=se_o,
                      osc_avg_se_over_v=w * se_o / v[str(b)])
        shown = " ".join("%+.2e" % x for x in osc) if not dense else "(64 values)"
        print("b=%5d  osc(ℓ): %s  avg %+.2e ± %.1e | /v: max-ℓ %.1e  ℓ-avg %.1e ± %.1e | non spread over ℓ /v %.1e"
              % (b, shown, avg_o, se_o, out[b]["osc_max_over_v"], out[b]["osc_avg_over_v"], out[b]["osc_avg_se_over_v"],
                 out[b]["non_spread_over_v"]))
    json.dump(out, open(os.path.join(rd, sub, "summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] == ["dense"])

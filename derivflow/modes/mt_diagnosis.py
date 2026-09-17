#!/usr/bin/env python3
"""POST-HOC, EXPLORATORY, UNSEALED. Re-reads mt_transfer.json (no new computation on roots) and
tests ONE correction formed after reading the sealed output: the Richardson primary arm's kernel
transfer is NOT B = 1 (BRIEF/seal) but the Richardson combination of the two Poisson transfers,
    B_R = 2 e^{-qw eps_sp} - e^{-2 qw eps_sp}  (= 1 - (1 - e^{-qw eps_sp})^2),
because the primary CDF is 2F(eps) - F(2eps) and each F is the Poisson-smoothed CDF.
COMMITTED GENERATOR of derivflow/modes/mt_diagnosis.json. Also lists which arms produced the
sealed failures, and applies the ML float64 assessability floor to flag cells whose RAW signal
is below what float64 can resolve (the seal's POPREF/RM1 expectations carried no such clause).
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modes_common as M                     # noqa: E402

a = json.load(open(os.path.join(HERE, "mt_transfer.json")))
n, A = a["n"], a["A"]
h = 2.0 / (n - 1)
floor = 4.0 * np.finfo(float).eps / h            # spacings, as in the ML seal
rows = []
for r in a["rows"]:
    qw, k = r["qw"], r["k"]
    eps_sp = M.eps_over_delta(n, k)
    growth = np.exp(k * (-np.log(1 - qw / np.pi) - qw / np.pi))
    B_R = 2 * np.exp(-qw * eps_sp) - np.exp(-2 * qw * eps_sp)
    Tp_R = 1 - B_R * growth
    P = r["arms"]["PROD_PRIMARY"]
    T = complex(P["T_re"], P["T_im"])
    assessable = bool(A * r["raw_gain_pred"] >= 1e3 * floor)
    rows.append({"qw": qw, "k": k, "eps_sp": eps_sp, "B_richardson": B_R, "T_pred_richardson": Tp_R,
                 "T_primary": [P["T_re"], P["T_im"]], "dev_richardson": abs(T - Tp_R),
                 "dev_sealed_B1": P["dev"], "assessable_float64": assessable,
                 "in_band": bool(0.1 <= qw <= 0.5),
                 "POPREF_abs_T_minus_1": abs(complex(r["arms"]["POPREF"]["T_re"], r["arms"]["POPREF"]["T_im"]) - 1),
                 "RM1_abs_T": r["arms"]["RM1"]["abs_T"],
                 "BW1_dev": r["arms"]["PROD_BW1"]["dev"], "BW2_dev": r["arms"]["PROD_BW2"]["dev"]})
band = [r for r in rows if r["in_band"]]
fail_arms = {}
for f in a["failures"]:
    fail_arms[f["arm"]] = fail_arms.get(f["arm"], 0) + 1
summ = {"sealed_failures_by_arm": fail_arms,
        "band_PRIMARY_worst_dev_sealed_B1": max(r["dev_sealed_B1"] for r in band),
        "band_PRIMARY_worst_dev_richardson_kernel": max(r["dev_richardson"] for r in band),
        "band_BW1_worst_dev": max(r["BW1_dev"] for r in band), "band_BW2_worst_dev": max(r["BW2_dev"] for r in band),
        "band_PRIMARY_cells_within_0.1_richardson": sum(r["dev_richardson"] <= 0.1 for r in band), "band_cells": len(band),
        "POPREF_worst_abs_T_minus_1_assessable": max(r["POPREF_abs_T_minus_1"] for r in rows if r["assessable_float64"]),
        "POPREF_assessable_cells": sum(r["assessable_float64"] for r in rows),
        "RM1_worst_abs_T_qw_le_0.1": max(r["RM1_abs_T"] for r in rows if r["qw"] <= 0.1),
        "PRIMARY_T_at_k1": {str(r["qw"]): r["T_primary"][0] for r in rows if r["k"] == 1},
        "PRIMARY_first_negative_k_by_qw": {str(qw): next((r["k"] for r in rows if r["qw"] == qw and r["assessable_float64"] and r["T_primary"][0] < 0), None) for qw in sorted({r["qw"] for r in rows})}}
json.dump({"grade": "EXPLORATORY, POST-HOC, UNSEALED", "rows": rows, "summary": summ},
          open(os.path.join(HERE, "mt_diagnosis.json"), "w"), indent=1)
print(json.dumps(summ, indent=1))
for r in band:
    print(f"qw={r['qw']} k={r['k']:2d}: T_primary {r['T_primary'][0]:+.3f}  pred(B=1) {1-(1-0)*0:+.0f}... sealed dev {r['dev_sealed_B1']:.3f}  B_R {r['B_richardson']:.3f} pred_R {r['T_pred_richardson']:+.3f} dev_R {r['dev_richardson']:.3f}")

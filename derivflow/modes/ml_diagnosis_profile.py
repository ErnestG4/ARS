#!/usr/bin/env python3
"""POST-HOC, EXPLORATORY, UNSEALED. Second diagnosis of GATE_ML_FAIL, on the banked roots only.
COMMITTED GENERATOR of derivflow/modes/ml_diagnosis_profile_<n>.json.

What it measures, per (qw, k) at A = 1e-5: the LOCAL complex gain in 8 Hann sub-windows across
the bulk window, in BOTH the sealed index basis (theta = qw (i + k/2) + phi) and the physical
basis (theta = qw (x_i^LAT + 1)/h + phi); the seed-index deviation of the LATTICE run's roots
(x_i^LAT + 1)/h - (i + k/2) at the window ends; and the coherence factor that a linear phase
drift of that size would cost a Hann-weighted global projection.

Hypothesis tested (formed after reading the n=4096 and n=16384 sealed outputs): the sealed loss
is COHERENCE loss from a linear phase drift across the window — the lattice bulk dilates by
c_k - 1 ~ k/(2n) (so the root at window offset j sits at seed index i + k/2 + j (c_k - 1)), and
the wave's wavenumber follows HALF that dilation — while the local amplitude at the window
centre stays within ~1% of (1 - qw/pi)^k. Drift ~ qw (c_k - 1) W/2 ~ qw k, n-independent for a
window proportional to n, which is the observed scaling.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modes_common as M                                  # noqa: E402
from ml_gain_gate import hann, local_spacing, PHI, QW, KS  # noqa: E402

n = int(sys.argv[1]); A = 1e-5; h = 2.0 / (n - 1)
Z = np.load(os.path.join(HERE, "roots", f"ml_{n}.npz"))
NSUB = 8
t0 = time.time()
rows = []
for qw in QW:
    for k in KS:
        pred = (1 - qw / np.pi) ** k
        if pred < 1e-8 or A * pred < 1e-9:
            continue
        m = n - k; xl = Z[f"lattice_k{k}"]; xw = Z[f"wave_qw{qw}_A{A}_k{k}"]
        bi = M.bulk_idx(m); idx = np.arange(m)[bi]
        dev = (xl[bi] + 1.0) / h - (idx + 0.5 * k)
        rec = {"qw": qw, "k": k, "gain_pred": pred, "W": int(len(idx)),
               "seed_index_dev_ends": [float(dev[0]), float(dev[-1])],
               "dilation_c_minus_1": float((dev[-1] - dev[0]) / (idx[-1] - idx[0]))}
        W = len(idx) // NSUB; w = hann(W)
        for name, y, th in (("index", ((xw - xl) / local_spacing(xl))[bi] / A, qw * (idx + 0.5 * k) + PHI),
                            ("phys", ((xw - xl) / h)[bi] / A, qw * (xl[bi] + 1.0) / h + PHI)):
            amps, phs = [], []
            for s in range(NSUB):
                sl = slice(s * W, (s + 1) * W)
                g = 1j * 2.0 * np.sum(w * y[sl] * np.exp(-1j * th[sl])) / np.sum(w)
                amps.append(float(abs(g) / pred)); phs.append(float(np.angle(g)))
            slope = float(np.polyfit(np.arange(NSUB), np.unwrap(phs), 1)[0]) * NSUB / len(idx)   # rad per root
            # coherence of a Hann-weighted global projection under this linear drift
            wg = hann(len(idx)); ph = slope * (np.arange(len(idx)) - len(idx) / 2)
            coh = float(abs(np.sum(wg * np.exp(1j * ph))) / np.sum(wg))
            rec[name] = {"local_gain_over_pred": amps, "local_phase": phs,
                         "centre_gain_over_pred": float(0.5 * (amps[NSUB // 2 - 1] + amps[NSUB // 2])),
                         "phase_slope_rad_per_root": slope, "delta_q_over_q": slope / qw,
                         "coherence_factor": coh}
        rows.append(rec)
sel = [r for r in rows if r["qw"] >= 0.1]
summary = {
    "n_cells": len(rows),
    "dilation_over_k_over_n_median": float(np.median([r["dilation_c_minus_1"] / (r["k"] / n) for r in rows])),
    "phys_delta_q_over_q_divided_by_dilation_median": float(np.median(
        [r["phys"]["delta_q_over_q"] / r["dilation_c_minus_1"] for r in sel if r["dilation_c_minus_1"] != 0])),
    "index_delta_q_over_q_divided_by_dilation_median": float(np.median(
        [r["index"]["delta_q_over_q"] / r["dilation_c_minus_1"] for r in sel if r["dilation_c_minus_1"] != 0])),
    "centre_gain_over_pred_worst_qw_ge_0.1": float(max(abs(r["index"]["centre_gain_over_pred"] - 1) for r in sel)),
    "centre_gain_over_pred_by_qwk": {f"{r['qw']}x{r['k']}": r["index"]["centre_gain_over_pred"] for r in sel},
    "coherence_predicts_sealed_loss_maxdev": None,
}
# does coherence x centre-amplitude reproduce the sealed global gain?
banked = {(c["qw"], c["k"]): c for c in json.load(open(os.path.join(HERE, f"ml_gain_gate_{n}.json")))["cells"] if c["A"] == A}
devs = []
for r in sel:
    g_sealed = abs(complex(banked[(r["qw"], r["k"])]["gain_re"], banked[(r["qw"], r["k"])]["gain_im"])) / r["gain_pred"]
    g_model = r["index"]["coherence_factor"] * np.mean(r["index"]["local_gain_over_pred"])
    devs.append(abs(g_sealed - g_model)); r["sealed_gain_over_pred"] = g_sealed; r["coherence_x_meanlocal"] = float(g_model)
summary["coherence_predicts_sealed_loss_maxdev"] = float(max(devs))
out = {"grade": "EXPLORATORY, POST-HOC, UNSEALED (hypothesis formed after reading the sealed outputs)",
       "n": n, "A": A, "rows": rows, "summary": summary, "runtime_s": time.time() - t0}
json.dump(out, open(os.path.join(HERE, f"ml_diagnosis_profile_{n}.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in summary.items() if k != "centre_gain_over_pred_by_qwk"}, indent=1))
for r in sel:
    if r["qw"] in (0.2, 0.5, 1.0):
        print(f"qw={r['qw']} k={r['k']:2d}: dil {r['dilation_c_minus_1']:.2e}  dq/q idx {r['index']['delta_q_over_q']:+.2e} phys {r['phys']['delta_q_over_q']:+.2e}  "
              f"centre {r['index']['centre_gain_over_pred']:.4f} ends {r['index']['local_gain_over_pred'][0]:.3f}  coh {r['index']['coherence_factor']:.4f}  sealed {r['sealed_gain_over_pred']:.4f} model {r['coherence_x_meanlocal']:.4f}")

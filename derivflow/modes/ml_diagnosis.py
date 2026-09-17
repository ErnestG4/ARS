#!/usr/bin/env python3
"""POST-HOC, EXPLORATORY, UNSEALED. Diagnosis of GATE_ML_FAIL at n=4096 — written AFTER the
sealed gate's output was read. COMMITTED GENERATOR of derivflow/modes/ml_diagnosis_<n>.json.
It does not change the sealed verdict (ml_gain_gate_<n>.json stays FAIL); it tests ONE
attribution on the SAME banked roots (roots/ml_<n>.npz, A = 1e-5 waves + LATTICE), with no
new wave flows and no free parameter:

  H_basis: the sealed recipe projects on sin(qw (i + k/2) + phi) — a phase in ROOT INDEX that
  assumes root i of p^(k) sits at seed index i + k/2. The linear response transports the wave
  in PHYSICAL position (the weights (x* - r_j)^-2 are symmetric about the new root), so the
  natural basis is theta_i = qw (x_i^LAT + 1)/h + phi with x_i^LAT the LATTICE run's root.
  If the bulk of the lattice dilates by O(k/n) under the flow, the index basis accumulates a
  phase error linear across the window and loses amplitude ~ (qw k W/n)^2 — A-independent,
  growing with qw and k, which is the observed pattern.

Variants computed on identical data (all reported, none selected):
  V0  sealed recipe (index basis, y = d/h_local)              [must reproduce the banked rel_err]
  V1  physical basis, y = d/h_seed
  V2  physical basis, y = d/h_local
  V3  physical basis, y = d/h_seed, prediction with the local wavenumber per step:
      prod_{k'<=k} (1 - qw c_{k'}/pi), c_{k'} = bulk mean gap of the LATTICE run at step k' / h_seed
      (c_k re-measured here by re-flowing the LATTICE seed with the certified GPU solver).
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

n = int(sys.argv[1])
A = 1e-5
h = 2.0 / (n - 1)
Z = np.load(os.path.join(HERE, "roots", f"ml_{n}.npz"))
t0 = time.time()

# c_k for every step (LATTICE re-flow on the certified GPU solver)
c = {}
r = M.seed_lattice(n)
for k in range(1, max(KS) + 1):
    r = M.diff_step_gpu(r)
    m = n - k
    c[k] = float(np.mean(np.diff(r[M.bulk_idx(m)])) / h)
# sanity: the re-flow reproduces the banked lattice roots
r_chk = np.load(os.path.join(HERE, "roots", f"ml_{n}.npz"))["lattice_k64"]
reflow_dev = float(np.max(np.abs(r - r_chk)))


def gains(qw, k):
    m = n - k
    xl, xw = Z[f"lattice_k{k}"], Z[f"wave_qw{qw}_A{A}_k{k}"]
    d = xw - xl
    bi = M.bulk_idx(m); idx = np.arange(m)[bi]
    w = hann(len(idx))
    out = {}
    th_idx = qw * (idx + 0.5 * k) + PHI
    th_phys = qw * (xl[bi] + 1.0) / h + PHI
    for name, y, th in (("V0_index_hloc", (d / local_spacing(xl))[bi], th_idx),
                        ("V1_phys_hseed", (d / h)[bi], th_phys),
                        ("V2_phys_hloc", (d / local_spacing(xl))[bi], th_phys)):
        g = 1j * 2.0 * np.sum(w * y * np.exp(-1j * th)) / (A * np.sum(w))
        out[name] = {"gain_re": float(g.real), "gain_im": float(g.imag)}
    pred0 = (1 - qw / np.pi) ** k
    pred3 = float(np.prod([1 - qw * c[kk] / np.pi for kk in range(1, k + 1)]))
    for name in out:
        g = complex(out[name]["gain_re"], out[name]["gain_im"])
        out[name]["rel_err_vs_(1-qw/pi)^k"] = float(abs(g - pred0) / pred0)
    g1 = complex(out["V1_phys_hseed"]["gain_re"], out["V1_phys_hseed"]["gain_im"])
    out["V3_phys_hseed_localq"] = {"pred": pred3, "rel_err": float(abs(g1 - pred3) / pred3)}
    out["pred0"] = pred0
    return out


rows = []
for qw in QW:
    for k in KS:
        rec = gains(qw, k); rec.update(qw=qw, k=k); rows.append(rec)
banked = {(cc["qw"], cc["k"]): cc["rel_err"] for cc in json.load(open(os.path.join(HERE, f"ml_gain_gate_{n}.json")))["cells"]
          if cc["A"] == A}
v0_repro = max(abs(rr["V0_index_hloc"]["rel_err_vs_(1-qw/pi)^k"] - banked[(rr["qw"], rr["k"])]) for rr in rows)


def worst(name, key, qmin=0.1):
    return max(rr[name][key] for rr in rows if rr["qw"] >= qmin and rr["pred0"] >= 1e-8)


summary = {"V0_worst": worst("V0_index_hloc", "rel_err_vs_(1-qw/pi)^k"),
           "V1_worst": worst("V1_phys_hseed", "rel_err_vs_(1-qw/pi)^k"),
           "V2_worst": worst("V2_phys_hloc", "rel_err_vs_(1-qw/pi)^k"),
           "V3_worst": worst("V3_phys_hseed_localq", "rel_err"),
           "V0_reproduces_banked_rel_err_maxdiff": v0_repro,
           "c_k": {str(k): c[k] for k in KS}, "c_64_minus_1": c[64] - 1.0,
           "lattice_reflow_max_dev": reflow_dev}
out = {"grade": "EXPLORATORY, POST-HOC, UNSEALED — written after ml_gain_gate_%d.json was read; the sealed FAIL stands" % n,
       "n": n, "A": A, "rows": rows, "summary": summary, "runtime_s": time.time() - t0}
json.dump(out, open(os.path.join(HERE, f"ml_diagnosis_{n}.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))
print(f"{'qw':>5} {'k':>3} {'V0 index':>10} {'V1 phys/h':>10} {'V2 phys/hl':>10} {'V3 localq':>10}")
for rr in rows:
    if rr["qw"] in (0.1, 0.2, 0.5, 1.0, 2.0):
        print(f"{rr['qw']:>5} {rr['k']:>3} {rr['V0_index_hloc']['rel_err_vs_(1-qw/pi)^k']:>10.2e} "
              f"{rr['V1_phys_hseed']['rel_err_vs_(1-qw/pi)^k']:>10.2e} {rr['V2_phys_hloc']['rel_err_vs_(1-qw/pi)^k']:>10.2e} "
              f"{rr['V3_phys_hseed_localq']['rel_err']:>10.2e}")

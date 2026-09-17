#!/usr/bin/env python3
"""GATE ML — linear gain of the derivative flow on a planted displacement wave (BRIEF §3 ML).
COMMITTED GENERATOR of derivflow/modes/ml_gain_gate_<n>.json and roots/ml_<n>.npz.

    usage: ml_gain_gate.py <n>

Executes seal_night1.json["ML"] verbatim: LATTICE and LATTICE_WAVE(qw, A, phi) flows to k=64,
gain measured by the declared complex Hann-tapered projection at seed index i + k/2 in units of the
LATTICE run's local spacing, prediction (1 - qw/pi)^k, float64 assessability by the declared
floor, plus the no-dynamics known answers and the M6 interlacing witness on every flow.
Solver: diff_step_gpu if gpu_solver_gate.json says GPU_SOLVER_CERTIFIED, else the CPU diff_step
with the declared contingency. Nothing here is chosen after seeing an output.
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modes_common as M                                              # noqa: E402
from modelparams import Model, Param, DECLARED                        # noqa: E402

SEAL = json.load(open(os.path.join(HERE, "seal_night1.json")))
ML = SEAL["ML"]
QW, AS, KS = ML["qw_grid"], ML["A_grid_float64"], ML["k_grid"]
PHI = 0.3
EPS_MACH = np.finfo(np.float64).eps
FLOOR_ULPS = 4.0
RELERR_TARGET = 1e-3
PASS_TOL = 1e-3
ONSET_TOL = 1e-2
LOG = os.path.join(HERE, "ml_gain_gate.progress.log")

INSTRUMENT = Model("gate ML measurement (declared in seal_night1.json)", [
    Param("KSTAR_LEVEL", DECLARED, value=M.KSTAR_LEVEL, why="imported constant; unused by ML but declared"),
    Param("FIT_WINDOW_MIN", DECLARED, value=M.FIT_WINDOW_MIN, why="imported constant; unused by ML but declared"),
    Param("BULK_FRACTION", DECLARED, value=M.BULK_FRACTION, why="the projection window (bulk_idx)"),
    Param("phi", DECLARED, value=PHI, why="seal"),
    Param("FLOAT64_FLOOR_ULPS", DECLARED, value=FLOOR_ULPS, why="seal: assessability floor"),
    Param("pass_tol", DECLARED, value=PASS_TOL, why="seal: rel_err <= 1e-3"),
    Param("onset_tol", DECLARED, value=ONSET_TOL, why="seal: nonlinear onset at rel_err > 1e-2"),
])


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def solver_choice():
    p = os.path.join(HERE, "gpu_solver_gate.json")
    if os.path.exists(p) and json.load(open(p)).get("verdict") == "GPU_SOLVER_CERTIFIED":
        return "diff_step_gpu", M.flow_gpu
    return "diff_step (CPU contingency)", M.flow


def hann(W):
    return np.sin(np.pi * (np.arange(W) + 0.5) / W) ** 2


def local_spacing(x):
    h = np.empty_like(x)
    h[1:-1] = 0.5 * (x[2:] - x[:-2])
    h[0], h[-1] = x[1] - x[0], x[-1] - x[-2]
    return h


def project(d, x_lat, n, k, qw, A):
    """Declared gain estimator. Returns dict with gain_c (complex), rel_err, residual_rms."""
    m = n - k
    bi = M.bulk_idx(m)
    idx = np.arange(m)[bi]
    y = (d / local_spacing(x_lat))[bi]
    theta = qw * (idx + 0.5 * k) + PHI
    w = hann(len(idx))
    gain_c = 1j * 2.0 * np.sum(w * y * np.exp(-1j * theta)) / (A * np.sum(w))
    pred = (1.0 - qw / np.pi) ** k
    fit = A * (gain_c.real * np.sin(theta) + gain_c.imag * np.cos(theta))   # Re[-i gain_c e^{i theta}]
    resid = np.sqrt(np.sum(w * (y - fit) ** 2) / np.sum(w))
    return {"gain_re": float(gain_c.real), "gain_im": float(gain_c.imag), "gain_pred": float(pred),
            "rel_err": float(abs(gain_c - pred) / pred), "residual_rms_spacings": float(resid),
            "signal_pred_spacings": float(A * pred)}


def run(n):
    t0 = time.time()
    open(LOG, "a").close()
    solver_name, flow = solver_choice()
    log(f"n={n} solver={solver_name}")
    h_bulk = 2.0 / (n - 1)
    floor_spacings = FLOOR_ULPS * EPS_MACH * 1.0 / h_bulk
    assess_min = floor_spacings / RELERR_TARGET
    # ---- LATTICE run ----
    lat = {}
    D_lat = {}
    seed_lat = M.seed_lattice(n)
    flow(seed_lat, KS, lambda k, r: (lat.__setitem__(k, r.copy()), D_lat.__setitem__(k, M.interlacing_D(seed_lat, r))))
    log(f"lattice flow done ({time.time()-t0:.0f}s)")
    roots = {f"lattice_k{k}": lat[k] for k in KS}
    cells = []
    Dmax = max(D_lat[k] * n / k for k in KS)
    for qw in QW:
        for A in AS:
            seed = M.seed_lattice_wave(n, qw, A, PHI)
            rec = {}
            def on_k(k, r, seed=seed, rec=rec):
                rec[k] = (r.copy(), M.interlacing_D(seed, r))
            flow(seed, KS, on_k)
            for k in KS:
                r, D = rec[k]
                Dmax = max(Dmax, D * n / k)
                p = project(r - lat[k], lat[k], n, k, qw, A)
                p.update(n=n, qw=qw, A=A, k=k,
                         assessable=bool(A * p["gain_pred"] >= assess_min),
                         in_pass_domain=bool(A <= 1e-5 and qw >= 0.1 and p["gain_pred"] >= 1e-8),
                         D_n_over_k=D * n / k)
                cells.append(p)
            if A == 1e-5:
                for k in KS:
                    roots[f"wave_qw{qw}_A{A}_k{k}"] = rec[k][0]
            log(f"qw={qw} A={A:g} done ({time.time()-t0:.0f}s); k=8 gain {rec and cells[-len(KS)+3]['gain_re']:.6f} "
                f"pred {cells[-len(KS)+3]['gain_pred']:.6f} rel {cells[-len(KS)+3]['rel_err']:.2e}")
    # ---- known answers, no dynamics ----
    ka = {}
    ka["LATTICE_omr"] = M.omr(seed_lat, n, 0, "NOUNFOLD")[0]
    for qw in (1.0, 2.0):
        v = M.omr(M.seed_lattice_wave(n, qw, 1e-4, PHI), n, 0, "NOUNFOLD")[0]
        want = (8 * 1e-4 / np.pi) * np.sin(qw / 2) ** 2
        ka[f"LATTICE_WAVE_A1e-4_qw{qw}"] = {"omr": v, "expected": float(want), "rel_dev": float(abs(v - want) / want)}
    for t_flow in (0.0, 64.0 / n):
        k = int(round(t_flow * n)); n_k = n - k
        q = M.seed_qlattice_semicircle(n_k, t_flow)
        v_nu = M.omr(q, n, k, "NOUNFOLD")[0]
        up, dg = M.popref_positions(M.F_semicircle(M.GUE_DE_SEMICIRCLE_SIGMA), q, n, k) if k > 0 else (None, None)
        if k == 0:
            # t_flow = 0: the reference at s=0 is the seed law itself; unfold analytically (kappa = 1)
            up = M.cdf_semicircle(q, M.GUE_DE_SEMICIRCLE_SIGMA) * n_k
            dg = {"note": "s=0: analytic CDF directly (reference_cdf needs k>=1 for its eps rule)"}
        v_po = M.omr(up, n, k, "POPREF", reference="analytic-semicircle")[0]
        ka[f"QLATTICE_semicircle_t{t_flow:g}"] = {"k": k, "NOUNFOLD_omr": v_nu, "POPREF_omr": v_po,
                                                 "POPREF_bar_brief": 1e-10, "POPREF_bar_gateL": 1e-7,
                                                 "popref_diag": dg}
    log(f"known answers: {json.dumps(ka)[:600]}")
    # ---- adjudication ----
    dom = [c for c in cells if c["in_pass_domain"]]
    assess = [c for c in dom if c["assessable"]]
    fails = [c for c in assess if c["rel_err"] > PASS_TOL]
    onset = {}
    for qw in QW:
        for k in KS:
            a_on = [c["A"] for c in cells if c["qw"] == qw and c["k"] == k and c["rel_err"] > ONSET_TOL
                    and c["assessable"]]
            onset[f"qw{qw}_k{k}"] = (min(a_on) if a_on else None)
    ka_ok = (ka["LATTICE_omr"] <= 1e-12
             and all(ka[f"LATTICE_WAVE_A1e-4_qw{q}"]["rel_dev"] <= 0.01 for q in (1.0, 2.0)))
    popref_ok_brief = all(ka[kk]["POPREF_omr"] <= 1e-10 for kk in ka if kk.startswith("QLATTICE"))
    popref_ok_gateL = all(ka[kk]["POPREF_omr"] <= 1e-7 for kk in ka if kk.startswith("QLATTICE"))
    out = {"cell": "gate ML", "n": n, "solver": solver_name, "instrument": INSTRUMENT.seal(),
           "float64_floor_spacings": floor_spacings, "assessable_min_A_times_gain": assess_min,
           "cells": cells, "known_answers": ka,
           "coverage": {"pass_domain_cells": len(dom), "assessable": len(assess),
                        "inapplicable_float64": len(dom) - len(assess)},
           "failures": fails, "n_fail": len(fails),
           "worst_rel_err_assessable": (max(c["rel_err"] for c in assess) if assess else None),
           "nonlinear_onset_A": onset,
           "interlacing": {"max_D_n_over_k": Dmax, "holds": bool(Dmax <= 1 + 1e-12)},
           "known_answers_pass": bool(ka_ok), "popref_qlattice_pass_brief_1e-10": bool(popref_ok_brief),
           "popref_qlattice_pass_gateL_1e-7": bool(popref_ok_gateL),
           "GATE_ML": ("PASS" if (not fails and ka_ok and assess) else "FAIL"),
           "runtime_s": time.time() - t0}
    npz = os.path.join(HERE, "roots", f"ml_{n}.npz")
    os.makedirs(os.path.dirname(npz), exist_ok=True)
    np.savez(npz, **roots)
    out["roots_npz"] = os.path.relpath(npz, M.ROOT); out["roots_npz_sha256"] = M.sha256_of(npz)
    json.dump(out, open(os.path.join(HERE, f"ml_gain_gate_{n}.json"), "w"), indent=1)
    print(f"GATE ML n={n}: {out['GATE_ML']}  fails {len(fails)}/{len(assess)} assessable of {len(dom)} in domain; "
          f"worst rel_err {out['worst_rel_err_assessable']}; known answers {ka_ok}; "
          f"POPREF qlattice <=1e-10: {popref_ok_brief} (<=1e-7: {popref_ok_gateL}); "
          f"interlacing max D n/k {Dmax:.4f}; runtime {out['runtime_s']:.0f}s")
    return out["GATE_ML"] == "PASS" and out["interlacing"]["holds"]


if __name__ == "__main__":
    sys.exit(0 if run(int(sys.argv[1])) else 1)

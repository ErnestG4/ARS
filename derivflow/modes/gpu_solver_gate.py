#!/usr/bin/env python3
"""Certify modes_common.diff_step_gpu BEFORE any ML/MT cell consumes it (RATE_QUESTION_SEAL
post_seal_change_protocol: a changed solver re-runs the affected gates first).
COMMITTED GENERATOR of derivflow/modes/gpu_solver_gate.json.

  G1  Hermite self-map gate (track0_harness.run_hermite_gate) with diff_step swapped for the GPU
      twin — identical constants (N_SEED 512, RAW_TOL 1e-9 vs mpmath dps 40, UNFOLD_MEAN_TOL 0.02).
      Its output JSON is written under derivflow/modes/gpu_gate_scratch/ (cwd trick) so the frozen
      derivflow/track0_hermite_gate.json is never touched; the verdict is copied into this file.
  G2  CPU-vs-GPU root agreement: same seed, both solvers, max |x_gpu - x_cpu| / local spacing
      at every banked k. Bar = RAW_TOL = 1e-9 (the existing gate's own tolerance), on
      IID_UNIFORM n=4096 (child 32) k in K_DENSE, LATTICE_WAVE(qw=1.0, A=1e-5, phi=0.3) n=4096
      k <= 64, and IID_UNIFORM n=16384 (child 96) k <= 8.
  G3  Red path: a deliberately wrong GPU solver (bisection stopped at 10 iterations, no Newton)
      must FAIL G2 — the agreement gate has to be able to fire.
"""
import json
import os
import shutil
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modes_common as M                       # noqa: E402
import track0_harness as TH                    # noqa: E402

OUT = os.path.join(HERE, "gpu_solver_gate.json")
SCRATCH = os.path.join(HERE, "gpu_gate_scratch")
RAW_TOL = TH.RAW_TOL


def scaled_dev(x, ref):
    return TH.scaled_dev(x, ref)


def agreement(seed, ks, step_gpu):
    rc, rg = seed.copy(), seed.copy()
    out = {}
    for k in range(1, max(ks) + 1):
        rc = TH.diff_step(rc)
        rg = step_gpu(rg)
        if k in ks:
            out[k] = scaled_dev(rg, rc)
    return out


def bad_gpu_step(r_np):
    """RED PATH solver: 10 bisections only. Must disagree with the CPU solver far above RAW_TOL."""
    import torch
    r = torch.as_tensor(r_np, device="cuda")
    a, b = r[:-1], r[1:]
    lo, hi = a.clone(), b.clone()
    for _ in range(10):
        mid = 0.5 * (lo + hi)
        s = (1.0 / (mid[:, None] - r[None, :])).sum(1)
        neg = s < 0.0
        hi = torch.where(neg, mid, hi); lo = torch.where(neg, lo, mid)
    return (0.5 * (lo + hi)).cpu().numpy()


if __name__ == "__main__":
    t0 = time.time()
    res = {"RAW_TOL": RAW_TOL, "gates": {}}
    # ---- G1: Hermite self-map gate with the GPU solver ----
    os.makedirs(os.path.join(SCRATCH, "derivflow"), exist_ok=True)
    cwd = os.getcwd()
    TH.diff_step = M.diff_step_gpu
    os.chdir(SCRATCH)
    try:
        verdict = TH.run_hermite_gate()
    finally:
        os.chdir(cwd)
        TH.diff_step = M.diff_step         # restore (module attr only; modes_common keeps both)
    import importlib; importlib.reload(TH)
    g1 = json.load(open(os.path.join(SCRATCH, "derivflow", "track0_hermite_gate.json")))
    res["gates"]["G1_hermite_selfmap_gpu"] = {
        "verdict": g1["verdict"], "fail_reason": g1["fail_reason"], "constants": g1["constants"],
        "worst_dev_vs_mpmath_scaled": max(c["dev_vs_mpmath_scaled"] for c in g1["checkpoints"]),
        "worst_unfold_mean_dev": max(s["unfold_mean_dev"] for s in g1["steps"]),
        "steps_run": len(g1["steps"]), "runtime_s": g1["runtime_s"]}
    shutil.rmtree(SCRATCH)
    # ---- G2: CPU vs GPU agreement ----
    ch = M.seal_children()
    cases = {
        "iid_4096_child32": (M.seed_iid_uniform(ch[32], 4096), M.K_DENSE),
        "lattice_wave_4096_qw1_A1e-5": (M.seed_lattice_wave(4096, 1.0, 1e-5, 0.3), M.K_DENSE),
        "iid_16384_child96": (M.seed_iid_uniform(ch[96], 16384), [1, 2, 4, 8]),
    }
    g2 = {}
    worst = 0.0
    for name, (seed, ks) in cases.items():
        d = agreement(seed, ks, M.diff_step_gpu)
        g2[name] = {str(k): v for k, v in d.items()}
        worst = max(worst, max(d.values()))
    res["gates"]["G2_cpu_gpu_agreement"] = {"per_case": g2, "worst_scaled_dev": worst,
                                             "pass": bool(worst <= RAW_TOL)}
    # ---- G3: red path ----
    seed, ks = cases["iid_4096_child32"]
    dbad = agreement(seed, [1, 2, 4], bad_gpu_step)
    res["gates"]["G3_red_path_bad_solver"] = {"scaled_dev": {str(k): v for k, v in dbad.items()},
                                              "fires": bool(max(dbad.values()) > RAW_TOL)}
    ok = (g1["verdict"] == "PASS") and res["gates"]["G2_cpu_gpu_agreement"]["pass"] \
        and res["gates"]["G3_red_path_bad_solver"]["fires"]
    res["verdict"] = "GPU_SOLVER_CERTIFIED" if ok else "GPU_SOLVER_NOT_CERTIFIED"
    res["runtime_s"] = time.time() - t0
    json.dump(res, open(OUT, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "gates"}, indent=1))
    for g, v in res["gates"].items():
        print(g, json.dumps({kk: vv for kk, vv in v.items() if kk != "per_case"})[:400])
    print("G2 per case:", json.dumps(g2))
    sys.exit(0 if ok else 1)

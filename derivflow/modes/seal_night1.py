#!/usr/bin/env python3
"""Night-1 SEAL for derivflow/modes (BRIEF §3). COMMITTED GENERATOR of seal_night1.json.
Committed via sealgen.sh BEFORE any ML / MT / M3 output exists (verify_seal_order.py pairs).

Everything below is declared here, before ML runs. The smoke cell (M0.10) has been seen — its
numbers are in MANIFEST_M0.json and m0_smoke.json — so every prediction that overlaps it, and
every prediction that overlaps PRIOR_LOOK.md, is graded DECLARED-WITH-PRIOR-LOOK, never SEALED.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modes_common as M                                              # noqa: E402
from modelparams import Model, Param, DECLARED, TESTED                # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def git(*a):
    return subprocess.run(["git", *a], cwd=M.ROOT, capture_output=True, text=True).stdout.strip()


QW_GRID = [0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
A_GRID = [1e-9, 1e-7, 1e-5, 1e-3, 1e-2, 1e-1]
K_ML = [1, 2, 4, 8, 16, 32, 64]
K_MT = [1, 2, 5, 10, 20, 40]
PHI = 0.3
FLOAT64_FLOOR_ULPS = 4.0
FLOAT64_RELERR_TARGET = 1e-3

INSTRUMENT = Model("derivflow production instrument + modes arms (Night 1)", [
    Param("KSTAR_LEVEL", DECLARED, value=M.KSTAR_LEVEL, why="science_rate_question.py:28; k* is its crossing"),
    Param("FIT_WINDOW_MIN", DECLARED, value=M.FIT_WINDOW_MIN, why="science_rate_question.py:27; sealed fit window rule"),
    Param("BULK_FRACTION", DECLARED, value=M.BULK_FRACTION, why="track0_harness.py:32; central window by ROOT INDEX"),
    Param("phi", DECLARED, value=PHI, why="BRIEF: planted phase 0.3; any fixed generic phase serves"),
    Param("hann_taper", DECLARED, value="w_j = sin^2(pi (j+1/2)/W) over the W bulk indices",
          why="BRIEF: Hann taper on the projection; suppresses window-edge leakage"),
    Param("index_shift", DECLARED, value="root i of p^(k) sits at seed index i + k/2",
          why="BRIEF: each derivative moves the root set by half an index"),
    Param("local_spacing", DECLARED, value="h_i = (x_{i+1} - x_{i-1})/2 of the LATTICE run (one-sided at ends)",
          why="BRIEF: convert displacements to local spacings using the LATTICE run's gaps"),
    Param("gain_estimator", DECLARED,
          value="gain_c = i * 2 * sum_j w_j y_j exp(-i theta_j) / (A * sum_j w_j); rel_err = |gain_c - gain_pred| / gain_pred",
          why="complex projection so a phase drift counts as error, not as a smaller real gain"),
    Param("FLOAT64_FLOOR_ULPS", DECLARED, value=FLOAT64_FLOOR_ULPS,
          why="assessability: a cell is FLOAT64-ASSESSABLE iff A*gain_pred >= (1/FLOAT64_RELERR_TARGET) * "
              "FLOAT64_FLOOR_ULPS * eps_mach * max|x| / h_bulk. Below that the 1e-3 bar is not testable "
              "in float64 (the int128 arm the BRIEF intended does not exist in the repo); such cells are "
              "INAPPLICABLE-FLOAT64, never PASS and never FAIL. The empirical residual RMS is reported per cell "
              "so the declared floor is checked against the measured one"),
    Param("solver", DECLARED,
          value="modes_common.diff_step_gpu IF gpu_solver_gate.json reads GPU_SOLVER_CERTIFIED, else track0_harness.diff_step",
          why="same algorithm and precision; GPU makes n=16384 feasible. Contingency if NOT certified: ML n=16384 "
              "restricted to A in {1e-5, 1e-3} and MT flows on CPU (declared now, before the gate result is known)"),
    Param("mt_unfolded_positions", DECLARED, value="F_at * m from reference_cdf (production exposes positions)",
          why="BRIEF: if only gaps were exposed, cumulative sums would be declared; not needed"),
    Param("mt_B_kernel", DECLARED,
          value="Poisson kernel at height eps: B = exp(-qw * eps_sp), eps_sp = eps_k/Delta_s = sqrt(0.25+16(n-k)/(kn)); "
                "PROD_BW1 eps_sp, PROD_BW2 2*eps_sp; B = 1 on PROD_PRIMARY (Richardson)",
          why="BRIEF: B is the arm's smoothing transfer at qw from the kernel recorded in M0.5 (Poisson/Cauchy kernel "
              "has Fourier transform exp(-|q| eps))"),
    Param("m6_bound", DECLARED, value="sharp k/n (Rolle); BRIEF's 2k/(n-k) reported alongside",
          why="MANIFEST_M0 M6_bound_conflict: the looser bound cannot fire on its own red path"),
    Param("p_tail_range", DECLARED, value="k in [16, k_grid_max]; report-only if k_grid_max < 48",
          why="BRIEF M3"),
    Param("bootstrap_resamples", DECLARED, value=200, why="replicate bootstrap for the second error model"),
    Param("kstar_ci_rng", DECLARED, value=12345, why="production kstar() draw seed"),
    Param("qlattice_semicircle_sigma", DECLARED, value=M.GUE_DE_SEMICIRCLE_SIGMA,
          why="read from the production GUE_DE normalisation (KS-minimising sigma = 1.00, MANIFEST_M0 M0.5)"),
])

seal = {
    "seal": "derivflow/modes Night 1 — gates ML/MT, M3 no-reference vs production, M6 interlacing witness",
    "sealed": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
    "brief": "derivflow/modes/BRIEF.md", "brief_sha256": sha(os.path.join(HERE, "BRIEF.md")),
    "prior_look_sha256": sha(os.path.join(HERE, "PRIOR_LOOK.md")),
    "manifest_status_at_sealing": ("MANIFEST_M0.json sha256 " + sha(os.path.join(HERE, "MANIFEST_M0.json"))
                                   if os.path.exists(os.path.join(HERE, "MANIFEST_M0.json")) else
                                   "MANIFEST_M0.json NOT YET WRITTEN: the M0.10 smoke cell was still running at sealing "
                                   "(round 2 of 2, progress log seen through k=11); all M0.1-M0.9 lookups were complete "
                                   "and are recorded in the manifest committed after the smoke cell"),
    "instrument": INSTRUMENT.seal(),
    "seen_before_sealing": [
        "PRIOR_LOOK.md (chat sandbox numbers) — every overlapping cell is DECLARED-WITH-PRIOR-LOOK",
        "m0_smoke progress log: IID_UNIFORM n=4096, per-replicate omr for PROD_PRIMARY / NOUNFOLD / POPREF at "
        "k <= 32 (round 1 complete, round 2 through k=11) — e.g. k=11: PROD ~9.0e-3 vs NOUNFOLD ~3.2e-2; "
        "so the M3 iid n=4096 predictions and branch rule 2 on the smoke cell are DECLARED-WITH-PRIOR-LOOK",
        "the banked science artifacts (science_dense_grid.json, step3_scale_law.json, seed_roster_beta.json)",
    ],
    "blind_at_sealing": [
        "every ML gain measurement; every MT transfer function; the QLATTICE and LATTICE_WAVE known answers "
        "through this code; GUE_DE NOUNFOLD/POPREF at every n; iid NOUNFOLD/POPREF at n != 4096",
    ],
    "ML": {
        "seeds": "LATTICE and LATTICE_WAVE(qw, A, phi=0.3), n in {4096, 16384}",
        "qw_grid": QW_GRID, "A_grid_float64": A_GRID, "k_grid": K_ML,
        "int128_arm": "HELD — no int128 path exists (MANIFEST_M0 M0.6); A in {1e-9, 1e-7} run as float64 twins only",
        "prediction": "gain(qw,k) = (1 - qw/pi)^k",
        "pass_rule": "PASS iff rel_err <= 1e-3 in EVERY cell with A <= 1e-5, qw >= 0.1, (1-qw/pi)^k >= 1e-8 that is "
                     "FLOAT64-ASSESSABLE (declared rule above); cells that are not assessable are listed, counted, "
                     "and the gate's coverage is stated. qw < 0.1 report-only (finite-n corrections ~ k/(qw n))",
        "grade": "SEALED for A >= 1e-5 float64 cells (unseen); the (1 - qw/pi) law itself is DECLARED-WITH-PRIOR-LOOK",
        "nonlinear_onset": "report the smallest A with rel_err > 1e-2, per (n, qw, k)",
        "red_path": "solver with sign(x-r_j)|x-r_j|^-1.2 (exists only inside the checker) must FAIL the gate",
        "known_answers": {
            "LATTICE_omr": "NOUNFOLD omr(LATTICE, k=0) <= 1e-12 at n in {4096, 16384}",
            "LATTICE_WAVE_omr": "A=1e-4, qw in {1.0, 2.0}: NOUNFOLD omr at k=0 within 1% of (8A/pi) sin^2(qw/2)",
            "QLATTICE_semicircle": "t_flow in {0, 64/n}, n in {4096, 16384}: NOUNFOLD omr reported (density-gradient "
                                   "floor ~1/n); POPREF omr <= 1e-10 (BRIEF bar). The repo's own Gate L bar for the "
                                   "same class of check is 1e-7; if 1e-10 fails and 1e-7 holds, that is reported as "
                                   "a BRIEF-vs-instrument conflict, not silently regraded",
        },
        "existing_gates_rerun": "track0_harness (Hermite self-map), reference_v2_gates (lattice + Hermite-through-reference), "
                                "verify_knownanswer (Gate D) — executed in a scratch cwd so no frozen artifact is rewritten; "
                                "verdicts and worst numbers recorded; any FAIL stops the night",
    },
    "MT": {
        "seeds": "LATTICE_WAVE(qw, A=1e-5, phi=0.3) and LATTICE at n=16384", "k_grid": K_MT, "qw_grid": QW_GRID,
        "arms": ["PROD_PRIMARY", "PROD_BW1", "PROD_BW2", "POPREF", "RM1"],
        "definition": "T = P_c(u_wave - u_lattice) / P_c((x_wave - x_lattice)/h_local), complex projections on "
                      "exp(-i theta), theta = qw (i + k/2) + phi, Hann-tapered bulk window; each run unfolded against "
                      "ITS OWN reference (F_empirical of its own seed) exactly as production",
        "expected": {"POPREF": "|T - 1| <= 0.02", "RM1": "|T| <= 0.05 for qw <= 0.1"},
        "prod_prediction": "T_pred = 1 - B exp(k [-ln(1 - qw/pi) - qw/pi]), B per arm as declared (mt_B_kernel)",
        "pass_rule": "PASS iff |T - T_pred| <= 0.1 for every PROD arm at 0.1 <= qw <= 0.5, every k in K_MT; other qw report-only",
        "grade": "SEALED (no MT number has been seen)",
    },
    "M3": {
        "cells": "IID_UNIFORM and GUE_DE x n in {1024, 2048, 4096} x sealed 16 replicates x K_DENSE, identical roots per cell; "
                 "n=16384 NOT RUN tonight (MANIFEST_M0 cuts)",
        "arms": ["PROD_PRIMARY", "PROD_BW1", "PROD_BW2", "NOUNFOLD", "POPREF"],
        "comparator": {"IID_UNIFORM": "NOUNFOLD", "GUE_DE": "POPREF (analytic semicircle, sigma=1)"},
        "banked_per_cell": "per-replicate omr at every k; k* by (a) production F3 ladder + kstar() and (b) monotone "
                           "log-linear interpolation; p_tail over [16, 64]; both error models",
        "predictions": [
            {"P_M3_1": "comparator k* > PROD_PRIMARY k* in every (class, n) cell", "grade": "DECLARED-WITH-PRIOR-LOOK"},
            {"P_M3_2": "NOUNFOLD k*_fit for IID_UNIFORM in [20, 32] at every n", "grade": "DECLARED-WITH-PRIOR-LOOK"},
            {"P_M3_3": "NOUNFOLD p_tail for IID_UNIFORM in [1.35, 1.65] at every n", "grade": "DECLARED-WITH-PRIOR-LOOK"},
        ],
        "lineage": "arms within a cell share roots -> non-independent along 'data' (lineage.Lineage recorded per cell)",
        "f3_ladder_on_comparators": "run, labelled NEW OBJECT (no seal covers its form on these arms)",
    },
    "M6": {"check": "D_k <= k/n at every banked k of every flow (sharp Rolle bound); report max D_k n/k and max D_k (n-k)/(2k) per class",
           "red_path": "one root moved one bracket outward must fire (checker)"},
    "branch_rules": {
        "1": "ML fails, or M0.10 fails to reproduce -> STOP",
        "2": "smoke cell: |k*(NOUNFOLD) - k*(PROD_PRIMARY)| <= 3 sigma_eff AND |p_tail difference| <= 0.15 -> reference "
             "hypothesis DEAD, DROPPED ledger row, Night 2 cancelled (sigma_eff = sqrt(err_cov(NOUNFOLD)^2 + err_cov(PROD)^2))",
        "3": "else if MT passes -> recommend Night 2 (needs Will's go)",
        "4": "else -> recommend a full MT characterisation night",
    },
    "verdict_tokens": ["GATE_ML_PASS|GATE_ML_FAIL", "REFERENCE_IS_MACROSCOPIC|REFERENCE_ABSORBS_AND_INJECTS",
                       "NOUNFOLD_EXCEEDS_PRODUCTION|NOUNFOLD_MATCHES_PRODUCTION", "INTERLACING_BOUND_HOLDS"],
    "token_rules": {
        "GATE_ML": "per ML pass_rule on float64-assessable cells; coverage stated",
        "REFERENCE": "REFERENCE_IS_MACROSCOPIC iff MT PASS and |T_pred - 1| <= 0.1 on all PROD arms at 0.1<=qw<=0.5 for k<=40 "
                     "(i.e. the reference neither absorbs nor injects at the planted scale); else REFERENCE_ABSORBS_AND_INJECTS",
        "NOUNFOLD": "NOUNFOLD_EXCEEDS_PRODUCTION iff branch rule 2 does NOT fire on the smoke cell AND P_M3_1 holds in every run cell",
        "INTERLACING": "INTERLACING_BOUND_HOLDS iff no flow ever exceeds k/n",
    },
    "bindings": {"HEAD_at_seal": git("rev-parse", "HEAD"), "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                 "modes_common_sha256": sha(os.path.join(HERE, "modes_common.py"))},
}
json.dump(seal, open(os.path.join(HERE, "seal_night1.json"), "w"), indent=1)
print(INSTRUMENT.report())
print("wrote seal_night1.json")

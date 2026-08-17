"""Holonomy seal addenda ADD-6 (C4 cell) and ADD-7 (P1 absorption upgrade),
run once, 2026-08-16, under the overnight authorization (items 2 and 3).
COMMITTED GENERATOR of the seal's addenda extension."""

import hashlib
import json

ROOT = "/home/combust/fmexplorer/criticality_tool"
P = f"{ROOT}/holonomy/prereg_sealed.json"


def blob(p):
    d = open(p, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest()


seal = json.load(open(P))
ids = [a["id"] for a in seal["addenda"]]
assert "ADD-6" not in ids, "run-once guard"

seal["addenda"] += [
    dict(
        id="ADD-6", date="2026-08-16",
        title="C4 window<->project measured — the census-found pair closed",
        prediction_first="predict_c4.py written, run, and its output banked "
                         "(c4_prediction.json) BEFORE run_c4.py was written; "
                         "blob SHAs recorded below.",
        observables="commutator observable q = fraction of points whose tile "
                    "membership differs between orderings (the direct, "
                    "unsuppressed quantity); downstream consequence dF(L) "
                    "under MATCHED ordering.",
        no_correctness_leg="BY CONSTRUCTION: both regions are legitimate "
                           "windows and a stationary process is unbiased on "
                           "either, so there is no ground truth for the "
                           "ordering question. Per-ordering F-vs-1 numbers "
                           "are diagnostics only (they also carry the "
                           "estimator's own fixed-N/finite-randoms offset, "
                           "common to both orderings).",
        kag_in_window_corrections=[
            "red demo v1 FIRED RED and halted the run: the non-inertness "
            "argument named the mechanism (data in A_sky, expectations from "
            "A_plane) but missed a suppressor — cells_F's CELL_FLOOR mask "
            "drops exactly the near-zero-expectation cells the mechanism "
            "creates. The §9 non-inertness rule worked as designed even "
            "though my analytic argument was incomplete.",
            "red demo v2: run at the dial top (TILE=30) with a statistical "
            "criterion; fires at z=-41.7 with dF=-0.0544 against a derived "
            "magnitude ~q=0.0523 (4% agreement)."],
        result="law CONFIRMED at tiles 10/20/30 (z=+0.90/+0.77/+1.39); "
               "MISSED at tile 5 (z=+5.57) -> lattice returned "
               "ORDER_RULING_REQUIRED, banked as produced.",
        tile5_attribution="DEMONSTRATED quadrature artifact of the "
                          "PREDICTION, not physics: the sealed NQ=3000 grid "
                          "under-resolves the thin XOR band at small tile. "
                          "Convergence check: q_pred(t=5) = 0.00098 "
                          "(NQ=3000) -> 0.00143 (8000) -> 0.00149 (24000), "
                          "converging on the measured 0.00144 +- 0.00008; "
                          "t=10 was already converged (0.00605 -> 0.00610 "
                          "vs measured 0.00616). Both tiles land on the "
                          "same q/theta^2 ~ 0.79 plateau. The banked "
                          "verdict is NOT retro-changed; the prediction "
                          "upgrade (NQ scaled as 1/tile) is registered.",
        ruling="MATCHED (data and randoms must be cut in the same order) — "
               "the same shape as OP1's MATCHED_LENS. Mechanism real and "
               "predicted (q ~ 0.79 theta^2, 0.6% of points at the deployed "
               "10 deg tile); statistic-level effect suppressed by the "
               "ratio estimator (dF zero-consistent at every dial, max|z| "
               "0.90); materiality clean against survey margins; real-data "
               "point check dF = -0.0004 at q = 0.0045.",
        artifacts=["predict_c4.py", "c4_prediction.json", "run_c4.py",
                   "c4_measured.json"],
        blob_shas={f: blob(f"{ROOT}/holonomy/{f}")
                   for f in ("predict_c4.py", "c4_prediction.json",
                             "run_c4.py", "c4_measured.json")},
    ),
    dict(
        id="ADD-7", date="2026-08-16",
        title="P1 absorption term derived and TESTED — registered attribution "
              "REFUTED, sealed law strengthened out-of-sample",
        derivation="predict_p1_absorption.py: the LS polynomial unfolding "
                   "fit is a linear projection Pi_O, so it absorbs Pi_O eta "
                   "and reduces the sliding-window variance by A_O(L) = "
                   "Var_v[(Pi_O eta)(v+L) - (Pi_O eta)(v)], exact linear "
                   "algebra given the counting covariance C(u,u') = "
                   "0.5[Sigma2(u)+Sigma2(u')-Sigma2(|u-u'|)]. "
                   "Delta_absorb = A_B - A_A > 0 because ordering B fits "
                   "d+1 parameters to the window alone. Parameter-free: no "
                   "constant is fitted to any residual.",
        three_tests=dict(
            T1_in_sample="mean|z| 1.14 -> 1.03, max|z| 7.79 -> 7.70, pass "
                         "count UNCHANGED at 14/15 — helps marginally, does "
                         "not fix the violated cell",
            T2_dial_independence="FALSIFIED at L=10 (flatness chi2 122.5/4 "
                                 "dof), driven entirely by the dial-2.0 "
                                 "residual; flat at L=20 and L=40",
            T3_out_of_sample="6/6 cells pass at two NEW dial values (1.5, "
                             "3.0) under BOTH predictions; amended mean|z| "
                             "0.88 vs trend-only 0.87 — the term is NOT "
                             "resolvable out of sample"),
        finding="The term is REAL (correct sign, parameter-free, magnitude "
                "0.003-0.027) but roughly 80x too small to explain the "
                "violated cell's +0.224 residual. THE SEAL'S REGISTERED "
                "ATTRIBUTION IS THEREFORE REFUTED: the pre-registered "
                "signature matched in SIGN by coincidence, not by "
                "mechanism. A second contribution was measured — the "
                "continuum prediction is ill-conditioned exactly there "
                "(at dial 2.0/L=10 an O(1%) domain-span jitter moves the "
                "prediction across -0.001..+0.061, i.e. more than its own "
                "base value of -0.013) — but that too is ~3.6x short. The "
                "residual remains OPEN and is registered as such.",
        strengthening="Independently of the absorption question, the sealed "
                      "P1 continuum law is now CONFIRMED OUT-OF-SAMPLE at "
                      "two dial values never measured (1.5 and 3.0), 6/6 "
                      "cells at |z| <= 1.51 — a genuine out-of-sample test "
                      "of the trend-tracking law, which the original arc "
                      "did not have.",
        verdict_unchanged="P1's banked verdict (ORDER_RULING_REQUIRED, "
                          "ruled window-then-unfold, RULED_CORRECT) is "
                          "untouched: this addendum refines the attribution "
                          "of one cell's residual, nothing else.",
        artifacts=["predict_p1_absorption.py", "p1_absorption.json",
                   "run_p1_absorption_test.py", "p1_absorption_test.json"],
    ),
]
json.dump(seal, open(P, "w"), indent=1)
print(f"addenda now: {[a['id'] for a in seal['addenda']]}")

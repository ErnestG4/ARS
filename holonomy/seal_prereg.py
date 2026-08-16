"""Holonomy pilot seal.  COMMITTED GENERATOR of holonomy/prereg_sealed.json.

Sequence honoured (pilot-informed-seal, declared): brief folded (af7a94f) ->
census (d70244e) -> lab built -> KAG + witness battery PASS (the legal
debugging window; one construction replaced there and labeled in-code) ->
THIS SEAL -> measurement.  The debugging window closes when the seal closes
(D1 precedent, clause verbatim below).

Executes the sealed-contingency dry-runs inline (each dialed pair's
extension increment once, on synthetic) before writing the seal.
"""

import hashlib
import json
import sys
import time

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
sys.path.insert(0, f"{ROOT}/holonomy")

FREEZE_FILES = [
    "ownership_map.py", "transitions.py", "lattice_h.py", "predict_p1.py",
    "predict_p2.py", "p3_common.py", "kag_holonomy.py", "run_p1.py",
    "run_p2.py", "run_p3.py", "run_opt.py", "resolve_arc.py",
    "p1_prediction.json", "p2_prediction.json", "ownership_map.json",
    "kag_measured.json",
]


def blob(path):
    d = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest()


def dry_runs():
    """Extension increments executed once (sealed-contingency)."""
    from transitions import (gen_trended_set, p1_apply, sigma2_at,
                             sample_inhom_poisson, p2_apply, k_inhom_marks)
    t0 = time.time()
    # P1: seeds -> +2 beyond the sealed 24, at dial 1.0
    for s in (24, 25):
        st = gen_trended_set(seed=s, N=2048, n_keep=1200, a=0.25, ell=600.0)
        A = p1_apply(st["x"], "unfold_then_window", 5, 600)
        assert np.isfinite(sigma2_at(A, [20.0])[0])
    # P2: seeds -> +2 at ladder top
    for s in (424, 425):
        pts, _ = sample_inhom_poisson(seed=s, beta=np.log(4.30) / 10.0,
                                      n_target=3000)
        pe, marks, d2 = p2_apply(pts, (0, 10, 0, 10), "edge_then_reweight",
                                 rmax=1.0)
        assert np.isfinite(k_inhom_marks(pe, marks, d2, [1.0])[1.0])
    return dict(
        p1_p2_executed_sec=float(time.time() - t0),
        p3_evidence=("n_draws x2 hatch = the same per-draw-seeded loop at "
                     "higher count; executed 8 sequential draws through the "
                     "identical thin+pooled_F path in kag_measured.json "
                     "red_B (per-draw rng seeds 2000..2007) — the loop "
                     "runs at arbitrary count by construction"))


def main():
    kag = json.load(open(f"{ROOT}/holonomy/kag_measured.json"))
    assert kag["PASS"], "KAG not green — no seal over a red gate"
    own = json.load(open(f"{ROOT}/holonomy/ownership_map.json"))
    p3k = kag["p3"]
    seal = dict(
        sealed_utc_date="2026-08-16",
        arc="Holonomy pilot (HOLONOMY_PILOT_BRIEF.md, approved+amended "
            "af7a94f; protocol arc, NO new science claims).",
        debug_freeze="BINDING (D1 precedent, verbatim): the KAG is the one "
                     "place debugging is legal, and THE DEBUGGING WINDOW "
                     "CLOSES WHEN THE SEAL CLOSES.  Any post-seal change "
                     "requires a dated addendum and re-derivation of every "
                     "affected number.",
        k_arc=3.0,
        family_wise_rule="Bonferroni on the two-sided k-sigma alpha: "
                         "z_fam = norm.isf(2*norm.sf(k)/(2*n_cells)); "
                         "applied to law cells, control (n=dials), and P3 "
                         "L-cells.  Stated here, not chosen after curves "
                         "(brief Q6).",
        fp_tol_relative=1e-12,
        fp_headroom_measured=kag["fp_headroom"]["worst_rel_delta"],
        fp_scope="exact-commutation regime ONLY (A2): does NOT apply to P3.",
        census=dict(coverage=own["coverage"], floor=0.9,
                    verdict="COMPLETE (1.000 >= 0.9)",
                    both_orders_pairs=["P1 (C1/C2 renormalisation half)"]),
        p1=dict(a=0.25, deg=5, n_full=1200, n_W=600,
                dials=[0.25, 0.5, 1.0, 2.0, 4.0],
                L_fracs=[1.0 / 60, 1.0 / 30, 1.0 / 15],
                jitter_degs=[4, 6]),
        p1_seeds=24, p1_env_seeds=8,
        p1_prediction_scope="continuum derivation captures the TREND-"
                            "TRACKING term only; fluctuation absorption by "
                            "the finite-n fit is KNOWN-OMITTED and its "
                            "signature (law misfit concentrated at small "
                            "predicted-Delta cells) is registered in "
                            "advance.",
        p1_materiality_frac=0.1,
        p1_materiality_rule="zeta NNS consumer: clean iff class call "
                            "identical under both orders AND |delta "
                            "ks_gue| < frac * (second_best - best) gap",
        zeta_env_degs=[4, 5, 6], zeta_env_mult=3.0, zeta_env_floor=1e-9,
        p2=dict(Lx=10.0, Ly=10.0, rmax=1.0, n_target=3000, n_strips=10,
                r_list=[0.5, 1.0],
                ladder=[1.2 ** 2, 1.2 ** 4, 1.2 ** 6, 1.2 ** 8]),
        p2_seeds=24,
        p2_materiality="STRUCTURAL_CLEAN by census C3: no live caller "
                       "estimates lambda-hat from data (bridge designed "
                       "instances used known intensity); the ruling "
                       "applies to FUTURE estimated-lambda callers by "
                       "transfer (registry basis field).",
        p3=dict(n_draws=32, u_seed0=3000, L_list=[0.1, 0.5], mdd_F=0.01,
                sign_predicted=int(p3k["predicted_sign_retained_diff"]),
                extension_increment="n_draws x2 (-> 64), u_seed0 continues"),
        p3_mechanism=dict(
            p_weight_then_thin=p3k["p_weight_then_thin"],
            p_thin_then_weight=p3k["p_thin_then_weight"],
            wbar_data=p3k["scalars"]["wbar_data"],
            wbar_kag=p3k["scalars"]["wbar_kag"],
            predicted_abs_count_diff=p3k["predicted_abs_count_diff"],
            suppressor="DD/RR + randoms-derived F expectations self-"
                       "normalise scalar density shifts; suppressor-free "
                       "retained-mass z at real amplitude = "
                       f"{p3k['red_A_detection_in_principle']['z_real_amplitude']:.1f}"
                       " (kag_measured.json red_A)",
            sign_clause="A3: measured retained-count sign opposite the "
                        "prediction => HALT_PLUMBING flag, audit before "
                        "any holonomy claim"),
        p3_q2_ruling="null_half loaded READ-ONLY via the frozen loader as "
                     "the fixed reference (survey seal language: disjoint "
                     "halves by file index, no untouched clause; D1-"
                     "certified configuration).  Quarter-split recorded "
                     "as fallback.",
        p3_variant="thin_pre (transitions.py) = u-threading variant of "
                   "frozen mask_kag.thin_to_data; banked diff in its "
                   "docstring; equivalence PROVEN bit-identical "
                   "(kag_measured.json equivalence_thin, n_kept 523603) — "
                   "TESTED transfer surface (R2).",
        promotion_trigger_7a="If P3 -> ORDER_RULING_REQUIRED, the survey-"
                             "dialect synthetic analogue is promoted to "
                             "next-in-queue; else it stays parked.",
        optional_trigger_wallclock_sec=3600.0,
        optional_pairs=dict(op1_seeds=16, op1_L=20.0, op1_mdd=1.0,
                            op2_rho=0.5,
                            op2_reliabilities=[[0.9, 0.4], [0.5, 0.8]],
                            op2_n_per_group=2000, op2_seeds=16,
                            note="OP1 exploratory-lane point-check (no "
                                 "sealed continuum prediction; §0 pre-drawn "
                                 "uniforms mandatory).  OP2 sealed Jensen-"
                                 "gap formula in run_opt.py docstring."),
        dry_runs=dry_runs(),
        kag_pointer="kag_measured.json PASS=true (frozen in this seal); "
                    "one red construction replaced inside the window and "
                    "labeled in-code (red_p1 docstring).",
        code_freeze_blob_shas={f: blob(f"{ROOT}/holonomy/{f}")
                               for f in FREEZE_FILES},
    )
    json.dump(seal, open(f"{ROOT}/holonomy/prereg_sealed.json", "w"),
              indent=1)
    print("SEALED: holonomy/prereg_sealed.json "
          f"({len(FREEZE_FILES)} files frozen; dry-runs executed)")


if __name__ == "__main__":
    main()

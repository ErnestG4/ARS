"""Canonical Order Registry — rulings-as-code (TOOLKIT §12's executable half).

Every ruled order lives HERE as data; call sites assert through
assert_canonical() instead of re-deciding order script-by-script.  Prose
copies of these rulings (TOOLKIT §12, COMMUTATOR_TABLE.md) cite this module
as the owner; if they ever disagree, THIS FILE wins and the prose is the
defect.

Ruling-basis vocabulary (brief §4):
  RULED_CORRECT              bias separated where measured; applied there
  RULED_CORRECT_BY_TRANSFER  bias separated on a synthetic analogue;
                             applied to a substrate where truth is absent
  RULED_CONSISTENT           truth absent or biases inseparable; order
                             fixed for coordination only
"""

CANONICAL = {
    # P1 — ORDER_RULING_REQUIRED (census C1/C2 both-orders + law cell)
    "unfold_window_1d": dict(
        order="window_then_unfold",
        basis="RULED_CORRECT",
        transfer_note="RULED_CORRECT on trended-GUE synthetic (bias 0.09 vs "
                      "4.85 at dial 1.0 L20, >100 sigma); "
                      "RULED_CORRECT_BY_TRANSFER at zeta call sites (no "
                      "ground truth there; re-derivation showed both orders "
                      "give identical NNS class calls, delta KS ~5e-14)",
        statement="Estimate/normalise the unfolding on the ANALYSIS WINDOW, "
                  "not on the pooled set.  compute_nns's internal unit-mean "
                  "renormalisation (census C1) self-enforces this for NNS "
                  "consumers as a MECHANISM (the renorm is unconditional in "
                  "code) — but the both-orders-equivalence DATUM is "
                  "zeta-window-only (seal ADD-4); other substrates inherit "
                  "the mechanism, not the measurement.  Sigma^2 consumers "
                  "have no self-enforcement and must window first or "
                  "re-unfold per window.",
        measured="holonomy/p1_measured.json, arc_verdicts.json P1"),
    # P2 — COMMUTATOR_MEASURED; ruling pre-positioned for future callers
    "reweight_edge_2d": dict(
        order="edge_then_reweight",
        basis="RULED_CORRECT",
        transfer_note="synthetic inhomogeneous Poisson, exact truth "
                      "K=pi r^2; applies BY TRANSFER to any future caller "
                      "that estimates lambda-hat from data (census C3: no "
                      "such live caller exists today; k_inhom with GIVEN "
                      "lambda is unaffected)",
        statement="Fit lambda-hat on the ERODED (post-edge) domain the "
                  "statistic will actually integrate over.",
        measured="holonomy/p2_measured.json law_agrees=true"),
    # P3 — POINT_CHECK_CLEAN: no ruling forced; row records mechanism+suppressor
    "weight_thin_survey": dict(
        order="weight_then_thin",
        basis="RULED_CONSISTENT",
        transfer_note="frozen live semantics kept as canonical for "
                      "coordination; no truth leg in this pilot (survey "
                      "synthetic analogue parked per sealed trigger 7a, "
                      "which did NOT fire)",
        statement="POINT_CHECK_CLEAN at sealed points/power ONLY — claims "
                  "no detectable order effect at L in {0.1,0.5} deg, 32 "
                  "draws, MDD_F 0.0018; asserts NO law, NO off-point "
                  "behaviour.  Mechanism REAL (nested keep-sets, -10003 "
                  "counts/draw, 12 sigma suppressor-free); cleanliness is "
                  "OWNED BY the ratio/self-normalising estimator family — "
                  "a refactor abandoning DD/RR-style normalisation does "
                  "NOT inherit this row.",
        measured="holonomy/p3_measured.json"),
    # OP1 — measured non-commutation; ruling REVISED under seal addendum
    # ADD-3 (original 'unfold_then_surrogate' RETRACTED: it would break the
    # matched-lens design the live sites implement deliberately)
    "surrogate_unfold_1d": dict(
        order="matched_lens",
        basis="RULED_CONSISTENT",
        separation_status="UNDER_RESOLVED",
        separation_note="NOT a genuine null: direction confirmed in BOTH "
                        "correctness runs (mixed order biases marginal-"
                        "class data rigid-ward), separation ~1.4 sigma — "
                        "under-resolved at k=3, not absent.  The pre-"
                        "committed rerun is consumed; no second bite.  A "
                        "future arc with a sharper comparator may upgrade "
                        "this to RULED_CORRECT; a reader must not cite it "
                        "as evidence the orders are equivalent.",
        transfer_note="bare-pair Delta Sigma^2(20) = +1.15 +- 0.23 (z=4.9) "
                      "is REAL; materiality vs the RIGID_GUE gate NOT clean "
                      "under the worst-case screen (margin 1.4x < k=3, "
                      "op1_materiality.json) -> correctness leg RUN "
                      "(op1_correctness.json): direction favors matched-"
                      "lens in both runs (mixed order biases marginal-class "
                      "data rigid-ward, z -0.32 vs -0.04) but separation "
                      "0.28+-0.20 < k=3 — biases do not separate at arc "
                      "power; site-specific verdict-level effect ~0.3 sigma "
                      "of the classification band",
        statement="The ruled invariant is MATCHED LENS: a surrogate/null "
                  "and the data it nulls must pass the IDENTICAL unfolding "
                  "apparatus (live sites already do — "
                  "longrange_discriminator '# same lens', "
                  "local_rate_unfold readouts).  No bare sequence order is "
                  "enforced; breaking lens-matching in either direction is "
                  "the violation.",
        measured="holonomy/opt_measured.json op1 + op1_materiality.json + "
                 "op1_correctness.json (seal ADD-1/ADD-3)"),
    # C4 — census-found pair, measured 2026-08-16 under seal ADD-6
    "window_project_survey": dict(
        order="matched",
        basis="RULED_CONSISTENT",
        separation_status="NO_TRUTH_BY_CONSTRUCTION",
        separation_note="both regions are legitimate windows and a "
                        "stationary process is unbiased on either, so the "
                        "ordering question has no ground truth and no "
                        "correctness leg exists to separate the arms — this "
                        "is a structural absence, not an under-resolved "
                        "measurement (contrast surrogate_unfold_1d).",
        transfer_note="mechanism REAL and predicted: q ~ 0.79*theta^2, i.e. "
                      "0.6% of points change tile membership at the "
                      "deployed 10 deg tile (law confirmed at tiles "
                      "10/20/30, z=+0.90/+0.77/+1.39; the tile-5 miss is a "
                      "demonstrated quadrature artifact of the prediction, "
                      "seal ADD-6). Statistic-level effect SUPPRESSED by "
                      "the ratio estimator: dF zero-consistent at every "
                      "dial (max|z| 0.90), real-data point check dF=-0.0004 "
                      "at q=0.0045. Suppression is owned by the "
                      "DD/RR-style estimator AND by cells_F's CELL_FLOOR "
                      "mask — a refactor dropping either does not inherit "
                      "this row.",
        statement="Cut and project in the SAME order for data and randoms. "
                  "No bare sequence order is enforced; breaking the match "
                  "in either direction is the violation (mismatched "
                  "ordering inflates F by ~q: measured -0.0544 at TILE=30 "
                  "against a derived -0.0523).",
        measured="holonomy/c4_measured.json + c4_prediction.json "
                 "(seal ADD-6)"),
    # OP2 — sealed-formula law confirmed
    "disattenuate_pool": dict(
        order="disattenuate_then_pool",
        basis="RULED_CORRECT",
        transfer_note="truth by construction (latent rho known); pooled-"
                      "then-disattenuated is biased by the Jensen factor "
                      "mean_g sqrt(RxgRyg)/sqrt(Rxbar Rybar), formula "
                      "confirmed z=0.64",
        statement="Disattenuate within reliability-homogeneous groups, "
                  "THEN pool.",
        measured="holonomy/opt_measured.json op2"),
}


def assert_canonical(pair_key, order):
    """Call-site guard: raises if `order` contradicts a ruled order."""
    row = CANONICAL.get(pair_key)
    if row is None:
        raise KeyError(f"unregistered pair '{pair_key}' — add a ruling or "
                       "measure it (HOLONOMY_PILOT_BRIEF.md §3)")
    if order != row["order"]:
        raise AssertionError(
            f"order '{order}' contradicts canonical '{row['order']}' for "
            f"{pair_key} ({row['basis']}; see {row['measured']})")
    return True


if __name__ == "__main__":
    for k, v in CANONICAL.items():
        print(f"{k}: {v['order']}  [{v['basis']}]")

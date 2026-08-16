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
                  "renormalisation (census C1) already self-enforces this "
                  "for NNS consumers; Sigma^2 consumers must window first "
                  "or re-unfold per window.",
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
    # OP1 — exploratory, measured non-commutation
    "surrogate_unfold_1d": dict(
        order="unfold_then_surrogate",
        basis="RULED_CONSISTENT",
        transfer_note="no truth leg in this pilot; rationale: surrogates "
                      "belong in the coordinate frame where the null is "
                      "defined (unfolded).  Delta Sigma^2(20) = +1.15 +- "
                      "0.23 (z=4.9) — a REAL non-commutation; any future "
                      "live surrogate machinery must consult this row",
        statement="Generate surrogates AFTER unfolding, in the unfolded "
                  "frame.",
        measured="holonomy/opt_measured.json op1"),
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

"""
phase35a/sharpening_sensitivity.py — Step-1 SHARPENING RUN (Will authorized
2026-05-18). Non-circular *sensitivity* validation of transition_diagnostic's
sub-quadrant axis: the no-false-positive half is non-circular and banked, but
sensitivity (does it separate genuinely-distinct regimes) still rested on the
circular Phase-20.5 calibrators. This puts it on non-circular footing.

EXACT path (not heuristic discriminant #6; per memory
discriminant_exact_question_check, pre-flight applied — see header in the
report). The α-null's finite-N φ-dependence is DETERMINISTIC golden-mean
continued-fraction structure (35b showed period 0.5 in φ): a dense φ-grid
over [0,0.5) characterises the finite-N α-ensemble EXACTLY (no estimation —
it is the actual deterministic family), + a few φ in [0.5,1) re-confirm the
period as a sanity check.

EXACT SUBSTANTIVE QUESTION: across the *proven* λ=1 boundary (regimes
anchored by the proven boundary, NOT fitted), is the sub-quadrant statistic
W1δ's separation between the subcritical and supercritical regimes larger
than the substrate-generated α-ensemble's own exactly-characterised finite-N
φ-spread within each regime?

CODED TEST = that question: per-regime exact α-ensemble of W1δ over the
dense φ-grid; PASS iff the two ensembles are strictly DISJOINT and the
inter-regime gap ≥ the larger within-regime φ-range (separation dominates
the *entire* span the null can produce). No tuned threshold; the bar is
"separation exceeds anything the substrate-generated null does."

SCOPING / arc-finish (tooling-confidence: non-circular sensitivity). NOT a
discovery, NOT §3, no stamping, Class II blocked.
"""
from __future__ import annotations
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from unfold_rotnum import am_eigs, unfold_rotnum, W1d, GOLDEN

NCELL, LITER = 2584, 1_000_000                 # validated-converged leg regime
LAM_SUB, LAM_SUP = 0.50, 1.50                  # proven-λ=1-anchored regimes (not fitted)
PHIS_MAIN = list(np.round(np.linspace(0.0, 0.5, 24, endpoint=False), 5))   # exact: period-0.5
PHIS_PERIOD_CHECK = [0.50, 0.625, 0.75, 0.875]  # re-confirm period-0.5


def alpha_ensemble(lam, phis):
    out = {}
    for phi in phis:
        e = am_eigs(lam, NCELL, phi)
        out[round(phi, 5)] = round(W1d(unfold_rotnum(e, lam, GOLDEN, LITER,
                                                      phis=(phi,))), 6)
    return out


def run():
    print("=" * 80)
    print("SHARPENING RUN — non-circular sensitivity (EXACT α-null characterisation)")
    print(f"  N={NCELL} L_iter={LITER} ; λ_sub={LAM_SUB} λ_sup={LAM_SUP} (proven-λ=1-anchored)")
    print(f"  dense φ-grid [0,0.5) n={len(PHIS_MAIN)} (exact, period-0.5 deterministic)")
    print("=" * 80)

    sub_e = alpha_ensemble(LAM_SUB, PHIS_MAIN)
    print(f"  subcritical λ={LAM_SUB}: α-ensemble W1δ characterised "
          f"({len(sub_e)} φ)", flush=True)
    sup_e = alpha_ensemble(LAM_SUP, PHIS_MAIN)
    print(f"  supercritical λ={LAM_SUP}: α-ensemble W1δ characterised "
          f"({len(sup_e)} φ)", flush=True)
    # period-0.5 sanity (φ and φ+0.5 should match within finite-L noise)
    sub_pc = alpha_ensemble(LAM_SUB, PHIS_PERIOD_CHECK)
    per_dev = max(abs(sub_pc[p] - sub_e[round(p - 0.5, 5)])
                  for p in [0.5, 0.625, 0.75, 0.875]
                  if round(p - 0.5, 5) in sub_e)

    sv = np.array(list(sub_e.values())); pv = np.array(list(sup_e.values()))
    sub_rng = float(sv.max() - sv.min())
    sup_rng = float(pv.max() - pv.min())
    disjoint = float(sv.max()) < float(pv.min())
    gap = float(pv.min() - sv.max())                 # >0 iff disjoint
    larger_within = max(sub_rng, sup_rng)
    # EXACT criterion: disjoint AND separation dominates the entire null span
    sensitivity_validated = bool(disjoint and gap >= larger_within)

    print("\n" + "=" * 80)
    print("EXACT α-NULL CHARACTERISATION + NON-CIRCULAR SENSITIVITY TEST")
    print(f"  subcritical λ={LAM_SUB}: W1δ ∈ [{sv.min():.5f}, {sv.max():.5f}] "
          f"mean={sv.mean():.5f}  φ-range={sub_rng:.5f}")
    print(f"  supercritical λ={LAM_SUP}: W1δ ∈ [{pv.min():.5f}, {pv.max():.5f}] "
          f"mean={pv.mean():.5f}  φ-range={sup_rng:.5f}")
    print(f"  period-0.5 sanity: max|W1δ(φ+0.5)−W1δ(φ)| = {per_dev:.6f} "
          f"(finite-L noise scale)")
    print(f"  ensembles disjoint = {disjoint} ; inter-regime gap = {gap:.5f} ; "
          f"larger within-regime φ-range = {larger_within:.5f}")
    print(f"  EXACT CRITERION (disjoint AND gap ≥ larger φ-range): "
          f"{'PASS' if sensitivity_validated else 'FAIL'}")
    verdict = ("SENSITIVITY_VALIDATED_NON_CIRCULAR — the sub-quadrant axis "
               "separates the proven subcritical/supercritical regimes by more "
               "than the substrate-generated α-ensemble's exact finite-N "
               "φ-spread" if sensitivity_validated else
               "SENSITIVITY_NOT_ESTABLISHED — separation does not dominate the "
               "exact α-null span (inspect; no auto-adjudication of next steps)")
    print(f"\n  VERDICT: {verdict}")
    print("  SCOPING/tooling-confidence. NOT a discovery, NOT §3, no stamping.")
    print("=" * 80)
    json.dump({"scoping_arc_finish": True, "exact_path": True,
               "leg": "unfold_rotnum VALIDATED",
               "lam_sub": LAM_SUB, "lam_sup": LAM_SUP, "N": NCELL, "L": LITER,
               "subcritical_alpha_ensemble": sub_e,
               "supercritical_alpha_ensemble": sup_e,
               "period_check_max_dev": round(per_dev, 6),
               "sub_phi_range": round(sub_rng, 6), "sup_phi_range": round(sup_rng, 6),
               "disjoint": disjoint, "inter_regime_gap": round(gap, 6),
               "exact_criterion": "disjoint AND gap >= max(within-regime φ-range)",
               "sensitivity_validated": sensitivity_validated, "verdict": verdict},
              open(os.path.join(HERE, "sharpening_sensitivity_results.json"), "w"),
              indent=1)


if __name__ == "__main__":
    run()

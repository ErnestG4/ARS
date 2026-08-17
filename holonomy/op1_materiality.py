"""OP1 margin-denominated materiality pass — COMMITTED GENERATOR of
holonomy/op1_materiality.json.

THREE-EVENT LABEL (post-banking, addendum-covered):
  (1) 2026-08-16 arc banked with OP1 lacking this pass — a defect: brief §2
      owes a materiality check to every pair with |Delta| above tolerance,
      and OP1's Delta Sigma^2(20) = +1.15 +/- 0.23 qualifies;
  (2) the post-arc audit flagged the omission (same day);
  (3) this pass, run under dated addendum ADD-1.

Scope note: 1-D surrogate call sites live OUTSIDE the sealed census
enumeration (stated at census time).  This pass enumerates them by targeted
search and computes the nearest downstream margin THROUGH THE CONSUMER'S OWN
MODULE (cross_substrate/longrange_discriminator.py), not from its docstring.

Call-site census (OP1 scope):
  * cross_substrate/longrange_discriminator.py:209 — references built with
    "# same lens": surrogate/decoy/data ALL pass the identical unfold stage
    (order B, surrogate-then-unfold, MATCHED-LENS by design).
  * cross_substrate/goes_flares.py:162-170, comcat_port.py:72-114 —
    local_rate_unfold applied to data and rate-matched surrogate readouts
    through the same lens (matched-lens; CV/mass readouts, not Sigma^2
    gates).
  * cross_substrate/quadrant_marginal_test.py:122-158 — marginal surrogate
    built FROM already-unfolded zeta (order A trivially; no second lens).
  * cross_substrate/rf_decoy_battery.py:43 — self-declares "does NOT touch
    the spacing path"; out of scope by its own line.

The materiality question: could the OP1 order effect (a surrogate arm
shifted by |Delta| ~ 1.15 in Sigma^2(20) under the opposite order) flip any
banked verdict?  The binding boundary is the discriminator's RIGID_GUE line
(gue_mean + 2.5 * gue_sd): a marginal-preserving surrogate must never cross
it.  Clean iff (nearest surrogate-arm value - rigid boundary) >= k * |Delta|
with the arc's sealed k = 3.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (ROOT, f"{ROOT}/cross_substrate", f"{ROOT}/holonomy"):
    if p not in sys.path:
        sys.path.insert(0, p)

DELTA_OP1 = 1.1499704516334017          # opt_measured.json op1 mean
K_ARC = 3.0
N, L, SEEDS, DEG = 1200, 20.0, 8, 6


def main():
    from longrange_discriminator import (_reference_ensembles,
                                         wigner_renewal, longrange_stats)
    gue, pois = _reference_ensembles(N, L, SEEDS, DEG, None)
    rigid_boundary = gue["sigma2"]["mean"] + 2.5 * gue["sigma2"]["sd"]
    ren = []
    for k in range(SEEDS):
        rng = np.random.default_rng(9100 + k)
        st = longrange_stats(wigner_renewal(N, rng), L, unfold_deg=DEG)
        ren.append(st["sigma2"])
    ren = np.array([r for r in ren if r is not None])
    nearest_surrogate_arm = float(ren.min())
    margin = nearest_surrogate_arm - rigid_boundary
    clean = bool(margin >= K_ARC * abs(DELTA_OP1))
    out = dict(
        three_event_label=["banked-without-pass 2026-08-16",
                           "flagged by the audit 2026-08-16",
                           "run under addendum ADD-1"],
        consumer="cross_substrate/longrange_discriminator.py (RIGID_GUE "
                 "gate; matched-lens references, '# same lens')",
        n=N, L=L, seeds=SEEDS, unfold_deg=DEG,
        gue_band=gue["sigma2"], poisson_band=pois["sigma2"],
        rigid_boundary=float(rigid_boundary),
        renewal_sigma2=dict(mean=float(ren.mean()), min=nearest_surrogate_arm,
                            sd=float(ren.std(ddof=1))),
        delta_op1=DELTA_OP1,
        margin_to_rigid=float(margin),
        margin_over_delta=float(margin / abs(DELTA_OP1)),
        clean=clean,
        structural_note="Live sites are MATCHED-LENS (surrogate rides the "
                        "identical unfold as data), so the OP1 absorption is "
                        "common-mode to first order; the margin above is the "
                        "worst case (full |Delta| applied to one arm).")
    json.dump(out, open(f"{ROOT}/holonomy/op1_materiality.json", "w"),
              indent=1)
    print(f"OP1 materiality: renewal min {nearest_surrogate_arm:.2f} vs "
          f"RIGID boundary {rigid_boundary:.3f} -> margin {margin:.2f} = "
          f"{margin / abs(DELTA_OP1):.1f}x |Delta| (need >= {K_ARC}) -> "
          f"clean={clean}")
    # exit 0 = generated + banked; the clean flag is DATA (pinned by
    # verify_holonomy) — a permanently-red generator would be an inert row.


if __name__ == "__main__":
    main()

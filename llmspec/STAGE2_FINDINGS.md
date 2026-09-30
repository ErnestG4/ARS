# Stage 2 findings — G7 multi-peak calibrator (brief v1.1 §5 G7)

**Pre-registration:** stage2_g7.py docstring (b1ca2b6).

**Targets:** the 34 OLMo 2 1B stage-1-end W_Q heads flagged multimodal by the licensed dip test (Stage 1b;
x ≥ 0.1). Gaussian-mixture fits gave K = 2: 21 heads, 3: 5, 4: 7, 5: 1. N = 128 per spectrum, 34 spectra pooled,
R = 20 replicate pools, plus the unimodal-control family.

## Verdict
- **As registered: NOT LICENSED.** No unfolding setting passes every class (a–d) on both families. So
  Brody-q-style local statistics on peaked attention spectra are not licensed, and aim-1 results are restricted
  to the density level: peak count, positions and widths.
- **Raw-x ⟨r̃⟩ (no unfolding): LICENSED** on both families. Its largest deviation from the oracle is 0.0037
  (β=2), within the 0.01 tolerance.
- **Unfolded ⟨r̃⟩:** within tolerance for kde(2–8), local(4–8), spline(8–32) and poly(3–15). Poly and spline fail
  q through the non-monotone rule.

## Where it fails (peaked family, Δq vs oracle)
- **Poly and spline:** β=1 and β=2 are dragged strongly toward clustering (Δq −0.4 to −1.4). Smooth staircase
  fits leave the peak modulation in the spacings, which is exactly the failure G7 was built to catch. These
  families also go non-monotone (2–7% non-positive spacings).
- **kde(1–2):** over-smooths the other way. Poisson reads repulsive (+0.16 to +0.38).
- **kde(4–8) and local(3):** pass Poisson, β=1 and both Neyman–Scott classes, but **fail β=2** (Δq −0.17 to
  −0.22), so β=2 would read as ~β=1.
  - kde(6) and kde(8) also pass the unimodal control on (a)–(c).
  - **Post-hoc sensitivity (NOT adopted):** restricted to the brief's required classes (a)–(c), dropping the
    optional (d), kde(6)/kde(8) would be licensed for "clustering vs β=1 vs Poisson" on peaked spectra, but not
    for β=1 vs β=2. Relaxing the registered pass rule after seeing results is Will's call, not mine.

## Zoo
- The four synthetic classes (Poisson / COE β=1 (+ Wishart-MP) / Neyman–Scott ×2 / CUE β=2, mapped through
  real-head peak mixtures) are defined in stage2_g7.py.
- Seating them in calibrator_panel.py (TIERS, `_schema_self_check`) was left for the branch-merge session.
  **2026-09-30: DEFERRED explicitly at that merge** (not seated in the published main). The reasons and
  requirements are in FINDINGS_MEMO §5 and NOTES.

## Output
- results/g7_olmo_stage1end_Q.json
- results/g7_targets_olmo_stage1end_Q.npz

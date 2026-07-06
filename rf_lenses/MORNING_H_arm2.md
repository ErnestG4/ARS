# MORNING_H (Arm 2) — the ⅓ genus-0 refit: INDISTINGUISHABLE at current precision

Branch `third-refit` off main. Banked A2 β data only (no new machinery; F clarified ⅓ is a genus-0 question).
main/refsuite untouched. Artifacts: `rf_lenses/third_refit.json`.

## Layer-zero
Banked A2 genus-0 β dataset (the certified CV≤0.11, three-base-field set): β means 0.228/0.379/0.534 at q=2,3,5.
No new measurement.

## Model comparison (β vs log₁₀q, through origin) — free slope vs 0.760 vs 0.7675
The ⅓ candidate is β=(⅓)ln q ⇒ slope **0.7675·log₁₀q**; the empirical A2 value is **0.760**.

- **Per-q robust slopes (β/log₁₀q, OLS+Theil–Sen):** 0.759 (q=2), 0.769 (q=3), **0.797 (q=5)** — they **rise with q**.
- **Honest CI (3 base fields as the independent unit):** mean slope 0.775, 95% CI (t, dof=2) = **[0.726, 0.824]**.
  **Both 0.760 and 0.7675 are inside** ⇒ indistinguishable.
- **Caveat on the tighter number:** a naive per-config fit (n=12: 2 estimators × 2 deg × 3 q) gives 0.785±0.005,
  CI [0.775,0.795], which excludes both — but that CI is **over-tight**: OLS and Theil–Sen at the same (q,deg) are
  correlated, so the effective n is 3 (the base fields), not 12. The honest CI is the 3-field one.

## Verdict — **INDISTINGUISHABLE; ⅓ neither supported nor refuted**
At 3 base fields the data cannot separate 0.760 from 0.7675 (0.008 apart, honest CI ±0.05). **And** the per-q slope
**trends upward** (+0.10 per unit log₁₀q) — the through-origin *constant*-slope model is itself imperfect, which
further muddies any exact-constant identification. So ⅓ stays **empirical-unresolved**, exactly the spec's third
outcome. This is a **verify-then-claim hold**, not a promotion.

**What would resolve it (future ask, not a build here):** add base fields **q=7,11,13** to the genus-0 𝔽_q[T]
calibrator (A2's own machinery — a genus-0 refit, cheap) *and* test the constant-slope assumption (fit β = a + s·log₁₀q,
or check curvature) — the upward per-q trend must be understood before ⅓ (or any closed form) can be claimed.

## Close
Committed on `third-refit`; main/refsuite untouched. Carry-forward: the genus-0 β refit at q=7,11,13 + the
constant-slope check is the concrete next step for ⅓; F's curve-function-field Ramanujan-sum build stays deferred
(it was never the ⅓ route).

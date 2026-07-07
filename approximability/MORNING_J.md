# MORNING_J — the cubics close the a=2 corner: g̃(a,f) is SUBSTRATE-UNIVERSAL; the G→J arc is complete

Branch `cubics-wilderness` off `e-magnitude-probe`. numba fast solver. main/refsuite untouched.
Artifacts: `J_prereg_SEALED.json`, `J_measure.py`, `J_measured.json`, `J_verdict.json`, `J_rule1_clean.json`,
`J_magnitude_universal.png`. **All 3 rules were byte-locked before the blind measurement.**

## Layer-zero (all passed)
1. **13 genuine irreducible cubics** (minimal polys printed): ∛2,3,4,5,6,7,9,10,11,12 (x³−k), plastic (x³−x−1),
   ∛2+1 (x³−3x²+3x−3), root of x³−3x−1 — non-periodic generic CFs (Lagrange), can't accidentally flatten.
2. **CFs computed not asserted** (unpredictable); reach budget stated: Lévy q≈3.28ⁿ, cap q<60k (covers every a=2
   step incl the high-f bracket q=317–1201). 85 steps measured.
3. **q=2 Floquet degeneracy caught on a pre-statable rule** (exclude q_{n−1}≤2 → W=0 → factor=0): one point
   (cbrt4@0.200) removed; cbrt4's *other* a=2 point agrees with the fifth to 4 decimals, so the substrate is sound.

## The three pre-registered tests — all PASS
### RULE 1 — the a=2 corner CLOSES
- **1a Collapse (well-powered):** 18 cubic+fifth a=2 points, matched-f, on **one monotone g̃(2,f)**, resid RMS
  **0.011** (< 0.043). Matched-f agreements near-exact: cbrt4/fifth = 0.622 @ f=0.167; fifth/cbrt10/cbrt11 = 0.684
  @ f≈0.20. → **PASS: a=2 is universal in form.**
- **1b π-anomaly (1-pt discriminator, pre-registered indicative):** cbrt11@0.264 = **0.873 > 0.81** → **π ON the
  curve**; the collapse fit at f=0.25 = 0.819 vs π 0.844 (gap +0.025, within band). **π's 0.844 was never anomalous.**
- **This closes the sole open sliver from I.** H's "a=2 split 0.844 vs 0.638" was the *same f-distribution confound*
  as the a=1 ~30% — π sampled a=2 at f=0.25, the fifth at f≤0.20, on a steep curve. Matched by f they coincide.

### RULE 2 — a=1 universality survives the wilderness
34 generic-CF cubic a=1 points vs the sealed I curve g̃(1,f): resid RMS **0.0215** (< 0.043), max per-substrate
offset **0.0234** (< 0.064). **PASS.** g̃(1,f) universality is **not** an artifact of special/patterned substrates —
it holds on statistically-generic non-periodic CFs. (This was the higher-value banked result: a universal law
surviving the wilderness.)

### RULE 3 — direction law survives the wilderness
`DROP iff ln(factor) > (1/dim_{n−1}−1)·ln(a/(1−f))` on cubic steps: **68/68 decidable correct (100%)**, 4
near-crossover steps (|margin|<0.10) excluded as pre-registered undecidable. **HOLDS.** The H closed-form direction
law (17/17 on special substrates) generalizes cleanly to generic CFs.

## Verdict — the finite-depth trajectory is FULLY CF-derivable; the G→J arc is complete
Across G→H→I→J the band-scaling-dimension trajectory has gone from "monotonicity is a substrate mystery" to fully
determined by the continued fraction:
- **Direction:** closed-form law in (a, f, dim), 17/17 (special) + 68/68 (generic cubics).
- **Magnitude:** a single substrate-universal surface **g̃(a,f)** — a=1 (I) and a=2 (J) both collapse across
  π+fifth+e+13 cubics; **no substrate-local component survives.** The ~30% scatter H reported (both a=1 and a=2) was
  entirely the f-distribution confound on a steep surface.

There is **no residual substrate-memory** in the finite-depth magnitude. The trajectory is set by the CF (the a_n
sequence and older-block fractions f_n) and the running dim — full stop.

## Close / carry-forward
- The finite-depth program is **complete**. The magnitude-origin question (the analytic form of g̃(a,f)) is now a
  clean *derivation* target, not an empirical one — and it's substrate-independent, so it's a property of the
  Sturmian-block renormalization itself (Thouless/DEGT), addressable analytically, no more substrates needed.
- **Natural next frontier is OFF-trajectory** (a different observable, not more CF depth): (a) the λ-dependence of
  g̃(a,f) — we fixed λ=8 throughout; does the universal surface carry λ as a parameter? (b) the long-range Σ²/Δ₃
  universality *class* the marginal g̃ does not see ([[nns_certifies_marginal_not_class]]) — the band spectrum's
  spectral-statistics class, a genuinely different question.
- Cubic deep tails (q>60k) parked (O(q²) wall). H-Arm2 ⅓ and the FF Ramanujan build stay deferred.
- The scout's Gauss-metric efficiency (carry-forward from the theory read) has its favorable regime exactly here —
  the generic cubic bulk (multifractal τ_D(α)≈1) — if it ever gets built, these substrates are its cheapest proving
  ground.

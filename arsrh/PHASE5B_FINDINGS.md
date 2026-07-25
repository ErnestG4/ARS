# Phase 5b — leverage vs sensitivity, and P1's corroboration line re-derived

`phase5b_leverage.py`, `phase5b_leverage_measured.json`. §0 held. **Not a re-run of Phase 5's G2 and
not a rescue of its seal** — Phase 5's sealed predictions remain unscored and its halt stands.

## 0. The premise correction, in the reviewer's disfavour and mine

The proposed inference was: *the designed GUE-vs-super-rigid contrast at L=1 is 0.0007, so Σ²(1) is
nearly blind to the structural difference the heterogeneity confound consists of, so the confound has
almost no leverage on a short-L reading.*

**The conclusion is right. The number does not support it.** Measured ladder, Σ²(1), N=500, 12 realizations:

| class | lattice η=0.02 | 0.05 | 0.10 | 0.20 | 0.30 | 0.50 | GUE | Poisson |
|---|---|---|---|---|---|---|---|---|
| Σ²(1) | 0.0897 | 0.0718 | 0.1099 | 0.2255 | **0.3370** | 0.5158 | **0.3425** | 1.0239 |

Σ²(1) spans **0.072 → 1.024** across the ladder. It is not blind to rigidity at all. The 0.0007 contrast
is a coincidence of **η = 0.3 landing on top of GUE at L=1** — a fact about my decoy's jitter parameter,
not about the statistic. So Phase 5's G2 failed on *two* compounding choices, not one: the L with least
contrast, and the η that put the decoy on the bracket at that L.

## 1. Why the conclusion survives anyway: mixing is averaging

The right support is structural, not a contrast number. Designed 4-way mixture
[lattice η=0.1 | GUE | GUE | Poisson], 500 each, on ζ's exact-θ backbone:

- part Σ²(1): 0.1074, 0.3452, 0.3307, 0.9141 — **mean 0.4243**
- whole-block Σ²(1): **0.4360**, i.e. |whole − mean(parts)| = 0.0117
- whole lies inside [min, max] of the parts: **true**

**Σ² of a heterogeneous block is the average of its parts.** Mixing therefore cannot push a block below
its most rigid component. A block sitting below a GUE bracket **entails** that at least one sub-block sits
below it. **Existence is entailed; only the address is open.** The heterogeneity confound has *zero*
leverage on existence — not "small" leverage, zero, by the structure of the estimator.

## 2. The two checks required before that is load-bearing — both clear

**Density really is handled exactly by θ.** Unfolded density by quarter of the ζ block, where the *raw*
density varies 7.4×:

| quarter | γ range | unfolded density |
|---|---|---|
| 1 | 14.1 – 811.2 | 1.000307 |
| 2 | 812.8 – 1419.4 | 1.000213 |
| 3 | 1420.4 – 1980.9 | 0.999554 |
| 4 | 1981.7 – 2515.3 | 0.999772 |

Spread **0.00075**, i.e. 0.075%. There is no residual drift for the sliding-window variance to mistake
for rigidity. Height-mixing does reduce to rigidity heterogeneity once θ is applied.

**Boundary effects at L=1 are negligible.** ζ whole-block Σ²(1) = 0.3112 against the mean of its four
sub-blocks 0.3122 — a discrepancy of 0.0010, which is **0.09 sd** of the N=500 bracket. Splitting costs
nothing at this L.

## 3. The decision computation the gate could not make

A single contrast number cannot separate *the confound lacks leverage* (proceed) from *the instrument
lacks sensitivity* (halt). They are two quantities:

| quantity | value | in sd units |
|---|---|---|
| measured effect \|ζ − bracket\| at L=1 | 0.0321 | **6.69** |
| instrument sensitivity (bracket sd, N=2000, B=20) | 0.0048 | 1 |
| confound leverage (mixing, §1) | **0.0000** | **0.00** |

Instrument **can** see it; confound **cannot** explain it. **PROCEED at L=1.** What remains open is
attribution, not existence.

## 4. P1's corroboration line, re-derived from corrected numbers

Both legs on the same block (`zeros6[:2000]`, γ = 14.1 – 2515.3, γ_mid = 1420.4):

| leg | statistic | ζ | bracket | dev | direction |
|---|---|---|---|---|---|
| P1 | ⟨r̃⟩ | 0.61717 | matched-density GUE 0.59986 ± 0.00706 | **+2.45σ** | more rigid |
| P3/5b | Σ²(L=1), θ path | 0.3112 | curvature-matched GUE 0.3433 ± 0.0048 | **−6.69σ** | more rigid |

**The line is re-derived and it is stronger than as originally filed** — the old figure was −4.49σ
against a *flat* GUE band read through a *fitted* poly9 unfold; the replacement is −6.69σ against a
curvature-matched bracket read through the exact θ path, with the density confound closed to 0.075% and
the mixing confound structurally excluded.

**What it is not.** ⟨r̃⟩ and Σ² are different families (§0d — r̃ reaches higher-order correlations), so
these are two legs on the *statistical* question. They are **one block read twice**, so they are **not
two independent witnesses in the data sense**, and no claim here upgrades to "robust". P1 moves from
*one witness, uncorroborated* to **one dataset, two statistic families, agreeing in sign and both
properly bracketed** — which is what the arc summary may now say, and no more.

**Attribution rider, carried with the claim, not appended to it.** Both legs are averages over
γ ∈ [14.1, 2515.3]. Neither is a measurement at γ = 1420. Any downstream use of "the excess at γ ≈ 1420"
is still mis-slotted until Phase 5 re-runs.

## 5. Disclosure: I have now seen ζ's sub-block values

Check §2's boundary test **required** ζ's per-sub-block Σ²(1) to compute. They are, at γ_mid ≈ 400 /
1120 / 1700 / 2250: **0.3138, 0.3138, 0.3131, 0.3081**. This is unavoidable given the check, and it has
two consequences that must be stated rather than absorbed:

- **These are unbracketed.** Each sub-block needs a curvature-matched band built on *its own* backbone;
  the comparison band available here was built at the first sub-block's backbone only. No σ is quoted.
- **They point AWAY from my sealed prediction.** Phase 5 sealed `H_bottom` (excess concentrated at the
  bottom, monotone decay). These four values are **flat** — if anything the *last* is lowest. That reads
  as `H_flat`. **This does not score the seal**: Phase 5 halted, its predictions remain unscored, and a
  post-hoc unbracketed reading cannot retire a sealed prediction in either direction.
- **Cold entry on the attribution question is now spent.** The Phase 5 re-seal must carry a
  `DISCLOSED_PRIOR_KNOWLEDGE` block listing these four numbers, exactly as the Task B seal did. It is
  still worth running — brackets are what would make it a result — but it is no longer a blind test.

## 6. Feasibility: the 3.4× is not an expense, it is a self-defeat

~202,000 zeros to resolve 1e-3 at low γ. They **exist** — `zeros6` holds 2,001,052 zeros. But the first
202,000 span γ = 14.1 → **140,757**, a **12.4×** density curvature against 7.4× for W=2000. The
resolution gain and the attribution problem move in opposite directions: buying the W that resolves 1e-3
buys a block so wide that "low γ" stops denoting anything. **Status line: not "expensive" and not
"unavailable" — available and self-defeating at low γ.** A 1e-3 resolution is reachable only at heights
where the effect P1 measured is already gone.

## 7. The wall as a design rule, with substrate triage

`L_max ≈ N / (2·(p+1))`, where p is the number of *fitted* density parameters and α_c ≈ (p+1)/N is the
support of the fitted-unfold artifact. Above L_max a long-range statistic on a fitted unfold is entirely
contaminated. Triage:

| substrate | density model | fitted params | cap |
|---|---|---|---|
| ζ | θ exact (identity, not a model) | **0** | **no cap** |
| Maass level-1 (`sessionK/maass_analysis.py`) | Weyl R² and R·lnR **theory-fixed**; only affine {R,1} fitted | 2 | L_max ≈ N/4 ≈ **66** (N=266) / **84** (N=334) |
| empirical-density substrates (fungal, solar, anything on `unfold_emp(order)`) | polynomial fit | order+1 | order 3, N=2000 → **250**; order 9 → **100** |

**Maass does not inherit ζ's exemption but is not blocked either.** Because only the affine offset is
fitted, its cap is ≈66–84, and Session K's Σ² was read to L = 15 — **within cap by ~4×**. That is a
retrospective clearance the phase never computed, and it is the answer to whether the Weyl law's
remainder costs Maass its long-range readout: at the L actually used, no.

## 8. One lesson, not three categories

Inert (false pass) and mis-fire (false fail) are the **same defect with opposite sign** — unquantified
power. The tell is that a single rule fixes both, so filing them as separate categories fragments the
antibody. Collapsed, and the rule is corrected: *"gate on the maximum-contrast arm"* was wrong — it
certifies an instrument you will not use.

**Power must be established at the arm where the measurement will be made.** And when contrast *there*
is low, two opposite situations look identical on a single number — the confound lacks leverage
(proceed) or the instrument lacks sensitivity (halt). Separating them is the second computation, §3
above: compare the confound's achievable range, the bracket sd, and the measured effect, all at the
measurement arm. G2 could not tell them apart and defaulted to halt.

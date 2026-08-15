# RESULTS — Comb Calibrator Micro-Arc

**Date:** 2026-08-15 (overnight). **Brief:** `COMB_CALIBRATOR_BRIEF.md` (approved with
amendments 2026-08-14). **Seal:** `comb/prereg_sealed.json` (prediction-first; code frozen at
`9eb285a` before any fresh datum existed). **Epistemic tier (binding on every artifact
below): CONJECTURE-BACKED-COMPUTABLE** — Gross–Smith / Hardy–Littlewood constellation weights
are unproven; the singular series is computable to arbitrary precision.

## TL;DR — verdicts

| Question | Verdict |
|---|---|
| Do the fresh-wedge comb weights match the computed ℤ[i] singular series? | **PASS (WEIGHTS_MATCH_SINGULAR_SERIES)** — 12/12 mandatory classes within 3σ (worst z = −2.33), no coherent drift (8/12 signs, one ≥2σ hit; threshold 8-of-12 AND ≥3 hits) |
| N=50 discriminator (two classes, same distance, predicted 4/3 apart) | **RESOLVED, predicted order, 53.9σ** — the sealed multiplicity rule ((2+i)² counts once) is confirmed |
| L1 anchoring | **NO DISCREPANCY** — §2's re-derivation matches the Gross–Smith form as stated in KRR (arXiv:2001.09513 = Ramanujan J. 58 (2022) 291–317; source archived `comb/lit/`); K=ℚ(i) explicitly instantiated in KRR's numerics; membership-not-valuation rule confirmed at their 𝔖(η) display |
| Calibrator seating (G4) | **SEATED** — `gp_comb` registered in `calibrator_panel.py` `CALIBRATORS_2D` with tier `conjecture-backed-computable`; validated at two disjoint norm bands [9·10⁶, 1.296·10⁷] ∪ [3.6·10⁷, 5.184·10⁷] (gap unmeasured — 2026-08-15 review correction) |

**The pilot, framed as the pilot it was (per review ruling):** the B2 glimpse — three
unrelated g-values collapsing to one constant matching the computed C′_G, plus the 4/3 factor
on cue at √10 — was a four-point structural agreement with a zero-parameter prediction. This
arc measured how precisely (answer: few-per-mille across 19 classes), tested shells the
glimpse never saw (N=18, 26, 32, 34, 50-both-classes, and the compound N=90), and earned the
seating on pre-registered ground. Disclosed pilots are how honest instruments get built.

## The result in one table

Fresh windows: wedge θ∈[0.45, 0.65] (disjoint from B2's [0.15, 0.35]); band-1 norms
[9.0·10⁶, 1.296·10⁷] (n=31,205), band-2 [3.6·10⁷, 5.184·10⁷] (n=114,644; fully new scale).
Prediction: 𝔖′ = C′_G·∏_{π|h odd}(q−1)/(q−2), **C′_G = 0.83829544** (tail bound 3.2·10⁻⁸ at
Q=10⁷). Pooled = inverse-variance across bands. M = mandatory (sealed), s = secondary
(descriptive, sealed as such).

| class | predicted | pooled measured | σ | z |
|---|---|---|---|---|
| M N2, N4, N8, N16, N32 (pure (1+i)-ladder) | 0.8383 | 0.8356, 0.8414, 0.8379, 0.8280, 0.8376 | 0.0044 | −0.6, +0.7, −0.1, −2.3, −0.2 |
| M N10, N20, N40 (one prime above 5) | 1.1177 | 1.1194, 1.1178, 1.1184 | 0.0036 | +0.5, +0.0, +0.2 |
| M N18 (inert 3) | 0.9581 | 0.9614 | 0.0047 | +0.7 |
| M N26 (prime above 13) | 0.9145 | 0.9151 | 0.0033 | +0.2 |
| M **N50 class A (both primes above 5)** | **1.4903** | **1.4901** | 0.0059 | −0.0 |
| M **N50 class B ((2+i)² ∥ h)** | **1.1177** | **1.1161** | 0.0036 | −0.4 |
| s N34 (prime above 17) | 0.8942 | 0.8939 | 0.0032 | −0.1 |
| s N36 (inert 3) | 0.9581 | 0.9535 | 0.0047 | −1.0 |
| s N64 (pure) | 0.8383 | 0.8370 | 0.0044 | −0.3 |
| s N80 (prime above 5) | 1.1177 | 1.1174 | 0.0036 | −0.1 |
| s **N90 (compound: inert 3 × prime above 5)** | **1.2774** | **1.2805** | 0.0039 | +0.8 |
| s **N100 (second discriminator, both classes)** | 1.1177 / 1.4903 | 1.1182 / 1.4896 | — | +0.1 / −0.1 |

Nineteen offset classes spanning predictions 0.838→1.490, matched at the few-per-mille
level by a formula with **zero free parameters** — every number on the predicted side comes
from the primes.

## Method (all sealed before fresh data)

Exact-offset counting on integer coordinates (`comb/exact_offsets.py` — no distance bins;
the B2 pcf bins were the pilot's convenience). Canonical half-set counting (one of ±h).
Null expectation per offset: E(h) = Σ_z 1[z+h∈W]·ρ_model(|z+h|), ρ_model = 4/(π ln r) —
exact border correction for lattice offsets; support null (independent checkerboard
occupancy) gives 𝔖′ ≡ 1 identically. Estimator KAG: 8-seed null recovery, worst |z| 3.07
over 152 tests, grand-mean z +0.015 (`comb/run_kag.py`, reproduction bit-identical).

## Defect log (all caught pre-seal by the arc's own gates)

1. **Even-residual factorization bug** (`singular_series.py` first run): odd primes hiding in
   an even residual were dropped, silently un-factoring N∈{10,20,26,34}. Caught by the
   executable hand-table gate (Will's review-verified table); the gate exists because a
   comment can't fail.
2. **±h double-count σ inflation** (`exact_offsets.py` first run): counting both h and −h
   tallies each unordered pair twice with perfectly correlated counts — naive Poisson z
   inflated by √2. Caught by the estimator KAG (false FAIL that was *correct to fire*).
3. **Independence-based bias threshold wrong in principle**: per-class z's within one point
   set are positively correlated (classes share endpoints; cov = ρ³(1−ρ) per shared-site
   triple). The KAG's pooled arm now self-calibrates from across-seed scatter, and the
   sealed drift arm is sign-coherence-based for the same reason.

## Committed-generator compliance (TOOLKIT §9)

Every banked artifact has its generator in the same commit lineage:
`singular_series_banked.json` ← `singular_series.py`; `exact_offsets_kag_measured.json` ←
`run_kag.py` (bit-identical reproduction verified); `comb_measured.json` ←
`run_measurement.py`; `prereg_sealed.json` ← `seal_prereg.py`. Code freeze commit `9eb285a`
referenced in the seal; no analysis code changed after fresh data existed.

## Seating record (G4)

`calibrator_panel.py` now carries the **epistemic-tier schema** — placed in the module gate
code imports, per the §8 ruling ("a tier field no gate can see is documentation cosplaying
as schema"): `CALIBRATOR_TIERS` (all 14 existing panel entries tiered; retroactive
application honestly reclassified `zeta_first_400` as conjecture-backed-computable — its
GUE-class ground truth is Montgomery), `assert_sole_anchor_allowed()` (verified to raise on
`gp_comb` as sole theorem-tier anchor), and `CALIBRATORS_2D` = {poisson2d, ginibre2d
(theorem-backed, bridge sampler), **gp_comb (conjecture-backed-computable, this arc)**}.
The zoo's first 2D arithmetic entry.

## Scope

No universality-class claims. The B2/B3 scale-qualified filing stands unmodified. k-tuples
beyond pairs: future arc. The calibrator is validated at **two disjoint norm bands**,
[9·10⁶, 1.296·10⁷] and [3.6·10⁷, 5.184·10⁷] — the seal validated bands, not an interval, and
the gap (1.296·10⁷, 3.6·10⁷) is unmeasured (2026-08-15 review correction of an earlier
contiguous-range overclaim). Consumers outside the bands extend the validation first (drift
was UNDETECTED here, not absent by theorem).

## Defect log, part 2 — post-closure high-effort code review (2026-08-15 overnight)

A dedicated review pass over the frozen package returned **10 verified findings**; none
touched the banked numbers on the path taken (re-derivation after all fixes: every class
statistic bit-identical, verdict unchanged, plus the additive `measured_power_ok: true`).
Dispositions, most severe first:

1. **Verdict lattice holes in the runner** (three findings): (level-match, discriminator
   unresolved, no drift) was UNBOUND → NameError; SOFT PASS bypassed the discriminator (a
   refuted multiplicity rule could launder into MATCH_WITH_BOUNDED_DRIFT); the
   UNDERPOWERED cell was implemented nowhere (huge-σ classes trivially pass |z|≤3 — an
   underpowered dataset laundering into PASS). All latent — the actual run took the fully
   satisfied path. **Fixed:** complete lattice with a named DISCRIMINATOR_UNRESOLVED cell
   and a measured-power check (banked run: all σ_pooled ≤ 0.0059 vs the 0.02 criterion).
   The same genus the review of the *brief* fixed in §5, surviving one level down in the
   implementation — partial satisfaction must have an address in code, not only in prose.
2. **Sealed extension geometry was invalid** (never fired): canonical reps end at π/4, so
   the sealed [0.45, 0.85] extension wedge could never be filled — ~16% guaranteed low bias
   ⇒ spurious FAIL had it fired, and the KAG could not have caught it (synthetic sites are
   built directly, not via `build_points`). **Fixed:** corrected numeric rule θ∈[0.36, 0.78]
   in the dated seal addendum; `build_points` now refuses t2 > π/4 loudly.
3. **KAG scope gap:** the estimator null gate had run at band-1 geometry only while band-2
   pooled with equal standing. **Remediated by extension:** band-2 KAG run post-measurement
   (null recovery on synthetics is science-data-independent) — **PASS**, worst |z| 4.33
   (≤4.5 over 152 tests; single hot seed at ~0.3% null probability, noted; grand mean
   +0.082). `comb/exact_offsets_kag_band2_measured.json`.
4. **Validated-range overclaim:** "[9·10⁶, 5.184·10⁷]" spanned the unmeasured gap between
   the two sealed bands. **Corrected in all three copies** (panel, TOOLKIT, this file) —
   the attribution-slot lesson applied to a range slot.
5. **Freeze was convention-only** and omitted the runner from the frozen list. **Fixed:**
   blob SHAs of all five analysis files recorded in the dated addendum and asserted at
   runner start (FREEZE VIOLATION raises).
6. **Schema teeth:** the tier guard had zero callers; `_schema_self_check()` now runs at
   import in every panel consumer (completeness + guard-fires probe). `gp_comb` is cached
   and flagged in `DETERMINISTIC_CALIBRATORS` (seed ignored by design — resampling-based
   reliability statistics must not consume it); empty-window paths degrade instead of crash.

Re-verification after all amendments: `run_measurement.py` re-derives the banked JSON with
all pre-existing keys bit-identical under the active freeze check; `run_kag.py` reproduces
bit-identically. Review agent record: 10 findings, 7 finder angles, banked-number
cross-checks confirmed independently.

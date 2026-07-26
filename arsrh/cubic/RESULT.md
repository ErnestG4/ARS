# RESULT — ARS cubic family, between-object approximation correlation

**Run:** `run_cubic_arm.py` → `run_cubic_arm_measured.json`, executing
`seals/CUBIC_ARM_SEAL.json` (arms hash `c2be21bf2a2ef4dd`) as amended by Addenda 1 and 2.
**Verdict: TARGET EMPTY. The deliverable is the upper limit named before the run.**

---

## The result

> **Totally real S₃ cubic conjugates show no coincidence of exceptional approximations above
> f = 0.05 at zero jitter (f = 0.10 at J ≤ 0.2, f = 0.20 at J = 1.0), per conjugate pair, on the
> log-denominator line.**

**Grade:** empirical bound against a permutation null. No analytic bracket exists in this region and
none is claimed. The floor is **demonstrated by injection, not argued**, and it is a floor **for the
sealed jitter family** Uniform(−J, J) — a heavy-tailed jitter has a different floor, which is
irreducible since the target's jitter shape is unknown by construction.

This is the sentence declared in the seal before any arm ran, so it is a result and not a
retrospective consolation.

## Target measurement

| | value | expected under H₀ |
|---|---|---|
| per-pair T below threshold 0.0225 | **2 / 72** | 3.6 |
| per-field T_field below 0.0100 | **1 / 24** | 1.2 |
| binomial p (one-sided) | **0.708** | — |

Per-pair T: min 0.0060, median 0.4940. Per-field T_field (min over each field's 3 conjugate pairs,
so **one witness per field**): min 0.0060, median 0.1195. Observed detections sit **at or below**
expectation on both accountings.

## Instrument checks — all four passed, which is what makes the negative a result

| check | requirement | measured | |
|---|---|---|---|
| **I1** stratum B smoke test | f_full ≥ 0.965; post-merge f = 1.000 exactly | min 0.9931; **24/24 fields, 3322/3322 events** | PASS |
| **I2** stratum C calibration | within ±12% of the calibrated formula, \|det\| ≤ 289 | worst \|ratio − 1\| = **0.098** over 23 fields at \|det\| ∈ {4, 9, 25, 169} | PASS |
| **I3** null / negative arm | false-positive rate ≤ 10% | **5.7%** at threshold 0.0225 | PASS |
| **I4** field counts | ≥ 20 per arm | 24 / 24 / 23 | PASS |

**The real permutation null's 5th percentile came out at 0.0225 against the 0.0235 sealed from
synthetics** — a 4% agreement between a pre-registered synthetic calibration and the real null.

**Edge-effect control on the limit:** the overlap domain available to the lag scan is 2262.8 for
within-field pairs vs 2255.4 for cross-field null pairs — **+0.33%, 1.78 sem**. Real and null pairs
draw on the same domain, so the null result is not an artifact of reduced overlap, and the direction
of the (insignificant) difference would favour detection rather than suppress it.

## The seal did its job, and that is worth recording separately

**The first execution HALTED**, on instrument check I1 — specifically on the *sharper* clause added in
Addendum 1. Two of 24 stratum-B fields failed post-merge exactness.

Diagnosis: events at convergent index 1953 and 1954 whose Serret partners sit at 1955 and 1956,
one and two positions past the `len(a1) − 45` guard. **A defect in my check, not in the transfer** —
the same defect class as everything else in this arc, two objects compared without intersecting their
valid domains. Addendum 2 fixes the **domain** and leaves the **tolerance** at exactly 1.000; after the
fix there were **zero** real misses.

That amendment is the highest-risk class in the protocol — a hard-halt check edited after it fired.
The guards that make it legitimate, all recorded in Addendum 2: no target data existed at halt time
(the script exits before the target block); the tolerance was not touched; the fix follows a
correctness principle that would have been applied identically had the check passed; and had even one
genuine miss survived, the honest reading would have been instrument failure rather than a further
amendment.

## What this does and does not say

- **Does not** say anything about boundedness of partial quotients. That is a tail property of an
  infinite sequence and no finite computation touches it. §0 of the seal, restated.
- **Does not** test Lang's conjecture, which is a within-object asymptotic claim.
- **Does** say that archimedean approximation quality carries no detectable memory of the Galois
  structure, on the between-object axis, at the stated sensitivity — **measured rather than assumed.**
- The mechanism was **absent by theorem** going in (α₂ ∉ ℚ(α₁) for S₃, and a ℚ-rational Möbius image of
  α₁ lands inside ℚ(α₁)), so the negative is the expected outcome. Its value is the **quantified floor**,
  not the direction.
- **Correlated objects are one witness:** the 72 pairs live on 24 fields, and the field-level accounting
  is the primary one. The 2/72 per-pair figure is reported alongside, not as a second witness.
- The limit is quoted **per conjugate pair at the sealed floor**. Aggregating across 24 fields would give
  a stronger bound, but that aggregation was not sealed, so it is not quoted.

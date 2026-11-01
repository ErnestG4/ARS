# FN1 stage-1 seal: the field ladder at X = 10¹⁰. REVISED TEXT for Will's review (not yet stamped)

Brief: Will, 2026-10-31 (Step 0; "staged, 10¹⁰ first") and 2026-11-01 ("Before stamping FN1"), filed verbatim in
`ph2/PH2_DECISIONS_2026-10-07.md`. Step 0, with the derivation of C_F and its LMFDB verification: `FN1_STEP0.md`.

**Order:** archives generated and hashed → witnesses → §9.F dry run → **this text reviewed by Will** → seal → stamp →
Bitcoin attestation verified on two explorers → double read → `cmp`.

**Stage.** This is stage 1 (10¹⁰). Whether to run a 10¹¹ stage is decided after this read. The 10¹⁰ archives are a
prefix of any 10¹¹ archive: the same contiguous segments, extended. So a 10¹¹ stage would re-include these data, its
fresh part would be (10¹⁰, 10¹¹], and its statistics would not be independent of these.

## 1. Fields, constants, data

**Fields.** The nine class-number-1 imaginary quadratic fields, with C_F = log(|D|·(w/2)²):

| Field | C_F |
|---|---|
| D = −7 | 1.946 |
| D = −8 | 2.079 |
| D = −11 | 2.398 |
| ℤ[i] | 2.773 |
| D = −19 | 2.944 |
| ℤ[ω] | 3.296 |
| D = −43 | 3.761 |
| D = −67 | 4.205 |
| D = −163 | 5.094 |

The C_F are all distinct.

**Verification.** All seven w = 2 values are verified on LMFDB through the weight-3 CM newforms of level |D|:
Γ_ℂ(s + 1), conductor |D|, and 105 coefficients a_p matching values computed independently (`FN1_STEP0.md` §2). log 16
and log 27 are as in `rq1/C_OMEGA_VERIFY.md`. ℤ[√2] enters only the secondary prediction, with C = 4.62 (from RQ1's
1.8489 difference).

**Angles.** For w = 2, θ = arg π / π with the mirror 1 − θ. ℤ[i] uses θ over π/2, ℤ[ω] θ over π/3, and ℤ[√2] the RQ1
map.

**Matched N.** n = 227,524,967, the ℤ[√2] split-prime count below 10¹⁰. N = 455,049,934, using each field's first n split
primes. K = round(N^β): 57,801 (β 0.55), 2,906 (0.40), 7,873 (0.45).

**Statistic.** R_F(β) = var_stream(θ, K)/(N/K), exact (`rq1_read.var_stream`).

**Archives and pins.**
- The seven new archives are under `/mnt/data/fn1/archive_1e10_D*`: 229.7 million rows each to 1.01·10¹⁰, integrity
  checked on every row, 14.24 core-hours.
- ℤ[i], ℤ[ω] and ℤ[√2] come from the pinned RQ1-c 10¹² archives (prefixes).
- All ten manifest sha256 values, and the two guard files', are in `fn1_pins.json`, sealed with this text.

## 1b. Prior exposure: exactly what was seen before this seal

| Source | Field(s) | X | Statistics seen |
|---|---|---|---|
| RQ1 sealed read (`rq1/results/read/read1.json`) | ℤ[√2], ℤ[i] | 10¹⁰, 10¹¹ | R at β = 0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90; D and D/SE |
| RQ1 collapse (`results/collapse/COLLAPSE.json`, post hoc) | ℤ[√2], ℤ[i] | 10¹⁰, 10¹¹ | R_ℤ[√2](K) and R_ℤ[i](aK), a = 2.5204, on the β grid 0.20–0.70 in steps of 0.01 (51 points); residuals |
| RQ1-c read (`rq1c_read_ruling/read1.stripped.json`) | ℤ[√2], ℤ[i], ℤ[ω] | 10¹⁰, 10¹¹ | R at β 0.40, 0.45, 0.55 (P4 cells, and the 10¹⁰ / 10¹¹ reproduction) |
| RQ1-c read | ℤ[√2], ℤ[i] | 10¹² | R at β 0.40, 0.45, 0.55, 0.60 (P1 / P2) and on the P3 fine grid (22 / 25 values) |
| RQ1-c read | ℤ[ω] | 10¹² | R at β 0.40, 0.45, 0.55 |
| RQ1-c REPRO (post hoc) | ℤ[√2], ℤ[i] | 10¹⁰, 10¹¹ | the same as the RQ1 read, recomputed (exact and binned) |
| L13 (`rq1/results/l13/L13.json`) | ℤ[√2], ℤ[i] | 10¹⁰, 10¹¹ | R at β 0.40, 0.45, 0.55, 0.60; block-arc SEs; residue-class subset R_j (p mod 5, 7, 13) |
| RQ1 Step 1 (Chen's statistic) | ℤ[√2], ℤ[i] | 10⁹ | Chen's smoothed ψ-weighted variance (a different statistic) |
| Phase 34d | ℤ[ω] | ≤ 10⁸ | angle statistics (different X) |

**At this seal's cells** (10¹⁰; β 0.55, 0.40, 0.45), therefore:
- ℤ[√2], ℤ[i] and ℤ[ω] have all been seen, at all three β.
- **The seven w = 2 fields have never been read.** Their archives were only generated and hashed. The §9.F rehearsal
  used seeded random stand-in rows in their place.

The read recomputes the three seen fields and requires them bit-identical to the values above; otherwise VOID (guard).

## 2. Predictions and rules (fixed here)

**Primary.**
- *Statistic:* Spearman ρ_s between C_F and R_F at β = 0.55 across the nine fields.
- *Rule:* PASS iff the exact one-sided permutation p is < 0.01 **and** ρ_s > 0. p counts all 9! = 362,880 orderings; the
  condition is Σd² ≤ 26, i.e. ρ_s ≥ 0.7833, where p = 0.0086. Otherwise FAIL, read as in §3a.

**Secondary (B2 cells).** The same rule at β = 0.40 and at β = 0.45, each reported separately.

**Secondary prediction (ℤ[√2]).** PASS iff R_ℚ(√−67) < R_ℤ[√2] < R_ℚ(√−163) at β = 0.55. Reported separately.

**Descriptive (no verdict).**
- The near-equal-C pairs:
  - (−7, −8): ΔC = 0.134, same w;
  - (ℤ[i], −19): ΔC = 0.172, w = 4 against 2.
- ρ_s against log|D|.
- The ℤ[√2] placement at β 0.40 and 0.45.
- **Fresh-only ρ_s on the seven never-read w = 2 fields**, with an exact p over 7! = 5,040 orderings. It is labelled
  UNPOWERED (n = 7: p < 0.01 needs ρ_s ≥ 0.893, Σd² ≤ 6, p = 0.0062).
  - *Note for Will:* the brief said "6 unseen fields". All seven w = 2 fields are unseen, so seven are used. For n = 6
    the threshold is the brief's ρ_s ≥ 0.943.

**Ties.** The test needs strict ranks. If any two of the compared R values are exactly equal (float equality), that
test is **VOID (ties)**. There is no mid-rank or random tie-breaking. The C_F have no ties. An exact tie between two
455-million-point variance integrals is not expected.

**VOID** (any one voids the read):
- a pinned manifest, guard file or segment sha256 mismatches;
- `/mnt/data` is not mounted;
- the seen-value guard fails;
- an exact tie;
- the double read is not byte-identical under `cmp`.

## 3. Power, stated before sealing (`results/FN1_POWER.json`)

**Model.** R_F = b·C_F + σ_F ε_F, where:
- b is the seen ℤ[√2]–ℤ[i] slope per unit C at 10¹⁰;
- σ is the sealed SE model times a noise scale;
- the scales are L13's empirical/model ratios at (10¹⁰, β), method A (block arcs) or B (residue subsets), using ℤ[i]'s
  ratio or ℤ[√2]'s.

D23 = P(PASS | ordering by C exactly true) = the power.

| Test | sealed model | B, ℤ[i] ratio | B, ℤ[√2] ratio | A, ℤ[i] ratio | A, ℤ[√2] ratio |
|---|---|---|---|---|---|
| Primary, β 0.55 | **1.00** (1×) | 0.78 (4.1×) | 0.31 (7.4×) | 0.25 (8.4×) | 0.06 (17.9×) |
| ℤ[√2] placement | 0.96 | 0.30 | 0.30 | 0.17 | 0.22 |
| β 0.45 | 0.89 | 0.68 (1.3×) | 0.15 (3.1×) | 0.08 (4.6×) | 0.07 (4.9×) |
| β 0.40 | 0.47 | 0.54 (0.9×) | 0.15 (1.8×) | 0.04 (3.7×) | 0.05 (3.2×) |

**Labels (accepted by Will).**
- β 0.40 is **UNPOWERED**.
- β 0.45 and the ℤ[√2] placement are powered only under the sealed model.
- **An unpowered cell is read one way only: a PASS is informative, a FAIL is not.** The same holds for the primary when
  §3a finds its power below 0.80.

**Does the sealed model overstate power?** No. At planted_h's slope the model predicts 0.718, against the measured 0.76.
Across the curve (§4) it predicts at or slightly below the measured rates, because its σ is mildly conservative on the
witness sets (0.0198 against a measured 0.0183). So the 1.00 primary figure stands.

### 3a. Read-time noise rule (sealed; it does not use the cross-field ranking)

**Estimate.**
- For each of the nine fields, its first n rows (prime order) are split into 8 contiguous segments.
- R_seg is computed at β 0.55 with K_seg = round((2·⌊n/8⌋)^0.55).
- relSD = SD(R_seg)/mean(R_seg), scaled to the full N by the 1/√K law, and pooled over the fields (63 degrees of
  freedom).
- noise_ratio = pooled relSD / √(2/(cK)).

**Interpretation.** The primary power at that noise comes from the model above (b = 0.04115, σ = noise_ratio ×
0.006148, 200,000 seeded simulations of the exact rule). It is 1.00 at 1×, 0.795 at 4× and 0.27 at 8×.
- **Power ≥ 0.80** ("near the sealed model"): a primary FAIL is informative.
- **Power < 0.80** ("near L13"): a primary FAIL is reported as **FAIL (UNPOWERED at the read-time noise)**.
- A primary PASS is informative either way, because the null is exact.

**Known bias.** Segments span different prime ranges, so any slow drift of R with X inflates the estimate. It therefore
leans toward calling a FAIL UNPOWERED, not toward over-reading one.

## 4. Witnesses (`results/FN1_WITNESS*.json`)

The read's own `rank_test` was run on synthetic nine-field ladders (mirror-symmetric lattice / i.i.d. mixtures, N = 2·10⁶,
β = 0.55).

**Will's conditions for planted_x.**
- **(a) Not met.** planted_x's slope (0.080) was chosen as twice planted_h's after planted_h failed, not from FN1's
  target. So **planted_x does not replace planted_h** as the must-pass witness.
- **(b) Met.** The sealed model's power at planted_h's slope is 0.718 ≈ the measured 0.76.

**planted_h is kept as a power-curve point.** It was run at slope 0.040, measured 0.76 (base ρ₀ = 0.20). The bar error
is recorded: its declared ≥ 0.90 was set above that slope's power, about 0.72–0.75.

**Power curve 1 (ρ₀ = 0.20; the first runs).** The model column is the measured-σ parametric value.

| Slope | Reps | Measured | Model |
|---|---|---|---|
| 0 (null) | 200 | 0.005 | |
| 0.015 | 200 | 0.145 | 0.146 |
| 0.040 (planted_h) | 200 | 0.760 | 0.752 |
| 0.080 (planted_x) | 200 | 1.000 | 0.998 |

**Shuffled C** gave 0.000.

**Power curve 2 (ρ₀ = 0.40; declared before running, after a correction recorded in `fn1_witness.py`).**

| Arm | Slope | Reps | Measured | Sealed-model power | Measured-σ power |
|---|---|---|---|---|---|
| null | 0 | 1000 | **10/1000 = 0.010** (must be about α; it was) | 0.009 | 0.008 |
| | 0.010 | 200 | 0.090 | 0.100 | 0.116 |
| | 0.025 | 200 | 0.625 | 0.561 | 0.630 |
| | 0.060 | 200 | 1.000 | 0.995 | 0.998 |
| **target (must-pass)** | 0.1327 | 200 | **1.000** | 1.000 | 1.000 |

The target slope comes from FN1's target effect size: b/σ = 6.694 per unit C at the primary cell, times the witness's
sealed-model σ.

**Every declared check holds:**
- null count in [1, 19];
- target ≥ 180/200;
- every curve point within 3 SE + 0.02 of the sealed-model power.

**What the witnesses establish:**
- the exact null is exact in the code;
- shuffling C destroys the pass;
- the code passes at FN1's target effect size;
- the power model of §3 matches measurement along the whole curve.

## 5. §9.F rehearsal (`results/dryrun/`)

The stand-ins are seeded random rows for the seven new fields. The seen archives are real.

1. **10⁹ dry run.** Two reads byte-identical.
2. **10¹⁰ dry run, with the guard active.**
   - The seen values were recomputed bit-identical, and two reads were byte-identical.
   - Red paths: a seen value shifted by 10⁻¹² gave VOID (guard); a flipped segment byte raised an assertion and wrote
     no output (VOID, hash).
3. **The guard-pin check was added, and the 10¹⁰ dry run rerun.**
   - Two reads byte-identical.
   - An altered guard file under the true pin raised `AssertionError ('guard pin')` with no output.
4. **The read-time noise rule, the fresh-only ρ_s and the tie statement were added** (Will, 2026-11-01). The 10¹⁰ dry
   double read is rerun again: *(rerun pending)*.

## 6. Attribution, fixed before the read

- **Primary PASS:** across the nine class-number-1 imaginary quadratic fields, R at matched N is ordered by
  C_F = log(|D|(w/2)²) beyond chance, under an exact, SE-free null. This supports C_F as the field-level determinant
  found in RQ1 / RQ1-c, across nine fields and three unit groups.
- **Primary FAIL, informative per §3a:** R is not ordered by C_F at this resolution. It does not by itself refute RQ1 /
  RQ1-c's SE-free patterns, which concern ℤ[√2] / ℤ[i] / ℤ[ω].
- **Primary FAIL, UNPOWERED per §3a:** no conclusion about the ordering. The fluctuations are too large for this test at
  n = 9.
- **ℤ[√2] placement:**
  - PASS: a real quadratic field sits on the imaginary-field ladder where its C puts it.
  - FAIL: informative only near the sealed noise level.
- **Inputs:**
  - C_F for w = 2 is verified (LMFDB);
  - the conductor-rescaling picture is the hypothesis being tested;
  - the noise model for deterministic arithmetic sets is unresolved (L13), hence the rank test and the §3a rule.

## 7. Cost

| Item | Core-h |
|---|---|
| Archives | 14.24 |
| Witnesses | about 0.3 (local) |
| Dry runs | about 2 |
| Double read | about 0.6 (now with the segment noise estimate) |

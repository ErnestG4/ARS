# FN1 stage-1 seal: the field ladder at X = 10¹⁰. FINAL TEXT for Will's review (not yet stamped)

Brief: Will, 2026-10-31 (FN1 Step 0, then "staged, 10¹⁰ first" with the seal requirements), filed verbatim in
`ph2/PH2_DECISIONS_2026-10-07.md`. Step 0, with the derivation of C_F and its LMFDB verification: `FN1_STEP0.md`.

**Order:** archives generated and hashed → witnesses → §9.F dry run → **this text reviewed by Will** → seal → stamp →
Bitcoin attestation verified on two explorers → double read → `cmp`.

**Stage.** This is stage 1 (10¹⁰). Whether to run a 10¹¹ stage is decided after this read. The 10¹⁰ archives are a
prefix of any 10¹¹ archive: the same contiguous segments, extended. So a 10¹¹ stage would re-include the 10¹⁰ data.
Its fresh part would be (10¹⁰, 10¹¹], and its statistics would not be independent of these.

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

**Verification.** All seven w = 2 values are verified on LMFDB through the weight-3 CM newforms of level |D|:
Γ_ℂ(s + 1), conductor |D|, and 105 coefficients a_p matching values computed independently (`FN1_STEP0.md` §2,
`LMFDB_WEIGHT3_CM.md`). log 16 and log 27 are as in `rq1/C_OMEGA_VERIFY.md`. ℤ[√2], a real quadratic field, enters
only the secondary prediction (C = 4.62, the value from RQ1's 1.8489 difference).

**Angles.** For w = 2, θ = arg π / π with the mirror 1 − θ (`fn1_archive.py`). ℤ[i] uses θ over π/2, ℤ[ω] θ over π/3,
and ℤ[√2] the RQ1 map. All are mirror-symmetrised, as in RQ1.

**Matched N.** n = 227,524,967, the ℤ[√2] split-prime count below 10¹⁰. N = 2n = 455,049,934, using each field's first
n split primes. K = round(N^β): 57,801 (β 0.55), 2,906 (0.40), 7,873 (0.45).

**Statistic.** R_F(β) = var_stream(θ, K)/(N/K), exact: `rq1_read.var_stream`, the RQ1 estimator.

**Archives.** The seven new ones are under `/mnt/data/fn1/archive_1e10_D*` (generated 2026-10-31; 101 segments of 10⁸
each; integrity asserted for every row). ℤ[i], ℤ[ω] and ℤ[√2] come from the pinned RQ1-c 10¹² archives (prefixes). The
manifests' sha256 values are in `fn1_pins.json`, sealed with this text (local copies in `results/manifests/`). Each
field has 229.7 million rows to 1.01·10¹⁰, all with integrity checked, which covers n. Six of the seven have slightly
fewer split primes below 10¹⁰ itself than ℤ[√2] does, which is why the archives run to 1.01·10¹⁰. The guard files
(RQ1 `read1.json` and RQ1-c `read1.stripped.json`) are pinned by sha256 in the same file.

**Seen data.** ℤ[i], ℤ[ω] and ℤ[√2] at 10¹⁰ were read in RQ1 / RQ1-c, at these exact K. The read recomputes them and
requires them bit-identical; otherwise VOID (guard). So three of the ten values are known. The seven w = 2 fields have
never been read; their archives were only generated and hashed. The predictions are fixed by C_F alone, so the known
values tune nothing.

## 2. Predictions and rules (fixed here)

**Primary.**
- *Statistic:* Spearman ρ_s between C_F and R_F at β = 0.55 across the nine fields.
- *Rule:* PASS iff the exact one-sided permutation p (all 9! = 362,880 orderings) is < 0.01 **and** ρ_s > 0. That is
  Σd² ≤ 26, or ρ_s ≥ 0.7833, where p = 0.0086. Otherwise FAIL.

**Secondary (B2 cells).** The same rule at β = 0.40 and at β = 0.45, each reported separately.

**Secondary prediction (ℤ[√2]).** PASS iff R_ℚ(√−67) < R_ℤ[√2] < R_ℚ(√−163) at β = 0.55. Reported separately.

**Descriptive (no verdict).**
- The near-equal-C pairs, reporting R differences against ΔC:
  - (−7, −8): ΔC = 0.134, same w;
  - (ℤ[i], −19): ΔC = 0.172, w = 4 against 2.
- ρ_s against log|D| (ignoring w), beside ρ_s against C_F.
- The ℤ[√2] placement at β 0.40 and 0.45.

**VOID** (any one voids the read):
- a pinned manifest's sha256 or any segment's sha256 mismatches;
- `/mnt/data` is not mounted;
- the seen-value guard fails;
- R has an exact tie among the nine fields;
- the double read is not byte-identical under `cmp`.

## 3. Power, as Will required, stated before sealing (`results/FN1_POWER.json`)

**Model.** R_F = b·C_F + σ_F ε_F, where:
- b is the seen ℤ[√2]–ℤ[i] slope per unit C at 10¹⁰;
- σ is the sealed SE model R·√(2/(cK)) times a noise scale;
- the scales are L13's measured empirical/model ratios at (10¹⁰, β), method A (block arcs) or B (residue subsets),
  using ℤ[i]'s ratio or ℤ[√2]'s.

D23 is P(PASS | ordering by C exactly true), which is the power.

| Test | sealed model | B, ℤ[i] ratio | B, ℤ[√2] ratio | A, ℤ[i] ratio | A, ℤ[√2] ratio |
|---|---|---|---|---|---|
| Primary, β 0.55 | **1.00** (scale 1×) | 0.78 (4.1×) | 0.31 (7.4×) | 0.25 (8.4×) | 0.06 (17.9×) |
| ℤ[√2] placement, β 0.55 | 0.96 | 0.30 | 0.30 | 0.17 | 0.22 |
| Secondary β 0.45 | 0.89 | 0.68 (1.3×) | 0.15 (3.1×) | 0.08 (4.6×) | 0.07 (4.9×) |
| Secondary β 0.40 | 0.47 | 0.54 (0.9×) | 0.15 (1.8×) | 0.04 (3.7×) | 0.05 (3.2×) |

**Consequences, fixed before the read.**
- D23 ≥ 0.95 holds for the primary test only under the sealed SE model.
- **A primary PASS is informative under any noise model**, because the permutation null is exact and needs no SE.
- **A primary FAIL is informative only if the fluctuations are near the sealed model's.** Under L13's scales, the power
  is between 0.06 and 0.78.
- The β 0.40 test is **UNPOWERED** (0.47 even under the sealed model).
- The β 0.45 test and the ℤ[√2] placement are powered only under the sealed model.

## 4. Witnesses (`results/FN1_WITNESS.json`, `FN1_WITNESS_EXTRA.json`)

The read's own `rank_test` was run on synthetic nine-field ladders: mirror-symmetric mixtures, N = 2·10⁶,
β = 0.55, 200 replicates per arm.

| Arm | Required | Result |
|---|---|---|
| Null (equal R) | false PASS ≤ 6/200 | 0.005 |
| Shuffled C | ≤ 6/200 | 0.000 |
| Power calibration, slope 0.040 | measured = parametric | 0.760 vs 0.752 |
| Power calibration, slope 0.015 | measured = parametric | 0.145 vs 0.146 |
| planted_h (slope 0.040) | ≥ 180/200 | **0.76: FAILED its declared bar** |

**The planted_h failure.** I set the bar above the parametric power that slope can deliver: a witness-design error, not
a pipeline error.

**The supplementary arm**, added after the failure, labelled, and committed before it ran: planted_x (slope 0.080)
passed 200/200, against a parametric 0.998. **Will decides** whether it stands in for planted_h.

What the witnesses establish:
- the exact null is exact in the code;
- shuffling C destroys the pass;
- the parametric power used in §3 matches the code on sets whose truth is known (TOOLKIT §9.G).

## 5. §9.F rehearsal (`results/dryrun/`)

1. **10⁹ dry run.** Seeded random stand-in rows replace the seven new fields, and the real seen archives are read at
   10⁹. The two reads were byte-identical (`cmp` status 0), 80 s wall each, with timings in sidecars and no verdict
   printed. The seen-value guard was skipped there, because it only applies at 10¹⁰.
2. **Change before sealing.** The guard now runs whenever X = 10¹⁰, including dry runs.
3. **10¹⁰ dry run.** Stand-ins at the full n (227,524,967 rows per field), with the guard active.
   - The seen ℤ[√2], ℤ[i] and ℤ[ω] values were recomputed bit-identical at all three β.
   - The two reads were byte-identical (`cmp` status 0), 12 min and 0.18 core-hours each.
   - Red paths: one seen value shifted by 10⁻¹² gave VOID (seen-value guard). One flipped byte in a segment raised an
     assertion and wrote no output, i.e. VOID (hash).
4. **A second change before sealing.** The read now also checks the guard files' sha256 against `fn1_pins.json`.
   Because of that change, the 10¹⁰ dry double read was run again, with an added red path (an altered guard file under
   the true pin must stop the read). **Rerun result:** the two reads were byte-identical (`cmp` status 0), and the seen
   values were again bit-identical. The altered value under its own pin gave VOID (seen-value guard). The altered
   guard file under the true pin raised `AssertionError: ('guard pin', 'rq1_read1')` and wrote no output.

## 6. Attribution, fixed before the read

- **Primary PASS:** across the nine class-number-1 imaginary quadratic fields, the angle-set statistic R at matched N is
  ordered by the conductor constant C_F = log(|D|(w/2)²). This holds beyond chance under an exact, SE-free null. It
  supports C_F as the field-level determinant found in RQ1 / RQ1-c, now across nine fields and three unit groups.
- **Primary FAIL:** either R is not ordered by C_F, or fluctuations at L13's scales hide the ordering (power
  0.06–0.78 there). It does not by itself refute RQ1 / RQ1-c's SE-free patterns.
- **ℤ[√2] placement:**
  - PASS: a real quadratic field sits on the imaginary-field ladder where its C puts it.
  - FAIL: informative only near the sealed noise level.
- **Inputs:**
  - C_F for w = 2 is verified (LMFDB);
  - the conductor-rescaling picture R_F(K) ≈ R₀(K e^{C_F/2}) is the hypothesis being tested, not an assumption of the
    test;
  - the noise model for deterministic arithmetic sets is unresolved (L13), which is why the test is a rank test.

## 7. Cost

| Item | Core-h |
|---|---|
| Archives (seven fields to 1.01·10¹⁰; checks 0.60× / 0.85× / 0.90×) | 14.24 |
| Witnesses | about 0.1 (local) |
| Dry runs | about 1 |
| Double read | about 0.4 |

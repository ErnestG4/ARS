# FN1 stage-2 read report: the field ladder on the fresh slice (10¹⁰, 10¹¹]

**Sealed by** `FN1_STAGE2_SEAL.md` (tag `fn1-seal2`, object cd93197c on 9c142c2e).

**Read:** 2026-11-02 (PST) on spot, through the shared pueue queue. Sealed `fn1_read2.py` sha256 92f9db78…, pins
`fn1_pins2.json` c511e4a4….

## 0. Protocol

| Step | Record |
|---|---|
| Stamp | OTS 2026-11-02 21:17:09 UTC, four calendars (commit 8b0dce22) |
| Bitcoin attestation | block 974305, 2026-11-02 21:32:23 UTC; the merkle root matches the block header on blockstream.info and mempool.space (`timestamps/FN1_STAGE2_SEAL_STAMP_2026-11-02_VERIFY.json`, commit 271e2bf3). All verifier checks hold. |
| Launch guards (`run_fn1_read2_one.sh`) | Before each read: the attestation record verified on both explorers; sha256 of `fn1_read2.py`, the pins, `fn1_archive.py` and the rq1 modules matched the sealed blobs; mount present; MemAvailable 110 GB (read 1) and 105 GB (read 2), against the 60 GB floor |
| Double read | pueue group `specarith-scored`, sequential: task 572 (14:40:37 → 17:58:13 PST), task 573 (17:58:14 → 21:15:47), both rc 0. 11,855 s and 11,853 s wall; CPU 10,579 s and 10,527 s; maxrss 43.2 GB each |
| cmp | **0** (task 574): `READ1.json` and `READ2.json` byte-identical (sha256 440c7f87f341cbe66f35a15f5e3163e864a45ee620192613392cd080eec3c128), on spot and again after copying here |
| Verdicts | viewed only after the cmp |
| Prefix guard | checked inside the read (raises on mismatch); it did not raise |
| VOID conditions | none: no pin mismatch, mount present, prefix guard held, no exact ties in any compared set, cmp 0 |

Outputs: `results/stage2/read/` (both reads, timing sidecars, logs, status, cmp, queue ids). Record checker:
`verify_fn1_read2.py`.

## 1. Verdicts (as sealed)

| Test | Mode | Statistic | Verdict |
|---|---|---|---|
| **Primary**, β 0.55, nine fields | two-way | ρ_s = **0.867**, Σd² = 16 (≤ 26), exact p = **0.0023** | **PASS** |
| Secondary β 0.45 | one-way | ρ_s = 0.967, Σd² = 4, exact p = 8.3 × 10⁻⁵ | **PASS** |
| Secondary β 0.40 | one-way | ρ_s = 0.983, Σd² = 2, exact p = 2.5 × 10⁻⁵ | **PASS** |
| −7 displacement, β 0.55 | one-way, flat null | T = 0.0137, margin m = 0.0212 | FAIL (one-way arm: FAIL not informative) |
| ℤ[√2] placement | descriptive | between −67 and −163 at β 0.45 only (§2) | no verdict, as sealed |

**Read-time noise (sealed raw rule, §2.1).**

| β | Pooled raw relSD | Ratio to the sealed model | Detrended ratio (descriptive) | Power at the read-time noise |
|---|---|---|---|---|
| 0.55 | 0.0184 | **4.40×** | 2.25× | **0.995** |
| 0.45 | 0.0218 | 1.73× | 0.82× | 0.380 (descriptive; one-way) |
| 0.40 | 0.0274 | 1.26× | 0.75× | 0.293 (descriptive; one-way) |

- The primary's power at its read-time noise is 0.995 ≥ 0.80, so a primary FAIL would have counted as informative.
  It passed, and a PASS is informative either way.
- The secondaries are one-way: their PASS is informative whatever the power. Their power figures use the sealed
  stage-1 slopes B; see §4 item 4.

**−7 arm (§2.4).**
- R_−7 = 0.83849, R_−8 = 0.82125, R_−11 = 0.82480. T = min(+0.01724, +0.01369) = **0.01369**.
- Rule noise: det 0.00942 (read-time pooled detrended relSD, β 0.55), DRIFT_SD 0.012458, so σ_rel = 0.01562. The
  nine-field mean R is 0.8718, so σ = 0.01362.
- Margin m (95th percentile of T under the flat null, 200,000 seeded draws) = **0.02118**. T is 0.0075 below it.
- False-PASS check on the independent seed: 0.0507.
- T is also below the design-time margin of 0.0183 (§3a), so the FAIL does not come from the read-time noise rising.

## 2. Descriptive (no verdict, as sealed)

**R_F by field** (rows ordered by C_F; stage-1 β 0.55 shown for comparison):

| Field | C_F | R β 0.40 | R β 0.45 | R β 0.55 | rank at 0.55 | stage-1 R β 0.55 | stage-1 rank |
|---|---|---|---|---|---|---|---|
| −7 | 1.946 | 0.5435 | 0.6370 | 0.8385 | 3 | 0.7973 | 4 |
| −8 | 2.079 | 0.5608 | 0.6486 | 0.8212 | 0 | 0.7773 | 0 |
| −11 | 2.398 | 0.5466 | 0.6430 | 0.8248 | 1 | 0.7779 | 1 |
| ℤ[i] | 2.773 | 0.5819 | 0.6726 | 0.8444 | 4 | 0.7896 | 3 |
| −19 | 2.944 | 0.5824 | 0.6637 | 0.8369 | 2 | 0.7821 | 2 |
| ℤ[ω] | 3.296 | 0.5973 | 0.6762 | 0.8598 | 5 | 0.8090 | 5 |
| −43 | 3.761 | 0.5991 | 0.6894 | 0.8877 | 6 | 0.8340 | 6 |
| −67 | 4.205 | 0.6283 | 0.7101 | 0.9283 | 7 | 0.8568 | 7 |
| −163 | 5.094 | 0.6505 | 0.7252 | 1.0046 | 8 | 0.9346 | 8 |
| ℤ[√2] | 4.62 | 0.6185 | 0.7115 | 0.9198 | (below −67) | 0.8657 | (between) |

**Where Σd² comes from.**
- β 0.55: Σd² = 16. Of that, 9 comes from −7 (C rank 0, R rank 3). The rest is 4 from −19 and 1 each from −8, −11
  and ℤ[i]. At stage 1, −7 carried 16 of 22.
- β 0.45: Σd² = 4, from −8, −11, ℤ[i] and −19, each one place off.
- β 0.40: Σd² = 2, from −8 and −11 swapped.

**Other descriptive results.**
- **ℤ[√2] placement** (R_−67 < R_ℤ[√2] < R_−163):
  - β 0.55: no; ℤ[√2] is 0.0085 below −67.
  - β 0.45: yes; 0.0014 above −67.
  - β 0.40: no; 0.0098 below −67.
  - At stage 1 it lay between them at all three β. As sealed (§2.3, §6), this carries no verdict and no conclusion
    either way.
- **ρ_s against log|D|:** 0.483 (p 0.097) at β 0.55, 0.567 at β 0.45, 0.633 at β 0.40. Against C_F the values are
  0.867, 0.967 and 0.983. ℤ[i] and ℤ[ω] sit mid-ladder (R ranks 4 and 5 at β 0.55), as C_F places them.
- **Fresh-only ρ_s, the seven w = 2 fields (unpowered by seal):**
  - β 0.55: ρ_s 0.786, Σd² 12, p 0.024 (above the 0.01 bar). The ranks follow C except −7 (fresh rank 3), the same
    pattern and numbers as stage 1.
  - β 0.45 and β 0.40: ρ_s 0.964, Σd² 2, p 0.0014 each.
- **Near-equal-C pairs** (ΔR = R_higher-C − R_lower-C):

| Pair | ΔC | ΔR β 0.40 | ΔR β 0.45 | ΔR β 0.55 |
|---|---|---|---|---|
| (−7, −8) | 0.134 | +0.0172 | +0.0117 | −0.0172 |
| (ℤ[i], −19) | 0.172 | +0.0005 | −0.0089 | −0.0075 |

  At β 0.55 both pairs are inverted again, as at stage 1.
- **OLS of R on C_F** (stage-2 slope b; Pearson r of the nine residuals with the stage-1 residuals):

| β | b (stage 2) | B (stage 1, sealed) | residual SD | r with stage-1 residuals |
|---|---|---|---|---|
| 0.55 | 0.0548 | 0.0455 | 0.0213 | **+0.977** |
| 0.45 | 0.0284 | 0.0139 | 0.0065 | −0.554 |
| 0.40 | 0.0335 | 0.0132 | 0.0087 | −0.176 |

  At β 0.55 the largest residuals are −7 +0.0335 (stage-1 DELTA7 +0.0352), −163 +0.0272, −19 −0.0228 and
  ℤ[ω] −0.0191.
- **Chen-form P_F fit, β 0.55:** P_full slope 0.0924, residual SD 0.0161; P_noA slope 0.0825, residual SD 0.0186.
  The OLS on C_F leaves 0.0213.
- **−7 rule under other noises (sealed as descriptive, §2.4):**

| Variant | σ | Margin | T above margin | Power under persistence |
|---|---|---|---|---|
| Rule (flat null, det + DRIFT_SD), **the verdict** | 0.0136 | 0.0212 | no | 0.642 |
| Detrended noise alone, flat | 0.0082 | 0.0128 | yes | 0.952 |
| Raw noise alone, flat | 0.0160 | 0.0250 | no | 0.525 |
| Local slope (option B, 0.0241) | 0.0136 | 0.0137 | no | 0.636 |
| Global slope (0.0548) | 0.0136 | 0.0031 | yes | 0.618 |

  These rows do not change the verdict. The sealed rule is the flat null at the rule noise; T sits below its margin.
  Two of the four variants would place T above their margins. The seal set both aside before the read. The
  detrended-only noise omits the drift term. A sloped null leaked under the stage-1 convexity (option B's local slope:
  0.112 in witness run 2), and the global slope is steeper still (§2.4).

## 3. Attribution (§6, applied)

- **Primary PASS.** The C_F ordering replicates on disjoint data, 8× larger. Across the nine class-number-1
  imaginary quadratic fields, R at matched N on the fresh slice is ordered by C_F = log(|D|(w/2)²) beyond chance,
  under an exact, SE-free null (ρ_s 0.867, p 0.0023).
- **Will's note (sealed at stage 1, carried by §6).** The C_F ordering is exactly the reverse of the L(1,χ) ordering.
  So this PASS supports the field invariant log(w²|D|) as the determinant. It does not distinguish an effect through
  the conductor from one through L(1,χ). It does distinguish C_F from plain log|D|: ℤ[i] and ℤ[ω] sit mid-ladder.
  The log|D| ρ_s of 0.48 against 0.87 is descriptive, not a sealed test of the difference.
- **β 0.45 PASS and β 0.40 PASS.** The ordering holds at those block scales too. These are one-way arms, and a PASS
  is their informative branch. At stage 1 both cells were FAIL (β 0.40 UNPOWERED; β 0.45 a plain FAIL under Will's
  annotation). Stage 2 does not relabel the stage-1 cells.
- **−7: FAIL (one-way arm: FAIL not informative).** This carries no conclusion. It does not show the displacement has
  gone, and it does not show it persists. The seal tabled a 0.752 PASS chance under persistence, and about 37% if the
  stage-1 gaps simply recur (§3a).
- **ℤ[√2] placement.** Descriptive: reported, with no verdict and no conclusion either way.

## 4. Post-hoc observations (labelled; no claim; candidates for leads only if Will wants them)

1. **The β 0.55 residual pattern replicates.** The nine OLS residuals on C_F at β 0.55 correlate +0.977 with the
   stage-1 residuals, on disjoint rows. With nine points this is one post-hoc number, but it is hard to reconcile with
   independent read noise: the departures from the C_F line look field-specific at this block size.
   - The −7 residual from the line, +0.0335, is close to stage 1's +0.0352.
   - T measures the gaps to the two neighbours instead, and those shrank: +0.0172 and +0.0137, against +0.0199 and
     +0.0194 at stage 1. The stage-2 slope is also steeper (0.0548 against 0.0455), which lifts −8 and −11 relative
     to −7.
   - At β 0.45 and 0.40 the residuals do not replicate (r −0.55 and −0.18), and the rank fit is near-perfect.
2. **Within-field drift along prime order, again in all nine fields at all three β.**
   - Every field's first segment has a higher R than its last: first/last ratio 1.07–1.12 at β 0.55, 1.07–1.13 at
     β 0.45 and 1.04–1.16 at β 0.40.
   - The total relative drift is −0.066 to −0.107 at β 0.55.
   - The raw noise rule is drift-inflated by construction. The β 0.55 raw ratio rose to 4.40× (stage 1 3.37×); the
     detrended ratio is 2.25× (stage 1 1.71×).
3. **The level of R rose.** The nine-field mean R at β 0.55 is 0.8718, against 0.8176 at stage 1. This is a
   different slice and a different K, so the levels are not comparable as a test.
4. **The secondaries' slopes.** The fresh-slice slopes at β 0.45 and 0.40 are about 2.0× and 2.5× the sealed
   stage-1 B. The power figures of 0.38 and 0.29 were computed at the sealed B, as sealed. The stage-2 slopes are
   themselves single estimates, so this is descriptive.

## 5. Cost

- **Double read:** CPU 21,106 s, i.e. **5.86 core-h** (sealed projection about 7.6). Wall 3.29 h per read.
- **Stage 2 total:** about 128 core-h (archives about 120, rehearsals about 2.2, segment noise 0.27, witnesses under
  0.1, read 5.86), against the sealed about 130.

## 6. Next

- Any further stage, or a lead from §4, is Will's call.
- Nothing is pushed. Pushes, including the tags `fn1-seal` and `fn1-seal2`, are Will's.

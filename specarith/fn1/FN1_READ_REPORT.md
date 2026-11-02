# FN1 stage-1 read report: the field ladder at X = 10¹⁰

**Sealed by** `FN1_SEAL.md` (tag `fn1-seal`, object e1f1e1fb on f05e5ca6).

**Read:** 2026-11-02 on spot. Sealed `fn1_read.py` sha256 e26002a7…, pins `fn1_pins.json` 693452cc….

## 0. Protocol

| Step | Record |
|---|---|
| Stamp | OTS 2026-11-01 23:31:51 UTC, four calendars (commit 42571dc2) |
| Bitcoin attestation | block 974194, 2026-11-02 00:39:24 UTC; merkle root c3e319e3… matches blockstream.info and mempool.space (`timestamps/FN1_SEAL_STAMP_2026-11-01_VERIFY.json`, commit 67c5df24). All six verifier checks hold. |
| Code on spot | `fn1_read.py`, the four rq1 modules it imports, both guard files and the pins match the sealed blobs by sha256 (checked before launch) |
| Double read | two separate processes (nice 10); both rc 0; 699 s and 697 s wall (0.19 core-h each) |
| cmp | **0**: `READ1.json` and `READ2.json` byte-identical (sha256 47c19dd2…), on spot and again after copying here |
| Verdicts | viewed only after the cmp |
| Seen-value guard | holds at β 0.40, 0.45, 0.55: ℤ[√2], ℤ[i], ℤ[ω] are bit-identical to RQ1 / RQ1-c |
| VOID conditions | none: no pin mismatch, mount present, guard holds, no ties, cmp 0 |

Outputs: `results/read/` (both reads, timing sidecars, logs, status, cmp).

## 1. Verdicts (as sealed)

| Test | Statistic | Verdict | Reading (§3 / §3a) |
|---|---|---|---|
| **Primary**, β 0.55, nine fields | ρ_s = **0.817**, Σd² = 22 (≤ 26), exact p = **0.0054** | **PASS** | informative (exact null) |
| ℤ[√2] placement, β 0.55 | R_−67 = 0.8568 < **R_ℤ[√2] = 0.8657** < R_−163 = 0.9346 | **PASS** | Will's label (2026-11-02): "PASS; margin (0.009) below the read-time per-field noise (~0.02); a middle placement by chance is ≈ 1 in 3" |
| Secondary β 0.45 | ρ_s = 0.400, Σd² = 72, p = 0.146 | FAIL | Will's label (2026-11-02): plain FAIL, "sealed as powered only under the sealed SE model; read-time noise at β 0.55 is 3.37× that model (cross-β inference)". Post-hoc direct estimate at β 0.45: 1.47× (power 0.61); see §3 |
| Secondary β 0.40 | ρ_s = 0.600, Σd² = 48, p = 0.048 | FAIL | **UNPOWERED** cell (0.47 at the model): one-way, so this FAIL is not informative |

**Read-time noise (§3a).**
- Pooled segment relSD 0.0251 gives noise_ratio = **3.37×** the sealed SE model.
- Power at that noise is **0.900**, which is ≥ 0.80, so a primary FAIL would have counted as informative.
- The primary passed, and a PASS is informative either way.

## 2. Descriptive (no verdict, as sealed)

**R_F by field** (rows ordered by C_F):

| Field | C_F | log\|D\| | R β 0.40 | R β 0.45 | R β 0.55 | rank of R at 0.55 |
|---|---|---|---|---|---|---|
| −7 | 1.946 | 1.95 | 0.5277 | 0.6225 | 0.7973 | 4 |
| −8 | 2.079 | 2.08 | 0.5453 | 0.6215 | 0.7773 | 0 |
| −11 | 2.398 | 2.40 | 0.5339 | 0.6360 | 0.7779 | 1 |
| ℤ[i] | 2.773 | 1.39 | 0.5429 | 0.6279 | 0.7896 | 3 |
| −19 | 2.944 | 2.94 | 0.5504 | 0.6266 | 0.7821 | 2 |
| ℤ[ω] | 3.296 | 1.10 | 0.5506 | 0.6331 | 0.8090 | 5 |
| −43 | 3.761 | 3.76 | 0.5751 | 0.6509 | 0.8340 | 6 |
| −67 | 4.205 | 4.20 | 0.5312 | 0.6175 | 0.8568 | 7 |
| −163 | 5.094 | 5.09 | 0.5867 | 0.6843 | 0.9346 | 8 |
| ℤ[√2] | 4.62 | — | 0.5816 | 0.6752 | 0.8657 | (between −67 and −163) |

The rank of R matches the rank of C_F at five of nine places (ℤ[i], ℤ[ω], −43, −67, −163). Of the Σd² = 22:
- 16 comes from −7, which has the lowest C but ranks fifth (R index 4);
- the other 6 comes from −8, −11 and −19, each displaced by one or two places.

**Other descriptive results.**
- **ρ_s against log|D|** at β 0.55: 0.500, p = 0.089. Against C_F it is 0.817. ℤ[i] and ℤ[ω] sit mid-ladder (R index 3 and 5), as C_F places them, not at the bottom where log|D| would put them.
- **Fresh-only ρ_s on the seven never-read w = 2 fields** (UNPOWERED by seal):
  - β 0.55: ρ_s 0.786, Σd² 12, p = 0.024, which is FAIL against the p < 0.01 bar. The seven fresh fields' R ranks follow C exactly except for −7 (fresh rank 3 instead of 0), which accounts for Σd² = 9 + 1 + 1 + 1.
  - β 0.45: ρ_s 0.393, p = 0.198.
  - β 0.40: ρ_s 0.607, p = 0.083.
- **Near-equal-C pairs** (ΔR = R_higher-C − R_lower-C):

| Pair | ΔC | ΔR β 0.40 | ΔR β 0.45 | ΔR β 0.55 |
|---|---|---|---|---|
| (−7, −8) | 0.134 | +0.0176 | −0.0010 | −0.0199 |
| (ℤ[i], −19) | 0.172 | +0.0075 | −0.0012 | −0.0075 |

  At β 0.55 both pairs are inverted. Both inversions are within about one read-time SD (about 0.02 in R).
- **ℤ[√2] placement at β 0.40 and 0.45:** it lies between −67 and −163 at both.

## 3. Attribution (§6, applied)

- **Primary PASS.** Across the nine class-number-1 imaginary quadratic fields, R at matched N is ordered by C_F = log(|D|(w/2)²) beyond chance, under an exact, SE-free null. This supports C_F as the field-level determinant found in RQ1 / RQ1-c, across nine fields and three unit groups.
- **Will's note (sealed).** The C_F ordering is exactly the reverse of the L(1,χ) ordering. So this PASS supports the field invariant log(w²|D|) as the determinant, and it does not distinguish an effect through the conductor from one through L(1,χ). It does distinguish C_F from plain log|D|: ℤ[i] and ℤ[ω] sit mid-ladder, as C_F predicts.
  - The log|D| ρ_s of 0.50 against 0.82 is descriptive, not a sealed test of the difference.
- **ℤ[√2] PASS.** A real quadratic field sits on the imaginary-field ladder where its C puts it. Per Will's label: the margin (0.009, to R_−67) is below the read-time per-field noise (about 0.02), and a middle placement among three by chance is about 1 in 3. It is a weak confirmation.
- **Secondaries.**
  - β 0.40 is UNPOWERED, so its FAIL carries nothing.
  - β 0.45: plain FAIL, annotated per Will (2026-11-02): "sealed as powered only under the sealed SE model; read-time noise at β 0.55 is 3.37× that model (cross-β inference)".
  - **Post-hoc, descriptive (Will's optional item; `lead/SEGNOISE_B045.json`).** The sealed §3a estimator was applied unchanged at β 0.45 (K_seg = round((2·⌊n/8⌋)^0.45)). The same script reproduces the sealed β 0.55 values exactly (pooled 0.02505, ratio 3.373). Results:
    - β 0.45: pooled relSD 0.0296, i.e. **1.47×** the sealed model. Detrended (descriptive): 1.06×.
    - At 1.47× the sealed power model gives power **0.61** for the β 0.45 test; at 1.06×, 0.86. The 1× recheck gives 0.89, matching the seal (`lead/FN1_POWER_B045_READNOISE.json`).
    - So the cross-β inference overstated the β 0.45 noise. Measured directly, the cell sits between the sealed model and L13's scales. This is descriptive: the sealed label stands as plain FAIL, with no one-way reading.
- **The SE question stays open.** The noise rule measured 3.37× the sealed model at β 0.55. That lies inside L13's range (method B ℤ[i] 4.1×). It is drift-inflated by construction; see §4.

## 4. Post-hoc observations (labelled; no claim; candidates for leads only if Will wants them)

1. **Within-field drift along prime order.** In all nine fields, the eight β 0.55 segment values R_seg fall from the first segment (small primes) to the last:
   - first/last ratio 1.06–1.15;
   - Spearman against segment index −0.67 to −0.98.

   Linear detrending reduces each field's segment relSD by a factor of 1.4–3.1. The seal's "known bias" note anticipated this: the noise estimate leans toward UNPOWERED. A detrended noise_ratio would be lower than 3.37, but no detrended estimate was sealed and none is used. The drift says R at fixed K depends on the prime range, i.e. on X. Comparing R across fields is still matched (same n, same prime-order prefix rule).
2. **The −7 displacement.** −7 alone carries 16 of Σd² = 22. Its R is higher than −8, −11, ℤ[i] and −19. Without −7 the nine-field ordering would be close to monotone. This is one field and post hoc; the stage-2 10¹¹ data would show whether it persists.
3. **−67 at small K.** At β 0.40 and 0.45, −67 has the second-lowest and the lowest R respectively, against C rank 7. Unpowered cells; noted only.

## 5. Cost

Double read: 0.39 core-h (sealed estimate 0.6). Stage 1 total: about 17 core-h (archives 14.24, witnesses about 0.3, dry runs about 2, read 0.39).

## 6. Next

- Post-hoc L′/L lead (Will 2026-11-02): `lead/FN1_LEAD_LPRIME.md`.
- Stage 2 (10¹¹): proposed seal `FN1_STAGE2_SEAL.md` (not sealed; for Will's review). No stage-2 compute has been started.

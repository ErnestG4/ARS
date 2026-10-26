# RQ1 reading seal — STATUS: RESUBMISSION DRAFT (round 88 fixes; round 89 margin rule committed before any witness result was read; witness running). Not sealed; no OpenTimestamps receipt; nothing read

**Step 3 runs only after:** Will approves this seal, its OTS receipt is Bitcoin-attested and verified on two explorers,
the environment is pinned, and the double read is in place.

**Archives.** The reduced generators, one per split prime, from `rq1_archive.py`: ℤ[√2] to 10¹¹ and ℤ[i] to
1.01·10¹¹.
- Their hashes are in §6: for each, the sha256 over the segment hashes, plus per-segment hashes in `MANIFEST.json`.
- No statistic of the angles has been computed from either.

## 1. Statistic
R(β, X) = Var(N_{K,X}) / (N/K):
- **Var:** RW's eq. 1.2 (window-centre average over θ ∈ [0, 1), window 1/K), computed exactly (`rq1_angles.var_exact`).
- **N:** the number of prime ideals above split p with N𝔭 ≤ X (both ideals: θ and 1 − θ). Inert primes and 2 are
  excluded; RW's N would include them, which differs by ≤ √X points at θ = 0.
- **K = round(N^β).**
- **The θ maps (round 88), as `rq1_read.field_thetas` computes them:**
  - ℤ[√2]: for the stored reduced generator π = a + b√2 (a > 0, b ≥ 0, 0 ≤ θ ≤ ½),
    θ = log|π/π′| / (2 log ε) = (2 log(a + b√2) − log p) / (2 log ε), with ε = 1 + √2 and p = |a² − 2b²|.
  - ℤ[i]: for the stored Cornacchia pair 0 < u < v (u² + v² = p), θ = atan(u/v) / (π/2) ∈ (0, ½). That is
    arg(v + iu)/(π/2), RW's θ_𝔭 = arg(π_𝔭)/(π/2) mod 1 (the angle modulo the units ±1, ±i) for the ideal (v + iu).
  - Both fields: the other ideal above p is added at 1 − θ (np.mod(1 − θ, 1)). So both sets are exactly
    mirror-symmetric, which is why the SE model is calibrated on mirror-symmetrised sets (§5).

## 2. X values and K grid
- **X:** 10¹⁰ (N ≈ 4.6·10⁸) and 10¹¹ (N ≈ 4.1·10⁹), both from the one archive.
- **β grid:** {0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90}, the same at both X.

## 3. Prediction (Step 0 §3)
- **Leading order, at the level of RW's heuristic:** R → min(1, 2β).
- **Lower-order terms are not derived.**
- **A heuristic next-order statement** (not a derivation):
  - With log q(λ^k) = 2 log k + C_F, the field enters only through C_F: C_ℤ[√2] = log(8π²/log²ε) = 4.62 and
    C_ℤ[i] = log 16 = 2.77.
  - So at matched N and β, ℤ[√2] should sit above ℤ[i] in the rigidity regime by roughly
    (C_ℤ[√2] − C_ℤ[i])/log N ≈ 1.85/log N (≈ 0.09 at X = 10¹⁰).
  - The difference should vanish in the saturation regime.

## 4. Why a direct test against min(1, 2β) is not proposed
- **The finite-X correction is not small.** On ℤ[i], descriptively and unsealed (Step 1, G3), the same statistic at
  x = 10⁸ is 0.24 at β = 0.3 (prediction 0.60), 0.61 at β = 0.5 (1.0) and 0.92 at β = 0.8 (1.0). At x = 10⁷ it is
  lower still.
- **Scaled to X = 10¹⁰–10¹¹** by 1/log X, the deviation near β = ½ is still tens of percent.
- **So the direct test would fail on the known finite-X effect,** not on anything about ℤ[√2]. A tolerance wide
  enough to pass it would make it uninformative.

## 5. Reading (B), as amended in round 86 (options A and C are not chosen; C may use the reserved X = 10¹²)
**Matching variable.** N is the number of prime ideals above split primes.
- ℤ[i]: both ideals above each p ≡ 1 mod 4; inert primes and (1 + i) excluded.
- ℤ[√2]: both ideals above each p ≡ ±1 mod 8; inert primes and 2 excluded.
- At each ℤ[√2] X (10¹⁰, 10¹¹), with n = the number of ℤ[√2] split primes ≤ X (manifest row count), the ℤ[i] set is
  its first n split primes in increasing order, both ideals each. N = 2n is then exactly equal for both fields, and
  K = round(N^β) is identical. This is what `rq1_read.py` does.
  - The cut is taken from the manifests' row counts; no angle is read to choose it.
  - It falls just above X: the n-th ℤ[i] split prime lies in (10¹⁰, 1.01·10¹⁰] (n = 227,524,967; 227,523,275 ℤ[i]
    split primes are ≤ 10¹⁰) and in (10¹¹, 1.001·10¹¹] (n = 2,059,026,114; 2,059,020,280 are ≤ 10¹¹).
  - (Corrected before sealing: the earlier wording "smallest X_i with N_ℤ[i](X_i) ≥ N_ℤ[√2](X)" did not match the
    code, which matches N exactly.)

**Heuristic, derived (`rq1_heuristic.py --mirror` → `results/HEURISTIC_B_MIRROR.json`; no archive data used).**
- **The formula:** R_F(K, X) = K·Σ_{k≠0} sin²(πk/K)/(πk)²·min(1, (2 log|k| + C_F)/L). That is RW's §5 form, with the
  field entering only through the conductor constant, C_ℤ[√2] = 4.6214 and C_ℤ[i] = 2.7726.
- **The offset** is R_ℤ[√2] − R_ℤ[i], with L = log X, or log N as a variant. K is at the matched N (manifest row
  counts):

| β | K (10¹⁰ / 10¹¹) | 10¹⁰: offset (L = log X / log N) | SE_diff | offset/SE | 10¹¹: offset | SE_diff | offset/SE |
|---|---|---|---|---|---|---|---|
| 0.20 | 54 / 84 | +0.079 / +0.091 | 0.133 | 0.6 | +0.072 / +0.082 | 0.106 | 0.7 |
| 0.30 | 396 / 766 | +0.080 / +0.091 | 0.071 | 1.1 | +0.073 / +0.083 | 0.051 | 1.4 |
| **0.40** | 2,906 / 7,013 | +0.079 / +0.085 | 0.034 | **2.3** | +0.072 / +0.077 | 0.022 | **3.3** |
| **0.45** | 7,873 / 21,213 | +0.076 / +0.065 | 0.023 | **2.8** | +0.070 / +0.062 | 0.014 | **4.4** |
| 0.50 | 21,332 / 64,172 | +0.069 / +0.029 | 0.015 | 1.9 | +0.064 / +0.026 | 0.009 | 2.9 |
| 0.55 | 57,801 / 194,125 | +0.041 / +0.011 | 0.010 | 1.1 | +0.035 / +0.009 | 0.005 | 1.6 |
| 0.60 | 156,616 / 587,239 | +0.016 / +0.004 | 0.006 | 0.7 | +0.013 / +0.003 | 0.003 | 0.9 |
| 0.70 | 1,149,850 / 5,373,835 | +0.002 / +0.001 | 0.002 | 0.2 | +0.001 / +0.000 | 0.001 | 0.3 |
| ≥ 0.80 | — | 0.000 | ≤ 0.001 | — | 0.000 | ≤ 0.001 | — |

  offset/SE uses the smaller of the two offset variants.
- **SE model (round 88: mirror pairing):** relative SD of the estimator = sqrt(2/(cK)), with c = 0.627.
  - Both archives are exactly mirror-symmetric (θ and 1 − θ), and the window at c and its mirror window at 1 − c
    then hold equal counts, so only half the window positions are independent.
  - c is therefore calibrated by Monte Carlo on symmetrised sets (n/2 points plus their mirrors): Poisson
    0.63–0.78, CUE 2.6–5.0. The unsymmetrised calibration was Poisson 1.4–1.8, CUE 6–10, so the mirror pairing
    halves c and multiplies SE_diff by about √2.
  - c_used = 0.627 is the smallest symmetrised c, so the SE is conservative for rigid data.
  - The empirical SEs at the matched N are measured by the witness and reported against this model (below).
- **The offset sits at ≈ ΔC/L = 1.85/log X** in the rigidity regime (+0.08 at 10¹⁰, +0.07–0.08 at 10¹¹), as round 86
  expected.

**A caveat on the heuristic, from the ℤ[i] data at x = 10⁸ (descriptive; Step 1, G3).**
- Its absolute level overshoots: 0.50 against 0.243 measured at β = 0.30, 0.83 against 0.607 at 0.50, and 0.98 against
  0.878 at 0.66.
- Its saturation sets in too early, as the missing lower-order terms of Chen et al. (the −K_Φ term below the crossover)
  would imply.
- **The offset is a difference, so a common level error cancels to first order. The size of the offset is reported,
  not gated.**

**B2 (margin rule, round 89; the pass criterion).**
- D = R_ℤ[√2] − R_ℤ[i] > k·s·SE_diff at every remaining gated cell (`rq1_read.b2_rule`). The round-88 sign rule
  (k = 0) is replaced.
  - SE_diff is the sealed model on the read's own R values (`rq1_read.se_diff`, c = 0.627).
  - k ∈ {0, 0.5, 1.0, 1.5} and the per-cell scale s (1 unless the SE check triggers) are fixed by the witness
    selection and confirmed on fresh seeds (below), before the seal is stamped.
- The candidate cells are β ∈ {0.40, 0.45} at both X: the β ≤ 0.45 cells where the heuristic offset is ≥ 2·SE_diff
  under the mirror-calibrated SE. The SE check against the witness may remove some (below). The conjunction's power
  is measured by the planted witness.
- **UNPOWERED, reported and not gated:** β = 0.20 and 0.30 at both X. β = 0.30 at 10¹¹ was gated in the round-87
  draft (offset/SE 2.1) and drops to 1.4 under the mirror calibration (round 88).
- β ≥ 0.50 is outside B2 (the rigidity regime is β ≤ 0.45; round 86). β = 0.50 at 10¹¹ reaches offset/SE 2.9 on
  the smaller (log N) variant but is not gated; it is reported with D(β).
- The magnitude is reported against 1.85/log X and 1.85/log N at every β.

**B1: dropped as a gate (round 87, option (iii)). Reported descriptively as D(β).**
- **Why:** the heuristic's saturation timing is contradicted by our own ℤ[i] data at 10⁸, which is still unsaturated
  (0.88–0.92) at β = 0.66–0.80 where the heuristic has saturated. A B1 FAIL therefore could not be attributed: it might
  be a ℤ[√2]–ℤ[i] difference, or only the heuristic's crossover.
- **What is reported:** D(β) = R_ℤ[√2] − R_ℤ[i] at matched N, at every β on the grid and at both X, with SE_diff. It
  is plotted with the heuristic's ΔC/L curves (L = log X and L = log N) overlaid, from `results/HEURISTIC_B.json`.
  No verdict.

**Reading (round 89).** PASS iff the confirmed rule holds at every remaining gated cell: D > k·s·SE_diff. FAIL iff
any remaining gated cell fails it.
- If no k qualifies in the selection, or the confirmation fails, B2 is UNPOWERED at these X. The read is then
  descriptive only: D(β) at every β, with SE_diff and the magnitudes against 1.85/log X and 1.85/log N. No verdict.
- The X-dependence of R and of D is reported, not gated.

**Attribution (round 88).**
- **PASS** supports the heuristic's field dependence through the conductor constant, and its direction (ℤ[√2]
  above ℤ[i] at matched N in the rigidity regime).
- **FAIL** means that field dependence does not show as predicted at these X, for example because lower-order
  terms dominate. It is not a statement about the leading order (§4).
- **UNPOWERED (round 89):** no k qualifies, or the confirmation fails. Descriptive read, no verdict. This replaces
  round 88's "a witness failure makes the read VOID".
- **VOID:** a `cmp` mismatch between the two reads, or a hash mismatch (on the read code, the selection or
  confirmation JSON, or any archive segment).

**Witness for B2 (round 88, TOOLKIT §9.D; `rq1_witness.py`, criteria committed in fdf9f26f before running; subset-draw fix 5640055e, criteria unchanged).**
Synthetic only, at the archives' matched N. Every set is n points φ ∈ [0, ½) plus their mirrors 1 − φ, as the data
are. The estimator, K, the gated cells and the rule are the read's own (imported from `rq1_read.py`).
- **Null (false PASS rate).** 100 replicates of two independent symmetrised i.i.d. sets.
  - The 10¹⁰ set is a uniformly random subset of the 10¹¹ set's points, so the cells are correlated as in the read:
    across β (same data) and across X (nesting). The round-87 "1/32" reasoning assumed independent cells and is
    withdrawn.
  - Criterion: the B2 rule's false PASS count ≤ 10 of 100 (rate ≤ 0.10).
  - A priori (not a criterion): with the β = 0.40 / 0.45 signs correlated at 0.3–0.6 within an X and the two X
    nearly independent, the rate is ≈ 0.09–0.12, so this arm may land near its threshold.
- **Planted (power).** 100 replicates of two mixtures, each a mirror-symmetric rigid lattice of fraction ρ plus
  i.i.d. points (R ≈ 1 − ρ at every K, checked: 0.895 ± 0.008 at 1 − ρ = 0.886, 0.502 ± 0.005 at 0.5).
  - ρ_ℤ[i] = 1 − (the largest heuristic R_ℤ[i] over the gated cells and both L variants, 0.886) = 0.114, so the
    planted level is the heuristic's highest (SE ∝ R: conservative).
  - ρ_ℤ[√2] = ρ_ℤ[i] − ΔR_X, with ΔR_X the smallest heuristic offset over the gated β at that X: 0.065 at 10¹⁰,
    0.062 at 10¹¹.
  - The 10¹⁰ and 10¹¹ planted sets are independent (a random subset of a lattice is not rigid), which lowers the
    conjunction's PASS probability against positive correlation: conservative.
  - Criterion: the rule reads PASS in ≥ 90 of 100.
- Round-88 summary (`rq1_witness.py summary`, `witness/WITNESS.json`): the sign rule against the criteria above.
  It is still written and reported, but round 89 supersedes it as the read's gate: the read takes the round-89
  selection and confirmation, not this summary.
- Reported, not gated: the empirical SD of R per field and cell and of D per cell, against R·sqrt(2/(cK)) and
  SE_diff; the mean planted D against ΔR_X; the null's per-cell positive fractions and pairwise sign agreement.

**B2 rule selection and confirmation (round 89; committed before any witness result was read).**
- **SE check** (`rq1_witness.py select`, on the round-88 replicates).
  - Per gated cell and arm: empirical SE_diff = the SD of D over the 100 replicates; model = the mean of the
    replicates' model SE_diff (`rq1_read.se_diff` on each replicate's own R). ratio = empirical / model, the larger
    over the two arms.
  - If ratio > 1.2 at any gated cell, every gated cell's offset/SE (the §5 table) is divided by its ratio; cells
    below 2 become UNPOWERED. The remaining cells' rule then uses s = ratio, i.e. the empirical SE. Otherwise s = 1.
- **Selection** (no new compute). The round-88 replicates are re-scored at k ∈ {0, 0.5, 1.0, 1.5} on the remaining
  cells. The chosen k is the smallest with null false PASS ≤ 5/100 and planted PASS ≥ 90/100. If none qualifies, B2
  is UNPOWERED. Output: `witness/SELECTION.json` (the SE check, the table at every k, the rule).
- **Confirmation** (`run_rq1_witness_confirm_spot.sh`, only if a k was selected). 100 fresh null and 100 fresh planted
  replicates, on seed base 8889 instead of 8888, with the same sets, N and planted parameters as round 88. They are
  scored at the selected rule, with the same criteria (≤ 5 and ≥ 90). Fail → B2 UNPOWERED. Output:
  `witness_confirm/CONFIRM.json`. Cost as the round-88 witness: about 46 spot core-h modelled; that run's first wave
  measured 0.597×.
- Selection and confirmation are reported separately, with the empirical against the model SEs.
- **Symmetrisation (confirmed in the code).** In both arms every set is n points φ plus their n mirrors 1 − φ. In
  `planted_set` the n − m i.i.d. points and the m lattice points are merged into the first half, and the whole half
  is mirrored. So the i.i.d. part is n − m points plus their mirrors, as in the null arm.
- **A priori forecast (the sealed SE model, cells treated as independent; not a criterion and not a witness
  result).**
  - The planted design puts the cells at z = ΔR_X / SE_diff = 1.51 (10¹⁰, β 0.40), 2.48 (10¹⁰, 0.45), 2.24 (10¹¹,
    0.40) and 3.89 (10¹¹, 0.45). The 10¹⁰ β = 0.40 cell is below 2 because ΔR_X is the smallest offset at that X
    (from β = 0.45) and the planted level is the heuristic's highest R (round-88 conservative choices).
  - Planted PASS probability: 0.92 at k = 0, 0.79 at k = 0.5, 0.58 at k = 1.0, 0.32 at k = 1.5 (fully correlated
    cells within an X: 0.93, 0.84, 0.69, 0.50).
  - Null false PASS probability: 0.0625 at k = 0 (independent cells), more with the positive correlation the nesting
    and shared data give; 0.009 at k = 0.5.
  - So the likeliest outcome on this grid is that no k qualifies (k = 0 fails the null at ≤ 5, k ≥ 0.5 fails the
    planted at ≥ 90), and B2 is UNPOWERED. This forecast is stated before the witness lands and changes nothing in
    the rule.

**Reserved:** X = 10¹² is unseen. It is held for a possible option (C) prediction (Chen et al.'s refined conjecture
adapted to ℤ[√2]). No statistic at 10¹².

**Order (rounds 87–89):**
1. Will approves this seal.
2. The seal file is stamped with OpenTimestamps.
3. Wait for the receipt's Bitcoin attestation, verified on two explorers.
4. On spot, re-check the sha256 of `rq1_read.py`, `rq1_angles.py`, the selection JSON and (if run) the confirmation
   JSON against §6 (`sha256sum -c`). Any mismatch: VOID (hash), no read.
5. Read in the pinned environment (§6), as a double read in two separate processes from a clean start, each under a
   40 GB memory cap. Both must produce byte-identical result JSONs.

**Chen et al. cross-check (`CHEN_XCHECK.md`).**
- **Secondary: PASS.** Our transcription of their Appendix A on our ℤ[i] angle set reproduces their Figure 1's 25
  points within 0.0014 (tolerance 0.01). This validates the angle set and the statistic machinery.
- **Primary (their Mathematica code): blocked; not needed** (round 87). No Wolfram activation.

## 6. Pins (Step 2 data and the read)
**ℤ[√2] archive** (spot `~/tmp/claude/specarith/rq1/archive/`; manifest copy `results/archive_zs2/MANIFEST.json`,
sha256 aa6d15fc67b262021f4ccda3dc9ebf6edf064bb84762fcf4ed46626ebc5722f1).
- **Contents:** 1,000 segments of 10⁸, 2,059,026,114 split primes below 10¹¹ (227,524,967 below 10¹⁰).
- **Integrity:** passes on every segment (the norms are exactly the split primes, in order).
- **Hash:** sha256 over the segment hashes c8433b089ebfc618a2bb725dc6a7565926167eb685c355951616db6cb030c0f0.
- **Generator:** `rq1_angles.py` @ e179155a (sha256 a30f02ea…442b) with `rq1_archive.py` @ b015d653.
  - The current `rq1_angles.py` regenerates segments 0 and 999 bit-identically.
- **No statistic computed.**

**ℤ[i] archive** (spot `~/tmp/claude/specarith/rq1/archive_zi/`, to 1.01·10¹¹; manifest copy
`results/archive_zi/MANIFEST.json`, sha256 8fd61856ea8a76c9b6fdc9f0f2e5cd6affc60d98a6ddae3e35b29d57b982d0cb).
- **Contents:** 1,010 segments of 10⁸, 2,078,758,475 split primes p ≡ 1 mod 4 below 1.01·10¹¹ (227,523,275 below
  10¹⁰). Each row is the Cornacchia pair (u, v), 0 < u < v, u² + v² = p; inert primes and (1 + i) are excluded.
- **Integrity:** passes on every segment (u² + v² is exactly the split primes, in order, with 0 < u < v).
- **Hash:** sha256 over the segment hashes a268e132e08030cb7f5fe5f223d0e7bee42959a9bbf8cc006fe1d2dfb5b72bc8
  (recomputed locally from the manifest).
- **Generator:** `rq1_angles.py` sha256 7764c23e…1a0c (the read-code pin below) with `rq1_archive.py` sha256
  eed304ce3512719eadec173cfae74aa3ece96540b150e6e8a6a17feee2cf037f (@ dde7502f), both checked identical on spot.
- **No statistic computed.**
- **Cost:** 27.9 spot core-h against 23.1 modelled (1.21×), 1 h 33 min wall at 28 processes, 16 GB.

**Version drift (round 88).**
- `rq1_angles.py` a30f02ea (the ℤ[√2] archive's generator, @ e179155a) → 7764c23e (current): the only difference is
  the added function `gen_segment_zi` (the ℤ[i] generator). `primes_in`, `sqrt_mod`, `gcd_zs2`, `reduce_zs2`,
  `gen_segment` and `thetas_from_ab` (the ℤ[√2] generation and angle path) are unchanged.
- Regeneration with the current code (`rq1_regen_check.py`, `results/r88/REGEN_CHECK.json`): segments 0, 999 and 10
  drawn with seed 8803 (58, 83, 259, 406, 482, 525, 677, 823, 848, 978) are all bit-identical to the manifest
  hashes.

**Angle precision (round 88; `rq1_precision.py`, `results/r88/PRECISION.json`).** Primes in
[1.01·10¹¹, 1.01·10¹¹ + 2·10⁶), outside both archives: 39,354 ℤ[√2] and 39,475 ℤ[i] split primes.
- Float θ (the read's map) against mpmath at 50 digits: max |Δθ| 2.1·10⁻¹⁵ (ℤ[√2]) and 1.1·10⁻¹⁶ (ℤ[i]); the mirror
  1 − θ: 2.2·10⁻¹⁵ and 1.5·10⁻¹⁶.
- Unit shifts (× ε, ε², ε³ for ℤ[√2]; × i, i², i³ for ℤ[i]) shift θ by exactly 1, 2, 3: deviations 1.8·10⁻¹⁵ and
  4.4·10⁻¹⁶ in float, ≤ 2.3·10⁻⁴⁹ in mpmath.
- The worst float deviation is 9.7·10⁻⁷ of the smallest window, 1/K_max = 1/450,010,519 = 2.2·10⁻⁹ (β = 0.90 at
  10¹¹).

**Read code (round 89).**
- `rq1_read.py`, sha256 f63ebc47cec7f553d4b191623570fc9c8f5dd3cd83fd1ba9a60061c1fb0c4be0 (round 89: `se_diff`, the margin `b2_rule`, `load_rule`; `var_stream`,
  `field_thetas`, `load_field` and `sorted_uniform` unchanged).
- `rq1_angles.py`, sha256 7764c23ef64c1f53efb1fb12bd1152d93f8956745cf623d40af93e108e7d1a0c.
- `rq1_witness.py`, sha256 d7a84441e962222f31ca3542d02c093a8f70c0f0bc2c522adb371f972341dc14 (round 89: `select`, `confirm`, the seed base; the task path at
  seed base 8888 is the round-88 one).

**Round-88 witness run** (spot, 200 tasks, seed base 8888), produced by the round-88 code:
- `rq1_read.py` 60dc1d9a7b3e27c6ebb97c6074667626bce40a3e19988dc4106fdba09b734916 (@ fdf9f26f);
- `rq1_witness.py` b00cb0e747241252fb0ef6c3e55849a62532396e61bce924b7c8889f75d132f0 (@ 5640055e; the fdf9f26f version
  failed on its first null tasks, numpy's hypergeometric limit, and was fixed before any replicate completed).
- **Round-88 summary (sign rule):** WITNESS_PENDING
- **Round-89 selection** (`witness/SELECTION.json`): SELECTION_PENDING
- **Round-89 confirmation** (`witness_confirm/CONFIRM.json`): CONFIRM_PENDING
- **Estimator check** (`rq1_read_check.py`, rerun on spot in ph6c, numba 0.68.0; `results/r88/READ_ESTIMATOR_CHECK.json`):
  - exact streaming variance against `var_exact` to 8.0·10⁻¹³ relative (K = 2…5000), and 2.4·10⁻¹² on
    mirror-symmetrised sets;
  - the sorted-uniform generator's mean ratio 0.998 ± 0.010 against 1 − 1/64 = 0.984;
  - bit-identical to the round-87 local values. Synthetic data only.

**Pinned environment (spot):**
- conda env `ph6c`: Python 3.12.15, numpy 2.5.3, scipy 1.18.1, numba 0.68.0 (spot; local is 0.66.0), mpmath 1.4.1;
- kernel 6.19.14-200.fc43;
- single-threaded (OMP / OPENBLAS / MKL / NUMBA_NUM_THREADS = 1).

**Double read** (two separate processes, one after the other, each capped at 40 GB; the measured peak at the 10¹¹
matched N is 30.8 GiB, `results/r88/memprobe.log`):

    cd ~/tmp/claude/specarith/rq1
    sha256sum -c read_pins.sha256                  # rq1_read.py, rq1_angles.py, SELECTION.json, CONFIRM.json (§6)
    for i in 1 2; do
      systemd-run --user --scope -p MemoryMax=40G -p MemorySwapMax=0 env NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 \
        ~/miniforge3/envs/ph6c/bin/python rq1_read.py archive archive_zi witness/SELECTION.json \
        witness_confirm/CONFIRM.json read$i.json   # "-" in place of CONFIRM.json if no k was selected
    done
    cmp read1.json read2.json                      # must be byte-identical; otherwise the read is VOID

- `read_pins.sha256` is committed with this seal, holding the §6 hashes of the read code and the round-89 JSONs.
- **Cost:** 2 fields × 2 X × 10 estimator passes, single core. Locally a pass takes 1.6·10⁻⁸ s per point, so
  ≈ 65 s per pass and ≈ 11 min per field at 10¹¹ (1/9 of that at 10¹⁰), plus hashing, loading and sorting (the sort
  and one pass: 3.4 min measured on spot). About 0.6 local core-hours per read, ≈ 1.4 spot core-hours at 2.3.
- **The first-wave rule applies to the read:** if the first X's timing exceeds the model by more than 25%, stop and
  report.

# RQ1 reading seal — STATUS: DRAFT for Will (rounds 85–86; B1's range is still to be chosen). Not sealed; no OpenTimestamps receipt; nothing read

**Step 3 runs only after:** Will approves this seal, its OTS receipt is Bitcoin-attested and verified on two explorers,
the environment is pinned, and the double read is in place.

**Archive.** The ℤ[√2] reduced generators, one per split prime, from `rq1_archive.py`.
- Its hash goes in §6 when Step 2 finishes: the sha256 over the 1,000 segment hashes, plus per-segment hashes in
  `MANIFEST.json`.
- No statistic of the angles has been computed from it.

## 1. Statistic
R(β, X) = Var(N_{K,X}) / (N/K):
- **Var:** RW's eq. 1.2 (window-centre average over θ ∈ [0, 1), window 1/K), computed exactly (`rq1_angles.var_exact`).
- **N:** the number of prime ideals above split p with N𝔭 ≤ X (both ideals: θ and 1 − θ). Inert primes and 2 are
  excluded; RW's N would include them, which differs by ≤ √X points at θ = 0.
- **K = round(N^β).**

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
- At each ℤ[√2] X (10¹⁰, 10¹¹), the ℤ[i] cut X_i is the smallest X_i with N_ℤ[i](X_i) ≥ N_ℤ[√2](X), taken from the
  manifests' row counts (no angle is read to choose it).
- K = round(N^β) is then identical for both fields.

**Heuristic, derived (`rq1_heuristic.py` → `results/HEURISTIC_B.json`; no archive data used).**
- **The formula:** R_F(K, X) = K·Σ_{k≠0} sin²(πk/K)/(πk)²·min(1, (2 log|k| + C_F)/L). That is RW's §5 form, with the
  field entering only through the conductor constant, C_ℤ[√2] = 4.6214 and C_ℤ[i] = 2.7726.
- **The offset** is R_ℤ[√2] − R_ℤ[i], with L = log X, or log N as a variant:

| β | 10¹⁰: offset (L = log X / log N) | SE_diff | offset/SE | 10¹¹: offset | SE_diff | offset/SE |
|---|---|---|---|---|---|---|
| 0.20 | +0.079 / +0.091 | 0.089 | 0.9 (unpowered) | +0.072 / +0.082 | 0.071 | 1.0 (unpowered) |
| 0.30 | +0.080 / +0.091 | 0.047 | 1.7 (unpowered) | +0.073 / +0.083 | 0.034 | 2.1 |
| 0.40 | +0.079 / +0.085 | 0.023 | 3.4 | +0.072 / +0.077 | 0.015 | 4.9 |
| 0.45 | +0.076 / +0.065 | 0.015 | 4.2 | +0.070 / +0.062 | 0.009 | 6.5 |
| 0.60 | +0.016 / +0.004 | 0.004 | 1.0 | +0.013 / +0.003 | 0.002 | 1.4 |
| 0.70 | +0.002 / +0.001 | 0.002 | 0.4 | +0.001 / +0.000 | 0.001 | 0.4 |
| ≥ 0.80 | 0.000 | ≤ 0.001 | — | 0.000 | ≤ 0.001 | — |

- **SE model:** relative SD of the estimator = sqrt(2/(cK)), with c = 1.4. That is the smallest c in a Monte Carlo
  calibration (Poisson 1.4–1.8, CUE 6–10), so the SE is conservative for rigid data.
- **The offset sits at ≈ ΔC/L = 1.85/log X** in the rigidity regime (+0.08 at 10¹⁰, +0.07–0.08 at 10¹¹), as round 86
  expected.

**A caveat on the heuristic, from the ℤ[i] data at x = 10⁸ (descriptive; Step 1, G3).**
- Its absolute level overshoots: 0.50 against 0.243 measured at β = 0.30, 0.83 against 0.607 at 0.50, and 0.98 against
  0.878 at 0.66.
- Its saturation sets in too early, as the missing lower-order terms of Chen et al. (the −K_Φ term below the crossover)
  would imply.
- **The offset is a difference, so a common level error cancels to first order. The size of the offset is reported,
  not gated.**

**B2 (sign; the pass criterion).**
- R_ℤ[√2] − R_ℤ[i] > 0 at β ∈ {0.40, 0.45} at both X, and at β = 0.30 at X = 10¹¹. These are the β where the heuristic
  offset is ≥ 2·SE_diff (power ≥ 0.977 if the true offset equals the heuristic).
- **β = 0.20 (both X) and β = 0.30 at 10¹⁰ are marked UNPOWERED:** reported, not gated.
- The magnitude is reported against 1.85/log X and 1.85/log N at every β.

**B1 (leading-order universality; tolerance and its basis).**
- **Basis from the lower-order estimate:** the heuristic offset at β ≥ 0.6 is ≤ 0.016 (L = log X) or ≤ 0.004
  (L = log N), and 2·SE_diff ≤ 0.008. So 0.05 is ≥ 2× the heuristic's maximum plus 2 SE at β ≥ 0.6.
- **But the heuristic saturates too early** (caveat above). On ℤ[i] at 10⁸ the data are still unsaturated at
  β = 0.66–0.80 (0.88–0.92).
  - Where unsaturated, the heuristic's own offset is the full ΔC/L ≈ 0.07–0.09, which exceeds 0.05.
  - **The 0.05 tolerance therefore has a basis only where both fields are saturated, and the data at 10¹⁰–10¹¹ may not
    yet be.**
- **Will's choice before sealing:**
  - (i) B1 at β ≥ 0.8 only, with tolerance 0.05;
  - (ii) B1 at β ≥ 0.6 with tolerance ΔC/log X + 2·SE_diff (0.088 at 10¹⁰, 0.077 at 10¹¹);
  - (iii) drop B1 and keep B2.
- Recommended: (i). It is the regime where the heuristic and the ℤ[i] trend both point to saturation.

**Reading.** PASS iff B1 (as chosen) and B2 both hold at X = 10¹⁰ and at X = 10¹¹. The X-dependence of R and of the
offset is reported, not gated (round 86, replacing B3).

**Power and witnesses (run on the archives' sizes, not their angles):**
- **B2's witness:** uniform i.i.d. angles at each matched N. Its "offset" against a second independent uniform set
  must be positive at ≤ 50% of the B2 β (no sign pattern).
- **B1's witness:** ℤ[√2] with every θ replaced by an independent uniform draw must fail B1 (R = 1 − 1/K against
  ℤ[i]'s saturated value) wherever ℤ[i] is below 0.95.

**Reserved:** X = 10¹² is unseen. It is held for a possible option (C) prediction (Chen et al.'s refined conjecture
adapted to ℤ[√2]). No statistic at 10¹².

**Order:** final seal → Will approves → OTS receipt Bitcoin-attested → read, in a pinned environment with a double
read.

## 6. To be filled when Step 2 finishes
The archive manifest hash, the row counts at X = 10¹⁰ and 10¹¹, and the pinned environment (python, numpy and the
`rq1_angles.py` sha256).

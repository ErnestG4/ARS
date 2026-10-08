# Phase 2, item 1 — findings: ζ consecutive spacings against CUE(N_eff), per height

Run under **PH2_SEAL_2.1** (commit a54bb182, tag `ph2-seal-2.1`; amendments A1–A8). Real run on spot 2026-10-07
22:39–23:00 (PDT), code sha256 = sealed (results/run/code_sha256_run.txt), every data file hash-checked by run.py before
it was opened. Tables: results/run/FINDINGS_TABLES.md; figure results/run/kappa_vs_height.png; per-bin JSON
results/run/<bin>.json. Estimand κ = N/N_eff (κ = 1: the zeros' spacing law is CUE(N_eff)'s; κ = ∞: the sine kernel).

## 1. Sealed verdicts

| bin | log(E/2π) | N_eff | zeros | SECONDARY κ̂ (the sharp test) | G1 | PRIMARY κ̂ [widened] | G1 |
|---|---|---|---|---|---|---|---|
| A | 9.4–10.5 | 2.33 | 243,454 | 1.211 [1.165, 1.262] | **FAIL** | 1.405 [1.193, 1.624] | **NOT RESOLVABLE (achieved)** ¹ |
| B | 11.0–12.1 | 2.69 | 1.40·10⁶ | 1.169 [1.147, 1.191] | **FAIL** | 1.313 [1.186, 1.441] | **FAIL** |
| P1 | 12.9–13.5 | 3.05 | 4.43·10⁶ | 1.133 [1.119, 1.147] | **FAIL** | 1.243 [1.157, 1.329] | **FAIL** |
| P2 | 14.9–15.0 | 3.45 | 5.01·10⁶ | 1.103 [1.088, 1.118] | **FAIL** | 1.188 [1.121, 1.255] | **FAIL** |
| P3 | 17.0 | 3.91 | 5.68·10⁶ | 1.085 [1.069, 1.103] | **FAIL** | 1.152 [1.096, 1.208] | **FAIL** |
| P4 | 19.0 | 4.37 | 6.35·10⁶ | 1.069 [1.049, 1.089] | **FAIL** | 1.121 [1.071, 1.172] | **FAIL** |
| P5 | 21.0 | 4.83 | 7.02·10⁶ | 1.057 [1.037, 1.078] | **FAIL** | 1.102 [1.057, 1.147] | **FAIL** |
| P6 | 22.3 | 5.13 | 7.45·10⁶ | 1.045 [1.024, 1.068] | **FAIL** | 1.082 [1.040, 1.126] | **FAIL** |
| H1 | 24.48 | 5.63 | 10⁴ | 1.07 [0.69, ∞] | NOT RESOLVABLE (pre-data) | 1.15 [0.71, ∞] | NOT RESOLVABLE (pre-data) |
| H2 | 44.58 | 10.26 | 10⁴ | ∞ [0.49, ∞] | NOT RESOLVABLE (pre-data) | ∞ [0.53, ∞] | NOT RESOLVABLE (pre-data) |
| H3 | 46.83 | 10.78 | 10⁴ | 0.60 [0.37, ∞] | NOT RESOLVABLE (pre-data) | 0.62 [0.38, ∞] | NOT RESOLVABLE (pre-data) |

¹ **Bin A's PRIMARY is the least informative entry by construction:** at N_eff ≈ 2.3 the truncation allowance (0.160,
A3 = max) is as large as the effect the primary is meant to measure; its achieved widened half-width (0.215) exceeds
the ±20% limit, so A6(iii) flags it NOT RESOLVABLE (achieved) — the first time that guard fired on data (it had been
made to fire on a synthetic witness in the dry run). **The SECONDARY is the sharp test** (statistical CI only, no
allowance).

- **Power arm (N = ∞ excluded):** yes in A–P6 for both arms; no in H1–H3 (as sealed).
- **Resolution:** PRIMARY h_bin arm INAPPLICABLE (A7); PRIMARY ±20% floor arm (widened interval inside 1 ± 0.20): met
  in P4–P6, not in A–P3. SECONDARY ±20% floor arm: met in B–P6, not in A. SECONDARY h_bin arm: not pinned in any bin
  (κ̂ is not within h_bin of 1 anywhere).
- **SECONDARY: FAIL in all 8 resolvable bins** (κ̂ − 1 = 2.1–9.2 half-widths). **PRIMARY: FAIL in all 7 of B–P6
  even with the allowance** (1.9–2.8 widened half-widths).

## 2. Red paths (all behaved)
- RP-misprint (log(E/2πe) unfolding): fails as required in all 11 bins (mean-spacing arm everywhere; κ̂ arms in A–P6,
  except A's PRIMARY arm INAPPLICABLE (achieved)).
- RP-mix (BBLM's α in place of ᾱ): DISTINGUISHED in A, B, P1 (required, power 0.84–0.94); descriptive elsewhere.
- RP-shuffle (i.i.d. resampling): κ̂ unchanged in B–P6; INAPPLICABLE where the PRIMARY is unresolved.
- RP-Λ: INAPPLICABLE (unreachable, declared). Mean spacing within its band in every bin (|mean − 1| ≤ 2·10⁻⁷ in the
  P bins).

## 3. What the verdicts say, and what they do not
**Direction:** κ̂ > 1 in every resolvable bin, both arms — the zeros' spacing distribution sits **closer to the sine
kernel than CUE(N_eff) predicts**: the fitted finite-size correction is 68% (A) → 92% (P6) of the predicted one
(SECONDARY c = 1/κ̂²). The excess shrinks monotonically with height.

The test asks whether the one-parameter O(N⁻²) family (BBLM's "N_eff alone", or BFM's ᾱ-rescaled form) describes the
ζ nearest-neighbour law at 0.5–1% precision for 10⁵ ≲ E ≲ 3·10¹⁰. **It does not.** This is not, by itself, a
statement that N_eff is the wrong scale: BBLM derive the match only for the two-point function at O(ρ̄⁻²); that the
spacing law follows is their extra conjecture, and at these heights N_eff⁻² is 4–19%, so terms beyond the leading
correction are not small. The pre-read already showed CUE's own O(N⁻⁴) term moving κ* by −2% to −16% here (G0c); the
zeros move it the other way and further, and the SECONDARY (which carries the arithmetic ᾱ term) does not absorb it.

## 4. Descriptive observations (post-hoc; not scored, not validated)
- **Scaling.** (κ̂ − 1)·N_eff² is nearly constant over all 8 resolvable bins: SECONDARY 1.14–1.33, PRIMARY 2.16–2.37,
  across heights 10⁵–3·10¹⁰. A κ-shift ∝ N_eff⁻² is what a fixed-coefficient O(N_eff⁻⁴) term in p(s), absent from both
  families, would produce. The between-bin spread is within each bin's resolution (e.g. ±0.13 at P1, ±0.6 at P6 on this
  scale), so this is not finer-than-resolution agreement — but it is a pattern noticed after the data, and it needs its
  own pre-registered model before it can be a finding.
- **Window dependence.** SECONDARY: κ̂ rises with the window in A–P5 (P1: 1.113 / 1.133 / 1.152 at s ≤ 1.8 / 2.0 /
  2.2); in P6, 1.8 and 2.0 agree (1.046 / 1.045) and 2.2 is higher (1.053). PRIMARY: the 2.2 window gives the highest κ̂
  in all 8 bins, but 1.8 sits slightly above 2.0 in all 8 — not monotone. If the zeros differed from the family only in
  N, κ̂ would not depend on the window; it does, most at the 2.2 edge, which suggests the difference is partly in the
  **shape** of p(s) near s ≈ 2. These are fits to the same data, and the significance of the differences has not been
  assessed (it needs a bootstrap of the difference), so this is a lead, not a finding.
- **A with the sum allowance (A3, descriptive):** NOT RESOLVABLE (as for B); P1–P6 still FAIL under the sum.
- **H bins** (10⁴ zeros each): point estimates are uninformative (κ̂ 0.6–∞); the 24.5–44.6 gap in log(E/2π) has no
  public data. The heights where BBLM/BFM report visual agreement (10¹⁵, 10²²–10²³) are outside every resolvable bin.

## 5. Open (Will's call)
1. A pre-registered next-order model for the descriptive scaling — e.g. p₀ + p₁N⁻² + p₂N⁻⁴ with p₂ from the
   Bogomolny–Keating arithmetic terms (the programme's "new part": singular-series terms for the residual) — tested on
   these same sealed bins as a new phase, not as an amendment to this one.
2. Whether to report the low-height (N_eff < 2) region descriptively (seal §3 allows it; not run).
3. Platt files at higher heights (up to log(E/2π) ≈ 24.5) would extend the resolvable range toward N_eff ≈ 5.6.

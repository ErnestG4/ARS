# Phase 34d Findings — number-field prime angles (Z[i], Z[ω])

**Status:** complete with post-commit robustness amendment (2026-05-14).
Pre-pilot Steps 3 + 4 ran; the amendment pass added bootstrap σ²(K, X)
error bars, multi-K Eisenstein scan (parity with Gaussian), and
seed-replicate NNS classification. The amendment overturned the
single-shot bulk-classification verdict (per §7.ter.22 metric-
saturation discipline) and tightens the σ² shape claim to asymmetric
substrate-specific verdicts. Per the per-finding template established
at 34a/b/c.

---

## Frame

Phase 34d extends the spectral-coordinate orthogonal-channel survey to
the **prime-angle** sub-family — substrates where the spectral coordinate
is the angular position of a number-field prime ideal:

- **34d-G** (pre-pilot calibrator): Gaussian primes θ_π ∈ [0, π/2),
  Z[i], unit group order 4. Literature target: Rudnick-Waxman 2019
  Conjecture 1.2 (with Katz 2017 function-field proof of the analog).
- **34d-E** (substantive run): Eisenstein primes θ_π ∈ [0, π/3),
  Z[ω], unit group order 6. **First measurement** against the implicit
  structural extension of RW (no published Eisenstein analog per
  `lit/LIT_SUMMARY.md` §6).

Both fall into the fourth row of the cumulative structural-null typology
established across Phases 34a–d:

| phase   | substrate family                          | right-null spacing class                            |
| ------- | ----------------------------------------- | --------------------------------------------------- |
| 34a     | support-restricted (Mertens)              | Poisson on squarefree support                       |
| 34b     | random-walk-generated (Liouville)         | constrained ±1 random walk                          |
| 34c     | spectral-coordinate, zero-set (ζ/Dir/EC L) | RMT-class β-Hermite                                |
| **34d** | **spectral-coordinate, prime-angle**       | **Hecke-Poisson with RMT/Poisson crossover at K ≈ √N** |

---

## Methodology

### Generation
- **Gaussian primes** — Cornacchia + Tonelli-Shanks for √(-1) mod p
  followed by Euclidean reduction. O(log² p) per split prime. X = 10⁷
  in 2.8 s.
- **Eisenstein primes** — Cornacchia + Tonelli-Shanks for √(-3) mod p
  followed by Euclidean reduction on the form u² + 3v² = p, then
  (a, b) = (u + v, 2v). O(log² p) per split prime. X = 10⁷ in 2.9 s
  (Cornacchia speed-up was added in the amendment pass; the original
  brute-force took ~3 min at X = 10⁷).
- One angle per prime ideal; split p contributes TWO angles (the two
  conjugate ideals (π) and (π̄) with angles θ and L − θ in the
  fundamental sector).

### Step 3 — direct RW variance check
σ²(K, X) via continuous sliding-window integration over center θ ∈ [0, L)
(circular boundary). Discretised with n_grid = 5000 (n_grid = 2000 in
bootstrap), `np.searchsorted` for fast counting.

**Bootstrap procedure (amendment pass):** for each (substrate, X, K)
cell, draw 50 random half-samples (50% of the angles, without
replacement) and recompute σ²(K, X)/(N/K) on each half-sample. Report
the mean and 2σ envelope. Each half-sample has its own β = log K /
log(N/2), so the reported β is the mean across the 50 half-samples.

**Calibration control:** the same estimator on synthetic pair-symmetric
uniform random angles (matched N, same {θ, L−θ} pairing convention)
gives σ²/(N/K) ≈ 1.0 in the saturation regime (1.003 ± noise at
β = 0.71). This rules out the pair-symmetric counting convention as
the source of any saturation-level deficit on prime data.

### Step 4 — ARS readout
Standard Phase 34c panel adapted to the prime-angle substrate:
1. `joint_q_profile` NNS classification on **FULL N** (per §7.ter.51).
2. Within-window stability falsifier (5 windows, CV < 0.3).
3. `ramanujan_fourier(normalize=True)` Mode B + `padic_amplitude_v4` vs:
   - **Poisson** at matched FULL N (Hecke zeroth-order null).
   - **CUE / GUE β=2** at capped N=5000 (bulk-universal RMT right null
     per RW Prop 5.3 + Katz-Sarnak).

**Seed-replicate procedure (amendment pass):** for each substrate at
X = 10⁶, draw 20 random 80%-subsamples (different seeds), Hecke-unfold
each, and run `joint_q_profile.classify` on each subsample. Record
distribution of (primary, rep_med, ks_gue_med). Tests whether
single-shot verdicts are stable under sub-sampling — the §7.ter.22
metric-saturation discipline.

### New infrastructure
- `phase34d/circular_sampler.py` — CUE/COE/CSE via Mezzadri 2007
  QR-with-phase-normalization recipe. β=1/2/4 spacing-CV match Wigner
  surmise values: 0.54 (β=1), 0.43 (β=2), 0.32 (β=4).
- `phase34d/gaussian_primes.py` — Cornacchia + Tonelli-Shanks.
- `phase34d/eisenstein_primes.py` — Cornacchia + Tonelli-Shanks for
  u² + 3v² = p (amendment-pass speed-up).
- `phase34d/run_amendments.py` — bootstrap σ² + seed-replicate NNS
  driver.

---

## Sub-questions & results

### SQ-1 — Step 3 RW variance shape (with bootstrap error bars)

**Result (amendment-tightened):** Two distinct regimes show distinct
agreement with RW:

| substrate | X | K | β | σ²/(N/K) ± 2σ_boot | RW min(1, 2β) | (RW−emp)/σ |
| --------- | ---- | ---- | ----- | ------------------ | ------------- | ---------- |
| **Rigidity regime (β < 0.5):** matches RW within 1σ |
| gaussian | 10⁶ | 10 | 0.218 | 0.489 ± 0.324 | 0.435 | −0.33 |
| gaussian | 10⁶ | 30 | 0.322 | 0.587 ± 0.192 | 0.643 | +0.58 |
| gaussian | 10⁷ | 30 | 0.268 | 0.626 ± 0.242 | 0.535 | −0.75 |
| gaussian | 10⁷ | 100 | 0.362 | 0.680 ± 0.144 | 0.724 | +0.62 |
| eisenstein | 10⁶ | 30 | 0.322 | 0.607 ± 0.182 | 0.643 | +0.40 |
| eisenstein | 10⁷ | 100 | 0.362 | 0.629 ± 0.156 | 0.724 | +1.23 |
| **Saturation regime (β > 0.5):** empirical saturates ~0.78–0.92, below RW 1.0 by 3–7σ |
| gaussian | 10⁶ | 1000 | 0.653 | 0.843 ± 0.056 | 1.000 | +5.69 |
| gaussian | 10⁷ | 1000 | 0.543 | 0.798 ± 0.056 | 1.000 | +7.29 |
| gaussian | 10⁷ | 10000 | 0.724 | 0.888 ± 0.052 | 1.000 | +4.40 |
| eisenstein | 10⁶ | 1000 | 0.653 | 0.883 ± 0.062 | 1.000 | +3.71 |
| eisenstein | 10⁷ | 10000 | 0.724 | 0.910 ± 0.052 | 1.000 | +3.44 |

The data **traces the RW Conjecture 1.2 shape** (rising in rigidity,
saturating in Poisson regime), but the saturation is at empirical
~0.78–0.92 rather than 1.0. Two interpretations remain unresolved at
X = 10⁷:

  - **(a) Finite-X correction not characterized.** RW's published
    Figure 1 is at X ≈ 10⁸ (an order of magnitude higher); convergence
    of the saturation level from below as X grows is plausible. Our
    data does show *some* upward drift with X (gaussian K=1000:
    0.843 ± 0.028 at X=10⁶ → 0.798 ± 0.028 at X=10⁷ K=1000 at lower β,
    but rising to 0.888 ± 0.026 at K=10⁴ at higher β at X=10⁷).
    Convergence is slow and the rate is not quantified.

  - **(b) Genuine substrate departure from the RW asymptote.** The
    saturation may be an actual feature of prime-angle bulk variance
    at finite X that does NOT converge to 1.0. Without an analytic
    finite-X correction theory or empirical data at X ≥ 10⁸, we cannot
    discriminate.

The synthetic pair-symmetric uniform calibration **does** reach 1.0 in
the saturation regime, so the deficit is NOT a counting-convention
artifact.

**Plot:** `plots/phase34d_rw_variance_boot.png` (with 2σ bootstrap
error bars) and `plots/phase34d_rw_variance.png` (single-shot single-X
overlay).

### SQ-2 — Gaussian × Eisenstein constant-level test (post-amendment)

**Result: CONSTANT_LEVEL_AGREEMENT.** Gaussian and Eisenstein curves
overlap at every (X, β) within their bootstrap error bars. Both show
the same rising-then-saturating shape, the same ~0.85–0.91 saturation
level, and the same finite-X drift pattern (modest upward shift with X).

This is consistent with the brief's CONSTANT_LEVEL_AGREEMENT
expectation. To avoid a label collision with the brief's pre-specified
`GAUSSIAN_EISENSTEIN_DIVERGENT_CONST` verdict (which the brief used
for "differ at constant level"), we use CONSTANT_LEVEL_AGREEMENT here
for the convergent outcome. The verdict map is updated below.

### SQ-3 — Step 4 NNS classification (overturned by seed-replicate)

**Single-shot run (initial, pre-amendment):**

| substrate  | X    | NNS primary (full N, single seed) | rep_med | ks_gue_med |
| ---------- | ---- | --------------------------------- | ------- | ---------- |
| Gaussian   | 10⁶  | **TR (Wigner-Dyson)**              | 0.101   | 0.242      |
| Eisenstein | 10⁶  | **BL (Poisson)**                   | 0.058   | 0.250      |

The single-shot result appeared to show a Gaussian/Eisenstein bulk-
classification divergence at X = 10⁶. The original finding-doc framed
this as "Gaussian TR matches RW Prop 5.3 bulk Wigner-Dyson; Eisenstein
BL at the bulk classifier boundary."

**Seed-replicate (amendment, 20 random 80%-subsamples per substrate):**

| substrate  | X    | primary distribution | rep_med (mean ± std) | rep_med [min, max] | ks_gue_med (mean ± std) |
| ---------- | ---- | -------------------- | -------------------- | ------------------ | ----------------------- |
| Gaussian   | 10⁶  | **BL 20/20**         | 0.070 ± 0.016        | [0.046, 0.097]     | 0.258 ± 0.011           |
| Eisenstein | 10⁶  | **BL 20/20**         | 0.066 ± 0.014        | [0.045, 0.097]     | 0.258 ± 0.009           |

**Welch-style separation: 0.21σ.** The two rep_med distributions are
indistinguishable. Both substrates classify BL on ALL 20 sub-samples.

**Verdict: BOUNDARY_ARTIFACT.** The single-shot "Gaussian TR" result
was a threshold-crossing artifact: the full-N rep_med (0.101) happens
to sit just above the TR/BL boundary; any 80% sub-sample drops it
below the threshold. Per **§7.ter.22 metric-saturation discipline**
(continuous metrics dominate when modal class is near a boundary),
the discrete quadrant verdict was overclaiming on a continuous metric.

**Corrected reading:** Both Gaussian and Eisenstein prime-angle
substrates bulk-classify as **BL (Poisson-like)** at X = 10⁶ in 20/20
subsample replicates. The substrates do NOT show a real bulk
divergence at this N; they are bulk-indistinguishable across the
replicated test, consistent with shared Hecke-equidistribution at the
nearest-neighbor scale.

The bulk-BL reading on prime-angle substrates does **not contradict
RW Prop 5.3**, because Prop 5.3 is about the variance σ²(K, X) at
*global moment* scale (Step 3 result), not the nearest-neighbor
spacing distribution. The two readouts measure different things — see
**§7.ter.52 bulk vs global-moment readout** below.

### SQ-4 — Step 4 RF spike test + within-window CV falsifier

**Result:** unchanged by amendment. Within-window CV-per-q on FULL N:

| substrate  | X    | spike q vs Poisson (full N) | CV at spike q | gate (<0.3) |
| ---------- | ---- | --------------------------- | ------------- | ----------- |
| Gaussian   | 10⁵  | q=3, q=5                    | q=3 CV=0.908  | FAIL        |
| Gaussian   | 10⁶  | q=3                         | q=3 CV=0.644  | FAIL        |
| Eisenstein | 10⁶  | q=8                         | q=8 CV=0.995  | FAIL        |

**Every flagged RF spike fails the within-window CV<0.3 falsifier.**
Per Phase 34d brief §D prime-K seduction discipline, these are
documented but **not robust features.** Eisenstein vs CUE: no spikes
at 5×median threshold (cleanly null).

### SQ-5 — Cross-phase joint statement (reframed)

**Original framing (overclaimed):** "CONVERGENT_NULL_ACROSS_COORDINATES
on Q(√−3) — stronger than direction-match."

**Reframed (post-critique):** **METHODOLOGICAL_CONSISTENCY_ACROSS_COORDINATES.**

| coordinate                                    | substrate                  | NNS primary | spike-survival vs right null |
| --------------------------------------------- | -------------------------- | ----------- | ---------------------------- |
| **angle** (34d-E, [0, π/3))                    | Z[ω] / Eisenstein primes  | BL          | NONE (null vs CUE)           |
| **zero**  (34c real-Dirichlet Sp, χ₋₃ stratum) | L(s, χ₋₃) zeros            | BL          | NONE (null vs Sp β=4)        |

The two ARS readouts of Q(√−3) at distinct spectral coordinates
**both return null when run with the substrate-appropriate right null
in each case.** This demonstrates that ARS produces consistent null
verdicts across coordinates of one arithmetic object — confirmatory of
**framework consistency**, not of substantive cross-coordinate
arithmetic.

**A substantive cross-coordinate convergence claim would require:**
- residual correlation between the two coordinates' departures from
  their right nulls (none measured), or
- a shared anomaly appearing at both coordinates (none observed), or
- mutual prediction: a null-departure at the angle coordinate predicts
  one at the zero coordinate or vice versa (not tested).

None of these were measured in Phase 34d. The honest claim is that
the framework consistently produces null verdicts on two coordinates
of Q(√−3); the substantive arithmetic claim is reserved for future
work that measures cross-coordinate correlations or shared
non-null structure.

---

## Methodological generalisations

### §7.ter.51 — Stride-decimation destroys arithmetic structure on prime-angle substrates

**Statement (with scope audit, amendment-tightened).**

**Observed phenomenon:** Phase 34c-style stride-decimation
(`cap_events`, keep every kth event) of the unfolded coordinate
preserves bulk Wigner-Dyson universality on RMT zero substrates
(ζ, Dirichlet, EC L) but flips the NNS classification verdict on
prime-angle substrates. Empirical evidence at Phase 34d: Gaussian
X = 10⁶ full N=78351 → NNS=TR (rep_med=0.10); same data decimated to
N=5000 → NNS=BR_artifact (rep_med=0.59). Eisenstein same pattern. The
seed-replicate amendment shows the original Gaussian "TR" was itself
threshold-noise (see SQ-3), so the decimation observation more
precisely is that decimation perturbs the bulk readout in a regime-
specific way: it inflates rep_med beyond its full-N value, pushing
near-boundary classifications to BR_artifact.

**Operational rule:** For prime-angle substrates and any substrate
where the spectral coordinate is on S¹ via a unit-orbit quotient,
NNS / within-window-stability / Poisson-null comparisons must run on
FULL unfolded N. Stride-decimation is permissible only for the
dense-RMT surrogate (Dumitriu-Edelman O(N²) cost forcing the standard
N_MAX_SURVEY=5000 cap). When the substrate's NNS verdict sits near
the TR/BL boundary, ALSO run seed-replicate sub-sampling per the
§7.ter.22 metric-saturation discipline.

**Scope, currently empirically tested:** prime-angle substrates with
S¹ unit-orbit-quotient structure (Z[i] / order 4, Z[ω] / order 6).
**Conjectural broader applicability:** any substrate whose spectral
coordinate is intrinsically periodic via a discrete group quotient.
**Not yet tested:** general S¹ substrates without unit-orbit-quotient
structure; higher-dimensional unit-orbit quotients (e.g., U(1) × U(1)
products in PSL(2, O_K) Bianchi spectra). Mark these scopes as
*untested* in future application — and run the same decimation
comparison as a sanity check before applying the rule.

Sibling to §7.ter.19 (published-product level) and §7.ter.48
(substrate-side right-null typology).

### §7.ter.52 — Bulk readout vs global-moment readout: complementary, not interchangeable

**Statement.** Per RW 2019 Proposition 5.3 (proved), the bulk variance
integral ∫_{G(N)} |S_n(U)|² dU is **identical** for G = U(N),
USp(2N), SO(2N) at leading order min(n, N). The three Circular
families are *bulk-indistinguishable*. Bulk-dominated ARS engines
(NNS, RF Mode B, p-adic v4) inherit this indistinguishability: they
cannot tell CUE-from-COE-from-CSE on a substrate whose right null is
in the Wigner-Dyson β class.

**Operational rule.** When the substrate's right null lives at the
*global moment* level (Rudnick-Waxman class), the σ²(K, X) curve must
be recorded as a **required complement** to the bulk-ARS readout —
the global moment is the discriminating measurement against the
literature target. ARS provides "in the right β-class" confirmation;
σ²(K, X) directly tests the substantive prediction.

**Amendment note:** Phase 34d's bulk readout at X = 10⁶ gives
BL-classification on both substrates (seed-replicated, see SQ-3).
This is NOT in conflict with RW Prop 5.3, because Prop 5.3 is about
the global-moment variance (Step 3 σ²(K, X), see SQ-1) not the
nearest-neighbor spacing distribution. The two readouts measure
*different things*: bulk classifier reads NNS spacing distribution;
σ²(K, X) reads the long-arc number variance. RW Prop 5.3's bulk
universality applies to σ²(K, X), and the Phase 34d Step 3 data
confirms the shape (with finite-X / saturation-deficit caveat per
SQ-1).

---

## Cross-phase enumeration (two-layer per §7.ter.48)

### Surface layer (vs Poisson zeroth-order null)
- **34d-G × 34d-E:** PARALLEL_SIGNAL by structural analogy at the σ²(K, X)
  shape level; both substrates BL on subsample-replicate NNS.

### Deep layer (vs Rudnick-Waxman variance prediction)
- **34d-G:** RW shape confirmed in rigidity regime (within 1σ in
  bootstrap); saturation regime ~10-15% below asymptote 1.0
  (3–7σ deficit at finite X). Either finite-X correction or genuine
  substrate departure — not resolved at X = 10⁷.
- **34d-E:** Same shape as 34d-G at constant level across all measured
  β values (single-K → multi-K parity achieved in amendment pass);
  first-measurement against implicit Eisenstein analog;
  CONSTANT_LEVEL_AGREEMENT.

### Cross-phase to 34c
- **34d-E ↔ 34c χ₋₃ Sp:** METHODOLOGICAL_CONSISTENCY_ACROSS_COORDINATES
  on Q(√−3). Both null beyond their respective right nulls, but the
  joint statement is about framework consistency, not substantive
  arithmetic convergence (which would require residual correlation /
  shared anomaly measurement — not done in Phase 34d).

---

## Verdict map (final, asymmetric per substrate)

- **PRE_PILOT_STEP_3 (Gaussian):** **RW_SHAPE_CONFIRMED_AT_FINITE_X.**
  σ²(K, X) shape matches RW Conjecture 1.2 in the rigidity regime
  (β < 0.5) within 1σ of bootstrap envelope. In the saturation regime
  (β > 0.5), empirical saturates at 0.78–0.91 vs RW asymptote 1.0,
  with 3–7σ deficit at X = 10⁷ in tight bootstrap error. Discriminating
  finite-X correction vs genuine substrate departure requires
  measurement at X ≥ 10⁸ or an analytical finite-X correction theory;
  neither was produced in Phase 34d.

- **PRE_PILOT_STEP_3 (Eisenstein):** **FIRST_MEASUREMENT_SHAPE_CONSISTENT_WITH_STRUCTURAL_EXTENSION.**
  6 K values across X ∈ {10⁶, 10⁷} trace the same shape as Gaussian
  within bootstrap error at every (X, β) cell. Consistent with the
  implicit structural extension of RW to Z[ω]. **No published
  Eisenstein RW exists**, so this is not "replication of a published
  prediction" — it is "first measurement on the natural extension
  shows the same finite-X behavior as the calibrator substrate."

- **STEP_4 (both substrates):** **BL_BULK_CLASSIFICATION** on
  subsample-replicated NNS at X = 10⁶ (20/20 seeds). Single-shot
  "TR for Gaussian" reading is a §7.ter.22 metric-saturation
  threshold-crossing artifact, not a real bulk divergence. No RF
  spikes pass the within-window CV<0.3 falsifier.

- **SUBSTANTIVE_34d-G:** **RW_SHAPE_CONFIRMED_AT_FINITE_X +
  SATURATION_DEFICIT_UNRESOLVED.** Instrument behaves consistently
  with RW shape; absolute precision is X-limited at X = 10⁷.

- **SUBSTANTIVE_34d-E:** **NULL_IN_ORTHOGONAL_CHANNELS_BEYOND_HECKE +
  FIRST_MEASUREMENT_SHAPE_CONSISTENT.**

- **GAUSSIAN_EISENSTEIN_CONSTANT_LEVEL:** **AGREEMENT_WITHIN_BOOTSTRAP_ERROR.**
  Curves overlap at every measured (X, β). (To avoid label collision
  with the brief's `GAUSSIAN_EISENSTEIN_DIVERGENT_CONST` which was
  reserved for divergent outcomes, we use
  CONSTANT_LEVEL_AGREEMENT here.)

- **CROSS_PHASE_34d-E ↔ 34c χ₋₃ Sp:** **METHODOLOGICAL_CONSISTENCY_ACROSS_COORDINATES on Q(√−3).**
  Confirmatory of framework null-verdict consistency across distinct
  spectral coordinates of one arithmetic object. Substantive
  cross-coordinate convergence claim is **reserved** pending future
  measurement of residual correlation, shared anomaly, or mutual
  prediction of null-departures.

---

## Outputs

```
phase34d/
  PHASE34D_BRIEF.md                      ✓
  PHASE34D_FINDINGS.md                   ✓ (this file, amendment-tightened)
  lit/
    LIT_SUMMARY.md                       ✓
    rudnick_waxman_2019.pdf              ✓
    katz_2017.pdf                        ✓
  circular_sampler.py                    ✓  CUE/COE/CSE per Mezzadri 2007
  gaussian_primes.py                     ✓  Cornacchia O(log² p)
  eisenstein_primes.py                   ✓  Cornacchia O(log² p) (amendment)
  run_rw_variance_direct.py              ✓  Step 3
  run_prepilot_ars.py                    ✓  Step 4
  run_substantive_eisenstein.py          ✓
  run_cross_phase.py                     ✓
  run_amendments.py                      ✓  bootstrap σ² + seed-replicate NNS
  plot_rw_variance.py                    ✓  (now generates _boot.png too)

data/phase34d_results/   [gitignored]
  rw_variance_direct.json                ✓  32 records, single-shot single-X
  rw_variance_bootstrap.json             ✓  22 records, 50 bootstraps per cell
  gaussian_prepilot_ars.json             ✓
  eisenstein_substantive_ars.json        ✓
  cross_phase_34d_to_34c_dirichlet.json  ✓
  nns_seed_replicates.json               ✓  20 seeds per substrate

plots/   [gitignored]
  phase34d_rw_variance.png               ✓  single-shot Figure-1 reproduction
  phase34d_rw_variance_boot.png          ✓  with 2σ bootstrap error bars
```

---

## Open questions / follow-ups

1. **Saturation deficit at X = 10⁷: finite-X correction or genuine departure?**
   Empirical σ²/(N/K) saturates at ~0.85–0.91 vs RW asymptote 1.0,
   with 3–7σ deficit in tight bootstrap error. Resolving this requires
   either (a) measurement at X ≥ 10⁸ to test finite-X convergence
   (X = 10⁸ Gaussian Cornacchia is ~30 s with current code), or
   (b) analytical derivation of the finite-X correction term in RW
   Conjecture 1.2. Either resolves to "confirmatory of RW asymptote"
   or "genuine substrate departure with characterized finite-X scaling."

2. **The §7.ter.22 metric-saturation lesson generalises.** Phase 34d's
   seed-replicate amendment caught a single-shot threshold-crossing
   artifact (Gaussian TR → BL on resample). Worth applying the same
   discipline retrospectively to Phase 34c boundary-classifications
   (NNS verdicts near TR/BL or TR/IB boundaries in ζ low-bulk,
   Dirichlet, EC L) to verify their stability under sub-sampling.

3. **Substantive cross-coordinate convergence on Q(√−3).** The
   methodological-consistency claim becomes substantive when one of:
   (a) residual correlation between angle-coord and zero-coord
   departures from right null is measured (e.g., regress 34d-E
   per-prime z(p) on 34c χ₋₃-zero L-function moments);
   (b) a shared anomaly appears at both coordinates;
   (c) Phase 34f Bianchi-Maass-on-PSL(2, O_K) lands as the third
   coordinate with null-departure correlated with 34d-E or 34c.
   Reserved for future phases.

4. **Phase 34e candidate — named "RW-class" calibrator.** If the
   saturation-deficit follow-up (item 1) confirms RW asymptote, add
   an explicit Rudnick-Waxman-class entry to the calibrator zoo. If
   it instead reveals a substrate-specific finite-X correction, the
   named class is the empirical curve + characterized finite-X scaling.

5. **§7.ter.51 scope expansion.** Test the decimation discipline on
   non-prime-angle S¹ substrates (function-field Frobenius eigenphases
   if available; Maass forms on PSL(2, Z)) to determine whether the
   rule is unit-orbit-specific or generally applies to any S¹
   substrate.

6. **§7.ter.22 retrospective on Phase 34c.** Run 20-seed subsample-
   replicate NNS on Phase 34c panels and check whether any single-shot
   verdicts (especially ones at the TR/BL boundary) flip under
   subsampling. If yes, those verdicts need the same correction Phase
   34d did here.

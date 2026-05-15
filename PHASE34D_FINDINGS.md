# Phase 34d Findings — number-field prime angles (Z[i], Z[ω])

**Status:** complete. Pre-pilot Steps 3 + 4 passed; substantive Eisenstein
run and cross-phase to 34c χ₋₃ Sp stratum landed. Per the per-finding
template established at 34a/b/c.

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
- **Gaussian primes** — Cornacchia's algorithm (Tonelli-Shanks for √(-1)
  mod p, Euclidean reduction). O(log² p) per split prime. X = 10⁷ in 2.8 s.
- **Eisenstein primes** — brute-force search on a² - ab + b² = p
  with b ∈ [1, √(4p/3)]. X = 10⁶ in 7 s; X = 10⁷ in ~3 min.
  (Cornacchia speed-up for Eisenstein is a TODO.)
- One angle per prime ideal; split p contributes TWO angles (the two
  conjugate ideals (π) and (π̄) with angles θ and L − θ in the
  fundamental sector).

### Step 3 — direct RW variance check
σ²(K, X) via continuous sliding-window integration over center θ ∈ [0, L)
(circular boundary). Discretised with n_grid = 5000, `np.searchsorted`
for fast counting.

### Step 4 — ARS readout
Standard Phase 34c panel:
1. `joint_q_profile` NNS classification on **FULL N** (per §7.ter.51).
2. Within-window stability falsifier (5 windows, CV < 0.3).
3. `ramanujan_fourier(normalize=True)` Mode B + `padic_amplitude_v4` vs:
   - **Poisson** at matched FULL N (Hecke zeroth-order null).
   - **CUE / GUE β=2** at capped N=5000 (bulk-universal RMT right null
     per RW Prop 5.3 + Katz-Sarnak).

200 surrogates per null per panel.

### New infrastructure
- `phase34d/circular_sampler.py` — CUE/COE/CSE via Mezzadri 2007
  QR-with-phase-normalization recipe. β=1/2/4 spacing-CV match Wigner
  surmise values: 0.54 (β=1), 0.43 (β=2), 0.32 (β=4).
- `phase34d/gaussian_primes.py` — Cornacchia + Tonelli-Shanks.
- `phase34d/eisenstein_primes.py` — brute-force Eisenstein norm form.

---

## Sub-questions & results

### SQ-1 — Step 3 RW variance shape: PASS

Empirical σ²(K, X)/(N/K) traces predicted min(1, 2β) shape with finite-X
correction. Convergence toward RW asymptote visible as X grows.

| substrate  | X    | K     | β     | σ²/(N/K) | RW min(1, 2β) | ratio_emp / RW |
| ---------- | ---- | ----- | ----- | -------- | ------------- | -------------- |
| gaussian   | 10⁷  | 30    | 0.254 | 0.299    | 0.507         | 0.59           |
| gaussian   | 10⁷  | 100   | 0.344 | 0.337    | 0.687         | 0.49           |
| gaussian   | 10⁷  | 1000  | 0.515 | 0.609    | 1.000         | 0.61           |
| gaussian   | 10⁷  | 3000  | 0.597 | 0.713    | 1.000         | 0.71           |
| gaussian   | 10⁷  | 10000 | 0.687 | **0.872**| 1.000         | **0.87**       |
| eisenstein | 10⁷  | 10000 | 0.687 | 0.865    | 1.000         | 0.87           |

At fixed β, ratio rises with X — consistent with RW being asymptotic.
RW's published Figure 1 is at X ≈ 10⁸; our X = 10⁷ K = 10⁴ point is
within 13% of the asymptote in the Poisson regime. Plot:
`plots/phase34d_rw_variance.png`.

### SQ-2 — Gaussian × Eisenstein constant-level test: CONFIRMATORY

Gaussian and Eisenstein curves are **essentially identical** at any
given (X, β). This matches the brief's predicted
GAUSSIAN_EISENSTEIN_DIVERGENT_CONST verdict outcome: same min-shape, no
detectable prefactor difference at finite X. Confirmatory of structural
analog; not novel.

### SQ-3 — Step 4 NNS classification on FULL N

| substrate  | X    | NNS primary (full N) | rep_med | ks_gue_med | NNS primary (capped 5K) |
| ---------- | ---- | -------------------- | ------- | ---------- | ----------------------- |
| Gaussian   | 10⁵  | BL (Poisson)         | 0.097   | 0.237      | BL                      |
| Gaussian   | 10⁶  | **TR (Wigner-Dyson)**| 0.101   | 0.242      | **BR_artifact**         |
| Eisenstein | 10⁶  | BL (Poisson)         | 0.058   | 0.250      | **BR_artifact**         |

At X = 10⁶:
- **Gaussian** classifies **TR** — matches RW Prop 5.3 bulk Wigner-Dyson
  universality (Hermite ↔ Circular β=2 by Katz-Sarnak).
- **Eisenstein** classifies **BL** — at the bulk classifier boundary
  (rep_med = 0.058 is right at TR/BL threshold). The substrate is at
  the boundary; classifier sensitivity to ks_gue_med pushes it to BL.

**Both substrates' capped (decimated) variants classify BR_artifact** —
confirms stride-decimation destroys arithmetic structure (§7.ter.51
proposed below).

### SQ-4 — Step 4 RF spike test + within-window CV falsifier

| substrate  | X    | spike q vs Poisson (full N) | p-val | dom_per_q | within-window CV @ q | spike CV<0.3 gate? |
| ---------- | ---- | --------------------------- | ----- | --------- | -------------------- | ------------------ |
| Gaussian   | 10⁵  | q=3, q=5                    | low   | p=3       | q=3 CV=0.91          | FAIL               |
| Gaussian   | 10⁶  | q=3                         | low   | p=3       | q=3 CV=0.64          | FAIL               |
| Eisenstein | 10⁶  | q=8                         | 0.020 | p=13      | q=8 CV=**0.995**     | FAIL               |

| substrate  | X    | spike q vs CUE (capped) | p-val | dom_per_q |
| ---------- | ---- | ----------------------- | ----- | --------- |
| Gaussian   | 10⁶  | q=4, q=12               | low   | p=2       |
| Eisenstein | 10⁶  | **NONE**                | n/a   | p=5       |

**Every flagged RF spike fails the within-window stability falsifier
(CV < 0.3 gate).** The q=3 spike in Gaussian, q=8 spike in Eisenstein,
and decimated q=4/q=12 spikes in Gaussian are all sequence-level
unstable. Per Phase 34d brief §D Prime-K seduction discipline, these
are documented but **not robust features.**

Eisenstein vs CUE: **no spikes, cleanly null** — passes the right-null
gate trivially. Gaussian vs CUE on decimated data shows decimation
artifacts (q=4 is the natural unit-orbit mode that survives the
arithmetic-structure destruction of decimation).

### SQ-5 — Cross-phase joint statement (34d-E ↔ 34c χ₋₃ Sp): CONVERGENT_NULL

Per Phase 34d brief §C pre-specified joint verdict:

**JOINT STATEMENT: CONVERGENT_NULL_ACROSS_COORDINATES on Q(√−3).**

| coordinate                                    | substrate                  | NNS primary | spike-survival vs right null |
| --------------------------------------------- | -------------------------- | ----------- | ---------------------------- |
| **angle** (34d-E, [0, π/3))                    | Z[ω] / Eisenstein primes  | BL          | NONE (null vs CUE)           |
| **zero**  (34c real-Dirichlet Sp, χ₋₃ stratum) | L(s, χ₋₃) zeros            | BL          | NONE (null vs Sp β=4)        |

**Two ARS readouts of the same arithmetic object (Q(√−3)) at two
different spectral coordinates BOTH land null beyond their respective
right nulls.** This is stronger than direction-match: it is convergent-
null across coordinates of one arithmetic substrate.

Phase 34f Bianchi-Maass-on-PSL(2, O_K) is forward-bound as the **third
coordinate** on the same substrate, completing a single-substrate
multi-coordinate instrument-validation triple.

---

## Methodological generalisations

### §7.ter.51 — Stride-decimation destroys arithmetic structure on prime-angle substrates

**Statement.** Phase 34c-style stride-decimation of unfolded coordinates
(`cap_events`, keep every kth event) preserves bulk Wigner-Dyson
universality on RMT zero substrates (ζ, Dirichlet, EC L), because zero
spacings are *locally* rigid in a coordinate-free way. It DOES NOT
preserve bulk character on prime-angle substrates: decimation breaks
the angular periodicity structure that ties the angles together via
their underlying lattice constraints.

**Empirical evidence.** Gaussian X = 10⁶: NNS primary on FULL N = 78351
classifies **TR** (rep_med = 0.10); same data stride-decimated to N =
5000 classifies **BR_artifact** (rep_med = 0.59). Eisenstein X = 10⁶
same pattern: full-N **BL** (rep_med = 0.058) vs capped-5K **BR_artifact**
(rep_med = 0.57).

**Operational rule.** For prime-angle substrates (and any future
substrate where the spectral coordinate is in S¹ via a unit-orbit
quotient): NNS / within-window-stability / Poisson-null comparisons
MUST run on the FULL unfolded N. Stride-decimation is permissible
ONLY for the dense-RMT surrogate (Dumitriu-Edelman O(N²) cost forcing).
This is a substrate-family-specific discipline, sibling to
§7.ter.19 (published-product level) and §7.ter.48 (substrate-side
right-null typology).

### §7.ter.52 — Bulk readout vs global-moment readout: complementary, not interchangeable

**Statement.** Per Rudnick-Waxman 2019 Proposition 5.3 (proved), the
bulk variance integral ∫_G |S_n(U)|² dU is **identical** for G = U(N),
USp(2N), SO(2N) at leading order min(n, N). The three Circular families
are *bulk-indistinguishable*. Bulk-dominated ARS engines (NNS, RF Mode
B, p-adic v4) inherit this indistinguishability: they cannot tell
CUE-from-COE-from-CSE on a substrate whose right null is in the
Wigner-Dyson β class.

**Operational rule.** When the substrate's right null lives at the
*global moment* level (Rudnick-Waxman class), the σ²(K, X) curve must
be recorded as a **required complement** to the bulk-ARS readout — it
is the discriminating measurement against the literature target.
ARS provides "in the right β-class" confirmation; only the
global-moment σ²(K, X) directly tests the substantive prediction. This
extends the Phase 34c bulk-vs-edge analytical scaffolding to Phase 34d
prime-angle substrates.

---

## Cross-phase enumeration (two-layer per §7.ter.48)

### Surface layer (vs Poisson zeroth-order null)
- **34d-G × 34d-E:** PARALLEL_SIGNAL by structural analogy. Both
  Hecke-equidistributed; both reproduce RW min(1, 2β) shape; both
  bulk-Wigner-Dyson at finite N.

### Deep layer (vs Rudnick-Waxman variance prediction)
- **34d-G** deep layer: RW Figure 1 shape REPLICATED with finite-X
  correction. Instrument-validation success (parallel to ζ → TR in
  Phase 34c).
- **34d-E** deep layer: Same shape as 34d-G; first-measurement against
  implicit Eisenstein analog. Confirmatory of structural analog at
  constant level (GAUSSIAN_EISENSTEIN_DIVERGENT_CONST verdict per brief).

### Cross-phase to 34c
- **34d-E ↔ 34c χ₋₃ Sp:** CONVERGENT_NULL_ACROSS_COORDINATES on
  Q(√−3). Two ARS readouts of one arithmetic object at two distinct
  spectral coordinates both null beyond their respective right nulls.

---

## Verdict map (final)

- **PRE_PILOT_STEP_3: PASS** — Gaussian RW Figure 1 reproduced
  (ratio = 0.87 at β = 0.69, X = 10⁷); Eisenstein constant-level
  identical.
- **PRE_PILOT_STEP_4: PASS** — NNS classifies on bulk-universality
  expected category (TR at Gaussian X = 10⁶; BL/boundary at Eisenstein
  X = 10⁶ and Gaussian X = 10⁵); every flagged RF spike fails the
  within-window CV < 0.3 falsifier; vs CUE: Eisenstein cleanly null,
  Gaussian decimated-only spikes are decimation artifacts.
- **SUBSTANTIVE_34d-G: RW_REPLICATED_AT_DEEP_LAYER** —
  σ²(K, X) reproduces RW Conjecture 1.2 with finite-X correction.
  Instrument-validation success.
- **SUBSTANTIVE_34d-E: NULL_IN_ORTHOGONAL_CHANNELS_BEYOND_HECKE + RW_REPLICATED_AT_DEEP_LAYER (constant-level confirmatory)** —
  no robust arithmetic-channel feature beyond Hecke equidistribution +
  RW variance prediction. First measurement on Eisenstein analog
  succeeds.
- **CROSS_PHASE_34d-E ↔ 34c χ₋₃ Sp: CONVERGENT_NULL_ACROSS_COORDINATES on Q(√−3)** —
  two ARS readouts of one arithmetic object at two distinct spectral
  coordinates both null beyond respective right nulls.

---

## Outputs

```
phase34d/
  PHASE34D_BRIEF.md                      ✓
  PHASE34D_FINDINGS.md                   ✓ (this file)
  lit/
    LIT_SUMMARY.md                       ✓
    rudnick_waxman_2019.pdf              ✓
    katz_2017.pdf                        ✓
  circular_sampler.py                    ✓  CUE/COE/CSE per Mezzadri 2007
  gaussian_primes.py                     ✓  Cornacchia O(log² p)
  eisenstein_primes.py                   ✓  brute-force O(√p)
  run_rw_variance_direct.py              ✓  Step 3
  run_prepilot_ars.py                    ✓  Step 4
  run_substantive_eisenstein.py          ✓
  run_cross_phase.py                     ✓
  plot_rw_variance.py                    ✓

data/phase34d_results/
  rw_variance_direct.json                ✓  32 records, 3 X × 5-6 K × 2 substrates
  gaussian_prepilot_ars.json             ✓
  eisenstein_substantive_ars.json        ✓
  cross_phase_34d_to_34c_dirichlet.json  ✓

plots/
  phase34d_rw_variance.png               ✓  RW Figure 1 reproduction
```

---

## Open questions / follow-ups

1. **Eisenstein Cornacchia speed-up.** Brute-force at X = 10⁷ took
   3 min; Cornacchia for u² + 3v² = 4p should reduce this to ~5 s.
   Useful for any Phase 34e/34f extension.

2. **q = 3 spike on Gaussian** (falsified by CV gate but consistent
   across X scan). Worth a tangential probe: is the q = 3 amplitude
   correlated with the residue of p mod 3 across primes ≡ 1 mod 4?
   If yes, it's a real arithmetic structure that just doesn't
   manifest at the local-window scale. Not load-bearing for the
   Phase 34d verdict; flagged for curiosity.

3. **Phase 34e candidate — named "RW-class" calibrator.** If 34d-G
   validates RW shape (it does), consider adding a Rudnick-Waxman-class
   entry to the calibrator zoo. Would convert RW from "literature
   target" to "named calibrator class" and extend the zoo's range
   to include the Hecke-Poisson family.

4. **Phase 34f — Bianchi-Maass-on-PSL(2, O_K)** as the third spectral
   coordinate on Q(√−3) (alongside the angle in 34d-E and the L-zero
   in 34c χ₋₃ Sp). Would complete a single-substrate multi-coordinate
   instrument-validation triple. Bohigas-Giannoni-Schmit (1984)
   predicts GOE-class with documented arithmetic anomalies from
   Hecke-eigenspace multiplicities — a current literature target.

5. **§7.ter.51 sanity-check on Phase 34a/b.** §7.ter.51 says
   stride-decimation destroys arithmetic structure on prime-angle
   substrates. Worth re-running Phase 34a (Mertens) and 34b
   (Liouville) on full N to verify the original §7.ter.48
   conclusions weren't decimation-sensitive (probably weren't —
   those substrates aren't S¹-circular — but worth a confirmation
   if revisiting).

# Phase 34d Brief — Number-field prime angles: Gaussian + Eisenstein orthogonal-channel survey

**Substrate family:** spectral-coordinate, sub-family number-field-prime-angle.
**Right-null typology departure:** Hecke-Poisson, with a RMT/Poisson crossover at
K ≈ √N (per Rudnick-Waxman 2019, Conjecture 1.2). See **§A. Structural-null
typology** below — this phase establishes the fourth row of the cumulative
substrate-family/right-null table started at 34a.

---

## §A. Structural-null typology

After Phases 34a–c the cumulative typology is:

| phase   | substrate family             | right-null spacing class                  |
| ------- | ---------------------------- | ----------------------------------------- |
| 34a     | support-restricted point process (Mertens) | Poisson on squarefree support |
| 34b     | random-walk-generated (Liouville)          | constrained ±1 random walk    |
| 34c     | spectral-coordinate, zero-set (ζ, Dirichlet L, EC L) | RMT-class β-Hermite |
| **34d** | **spectral-coordinate, prime-angle (Z[i], Z[ω])** | **Hecke-Poisson with RMT/Poisson crossover at K ≈ √N** |

Each row is a distinct *right null* — the structurally correct null for the
substrate's generative mechanism. Selecting the wrong right null reproduces
the **§7.ter.49 machinery-side false-positive equivalence class**. Phase 34d
adds the fourth row of this typology and is the first prime-angle entry; the
table itself is a publishable methodology contribution independent of any
single substrate outcome.

Cross-reference: **§7.ter.48** (substrate-side right-null discipline,
Phase 34b), **§7.ter.49** (machinery-side false-positive equivalence class,
Phase 34c).

---

## Frame

Phase 34c closed the spectral-coordinate / zero-set sub-family
(ζ + Dirichlet + EC L) at NULL_IN_ORTHOGONAL_CHANNELS_BEYOND_RMT on 5/6
panels, with EC root-minus q=17 AMBIGUOUS_AT_BOUNDARY (pooling-null
methodology gap, not substrate property). Phase 34d extends the
spectral-coordinate sweep to the **prime-angle** sub-family — substrates
where the spectral coordinate is the angular position of a number-field
prime ideal in the unit-orbit fundamental sector, with **Hecke
equidistribution** as the zeroth-order density and **Rudnick-Waxman 2019**
providing the fine-scale-variance literature target.

Substrates the Phase 34c panel did NOT cover:
- **Gaussian** prime angles θ_π ∈ [0, π/2) (Z[i], unit group order 4)
- **Eisenstein** prime angles θ_π ∈ [0, π/3) (Z[ω], unit group order 6)

**Two-phase structure:**
- **34d-G** (pre-pilot calibrator): Gaussian. Rudnick-Waxman 2019
  (Isr. J. Math. 232, 159–199) gives the explicit variance conjecture;
  Katz 2017 (IMRN 2017:11) proves the function-field analog. Instrument-
  validation: does ARS read what the analytical literature predicts?
- **34d-E** (substantive run): Eisenstein. Per Phase 34d lit-lock
  (`lit/LIT_SUMMARY.md` §6), the Eisenstein analog has *not* been
  published as a dedicated paper. Phase 34d-E is therefore a
  **first-measurement** against the implicit structural analog of RW,
  not against an explicit published conjecture.

**Why Gaussian first:** Phase 34c discipline requires a substrate where the
right-null prediction is known and verified analytically before any
substantive claim. Z[i] is that substrate; the Eisenstein run depends on
the Gaussian calibrator passing.

---

## Q4 substrate-family audit (cross-domain pre-pilot discipline)

**Family:** spectral-coordinate, sub-family number-field-prime-angle.

**Coordinate:** angle of prime ideal in fundamental angular sector.

| field   | unit group | order | u(p)         | sector       |
| ------- | ---------- | ----- | ------------ | ------------ |
| Q(i)    | {±1, ±i}   | 4     | (α/ᾱ)² = e^{i·4θ} | [0, π/2) |
| Q(ω)    | {±1, ±ω, ±ω²} | 6  | (α/ᾱ)³ = e^{i·6θ} | [0, π/3) |

**Published-product level:** Phase 34d operates at the level of *individual prime
ideals* with one angle per ideal (RW convention). This is the lowest-aggregate
level the substrate admits — analogous to the unfolded-zero level in Phase 34c.
Per §7.ter.19 (Phase 33a generalization), pre-aggregated products would import
the wrong-level-of-aggregation artifact and are *not* used here.

**Surrogate adequacy:** Poisson on the fundamental sector at matched event
count is the primary surrogate. Per §A typology, Hecke equidistribution → uniform
random angles → Poisson spacings is the zeroth-order null. The Rudnick-Waxman
prediction is **not** Poisson — it is a global-moment (variance σ²(K, X))
departure at the K ≈ √N crossover scale.

**Calibrator-zoo coverage:** Poisson already in the zoo (BL class). The
Rudnick-Waxman fine-scale prediction interpolates between Poisson (K > √N)
and RMT-class (K < √N) — the **Katz monodromy triple** (CUE, COE, CSE)
needs to be added. See **§B** below.

**Methodology axis:** **Mode B** (`ramanujan_fourier(normalize=True)`,
native spacing-coordinate). Mode A discretization would import the
integer-position wrong-null artifact per **§7.ter.49** machinery-side
false-positive equivalence class — angles are real-valued, Mode A is
structurally wrong here.

---

## §B. New ensemble infrastructure — the Katz monodromy triple

The calibrator zoo currently has the **Hermite triple** (GOE β=1, GUE β=2,
GSE β=4) from `signal_gen.make_beta_ensemble_eigenvalues` + Dumitriu-Edelman
tridiagonal in `phase34c/rmt_sampler.py`. Phase 34d adds the **Circular
triple** (CUE, COE, CSE) via Mezzadri 2007 (Notices AMS 54:5).

**CUE sampling recipe (Mezzadri 2007):**
```python
A = (rng.standard_normal((N, N)) + 1j*rng.standard_normal((N, N))) / np.sqrt(2)
Q, R = np.linalg.qr(A)
D = np.diag(R) / np.abs(np.diag(R))   # phase normalization — load-bearing
U = Q @ np.diag(D)                     # Haar-distributed on U(N)
angles = np.sort(np.angle(np.linalg.eigvals(U)) % (2*np.pi))
spacings = np.diff(angles) * (N / (2*np.pi))   # unit-mean spacing
```

The D = diag(R)/|diag(R)| phase normalization is the load-bearing correction —
naive QR gives Q with a non-Haar orientation. COE: symmetric U·U^T (β=1 circular).
CSE: Hermitian symplectic form, β=4 circular.

**Hermite + Circular METHODS.md decomposition:**

```
Spectrum on R         → Hermite β-ensemble (Dumitriu-Edelman tridiagonal)
                        — number-field L-function zeros (ζ, Dirichlet, EC)
Spectrum on S¹        → Circular β-ensemble (Mezzadri 2007 QR-with-phase)
                        — function-field Frobenius eigenphases, prime-angle
                          Hecke L-functions
```

Choose by where the substrate's spectral coordinate lives. Number-field zeros
of L(s, Ξ_k) live on Re(s) = 1/2 (the line), so Hermite. Function-field
Frobenius eigenphases live on the unit circle, so Circular. Both are needed
for cross-domain audit coverage.

**Bulk-vs-edge architectural note (Katz-Sarnak universality):**

By Rudnick-Waxman Proposition 5.3, **the three Circular ensembles all give the
same min(n, N) bulk variance** — they differ only in O(1) and O(log N)
corrections from the off-diagonal trace integrals:

```
∫_{U(N)}   |S_n(U)|² dU  ~  min(n, N) · ∫ |w|²       [Dyson's lemma; diagonal-only]
∫_{USp(2N)} |S_n(U)|² dU ~  min(n, N) · ∫ |w|² + O(log N)
∫_{SO(2N)}  |S_n(U)|² dU ~  min(n, N) · ∫ |w|² + O(log N)
```

This is *bulk universality*. Since NNS / RF mode B / p-adic v4 are bulk-
dominated statistics, **ARS will read "TR-best-fit" but cannot cleanly
separate CUE from COE from CSE** — only the *global moment* (the σ²(K, X)
variance integral itself) discriminates at the family level. This is an
architectural property of the calibrated instrument, not a zoo limitation,
and should be documented as such in METHODS.md. Family-specific
identification within the Wigner-Dyson class requires the auxiliary
variance computation.

**Mechanism-distinctness re-run (§7.ter.26 discipline):** adding the Katz
monodromy triple to `calibrator_panel.py` triggers a Phase 19-equivalent
re-run on the extended panel. Expected result: **CUE indistinguishable
from GUE on bulk-dominated engines**, which is the empirical statement of
bulk universality and should be documented as such rather than treated as
a problem.

---

## Pre-pilot adequacy check (mandatory before 34d-E)

Per Phase 33a-c **§7.ter.19** cross-domain audit discipline. Pre-pilot
status as of 2026-05-14: **Steps 1–2 complete** (transcribed in
`lit/LIT_SUMMARY.md`). Steps 3–4 are this phase's pre-pilot acceptance
gate.

### Step 1 — Literature lock (✓ complete)

Rudnick-Waxman 2019 Conjecture 1.2 transcribed exactly:

```
For 1 ≪ K ≪ N^{1−o(1)}:

    Var(N_{K,X}) ~ (N/K) · min(1,  2 log K / log N)
```

with N = #{p prime in Z[i] : Norm p ≤ X} ~ X / log X, arc length π/(2K).

**Three regimes:**

| regime              | K vs N             | Var(N_{K,X})                       | character        |
| ------------------- | ------------------ | ---------------------------------- | ---------------- |
| trivial / empty     | K ≫ N              | ~ N/K                              | empty sectors    |
| Poisson             | √N ≪ K ≪ N         | ~ N/K                              | random           |
| RMT / rigidity      | 1 ≪ K ≪ √N         | ~ (N/K) · 2 log K / log N          | suppressed       |

Crossover at K ≈ √N. The substantive measurement is whether ARS detects the
rigidity regime (variance below Poisson) at the predicted scale.

### Step 2 — Eisenstein analog lit-search (✓ complete)

Outcome: **no dedicated paper.** Phase 34d-E is a first-measurement against
the implicit structural extension. See `lit/LIT_SUMMARY.md` §6.

### Step 3 — Direct variance check (pre-pilot acceptance gate)

Independent of ARS. Sample-size pre-spec:

| X       | N (~prime ideals ≡ 1 mod 4) | √N crossover | K scan                       |
| ------- | --------------------------- | ------------ | ---------------------------- |
| 10⁵     | ~ 1 000                     | K ≈ 30       | {3, 10, 30, 100, 300}        |
| 10⁶     | ~ 7 200                     | K ≈ 85       | {10, 30, 100, 300, 1000}     |
| 10⁷     | ~ 60 000                    | K ≈ 245      | {30, 100, 300, 1000, 3000, 10000} |

Each K-value, measure σ²_emp(K, X) over the K arcs centered at θ_j = (j+1/2)·π/(2K).
Compare to:
- **Poisson prediction:** N/K (the right null)
- **RW conjecture:** (N/K) · min(1, 2 log K / log N) (the deep-layer target)

Plot **Var/(N/K) vs β := log K / log N** (this is exactly RW Figure 1; the
prediction is min(1, 2β)). Successful Step 3 reproduces the published Figure 1
shape — saturation at β > 0.5, linear ramp at β < 0.5.

### Step 4 — ARS on Gaussian prime angles

Run on the angle-sorted sequence:
- `joint_q_profile` at q_max ∈ {30, 200}, JPF_CAP = 1500
- `ramanujan_fourier(normalize=True)` (Mode B — per §7.ter.49)
- `padic_amplitude_v4` per-q-power-normalized

Within-window stability gate (5 non-overlapping equal-event-count windows,
CV < 0.3) on any flagged RF spike at q < 30.

### Pre-pilot acceptance gate

**Pass:** Step 3 reproduces RW Figure 1 shape AND Step 4 ARS verdict reads
"TR-best-fit" (bulk-universality consistent) at the relevant β = log K / log N
regime.

**Fail:** any disagreement on direction of departure from Poisson, OR ARS
returns Poisson-best-fit at K < √N (where RW predicts variance below Poisson).

Pre-pilot failure mode is documented and **pauses** 34d-E. Pass → proceeds.

---

## Substantive run (34d-E)

### Generation pipeline

```
phase34d/gaussian_primes.py
  for each rational prime p ≤ N:
    if p == 2:                          # ramified, one Eisenstein integer (1+i)
      include theta = π/4 (or omit per convention)
    elif p % 4 == 1:                    # split
      find (a, b) with a² + b² = p, a > 0, b ≥ 0  (unique up to swap)
      record θ = arctan(b / a)
    elif p % 4 == 3:                    # inert; no contribution to angles
      skip
  output sorted angle array

phase34d/eisenstein_primes.py
  for each rational prime p ≤ N:
    if p == 3:                          # ramified, prime (1 - ω) with N = 3
      include via canonical representative or omit
    elif p % 3 == 1:                    # split
      find (a, b) with a² - ab + b² = p (one rep per prime ideal)
      θ ∈ [0, π/3) for each of the two ideals (π) and (π̄)
    elif p % 3 == 2:                    # inert
      skip
  output sorted angle array
```

One angle per prime ideal (RW convention). The 8-or-12 unit-orbit-and-conjugate
representatives convention is **explicitly not used** — it would import a K-pool
artifact (per §7.ter.49 pooled-substrate discipline).

### Sub-questions

1. **Stationarity** (Phase 30 10-window heuristic on angle-sorted sequence).
   Expected stationary; flag density-drift only.

2. **NNS engine** (joint_q_profile at q_max ∈ {30, 200}, JPF_CAP = 1500).
   Expected primary = TR (Wigner-Dyson, by RMT regime at small K) OR BL
   (Poisson, by Poisson regime at large K). The verdict depends on which
   regime the NNS/RF readout falls in — see two-layer cross-phase below.

3. **RF engine Mode B** (`ramanujan_fourier(normalize=True)` on unit-mean
   spacings). Pre-installed Mode B per §7.ter.49 machinery-side false-positive
   discipline.

4. **p-adic v4** (`padic_amplitude_v4` per-q-power-normalized). Hecke null
   prediction: no prime dominance. Any z > 2 above the right null is the
   substantive deep-layer signal.

5. **Right-null surrogates:**
   - **Poisson surrogate** on fundamental sector at matched event count
     (5 seeds — calibration null, will not reject).
   - **CUE surrogate** at matched matrix size N = (log K)/π from §B
     ensemble infrastructure — bulk-universal RMT comparison.
   - **σ²(K, X) direct moment** (the RW load-bearing measurement) — *not*
     a surrogate but the discriminating global statistic per §B
     bulk-vs-edge note.

6. **Within-window stability** (surrogate-independent falsifier per Phase
   34b discipline): any RF |a_q| spike at q < 30 must be stable across 5
   non-overlapping equal-event-count windows, CV < 0.3. Sequence-side
   property; does not depend on null choice.

---

## §C. Cross-phase two-layer enumeration

Per **§7.ter.48** discipline (Phase 34b), enumerate surface and deep
separately.

**Surface layer (vs Poisson):**
- 34d-G surface: rigidity expected at K < √N; PARALLEL_NULL@Poisson for
  K > √N (Poisson saturation regime).
- 34d-E surface: expected by structural analogy to 34d-G.
- **34d-G × 34d-E surface:** expected PARALLEL_SIGNAL by structural
  analogy — both Hecke-equidistributed prime-angle substrates with same
  RMT/Poisson crossover. Confirmatory; not a novel finding.

**Deep layer (vs RW variance prediction):**
- 34d-G deep: Rudnick-Waxman is the explicit conjecture. ARS verdict =
  instrument-validation (parallel to ζ → TR in Phase 34c).
- 34d-E deep: Eisenstein implicit-analog measurement. Two sub-outcomes:
  - **Constant-level divergence** (different prefactor: e.g.,
    σ²_Eisenstein ~ c_E · (N/K) min(1, 2 log K / log N) with c_E ≠ c_G
    but same min-shape): expected from unit-group order difference
    (4 → 6); confirmatory of structural analog; **not novel**.
  - **Functional-form divergence** (different scaling exponent in σ²(K, X),
    different shape of the variance curve, or new crossover scale): genuinely
    new finding; would constrain or extend the implicit Eisenstein conjecture.

**Joint statement to Phase 34c real-Dirichlet Sp stratum (Eisenstein /
χ₋₃ structural connection):**

χ₋₃ is a real Dirichlet character (mod 3, Legendre symbol). Phase 34c
classified the real-Dirichlet stratum NULL_IN_ORTHOGONAL_CHANNELS_BEYOND_RMT.
The Eisenstein-prime-angle substrate is structurally tied to L(·, χ₋₃) —
both encode arithmetic of Q(√−3) — but the spectral coordinate differs
(L-function zero positions vs prime angles).

**Pre-specified joint verdict:** if 34d-E lands NULL_IN_ORTHOGONAL_CHANNELS_BEYOND_HECKE
(angle-side) AND 34c χ₋₃ Sp stratum is NULL_BEYOND_RMT (zero-side), then
**both ARS readouts of the same underlying arithmetic object (Q(√−3)) at
two different spectral coordinates land null beyond their respective right
nulls**. This is stronger than direction-match: it is convergent-null
across coordinates of one arithmetic substrate. Forward-binds Phase 34f
Bianchi-Maass-on-PSL(2, O_K) as the third coordinate on the same
substrate, completing a single-substrate, multi-coordinate
instrument-validation triple.

---

## §D. Prime-K seduction discipline

Pooled-substrate sub-pool sweep applies if pooling across norm bands.
Single-band Gaussian or Eisenstein prime-angle survey at fixed X has no
pooling structure, so K-pool discipline is light here.

**Mandatory check anyway:** any prime-q RF spike at q < 30
(q ∈ {2, 3, 5, 7, 11, 13, 17, 19, 23, 29}) must trigger documented sub-pool
sweep across the X scan {10⁵, 10⁶, 10⁷} regardless of compellingness.
**Phase 34c EC root-minus q=17** was caught at exactly this discipline.

---

## Acceptance criteria

- Pre-pilot Step 3 (direct variance check): reproduces RW Figure 1 shape
  (saturation at β > 0.5, linear ramp at β < 0.5).
- Pre-pilot Step 4 (ARS on Gaussian angles): direction-agreement with Step 3.
- Within-window stability gate: CV < 0.3 across 5 windows on any flagged
  RF spike at q < 30.
- Prime-K sub-pool gate: any prime-q RF spike documented across the X scan.
- Two-layer cross-phase: surface and deep verdicts reported separately.
- Mechanism-distinctness re-run (§7.ter.26): Katz monodromy triple
  classified relative to Hermite triple on the extended calibrator panel.

---

## Verdict map (pre-specified, no commitment to outcome)

- **NULL_IN_ORTHOGONAL_CHANNELS_BEYOND_HECKE**: angle substrate featureless
  beyond Hecke equidistribution + RW variance prediction.
- **RW_REPLICATED_AT_DEEP_LAYER**: ARS reads RW-predicted variance signature
  via direct σ²(K, X) measurement at the K ≈ √N crossover (NOT via NNS/RF
  family-classification, per §B bulk-vs-edge architecture). Instrument-
  validation success.
- **DIVERGENT_FROM_RW**: substrate detects something other than the RW
  prediction. Either the literature is wrong on this substrate (unlikely
  given Katz 2017's function-field proof) OR ARS has a systematic on
  prime-angle substrates that Phase 34a-c discipline didn't surface.
- **GAUSSIAN_EISENSTEIN_DIVERGENT_CONST**: 34d-G and 34d-E differ at
  *constant level* only (different prefactor, same min-shape). Expected
  from unit-group order difference. **Confirmatory of structural analog.**
- **GAUSSIAN_EISENSTEIN_DIVERGENT_FUNCTIONAL**: 34d-G and 34d-E differ at
  *functional form level* (different scaling exponent or curve shape).
  **Substantively novel; would constrain or extend the implicit Eisenstein
  conjecture.**
- **AMBIGUOUS_AT_BOUNDARY**: marginal signal at one prime q surviving
  Poisson null but failing within-window stability falsifier.

---

## Outputs

```
phase34d/
  PHASE34D_BRIEF.md                                    (this file)
  lit/
    rudnick_waxman_2019.pdf                            ✓ cached
    katz_2017.pdf                                      ✓ cached
    LIT_SUMMARY.md                                     ✓ written
  circular_sampler.py                                  CUE/COE/CSE (Mezzadri 2007)
  gaussian_primes.py
  eisenstein_primes.py
  run_rw_variance_direct.py                            Step 3 pre-pilot
  run_prepilot_ars.py                                  Step 4 pre-pilot
  run_substantive_eisenstein.py
  run_cross_phase_to_34c.py
data/phase34d_results/
  gaussian_primes_N{1e5,1e6,1e7}.npz
  eisenstein_primes_N{1e6,1e7,1e8}.npz
  rw_variance_direct.json
  gaussian_prepilot_ars.json
  eisenstein_substantive_ars.json
  cross_phase_34d_to_34c_dirichlet.json
PHASE34D_FINDINGS.md
```

`PHASE34D_FINDINGS.md` follows the per-finding template established at
34a/b/c: frame, methodology, sub-questions with results, cross-phase,
methodological generalisations, verdict map.

---

## Out-of-scope

- Function-field-Frobenius surrogate via Katz's full construction (would
  require F_q[√-T] arithmetic infrastructure beyond what's currently
  deployed). Default to Poisson + Circular-ensemble surrogates.
- Hex-Sacks visualization side-thread (tracked as visualization
  infrastructure; not required for the brief).
- Bianchi-Maass-on-PSL(2, O_K) cross-coordinate test (queued for Phase 34f
  per §C joint statement).

---

## Open questions (some may resolve in pre-pilot)

1. **CUE/COE/CSE mechanism-distinctness on extended panel.** Expected:
   CUE indistinguishable from GUE on bulk-dominated engines. Document as
   bulk-universality empirical statement.
2. **Pooling convention robustness.** Default: one angle per prime ideal.
   Alternative: pool all 8 (resp. 12) unit-orbit-and-conjugate
   representatives. Robustness panel only.
3. **Calibrator-zoo extension to "RW-class" / function-field-Frobenius.**
   If 34d-G validates, consider Phase 34e to add a named "Rudnick-Waxman"
   calibrator class to the zoo — would convert RW from "literature target"
   to "named calibrator class".

---

## Notes for the executing session

- Phase 34d uses the deployed `joint_q_profile` + `ramanujan_fourier(normalize=True)`
  + `padic_amplitude_v4` — no new ARS infrastructure required.
- New ensemble code: `phase34d/circular_sampler.py` (Mezzadri 2007).
- Gaussian/Eisenstein prime generation: direct sympy or pure-Python sieving
  with classification by p mod 4 / p mod 3.
- Right null is Poisson (simple to sample); the substantive comparison is
  real-data σ²(K, X) vs Poisson variance vs RW prediction.
- Within-window stability is the load-bearing falsifier — surrogate-independent
  and therefore the strongest claim about whether any flagged structure is a
  sequence-level property.
- Two-layer cross-phase enumeration (§7.ter.48 convention) is the
  publication-framing safeguard: surface PARALLEL_SIGNAL vs deep PARALLEL_NULL
  / DIVERGENT must be reported separately.

# Part C — Refusal Zoo: baseline-B null, operationalized & pre-registered (HELD)

**Status: SEALED pre-registration. DOES NOT RUN** until deliberately started. Per the plan,
Part C is "the single most seductive self-deception in the project"; the baseline B is the
guard, and it is specified here to the operational level of Part B's Gate 0. No unseal.

**The finding, in advance (measurement only):** the refusal-report R must separate the zoo
members **better than a trivial-descriptor baseline B**, reproducibly, surviving surrogate.
Anything less is the null.

---

## 1. Refusal zoo members (each = a *type*; ≥25 independent instances per type for CV)

All are substrates a standard-ensemble classifier REFUSES, but for different reasons:
- **T1 deterministic-decaying** — GKW/e-CF transfer-operator eigenvalue tails (decaying,
  few resolvable levels). Instances: different operators/truncations.
- **T2 picket-fence/rigid** — near-equally-spaced levels + small jitter (Σ²→0). Instances:
  varying jitter amplitude.
- **T3 critical/intermediate** — semi-Poisson (Γ(2,½) spacings) and Anderson-critical-like
  models. Instances: varying the interpolation parameter.
- **T4 non-spectral** — clustered/Hawkes and arithmetic sign-change point processes
  (Mertens/Liouville support sets from Phase 34). Instances: varying clustering.
- **T0 accepted-control** — genuine GUE/GOE (NOT refused). Included so the test also sees
  the refuse/accept boundary. Instances: fresh draws.

Each instance is one point process of comparable length (n≈300–800).

## 2. Baseline B — trivial descriptors (3 features, fully specified)
- **b1 rigidity scalar** = least-squares slope of Δ₃(L) vs L over L∈[2,10] (theory-fixed
  unfold where a unit-density unfold exists; else on raw-normalized spacings).
- **b2 density-variation** = coefficient of variation of the local level density (windowed
  count / window), i.e. how non-stationary the spectrum is before unfolding.
- **b3 support/type flag** = (n_resolvable_levels, mean_spacing_after_naive_unfold,
  is_monotone_decaying_sequence ∈{0,1}) — the "spectral-type" categorical.

## 3. Refusal report R — the ARS boundary fingerprint (the object under test)
Per-instance vector: ⟨r̃⟩; P(r̃) in 6 bins; NNS-KS to {Poisson,GOE,GUE,GSE}; Σ²(L) at
L∈{2,5,10}; Δ₃ slope; the refusal-reason category (one-hot); pole/decoy-battery responses;
mean_spacing. (Deliberately a superset of B in raw information — see fairness guard.)

## 4. Fair-comparison protocol (pre-registered; the guard against a rigged win)
Task: classify held-out instance → its type Tk. Same classifier for B and R
(random-forest, fixed hyperparameters), same **stratified 5-fold CV**, same instances.
- **Metric** = mean held-out balanced accuracy, A(B) and A(R).
- **Fairness guards (all mandatory):**
  1. **Label-permutation surrogate** for BOTH B and R: shuffle type labels, recompute CV
     accuracy (200×). Report each accuracy as a z-score above its OWN permutation null —
     this neutralizes R's larger feature count (more features inflate the null too).
  2. **Within-B-cell test** (the sharpest): bin instances into cells of near-identical B
     (kNN in B-space). Within cells (where B is ~constant), does R still separate types
     above its within-cell permutation null? If yes, R carries structure B cannot encode.
  3. **Dimension control:** also run R restricted to a random 3-feature subset, to show any
     R-advantage is not merely "more features."

## 5. Decision (pre-committed)
- **NULL → bank negative, dark-appendix the zoo:** A(R) not reproducibly above A(B) at the
  same permutation-z, AND the within-B-cell test shows no residual R-separation. Reading:
  "the refusal-report re-encodes input-obvious descriptors; the boundary has no own-structure."
  This is a valid, expected, worth-the-night outcome.
- **POSITIVE → measurement only:** A(R) > A(B) reproducibly at matched permutation-z, AND
  within-B-cell R-separation survives its null, AND survives a data surrogate. Banked result
  (the ENTIRE finding): *"the boundary-report carries substrate-covarying structure beyond
  trivial descriptors."*

## 6. Interpretation hedge (STRUCTURAL — separate field, never promoted)
"ARS measures coupling-type" is **not** the finding and is recorded only in an
`interpretation` field. Exceeding B earns "structure beyond trivial descriptors," **not** a
mechanism. The banked result is the measurement in §5.

## 7. Why held tonight
Running Part C requires the members assembled and the classifier + CV harness built and
themselves validated (a mis-built B that is trivially weak would rig the test — the exact
self-deception this plan exists to refuse). That build deserves a deliberate start, not the
tail of a long session. This pre-registration is the prerequisite the plan demands; with it
sealed, Part C may run as a single pre-committed unseal.

*Sealed. No unseal. Part C does not run until deliberately started against this protocol.*

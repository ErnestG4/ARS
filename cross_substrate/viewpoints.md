# ARS Landscape Viewpoints — Coordinate Candidates

**Status:** working artifact, v0 first cut. Companion to `landscape.md`.
**Date:** 2026-05-22
**Frame:** explorer-shaped, no commitment to "the" coordinate system; compute multiple candidate axis sets per substrate; let descriptive axes earn their place empirically.

---

## §1 — Framing

The substrate landscape (`landscape.md`) charts where substrates fall on the spectral side. A *viewpoint* is a specific choice of axes used to look at that landscape — a 2D or 3D projection that makes some cluster structure visible and other structure invisible.

The methodological commitment: do not pre-pick a single viewpoint. Multiple candidate axis sets are computed per substrate; the landscape gets multiple parallel projections; we let the data reveal which viewpoints turn out to be descriptive for the questions we end up asking.

This is computationally cheap. Substrate generation (event trains at large N, large L; spike-train acquisition; simulations) dominates compute cost by orders of magnitude. Per-substrate post-processing across many candidate axes is small additional cost. Compute everything applicable; project later.

Naming convention: *coordinate* is a single axis; *viewpoint* is a set of 2-4 coordinates that together project the landscape. Sets are letters A, B, C…; individual axes are numbered within families.

---

## §2 — Individual candidate axes (catalog)

Organized into families. Each axis has:
- **Definition.** Precise enough to implement.
- **Range.** What values it can take.
- **Discriminates.** What it ranks substrates by.
- **Applicability.** Which substrate classes it applies to.
- **Source.** What the axis is computed from.

### Family I — NNS distribution distances

Pair-level level-spacing statistics. Computed from unfolded NNS distribution.

**I.1 — W1δ (Wasserstein-1 from clock).**
- **Definition.** 1-Wasserstein distance between unfolded NNS distribution and δ(s−1) (clock).
- **Range.** 0 (clock) to ~0.736 (Poisson, 2/e).
- **Discriminates.** Clock ↔ Wigner-Dyson ↔ Poisson distance along the rigidity axis.
- **Applicability.** Any substrate yielding a point process.
- **Source.** Unfolded NNS distribution.
- **Notes.** ARS primary scalar. Used as W1δ in Phase 35.

**I.2 — W1-GUE (Wasserstein-1 from GUE).**
- **Definition.** 1-Wasserstein distance between unfolded NNS and the GUE Wigner-Dyson distribution.
- **Range.** 0 (perfect GUE) to ~0.5 (clock or Poisson, depending on direction).
- **Discriminates.** How GUE-like the substrate is.
- **Applicability.** Universal.

**I.3 — W1-GOE.**
- **Definition.** Analogous to I.2 with GOE reference.
- **Applicability.** Universal; useful for substrates with time-reversal symmetry expected.

**I.4 — W1-Poisson.**
- **Definition.** 1-Wasserstein from unfolded NNS to exp(1) (Poisson NNS).
- **Discriminates.** How Poisson-like; complement to I.1 and I.2.
- **Applicability.** Universal.

**I.5 — ks_gue_med (KS-median to GUE).**
- **Definition.** Median over bootstrap of Kolmogorov-Smirnov distance between unfolded NNS and GUE Wigner-Dyson.
- **Discriminates.** GUE-likeness; more sensitive to distribution tail than W1.
- **Applicability.** Universal.
- **Notes.** Used in pvc-11 H1 work.

**I.6 — ks_clock.**
- **Definition.** KS from unfolded NNS to δ(s−1).
- **Applicability.** Universal.

**I.7 — ks_poisson.**
- **Definition.** KS from unfolded NNS to exp(1).
- **Applicability.** Universal.

**I.8 — Brody parameter q.**
- **Definition.** Fit parameter in Brody distribution P(s) = c sᵛ exp(−α s^(v+1)) interpolating Poisson (q=0) and Wigner (q=1).
- **Range.** [0, 1] (or beyond if extrapolated).
- **Discriminates.** Single-parameter interpolation Poisson ↔ Wigner.
- **Applicability.** Universal; common in quantum chaos literature.

**I.9 — Berry-Robnik parameter ρ.**
- **Definition.** Mixed-phase-space fraction parameter in BR distribution.
- **Discriminates.** Phase-space mixing fraction; useful when substrate is suspected mixed-regime.
- **Applicability.** Universal; more sophisticated than Brody.

### Family II — Long-range NNS correlations

Beyond pair statistics. Captures correlations over multiple spacings.

**II.1 — Σ²(L) at fixed L (number variance).**
- **Definition.** Var(N(L)) where N(L) counts unfolded events in an interval of length L.
- **Range.** Substrate-dependent.
- **Discriminates.** Clock (Σ²=0); Poisson (Σ²=L); GUE (Σ²~(1/π²) log(L)).
- **Applicability.** Universal.
- **Notes.** Choose L based on substrate scale; matched L across substrates for cross-substrate comparison.

**II.2 — Δ₃(L) (spectral rigidity).**
- **Definition.** Minimum mean-square deviation of N(s) from best linear fit on interval L.
- **Discriminates.** Long-range rigidity; classical universality-class diagnostic.
- **Applicability.** Universal.

**II.3 — Spectral form factor K(τ) at fixed τ.**
- **Definition.** Fourier transform of two-point density-density correlation; canonical RMT diagnostic.
- **Discriminates.** Fine universality-class structure; sensitive to small departures from canonical classes.
- **Applicability.** Universal.

**II.4 — R₂(s) shape parameters.**
- **Definition.** Parameters fit to two-point correlation R₂(s); e.g., long-range decay exponent.
- **Applicability.** Universal.

### Family III — Arithmetic / RF (number-theoretic)

Captures arithmetic structure orthogonal to NNS averaging.

**III.1 — p-adic concentration at prime p.**
- **Definition.** Sum (or peak) of RF basis-mode amplitudes at modes corresponding to prime p.
- **Discriminates.** Arithmetic resonance at p; orthogonal to NNS-class.
- **Applicability.** Substrates with discrete event-train structure aligned to integer index; less natural for continuous-time event extraction.
- **Notes.** p=7 enrichment as canonical example from prior ARS work.

**III.2 — Small-prime arithmetic vector (p=2, 3, 5, 7).**
- **Definition.** Vector of p-adic concentrations for small primes; can be reduced to scalar (e.g., max, sum, principal-component projection).
- **Applicability.** Same as III.1.

**III.3 — RF basis-mode coefficient (top-k).**
- **Definition.** Truncated RF basis-mode amplitudes, vector form.
- **Applicability.** Same as III.1.

**III.4 — p-adic spectrum integral (scalar reduction).**
- **Definition.** Scalar reduction of RF p-adic spectrum (e.g., integral over primes weighted by amplitude).
- **Applicability.** Same as III.1.

### Family IV — Spectral measure character

For substrates with explicit spectral measure (eigenvalue substrates, dynamical-system attractors).

**IV.1 — Multifractal exponent (DGY-style).**
- **Definition.** Scaling exponent of spectral measure moments; for DGY-controlled systems, exact.
- **Discriminates.** Singular-continuous vs absolutely-continuous vs pure-point spectral character; Cantor-set structure.
- **Applicability.** Substrates with spectral measure analyzable in DGY framework — Fibonacci yes, AM in some regimes, ζ-zeros formally, V1 questionable (would require defining what the "spectral measure" of a spike train is).
- **Source.** Spectral measure box-counting / partition function.

**IV.2 — Spectral measure dimension (Hausdorff / box).**
- **Definition.** Fractal dimension of spectral support.
- **Discriminates.** Lebesgue (D=1) vs Cantor (D<1) vs pure-point (D=0).
- **Applicability.** Eigenvalue substrates; not natural for biological substrates without modification.

**IV.3 — Spectral decomposition weights.**
- **Definition.** Weights of Lebesgue / singular-continuous / pure-point components of spectral measure.
- **Discriminates.** Categorical spectral type; can be 3-vector or scalar reduction.
- **Applicability.** Eigenvalue substrates.

### Family V — Dynamical / chaos

For substrates with underlying time series (continuous-time dynamical systems).

**V.1 — Lyapunov exponent.**
- **Definition.** Largest Lyapunov exponent of attractor dynamics.
- **Discriminates.** Chaos (λ>0) vs non-chaos (λ≤0); magnitude indicates rate of phase-space divergence.
- **Applicability.** Substrates with time-series data — Mackey-Glass yes, biological-neural questionable (definition issues for noisy systems), ζ-zeros no.

**V.2 — Correlation dimension (Grassberger-Procaccia).**
- **Definition.** Scaling exponent of correlation integral C(ε) ~ ε^D.
- **Discriminates.** Attractor dimensionality.
- **Applicability.** Same as V.1.

**V.3 — Recurrence-quantification metrics.**
- **Definition.** RR (recurrence rate), DET (determinism), LAM (laminarity), TT (trapping time).
- **Discriminates.** Recurrent-structure properties of trajectory.
- **Applicability.** Same as V.1.

**V.4 — Permutation entropy.**
- **Definition.** Shannon entropy of ordinal patterns in time series.
- **Discriminates.** Complexity vs regularity of trajectory.
- **Applicability.** Time-series substrates.

### Family VI — Extraction-meta

Capture how the substrate fingerprint depends on instrument variations. Not spectral-class axes — substrate-robustness profile.

**VI.1 — L_iter convergence rate.**
- **Definition.** Exponent α in per_phi_shift_ptp(L) ~ L^(−α) decay of L-suppression.
- **Discriminates.** How quickly substrate signal emerges from L-iter artifact; varies with N (Phase 35 finding); can be L-range-dependent (rev-5.2.1 sub-side finding).
- **Applicability.** Eigenvalue substrates with iterative unfolding; possibly generalizable.
- **Source.** L-sweep of substrate spread at fixed (substrate parameters, N).

**VI.2 — N-scaling exponent of substrate spread.**
- **Definition.** Exponent β in substrate_spread(N) ~ N^β scaling of L-converged substrate spread.
- **Discriminates.** Magnitude of L-suppression growth with N — Phase 35 finding for AM (β positive, super-linear).
- **Applicability.** Eigenvalue substrates with variable-N capability.

**VI.3 — Cross-extraction variance.**
- **Definition.** Variance of fingerprint metric across different event-extraction choices for same substrate.
- **Discriminates.** Substrate robustness to extraction choice; useful for substrates with non-canonical event extraction (FM, time-series substrates).
- **Applicability.** Substrates with multiple plausible extraction methods.

---

## §3 — Coordinate sets (viewpoint candidates)

Coherent 2D or 3D groupings. Each set has a rationale and intended substrate scope.

### Set A — NNS-class triangle

- **Coordinates.** I.1 (W1δ) × I.2 (W1-GUE) × I.4 (W1-Poisson).
- **Rationale.** Places substrate in the canonical clock — Wigner — Poisson interpolation space. Universal baseline.
- **Applicability.** Every substrate producing a point process. The lingua-franca viewpoint.
- **Visualization.** 2-simplex (triangle) embedded in 3D, since the three distances are constrained.

### Set B — NNS + long-range

- **Coordinates.** I.1 (W1δ) × II.1 (Σ²(L) at chosen L) × I.5 (ks_gue_med).
- **Rationale.** Pairs short-range (NNS) and long-range (Σ²) information. Substrates that look similar at NNS may diverge at large L.
- **Applicability.** Universal; choice of L for Σ² needs matching across substrates.

### Set C — NNS + arithmetic

- **Coordinates.** I.1 (W1δ) × I.5 (ks_gue_med) × III.4 (p-adic spectrum integral, scalar reduction).
- **Rationale.** Adds arithmetic-structure axis orthogonal to NNS-only reads.
- **Applicability.** Substrates with arithmetic-structured event-trains; AM yes, ζ-zeros yes, V1 questionable.

### Set D — NNS + dynamical

- **Coordinates.** I.1 (W1δ) × I.5 (ks_gue_med) × V.1 (Lyapunov) or V.2 (correlation dimension).
- **Rationale.** Connects level statistics to dynamical chaos.
- **Applicability.** Substrates with underlying time series — Mackey-Glass yes, FM synth yes, V1 questionable, ζ-zeros no.

### Set E — NNS + spectral character

- **Coordinates.** I.1 (W1δ) × I.5 (ks_gue_med) × IV.1 (multifractal exponent).
- **Rationale.** Connects level statistics to spectral measure type. Particularly useful for substrates straddling spectral-type boundaries.
- **Applicability.** Substrates with definable spectral measure — Fibonacci yes, AM yes, ζ-zeros yes, V1 no (without spike-train spectral measure redefinition).

### Set F — Pure arithmetic

- **Coordinates.** III.1 (p=2 concentration) × III.1 (p=3) × III.1 (p=7) — or principal-component reduction of III.2 vector.
- **Rationale.** Number-theoretic landscape on its own; orthogonal to all NNS reads.
- **Applicability.** Arithmetic-structured substrates.

### Set G — Substrate-extraction-aware (meta)

- **Coordinates.** VI.1 (L_iter convergence rate) × VI.2 (N-scaling exponent) × VI.3 (cross-extraction variance).
- **Rationale.** Captures how substrate behaves under instrument variation. AM's L-pathology lives natively here. Not a fingerprint in the spectral-class sense — substrate-robustness profile.
- **Applicability.** Any substrate where we've done extraction-axis variation work; AM yes (Phase 35), pvc-11 V1 partially (cross-extraction studies exist).
- **Notes.** Set G is conceptually distinct from A-F. The other sets characterize what the substrate IS; G characterizes how the substrate RESPONDS to the instrument. Cluster structure in G would reveal substrates with similar extraction-pathology profiles, which is a different scientific yield than spectral-class confluence.

---

## §4 — Substrate-applicability matrix

Rows: substrates (from `landscape.md` §3). Columns: axis families.

| Substrate | I (NNS dist) | II (long-range) | III (arithmetic) | IV (spectral char) | V (dynamical) | VI (extraction-meta) |
|---|---|---|---|---|---|---|
| AM | ✓ | ✓ | ✓ | ✓ (partial — AC/PP regimes) | — (eigenvalues, no time series) | ✓ (Phase 35 data) |
| Fibonacci | ✓ | ✓ | ✓ | ✓ (DGY-exact) | — | ○ (not yet measured) |
| pvc-11 V1 | ✓ | ✓ | ◐ (event-index alignment question) | ✗ (no natural spectral measure) | ◐ (time series in some sense but noisy) | ◐ (cross-extraction work exists, not banked as VI) |
| Allen NP | ✓ | ✓ | ◐ | ✗ | ◐ | ○ |
| Retinal | ✓ (when acquired) | ✓ | ◐ | ✗ | ◐ | ○ |
| FM/brocot.fm | ✓ (when event-train defined) | ✓ | ✓ (Stern-Brocot path is arithmetic) | ◐ | ✓ (time-series substrate) | ✓ (extraction-choice native to substrate) |
| ζ-zeros | ✓ | ✓ | ✓ | ✓ | ✗ (no underlying dynamical system, though Hilbert-Pólya conjectures one) | — (canonical, no extraction variation) |
| Mackey-Glass | ✓ (when event-extraction defined) | ✓ | ◐ | ◐ | ✓ (canonical dynamical) | ✓ (extraction-choice variation natural) |
| Sacks/quadratic | ✓ (when event-train defined) | ✓ | ✓ (number-theoretic substrate) | ◐ | — | ◐ |

Legend: ✓ applicable / done where applicable; ◐ partially applicable or requires methodological work; ✗ not applicable; ○ applicable but not done; — not applicable in principle.

---

## §5 — Computation specifications

### Universal preprocessing

For each substrate, given an event train (sequence of event positions or inter-event intervals):

1. **Unfold** — apply substrate's chosen unfolding method to obtain unit-mean spacings.
2. **L-iter audit (where applicable)** — for substrates with iterative unfolding, audit L-convergence per Phase 35 discipline.
3. **Compute applicable axes** — per §4 applicability matrix.

### Family I (NNS-distance) — implementation

- I.1 (W1δ): `W1δ = E[|s - 1|]` over unfolded spacings.
- I.2-I.4 (W1 to reference): scipy `wasserstein_distance` against canonical reference distributions.
- I.5 (ks_gue_med): bootstrap KS distance to GUE, median over resamples (parameters per pvc-11 H1 convention).
- I.6-I.7: scipy `ks_2samp` against canonical references.
- I.8 (Brody q): maximum-likelihood fit of Brody distribution to empirical NNS.
- I.9 (Berry-Robnik ρ): MLE of BR mixture parameter.

### Family II (long-range) — implementation

- II.1 (Σ²(L)): cumulative count variance computation; choose L per substrate scale; cross-substrate-matched L for set B.
- II.2 (Δ₃(L)): least-squares deviation from linear fit on length-L window.
- II.3 (K(τ)): Fourier transform of two-point correlation.
- II.4 (R₂ shape): fit canonical R₂ form to empirical pair-correlation.

### Family III (RF arithmetic) — implementation

- Existing ARS RF engine output. III.1 from RF spectrum at prime-p mode; III.2 vector; III.3 top-k coefficients; III.4 scalar reduction (specify reduction method).

### Family IV (spectral character) — implementation

- IV.1 (multifractal): box-counting partition function; scaling exponent extraction.
- IV.2 (spectral dimension): Hausdorff / box-counting on spectral support.
- IV.3 (decomposition weights): spectral measure decomposition via standard methods.

### Family V (dynamical) — implementation

- V.1 (Lyapunov): Rosenstein or Wolf algorithm; choose parameters per substrate.
- V.2 (correlation dimension): Grassberger-Procaccia.
- V.3 (RQA): standard recurrence-plot quantification.
- V.4 (permutation entropy): ordinal-pattern Shannon entropy.

### Family VI (extraction-meta) — implementation

- VI.1 (L_iter convergence rate): linear fit on log(per_phi_shift_ptp) vs log(L) → α; flag L-range-dependence if α not constant.
- VI.2 (N-scaling exponent): linear fit on log(L-converged spread) vs log(N) → β.
- VI.3 (cross-extraction variance): variance of fingerprint scalar across extraction choices.

---

## §6 — Coordinate banking format

Per substrate, per cell (where cells are meaningful — AM cells indexed by N; V1 cells indexed by unit; etc.), produce a record:

```
{
  "substrate": "AM",
  "cell_id": "N=70k,sup,delta=0.5,lambda=1.5",
  "axes_computed": {
    "I.1_W1d_clock": 0.382,
    "I.2_W1_GUE": null,            // not yet computed
    "I.5_ks_gue_med": null,
    "III.1_p7_concentration": null,
    ...
    "VI.1_L_iter_alpha": "L-range-dependent (1.25 → 0.50)",
    "VI.2_N_scaling_beta": 1.5     // approximate, from Phase 35 chain
  },
  "applicable_axes_not_yet_computed": [...],
  "non_applicable_axes": ["V.1_Lyapunov", "V.2_correlation_dim"],
  "extraction_method": "unfold_rotnum",
  "extraction_audit": {
    "L_iter_converged": true,
    "L_iter_value": 2.56e7,
    ...
  },
  "source_artifact": "bo73me0uq",
  "source_commit": "...",
  "computed_date": "2026-MM-DD"
}
```

Format flexible (JSON, CSV, or DB schema); the structural commitment is per-substrate per-cell per-axis with applicability metadata.

---

## §7 — Update protocol

This document populates as work proceeds:

- **New axis candidates.** Add to §2 family catalog with definition, range, applicability, source. If it doesn't fit an existing family, add a family.
- **New coordinate sets.** Add to §3 with rationale and applicability scope.
- **Substrate-applicability decisions.** Update §4 matrix as substrate methodology develops.
- **Implementation refinements.** §5 evolves with implementation experience.

No axis or set gets retired unless empirically shown to be non-descriptive across enough substrates that the case for inclusion fails. The default posture is breadth — compute everything applicable; let cluster structure across many viewpoints earn or fail to earn the axes' inclusion in the descriptive landscape.

Working artifact, no rev-numbering; edits land in-place.

**v0 — 2026-05-22.** First cut. Six axis families (NNS distance, long-range NNS, RF arithmetic, spectral character, dynamical, extraction-meta) with 25+ individual candidate axes. Seven coordinate sets (A-G). Substrate-applicability matrix sketched across 9 substrates. Computation specifications outlined at family level.

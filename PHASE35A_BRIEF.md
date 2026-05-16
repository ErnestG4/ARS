# PHASE 35a BRIEF (revised 2026-05-16 — Will's phantom catch)
## Derive + anchor the resolution-indexed Cantor-spectrum NNS calibrator family (prerequisite for the Almost-Mathieu transition-diagnostic arc)

**Status:** Pre-execution. **BRIEF ONLY — brief-and-hold** (no code, no compute, no execution without explicit go). **Revised** from the first draft, which reintroduced exactly the phantom it claimed to eliminate (an *asserted*, not derived, Cantor NNS signature; a "two clean classes" partition Ten Martini forbids). This revision **changes what 35a's goals are**, so it goes back to hold for re-review, not into execution. Decision record: memory `phase35_am_arc_design`.

**Lit-lock (verify at execution start, BCGNT-style — cited, not yet independently verified):** Avila–Jitomirskaya **Ten Martini** (AM spectrum is a Cantor set for *all* irrational θ and *all* λ≠0 — load-bearing for the corrected class structure); Avila–Jitomirskaya phase diagram (the proven λ=1 boundary; subcritical AC- / critical SC- / supercritical PP- *spectral-measure* type); Damanik–Gorodetski–Yessen (Fibonacci-Hamiltonian exact multifractal exponents + rigorous trace-map renormalisation — of the **DOS/spectrum**, not the NNS); gap-labelling (Johnson–Moser / Bellissard: IDS ∈ ℤ+θℤ on gaps — makes the *unfolding* well-defined); Avila one-frequency cocycle theory (the AM↔cocycle-over-irrational-rotation bridge).

---

## §0. Frame

Phase 35 is **instrument-validation, not measurement** — nothing novel to discover in AM spacing statistics (40 yr literature). The value-add: **AM is the first *non-synthetic* universality-transition substrate to validate `transition_diagnostic`** (Phase-20.5 blends are circular hand-tuned mixing weights; AM's λ=1 boundary is Avila–Jitomirskaya-*proven*). 35a is the prerequisite: it must hand 35b an honest NNS reference for the AM regimes.

**Named honestly (the recurring error class).** The first draft partitioned by *substrate type* what is actually a *resolution regime*, and asserted an NNS signature ("atom at zero + multifractal tail") that was never derived. This is the same resolution/regime-dependence error that recurred through the 34-arc (p-value regime → KS sample-size regime, §7.ter.59) — here at *spectral resolution*. Stated as a standing discipline: **"the operation is well-defined" ≠ "the resulting statistic is known."** Gap-labelling made the IDS-unfolding well-defined; it did **not** hand over the unfolded NNS distribution. 35a's primary deliverable is that **derivation**, not its assertion.

## §1. Goals

1. **PRIMARY (the real research content): derive the IDS-unfolded, finite-N, Cantor-spectrum NNS** as a function of (λ, N) — shape, small-spacing mass, tail — **explicitly separating the finite-N gap-stranding artifact** (eigenvalues stranded inside limiting-spectrum gaps by finite-size error, which →0 as N→∞) **from the N→∞ behaviour.** No NNS signature is assumed; deriving it (analytically, or via a clean N→∞ extrapolation that isolates the artifact) is the task.
2. **Anchor:** the λ=0 exact clock (the *unique* genuinely non-Cantor point — free Laplacian, single band [−2,2]) as the rigorous endpoint of the family.
3. **Generator-validation:** confirm the Fibonacci trace-map reproduces the DGY exact multifractal exponents — this validates the *generator*, separately from (1).
4. Construct the calibrator **only after (1) yields its NNS ground truth.** The deliverable is **one resolution-indexed Cantor-spectrum calibrator family** (λ, N parameters; λ=0 exact-clock endpoint), **not two classes.**

If (1) is analytically intractable and no clean N→∞ extrapolation isolates the artifact, 35a **halts** (`DERIVATION_INTRACTABLE_HALT`) and the AM arc does not proceed to 35b — an honest dead-end is a valid outcome.

## §2. Scope

**IN:** the Cantor-NNS derivation (§3); the λ=0 anchor (§4); DGY generator-validation (§5a); calibrator construction *gated on* the derivation (§5b); verdict per §7.

**OUT (load-bearing):**
- **NOT** AM measurement / the (θ,λ) sweep / the transition diagnostic — that is 35b, gated on 35a.
- **NOT** the λ=1 critical line *as a measured substrate* on the joint plane (f(α) singularity-spectrum territory — a different instrument; §7.ter.49 mode-A class). 35a builds a *calibrator so the zoo can recognise/quarantine* Cantor spectra; it does not classify λ=1 on BL/TR/BR/TL.
- **NOT** a discovery/measurement cell — calibrator construction, never a result (asymmetric-label, METHODS §1).

**Corrections that must NOT be re-imported:**
- **Ten Martini (new, load-bearing):** the AM spectrum is Cantor for *all* λ≠0 — subcritical AM is **not** band-structured. "Clock-like vs Cantor-like" is a **finite-N resolution regime** (sub-1/N gaps unresolved), not a substrate partition. Spectral-measure type (AC/SC/PP) is NNS-invisible and does **not** index the family.
- **No asserted NNS signature.** No "atom at zero / multifractal tail / recover it." The finite-N stranding atom is an artifact to *characterise and exclude*, never a defining feature (stamping it = §D.0b silent corruption — the very thing the brief's discipline forbids).
- No AM regime is BCGNT-grade; supercritical Poisson is Bourgain–Goldstein/Jitomirskaya, **not** Minami (iid-only). Rigour anchor = the *transition boundary*, not regime-wise NNS theorems.
- Cocycle-over-irrational-rotation bridge kept; "deformed-bucket = vary λ" scaffold stays killed.
- AM is GOE-by-symmetry for bookkeeping, but no regime is Wigner; predictions are Poisson (supercritical) / clock-rigid (λ→0 coarse-resolution limit only).

## §3. The resolution-indexed Cantor-spectrum family (the derivation — 35a's core)

- **Ten Martini:** for irrational θ and every λ≠0 the spectrum is a Cantor set. There is no finite band union at any λ∈(0,1); there is a Cantor set of bands at every λ≠0. Only λ=0 is a genuine single band.
- **Resolution crossover (a (λ,N) statement, not a substrate one):** a finite-N truncation resolves the spectrum to scale ~1/N. Cantor gaps narrower than that scale are invisible; the finite-N spectrum *looks* band-/clock-like when N is coarse relative to the λ-dependent gap scale, and the Cantor structure progressively emerges as N grows at fixed λ. "Class II → Class I" of the first draft is this continuous crossover — **one family**, indexed by (λ, N).
- **Unfolding is well-defined; the NNS is not known.** Unfold by the IDS via gap-labelling (IDS ∈ ℤ+θℤ on gaps, explicitly computable) — this is settled (the earlier correction stands). But IDS-unfolding *erases* gaps (maps eigenvalues to ≈ uniform mean spacing, exactly as GUE-by-semicircle / ζ-by-RvM); it does **not** atomise them. What the resulting NNS distribution *is* — small-spacing mass, bulk shape, tail, and how each depends on (λ, N), and which features are finite-N artifact vs N→∞ limit — **is underived. Deriving it is the task of this phase.** Plausible going in (NOT assumed): heavy/multifractal-flavoured spacings reflecting the DOS multifractality, plus a finite-N stranding contribution near zero that must be shown to vanish with N; both to be established, not asserted.

## §4. The λ=0 exact-clock anchor + the orthogonal AC/SC/PP label

- **Anchor:** λ=0 free Laplacian, N-truncation eigenvalues 2cos(πk/(N+1)); arcsine-IDS unfold → exactly equispaced (clock, spacing 1, zero variance). Rigorous, exact, the family's λ=0 endpoint. (This is the *only* non-Cantor point — its specialness is now explicit, not a "second class".)
- **Spectral-measure type is an orthogonal, NNS-invisible label.** Subcritical AC (λ<1, diophantine θ) / critical SC (λ=1) / supercritical PP (λ>1) describe the spectral *measure* and eigenfunctions, not the spectrum-as-a-set and not directly the finite-N level spacings. It does **not** partition the calibrator family; it is recorded as metadata. The first draft's "clock+band-perturbation AC class" is **dissolved** into the §3 family as its small-λ / coarse-N corner, pinned by explicit (λ, N), not by spectral type.

## §5. Validation discipline — generator vs calibrator separated (Will's catch)

- **§5a Generator-validation (keep):** recover the DGY *exact multifractal exponents of the DOS/spectrum* from the Fibonacci trace-map truncations within tolerance. This validates that the **generator** reproduces the right spectrum. It does **NOT** validate the calibrator (the NNS is not the DOS f(α); the DOS-f(α)→NNS-shape map is precisely the §3 underived step).
- **§5b Calibrator-validation (gated):** there is **no NNS ground truth until §3 derives it.** Calibrator-validation is therefore *gated on* the §3 derivation: once the derivation yields a predicted (λ,N) NNS, the trace-map generator's empirical NNS must match that prediction — and this match is judged under the **§7.ter.59 sample-size-floor discipline**: every distribution test read as `KS / (0.8687/√n)` vs its own N/depth, never raw KS, never a large-n p-value, validated at realistic N (the cohomological-H lesson, imported as a hard precondition). Until §3 succeeds, §5b cannot run and nothing is stamped.
- **Negative controls:** the derived Cantor-family NNS must be distinct from BL/TR/BR/TL and from the λ=0 clock; the finite-N stranding artifact must be shown to shrink with N (if it does not, the "signature" is an artifact and the calibrator is rejected).

## §6. Pre-flight gates

- **Lit-lock** (incl. Ten Martini — load-bearing) before any build; halt on mismatch.
- **Compute (corrected):** AM / Fibonacci operators are tridiagonal — symmetric-tridiagonal eigensolve (LAPACK `stev`/`stebz`) sub-second at N=10⁴; cost driver across the arc is (θ,λ)-cell × seed × surrogate combinatorics and the Fibonacci-N-ladder (discrete). 35a is small except possibly the N→∞ extrapolation (multiple N per (θ,λ)).
- **Corrections checklist** (§2) is a hard pre-flight; any reappearance halts.

## §7. Verdict vocabulary (asymmetric — calibrator construction, never a result)

- `CANTOR_NNS_SIGNATURE_DERIVED` — §3 yields a (λ,N) NNS with the finite-N stranding artifact isolated and shown N→∞-vanishing.
- `GENERATOR_VALIDATED_VS_DGY_EXPONENTS` — §5a passes (generator, not calibrator).
- `RESOLUTION_INDEXED_CANTOR_CALIBRATOR_FAMILY_STAMPED` — derived NNS + generator-validated + §5b floor-anchored match; the family (incl. the λ=0 exact-clock endpoint) enters the zoo.
- `DERIVATION_INTRACTABLE_HALT` — §3 cannot be derived nor cleanly N→∞-extrapolated; **halt, do not stamp, AM arc does not proceed to 35b.** An honest dead-end.
- Cell-level: `PHASE35A_FAMILY_VALIDATED` / `_PARTIAL` / `_HALT`. **Never** a discovery/measurement/AM-result verdict.

## §8. Forward / scope boundary

On `PHASE35A_FAMILY_VALIDATED` (derivation + generator + floor-anchored calibrator):
- **35b (separate brief, gated):** transition-diagnostic validation. Supercritical + λ→1⁻ only; golden-mean θ; Fibonacci-N-ladder. Right-null = the **α-ensemble** (cos(2π(θn+α)) phase is part of the operator; α-ensemble at fixed (θ,λ) is the substrate-generated null per §7.ter.48; non-circular), **localised-regime only**. Verdict map pre-specified **both ways**: quadrant-flip (validates the diagnostic on a non-synthetic substrate) **and** sub-quadrant/rep_med-drift (the §7.ter.28 BGP precedent — diagnostic correctly returns null, evolution lives sub-quadrant).
- **35c (optional, contingent on 35b sub-quadrant outcome):** AM as the validation substrate for the Phase-22+ sub-quadrant-trajectory extension.
- λ=1 stays **out** of the whole arc as a measured substrate.

The arc validates `transition_diagnostic`; it is **not** AM measurement and yields no AM result.

## §9. Methodological commitments

- Brief-first / compute-after; no execution without explicit Will go (brief-and-hold).
- **"Well-defined operation" ≠ "known statistic"** (the §7.ter.59-class discipline, here at spectral resolution): a brief carries forward only what was actually *derived*; an unfolding being well-defined does not hand over its NNS. 35a's deliverable is the derivation; assertion is forbidden.
- Generator-validation and calibrator-validation are distinct gates; DGY validates the generator only.
- Resolution-regime, not substrate-partition (Ten Martini); spectral-measure type is NNS-invisible metadata.
- Synthetic/derived-ground-truth validation judged against its own sample-size/regime floor, realistic N (§7.ter.55/59).
- §D.0b: a mis-derived or artifact-stamped calibrator is the silent-corruption surface — `_HALT` over stamp.

## §10. References / cross-refs

- Avila, Jitomirskaya — *The Ten Martini Problem* (Annals 2009): Cantor spectrum for all irrational θ, all λ≠0. **Load-bearing.**
- Avila, Jitomirskaya — AM phase diagram (AC/SC/PP spectral-measure type; the proven λ=1 boundary).
- Damanik, Gorodetski, Yessen — Fibonacci-Hamiltonian exact multifractal exponents + trace-map renormalisation (DOS/spectrum, **not** NNS).
- Johnson–Moser / Bellissard — gap-labelling (IDS ∈ ℤ+θℤ on gaps; unfolding well-defined).
- Avila — one-frequency analytic SL(2,ℝ) cocycles (the bucket↔AM bridge).
- Bourgain–Goldstein / Jitomirskaya — supercritical localisation (the non-Minami status of supercritical Poisson).
- Cross-ref: memory `phase35_am_arc_design`; METHODS.md §1; RESULTS §7.ter.59 (sample-size-floor), §7.ter.28 (BGP sub-quadrant), §7.ter.46 (zoo-extension precedes instrument-validation), §7.ter.48 (substrate-generated null), §7.ter.49 (mode-A), §7.ter.55/57 (validate-on-known-truth), §7.ter.5/22 (resolution-dependence).

---

End of brief — **goals revised; back to brief-and-hold, awaiting Will's re-review** before any 35a derivation/build. Execution still requires explicit go.

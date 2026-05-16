# PHASE 35a BRIEF (rev 2 — 2026-05-16 — Will's option-2 two-operator-forced restructure)
## Build the two analytically-anchored Cantor / AC NNS calibrators on the two operators each is mathematically forced onto (prerequisite for the Almost-Mathieu transition-diagnostic arc)

**Status:** Pre-execution. **BRIEF ONLY — brief-and-hold** (no code, no compute, no execution without explicit go). **Rev 2** of the revised brief. Rev 1 (commit 6bc2b78) collapsed 35a to "ONE resolution-indexed Cantor family on AM"; that is now superseded — it had no analytic ground truth to derive against (AM-critical multifractal structure is itself conjectural/numerical, not DGY-grade), so the calibrator could not be §5-synthetic-validated. Rev 2 puts each calibrator on the operator that supplies it *both* an analytic anchor *and* the correct spectral type. This **changes 35a's goals again**, so by the standing line-4 logic it goes back to **brief-and-hold for Will's final compute-go**, not into execution (also matches "give it one more pass before you start"). 35a is authorized in principle (memory `phase35_am_arc_design`); compute still requires an explicit go. Decision record: memory `phase35_am_arc_design`.

**Lit-lock (verify at execution start, BCGNT-style — cited, not yet independently verified):**
- Avila–Jitomirskaya **Ten Martini** — AM spectrum is a Cantor set for *all* irrational θ and *all* λ≠0. **Still binds:** it does **not** make AM the Cantor *calibrator* (no DGY-grade exponent control on AM); it constrains Class II's (λ,N) pinning (below).
- Avila–Jitomirskaya AM phase diagram — the proven λ=1 boundary; subcritical **AC** (λ<1, diophantine θ) / critical SC / supercritical PP *spectral-measure* type. Load-bearing: AC exists **only on AM**.
- **Fibonacci Hamiltonian spectral type** — purely **singular-continuous, zero-measure (Cantor)** spectrum for **every** V≠0 (Sütő / BIST / Damanik lineage). Load-bearing: Fibonacci **never** has an AC regime, so a clock+band-perturbation AC calibrator on Fibonacci is impossible *in principle*.
- Damanik–Gorodetski–Yessen — Fibonacci-Hamiltonian **exact multifractal exponents of the DOS/spectrum**, made rigorous from the **hyperbolicity of the Fibonacci trace map on the Fricke–Vogt invariant surface**. This hyperbolicity is **Fibonacci-specific**; the Harper (AM) trace map is *not* that dynamical object.
- Gap-labelling (Johnson–Moser / Bellissard) — IDS ∈ ℤ+αℤ (Fibonacci) / ℤ+θℤ (AM) on gaps — makes the *unfolding* well-defined (does **not** hand over the unfolded NNS).
- Avila one-frequency analytic SL(2,ℝ) cocycle theory — AM has an **analytic** sampling function (the cosine); the AM↔cocycle-over-irrational-rotation bridge. Fibonacci's sampling function is **discontinuous two-valued** (characteristic function of an interval along an irrational orbit — Sturmian/substitution). Different regimes of QP-Schrödinger theory, different methods.
- **Lit-lock BAR (option-3's grave — load-bearing):** any candidate "AM↔Fibonacci bridge" reference must clear **shared NNS distribution / shared exponents**, *not* "both are critical quasi-periodic operators." Multifractal exponents are not even shared *within* a family (coupling-dependent for Fibonacci, θ-dependent for AM) — there is no single universality class with shared exponents, hence nothing to cite. Kohmoto–Ostlund-lineage "critical QP operators share multifractal phenomenology" is **qualitative folklore, not BCGNT-grade**; carrying a calibrator on it = the **§7.ter.48 error** (surface parallel mistaken for structural identity — the Möbius-family mistake one substrate up). Halt on any bridge that clears only the folklore bar.

---

## §0. Frame

Phase 35 is **instrument-validation, not measurement** — nothing novel to discover in AM/Fibonacci spacing statistics (40 yr literature). The value-add: **AM is the first *non-synthetic* universality-transition substrate to validate `transition_diagnostic`** (Phase-20.5 blends are circular hand-tuned mixing weights; AM's λ=1 boundary is Avila–Jitomirskaya-*proven*). 35a is the prerequisite: it must hand 35b an honest NNS reference for the regimes 35b will read.

**Named honestly (the recurring error class, two levels deep now).** Rev 0 partitioned by *substrate type* what was a *resolution regime* and *asserted* an undrived NNS signature. Rev 1 fixed that but over-collapsed: "one Cantor family on AM" left the calibrator with **no analytic generator to synthetic-validate against** (AM-critical is conjectural/numerical) — a calibrator you cannot validate is the §D.0b silent-corruption surface by construction. Rev 2's discipline: **a calibrator must be derived on, and validated against, an operator that supplies a rigorous analytic ground truth.** Only the Fibonacci Hamiltonian does, for Cantor (DGY). Forcing AM-critical to be that operator would re-introduce the phantom *named but not eliminated* — the assumption "AM≈Fibonacci Cantor-NNS" would carry all the load while being precisely the unproven thing. So AM-critical is **not** a 35a calibrator; it is a **35b pre-specified empirical test** of exactly that cross-substrate universality — measured, never assumed (the project's test-don't-assume-cross-substrate-universality discipline).

## §1. Goals — two calibrators, two operators, one shared anchor

The two-operator structure is **mathematically forced, not a wart**: each class lands on the operator that gives it *both* an analytic anchor *and* the correct spectral type.

1. **PRIMARY (the real research content) — Class I: derive the Fibonacci-Hamiltonian IDS-unfolded Cantor-spectrum NNS** as a function of (V, N) — shape, small-spacing mass, tail — **explicitly separating the finite-N gap-stranding artifact** (eigenvalues stranded inside limiting-spectrum gaps by finite-size error, →0 as N→∞) **from the N→∞ behaviour.** No NNS signature is assumed; the asserted "atom at zero / multifractal tail" stays dropped (the stranding atom is an artifact to characterise and *exclude*, never a feature). Deriving the actual signature — analytically, or via a clean N→∞ extrapolation that isolates the artifact — is the task. The derivation is now *possible* (rigorous DGY-controlled base) but **not free** (the DOS-multifractal→NNS-shape map is still a real derivation step; §5).
2. **Class II: build the AM small-λ clock+band-perturbation AC calibrator**, anchored at the λ=0 free Laplacian. Forced onto AM: the AC spectral type exists *only* on AM. Ten Martini still binds — Class II is pinned by explicit **(λ,N) as a coarse-N / small-λ resolution corner**, *not* a substrate band-structure claim; rev 1's resolution-regime framing is carried into Class II's pinning (option 2 does **not** dissolve the Ten Martini constraint).
3. **Shared anchor:** AM λ=0 ≡ Fibonacci V=0 ≡ the free Laplacian. The two classes share *exactly* the zero-coupling point (free Laplacian, N-truncation eigenvalues 2cos(πk/(N+1)), arcsine-IDS → exact clock, zero variance) and diverge immediately above it.
4. **Generator-validation (Class I):** confirm the Fibonacci trace-map reproduces the DGY exact DOS multifractal exponents — validates the *generator*, distinct from validating the calibrator (§5).
5. Construct each calibrator **only after its ground truth exists** (Class I: after the §3 derivation; Class II: off the rigorous λ=0 anchor under pinned (λ,N)).

If the Class I derivation is analytically intractable and no clean N→∞ extrapolation isolates the artifact, 35a **halts** (`DERIVATION_INTRACTABLE_HALT`) and the AM arc does not proceed to 35b — an honest dead-end is a valid outcome.

## §2. Scope

**IN:** the Class I Fibonacci Cantor-NNS derivation (§3); the Class II AM small-λ AC calibrator + the shared free-Laplacian anchor (§4); DGY generator-validation (§5a); calibrator-validation *gated on* the derivation (§5b); verdict per §7.

**OUT (load-bearing):**
- **NOT** AM-critical (λ→1⁻, λ=1) *as a 35a calibrator* — it has no DGY-grade analytic control. It is the §8 35b pre-specified empirical test "does AM near λ→1⁻ land in the Fibonacci-built Cantor class"; 35a does **not** build an AM-critical-specific class.
- **NOT** AM measurement / the (θ,λ) sweep / the transition diagnostic — that is 35b, gated on 35a.
- **NOT** the λ=1 critical line *as a measured substrate* on the joint plane (f(α) singularity-spectrum territory — a different instrument; §7.ter.49 mode-A class).
- **NOT** a discovery/measurement cell — calibrator construction, never a result (asymmetric-label, METHODS §1).

**Corrections that must NOT be re-imported:**
- **Option 1 (derive on AM directly) is rejected:** no DGY-grade analytic ground truth on AM-critical ⇒ no §5-synthetic-validation possible; the flagged "AM≈Fib" assumption would do all the load-bearing work while being the unproven thing. Naming a phantom ≠ eliminating it.
- **Option 3 (cite an AM↔Fib universality bridge) is rejected at lit-lock:** no theorem at the required bar exists (see Lit-lock BAR); folklore-grade similarity = the §7.ter.48 error.
- **Ten Martini still binds:** AM is Cantor for all λ≠0; Class II's clock+band appearance is a coarse-N/small-λ *resolution corner*, not a substrate band-structure claim. Spectral-measure type (AC/SC/PP) is NNS-invisible *metadata within an operator*; it is **not** an intra-AM partition. It *is* what forces the Class I↔Class II operator choice (AC only on AM; SC/Cantor with DGY-control only on Fibonacci) — operator-level, not regime-level.
- **No asserted NNS signature.** No "atom at zero / multifractal tail / recover it." The finite-N stranding atom is an artifact to characterise and exclude (stamping it = §D.0b silent corruption).
- No regime is BCGNT-grade; supercritical AM Poisson is Bourgain–Goldstein/Jitomirskaya, **not** Minami (iid-only). Rigour anchors = the AM transition boundary (λ=1, AJ) and the Fibonacci DGY exponents — **not** regime-wise NNS theorems.
- Cocycle-over-irrational-rotation bridge kept (Avila one-frequency, AM only — analytic sampling function); "deformed-bucket = vary λ" scaffold stays killed.
- AM/Fibonacci are GOE-by-symmetry for bookkeeping, but no regime is Wigner; predictions are Fibonacci-Cantor (Class I, to be derived) / clock-rigid + AC-band-perturbation (Class II) / Poisson (supercritical AM, 35b only).

## §3. Class I — the Fibonacci-Hamiltonian Cantor-NNS derivation (35a's core)

- **Operator:** Fibonacci Hamiltonian, coupling V, truncation N (Sturmian potential = characteristic function of an interval sampled along the golden-mean orbit). Tridiagonal ⇒ cheap symmetric-tridiagonal eigensolve. Spectrum is purely singular-continuous, zero-measure (Cantor) for every V≠0 — lit-lock.
- **Why here and not AM:** DGY rigorously control the Fibonacci spectrum *and* its DOS multifractal exponents via Fibonacci-trace-map hyperbolicity on the Fricke–Vogt surface. AM-critical has no analog at that rigour. The calibrator must be derived where there is a rigorous base.
- **Unfolding is well-defined; the NNS is not known.** Unfold by the IDS via gap-labelling (IDS ∈ ℤ+αℤ on gaps, α = golden mean, explicitly computable). IDS-unfolding *erases* gaps (maps eigenvalues to ≈ uniform mean spacing, as GUE-by-semicircle / ζ-by-RvM); it does **not** atomise them. What the resulting NNS *is* — small-spacing mass, bulk shape, tail, and how each depends on (V,N), which features are finite-N stranding artifact vs N→∞ limit — **is underived. Deriving it is the task of this phase.**
- **The DOS→NNS step (the prior-turn 1b catch) does not vanish — it becomes tractable.** DGY hand over the rigorous *DOS* multifractal exponents; the IDS-unfolded *NNS* is a derived object *on top of* that. Rev 2's gain is that the derivation now proceeds from a **rigorous base with the DGY exponents as a consistency anchor**, instead of from a conjectural one. Plausible going in (NOT assumed): the unfolded NNS inherits multifractal-flavoured structure from the DOS multifractality, plus a finite-N stranding contribution near zero that must be *shown* to vanish with N; both to be established, not asserted.

## §4. Class II — the AM small-λ AC calibrator + the shared free-Laplacian anchor

- **Shared anchor (rigorous, exact):** λ=0 (AM) = V=0 (Fibonacci) = free Laplacian; N-truncation eigenvalues 2cos(πk/(N+1)); arcsine-IDS unfold → exactly equispaced (clock, spacing 1, zero variance). The unique non-Cantor point and the single shared point of the two classes.
- **Class II is forced onto AM:** the absolutely-continuous spectral type exists *only* for AM (subcritical, λ<1, diophantine θ); the Fibonacci Hamiltonian is purely singular-continuous / zero-measure for every V≠0 and has **no AC regime in principle**. A clock+band-perturbation AC calibrator therefore *cannot* be built on Fibonacci — the operator asymmetry of Class I (Fibonacci/Cantor/SC) vs Class II (AM/clock/AC) is mathematically forced.
- **Ten Martini still binds Class II (option 2 does not dissolve it).** AM is Cantor for all λ≠0, so "clock+band" at small λ is a **finite-N resolution corner** (Cantor gaps sub-1/N, unresolved), pinned by explicit (λ,N) — *not* a claim that subcritical AM is band-structured. Class II's deliverable is the controlled deformation off the λ=0 anchor across a pinned small-λ / coarse-N (λ,N) range; the AC spectral type is recorded as the metadata that *justifies the operator choice*, not as an NNS feature.
- **Pinning (open, to be fixed at execution):** the (λ,N) range for Class II must be pinned by an explicit analytical small-λ / coarse-resolution condition (subcritical AC proven λ<1 diophantine θ, with margin from the λ→1 duality), **not** by "where the NNS looks AC." This is the one genuinely under-pinned item rev 2 carries forward; resolve at execution-start, halt if it cannot be pinned principled-ly.

## §5. Validation discipline — generator vs calibrator, the two-step split

- **§5a Generator-validation (Class I, keep):** recover the DGY *exact multifractal exponents of the Fibonacci DOS/spectrum* from the trace-map truncations within tolerance. Validates that the **generator** reproduces the right spectrum. It does **NOT** validate the calibrator (the NNS is not the DOS f(α); the DOS→NNS map is the §3 derivation, not a checked identity).
- **§5b Calibrator-validation (gated, the clean two-step):**
  1. **Generator** is DGY-exponent-validated (§5a).
  2. The IDS-unfolded NNS **derived from that rigorous generator** (DGY exponents as consistency anchor) **is the calibrator ground truth** (the §3 deliverable).
  3. The empirical trace-map NNS is validated **against that derived ground truth**, judged under the **§7.ter.59 sample-size-floor discipline**: every distribution test read as `KS / (0.8687/√n)` vs its own N/depth, never raw KS, never a large-n p-value, validated at *realistic* N (the cohomological-H lesson, hard precondition). Both steps are doable; until §3 yields the ground truth, step 3 cannot run and nothing is stamped.
- **Class II validation:** controlled deformation off the rigorous λ=0 anchor; the calibrator NNS must vary continuously and predictably away from the exact-clock endpoint across the pinned (λ,N) corner, distinct from BL/TR/BR/TL.
- **Negative controls:** the derived Class I Fibonacci-Cantor NNS must be distinct from BL/TR/BR/TL, from the λ=0 clock, and from the Class II AC calibrator; the finite-N stranding artifact must be shown to shrink with N (if it does not, the "signature" is an artifact and the calibrator is rejected).

## §6. Pre-flight gates

- **Lit-lock** (incl. Ten Martini, Fibonacci spectral type, DGY/Fricke–Vogt hyperbolicity, and the **Lit-lock BAR**) before any build; halt on mismatch *or* on any AM↔Fib bridge that clears only the folklore bar.
- **Compute:** AM *and* Fibonacci operators are tridiagonal — symmetric-tridiagonal eigensolve (LAPACK `stev`/`stebz`) sub-second at N=10⁴; cost driver across the arc is the per-operator coupling × N-ladder × seed × surrogate combinatorics (Fibonacci N-ladder discrete). 35a is small except possibly the Class I N→∞ extrapolation (multiple N per V).
- **Corrections checklist** (§2) is a hard pre-flight; any reappearance halts.
- Use `/home/combust/fmexplorer/bin/python3` (venv).

## §7. Verdict vocabulary (asymmetric — calibrator construction, never a result)

- `FIB_CANTOR_NNS_SIGNATURE_DERIVED` — §3 yields a (V,N) Fibonacci NNS with the finite-N stranding artifact isolated and shown N→∞-vanishing.
- `GENERATOR_VALIDATED_VS_DGY_EXPONENTS` — §5a passes (generator, not calibrator).
- `FIB_CANTOR_CALIBRATOR_STAMPED` — derived NNS + generator-validated + §5b floor-anchored two-step match; Class I enters the zoo.
- `AM_AC_CALIBRATOR_STAMPED` — Class II built off the rigorous shared anchor under principled-ly pinned (λ,N); enters the zoo.
- `DERIVATION_INTRACTABLE_HALT` — §3 cannot be derived nor cleanly N→∞-extrapolated; **halt, do not stamp, AM arc does not proceed to 35b.** An honest dead-end.
- `CLASS_II_PINNING_INTRACTABLE_HALT` — §4 (λ,N) range cannot be pinned by a principled analytical condition; Class II not stamped.
- Cell-level: `PHASE35A_FAMILY_VALIDATED` (both classes) / `_PARTIAL` (one class) / `_HALT`. **Never** a discovery/measurement/AM-result verdict.

## §8. Forward / scope boundary

On `PHASE35A_FAMILY_VALIDATED` (Class I derived + generator-validated + floor-anchored; Class II anchored + pinned):
- **35b (separate brief, gated):** transition-diagnostic validation. Supercritical + λ→1⁻ only; golden-mean θ; Fibonacci-N-ladder. Right-null = the **α-ensemble** (cos(2π(θn+α)) phase is part of the operator; α-ensemble at fixed (θ,λ) is the substrate-generated null per §7.ter.48; non-circular), **localised-regime only**. **Pre-specified cross-substrate universality test (the option-2 deliverable to 35b):** *does AM near λ→1⁻ land in the Fibonacci-built Cantor calibrator class?* Both outcomes pre-specified and informative: **match** ⇒ earned cross-substrate Cantor-class universality (a real instrument-validation result, *measured not assumed*); **non-match** ⇒ AM-critical is its own object, would need an AM-critical-specific class built *without* DGY-grade control (35a did not, by design, attempt that). This is independent of, and additional to, the transition-diagnostic verdict map, which is pre-specified **both ways**: quadrant-flip (validates the diagnostic on a non-synthetic substrate) **and** sub-quadrant/rep_med-drift (the §7.ter.28 BGP precedent — diagnostic correctly returns null, evolution lives sub-quadrant).
- **35c (optional, contingent on 35b sub-quadrant outcome):** AM as the validation substrate for the Phase-22+ sub-quadrant-trajectory extension.
- λ=1 stays **out** of the whole arc as a measured substrate.

The arc validates `transition_diagnostic`; it is **not** AM/Fibonacci measurement and yields no spectral-physics result.

## §9. Methodological commitments

- Brief-first / compute-after; no execution without explicit Will go (brief-and-hold). A goals-changing revision returns to hold (line-4 logic).
- **"Well-defined operation" ≠ "known statistic"** (the §7.ter.59-class discipline at spectral resolution): a brief carries forward only what was actually *derived*; gap-labelling making the unfolding well-defined does not hand over its NNS. 35a's deliverable is the derivation; assertion is forbidden.
- **A calibrator must be derived on, and validated against, an operator with a rigorous analytic ground truth.** Where none exists (AM-critical), the cross-substrate transfer is *measured downstream* (35b), never assumed into the calibrator (the test-don't-assume-cross-substrate-universality discipline).
- **Operator-asymmetry is forced, not a wart:** each class on the operator giving it both an analytic anchor and the correct spectral type (Fibonacci→Cantor/SC; AM→clock/AC); state it as deliberate.
- Generator-validation and calibrator-validation are distinct gates; DGY validates the generator only; the DOS→NNS derivation is a separate, real, now-tractable step.
- Ten Martini = resolution-regime not substrate-partition (binds Class II pinning); spectral-measure type is operator-choice-forcing metadata, NNS-invisible within an operator.
- **§7.ter.48 surface-parallel discipline:** a cross-operator bridge must clear shared-NNS/shared-exponents, never "both are critical QP"; folklore similarity is the Möbius-family mistake one substrate up.
- Synthetic/derived-ground-truth validation judged against its own sample-size/regime floor at realistic N (§7.ter.55/57/59).
- §D.0b: a mis-derived, unvalidatable, or artifact-stamped calibrator is the silent-corruption surface — `_HALT` over stamp.

## §10. References / cross-refs

- Avila, Jitomirskaya — *The Ten Martini Problem* (Annals 2009): Cantor spectrum for all irrational θ, all λ≠0. **Binds Class II pinning.**
- Avila, Jitomirskaya — AM phase diagram (subcritical AC / critical SC / supercritical PP; proven λ=1 boundary). **AC exists only on AM.**
- Damanik, Gorodetski, Yessen — Fibonacci-Hamiltonian exact multifractal exponents + trace-map renormalisation via Fricke–Vogt-surface hyperbolicity (DOS/spectrum, **not** NNS; Fibonacci-specific). **Class I rigorous base.**
- Sütő / Bellissard–Iochum–Scoppola–Testard / Damanik — Fibonacci Hamiltonian: purely singular-continuous, zero-measure spectrum for all V≠0 (no AC regime ever). **Forces Class II off Fibonacci.**
- Johnson–Moser / Bellissard — gap-labelling (IDS ∈ ℤ+αℤ / ℤ+θℤ on gaps; unfolding well-defined, NNS not handed over).
- Avila — one-frequency analytic SL(2,ℝ) cocycles (AM analytic sampling function; the bucket↔AM bridge — AM only).
- Bourgain–Goldstein / Jitomirskaya — supercritical localisation (the non-Minami status of supercritical AM Poisson).
- Kohmoto–Ostlund-lineage — qualitative "critical QP share multifractal phenomenology" folklore; **explicitly below the lit-lock bar, not citable as a calibrator bridge.**
- Cross-ref: memory `phase35_am_arc_design`; METHODS.md §1; RESULTS §7.ter.59 (sample-size-floor), §7.ter.28 (BGP sub-quadrant), §7.ter.46 (zoo-extension precedes instrument-validation), §7.ter.48 (substrate-generated null / surface-parallel discipline), §7.ter.49 (mode-A), §7.ter.55/57 (validate-on-known-truth), §7.ter.5/22 (resolution-dependence).

---

End of brief — **rev 2: goals changed (two-operator-forced restructure); back to brief-and-hold, awaiting Will's final compute-go.** 35a authorized in principle; compute still requires an explicit go.

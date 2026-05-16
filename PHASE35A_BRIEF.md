# PHASE 35a BRIEF (rev 3 — 2026-05-16 — P1 resolved: Fibonacci NNS PRESERVES the renormalization log-periodicity)

## Build the renormalization-phase-indexed Fibonacci Cantor NNS calibrator + the AM small-λ AC calibrator, on the two operators each is mathematically forced onto (prerequisite for the Almost-Mathieu transition-diagnostic arc)

**Status:** Pre-execution. **BRIEF ONLY — brief-and-hold** (no code, no compute, no execution without explicit go). **Rev 3.** Rev 2's structure (forced two-operator: Class I Fibonacci-Cantor / Class II AM-small-λ-AC; §5 split; AM-critical→35b) stands. Rev 3 folds in **Will's P1 adjudication** (`PHASE35A_PRECOMPUTE_REVIEW.md`): the IDS-unfolded Fibonacci NNS **preserves** the trace-map renormalization log-periodicity, so Class I's signature is **not a single reference P(s)** but a **log-periodic family indexed by renormalization phase k mod L** (L = the trace-map cycle length DGY computes). This refines (does not reverse) rev 2's goals; the §7 verdict-map gap is closed. **One Class-II item (P3) remains open and is reserved for Will's adjudication — flagged in §4, not resolved here.** 35a authorized in principle; compute still requires an explicit go (and the P3 call). Decision record: memory `phase35_am_arc_design`; review trail: `PHASE35A_PRECOMPUTE_REVIEW.md`.

**Lit-lock (verify at execution start, BCGNT-style — cited, not yet independently verified):**
- Avila–Jitomirskaya **Ten Martini** — AM spectrum Cantor for *all* irrational θ, *all* λ≠0. Binds Class II's (λ,N) pinning (§4); does **not** make AM the Cantor calibrator.
- Avila–Jitomirskaya AM phase diagram — proven λ=1 boundary; subcritical **AC** (λ<1, dioph. θ) / critical SC / supercritical PP. **AC exists only on AM.**
- **Fibonacci Hamiltonian spectral type** — purely **singular-continuous, zero-measure (Cantor)** for **every** V≠0 (Sütő / BIST / Damanik). Fibonacci **never** has an AC regime ⇒ a clock+band-perturbation AC calibrator on Fibonacci is impossible *in principle*.
- Damanik–Gorodetski–Yessen — Fibonacci exact multifractal exponents from **hyperbolicity of the Fibonacci trace map on the Fricke–Vogt invariant surface** (Fibonacci-specific; the Harper/AM trace map is *not* that object). **The trace-map renormalization also computes the log-periodic cycle length L** (the period in the renormalization index) — load-bearing for §3/§5/§7.
- **Fibonacci renormalization log-periodicity** — documented: the trace map is a discrete renormalization applied once per Fibonacci level; since F_k ~ φ^k, observables carry a log-periodic-in-scale step-dependence (Jagannathan, *Rev. Mod. Phys.* 93, 045001 (2021), arXiv:2012.14744; Lifshitz–Even-Dar Mandel; Damanik–Gorodetski, *GAFA* 2012 — DOS measure exact-dimensional, local scaling < Hausdorff dim). **Load-bearing for the P1 resolution.**
- Gap-labelling (Johnson–Moser / Bellissard) — IDS ∈ ℤ+αℤ (Fib) / ℤ+θℤ (AM) on gaps — the *unfolding* well-defined (does **not** hand over the unfolded NNS).
- Avila one-frequency analytic SL(2,ℝ) cocycle theory — AM analytic cosine sampling; AM↔cocycle-over-rotation bridge (AM only; Fibonacci's sampling is discontinuous Sturmian — different QP regime/methods).
- **Lit-lock BAR (option-3's grave — load-bearing):** any "AM↔Fibonacci bridge" reference must clear **shared NNS / shared exponents**, *not* "both are critical QP." Exponents are not shared even within a family (V-dependent Fib / θ-dependent AM). Kohmoto–Ostlund "critical QP share multifractal phenomenology" is qualitative folklore, not BCGNT-grade; folklore-as-identity = the **§7.ter.48 error** (surface parallel ≠ structural identity — the Möbius-family mistake one substrate up). Halt on any bridge clearing only the folklore bar.

---

## §0. Frame

Phase 35 is **instrument-validation, not measurement** — nothing novel to discover in AM/Fibonacci spacing statistics (40 yr literature). Value-add: **AM is the first *non-synthetic* universality-transition substrate to validate `transition_diagnostic`** (Phase-20.5 blends are circular hand-tuned mixing weights; AM's λ=1 boundary is Avila–Jitomirskaya-*proven*). 35a is the prerequisite: it must hand 35b an honest NNS reference.

**Named honestly (the recurring error class, P1 instance — and why it is good news).** Rev 0 asserted an underived signature. Rev 1 over-collapsed (no analytic ground truth on AM-critical). Rev 2 fixed the operator but its §1/§3/§7 silently assumed the Class I NNS converges to *a single limit distribution* as N→∞. P1 (Will, adjudicated): **it does not — it preserves the renormalization log-periodicity.** "Well-defined operation ≠ known statistic," one level deeper still: the *unfolding* is well-defined; *whether it absorbs or preserves* the discrete scale invariance was the unknown; the answer is **preserves** — because unfolding (the probability-integral transform) uniformizes the DOS and so removes only the log-periodicity that is purely a *one-point-counting-density* feature; Fibonacci's log-periodicity is *renormalization-carried* (trace-map dynamics), which a one-time per-level scale normalization cannot touch. The signature is a **structured, finite-parameter, DGY-computed log-periodic cycle** — *more* tractable to calibrate than rev 0's unstructured "multifractal tail," and the surviving structure *is the DGY-controlled structure* (a further point for option 2). Good news, derived not asserted: the cycle and its period are to be *derived/confirmed against DGY*, never stamped.

## §1. Goals — two calibrators, two operators, one shared anchor

The two-operator structure is **mathematically forced** (each class on the operator giving it *both* an analytic anchor *and* the correct spectral type).

1. **PRIMARY — Class I: derive the Fibonacci-Hamiltonian IDS-unfolded Cantor NNS as a renormalization-phase-indexed log-periodic family** `P_k(s)`, k indexed by the trace-map renormalization step (truncation N = F_k), **periodic with period L = the trace-map cycle length DGY's renormalization computes** (k mod L). The deliverable is *the cycle* — the L phase-members and the confirmed period — **not** a single P(s). Within each phase, the finite-N gap-stranding artifact (eigenvalues stranded in limiting-spectrum gaps, →0 as N→∞ *along that phase's subsequence*) must be **isolated from the phase structure**, never conflated with it. No signature asserted; the asserted "atom at zero" stays dropped (stranding atom = artifact to characterise and *exclude*).
2. **Class II: build the AM small-λ clock+band-perturbation AC calibrator**, anchored at λ=0 free Laplacian. Forced onto AM (AC type exists only on AM). Ten Martini still binds — Class II pinned by explicit **(λ,N) as a coarse-N/small-λ resolution corner**, *not* a substrate band-structure claim. **(λ,N)-pinning is the open P3 item — see §4; reserved for Will.**
3. **Shared anchor:** AM λ=0 ≡ Fibonacci V=0 ≡ free Laplacian; N-truncation eigenvalues 2cos(πk/(N+1)); arcsine-IDS → exact clock (spacing 1, zero variance). The unique non-Cantor point; both classes share *exactly* it (including the unfolding) and diverge immediately above it.
4. **Generator-validation (Class I):** the Fibonacci trace-map reproduces the DGY exact DOS multifractal exponents — validates the *generator*, distinct from validating the calibrator (§5).
5. Construct each calibrator **only after its ground truth exists** (Class I: after §3 yields the confirmed cycle; Class II: off the rigorous λ=0 anchor under pinned (λ,N)).

If §3's cycle is analytically intractable and no clean extrapolation confirms the period, 35a **halts** (`DERIVATION_INTRACTABLE_HALT`) and the arc does not proceed to 35b — an honest dead-end is valid.

## §2. Scope

**IN:** the Class I renormalization-phase cycle derivation (§3); the Class II AM small-λ AC calibrator + shared anchor (§4); DGY generator-validation (§5a); cycle-validation gated on §3 (§5b); zoo representation (§5c); verdict per §7.

**OUT (load-bearing):**
- **NOT** AM-critical (λ→1⁻, λ=1) *as a 35a calibrator* — no DGY-grade control. It is the §8 35b pre-specified test ("does AM near λ→1⁻ land in the phase-appropriate member of the Fibonacci cycle"); 35a does **not** build an AM-critical class.
- **NOT** AM measurement / (θ,λ) sweep / the transition diagnostic — 35b, gated on 35a.
- **NOT** the λ=1 critical line as a measured substrate (f(α) singularity-spectrum / §7.ter.49 mode-A territory).
- **NOT** a discovery/measurement cell — calibrator construction, never a result (asymmetric-label, METHODS §1).

**Corrections that must NOT be re-imported:**
- **Single-limit framing is rejected (P1):** the Class I object is a log-periodic cycle, not a limit distribution; an N→∞ "extrapolation to a single P(s)" is the wrong target and would mis-stamp or false-HALT (§D.0b).
- **Option 1** (derive on AM directly): no DGY-grade ground truth on AM-critical ⇒ no §5-validation; rejected.
- **Option 3** (cite an AM↔Fib bridge): no theorem at the required bar; rejected at lit-lock (BAR).
- **Ten Martini still binds:** AM Cantor for all λ≠0; Class II's clock+band is a coarse-N/small-λ *resolution corner*, not a substrate-band claim. Spectral-measure type is operator-choice-forcing metadata (AC only on AM; SC/Cantor-with-DGY-control only on Fibonacci), NNS-invisible *within* an operator.
- **No asserted NNS signature**; stranding atom is artifact, characterise-and-exclude (§D.0b).
- No regime is BCGNT-grade; supercritical AM Poisson is Bourgain–Goldstein/Jitomirskaya, not Minami. Rigour anchors = AM λ=1 boundary (AJ) and the Fibonacci DGY exponents *and the DGY-computed cycle length L* — not regime-wise NNS theorems.
- Cocycle-over-rotation bridge kept (Avila, AM only); "deformed-bucket = vary λ" stays killed.

## §3. Class I — the Fibonacci renormalization-phase NNS cycle (35a's core)

- **Operator:** Fibonacci Hamiltonian, coupling V, truncation N = F_k (Sturmian potential along the golden-mean orbit). Tridiagonal ⇒ cheap symmetric-tridiagonal eigensolve. Purely singular-continuous, zero-measure (Cantor) for every V≠0 (lit-lock).
- **Why here, not AM:** DGY rigorously control the Fibonacci spectrum, its DOS multifractal exponents, *and the trace-map renormalization period L*. AM-critical has no analog at that rigour.
- **The P1 mechanism (encode exactly).** Unfold by the IDS via gap-labelling (IDS ∈ ℤ+αℤ on gaps, α golden mean, explicitly computable). IDS-unfolding is the **probability-integral transform**: it uniformizes the DOS measure, so it absorbs *only* log-periodicity carried by the one-point counting density (gone by construction). It **cannot** absorb log-periodicity carried by the **renormalization itself**. Fibonacci's is the latter: the trace map is a discrete renormalization applied **once per Fibonacci level**; observables carry that discrete-step dependence; since F_k ~ φ^k, step-dependence **is** log-periodicity in scale. Unfolding is a one-time per-level scale normalization — it removes the absolute scale, **not** the trace-map dynamics. ⟹ **the IDS-unfolded NNS shape itself varies log-periodically with the truncation index F_k.**
- **The deliverable is the cycle.** `P_k(s)` is periodic in k with period **L = the trace-map cycle length DGY computes**. §3 derives/identifies L (from the trace-map renormalization, the DGY-controlled object) and the L phase-members, separating *within each phase* the finite-N stranding contribution (must →0 along that phase's F_k subsequence) from the phase structure (the non-artifact, log-periodic signal). Plausible going in (NOT assumed): each phase-member inherits multifractal-flavoured structure from the DOS multifractality; the cycle length and member shapes are *derived and DGY-cross-checked*, not asserted.

## §4. Class II — the AM small-λ AC calibrator + the shared free-Laplacian anchor

- **Shared anchor (rigorous, exact):** λ=0 (AM) = V=0 (Fibonacci) = free Laplacian; eigenvalues 2cos(πk/(N+1)); arcsine-IDS → exactly equispaced clock (spacing 1, zero variance). Unique non-Cantor point; the single shared point of both classes, unfolding included.
- **Class II forced onto AM:** AC spectral type exists only for AM (subcritical, λ<1, dioph. θ); Fibonacci is purely SC / zero-measure for every V≠0 — no AC regime in principle. The operator asymmetry (Class I Fib/Cantor/SC vs Class II AM/clock/AC) is mathematically forced, not a wart.
- **Ten Martini still binds:** AM Cantor for all λ≠0, so "clock+band" at small λ is a **finite-N resolution corner** (Cantor gaps sub-1/N, unresolved), pinned by explicit (λ,N) — *not* a claim subcritical AM is band-structured. Class II's deliverable is the controlled deformation off the λ=0 anchor across the pinned corner.
- **OPEN — P3, reserved for Will's adjudication (not resolved in rev 3).** `PHASE35A_PRECOMPUTE_REVIEW.md` P3: the (λ,N) pinning is **not a free parameter choice** — Class II is rigorous *only* where finite N has provably **not yet resolved** the (exponentially-small-in-1/λ) Cantor gaps; the instant (λ,N) crosses into resolved-Cantor, the object *is* AM-Cantor NNS, which has **no DGY-grade ground truth** (exactly why option 1 was killed). So the proposed pinning condition is a **hard gap-scale-vs-1/N inequality with `CLASS_II_PINNING_INTRACTABLE_HALT` at the boundary (option-1 territory), not a soft edge.** This framing is *proposed* by the review; **Will to adjudicate whether Class II is pinned this way or scoped differently** before any compute-go. Until adjudicated, Class II is `_HELD`.

## §5. Validation discipline — generator vs calibrator; validate the *cycle*, not a fixed distribution

- **§5a Generator-validation (Class I):** recover the DGY *exact multifractal exponents of the Fibonacci DOS/spectrum* from the trace-map truncations within tolerance. Validates the **generator**. Does **not** validate the calibrator (the NNS cycle is not the DOS f(α); the DOS→NNS-cycle is the §3 derivation).
- **§5b Calibrator(cycle)-validation (gated on §3) — validate the CYCLE:**
  1. **Generator** DGY-exponent-validated (§5a).
  2. **Sample consecutive F_k across ≥ 2 full renormalization periods** (≥ 2L members). **Confirm (i) periodicity** in k, **(ii) the empirical period equals L = the DGY-trace-map-computed cycle length** (this DGY-derived period is the *independent external anchor* — it is what gives §5b teeth beyond self-consistency; addresses review P2: a self-consistent-but-wrong derivation fails the period match), **(iii) within each phase the finite-N stranding artifact shrinks along that phase's F_k subsequence** and does not masquerade as cycle structure.
  3. Each distribution comparison judged under the **§7.ter.59 sample-size-floor discipline**: `KS / (0.8687/√n)` vs its own n, never raw KS, never a large-n p-value, validated at *realistic* n. Until §3 yields L + members, §5b cannot run; nothing is stamped.
- **Class II validation (gated on P3 adjudication):** controlled deformation off the rigorous λ=0 anchor; NNS varies continuously/predictably away from the exact clock across the (adjudicated) pinned corner; distinct from BL/TR/BR/TL and from the Class I cycle members.
- **Negative controls:** Class I cycle-members distinct from BL/TR/BR/TL, from the λ=0 clock, and from Class II; an empirical period ≠ DGY-computed L is a silent-corruption surface ⇒ HALT (§7), not a stamp.

## §5c. Zoo representation (review P4 — resolved by the cycle being finite)

The cycle is a **finite** object (L phase-members, L = DGY-computed). It maps cleanly onto the existing fixed-N `(name, gen_fn)` zoo idiom (`calibrator_panel.py`): **L named phase-members** `fib_cantor_V*_phase{0..L-1}` + the **shared `free_laplacian_clock` anchor** + (post-P3) the Class II member(s). The zoo/`transition_diagnostic` **selects the phase-appropriate member** for comparison (the renormalization phase is computable from the substrate's effective truncation index). No parametric-family interface extension is required — the finiteness of L is what dissolves review P4. (If §3 finds L impractically large, that is itself a `DERIVATION_INTRACTABLE_HALT` signal, not an interface problem.)

## §6. Pre-flight gates

- **Lit-lock** (Ten Martini; Fibonacci spectral type; DGY/Fricke–Vogt hyperbolicity **incl. the trace-map cycle length L**; renormalization log-periodicity refs; AJ phase diagram; gap-labelling; Avila cocycle; **the BAR**) before any build; halt on mismatch or on any AM↔Fib bridge clearing only the folklore bar.
- **P3 adjudicated** (Class II pinning) — a hard pre-flight; Class II stays `_HELD` until then.
- **Compute:** AM and Fibonacci both tridiagonal — symmetric-tridiagonal eigensolve (LAPACK `stev`/`stebz`) sub-second at N=10⁴; cost driver = per-operator coupling × the F_k ladder (≥2L members) × seed × surrogate combinatorics. Still small.
- **Corrections checklist** (§2) is a hard pre-flight; any reappearance (esp. single-limit framing) halts.
- Use `/home/combust/fmexplorer/bin/python3` (venv).

## §7. Verdict vocabulary (asymmetric — calibrator construction, never a result)

- `FIB_CANTOR_NNS_RENORM_PHASE_FAMILY_DERIVED` — §3 yields the L-member cycle, period **confirmed = DGY-computed L**, finite-N stranding isolated within each phase. *(Replaces rev 2's single-limit `..._SIGNATURE_DERIVED`; closes the §D.0b mis-stamp/false-HALT gap.)*
- `GENERATOR_VALIDATED_VS_DGY_EXPONENTS` — §5a passes (generator, not calibrator).
- `FIB_CANTOR_CYCLE_CALIBRATOR_STAMPED` — derived cycle + generator-validated + §5b floor-anchored period/phase match; the L phase-members + shared anchor enter the zoo (§5c).
- `AM_AC_CALIBRATOR_STAMPED` — Class II built off the rigorous anchor under Will-adjudicated (P3) pinned (λ,N).
- `CYCLE_PERIOD_MISMATCH_HALT` — empirical period ≠ DGY-computed L: silent-corruption surface, **HALT not stamp** (§D.0b).
- `DERIVATION_INTRACTABLE_HALT` — cycle/period cannot be derived nor cleanly confirmed (incl. L impractically large); **halt; arc does not proceed to 35b.** Honest dead-end.
- `CLASS_II_PINNING_INTRACTABLE_HALT` — §4 (P3) condition unpinnable post-adjudication; Class II not stamped.
- Cell-level: `PHASE35A_FAMILY_VALIDATED` (both) / `_PARTIAL` (Class I cycle only; Class II `_HELD`/`_HALT`) / `_HALT`. **Never** a discovery/measurement/AM-result verdict.

## §8. Forward / scope boundary

On `PHASE35A_FAMILY_VALIDATED` (Class I cycle derived + generator-validated + period/phase floor-anchored; Class II anchored + P3-pinned):
- **35b (separate brief, gated):** transition-diagnostic validation. Supercritical + λ→1⁻ only; golden-mean θ; Fibonacci-F_k ladder. Right-null = the **α-ensemble** (cos(2π(θn+α)) phase is part of the operator; α-ensemble at fixed (θ,λ) is the substrate-generated null per §7.ter.48; non-circular), **localised-regime only**. **Pre-specified cross-substrate test:** *does AM near λ→1⁻ land in the phase-appropriate member of the Fibonacci renormalization cycle?* Both outcomes pre-specified: **match** ⇒ earned cross-substrate Cantor-class universality (measured, not assumed); **non-match** ⇒ AM-critical is its own object (35a, by design, did not build it). Independent of, and additional to, the transition-diagnostic verdict map, pre-specified **both ways**: quadrant-flip (validates the diagnostic on a non-synthetic substrate) **and** sub-quadrant/rep_med-drift (§7.ter.28 BGP precedent — diagnostic correctly returns null, evolution lives sub-quadrant).
- **35c (optional, contingent on 35b sub-quadrant outcome):** AM as the validation substrate for the Phase-22+ sub-quadrant-trajectory extension.
- λ=1 stays **out** of the whole arc as a measured substrate.

The arc validates `transition_diagnostic`; it is **not** AM/Fibonacci measurement and yields no spectral-physics result.

## §9. Methodological commitments

- Brief-first / compute-after; no execution without explicit Will go (brief-and-hold). A goals-changing revision returns to hold (line-4 logic); a goals-*refining* one (rev 3) stays held pending the explicit go + open P3.
- **"Well-defined operation" ≠ "known statistic," recursively:** the unfolding is well-defined; *whether it absorbs or preserves* the discrete scale invariance was the unknown; resolved (P1) to **preserves**, because unfolding uniformizes only the 1-point density and Fibonacci's log-periodicity is renormalization-carried. A brief carries forward only what is *derived*; the cycle/period are derived-and-DGY-cross-checked, never asserted.
- **A calibrator must be derived on, and validated against, an operator with a rigorous analytic ground truth.** The surviving Class I structure *is* the DGY-controlled structure (the cycle length is what DGY's trace-map renormalization computes). Where no such truth exists (AM-critical), the cross-substrate transfer is *measured downstream* (35b), never assumed.
- **Validate the cycle, not a fixed distribution:** §5b confirms periodicity + the DGY-computed period (the independent anchor); the zoo compares the phase-appropriate member.
- **Operator-asymmetry is forced, not a wart.** Ten Martini = resolution-regime not substrate-partition (binds Class II). Spectral-measure type is operator-choice-forcing metadata.
- **§7.ter.48 surface-parallel discipline:** a cross-operator bridge must clear shared-NNS/shared-exponents, never "both are critical QP."
- Synthetic/derived-ground-truth validation judged against its own sample-size/regime floor at realistic n (§7.ter.55/57/59).
- §D.0b: a mis-derived, period-mismatched, unvalidatable, or artifact-stamped calibrator is the silent-corruption surface — `_HALT` over stamp.
- **P3 (Class II pinning) is reserved for Will; Class II is `_HELD` until adjudicated.** Not silently resolved by the brief.

## §10. References / cross-refs

- Avila, Jitomirskaya — *The Ten Martini Problem* (Annals 2009). **Binds Class II pinning.**
- Avila, Jitomirskaya — AM phase diagram (subcritical AC / critical SC / supercritical PP; proven λ=1 boundary). **AC only on AM.**
- Damanik, Gorodetski, Yessen — Fibonacci exact multifractal exponents + trace-map renormalisation via Fricke–Vogt-surface hyperbolicity (DOS/spectrum; **also computes the cycle length L**). **Class I rigorous base.**
- Sütő / Bellissard–Iochum–Scoppola–Testard / Damanik — Fibonacci: purely singular-continuous, zero-measure for all V≠0 (no AC regime). **Forces Class II off Fibonacci.**
- Jagannathan, *Rev. Mod. Phys.* 93, 045001 (2021) (arXiv:2012.14744); Lifshitz–Even-Dar Mandel; Damanik–Gorodetski, *GAFA* (2012) — **Fibonacci renormalization log-periodicity / discrete scale invariance; the P1 resolution.**
- Johnson–Moser / Bellissard — gap-labelling (IDS ∈ ℤ+αℤ / ℤ+θℤ on gaps; unfolding well-defined, NNS not handed over).
- Avila — one-frequency analytic SL(2,ℝ) cocycles (AM analytic sampling; AM only).
- Bourgain–Goldstein / Jitomirskaya — supercritical localisation (non-Minami status of supercritical AM Poisson).
- Kohmoto–Ostlund-lineage — qualitative "critical QP share multifractal phenomenology" folklore; **below the lit-lock bar, not citable as a calibrator bridge.**
- Cross-ref: memory `phase35_am_arc_design`; `PHASE35A_PRECOMPUTE_REVIEW.md`; METHODS.md §1; RESULTS §7.ter.59 (sample-size-floor), §7.ter.52 (bulk vs global-moment readout), §7.ter.28 (BGP sub-quadrant), §7.ter.46 (zoo-extension precedes instrument-validation), §7.ter.48 (substrate-generated null / surface-parallel discipline), §7.ter.49 (mode-A), §7.ter.55/57 (validate-on-known-truth), §7.ter.5/22 (resolution-dependence).

---

End of brief — **rev 3: P1 resolved (preserves ⇒ log-periodic renormalization-phase cycle, DGY-computed period); review P2/P4 folded in; Class II P3 reserved for Will.** Back to **brief-and-hold**; compute requires (1) Will's P3 adjudication and (2) an explicit compute-go.

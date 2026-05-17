# PHASE 35a BRIEF (rev 4 — 2026-05-16 — the heavier-branch revision; certified-scoping outcome folded in)
## Build the AM-side calibrator the certified zoo gap demonstrates 35b needs — generative model deferred to §3, acceptance target re-specified by the certified grid

**Status:** Pre-execution. **BRIEF ONLY — brief-and-hold.** Rev 4 is "the heavier-branch revision" Will has been calling *rev-3 sequencing*. It **supersedes the committed rev-3** (8a82346), which was written on the since-**walked-back** P1 "preserves ⇒ log-periodic renorm-phase cycle" answer; that framing is **not** carried forward as settled (P1 is back to *underived, all branches live*, folded into §3). Rev 4 folds in the **certified scoping campaign** (`phase35a/UNFOLDING_INVARIANCE_FINDINGS.md`; `PHASE35A_PRECOMPUTE_REVIEW.md`) and Will's Q-i/Q-ii/Q-iii adjudication (2026-05-16). Decision record: memory `phase35_am_arc_design`. Compute on 35a still requires an explicit go; the Q-iii scoped sub-task additionally requires sign-off on its **pre-registered threshold rule** (below).

**What the certified scoping settled — and its ceiling (load-bearing frame).** The scoping instrument is now **certified on known truth** (gates A clock / B Poisson / C-absorb + C-plateau all pass; the prior KS-to-δ degeneracy and un-gated IDS leg are repaired). On that certified instrument:
- **The Poisson/descope reading is dead** — reconfirmed, not merely by leg-divergence: the supercritical "BL/Poisson" was the deg-poly variance-exploding (monotone-in-N) Reading-2 artifact; the certified IDS leg shows AM across the **entire 35b grid** (supercritical λ→1⁺ *and* subcritical small-λ) is **low-variance, repulsive, NOT Poisson, NOT clock**.
- The classifier returns **BR_artifact**, which (Will, Q-i) is **neither recognition nor mis-fit** — it is the certified classifier **correctly declining**: reporting that AM falls **outside the zoo's calibrated class set**. That is the correct disciplined output, and it **positively demonstrates a zoo gap**.
- **Ceiling:** a scoping grid can demonstrate the *gap*; it **cannot** decide that a dedicated calibrator *must* be built (a research-scope call), nor *which* model fills it, nor *what AM's NNS is*. "Nearest-Wigner among {clock,Wigner,Poisson}" is a bounded phenomenology, **not** "AM is GUE" (the instrument itself respects this — it declined to TR). The grid killed the false reading, bounded the phenomenology, and demonstrated the gap. That is the structural limit of scoping. Everything past it is **§3**.

**Lit-lock (verify at execution start, BCGNT-style — cited, not yet independently verified):** unchanged from rev 2/3 and still load-bearing — Avila–Jitomirskaya Ten Martini (binds Class-II resolution-regime, see §4); AJ phase diagram (AC only on AM; proven λ=1 boundary); Fibonacci spectral type (purely SC/zero-measure ∀V≠0; no AC regime — forces the two-operator split); DGY exact multifractal exponents + Fricke–Vogt-surface trace-map hyperbolicity (Fibonacci-specific); gap-labelling (IDS ∈ ℤ+αℤ / ℤ+θℤ); Avila one-frequency analytic cocycle (AM only). **Lit-lock BAR (option-3's grave, still binding):** any AM↔Fibonacci bridge must clear *shared NNS / shared exponents*, never "both critical QP"; folklore-as-identity = the §7.ter.48 error. **This BAR is now operative content, not abstract:** §3 must decide whether AM's demonstrated-gap object *is* the Fibonacci-Cantor class **without assuming the bridge**.

---

## §0. Frame

Phase 35 validates `transition_diagnostic` on AM (35b) — the first non-synthetic universality-transition substrate. 35a is the prerequisite: hand 35b a zoo that **recognizes** AM's regimes instead of correctly-declining them. The certified campaign converted "does 35b need a new calibrator?" from speculation into a **positively-demonstrated zoo gap**: on a certified instrument the zoo has *no class* for AM's 35b-grid NNS. 35a's job is now concretely motivated and concretely bounded.

**Named honestly (the recurring error class — this turn's instance).** Rev 3 enshrined Will's "preserves" *hypothesis* as the §3 framing (a renorm-phase cycle, asserted). He walked it back: hypothesis dressed as conclusion — the exact assert-not-derive failure the arc exists to prevent, committed one turn after we named it. Rev 4's discipline: the certified grid **re-specifies what the calibrator must reproduce** (its acceptance target) but **leaves the generative model open**; a *phenomenological description* ("low-variance, repulsive, drifts off clock with N") is **not** a generative model and must not occupy the calibrator's slot. The generative model is §3, to be derived, never asserted.

## §1. Goals — restated against the certified outcome

The two-operator forced structure stands (Class I = Fibonacci Hamiltonian, the only DGY-controlled Cantor object; Class II = AM, the only operator with an AC regime; shared free-Laplacian anchor at zero coupling; operator-asymmetry mathematically forced — §4). What the campaign changed:

1. **The demonstrated deliverable (new, certified):** the zoo needs a calibrator for the object AM presents across the 35b grid — *certified* low-variance, repulsive, non-Poisson, non-clock, currently correctly-declined (BR_artifact). This is a **positively-demonstrated zoo gap**, not a precaution.
2. **Class I status — upgraded, bounded (Will, Q-i):** from "precautionary guard" (rev-3, retained only because the descope evidence was invalidated) to **"live candidate, motivated by a positively-demonstrated zoo gap."** A real upgrade — the certified grid added something. It stops **strictly short** of "class I specifically is demonstrated-necessary": whether the gap is filled by class I (Fibonacci-Cantor, *requiring the lit-lock-BAR'd universality bridge — to be derived, not assumed*) or by an AM-specific extended Class II is **§3 content**, not scoping-decidable.
3. **PRIMARY (§3, the new critical path): derive what AM's irrational-θ NNS on the 35b grid actually is** — the generative model — among the candidate models:
   - (A) it *is* the Fibonacci-Cantor class (⇒ class I fills the gap), admissible **only** if the AM↔Fibonacci shared-NNS bridge is *derived* past the lit-lock BAR (§7.ter.48 — not assumed);
   - (B) it is an **AM-specific AC-with-repulsive-fine-structure** object (⇒ an extended Class II with its own generative model).
   §3 simultaneously answers Q-i (which calibrator) and Q-ii (the generative model). P1 ("preserves" vs absorbed; single-limit vs renorm-periodic) is **underived, all branches live**, and lives **inside** §3's class-I branch — not asserted anywhere in this brief.
4. **Acceptance target re-specified (Will, Q-ii):** whatever §3's generative model, the Class-II / gap calibrator **must reproduce the certified drift-with-N** (W1δ-to-clock grows with N at fixed λ: e.g. λ=0.10 → 0.013/0.039/0.113 at N=377/2584/6765). The **static perturbed-clock premise is dropped** (a fixed deformation of a clock cannot produce drift-with-N). Precision (Will): the premise's defect is **not** "predicts no drift" (a genuine perturbed clock at rising resolution would also drift) — it is **presupposing a generator ("clock + small correction") that §3 has not derived and that may be wrong.**
5. If §3 is intractable / no admissible generative model survives the BAR → `DERIVATION_INTRACTABLE_HALT`; the arc does not reach 35b. Honest dead-end remains valid.

## §2. Scope

**IN:** §3 generative-model derivation (the critical path); §4 Class-II re-specification + shared anchor + Ten-Martini binding; §5 validation discipline (generator vs calibrator, two-step, §7.ter.59 floor); §5c zoo representation (deferred per P4); §Q3 the parallel scoped HALT-extraction sub-task (pre-registered, gated on threshold-rule sign-off); verdict per §7.

**OUT (load-bearing):** AM-critical λ=1 as a measured substrate (§7.ter.49 mode-A); AM measurement / the (θ,λ) sweep / the diagnostic itself (35b); a discovery/measurement cell (asymmetric label, METHODS §1). **Not re-importable:** option 1 (derive-on-AM, no DGY truth); option 3 (cite an AM↔Fib bridge — fails the BAR); the single-limit framing of P1 as settled; the **static perturbed-clock Class-II premise** (now dropped); a *phenomenological description* used as a generative model.

## §3. PRIMARY — the generative-model derivation (the new critical path)

The certified campaign fixed the *acceptance target* and demonstrated the *gap*; §3 is the irreducible research content the scoping ceiling hands up. Deliver the **generative model** for AM's irrational-θ NNS on the 35b grid, deciding between candidate models (A) Fibonacci-Cantor (admissible only with a BAR-passing derived bridge) and (B) AM-specific AC-with-repulsive-fine-structure, isolating finite-N stranding from the N→∞ / renormalization structure, **deriving** (never asserting) which model holds and its samplable generator. P1's single-limit-vs-renorm-periodic question is internal to model (A) and is itself to be derived here. Gate on the lit-lock BAR throughout: a Fibonacci↔AM identification is a *result of §3*, not an input. `DERIVATION_INTRACTABLE_HALT` if no BAR-admissible samplable generator survives.

## §4. Class II — re-specified; shared anchor; Ten Martini still binds

- **Shared anchor unchanged:** AM λ=0 ≡ Fibonacci V=0 ≡ free Laplacian; arcsine-IDS → exact clock (Gate A certified: var=0, W1δ=0). The unique non-Cantor point; the single shared point.
- **Premise dropped, target re-specified:** Class II is **no longer** "exact clock + static λ-deformation." Its **acceptance target** is the certified phenomenology: low-variance, repulsive, non-Poisson, non-clock, **W1δ-drift-with-N**, with subcritical small-λ markedly closer to clock than supercritical (certified ids W1δ ≈ 0.04 vs ≈ 0.26 at N=2584). The **generative model is §3**, not this brief.
- **Ten Martini still binds:** AM is Cantor ∀λ≠0; the small-λ near-clock corner is a **resolution regime**, pinned by explicit (λ,N), not a substrate-band claim. The drift-with-N *is* the resolution crossover — which §Q3 turns into the HALT boundary.

## §Q3. Parallel scoped sub-task — HALT extraction (does NOT need §3; interpretation does)

Will (Q-iii): extracting P3's HALT is the right next scoped step, **but not "read it off the trend."** This sub-task is brief-and-hold compatible (a statement about *instrument validity*, not AM's nature) and runs **in parallel** with §3; its **interpretation waits on §3**. Two hard requirements, written into the sub-spec **before any run**:

1. **Pre-registered, principled threshold rule (not a fitted number).** The W1δ-to-clock crossover is *continuous* — declaring a HALT requires a threshold W1δ\*, and it must be a **rule fixed and reviewed before the extraction runs**, tied to an instrument-meaningful event, e.g. **either** (a) the (λ,N) locus where the certified classifier verdict flips out of the clock-rigid label, **or** (b) the locus where AM becomes statistically distinguishable from the exact clock at the instrument's own resolution on the **§7.ter.59 floor** (W1δ\* set by the floor at that n, not chosen). The rule is pre-registered in the sub-spec; **no post-hoc fit.**
2. **Analytic cross-check against P3's criterion:** the empirical (λ,N) HALT boundary vs the perturbative **λ^|k| gap-width vs 1/N** resolution criterion. **Agree → doubly-certified HALT.** **Disagree → itself a finding** (either the W1δ trend is not tracking Cantor resolution, or perturbative scaling fails here) — a real falsification opportunity, recorded, not smoothed.

**Pre-registration discipline (load-bearing):** if the threshold rule is both authored and executed in one unreviewed step, pre-registration is hollow. **§Q3 holds for Will's explicit sign-off on the threshold *rule* (not a number) before it runs.** This session has been bitten four times by loosely-specified metrics (deg-11, KS-to-δ, the plateau-locator, the van-Hove gap count); the threshold gets the same discipline.

## §5. Validation discipline (unchanged in principle; gated on §3)

Generator-validation (DGY exponents) vs calibrator-validation remain distinct gates; the calibrator's ground truth exists only once §3 yields the generative model; every distribution test read as `KS/(0.8687/√n)` vs its own n on the §7.ter.59 floor, validated at realistic n; a self-consistent-but-wrong derivation is closed only by an independent derived f(α)→NNS-feature relation (the P2 root, folded into §3, not a separate patch). §D.0b: mis-derived / unvalidatable / target-missing calibrator ⇒ `_HALT` over stamp.

## §5c. Zoo representation — DEFERRED (P4, Will)

P4 stays deferred: premature infra for a need whose shape is §3-contingent. Decide the zoo representation **after** §3 fixes the generative model (finite phase-set vs parametric family vs single representative). Not in rev-4 scope.

## §6 / §7. Pre-flight & verdict vocabulary

Pre-flight: lit-lock incl. the operative BAR; **§Q3 threshold-rule sign-off**; corrections checklist (no single-limit-as-settled, no perturbed-clock premise, no phenomenology-as-generator, no option 1/3). Verdict (asymmetric, calibrator construction never a result): `GENERATIVE_MODEL_DERIVED_{FIB_CANTOR_BRIDGE|AM_SPECIFIC}` (BAR-passed) ; `ZOO_GAP_CALIBRATOR_STAMPED` (model + generator-validated + §7.ter.59-floor target-match incl. drift-with-N) ; `HALT_BOUNDARY_DOUBLY_CERTIFIED` / `_DISAGREEMENT_FINDING` (§Q3) ; `DERIVATION_INTRACTABLE_HALT` ; `CLASS_II_*_HALT`. Cell: `PHASE35A_*_VALIDATED/_PARTIAL/_HALT`. The certified scoping verdict on record is **"demonstrated zoo gap," not "AM characterized."**

## §8. Sequencing (updated — Will)

- **Instrument re-gating: DONE.** Last turn's upstream blocker is cleared (instrument certified).
- **New critical path: §3** — gates Q-i (which calibrator) and Q-ii (the generative model).
- **§Q3 (HALT extraction): parallel** — does not need §3; sub-spec (pre-registered rule + analytic cross-check) written here; **holds for threshold-rule sign-off**; its *interpretation* waits on §3.
- **P4: deferred.** **Class I:** live candidate (demonstrated gap), not precautionary, not demonstrated-necessary. Brief-and-hold; explicit go required for 35a; separate sign-off for §Q3's rule.
- 35b unchanged downstream (α-ensemble right-null; supercritical + λ→1⁻; the cross-substrate-universality test is now sharpened: it is the *empirical* side of §3's BAR-gated (A)-vs-(B) decision).

## §9. Methodological commitments

Brief-first/compute-after; explicit-go; goals-refining revision returns to hold. **A phenomenological description is not a generative model** (this turn's named lesson). **"Demonstrated gap" ≠ "calibrator must be built" ≠ "which calibrator"** — three distinct claims; scoping reaches only the first. The certified instrument **correctly declining** (BR_artifact) is a *disciplined output*, not a failure. Pre-registration is hollow if authored-and-run unreviewed (§Q3). Lit-lock BAR is operative, not abstract: a Fibonacci↔AM identification is a §3 *result*, never an input (§7.ter.48). P1 underived; assertion forbidden. §7.ter.59 floor on every distribution test. §D.0b: `_HALT` over stamp.

## §10. References / cross-refs

Unchanged set (Ten Martini; AJ phase diagram; DGY/Fricke–Vogt; Fibonacci spectral type; gap-labelling; Avila cocycle; Bourgain–Goldstein/Jitomirskaya; Kohmoto–Ostlund as *below* the BAR). Add: `phase35a/UNFOLDING_INVARIANCE_FINDINGS.md`, `regated_instrument_results.json`, `PHASE35A_PRECOMPUTE_REVIEW.md` (certified-scoping record). RESULTS §7.ter.59 (floor), §7.ter.55/57 (validate-on-known-truth — the gate discipline this campaign embodied), §7.ter.52 / [[bulk_vs_global_moment_readout]], §7.ter.48 (surface-parallel / the operative BAR), §7.ter.49 (mode-A), §7.ter.5/22 (resolution-dependence — the drift-with-N / HALT). Decision record: memory `phase35_am_arc_design`.

---

End of brief — **rev 4 (the heavier-branch revision): descope dead on a certified instrument; class I = live candidate via a positively-demonstrated zoo gap; static perturbed-clock premise dropped, acceptance target re-specified (drift-with-N), generative model = §3 (the new critical path, BAR-gated); §Q3 HALT-extraction parallel, holds for threshold-rule sign-off; P4 deferred; instrument re-gating done.** Brief-and-hold; the scoping verdict on record is "demonstrated gap," not "AM characterized."

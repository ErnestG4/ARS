# PHASE 35 SLICING-COMPARISON — SLATE UNIT 2: NUMBERS + G1b-CAMPAIGN SPEC (DRAFT)

**Status:** **SIGNED OFF (Will, 2026-05-19).** rev 3 = post-sign-off
campaign-spec finalization, two riders folded (sharpening, not
re-opens; no numeric-constant changes; everything else holds): **§A** —
the per-rung monotonicity call requires N-density sufficient for a
*reliable* verdict (reliability criterion is fixed structure; exact
N-count proposed-not-fixed), and an **ambiguous rung defaults to
G1b-conditional** (conservative). **§D** — the **terminal** is
separated from the **membership consequence**: COLLAPSE is reserved for
*positive shared-root evidence only* (not a catch-all — that would be
the §Q3 "slow-convergence ≠ divergence" honest-terminal violation);
every "couldn't determine", including independence-shown-but-
transfer-not-established, routes to ROOT_INDETERMINATE; the conservative
default lives on T1′'s *membership*, not on the COLLAPSE label.
(rev-1: structural draft on explicit go after the rev-3 §4 cut;
rev-2: Will's two pre-sign-off flags folded.) Slate unit 2 of the staged plan:
the slice ladder + bracket geometry (§A), the T0 excision-width ladder
(§B), the per-statistic noise-floor estimator (§C), and the G1b-campaign
spec including determination (3)'s shared-vs-separate-root discriminator
(§D). **This is the unit where numbers are proposed for review** (the
§Q3 lesson scopes *which* unit the numbers live in — here — not whether
they may exist); every number below is a **proposal, Will's to adjust /
cut / fix**, each with a one-line justification and its axis/discipline
annotation. **brief-and-hold; nothing computes; uncommitted.**
Gate-language is rev-3 (G1a-met / G1b-open / G2-met; T0 existing-data
read now / new runs slate-2-gated; T1 / T1′ / T2-N-refinement G1b-held;
T3 §3-(A)-held). Apparatus-invariance (§5) is the spine: every number is
justified by *matched across compared slices, or declared axis*. BAR
rider on §D (Fibonacci/DGY = instrument-fidelity only, not Fib→AM
transfer). Asymmetric labels — instrument/methodology, never "AM
characterized."

---

## §A. Bracket ladder + geometry

**Design lemma (a §5 first-law application to the ladder itself).** The
sub≠super contrast must be read at **matched detuning**: paired
subcritical/supercritical slices at the *same* |λ−1|, so the only
declared difference between a pair is the sign of (λ−1) — i.e. the
spectral-type difference (AC vs PP) at fixed distance from criticality.
An unmatched pair (e.g. λ=0.5 vs λ=2.0) confounds the contrast with
detuning. Hence a **single symmetric detuning ladder** δ_k, with
λ_k^sub = 1−δ_k and λ_k^sup = 1+δ_k. Any sub/super asymmetry that then
appears is a *finding*, not a design artifact.

**Geometry — geometric in detuning δ=|λ−1|, not linear in λ.** λ=1 is a
scaling point; the governing variable on approach is the multiplicative
detuning. Linear-in-λ under-resolves near criticality and wastes rungs
far from it. So δ_k is geometric.

| Parameter | Proposed value | Justification / annotation |
|---|---|---|
| δ_max | **0.5** | = the banked ratio-immune sub/super contrast (λ=0.5 / 1.5). Makes the **existing-data T0 instance the outermost rung** ⇒ direct continuity with banked data, same N, same statistic (apparatus-invariant link to what's already validated) |
| δ_min | **0.005** | deliberately *below* w_min (§B, 0.01) so near-critical rungs exist on both sides of every excision-width cut — required for §B to be a real tuning guard, not cosmetic |
| K (rungs/side) | **8** | geometric step ratio (0.5/0.005)^(1/7) ≈ 1.93; δ ≈ {0.005, 0.0097, 0.0187, 0.036, 0.070, 0.135, 0.260, 0.500}. Enough to resolve the approach without over-claiming a curve |
| θ | golden mean (`GOLDEN`) | substrate constant; unchanged from all banked AM work |
| φ-ensemble | 16 φ ∈ [0,0.5), endpoint=False | **inherited verbatim** from `sensitivity_confirm` (§7.ter.48 period-0.5 α-ensemble) — not a newly chosen number |
| L_iter | **1e5** | inherited verbatim from the banked validated runs; G4-converged incl. critical λ |

**Fixed N for the brackets, and the N-robustness check —
δ-CONDITIONAL, not categorical (Will's §A flag).** It is *not*
categorically true that "brackets are λ≠1 ⇒ non-singular ⇒ vary-N is
G2-scoped." That holds for the **outer** rungs only. Near criticality
there is a **resolution crossover** at a δ-dependent scale N_c(δ),
N_c(δ)→∞ as δ→0: below N_c(δ) a slightly-off-critical slice still reads
critical-like. The banked sensitivity result is positive reason to
worry — N\*≈4.3×10⁴ is itself a near-critical resolution scale, and
δ=0.005 (and 0.0097, 0.0187) is finer detuning than whatever δ that N\*
resolves, so the **inner rungs may simply not be resolved at N=70000**.
Then varying N across {70000, 75025, 1e5} on an inner rung, **if it
drifts, that drift is a G1b-class resolution-crossover signature, not
G2-scope noise** — the categorical annotation would mis-read it and
smuggle exactly the T1/G1b confound it set out to exclude, just at
near-critical λ rather than at λ=1.

**The check is well-placed to *be* the test; the scoping is made
operational, not assumed (no guessed δ-boundary — §Q3 lesson).** Per
rung, judged against that rung's own §C α-ensemble floor:

- **N-stable** across {70000, 75025, 1e5} within floor ⇒ the rung is
  resolved at these N ⇒ genuinely non-singular ⇒ **G2-scoped (MET),
  runnable (G1a-met)** — the original annotation, now earned per-rung.
- **Monotone N-drift toward the off-critical expectation** (the *exact*
  resolution-crossover signature — not mere "varies"; a
  `discriminant_exact_question_check` framing: the question is "is this
  rung crossing N_c(δ)?", not "does it move?") ⇒ **G1b-class** ⇒ the
  rung is **critical-adjacent**: excluded from the non-singular bracket
  structure and routed to the G1b-held side (it is a soft-T1
  measurement). Non-monotone variation within floor ⇒ ordinary
  finite-N noise, stays G2.
- **Ambiguous** — monotonicity not *reliably* callable, or drift not
  cleanly separable from the §C-floor noise ⇒ **default
  G1b-conditional** (Will §A rider, 2026-05-19): the conservative
  classification, consistent with the direction both fixes already
  took. The campaign does not get to call a thin/ambiguous rung "G2"
  by under-powering the test.

The drift-determined boundary **is** the measured δ_res(N≈7×10⁴),
reported — not a pre-guessed constant. Consequence (honest, conservative
direction): the bracket ladder is **δ-graded** — outer rungs
G1a-met-runnable; inner rungs **G1b-conditional**, runnable only on a
no-drift result, else critical-adjacent/G1b-held. This narrows
rev-3 §8's "new T0 + T2-core runnable on slate-2 sign-off" to *outer
rungs runnable; inner rungs G1b-conditional* — propagated into rev-4
§4/§6/§8. (§B's w-ladder covers this for T0 specifically via large-w
excision of suspect inner rungs, but not for the bracket structure's
scoping generally — T2-core and the per-slice/parts-to-whole
observables also touch the inner rungs; hence the fix is at the
scoping level, not delegated to §B.) **Fixed structure (Will §A
rider):** the robustness-N-set must carry density sufficient for a
*reliable* monotonicity verdict — a reliability criterion (monotone
trend separable from §C-floor noise at a pre-registered confidence) is
part of the fixed campaign structure; the exact N-count and spacing are
proposed-not-fixed (numeric), but they may not be so thin that the
verdict is uncallable — an uncallable rung is *ambiguous* ⇒
G1b-conditional, never silently G2.

| Parameter | Proposed | Justification / annotation |
|---|---|---|
| Primary fixed N | **70000** | central `sensitivity_confirm`/`quadrant_useregime` validated point; non-Fibonacci interior (consistent with the banked "commensurability RULED OUT" finding — the pick is not a commensurate-N artifact) |
| N-robustness check | **{75025 (=F₂₅, Fibonacci), 100000}** | a *declared apparatus axis* (§5). **δ-conditional scoping** (see prose): outer rungs → G2-scoped (MET); inner rungs → the check *is* the G1b-class drift test, monotone-drift ⇒ critical-adjacent/G1b-held. NOT a categorical G2 claim. F₂₅ included so a Fibonacci/commensurate N is present. Standard Fibonacci indexing F₀=0,F₁=1 (the burned off-by-one — `fib_neighborhood`) |

---

## §B. T0 excision-neighborhood width ladder

T0's named artifact risk (rev-3 §4): *excision width tuned to result.*
The discipline (rev-3 §4 / §9): width is a **declared ladder**, never
free. Design: the §A δ-ladder is fine and reaches δ_min=0.005; the
excision half-width **w is a declared cut on that ladder** — T0 at width
w uses only bracket rungs with δ > w. The w-ladder then genuinely tests
tuning: does the sub≠super conclusion flip as near-critical rungs are
included/excluded?

| Parameter | Proposed | Justification / annotation |
|---|---|---|
| w-ladder | **{0.01, 0.02, 0.04, 0.08}** | geometric ×2, 4 rungs. At w=0.01 the two innermost δ-rungs are excised; at w=0.08, five — so the cut meaningfully varies how near λ=1 the brackets reach |
| Read | **width-robust vs width-dependent** | conclusion stable across the whole w-ladder ⇒ `width-robust` (a real T0 result). Conclusion that moves with w ⇒ the w-dependence **is** the finding (localizes it as a near-critical artifact and names the w at which it changes). Tuning is precluded *by construction*: the result is reported across the entire ladder, never at a chosen w |

This makes §A and §B **one coupled structure**: a fine symmetric
detuning ladder, with w the declared, fully-reported cut on it.

---

## §C. Per-statistic noise-floor estimator

§9 / §7.ter.59: each statistic read against its **own
empirically-estimated** noise; W1δ ≠ KS ≠ var(s); no assumed/folklore
floor (the burned "≈0.74" mis-spec → replaced by an *estimated* anchor).

**Estimator (a verbatim generalization of the already-validated
`sensitivity_confirm` criterion — NOT a new discriminant).** For any
slice (λ,N) and any statistic S ∈ {W1δ, var(s), the sub≠super contrast,
parts-to-whole}:

> **floor(S; λ, N) := the spread (max−min) of S over the exact 16-φ
> α-ensemble (φ ∈ [0,0.5), L=1e5, golden θ) at that (λ,N).**

A comparison/contrast is significant **iff** (verbatim
`sensitivity_confirm` form): the two slices' S-ensembles are **disjoint
AND the inter-slice gap ≥ max of the involved per-slice floors**. Each
statistic gets its *own* ensemble-estimated floor (W1δ's floor ≠ var(s)'s
floor — separately estimated, never shared/assumed). The α-ensemble is
the §7.ter.48 substrate-generated null ⇒ the floor is the substrate's
*own* finite-N φ-variability (support-set-respecting; the right null for
"is the contrast bigger than the substrate's own slice-to-slice
noise"). Reusing the banked validated criterion verbatim is the
strongest discipline posture — this is not a new test, it is the
sensitivity criterion applied per-observable.

---

## §D. G1b / G1b′ campaign + determination (3), detrended

**Substrate:** the Fibonacci Hamiltonian, DGY-exact multifractal
exponents (gap-labelling IDS ∈ ℤ+θℤ; DGY τ(q) via Fricke–Vogt trace-map
hyperbolicity). **BAR rider, verbatim:** this campaign is
**instrument-fidelity only** — it certifies whether `unfold_rotnum`'s
vary-N trajectory recovers a *known external* scaling. It is **NOT** a
Fib→AM substrate transfer, NOT a §3 input, NOT Class-II construction.

**N-ladder:** Fibonacci numbers, **standard indexing F₀=0, F₁=1, hard
asserted** (the burned off-by-one — `fib_neighborhood`). Proposed span
**F₁₅…F₂₆** {610 … 121393} — wide enough to expose the N-scaling of the
residual-from-truth; the upper end overlaps the AM validated regime.

**The three determinations (rev-3 §6):**

1. **G1b PASS/FAIL.** Run the T1 vary-N protocol (`unfold_rotnum`
   rotation-number IDS) on the Fibonacci substrate across the N-ladder;
   compare the recovered scaling to the DGY-exact target. PASS iff the
   N-trajectory converges to DGY-exact within the §C ensemble-estimated
   tolerance (the floor logic applied on the Fibonacci substrate — an
   *estimated* tolerance, not an assumed one).
2. **G1b′ PASS/FAIL.** Same, for the energy-resolved Thouless-coordinate
   indexing (T1′'s anchor) against the Fibonacci substrate's known
   Thouless / gap-labelling structure.
3. **Shared-vs-separate-root discriminator — DETRENDED (the flagged
   hazard avoided).** On the **same paired runs** (same substrate, same
   N-ladder, same φ — apparatus-matched by construction, §5), form each
   indexing's residual-from-DGY-truth r_G1b(N), r_G1b′(N).

   - **The hazard (stated so it is provably avoided):** both residuals
     →0 ~monotonically, so a *raw* corr(r_G1b, r_G1b′) → ≈1 **by
     construction** — it codes the proxy question "do both converge?",
     not the exact question "do they share a finite-N root?". This is a
     `discriminant_exact_question_check` instance; §9 codifies it (a
     named terminal must be one the test is built to produce).
   - **Exact-question coding (two legs):**
     - **(3a) scaling-exponent test.** Fit each residual to its
       expected power-law approach r(N) ≈ A·N^(−γ); extract γ̂_G1b,
       γ̂_G1b′ with jointly-estimated uncertainty. *Same* convergence
       exponent ⇒ same finite-N-truncation scaling ⇒ shared-root
       evidence.
     - **(3b) detrended-fluctuation correlation.** δr(N) := r(N) −
       Â·N^(−γ̂) (convergence trend partialled out); correlate the
       *detrended* fluctuations δr_G1b vs δr_G1b′ on the paired runs.
       Correlated idiosyncratic part ⇒ shared mechanism; uncorrelated
       ⇒ independent. Read against its own §C ensemble-estimated floor.
   - **Decision — ASYMMETRIC burden, TERMINAL separated from MEMBERSHIP
     consequence (Will's §D flag + §D terminal-logic rider; the draft's
     original rule was symmetric *and* made COLLAPSE a catch-all — both
     corrected).** The two verdicts do not transfer equally from
     Fibonacci to AM (see Transfer scope, below): COLLAPSE is
     instrument-property-ish and transfers; INDEPENDENT is the
     substrate-fragile verdict. But COLLAPSE is a **positive** verdict —
     stamping "couldn't determine" as COLLAPSE is the §Q3
     "slow-convergence ≠ divergence" honest-terminal violation. So:
     - **Terminal `T1PRIME_COLLAPSES_TO_T1`** — *positive shared-root
       evidence only*: (3a) shared exponent **and** (3b) correlated
       detrended fluctuation (both legs ⇒ one root). **Never** by
       default, never the catch-all.
     - **Terminal `T1PRIME_INDEPENDENT`** — only if (3b) uncorrelated
       **and** (3a) exponents differ **and** transfer to AM is
       established (a supplied transfer argument that the Fibonacci
       independence is instrument-driven not substrate-driven, **or** an
       AM-side spot-check that corroborates).
     - **Terminal `T1PRIME_ROOT_INDETERMINATE`** — *every* "couldn't
       determine": legs disagree, power insufficient, **or
       independence-shown-on-Fibonacci-but-transfer-not-established**,
       or neither positive terminal earned. The honest catch-all is
       INDETERMINATE, **not** COLLAPSE (`_HALT`/indeterminate over
       stamp; the §Q3 error class).
     - **Membership consequence (separate from the terminal).** T1′
       counts as an *independent cross-check* in the §4 matrix **iff
       the terminal is `T1PRIME_INDEPENDENT`**. Under COLLAPSE *or*
       ROOT_INDETERMINATE, T1′ does **not** count as an independent
       cross-check — the conservative default lives **here, on
       membership**, not on the COLLAPSE label. Conservative posture on
       T1′'s evidentiary weight preserved without false-stamping a
       shared root.

**Transfer scope of determination (3) (Will's §D flag).** The BAR
rider makes Fibonacci a clean instrument-fidelity calibrator for (1)
and (2): "does `unfold_rotnum` recover known scaling" is a *pure
instrument* property, independent of substrate, so a Fibonacci verdict
transfers to AM. **(3) is different — it is an instrument × substrate-
multifractal-structure interaction, not a pure instrument property.**
Running (3) on Fibonacci answers it *for Fibonacci*: the
instrument-numerics contribution to root-sharing transfers; the
substrate-multifractal-structure contribution is Fibonacci-specific and
does **not** automatically transfer to AM (different multifractal
structure ⇒ two indexings independent on Fibonacci could still be
coupled on AM). The asymmetry: **COLLAPSE** (shared root) is the
instrument-ish verdict and **transfers**; **INDEPENDENT** (separate
roots) is **substrate-fragile** and does not transfer without an
argument. This is the residual of the Fibonacci-faithfulness concern —
the BAR rider closes it for (1)/(2), **not** for (3); the asymmetric
decision rule above is how (3) is closed. The transfer argument /
AM-side spot-check that can upgrade ROOT_INDETERMINATE → INDEPENDENT is
itself slate-2-spec'd-structure (its numeric form proposed-not-fixed);
that the upgrade *requires* one is fixed here.

**Numeric specs deferred-within-§D, flagged:** the (3a) fit form +
exponent-equality test + its uncertainty model, the (3b) correlation
statistic + its floor, the §C-tolerance constants for (1)/(2), and the
N-ladder density are **proposed-for-sign-off**, not fixed — but the
*structure* (detrended, two-leg, indeterminate-allowed) is fixed here so
the campaign is built to produce the §7 terminal it names.

---

## §E. Scope / discipline

Reviewable DRAFT — Will's to sign off / cut / fix; numbers are
proposals, none self-authorized or run. brief-and-hold; **nothing
computes**; uncommitted. Gate-language rev-3-consistent. §A/§B coupled
(one detuning ladder, w the declared reported cut — tuning precluded by
construction). §C reuses the banked validated `sensitivity_confirm`
criterion verbatim per-observable (not a new discriminant); each
statistic its own ensemble-estimated floor (W1δ ≠ KS ≠ var(s)); the
floor is the substrate's own φ-variability (support-respecting). The
bracket N-robustness check is **δ-conditional** — G2-scoped (MET) for
outer rungs; for inner rungs the check *is* the G1b-class
resolution-crossover test (reliable-monotone-drift ⇒
critical-adjacent/G1b-held; **ambiguous/uncallable rung ⇒ default
G1b-conditional**, never silently G2); the bracket ladder is thus
δ-graded, narrowing what is runnable on slate-2 sign-off (propagated
into rev-4 §4/§6/§8). §D is BAR-scoped instrument-fidelity for (1)/(2);
determination (3) is **detrended / two-leg / asymmetric, TERMINAL ≠
MEMBERSHIP** — (3) is an instrument×substrate interaction, not pure
instrument; **COLLAPSE is positive-shared-root-evidence-only (never the
catch-all — §Q3 honest-terminal discipline)**, INDEPENDENT requires
established AM-transfer, **every "couldn't determine" → ROOT_INDETERMINATE**,
and the conservative default lives on **T1′'s membership** (counts as an
independent cross-check iff terminal=INDEPENDENT), not on the COLLAPSE
label; the raw-correlation trap avoided by construction,
exact-question/proxy mapping tied to `discriminant_exact_question_check`. No §3 adjudication; T3 forward
§3-(A)-gated, reverse G1b-inherited. Asymmetric labels — instrument /
methodology validation, never "AM characterized," never a discovery.
Banked Step-1 untouched / additive.

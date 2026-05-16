# PHASE 35a BRIEF
## Calibrator-zoo extension — Cantor/multifractal + clock+band-perturbation AC classes (prerequisite for the Almost-Mathieu transition-diagnostic arc)

**Status:** Pre-execution. **BRIEF ONLY — brief-and-hold** (no code, no compute; no execution without explicit go), exactly as cohomological-H was. 35a is the **prerequisite** of the Phase 35 arc: 35b (transition-diagnostic validation) and 35c (optional sub-quadrant) gate on 35a's calibrators existing and being synthetic-validated. Decision record: memory `phase35_am_arc_design` (design settled 2026-05-15 in a critical-review exchange). This brief transcribes that settled design so 35a carries **no phantom research-unknowns**.

**Lit-lock (to verify at 35a execution start, BCGNT-style — cited here, not yet independently verified):** Avila–Jitomirskaya (AM spectral phase diagram; the **proven** λ=1 boundary; subcritical AC for λ<1 diophantine θ; supercritical pure-point); Damanik–Gorodetski–Yessen (Fibonacci-Hamiltonian **exact** multifractal exponents + rigorous trace-map renormalisation); the gap-labelling theorem (Johnson–Moser / Bellissard: IDS takes values in ℤ+θℤ on spectral gaps); Avila one-frequency cocycle theory (the AM ↔ Schrödinger-cocycle-over-irrational-rotation bridge). No claim rests on these until lit-locked.

---

## §0. Frame

The Phase 35 arc is **instrument-validation, not measurement**. There is nothing novel to discover in Almost-Mathieu (AM) spacing statistics — 40 years of literature; the Hofstadter butterfly is textbook. The value-add: **AM is the first *non-synthetic* universality-transition substrate available to validate the `transition_diagnostic` itself.** The Phase-20.5 transition calibrators are hand-tuned GUE↔Poisson blends — circular: the diagnostic could merely be reading back the mixing weight. AM's transition has an **independently *proven* phase boundary at λ=1** (Avila–Jitomirskaya), set by mathematics, not by ARS.

35a does not touch AM measurement or the diagnostic. It builds the **two calibrator classes the existing zoo has no slot for**, which the AM regimes will require, and synthetic-validates them against their analytically-controlled generators. Without these, 35b cannot honestly classify the AM regimes (Phase-34f playbook: extend + synthetic-validate the instrument *before* it meets the substrate; the §7.ter.46 single-molecule lesson — calibrator-zoo extension precedes instrument-validation on a new universality-class substrate).

## §1. Goals

Build, and synthetic-validate against analytically-controlled generators, **two new named calibrator classes**:

1. **Cantor/multifractal class** (for the AM critical line / Fibonacci-type Cantor spectra).
2. **clock+band-perturbation AC class** (for subcritical AM, absolutely-continuous regime).

Both enter `STATIONARY_CALIBRATORS` (or a clearly-segregated extended set) only after passing §5 synthetic validation. 35a produces calibrators + a validation report; **no AM data, no transition diagnostic, no measurement.**

## §2. Scope

**IN:** the two calibrator generators; their unfolding procedures (specified in §3/§4, not open research); §5 synthetic validation against analytic ground truth; verdict per §7.

**OUT (load-bearing):**
- **NOT** AM measurement, the (θ,λ) sweep, or the transition diagnostic — that is 35b, separately briefed and gated on 35a.
- **NOT** the AM critical line λ=1 *as a measured substrate*. The λ=1 Cantor spectrum is a real renormalisation signature but **outside the joint-plane (BL/TR/BR/TL) vocabulary**; its correct instrument is the f(α) singularity spectrum / box-counting, a *different* tool — same false-positive class as §7.ter.49 mode-A discretisation. 35a builds a *calibrator* for the Cantor class (so the zoo can *recognise and reject* such spectra), it does not propose to *classify* λ=1 on the joint plane.
- **NOT** a discovery/measurement cell — calibrator-extension only; asymmetric-label discipline (METHODS §1): this is instrument construction, never a result.

**Corrections that must NOT be re-imported** (from the original measurement-framed proposal; scope guards):
- "Proven theorems vs conjectures" overstates: **no AM regime is BCGNT-grade.** Supercritical Poisson is Bourgain–Goldstein / Jitomirskaya (diophantine-class-dependent), **not** Minami-grade (Minami = iid disorder, breaks under quasi-periodicity). The arc's rigour anchor is the *transition boundary* (Avila–Jitomirskaya), not regime-wise NNS-class theorems.
- The bucket↔AM link is **cocycle over an irrational circle rotation** (real; Avila one-frequency theory) — keep that bridge; the "deformed-bucket = vary λ" scaffold is **killed** (the bucket has no λ-analog; it drove an unjustified parameter-sweep framing).
- AM is GOE-by-symmetry (real-symmetric, time-reversal) for calibrator bookkeeping, but the **predictions are Poisson (supercritical localised) / clock-rigid (subcritical AC), NOT Wigner.** Subcritical AC is a *distinct class*, not "more nuanced GOE" — hence calibrator class II exists.

## §3. Calibrator class I — Cantor/multifractal (Fibonacci-Hamiltonian / DGY generator)

- **Generator:** the Fibonacci Hamiltonian (Damanik–Gorodetski–Yessen), evaluated at golden-mean continued-fraction denominators (Fibonacci numbers) via the rigorous trace-map renormalisation. DGY supply **exact** multifractal exponents — the analytic ground truth for §5.
- **Unfolding (specified, NOT open):** unfold by the integrated density of states via the **gap-labelling theorem** — the IDS takes values in ℤ+θℤ on spectral gaps and is explicitly computable there. This is well-defined; it is *not* a research unknown (the original proposal wrongly treated "how to normalise a measure-zero Cantor set" as open).
- **Characteristic NNS signature:** the IDS is locally constant on gaps, so gap-edges collapse to a single unfolded coordinate ⇒ an **atom at spacing zero** + a **multifractal tail** from within-band spacings. This is precisely the signature the existing BL/TR/BR/TL vocabulary has *no slot for* — the reason a new class is needed. The calibrator's job is to let the zoo *recognise and quarantine* Cantor-class spectra (a Cantor spectrum fed to the joint plane must classify as this class, not be force-fit to BL/TR).

## §4. Calibrator class II — clock+band-perturbation AC

- **Exact endpoint anchor (λ=0):** the free discrete Laplacian. The N-truncation eigenvalues are 2cos(πk/(N+1)); unfolding by the arcsine IDS maps them to an **exactly equispaced** sequence (a perfect clock: spacing 1, zero variance). This is the rigorous anchor.
- **Calibrator = controlled deformation off the λ=0 clock** for 0<λ<λ*, **with λ\* bounded by the analytical AC-regime condition** (subcritical AC proven for λ<1 with diophantine θ, with margin away from the λ→1 self-dual point) — **NOT** by "where the NNS happens to look AC". The class is anchored at an exact endpoint and bounded by a proven condition; the interior shape between the two principled posts is filled empirically. Epistemic tier: **anchored, not exponent-controlled** (unlike DGY-Fibonacci) and **not free-empirical** — a deliberate middle tier, stated as such so it is not over-trusted.
- **Why it must exist:** subcritical AC is band-structured / number-rigid (clock-like with band-modulated fluctuations), categorically *not* Wigner-Dyson β=1. Absent this class, 35b would be forced to read the subcritical regime against an inapplicable GOE reference.

## §5. Synthetic-validation discipline (Phase-34f playbook + the cohomological-H §7.ter.57 sharpening)

Each calibrator is validated against its analytic generator **before** it enters the zoo, and the validation obeys the discipline just hardened in cohomological-H:

- **Class I:** recover the DGY exact multifractal exponents (and the atom-at-zero structure) from the trace-map truncations within tolerance.
- **Class II:** at λ=0, the unfolded sequence must be the exact clock (zero variance); for 0<λ<λ*, recover the band-perturbed clock consistently and monotonically in λ.
- **Sample-size/regime-floor anchoring (LOAD-BEARING, imported from §7.ter.59):** every distribution test is judged **against its own sample-size floor** — for KS, the statistic is read as `KS / (0.8687/√n)` versus the relevant depth/N, **never raw KS, never a large-n p-value** (a p-value →0 for any infinitesimal deviation at large n; a raw KS is calibrator-grade at n~2000 and a large deviation at n~10⁷). Validate at **realistic n / realistic per-replicate depth**, not convenient n — the §6/§7 cohomological-H harness bugs were n-scale-only failure modes a small-n harness passes. A calibrator is "stamped" only if it recovers its analytic ground truth *to its own floor*, with that floor stated explicitly.
- **Negative controls:** a Cantor-class synthetic must NOT classify BL/TR/BR; an AC-clock synthetic must NOT classify Poisson; cross-feed each generator's output to the other's test and confirm rejection.

## §6. Pre-flight gates

- **Lit-lock gate:** verify Avila–Jitomirskaya / DGY / gap-labelling / Avila-cocycle as cited (BCGNT-style) before any build; halt + report on any mismatch.
- **Compute note (corrected):** the AM / Fibonacci operators are **tridiagonal** — symmetric-tridiagonal eigensolve (LAPACK `stev`/`stebz`) is sub-second at N=10⁴, ~1000× cheaper than dense. The cost driver across the arc is the (θ,λ)-cell × seed × surrogate combinatorics and the Fibonacci-denominator N-ladder (discrete, not a continuum). 35a itself (calibrator construction + synthetic validation) is small.
- **Corrections checklist:** the §2 corrections-not-to-re-import are a hard pre-flight checklist; any reappearance halts.

## §7. Verdict vocabulary (asymmetric — calibrator-extension, never a result)

- `CANTOR_MULTIFRACTAL_CALIBRATOR_SYNTHETIC_VALIDATED` — recovers DGY exact exponents + atom-at-zero to its stated sample-size floor; negative controls pass.
- `AC_CLOCK_PERTURBATION_CALIBRATOR_ANCHORED_AND_VALIDATED` — exact at λ=0; consistent monotone deformation for 0<λ<λ* (λ* analytically bounded); negative controls pass.
- `CALIBRATOR_UNRESOLVED_HALT` — a generator/unfolding does not recover its analytic ground truth to floor; **halt, do not stamp, do not proceed to 35b** (the §D.0b discipline: a mis-specified calibrator silently corrupts every downstream classification).
- Cell-level: `PHASE35A_ZOO_EXTENDED_VALIDATED` (both classes stamped) or `PHASE35A_PARTIAL` / `_HALT`. **Never** a discovery, measurement, or "AM result" verdict.

## §8. Forward / scope boundary

On `PHASE35A_ZOO_EXTENDED_VALIDATED`:
- **35b (separate brief, gated on 35a):** transition-diagnostic validation. Supercritical + λ→1⁻ approach **only**; golden-mean θ; Fibonacci-denominator N-ladder. Right-null = the **α-ensemble** (the cos(2π(θn+α)) phase is part of the operator; the α-ensemble at fixed (θ,λ) is the substrate-generated null per §7.ter.48 — non-circular, doesn't presuppose β), valid **localised-regime only** (subcritical α-ensemble mixes spectra-as-sets — a separate audit if ever extended). Verdict map pre-specified **both ways**: a quadrant-flip (validates the diagnostic on a non-synthetic substrate) **and** a BL-throughout-with-rep_med-drift / sub-quadrant outcome (the §7.ter.28 BGP-shape precedent — the diagnostic correctly returns null while the substrate's evolution lives sub-quadrant).
- **35c (optional, contingent on 35b):** if 35b is sub-quadrant-only (BGP-shape), AM becomes the validation substrate for the long-queued Phase-22+ sub-quadrant-trajectory extension.
- **λ=1 stays OUT of the whole arc** as a measured substrate — a different instrument (f(α) singularity spectrum), not the joint plane.

The arc validates `transition_diagnostic`; it is **not** AM measurement and yields **no** arithmetic/physics result about AM.

## §9. Methodological commitments

- Brief-first / compute-after (Phase-34f playbook); no execution without explicit Will go (brief-and-hold).
- Synthetic-validate each calibrator against its analytic generator, **at realistic n, judged against its own sample-size/regime floor** (§7.ter.55 / §7.ter.59 — the cohomological-H lesson: a statistic is only interpretable against its own regime floor; KS/(0.87/√n), never raw KS, never large-n p).
- Asymmetric-label: calibrator-extension is instrument construction, **never** a discovery (METHODS §1).
- Keep the cocycle-over-irrational-rotation bridge; the deformed-bucket scaffold stays killed.
- §D.0b: a mis-specified calibrator is the silent-corruption surface — `_HALT` rather than stamp a calibrator that fails its analytic ground truth.

## §10. References / cross-refs

- Avila, Jitomirskaya — AM spectral phase diagram, the λ=1 boundary, subcritical AC / supercritical pure-point.
- Damanik, Gorodetski, Yessen — Fibonacci-Hamiltonian exact multifractal exponents + trace-map renormalisation.
- Johnson–Moser / Bellissard — gap-labelling theorem (IDS ∈ ℤ+θℤ on gaps).
- Avila — global theory of one-frequency analytic SL(2,ℝ) cocycles (the bucket↔AM structural bridge).
- Bourgain–Goldstein / Jitomirskaya — supercritical localisation (the *correct*, conjecture-grade-not-Minami status of supercritical Poisson).
- Cross-ref: memory `phase35_am_arc_design`; METHODS.md §1 (asymmetric-label tiers); RESULTS §7.ter.59 (the sample-size-floor sharpening); §7.ter.28 (BGP sub-quadrant precedent), §7.ter.46 (calibrator-zoo-extension-precedes-instrument-validation), §7.ter.48 (substrate-generated right-null), §7.ter.49 (mode-A discretisation false-positive class), §7.ter.55/57 (validate the instrument on known truth).

---

End of brief — awaiting Will's review before any 35a build / synthetic validation. brief-and-hold.

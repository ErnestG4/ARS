# ARS Look Arc — Task B findings

**§0 binding:** nothing here estimates Λ; nothing bears on RH. ζ is a calibrator substrate.
**§0d two-point family collapse:** F(α), Σ² and Δ₃ are **one witness under three headings**. Nothing below
is reported as F corroborating Σ².

Seals: `seals/TASKB_SEAL.json` + `seals/TASKB_SEAL_ADDENDUM_1.json`, both committed before any run
(`2445eb5`, `0dc5a32`). Runs: `taskB_falpha.py`, `taskB_diagnostics.py`, `taskB_diagnostics2.py`.
Every run attempted is logged; none were re-run to agree.

---

## Honest state: **RESOLVED, premise corrected. Not robust.**

Resolved: on one block, through one statistic family, above a properly built floor, with the decoy
battery that Phase 3's lesson demanded and Phase 3 did not have. Not robust: single block, single
family, and the headline rests on synthetics whose class is known by construction rather than on a
second substrate.

---

## 1. The premise is wrong, and the *correct* version is stronger than the stated one

**Stated premise:** F(α) can be computed as a direct exponential sum over raw γ with the θ-exact
density, *with no unfolding step*; a readout that never unfolds cannot acquire Phase 3's artifact.

**Measured:**

| test | result | sealed | verdict |
|---|---|---|---|
| P-B0-a: Montgomery's literal pair sum over raw heights vs unfold-then-transform | max abs diff **1.76e-12** | < 1e-10 | **HOLDS — and pre-declared INERT** |
| P-B0-b: F under poly3 vs θ | **11.62%** median rel-diff (α ∈ [0.2,2]) | > 10% | HOLDS |
| P-B0-b: F under poly9 vs θ | **2.10%** | > 2% | HOLDS |
| P-B0-c: F under constant block-mean density vs θ | **28.90%** | > 50% | **sealed predicate FAILS** (ordering held, magnitude overpredicted) |

So: **F(α) is unfolding-DEPENDENT.** Writing the density inside the exponent is the same operation as
unfolding and then transforming — the pair sum and the periodogram agree to 2×10⁻¹², which is the point,
not a reassurance. "No unfolding step" describes *where the multiplication is written*, not what is
consumed. The literal "raw γ" reading (constant block-mean density) is the **worst** of the four schemes
at 28.9% — it is the crudest unfolding, not the absence of one.

**The spec's own B.1 test is inert and was pre-declared so.** "Run F under both unfolding schemes,
expect bit-identical" passes vacuously, because a θ implementation ignores its scheme argument. This is
the fourth member of the program's inert-falsifier family (shared-catalog SOC agreement; the unfold test
on an unfold-invariant statistic; the flat decoy battery against a curvature confound; this).

## 2. …but F really is better conditioned than Σ², and my seal said it wasn't

**P-B2-slot is FALSIFIED**, against my own sealed expectation. I sealed: *"Σ² through the θ path will
recover the known answers just as well as F does ⇒ F has NO conditioning advantage; the advantage is
θ's."* That is wrong.

On curvature-matched **GUE** (known class, imposed on ζ's exact-θ density backbone, 7.4× density
variation across the block):

| path | Σ²(L=32) vs known 0.697 | F(α), median rel-err over α∈[0.5,2] |
|---|---|---|
| θ (exact density) | **1.00×** | 3.4% |
| poly-order-3 (fitted) | **4.51×** — botched | **2.5% — fine** |

Σ² through a fitted unfold is 4.5× wrong on a case where F through the *same* fitted unfold is right to
2.5%. F's advantage over Σ² is real and large — **when the unfolding is imperfect.** With an exact
density model both are fine.

**Mechanism (measured, not asserted).** The fitted unfold's error is a smooth, low-frequency distortion,
so it has Fourier support only at very small α. Locating it (`taskB_diagnostics2.py` D2′, curvature-matched
GUE, B=10):

| α band | F_θ | F_poly3 | ratio poly3/θ |
|---|---|---|---|
| 0.001–0.002 | 0.0018 | **0.0358** | **20.1** |
| 0.002–0.004 | 0.0026 | 0.0028 | 1.05 |
| 0.004–0.008 | 0.0060 | 0.0060 | 1.00 |
| … up to 1.0 | — | — | 0.91–1.15 |

The entire artifact lives in **α < 0.002** — i.e. below ~2/N. Σ²(L) integrates the two-point function
with a kernel that diverges as α→0, so it eats the artifact whole; F read at α ≥ 0.002 never sees it.

**This corrects the slot, and the correction matters:** the advantage belongs to *reading the two-point
function at frequencies above the artifact's support*, not to "not unfolding". And it is bounded in a way
the stated premise was not — **F does not recover the long-L region; it declines to look there.**
Σ²(L=32) and F(α≥0.002) are different slices of the same two-point function. The labeled inference that
this "converts P3's low-γ long-L region from curvature-blocked to measurable" is **NOT supported**: F
measures a different, cleaner region. What actually unblocks the long-L region is §4 below.

## 3. A powered falsifier that FIRED: Phase 3's order-3 long-L anomaly is constructed

Phase 3's low-γ block through an order-3 empirical unfold gives Σ²(32) = **2.878** against a GUE band of
0.703 — the +45.8σ "wildly anti-rigid" reading (correctly slotted; see `LOOK_ARC_PROVENANCE.md` #11).

Building the *same* artifact on synthetics of **known** class, imposed on ζ's exact-θ density backbone
(`taskB_diagnostics.py` D3, B=6):

| substrate | Σ²(32) via θ | Σ²(32) via poly-3 | **excess** |
|---|---|---|---|
| Poisson (known 32.0) | 33.58 | 36.50 | **+2.92** |
| GUE (known 0.697) | 0.700 | 3.106 | **+2.41** |
| super-rigid | 0.344 | 2.945 | **+2.60** |
| **ζ, Phase 3 low-γ** | 0.285 | 2.878 | **+2.59** |

The artifact is **additive and class-independent at ≈ +2.5**, and ζ's excess (+2.59) sits inside the
synthetic range [2.41, 2.92]. Phase 3's +45.8σ is **shown, not argued,** to be the fitted-unfold artifact:
the confound was *constructed* at the right magnitude on data whose answer is known. Same shape as the
Phase 4 pooling decoy — the strongest kind of specificity evidence available.

**The one-line gate that would have caught it, never run.** ζ is the one substrate where the smooth
counting function is known *exactly*, so a fitted unfold can be checked directly against it
(`taskB_diagnostics2.py` D4):

| unfold | misfit vs exact θ counting |
|---|---|
| poly-3 | **2.764 levels** |
| poly-5 | 0.666 levels |
| poly-9 | 0.100 levels |
| poly-13 | 0.025 levels |

Phase 3 selected order-3 as "lowest passing = least over-smoothing risk". It misfits ζ's counting function
by **2.8 mean spacings**. One line of code, available at the time, decides it.

*Caveat, stated because it undercuts the neatness:* the naive prediction excess ≈ 2·Var[misfit] gives 15.3
for poly-3, against a measured ≈2.5. The identity does not apply — the misfit is a smooth deterministic
drift across the block, not a stationary decorrelated residual, so Σ²(L) only sees its variation over an
L-window. The misfit table diagnoses *which order is adequate*; it does not predict the excess magnitude.

## 4. The long-L low-γ plateau is Berry saturation — now bracketed, not attributed

Phase 3 attributed its long-L low-γ behaviour to "known Berry saturation". That was a **candidate
explanation, not a bracket** — the Phase-4 catch-#2 shape. An independent computation now brackets it.

Saturation identity: Σ²(L→∞) → 2·Var[S], where S(t) = N(t) − θ(t)/π − 1 is the counting-function
fluctuation. Var[S] is a different functional of a different object than Σ²(L), so the check has power.

- observed θ-path plateau (mean of L=16, 32): **0.2829**
- 2·Var[S] (S sampled uniformly in t): **0.3077**
- **plateau / 2·Var[S] = 0.919** — the identity holds to 8%.

**How this was nearly filed wrong, in my own disfavour.** The sealed run measured
`Var[S] = Var(rank_j − rvm_N(γ_j))` — S sampled *at the zeros*, i.e. the post-jump value of a jump
process, which is not the object the identity is about. That gives 0.0724, so 2·Var[S] = 0.145 and
**P-B5-saturation FIRED** against its sealed bracket [0.20, 0.36]. Re-sampled uniformly in t it is 0.1539,
2·Var[S] = 0.3077, inside the bracket. The sealed *number* (Var[S] ∈ [0.12, 0.16]) was right; the sealed
*estimator* was wrong. The prediction fired on my slot error, not on physics.

**θ-truncation certificate, powered.** Register R-003 established that Phase 2's θ-cert was inert **by
construction** (it measured Δ⟨r̃⟩, and r̃ is density-invariant). Re-run on a statistic that *can* see it:
Σ² under `rvm_N` vs `rvm_N + 1/(48πt)` vs the **exact** Riemann–Siegel θ differs by **0.0899%** at every
L, and Var[S] by 2×10⁻⁸. **Demonstrated inert**, which is a different and stronger object than
structurally inert. Note the honest limit: the perturbation is genuinely tiny, so this leg has little
power of its own. Its real content is that for ζ the smooth counting is **exact, not modelled** —
N(t) = θ(t)/π + 1 + S(t) is an identity — so "unfold by θ" is not a model choice for this substrate.

## 5. B.3 completion — the curvature-matched bracket Phase 3 never had

Phase 3 compared its θ-exact column against a GUE band built from **flat-density** GUE pushed through the
*empirical* unfold — not a matched bracket, and Phase 3 correctly quoted no σ for that column. Built
properly (`taskB_diagnostics2.py` D5; GUE imposed on ζ's exact-θ backbone, read through the θ path, B=20):

| L | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| curved-GUE band mean | 0.3433 | 0.4144 | 0.4858 | 0.5577 | 0.6339 | 0.7152 |
| band sd | 0.0048 | 0.0090 | 0.0160 | 0.0177 | 0.0284 | 0.0409 |
| ζ (θ path) | 0.3112 | 0.3465 | 0.3395 | 0.2883 | 0.2804 | 0.2855 |
| (ζ − GUE)/sd | −6.68 | −7.57 | −9.12 | −15.25 | −12.46 | −10.52 |

Two things this does and one it does not:

- **Does:** confirm Phase 3's poly9 verdict (−4.49 … −17.50 across the same L) through an independent,
  non-fitted path against a properly matched bracket. Same sign, same shape, comparable magnitude.
- **Does:** retire Phase 3's order-3 reading, per §3.
- **Does NOT:** establish a finite-height rigidity excess. **The block is not statistically homogeneous.**
  It spans γ = 14.13 → 2515.3 with mean spacing varying 7.4×, so ζ's own fluctuation statistics vary
  across it, while the bracket imposes *homogeneous* GUE fluctuations on that density. "More rigid than
  homogeneous GUE" is degenerate between a real finite-height excess and height-mixing. The bracket
  controls density; it does not control heterogeneity of the fluctuations. **This is the single most
  important untested confound in Phase 3 and it is now the top of the queue (R-010).**

Also note the near-identity of the curvature-matched band with Phase 3's flat band (< 2% at every L) —
when read through an exact density model, matching the bracket's curvature barely matters. The curvature
sensitivity was entirely in the *fitted* path.

## 6. α regions (B.4)

**α < 1 — calibration region.** ζ low-γ, θ path, sits at or slightly below the GUE line
min(α,1) across most of the region (F/α ≈ 0.75–1.0 for α ∈ [0.1, 0.6], reaching ≈1.0 by α ≈ 0.7–0.85).
Below-GUE = more rigid, the same direction as §5, and it is the *same witness*.
**Provenance slot, kept separate:** Montgomery's F(α) result and the Goldston–Montgomery equivalence are
stated conditionally on RH, and Goldston–Montgomery is an equivalence *between two conjectures*, not a
proof of either. That conditionality is filed against the **reference number**, never against the
instrument — the measurement consumes a finite list of verified zeros and reads only imaginary parts.

**Provenance slot — 2026-08-10 amendment (BGST unconditionality).** First, the "why GUE" proof-status
seam, discussed in the July session but never landed in the repo, is filed here for the first time.
Three slots: **(1) proven-restricted-support** — Montgomery's pair-correlation window and
Rudnick–Sarnak's restricted-support n-level correlations; **(2) proven-function-field** — Katz–Sarnak;
**(3) conjectured-full**. Amendment to slot (1): the Baluyot–Goldston–Suriajaya–Turnage-Butterbaugh
series ("An unconditional Montgomery Theorem for Pair Correlation of Zeros of the Riemann Zeta
Function," arXiv:2306.04799, and successors incl. arXiv:2501.14545) removes the RH assumption from
Montgomery's restricted-window pair-correlation machinery. **The window content moves from "theorem
assuming RH" to "theorem."** The paragraph above is superseded on that clause only; the
Goldston–Montgomery clause is untouched (still an equivalence between conjectures), and the sealed
twin at `seals/TASKB_SEAL.json` (`alpha_lt_1`) is left as sealed history per R-153 discipline — this
amendment supersedes it in prose, it does not edit it. BGST owns the unconditionality (2023–2025);
the occasion that surfaced it is Anthropic's 2026-08 result (a research version of Claude raised the
unconditional on-line proportion 41.6% → 67.2% via the BGST series + Bombieri 2000, Weil-quadratic-form
rank inequality; human-validated + Lean-verified).

Slot-discipline pre-catch, filed as caught before it fired: Montgomery's 2/3 is the **simple-zero**
proportion, **conditional on RH**; the 67.2% is the **on-line** proportion, **unconditional**.
Different slot, different conditionality — the numerical proximity may reflect a shared second-moment
source term, and that inference stands as inference; the two constants must not be filed as one fact.

What this amendment does NOT touch: Phase 2's Λ bracket [0, 0.22] and the classifier resolution
(0.00162 as filed; 0.00197 after the `LOOK_ARC_PROVENANCE.md` row-c correction) — the proportion
bound says nothing about Λ, and the flow-amplified +2σ finite-height residual stands as measured;
Phase 1/3's finite-height crossover (⟨r̃⟩ 0.615 → 0.603) — the proof lives in the liminf/asymptotic
regime and neither predicts nor explains the low-γ rigidity deficit; and CP1, which stays
load-bearing — the proof's mechanism is a genericity argument routed through proven moment bounds,
not an "arithmetic ⟹ chaotic" step, consonant with CP1's banked 7–8σ demonstration that
arithmeticity alone does not buy RMT. Register mirror: R-187.

**α ≥ 1 — LOOK region.** Calibrator grade zero. Reported qualitatively only, no σ/z/p: F fluctuates
about the GUE limit of 1.0 with no visible ramp or plateau structure beyond the estimator's own
exponential jitter (mean 1.04, range 0.68–1.63 over α ∈ [1.0, 2.9]). Filed as R-006. **Nothing is
claimed here.** The single elevated bin at α ≈ 0.95–1.0 is not distinguished from the estimator's
behaviour on a crystalline decoy (see R-007) and is not called structure.

---

## Scorecard — which falsifiers had power

| prediction | outcome | had power? |
|---|---|---|
| P-B0-a (pair sum ≡ periodogram) | HOLDS | **INERT** — algebraic; pre-declared inert in the seal |
| P-B0-b (F is scheme-dependent) | HOLDS | yes — could have shown F scheme-independent |
| P-B0-c (const-density worst, >50%) | **predicate FAILS** (28.9%); ordering holds | yes |
| P-B1 (spec's identity test) | passes | **INERT** — pre-declared |
| P-B2-power (poly leg botches curvature) | **conjunction FAILS**; GUE arm 4.51× and super-rigid 8.6× hold decisively | **partly** — see below |
| P-B2-slot (F has no advantage over Σ²) | **FALSIFIED** | yes — and it falsified *my* reading |
| P-B5-saturation | fired, then traced to my sampling slot error; substantive claim holds at 8% | yes |
| P-B5-θ-cert | HOLDS (0.09%) | weak — the perturbation is tiny; **demonstrated** inert, not structurally inert |

**New instance of the inert-falsifier family, and a new variant.** P-B2-power was sealed as a
*conjunction* requiring the poly path to botch Poisson (ratio > 1.3) as well as GUE. The measured Poisson
ratio is 1.05–1.14, because the artifact is **additive at ≈+2.5** and Poisson's Σ²(32) is 32 — an 8%
effect, invisible by construction. The Poisson arm had essentially no power, and I could have known that
at seal time. Previous inert falsifiers produced false *passes*; this one sat inside a conjunction and
produced a nominal **FAIL**, which under a mechanical reading of the seal's stop rule would have halted
the session with the substantive question already answered on the two arms that had power.

The stop rule was not followed mechanically, and that is a judgement call recorded here rather than
hidden: **the sealed predicate failed and the substantive check it was built to run passed 2 of 3 legs
decisively.** The re-reading is post-hoc and is not itself sealed.

## Underclaim check (spec: flag underclaims equally)

Two results here are stronger than a cautious reading would file them, and are stated at full strength:
§3 is a *constructed* confound at matching magnitude — that is shown-not-argued and should not be softened
to "consistent with an artifact"; and §2 is a real, mechanistically located conditioning advantage for
F(α) that my own seal predicted against — it should not be softened because it embarrasses the seal.

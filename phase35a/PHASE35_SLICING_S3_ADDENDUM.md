# PHASE 35 — Slicing Slate Unit 3: ADDENDUM (curiosity additions + overnight execution)

**Status:** rev-0 draft addendum to `PHASE35_SLICING_S3_BRIEF.md`-class scope (Will 2026-05-20).
**Authorizes:** overnight execution chain Test 1 → C1 → Test 2 → (Test 3 if budget allows).
**Does NOT authorize:** §D, Class-II, §A reclass, Step-1 verdict math, rev-5 writing, retro-adjudication.

## Curiosity additions

Two curiosity probes added under Will's "any other exploratory tests
you would like out of curiosity" authorization. Same surface-not-
adjudicate framing as the mandated tests.

**C1 — θ-robustness probe** (separate script). Tests whether the
φ-mode contamination is golden-θ-specific or θ-universal: re-runs the
b1crocze1/b0haqgof3 instrument at the load-bearing cells with an
alternative Diophantine θ (silver mean √2−1 ≈ 0.41421). 2 cells
(sub δ=0.5/λ=0.5 + sup δ=0.5/λ=1.5) at N=70k, L=1×10⁵ only, 16 φ.
32 tasks total, ~2 min local 18w. Terminals: `THETA_RATIO_TRACKS_GOLDEN`
(within 30% of b1crocze1/b0haqgof3 ratios on both legs ⇒ φ-mode
structure is θ-universal across Diophantine class) /
`THETA_RATIO_DEVIATES` (>30% deviation ⇒ φ-mode is θ-specific; flag,
do not adjudicate (A)/(B)) / `THETA_RATIO_MIXED` (legs differ).
**Implication framing:** θ-universal contamination supports the
φ-mode being a property of the leg×Diophantine-class interaction;
θ-specific would localise it to golden-mean's Fibonacci-approximant
structure. **Never adjudicates (A)/(B)**, never adjudicates Step-1.

**C2 — Fibonacci-N spot-check folded into Test 1**. Adds N=46368
(=F₂₄) to Test 1's N-set, giving {4.3×10⁴, 4.6368×10⁴, 5×10⁴} =
non-commensurate / Fibonacci-commensurate / non-commensurate triplet.
Tests whether the Fibonacci-commensurate point gives an anomalous
contamination ratio. Adds 2 cells (sub+sup at δ=0.5, N=46368) ⇒
Test 1 grows from 4→6 cells (96→288 tasks). **Independent of the
brief's main terminal logic**; emits its own per-leg
`COMMENSURATE_NO_ANOMALY` (F₂₄ ratio within 30% of bracket-cell
ratios) / `COMMENSURATE_ANOMALY` (deviates) sub-terminal alongside
the primary `FLIP_N_PHI_RATIO_*` terminal. Consistent with the
established `fib_neighborhood` "commensurability RULED OUT" finding
at one slice; this spot-checks at flip-N.

## Overnight execution chain

Sequential (local 18w cannot parallel without oversubscription).
**Honest cost estimates** based on b1crocze1/b0haqgof3/bh22pfzoa
timings:

| # | Run | Tasks | Est wall | Cost-cap |
|---|---|---|---|---|
| 1 | Test 1 + C2 | 288 (6 cells × 16 φ × 3 L) | ~85 min | none — fixed ladder |
| 2 | C1 (curiosity) | 32 (2 cells × 16 φ × 1 L) | ~2 min | none |
| 3 | Test 2 | up to 48 (1 cell × 16 φ × 3 L) | ~5–6 h | drop L=2.56×10⁷ if projection >8 h |
| 4 | Test 3 (optional) | 64 (2 cells × 16 φ × 2 L) | ~4 h | skip if total elapsed >7 h |

Total without Test 3: ~6–6.5 h. With Test 3: ~10 h. **Test 3 launched
only if remaining budget at completion of Test 2 permits.**

**Chain orchestration.** I orchestrate through the night, harness
notifies on each completion:
- On each terminal: surface factually (no adjudication), update
  decision record, commit artifacts under same progress-log framing,
  launch next.
- **Halt chain on any `_INSTRUMENT_INCONSISTENT` terminal** — do not
  proceed past an apparatus-identity failure. Surface for Will.
- **Halt chain on a non-terminal crash** (script exception). Surface
  the failure, do not relaunch autonomously (no auto-chase).
- Ambiguous terminals (`PHI_RATIO_NON_MONOTONE`, `SUP_L_PATHOLOGICAL`,
  C1's `MIXED`) **do not halt the chain** — surface as observations,
  proceed.

**Apparatus identity checks (cross-env / cross-run).**
- Test 1: at the (δ=0.5, N=5×10⁴) sub and sup cells overlapping
  `sensitivity_confirm`'s stored `sub_spread@N=5e4=0.000292` and
  `sup_spread@N=5e4=0.122862`. Halt as `FLIP_N_INSTRUMENT_INCONSISTENT`
  if structural divergence.
- Test 2: at the (δ=0.5, N=70k, L=1.6×10⁶) cell vs b0haqgof3's stored
  per-φ values. Halt as `SUP_L_INSTRUMENT_INCONSISTENT`.
- Test 3: at the (δ=0.5, N=70k, L=1.6×10⁶) and (δ=0.5, N=125k,
  L=1.6×10⁶) cells vs bh22pfzoa's rawtable. Halt as
  `SUB_L_INSTRUMENT_INCONSISTENT`.
- C1: no prior-run identity check (novel θ); reports its own ratios
  and compares to b1crocze1/b0haqgof3 golden-θ baseline.

## Cost-cap protocol (Test 2)

Two-phase submission, NOT mid-pool cancellation:
1. **Phase 1:** submit L ∈ {1.6×10⁶, 6.4×10⁶} (32 tasks), measure
   wall time.
2. **Decision:** project L=2.56×10⁷ wall from observed L=1.6×10⁶ →
   6.4×10⁶ scaling (expected factor ~4 per Sturm-cost ∝ L). If
   projected wall + elapsed > 8 h budget, skip L=2.56×10⁷ and set
   top L = 6.4×10⁶ for postproc.
3. **Phase 2 (conditional):** submit L=2.56×10⁷ tasks if budget
   permits.

Pre-registered: skipping L=2.56×10⁷ does NOT change terminal logic
beyond top-L identity — `SUP_L_CONVERGED` still requires top_inc <
0.05 between the top two L points actually computed; the lower bound
remains a lower bound either way.

## Guardrails (re-stated)

- No adjudication: (A)/(B), Step-1 verdicts, §D timing, all Will's.
- No commits except as progress increments under the established
  framing ("Phase 35a progress log: …, NOT validated results").
- No rev-5 writing.
- No auto-chase beyond pre-registered ladders.
- Ambiguous terminals reported as-is; do not unlock downstream.
- `_tentative_review/` and `phase28/*` continue to be excluded from
  commits.

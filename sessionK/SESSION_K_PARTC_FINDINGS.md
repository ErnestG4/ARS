# Part C — Refusal Zoo vs Baseline B — **NULL (dark-appendix)**

Executed 2026-07-09 against the sealed pre-registration `SESSION_K_PARTC_PREREG_SEALED.md`.
Raw: `partC_measured.json`, `partC_refusal_zoo.py`.

## Result

**NULL. The refusal-report R re-encodes the trivial descriptors B; the boundary has no
own-structure. Dark-appendix the zoo.** This is the outcome the plan named as most likely
and most valuable — and the baseline guard earned its keep by catching a false positive.

## The measurement

Zoo: 40 instances × 5 types (T0 ensemble GUE/GOE, T1 deterministic-decaying, T2 rigid,
T3 critical/intermediate, T4 non-spectral), each a point process n≈300–800, with within-type
variation designed to make B-space overlap.

- **Harness validation:** single-type-relabeled control → B z=−0.38, R z=+1.04 (both ≈0; the
  small R value is real GUE/GOE sub-structure in T0, not a false-positive engine).
- **Global (5-type classification, permutation-z, the fair metric):** B acc 0.925 (z=21.4),
  R acc 0.960 (**z=20.7**). R does **not** exceed B at matched permutation-z — R's higher raw
  accuracy is within the feature-count inflation the permutation-z neutralizes. B+R=0.950,
  R-random-3-features=0.810. The types are grossly separable by trivial descriptors, so the
  global test is ceiling-limited and not discriminating.
- **Within-B-cell (the sharp test), with the decisive control:**

| quantity | value |
|---|---|
| R held-out accuracy in B-cells | 0.826 |
| **B held-out accuracy in same cells (CONTROL)** | **0.861** |
| R-orthogonalized (drop R's B-overlapping features) | 0.826 |
| permutation null | 0.368 |
| R − null | **+0.458** |
| **R − B (in-cell)** | **−0.035** |
| frac cells R beats B | 0.14 |

## Why this is the honest NULL, and how the guard worked

An **intermediate, under-controlled version of the sharp test gave a false POSITIVE**: R beat
the permutation null by +0.458 in 100% of cells → "R carries orthogonal structure!" That is
exactly the seductive result the plan warned about. **The B-within-cell control refuted it:**
B separates the types within the same cells *even better* than R (0.861 vs 0.826). The k-NN
cells were not truly B-constant — R was re-encoding residual B-variation, not anything
orthogonal. Comparing R to a permutation null answers the wrong question; comparing R to **B**
answers the right one, and B wins. (An earlier *resubstitution* version was saturated at
ceiling for both and equally uninformative — fixed to held-out CV, then controlled against B.)

So across every fair comparison — global matched-z, and within-B-cell against the B-control,
including B-orthogonalized R — **R shows no separation power beyond B.**

## Banked verdict (measurement only, scoped)

> Across these five refusal-types, at these statistics, against a strong three-feature trivial
> baseline B, the refusal-report R carries **nothing orthogonal to {rigidity, density-variation,
> spectral-type}**. The boundary did not pay rent **as a measurement here**. **Dark-appendix the
> refusal zoo.**

**Scope discipline (do not round up).** This is a **measurement-null, not a physics-null.** The
null is "R adds nothing beyond a *good trivial descriptor* B" — deliberately a strong B, which is
the honest choice — not "there is nothing in the boundary." The "reading-is-the-pair"
crystallization insight is **not refuted**; it simply did not cash out as a *second measurable
orthogonal axis* in this instance. Keep the "here": this zoo, this B, these statistics.

**Interpretation field (NOT promoted):** no "ARS measures coupling-type" claim — there is nothing
orthogonal to interpret. The axis could be real and simply not an orthogonal ARS observable.

## On a heavier confirmation run — confirmatory-of-confirmatory, NOT load-bearing

The direction is unambiguous, not a near-miss: R−B = −0.035 with R winning only 14% of cells is a
**loss**, and B-orthogonalized R *also* lost. The within-cell test's one residual interpretive gap
is that the k-NN cells weren't perfectly B-constant (that is how the +0.458 got in); a tighter-cell
run would test whether R stays null as cells actually approach B-constant. But **the
B-orthogonalized-R loss already closes that gap** (it removes the residual-B channel and R still
loses), so a tighter-cell run is confirmatory-of-confirmatory. Optional, for the tightest possible
write-up only — a future reader should not reopen this thinking it is load-bearing.

## Methodological deposit (the durable part)

The permutation-null is **not** a sufficient guard for a "beyond-baseline" claim: a rich report
R will beat a permutation null whenever it carries *any* signal, including signal the baseline
already has. The correct control is the **baseline itself, run head-to-head inside the same
cells** (and the report stripped of baseline-overlapping features). Two of my own intermediate
results — a saturated resubstitution test and a permutation-null-only test — pointed POSITIVE;
only the B-control gave the true NULL. Bank this as the operational form of "the baseline is the
guard."

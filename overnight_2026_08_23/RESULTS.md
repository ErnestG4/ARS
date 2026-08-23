# OVERNIGHT 2026-08-23 — R3 ARTIFACT BASELINE CAPTURE: RESULTS

Scored against `SEALED_CRITERIA.md` and its Amendment 1. **Nothing was migrated.**
`c3_rulings.migration_may_begin()` still raises.

---

## 1. Predictions, misses first

| # | prediction | outcome | |
|---|---|---|---|
| **P3** | ≤2 of the module script files reach `CAPTURED` | **3 of 3** did | **MISSED** |
| **P5** | ≥1 site lands `CAPTURED_INERT` | **0** in the final state | **MISSED** |
| P1 | every `def` site captures mechanically | 16 of 16 | met |
| P2 | ≥12 of the `def` sites reach `CAPTURED` | 16 of 16 | met |
| P4 | ≥1 input makes sites disagree on `best` | **45 of 55** | met |
| P6 | ≥1 site is `OBSERVABLE_ABSENT` | `run_analytical_nns.py:184` | met |

**P3's denominator was also wrong**, in Amendment 1, by me: it says "the same 4 script files"
when there are **3**. The fourth (`universality.py`) is a `def` site, which A1.6 corrected in one
clause and then miscounted in the next. P3 misses under either denominator.

**P5 deserves its own paragraph, because it appeared to land and did not.** The first mutation run
returned `universality.py:129 → CAPTURED_INERT`, exactly as predicted. Investigating it showed the
cause was **my harness**: `ast.get_source_segment` on a `ClassDef` drops decorators, so `NNSResult`
arrived undecorated and raised on all 55 inputs — and 55 identical exceptions cannot be perturbed.
Two sibling sites were likewise capturing only exceptions. A predicted failure appeared, and it was
a property of the instrument, not the population. Had I banked the verdict instead of diagnosing
it, the arc would carry a false finding about `universality.py` that matched a pre-registration —
which is the most durable kind of wrong.

## 2. Def-scope sites — 16 of 16 `CAPTURED`

Baselines: `baselines_def.json` (generator `capture_def_baselines.py`). Mutation:
`mutations_def.json` (generator `mutate_def_baselines.py`). Ruler: `inputs.json`, 55 vectors,
5 families × 11 sizes, seed 20260823, sealed before capture.

**The ruler discriminates.** 45 of 55 inputs produce disagreement on `best` across sites. The
band added by Amendment 1 is where the R1 fork is legible: at `clock_n30`, **four sites answer GUE
and nine answer `insufficient`** — the 5≤n<50 guard band that the first sealed input set had
nothing in the middle of. At `clock_n5`, three sites say `'Poiss'`, one `'Poisson'`, nine
`insufficient`: label divergence and guard boundary in one cell.

**Discrimination: 95 applicable attacks, 92 detected, 3 genuine survivals.**

| attack | applicable | detected | survived |
|---|---|---|---|
| guard_flip | 16 | 16 | 0 |
| guard_boundary | 16 | 13 | **3** |
| label_flip | 16 | 16 | 0 |
| key_drop | 15 | 15 | 0 |
| argmin_swap | 16 | 16 | 0 |
| statistic_perturb | 16 | 16 | 0 |

The three survivals are real and each is structurally explained by the edit it made:

- `run_lmfdb_family.py:102` and `verify/tier1_lfunction_guard.py:73` — edit `if n <= 5` inside
  `ks_to`. **The body guard at 50 shadows it.** No input can reach the helper's boundary, so the
  *inner layer of the D7 two-layer guard is dead wherever the outer layer is stricter.*
- `universality.py:129` — edit inside `_ks_pvalue`, whose output nothing compares. Unobservable by
  construction, which is the `COMPUTED_UNUSED` finding showing up as a hole in the baseline.

`statistic_perturb` is the load-bearing attack: it moves every KS distance by ~1e-14 without
touching control flow, and is detected at all 16 sites. An independent check measured that a
9-significant-digit serialiser would catch **0 of 55**, and `%.12g` only 2 of 55. The `float.hex()`
choice is doing demonstrated work rather than decorative work.

## 3. Module-scope sites — 3 of 3 scripts `CAPTURED`, repo unmutated

All three exit 0, with **byte-identical stdout across two runs** and **bit-identical PNGs**. The
restore verification reports **0 files differing** from a pre-run snapshot taken over `plots/`,
`signals_cache/` and the root `.npy` files — deliberately wider than the known write inventory, so
that "only the PNG changed" is a measurement rather than a reading of the source.

**Two sites carry declared observable limits, recorded with the artifact:**

- `run_analytical_nns.py:184` — `OBSERVABLE_ABSENT`. Its `p_o/p_p/p_u` are computed and never
  printed, plotted, or written. A migration that drops or corrupts them yields a byte-identical
  baseline. **These are exactly the quantities R5 promotes**, so the baseline is structurally
  blind to the thing this stratum was flagged for.
- `run_analytical_nns.py:297` — `OBSERVABLE_IS_FIGURE_ONLY`. The 21st decision site emits **no
  stdout at all**; its label reaches `ax.set_title` and stops. Its only witness is a PNG hash,
  which says *that* something changed and never *what*. The first version of the harness archived
  and restored the PNGs, discarding that site's only observable while reporting its file
  `CAPTURED`.

## 4. What these baselines certify — and what they do not

They are a strong **equality** gate and a weak **contract** gate. An independent adversarial review
constructed surviving mutants in four classes, all of which the consolidation will actually stress:

1. **Discarded helper elements.** `run_phase4`'s `ks_to` returns `(ks, n)` while its siblings
   return `(ks, p)`; the second element is discarded at the call site, so changing it survives all
   55 inputs. This is the precise hazard Amendment A1.5 named as the reason for per-site closures —
   the per-site closure is still necessary, and still not sufficient.
2. **Tie-break order.** Reordering the `min` arms changes behaviour only on exact KS ties, and no
   input produces one. Migration onto a different tie-break is certified as "no change".
3. **Dead branches.** `universality`'s `'empty'` sentinel is unreachable from any positive-spacings
   input.
4. **Out-of-range n.** The input set tops out at n=200; behaviour introduced above that is invisible.

**And one thing the migration protocol must handle explicitly:** the consolidation target,
`arithmetic_toolkit._classify`, returns a **superset** dict (`fit_poor`, `fit_rejected`,
`ks_crit_01`). An equality baseline will therefore flag the *intended* migration as a diff, and
cannot distinguish "gained the refusal keys as designed" from corruption. Brief clause 1's
bit-identity was written for the 7 shared keys; that is what it can check.

## 5. Corrections made during the run

Every one was found by something failing, not by review — and three of them were mine.

| # | defect | how it surfaced |
|---|---|---|
| 1 | closure followed only same-module names, so `_ks_pvalue` was missing; two sites "raised" on 40/55 inputs **only at large n** | the capture failing |
| 2 | `ast.get_source_segment` drops decorators; `NNSResult` arrived undecorated and raised on all 55 | investigating a predicted `CAPTURED_INERT` |
| 3 | the report counted closure **builds** and printed "16 of 16, zero failures" while three sites captured only exceptions | reading the mutation output, not the capture output |
| 4 | a module-level `ks_p = [...]` was pulled into a closure because `classify` has a **local** of that name | the capture failing |
| 5 | sentinel `"Task 1"` vs printed `"TASK 1"` → a **false `INFEASIBLE_TRUNCATED_RUN`** on a clean, deterministic run | the verdict being implausible |
| 6 | four **false `INAPPLICABLE`**s from regex spelling assumptions | independent audit |
| 7 | the widened `statistic_perturb` rebuilt the source **unchanged** — a no-op reporting as an applied attack, manufacturing 16 false survivals | 0/16 detection on an attack that had just measured 14/14 |

Defect 1 is the one worth keeping: it failed *only at large n*, because the helper returns its NaN
sentinel before reaching the missing name at small n. **A harness gap that fails in a
behaviourally plausible pattern is worse than one that fails everywhere** — it was ready to be
written up as a finding about two sites.

Defect 5 is a mirror of a lesson already in this repo's ledger: the B4 extraction's uppercase-only
matcher missed `universality.py` and emitted `NEEDS_JUDGMENT` for a tooling reason. I made the same
mistake in the opposite direction, in the harness written after filing it.

Defect 6 is the arc's **fourth** instance of one blind spot, each a level further in: which *files*
the extractor reaches → which *code* counts as the classifier (D7) → which *syntax* the values
arrive in (the 21st site) → which *syntax the guard is written in*, inside the instrument built to
audit the instrument.

## 6. Migration status: still **NOT AUTHORISED**

`migration_may_begin()` raises. Baselines now exist for all 21 decision sites, but SEALED_CRITERIA
§6.5 requires **every** site `CAPTURED` for migration to unblock, and two sites
(`run_analytical_nns.py:184` and `:297`) have observables that are respectively absent and
figure-only. Reporting this arc as "baselines captured, migration unblocked" would be the
`gate_certifies_half_say_so` defect exactly.

**What would unblock it:** an observable for the two qualified sites. For `:184` that means the
p-values must be emitted somewhere — which is what R5's COMPARE-DIRECTIVE would do anyway, since a
compared quantity is by definition an observed one. **The fix for the blind spot and the fix for
the finding are the same edit**, and that is an argument for doing R5 before the migration rather
than as part of it.

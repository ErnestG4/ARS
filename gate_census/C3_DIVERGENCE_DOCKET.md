# C3 DIVERGENCE DOCKET — measured facts, then the questions that need ruling

**Status:** inventory COMPLETE and certified. **No site migrated.** Brief clause 7 forbids
migration before the ruling, and this document is the thing to be ruled on.

**Generators:** `c3_divergence_inventory.py` (def-based, sealed `d8d8e07` → output `f71c898`),
`c3_inline_inventory.py` (completion, sealed `2e34eb8` → output `b0188ee`, amended `1144155`),
`c3_certify_d2.py` (sealed `58d0bbe`).

---

## 1. What the completed inventory measures

The def-based inventory found **11 variants**. It finds classifiers by `ast.FunctionDef` named
`classify`/`_classify`. `copy_dedup.json` had recorded the shortfall in plain sight —
`"sites_checked": 19, "bodies_found": 15` — and neither number was ever reconciled to the other.

**The four unreached files are not a random four.** Three of them (`run_analytical_nns`,
`run_per_pll_nns`, `universality`) are exactly the `COMPUTED_UNUSED` sites of Ruling 2. The
extractor's blind spot is **correlated with the divergence the inventory exists to measure**:
sites whose classifier is not a tidy named function are the same sites carrying extra computed
quantities. The sealed axis counts were therefore biased **low**, not merely incomplete.

Completed population, counting **per decision** rather than per file:

| | def-only | completed |
|---|---|---|
| decision sites | 11 | **20** (across 19 call sites) |
| label vocabularies (D5) | 2 | **3** |
| sites with no size guard | 1 | **3** |
| sites that are module-level script code | 0 | **5** |

The five previously invisible decisions:

| site | mechanism | scope | guard | labels |
|---|---|---|---|---|
| `run_controls.py:217` | `min` | module | none | `Poiss/GOE/GUE` |
| `run_analytical_nns.py:184` | `min` | module | 5 | `Poiss/GOE/GUE` |
| `run_analytical_nns.py:249` | `np.argmin` | module | 5 | `Poiss/GOE/GUE` |
| `run_per_pll_nns.py:138` | `min` | module | none | `Poisson/GOE/GUE` |
| `universality.py:129` | `min` | def | 5 | `poisson/goe/gue` (lowercase) |

**Not restated:** the sealed dedup number (11 distinct bodies, predicted range [4,6]) was taken
under its own stated normalisation and **stays scored there**. The completion changes the
population description, not that measurement — the same forward-only discipline as Ruling 2.

## 2. The D2 detector is certified against its nearest confusable

The confusable was not constructed; it was already in the repo. `p_two`, produced by the same
`_ks_pvalue(ks_two, ...)` idiom, appears at five sites:

- `run_decisive.py:247` — `if ks_two > 0.10 and p_two < 0.05` → **compared**
- `run_controls.py:287` — `if ks_two < 0.10 and p_two > 0.05` → **compared**
- `run_calibration.py:318` — `(ks_two > 0.10 and p_two < 0.05)` → **compared**
- `run_analytical_nns.py:266` — `print(f"... p={p_two:.4f}")` → **printed only**

Same name, same idiom, same computation. **Sensitivity 1/1, specificity 3/3.** The certifier
imports the shipped predicate rather than mirroring it — a verifier holding a copied body is the
precise defect (`verify/tier1_lfunction_guard.py`) that C3 exists to reconcile.

**The negative set carries a finding.** The comparison is present in three siblings and absent in
the fourth: **the rejection region was in the ancestor and was shed by a copy.** Clause 8's
COMPARE-DIRECTIVE is therefore not a policy preference imposed on the variants — it restores a
comparison the population demonstrably used to have, and consolidation is the fix for the
mechanism that lost it.

---

## 3. Questions for ruling

### R1 — the guard fork (5 / 50 / none)
**Measured:** `50` at 5 sites, `5` at 5 sites, **no guard at all** at 3 (`run_phase4`,
`run_controls`, `run_per_pll_nns`). Under Ruling 1 every one of these is a **free constant** —
none is re-derivable from the classifier's own parameters.

**Recommend:** the shared implementation takes `min_n` as a **required argument with no default**.
A default silently re-creates the free constant at every call site and hides the fork the
inventory just exposed. Separately, the derived option exists — `MIN_N = 1/RAIL_RATIO`, below
which an arm provably cannot fire — and it is the **only** option that would earn `GUARD_DERIVED`
from `classify_guard`. Adopting it is a real change of behaviour at all 13 guarded sites and
should be ruled on as such, not folded into a refactor.

### R2 — three label vocabularies, not two
**Measured:** `Poiss` (17), `Poisson` (2), `poisson` (1).

**Recommend:** uphold brief clause 3 and extend it to the third. Banked artifacts contain all
three spellings; normalising changes banked strings. `labels=` becomes a required parameter, no
default, for the same reason as R1.

### R3 — the acceptance criteria do not cover 5 of 20 sites
**Measured:** five decisions are module-level script code with no enclosing function. They have
**no returned key set** — recorded `INAPPLICABLE`, never an empty value that a distinct-count
would score as a variant.

**This breaks acceptance clause 1 as written.** Bit-identity of `best`/`gap`/`ks_*`/`n`/`mass03`
presumes a returned dict. At these five sites there is none; the observable is printed output and
the assigned `best` label. **A ruling is needed on what bit-identity means for a script**, before
migration, or five sites migrate under an acceptance test that cannot be applied to them.

**Recommend:** for module-level sites, acceptance is identity of the `best` label and of the
printed line, captured as a baseline snapshot per the C2 pattern. Migration here also means
*introducing a function call where there is straight-line code* — a larger change than at the 15
def sites, and worth sequencing last, after the shared implementation is proven on the others.

### R4 — one file, two decisions, two mechanisms
`run_analytical_nns.py` decides at `:184` (`min`) and again at `:249` (`np.argmin`), on different
data. **Recommend:** two rows in the migration ledger, not one. Per-file counting would hide a
mechanism divergence inside a file that already has a row.

### R5 — scope of the COMPARE-DIRECTIVE
Three families of quantity are computed and never compared: `ks_*` (most sites), `pv_*`
(`run_phase4`), `p_*` (`run_analytical_nns`, `run_per_pll_nns`).

**Recommend:** all three promoted to the `fit_rejected` / `ks_crit_01` mechanism already built and
proven in `arithmetic_toolkit`. This is clause 8 applied to the completed population rather than
to the def-only sample — and note that the sample it was originally ruled on omitted three of the
four sites the ruling was about.

---

## 4. Standing caution for whoever executes this

The def-based extractor reported a clean 11 and was wrong in a direction that mattered. It did not
fail loudly; it returned a plausible number. The completion generator carries a `redpath`
non-vacuity floor for exactly this reason — but the floor was written **after** hand-measuring the
five sites it asserts. *An extractor's reach is a claim about the world, and it needs a witness
that can fail.*

---

## 5. ⚖ ADJUDICATED 2026-08-22 — all five ruled, encoded in `c3_rulings.py`

**R1 — guard fork.** All free constants, so none has a claim to inherit. Sequence: attempt
derivation from the reconciled classifier's own validity first (precedent `MIN_N = 1/RAIL_RATIO`);
failing that, **one** convention constant chosen explicitly and typed as policy.
**Forbidden: silent inheritance from whichever variant the migration starts at.** *A convention
chosen is a convention; a convention inherited is an accident wearing one's clothes.*
Encoded: `guard_decision(n_min, derivation)` has **no default for `n_min`** — a default is silent
inheritance with extra steps.

**R2 — three vocabularies.** One canonical vocabulary plus a **committed translation table**, so
banked data stays interpretable without archaeology. Two constraints: no legacy label may be
reused with an altered referent (a label that changes meaning is worse than a new label, because
old readings stay syntactically valid while becoming false), and the table is **data the certifier
consumes**, not prose. Encoded: `LABEL_TRANSLATION`, `to_canonical()`, `check_no_altered_referent()`.

**R3 — the criteria generalize, they do not exempt.** Bit-identity of a returned dict was always a
proxy for the real invariant: **identical inputs produce identical observable outputs.** For
function sites the observable is the dict; for the five script sites it is whatever the
straight-line code emits — banked values, printed results, written files — bit-identical under
identical inputs, captured **before** migration. Exempting the five would exclude precisely the
stratum the extractor already missed once. Encoded: `OBSERVABLE_BY_SCOPE`, `migration_authorised()`.

**R4 — the unit is the decision.** A file is a storage convention. `run_analytical_nns.py:249` gets
its own row, verdict, and migration. Now stated in the inventory header so no future census
re-derives it. Encoded: `COUNTING_RULE`.

**R5 — COMPARE-DIRECTIVE scope.** Every `_ks_pvalue`-idiom quantity and kin is compared against a
threshold in the reconciled classifier; the threshold is a constant and is typed through
`classify_guard` (α = 0.05, convention unless derived). **The lineage finding travels with the
directive in the reconciled source** — `CLAUSE_8_LINEAGE_RECORD` — so no future reader has to
wonder whether clause 8 was editorial. It was not: the comparison is ancestral and was shed by
copying.

## 6. Reconciliation, per the standing check

`c3_sweep_reconciliation.json` (generator `cdbb6bd`, amended `adc5d26`). Seven counts, six
enumerated differences, all connected.

| | |
|---|---|
| inventory decisions | **20** across 19 files |
| sweep verdict rows | 19 by file → **15** units → **11** sealed distinct bodies |
| **unswept as a distinct unit** | **`run_analytical_nns.py:249`** (np.argmin; the file's single row cannot be attributed to it) |

**Denominator restated, not re-scored.** The sealed rate is **9 of 11 distinct def-extractable
implementations** — a stratum of 15 files and 15 decisions. It is **not** 9 of 11
classifiers-in-the-codebase, which is 19 files and 20 decisions. Quoting the stratum rate as a
population rate would repeat, in the presumption itself, the promotion that the extractor bias
already punished once. The sweep is not re-scored: retro-scoring under a later rule is what
Ruling 2 and Amendment 1 both refused, and the refusal does not weaken because the new number
would be less flattering.

## 7. Migration status: **NOT AUTHORISED**

`c3_rulings.migration_may_begin()` raises. Preconditions: sweep-row reconciliation **[done]**,
R3 artifact baselines **[not captured]**. Baseline before write — the one lapse of that rule this
arc cost 1159 records truncated to 3.

---

## 8. CORRECTIONS TO THIS DOCKET'S MEASURED BASIS — 2026-08-23

The rulings in §5 stand. What follows corrects the **measurements they were taken against**,
which is a different thing and is recorded separately so the distinction stays visible.

### 8.1 "No size guard at all at 3 sites" (§3 R1) is FALSE

Measured in `gate_census/c3_helper_axis.json`: **no site is unguarded.** `run_phase4`,
`run_controls` and `run_per_pll_nns` each call a KS helper carrying its own `n < 5` NaN sentinel.
The body-guard census saw only the outer layer. The real structure is a **two-layer lattice**:

| body guard | helper floor | sites |
|---|---|---|
| `sentinel:<50` | none | 7 |
| `sentinel:<5` | none | 4 |
| `sentinel:<5` | 5 | 3 |
| `sentinel:<50` | 5 | 2 |
| none | 5 | 2 |
| `enclosing:>0` | 5 | 1 |

The helper axis is one the two prior inventories **structurally could not see** — every axis they
measure is intra-body, so a divergence in a *called* function leaves no trace in the segment they
read. R1's ruling is unaffected: these constants are all still free, and silent inheritance is
still forbidden. R1's *basis* is corrected.

### 8.2 The population is **21** decision sites, not 20

`run_analytical_nns.py:297` was missed by both detection prongs — the KS values arrive as inline
`ks_to(...)` **calls** and the labels sit in the enclosing **subscript**. Found by an independent
reader of the file this docket certified complete. **Two** sites are now unswept as distinct units
(`:249` and `:297`).

### 8.3 The guard column was wrong in both directions within one hour

D1 scraped `.size < N` over the scope, which at module level is the whole **file** — so `:184`'s
`< 5` was attributed to `:249`, whose guard is `> 5` and **excludes** n=5. Two opposite guards
printed as the same value. The first repair read only *enclosing* conditionals, which lost every
def site's guard, since those are early-return **sentinels**. Guards now carry **kind and
operator** (`sentinel:<50`, `enclosing:>5`) so a bare number cannot represent two opposite
conditions again.

### 8.4 The pattern these three share

Each correction is the same shape at a different depth: **the extractor's structural assumption,
not the domain, defined what was missing.** Which files → which code counts as the classifier →
which syntax the values arrive in. Each was found only by widening the aperture *after* the
narrower measurement had been certified complete, and twice by a reader who did not build the
instrument. The standing check that came out of it is `countrecon.py`: two instruments counting
one population must reconcile or say why.

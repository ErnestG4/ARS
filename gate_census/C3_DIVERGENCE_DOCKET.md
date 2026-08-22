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

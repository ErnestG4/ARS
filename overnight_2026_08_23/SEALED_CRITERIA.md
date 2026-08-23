# OVERNIGHT 2026-08-23 — R3 ARTIFACT BASELINE CAPTURE

**Sealed before any baseline exists.** The single unit of work: capture the R3 observables that
`c3_rulings.migration_may_begin()` is currently blocking on. Nothing is migrated tonight.
Migration remains unauthorised at dawn regardless of outcome — capture is the *precondition*,
not the act.

---

## 1. What a baseline IS (the ruler, sealed with the prediction)

**Unit:** the DECISION SITE (R4). Twenty of them, per `gate_census/c3_inline_divergences.json`.

**Observable, by scope (R3, `OBSERVABLE_BY_SCOPE`):**
- `def` sites (15): the returned dict, `repr()` round-trip, bit-identical.
- `module` sites (5): what the straight-line code emits — printed lines, written files, and the
  assigned `best` label — bit-identical under identical inputs.

**Denominator:** 20 decision sites. Not 19 files, not 15 sweep units, not 11 bodies. Any rate
reported tomorrow is over 20 unless it explicitly names a different stratum, and if it names one
the difference goes through `countrecon`.

**Categorizer — the sealed verdict vocabulary.** Every site gets exactly one:

| verdict | meaning |
|---|---|
| `CAPTURED` | baseline captured **and** it discriminates (see §2) |
| `CAPTURED_INERT` | baseline captured but it does **not** discriminate — recorded, **not counted as captured** |
| `INFEASIBLE_DATA` | required input data absent from the repo |
| `INFEASIBLE_NONDETERMINISM` | reruns differ; no fixed-input form exists without editing the site |
| `INFEASIBLE_MUTATION` | capture would overwrite a banked artifact |
| `NOT_ATTEMPTED` | ran out of night; stated, never silently absent |

**Occurrence threshold:** a verdict is assigned per site, once. No site may be reported as a
fraction, and no verdict may be inferred from a sibling site's result — identical bodies still get
their own capture, because the point of a baseline is to catch the case where they stop being
identical.

## 2. THE DISCRIMINATION REQUIREMENT — a baseline is not a baseline until it can fail

A captured artifact that would not change when the site changes protects nothing. It is the
inert-arm defect wearing a new shirt, and this arc has already paid for that lesson three times
(`ASSERT_MIN_BLOBS` vacuous pass, the red-path that found zero pairs, `verify_c3`'s content arms
reading a regenerated file).

**So: every baseline must be mutation-tested at capture time.** For each site, a planted
perturbation is applied *to a copy*, the observable recaptured, and the two compared. If the
baseline does not change, the site is `CAPTURED_INERT`, not `CAPTURED`.

The planted perturbations, fixed here, before any are run — one per divergence axis the inventory
actually found, so the mutation set is derived from measured divergence rather than invented:

| axis | planted perturbation | must change the observable |
|---|---|---|
| D1 guard threshold | flip the site's `n < K` constant (50↔5, or insert 5 where absent) | yes, at inputs straddling K |
| D5 label vocabulary | `'Poiss'` → `'Poisson'` (or case-flip) | yes |
| D4 returned keys | drop one emitted key | yes (def sites only) |
| D2 comparison state | delete a comparison that gates output | yes where one exists |
| argmin outcome | swap two KS arguments so the winner changes | yes |

A site that survives **all applicable** perturbations unchanged is `CAPTURED_INERT`.
"Applicable" is decided by the inventory row, not by convenience, and a perturbation ruled
inapplicable must name why — `INAPPLICABLE`, never silently dropped from the denominator.

## 3. Input vectors must EXERCISE the divergence, not merely execute

A single input landing above every guard makes the 50/5/none fork invisible: every variant agrees,
the baseline is bit-identical everywhere, and it has measured nothing. **The input set must
straddle every guard constant in the population.**

Sealed input set — sizes chosen against the measured guards {none, 5, 50}:

- `n ∈ {3, 5, 8, 49, 50, 51, 200}` — straddles both 5 and 50 on each side, and includes n below
  any guard so the no-guard variants visibly diverge from the guarded ones.
- three distributions per size: Poisson-like, GOE-like, GUE-like unfolded spacings, plus one
  **non-member** (uniform on [0,3]) because a classifier with no rejection region is exactly what
  this population is known for, and the non-member is where that shows.
- fixed seed, stated in the generator; the seed is part of the ruler.

**Pre-registered claim about the input set itself:** at least one input pair must produce
*different* `best` labels across the 11 def variants. If all variants agree on every input, the
input set is too weak to be a baseline and that is a **failure of the ruler**, to be reported as
such rather than written up as "variants agree".

## 4. Pre-registered predictions

Committed before running anything. Scored tomorrow against §1's vocabulary.

| # | prediction |
|---|---|
| P1 | **15 of 15** `def` sites reach `CAPTURED` or `CAPTURED_INERT` (i.e. capture mechanically succeeds) |
| P2 | **≥12 of 15** `def` sites reach `CAPTURED` (discriminate under ≥1 applicable perturbation) |
| P3 | **≤2 of 4** module-level script files run reproducibly enough to reach `CAPTURED`; the rest land `INFEASIBLE_*` |
| P4 | the input set discriminates: **≥1** input on which def variants disagree on `best` |
| P5 | **≥1** site lands `CAPTURED_INERT` — I expect the mutation test to catch at least one baseline that looked fine |

P3 and P5 are the ones I expect to be wrong in an informative direction. P5 predicting a *failure*
is deliberate: a mutation test that catches nothing on twenty sites is more likely to be a broken
mutation test than a clean population, given this arc's base rates.

## 5. Hazards, named before they can be discovered mid-run

- **No script may be run in a way that writes into the repo.** The four module-level files emit
  artifacts; capture runs in a scratch copy with a scratch CWD. Precedent: a `--limit 3` flag once
  truncated `pvc-11.jsonl` from 1159 records to 3. A capture that mutates its subject is
  `INFEASIBLE_MUTATION`, and finding that out by doing it is not acceptable.
- **No site file is edited.** Mutation testing operates on copies in scratch. The repo working
  tree stays clean; `git status` is checked after every capture phase.
- **Frozen blobs.** Files under a blob-SHA freeze belong to their arcs. A site under a freeze is
  registered as a proposal, not touched — the `bridge/dpp_python.py` precedent.
- **Exit codes** are read via `checkrun.sh`, never after a pipe.

## 6. What tomorrow's report must contain

1. All 20 sites, each with exactly one §1 verdict, and no site absent.
2. Every prediction P1–P5 scored, including the ones that missed, with the miss stated first.
3. The mutation-test results per site, including which perturbations were `INAPPLICABLE` and why.
4. Any count reported alongside another count over the same population goes through `countrecon`.
5. `migration_may_begin()` still raises unless **every** site is `CAPTURED` — partial capture does
   not unblock migration, and a partial gate that reports as a full one is the defect named in
   `gate_certifies_half_say_so`.

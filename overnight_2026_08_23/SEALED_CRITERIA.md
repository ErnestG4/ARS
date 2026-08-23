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

---

# AMENDMENT 1 — 2026-08-23, before any baseline exists

Two independent adversarial reviews ran against the sealed criteria while the harness was being
built. Both found defects in the criteria themselves. Amending now, with reasons, is the honest
move: **no baseline has been captured, so nothing is being re-scored** — but the amendment is
recorded rather than folded silently into the original text, because a ruler edited after seeing
results is not a ruler, and only the commit graph can tell those two situations apart.

## A1.1 — the denominator is **21**, not 20

A **21st decision site** exists: `run_analytical_nns.py:297`. It is
`['Poiss','GOE','GUE'][int(np.argmin([ks_to(x, cdf)[0], ...]))]` — the KS values arrive as inline
**calls**, and the labels sit in the enclosing **subscript**. Both of the census's detection prongs
assume the values arrive as named variables or that the labels sit inside the `min`/`argmin` call.
Neither held.

This is the arc's blind-spot lesson for the **third** time, one level further in each time:
which **files** the extractor reaches → which **code** counts as the classifier (the D7 helper
axis) → which **syntax** the values arrive in. Each time the missing region was defined by the
extractor's own structural assumption rather than by the domain. Each time it was found by
widening the aperture *after* certifying completeness.

Consequences: 21 decision sites; **2** unswept as distinct units (`:249` and `:297`); the R4
counting rule now states how values may reach a decision, because that assumption left implicit is
what hid this one.

## A1.2 — D1 was measured wrong, in both directions, within one hour

The guard column scraped `.size < N` over the scope — which at module level means the whole
**file**, so `run_analytical_nns:184`'s `< 5` was attributed to `:249`, whose guard is `> 5` and
**excludes** n=5. Two opposite guards printed as the same value. The first repair read only
*enclosing* conditionals, which lost every def site's guard, since those are all early-return
**sentinels**. Guards are now GOVERNING and carry both **kind** and **operator**:
`sentinel:<50`, `enclosing:>5`. A bare `5` cannot represent two opposite conditions again.

## A1.3 — the input set widens (the ruler was too weak to see its own targets)

Sealed sizes were `{3, 5, 8, 49, 50, 51, 200}`. Added, each for a named reason:

| added | why |
|---|---|
| `n=0` | `universality.py:129` carries a `==0` sentinel no other site has; without n=0 that branch is never observed |
| `n=4` | `< 5` versus `<= 5` differ on exactly one input, and it is not 5 |
| `n=6` | the only size strictly between the helper floor and the 5-guard's neighbourhood |
| `n=30` | mid-band 5≤n<50, where guard-50 sites return `insufficient` and guard-5 sites return a full dict — **the** discriminating band for the R1 fork |

Added family: **`clock`** — all spacings exactly 1.0. The perfect clock reads GUE through this
gate (the RIGID_GUE failure reached by another route) and is the calibrated `fit_poor=True` case;
without it the `fit_poor`/`fit_rejected` keys are captured on one side only, which is the
one-sided-calibration defect reappearing inside the instrument built to audit it.

## A1.4 — three limits on what the module-site baselines can certify, stated now

1. **`run_analytical_nns`'s `p_o/p_p/p_u` have no observable at all** — computed, never printed,
   never written. A migration that drops or corrupts them yields a byte-identical baseline. These
   are exactly the quantities R5 promotes, so the baseline is structurally blind to the thing this
   stratum was flagged for. Recorded per-site as `OBSERVABLE_ABSENT`, never as a pass.
2. **The guardless paths are unreachable by running the scripts.** `run_controls:217` and
   `run_per_pll_nns:138` operate on banked signals of fixed size, so the no-guard NaN path never
   executes. Migrating them onto a guarded classifier is a policy change the baseline would certify
   as "no change".
3. **One trajectory only.** Each script's multi-branch verdicts exercise one branch per run. The
   baseline certifies that trajectory and nothing else, and says so.

## A1.5 — capture hazards, promoted to blocking

- **Per-site helper extraction is mandatory.** Injecting one canonical `ks_to` is silent at
  `run_phase4`, whose helper returns `(ks, n)` while others return `(ks, p)` — the second element
  is discarded, values agree today, and the baseline would certify a function wired to a helper the
  site does not use. Each site's own helper is extracted alongside its classifier; only `np` and
  the genuinely shared `nns_cdf_*` are injected.
- **`universality.py:129` needs full-precision serialisation.** It returns a dataclass whose
  `spacings` field is an ndarray; `repr()` summarises above ~1000 elements and truncates to 8
  significant digits below, so a low-order-bit change passes. Its observable is field-wise
  `float.hex()` plus a hash of `tobytes()`.
- **PNG/JSON overwrite.** The three module scripts unconditionally overwrite plots that are **not
  in git**, and `run_lmfdb_family` rewrites a 3.2 MB untracked data file. Any script run archives
  hashes and copies first, or the site is `INFEASIBLE_MUTATION`. This is the `--limit 3` shape and
  it is the reason §5 exists.
- **Exit status is part of the observable.** `run_analytical_nns` imports `cupy` mid-file, after
  site `:184` has already printed. A GPU-less box emits the `:184` table and dies — banking that
  stdout captures a baseline in which `:249` and `:297` **do not exist**, and a post-migration run
  that also dies "matches". Capture requires exit 0 **and** sentinel lines for every site in the
  file.
- **Inputs must be pinned.** R3's invariant is conditional on "identical inputs", and the data
  files are untracked. The baseline embeds sha256 of every input file it read, plus library
  versions. Otherwise a regenerated cache diffs the comparison for input reasons and the natural
  response — recapture — launders any concurrent behavioural change.

## A1.6 — predictions, restated against the corrected denominator

P1–P5 stand as written, with P1 and P2 now over **16 def sites** (15 + `universality:129`, which
the original text miscounted as module) and P3 over the same 4 script files. **P6 is added:**
at least one site will land `OBSERVABLE_ABSENT` — `run_analytical_nns`'s p-values are already known
to, so P6 is scored as a check that the harness *reports* it rather than as a discovery.

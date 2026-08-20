# BRIEF — Consolidating the 19 `classify()` copies

**Status:** DRAFT, authored 2026-08-19. **Not executed.** Deliverable of C3 was the brief.
**Posture:** refactor with real regression risk against banked outputs. Not an overnight.

## The problem

`arithmetic_toolkit._classify` assigns a spectral class by `min()` over three KS distances with **no
rejection region** — measured: 7/7 non-member distributions receive a confident label, every best fit
rejected by a standard KS test, and **a perfect clock reads GUE**. It was repaired 2026-08-19 to
expose `best_ks` / `fit_poor` while leaving `best` and every pre-existing key bit-identical.

**That repair reaches 1 of 19 call sites.** Nineteen files define their own copy rather than importing
it (found by structure — argmin over a Poisson/GOE/GUE KS triple — *and* by value: the distinctive
`'Poiss'` short string and the `nns_cdf_*` triple computed together, since a paraphrased copy that
dodges a structural grep usually still carries the constants):

`run_lmfdb_family` · `run_controls` · `run_fungal_nns` · `run_mertens_liouville` · `run_eeg_full` ·
`run_lmfdb_postprocess` · `run_dirichlet_family` · `run_zeta_height_convergence` · `run_phase5` ·
`run_eeg_depth` · `run_phase4` · `run_analytical_nns` · `run_earthquake_nns` · `run_lmfdb_extend` ·
`run_per_pll_nns` · `universality.py` · `run_lmfdb_edge` · **`verify/tier1_lfunction_guard.py`**

## Why this is a refactor and not a cleanup

`verify/tier1_lfunction_guard.py` marks its copy **`VERBATIM run_lmfdb_family.py:88-104`** — a
*deliberate* mirror, so the guard reproduces banked numbers bit-identically. That is correct practice,
and it is exactly how the blind spot propagated into a verifier. **Any consolidation must preserve
the property the mirror exists for**, which is why the acceptance criteria below are bit-identity
rather than "tests pass".

*(Precedent from this session: an attempt to add reporting keys to `bridge/dpp_python.py` broke that
arc's blob-SHA freeze and was reverted. Frozen files belong to their arcs — expect the same here and
budget for it rather than discovering it mid-refactor.)*

## Acceptance criteria — bit-identity, not green tests

For **every one of the 19 call sites**, on its own banked inputs:

1. `best`, `gap`, `ks_p`, `ks_o`, `ks_u`, `n`, `mass03` **bit-identical** to pre-refactor output
   (`repr()` round-trip, not `np.isclose`).
2. `fit_poor` / `best_ks` **newly present** — the point of consolidating.
3. Class-label vocabulary preserved per site: `run_mertens_liouville` emits `'Poiss'`, others
   `'Poisson'`. **Do not normalise this** — banked artifacts contain both spellings and normalising
   changes banked strings.
4. `MIN_N_FIT` / `pooled.size < 50` thresholds preserved per site; they differ (`_classify` uses 5,
   `tier1_lfunction_guard` uses 50).
5. Baselines snapshotted and committed **before** the refactor begins, hashed and pinned in the
   acceptance checker, per the C2 pattern.

## Sequencing

1. Snapshot + commit baselines for all 19 (read-only).
2. Write the acceptance checker; commit it **before** touching any call site.
3. Migrate sites one commit at a time, checker green after each. **A site whose file is under a
   blob-SHA freeze is stopped and registered as a proposal, not edited.**
4. `verify/tier1_lfunction_guard.py` **last** — it is a guard, and it should be migrated only once the
   shared implementation has been proven bit-identical on the other 18.

## Copy census as appendix — so a twentieth is detectable

The detector is a two-pronged grep: structure (`min([...])` over a KS triple) **and** value (`'Poiss'`,
`nns_cdf_goe`). Committed as `gate_census/` output. **Run it after consolidation**; a non-zero count
that is not the shared module is a new copy.

## Out of scope

Changing any classification. The repair adds a refusal *signal*; it does not demote rows. The 936-row
fit-quality work list is triage input and is handled separately, under the Q3 theorem — a poor fit
costs a row its class, never changes it.

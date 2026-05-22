# Claude Code Task Brief — Landscape Coordinate Computation, Initial Population

**Status:** brief-and-hold. Brief sign-off ≠ compute-go. Will explicit "go" required before compute starts.
**Date:** 2026-05-22
**Companion docs:** `./cross-substrate/landscape.md`, `./cross-substrate/viewpoints.md`

---

## §1 — Read first

Before any implementation work, read both companion docs in order:

1. `./cross-substrate/landscape.md` — substrate catalog, analytical-angle catalog, substrates × angles matrix, methodological notes. Provides the framing: operator-IS-substrate, cross-substrate landscape-mapping, explorer-shaped methodology.
2. `./cross-substrate/viewpoints.md` — candidate coordinate axes (individual + sets), substrate-applicability matrix, computation specifications, banking format.

These are the grounding documents for everything in this task. The methodological commitments in landscape.md §6 (extraction artifacts, multi-scope reads, matched-instrument protocol, L_iter lesson) and viewpoints.md §1 (no premature axis commitment, compute breadth) hold throughout.

---

## §2 — Primary task

**Implement candidate coordinate computations specified in `viewpoints.md` §5, apply to substrates with existing data, and populate the landscape matrix (`landscape.md` §5) with banked coordinate values.**

Two substrates have existing data ready for retroactive characterization:

- **AM (almost-Mathieu)** — Phase 35 artifacts across multiple cells.
- **pvc-11 V1** — Phase 22a/22b/24/25/26 artifacts.

This is post-processing of existing event-train data. No new substrate generation required for the initial pass.

---

## §3 — Specific subtasks

### Subtask 3.1 — Implement applicable axes

Implement the computation functions for axis families I, II, III, VI per `viewpoints.md` §5. Family IV (spectral character) and Family V (dynamical) are deferred for the initial pass — both require substrate-specific methodological decisions (what's V1's spectral measure? what's a Lyapunov exponent for a spike train?) and aren't necessary for the AM + V1 initial population.

Priority order within the initial families:

1. **Family I (NNS distances).** Most universal; smallest implementation; baseline coverage. All nine axes (I.1 through I.9).
2. **Family II (long-range NNS).** Σ²(L) and Δ₃(L) at substrate-matched L values (II.1, II.2). K(τ) and R₂ shape (II.3, II.4) lower priority if II.1/II.2 land first.
3. **Family III (RF arithmetic).** Use existing ARS RF engine output where possible. III.1 (per-prime concentration) for small primes p ∈ {2, 3, 5, 7}; III.4 (scalar reduction) using a defensible choice (e.g., sum over small primes, or max over small primes) — flag the reduction choice for Will's review.
4. **Family VI (extraction-meta).** VI.1 (L_iter convergence rate) and VI.2 (N-scaling exponent) computable from Phase 35 chain data; VI.3 (cross-extraction variance) requires multiple extraction-method runs not all done — flag what's available.

Each axis implementation should be a pure function taking event-train input (with substrate-appropriate metadata) and returning a scalar (or vector for III.2-type axes), with consistent error/N/A returns for cases where the axis doesn't apply or data is missing.

### Subtask 3.2 — Apply to AM cells

Compute applicable axes for the AM cells characterized in Phase 35. Relevant artifacts (Will to confirm paths in repo):

- **N=50k sup at L-converged** — Tier 2 artifact box6iq1j4; commit 928c0a4.
- **N=70k sup at L-converged** — Test 2 artifact bo73me0uq (5.6h L-extension); also b0haqgof3 for φ-resolved baseline.
- **N=100k sup at L-converged** — Tier 2 artifact bsvv0q6tz; commit d069ec8.
- **N=70k sub** — Test 3 artifact (commit 7a66ff6) at L=6.4×10⁶; substrate not L-converged (per rev-5.2.1) — flag accordingly.
- **N=125k sub** — Test 3 artifact (commit 7a66ff6); substrate not L-converged.
- **N=100k sub** — bh22pfzoa at L=1.6×10⁶ (L-converged sub-side at this N).

For each cell, compute all applicable axes (per viewpoints.md §4 row for AM). Substrate-side metadata: (δ, λ, θ-class, φ) parameters preserved per cell.

VI.1 (L_iter convergence rate α): use the L-sweep data available per cell. Note rev-5.2.1 finding that α can be L-range-dependent — flag where it is (N=70k sub is the known case; check others).

VI.2 (N-scaling exponent β): linear fit on log(L-converged sup spread) vs log(N) across the three sup cells (0.115, 0.382, 0.847 at N ∈ {50k, 70k, 100k}). Report β with confidence interval.

### Subtask 3.3 — Apply to pvc-11 V1 cells

Compute applicable axes for pvc-11 V1 units characterized in earlier work. Existing fingerprint metrics from H1 (ks_gue_med per unit) and H2 (surrogate-survival metrics) already available — fold into axis I.5 directly.

Compute additional axes (I.1-I.4, I.6-I.9, II.1, II.2, applicable III axes) on the unit-level event trains. Substrate-applicability per viewpoints.md §4 row for pvc-11 V1.

Cell-id convention: unit-id within session-id. Bank per-unit coordinates so cross-unit cluster structure within V1 becomes visible (in addition to across-substrate structure).

### Subtask 3.4 — Bank coordinates

Output format per `viewpoints.md` §6 — per-substrate-per-cell-per-axis records with applicability metadata.

Implementation choice:

- Lightweight: JSON-lines (one record per line, file per substrate) under `./cross-substrate/coordinates/`. Simple to read, simple to extend.
- Alternative: SQLite DB if cross-substrate queries become unwieldy. Flag if you reach that point.

Each record must include:
- substrate, cell_id, axis name + value pairs
- applicability metadata (axes not applicable, axes applicable but not computed, reasoning)
- source artifact reference (hash, commit, file path)
- extraction method + audit (e.g., unfold_rotnum + L_iter convergence audit for AM)
- computed_date

### Subtask 3.5 — Update landscape.md §5 matrix

Populate the substrates × angles matrix entries from blank → done where computation lands. Use marker convention from `landscape.md` §5 (✓ done, ◐ partial, ○ planned, — N/A).

Don't restructure landscape.md beyond the matrix updates and any necessary corrections to substrate-applicability claims revealed by implementation work.

### Subtask 3.6 — Flag findings

Bank any methodological observations that come out of implementation work:

- Axes that turn out to be ill-defined or implementation-ambiguous → propose specification refinement.
- Substrates that turn out to need methodological work before axis computation is meaningful → flag in landscape.md §6 or §8.
- Cross-substrate matched-instrument issues that come up (e.g., what L value to use for Σ²(L) across substrates with different scales) → flag for Will's adjudication.
- Surprises in the coordinates (e.g., AM and V1 land surprisingly close on some axis) — flag for Will's review without prejudicing interpretation.

---

## §4 — Discipline notes

### Multi-axis breadth, not narrow focus

Per `viewpoints.md` §1: compute all applicable axes per substrate. Resist the temptation to focus on "the most informative" axes — that's a hypothesis-shaped move, premature for this stage. Breadth now; selection later from cluster structure across many viewpoints.

### Substrate-applicability honesty

Per `viewpoints.md` §4: some axes don't apply to some substrates. Mark non-applicable cells as such; do not stub with zeros or sentinel values that could be mistaken for measurements. The N/A status is itself substrate information.

### Multi-scope, not point-as-substrate

Per `landscape.md` §6: substrates can move across regions at different scales. AM's N-trajectory (N=50k → 70k → 100k cells) is exactly this. Bank cells separately; do not collapse to a single per-substrate value unless explicitly summarizing.

### Brief-and-hold

This brief authorizes scope; it does not authorize compute. Will sees the brief, signs off on scope, then explicitly signals compute-go. Any drift from this brief's scope during implementation pauses for Will's input. If implementation reveals the brief's scope is wrong or incomplete, flag it as a brief revision rather than proceeding with scope drift.

### Cost-cap discipline

Per Phase 35 precedent: per-step cost budget; cost-cap trigger if elapsed time approaches plan limit; halt + report rather than overrunning budget silently. Reasonable initial budget for this task: 4-8 hours, since it's post-processing not generation. Flag if any subtask exceeds 2 hours individually.

### Cite, don't invent

Where Phase 35 commits or artifact hashes are referenced in this brief, verify the references against Will's codebase before relying on them. Where references are wrong or stale, flag and ask Will rather than confabulating substitutes.

### Cross-substrate matched-instrument

Per `landscape.md` §6: cross-substrate comparison requires matched preprocessing. For axes requiring substrate-side parameter choice (e.g., L value in II.1 Σ²(L)), propose a substrate-matched convention (e.g., L as fraction of event count, or L at fixed physical scale) and apply consistently. Flag the choice for Will's review.

---

## §5 — Output destinations

- **Coordinate values.** `./cross-substrate/coordinates/{substrate}.jsonl` (or DB if needed).
- **Axis implementation code.** Within the `criticality_tool` codebase (or wherever ARS post-processing lives); propose path and structure if not obvious.
- **Updated landscape.md §5 matrix.** In-place edit of `./cross-substrate/landscape.md`.
- **Implementation notes.** `./cross-substrate/implementation_notes_v0.md` — methodological observations from implementation work; refinements to viewpoints.md proposed but not made (Will's edit, not Claude Code's).
- **Findings log.** `./cross-substrate/findings_log.md` — substrate-observations that come out of coordinate computation; written conservatively, no over-interpretation.

---

## §6 — What this brief does NOT authorize

- Generating new substrate event-train data (e.g., new AM L-sweeps, new V1 acquisitions, Mackey-Glass simulations, FM event-train derivation work). All of those are separate briefs.
- Restructuring landscape.md or viewpoints.md beyond §5-matrix population.
- Deciding the "winning" axis set or viewpoint — initial population is broad coverage, not winnowing.
- Cross-substrate comparison claims based on initial coordinates — flag interesting observations, don't draw conclusions.
- Retiring or proposing retirement of any candidate axis based on initial computations — too early.

---

## §7 — Reporting back

After implementation + initial population:

- Per-substrate summary: how many cells × how many axes computed; what's banked; what's flagged.
- Matrix update summary: what cells in `landscape.md` §5 transitioned from blank to populated.
- Methodology flags: ambiguities, refinement proposals, cross-substrate matched-instrument decisions.
- Surprises log: anything that landed unexpectedly (without interpretation).
- Cost report: time spent per subtask; any cost-cap triggers; any subtasks deferred.

Will reviews the report, decides next moves (slate 4 reframed, next substrate, viewpoints.md refinements, etc.).

---

## §8 — Open items / Will-to-confirm

Items requiring Will input before implementation lands:

1. **Phase 35 artifact paths.** Confirm where bo73me0uq, bsvv0q6tz, box6iq1j4, 7a66ff6, bh22pfzoa, b0haqgof3 are stored in the criticality_tool repo (or wherever AM event-train data lives).
2. **pvc-11 V1 data path.** Confirm where Phase 22a/22b/24/25/26 V1 event-train artifacts are stored.
3. **III.4 scalar reduction choice.** What scalar reduction to use for RF p-adic spectrum (sum over small primes, max, PCA, etc.).
4. **II.1 L choice.** What L value(s) to use for Σ²(L) computation across substrates with different scales.
5. **Compute budget.** Confirm 4-8 hour initial budget is appropriate.
6. **Coordinate storage format.** JSON-lines vs DB vs other.
7. **Code path.** Where in criticality_tool (or elsewhere) the axis-computation module should live.

---

**Brief sign-off:** Will reviews, adjusts §8 items, says go. Compute proceeds within scope. Implementation report + findings come back; next brief follows.

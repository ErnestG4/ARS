# Buzsáki CA1 framework-port — overnight brief (RATIFIED 2026-05-25)

**Status:** RATIFIED 2026-05-25. Decisions below; executing probe-1-session → full-3 → full-8-if-time.

## Ratified decisions
1. **H1-analogue battery:** spatial-information (bits/spike, primary) + theta phase-locking MRL (LFP) +
   burst index + mean rate. (Theta INCLUDED.)
2. **Sessions:** remaining-5 download started in background; begin 3-session work now; extend to full 8 if
   the 3 finish in time.
3. **Run staging:** probe 1 session (validate H1-analogue extraction + natural-cell factorisation) → full.
4. **Stratification — NATURAL CELLS primary, marginal-with-caveat secondary** (EPOCH×STATE is structurally
   confounded; marginal η² would average over biologically-different conditions). Cell-type orthogonal layer.
   - **Natural cells (primary):** PRE-NonREM, PRE-REM, Maze-Awake, POST-NonREM, POST-REM, + Awake-in-sleep
     (disentangle-control: brief wake within sleep blocks). Each a biologically-interpretable condition,
     analysed the way the hippocampus literature does.
   - **Cell-type × natural-cell** ≈ 10–12 cells; pyramidal/interneuron orthogonal.
   - **Named biological contrasts** (the confound-disentangling questions, cross-referenceable to the
     replay/consolidation literature):
       • PRE-NonREM vs POST-NonREM — NonREM consolidation (the classic replay contrast)
       • PRE-REM vs POST-REM — REM consolidation
       • Maze-Awake vs Awake-in-sleep — wake-state effect, partial epoch control
       • all-NonREM vs all-REM (across epochs) — state effect, mixing PRE/POST
   - **Marginal (secondary):** η² on EPOCH and STATE separately, confound flagged explicitly — for
     format-comparison to Allen's area×stimulus only; marginal interpretation constrained by design.

## Frame
The cross-substrate fingerprint framework was hardened on Allen (mouse visual cortex): per-cell + population
fingerprints, the structural-high / biological-signal / structural-low population hierarchy, the rate-match
de-confound, temporal-stationarity, the discriminant-exact-question discipline. This brief applies the
**identical tooling** to CA1 hippocampus (Grosmark & Buzsáki 2016, DANDI 000044; 3 sessions: Achilles×2,
Cicero×1; rCA1/lCA1, 137+ units/session, exc/inh labels, STATE + EPOCH + position + LFP). The question is
**generalization**: do the Allen cross-substrate findings hold in a non-sensory circuit, or were they
sensory-cortex-specific? Fair-comparison is the whole point — hippocampus-specific analyses are OUT of scope
for this cycle (they answer different questions; they become richer with the framework baseline in place).

## Goals (the 4 cross-reference questions)
- **G1 — Population fragmentation hierarchy in CA1.** Do the 3 trustable observables show the same
  structural-high (corr-eig ~GUE-invariant) / biological-signal (avl-onset, structured+stationary) /
  structural-low (sync-event Poisson-invariant) hierarchy? Or does CA1 reorganise which observable carries
  the signal?
- **G2 — H1-analogue.** Is there a CA1 per-cell SELECTIVITY property that correlates with per-cell ks_gue —
  the hippocampal analogue of OSI↔ks_gue? Candidates: spatial information (bits/spike) on the maze [primary,
  the canonical "what makes a CA1 cell selective"], theta phase-locking strength (MRL), burst index.
- **G3 — State/epoch effect.** Does the biological-signal observable's q vary by STATE (Awake / Non-REM /
  REM) and/or EPOCH (PRE-sleep / Maze-run / POST-sleep) the way it varied by AREA in Allen? Same
  population-level methodology, different stratification dimension; rate-matched de-confound from the start.
- **G4 — Cell-type stratification.** Does fingerprint position differ for pyramidal (excitatory) vs
  interneuron (inhibitory)? A within-substrate axis Allen mostly lacked.

## Acceptance (verdict vocabulary, per goal)
Each goal resolves to GENERALIZES (same structure as Allen) / DIVERGES (different structure, characterised) /
SUBSTRATE-SPECIFIC (no Allen analogue), with the explicit discriminant stated. Null/underpowered is a valid
verdict given n=3 sessions. No interpretation beyond the flagged structure — verdicts are Will's.

## Out of scope (deferred to cycle 2 — hippocampus-specific)
Theta-gamma cross-frequency coupling (Colgin); replay-event detection + sequence statistics; place-field
geometry / remapping; sharp-wave-ripple analysis. These are not framework-port; they get the framework
baseline as context first.

## Methodological commitments
1. **Fair-comparison (load-bearing).** Same observables (corr-eig / avl-onset / sync-event), same ars_classify,
   same Family-I/II axes, same dt=25 ms, same MIN_UNITS=30, same _fp as Allen. NO mid-substrate methodology
   changes. Whatever the framework did in Allen, do identically in CA1.
2. **Rate-match de-confound from the start** (population-level recipe: match unit-count + total spikes within
   each recording before calling any state/epoch/cell-type/hemisphere effect biological).
3. **Temporal-stationarity tracked** (early/late split) for any structured observable.
4. **Discriminant-exact-question / cheap-proxy discipline** — especially on auto-verdict labels (the corr-eig
   "DRIFTS" mislabel burned this in last cycle); report ρ + within-vs-between, not just a threshold tag.
5. **Interpretive frame:** structural-high / biological / structural-low hierarchy as the reference.
6. **Observable-binding:** CA1 spikes are a point-process substrate like Allen ⇒ the spike-time/population
   observables port directly (no Cantor/box-dim issue here).
7. **n caveat flagged:** 3 sessions vs 12 in Allen. Per-cell n is large (137+ units × states × epochs); but
   population-level cross-session statistics (Kendall W etc.) are underpowered — report n_groups, lean on
   per-cell + within-session where the population n is thin. (5 more Grosmark sessions available if needed.)

## Concrete build plan
- **`buzsaki_port.py`** — per-cell fingerprints (ks_gue + Family I on per-cell spike-times) + the 3 population
  observables, stratified by EPOCH × STATE × {cell_type, hemisphere}. Stratification cells = concatenated
  intervals of a STATE within an EPOCH (e.g. POST-NonREM, POST-REM, Maze-Awake, PRE-NonREM…). Reuses
  ars_classify + population_fingerprint observables + _fp verbatim.
- **`buzsaki_selectivity.py`** — per-cell H1-analogue properties: spatial information (bits/spike) from
  linearized maze position during Maze epoch; theta phase-locking MRL from LFP (if included); burst index;
  mean rate → correlate each with per-cell ks_gue (the H1-analogue search).
- **`buzsaki_port_analysis.py`** — the 4 goals' readouts (fragmentation hierarchy table; H1-analogue
  correlation sweep; state/epoch Kendall-W + rate-matched; cell-type contrast) + figures.
- Interpreter: `/home/combust/fmexplorer/bin/python3` (has h5py 3.16 + the ARS modules), 10 workers.

## Discussion items (resolve before ratify/execute)
1. **H1-analogue properties:** lead with spatial-information (bits/spike) as the primary OSI-analogue; include
   theta phase-locking MRL and burst index as secondary? Or is theta phase-locking too hippocampus-specific
   for the port (it edges toward cycle-2 territory)?
2. **Stratification factorization:** EPOCH × STATE is partly confounded (Maze≈Awake; REM/NonREM live in sleep
   epochs). Propose the natural cells (PRE-NonREM, PRE-REM, Maze-Awake, POST-NonREM, POST-REM). Confirm, or
   prefer EPOCH and STATE as separate marginal axes?
3. **Per-cell fingerprint window:** compute per-cell ks_gue per (epoch×state) cell (parallel to Allen
   per-stimulus), or one per-cell value over the whole session? (Per-condition is the fair parallel.)
4. **n / power:** start with 3 sessions, or pull the other 5 Grosmark sessions first for population-level
   power? (3 is enough for per-cell + within-session; thin for cross-session Kendall-W.)
5. **Scheduling:** single overnight run, or stage as a probe (1 session, validate the H1-analogue + state
   factorization) → then full 3-session run?

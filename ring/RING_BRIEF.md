# ring/ — Stage 0 + Stage 1 brief (2026-09-16)

Companion to `rotational-dynamics-build-plan.md` (v5). This is the executable
scope for the first arc; the plan is the standing document.

## Frame

The plan's v3 carried three defects that the ARS vocabulary names as numbered
failure modes (C1 sign inversion via rival rule; C2 collision with the banked
EC/CA3 bounded-negative; C3 an identity-map null). v4 retracted them; v5
applied six stale items after a second pass. Stage 0 is a **port**, not a
build: the verification layer at the repo root is inherited by placement in
`criticality_tool/ring/`, and the one forcing constraint — `verify_seal_order.py`
is a commit-graph property — is why this is a subdir and not a sibling repo.

Prior state on the ARS side that bounds this arc:
- **phase30** (Kuramoto → ARS): BR_artifact at every K; excluded from the zoo
  on **redundancy** with `periodic_q7` / `uniform_jitter`.
- **EC/CA3 attractor arc** (2026-05-28): attractor topology is not a
  spike-train-fingerprint property; ARS cannot resolve it per-cell by
  construction.
- **NEGATIVE_HALFLINE**: hc3-port Σ²(5)=43.1, allen-hpf 183.5 — super-Poissonian;
  Cox at 45.4 already sits on the hippocampal number.

## Structural-null audit (front-loaded)

Two analysis objects, two generative families, two right nulls:

| object | family | right null | status |
|---|---|---|---|
| per-unit spike trains off the ring | **rate-modulated (Cox)** — a unit under a passing bump is a doubly-stochastic process | matched-envelope Cox: same rate envelope, no attractor | measured at Σ²(5)=45.4; QUEUED arm |
| population-vector cloud → PH | **marginal cloud shape** — PH is order-blind | (a) di Sarra construction: independent oscillation-modulated Poisson on S¹, no recurrence; (b) pinned ring: attractor, no continuum | (a) published + code; (b) built this session at ε=0.1 |

The wrong null for both is rate-matched Poisson; it is not used anywhere in
this arc as the null of record.

## Goals

1. **Stage 0 port.** Every detector the arc will report is declared in
   `detectors.py` with its negative set and nearest confusable before it is
   built; the board (`verify_ring.py`) refuses a declared-only detector that
   reads as certified. Torch is guarded and the guard is tested.
2. **Stage 1, measure 1 — marginal stability along the ring, and where the
   heterogeneity dial destroys it.** Banked table over ε × T with the ε=0 row as
   the instrument floor.
3. **Stage 1, measure 2 — PH H₁ rank 1 on the population cloud**, through the
   jitter ladder, the within-cell ISI-order scramble, and the subsetting sweep.
   *Not this session*: no PH library is in the venv (ripser/gudhi/persim all
   absent); adding one is a declared venv change, made next session.

## Methodology

- Model: Ben-Yishai ring, N=128, `W = (J0 + J1 cos Δθ)/N`, J0=−2, J1=4, I0=1,
  smooth gain `β·softplus(u/β)`, β=0.1. **Threshold-linear was rejected for the
  instrument**: its fixed-point Jacobian is one-sided at the active-set edge
  and read λ₁ = ±1.7e-3 for a bump that did not move in 200τ (drift 1e-15).
- Dial: fixed per-unit input bias `ε·ξᵢ`, ξ ~ N(0,1) seed 1;
  ε ∈ {0, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1}; T ∈ {200, 2000}τ; B=16 bumps
  per batch at **off-grid** starting angles (on-grid starts sit on exact
  symmetry points and never see pinning).
- Reads: λ₁, λ₂ (Jacobian spectrum); `relax_rate` (displace the bump 0.05 rad,
  integrate 50τ, log-ratio — no linearisation); `n_distinct` final positions;
  `drift_median`; `resid_max` (is it a fixed point).
- Instrument sealed via `modelparams.Model` in the generator; 2 TESTED, 8 DECLARED.
- Generator-before-output via `sealgen.sh`; outcome claims only with CHECKRUN lines.

## Acceptance criteria (board rows R0–R7 in `verify_ring.py`)

- **PASS**: all eight rows green — guard real; specs construct; floor at
  |λ₁|<1e-12, drift<1e-9; λ₁ strictly decreasing with ε; ε=0.1 row converged
  (resid<1e-8) and collapsed (n_distinct ≤ B/2); spectral/dynamic agree within
  20% on the converged row; n_distinct differs across T at some ε; built
  detector two-sided-correct with the nearest confusable silent by >10×.
- **SOFT PASS**: R5 (T-dependence) is the only red — the sweep is too short to
  show it; extend T, do not lower the bar.
- **FAIL**: R6 red — the detector fires on the weakly pinned ring, or the
  confusable is silent only via the convergence gate and not via λ₁. That is a
  one-sided calibration and the threshold is redrawn against the table, never
  the other way.

## Out of scope this session

PH (no library); Stage 2+; spikes off the ring and the QUEUED ring→ARS
instrument bound; any population-level claim.

## Deliverables

1. `rotational-dynamics-build-plan.md` v5.
2. `__init__.py` (guarded torch), `ringnet.py`, `detectors.py`, `verify_ring.py`.
3. `stage1_marginal.py` (sealed generator) → `stage1_marginal_measured.json`.
4. This brief; RESULTS.md §7.ter row deferred until measure 2 lands (one
   commit per phase convention).

## Open questions carried forward

- Collapse threshold vs T: drift is ≈ linear in ε·T at small ε (5.9e-4 rad at
  ε=1e-4, T=200 → 5.9e-3 at T=2000). A collapse "threshold" is therefore an
  ε·T contour, not an ε. State it that way when it is banked.
- Which PH library, and whether zigzag needs a second one.
- Where the QUEUED arm's "which calibrator is each dial setting redundant with"
  column is computed — `extractor_distinctness` machinery or a new panel.

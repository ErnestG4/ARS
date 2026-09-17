# ring/ — Stage 0 + Stage 1 brief (2026-09-16)

Companion to `rotational-dynamics-build-plan.md` (v5). This is the executable
scope for the first arc; the plan is the standing document.

## Superseded claims (read first; grep before citing)

**S1 — RETRACTED 2026-09-16.** *"At ε=0.1, T=2000 the spectral (−λ₁ = 1.49e-2)
and dynamic (1.57e-2) reads agree to 5%"*, cited as the cross-check paying for
itself. Made in: commit message `ff4f786` (immutable — this block is its
pointer), the Standing-invariant paragraph of this brief as of `e572593`, and
the session report of the same round. **Why wrong:** the dynamic read was
taken at a hard-coded, undeclared δ = 0.05 rad (one grid step) in a regime
where the pinning wells are anharmonic below half a step; the 5% was partly
which basin bump 0 sat in — the neighbouring basin at the same ε reads 0.65 at
that δ. The number cited as evidence of the invariant working was produced by
the constant the invariant later caught. **The check was sound; the witness
was not evidence of it.** Replaced by: δ declared and swept, banked read at
δ = 0.005, five converged witnesses within 4% (R4), the δ = 0.05 defect pinned
so it cannot return silently (R4b). Tables re-sealed at v2 (`679fc38`,
`b2b5a04`).

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

## The finding from measure 1, and what it re-indexes (second pass, 2026-09-16)

**There is no ε\*.** Drift is ≈ linear in ε·T at small ε, so in the long-T
limit any ε > 0 collapses the continuum, and "the heterogeneity at which the
ring goes discrete" is a property of the network **and the observation window
jointly**. Two banked rows at the same ε=0.03 say it: 16 distinct attractors
at T=200, 4 at T=2000. The index is an **ε·T contour** (#20 on first contact).

Three upstream consequences, all applied to the plan on the branch:
1. **Stage 1's gotcha is now a measured law** citing those two rows.
2. **Stage 6 is re-posed**: gain modulates the drift coefficient; fit c(g) and
   report the surface, not "the g at which it stiffens".
3. **Stage 5 / QUEUED acquire a structural confound.** The certifier needs
   n=2000 events at rate r ⇒ T = 2000/r ⇒ contour position 2000·ε/r, fixed by
   the certifier. Window length and attractor state cannot be chosen
   independently. The QUEUED arm is **confounded by construction, not
   underpowered**; it does not leave the queue until one of the three options
   in the plan's QUEUED entry is chosen.

**Detector naming.** `ph_topology_implies_continuous_attractor` asserted the
inference Stage 1's own framing denies. Measure 2 now scores
`ph_topology_consistent_with_continuous_attractor` (marginal claim; negative
set = converged pinned-ring cloud, jittered cloud above τ_c, within-cell
scrambled cloud; nearest confusable = the pinned ring's *transient* cloud,
which traces the ring before collapse). The `implies` form stays DECLARED
through all of Stage 1 by design (`STAGE1_CANNOT_CERTIFY`); it needs Stage 3
path-lifting or zigzag. `rotational_dynamics_fit` has a real certification
path (skew_frac vs TME) and is unchanged.

**Rates carry intervals.** Sensitivity 2/2 → CP95 ≥ 0.158, specificity 3/3 →
CP95 ≥ 0.292, both UNINFORMATIVE per `boundary_rate`. The number doing the
work is the **256× margin** on λ₁ between the ε=0 floor and the nearest
confusable; the board leads with it.

**Standing invariant, and what it caught the moment it had a second witness.**
R4 runs on every row of both tables: converged rows must agree within 20%;
non-converged rows are flagged and attributed; ≥3 live witnesses required.
The contour table added long-T rows, and on the first new converged witness
(ε=0.01, T=20000) the reads were **39% apart**. A δ sweep showed the dynamic
read converging to λ₁ as δ→0 (ratio 0.965 at 0.005, 0.61 at 0.05, 0.32 at
0.1; same at T=50/200; at both ε): the pinning wells are anharmonic below
half a grid step, and δ=0.05 — one grid step — was a **hard-coded, undeclared
instrument constant**. The 5% agreement banked earlier at ε=0.1 was partly
the luck of bump 0's basin (the next basin reads 0.65 at δ=0.05). Fix: δ
declared and swept (`relax_delta_sweep`), banked read at δ=0.005, both
generators re-sealed at v2 (λ₁/drift/n_distinct bit-identical — δ enters only
the dynamic read). R4 now has **5 live witnesses**, all within 4%. R4b pins the
δ=0.05 defect (ratio must stay < 0.8 on that row) so a refactor cannot
silently restore the constant. The dynamic read's own floor is measured on the
ε=0 rows (≈6e-6 at δ=0.005; it scales ~1/δ) under a declared ceiling of 1e-4.

**c(ε·T) fitted, contour domain found (R8).** c = 2.905e-2 rad/τ per unit ε,
max residual 2.3% on 9 linear-regime rows; splits at equal P agree to 0.1–3%
(drift) and within 1 (n_distinct) at P=20, 60. **At P=200 the pre-declared
check fails (1/4/3)** because the ε=1 split deforms the bump (amp 0.710) —
the contour is perturbative, valid while the bump is undeformed. R8 asserts
that failure remains, as the domain boundary.

**Venv, declared as three capabilities** (checked against packaged wheels):
`ripser 0.6.15` + `persim 0.3.8` **installed** (barcodes with
`do_cocycles=True` from the first pass; diagram distances for the jitter
curve). `DREiMac 0.3.0` declared, install with Stage 3. Zigzag: **not GUDHI**
— the 3.13.0 Python wheel has no zigzag module or symbol; `Dionysus 2.2.3`
ships a cp312 `manylinux_2_39` wheel and host glibc is 2.39, so it installs
as a wheel when reached.

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
   Scores `ph_topology_consistent_with_continuous_attractor` only. Unblocked:
   ripser + persim are installed (see above). *Not this session.*

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
- Instrument sealed via `modelparams.Model` in each generator (v2): 3 TESTED
  (ε or P, T, `relax_delta_sweep`), 9 DECLARED.
- Generator-before-output via `sealgen.sh`; outcome claims only with CHECKRUN lines.

## Acceptance criteria (board rows R0–R7 in `verify_ring.py`)

- **PASS**: all eight rows green — guard real; specs construct; floor at
  |λ₁|<1e-12, drift<1e-9; λ₁ strictly decreasing with ε; ε=0.1 row converged
  (resid<1e-8) and collapsed (n_distinct ≤ B/2); spectral/dynamic agree within
  20% on **every** converged row above the floor at the smallest declared δ,
  ≥3 such witnesses (R4; was "the converged row", singular — see S1);
  n_distinct differs across T at some ε; built
  detector two-sided-correct with the nearest confusable silent by >10×.
- **SOFT PASS**: R5 (T-dependence) is the only red — the sweep is too short to
  show it; extend T, do not lower the bar.
- **FAIL**: R6 red — the detector fires on the weakly pinned ring, or the
  confusable is silent only via the convergence gate and not via λ₁. That is a
  one-sided calibration and the threshold is redrawn against the table, never
  the other way.

## Out of scope this session

PH measure 2 (library installed, not run); Stage 2+; spikes off the ring and the QUEUED ring→ARS
instrument bound; any population-level claim.

## Deliverables

1. `rotational-dynamics-build-plan.md` v5.
2. `__init__.py` (guarded torch), `ringnet.py`, `detectors.py`, `verify_ring.py`.
3. `stage1_marginal.py` (sealed generator, v2) → `stage1_marginal_measured.json`;
   `stage1_contour.py` (sealed, v2) → `stage1_contour_measured.json`.
4. This brief; RESULTS.md §7.ter row deferred until measure 2 lands (one
   commit per phase convention).

## Open questions carried forward

- QUEUED arm: **(b) chosen** — long-range certification dropped, matched-Cox +
  `wigner_renewal` kept, deliverable re-sealed as the per-cell detection
  margin vs the dial; bank where the margin crosses the floor. (Plan, QUEUED.)
- ~~c(ε·T) fit before measure 2~~ — **done** (above). Measure 2 is next.
- Per-basin λ₁ spread: at ε=0.1 the three pinned basins have λ₁ = 1.28e-2 /
  1.49e-2 / 1.53e-2; the tables bank the median, min and max. If Stage 6 needs
  per-basin curvature, the column exists.
- Where the QUEUED arm's "which calibrator is each dial setting redundant with"
  column is computed — `extractor_distinctness` machinery or a new panel.

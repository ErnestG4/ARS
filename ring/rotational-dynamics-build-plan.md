# Rotational Dynamics / Attractor Geometry — Build Plan v5

Working doc for picking up in Claude Code. Target location:
**`criticality_tool/ring/`** (see Placement).

---

## Corrections from v3 — read before anything else

Three defects, found by review against the repo. Chased to every call site
per failure mode #21 (a retraction that leaves the claim standing elsewhere in
the same file is not a retraction).

**v5 (2026-09-16):** C1–C3 re-verified clean at every call site by grep. Six
stale items from the review's second pass applied in place: torch was already
in the venv (Placement); all 12 references resolved directly (Reading first);
the zoo narrowing re-based on *redundancy*, with its promotion condition pinned
(This plan → ARS); the decoy's target detector named and di Sarra's model
added as the torus-without-attractor half of the Stage 1 negative set (Stage 0
domain nulls); the rotation-null paragraph made internally consistent; the
`Zone.Identifier` stray dropped.

**v5, second pass (2026-09-16, after Stage 1 measure 1 banked):** the ε·T
contour is a finding, not a detail, and it re-indexes three things upstream
(Stage 1 gotcha → measured law; Stage 6 → fit the drift coefficient c(g), not a
threshold; Stage 5 / QUEUED → the certifier's n=2000 pins the contour position,
so the arm is confounded by construction). Detector
`ph_topology_implies_continuous_attractor` renamed to the claim PH can
support; the `implies` form stays DECLARED through Stage 1 by design. Venv
declared as three capabilities. Applied in place on the branch — a v6 written
from v4 would fork against this file.

**C1 — The joint experiment predicted the wrong sign. RETRACTED.** v3 read
"hc-3 6% / allen-hpf 0% of cells individually indistinguishable from Poisson at
long range" as *rigidity*. Σ² failing Poisson is two-sided, and these fail
upward:

| | Σ²(L=5) |
|---|---|
| GUE-rigid | ≈ 0.5 |
| Poisson | 5.00 [4.63, 5.33] |
| hc3-port | 43.1 (n=35) |
| allen-hpf | 183.5 (n=51) |

Super-Poissonian by an order of magnitude — long-range **clustered**, the
opposite of what v3 sealed. The 2026-06-30 truth audit's FIX-2 was this same
inversion on the calibrators (GUE 107 > Poisson 55 from a unit-mean unfold), so
the vocabulary has a demonstrated trap here. `EPISTEMIC_STATE.md`'s "every
neural substrate is clustered was a short-range verdict" points the right way and
was read past.

Corrected, the hypothesis becomes trivial: a unit under a passing bump is a
rate-modulated process, so its Σ² is super-Poissonian by construction. The
nearest confusable is already measured — **Cox process, Σ²(5) = 45.4**, sitting
on hc3-port's 43.1. A rate-matched Cox with the ring unit's own envelope passes
the arm identically. **Rival rule fires before the run.**

**C2 — The arm collides with a banked ruling.** The 2026-05-28 EC/CA3 attractor
arc (DANDI 000638, then hc-3 within-implant, 22 sessions) ruled attractor
topology bounded-negative and bounding the instrument: the whole EC-vs-CA3
difference reduced to burst fraction (ρ=0.78, n=659; residualized δ −0.51 →
+0.03). Banked conclusion: attractor topology is not a spike-train-fingerprint
property; if it holds it lives at population-manifold geometry, which ARS cannot
resolve by construction. v3 proposed per-cell spike-train fingerprints as the
readout — the readout already ruled unable to see it.

**C3 — The order-scramble null was an identity map.** v3 stated PH on population
vectors is order-blind by construction, then proposed an order-scramble surrogate
as its null. A scramble of population-vector time order leaves the point cloud
the same *set*; PH is bit-identical. The surrogate cannot fail — a violation of
"verify the test CAN fire," one paragraph after importing that rule. Corrected in
Stage 1.

**Claim scope also narrowed.** v3 said nobody has stated the order-blindness
point. di Sarra et al.'s jitter result is a temporal perturbation destroying the
torus, so the field has noticed time is in the object; Gardner-style claims lean
on sleep preservation as the dynamical leg. The defensible version: **PH-topology
is a marginal statement, and any dynamical claim needs a temporal statistic** —
which Stage 3's path-lifting decoder and zigzag PH both are.

---

## Central thesis

The interesting structure in these systems is angular, and standard formulations
(symmetric Hopfield, spectrogram, Cartesian state space) define it away before
analysis starts.

**Corollary the angular camp does not get to skip:** jPCA finds rotation because
it is constrained to fit rotation — failure mode #14, a class space with no
rejection region. Same defect, different substrate.

---

## Placement

**`criticality_tool/ring/`**, following the `arsrh/` `holonomy/` `lcap/`
`rigidgate/` pattern, so the arc inherits the verification layer rather than
rewiring nine files plus `checkrun.sh` and the commit-msg hook.

The forcing constraint is `verify_seal_order.py`: generator-before-output is a
**commit-graph property**, so a generator in a sibling repo breaks sealing
outright. One repo is not a preference here.

**Consequence to decide explicitly, not by accident.** v4 said torch "enters"
the venv; it was already there — `$HOME/fmexplorer/bin/python3` carries
`torch 2.11.0+cu130` (CUDA visible) *and* `cupy 14.0.1`, and the repo's declared
GPU path is cupy (`requirements.txt:20`, `riemann_explorer` kernels). The live
decision is therefore **torch vs cupy for the ring sims**, not whether torch is
installed. Decision: **torch**, for the leading-batch-axis sweeps and because
Stage 6's plasticity is easier to express with autograd; cupy stays the path for
anything shared with the scanner. Either way the import is **guarded** —
`ring/__init__.py` exposes `HAVE_TORCH`, every verification file runs on numpy,
and `verify_ring.py` proves it by importing the package with torch blocked.

**PH is three capabilities, declared together so the same stage does not force
a second venv change** (facts checked against the packaged wheels, 2026-09-16):

| capability | package | status |
|---|---|---|
| static barcodes + cocycles | `ripser 0.6.15` (`do_cocycles=True` from the first pass — Stage 3's path-lifting consumes them; ~10³ diagrams in measure 2 are not worth recomputing) | **installed** |
| diagram distances (the jitter ladder's output is a bottleneck/Wasserstein curve) | `persim 0.3.8` | **installed** |
| circular/toroidal coordinates from persistent cohomology | `DREiMac 0.3.0` (sits on ripser) | **installed** (Stage 3a) |
| zigzag persistence | **not GUDHI**: the 3.13.0 Python wheel carries no zigzag module or symbol (C++ has it, the bindings don't). `Dionysus 2.2.3` ships a cp312 `manylinux_2_39` wheel; host glibc is 2.39, so it installs without the boost build | **installed 2026-09-17** (wheel; `zigzag_homology_persistence` present); E-cloud work deprioritized — E was the pathological case, not the target |

Point-cloud size is T (timepoints), not N: a 2000-point Rips to H₁ is
unremarkable individually; the thousand of them wants the batching.

---

## Hardware and numerics

- Every model is tiny (N = 100–2000). The 4090 is for **parameter sweeps and
  surrogate ensembles as a batch dimension**, not model size. Leading batch axis
  on everything.
- **float64 for anything accumulating phase.** Ada fp64 runs at ~1/64 fp32, so
  the GPU is not the reason it's fast — at these sizes (10⁶ grid cells × 10⁴
  iterations) it's seconds either way. Keep float64; drop the framing that the
  card is doing the work.
- Carry the integer winding count separately from the residual phase. The
  numerics force the same `(n, θ)` split the theory arrived at independently.
- Symplectic integrator for anything Hamiltonian. RK4 drifts energy secularly and
  the drift reads as dynamics.
- **Pin BLAS threads before banking anything from Schur/Henrici.** Dense LAPACK
  is path-dependent (memory: `lapack_reproducibility_depends_on_the_path`).

---

## Reading first — half a day, not a stage

**All twelve references resolved directly on 2026-09-16** (arXiv abstract pages
for the five IDs; publisher/DOI pages for the seven journal items). Every one
matches its description here; none was a reconstructed ID. Note that
`citation_provenance.py` / `verify_literature_anchors.py` do **not** do this —
they check guard-module provenance declarations and count surname hits — so a
resolved-ID check has no board row yet. Remaining unverified: Clark's journal
version ("PRE 2026") — the arXiv paper was confirmed, the journal publication
was not.

- **Clark, "Transient dynamics of associative memory models"** (arXiv 2506.05303;
  journal version unverified). The blackout catastrophe is largely an equilibrium artifact; above
  capacity, patterns retrieve transiently because slow regions persist as shallow
  remnants of basins that existed below capacity. Capacity was the wrong
  question — the transient framing is the organizing axis of this build.
- **Chandra, Sharma, Chaudhuri & Fiete, Vector-HaSH** (Nature 638:739–751, 2025).
  Grid-cell continuous attractor as a scaffold for associative memory.
- **"Beyond Fixed Points: Superpolynomial Capacity of Asymmetric Hopfield
  Networks"** (arXiv 2605.24611). Symmetry buys a Lyapunov function and costs
  every attractor that isn't a point.

---

## Stage 0 — Port the ARS harness (do not rebuild it)

v1 and v2 specified a null harness from scratch. That was a naive reconstruction
of infrastructure that already exists and has been broken in scratch by
adversarial review and hardened.

| component | what it enforces here |
|---|---|
| `detector_spec.py` | no detector without a negative set + named nearest confusable |
| `boundary_rate.py` | every rate carries a denominator + Clopper–Pearson interval |
| `redpath.py` | probes assert their own reach; when `expect_min` fires, raise power, never lower the floor |
| `modelparams.py` | every parameter swept-with-test or declared-with-defence; `swept()` returns the pre-registered config, not the max (+0.331 measured selection penalty) |
| `reachable.py` | Bars with defended ranges, both-edge raises, edge probes, **rival rule** |
| `threadledger.py` | QUEUED/LANDED/DROPPED as data; drift measured against the **effective** verdict |
| `checkrun.sh` + commit-msg hook | machine writes the verdict; no outcome claim without a CHECKRUN line |
| `sealgen.sh` + `verify_seal_order.py` | generator-before-output as a commit-graph property (`--full-history`) |

Carry the AUDIT.md caveat verbatim: **green means the checkers pass, not that the
instrument measures what we claim.**

**Rules imported as rules:**

- One null excludes only its confound. A powered falsifier CONSTRUCTS the
  confound it rules out.
- **Rival rule.** An arm both the hypothesis and its rival pass is evidence for
  neither. C1 above is what it looks like when this fires late.
- Stratify before pooling.
- **Non-evidence scored as a verdict** (#19) is ARS's dominant error mode. Assume
  it is this project's too.

**ARS failure modes that are already the open problems in this literature:**

- **#14 — argmin with no null option.** jPCA constrains its fit matrix to be
  skew-symmetric, so only rotational dynamics can be fit: a class space with no
  rejection region. ARS's case: `_classify` labeled 7/7 non-members, a perfect
  clock read GUE at 15× the KS critical value, 754 banked classifications fit no
  better than a known non-member.
- **#16 — censoring at the null.** The V1 power law (Stringer et al. 2019)
  reanalyzed with an unbiased eigenmoment estimator (PNAS 2025) is a broken power
  law, not critical-limit; the original cvPCA estimator was biased.
- **#17 — bounded fitters rail on a constant.** Check the distinct-value ratio
  (pvc-11 Brody: 4/15,174 distinct = optimizer floor; 7,319/7,328 = real
  concentration).
- **#20 — mis-indexing masquerades as underpower.** See Stage 4.

**Rotation null.** Two fits, both cheap, both reported: the unconstrained
`M` and the skew-constrained `A`. From the unconstrained fit also carry the
null-free scalar `‖A_M‖²/‖M‖²` (skew part of `M = S + A_M`). Copy the
`_classify` repair shape exactly: `r2_skew`, `r2_full`, `skew_frac`,
`r2_tme_95`, `fit_rejected`, pre-existing keys bit-identical. Small
`r2_full − r2_skew` gap = the constraint isn't doing work; large gap = the
rotation is a property of the constraint. (TME unreliable below ~30 signals.)

**Domain nulls still to build:**

- **Jitter ladder** τ ∈ {1, 10, 50, 100, 250, 500, 1000} ms — excludes
  **fine-timescale coincidence**. di Sarra, Jha & Roudi: 100–500 ms jitter
  destroys grid-cell toroidal topology while grid scores largely survive.
- **Within-cell ISI-order scramble** — excludes **sequence**. Preserves each
  cell's marginal ISI distribution, destroys cross-cell coincidence, changes the
  population vectors, and can therefore kill the torus. This is the surrogate C3
  should have specified.
- These are different confounds. Run both; name the level of the scramble in
  scope, once.
- **Preprocessing sensitivity.** di Sarra's toroidal barcodes required PH on a
  selected high-mean-activity subset (random time points collapse toroidality
  on real data — S1 Appendix). Sweep the subsetting rule.
- **The torus-without-attractor confusable is already built.** di Sarra et al.'s
  own model is a population of *independent* rate-modulated Poisson units —
  hexagonal spatial tuning plus theta/eta oscillatory modulation, no recurrence,
  no attractor — and it reproduces the toroidal barcodes. Code:
  `gdisarra/Oscillations_toroidal_topology`. This is the `nearest_confusable`
  for any "PH topology ⇒ continuous attractor" inference, and it makes the
  Stage 1 negative set **two-sided**: (a) topology without an attractor (the
  di Sarra construction, on S¹ here), (b) attractor without a continuum (the
  pinned ring). v3/v4 cited the jitter result and not the model; the model is
  the half of the negative set that already exists.

---

## Stage 1 — The ring (continuous attractor first)

The entry point: the only architecture where a winding count is *defined*.

- Ring attractor, N units, local excitation + global inhibition (Ben-Yishai et
  al. 1995; Zhang 1996).
- **Measure:** bump formation; marginal stability along the ring (one eigenvalue
  ≈ 0), negative transverse.
- **Measure:** PH, H₁ rank 1 — through the jitter ladder, the within-cell
  scramble, and the subsetting sweep *on your own simulated data, where you know
  the answer*. This calibrates how much the pipeline invents before it points at
  anything unknown, and it is the **marginal-vs-dynamical result** everything
  downstream depends on.
- **Measure 2 ran (2026-09-16; `ring/RING_BRIEF.md` §Measure 2 — results).**
  The static 16-bump cloud reads identically to the driven ring (r₁₂ 61 vs 71,
  q-invariant): **PH on the cloud cannot tell a traversed manifold from a
  sampled one** — the marginal-vs-dynamical result, measured. τ_c(A) = 100τ
  (P1 failed as sealed; ~~"the period, not bump-width/ω"~~ — brief S2: at
  the true FWHM both give ~100τ and F4 decided it, H_cov); ~~the pinned ring
  is one rung more jitter-robust (P2: divergence)~~ (brief S3: not
  replicated); the ISI scramble is
  under-powered on single-visit units (blind spot recorded in the spec); the
  subsetting rule flips the verdict only at the transient confusable.
- **Coverage test ran (2026-09-16; brief §Coverage test).** PH's jitter
  sensitivity depends on **angular displacement over τ_j alone**: ω·τ_c ≈ 2.8
  rad across a 4× speed range, independent of bump width (1.57–2.65 rad),
  rotations (1–10), and pinning. The bump-width account is falsified; the
  P2 "pinned ring more robust" reading did not replicate (brief S3); the
  "jitter lifts SNR" reading was wrong — jitter **constructs** loops on clouds
  whose time-order encodes the manifold's order (brief S4). r₁₂ is scale-free
  and blind to smoothing; b₁ half-life is the estimator. The jitter ladder's
  spec now requires a predicted τ_c = 2.8/ω and a sequence-order statement.
- **What measure 2 can certify, by name.** PH on the cloud is order-blind, so
  no barcode promotes "PH topology ⇒ continuous attractor". The detector measure
  2 scores is `ph_topology_consistent_with_continuous_attractor` — a marginal
  claim whose negative set is the pinned-ring cloud and the jitter/scramble
  surrogates. The `implies` form (`ph_topology_implies_continuous_attractor`)
  stays DECLARED through all of Stage 1 **by design**: it needs a temporal
  statistic (Stage 3 path-lifting or zigzag PH), and the board refuses to let it
  read as certified until one exists. Naming this now is what stops a clean
  measure-2 result from being banked as a dynamical finding.
- **Zigzag persistence** (arXiv 2603.03037, Gardinazzi et al. 2026) for the time-varying case.
  Classical PH assumes a static point-cloud filtration, wrong from Stage 4 on.

**The transferable framing (scope-corrected).** ARS §4: NNS / ks_gue / rep_med
certify the **marginal** gap distribution, not the class — an order-scramble
surrogate reproduces 0.87–1.00 of quadrant labels on every real substrate. The
analogue here: PH on a cloud of population vectors is order-blind, so
"the population lives on a torus" is a marginal statement. It does **not** follow
that an order surrogate tests it (C3). It follows that **a dynamical claim needs a
temporal statistic** — path-lifting (Stage 3) and zigzag PH are the two on hand.

**Measured law (was a caveat; banked 2026-09-16, `stage1_marginal_measured.json`).**
Continuous attractors are structurally fragile — fixed asymmetries cause directed
drift and collapse the continuum into discrete attractors — and the collapse has
an index with a form: **drift ≈ linear in ε·T at small ε** (5.9e-4 rad at
ε=1e-4, T=200 → 5.9e-3 at T=2000). So **there is no ε\***. In the long-T limit
any ε > 0 collapses the continuum; "the heterogeneity at which the ring goes
discrete" is a property of the network *and the observation window jointly*,
not of the network. Stated cleanly by two banked rows at the same ε=0.03:
**16 distinct attractors at T=200, 4 at T=2000.** This is failure mode #20
(asymptotic label + bounded instrument) handled on first contact: the index is
an **ε·T contour**, and every downstream "threshold" question (Stage 6, Stage 5,
QUEUED) is re-posed against it.

**Fitted and domain-bounded (`stage1_contour_measured.json`, tolerances
declared before the run).** Six products P = ε·T, each realised by three
(ε, T) splits: in the linear regime (P ≤ 2) the splits agree to 0.1–3% and
**drift = c·ε·T with c = 2.905e-2 rad/τ per unit ε** (max residual 2.3%, 9
rows) — this is Stage 6's baseline c(g=1). In the collapse regime the splits
agree on n_distinct at P=20 (13/14/14) and P=60 (3/4/4). **At P=200 the
declared check fails: 1 / 4 / 3** — the ε=1 split deforms the bump (amplitude
0.710 vs 0.780) and collapses to a single attractor. That failure is the
contour's domain: it is a *perturbative* statement, valid while the bump is
undeformed (ε ≲ 0.3 here), and `verify_ring.py` R8 asserts the failure stays
visible rather than loosening the tolerance.

**Standing warning:** *per-cell fingerprints cohere; population observables
fragment — aggregation, not biology, sets the population class.* This plan is
population-level throughout. Compute the per-unit version before trusting any
population statistic.

---

## Stage 2 — Asymmetry and non-normality (merged)

Dropping symmetry is what creates non-normality; same instruments.

- `W = W_sym + αW_asym`, sweep α. Eigenvalues go complex; point attractors →
  limit cycles → sequences.
- **Schur decomposition, not eigendecomposition** — orthonormal basis making the
  feedforward structure explicit; project onto Schur dimensions grouped by sign of
  the real part (as in the 2025 decision-making paper, "Neural dynamics outside
  task-coding dimensions drive decision trajectories through transient
  amplification"). Pin threads first.
- **Henrici index** as a scalar non-normality measure, sweepable against α.
- **Pseudospectra** (resolvent norm over a grid in ℂ). Normal → isolated contours;
  non-normal → broad overlapping ones.
- **Max transient gain** `max_t ‖e^{At}‖₂` via SVD — what the spectrum cannot see.

**Open question worth the time:** whether Clark's above-capacity "slow regions
without stable attractors" and Stage 7's SHC saddle-lingering are the same object
in two vocabularies. Nobody appears to have checked.

**Stage 2 ran (2026-09-17; brief §Stage 2 — results).** The premise above —
dropping symmetry creates non-normality — is **falsified for the ring**: the
symmetric attractor's linearisation is already non-normal (Henrici 18% of
‖J‖_F, numerical abscissa 0.178 above spectral, G_max = κ = K = 1.356), set by
the gain profile of the bump. Circulant asymmetry over 16×, random asymmetry
at matched norm, and heterogeneity over 100× each move Henrici by < 0.2% on
every converged row; heterogeneity *reduces* G_max monotonically (exponent
0.86), converting persistent amplification into a shrinking transient. Three
rails caught three instrument defects before any number was read.

---

## Stage 3 — Path integration: the count accumulates

- Asymmetric coupling pushes the bump; input sets velocity. Expect near-linear
  velocity/modulation mapping (holds down to neuromorphic hardware — DYNAP-SE,
  multi-second stability).
- **Measure:** long runs, extract `(n, θ)`; check `n` survives noise that visibly
  corrupts `θ`. The topological-protection claim, tested.
- **Stage 3b/I1b/I1c ran (2026-09-17; brief).** The along-manifold kick is the
  attractor predicate, operationalized: the continuum retains (1.00), the
  trapped discrete attractor restores (0.02), the input-driven look-alike
  restores (0.00); registered as the intervention-class detector
  `attractor_by_along_manifold_memory`, separate from the observational
  ladder by design. Deviation statistics fail even at the rate level. The
  passive dual — MSD along the manifold (Stage 3e) — decides whether the
  observational `implies` rung is reachable.
- **Stage 3e / T2 / T3 / 3h ran (2026-09-17 → 09-20; brief).** The MSD
  growth law separates the three systems **in kind** (continuum slope ~1,
  D = 1.5·10⁻⁵ rad²/τ; trapped saturating; IND_u flat): the zero mode's
  passive signature is that it integrates noise, so "unreachable
  observationally" is NOT banked; but the trapped clauses sealed against
  the linear λ₁ miss by a common factor 0.19–0.35, and Stage 3h (the MSD
  well's own δ-sweep, both signs) found that well **asymmetric but nowhere
  near Stage 3e's number** at the 0.1-rad excursion (0.99/1.01 on one side,
  0.70/0.87 on the other, against a cited 0.32) — the anharmonic explanation
  is retracted (brief S5), the cause is open (candidates: noisy-bump
  effective potential; crossover estimator; rare escapes past the basin edge
  at −0.2 to −0.3 rad).
  T2 and T3 (traversal statistics on the lifted path) each separated
  qualitatively and failed their own sealed numbers; three versions is the
  stopping point — ordering pinned (R13d), thresholds to a negative-set
  calibration (Will).
- **Stage 4/4b ran (2026-09-17; brief).** Circle-map rails all green; the
  reduced phase model predicts the ring's depinning **to 3% and 12% at two ε,
  both within a grid step**, from the maximal pinning speed measured at
  γ = 0 — an extreme-value statistic, where Stage 1's contour is the median.
- **Stage 3a ran (2026-09-17; brief §Stage 3a — results).** DREiMac circular
  coordinates + lift recover |n| = 3 exactly in 9/9 readable seeds with k = 1
  and θ residual 0.02–0.04 rad after removing the reparametrization. The
  protection claim is **not reached**: the instrument fails wholesale below a
  censored ρ edge rather than degrading θ first, and the fallback coordinate
  emits wrong counts (never read). The lift certifies *traversal*, not
  *attractor* — an independent-unit construction on the same trajectory reads
  identically — so the detector ladder has a kinematic rung; the attractor
  rung's transverse-relaxation instrument failed at the rate level (L4b ran in
  Stage 3b: sealed-to-fail confirmed).
- **Readout to copy, not reinvent:** "Topological decoding of grid cell activity
  via path lifting to covering spaces" (arXiv 2510.16216, Yao & Yoon 2025) —
  toroidal coordinates via persistent cohomology, then path-lift to the universal
  cover; trajectories recovered up to an affine transformation. This is also one
  of the two temporal statistics Stage 1 says a dynamical claim requires.

---

## Stage 4 — Mode locking / Arnold tongues

### Re-index before you sweep (failure mode #20)

ρ = lim(θ_N − θ_0)/N is an **asymptotic label**. Rational-vs-irrational is not
decidable from a finite window at any N. *Asymptotic label + bounded instrument →
no n fixes it; re-index.*

Precedent and template: class-level ρ = −0.91 was a one-representative-per-class
artifact; the finding held per-α at ρ = +0.699 (n=255) after re-indexing.
Mis-indexed, not underpowered.

**So don't ask "is it locked at p/q."** Ask a bounded question — residence time
within tolerance ε of the nearest p/q with q ≤ Q_max over a fixed window, ε and
Q_max declared and swept per `modelparams`. State the index once, in scope.

Settled ARS arc: **approximability ⟂ mode-locking, theorem-level disjoint.** If
Stage 4 was going to lean on Brocot depth predicting tongue structure, it cannot.
Two independent coordinates.

### Then sweep

- Sine circle map first: `θ_{n+1} = θ_n + Ω − (K/2π)·sin(2πθ_n)`.
- Sweep (Ω, K) batched, ~10⁴ iterations per cell.
- **`riemann_explorer` is already an Arnold-tongue map tool.** Compare against it
  rather than starting cold; the memories `capture_full_per_axis_sweep`,
  `seed_replicate_near_boundary` and `sweep_coupling_class_before_distinctness`
  are lessons from that exact sweep.
- **Hysteresis arm, with its dead region declared.** For K < 1 the map is an
  orientation-preserving circle homeomorphism, so by Denjoy the rotation number is
  unique and independent-init must agree with adiabatic continuation. **Discrepancy
  at K < 1 is a bug, not a finding** — which gives the arm a free must-be-zero
  region and satisfies "verify it can fire." Hysteresis is only admissible for
  K > 1. The PRResearch 7, 043156 (2025) explosive-entrainment result is for
  *adaptive* oscillators (extra state variable); it does not transfer to the plain
  map, and v3 imported it without noting the system difference.
- Reproduce in the full ring network; check whether the reduced map predicted it.
- **Experimental template:** the mouse segmentation clock (eLife 2022) derives PRCs
  and Arnold tongues from a living oscillator by microfluidic entrainment.

---

## Stage 5 — The (n, ψ, r) readout

**UNRUN as of 2026-09-20, ~65 commits in — the question this plan was written
for — and now NEXT: nothing is queued ahead of it.** Kept visible so the
instrument-building does not become the project by default. Stage 3a supplies
its first two inputs: the integer channel's error rate is 0 wherever the
coordinate exists and undefined where it does not (never intermediate); the
ψ channel's floor is 0.02–0.04 rad. ~~Queued directly after Stage 3e and
T2~~ — both ran.

| channel | object | robustness |
|---|---|---|
| `n` | winding count, ℤ | topological — noise can't touch it without a full turn |
| `ψ` | mean phase, `arg⟨e^{iθ}⟩` | analog, noise-floor limited |
| `r`, higher moments | `\|⟨e^{iθ}⟩\|`, `⟨e^{2iθ}⟩`, … | cluster structure inside the window |

- Kuramoto order parameter for `r`, `ψ`. Second circular moment separates one
  tight cluster from two antipodal ones — both give intermediate `r`.
- **Measure:** bits per window vs. noise floor, split across the three channels.
  This decides whether the scheme is worth anything. Note this readout is not an
  ARS statistic and carries none of the above constraints.
- **Measure:** the two readout modes are not equivalent — one oscillator across
  time vs. many at an instant. Mode-locked systems have sharp time averages and
  spread ensembles; drifting systems the reverse. The gap is a measurement.

**If windows are to carry long-range certification, they have a floor set by the
certifier, not the phenomenon.** lcap policy: `L_judge = min(requested_L,
validity_L, discrimination_L)`; at n=343 the gate is blind at *every* L (GOE
admitted 32–90%); the only admissible cell measured anywhere is **n=2000, L=5**.
Terminal ruling on the ARS side: needs more data, not a different statistic.

**And the floor couples to the ε·T contour.** n=2000 events at rate r means
T = 2000/r, so the position on the collapse contour is **2000·ε/r — fixed by
the certifier's sample requirement**, not chosen. Window length and attractor
state cannot be set independently: holding the contour position while
satisfying n=2000 means co-varying r, which changes the point process being
measured. Any Stage 5 window that carries long-range certification inherits
this; state the contour position of every window alongside its L.

---

## Stage 6 — Gain modulation, constrained

**Secer, Knierim & Cowan (Nat Commun, Oct 2025):** in a continuous bump attractor network, gain
*recalibration* requires an additional signal explicitly encoding the
representation's error via a rate code — instantaneous error or its time integral.
Error *correction* works from ground-truth input through network dynamics;
recalibration does not. A global gain scalar is provably insufficient.

Build the error channel, don't just add a knob:
- global gain `g`, temperature `T`, **plus** an explicit error-rate channel with
  Hebbian plasticity on the gain pathway.
- **Measure (re-indexed, #20):** v4 asked "at what `g` does the continuum
  stiffen into discrete points." Ill-posed — same defect as ε\*. What gain
  modulates is the **drift coefficient**: with drift ≈ c(g)·ε·T, the measurement
  is **how `g` moves the contour. Fit c(g) and report the surface**, not a
  threshold. Same for temperature: c(g, T_noise). Sharper and falsifiable — a
  c(g) that is flat says gain does nothing to the continuum; one that crosses
  zero says gain can *unpin*.
- **Measure:** how `g` shifts Stage 4's tongue boundaries — does gain change which
  counts are selectable?
- Bounded parameters here: check distinct-value ratios (#17).

**Prior art:** "Neuromodulation-inspired gated associative memory networks"
(arXiv 2512.13859, Goto et al. 2025).

---

## Stage 7 — Stable heteroclinic channels (side quest)

No stable fixed point; saddles connected by unstable manifolds; approach, linger,
ejection.

- Generalized Lotka-Volterra with asymmetric inhibition (Rabinovich, Afraimovich,
  Varona; winnerless competition).
- **Measure:** sequence reproducibility under noise; dwell time scaling
  logarithmically with noise level.
- **Status:** migrated from neuroscience into bio-inspired robotics (Rouse et al.,
  *Bioinspir. Biomim.* 20, 036004, 2025). Look there for code.

---

## QUEUED — Ring→ARS instrument bound (re-sealed; formerly "joint experiment")

**Demoted from first-class.** v3's version is retracted under C1 and C2. What
replaces it is not a hypothesis test — the banked EC/CA3 ruling already supplies
the expected answer — but a **measurement of the instrument's blindness with a
dial**, which belongs to the §5 estimator-reliability capability class.

**Question:** with each unit's rate envelope held fixed, how much attractor
structure must be present before ARS can see it per-cell, and where does that
cross the noise floor?

**Design.**
1. Stage 1 ring emitting spikes; heterogeneity dial from intact continuum →
   partially pinned → fully discrete.
2. **Matched Cox control at every dial setting** — same rate envelope as the ring
   unit, no attractor. This is the designed-instance version of the rival that
   already fires at Σ²(5) = 45.4 against hc3-port's 43.1.
3. `wigner_renewal` decoy: **already exists at
   `longrange_discriminator.py:55`** — a call, not a build.
4. `phase22a.ars_classify.classify(events)` — marginal read only. ~~Long-range
   via `longrange_discriminator.py` at n=2000 / L=5~~ — **dropped under (b)**,
   see the confound below.
5. ~~Carry the declared Σ² < 8 near-Poisson threshold~~ — dropped with 4; no
   class comparison is made.

**Pre-registered expectation: null per-cell at every dial setting.** The
deliverable is the bound, not the verdict. A positive would contradict a banked
ruling and should be treated as a defect hunt first.

**Structural confound, found 2026-09-16 — decide survival BEFORE dequeue.** The
long-range certifier needs n=2000 events; at unit rate r that is T = 2000/r of
ring time; so the dial setting's position on the collapse contour is
**2000·ε/r, fixed by the certifier**. "Attractor structure on a dial, window
held fixed" is not a design that exists: moving ε moves the contour position
*and* the certifier's window is what sets it. Co-varying r to hold the contour
position changes the point process. This is worse than "expect null" — the arm
is **confounded by construction, not underpowered**. Options considered: (a)
re-pose over the contour coordinate 2000ε/r with r in the dial — rejected: it
changes the point process being measured while claiming to hold it fixed, so
the confound moves rather than resolves; (b) drop the long-range arm, keep
NNS/`classify` — **chosen (2026-09-16)**; (c) drop the item — rejected: throws
away the one thing the arm can still do.

**Re-sealed under (b) — then re-filed BLOCKED ON A SPIKING RING (2026-09-17).**
The ring's spikes are inhomogeneous Poisson from the rate envelope, so the
matched-Cox control with the same envelope is *identical in distribution* to
the ring unit's train: the per-cell margin is zero by construction and (b)'s
deliverable is vacuous, as are (a) and (c). A non-vacuous version needs a
spiking ring whose spikes feed back into the dynamics — a generator change
with consequences for every Stage 1–4 number's applicability. Not near-term.

**Baseline to expect.** phase30 built Kuramoto populations emitting spikes across
(K, σ), fed them to ARS, and got BR_artifact at every K with 156/160 real-data
rows unmatched — and a locked decision not to add Kuramoto to the zoo, recorded
as a **redundancy** verdict ("redundant with `periodic_q7` and `uniform_jitter`").
The ring's dial has predictable per-cell endpoints and each already has a
calibrator: constant-velocity bump → periodic rate envelope → BR_artifact
(Kuramoto-redundant); diffusing bump → Cox-like (Σ²(5) ≈ 45, in the
NEGATIVE_HALFLINE table); pinned bump → stationary rate → Poisson/refractory
renewal. Expect phase30's outcome as the null baseline, and record **which
existing calibrator each dial setting is redundant with** — that column is what
settles the zoo question below.

**Interface hazard.** Spike times are native and safe. A bump crossing a fixed
ring angle is a Poincaré section — failure mode #2, threshold-upcrossing
extraction. If you use passage times, the artifact lives there.

**Engine note.** NNS is provably invariant under linear time scaling, so it cannot
see rotation *rate* — only spacing shape. For the `(n, θ)` question that's a
feature: blind to the count, sensitive to the residual.

---

## What the two toolboxes give each other

**ARS → this plan:** the Stage 0 harness; the marginal-vs-class distinction, which
reframes every topological claim here; the mis-indexing warning that reshapes
Stage 4; the n=2000 floor; the aggregation warning; and — demonstrated above — a
vocabulary in which v3's three defects are named, numbered failure modes rather
than surprises.

**This plan → ARS, corrected scope.** v3 pitched the ring as a calibrator-zoo
contribution — "a class with a dial and a mechanism, different from a blend."
That was wrong on novelty before any mechanism argument: the zoo already has
exactly that class in `transition_calibrators_dynamical.py` (Phase 20.5 Tier
1.B — logistic map over r, Mackey-Glass over τ, Lorenz; bifurcation-parameter
calibrators with event extraction). And the reason phase30 excluded Kuramoto is
**redundancy**, measured, not "rate modulation dominates" as a rule — stated as
a rule it would evict the dynamical transition calibrators too, whose events are
rate-modulated by construction.

What survives is smaller and still real: the ring as a **decoy generator** for
a named detector — `detector_spec` negative-set machinery, not zoo
class-reference machinery. The target detector is Stage 1's
**PH-topology ⇒ continuous attractor** inference; the ring supplies its
attractor-without-continuum half (pinned ring, ground truth at every dial
setting, event trains native), and di Sarra's construction supplies the
topology-without-attractor half.

**Promotion condition, pinned now:** the ring becomes a zoo *member* iff the
QUEUED instrument-bound sweep finds a dial region whose per-cell ARS reading
matches **none** of {`periodic_q7`, `uniform_jitter`, Cox, Poisson,
refractory-renewal} under the existing calibrator-distinctness test. Absent
that region it stays a decoy generator. The classification is an output of that
sweep, not a judgment in this file.

---

## What this won't settle

- Nothing here says the same geometry runs in a brain.
- Rotational structure being *representable* isn't evidence it's *used*. Stage 5's
  bits-per-window is the only argument for utility.
- Stage 6 is a structural analogy to neuromodulation, not a claim about affect.
- Stage 0 bounds everything else. Three published cases where headline geometric
  findings were attributed to their pipelines, ARS's own 754 banked
  classifications fitting no better than a known non-member, and three defects in
  v3 of this file caught by one review pass. **The prior should be that some of
  these results won't survive.** Plan for retractions that actually retract.

---

## Order

**0 → 1 → 2 → 4 → 5.**

Stages 3 and 6 slot in where needed. Stage 7 is the side quest and the most likely
place to find something nobody has looked at. The ring→ARS bound stays QUEUED
behind Stage 1's marginal-vs-dynamical null, which is cheaper to get and doesn't
fight a banked ruling.

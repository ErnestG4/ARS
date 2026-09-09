# DERIVFLOW POST-VERDICT ROADMAP
## Step-through document — five items, strict order, state tracked in place

**Purpose:** Working checklist for the post-Track-0 sequence. Each step carries its own
rationale, entry/exit criteria, and a STATE line to be edited in place as work proceeds,
so any session (or any resumption after an intensive detour) can re-orient from this
file alone without reconstructing the plan from conversation.

**Authority:** Repo and EPISTEMIC_STATE.md over this doc; this doc over conversation
memory. If a step's work product contradicts this doc's assumptions, amend the doc in
the same commit as the finding and note it in the step's LOG.

**Context as of writing (2026-08-11):** Track-0 closed at 4f29d70. Sealed verdict:
RATE-SEED-DEPENDENT (iid → F3 stretched exponential β ≈ 0.68; GUE → F2 exponential;
form disagreement adjudicated per seal 95e1ad3). Gates all green (Hermite 655700f,
§6.iii c2538de, §6.iv-a 90a1787). Open findings: (F-1) ladder misfit at achieved
precision, χ²/dof ≈ 31 (iid) / ≈ 1062 (GUE) — **now with an instrument prime suspect,
findings §9**; (F-2) picket-fence clause fired on one row — **RESOLVED
INSTRUMENT-OWNED, findings §8**; verdict UNDER INSTRUMENT REVIEW pending the v1.5
corrected-reference recompute campaign (findings §9 + scope §4 v1.5).
Do not inherit numbers from this paragraph into new work without repo confirmation
(row-c rule).

**Ordering principle:** each step is the cheapest thing that de-risks the next.
Steps may be *interleaved* only where a WAIT state says so; they may not be *reordered*
without amending this header with the reason.

---

## STEP 1 — Standalone k=1 lattice computation (instrument credibility)

**STATE:** EXITED 2026-08-11, DONE-WITH-CONSEQUENCE — INSTRUMENT-OWNED (branch 2 of the
pre-committed adjudication); the consequence is the v1.5 corrected-reference definition
(scope §4) and the overnight recompute campaign that Steps 2–4 now sit behind.
**LOG:** `step1_lattice_k1.py` + `step1_lattice_k1.json`. Part A: raw bulk gaps of the
once-differentiated lattice are 9.4e-8 / 2.4e-8 / 5.9e-9 at n = 1024/2048/4096 —
DECREASING with n, 3–6 orders below the flagged pipeline values (3.0e-4 / 5.8e-4 / 4.6e-3),
which the pipeline readout on the SAME roots reproduces exactly. Rootfinder independently
verified (mpmath dps 30, dev ≤ 1e-13 of spacing). Part B attribution: grid 16001 drops the
artifact 15–51×; 2ε drops it ~20× — the artifact is reference-CDF resolution at near-atomic κ,
worst at the n = 4096 aliasing crossover (4001 grid points < n roots). Runge-envelope magnitude
test moot (branch 1 not taken); the raw values' n-DECREASE matches the envelope-displacement
direction, consistent with real dynamics being ≤ 1e-8 in bulk. CONSEQUENCE FOR THE VERDICT
(measured, not assumed — probe in flight): the fit-window rows (iid/GUE k = 1, 2) were computed
on the same grid-4001 instrument; shift-vs-σ_mean probe running (6 replicates per seed class,
grid 4001 vs 16001). If material, the seal's post-change protocol governs: gate re-runs, then
instrument-corrected recomputation, verdict updated with full disclosure — F-1's misfit may be
partly this systematic.
PROBE LANDED (findings §9, be7f2b9): MATERIAL — shifts +24 to +38 σ_mean on the k = 1, 2 anchor
rows (~15% of signal at k = 1). VERDICT UNDER INSTRUMENT REVIEW; recompute campaign to be costed
after the grid-convergence study; Steps 2–4 all inherit the corrected instrument.

**Question:** Is the F-2 picket-fence row real root dynamics or an instrument artifact
in the near-atomic reference regime?

**Why first:** Cheapest item on the board, and every downstream claim (including the
banked verdict) is stronger or weaker depending on the answer. Resolve before any
external eyes on the arc.

**Method:** One polynomial with equally spaced roots at n ∈ {1024, 4096} (match the
flow runs), differentiate once, rootfind directly — no flow harness, no free-convolution
reference, no pipeline. Apply the identical central-window gap-ratio statistic
(BULK_FRACTION and unfolding convention copied from the harness, cited by file:line).

**Adjudication (pre-committed):**
- Standalone reproduces the flagged value AND its n-growth → row is real dynamics;
  candidate 2 (instrument) CLOSED; Runge-envelope mechanism gets its magnitude test
  (compute predicted midpoint displacement from the envelope log-derivative; compare;
  file match/mismatch either way).
- Standalone does not reproduce → instrument owns the residual; the ε-doubling trace
  and wider-bulk-window probes (already queued in findings) escalate from optional to
  required before Step 4.

**Exit criteria:** Adjudication filed as a finding with the F-2 cross-reference;
this doc's STATE updated; if instrument-owned, Step 4 gains a blocking dependency
(note it in Step 4's header).

**Budget guess:** Hours.

---

## STEP 2 — Environment-conditioned decomposition of the stretch (mechanism)

**STATE:** EXITED 2026-08-12 — **NOT_SUPPORTED** (pinned clause: 4/5 bins still F3, β ≈ 0.67–0.72).
The stretch is not (only) initial-environment heterogeneity. Richer-form fits returned to
exploratory backlog per the pinned ladder. Prize clause did not fire; no seal. Findings §11.
Texture banked without interpretation: bin0 alone exponential (τ = 3.07), bins 1–4 stretched
(τ ≈ 1.1–1.3).
**LOG:** Campaign outcome the run inherits: verdict INCONCLUSIVE-ON-INSTRUMENT-GROUNDS
(findings §10 — sealed powers-of-2 grid cannot adjudicate GUE's k* ≈ 6 transition; 4-point
primary window). Robust: both seeds stretched-exp where ladder assessable; k* flat in n
(iid ~11.0, GUE ~6.3). NOTE for interpretation: Step 2's per-bin fit windows use the same
sparse k-grid — fast bins may hit the same 4-point limitation; exploratory status absorbs
this, but the ladder outcome should name it if it binds.

**Question:** Does iid's stretched exponential decompose into narrower per-environment
exponentials when conditioned on initial local gap environment?

**Why before richer-form fitting:** Converts F-1's misfit work from fishing into
theory-selection. If decomposition holds, the correct richer family is a *derived*
rate-mixture integral over the seed's gap law, not a bigger fitted form.

**Method (first pass, no new flows):** Use the banked 48 iid §6.iv-b/science replicates.
Bin roots by initial local environment (e.g., quintiles of seed gap size around each
root; pin the binning rule in the runner header BEFORE looking at per-bin curves).
Track per-bin 1−⟨r̃⟩-style relaxation across k. Compare per-bin curves against
single-exponential fits.

**Interpretation ladder (pre-committed):**
- Per-bin ≈ exponential, rates ordered by environment → heterogeneous-relaxation
  mechanism SUPPORTED; stretch is a rate mixture; proceed to the derived-form test.
- Per-bin still stretched → mechanism NOT SUPPORTED as stated; the heterogeneity is
  not (only) initial-environment; file and stop — richer forms return to exploratory
  status.
- **The prize (only if supported):** derived prediction — for ANY seed class, the
  relaxation form is the mixture functional of its gap law. A falsifiable universality
  one level up from the one Track-0 falsified. If reached, this becomes a sealable
  claim: seal it against the picket-fence flow curves (already banked, never fitted)
  and/or a fresh seed class BEFORE computing the mixture prediction for them.

**Status note:** All of Step 2 is exploratory and unsealed unless/until the prize
clause fires, at which point the seal machinery from Track-0 is reused verbatim.

**Exit criteria:** One of the three ladder outcomes filed; STATE updated; if the
prize fired, the new seal committed before any cross-seed mixture computation.

**Budget guess:** A day, dominated by careful binning-rule pre-commitment.

---

## STEP 3 — Sealed n = 16384 scale-law discrimination (one expensive number)

**STATE:** EXITED 2026-08-13 — **SCALE-FLAT, sealed (iid arm: k* = 10.828 ± 0.011 vs
H_flat = 10.827, three decimals; log excluded ~10σ_eff)**; GUE rider unsealed-confirmatory
SCALE-FLAT (6.220 ± 0.004 vs 6.202, 0.35σ_eff). Both-arm runtime 23.5 h under the parallel
driver. Findings §13 + append.
**LOG:** Predictions re-derived from science_dense_grid.json — and the row-c rule caught the
conversation-level arithmetic: an affine log fit through the near-flat anchors is
non-identifiable (predicts 10.97, growth absorbed into the intercept), so the sealed log
hypothesis is PROPORTIONAL growth anchored at n = 4096. iid: H_flat = 10.827 vs
H_log = 12.704, separation 1.876; σ_sys = 0.192 filed openly (flat-model χ² = 27.9/2 — the
anchors are non-monotone with scatter beyond fit errors). GUE if-time arm: 6.202 vs 7.190.
Acceptance bands (3σ_eff/5σ_eff ≈ 0.6/1.0) cannot overlap — no double-positive possible.
Form-consistency rider reported, non-gating.

**Question:** Is k*(n) O(1)-flat or O(log n)? Three existing n's bound (α ≲ 0.1)
but cannot split these.

**The two predictions (to be RE-DERIVED from repo values and sealed before launch —
the anchors quoted in this doc's context paragraph are row-c-suspect by rule):**
- log-scaling: k*(iid, 16384) extrapolated from the two banked anchors (~13.2 by
  the conversation-level arithmetic; recompute).
- flat: continuation of the plateau (~11.5; recompute).
- Discrimination is many-σ if n=4096 precision (±0.07) holds; the seal must state
  the minimum separation that counts as discrimination, and an INCONCLUSIVE arm
  with power statement if precision degrades.

**Seal (tiny, uses existing machinery):** two point predictions + separation rule +
GUE arm optional (pre-decide: include iff budget allows both, and say which runs
first if the box dies mid-run). Master-seed protocol extended from 95e1ad3's
SeedSequence allocation — spawn NEW child indices; never reuse 0–95.

**Cost note:** per-step work ~n²; science window is small-k (k ≤ ~20) so flows are
shallow. Estimate wall-clock from the n=4096 arm's measured per-flow cost before
committing to the GUE arm. If cost is prohibitive → SKIP is legitimate: Step 4's
note is publishable at three n's with the scale question stated as bounded-not-resolved.
Record the skip decision and reason here if taken.

**Exit criteria:** Sealed verdict (log / flat / inconclusive-with-power) filed, or
documented SKIP. STATE updated.

**Budget guess:** Seal in an hour; run wall-clock TBD from measured cost — could be
the intensive step this doc exists for.

---

## STEP 4 — The writeup (short arXiv note)

**STATE:** UNBLOCKED 2026-08-12 — the corrected story is settled (findings §12):
RATE-SEED-DEPENDENT via the z-clause [SEALED-PROCEDURE, DISCLOSED-PRIOR-LOOK], triple-band
invariant F3/F3, z(τ) = 20.4 / z(β) = 9.3, k* flat. The verdict-history chain is the paper's
methodology section. UPGRADED 2026-08-12 (Will): the paper is now better than the
one queued — the instrument-review episode (artifact found by the roadmap's own regression step,
cured under the seal's pre-committed protocol, two permanent known-answer gates added, verdict
downgraded honestly rather than defended) is publishable methodology in its own right, and F-1's
resolution (the misfit was substantially the instrument) rehabilitates the form ladder the note
relies on. The honesty section writes itself from commits. The dense-grid verdict carries its
SEALED-PROCEDURE, DISCLOSED-PRIOR-LOOK grade label into the paper verbatim.
**LOG:** —

**Claim of the note:** First sealed, gate-certified measurement of fixed-k local
spacing statistics under repeated differentiation — the regime the literature pull
certified open (fixed-s/fixed-k local statistics; the proven results are global-law
along the flow and the k→∞ entire-function endpoint). Verdict: seed-class dependence
of the relaxation form (stretched vs exponential), k* separation, α ≲ 0.1 scale bound.

**Format:** Short note, math.PR (cross math.CA), harness public (repo link), floor
(Rolle/interlacing — citations pinned by the adversarial pull; verify pin state in
repo before citing) and ceiling (Hermite arm, measured) both stated. The seal protocol
is part of the contribution — pre-registered adjudication in experimental mathematics;
include the seal JSON and the commit-ordering table as an appendix.

**Honesty requirements (from findings §7, restate verbatim-equivalent):**
"F3 best-of-three, not a demonstrated law"; χ²/dof values; program-derived floor
label on the interlacing bracket; F-2 disposition per Step 1's outcome; verdict
string appears before narrative, same as the findings convention.

**Audience note:** Campbell–O'Rourke–Renfrew close at the entire-function limit
precisely because finite-n local statistics lacked results; they are the natural
first readers. Check 2410.06403 v2 (2026-05-21) and its citation graph one more
time at writing time — the pull's OPEN verdict ages.

**FRAME NOTE (2026-08-13, Will):** this is exploration published live on codeberg — the date
below was Will's own anti-completionism device (pinned 08-12 to stop the draft waiting on
runs), not an external obligation. It did its job (every slot filled ahead of it) and now
converts to: ship when ready, don't let the draft age, share what matters.

**PAPER PRE-COMMITMENTS (2026-08-12, pinned before drafting starts — the last place discretion
was hiding):** (1) **Target submission date: 2026-08-19.** (2) **Inclusion rule for the 16384
arm:** the paper ships on that date with whatever scale-law state exists then — the sealed
Step-3 verdict if landed, else three-n's bounded-not-resolved (α ≲ 0.1, non-monotone anchors,
O(1)-consistent). The paper is publishable today; the 16384 arm makes it better, not viable —
better does not take viable hostage. (3) The run's scope is pre-pruned in the seal itself:
iid-first, GUE-if-time. (4) The grade label travels with the verdict everywhere it appears,
abstract included; the v1 → review → INCONCLUSIVE → resolution chain is the honesty appendix
with commit hashes. (5) Abstract framing: ONE functional family (stretched exponential) with
seed-dependent parameters at 20σ/9σ, beneath a global measure ANP-class theorems freeze at
these k — same-family universality and its refutation one level down, measured under a sealed
procedure that survived its own instrument crisis in public. The β-composition (both seeds
stretch; Step 2 falsified seed-carried heterogeneity under blind rules) goes in the discussion
as the open mechanism question.

**FRAMING REBUILD (2026-08-12, Will's post-pull sweep — scope §9):** the introduction is built
around the two-scale contrast with Angst–Nguyen–Poly 2601.01212: the global zero measure is
provably FROZEN through k = o(n/log n) while our measurement shows local spacing fully
crystallized by k ≈ 10 at every n — small-k crystallization is a purely local rearrangement
beneath a provably preserved macroscopic profile, open AND provably invisible to the strongest
global theorems. Care-flag DISCHARGED (scope §9): Uniform[−1,1] is inside ANP Thm 1.3(2) via
their C¹-curve example; the paper is verified silent on local statistics — the citation is safe
and the contrast exact. Writing-time re-sweep
must specifically check Jalowy–Kabluchko–Marynych Part III (fluctuations/functional limit
theorems — either the theory our curves test or the scooping result). Cite the complex-flow
exclusion as a live boundary (Galligo–Najnudel–Vu line).

**Exit criteria:** Preprint on arXiv; repo tagged; STATE updated with the identifier.

**Budget guess:** Days, spread.

---

## STEP 5 — dBN cross-flow comparison (new arc, not a task)

**STATE:** NOT STARTED — QUEUED behind Step 4 (its scope is cleaner out of the note,
and it deserves its own arc doc)
**LOG:** —

**Question:** Run Phase 2's dBN heat-flow rigidification through the same
⟨r̃⟩-distance readout and matched seed classes: exponential, stretched, or other?
First genuinely cross-instrument measurement of the program — two flows, one axis,
one statistic.

**When opened:** Gets its own scope doc on the Track-0 template (gates → seeds →
seal → verdict), authored fresh; this doc's role ends at handing over the measured
derivflow form pair as the comparison target. ζ′/Speiser stays queued behind this —
differentiation statistics of ζ is where those threads meet.

**SCOPE-TEMPLATE REQUIREMENT (2026-08-13, from the lemmatizer-essay review — the frame's first
falsifiable export):** the cross-flow scope doc MUST pre-register a commutativity audit — two
or three view-move orderings (e.g., unfold∘window vs window∘unfold), both run, discrepancy
either banked as a commutativity certificate or named as a transition-function bug / genuine
path-dependence before it names itself. See essays/lemmatizer_review_2026_08_13.md.

**VALUE/URGENCY RAISED (2026-08-12, scope §9 sweep):** the heat-flow half of the bridge is now
built and published (Hall–Ho–Jalowy–Kabluchko: Indiana 2025, EJP 2025, LMP 2025), and the
literature is already citing Lehmer-pair/dBN work alongside differentiation-flow papers — the
local-statistics comparison this step queues is the unclaimed measurement in a visibly
converging field. Worth moving while that's true.

**Exit criteria (for THIS doc):** Cross-flow scope doc committed; STATE here updated
with its path; this roadmap is then complete and archives.

---

## Parallel-track notes (not steps, do not interleave into the queue)

- **Wrap arc** runs independently on WRAP_ARC_BRIEF.md in its own session. No shared
  state with this queue except the eventual ζ′ convergence noted in Step 5.
- **Richer-form fits** for F-1 exist only inside Step 2's ladder; they do not get
  their own queue slot. If Step 2 files NOT-SUPPORTED, they return to backlog as
  exploratory, and stay there. [2026-08-12: NOT_SUPPORTED filed; returned to backlog.]
- **Dynamical-heterogeneity hypothesis (backlog, unsealed, 2026-08-12; upgraded 2026-08-13):**
  Step 2 falsified seed-carried heterogeneity; the corrected instrument shows homogeneous-rigid
  GUE also relaxes stretched. In the glass literature's own dichotomy (KWW origin: dynamically
  generated heterogeneity vs intrinsic local nonexponentiality), the mid-flow re-conditioning
  probe (bin on environment at k = 2 instead of k = 0) **is the ISOCONFIGURATIONAL-ENSEMBLE
  move translated to root flows** — the field's standard instrument for exactly this
  separation, and structurally an experiment the harness already performs. The bin0 texture
  (clean exponential, 3× slower, one tail of the environment distribution) is the fact any
  mechanism must face.
- **Seed-roster extension — DONE 2026-09-09** (`seed_roster_beta.py/.json`,
  `verify_seed_roster.py`, board row). Verdict
  **RELAXATION_SCALE_ORDERS_WITH_SEED_REPULSION**: the (τ, β) seed-dependence is a
  SURFACE and local repulsion is its coordinate. **Roster changed from the wording
  below, with reasons**: the JKM combinatorial families are catalogued by their
  GLOBAL shape, their roots at n = 4096 are numerically out of reach, and varying
  global shape would confound the very two-scale structure this arc separates.
  β-Hermite ensembles fix all three — the existing GUE seed is already the DE β = 2
  tridiagonal, every β shares the same semicircle global law, and β *is* the
  repulsion exponent. P1 = **0 of 40** (β = 2 reproduces the banked GUE arm
  exactly, so the existing science run became this cell's premise); P2 max
  pairwise seed-law KS **0.0012** against a 0.05 bar, so the global measure is
  genuinely held fixed. The matched surface:

  | β | k* | τ | stretch |
  |---|---|---|---|
  | 1 | 6.9223 | 0.9732 | 0.7172 |
  | 2 | 6.1628 | 0.8884 | 0.7030 |
  | 4 | 5.4664 | 0.8031 | 0.6837 |

  k* strictly decreasing, 0 inversions, ends separated by **122.9 σ**; τ and the
  stretch exponent order with it, so all three fit coordinates move together with
  repulsion. **Scope:** the matched comparison is the β-ensembles only. iid
  (k* 10.889, τ 1.734, stretch 0.788) continues the trend in every coordinate but
  carries a *different* global law (uniform, not semicircle), so it is an
  unmatched reference and not a fourth point on the surface. All comparisons at
  k*, never τ. ORIGINAL ITEM, kept for provenance:
- **Seed-roster extension (backlog, 2026-08-13):** JKM Part II is a catalog of
  exactly-characterized seed families (Touchard, Fubini, Eulerian, Narayana, hypergeometric
  incl. Hermite/Laguerre/Jacobi) — the ready-made third and fourth seed classes if the
  (τ, β) parameter-dependence question graduates from two-point comparison to a
  parameter-surface measurement.
- **GUE-adapted isoconfigurational probe — DONE 2026-09-08**
  (`gue_isoconfig_adapted.py/.json`, amendment `gue_isoconfig_kstar_amendment.py/.json`,
  `verify_gue_isoconfig.py`, board row). Verdict
  **STRETCH_MECHANISM_IS_NOT_SEED_DEPENDENT.** The adaptation worked as designed:
  smallest GUE per-bin window 3 -> 10, so the question became askable. Under the
  IDENTICAL adapted design both classes read NOT_SUPPORTED with **5/5 bins selecting
  F3 with beta < 0.9** — iid 5/5 is the control, so the result is not an artifact of
  the redesign. **What is seed-dependent is the parameters, not the mechanism**;
  conditioning fails to decompose the stretch in either seed class, at a third
  conditioning time. The pre-committed GUE texture appeared: its bins span only 2.2x
  in tau against iid's 49x, yet every one is stretched at beta 0.62-0.78 — stretch
  with almost nothing left to average over, which the 08-14 note named in advance as
  the cleanest intrinsic-nonexponentiality datum available.
  **THE BINDING SECONDARY, and my own defect in it.** C2 MISSED (1.897 vs 1.5) and is
  kept missed, but the arm compared tau across DIFFERENT FORMS — the slow bin is F2 at
  K_COND=2 and F3 at K_COND=1 in both classes, and F3's tau is degenerate with beta.
  On k* (level crossing, form-independent, already this arc's scale-law statistic) the
  reading REVERSES: iid 13.631 -> 13.510 (1.009), gue 7.039 -> 6.754 (1.042), both
  stable to within 5%, every bin stable rather than only the slowest. So the slow
  subpopulation DOES keep its timescale across a third conditioning time — the
  scientific claim is supported, the arm is not, and the two are recorded separately.
  Same cause found in a second place: the artifact's tau_monotone = False for adapted
  GUE is a degeneracy artifact; k* decreases strictly, so GUE does order monotonically
  by environment. **CARRY-FORWARD: tau is not a safe cross-fit comparison quantity in
  this arc — compare relaxation timescales at a level crossing.**
  ORIGINAL ITEM, kept for provenance:
- **GUE-adapted isoconfigurational probe (backlog, 2026-08-14):** the 2b GUE arm was
  underpowered (findings §14 addendum — 3–4-point windows, F3 unassessable); the adapted design
  is K_COND = 1 with k-grid from 2. Whether GUE's stretch decomposes under conditioning —
  which would make the STRETCH MECHANISM itself seed-dependent, not just the parameters — is
  the open question this probe exists to answer. BINDING (2026-08-14, findings §14 closing
  note): the probe's scope must carry the SLOW-SUBPOPULATION question as a sealed secondary —
  three unsought sightings (τ 3.07 / 3.18 / 2.34–2.35) across two seed classes and independent
  conditionings; both heterogeneous and intrinsic fingerprints present at once; the sealed
  secondary adjudicates coexistence vs wrong-conditioning-variable rather than waiting for a
  fourth accident.

- **Correlated-error treatment of the shape-z — DONE 2026-09-08**
  (`zbeta_correlated_error.py/.json`, `verify_zbeta_correlated_error.py`, board row).
  The repair the item below asks for was built and run: the 16 per-replicate curves were
  RECOVERED (they were never banked — only means and SEs were) and reproduce the sealed
  artifact exactly, 0 of 80 numbers mismatched, with the recovered fit parameters equal to
  the banked `shape_params` to double precision. Findings, in the order they matter:
  (i) **the decision is invariant** — z(beta) clears the sealed 5-sigma bar under all seven
  treatments (bootstrap 8.24, GLS shrinkage sweep 9.97–11.12, sealed 9.31, conservative
  5.84), so beta's margin is not an artifact of the independent-sigma assumption and the
  "thin margin" worry is retired; (ii) **the diagnosed mechanism is real** — median |r|
  across fit-window k-pairs is 0.729 (GUE) and 0.875 (iid); (iii) **but the audit's reading
  of its DIRECTION was backwards for GUE** — correlation TIGHTENS beta there
  (sigma_boot/sigma_indep = 0.735) because the common mode is degenerate with the amplitude
  parameter while the shape lives in cross-k differences; (iv) **and the direction is itself
  seed-dependent**, which the seal did not anticipate: iid LOOSENS (1.363), since its
  chi2/dof = 3.76 misfit is absorbed as genuine parameter scatter where GUE's 0.0175 is
  dominated by common-mode cancellation. (v) **C4 MISSED and is kept**: bootstrap and GLS
  disagree by up to 34.9% against a 25% bar, so this cell licenses a RANGE and not a point
  value — plausibly the bootstrap's own declared ~18% SE floor at R=16 plus GLS
  regularisation sensitivity (the GLS sweep trends to the sealed value as shrinkage rises,
  which is its sanity check passing), but that reading is a diagnosis and is not tested here.
  ORIGINAL ITEM, kept for provenance:
- **Correlated-error treatment of the shape-z (backlog, 2026-08-16, from the packaging audit):**
  the conservative convention rescales each covariance by max(1, χ²/dof). On the n = 4096
  primary arm that inflates iid by 3.76 and is **INERT on GUE**, whose χ²/dof = 0.017 — so the
  conservative z(β) = 5.84 clears the sealed 5σ bar while resting on a GUE σ that the same
  readout discloses as underdispersed by cross-k correlation from shared replicates. The
  asymmetry is now STATED in the brief and in PROSE; it is not repaired, because repairing it
  is a new analysis, not a transcription. What the repair needs: an error model that carries
  the replicate-sharing covariance between k-points explicitly (block covariance over the
  16-replicate ensemble), rather than treating the per-k σ_mean as independent. Until then
  z(β)'s margin should be read as thin in the direction NOT covered by the rescale. Note the
  under-dispersion is itself an untested mechanism claim — 'shared-replicate correlation' is
  the diagnosis on offer, and nothing in the record tests it; the repair would test it.
  This does not touch the sealed verdict, which stands on the sealed rule as executed.

## Resumption protocol (the reason this doc exists)

On picking this doc up after a gap or an intensive detour:
1. Read STATEs top to bottom; find the first non-exited step.
2. Read that step's LOG; check its cited commits exist and its blocking deps are exited.
3. Re-verify any number the step consumes against the repo (row-c rule) — including
   the numbers in this doc's own context paragraph.
4. Continue. If the plan no longer fits what was found, amend the doc FIRST, in its
   own commit, then work.

## QUEUE REORDER 2026-08-18 — the correspondence is not a collaboration

**STATE:** Campbell (ISTA) replied to the measured-values sheet with corrections and
pointers. He is not a collaborator and this is not a joint project; he was told
something possibly interesting and pointed at places to look. Consequences for the
queue, in Will's framing:

- **NO REPLY IS PENDING, and no draft is held.** If a reply happens at all it is weeks
  out, three lines, and only if the reading produces something worth saying. The arXiv
  posting can itself be the next contact. He learns the exchange mattered by seeing his
  references cited correctly and his corrections absorbed in a finished artifact —
  which is the only currency this community runs on. Asking him to summarise his own
  field's unwritten folklore is the thing not to do.
- **PRIORITY 1 — read arXiv:2408.09337 (Arizmendi–Fujie–Perales–Ueda, S-transform in
  finite free probability) properly.** This is the load-bearing one and we have only
  skimmed it. His "understood or follow from work that's out there" almost certainly
  routes through this machinery. The real question, and it is checkable rather than
  rhetorical: **is the local relaxation form derivable from finite free cumulants /
  S-transform asymptotics by someone willing to grind?** Specifically, does a
  stretched exponential in k with seed-dependent (τ, β) fall out, or does the machinery
  control only the global measure? Days of reading, not an email.
- **PRIORITY 2 — absorb doi:10.4171/dm/1071 (Campbell, Appell polynomials).** This is
  now the correct citation for the endpoint regime and should be cited as such rather
  than via the Hoskins–Steinerberger shorthand.
- **PRIORITY 3 — finish the note under the corrected framing** (§9 amendment
  2026-08-17): real-roots o(n), and folklore re-grade — the local regime is EXPECTED by
  the people who would know, so the note is a quantified measurement of something
  believed but unquantified, not a report from open territory.
- **CLOSED, needs nothing from him:** EDGE-0 (`edge0_gate.py`, verdict
  EDGE_NOT_READABLE) is complete as an internal result — gate-before-science, the
  definitional diagnosis, and the limitation line all stand on our own run.

## RESUME HERE — state at 2026-08-19

**One-line state:** the arc is in its READING phase, not its measuring phase. Priority 1
is done and produced a memo that changes the note's framing; Priority 2 is next and has
not been started. **No reply to Campbell is pending or drafted — that is deliberate, not
an omission** (see the 2026-08-18 queue reorder above before considering one).

### Done since the correspondence
- `TRACK0_SCOPE.md` §9 — external-correction amendment (2026-08-17). Real-roots **o(n)**,
  not o(n/log n); the OPEN verdict is narrowed to a folklore re-grade. Propagated to
  PROSE, README, fig4.
- `edge0_gate.py` → `edge0_gate.json`. **EDGE_NOT_READABLE**, 0/10 cells, acceptance rule
  stated before the run. The bulk unfolding has no valid edge extension; this is
  definitional, not a resolution bug. CLOSED — needs nothing from anyone.
- `cumulant_gate.py` → `cumulant_gate.json`. **PASS** at machine precision, 42 cells. New
  independent gate from AFPU Lemma 3.2 (normalized coefficients invariant under
  differentiation). Tests the FLOW, where every other gate tests the readout.
- `DERIVABILITY_MEMO.md` — **Priority 1 COMPLETE.** arXiv:2408.09337 read in full text.
  Verdict: the measured form is NOT derivable from that machinery, structurally. The
  controlled quantity is invariant to 2.6e-14 while the measured one moves 4,492x.

### Update 2026-09-08 — the regime sweep Priority 1 did not do

Priorities 1–3 were organised around the three papers Campbell NAMED. Enumerating a
correspondent's citations is not a literature sweep of the surrounding regime, and the
difference cost three weeks: **arXiv:2408.13851 (Martínez-Finkelshtein–Rakhmanov, "Flow
of the zeros of polynomials under iterated differentiation", v3 2025-09-21)** — the most
general global treatment of the proportional regime k/n → t, unifying Burgers/Hopf,
fractional free convolution and the nonlocal diffusion equation — was in no document in
this repo until today. It was found by sweeping the regime rather than the correspondence.
Read in extracted full text on the same vocabulary as 2408.09337: **0 hits** for spacing,
gap, microscopic, consecutive roots, fluctuation, rigidity, point process, pair
correlation, universality, nearest-neighbour, crystalliz-; all 12 *local* hits are
"nonlocal transport/diffusion" (the PDE's name) or "locally uniformly". The gap claim is
INTACT, and PROSE now states it regime-by-regime — proportional / small-k / endpoint, each
covered globally, none containing a local-spacing statement — which is a stronger and more
falsifiable form of the claim than the two-territory sandwich it replaces.
Also filed today: PROSE contained **no mention of the edge anywhere**, so a reader could
have taken bulk results for edge claims; the EDGE-0 verdict is now stated at the readout.

### Next, in order
1. **Priority 2 — doi:10.4171/dm/1071 (Campbell, Appell) at full depth.** Abstract now
   VERIFIED at the published DOI (Documenta Math., 2026-05-03), which states the regime in
   the author's own words — the limits are the real rooted Appell sequences when "the
   number of derivatives is such that the remaining degree is fixed" — so the endpoint
   placement no longer rests on context. Full-text depth is still open, and is now a
   citation-quality item rather than a scoping risk. Route: fetch the PDF and extract with
   `pypdf` (available in the venv; no pdftotext/gs on this box) exactly as was done for
   2408.09337 and 2408.13851.
2. **Priority 3 — finish the note under the corrected framing.** The memo §5 gives the
   new lead: *the scale confirms the folklore; the form is what it does not reach.*
   Retire "the local regime is open" and retire the flat scale as headline novelty.
   `paper/PROSE.md` is the draft; the outreach PDFs live OUTSIDE this repo.
3. The reply question answers itself from 1–2, or does not, and then there is no reply.

### Housekeeping a fresh session should know
- **55 commits unpushed.** `git push origin cubics-wilderness` needs Will's ssh key; it
  cannot be done from an agent shell (no ssh-agent, passphrase-protected).
- **`git gc` is warning on every commit** (`.git/gc.log`, too many unreachable loose
  objects). `git prune` clears it — and would also drop the unreachable objects from an
  earlier local history rewrite, which is desirable. Not run: it discards ALL unreachable
  objects repo-wide and this repo has other sessions' history in it.
- **Another session works in this repo concurrently.** Check `git status` before assuming
  a dirty tree is yours.
- Verification board: `python3 verify_all.py` (~20 s, 9/9). `AUDIT.md` and `REPRODUCE.md`
  are the outside-reader entry points.

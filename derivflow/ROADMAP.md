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

**STATE:** SEALED + LAUNCHED 2026-08-12 (`seals/SCALE_LAW_SEAL.json`; runner
`step3_scale_law.py`, detached). Multi-day intensive step; the draft does not wait up for it.
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
- **Dynamical-heterogeneity hypothesis (backlog, unsealed, 2026-08-12):** Step 2 falsified
  seed-carried heterogeneity; the corrected instrument shows homogeneous-rigid GUE also relaxes
  stretched. The conjunction points the mechanism hunt away from "carried from the seed" toward
  "generated by the flow" — dynamical heterogeneity in the glass-relaxation sense. Cheap future
  discriminator: re-condition MID-FLOW (bin on environment at k = 2 instead of k = 0) and see
  whether that decomposes the stretch. The bin0 texture (clean exponential, 3× slower, in
  exactly one tail of the environment distribution) is the fact any such mechanism must face.

## Resumption protocol (the reason this doc exists)

On picking this doc up after a gap or an intensive detour:
1. Read STATEs top to bottom; find the first non-exited step.
2. Read that step's LOG; check its cited commits exist and its blocking deps are exited.
3. Re-verify any number the step consumes against the repo (row-c rule) — including
   the numbers in this doc's own context paragraph.
4. Continue. If the plan no longer fits what was found, amend the doc FIRST, in its
   own commit, then work.

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
precision, χ²/dof ≈ 31 (iid) / ≈ 1062 (GUE); (F-2) picket-fence clause fired on one
row (n=4096, k=1, 4.6×10⁻³ vs 10⁻³ bound, transient by k=8, grows with n).
Do not inherit numbers from this paragraph into new work without repo confirmation
(row-c rule).

**Ordering principle:** each step is the cheapest thing that de-risks the next.
Steps may be *interleaved* only where a WAIT state says so; they may not be *reordered*
without amending this header with the reason.

---

## STEP 1 — Standalone k=1 lattice computation (instrument credibility)

**STATE:** NOT STARTED
**LOG:** —

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

**STATE:** NOT STARTED — may start in parallel with Step 1 (no shared dependency)
**LOG:** —

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

**STATE:** NOT STARTED — BLOCKED until Steps 1–2 exit (Step 1 for instrument
credibility; Step 2 because its outcome may add a sealed per-environment prediction
to this run for free)
**LOG:** —

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

**STATE:** NOT STARTED — BLOCKED on Step 1 exit (instrument credibility). NOT blocked
on Steps 2–3: publishable at three n's, scale bounded-not-resolved, mechanism section
conditional on whatever Step 2 filed by then.
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

**Exit criteria (for THIS doc):** Cross-flow scope doc committed; STATE here updated
with its path; this roadmap is then complete and archives.

---

## Parallel-track notes (not steps, do not interleave into the queue)

- **Wrap arc** runs independently on WRAP_ARC_BRIEF.md in its own session. No shared
  state with this queue except the eventual ζ′ convergence noted in Step 5.
- **Richer-form fits** for F-1 exist only inside Step 2's ladder; they do not get
  their own queue slot. If Step 2 files NOT-SUPPORTED, they return to backlog as
  exploratory, and stay there.

## Resumption protocol (the reason this doc exists)

On picking this doc up after a gap or an intensive detour:
1. Read STATEs top to bottom; find the first non-exited step.
2. Read that step's LOG; check its cited commits exist and its blocking deps are exited.
3. Re-verify any number the step consumes against the repo (row-c rule) — including
   the numbers in this doc's own context paragraph.
4. Continue. If the plan no longer fits what was found, amend the doc FIRST, in its
   own commit, then work.

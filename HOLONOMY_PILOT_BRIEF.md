# Commutativity Pilot — Measuring the Holonomy of the Measurement Stack

**Status:** APPROVED, AMENDMENTS FOLDED (Will's A1–A3 + CC's R1–R5, 2026-08-15). Authorized
for an overnight run. Pilot-sized: one session target, protocol-arc opening cell per the
registered follow-up (bridge follow-ups list).
**Lineage:** Atlas/Erlangen session (2026-08-13): non-commuting view-moves = curvature of
measurement space; the Σ² inverted-lens bug (found by accident, motivating instrumentation);
bridge dual implementations of every transition (the reason this is now cheap); promoted
protocol rules (TOOLKIT §9: dry-run, rulings-as-code, witness-must-fail, committed generators).
**Epistemic posture:** protocol arc. Synthetic data and already-banked substrates only;
**no new science claims of any kind.** The deliverable is a measured commutator table and a
canonical-order registry enforced in code.
**Honest one-line frame:** the pipeline applies sequences of transitions (unfold, window,
reweight, edge-correct, surrogate, disattenuate) whose order was chosen implicitly, script by
script. This pilot measures which orders matter, how much, and under what law — then turns
every order that matters into a code-enforced ruling instead of a per-script accident.

---

## 0. Objects and definitions

A **move** is a registered transition function T acting on a point set + metadata. **Notation,
stated once: all orderings are written in arrow form, "A → B" meaning A applied first**
(matching the §1 pair names; the ∘ convention is not used anywhere in this arc). For a pair
sealed as "A → B vs B → A" and scalar statistic S, the **commutator observable** is the
**signed difference under the sealed listing order**: Δ = S(X under A → B) − S(X under B → A).
The sign is load-bearing — it says which direction the order pushes the statistic and is half
of what makes each law falsifiable; |Δ| is used for all magnitude comparisons. Class calls are
not an S — categorical outputs have no difference; their order-sensitivity is measured as
**the shift in margin of the underlying discriminating statistic**, which folds into the
materiality metric below.

**Pre-drawn randomness (applies to every pair containing a stochastic transition — thinning,
surrogate generation):** where a transition makes per-point random decisions, the randomness
is **drawn once, before either ordering runs, and attached to each point as metadata**; the
transition consumes that point's own pre-drawn value regardless of where it falls in the
sequence. Without this, the two orderings consume the RNG stream against different inputs
(weighted vs unweighted point sets) and diverge in their accept/reject sequences — Δ would
then measure stream drift, not order, and would look exactly like a finding. This discipline
is sealed once here and inherited by P3 and by optional pair 1.

**Instrument randomness is re-runnable (A1):** a pair with a fixed substrate is dial-less but
**not seed-less** when it contains a stochastic transition. The pre-drawn u is itself a draw:
re-drawing u and re-running **both orderings against each new u** gives a paired difference
per draw and a genuine σ_Δ over draws. Δ is deterministic *conditional on u* and random
*over u*; the two must not be collapsed. This upgrades such pairs from bare tolerance
comparisons to properly powered detection tests. Only substrates with **no** stochastic
transition anywhere in the pair (the zeta window in P1) are true deterministic point-checks,
reported with a sensitivity envelope and never significance-tested.

**Two denominators, never interchanged — and two substrate roles, never conflated:**
**law-fitting happens on the synthetic families only**, where seeds exist and σ_Δ (the
paired-difference standard error over seeds) is a real sampling error. **Deterministic fixed
substrates (the zeta window) contribute point-checks only:** their Δ is deterministic; it is
reported with a sensitivity envelope (sealed estimator-bandwidth jitter) and checked for
consistency with the synthetic-fitted law where one exists, **never significance-tested** —
an envelope is not a test statistic. **Stochastic fixed substrates (D1 randoms under
thinning)** get σ_Δ over u-draws per A1. For **materiality**, the denominator is **the banked
result's margin to its own gate boundary** — a verdict 0.3σ from threshold is at risk from a
small Δ; one 5σ clear is untouched by a large one.

Three regimes, named in advance:
- **Exact commutation:** |Δ| within the sealed numerical tolerance (e.g., two diagonal
  reweightings). **The fp tolerance is scoped to this regime only (A2): it applies to
  reordered floating-point arithmetic of provably-commuting transitions, and explicitly does
  NOT apply to P3**, whose mechanism produces genuinely different keep-sets with a stochastic
  Δ floor orders of magnitude above fp scatter.
- **Approximate commutation:** |Δ| above tolerance with a derivable scaling law in **the
  pair's own sealed dial** (see §2) — the prediction is part of the arc.
- **Material non-commutation:** Δ consumes a non-trivial fraction of any banked gate-feeding
  statistic's margin to its boundary at realistic dial values.

## 1. Mandatory move pairs (one per dialect family; optional pairs listed in §8)

- **P1 (1D home dialect):** unfold → window vs window → unfold. Substrate: zeta window
  (banked, `zeros_2000.npy`, Odlyzko lineage) + synthetic GUE with imposed smooth density
  trend. **Dial: one sealed primary axis — window-length-to-density-variation-scale ratio —
  with unfolding-estimator bandwidth fixed at a stated sealed value** (a 2D dial has no top,
  and the lattice quantifies over a top). **Bandwidth sensitivity is reported, not swept, and
  on both substrate roles: the same sealed jitter that produces the fixed-substrate envelope
  is also applied to the synthetic runs as a reported envelope on the fitted coefficient.**
  Probing bandwidth only on the substrate that contributes no law would leave the law itself
  bandwidth-unprobed; this is cheap and says whether the coefficient is bandwidth-fragile.
  Statistics: Σ²(L) (primary ruling statistic), NNS-KS (expectation-target form, secondary),
  ⟨r̃⟩ (predicted commutation-insensitive — the internal control).
  **Three unfoldings are in play (R4): the true analytic warp (imposed on the synthetic),
  the full-set estimated unfolding, and the truncated-set estimated unfolding. The
  correctness leg's S_true is computed under the analytic inverse warp — never against either
  estimated unfolding as if it were truth.**
  **Σ²'s own L-grid is sealed as fractions of window length (R5), not absolute L:** the dial
  sweeps window length, and a fixed absolute L would silently change L/W along the ladder,
  confounding the law fit.
- **P2 (2D bridge dialect):** intensity-reweight → edge-correct vs edge-correct → reweight.
  Substrate: synthetic inhomogeneous Poisson through the bridge window classes at the FIX-2
  designed-gradient family (1.2^n ladder up to 4.30×). Statistics: K_inhom, pcf. The
  mechanism, named: the λ̂ estimation domain — one ordering fits intensity on the full
  window, the other on the edge-operation's eroded domain; with a gradient the two fits
  differ at the boundary. (Same mechanism family as P1: estimate-on-what-domain.)
- **P3 (survey dialect):** weight-application → randoms-thinning vs thinning → weighting on
  the D1 sealed randoms subsets (KAG data only; no catalog rows touched). Statistic: F(L) at
  two sealed L. **P3 is dial-less (the survey selection function cannot be dialed: no
  gradient ladder, no fitted law) but per A1 it is not seed-less: the sealed design is
  n_draws pre-drawn u-vectors, both orderings run per draw, paired Δ per draw, σ_Δ = SEM
  over draws.** Its reachable verdicts are POINT_CHECK_CLEAN, UNDERPOWERED, or
  ORDER_RULING_REQUIRED (§3); its honest positive result is "mean order effect consistent
  with zero at the sealed power," not a law. Thinning is stochastic — the §0
  pre-drawn-randomness discipline is mandatory here.
  **The mechanism, named in the seal (R1):** the frozen `thin_to_data` computes a *scalar*
  keep probability p = W_target / Σw_randoms — normalized by the **weighted** total.
  Thin-then-weight normalizes by count, weight-then-thin by weighted sum; since randoms
  weights are non-uniform, p differs between orderings and the shared pre-drawn u makes the
  two keep-sets **nested** (scalar thresholds on the same u). The pair can fail.
  **The suppressor, named in the same breath (R1):** the mechanism is a scalar density
  shift, and the downstream stack (DD/RR ratios, randoms-derived F expectations) is built to
  cancel scalar density shifts. A clean P3 therefore certifies "mechanism present AND
  estimator suppresses it," not "no mechanism" — the §12 registry entry carries both halves
  (gate-certifies-half discipline), so a future refactor that abandons ratio estimators does
  not inherit a clean row it isn't entitled to.
  **Sealed sign prediction (A3):** because the keep-sets are nested, one ordering always
  retains fewer points, and which one follows from the sign of (w̄_data − w̄_randoms) via
  p_W/p_T = w̄_data/w̄_randoms. This is sealed as a prediction-first commitment **on the
  retained-count observable** (the direct prediction; Δ_F's sign is suppressor-mediated and
  not predicted). If the measured count-difference sign comes back opposite, that is a
  finding about the plumbing before it is a finding about holonomy — halt and audit.
  **Freeze collision, resolved (R2):** `thin_to_data` draws its RNG internally and lives in
  `mask_kag.py`, which is blob-SHA frozen under the survey seal; threading pre-drawn u
  through it requires a signature change, and touching the file trips `verify_survey.py`.
  Therefore holonomy/ carries its own u-threading variant. Two obligations attach: (i) the
  variant's **diff against the frozen blob is banked** as part of the committed generator;
  (ii) an **equivalence test** is run and banked — the variant, driven with internally-drawn
  u at a matched seed path, must reproduce the frozen function's behavior — otherwise
  wrapper fidelity is asserted rather than measured. The census records the variant as a
  **transfer surface**, and it is a *tested* surface only once (ii) passes.

## 2. Design

- **KAG (commutation null, non-vacuous):** the null must test the composition machinery under
  load, not that identity maps compose. Each pair's null uses **non-identity transitions that
  provably commute analytically** (e.g., two diagonal reweightings with distinct, non-trivial
  weight functions) run through the same plumbing — exact commutation required within the
  sealed numerical tolerance. Homogeneous-identity runs are retained only as a smoke test,
  explicitly labeled as such. A pair failing its null is an implementation defect, not
  holonomy — fix before measurement (the KAG is the legal debugging window, per the D1
  precedent; sealed before measurement runs).
- **Per-pair dial, sealed with the derivation:** each pair names its own sensitivity axis in
  its sealed derivation, because the pairs' commutators live on different axes — **P2** on
  the inhomogeneity-gradient ladder (1.2^n up to 4.30×); **P1** on
  window-length-to-density-variation-scale ratio, because its leading term is boundary-driven
  (whether the unfolding density was estimated on the full or truncated set), not a power of
  g — bandwidth enters the sealed derivation as a fixed coefficient at its sealed value,
  never as a swept variable, so the predicted law is not written in a quantity the run never
  moves; **P3** has no dial at all (§1) but has a sealed draw count (A1). Sweeping a wrong
  common axis and banking COMMUTES off a flat curve is the failure mode this clause exists
  to prevent. The banked object per dialed pair is **Δ(dial) with its fitted law against the
  sealed prediction**; for P3 it is the draw-ensemble mean Δ with its SEM and the A3 sign
  check. **Sealed predictions are committed continuum derivations, not exponent guesses:
  each dialed pair's prediction is generated by a committed script that applies both
  orderings to the exact continuum density (deterministic functional calculation, no point
  noise), producing a parameter-free predicted Δ(dial) curve before measurement.**
- **Correctness leg (the ruling basis, with type-dependent targets):** where ground truth
  exists — P2's synthetics and P1's trended GUE — the arc measures per-ordering bias. **For
  point-value statistics (K_inhom, pcf, Σ²), the target is S_true and the comparator is
  |S − S_true| — with S_true computed under the analytic truth (R4), never an estimated
  unfolding. For distributional discrepancy statistics (NNS-KS), "true" is a null
  distribution, not zero: a KS against the GUE reference has a positive finite-N
  expectation, and ruling toward the smaller KS would select for overfit and call it lower
  bias. The comparator there is closeness to the finite-N null expectation under the sealed
  construction. P1's primary ruling statistic is Σ²(L); KS participates in the leg only
  under the expectation-target form, labeled secondary.** Where the orders differ, the
  canonical order is **ruled toward lower bias**; where biases are indistinguishable, the
  ruling is arbitrary-but-consistent and the registry says so (§4). **The leg has its own
  two-sided witness (§6).** **P3 has no ground truth (the D1 randoms are data, not a model):
  its rulings are RULED_CONSISTENT by construction, stated in the seal** — a survey-dialect
  synthetic analogue is out of pilot scope (§7) with a sealed promotion trigger (§7a). Where
  a synthetic-derived ruling is applied to a fixed-substrate call site, that is a **transfer
  inference** and the registry records it as such. Δ alone establishes that orders differ —
  it cannot say which is right; this leg can, where truth exists.
- **Repo retro-audit (ownership map first, then grep):** call-site grep alone misses
  transitions performed *inside* functions that don't advertise them (a window routine that
  internally edge-corrects reads as one call and the pair silently vanishes from the
  census). Step 1: build the **function → transitions-performed map** for the estimator
  stack. **The coverage fraction has a committed denominator (R3): the frozen
  estimator-stack file/function list is enumerated FIRST and committed — that list is the
  denominator; the numerator is functions classified, where "performs no transition" is
  itself an explicit classification.** Coverage = classified/enumerated, not mapped/found —
  a lazy map cannot read 100%. Step 2: census orders against that map, every row file:line.
  Step 3: bank the coverage fraction with a committed generator, **against a sealed
  minimum: below the floor, the census verdict is INCOMPLETE and no pair may be marked
  clean on census grounds — only on measured-Δ grounds.** A 55% census and a 98% census
  must not produce identical-looking clean rows. Flag any pair appearing in both orders in
  live code (latent defect class regardless of measured Δ); list banked results downstream
  of each ordered pair.
- **Materiality check (margin-denominated):** for every pair with **|Δ| above the sealed
  numerical tolerance** (or, for P3, mean Δ excluded from zero), evaluate Δ at each
  downstream banked result's own dial values **against that result's margin to its gate
  boundary** — the corruption question asked prospectively: could any banked verdict flip
  under the opposite order? Expected answer no; the check converts expected into verified,
  in the only units where "material" means anything.

## 3. Verdict lattice (shared module; per-pair)

- **COMMUTES(pair):** |Δ| within numerical tolerance at all sealed dial values including the
  dial top, *on the pair's own sealed axis*. Dialed pairs only.
- **COMMUTATOR_MEASURED(pair, law):** Δ follows the sealed predicted scaling within k·σ_Δ;
  law banked with sign and coefficient; margin-denominated materiality check clean. Dialed
  pairs only.
- **POINT_CHECK_CLEAN(pair):** for pairs whose substrate admits no dial (P3, zeta leg of
  P1). **Admissibility per A2: for stochastic point-checks (P3), mean Δ over u-draws
  consistent with zero at k·SEM (the fp tolerance does not apply — §0); for deterministic
  point-checks (zeta), |Δ| within the sealed sensitivity envelope.** Materiality check
  clean; for P3, the A3 sign check on retained counts must also have passed (an opposite
  sign is a plumbing halt, not a clean row). **Admissibility is explicit: this verdict
  claims no order effect detectable at the sealed points and power, and asserts no law and
  no scaling behavior.** It is not a weaker COMMUTES; it is a different, narrower claim, and
  §12 records it as such so no future reader upgrades it by reading.
- **ORDER_RULING_REQUIRED(pair):** Δ consumes material margin for any gate-feeding banked
  statistic, or the measured law disagrees with its sealed derivation, or the retro-audit
  finds both orders in live code. Consequence (the arc's teeth): a canonical order is ruled —
  **by the correctness leg where bias separates the orders (with transfer recorded when the
  ruling crosses from synthetic to fixed substrate); arbitrary-but-consistent where truth is
  absent or biases don't separate, with the basis recorded** — entered in the order
  registry, enforced by assertion at every call site, and any affected banked result re-run
  under the canonical order and three-event labeled.
- **UNDERPOWERED(pair):** σ_Δ too large to resolve the target — **the predicted law at dial
  top (synthetic families), or a zero-consistency test of sealed minimum detectable Δ
  (stochastic point-checks, per A1).** Extension = a seed/draw increase and/or **the pair's
  own named extension increment, declared in its seal** (a ladder has a next rung; a fixed
  bandwidth axis states its own step; a draw ensemble states its next size), dry-run
  verified, fires once. **Only deterministic point-checks (the zeta leg) cannot be
  UNDERPOWERED (A1 scoping)** — they are consistent-or-inconsistent with the fitted law
  where one exists, reported with their envelope.

## 4. Deliverables

1. `holonomy/commutator_lab.py` + per-pair measured JSONs, committed generators throughout.
2. `holonomy/COMMUTATOR_TABLE.md` — per pair: predicted law / measured law / materiality
   verdict / retro-audit order census.
3. **TOOLKIT §12 — Canonical Order Registry:** every ruled order with its measured
   justification and a **ruling-basis field: RULED_CORRECT (bias separated, ruling applied
   where measured), RULED_CORRECT_BY_TRANSFER (bias separated on a synthetic analogue;
   ruling applied to a substrate where truth is unavailable), RULED_CONSISTENT (biases
   indistinguishable or truth absent; order fixed for consistency only)** — a future reader
   must be able to recover which rulings carry evidential weight, which carry transferred
   weight, and which carry only coordination weight. Assertions live at call sites
   (rulings-as-code); §12 also records pairs proven to commute **and pairs cleared only at
   sealed points (POINT_CHECK_CLEAN), distinguished from COMMUTES**, so future refactors
   know which orders are free and which are merely untested off-point. **P3's row carries
   both halves of R1: mechanism named, suppressor named.**
4. `verify_holonomy.py` nonzero-exit checker joining the standing green board; cross-refs
   (bridge follow-up closed with pointer, EPISTEMIC_STATE.md same stroke, memory).

## 5. Tripwires

1. Debugging outside the commutation-null KAG window is prohibited once measurement is
   sealed (D1 precedent, freeze clause verbatim).
2. **Two denominators, never crossed:** law-fitting Δ is reported against σ_Δ —
   paired-difference error over synthetic seeds (or u-draws, per A1), **synthetic families
   and stochastic point-checks respectively**; deterministic fixed-substrate Δ is a
   point-check reported with its sensitivity envelope and is never significance-tested (§0).
   Materiality Δ is reported against the affected result's margin-to-boundary. Reporting
   either against raw σ_S, significance-testing an envelope, applying the fp tolerance to
   P3 (A2), or importing a tolerance from another arc, is a defect.
3. The retro-audit's order census runs against the function→transitions ownership map, not
   raw call-site grep; every row cites file:line, the census's coverage fraction is banked
   alongside it, and the denominator is the committed enumeration (R3).
4. ⟨r̃⟩ control: the control is a **detection** question — halt if the control's |Δ| exceeds
   k·σ_Δ on the synthetic family (margin-denomination does not apply; the control feeds no
   gate and has no boundary). A firing control is an instrument defect masquerading as
   holonomy. **The control is tested family-wise, not per dial point** (§9 Q6) — a per-point
   threshold compounds false-halt probability with ladder length, and a spurious halt burns
   the arc.
5. No pair may be dropped after seeing its Δ; the mandatory set is sealed.
6. **Stochastic transitions run against pre-drawn per-point randomness (§0).** A stochastic
   pair measured without it is void, not merely noisy — its Δ contains RNG-stream drift and
   cannot be separated from order effect after the fact.
7. **P3 never touches survey/ (R2):** frozen files are exercised through their public
   surfaces or through the banked-diff variant; no survey file is modified; `null_half` is
   loaded read-only via the frozen loader as the fixed reference (Q2 ruling below) and
   never enters a manipulated path; the P3 runner asserts it writes nothing under survey/.

## 6. Carried-through protocol

Code freeze + blob-SHA at seal; prediction-first (per-pair continuum derivations sealed;
A3 sign sealed); sealed-contingency dry-runs (each dialed pair's own named extension
increment executed once on synthetic; P3's draw-count increment likewise; the deterministic
zeta leg has none); witness-must-fail, thrice over: (i) each pair's Δ-detection demonstrated
red once via a deliberately order-sensitive synthetic construction; (i′) **P3
specifically gets two red demos with distinct labels (Will's note on R1): the
suppressor-broken demo (expectations frozen at pre-thinning normalization) is labeled
DETECTION-IN-PRINCIPLE — it certifies the Δ machinery but tests a modified estimator — and
an injected order-sensitivity of controlled size (sealed δ on the thinning target) detected
at the UNMODIFIED F path with the A1 σ_Δ is the stronger witness and the one the clean
verdict cites;** (ii) **the correctness leg's bias comparator demonstrated two-sided — it
must rule correctly on a construction where one ordering is known more biased by design,
AND return indistinguishable on a symmetric construction where neither is** (without the
null half, RULED_CONSISTENT is unfalsifiable: a comparator stuck on "separated" would never
be caught) — no real ruling is trusted before both halves pass; verdict lattice as shared
module; committed generators; pilot-informed-seal addendum if pilots shape the seal;
three-event labeling for anything post-hoc.

## 7. Out of scope

New science claims; new substrates; transitions not among the registered set; fixing
non-material inconsistent orders beyond registry entry + assertion (no refactor crusade —
the registry is the fix); any re-derivation of banked statistics except where
ORDER_RULING_REQUIRED forces it; a survey-dialect synthetic analogue (see §7a). **Scope
limit, stated so the table cannot be over-read: this pilot bounds pairwise
order-sensitivity only.** Approximate pairwise commutation does not bound full-sequence
holonomy — mid-stack dial values differ from bare-substrate ones, and non-linear downstream
steps (disattenuation, thresholding) can amplify a pairwise-negligible Δ. Full-sequence
holonomy is a possible future arc, not a corollary of this table.

### 7a. Promotion trigger (sealed conditional, replacing the judgment call)

**If P3 returns ORDER_RULING_REQUIRED, the survey-dialect synthetic analogue is
automatically promoted to next-in-queue** — it is the only route to a RULED_CORRECT for the
ruling P3 would then need; without it that ruling is stuck at RULED_CONSISTENT forever. If
P3 comes back clean or underpowered, the analogue stays parked as a future upgrade. Running
or not running it therefore depends on a sealed trigger, not post-hoc appetite (same shape
as §8).

## 8. Optional pairs (sealed trigger, not headroom judgment)

Run **if and only if** the sealed trigger fires: mandatory pairs P1–P3 complete (all gates
and verdicts filed) with wall-clock under a threshold fixed in the seal — the decision rule
is sealed *before* compute so that running or skipping the optional pairs cannot depend on
what P1–P3 showed. Sealed order:
1. surrogate-generation → unfolding vs unfolding → surrogates (1D). **Surrogate generation
   is stochastic — inherits the §0 pre-drawn-randomness discipline and the A1 draw
   ensemble.**
2. disattenuation → pooling vs pooling → disattenuation (cross-substrate machinery).

## 9. Open questions — resolutions at seal

1. Transition inventory: confirmed against the **ownership map** at current head (the census
   scope amends to whatever the map finds — the list of six in the one-line frame is the
   current-head enumeration, not a bound). → resolved by the census cell, pre-seal.
2. **RESOLVED (ruling recorded):** P3 runs with kag_half as the manipulated object and
   null_half as the read-only fixed reference. The survey seal's own language is
   "8-file subset, disjoint halves (even=KAG, odd=null)" — disjointness by file index, no
   "untouched" clause; null_half is the measurement's expectation source and the D1 KAG
   itself read it as reference, so this replicates the certified configuration. Runner
   asserts: loaded via the frozen loader, read-only, never in a manipulated path
   (tripwire 7). The quarter-split remains the recorded fallback if this ruling is ever
   revisited.
3. Numerical-precision tolerance for exact commutation: **proposal ~1e-12 relative (a few
   thousand ε)** — the bridge precedent (`test_sigma2_equality` at exactly 0.0) covers pure
   reordering of identical arithmetic, but commuting non-identity reweightings reorder
   floating-point operations, so exact zero is not guaranteed. The KAG measures the actual
   fp scatter and the seal records the measured headroom. Scoped per A2: exact-commutation
   regime only.
4. **The single sealed k** used in COMMUTATOR_MEASURED, POINT_CHECK_CLEAN (A2 form), and
   tripwire 4 — one value arc-wide, proposed at seal, not per-site.
5. **The census coverage floor** (§2) — proposed from the committed enumeration's own
   accounting (R3) before the census runs.
6. **Family-wise correction form for tripwire 4** — the control is evaluated at every dial
   point; the specific family-wise rule is stated in the seal, not chosen after seeing the
   control curve.
7. **RESOLVED (R2):** the randoms structures are dicts of parallel numpy arrays — adding a
   per-point u is a parallel array, no schema change; the change is in the function
   *signature*, and it lives in holonomy/ (banked diff + equivalence test), never in
   survey/.
8. **NEW (A2): the P3 draw count n_draws** — sealed before measurement; cost is
   2 × n_draws full F-path runs at two L. Proposed from a pre-seal timing pilot (declared,
   pilot-informed-seal), with the minimum detectable mean Δ at k·SEM stated alongside so
   UNDERPOWERED is decidable.

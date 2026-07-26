# LOOK_REGISTER — ARS Look Arc

Places worth pointing the instrument next. **This is not a findings doc. Nothing cites it as support.**

**Register rules in force** (from the session spec §R): entries do not accumulate, sum, or reinforce;
N entries pointing one way is N entries. POST is permanent and is never edited to PRE. No σ/z/p on
entries from regions where no calibrator bracket exists. Demotion and retirement are results of the same
grade as addition.

---

### R-001 — Phase-2 σ-column decline between blocks is effect-size, not null variance
- **Seen:** t=0 row, block-1 → block-2: z falls 2.0414 → 1.2604. Decomposed: the ζ−control **gap** falls
  0.018634 → 0.008732 (ratio 0.469); the control **sd** falls 0.009128 → 0.006928 (ratio 0.759). In logs,
  Δln z = −0.482 = **−0.758 (effect)** + **+0.276 (variance)**. The variance change is a *headwind*: had the
  gap held, the new sd would have given z = **2.69**, not 1.26. So 100%+ of the σ decline is effect-size.
- **Where:** `phase2_residual_measured.json` row t=0 (γ=2516.571); `phase2_thetacert_freshblock.json`
  `sigma_shape` row t=0 (γ=33923.100). Arithmetic only — no run.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** (a) not that the gap shrank *significantly* — Δgap = 0.009902 against a combined
  sd of 0.011459 is **0.86σ**, i.e. the two blocks' gaps are statistically compatible; (b) not that this
  corroborates P1's crossover — direction agrees, magnitude cannot discriminate; (c) not a second witness:
  block-2's t=0 row is the *same measurement family* as P1's own W=2000 γ=33923 row (P1 dev = +0.008482 vs
  P2 gap = +0.008732 — same zeros, two nulls); (d) **the variance leg is not slot-verified** — block-1 has
  W_int=2000 and block-2 is a 2000-zero block whose interior width is unrecoverable
  (`LOOK_ARC_PROVENANCE.md` #13/#14), so part of the sd ratio may be a window-size artifact, not height.
- **What would make it a lead:** re-running block-2's control at *explicitly* W_int=2000 with the block-1
  construction. If the gap ratio survives at matched W, the height-decline is clean.
- **Cost to check:** one flow-control block (~minutes) *after* the Phase-2 control script is reconstructed.
- **Status:** OPEN

### R-002 — The finite-window ⟨r̃⟩ jitter floor does not scale as W^(−1/2)
- **Seen:** Phase-1 null sd at W = 2000 / 5000 / 10000 = 0.005442 / 0.003800 / 0.003030. Implied
  c = sd·√W = 0.243 / 0.269 / 0.303 — monotonically increasing. Log-log fit: **sd ≈ 0.0868·W^(−0.365)**.
- **Where:** `phase1_zeta_crossover_measured.json` `by_W[*].null_sd`.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** not established as a real anomalous exponent. Each sd is estimated from n_real =
  80/60/40 draws (relative error ~8–11%), so three points with a monotone trend is suggestive, not decided.
  Two mundane explanations are untested: edge effects in the Dumitriu–Edelman central-window extraction
  growing with W, and correlation between r̃ values reducing the effective sample.
- **What would make it a lead:** a dedicated null-only sweep — W ∈ {1000 … 40000}, n_real ≥ 400 each, fit
  the exponent with a confidence interval. This is the **W-sweep** item, correctly re-slotted: it is a
  *null-calibration* measurement, not a ζ measurement.
- **Cost to check:** cheap; pure synthetic, no ζ data. Hours at most.
- **Status:** OPEN — and it already has a consequence: every "×floor" number in Phase 2 is inflated
  (see `LOOK_ARC_PROVENANCE.md` §B/#12).

### R-003 — Phase 2's θ-certification is inert for any long-range statistic
- **Seen:** the θ-cert measured `dr_mean` — a **Δ⟨r̃⟩** — and got 0.000000 at every t. But P1 established
  that r̃ is *invariant* to smooth density, and the θ-truncation is a smooth-density perturbation. So the
  cert could not have fired **by construction**, exactly like P1's original unfold falsifier.
- **Where:** `phase2_thetacert_freshblock.json` `theta_cert[*].dr_mean`.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** not that θ-truncation *is* a problem — only that the existing certificate carries no
  information about it. Σ², Δ₃ and F(α) all consume the smooth density directly and are *not* protected by
  this cert. Phase 3 already relies on the θ-exact unfold (`rvm_N`, leading order + 7/8) with no cert of
  its own.
- **What would make it a lead:** re-run the θ-cert on a statistic that *can* see it (Σ² or F(α)), comparing
  `rvm_N` against `rvm_N + 1/(48πt)`. Prediction is that it stays inert (the correction is ~5×10⁻⁴ levels
  at γ=14), but then it would be **demonstrably** inert rather than structurally inert.
- **Cost to check:** minutes. **Folded into Task B.**
- **Status:** **RETIRED** — done in Task B (`LOOK_ARC_TASKB_FINDINGS.md` §4). Σ² under `rvm_N` vs
  `rvm_N + 1/(48πt)` vs the **exact** Riemann–Siegel θ differs by 0.0899% at every L; ΔVar[S] = 2×10⁻⁸.
  Now **demonstrated** inert on a statistic that can see it, not structurally inert. Retiring an entry is
  a result of the same grade as adding one; this one cost minutes and closes a standing worry about every
  long-range readout on ζ. Honest limit: the perturbation is tiny, so the leg has little power of its own
  — its real content is that for ζ the smooth counting is *exact*, not modelled.

### R-004 — Three-height matched-density ⟨r̃⟩ excess, monotone but heterogeneous
- **Seen:** ζ minus matched-density GUE null: γ=1420.4 → +0.017316 (+2.45σ); γ=33923.1 → +0.008732
  (+1.26σ); γ=1131971.6 → −0.000966 (−0.17σ). Monotone decline, the shape P1's crossover asserts.
- **Where:** `phase1_density_check_measured.json` rows 1 and 2; middle point from
  `phase2_thetacert_freshblock.json` t=0.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** **not a three-point series.** The two outer points are W=2000, n_real=30, unflowed
  matched-density nulls from one script; the middle point is a t=0 row of a *flow* control with B=12 and an
  unverifiable interior width. Different construction, different realization count, possibly different W.
  It is two points plus a differently-built third. No slope is fitted here and none should be.
- **What would make it a lead:** measure the middle height with `phase1_density_check.py` itself — same
  script, same W, same n_real. That converts it into an actual three-point series.
- **Cost to check:** one script invocation with a third `starts` entry. Very cheap. **Not run this session
  — it has no seal.**
- **Status:** OPEN

### R-005 — CP1 parity-count labels are inverted relative to the file's own convention
- **Seen:** `maass_analysis.py:45` fixes sym0 = EVEN and `names={0:"even",1:"odd"}` (line 179) follows it,
  but lines 96–97 compute `even_count = (sym==1).sum()` = 334, `odd_count = (sym==0).sum()` = 266.
- **Where:** `sessionK/maass_analysis.py:96-97` vs `:45`, `:179`.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** **not a result error.** The sectors split on the raw symmetry field, so sector "even"
  correctly carries n=266 and ⟨r̃⟩=0.3992, matching Phase 4's parity=0. Only the completeness-block labels
  are swapped. Nothing downstream consumed them.
- **What would make it a lead:** nothing — it is a fix, not a lead. Listed because it sits inside the file
  CP1 rests on and is the program's dominant error mode.
- **Cost to check:** done.
- **Status:** OPEN (pending a one-line fix; will be RETIRED on fix)

---

## Task B additions

### R-006 — α ≥ 1 shape on the ζ low-γ block
- **Seen:** F(α) through the θ path fluctuates about the GUE limit 1.0 with no visible ramp or plateau —
  mean 1.04, range 0.68–1.63 over α ∈ [1.0, 2.9]. Qualitative description only.
- **Where:** `taskB_falpha_measured.json` → `B4_look_region`; block `zeros6[:2000]`, θ path.
- **Pre-registered or post-hoc:** **PRE** (the seal names α ≥ 1 as the look region)
- **NOT claimed:** no σ, no z, no p — calibrator grade in this region is **zero** and that is the entire
  reason it is interesting. The spread is not distinguished from the estimator's own exponential jitter.
  The single elevated bin near α ≈ 0.95–1.0 is **not** called structure: a crystalline decoy produces a
  Bragg peak at exactly α = 1 (R-007), so an elevated bin there has a known mundane generator.
- **What would make it a lead:** a bracket. Any α ≥ 1 statement needs a reference curve that does not
  exist; the tractable substitute is a *comparative* read — the same F(α ≥ 1) shape on several γ-blocks,
  where a height-trend would be interpretable without an absolute reference.
- **Cost to check:** cheap per block (~1 min).
- **Status:** OPEN

### R-007 — Crystalline decoys are not a valid rigid bracket for a form factor
- **Seen:** the jittered picket fence (super-rigid, η = 0.3) gives K(0.15) = 0.082 (correctly below GUE's
  0.160) but **K(1.0) = 1.77** — *above* Poisson — because it is crystalline and carries Bragg peaks at
  integer α. Its Σ²(32) = 0.34 is meanwhile correctly far below GUE.
- **Where:** `taskB_falpha_measured.json` → `G_estimator_gate.rows.superrigid`.
- **Pre-registered or post-hoc:** **POST** (found while writing the gate; the gate criterion was
  corrected before the run, not after)
- **NOT claimed:** not a defect in the decoy — it is a defect in *reusing* it. The same object is a valid
  "more rigid than GUE" bracket for Σ² and an invalid one for F(α) at integer α.
- **What would make it a lead:** it is already actionable — the calibrator zoo needs a **non-crystalline**
  super-rigid class (e.g. a β→∞ or Coulomb-gas construction) if form-factor readouts are to have a rigid
  bracket. This generalises beyond ζ to every substrate the zoo brackets.
- **Cost to check:** design work, not compute.
- **Status:** OPEN

### R-008 — Statistics with silent unfolding dependence (the spec's seed question, answered)
- **Seen:** on the ζ low-γ block, median relative difference from the θ path over α ∈ [0.2, 2]:
  constant-density **28.9%**, poly-3 **11.6%**, poly-9 **2.1%**. And the fitted-unfold artifact is
  confined to **α < 0.002** (ratio poly3/θ = 20.1 there, ≈1.0 above).
- **Where:** `taskB_falpha_measured.json` → `B0_premise`; `taskB_diagnostics2_measured.json` → `D2p`.
- **Pre-registered or post-hoc:** **PRE** (P-B0-b/c)
- **NOT claimed:** not that F is unfolding-free — it is not; the dependence is real and located. Not that
  every long-range statistic behaves this way: Δ₃ smooths Σ² and should be *more* exposed, not less, but
  that was not measured.
- **What would make it a lead:** run the same α-localisation for Δ₃ and for the pair-correlation
  estimator, to get an artifact-support map across the whole two-point family. Cheap and useful.
- **Cost to check:** hours.
- **Status:** OPEN

### R-009 — Selberg CLT feasibility at accessible heights (window property, NOT a ζ result)
- **Seen:** on `zeros6[:2000]` (γ ≈ 14 → 2515), Var[S] sampled uniformly in t = **0.1539**. The Selberg
  asymptotic (1/2π²)·log log(γ/2π) at γ_mid = 1420.4 gives **0.0856**. Measured/asymptotic = **1.80×**.
  (Sampled at the zeros instead of uniformly, Var[S] = 0.0724 — see R-011.)
- **Where:** `taskB_falpha_measured.json` → `B5`; `taskB_diagnostics_measured.json` → `D1`.
- **Pre-registered or post-hoc:** **PRE** (spec §R seed item)
- **NOT claimed:** this is a fact about **the window**, not about ζ. The asymptotic has not arrived: at
  γ = 14 the smooth term rvm_N(14.13) = 0.449 against a true count of 1, so the bottom of this block is
  nowhere near the asymptotic regime. A factor of 1.8 is the concrete size of "not arrived".
- **What would make it a lead:** nothing — it is a standing feasibility note. Its use is to bound any
  future long-range claim that leans on log log growth at accessible heights.
- **Cost to check:** done; extend to other blocks for ~free.
- **Status:** OPEN

### R-010 — **Top of queue.** The ζ low-γ block is not statistically homogeneous
- **Seen:** ζ (θ path) sits below a curvature-matched GUE band at every L, (ζ−GUE)/sd = −6.68, −7.57,
  −9.12, −15.25, −12.46, −10.52 at L = 1…32. But the block spans γ = 14.13 → 2515.3, mean spacing varying
  **7.4×**, so ζ's own fluctuation statistics vary across it while the bracket imposes *homogeneous* GUE
  fluctuations on that density.
- **Where:** `taskB_diagnostics2_measured.json` → `D5`; block `zeros6[:2000]`.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** **not a finite-height rigidity excess.** "More rigid than homogeneous GUE" is
  degenerate between a real excess and height-mixing. The bracket controls the *density* confound and not
  the *heterogeneity-of-fluctuations* confound; they are different confounds and only one is closed
  ([[null_excludes_only_its_confound]]). Nor is it a new witness: it is the same two-point function
  Phase 3 read, on the same block.
- **What would make it a lead:** the decisive test is cheap and specific — re-run the curvature-matched
  θ-path bracket on a **narrow** block at low γ (small density variation, e.g. 2000 zeros starting near
  γ ≈ 2000 rather than γ ≈ 14). If the rigidity excess survives on a homogeneous block it is real; if it
  collapses, Phase 3's low-γ Σ² reading is height-mixing and must be refiled.
- **Cost to check:** minutes of compute. **Deliberately NOT run this session — it has no seal, and it is
  a ζ reading, not instrument calibration.** It should open the next sealed phase.
- **Status:** OPEN

### R-011 — Var[S] sampled at the zeros is not Var[S]
- **Seen:** Var(rank_j − rvm_N(γ_j)) = **0.0724**; Var[S] sampled uniformly in t = **0.1539**. Ratio 2.1×.
- **Where:** `taskB_diagnostics_measured.json` → `D1`.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** not a subtle effect — S is a jump process and sampling at its jump points takes the
  post-jump branch systematically. This is elementary and was still enough to make a sealed prediction
  fire against its own bracket (`LOOK_ARC_TASKB_FINDINGS.md` §4).
- **What would make it a lead:** it is a call-site lesson, not a lead — any estimator that evaluates a
  counting-function residual **at the points of the process** is reading a biased branch.
  [[knowledge_does_not_propagate]]: this belongs attached to the estimator, not to this phase.
- **Cost to check:** done.
- **Status:** OPEN

---

## Phase 5 additions

### R-012 — Gate arms must be chosen by computed contrast, not by default
- **Seen:** Phase 5's G2 gate was sealed on Σ² at **L=1**, where the designed GUE-vs-super-rigid contrast
  is **0.0007**. At L=8 it is **0.2440** — **364×** larger. The gate returned FAIL on a signal that the
  same measurement localizes at −6.15σ twenty level-units away.
- **Where:** `PHASE5_FINDINGS.md`; `phase5_attribution_measured.json` → `G2`; contrast table measured at
  flat unit density, N=500, 15 realizations.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** not that the method fails — G1 passed and the L=8 localization is clean. Not that the
  seal should be rescored: the post-hoc L=8 reading cannot rescue a failed seal and is not used to.
- **What would make it a lead:** it is already a fix. Before sealing any power gate, tabulate the expected
  contrast for **every** candidate arm (L, α, statistic, sub-population) and gate on the **maximum**, as a
  number produced pre-seal. See [[sealed_conjunction_inert_arm]] — that lesson said "check each arm's
  power" and was insufficient to prevent this repeat, because it says to check without saying against what.
- **Cost to check:** minutes per gate.
- **Status:** OPEN

### R-013 — Mis-firing is a third falsifier category
- **Seen:** this program catalogues falsifiers that **fire** (pooling decoy, Task B's constructed unfold
  artifact) and falsifiers that are **inert** (shared-catalog SOC, the unfold test on an unfold-invariant
  statistic, the flat decoy battery, Task B's B.1 identity test). Phase 5's G2 is neither: it **mis-fired**
  — returned FAIL against a signal that was present and detectable.
- **Where:** `PHASE5_FINDINGS.md` scorecard.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** not that mis-firing is common — this is n=1, plus Task B's `P-B2-power` conjunction as
  a near-relative (nominal FAIL on a decisively answered question). Two instances, one session, same
  author, same root cause; that is a pattern in the *gate-writing*, not an established base rate.
- **What would make it a lead:** a sweep of the catalogued falsifiers in this program asking, for each,
  "was the arm chosen the contrast-maximising one?" Cheap and likely to find more.
- **Cost to check:** a reading pass over the phase docs.
- **Status:** OPEN

### R-010 — status update
- **Still OPEN and still held.** Phase 5 halted at G2 before any ζ reading. The decisive measurement is
  now blocked on a re-seal, not on compute: the instrument is adequate (G1 passed, bracket sd = 0.0113 at
  N=500, 2.84σ per sub-block), the gate was not.

---

## Phase 5b additions

### R-012 — status update: the rule was under-specified and is corrected
- "Gate on the maximum-contrast arm" **certifies an instrument you will not use.** Power must be
  established at the arm where the measurement is made. When contrast there is low, *confound lacks
  leverage* (proceed) and *instrument lacks sensitivity* (halt) look identical on one number; separating
  them is a second computation (`PHASE5B_FINDINGS.md` §3). Also: a decoy's tuning parameter can null the
  contrast independently of the arm — η=0.3 sits on GUE at L=1 by coincidence, while Σ²(1) spans
  0.072–1.024 across the rigidity ladder. **Status: OPEN**, rule superseded in place.

### R-013 — **RETIRED.** Mis-fire is not a third category
- Inert (false pass) and mis-fire (false FAIL) are the same defect — unquantified power — with opposite
  signs. The tell is that one rule fixes both. Three categories implies three lessons; there is one lesson
  with two consequences, and collapsing them keeps the antibody from fragmenting. Retiring an entry is a
  result of the same grade as adding one. **Status: RETIRED**, folded into R-012.

### R-014 — ζ's per-sub-block Σ²(1) is FLAT, unbracketed, and points away from the sealed prediction
- **Seen:** ζ sub-block Σ²(1) at γ_mid ≈ 400 / 1120 / 1700 / 2250 = **0.3138, 0.3138, 0.3131, 0.3081**.
  Flat; if anything the *highest* sub-block is lowest.
- **Where:** `phase5b_leverage_measured.json` → `C4`. Computed as a by-product of the boundary-effect
  check, which required them.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** **unbracketed — no σ is quoted.** Each sub-block needs a curvature-matched band built
  on *its own* backbone; the band available here was built at the first sub-block's backbone only. And
  this **does not score Phase 5's seal**: that phase halted at G2, `H_bottom`/`H_flat`/`H_null`/`H_split`
  remain unscored, and a post-hoc unbracketed reading cannot retire a sealed prediction in either
  direction — including one of mine that it appears to contradict (I sealed `H_bottom`; this reads flat).
- **What would make it a lead:** the Phase 5 re-seal, with per-sub-block brackets. **It must carry a
  `DISCLOSED_PRIOR_KNOWLEDGE` block listing these four numbers** — cold entry on the attribution question
  is spent, exactly as it was for Task B. Still worth running; brackets are what would make it a result.
- **Cost to check:** minutes.
- **Status:** OPEN

### R-015 — Substrate triage from the L_max wall
- **Seen:** `L_max ≈ N/(2(p+1))` with p = number of *fitted* density parameters. ζ: θ is an identity, p=0,
  **no cap**. Maass level-1: Weyl R² and R·lnR theory-fixed, only affine {R,1} fitted, p=2 →
  **L_max ≈ 66 (N=266) / 84 (N=334)**; Session K read Σ² to L=15, **within cap by ~4×**. Empirical-density
  substrates on `unfold_emp(order)`: p = order+1 → L_max = 250 (order 3, N=2000), 100 (order 9).
- **Where:** `PHASE5B_FINDINGS.md` §7; `taskB_kernel_check_measured.json` → `K1`;
  `sessionK/maass_analysis.py:44-58`.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** the cap is a *contamination* bound, not a noise bound — being under it does not make a
  reading good, only un-artifacted by this mechanism. Maass's clearance is retrospective and was not
  computed at the time.
- **What would make it a lead:** apply the triage to every long-range readout in the program and flag any
  that sits above its cap. Cheap, mechanical, and likely to find at least one.
- **Cost to check:** a reading pass plus one arithmetic line per substrate.
- **Status:** OPEN

### R-010 — status update: EXISTENCE closed, ATTRIBUTION open
- The heterogeneity confound has **zero leverage on existence**: Σ² of a heterogeneous block is the
  *average* of its parts (verified — designed mixture, |whole − mean(parts)| = 0.0117 at L=1, whole inside
  the part range), so a block below a GUE bracket **entails** at least one sub-block below it. θ removes
  density to 0.075% across quarters; boundary effects at L=1 are 0.09 sd. The three-way decision at the
  measurement arm reads effect 6.69 sd, leverage 0.00 sd → **PROCEED**. R-010's original "degenerate
  between a real excess and height-mixing" was **too strong and is withdrawn**. What survives is the
  attribution question. **Status: OPEN (attribution only).**

---

## Phase 5c additions

### R-016 — Maass fixed-theory Weyl law leaves 58–71% of S(R) as smooth trend
- **Seen:** residual S(R) after `maass_analysis.py`'s theory-fixed fit (R², R·lnR fixed; affine {R,1}
  fitted): parity 0 sd = 0.8136 levels, of which a deg-2 fit captures **0.6174 levels = 57.6%** of Var[S];
  parity 1 sd = 0.8781, deg-2 captures **0.7296 = 69.0%**. Saturates by deg-3 (58.9% / 70.9%) → genuinely
  low-frequency, not a probe artifact.
- **Where:** `phase5c_followups_measured.json` → `F3`; `sessionK/maass_analysis.py:44-58`.
- **Pre-registered or post-hoc:** **POST** (the check was proposed pre-run by the reviewer as the
  companion to R-015's cap-clear, then computed)
- **NOT claimed:** **does not touch CP1 / Phase 4's endpoint verdict** — that rests on ⟨r̃⟩, which is
  unfold-invariant, so this systematic cannot reach it; 7.3σ / 6.4σ stand. Not claimed that the Weyl
  constants are wrong — an asymptotic law with a remainder leaving a low-order residual at finite R is
  expected; what is claimed is that the residual is **unabsorbed**, so it rides in the statistic.
- **What would make it a lead:** it already is one. Re-read any Σ²/long-range Maass quantity with the
  trend removed, and compare. Being under the L_max cap does not help — the cap bounds contamination
  **reach in L**, this is an **amplitude** problem inside it.
- **Cost to check:** minutes.
- **Status:** OPEN

### R-017 — The low-γ region is permanently data-limited
- **Seen:** below γ = 2515.3 there are **1999 zeros in the entire catalogue** (R-vM smooth: 1999.4), so
  `zeros6[:2000]` is the whole population below its own top, not a window choice. Best-ever ⟨r̃⟩ floor
  there is 0.00542–0.00544, so P1's 0.01732 excess has a **permanent ceiling of 3.18–3.20σ** and its
  measured **2.45σ is 77% of everything that can ever exist at that height.**
- **Where:** `phase5c_followups_measured.json` → `F4`.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** not that P1 is maxed out in general — going higher in γ buys resolution (4520 zeros
  below γ=5000, 10142 below γ=10⁴) but the effect decays with height, which is P1's own finding. The
  ceiling is specific to the height where the effect is largest.
- **What would make it a lead:** nothing — it is a boundary, not a lead. It **retires** the earlier
  status lines "expensive" and "available but self-defeating", both of which implied a tradeoff to
  navigate. There is no tradeoff.
- **Cost to check:** done.
- **Status:** OPEN (standing constraint)

### R-018 — The low-γ internal-slope test is permanently underpowered
- **Seen:** P1's local slope extrapolated below its mapped range predicts a ⟨r̃⟩ span of **+0.00548**
  across the four sub-blocks; observed span **0.00123**, fitted slope −0.0114 vs predicted +0.0892;
  per-sub-block jitter **0.0090–0.0109**. Predicted span = **0.50–0.61 sd**.
- **Where:** `phase5c_followups_measured.json` → `F2`.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** **no tension established between the flat profile and P1's mechanism, and none
  excluded.** The opposite-sign fitted slope is not evidence at this N. This is a null **with stated
  power**, not a null.
- **What would make it a lead:** nothing at low γ — this is R-017 appearing in a second place. The
  predicted internal variation (~0.005) sits at the noise floor of every zero that exists below γ=2515
  (~0.0054), so no re-cut of the block helps. The test is only available at heights where the effect has
  already decayed.
- **Cost to check:** done.
- **Status:** OPEN (standing constraint)

### R-010 — status update: the averaging argument is a theorem
- Upgraded from demonstrated to **proved**: law of total variance, Var(N) = E_g[Var(N|g)] + Var_g(E[N|g]);
  θ equalizes density ⇒ second term vanishes ⇒ whole = window-count-weighted mean of parts, and any
  residual density mismatch makes that term **positive, never negative**. So whole ≥ weighted mean ≥ min
  part, and the entailment holds **a priori and in the conservative direction**. The Phase 5b +0.0117
  "excess" is retired: it was an **unweighted** mean compared against a quantity requiring window-count
  weighting (`PHASE5C_FINDINGS.md` §2); the exact decomposition closes to 0.14%.

---

## Phase 5d additions

### R-016 — **RETIRED as repairable; the Luo–Sarnak bracket is UNREACHABLE**
- Detrending moves Maass Σ² **away** from Poisson, not toward it: Var[S] 0.6620→0.2808 (parity 0),
  0.7711→0.2388 (parity 1), and Σ²(15) falls 0.888→0.735 / 0.750→0.669. The removed trend was
  contributing long-range variance — which is what a long-range statistic is for.
  **Unabsorbed Weyl-remainder systematic and genuine long-range fluctuation occupy the same low-α band
  and are not separable at N = 266/334.** After detrending Σ² saturates at 2·Var[S] = 0.562 / 0.478,
  *below one mean spacing*; no L in {1,2,4,8,15} is within 20% of Poisson's L; the banked leg is 17–20×
  short of its own reference. Also excluded: the final `sp/sp.mean()` rescale (reproduces to 2%).
  **Not repairable by detrending — the repair and the signal are the same object.** More eigenvalues at
  the same heights extend L but do not separate them. **Status: RETIRED.**

### R-019 — CP1's unfold-invariance is now measured, not transferred
- **Seen:** ⟨r̃⟩ across raw R / pipeline unfold / theory-affine / detrended: max spread **0.00063**
  (parity 0) and **0.00114** (parity 1) — **0.03σ / 0.06σ** of the Phase-4 bracket sd, against a 7.3σ /
  6.4σ verdict. Non-trivial: the Maass density varies ~10× across the sector.
- **Where:** `phase5d_maass_gate_measured.json` → `sectors.*.rtilde`.
- **Pre-registered or post-hoc:** **PRE** (proposed as a companion one-liner before the run)
- **NOT claimed:** does not revalidate CP1's *data* — extraction, list provenance and completeness are
  untouched. It closes exactly one assumption: that ζ-measured r̃ invariance transfers to Maass.
- **What would make it a lead:** nothing — it is closed. **Status: RETIRED.**

### R-021 — Session-local document cited as banked record
- **Seen:** the Luo–Sarnak reference originated in a web search during this session, entered the
  long-range methods brief (**presented, never committed**), and was then cited as "the long-range brief
  flagged" — which reads as repo provenance. `grep -rni "luo"` over the repo returns nothing.
- **Where:** `PHASE5D_FINDINGS.md` §0. Reviewer-reported, not caught by CC.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** not that the reference is fabricated — the paper is real (CMP 161 (1994) 419–432) and
  its substance was tested on merits and found unreachable (R-016). The defect is the **slot**, not the
  value. Also not a variant of the catalogued modes: it is neither unquantified power nor a
  wrong-slot *value* — it is a wrong-slot *source*, and it is invisible to §0b until the grep runs.
- **What would make it a lead:** a provenance header on every brief marking each pointer **in-repo** vs
  **in-session**, so the distinction survives the gap between writing and citing. Cheap, and it is the
  structural fix rather than a per-instance patch. The deeper fix is to **commit** briefs that acquire
  load-bearing pointers, so "session artifact" stops being a category that can be cited from.
- **Cost to check:** a header per brief.
- **Status:** OPEN

### R-020 — Reach / amplitude / separability: three gates, not one
- **Seen:** **Reach** = L_max ≈ N/(2(p+1)); **Amplitude** = fraction of Var[S] that is smooth low-order
  trend; **Separability** = is the smooth counting known exactly or only asymptotically. ζ passes all
  three; **Maass passes reach (cap 66–84, read to L=15) and fails amplitude (58–71%) and separability
  (Weyl is asymptotic)**; `unfold_emp` substrates fail the last two by construction.
- **Where:** `PHASE5D_FINDINGS.md` §3.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** separability is a property of the *substrate's* density model, not of the statistic —
  no choice of long-range statistic repairs it, which is the corrected form of the earlier "cleverer
  readout" refutation.
- **What would make it a lead:** apply all three to every long-range readout in the program. Closes the
  long-range brief's "log the L-to-window ratio" slot. **Status: OPEN**

### R-017 — status correction: the ceiling figure was withdrawn
- **3.18–3.20σ is withdrawn — wrong slot.** It divided the matched-density-null effect (0.017316) by the
  **uniform** GUE null sd (0.005442) — a different null, and the one P1's reviewer showed to be
  powerless. The correct floor is the matched-density null sd **0.007063**, giving **2.452σ**, which is
  P1's banked figure. **P1's low-γ leg is at 100% of available data and 2.452σ is terminal — not 77% of
  a ceiling.** Estimator of record: ⟨r̃⟩ = mean min/max of consecutive spacings on raw γ, block
  `zeros6[:2000]`, vs `phase1_density_check.py::matched_density_null` (DE β=2 tridiagonal central window
  on the R–vM backbone, W=2000, n_real=30, sd 0.007063).
- **Second correction — the boundary is on the STATISTIC, not the block.** "The low-γ end of P1 is
  exhausted; further movement must come from high γ" merged statistic with data and is withdrawn.
  Σ²(L=1) reads **−6.69σ on the identical 1999 zeros** (different null, different correlation family — no
  ratio claimed, and none needed). **Corrected: P1-as-⟨r̃⟩ is data-exhausted at low γ; the low-γ block is
  not**, and the corroboration leg does not inherit the primary leg's boundary. Σ²'s low-γ headroom is a
  separate open question under its own three gates (R-020).

### R-012 — status update: the rule must fire at RECOMMENDATION time
- Both parties produced an uncomputed-power failure *after* naming the defect: a gate sealed at 0.3%
  contrast, and a test recommended as "the sharpest unrun thing on the board" without its power
  computed. **Establishing power is a precondition for proposing a test, not only for sealing one.**
  **Status: OPEN.**

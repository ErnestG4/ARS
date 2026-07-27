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
- **Seen:** `L_max ≈ N/(2·p_fit)` with p_fit = number of *fitted* density parameters (α_c ≈ p_fit/N; for a polynomial of order k, p_fit = k+1). ζ: θ is an identity, p_fit=0,
  **no cap**. Maass level-1: Weyl R² and R·lnR theory-fixed, only affine {R,1} fitted, p=2 →
  **L_max ≈ 66 (N=266) / 84 (N=334)**; Session K read Σ² to L=15, **within cap by ~4×**. Empirical-density
  substrates on `unfold_emp(order)`: p_fit = order+1 → L_max = 250 (order 3, N=2000), 100 (order 9).
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
- **Seen:** **Reach** = L_max ≈ N/(2·p_fit), p_fit = fitted density params; **Amplitude** = fraction of Var[S] that is smooth low-order
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

---

## Phase 5e additions

### R-022 — The L-function triage row is MEASURED, not an expectation
- **Seen:** 630 primitive Dirichlet characters (n≥100, conductors 3–149), exact smooth counting
  θ_χ(t) = Im log Γ((a+½+it)/2) + (t/2)log(q/π), only a constant fitted (p_fit = 1).
  **Amplitude: 626/630 at median 0.015%** (max 0.12%) of Var[S] captured by a deg-2 fit, against
  **Maass's 57.6%/69.0%** and a **positive control at 83.8%** (a 0.62-level trend — the Maass parity-0
  amplitude — injected into the real data). Gate resolves trends to **0.157 levels**; the Dirichlet trend
  is **≤ 0.0033 levels, 47× below** what the gate can see. **Separability: PASS** — the counting function
  is exact (gamma factor of a known functional equation), so p_fit = 1, α_c = 1/n, L_max = n/2 ≈ 111.
  §4 one-liner: poly3 misfits the exact counting by **0.246 levels** median (ζ's was 2.764).
- **Where:** `phase5e_lfunction_row.py`, `phase5e_lfunction_row_measured.json`.
- **Pre-registered or post-hoc:** **POST** — run in response to the reviewer's question of whether the
  row should stay as a flagged expectation or come out until measured. It did neither.
- **NOT claimed:** **Dirichlet only.** EC L-functions are the same test one gamma factor away and are
  **not** claimed — the triage row must say *Dirichlet*, not *L-functions*. Not a claim about zero
  statistics: this measures the density model, not rigidity. Parity was verified absorbed (Var[S] for
  a=0 and a=1 agree to 4 s.f.), so a=0 throughout — that is verified, not assumed.
- **Two defects caught in my own gate en route, both filed:** (i) a "3/n chance level" reference, invalid
  here because it assumes white residuals while S(t) is oscillatory — the measured 0.015% is *below* the
  nominal 1.4%, which is expected, not anomalous; (ii) a Poisson-on-backbone null, which is a rigidity
  contrast, not a trend contrast — the wrong null for an amplitude gate. Both replaced by the injected-
  trend positive control, which is the only reference that establishes power here.
- **Status:** OPEN (Dirichlet measured; EC unmeasured)

### R-023 — **DIAGNOSED and RETIRED.** Four Dirichlet characters are missing zeros
- **Seen:** cleanly bimodal — 626 characters below 0.12%, and exactly **4 above 50%**: conductors 91
  (73.8%), 103 (72.1%), 121 (69.9%), 56 (53.8%). Those four carry sd[S] ≈ 0.67–1.04 against a main-
  population median of **0.272**, and a smooth-trend end-to-end drift of **−1.07 to −2.96 levels**
  against a main-population **0.008**.
- **Where:** `phase5e_lfunction_row_measured.json` → `outliers`.
- **Pre-registered or post-hoc:** **POST**
- **DIAGNOSED (no re-fetch needed).** The exact counting function predicts how many zeros lie in
  [γ_min, γ_max]; a catalogue missing k zeros shows a deficit ≈ k. Main population (626): median
  **−0.151**, sd **0.337**. **Exactly 4 of 630 characters have a deficit > 0.9** — conductors 56
  (**+1.88**), 103 (**+1.86**), 121 (**+1.79**), 91 (**+1.32**) — and they are **the same four objects**
  as the amplitude outliers (verified by (conductor, n) identity, not by conductor alone). ~1–2 missing
  zeros each. My earlier "not a single missing zero, so not diagnosed" reasoning was measuring the wrong
  thing: the deg-2 **drift** is a *smoothed* proxy and reads non-integer by construction; the **count
  deficit** is the clean form and it resolves cleanly.
- **NOT claimed:** not an amplitude failure and not a density-model failure — the family passes 626/630
  with a powered gate, and these four fail for want of data, not for want of a model.
- **Consequence — the §6 byproduct is now SHOWN, not asserted:** the amplitude gate doubles as a
  **per-object catalogue-completeness check**, free on every object it already processes, detecting a
  data defect the statistics themselves would silently absorb. The correct diagnostic to bank is the
  **count deficit against the exact counting function**, not "integer-valued drift in S".
- **Status:** **RETIRED** — diagnosed. (The four objects remain worth re-fetching as a data-hygiene
  chore, but nothing methodological is open.)

---

## Scout-series additions (unsealed; no significance values quoted)

### R-024 — Berry's 8% must be RE-GRADED DOWN: consistent, non-discriminating
- **Seen:** Σ²(L)/2·Var[S] oscillates — measured 0.70, 0.83, 0.97, 1.08, 1.10, 0.95, 0.86, 1.13 at
  L = 0.5…64 on the top block. An envelope of roughly ±20–30% about 1.
- **Consequence:** §10's "bracketed, not attributed — 2·Var[S] = 0.3077 vs plateau 0.2829, 8%" was a
  **single point inside an oscillating envelope**. Any theory with the right mean lands within 8% at a
  randomly chosen L, so the agreement **does not discriminate**. **Re-grade: CONSISTENT,
  NON-DISCRIMINATING** — until the curve is matched *as a curve*, not at a point.
- **Where:** `scout2_cap_and_power.py` [A]; supersedes the grade in `LOOK_ARC_TASKB_FINDINGS.md` §4.
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** the 8% number is not wrong and the saturation identity is not in doubt — it was
  verified to 5 decimals. What is withdrawn is its **discriminating power**, which is the property the
  "excluded-because-known" grade rests on. This is the honest cost of the oscillation discovery and it
  propagates to the brief, not just to a scout header.
- **What would make it a lead:** match Σ²(L) as a curve against Berry's oscillatory formula over a
  densely sampled L, not at a plateau point.
- **Status:** OPEN

### R-025 — L_sat = 1.62 is the FIRST crossing, not "the" saturation scale
- **Seen:** with an oscillating target, GUE's log-growing Σ² can cross ζ's curve more than once.
  L_sat solves gue(L) = 2·Var[S], which locates the **first** crossing of the asymptotic *limit*.
- **NOT claimed:** the parting-of-ways conclusion survives untouched — GUE grows without bound, ζ
  oscillates about a finite limit, so they diverge. Only the uniqueness of the number is withdrawn.
  Cite it as "first crossing", never as "the saturation scale", or it will be read as a wall.
- **Status:** OPEN (qualifier required at every citation)

### R-026 — Prime-power peaks: attribution EARNED
- **Seen:** frequency rescaled by L̄ = ln(γ/2π) puts the explicit formula's terms at log p^k for every
  block. 20 blocks averaged, peak-**found** (not sampled at predicted spots): **8/8 maxima land on log
  of a prime power**, |Δ| ≤ 0.0002 — log 2, 3, 4, 5, 7, 9, 11, 13. Composite non-prime-power integers
  are silent (log 6 → 1.4× median, log 10 → 2.5×, log 12 → 2.8×) against log 2 at 14,440×.
- **Where:** `scout3_primes_and_systematics.py` [3].
- **Pre-registered or post-hoc:** **POST**, but the location prediction was fixed before the peak-find.
- **UPGRADED by Scout 4 — the estimator was the defect.** v3 used a point sample of the interpolated
  peak; a point sample of a sharp peak is attenuated by random sub-bin phase. With **integrated** peak
  power on each block's **native** grid: locations by parabolic sub-bin interpolation give
  **|Δ| = 1–6 ×10⁻⁵ at sem 3×10⁻⁵** (0.38–2.19 sem; two of nine near 2.2 sem, the expected tail for
  nine points). **The amplitude law is now BRACKETED**: ratios collapse to **127.4–132.8**, spread
  **1.04** (was 1.56), fit exponent n^(−0.014) ⇒ weight **Λ(n)²/n¹ confirmed to 4%** across nine prime
  powers spanning ×6.5 in n and ×9 in weight. **Spearman ρ = 1.000** on n=9 — measured order is exactly
  the Λ(n)²/n order — so v3's ρ=0.881 disagreements were estimator artifacts, not scatter.
- **NOT claimed:** this is a *rediscovery* of the explicit formula's structure — known physics, not a
  new finding. Its value is that our own attribution is bracketed on **both** location and magnitude,
  and that it end-to-end validates the instrument at high γ.
- **Why the control class matters:** composites are a **built-in** control class rather than a
  hand-picked one — the explicit formula sums over prime *powers*, so 6/10/12 *must* be absent. A
  control class the theory itself specifies is stronger than one chosen by the analyst.
- **Status:** **RETIRED — earned on both axes.** Locations and amplitudes bracketed; see R-028/R-029.

### R-027 — Systematics budget for the Selberg-coefficient program
- **completeness:** on ζ, per-block count deficit mean +0.005, sd 0.503, corr with ln γ = **−0.138** —
  no height drift. sd consistent with endpoint S-fluctuation (√2·sd[S] = 0.63), not missing zeros.
  Also calibrates the detector on a known-complete catalogue: **0 ± 0.5**, against which Dirichlet's
  four outliers at +1.3…+1.9 sit 2.6–3.8σ out.
- **curvature:** the bias is `C·(mean_over_block[lnln] − lnln(γ_mid))`, second-order, **not** the
  within-block range I first reported. Measured at both ends: **0.10× σ_V** at the low end (curv
  1.0419), ~0 at the top. **Controlled by construction** if the abscissa is mean-over-block lnln.
- **demean bias:** constant at fixed W ⇒ hits the intercept, not the slope. This is why the seal
  belongs on the **coefficient**.
- **NOT claimed:** these are the systematics we thought to look for. σ_V is sampling scatter and cannot
  see a systematic that varies with height; three are now checked, others are untested.
- **Status:** OPEN

### R-028 — The log-8 falsifier, spent and passed
- **Seen:** nine prime powers sit in the band; Scout 3 reported eight. The missing one, **8 = 2³** at
  log 8 = 2.07944, is predicted **present and weakest** (Λ(8)²/8 = 0.0601, exactly half of Λ(4)²/4).
  Measured: present at 2.07945 (0.38 sem), **smallest of the nine**, and amplitude relative to log 4
  = **0.500 against a predicted 0.500**.
- **Where:** `scout4_peak_estimator.py` [F].
- **Pre-registered or post-hoc:** **PRE** — location and relative magnitude were both specified before
  the measurement, by a reviewer, from the theory, on data already in hand.
- **NOT claimed:** one prediction, not a program. And it consumed nothing the location test used, which
  is what made it free — but "free" is why it was nearly left unspent.
- **Status:** RETIRED (passed)

### R-029 — A point-sampled peak is not an amplitude
- **Seen:** taking the *value* of an interpolated peak instead of the *integrated power* produced a
  spurious monotone drift (ratios 49–77, spread 1.56) and corrupted the rank order (ρ = 0.881 with
  three "disagreements"). Integrating over the peak on the native grid: spread **1.04**, ρ = **1.000**.
  Cause: a sharp peak sampled at random sub-bin phase is attenuated, and the attenuation correlates
  with frequency through the interpolation grid.
- **Where:** `scout4_peak_estimator.py` [A]/[R] vs `scout3_primes_and_systematics.py` [3].
- **Pre-registered or post-hoc:** **POST**
- **NOT claimed:** not that point sampling is always wrong — for *locations* it was fine, and the
  location result survived unchanged. The defect is specific to amplitude.
- **Generalises:** this is [[sealed_conjunction_inert_arm]]'s sibling for estimators rather than gates.
  A structured residual is diagnostic — but what it diagnoses may be the instrument, and the instrument
  is the cheaper hypothesis to test first. Both times this arc that a monotone trend appeared
  (sd(W)'s exponent, this drift), the instrument was the live suspect.
- **Status:** OPEN — the same audit is owed anywhere an amplitude was read off a peak value.

### R-030 — Completeness detector: sensitivity spec
- **Seen:** on ζ (known-complete), per-block count deficit has **sd 0.503**. One missing zero shifts the
  deficit by exactly 1, so it reads at **1/0.503 ≈ 2.0σ**.
- **NOT claimed:** the detector is a **k ≥ 1 instrument, not a fractional one.** It resolves whole
  missing zeros at ~2σ each and cannot see partial or subtler catalogue defects. File this before it is
  used anywhere that assumes finer resolution. Dirichlet's four outliers at +1.3…+1.9 sit 2.6–3.8σ out,
  i.e. 1–2 missing zeros each, which is exactly at the instrument's floor and should not be read as a
  precise count.
- **Status:** OPEN (standing spec)

### R-031 — A systematic budgeted for ONE observable does not transfer to another
- **Seen:** R-027 budgeted the within-block curvature systematic and found it **second order** for
  Var[S] (0.10× σ_V), concluding "controlled by construction." That was correct — **for Var[S].** For
  the spectral readout it is **first order in log n**: the term for n sits at α = log n / L̄(t), and L̄
  drifts within a block, smearing the peak by `d_α ≈ log n · ΔL̄/L̄²` — up to **234 native bins at
  n=13** in the low-γ set against **under one bin** at high γ. A fixed integration window then loses
  power in proportion to log n, manufacturing a monotone falloff.
- **What it manufactured:** Scout 5's height test read HIGH n^(−0.014) vs **LOW n^(−0.632)**, i.e. "the
  Λ(n)²/n law is not stable across height." That conclusion was **entirely instrumental.**
- **The fix was a coordinate, not a correction.** In **raw t** the explicit formula's terms sit at fixed
  frequency log n — no L̄ anywhere, nothing to drift. Redone there: **HIGH n^(−0.0134), LOW n^(−0.0141)**,
  spreads 3.85% / 3.63%, and the rank order is identical at both heights and matches prediction.
- **Where:** `scout6_raw_frequency.py` vs `scout5_precision_and_height.py` [H].
- **Pre-registered or post-hoc:** **POST**
- **Generalises:** this is [[knowledge_does_not_propagate]] sharpened. The budget was not missing and was
  not wrong — it was *run on the wrong observable and then treated as a property of the data*. **A
  systematic's order is a property of the (systematic, observable) PAIR.** Re-derive it for every
  observable that consumes the same data; do not inherit the verdict.
- **Status:** OPEN — audit owed for every other systematic declared controlled on one observable.

### R-032 — "Confirmed to 4%" was a RANGE reported as a precision
- **Seen:** per-block scatter gives sem **0.64–1.14%** (typical **0.82%**) on each of the nine ratio
  means. The 4.07% figure is the **max−min range of nine means**, not a per-point precision.
- **Consequence for the too-good question:** with 0.82% per point, the three adjacent orderings the
  reviewer flagged (11-vs-5 at 1.0%, 13-vs-5 at 2.3%, 7-vs-11 at 3.4%) sit at **0.9σ, 1.5σ, 2.7σ** —
  all three correct has probability ≈ **0.76**, not 1-in-8. **ρ = 1.000 is not too good.** The first
  horn of the dilemma was the right one: precision is much better than 4%.
- **But there is mild excess scatter:** χ² = **16.9 on 8 dof** (p ≈ 0.03) about a constant, implying
  ~0.9% unexplained systematic on top of the 0.82% statistical. **So: the weight law holds at the ~1%
  level, with a ~2σ hint of residual structure** — not "to 4%", which understated the precision and
  overstated the agreement at the same time.
- **Also corrected:** the log-8 ratio is **0.501 ± 0.006**, not "0.500". The prediction is exact by
  construction; the measurement carries the ratio's scatter and must not borrow the prediction's digits.
- **Re-slotted:** the weight law is a **theorem**, so a p≈0.03 residual is **not tension with the law** —
  it is a **measured noise floor for the readout**. That is the useful reading and it is what the number
  should be filed as. And by **R-031's own rule**, this 0.9% is a spec for the **periodogram-amplitude**
  observable and does **not** become a budget entry for the Var[S] slope — a systematic's order is a
  property of the (systematic, observable) pair, including this one. R-031 applied to R-031's output.
- **Status:** OPEN (noise floor for the periodogram readout: ~0.8% statistical, ~0.9% systematic)

### R-033 — Rank and ratio are ONE witness
- If the ratios are constant, the rank order follows automatically. Spearman ρ is a **coarsening** of
  the ratio statistic, not an independent check of it. R-026 filed them as two brackets; they are two
  headings on one measurement. §2's family collapse, one substrate over.
- **Status:** RETIRED (filing corrected)

### R-034 — **RETRACTION.** The certification gate does not discharge the lnln prerequisite
- **What was claimed:** that Scouts 3–6 certified ARS's long-range readout at high γ and therefore
  discharged the lnln program's calibrator prerequisite. **That is wrong**, and it is the
  capability-claim-from-correct-mechanism failure again.
- **Measured (`scout7_band_decomposition.py`):** Var[S] = (1/2π²)·Σ_p Σ_k 1/(k²p^k), whose leading part
  is Σ_{p≤X} 1/p = lnln X + M. The certified peaks are n ≤ 16, i.e. **primes ≤ 13**, whose 1/p mass is
  **1.3440 — a constant.**
  - their contribution to Var[S] = **0.07494** against a measured intercept of **0.0738** → the
    certified band accounts for **101.5% of the intercept**;
  - across the lever arm the Mertens cutoff X = t/2π runs 5,259 → 179,411, so **15,587 primes enter**,
    carrying 1/p mass 0.3440 → ×C = **0.01743** against a predicted rise of **0.01748**;
  - **fraction of that carried by primes ≤ 13: 0.0%.**
- **So: the certification measured the INTERCEPT and the program measures the SLOPE. Disjoint bands of
  the same spectrum**, confirmed to ~1.5%.
- **Second, independent reason it does not transfer:** Var[S] weights the prime sum by Λ(n)²/(n log²n);
  the periodogram I certified weights it by Λ(n)²/n, because S is the *integral* of the density
  fluctuation and the two spectra differ by ω² = log²n. Both weights are correct for their own
  observable — and **the density weight suppresses exactly the tail that carries the growth**
  (weight-sum over p ≤ 13: density 3.4858 vs Var[S] 1.4793, the Mertens object).
- **What the certification IS worth:** the readout reproduces theorem-grade structure — nine locations,
  correct rank, correct weight exponent, theory-specified controls, a passed pre-registered falsifier —
  at **both** ends of the height range. That is a Phase-0-grade calibrator result and stronger than
  Farey/Hall (one distribution matched vs a nine-point structured prediction). It is **not** a
  prerequisite for the slope.
- **THE GATE THAT IS ACTUALLY NEEDED — still open:** *tail fidelity and cutoff drift.* The lnln growth
  **is** the moving cutoff (Mertens with X = t/2π), so the question is not whether the physical cutoff
  drifts — it must — but whether the **estimator's** effective cutoff tracks it faithfully at every
  height. An estimator cutoff drifting differently manufactures or destroys lnln growth directly.
  Test: vary S-sampling resolution and block length; the **slope** must be stable while the intercept
  moves. Argued but **not measured**, and nothing in Scouts 3–7 touches it.
- **Status:** OPEN — this is the real prerequisite.

### R-035 — The 1.44 is explained, and the certification is stronger for it
- **Seen:** predicted periodogram amplitude for a resonant mode scales as **W/L̄²** (span = W·2π/L̄), so
  the LOW/HIGH ratio should be **(L̄_HI/L̄_LO)²** with block means: **1.431 predicted vs 1.441–1.464
  measured.** Absolutes: HIGH 138.8 predicted vs 133.5 measured; LOW 198.6 vs 194.2 — both inside the
  ~4% spread.
- **NOT claimed:** the reviewer's candidate (mean-spacing) was right; the exponent is **2, not 1** —
  their 1.41 used the L̄ ratio and endpoints where the correct form is the square with block means.
- **Consequence:** height-invariance holds **including the overall scale**, not only the n-dependence.
  An unexplained 1.44 sitting inside a certification is exactly where such a thing quietly parks; it is
  now explained.
- **Status:** RETIRED

### R-036 — The intercept collision: BOTH attributions were mine and BOTH are wrong
- **The collision:** 0.0738 was filed as the finite-block **demean bias** (justifying the coefficient
  seal), then as the **n ≤ 16 prime contribution** at "101.5%". They sum to ~0.15 against a measured
  0.0738, so at most one could hold.
- **Discriminator run** (`scout8_intercept_collision.py`): demean bias scales with block length W;
  a sawtooth term scales with sampling resolution; a prime constant scales with neither.

| W | 2500 | 5000 | 10000 | 20000 | 40000 |
|---|---|---|---|---|---|
| intercept | 0.07663 | 0.07505 | 0.07294 | 0.07253 | 0.07338 |
| slope | 0.04855 | 0.04918 | 0.05007 | 0.05026 | 0.04988 |

| pts/spacing | 1 | 2 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| intercept | 0.10824 | 0.07283 | 0.07327 | 0.07253 | 0.07383 | 0.07375 |
| slope | 0.03566 | 0.05011 | 0.04988 | 0.05026 | 0.04970 | 0.04973 |

- **(a) DEMEAN BIAS — FALSIFIED.** The intercept moves 5% over a **16× range in W**, non-monotonically.
  It does not scale with W. The argument that justified sealing on the coefficient was resting on a
  misattribution.
- **(b) PRIME-≤13 — FALSIFIED AS AN ATTRIBUTION, and the error is double-counting.** Σ_{p≤X} 1/p =
  lnln X + M *already contains* the p ≤ 13 mass; it is a **sub-component of the sum**, not an additive
  constant on top of it. Comparing 0.07494 (a component) against 0.0738 (a fit parameter) compared two
  categorically different objects that happened to be numerically close. **A numerical coincidence,
  which is exactly why the reviewer said the sweep must decide it rather than the agreement.**
- **What the retraction (R-034) keeps:** the disjoint-bands conclusion is **unaffected** — primes ≤ 13
  contribute **0.0% of the slope** because the slope comes from the 15,587 primes entering between
  X_lo and X_hi. That never depended on the intercept coincidence. Only the "101.5% of the intercept"
  flourish dies.
- **⚠ WITHDRAWN by R-039.** "0.052 unaccounted, a genuine constant of the process" audited only the
  **measurement** side. The prediction 0.0203 assumes a *sharp* cutoff at X = t/2π and is not sharp
  enough to support a gap — see R-039. Withdrawn as a claim.
- **⚠ WEAKENED: "invariant to W" was too strong.** With the intercept's sem (0.00093–0.00345, typical
  **0.00175**), the across-W spread of 0.00411 is **2.3 sem** — a small W-dependent term *is* present.
  The sweep supports only the weaker statement: **demean bias is excluded as the DOMINANT term, not as
  a few-percent one.** "Moves 5% non-monotonically" and "invariant to W" cannot both stand without the
  error bar, and with it only the first survives.
- **THE LOAD-BEARING RESULT IS BETTER THAN THE ARGUMENT IT REPLACES:** the **slope is measured-stable**
  — 0.0499–0.0503 for W ≥ 10000 and ≥2 pts/spacing, i.e. invariant across **16× in W** and **16× in
  resolution**. The coefficient seal is safe, and now for a *measured* reason rather than an argued one.
- **Status:** OPEN (intercept unexplained; slope stability established)

### R-037 — An invariance sweep cannot gate an invariant systematic
- **Seen:** R-036's sweeps establish insensitivity to W and to sampling resolution. They say **nothing**
  about a cutoff whose height-dependence mimics lnln — if the estimator's effective cutoff is set by
  local mean spacing, it moves with height at **every** resolution, the sweep rescales all arms equally,
  reports a stable slope, and the contamination survives untouched. **Passing it would be this arc's
  fourth inert falsifier.**
- **The powered version — a known-answer null.** Build a synthetic whose prime sum is truncated at a
  **fixed X₀**: it has **no lnln growth by construction**. Run it through the identical estimator at
  both heights. Any reported growth is manufactured, and its size *is* the budget entry. This is the
  theory-specified-control-class move again — a control the theory fixes rather than the analyst.
- **Constructibility (the reviewer flagged this gates the suggestion): YES.** S_synth(t) =
  −(1/π)·Σ_{n≤X₀} Λ(n)/(√n log n)·sin(t log n) is a finite sum; place zeros at solutions of
  N_smooth(t) + S_synth(t) = j by numerical inversion. Cost is O(X₀) terms per evaluation and the
  inversion is monotone. Cheap.
- **Status:** OPEN — this, not the sweep, is the real cutoff gate.

### R-038 — Normality certifies the observable, NOT the cutoff
- Selberg's CLT gives normality of normalized S — a statement about **shape**, independent of the
  variance coefficient, so skewness→0 and kurtosis→3 certify the S observable at both heights
  **without consuming the quantity being measured**. Same structure as sealing on the coefficient
  rather than the level, one layer up.
- **NOT claimed:** its power against **cutoff drift** is weak — a truncated prime sum is still a sum of
  many near-independent terms, so normality is robust to truncation. **Run it as certification of the
  observable and do not credit it as the cutoff gate.** Two slots; the first does not discharge the
  second.
- **Status:** OPEN

### R-039 — Audit the PREDICTION before filing a residual
- **Seen:** R-036 filed 0.052 as an unexplained constant after establishing the *measurement* was clean
  (W- and resolution-invariant). The **prediction** was never audited. C·(M + C₂) = 0.02028 assumes a
  **sharp** cutoff of the prime sum at X = t/2π, and that convention alone moves the constant:

| convention | shift | intercept |
|---|---|---|
| sharp, X = t/2π | — | 0.02028 |
| smooth w(u) = e^(−u) | C·(−γ_E) = **−0.02924** | −0.00896 |
| X = (t/2π)² | C·log 2 = +0.03512 | 0.05540 |
| X = t | C·log 2π = **+0.09311** | 0.11339 |

- **Measured intercept 0.07411 ± 0.00175; gap vs sharp-t/2π = 0.05383; the convention span alone is
  0.1224 wide.** The gap sits **inside** it. **The prediction is not sharp enough to declare a gap.**
- **Generalises — R-029 one level up:** when measurement and prediction disagree and the measurement is
  clean, **the prediction is the cheaper suspect.** R-029 said a structured residual may diagnose the
  instrument; this says an unstructured one may diagnose the *theory-side convention*. Both times the
  residual was real and both times it was not about the object.
- **Checkable corollary, consistent with everything measured:** cutoff shape moves the **intercept** and
  not the **slope**, because the slope is set by the density of primes entering, shape-independent to
  leading order. This is why the coefficient seal survives the withdrawal.
- **Status:** OPEN (narrowly scoped lit question, NOT a survey: *does an exact second-order constant for
  the mean square of S(t) exist in the literature — Fujii and successors?* If yes, 0.052 becomes a
  comparison rather than an open item. One question; the answer closes or sharpens it.)

### R-040 — The fixed-X₀ null needs a tracking-X₀ positive arm
- **Null-only is unpowered.** X₀ fixed ⇒ no lnln growth by construction; if the estimator returns zero
  slope you have learned either that it manufactures nothing **or that it cannot see growth at all.**
  The discriminator is the second arm: **X₀ = t/2π tracking, which must reproduce the full 0.0500.**
- **Pre-tabulate** the smallest spurious slope the null can detect — the synthetic is cheap enough to
  run to arbitrary precision, so there is no excuse for an unquantified floor.
- **Construction verified:** each sine contributes variance ½, so
  Var[S_synth] = (1/2π²)·Σ_{n≤X₀} Λ(n)²/(n log²n) — the correct weight for S, not for the density.
- **Same lesson as the Dirichlet amplitude gate**, which was an unpowered pass until the injected-trend
  control fired. Both arms, or it is the fourth inert falsifier.
- **Status:** OPEN — this is the real cutoff gate.

### R-041 — The slope now has an error bar, and systematics already dominate
- **Seen:** inverse-variance combined over W ≥ 10000: **slope = 0.05008 ± 0.00026** (statistical).
  Selberg 1/2π² = 0.05066 → **2.22σ low.**
- **NOT claimed:** this is **not** a confirmation and **not** a tension. 2.2σ with a *statistical* error
  bar, against an intercept whose W-drift is already 2.3 sem, means there is an unbudgeted systematic of
  at least that size. **"Consistent with 1/2π²" stands; "measures 1/2π²" does not.**
- **The design consequence, predicted two messages before it was measured:** at 0.5% slope precision the
  program is **systematics-dominated before it has been sealed**. The seal belongs on the systematics
  budget, not on power — and R-040 is the first entry that budget needs.
- **Status:** OPEN

### R-042 — Cross-slot collision 0.0724 / 0.0725: ruled out
- Var[S]-at-the-zeros (Task B D1, γ≈1420 block, n=2000) = **0.07244**; the high-γ fit intercept =
  **0.07411** — 2.3% apart, different data, different observable, different estimator. The fit
  reproduces the scout table independently (0.1897/0.1959/0.1990 vs 0.1884/0.1945/0.1976), so the
  intercept is doing real work in its own slot. **Coincidence.** Checked because this arc has been
  bitten repeatedly by two slots sharing one number, and the check was a grep.
- **Status:** RETIRED

### R-043 — **The intercept is CLOSED. It is the pair-correlation integral.**
- **Recomputed independently** (`scout10_goldston.py`, mpmath 30 dps), reviewer's values confirmed:
  Σ = Σ_p Σ_{m≥2}(1/m − 1/m²)p^(−m) = **0.1762478124** (the m=1 term vanishes identically);
  C₀ = γ_E = 0.5772156649; bracket = ∫₁^∞ F/α² dα + C₀ − Σ = **1.400967852**;
  **predicted intercept = 0.07097386** against measured **0.07411 ± 0.00175 → 1.79 sem.**
- **My "prediction" was Goldston's non-F terms relabelled, and it is an EXACT IDENTITY, not a near-miss.**
  M + C₂ = 0.400967852459 and C₀ − Σ = 0.400967852459 — agreement **4.9×10⁻³²**. Proof: Mertens gives
  M = γ + Σ_p[ln(1−1/p) + 1/p] and ln(1−1/p) + 1/p = −Σ_{m≥2}(1/m)p^(−m), so
  M + Σ_p Σ_{m≥2}(1/m²)p^(−m) = γ − Σ_p Σ_{m≥2}(1/m − 1/m²)p^(−m) = C₀ − Σ. **QED.**
- **So the sole missing term was the F-integral, worth exactly 1 in bracket units.** Measured residual:
  **1.031** (W=20000) to **1.062** (W-combined), against **1** predicted under Montgomery's Strong Pair
  Correlation Conjecture. The "unexplained 0.052" was 1/2π² = 0.05066 all along.
- **Provenance: `LIT`, conditional on RH.** Per rule 11 that conditionality is a fact about the
  **reference**, never about the measurement — ARS consumes a finite list of verified zeros.
- **Status:** **RETIRED — closed.** R-036's residual and R-039's "prediction not sharp enough" are both
  superseded: the prediction *was* sharp, it was simply **incomplete by one term**, and the term is
  identifiable to a decimal.

### R-044 — The intercept as an α ≥ 1 handle: UNEARNED
- **Seen:** Goldston makes the intercept a functional of F(α) on **α ≥ 1** — precisely the region §7
  grades as having no bracket. 2.36% intercept precision maps to **3.25%** on ∫₁^∞ F/α² dα.
- **NOT claimed, and flagged unearned by the reviewer as their own fourth capability-from-mechanism:**
  the o(T) in Goldston's formula is **unbounded at finite T**, which is exactly where such a handle
  would die. **Treat as unearned until someone bounds that term at these heights.** Filing it as a look
  rather than a capability is the whole point of §R.
- **Status:** OPEN (candidate, explicitly not a capability)

### R-041 — AMENDED: the slope deficit is the size of a next-order term
- The 2.22σ deficit (0.05008 ± 0.00026 vs 0.05066) is **exactly what an O(0.1) next-order coefficient
  produces over this lever arm.** 1/ln X falls 0.1167 → 0.0826 across the arc, so if
  Var[S] = C[lnln X + const + a/ln X + …] the apparent slope is C[1 − a/ln X] with ln X ≈ 10.33
  mid-arm; the measured 1.14% deficit requires **a = 0.118**.
- **Consequence:** at 0.345 in lnln, **the leading asymptotic is not the right prediction.** The
  measurement is a **joint constraint on (coefficient, correction)**, not a test of the coefficient
  alone. Chan's ratios-conjecture expansion of the lower-order terms makes this checkable rather than
  hand-waved. Adjacent: arXiv:2211.14918 (number variance of ζ zeros, Berry's conjecture).
- **Status:** OPEN — and this, not power, is what the seal must be written against.

### R-045 — Declining to fetch is the underclaim face of the provenance rule
- **Seen:** after the Luo failure I declined to run a targeted lit query, reasoning that introducing a
  `LIT` pointer unilaterally was the risk. **Wrong diagnosis.** Luo failed because a `SESSION` pointer
  was **cited as record** — not because it was fetched. The four-grade ladder exists precisely so `LIT`
  can enter safely with its mapping flagged unaudited.
- **The cost was measured, not hypothetical:** the intercept sat filed as an open property of ζ for a
  full cycle, and two register entries (R-036's residual, R-039's "prediction not sharp enough") were
  written that a single query would have pre-empted.
- **Rule:** abstinence does not reduce provenance risk; **it converts a gradeable pointer into an
  unasked question.** Rule 13's underclaim face at the level of research conduct — downgrade for absence
  of verification, never for caution, and *asking* is not the thing that needs guarding.
- **Status:** OPEN (standing rule)

### R-046 — **The 0.0203 was never wrong. It was the SYNTHETIC's intercept.**
- The synthetic has no zeros, hence **no F-integral**. Verified independently: for n = p^m,
  Λ(n)²/(n log²n) = **1/(m²p^m)** exactly (max |diff| 3.5×10⁻¹⁸ over 15 cases), so
  Σ_{p^m≤X} 1/(m²p^m) = **lnln X + C₀ − Σ** (checked at X = 10⁴…10⁷; residual 7.4×10⁻⁴ → 5.0×10⁻⁷,
  the Mertens error term). Therefore **Var[S_synth] = (1/2π²)[lnln X₀ + C₀ − Σ]** — Goldston's
  expression *minus the F-integral*, which is precisely what a prime-sum-only object should be.
- **So C·(M + C₂) = 0.020313 correctly predicts R-040's tracking arm.** Correct-fact/wrong-slot — the
  program's dominant error mode, landing on its final number.
- **R-040 upgrades from one prediction to three, pre-registered here:**

| quantity | predicted |
|---|---|
| tracking arm (X₀ = t/2π), slope | **0.050660592** |
| tracking arm (X₀ = t/2π), intercept | **0.020313269** |
| ζ intercept (Goldston, SPCC) | **0.070973861** |
| **ζ − synthetic intercept difference** | **0.050660592 = 1/2π² = the F-integral** |

- **The third is the valuable one.** Both arms run through the **identical estimator**, so estimator
  bias **cancels in the difference**. That measures the F-integral without needing Goldston's constants
  to precision and without common-mode bias, because the synthetic side is known in **closed form**
  rather than resting on o(T).
- **R-044 nonetheless stays a LOOK:** o(T) remains on the ζ side. But the differential form is the
  right way to take it if it is ever taken — materially better than the direct handle.
- **Status:** OPEN (pre-registered; unrun)

### R-047 — The third failure mode reorders the diagnostic sequence
- Three ways a measurement–prediction gap resolves, now all three observed in this arc:
  **(a) instrument** (R-029: a point-sampled peak is not an amplitude) — residual is an artifact, work
  is to remove it; **(b) convention** (R-039: sharp-vs-smooth cutoff) — same, no owner;
  **(c) an omitted term in a published expression** (R-043: the F-integral) — **the residual is a real
  quantity someone has already named.**
- **(c) has a property the others lack, and it is the cheapest to check.** So the first question when
  measurement and prediction disagree is **"does a published expression for this quantity contain a
  term I omitted?"** — one query, cheaper than an instrument audit or a convention audit, and it
  belongs **before both.**
- **Measured cost of not running it here:** two register entries (R-036's residual, R-039's
  not-sharp-enough) and a full cycle, both superseded by one lookup. See [[R-045]].
- **Status:** OPEN (standing rule; reorders R-029/R-039's sequence)

### R-041 — AMENDED AGAIN: a = 0.118 is zero-dof, and the fallback lever does not exist
- Fitting one correction coefficient from one deficit is **zero degrees of freedom** — unfalsifiable
  as stated, and the temptation is to treat the fitted value as the explanation.
- **The proposed second lever is NOT available at this lever arm.** Over lnln 2.148→2.493,
  corr(1, 1/ln X) = **−0.999** and the design matrix [lnln, 1, 1/ln X] has condition number **4107**.
  A 3-parameter fit is degenerate by construction; disjoint γ sub-ranges make it worse, not better.
- **PRE-COMMIT:** take `a` from Chan's ratios-conjecture expansion **independently**, and use the
  measurement to **test** it. Do not offer sub-range consistency as a fallback — it is unavailable and
  saying so now prevents it being reached for later.
- **Status:** OPEN

---

## Phase 6 — R-040 RUN

### R-048 — **R-040's construction does not define a point process. Constructibility gate FAILS.**
- **Ran it** (`phase6_r040_run.py`). The ζ arm was clean; **both synthetic arms returned values of order
  10¹²** — garbage, not a measurement.
- **Diagnosis:** the synthetic requires γ_j to solve N_smooth(t) + S_synth(t) = j − ½. Newton needs
  N_smooth + S_synth to be **monotone**. But
  dS_synth/dt = −(1/π)·Σ_{n≤X₀} Λ(n)/√n·cos(t log n), whose amplitude bound is ~(2/π)√X₀:

| γ | X₀ = t/2π | dN_smooth/dt | max\|dS_synth/dt\| | ratio |
|---|---|---|---|---|
| 3.3×10⁴ | 5,252 | 1.363 | 45.2 | **33×** |
| 2×10⁵ | 3.18×10⁴ | 1.650 | 112.6 | **68×** |
| 5.5×10⁵ | 8.75×10⁴ | 1.811 | 187.4 | **104×** |
| 1.1×10⁶ | 1.75×10⁵ | 1.922 | 265.4 | **138×** |

  The truncated prime sum's derivative exceeds the smooth density by **2–3 orders of magnitude**, so
  N_smooth + S_synth is wildly non-monotone, the defining equation has **no unique root**, and Newton
  diverges. Monotonicity would need X₀ ≲ 10 — useless.
- **The truncated explicit-formula sum is a DISTRIBUTIONAL object, not a density.** It defines a point
  process only after smoothing — and smoothing is exactly what R-039 showed shifts the constant, so the
  sharp-X₀ arms are not merely hard to build, they are **not well-defined as specified.**
- **This is mine.** The reviewer flagged constructibility as gating the whole suggestion and explicitly
  did not claim it. I filed "**constructible: YES… cheap**" in R-037 from a correct-looking closed form
  for Var[S_synth] without checking whether the object generating it exists. Capability claim from a
  mechanism, one more time, and the closed form was never the issue — the *point process* was.
- **And my script's verdict logic issued an inert PASS.** It printed "PASS — estimator manufactures no
  growth" because |slope/sem| < 2 on numbers of order 10¹² divided by errors of order 10¹². A threshold
  test on meaningless input returning a pass — the exact shape this arc has catalogued four times,
  produced here by my own harness. **A verdict line must gate on input sanity before it gates on a
  threshold.**
- **Status:** OPEN — the cutoff gate has **no valid construction** and is not merely unrun. A direction
  (not a design): band-limit the *real* zeros by a known amount and check the estimator recovers the
  known change, rather than synthesising a spectrum from scratch.

### R-049 — Normality: skewness clean, kurtosis contaminated
- **Measured on the ζ blocks:** skewness **−0.0003 ± 0.0006** against Selberg's 0 — clean.
  Kurtosis **2.6942 ± 0.0051** against 3 — **60 sem low.**
- **NOT a failure of Selberg.** S as estimated includes the **sawtooth** (S falls linearly by 1 between
  zeros then jumps), a bounded roughly-uniform component with kurtosis 1.8. Mixing it with a Gaussian
  pulls the kurtosis down; both components are symmetric, which is why skewness is unaffected.
- **So the normality certification is contaminated and cannot be read as a test of Selberg's CLT
  without removing the sawtooth.** Filed as certification **attempted and not achieved**, not as
  tension. R-038's slot stands; the arm has not yet filled it.
- **Status:** OPEN

### Phase 6 — what the ζ arm gives (the only clean result)
- slope **+0.050164 ± 0.000814**, intercept **+0.072745 ± 0.001923** at W=5000, n=16 — consistent with
  the W-sweep and with Goldston. No new claim.

---

## Phase 7 — exact moments, and the program read

### R-050 — The right estimator removed the systematic instead of gating it
- **Move (reviewer's):** on (γ_j, γ_{j+1}), N(t) = j exactly, so in the **unfolded** variable
  S(u) = j − u is **linear**. With s_j = j − u_j: interval length = 1 − s_{j+1} + s_j and
  ∫S^k du = Σ_j [s_j^(k+1) − (s_{j+1}−1)^(k+1)]/(k+1). **Exact, O(W), no grid, no resolution
  parameter, no aliasing, no height-dependent effective cutoff.** No θ² quadrature either — in u the
  integrand is a cubic, so the reviewer's flagged concern dissolves.
- **The cutoff-drift mechanism lived entirely in the sampling step. Deleting the step deleted the
  mechanism** — R-040 is **VOID**, not open, and R-048's dead construction no longer matters.
- **Measured cost of the step that was removed:** exact − sampled Var[S] = **−0.000048 (0.02%)**. So
  the sampling bias was small and the earlier numbers were not materially wrong — the gain is the
  *elimination of a class of concern*, not a correction.
- **Third instance this arc** of the same move: count-deficit over smoothed drift (R-023); raw-t
  coordinate over L̄-rescaled (R-031); exact integration over sampled (here). **Bank it: when a gate is
  hard to build, first check whether a different estimator makes the systematic impossible.**
- **My bug, same shape as several others:** I wrote "all O(1), numerically stable" and then used
  **local** j with **global** u_j (~10⁶), so s was O(10⁶) and the fifth powers lost all precision —
  negative variance, complex skewness. The *formula* was stable; the *implementation* was not
  normalised. Caught by the output being obviously impossible, which is the only reason it was cheap.
- **Status:** RETIRED (R-040 void, R-037 superseded)

### R-051 — **The program, run: leading order is REJECTED, and the lever arm cannot fit the correction**
- **Exact estimator, W=20000, n=20:** slope **0.049974 ± 0.000226** (Selberg 0.050661 → **−3.03 sem**);
  intercept **0.073152 ± 0.000538** (Goldston 0.070974 → **+4.05 sem**).
- **These are ONE degree of freedom, not two.** Over this lever arm the fitted slope and intercept have
  correlation **−0.9991**, so a low slope *forces* a high intercept. The 3σ and 4σ are the same
  discrepancy seen twice, and quoting them as independent tensions would be double-counting — the same
  error as R-036's component-vs-fit-parameter comparison.
- **What it means:** at 0.45% slope precision the **two-parameter (slope, intercept) model is
  rejected.** The deficit corresponds to a next-order coefficient **a = 0.140** (the coarser earlier
  fit gave 0.118). R-041's "the measurement is a joint constraint, not a coefficient test" is now
  **measured** rather than inferred from a 2.2σ hint.
- **⚠ Therefore the F-integral is NOT measured at 1.0430 ± 0.0106.** That is a 2-parameter reading of a
  3-parameter reality, and the anti-correlation puts the missing correction directly into the
  intercept. R-046's differential remains the right way to isolate it — but its synthetic arm is void.
- **The terminal statement:** *the data are precise enough to show that leading order is wrong, and not
  extended enough to fit the correction* (cond[lnln, 1, 1/lnX] = 4107 over this arm).
- **This inverts the standing of the lever-arm extension.** Odlyzko's 10²¹/10²² tables were filed as a
  next phase, not a prerequisite. They are now **what the measurement demands**: at ln X ≈ 46.8, lnln
  reaches ≈3.85 against the current 2.493, 1/ln X falls to 0.021, and the collinearity that makes `a`
  unfittable breaks. Caveats stand and are the reviewer's: 10⁴ zeros/block sits at the W-stability
  boundary, one block per height gives no within-height σ_V, and 10²¹/10²² are nearly one lnln point.
- **Status:** OPEN — and this is the program's actual result.

### R-052 — Normality: skewness certifies, kurtosis drift fires in the predicted direction
- **Exact moments, n=20:** skewness **+0.00010 ± 0.00026** against Selberg's 0 — **clean, R-038's slot
  filled on this arm.**
- Kurtosis **2.69690 ± 0.00376** against 3. The reviewer's Gaussian+sawtooth model
  (kurt = [3σ_G⁴ + 6σ_G²/12 + 1.8/144]/V², σ_G² = V − 1/12) predicts **2.7474 → 2.7869** across the arm,
  i.e. a **drift of +0.0396**. **Measured drift +0.0500 ± 0.0032 — 15.4 sem from zero, and +3.20 sem
  from the prediction.**
- **Reading:** the drift is real, in the predicted direction, at the predicted order — so the
  contamination is **modelled, not merely named**, which is what R-038 needed. But it is **26% larger
  than the idealised model**, and the point estimate is 2.77% off at the actual mean V (the reviewer's
  0.6% used V = 0.170, below this run's range). Both gaps are expected from the model's own stated
  idealisations: spacings are not uniform so the sawtooth variance is not exactly 1/12, and
  independence of the two components is heuristic.
- **Status:** OPEN — certification **achieved on skewness**, **directional on kurtosis**.

---

## Phase 8 — the invariant, the slot problem, and the extension's power

### R-053 — **SLOT PROBLEM: cumulative vs local. The centroid offset is not a rejection.**
- Goldston as reported is **cumulative**: ∫₀^T S²dt = (T/2π²)[lnln(T/2π) + B] + o(T). My Var[S] is a
  **block-local** mean square at height ≈T. They differ by a derivative, and
  d/dT[(T/2π²)(lnln+B)] = (1/2π²)[lnln + B + **1/ln X**] — the local form carries an extra 1/ln X term
  with coefficient **exactly 1**, worth 0.00471 at the centroid, **200× the sem.**

| at centroid lnln = 2.37565 | value | vs measured 0.191874 ± 0.000023 |
|---|---|---|
| cumulative reading C(lnln+K) | 0.191326 | **+23.8 sem** |
| local reading C(lnln+K) + C/lnX | 0.196035 | **−180.9 sem** |

  and on the slope: the local form predicts C[1 − 1/lnX] = 0.045951 → **+17.8 sem**; the cumulative
  form predicts C → **−3.0 sem**.
- **NEITHER FORM FITS.** So the offset is **slot-uncertain, not a rejection**, and the implied
  a = 0.116 is what it takes to close the *cumulative* reading — not an independent measurement.
- **This is R-047 applied one notch further than I applied it.** I asked "does the published expression
  contain a term I omitted?" and stopped. I did not ask **"is the published expression in the same FORM
  as my estimator?"** Cumulative-vs-local is a form mismatch, not a missing term, and it is invisible to
  the check that caught the F-integral.
- **Consequence for grading:** the Phase-7 result cannot be filed as *"a genuine finding about ζ at
  finite height."* Its grade is contingent on a slot question I cannot close without the paper.
  **Filed as: leading-order-plus-Goldston is rejected in ONE reading and over-predicted in the other.**
- **Status:** OPEN — dominant open question, and cheaper to resolve than anything else here (read the
  form of the stated theorem, one query).

### R-054 — The invariant combination: what the run actually measured
- corr(slope, intercept) = −0.9991, so neither is believable alone. For an OLS line the fitted value at
  the **centroid** has variance s²/n and is **uncorrelated with the slope**:
  **V(lnln = 2.37565) = 0.191874 ± 0.000023** — **23× tighter than the intercept.**
- **That is the transferable number**: it survives into a 3-parameter fit without re-litigation, where
  the slope and intercept do not. Quote it in preference to either.
- **Status:** OPEN (the number stands; its comparison is R-053)

### R-055 — Extension power, pre-registered before any table is fetched
- **σ_V at W=10⁴ = 0.000236**, measured on 12 disjoint blocks, not scaled. (Ratio to W=2×10⁴ is
  **1.21**, not √2 — the same non-√W scaling R-002 found for the ⟨r̃⟩ floor, now confirmed for Var[S].)
- **3-parameter WLS [lnln, 1, 1/lnX]:** near data alone cond = **6259** (rank-deficient in practice);
  + one far block cond **610**, σ(a) = **0.116**; + both blocks cond **632**, σ(a) = **0.108**.
  Against a ≈ 0.15 that is ~1.4σ — **`a` becomes identifiable but NOT precise.**
- **Two-model discrimination at γ = 10²²:** separation **0.000619** against σ 0.000236 →
  **2.62σ with one block, 3.71σ with two.** So: **run it only with both blocks**, and even then it is a
  ~3.7σ discrimination, **not a measurement of a**.
- **The reviewer's caveat is doubly void:** 10²¹ and 10²² being nearly coincident in lnln does not
  matter — you need one far point for rank, and you need *both* for the precision.
- **PRE-REGISTERED ASYMMETRY:** a = 0.146 was **fitted from these data to absorb the misfit.** A refitted
  `a` near 0.146 after the extension is **not** confirmation — the same data drive both. The test is the
  far point's **position** against the 2-parameter extrapolation:
  γ=10²² → 2-param **0.265404**, 3-param **0.266023**; γ=10²¹ → **0.262905** vs **0.263498**.
- **Status:** OPEN (pre-registered; gated on R-053, since the model being extrapolated is the one in
  question)

### R-052 — AMENDED: kurtosis is modelled, not bracketed
- +3.20 sem from prediction is the model's grade: **direction and order confirmed, magnitude 26% off.**
  That is **candidate-upgraded-to-modelled**, the same standard the +2.27σ Maass departure never
  earned its label under. **Filing it as validating the sawtooth model would be wrong.** The two known
  idealisations (non-uniform spacings, heuristic independence) both push the same way, so 26% is
  unsurprising — but it was **unpredicted**, which is the distinction.
- The 0.6% point-estimate agreement was computed at V = 0.170, below this run's range; at the actual
  mean V the honest figure is **2.77%**.

---

## Phase 9 — R-053 RESOLVED from inside

### R-056 — **The form question is settled, and the answer voids both comparisons**
- **The "local" row is struck**, per the reviewer: it was obtained by differentiating an asymptotic
  carrying an o(T) error, and d/dT of o(T) is **not** o(1) — it is unbounded. The algebra was right
  (coefficient exactly 1, 0.00471 at the centroid) but the object does **not** inherit the theorem's
  grade and was never a legitimate prediction.
- **The "cumulative" row is also void, and the data say why.** Computed directly with the same exact
  O(W) machinery over all 2×10⁶ zeros, G(T) = (2π²/T)∫₀^T S²dt − lnln(T/2π):

| T | 7.5×10⁴ | 2.0×10⁵ | 4.3×10⁵ | 7.1×10⁵ | 9.8×10⁵ | 1.13×10⁶ |
|---|---|---|---|---|---|---|
| G(T) | 1.29685 | 1.30660 | 1.31346 | 1.31715 | 1.31937 | **1.32041** |
| G − K | −0.104 | −0.094 | −0.088 | −0.084 | −0.082 | **−0.081** |

  **Goldston's asymptotic has NOT converged at accessible heights** — 5.8% short at the top, rising at
  0.0927 per unit lnln, extrapolating to arrival near **T ~ 10¹³.**
- **So the Phase-7/8 comparison was against a constant the data show is not yet reached**, and the
  "leading order rejected at 0.45%" reading was right about the *measurement* and wrong about the
  *meaning*: it is not that ζ deviates from theory, it is that **the theory's asymptotic has not
  arrived.** `a` ≈ 0.12–0.15 is a **parameterisation of the non-convergence**, not a physical
  next-order coefficient.
- **This is R-009 one observable over.** That entry already measured Selberg's CLT variance at
  **1.80× the asymptotic** at γ≈1420 and filed it as a *window property, not a result about ζ*. The
  same phenomenon, on the same axis, and I did not connect them.
- **Two of the three form axes are NULL, measured:** centred-vs-uncentred gives ⟨S⟩² = **0.000000**
  (0.00% of V); u-average vs t-average differ by **10⁻⁶**. Only cumulative-vs-local mattered, and it
  matters for a reason neither of us named. Machinery check: dI/dT equals the local M2(t) to **10⁻¹³**.
- **Stub, per the reviewer's flag:** ∫₀^γ₁ S²dt = **0.8974**, worth 0.001% of K at T=10⁶. Real,
  computed, negligible.
- **Phase 7's grade, finally:** not a finding about ζ, and not slot-uncertain either — **a measured
  window property: the second-moment asymptotic is ~6% from arrival at the top of the catalogue.**
- **Status:** RETIRED (R-053 resolved; no lit query was needed)

### R-057 — `a`: five values, one symbol, one table
Filed because this is the program's central parameter and the extension was pre-registered against it.

| value | estimator | lnX convention | source |
|---|---|---|---|
| 0.118 | sampled | 10.33 (mid-arm) | slope 0.05008 ± 0.00026, W≥10000 combined |
| 0.140 | **exact** | 10.33 (mid-arm) | slope 0.049974 ± 0.000226 |
| 0.146 | **exact** | 10.759 (centroid) | phase8 a_fit = (C−sl)/C·e^x̄ |
| 0.116 | **exact** | 10.759 (centroid) | intercept offset ÷ (C/lnX) |
| "~0.15" | — | — | my loose verbal reference to the above |

  The spread is **two estimators × two lnX conventions**, not five measurements. **And all five are
  now void as physical coefficients** (R-056): they parameterise non-convergence.
- **Status:** RETIRED (superseded by R-056; table kept so the drift is not repeated)

### R-058 — Non-√W scaling: two independent instances, promote from quirk to property
- ⟨r̃⟩ floor: c = sd·√W grows 0.243 → 0.303 over W = 2000 → 10000 (R-002/§9, filed "a fact about the
  statistic, untested"). **Var[S]:** σ_V ratio W=10⁴ → 2×10⁴ is **1.21, not √2 = 1.41** (R-055).
- **Two statistics, same direction, is no longer one statistic's quirk** — it is a property of block
  estimates on these spectra, and both instances belong attached to it.
- **Consequence:** any error bar anywhere in the repo computed by assuming √W scaling is **optimistic**.
- **Status:** OPEN (promoted; §9's "untested" line superseded)

---

## Phase 10 — R-056 REVERSED. The deficit is an integration artifact.

### R-059 — **The cumulative deficit is derivable arithmetic, not non-convergence**
- **Derivation (reviewer's), verified:** ∫₀^T lnln(t/2π)dt = T·lnln(T/2π) − T/L − T/L² − …, so if the
  **local** bracket is a constant K, the **cumulative** bracket is its running average:
  **G(T) = K − 1/L − …, coefficient on 1/L exactly 1, by integration.**
- **Form test from raw, 40 heights** — unambiguous:

| model | coefficient | rms residual (% of deficit) |
|---|---|---|
| **b/L** | **0.97627** | **0.22%** |
| b/L² | 10.75 | 7.94% |
| b·lnln (linear) | 0.0359 | 10.50% |
| constant | 0.0871 | 7.60% |

  **1/L wins by 35× in residual.** My R-056 reading — "linear-in-lnln decay, arrival near T ~ 10¹³" —
  was the wrong functional form and is **dead**. (K−G)·L = **0.97602 ± 0.00189** across 40 heights.
- **b = 0.976 against a derived 1: the 2.4% gap is ~12 sd of the scatter, so it is REAL, not rounding**
  — resolving the reviewer's flagged uncertainty. It corresponds to a small genuine local correction
  of ≈ 0.024/L. Two-term fit: deficit = 0.953/L + 0.254/L².

### R-060 — **"Leading order rejected at 0.45%" does not survive — and neither does the residual**
- Inverting exactly (BOTH terms; dropping (1−b)/L is what leaves a residual):
  **V_local = C[lnln X + K + (1−b)/L + b/L²]**

| | invariant (meas. 0.191874 ± 0.000023) | slope (meas. 0.049974 ± 0.000226) |
|---|---|---|
| plain C(lnln+K), no correction | 0.191325 → **+23.71 sem** | 0.050661 → **−3.03 sem** |
| b/L² only (reviewer's form) | 0.191753 → **+5.24 sem** | 0.049806 → **+0.74 sem** |
| **both terms, derived** | **0.191866 → +0.36 sem** | **0.049693 → +1.24 sem** |

- **With the derived relation applied in full, both are consistent at ≤1.3 sem. There is no residual to
  explain.** The reviewer's "+5.2 sem real residual at 1/ln²X order" was the dropped (1−b)/L term, and
  my −3.03 sem was the missing correction entirely.
- **Every downstream claim collapses together:** R-051's rejection of leading order, R-053's slot
  problem, R-056's non-convergence, and a ≈ 0.12–0.15 in all four of its slotted forms. **All were one
  artifact: comparing a local statistic against a cumulative formula without inverting the relation.**
- **Status:** the lnln program's terminal state — **measured Var[S] is consistent with
  Selberg + Goldston (SPCC) once the integration relation is applied**, at 0.36 sem on the invariant
  and 1.24 sem on the slope. The one surviving residual is b = 0.976 vs 1.

### R-061 — R-047, one notch further: check whether the relation between forms is DERIVABLE
- R-047 said: when measurement and prediction disagree, first ask whether the published expression
  contains a term you omitted. R-053 extended it: ask whether it is in the same **form** as your
  estimator. **This adds the third rung: when the forms differ, ask whether the RELATION between them
  is derivable — before treating the difference as an unknown to be measured.**
- Here the answer was yes, in two lines of calculus, and I instead filed the difference as a slot
  problem (R-053), then as evidence of non-convergence (R-056), then extrapolated an arrival height
  from it. **The residual had an owner and the owner was arithmetic, not literature.**
- **Sequence to bank:** omitted term → form mismatch → **derivable relation between forms** → only then
  a measurement.
- **Status:** OPEN (standing rule)

### R-055 — AMENDED: the extension's case is stronger and simpler
- Correction size in V units: catalogue top **4.38×10⁻⁴ = 1.86 far-block sem**; γ=10²¹ **5.22×10⁻⁵ =
  0.22 sem**; γ=10²² **4.85×10⁻⁵ = 0.21 sem.**
- **At 10²² the correction is below noise, so the far point measures K DIRECTLY** — no `a` to fit, no
  CFZ-ratios import, **grade cap gone.** The pre-registered 2-param/3-param positions are void; the
  extension's question is now simply *what is K*, which is cleaner than the one it replaces.

---

## Phase 10 — filing corrections

### R-062 — **b = 0.976 has no theoretical owner. File it, do not absorb it.**
- **Precisely what it is:** if the local bracket carries K + c/L, averaging gives cumulative
  = lnln + K − (1−c)/L, so **b = 1 − c** and b = 0.976 means the local bracket has a real correction
  of **+0.024/L**. The *derivation* fixes the coefficient 1; the **0.024 is fitted** from 40 heights.
- **So the terminal state has ONE residual degree of freedom, not zero.** It is: derived relation +
  one empirically fitted local coefficient, which then predicts two local quantities landing at
  **0.36 sem** (invariant) and **1.24 sem** (slope). That is a **genuine cross-prediction** — fitted on
  the cumulative functional, tested on the local one — but **not an independent** one: same zeros.
- **CORRECTED TERMINAL LINE.** Not "consistent with Selberg + Goldston once the relation is applied"
  full stop, which absorbs the residual. It is: **consistent with Selberg + Goldston (SPCC), plus a
  local correction of 0.024/L that no cited expression predicts.** That last clause is the only thing
  in the program still pointing at anything — small, measured, unattributed.
- **Where a predicted value would live:** Chan's ratios-conjecture expansion — the same query that
  closed the intercept, now with a **specific target** (does any expansion predict +0.024/L in the
  local second-moment bracket?) rather than an open question.
- **Status:** OPEN — the program's one live item.

### R-063 — "No finding about ζ" is an underclaim, by rule 13's own face
- The program asked a well-posed question: **does ζ's Var[S] depart from Selberg at accessible
  heights?** It answered **no, at 0.45% precision**, on an estimator with a systematic *class*
  eliminated rather than bounded. **A null on a well-posed question at quantified precision is a
  result** — and it is the result that was available.
- **What did not happen is the deliverable.** At three separate points this program had a
  publishable-looking positive: leading order rejected at 3σ (R-051); an unexplained constant of the
  process (R-036); a non-convergence with an arrival height (R-056). **All three were artifacts. The
  apparatus caught all three.** That is a stronger demonstration than a finding would have been,
  because a finding would not have tested the apparatus at all.
- Reaching it required inverting a wrong sign, a wrong functional form, and four slotted values of a
  parameter that turned out not to exist.
- **Status:** filing correction (supersedes the "no finding" line)

### R-044 — PROMOTED: the extension's payload is the F-integral, not K
- **K is predicted** by Goldston under RH + SPCC. So measuring it at 10²² does not ask "what is K" —
  it **tests the F-integral**, ∫₁^∞ F(α)/α² dα, which lives at **α ≥ 1**, the region §7 grades as
  having **no bracket at all.**
- **Precision:** σ_V = 0.000236 → σ_K = **0.00466** in bracket units → the F-integral (predicted
  **exactly 1** under SPCC) to **0.47%** with one far block, **0.33%** with both.
- **The objection that made this a look has weakened on its own:** o(T) is no longer
  unbounded-in-principle — it is **measured as −1/L with the coefficient now pinned** (R-059).
- **Still flagged unearned, in the usual way:** σ_V at 10²² is *assumed* from the current catalogue and
  could differ, and whether the 0.024/L local correction is stable at lnX = 46.8 is untested.
- **But the question has changed for the better:** a bracket-free region becoming measurable, rather
  than a coefficient being fitted. **Status:** OPEN — and now the best-posed item in the arc.

### R-044 — final amendments, filed before the number exists
- **The caveat as I wrote it reads like a live threat and is not one.** At lnX = 46.8 the local
  correction is c/L = 0.024/46.8 = **0.00051 bracket units = 11% of σ_K** (0.00466). A **factor-of-two
  error in c moves the answer by a tenth of the error bar.** So **any O(1) coefficient on a 1/L term is
  harmless at that height** — the live risk is whether the correction stays **1/L-shaped** out there,
  not what c is. (At the catalogue top the same term is 0.4× σ_K against the FAR-block error — but 1.86 sem against the near-block errors the current fit uses, which is why it mattered *here*.)
  Restated in that form; the stability-of-c flag is withdrawn as binding.
- **SLOT, set before the number exists (rule 11).** What the far block measures is **K**. Converting K
  to the F-integral runs through **Goldston's formula, which is RH-conditional.** So the deliverable is
  ***"the value of ∫₁^∞ F(α)/α² dα implied by Goldston under RH"*** — **not a direct measurement of F
  at α ≥ 1.** §7's bracket-free grade for that region is **unchanged**: this offers an RH-conditional
  **indirect** handle, which is a different and lesser thing. Easy to lose in a write-up because the
  conditionality sits **one inference upstream** of the number.
- **But the CATEGORY is new, and this is the real reason it is the best-posed item.** Every calibrator
  success in this arc **reproduced a theorem** — Farey/Hall, the explicit formula, Goldston's constant,
  Selberg's coefficient, Selberg's skewness. **R-044 would test a CONJECTURE:** SPCC predicts the
  integral is **exactly 1**, and 0.33% is a real constraint on it. **It is the first item in the whole
  program pointing at something not already known to be true.**
- **Status:** OPEN — best-posed item on the board, for this reason rather than the one first given.

---

### R-064 — GATE 0 RESOLVED: the (∛m, ∛m²) ladder is a theorem, factor g²/m not 1/2
- **Derived and verified:** λ′ = (g²/m)·λ with g = gcd(m,p), exact to relative O(q⁻²); location shifts
  by the constant (1/3)log m − log g. Residual measured against the derived 1/(αλq²) term: **ratio
  1.000**, to the double-precision floor. Verified against **β's own continued fraction** for
  m = 2,3,5,6,7,10,12, not against the algebra.
- **"Roughly half" is the m=2, g=1 case only.** ∛2's a = **534** → ∛4's **266** (predicted 267.376,
  measured 267.376). For m=2, **33.1%** of convergents have p even and map with factor **2**, not 1/2 —
  a ladder stated as "roughly half" is wrong on a third of events by a factor of four.
- **Branch taken:** §2 branch 1. The arm is a **calibrator / instrument certification**, never a finding.
- **Where:** `cubic/gate0_ladder.py`, `cubic/GATE0_FINDINGS.md`.
- **Pre-registered or post-hoc:** N/A — a derivation, gated before any arm ran. No seal, no measurement.
- **NOT claimed:** nothing about boundedness of partial quotients (§0); and the mapping to the `LIT`
  sentence is **unresolved** — either the source was ∛2-specific (right, incomplete) or general (wrong).
- **Status:** CLOSED as a gate.

### R-065 — the mechanism is GL₂(Q)-equivalence, and it is ABSENT on the target by theorem
- **General law:** for integer M ∈ GL₂(Q) with determinant Δ, transfer factor is **g²/|Δ|**. Verified on
  x ↦ (3x+1)/(x+2), Δ = 5: measured factors exactly 1/5 and 5. For **any rational map of degree ≥ 2**,
  λ′ ~ λ/q² → 0 — measured collapse 8e−04 → 7e−91 across n = 5…80 on x ↦ x² and x ↦ x²+x+1.
- **So:** derivable correlation of exceptional approximations exists **iff the objects are
  GL₂(Q)-equivalent**. The (∛m,∛m²) anomaly is that classical fact in non-unimodular form and nothing else.
- **And Galois conjugates are not GL₂(Q)-equivalent** — S₃: α₂ ∉ Q(α₁); cyclic: α₂ = f(α₁) with deg f = 2,
  which by the same table transfers nothing. **The derivable mechanism is absent on the target arm by
  theorem, in both sub-cases.** This upgrades §4's "no obvious reason to respect archimedean quality"
  from a plausibility argument to a structural one.
- **Pre-registered or post-hoc:** **POST** — found while executing Gate 0, not anticipated by the spec.
- **NOT claimed:** not that the target correlation is zero. Only that **no derivable mechanism produces
  one**, so a positive would have no candidate source. That is a statement about mechanisms, not data.
- **Status:** OPEN — this is the sharpened form of the phase's question.

### R-066 — the calibrator is a CEILING arm; §5's power requirement is NOT discharged by it
- The ladder is a **deterministic translation**: ρ = 1, a delta at a known lag, per-branch amplitude
  exact. An instrument firing on it has demonstrated it can see an **infinitely strong** signal and has
  licensed **nothing** about a weak one. Floor/ceiling doctrine; unquantified-power antibody.
- **§5 says the positive arm must clear the permutation null "by a stated margin" and halt otherwise.
  As specified, that gate is a ceiling and would pass inertly.**
- **The fix is theory-supplied, not dilution.** At threshold A an α-event survives into β's event set
  only when λ′ = (g²/m)λ ≥ A, i.e. λ ≥ mA/g²: the g=1 branch's coincidence rate falls like ≈1/m while the
  g=m branch transfers everything. **|Δ| = m is a graded coupling knob with a computable answer at every
  setting**, so the detection floor can be *measured* across a family of known-answer pairs.
- **Owed before any seal:** tabulate that floor. A margin quoted from m=2 alone is a ceiling number.
- **Pre-registered or post-hoc:** **POST**. **Status:** OPEN — blocking the seals, not the arms.

### R-067 — §6's digit budget is short by a factor of 2
- §6's arithmetic is right where checkable: P(a≥A) = log₂(1+1/A) (the 1.4427/A form is +1.0% at A=50,
  +0.1% at A=500); Lévy = **0.51532** decimal digits/PQ; event counts 289/29/2885/289 reproduce.
- **But certifying a CF by interval pins terms only while q_n² < 10^D, i.e. n < 0.970·D.** Measured:
  D = 700 → 659 PQs, 1400 → 1365, 2800 → 2738 (predicted 679/1358/2716). So **≈1.03 digits per
  *certified* PQ**; 10⁴ PQs/object needs **~10,300** digits, not ~5,200.
- Negligible at 10⁴; it is the factor that bites at 10⁵, where §6 already flags O(n²) extraction.
- **Pre-registered or post-hoc:** **POST**. **Status:** CLOSED — a correction, applied.

### R-065 — DEMOTED: the cyclic half was wrong; Shanks's simplest cubics are the counterexample
- **What R-065 claimed:** the derivable mechanism is absent on the Galois-conjugate target "by theorem,
  in both sub-cases." **The S₃ half stands. The cyclic half is FALSE.**
- **Counterexample, named and verified:** x³ − ax² − (a+3)x − 1, roots permuted by a Möbius map over ℚ.
  Measured a = 0…11: **M = (1,1;−1,0), t = 1, |det| = 1**, disc = 81, 169, 361, … all perfect squares
  and positive ⇒ totally real cyclic ⇒ **members of the target arm's own population**, and unimodular
  ⇒ Serret-equivalent, shared CF tail, **ρ = 1 with no attenuation**.
- **The error, precisely: I tested a REPRESENTATIVE, not the CLASS.** "α₂ = f(α₁), deg f = 2" is true and
  does not imply the automorphism has no Möbius representative — two rational functions can agree on
  the three roots while differing as functions, and only the Möbius one transfers approximation quality.
  Generalisable: *a property of a map on a finite set is not a property of the formula written for it.*
- **Consequence is a POOLING error, not a scope trim** — the target arm as specified averages a ρ=1
  subfamily against a presumed-ρ=0 subfamily. Same shape as the Palm–Khintchine null and the Maass
  desymmetrization.
- **Status:** DEMOTED to the S₃ case only. Superseded by R-068.

### R-068 — the target arm is THREE strata, and only S₃ is a clean target
- **Stratum 3 as proposed ("cyclic without an order-3 PGL₂(ℚ) element") is EMPTY.** Over Q̄ a 3-cycle on
  3 points determines M uniquely; σ(M) = M for the cyclic generator; PGL₂(Q̄)^Gal = PGL₂(ℚ) by
  Hilbert 90. **Measured: 0 of 162 cyclic cubics lacked a rational Möbius map.**
- **The real stratifier is |det|.** Cayley–Hamilton on a coprime-integer M with M³ = λI forces
  **Δ = t²** — so |det| = 1 iff |t| = 1. **Gapless:** if M, M′ both send α₁↦α₂ then M⁻¹M′ fixes α₁, and a
  non-identity rational Möbius map has fixed points of degree ≤ 2, so **M is unique** and Serret
  equivalence holds **iff |Δ| = 1**. |Δ| is a GL₂(ℤ)-conjugation invariant ⇒ an invariant of the object.
- **A** S₃, no rational Möbius map — **clean target**. **B** cyclic |t|=1 — ceiling, ρ=1.
  **C** cyclic |t|>1 — graded, attenuation g²/t².
- **Census** (|A|,|B|,|C| ≤ 12, irreducible, disc > 0; n = 5388): S₃ **96.99%**; cyclic **3.01%**, split
  **80 / 82** between |t| = 1 and |t| > 1, with |t| ∈ {2,4,5,7,11,13,17}. Δ = t² on all 162.
- **So the "interesting middle" is nonempty — it is half the cyclic population**, just not where it was
  expected. Classification is per-object and costs **0.4 s for 5388 cubics**: disc square-or-not, then |t|.
- **Pre-registered or post-hoc:** **POST**. **Status:** OPEN — this is the corrected target definition.

### R-069 — the dial is a formula, verified; stratum B/C replace the ∛m arm
- Law generalises unchanged: **λ′ = (g²/|Δ|)λ**, g = gcd(ap+bq, cp+dq), and **g | Δ** (verified on every
  convergent tested). Stratum B gives λ′ = λ exactly, hit rate **100.0%**, a = 88 → 88 — the shared tail.
  Hit rates **100 / 47.7 / 17.8 / 6.9%** at |det| = **1 / 4 / 25 / 169**.
- **Event-level rate is what the seals need, and it is predicted:**
  **rate = Σ_g P(g)·min(1, g²/|Δ|)**. Predicted vs measured: 1.00, 1.00, 0.99, 1.35 (cyclic) and
  1.02, 0.99, 1.17, 0.82, 0.90 (∛m). **Any |det| can be sized without running it.** Note the rate does
  **not** fall like 1/|Δ| — the g = |Δ| branch transfers everything and sets the floor.
- **Stratum B replaces the ∛m ladder as positive control** (same ceiling, but inside the target's own
  construction, so it controls for construction); **stratum C replaces the m-dial** for the same reason.
- **Pre-registered or post-hoc:** **POST**. **Status:** OPEN.

### R-070 — axis 2 (jitter) has NO handle in real data; §5's margin is still undischarged
- The ladder places partners at an **exact** lag: asymptotic (n ≥ 200) spread **2–5×10⁻¹³**, the numerical
  floor. Full-range spreads of 1e−2…1e−1 are a small-q transient, not jitter.
- So the ladder varies **count at fixed perfect alignment** and nothing else. The target's plausible weak
  signal is the opposite shape — **many events, partially coincident, smeared in u** — and a detector
  calibrated on "few but perfect" is **uncalibrated** for "many but smeared."
- **Dirichlet precedent is exact:** the amplitude gate was unpowered until the injected control fired.
- **Owed before any seal, NOT delivered:** injection at controlled coincidence fraction **and** controlled
  jitter width, detection floor reported jointly on both axes. **Axis 1 alone does not discharge §5.**
- **Pre-registered or post-hoc:** **POST**. **Status:** OPEN — blocking the seals.

### R-071 — the rate formula, quoted at the precision it has (supersedes R-069's licensing sentence)
- **R-069 said "any |det| can be sized without running it." WITHDRAWN.** The honest summary of the nine
  ratios was ~20% typical / 35% worst, with the worst at the largest |det| — accuracy degrading in the
  direction of extrapolation.
- **Two causes, both in my derivation.** (i) **P(g | event) ≠ P(g)** — an unstated assumption. The g = t
  branch has factor 1 and transfers everything, and events are enriched in it (|t|=13: 0.0674 → 0.1077;
  |t|=29: 0.0365 → 0.0750 — exactly the two anomalous strata). The conditional histogram is a
  **within-object** quantity, free at design time. (ii) **λ = a + δ, δ ∈ [0,2)**, so `a ≥ A` and
  `λ ≥ A` disagree at order 2/A; the four |t|=17 misses were **one event seen in four polynomials**.
- **My error bar was wrong in both directions.** Per-event p is heterogeneous (p = 1 on g = t), so
  variance is Σ_g n_g p_g(1−p_g), not N·p̄(1−p̄) — the pooled form deflates χ². Corrected, p = 1 branches
  have zero model variance and a single miss gives unbounded z. **Per-branch validation is the only
  honest form**, and every g < t branch agrees (p = 0.06–1.00, no pattern).
- **LICENSED:** verified over **|det| = 1…289 at ±12%**. |t| = 43's deciding branch holds **2 events on
  1 field**, so **above |det| ≈ 300 the formula is UNCALIBRATED — not contradicted, uncalibrated.**
- **Still standing:** the rate does not fall like 1/|Δ| because the g = |Δ| branch caps at 1.
- **Pre-registered or post-hoc:** **POST**. **Status:** CLOSED at the stated band.

### R-072 — the census was a fact about a coefficient box, and the witness count is far below it
- Frame was **monic, |A|,|B|,|C| ≤ 12**. Cyclic fraction by box: 7.438% (N=6), 3.007% (12), 0.945% (24),
  0.463% (40) — **measured log-log exponent −1.46** (I predicted −2; quote the measurement). Cyclic
  cubic **fields** have density zero (Davenport–Heilbronn vs the cyclic count), so **"97% of cubics are
  S₃" is a slot error**; the correct sentence names the box.
- **At N = 40, 184 distinct discriminants back 1196 polynomials.** This bit R-069/R-071 directly: the
  8-objects-per-stratum pooling was mostly **one field counted eight times**.
- **Pre-registered or post-hoc:** **POST**. **Status:** CLOSED — a correction, applied.

### R-073 — |t| ≡ 0 mod 3 is a SAMPLING ARTIFACT, and |t| is not a field invariant
- **Realizable as a Möbius map:** M = (0,1;−9,3), t = 3, det 9 = t², M³ = −27·I verified, order 3.
- **Realizable as a monic cubic:** the N = 26 search finds **|t| ∈ {3, 9, 15}**. The N = 12 census simply
  did not reach one. **My hypothesis that integrality excludes 3 | t is falsified.** No theorem.
- **Second construction, and it is the structural one:** the orbit invariant for that M gives
  27x³ − 9x + 1 at s = 0, whose roots are **α/3 for α a root of y³ − 3y + 1** — the Shanks t = 1 cubic.
  **The same field carries t = 1 on its algebraic integers and t = 3 on their thirds.** |t| is a
  GL₂(ℤ)-invariant of the **object**, not of the field; x ↦ x/3 is not in GL₂(ℤ).
- **Pre-registered or post-hoc:** **POST**. **Status:** CLOSED.

### R-074 — the floor DOES transfer from cyclic to S₃, and the check was powered
- The floor depends on **events per unit u** and nothing else. 24 objects/stratum, **distinct
  discriminants**, λ ≥ 20: A **0.06119 ± 0.00113**, B 0.05976 ± 0.00103, C 0.06023 ± 0.00103.
- **A vs B +0.94 sem, A vs C +0.63 sem; worst |z| over all four anchors and all pairs = 1.25.**
- **Powered:** the sem is **1.8% of the value**, so the test could have caught a **4% difference**.
- **NOT claimed:** that the strata are identical in every respect — only the one quantity the floor
  depends on. (All four A-vs-theory z's are positive, +1.24…+1.66; the strata agree with each other, so
  the transfer is unaffected. Looks like a shared finite-n bias; not chased.)
- **Pre-registered or post-hoc:** **POST**. **Status:** CLOSED — TRANSFER LICENSED.

### R-075 — axis 2 delivered: the joint (fraction × jitter) detection floor, multiplicity-corrected
- Synthetic Gauss–Kuzmin processes calibrated to R-074's anchors (0.0602 vs 0.06119 ± 0.00113 ev/unit u).
  **No target data touched; no real pairing computed anywhere.**
- **Detector (sealable verbatim):** S(w) = max over lag L of #{(i,j) : |u_i − v_j − L| ≤ w}, exact by
  sliding a 2w window over the sorted pairwise-difference multiset. Null: permutation over pairings.
- **The single-w floor is POST-HOC** — w chosen with hindsight. The sealable statistic fixes the ladder
  in advance: **T = min over a pre-registered w-ladder of the null-tail probability of S(w)**, T's null
  from the same permutation. 5% threshold is **T ≤ 0.0368**, not 0.05 — that gap is the multiplicity cost.
- **FLOOR (80% power, corrected):** f_min = **0.05** (J=0), **0.10** (J=0.05), **0.10** (J=0.2),
  **0.20** (J=1.0). Equal to the post-hoc row at this grid, so the multiplicity cost is **smaller than
  one step of the f-grid** — not zero, smaller than resolved.
- **The ladder arm occupies the J = 0 column and only that column**, at f = 1.00/0.48/0.21/0.12/0.08 for
  |det| = 1/4/25/169/841. Everything to the right is reachable only by injection.
- **Pre-registered or post-hoc:** **POST**. **Status:** CLOSED — R-066 and R-070 are now dischargeable.

### R-076 — Hilbert 90 was asserted as mechanism and evidenced as census; now proved elementarily
- **The defect:** "Hilbert 90 kills it: 0 of 162" states a theorem and evidences a census. Named
  mechanism, asserted capability — the arc's most-repeated shape.
- **Written out, no cohomology needed.** σ(M) = M in PGL₂(K) since both send α_{i+1} ↦ α_{i+2}. Lift:
  normalise M̃ by a nonzero entry so that entry is 1; σ(M̃′) has the same entry 1 and represents the same
  projective element, so the connecting scalar is 1 and σ(M̃′) = M̃′ entrywise. All entries lie in Q. ∎
  Hilbert 90 is now a **remark**, not the load-bearing step; the census is a **check**.
- **SLOT, and it is the point that matters:** **stratum A's cleanliness does not depend on any of this.**
  S₃ rests on α₂ ∉ ℚ(α₁), which stands alone. This governs only whether a **fourth stratum** exists, so
  the target's grade is unaffected either way. Separated so no later reader has the target inherit it.
- **Pre-registered or post-hoc:** **POST**. **Status:** CLOSED.

### R-077 — the rate formula's GRADE: it is CALIBRATED, not derived
- **R-071 fixed the number and left the grade behind.** `rate = Σ_g P(g)·min(1, g²/|Δ|)` was a
  prediction from structure. The correction replaces P(g) with **P(g | event), measured**, and the
  enrichment's mechanism is unstated. So the formula now carries an **empirical input of unknown
  mechanism** — and *that*, not a count of misses, is why it cannot extrapolate.
- **A route exists and is open.** An α₁-convergent in branch g maps to λ′ = (g²/Δ)λ, a convergent
  essentially iff λ′ ≳ 1, so the g = 1 branch should feed exactly α₂'s g′ = Δ branch:
  **P(g=Δ) ≈ P(g=1)·1.4427/Δ.** Measured pred/meas ratio across |det| = 4…841: **1.64, 1.67, 1.78,
  1.20, 2.02, 1.53, 1.80, 1.35, 1.81 — mean 1.65, range 1.20–2.02.** The **form holds over two orders
  of magnitude; the constant does not.** Closing it returns the formula to DERIVED and opens the range.
- **Status:** OPEN — and it is the one item whose resolution would change a stated limit.

### R-078 — field-level dedup holds the transfer license, and fixed two sampling defects of mine
- **Polynomial-discriminant dedup is not field dedup** (disc_poly = index²·disc_field). Implemented
  properly: PSLQ on (1, α, α², β) proposes, **exact reduction of f₂(g(x)) mod f₁(x) over ℚ disposes.**
  24 polynomials → **22 / 20 / 13** fields for A / B / C.
- **Two defects found while doing it, both mine.** (i) A raw triple loop returned every object sharing
  the smallest A — a **thin coefficient slice**, the same sampling-frame error gate 0f was about. Fixed
  by enumerating in order of increasing height. (ii) The theory reference for P(λ ≥ A) was the
  **Gauss–Kuzmin a-tail log₂(1+1/A)** where the **λ-tail 1/(A ln 2)** belongs — the same a-versus-λ
  convention slip, one table over.
- **Together those two manufactured the "+1.2 to +1.7 sem common offset" I had filed as a shared
  finite-n estimator bias. It was neither.** Corrected, all four anchors sit within ~1 sem of theory.
- **License, restated at field level:** events per unit u agrees across all three strata to
  **|z| ≤ 0.16**; sem = **1.6%** of value, so a **3% difference was detectable**. TRANSFER LICENSED.
- **Status:** CLOSED.

### R-079 — two numbers quoted past their resolution
- **T threshold:** 0.0368 came from **400** permutation draws. At **2000** draws it is
  **0.0235 ± 0.0075** (bootstrap 95% CI [0.0205, 0.0470], and T is discrete in steps of 1/N so the
  percentile is lumpy). The third figure was not real, and the value moved by 1.8 bootstrap sd.
- **Census exponent −1.46:** four points over **0.8 decades**. This arc's entire preceding program was
  about what a short lever arm does to a fitted exponent. **File the DIRECTION** — the cyclic fraction
  falls with box size, and cyclic cubic fields have density zero — **not the digits.**
- **Status:** CLOSED — both restated.

### R-080 — the deliverable is an UPPER LIMIT, named before the run
- **No predicted effect size exists on the target arm and none can — that is what makes it the target.**
  So this phase is an upper-limit measurement **by construction**, and its likely product is a bound.
- **Named now so it cannot be written up later as a non-finding:** *"Totally real S₃ cubic conjugates
  show no coincidence of exceptional approximations above f = 0.05 at zero jitter (0.10 at J ≤ 0.2,
  0.20 at J = 1.0), with the floor demonstrated by injection rather than argued, on the
  between-object axis."*
- **Grade of that sentence:** empirical bound against a permutation null. No analytic bracket exists in
  this region and none is claimed.
- **Status:** OPEN — this is what the design produces.

### R-081 — SEALED. `seals/CUBIC_ARM_SEAL.json`, arms hash `c2be21bf2a2ef4dd`
- Ten frozen fields, not five: **A = 20**; **event = λ ≥ A, not a ≥ A**; **u = log q**; the statistic;
  the **w-ladder {0.02, 0.05, 0.2, 1.0}**; **2000 permutations**; **T ≤ 0.0235**; the **stratum
  assignment rule with the object lists frozen** (computable ⇒ tunable); the **field-dedup rule**; the
  **injection jitter family Uniform(−J,J)**, with the caveat that **the floor is a floor for that
  family** and a heavy-tailed jitter has a different one — irreducible, since the target's jitter shape
  is unknown by construction, so it is *stated* rather than discovered.
- **Failure condition written FIRST**, separating instrument failure from an empty target: stratum B
  not returning 1.00, stratum C off the calibrated formula by >±12% at |det| ≤ 289, null false-positive
  rate >10%, or fewer than 20 fields surviving dedup ⇒ **the target result means nothing**.
- **The negative arm IS the permutation null**, stated so it is not counted as a second witness.
- **The quadratic/Galois positive arm is RETIRED**: stratum B supersedes it — derived here rather than
  `LIT`, and on the target's own substrate. Quadratics have **periodic** CFs, which is not the target's
  regime, so that arm would have certified the instrument on the wrong data.
- **Status:** SEALED. No arm has been run.

### R-082 — stratum B is a SMOKE TEST, not a ceiling, and its hard-halt would have FALSE-FIRED
- **The regrade.** |Δ| = 1 is Serret equivalence: the two CFs are **identical** from some index n₀. So
  the λ-events are literally the same events with log q offset by a constant, and the detector's task
  on B is *"find the shift aligning two identical sequences."* That confirms the code runs and the
  coordinate convention is right — **almost nothing about resolving two DISTINCT coincident processes.
  Stratum C carries the calibration.**
- **The false-fire, measured.** n₀ across the 24 frozen B fields: **min 2, median 3, max 3**. f over the
  full range = (n−n₀)/n, and **6 of 24 fields return f_full < 1.00** (min **0.9846**). The sealed
  condition "B must return 1.00" would have **halted on a derivable finite-depth transient**, voiding a
  target result for an instrument reason that is not an instrument defect.
- **Amended** (`CUBIC_ARM_SEAL_ADDENDUM_1.json`): **f_full(B) ≥ 0.965**, set from the measured
  distribution rather than from the number 1.00 — **plus** the sharper clause that on the **post-merge**
  segment (index ≥ n₀) f must be **1.000 exactly**. The first clause loosens a hard halt and is
  flagged as such; the second tightens. A false-firing test replaced by a correct one plus a stricter one.
- **Pre-registered or post-hoc:** amendment before any arm ran, no target data seen. **Status:** CLOSED.

### R-083 — P(λ ≥ A) = 1/(A ln 2) is EXACT, and the a-vs-λ slip was worse than a slot error
- Under the Gauss natural extension (density 1/(log2 (1+xy)²), λ = 1/x + y), the condition λ ≥ A is
  x ≤ 1/(A−y) and the inner integral **collapses**: ∫₀^X dx/(1+xy)² = X/(1+Xy) = **1/A, independent of
  y**. So P(λ ≥ A) = **1/(A ln 2) exactly, for all A ≥ 2** — no asymptotic correction at any A.
- **Verified:** normalisation 1.000000000000; numeric vs exact at A = 2, 3, 5, 20, 100 to **2.2e−16**.
- **Consequence:** the anchor reference carries **zero uncertainty**, so R-078's 1.6% sem is the *entire*
  error budget on that comparison. The transfer licence is cleaner than it was stated at seal time.
- **And the slip:** log₂(1+1/A) is the approximate-**looking** form that is exact **for a**; 1/(A ln2) is
  the exact form **for λ**. Using the first where the second belongs swapped an exact reference for one
  exact only in the wrong variable. **Status:** CLOSED.

### R-084 — R-077 grade change: the MARGINAL P(g) is DERIVED; the conditional is not
- **g divides Δ, so g = gcd(ap+bq, cp+dq, Δ) — a function of (p,q) mod Δ alone.** The residues
  equidistribute over {(p,q) mod Δ : gcd(p,q,Δ)=1}, so **P(g) is a finite COUNT**. Verified:
  count-weighted **χ² = 11.7 on 12 df, p = 0.473**, over 18 branches, 6 objects, |det| = 4, 25, 169.
- **This kills my own earlier route.** P(g=Δ) ≈ P(g=1)·1.4427/Δ was simply the wrong formula: at
  |det| = 4 the count gives **P(g=4) = 1/6 exactly** against the heuristic's 0.2405. **The 1.65 factor
  was chasing an error of mine, not a missing mechanism.**
- **The proposed closure fails on SIGN.** Preimage-less α₂ convergents inflating the g=Δ branch would
  drive pred/meas **below** 1; observed is **1.65 > 1**, the prediction overshoots. Not the explanation.
- **Still not derived:** the formula needs **P(g | event)**, and the residue class and λ are correlated
  through **y_n = q_{n−1}/q_n**, which enters both. So R-077 moves from *"an empirical input of unknown
  mechanism"* to *"one identified correlation in a skew product whose marginal is derived."*
  **A grade change, not a closure.** The formula stays CALIBRATED, |det| ≤ 289 at ±12%, range unopened.
- **Status:** OPEN, better localised.

### R-085 — the retired quadratic arm would have mis-fired for a SECOND, independent reason
- At seal time it was retired because quadratics have **periodic** CFs — the wrong regime.
- **The second reason is sharper.** Galois relates a quadratic irrational's CF to its conjugate's by
  **period reversal**. The sealed statistic maximises over **lag** — a *translation*. **A reversal is
  not a translation**, so the estimator could not have read the relation the theorem supplies, and the
  arm would have returned null **while the theorem held**: a false FAIL on a known-answer control.
- **The lesson, and it generalises:** *a positive control taken from a theorem must be checked against
  the ESTIMATOR, not only against the substrate — verify the statistic can read the relation the
  theorem supplies.* Adjacent to but distinct from "a property of a map on a finite set is not a
  property of the formula you write for it."
- **No design change** — the arm is already retired. Recorded so the retirement is not later reversed
  for the wrong reason. **Status:** CLOSED.

### R-086 — seal integrity verified; transport corruption did NOT reach the artifact
- Seal re-read from git object `5027213:arsrh/seals/CUBIC_ARM_SEAL.json`; **arms hash recomputed
  `c2be21bf2a2ef4dd`, MATCHES**; JSON parses clean at 9022 chars; all ten frozen fields present; working
  tree clean. **Third observed occurrence of conversation-transport corruption, and the first to land on
  text that is itself the reference — it did not reach the committed file.**
- **Standing rule this makes explicit:** the seal is verified from the git object and its hash, never
  from quoted prose. **Status:** CLOSED.

### R-087 — RUN COMPLETE. Target empty; the deliverable is the sealed upper limit
- **All four instrument checks passed** — I1 24/24 fields and 3322/3322 post-merge events; I2 worst
  |ratio−1| = **0.098** against a 0.12 tolerance over 23 fields at |det| ∈ {4,9,25,169}; I3 false-
  positive rate **5.7%**; I4 counts 24/24/23. **That is what makes the negative a result.**
- **Target:** per-field **1/24** detections against 1.2 expected; per-pair **2/72** against 3.6;
  binomial **p = 0.708**. Detections sit at or below expectation on both accountings.
- **The stated limit:** *totally real S₃ cubic conjugates show no coincidence of exceptional
  approximations above **f = 0.05** at zero jitter (0.10 at J ≤ 0.2, 0.20 at J = 1.0), per conjugate
  pair.* Floor **demonstrated by injection**, and a floor **for the sealed jitter family**.
- **Pre-registered:** yes — this sentence is R-080, written before any arm ran.
- **NOT claimed:** nothing about boundedness (§0); not a second witness from the 72 pairs, which live
  on 24 fields; not the stronger aggregate bound, which was not sealed.
- **Nice check, unearned but real:** the live permutation null's 5th percentile came out **0.0225**
  against **0.0235** sealed from synthetics — 4% agreement between a pre-registered calibration and
  the real null. **Status:** CLOSED.

### R-088 — the seal HALTED the run, on the clause the addendum had just tightened
- **The first execution failed I1 and exited before the target block.** 2 of 24 stratum-B fields
  missed post-merge exactness — the *sharper* clause added in Addendum 1, not the loosened one.
- **Diagnosis: my check, not the transfer.** Events at index 1953/1954 with Serret partners at
  1955/1956, one and two past the `len(a1) − 45` guard. **Two objects compared without intersecting
  their valid domains** — the same defect class as the thin coefficient slice, the a-vs-λ threshold,
  and the polynomial-vs-field dedup. Fourth instance this phase.
- **Addendum 2 changes the DOMAIN, not the TOLERANCE** (still exactly 1.000). After the fix: **zero**
  real misses, 3322/3322.
- **This is the highest-risk amendment class** — a hard-halt check edited after it fired. Recorded with
  its guards: no target data existed at halt (the script exits first); the tolerance was untouched; the
  fix follows a correctness principle that applies regardless of outcome; and one surviving genuine
  miss would have meant instrument failure, not another amendment.
- **The seal earned its keep here.** A protocol that had not written the failure condition first would
  have run the target, gotten p = 0.708, and never learned the check was broken.
- **Status:** CLOSED.

### R-089 — the limit's edge-effect control
- The lag scan needs overlapping u-range. Within-field pairs **2262.8** vs cross-field null pairs
  **2255.4** — **+0.33%, 1.78 sem**. Real and null pairs draw on the same domain, so the negative is
  not an artifact of reduced overlap, and the (insignificant) difference points toward *more*
  detectability, not less.
- **Why it mattered:** an unchecked overlap deficit would have weakened the *limit* while leaving the
  *null* intact — a defect that only shows up on the number being reported, not on the verdict.
- **Status:** CLOSED.

### R-090 — the target comparison had the SAME domain defect, and removing it moves nothing
- The amendment in Addendum 2 was confined to the I1 block: `events()` and the target statistic were
  untouched, so the sealed target number is not a function of that fix. **But the reviewer's underlying
  point is correct and stronger:** the target statistic compares two objects over **unintersected
  certified domains** as well, and I bounded that empirically (+0.33%, 1.78 sem) rather than removing it.
- **POST-HOC robustness check, labelled as such because the answer was already known.** Restricting both
  event sets to their common u-range, for real pairs and null pairs alike:
  sealed **2/72 pairs, 1/24 fields, p = 0.708**; domain-intersected **2/72, 1/24, p = 0.708**.
  Per-pair threshold moves 0.0225 → 0.0250; field threshold unchanged at 0.0100.
- **This is a second instance of R-088's headline inside the same run:** the defect was present, and
  removing it changed nothing, so **nothing in the result would have looked wrong.** The empirical
  +0.33% bound was not load-bearing — but that was not knowable in advance.
- **Status:** CLOSED. The sealed statistic remains the result; this is a sensitivity check, not a
  restatement.

### R-091 — the field-level expectation, with its definition attached
- **1.2 is right, and only under its definition.** The statistic is **T_field = min over the field's 3
  conjugate pairs**, compared against the null distribution **of min-of-3 from permuted triples**, with
  the threshold at that null's 5th percentile. So **P(detect | H₀) = 0.05 by construction** — one
  calibrated test per field, multiplicity already inside the statistic — and 24 × 0.05 = **1.2**.
- **24(1 − 0.95³) = 3.4 is the ANY-PAIR-FIRES reading**, a different statistic that was not computed.
- Observed **1/24**. Null under either convention, so the conclusion is robust; **the number needed its
  definition attached, and now carries it.** **Status:** CLOSED.

### R-092 — THE UNIFICATION: nine failures, one defect, one mechanical check
- Across four programs, Will's and mine in roughly equal share: **component vs fit parameter; local vs
  cumulative form; two denominators; unweighted mean vs weighted whole; a-tail vs λ-threshold (twice);
  polynomial units vs field units; smoothed proxy vs integer count; p_fit vs polynomial order;
  mismatched certified domains.** Nine instances of **the two sides of a comparison not being
  commensurable.**
- **THE CHECK:** *before comparing two numbers, verify both sides are the same **quantity**, in the same
  **units**, over the same **domain**, at the same **unit of analysis**.* Four clauses because each of
  the nine fails a different one. Not generic correct-fact/wrong-slot — the **comparison-specific** face
  of it, and unlike slot discipline it is a ten-second checklist.
- **And the design lesson that came with it (R-088, R-090):** the domain bug changed **no** answer —
  p = 0.708 either way, verified. **A design that only catches defects when they change the answer
  catches nothing here.** A pre-written condition on an *instrument* arm caught it when it didn't.
  That is the argument for writing the failure condition first, and it is stronger than "the seal worked."
- **Status:** BANKED — memory `commensurability_check.md`. The arc's one durable finding about process.

### R-093 — CLIP SCOUT (the decidable half of the fork): mass03 is immune, I_rep is REACHED
- **mass03: UNREACHABLE.** `arithmetic_toolkit.py:116`, `mass03 = float((spacings < 0.3).mean())`,
  computed in `_classify` from unfolded spacings. It never touches `pair_correlation_full`. Fungal's
  mass03 claim cannot be reached by this bug. **Closed, and it was the larger of the two exposures.**
- **The clip, located:** `arithmetic_toolkit.py:504`,
  `I_rep = np.trapezoid(np.maximum(0, 1 - R2[mask]), r[mask])` — the clip is on the **integrand**, not
  the integral, three lines below a docstring that says *"negative → clustering."*
- **I_rep: REACHED, in two ways the dormancy argument does not cover, because it is stated on the
  wrong side of the comparison.** Dormancy cites where the *null* sits; the claim rests on where the
  *observation* sits, and the clip acts differently on the two.
  - **(a) SATURATION, observed side.** Constructed confound, Neyman–Scott bursts: true I_rep
    **−0.51, −0.84, −1.56, −2.98** all read **exactly 0.00000** clipped. Real fungal (194/194 BL rows)
    and real solar (`observed_irep_recon = 0.0`) both sit at that saturated value. **Direction
    survives; magnitude does not, and fungal and solar are indistinguishable on this axis.**
  - **(b) RECTIFICATION, null side.** Poisson with true I_rep = 0.000 reads **+0.020** clipped — the
    clip converts symmetric noise into a positive mean. On the *actual* fungal null (12 draws of the
    corrected construction): clipped **+0.0517 ± 0.0124** (4.2 sd from zero) vs true
    **+0.0338 ± 0.0289** (1.2 sd). **35% of the quoted margin is bias, and the clip also compresses
    the sd 2.3× by truncating the lower tail.** The "far from the boundary" that licenses dormancy is
    measured on the biased, variance-compressed version of the statistic; unclipped, the null is 1.2 sd
    from zero.
- **NOT claimed:** not that fungal or solar are unclustered. The direction (real below null) survives
  both effects. What does not survive is the *margin*, the *degree*, and the dormancy argument itself.
- **And it is the commensurability defect again, in its subtlest form yet:** the observed side carries
  bias 0 (saturated) and the null side carries bias +0.018 (rectified) — **the same statistic name with
  different estimator behaviour on the two sides of the comparison.** Clause 1, failing invisibly.
- **The fix is one line** (drop `np.maximum(0, ·)`), after which I_rep is graded and signed. Whether to
  run it, and what it does to the fungal/solar claims, is the fork and is Will's call.
- **Pre-registered or post-hoc:** **POST** — a scout, not a gate. **Status:** OPEN, and now decidable
  without judgment as intended: the answer is **yes, it reaches I_rep; no, it does not reach mass03.**

### R-094 — CLIP FIXED (non-destructively), and the hidden number is −2.21
- **My scout computed one side.** I filed "observed side carries bias 0, null side +0.018." **Wrong,
  and the error was the interesting one:** the observed side carries **saturation**, which is the
  *larger* bias and points the *other* way. Clause 1 of the commensurability check fails on **both
  sides, in opposite directions, at different magnitudes.**
- **Sign was NOT certain, and the threshold is computable.** Unclipped z exceeds clipped z only if the
  true observed value is below **−0.0867**; between there and 0 the fix *weakens* the claim.
- **Measured, on the real data (18 CSVs re-detected, 1470 pooled intervals):**
  **I_rep clipped = +0.00000, signed = −2.21224.** Twenty-five times past the crossover.
  clipped: null +0.05170 ± 0.01293, observed +0.00000, **z = 4.00**.
  signed: null +0.03376 ± 0.03021, observed **−2.21224**, **z = 74.33**.
- **So the fix STRENGTHENS fungal's I_rep claim**, which inverts how the fork read. Direction was
  Will's call; the crossover arithmetic says it was conditional on a magnitude met by 25×.
- **Fixed non-destructively.** `repulsion_integral` retained **bit-identical** (regression-checked:
  Poisson +0.02025 before and after) because **62 files / 212 references** consume it; the new
  `repulsion_integral_signed` is the statistic the docstring always described. Not a one-line change
  in effect — a one-line change plus a deprecation surface.
- **AND THE FIX IS NOT FREE, exactly as predicted.** z = 74 is uninformative. The live quantity is now
  the **magnitude I_rep = −2.21, which has no bracket at all** — a single realization with no error
  bar, against a null that only bounds the *null's* spread. Same earned-existence / unearned-magnitude
  split as solar. **New open item: I_rep magnitude needs its own null and its own gate.**
- **Status:** CLOSED as a bug; OPEN as a measurement.

### R-095 — mass03's real exposure is unfolding, and it is now SIZED
- Clip-unreachability (R-093) **does not discharge mass03's audit debt.** `(spacings < 0.3).mean()` is a
  **fixed threshold** on unfolded spacings; ⟨r̃⟩ is a **ratio** and therefore affine-invariant. A fixed
  threshold moves when the normalisation moves.
- **Verified and quantified** on the real fungal pool: sweeping a multiplicative normalisation error c,
  **r̃ deltas are identically 0.0000** at every c, while mass03 runs 0.6099 → 0.6909 over c ∈ [0.80, 1.25].
  **d(mass03)/dc = +0.34** at c = 1, so a 10% error moves mass03 by **0.034**.
- **Bound:** solar's quotable floor is **0.20** in mass03, so a *global* rescale would need **~59%** to
  consume it. That bounds the **global** channel only — **local, density-dependent unfolding error is
  not tested by this sweep and remains open.**
- **Scope:** solar's quotable claim is mass03 + p99-exceedance with "no z quotable"; I_rep appears only
  as a descriptive line about the deployed detector. **So solar's exposure is this route and not R-093's**,
  and the saturation finding does not touch it.
- **And a consequence worth stating:** any cross-substrate comparison ever made **on I_rep** is void —
  both fungal and solar read the same saturated 0.000, so the axis carried no information to compare on.
- **Status:** OPEN, sized on the global channel, untested on the local one. The larger of the two claims.

### R-096 — fungal I_rep inherits solar's footing; z = 74 is retracted as external
- **z = 74 is not quotable, and "uninformative" undersells it.** The null has 12 draws, so the sampled
  range is a few sd wide; 74 sd extrapolates Gaussianity **~25× beyond anything the simulation visited.**
- **Inherit solar's convention rather than invent one:** *existence on outside-the-null-range footing,
  no z quoted externally, magnitude as the live quantity.* Observed (−2.21) lies outside the entire
  null range (+0.034 ± 0.030, 12 draws) — **existence unassailable, significance not quantified.**
- **Crossover corrected to Will's value:** −0.0870, not my −0.0867. The ddof=1 sds (0.01293, 0.03021)
  are the right inputs; I used pre-final ones. Conclusion unchanged (observed is 25× past it).
- **Status:** CLOSED as existence; the magnitude is R-097.

### R-097 — the magnitude bracket existed already: estimator certified against an ANALYTIC target
- The scout's Neyman–Scott anchors have a **closed-form** I_rep. Parents unit-rate Poisson, k points per
  parent dispersed N(0,s²), spacings normalised to unit mean ⇒ g(r) = 1 + ((k−1)/k)·h(r) with h the
  N(0,2s²) density, and rescaling by the intensity k gives
  **I_rep = −((k−1)/2)·erf(1/(2ks))**.
- **Measured recovery of that known value, 6 configurations spanning −0.57 to −3.23:**
  at n = 64k, **0.903 ± 0.006**; at fungal's own n = 1470, **0.892 ± 0.017**. The estimator
  under-recovers by a **stable multiplicative factor**, not by noise.
- **Bias-corrected fungal estimate: I_rep ≈ −2.48** (−2.212 / 0.892).
- **SLOT, kept separate as instructed:** this brackets **the estimator on known inputs**. It does
  **not** bracket fungal's true value — that holds only to the extent the Neyman–Scott family is
  representative of fungal, **which is not established.** Grade change from *no bracket* to
  *estimator certified on a known family, interpretation open*, at zero new cost.
- **Status:** CLOSED for the estimator; OPEN for the interpretation.

### R-098 — the deprecation surface was the fix's own inert-pass risk; both remedies applied
- **The risk, correctly named:** two live fields with near-identical names, one biased in a way that
  does not announce itself, and **the default action at every call site is to do nothing.** The
  verify-harness precedent inverted — retiring a check needed the scrutiny that adding one did, so
  keeping a superseded field does too.
- **Remedy 1: it now announces itself.** `pair_correlation_full` returns a dict subclass that raises a
  `DeprecationWarning` on read of `repulsion_integral`, via **both** `__getitem__` and `.get` (verified:
  2 warnings, signed field silent).
- **Remedy 2: triage, with both counts recorded. And my earlier "212 references" was WRONG — the
  real count is 399** (my pattern was narrower than the field's actual usage):
  **NEEDS-SIGNED 154 (39%)** — thresholding, correlating, or ordering on the clipped value;
  **UNCLASSIFIED 185 (46%)** — need a human read; **clipped-fine 56 (14%)**; already-signed 4.
- **So the fix is applied at 4 sites out of 399.** "The fix exists and isn't applied" was the right
  worry and the number is now on the record. **Status:** OPEN — 154 known + 185 unknown sites.

### R-099 — "void" was the wrong status, and one live candidate exists
- Correct status: **void pending recompute, not terminal** — signed values are real numbers on both
  sides now, so the comparisons can be *redone*, not merely discarded.
- **And "any comparison ever made" implied some were, so I grepped.** One live candidate, in
  `cross_substrate/INSTRUMENT_CONFOUND_FINDINGS.md`: *"ρ(rep_int, ks_gue) is tightly coupled on
  arithmetic (zeta −0.93, primes −0.99) but ~0 on Allen V1 — rep_int carries a DIFFERENT marginal
  feature there."* **The same document states Allen V1 is super-Poisson/clustered.** Clustered ⇒
  rep_int saturates ⇒ near-zero variance ⇒ **ρ → 0 mechanically.** The stated explanation is exactly
  what the artifact predicts.
- **Not retracted on suspicion:** the underlying arrays are not banked (0 stored rep_int arrays in
  `cross_substrate/`), so this is **unresolvable from artifacts and needs recompute.**
- **Status:** OPEN — one identified candidate, one recompute to settle it.

### R-100 — mass03's local channel is OPEN-BOUNDABLE, not terminal
- The standing move (check the unfold against an exact counting function) is unavailable — fungal has
  no exact counting function. **But the separability transfer FAILS, and that is what decides it.**
  Separability bites when remainder and signal **share a band**; a slowly-varying normalisation error
  c(x) is **low-frequency** while mass03 reads the **high-frequency** spacing shape. Different bands.
- **Structure:** mass03_obs = E_x[m(c(x))] ≈ m(1) + m′(1)·E[c−1] + ½m″(1)·Var[c]. The first-order term
  is the **global channel already bounded**; for an unbiased normalisation it **vanishes**, leaving a
  **second-order** term. Measured m″(1) ≈ −1.70.
- **Measured, block-varying c with E[c] = 1:** shift −0.0020 (sd 0.05), −0.0082 (0.10), −0.0048 (0.20),
  −0.0191 (0.30); the 2nd-order prediction tracks at small sd and **over**-predicts at large, i.e. it is
  conservative. **A 30% local normalisation error moves mass03 by ≤ 0.02 — an order of magnitude below
  solar's 0.20 floor.**
- **Caveat on my own derivative:** the finite-difference m′(1) is noisy on 1470 discrete spacings
  (+0.34 at h = 0.01, +0.22 at h = 0.02). The analytic form **0.3·f(0.3) ≈ 0.34** is the right value and
  it is Will's independent check that carries it, not my difference quotient.
- **Status:** OPEN-BOUNDABLE. Not terminal, and the bound is small.

### R-101 — the local-channel bound was four single draws; replicated, and three of my numbers were wrong
- **The non-monotonicity was the tell.** −0.0020, −0.0082, −0.0048, −0.0191 — a second-order term scales
  as sd², which is monotone, so the third point was realization noise comparable to the effect.
  **"≤0.02" was a max of four unreplicated draws, not a bound.**
- **Replicated, 40 draws per sd, quoted as quantiles** (mean / 5th / 95th / |max|):
  sd 0.05 → −0.0017 / −0.0048 / +0.0020 / 0.0068; 0.10 → −0.0027 / −0.0082 / +0.0014 / 0.0102;
  0.20 → −0.0088 / −0.0191 / +0.0007 / 0.0252; 0.30 → −0.0172 / −0.0328 / −0.0033 / 0.0368.
- **m″ now analytic, no difference quotient.** m(c) = F(0.3c) ⇒ **m′(1) = 0.3·f(0.3)**,
  **m″(1) = 0.09·f′(0.3)**. Estimating the density by local linear fit on [0.10, 0.60]:
  f(0.3) = 0.844, f′(0.3) = −3.39 ⇒ **m′ ≈ 0.25, m″ ≈ −0.305**. The free sign check passes: fungal is
  clustered ⇒ f′(0.3) < 0 ⇒ m″ < 0, and all measured shifts are negative.
- **THREE of my own estimates were wrong, in both directions.** A Gaussian KDE (boundary-biased on data
  spiked at 0) gave m″ = −0.009, under by 30×; the finite difference gave −1.70, over by 5×. The local
  linear fit at −0.305 reproduces the measured shifts to ~1.5×. **And m′ ≈ 0.25, not the 0.34 I quoted
  from a noisy difference — so consuming solar's 0.20 floor needs an ~80% global rescale, not 59%.**
- **Status:** CLOSED — bound now replicated and quantile-quoted.

### R-102 — the measured c-variation, and a transfer slip of mine caught before it was committed
- **Measured on fungal's pooled process** (29 blocks of 50): sd(block means) = 0.3521 against an iid
  floor of 0.3801 — **observed is BELOW the floor, so the point estimate of real normalisation
  variation is ZERO.**
- **But 29 blocks is few, so the honest form is an upper limit: sd(c) ≤ 0.246 at 95%.** At that limit
  the replicated sweep gives a mass03 shift of roughly −0.012 mean with a 95th-percentile magnitude
  near 0.03 — against solar's 0.20 floor, a factor ~7 margin, not the order of magnitude I claimed.
- **⚠ AND THE SLIP:** this c-variation is measured on **fungal**, and I was about to use it to bound
  **solar's** floor. Different substrate — that is clause 1/3 of the commensurability check, caught
  before filing. **Solar's own block-to-block variation has NOT been measured, and the local channel
  for solar is therefore still unbounded by measurement.**
- **Status:** OPEN for solar; bounded for fungal.

### R-103 — recovery is a function of I_rep alone, not of k, at this power
- My ±0.006 **was** the across-configuration spread, so the question was closed in the right direction —
  **but k and |I_rep| were correlated across those six configurations**, so the degeneracy stood.
- **Discriminating test, Will's:** solve s from −((k−1)/2)·erf(1/(2ks)) = target, giving matched I_rep at
  very different k. At target −1.5, k = 5/8/16/32: recovery 0.899, 0.924, 0.847, 0.876,
  **χ² = 4.02 on 3 df, p = 0.259.** At target −0.8: 0.863, 0.933, 0.925, 0.927,
  **χ² = 5.70 on 3 df, p = 0.127.** **No k-dependence at a 6.4× range in k.**
- **Pooled recovery 0.899 ± 0.033.** So the correction is a function of I_rep alone and transfers beyond
  this family — at this power. **Fungal bias-corrected: I_rep = −2.46 ± 0.09** from the calibration
  spread alone (other sources not included).
- **The defensible fallback remains available and is weaker but assumption-free:** |true I_rep| ≥ 2.21,
  since the estimator under-recovers in every configuration tested.
- **Status:** CLOSED at this power — recovery is I_rep-only, and −2.46 ± 0.09 is supportable.

### R-104 — SECOND clause-1/3 instance in the same computation, and it was the half still pointing at solar
- I caught that **fungal's block variation** cannot bound solar. I did **not** catch that
  **f(0.3) = 0.844 and f′(0.3) = −3.39 are fungal's density derivatives** — and I used them to size
  **solar's** 0.20 floor. Same clause, same computation, twice.
- **Solar's own coefficients, measured** (n = 1999, its own pooled process): mass03 **0.5968** (vs
  fungal's 0.6549), **f(0.3) = 0.995**, **f′(0.3) = −3.33** ⇒ **m′ = 0.2985, m″ = −0.2999**.
  ⇒ consuming solar's floor needs a **67% global rescale**, not the 79% fungal implies, nor the 59%
  from the circular 0.34, nor my 80%.
- **The coefficients do not track between substrates**, as Will predicted: f(0.3) differs by 18%.
- **Provenance note, Will's own:** the 0.34 that carried the sizing for a full cycle was **circular** —
  "0.3·f(0.3) ≈ 0.34 recovers your derivative" was written without computing f(0.3), so my noisy
  difference quotient was dressed as independent analytic agreement. **Flagged retrospectively as
  unverified arithmetic.** First genuinely independent value is the local-linear-fit f(0.3).
- **Status:** CLOSED — each substrate now sized on its own density.

### R-105 — solar's local channel is bounded by CANCELLATION, not by smallness
- **Solar's block-to-block variation is enormous and real:** sd(block means) **1.5806** vs iid floor
  **0.6105** — **+13.85 sampling sd**, excess **sd(c) = 1.458**. (Fungal's, by contrast, is −0.55
  sampling sd, i.e. noise — as Will noted, nothing to read in observed-below-floor.) The solar cycle is
  presumably the source, given the ~1000× envelope.
- **So the fungal-style argument fails for solar** — sd(c) ≈ 1.46 is far outside any regime where a
  second-order bound holds.
- **But the null is rate-envelope-preserving by construction, so the channel largely CANCELS.**
  Measured: cycle-preserving null excess sd(c) = **1.3948 ± 0.0388** (8 draws) against the observed
  **1.4579** — a difference of **+0.063, or +1.6 null sd**, consistent with zero.
- Propagating that residual through solar's own m″ gives ≈ **−0.027 in mass03, ~13% of the 0.20
  floor** — and itself consistent with zero. **Order-of-magnitude only:** the second-order expansion is
  invalid at sd(c) ≈ 1.4, so this is an estimate, not a bound.
- **Status:** CLOSED-BY-CANCELLATION, with the residual estimate flagged as non-rigorous.

### R-106 — the three exact table coincidences are QUANTISATION, not common random numbers
- Will's hypothesis was a shared z-field across sd. **Ruled out by construction** — different seeds
  (5 vs 101), and each draw advances a single stream, so no field is reused.
- **Actual cause:** mass03 is a **count over 1469 spacings**, so shifts are multiples of **1/1469 =
  0.000681**. The three "coincidences" are the **same integer count**: −7, −12, −28. Old sd = 0.20 and
  new 5th-pct at 0.05 both equal −7/1469; old 0.10 and new 0.10 both −12/1469; old 0.30 and new 0.20
  both −28/1469.
- **Consequence for the sd = 0.246 interpolation:** columns are **independent** (good, the concern is
  discharged) — **but the statistic is coarse.** One count is 0.00068, so a 0.03 shift is only ~44
  counts, and quoted shifts below ~0.002 are within a few counts of zero.
- **Status:** CLOSED.

### R-107 — the family transfer, done on the KERNEL rather than on k
- Will: the k-sweep varied k with **N(0,s²) dispersal throughout**, so the one structural feature that
  could drive recovery was **held fixed in every configuration**. Correct.
- **Kernel-varied test:** matched I_rep = −1.2, **k = 6 fixed**, dispersal shape varied; scale solved
  per kernel from I_rep = −(k−1)·P(0 < X₁−X₂ < 1/k), computed by 4×10⁶-sample Monte Carlo.
  **gaussian 0.916, uniform 0.878, laplace 0.919, two-scale 0.909 — mean 0.906, spread 0.041**
  (sems ≈ 0.02, so ~2 sem).
- **Combined with the k-sweep (0.899 ± 0.033 over a 6.4× k-range), recovery ≈ 0.90 across BOTH
  structural axes.** That upgrades "transfers within Neyman–Scott" toward "transfers".
- **POWER, named as requested:** recovery vs log₂k has slope **−0.0169 ± 0.0137** per doubling,
  excluding |slope| > **0.027** at 95% — a total possible drift of **0.072** across the k-range,
  **comparable to the 0.101 correction itself.** So "no k-dependence" means *none larger than roughly
  the size of the correction*, not none.
- **And the fallback's true grade:** |true I_rep| ≥ 2.21 rests on under-recovery holding in **every
  configuration tested**, which is the same family conditioning one level weaker — **nearly
  assumption-free, not quite.** Will's wording, adopted.
- **Status:** CLOSED at the stated power.

### R-108 — the expansion was used where the EXACT form is free, and once provably invalid
- **m(c) = F(0.3c) is exact.** No Taylor, no validity question. My 67%/79% used the **linear term only**,
  discarding the m″ I had just computed; adding it gives a quadratic that **maxes at 0.149 near x ≈ 1**,
  so a +0.20 shift reads "unreachable". **But F(0.3c) is a CDF — monotone in c, no maximum. The
  turning point IS the proof the expansion was being evaluated far outside its range.**
- **EXACT, by evaluating the empirical CDF at 0.3c:**
  **solar +0.20 needs c = 2.81 (+181%), −0.20 needs c = 0.45 (−55%)**;
  fungal +409% / −59%.
- **So every previous figure is superseded, and in both directions:** the circular 59%, my 80%,
  fungal-derived 79%, solar-linear 67%. Upward is much *harder* than linear said and downward much
  *easier* — the asymmetry the expansion could not represent. (Will's quadratic −53% ≈ exact −55%.)
- **Status:** CLOSED — exact form adopted, expansions retired from this computation.

### R-109 — solar's local channel, computed exactly instead of propagated
- Propagating sd(c) ≈ 1.4 through a second-order expansion was invalid for the same reason. Exact:
  impose positive (lognormal, E[c] = 1) block c-fields at the observed **1.4579** and the null's
  **1.3948** and difference the induced mass03, 400 draws each.
- **Channel contribution to observed-minus-null = −0.0060 ± 0.0023** — **3.0% of solar's 0.20 floor**,
  where the invalid propagation said −0.027 = 13%. **4.5× smaller.**
- The argument's structure was right — the rate-envelope-preserving null nets the channel out, leaving
  only the residual — **it was the propagation that had to go.**
- **Status:** CLOSED. Solar's local channel is bounded at 3% of the floor, exactly.

### R-110 — POWER RECONCILED, and the conclusion FLIPS: −2.46 is retracted
- **±0.0137 was a standard error (1 sem), not a 95% half-width.** I then quoted 1.96·se as if it were a
  bound on |slope|, which it is not — the bound is the far end of the CI around the point estimate.
- **95% CI = [−0.0438, +0.0100] ⇒ supported bound |slope| ≤ 0.0438**, not 0.027. Over
  log₂(32/5) = 2.68 doublings that is a drift of **0.117**, against a correction of **0.101**.
  **Drift > correction.**
- **THEREFORE: the k-sweep does NOT license applying the 0.899 recovery correction.**
  **R-103's "I_rep = −2.46 ± 0.09" is RETRACTED.** The defensible statement is the one Will named:
  **|true I_rep| ≥ 2.21**, resting only on under-recovery holding in every configuration tested.
- **This is the third time in this arc a conclusion turned on a sem-vs-CI conflation.** The rule:
  *a quoted ± is a standard error unless it says otherwise, and a bound on |θ| is the far end of the
  interval, not its half-width.*
- **Status:** CLOSED — the weaker claim is the supported one.

### R-111 — the compact-support hypothesis, tested and rejected
- Will: uniform's 0.878 was one-vs-three with a structural distinction — it was the **only compactly
  supported** kernel, and gaussian/laplace/two-scale are all unbounded. Testable with a second compact
  kernel.
- **Tested with three compact (uniform, triangular, arcsine) vs three unbounded, matched I_rep = −1.2,
  k = 6, 24 reps each:** compact mean recovery **0.8838**, unbounded **0.8914**,
  **difference −0.0076 ± 0.0145 = 0.52 sem.** Uniform itself came back at **0.894** with more reps.
- **NOT support-dependent**, and adequately powered for the purpose: it excludes a support effect larger
  than ~**0.029**, against a correction of 0.101. Kernel-independence stands.
- **Status:** CLOSED — uniform was scatter.

### R-112 — the two small ones, both Will's, both accepted
- **Quantisation is a loose end, not a defect.** Three exact integer matches are *possible* under
  quantisation but not *likely*; the load-bearing check is **independence-by-construction** (different
  seeds, single advancing stream), which holds. Recorded as such rather than as an explanation.
- **Granularity is inside the floor budget, not beside it.** mass03's binomial sem is **0.0124**
  (fungal, n = 1469) and **0.0110** (solar, n = 1999); solar's 0.20 floor is **16–18× sem**, and one
  count is 0.0005–0.0007. Confirmed inside, as asked.

### R-113 — the rule from R-110 violated ONE PARAGRAPH after banking it. FOURTH instance.
- Compact-support bound: difference 0.0076, sem 0.0145 (0.52 sem). **I quoted 1.96·se = 0.0284 ≈ 0.029
  as the excluded effect — the CI half-width again, not the bound.** Supported bound is the far end:
  **|0.0076| + 0.0284 = 0.036.**
- Conclusion unchanged (0.036 ≪ 0.101, still adequately powered) — **but the number was wrong by the
  exact defect filed one paragraph earlier, and that is worth more than the number.**
- **Fourth instance, not third.** Banking a rule and violating it in the same message is the strongest
  evidence yet that this one needs to be a mechanical check, not a remembered principle.
- **Status:** CLOSED, count corrected to 4.

### R-114 — the ±0.20 column applied SOLAR's floor to FUNGAL's row
- Fungal's margin is **mass03 0.6549 − null 0.2451 = 0.4098**, not 0.20. So my "+409%" answered a
  question fungal does not ask. Clause 1, in the **presentation** rather than the computation — the two
  rows were measured against different things while the table invited comparison.
- **Recomputed against each substrate's own margin:**
  **fungal (±0.4098): upward is genuinely UNREACHABLE** — 0.6549 + 0.4098 = 1.065 > 1, so no rescale can
  do it, a hard fact rather than an expansion artifact — **downward needs −87% (c = 0.13)**.
  **solar (±0.20): +181% (c = 2.81) / −55% (c = 0.45).**
- Conservative in direction (fungal's real requirement is *larger* than quoted), but wrong as presented.
- **Status:** CLOSED — each row now against its own margin.

### R-115 — solar's channel is a DETECTION, not a bound; refiled as measured
- **−0.0060 ± 0.0023 is 2.6 sem from zero.** "3.0% of the floor" reads as a ceiling; it is a **point
  estimate with an error bar that excludes zero** — a small, real bias, now *measured* rather than
  propagated. Better than a bound, and it should be filed as what it is.
- Does not threaten the claim at that size (3% of 0.20), and it supersedes the invalid −0.027.
- **Status:** CLOSED as MEASURED.

### R-116 — the void class widened, and the decaying bucket made to FAIL instead
- **Widened, per Will:** the void class is not "comparisons on I_rep" but **anything consuming
  rep_int's VARIANCE where it saturates** — correlations, percentile/rank comparisons, real-vs-surrogate
  tests, ordering. A saturated variable has near-zero variance, so every one of those is corrupted, not
  merely the explicit cross-substrate comparisons.
- **And the decay, addressed structurally.** Everything else on the board is a choice; an unclassified
  bucket with no assigned resolution **becomes permanent by default, because the default action is to
  do nothing.** So the default action is now a **failing check**:
  `arsrh/rep_int_migration.py` + `rep_int_migration_manifest.json`, which classifies every reference and
  **exits non-zero** while any remain open, with the manifest requiring a *reason* per resolution and an
  explicit warning against bulk-marking `fine` to clear it.
- **Current state: 399 sites — 4 migrated, 61 fine, 187 needs-signed, 147 unreviewed = 334 open.**
- **Status:** OPEN and now VISIBLE. The bucket can no longer decay silently; it fails until worked.

### R-117 — Will's own, recorded: the −53% was quoted from the invalid quadratic
- The turning-point argument (a CDF is monotone, a truncated quadratic has a maximum, therefore the
  expansion is outside its range) was **valid and decisive**. The **−53%** quoted in the same breath came
  from that same invalid quadratic; it landed within two points of the exact −55%, **which was luck at
  that range, not something established.**
- Filed because it is the same shape as R-104's circular 0.34: **a number carried along by an argument
  that had just been shown not to support it.**

### R-118 — the exit code had the ALARM-FATIGUE failure mode; replaced by a ratchet
- **The defect, Will's, and it is the SUPERSEDED lesson one level over.** 334 open sites means the
  check fails on **every run for as long as the backlog exists** — and a permanently-failing check gets
  **learned as noise**, at which point it is inert regardless of what it reports. Someone appends
  `|| true` in three weeks and the decay resumes *behind a green light*. **A permanently-red row is as
  inert as a missing one** — exactly the argument that put SUPERSEDED in the verify harness.
- **Fixed as a ratchet: fail on INCREASE.** High-water mark stored in the manifest, **moves DOWN only**;
  static backlog does not fire, regression does. Verified both ways: adding one new site on the
  deprecated field → **exit 1**; unchanged backlog → **exit 0**.
- **The two guards are complementary, not alternatives:** the manifest's warning against bulk-marking
  `fine` closes the *cheap* escape; the ratchet closes the *silent* one.
- **Status:** CLOSED — the check now fires only on what it exists to catch.

### R-119 — the split rate: "one line plus a deprecation surface" is a ~310-site migration
- **Triage moved; deployment did not.** 4 migrated in both passes. What changed was classification:
  **38 sites newly classified, 33 → needs-signed, 5 → fine — 87% toward needs-signed.**
- **Projecting the remaining 147 at that rate: ~315 of 399 need the signed field — roughly four in
  five.** That is the number that says the scope, and it belongs beside the counts.
- **Status:** OPEN, quantified.

### R-120 — fungal's global channel is TERMINAL, not bounded (different grade from solar's)
- mass03 is a **fraction**. Fungal's margin is 0.4098 and its mass03 is 0.6549, so the required upward
  shift needs F(0.3c) = 1.065 — **greater than 1, unreachable by ANY rescale, at any c.**
- **That is a closure of a different grade from solar's +181%:** solar's is "an implausibly large
  rescale would be required"; fungal's is "**no rescale exists**". Filed as TERMINAL rather than bounded.
- **Status:** CLOSED — terminal.

### R-121 — the commensurability check MECHANIZED, and it catches the arc's own failures
- **Will's argument, and my own evidence forced it:** *a rule violated one paragraph after banking is
  the strongest evidence it cannot live as a remembered principle.* `commensurability_check.md` was in
  **exactly the state the sem/CI rule was in when it failed a fourth time** — a memory file requiring
  someone to remember to consult it, **with ten instances behind it**. The sem/CI rule got mechanized
  after four. This one had ten.
- **`commensurable.py`:** a `Measurement` dataclass that **REQUIRES all five clauses** (quantity, units,
  domain, unit_of_analysis, conditioning) with **no silent defaults** — an unstated clause raises, since
  the unstated one is what fails invisibly — and `check()`/`difference()` that **refuse rather than
  assume**, with waivers written at the call site via `allow=(...)`.
- **And the sem/CI rule is in the same module as code:** `bound()` returns the **far end** of the
  interval; `half_width()` is named differently so it cannot be mistaken for a bound. Nobody
  hand-writes 1.96·se again.
- **SELF-TEST replays the arc's own documented failures** — a guard that cannot construct the defect it
  prevents is inert. **8/8 caught:** fungal-m′-sizing-solar (domain), polynomial-vs-field units
  (unit_of_analysis), P(g) vs P(g|event) (conditioning), a-tail vs λ-tail (quantity), solar-floor-on-
  fungal (domain), mismatched certified domains (domain), **plus a control that must NOT raise**, and
  bound-vs-half-width. **GUARD IS LIVE.**
- **Rules that need remembering have failed here repeatedly; rules in code have held.** Status: CLOSED.

### R-122 — the guard got the scrutiny the guard applies: specificity widened, usage collision closed
- **Two holes, both Will's, neither a defect in the build — "the guard now needs the same scrutiny the
  guard applies."** An instrument gets sensitivity and specificity checked **separately**; 8 catches
  demonstrated sensitivity, and **the entire specificity check was one control row.**
- **HOLE 1 — single-witness specificity.** *A guard that raises on everything also scores 8/8 on a
  rejection-only suite* — the always-red-light failure fixed in the ratchet one item earlier.
  **Widened to a 9-case battery** across clause combinations: identical clauses/different values;
  differ only in sem; only in n; only in `note` (not a clause); matched non-trivial conditioning;
  matched field-level unit of analysis; matched non-dimensionless units; matched restricted domain;
  and **a deliberate `allow=` waiver being honoured.** All 9 pass — false-positive rate pinned, not
  touched.
- **HOLE 2 — the usage collision survived the naming split.** The original defect was never calling a
  half-width a bound; it was **using** one where a bound was required. `bound()`/`half_width()`
  returning bare floats left that advisory. **Fixed by typing the boundary:** `Bound` and `HalfWidth`
  are distinct classes with **no `__float__`**, so substitution is a `TypeError` rather than a wrong
  number in a sentence; `require_bound()` guards consumers; `check()` rejects bare values with an
  explicit message rather than an incidental `AttributeError`; and **`difference()` now returns a
  `Difference` carrying `.bound()`/`.half_width()` as methods**, so nobody reconstructs 1.96·se from a
  returned tuple. 7/7 interface tests pass.
- **Independent confirmation, unplanned:** `difference()` on the compact-support pair returns
  **bound = 0.0360** — the module reproducing R-113's corrected value without being told it.
- **CORPUS DISCIPLINE welded into the module docstring:** the sensitivity corpus is this arc's own
  escapes, never invented cases, *because a guard tested on synthetic defects proves only that it
  catches what someone could imagine.* **Every future slot error this guard misses becomes the next
  case.**
- **Final: sensitivity 6/6, specificity 9/9, interface 7/7 → 22/22. GUARD IS LIVE AND SPECIFIC.**
- **Status:** CLOSED.

### R-123 — the out-of-sample reproduction, banked as a different currency
- **`difference()` returning bound = 0.0360 on the compact-support pair reproduces R-113's corrected
  value — and I did not build that test.** It fell out of an interface check written for another
  purpose, from metadata the module had no access to, matching an answer computed by a different route.
- **File it as what it is: OUT-OF-SAMPLE corroboration that the boundary arithmetic is correct, not
  merely internally consistent.** "22/22 on tests I wrote" and "1/1 on a test I did not" are different
  currencies. Every one of the 22 was built to pass; this one was not built at all.
- **By this arc's own powered-falsifier standard it is the most informative single result in the
  guard's validation** — the only one that could not have been reverse-engineered to green.
- **Status:** BANKED as out-of-sample.

### R-124 — Allen V1 is the guard's FIRST REAL ESCAPE, not its first catch
- **Ran it through the guard before filing it as routine, as instructed. THE GUARD DOES NOT FIRE.**
  Stated honestly — quantity `rho(rep_int, ks_gue)`, units dimensionless, domain q-bands, unit of
  analysis q-band, conditioning none — **all five clauses MATCH on both sides.**
- **Because the defect is not a clause mismatch.** It is that rep_int is **saturated** on Allen V1
  (clustered ⇒ clipped to exactly 0 ⇒ near-zero variance), so ρ reports the saturation rather than the
  relationship. **That is an undeclared property of the DATA, not of the comparison's metadata** — and
  declared-metadata equality cannot reach it.
- **So it becomes the next corpus case, per the discipline welded into the module — and it needs a NEW
  KIND of check: a PRECONDITION on the statistic, not a clause on the comparison.**
  Added `saturation()`, `require_varying()`, `check_correlation()`: a correlation/rank/order statistic
  requires non-degenerate variance in both inputs, and clipping produces **exact ties**, so exact-equality
  is the right detector.
- **Constructed confound, both directions:** a latent variable with true ρ = −0.918 against ks_gue,
  clipped the way rep_int is → **`require_varying` FIRES on the clipped version and stays silent on the
  same data unclipped.** Sensitivity and specificity on one confound.
- **Quantitatively, and correcting myself:** ρ attenuates monotonically with saturation
  (0% → −0.902, 50% → −0.763, 95% → −0.375, 99% → −0.255). **My "ρ ~ 0 needs above ~95%" was wrong.**
  The regime that matters is **100%** — variance exactly zero, ρ **undefined** — which is precisely the
  fungal precedent (194/194 BL rows exact-0). Allen V1 clustered across all bands gives that.
  **The mechanism is consistent with the banked ~0; only recompute settles whether it was the cause.**
- **AND IT IS THE TOP OF A LIST, as suspected.** Excluding my own tooling: **18 sites across 10 files**
  run correlation / rank / percentile **on the saturating field** — `solar_surrogate_port`,
  `bulk_recovery`, `cross_substrate/quadrant_marginal_test`, `phase22a/h2_survival`,
  `phase22b/pass_d_glm_surrogate`, `phase22b/run_phase22b`, `phase25/run_phase25`,
  `phase31b/h2_per_window_surrogate`, `run_phase13_calibrators{,_v2}`. Each owes `require_varying()`.
- **Re-graded from "recompute Allen V1's ρ" to "run the precondition over the 18 variance-consuming
  sites."** Not one item; the head of one.
- **Status:** OPEN, re-graded, enumerated.

### R-125 — the precondition made GRADED, and a correction to how I described my own code
- **The push, and the premise needs one correction before the fix is credited.** Will read my prose
  ("clipping produces exact ties, so exact-equality is the right detector") as a **binary** check with
  power only at 100% saturation, green-lighting a site at 85%. **The code did not do that** — it used
  `max_saturation = 0.30` and fires at 50/70/85/90%. **My description misrepresented my own
  implementation**, and the push was against the description.
- **But the fix is real anyway, for a better reason: 0.30 was an ARBITRARY constant I never
  justified.** The graded version replaces it with a threshold **derived from the attenuation curve**
  and tied to a **declared tolerance on rho loss.**
- **The calibration is clean because the attenuation factor is UNIVERSAL in the partner variable.**
  If y = βx + ε then ρ(x_c,y)/ρ(x,y) = **ρ(x_c, x)** — no y. Verified across β = −0.9, 0.3, 2.0 to four
  decimals. So **one curve in saturation serves every correlation on a clipped field**:
  retained ρ = 1.000, 0.932, 0.856, 0.741, 0.519, 0.407, 0.219, 0.000 at sat = 0, .3, .5, .7, .9, .95,
  .99, 1.0.
- **And it need not be assumed at all.** `attenuation_measured(clipped, signed)` = ρ(clipped, signed)
  is **exact and assumption-free**, available at every site precisely because the fix added the signed
  field. The Gaussian curve is the fallback for banked results where only the clipped field survives,
  and the assumption is printed in the refusal message.
- **The check now states its own power**, which a precondition without one is the unquantified-power
  defect a level down: *at max_loss = 10% it fires above **39%** saturation; at 25%, above **69%*** —
  and is silent below **by design**, with residual attenuation under the tolerance.
- **Corpus grown by the real escape, per the discipline: 6 → 11 sensitivity cases**, including graded
  firing at 50/85/100%, deliberate silence at 20%, and measured-vs-calibrated agreement.
  **Final: sensitivity 11/11, specificity 9/9, interface 7/7 → 27/27.**
- **Status:** CLOSED — the precondition now watches degeneracy, not merely full degeneracy.

### R-126 — the sweep's real payload: saturation manufactures FALSE NEGATIVES
- **Pre-filed before the 18-site sweep runs, because it changes what the sweep is for.** Saturation does
  not create spurious detections — it **attenuates real relationships toward zero**. So the dangerous
  banked claim is **not a false positive; it is a missed one.**
- **Therefore the sweep is not cleanup.** It is a check on whether any *"weak or no relationship"*
  conclusion in those 10 files was actually **"saturated-and-attenuated" in disguise** — Allen V1's
  ρ ≈ 0 being the exemplar, not the exception.
- **And the partial-saturation regime is the worse one:** full saturation gives an **undefined** ρ,
  which stops you; partial gives a **plausible wrong number**, which does not.
- **Status:** OPEN — the sweep's verdict now has a stated direction of risk.

### R-127 — two principles the arc has now earned, banked as families
- **EXACT TIES IN A CONTINUOUS FIELD ARE ALWAYS A MECHANISM, NEVER A FLUCTUATION.** Exact equality is
  measure-zero under any continuous process, so its presence is a near-certain signature of a
  degenerate mechanism. **Firing in three places now:** fungal's 194/194 exact-zero detection, the
  dormant clip bug's 100% exact-zero rate, and saturation preconditions. It is a family, not a one-off:
  *any statistic on a field that can saturate needs a variance precondition, and exact-tie density is
  the universal detector.*
- **THE INSTRUMENT IS NOT ONE OF ITS OWN WITNESSES.** My first count of at-risk sites included the
  sweep tool's own references to the field — the measurement instrument counting itself as a data
  point, inflating the very number used to scope the sweep (20 → **18** once excluded). **Recurring
  shape, not a one-off:** any sweep for "sites affected by X" is itself a site touching X, and the tool
  is not a site. Sibling of shared-source-is-not-corroboration.
- **Status:** BANKED.

### R-128 — attenuation universality is a THEOREM, and it makes the precondition family tractable
- **Statement:** for y = βx + ε and x_c any deterministic clipping of x,
  **ρ(x_c, y) / ρ(x, y) = ρ(x_c, x)** — independent of β, of var(ε), and of the partner variable
  entirely.
- **Proof (a derivation, not a fit):** ρ is bilinear in the standardised variables and the clipping
  acts only on x, so the y-dependence factors out — cov(x_c,y) = β·cov(x_c,x), cov(x,y) = β·var(x),
  hence the ratio is cov(x_c,x)/(sd(x_c)·sd(x)) = ρ(x_c,x). Verified across β = −0.9, 0.3, 2.0 to four
  decimals.
- **Consequence, and it is the reason this matters:** saturation attenuation is a property of **the
  clipped field alone**, not of the relationship being measured. **Characterise a field's saturation
  once and you know its effect on every statistic that field will ever enter** — no per-relationship
  recomputation, ever.
- **Honest seam, filed with it:** exact under the linear model, approximate when the relationship is
  not linear. So `attenuation_measured` (assumption-free, ρ(clipped, signed) directly) is preferred
  wherever the signed field survives; the Gaussian curve is the **labelled** fallback for banked-only
  sites, and its assumption prints in every refusal that uses it.
- **Status:** BANKED as a theorem in the module header.

### R-129 — the sweep is now a CORRECTOR, and fungal demonstrates R-126 on real data
- **Built:** `joint_q_profile` now emits `rep_int_signed_q` alongside the clipped field, so per-site
  attenuation is **measurable** at every site rather than assumed. `recover_rho()` returns
  (ρ_true, how) — divide the banked ρ by the measured attenuation.
- **Verified on constructed data with known truth:** recovery to **±0.002** across 30–90% saturation
  (banked −0.853/−0.780/−0.674/−0.466 → recovered −0.912/−0.913/−0.913/−0.915 against truth −0.914).
- **HARD LIMIT, filed with the tool:** recovery works only under **partial** saturation. At 100% the
  clipped field has zero variance, ρ is **undefined rather than attenuated**, and no factor recovers
  it — the only route is recomputation on the signed field, which is why emitting it was the
  load-bearing part of the fix.
- **AND THE REAL-DATA DEMONSTRATION.** Fungal's q-band profile, 120 well-powered bands:
  **saturation 100.0%**, so **ρ(rep_int CLIPPED, ks_gue) = undefined** — while
  **ρ(rep_int SIGNED, ks_gue) = −0.868.** A strong real relationship, erased.
- **That is R-126's false-negative prediction, demonstrated rather than argued** — and −0.868 sits in
  the same "tightly coupled" range the docs report for arithmetic substrates (−0.93, −0.99), which is
  exactly what the Allen V1 sentence attributed to "a different marginal feature."
  **NOT claimed:** that this settles Allen V1 — different substrate, still needs its own recompute.
  Claimed: the mechanism is now demonstrated on real data from the same detector.
- **Status:** OPEN — the 18-site sweep now has a corrector, not just a flag.

### R-130 — the two families sharpened, both Will's
- **Exact-ties needs its precondition or the fourth firing cries wolf.** The inference is valid only
  for a field **continuous by construction** — a discrete field (counts, categoricals, quantised
  instruments) has exact ties as its **normal state**. `saturation()` now **refuses without a declared
  `field_type`**, and that declaration is itself a commensurability question: is `ties` signal here or
  noise?
- **Witness-independence is ONE family with three faces**, not three rules: a measurement is
  contaminated when it shares structure with what it measures — an upstream catalogue (the struck SOC
  "independent" check, same GOES data), a data source (shared-source-is-not-corroboration), or **the
  tool being one of its own counted units** (my sweep counting its own references, 20 → 18). Filed as
  one principle so the fourth instance is *recognised* rather than discovered again.
- **Status:** BANKED.

### R-131 — a limit on this arc's review, worth carrying forward
- Will's own, and it generalises: **the review of this arc has been review-of-prose, not
  review-of-code.** Reported numbers and reported designs were what sat in the reviewer's context, so
  they were what could be falsified. R-125 is that caveat cashing out live — the code was sound and
  **the description implied a weaker check than existed.**
- **The divergence class is asymmetric in a way worth naming:** a report can be wrong in the *safe*
  direction (describing a weaker guard than exists) as easily as the dangerous one, and **only the
  side holding the code can catch either.** Prose/code divergence is therefore mine to audit, not the
  reviewer's — the reviewer can only ever falsify the artifact in front of them.
- **Status:** BANKED as a standing caveat on this arc's verification grade.

### R-132 — the sweep PRE-COMMITTED before it runs, including the outcome that reflects badly
- `seals/SATURATION_SWEEP_PRECOMMIT.json`, written **before** the sweep, per the arc's own discipline
  applied to a result whose likely direction is unflattering.
- **The uncomfortable outcome, named in advance so it cannot be softened afterwards:** if the sweep
  recovers strong couplings across multiple sites banked as null, **the corrected record has MORE
  structure than the original, not less** — which means **prior caution was miscalibrated toward false
  nulls**, and the conservatism that felt like rigour was the defect. Committed response: report it in
  that sentence, not as "some results need revisiting."
- **All four outcomes pre-mapped**, including **C (no recovery, nulls stand)** with the note that it
  **must be reported with the same prominence as A** — a sweep that only reports when it finds
  something is a publication-bias engine — and **D (100% saturation, no signed field retained)** as
  **UNRECOVERABLE, not null**: an erased relationship and an absent one are different things.
- **Instrument-failure conditions listed**, chief among them that `recover_rho()` returning a finite
  value at 100% saturation is a failure, not a convenience.
- **Allen V1's slot held in writing:** fungal is *family resemblance*, not identity; letting it
  retroactively close Allen V1 would be correct-fact/wrong-slot in its purest form. **Recompute
  required — and the data is present (~/fmexplorer/allen_cache, 29 GB), so it is QUEUED, not blocked.**
- **Status:** SEALED, unrun.

### R-133 — the fix's real payload, and the corrector's three regimes
- **Emitting `rep_int_signed_q` does not merely enable correction — it PREVENTS the unrecoverable
  regime for all future data.** Every result computed after the fix banks both fields and can never be
  fully erased. **Fungal's blank cell is blank because the signed field was not retained then**, not
  because the relationship was absent.
- **Three regimes, filed as distinct** — below the power floor (silent, clean); 30–90% (attenuated,
  recoverable, ±0.002); 100% (undefined, unrecoverable, corrector **refuses**). The refusal is the
  load-bearing behaviour: a tool returning a number there would manufacture signal from a field with
  none, which is the exact failure the precondition family exists to stop.
- **Status:** BANKED.

### R-134 — ★ THE REPAIR ALREADY EXISTED. Propagation, not discovery, was the failure
- **`overnight_2026_07_12/run_overnight.py:325` defines `irep_unclipped` — "The repair: signed
  ∫₀¹(1−R₂)dr — NO np.maximum(0,·)."** Built **two weeks before this session**, used in `VERDICT_A.md`
  to overturn a load-bearing claim, and **never propagated into `arithmetic_toolkit.py`.** The deployed
  detector kept clipping; this session rediscovered the repair from scratch.
- **Fifth instance of knowledge-does-not-propagate** — a fix filed where it could not fire. The
  antibody says *attach lessons to CALL SITES*; a repair living in one overnight directory is the
  literal counterexample.
- **AND IT CARRIES THE ALLEN ANSWER, which upgrades R-124.** From `VERDICT_A.md` on the unclipped axis:
  median signed I_rep = **allen −5.003**, hc3 −2.841, ret1 −4.767, with ρ(burst, I_rep) negative on all
  three and CIs excluding zero — *"the physically expected direction, for the first time. Allen is no
  longer an inverted outlier. The sign pathology was the instrument."*
- **So Allen's true I_rep ≈ −5.0 ⇒ clips to exactly 0 ⇒ 100% saturation is CONFIRMED FROM BANKED DATA,
  not assumed.** R-124's premise is established; what remains is only whether the specific
  ρ(rep_int, ks_gue) was computed on saturated bands — a far smaller question than "recompute Allen V1."
- **Two independent derivations of the same repair is evidence the repair is right. It is equally
  evidence the propagation channel is broken**, and the second is the actionable half.
- **ACTION:** reconcile `overnight_2026_07_12` against this session **before** further work on this axis.
- **Status:** OPEN — and it reorders the board.

### R-135 — the repo-wide sweep for the same defect classes: three flags, one clear
- **`phase36/kpm_dos.py:74`** — `np.clip(rho_x, 0, None)` on a KPM density, then `cumsum` → CDF →
  unfolding. **Same shape as the rep_int bug** (signed quantity clipped, then integrated), and Gibbs
  ringing is exactly what goes negative, so the clip **rectifies** rather than regularises.
  **Grade: low** — Jackson damping already mitigates Gibbs and **no callers were found.** Verify before
  spending effort.
- **`universality.py:92`, `intermittency.py:155`** — p-values clipped to [0,1], then `nanmedian(ks_p)`,
  a **rank** statistic on a clipped field. **Lower grade:** the clip enforces a *definition* rather than
  destroying sign information, unlike I_rep where negatives are the signal. Check only if
  `median_ks_p` carries a comparison.
- **`cross_substrate/validate_fitters.py:35`** — `np.clip(F, 0, 1)` on a CDF. Legitimate; logged.
- **CLEAR: `arsrh/solar_gap_checks.py:54`** — `gap_ci = 1.96*nse` is reported as `GAP_95CI` beside
  `GAP`, i.e. a half-width used and labelled as a half-width. **Correct usage, and the only 1.96·se in
  the repo outside the guard.** The R-110/R-113 defect does not recur elsewhere.
- **Status:** CLOSED as a sweep; two flags carried forward at low grade.

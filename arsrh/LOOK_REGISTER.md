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

- **⚠ SUPERSEDED 2026-07-28 — CLOSED AS VOID by R-166.** The anomaly this entry was opened to explain does not exist outside its own window (deduped, 5x depth: remainder +0.00133 ± 0.00394; H1 rejected at 7.6 sem, H0 consistent p = 0.736). R-077 is no longer an open item. The formula stays CALIBRATED at |det| ≤ 289, ±12% — that band is a ratio and is duplication-invariant.

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

### R-136 — RECONCILED against `overnight_2026_07_12`. Each corrects the other once.
- **Same quantity, verified not assumed.** `irep_unclipped` uses `(r_max=5.0, n_bins=50)`; my
  `repulsion_integral_signed` defaults to `(10.0, 100)`. **Bin width is 0.1 either way**, and fungal
  reads **−2.21198 under both**, to five decimals — and matches the deployed `joint_q_profile` path,
  which itself calls `(5.0, 50)`. A five-clause question, answered by running it.
- **TWO INDEPENDENT CERTIFICATIONS of one estimator.** The overnight used a **calibrator zoo with a
  pre-committed HARD STOP** (*"if the clustered class fails its reading, the REPAIR is wrong, not the
  class"*); this session used an **analytic Neyman–Scott target**. Poisson reads **−0.0094** there and
  **−0.00000** here. Different methods, same verdict — stronger than either alone.
- **AND THE OVERNIGHT GIVES FUNGAL UNITS, which this session could not.** Its swept ladder puts
  −2.21 between `neyman_scott` 2.0 (−1.376) and 5.0 (−4.951), beside `cox` 1.5–2.0 and
  `gamma_renewal` 3.0. **Fungal is moderately-to-strongly clustered on an independently calibrated
  scale** — an upgrade from "outside the null range."

### R-137 — the overnight corrects ME: I cited a table its own document supersedes
- My compilation quoted VERDICT_A **lines 85–87** (allen −5.003). **POST-RUN #2(a) of that same file
  retracts them:** `irep_unclipped` had been called on **raw spike times**, and r ∈ [0,1] is *in the
  input's own units*, so the window meant a different number of mean-ISIs per cell. Caught by a
  threshold-free predictor returning a **physically backwards sign** — *"a sign that cannot be right is
  worth more than a magnitude that looks plausible."*
- **Current, rate-corrected:** allen-hpf **−7.99 (100% < 0)**, hc3 −1.44 (98%), ret1 −0.32 (77%).
- **This strengthens R-124/R-134 rather than weakening it:** Allen's true I_rep is **−7.99** with
  **every cell negative**, so the clip pins **all of them** to exactly 0. **Saturation confirmed at the
  maximum**, from banked data.
- **My fungal −2.212 is NOT touched by that bug** — pooled fungal spacings have mean **1.000000** by
  construction, so r ∈ [0,1] is exactly one mean-ISI. Checked, not assumed.
- **And a grading correction:** the overnight banks ρ(burst, I_rep) < 0 as **INSTRUMENT VALIDATION, not
  a discovery** — *"banking it as a discovery is how the next twenty messages get spent defending it."*
  My compilation presented it as a substrate finding. **Their slot is the correct one.**

### R-138 — I correct the overnight: VERDICT_C is stale and was never marked
- **`VERDICT_C.md` (02:37) carries the pre-rate-fix census** — allen −4.8526, hc3 −2.4727, ret1 −4.7427
  — which **VERDICT_A (20:15) supersedes** with −7.99 / −1.44 / −0.32. **C was never updated.**
- So the overnight's record holds **three tables of one quantity, two stale, none marked.** A reader
  taking VERDICT_C at face value gets a retracted number. **Exactly the defect that caught me in
  R-137** — which is why I made it.
- **Marked SUPERSEDED in place, not deleted**, per the harness discipline, with the current numbers and
  the reason inline.

### R-139 — what the overnight holds that this session lacked, and vice versa
- **Theirs:** (i) **reference poles + a clustered ladder** giving the signed scale *units*;
  (ii) **the rate-contamination lesson** — `pair_correlation_full` integrates r ∈ [0,1] in the **input's
  own units**, so inputs must be unit-mean-normalised or the window means something different per
  object. **This is a live trap for the 18-site sweep and was NOT on its list**; it is now.
  (iii) the grading discipline of R-137.
- **Mine:** the attenuation universality theorem; the corrector; the three watchers; and **the
  propagation finding itself.**
- **The standing defect is the channel.** Two correct derivations, neither reaching the shared toolkit
  until the second was forced to. **The repair is now IN `arithmetic_toolkit.py` — the first time it
  has been anywhere it can fire.**
- **Status:** RECONCILED. Full audit in `arsrh/RECONCILIATION_overnight_2026_07_12.md`.

### R-140 — ★★ SIXTH INSTANCE, found by the watcher's own signature, from THE SAME NIGHT
- **The same overnight defined TWO repairs. I propagated one.** `run_overnight.py:337`,
  `brody_unbounded` — *"The repair: Brody with BOTH bounds opened (GUE≈2, GSE≈4 need the upper one)."*
- **`cross_substrate/axes.py:158` still fits `bounds=(0.0, 1.0)`, so the deployed Brody axis
  SATURATES AT BOTH ENDS.** Verified:
  | input | deployed q | repaired q | overnight |
  |---|---|---|---|
  | Poisson | 0.0052 | 0.0035 | −0.0052 |
  | clustered k=3 s=0.30 | **0.0001 (AT BOUND)** | −0.2482 | — |
  | clustered k=8 s=0.05 | **0.0001 (AT BOUND)** | −0.5264 | — |
  | GOE (inv-cdf) | **0.9999 (AT BOUND)** | 1.0087 | +1.0032 |
  | GUE (inv-cdf) | **0.9999 (AT BOUND)** | 1.5313 | +1.5325 |
- **So the deployed axis can represent neither clustering nor GUE/GSE, and cannot distinguish GOE
  from GUE — all three pin to 0.9999.** Worse than the I_rep clip, which saturated at one end only.
- **My repaired values reproduce the overnight's to 3–4 decimals** — independent reproduction of their
  calibration, unplanned.
- **Correction to my own first check:** a random-matrix GUE at n=600 read 0.842 both ways and did *not*
  reach the bound; the overnight's inv-cdf sampling was the right method and I re-ran with it. A
  spot-check that fails to reproduce a claim is not a refutation of it.
- **Propagated** as `I8_brody_q_unbounded`, `I8_brody_q` retained bit-identical (regression-checked).
- **Status:** CLOSED as a fix; the pattern it evidences is R-141.

### R-141 — the FOURTH WATCHER: `propagation_watch.py`. The most-attested defect finally has a guard
- **The diagnosis, and it reorders the arc:** the standing defect was never the saturation bug — it was
  **the channel**. The repair existed, validated, on 2026-07-12; everything expensive after that was a
  **propagation failure wearing the costume of research.** Three watchers guard against **wrong**
  results; **nothing guarded against right results filed where they cannot fire** — six instances, the
  most-attested defect in the repo, zero automated coverage.
- **Three mechanical signatures.** **A** — a leaf module imports a **private** symbol from a shared
  module (the public API didn't offer it, so someone wrapped it locally). **B** — repair language in a
  non-shared module. **C** — a leaf defines a **repair-variant** name (`X_unclipped`, `X_unbounded`,
  `X_fixed`, `X_v2`, …) of a shared stem.
- **It found instance 6 on its first run**, via signature C, which is the only evidence available that
  it detects rather than describes.
- **SPECIFICITY FIX, same lesson one level over:** the first draft matched "bounded"/"unbounded"/
  "proper" as *mathematical* terms and returned **41 hits, mostly false** — a watcher whose hit list is
  mostly noise is the alarm fatigue it exists to prevent. Signature B restricted to phrases that can
  only mean a repair: **41 → 14**, both known instances still caught. **A and C carry the recall and
  are structural rather than lexical.**
- **Ratcheted** like the migration checker; manifest demands a reason per resolution.
  **Current: 6 propagated, 1 local-by-design, 2 not-a-repair, 5 unresolved (from 14).**
- **Two candidates checked and CLEARED, one of them exemplary:** the Jenkinson–Pollicott digit
  transposition is **propagated**, with the wrong value retained in `thermo/gate_fixtures.py` as the
  **named fixture `DIM_E2_REPO_TRANSPOSED`** — the error kept as a regression fixture rather than
  deleted. **That is the model.** And phase23's `N_SHUFFLE_SEEDS=2` is a detector-label control whose
  own comment records the shuffle is a no-op for the pooled stream — thin, but a different construct,
  not phase38's under-powered-null repair.
- **Status:** LIVE. Fourth watcher, fourth declared power.

### R-142 — ★★★ THE GUARDS WERE ORPHANED. Seventh instance, mine, built this session
- **Pointed the propagation watcher at the guards, as instructed. The joke wrote itself.**
  `commensurable` imported by **0** modules. `propagation_watch` **0**. `rep_int_migration` **0**.
  `require_varying` / `check_correlation` / `recover_rho` at **0 call sites**. `Measurement(` at **0**.
- **Every guard built this session was in exactly the state `irep_unclipped` was in on 2026-07-12:**
  correct, validated, and **unable to fire** — standalone scripts nobody imports and nobody runs.
  A guard that must be *remembered* is not a guard. **Seventh instance, and I built it while writing
  the watcher for precisely this.**
- **FIXED: `tests/test_known_defects.py`** — pytest now runs all three watchers plus the guard's own
  self-test. A test file is in the shared path **by construction**, which is the only form that
  survives this channel.
- **Status:** CLOSED — guards now fire under `pytest`.

### R-143 — every real defect FIXTURED, on the model the sweep itself found
- **The model:** `thermo/gate_fixtures.py` keeps the Jenkinson–Pollicott digit transposition as the
  *named* constant `DIM_E2_REPO_TRANSPOSED` — the **wrong value retained and tested against**, not
  deleted. Deleting loses the evidence the error happened; naming it means the suite permanently tests
  that this specific error cannot return. **Fixed-and-FIXTURED, not fixed-and-forgotten.**
- Now banked the same way: `IREP_CLIPPED_SATURATES_TO_ZERO`, `FUNGAL_IREP_SIGNED_TRUTH = −2.21198`,
  **`BRODY_AXIS_SATURATES_BOTH_ENDS = (0.0, 1.0)`**, `BRODY_GOE_TRUTH`, `BRODY_GUE_TRUTH`. Each test
  asserts **both** that the deprecated path stays bit-identical *and* that the repaired one separates
  what the defect collapsed.
- **Two of my own errors caught by writing the fixtures**, both previously-banked lessons recurring:
  (i) `abs(signed) < 0.01` on Poisson **pinned a magnitude seen in one draw** — it scatters ±0.03 at
  n=4000 between seeds. Rewritten to assert **direction over 20 replicates** (R-101's lesson, applied
  to a fixture). (ii) My `tests/` exclusion used `startswith("tests/")` while grep emits `./tests/…`,
  **so the exclusion did nothing** — caught by the test failing, which is the arrangement working.
- **Status:** CLOSED — 7/7 passing.

### R-144 — answering the two direct questions, and a new sweep the sixth instance raises
- **Is brody the only two-ended one? YES, among the current hits.** The other four unresolved:
  `verify/tier3_chirp_and_cap.py` ×2 (a *verification harness* that deliberately runs deployed-vs-fixed
  paths — the semicircle unfolding fix lives in `fix_gue_generator.py` at repo root, importable);
  `_ks_pvalue` private-imported by two files (a **public-API gap** signal, and a p-value is bounded by
  *definition*, not class-collapsing); and a `_v2` suffix with no shared stem. **Only `I8_brody_q` is
  a two-ended saturation of an axis carrying a classification.**
- **THE CLASS-COLLAPSE SWEEP, newly raised and unstarted.** One-ended saturation hides **magnitude**;
  two-ended hides **identity**. The deployed Brody axis pinned clustered → 0.0000 and **GOE *and* GUE
  both → 0.9999**, collapsing the two RMT classes the program exists to separate — and it is consumed
  at **87 sites across `harvest.py`, `calibration_anchors.py`, `brocot_approximability.py`,
  `hc3_ec_pillar1.py`, `phase2b_*`.**
- **The question, filed in the same shape as the false-negative sweep:** *how many banked
  "GOE-like"/"GUE-like" class assignments came off this axis while it could not tell them apart?*
  Saturation there does not attenuate a magnitude — **it substitutes a bound for a class label.**
- **Status:** OPEN, unstarted, and the larger of the two sweeps.

### R-145 — CLASS-COLLAPSE SWEEP: RUN. And it is mostly magnitude-hiding, not identity-hiding
- **Provenance answered FIRST, as asked.** `calibration_anchors.py` defines its anchors as **known-class
  synthetic processes** (`GOE_b1`, `GUE_b2`, `GSE_b4` beta-ensembles, poisson, clock) — brody_q is
  **displayed, never used to define them**. So the sweep's **class reference is clean by construction**;
  only the anchors' brody *coordinate* is saturated. The baseline is not contaminated.
- **⚠ AND IT CORRECTS MY OWN EARLIER CLAIM.** On the actual anchor construction:
  **GOE_b1 0.8607 (both fits, NOT at the bound)**, GUE_b2 **0.9999 → 1.3814**, GSE_b4 **0.9999 → 2.0509**.
  **The collapse is GUE↔GSE, not GOE↔GUE.** My "cannot distinguish GOE from GUE" came from idealized
  Wigner-surmise inv-cdf samples and does **not** reproduce on the beta-ensemble anchors. Class spread
  **0.139 deployed → 1.190 repaired, 9×**. And the GUE anchor's documented expectation **"q≈1" IS the
  bound**, not the truth (1.38).
- **THE SWEEP.** Fingerprint store: **436,040 entries, 77 coordinate files.**
  **`I.8_brody_q`: 20,801 banked values across 46 substrates — 74.8% at a bound** (72.5% at 0.0,
  2.4% at 1.0). `ARS.rep_med` (the clipped I_rep, same store): **8,106 values, 16.6% at 0.0.**
- **THE DISTINCTION THAT MATTERS, and I nearly skipped it:** q = 0.0 exactly is **also the correct
  reading for a genuinely Poisson process**, so "at bound" is an **upper bound on saturation**, not a
  count of it. Split by whether the substrate was **independently established clustered** by the
  2026-07-12 census:
  | | n | at 0.0 | at 1.0 |
  |---|---|---|---|
  | **neural (known clustered)** | 15,107 | **13,773 (91.2%)** | 143 (0.9%) |
  | other | 5,694 | 1,302 (22.9%) | 351 (6.2%) |
  **The neural row is CONFIRMED saturation** — those substrates read 100%/98%/77% of cells with
  I_rep < 0, so their q = 0 is the bound. The other row is an upper bound only.
- **SO THE EXPOSURE IS 91% MAGNITUDE-HIDING, ~1% IDENTITY-HIDING.** The dominant defect is the same
  shape as the I_rep clip — *how* clustered, erased — not misclassification. **The two-ended
  class-collapse is real but rare: 494 upper-bound values, 2.4%.** That is a materially smaller and
  differently-shaped exposure than "87 sites of possible misclassification," and it is the honest size.
- **OUTCOME C, reported at equal prominence per the pre-commitment:** **0 entries carry an explicit
  GOE/GUE/Poisson/GSE label in `axes_computed`.** The coordinate store records **values, not
  derivations**, so the sweep counts exposure and **cannot prove any specific class call was made from
  a saturated value.** No banked misclassification is demonstrated. That is a real result and it is
  reported as prominently as the counts.
- **UNRECOVERABLE, not null:** a q pinned at a bound cannot be corrected by a factor — the spacings are
  not in the store, so only recomputation recovers it. Same regime as 100% I_rep saturation.
- **Status:** RUN. Exposure sized, direction corrected, no misclassification demonstrated.

### R-146 — ★★★★ THE REPAIR SET WAS ALREADY WRITTEN DOWN. 2 of 9 propagated.
- **`CLUSTERING_COUPLING_FINDINGS.md` carries a NINE-ROW DEFECT TABLE and the line "Repairs, all
  validated."** Every defect this session rediscovered is in it, correctly characterised, with its
  repair already built and checked. **I have propagated two.**
  | documented defect | status in deployed code |
  |---|---|
  | `I_rep`'s `np.maximum(0,·)` clip | **PROPAGATED** 2026-07-26 |
  | Brody `bounds=(0,1)` | **PROPAGATED** 2026-07-27 |
  | `s < 10.0` truncation (`axes.py:150`) | **LIVE** — "discards the heavy tail *that is* the clustering signature" |
  | `spacings()` positional slice (`phase35a/unfold_rotnum.py:70`) | **LIVE** — `d[int(.02n):int(.98n)]` on an unsorted diff array: removes **no** outliers |
  | `bulk_recovery`'s `np.interp` clamp (`:133,:140`) | **LIVE** — clamps outside the calibration range, so "every clustered band → the σ of the *(Poisson regime)* knot" |
  | `validate_fitters` probing only at the rails | **LIVE** — *"probing at the rails cannot detect railing"* |
  | Berry–Robnik CI collapse at the rail | unverified here |
  | global unit-mean normalisation (CV-16 drift) | unverified here |
  | `I_rep` on raw spike times | documented; my fungal use is unit-mean, checked |
  **PROPAGATED 2/9. LIVE AND CONFIRMED 4. UNVERIFIED 2.**
- **AND THE DOC HAD THE CHARACTERISATION RIGHT WHERE BOTH OF US HAD IT WRONG.** It says Brody
  `bounds=(0,1)` sends **"GUE/GSE → GOE rail"** — which is exactly what the anchors measure
  (GUE 0.9999, GSE 0.9999, GOE 0.8607). My "cannot distinguish GOE from GUE" and Will's
  GOE↔GUE class-collapse escalation were both **wrong against a document already in the repo.**
  `audit/02-math.md:156` flagged it independently too: *"a one-sided fitter… the cap is the upper
  (repulsive) side."* **Two prior write-ups, both correct, neither in the code.**
- **THIS IS THE ARC'S SUBJECT AT FULL SCALE.** The defects were not undiscovered — they were
  **discovered, characterised, repaired, validated, and written down, and the code has none of it.**
  Everything this session spent effort rediscovering was already answered in prose. **The gap was
  never knowledge. It was always the channel.**
- **Status:** OPEN — and it is now unambiguously the top item on the board.

### R-147 — the identity-collapse tail closes cheaply; the sizing was wrong twice, by both of us
- **No banked prose claim rests on a Brody class call.** The only prose hits are the defect table
  itself and the audit's own flag. Combined with outcome C (zero class labels in `axes_computed`),
  **the 494 upper-bound values have no demonstrated consequence** — exposure without a claim resting
  on it. **The identity-collapse tail closes.**
- **Both sizings were wrong, and symmetrically.** Will escalated on severity ("two-ended hides
  identity") without base rates; **I banked it in R-144 as "the larger of the two sweeps" on the same
  reasoning.** The data: **~91% magnitude-hiding, 2.4% identity-hiding, 0 demonstrated
  misclassifications.** Severity-without-frequency mis-sizes an exposure, and neither of us checked
  frequency before filing.
- **Status:** CLOSED.

### R-148 — ALL SEVEN PROPAGATED. The nine-row repair table is closed.
Non-destructive throughout: every deployed function retained **bit-identical**, repair added alongside,
each with a **named regression fixture** in `tests/test_known_defects.py` (11 passing).

| # | defect | repair | verification |
|---|---|---|---|
| 3 | `s < 10.0` truncation | **already bundled** into `I8_brody_q_unbounded` (`s[s>0]`, no cut) | isolated: −0.4872 with cut vs −0.4976 without; 1.70% of mass in the tail |
| 4 | `spacings()` positional slice | `spacings_value_trimmed` — trims by **value** percentile | injected outliers: deployed **retains** (max 52.5), repaired **removes** (max 3.9) |
| 5 | `bulk_recovery` `np.interp` clamp | `beta_hat_nonclamped` / `beta_per_q_nonclamped` — **NaN** outside the calibrated span | extrapolating a calibration is not a measurement |
| 6 | `validate_fitters` probes at rails | out-of-range CASES existed (07-11/12); added a **repaired COLUMN beside the deployed one, not a swap** | deployed 2/5, **repaired 4/5** |
| 7 | Berry–Robnik CI collapse | `I9_berry_robnik_rail_flag` + no `s<10` clip | poisson 0.0015, clustered 0.0045, goe 0.9965, gue 0.9975 — **all four rail-proximate** |
| 8 | global unit-mean normalisation | `unfold_unit_mean_windowed` | drifting cell CV **1.2185 → 1.0122** (true 1.0) |
| 9 | `I_rep` on raw spike times | **unit-mean guard** on `pair_correlation_full` | warns on raw (0.3 s ISI), silent on unit-mean |
- **⚠ MY FIRST ATTEMPT AT REPAIR 7 WAS WRONG, and the error is the session's own lesson recurring.**
  I returned `None` at the rail. But **ρ ≈ 0 is legitimately Poisson and ρ ≈ 1 legitimately GOE** —
  refusing the rail discards correct measurements. Same structure as "q = 0 is also correct for genuine
  Poisson." The rail is **ambiguous, not invalid**, so the repair is to **flag** it and require a
  sign-carrying axis (`I10_cv`) to disambiguate. Rewritten.
- **AND THE GATE'S OWN EXPECTATION IS WRONG, left unrepaired on purpose.** `CASES` expects GUE Brody
  q = **2.0 ± 0.3**; four independent runs give **~1.53** (overnight 1.5325; today 1.5313, 1.5433,
  1.5166). The repaired fitter "fails" that row by being **right**. **Not fixed** — editing an
  expectation to make a test pass is the one move the seals forbid. Filed `documented-open`.
- **Status:** CLOSED. 9/9 propagated.

### R-149 — the watcher's model was wrong, and fixing it is the fourth specificity pass
- **`SHARED` was 8 hand-picked modules. Measured, it is 27** (≥ 8 importers) — and my list omitted
  **`ars_classify.py` (51 importers)** and **`unfold_rotnum.py` (33)**. The watcher was **under-scoped**:
  it would have called a repair landing in either "unpropagated" when it had reached dozens of
  consumers. **"Shared" is now measured, not guessed**, and cached.
- **That widening broke signature A's precision** — hits 5 → 27, almost all **intra-package** private
  imports (`cross_substrate/allen_hpf` ← `cross_substrate/population_fingerprint`), which are ordinary
  internal reuse. Restricted to **cross-package** private imports: 27 → **15**.
- **RECALL LIMIT, recorded rather than papered over:** signature C is a **fixed suffix list**, so it
  **missed my own repairs** (`_value_trimmed`, `_windowed`, `_railaware`) until I added them. A lexical
  signature has bounded recall by construction; A is structural and the manifest carries the rest.
- **Fourth manifest category added: `documented-open`** — a real defect, deliberately unrepaired, with
  a reason. Without it the GUE-expectation item had nowhere honest to sit.
- **Ratchet reset DELIBERATELY and recorded:** the count moved because **the instrument improved**, not
  because defects appeared. Silently ratcheting would have hidden the model change.
- **Status:** CLOSED. 6 propagated / 1 local-by-design / 2 not-a-repair / 1 documented-open / 15 open.

### R-150 — DOWNSTREAM SWEEP: what the two-week propagation gap cost the record
- **The question the arc kept deferring: now that the deployed path is correct, which banked
  conclusions move?** Measured on the two substrates whose raw data is in the repo.
- **Row 8 verified on REAL data (it had only been verified on a synthetic drifting cell):** the
  global-unfold defect is **strongly substrate-dependent** — fungal CV 2.6865 → 2.7137 (**−1.0%**,
  negligible), **solar CV 4.3248 → 2.5019 (−42.1%)**. Solar has the ~1000× cycle envelope, so **42% of
  its CV was drift, not clustering.** Row 7 was verified live before repair (clip + bounds read
  directly, rail-proximity measured on all four calibrators); **row 8's real-data magnitude is now
  closed too.**
- **SOLAR — the claim SURVIVES and STRENGTHENS.** mass03 vs a cycle-preserving null:
  | unfold | observed | null | GAP | exceeds p99 |
  |---|---|---|---|---|
  | global (deployed) | 0.5968 | 0.3078 ± 0.0069 | **+0.2890** | yes |
  | windowed (repaired) | 0.4762 | 0.0885 ± 0.0063 | **+0.3877** | yes |
  **GAP +0.2890 → +0.3877, a 34% strengthening.** Both observed and null fall under the repair, but
  **the null falls much further** — it is cycle-preserving, so it carries the drift the observed has
  genuine clustering *on top of*. Against the quoted 0.20 floor, the claim is comfortably intact.
- **FUNGAL — the claim is UNCHANGED.** GAP **+0.4089 → +0.3975** (−2.8%); the null reproduces its
  banked 0.245 under both unfolds (0.2457 / 0.2497). Consistent with fungal's −1.0% CV change.
- **SO: NO BANKED VERDICT FLIPS.** Both quotable claims survive; one strengthens materially, one is
  flat. **The direction matches the pre-commitment** — the defects were conservative on the observed
  side, so the repairs move claims *toward* stronger, not weaker.
- **WHAT IS NOT SWEPT, stated rather than implied:** substrates whose raw data is not in the repo
  (allen, hc3, ret1, ibl, buzsaki, dr-port, pvc-11) — their **coordinate entries are known to move**
  (74.8% of banked Brody values sit at a bound, 16.6% of `ARS.rep_med`), but whether any *conclusion*
  of theirs moves is **unmeasured**. That is the remaining downstream work and it needs the source data.
- **Status:** PARTIAL — closed for fungal and solar, open for the seven substrates without local data.

### R-151 — the boundary-saturation antibody, banked after it caught my own repair
- **Three firings:** the corrector refusing to null the 100% case; the sweep splitting q=0-saturated
  from q=0-Poisson; and **my first Berry–Robnik repair returning `None` at the rail.**
- **THE RULE: the repair for a boundary-saturation defect is DISAMBIGUATION, never REJECTION.**
  Fixing "the bound is reported as truth" by "refuse the bound entirely" trades a false positive for a
  false negative. **A boundary value is ambiguous, not invalid** — flag it and require a sign-carrying
  axis. It caught my own first attempt, which is the only evidence that makes it a rule rather than a
  description. **Status:** BANKED.

### R-152 — the "seven substrates" item CLOSES, and my blocker was wrong twice
- **My blocker was "raw data isn't local." FALSE:** `allen_cache` 29G, `buzsaki_cache` 62G,
  `ibl_cache` 7.7G, `crcns_cache` (ret1 + sessions) 630M, `data/` 11G, `fungi/` 1.1G. **I asserted a
  blocker without checking** — the reasoning-instead-of-running failure, one more time, and it took
  Will saying "we should have the data" to make me look.
- **But the item closes for a better reason than data availability, and it is checkable in seconds:**
  **the load-bearing n=7 finding was ALREADY computed on repaired axes.**
  `CLUSTERING_COUPLING_FINDINGS.md` says *"on a repaired instrument"* in its title; its axis is the
  **signed** I_rep over **unit-mean-normalised** spacings (so neither the clip nor the
  rate-contamination touches it); and its values are **negative** (−0.236 … −8.306), which the clipped
  field **cannot produce**. Its columns contain **no Brody axis at all.**
- **Direct confirmation:** only pvc-11 carries `ARS.rep_med` in the coordinate store, at **median
  0.0000 with 79.2% exact zeros** — the clipped field — while the finding's pvc-11 value is
  **−0.863**. **Different quantities under related names.** The other six substrates have no
  `ARS.rep_med` banked at all.
- **SO: THE COORDINATES ARE STALE; THE CONCLUSIONS ARE NOT.** The seven substrates' load-bearing claim
  does not rest on any unrepaired axis. Marked in place with `coordinates/STALE_AXES_NOTICE.md` —
  retained, not deleted, with the counts, the Poisson-vs-saturated caveat, and the repaired functions
  named. Anything reading those two axes out of the store (landscape views, `harvest.py`) is showing
  pre-repair values and must recompute.
- **Status:** CLOSED. The remaining downstream exposure is display surfaces, not conclusions.

### R-153 — the GUE expectation RE-REGISTERED through the seal, not edited
- **The move the seals forbid was available and refused.** Four measurements said 1.53 against a
  documented 2.0; the easy path was to write 1.53 in and close the board. Instead:
  `seals/GUE_EXPECTATION_REREGISTRATION.json`, written **before** the definitive run.
- **The seal states openly that it is NOT blind** — four measurements already existed, and pretending
  otherwise would be theatre. Its job is to fix the **procedure and the acceptance rule** so the new
  number cannot be tuned: same sampler as the CASES row (changing sampler and expectation together
  would make it unfalsifiable), same fitter, n = 40000, seeds 0–9, and
  **exp_q := round(mean,2), tol := max(0.10, 3·sd) — both DERIVED, not chosen after seeing the result.**
- **Invalidation conditions pre-listed:** 10-seed mean outside 1.5309 ± 0.10, or sd > 0.10 → *the
  discrepancy is the finding, do NOT edit CASES.*
- **RUN:** per-seed 1.5423 1.5397 1.5257 1.5252 1.5368 1.5156 1.5233 1.5434 1.5411 1.5266 →
  **mean 1.5320, sd 0.0098**, |diff| from the prior four **0.0010**. Both acceptance conditions met.
  **VALID.** Derived: **exp_q = 1.53, tol = 0.10.**
- **Applied, with the grade attached:** Brody is a one-parameter **interpolation**, not an exact GUE
  law, so **1.53 is an INSTRUMENT constant** — what the Brody MLE reads on GUE spacings — not a
  physical one, and the comment says so.
- **`exp_rho` left at 2.0 deliberately.** Berry–Robnik ρ is a GOE *fraction* bounded to [0,1], so **no
  value can satisfy it for GUE**. That row *should* fail — it is the axis saying "GUE is outside what I
  can represent," which is R-148's rail finding, not a bad expectation. Fixing it would hide the defect.
- **Result: repaired column 5/5; deployed ALL_PASS unchanged at False**, as intended — the deployed
  fitter genuinely cannot represent those cases and the gate must keep saying so.
- **Status:** CLOSED. `documented-open` retired for this item.

### R-154 — SATURATION SWEEP EXECUTED. And a guard that checked the wrong quantity.
- **18 sites, 10 files.** Only `arsrh/solar_surrogate_port.py` writes a JSON artifact; the rest print.
  But the files ARE cited in findings prose — `bulk_recovery` in 9 docs, `phase22b` in 5,
  `quadrant_marginal_test` in 3 — so "writes no json" is not "reaches nothing."
- **★ `quadrant_marginal_test.py` prints "the metric-sanity check confirms the metric is NOT
  saturated" — and `metric_sanity()` never touches `rep_int`.** It tests the **agreement metric's**
  dynamic range (do quadrant labels differ across substrates?). The sentence sits immediately after a
  clause about `rep_int`, where a reader looks for exactly that check. **A guard on one quantity,
  reported where a reader needs a guard on another** — clause 1, at the level of what a guard *covers*.
- **Measured what was never checked, in that file's own pipeline:**
  | substrate | q-bands | % rep_int_q == 0 | median rep | ρ(rep,ks) |
  |---|---|---|---|---|
  | zeta | 30 | **0.0%** | 0.4253 | −0.932 |
  | primes | 30 | **0.0%** | 0.4991 | −0.987 |
  | solar | 30 | **100.0%** | 0.0000 | **nan** |
  | poisson | 30 | 0.0% | 0.0255 | −0.923 |
  **The arithmetic ρ values are on unsaturated data and stand.** Solar is fully saturated and its ρ is
  **undefined, not ~0** — which is the mechanism confirmed on a real substrate in the exact pipeline.
- **Status:** CLOSED as a sweep.

### R-155 — ★★ ALLEN V1: MY HYPOTHESIS IS REFUTED. The banked claim STANDS, and is now better supported.
- **I filed the Allen ρ ≈ 0 as a "live retraction candidate"** (R-099/R-124), reasoning that a
  clustered substrate saturates and therefore ρ → 0 *mechanically*. **Will pushed to hold the slot;
  I held it; and the measurement now refutes my hypothesis outright.**
- **20 real Allen V1 units loaded from the 29 GB cache.** On the CLIPPED field: **16 of 20 units are
  100% saturated** (every q-band exactly 0.0000 ⇒ ρ undefined); only 4/20 give a finite ρ. Mean
  saturation **80%**. So the saturation is real and severe — *that* part of my reasoning was right.
- **BUT ON THE SIGNED FIELD IT DOES NOT RECOVER A COUPLING.** 19/20 units now give a finite ρ, and:
  **mean +0.0319 ± 0.0571, median +0.0752, 95% CI [−0.080, +0.144].**
  **Indistinguishable from zero (0.56 sem). Distinguishable from arithmetic (−0.95) at 17.2 sem.**
  Median signed rep_int = **−1.1306** — Allen is clustered, as established, and *still* uncoupled.
- **So the banked sentence — "ρ(rep_int, ks_gue) is tightly coupled on arithmetic but ~0 on Allen V1;
  rep_int carries a DIFFERENT marginal feature there" — is CONFIRMED on the repaired axis**, with
  better evidence than it originally had (19 units with a CI, vs a single number).
- **What WAS wrong was the evidential basis, not the conclusion:** the original ~0 was computed where
  **80% of the input had zero variance**, so it was reported as a correlation when most of it was
  undefined. Right answer, unsound support — now sound.
- **This is OUTCOME C of the saturation pre-commitment, reported at the prominence I bound myself to:**
  *no recovery, the prior conclusion stands.* I had built a case for the artifact reading and the data
  refused it. **A sweep that only speaks when it finds something is a publication-bias engine** — so
  this gets the same prominence as a positive would have.
- **Status:** CLOSED. R-099 and R-124's retraction hypothesis: **REFUTED BY MEASUREMENT.**

### R-156 — R-077: the exact event-weight is DERIVED and it is INSUFFICIENT. Candidate eliminated.
- **Derived, and verified exact.** In the natural extension (density 1/(log2(1+xy)²), λ = 1/x + y with
  x the future and y = q_{n−1}/q_n the past), for **fixed y**:
  P(λ ≥ A | y) = [∫₀^{1/(A−y)} dx/(1+xy)²] / [∫₀¹ dx/(1+xy)²] = **(1+y)/A**.
  The numerator collapses to 1/A independently of y (the R-083 result); **the denominator does not.**
  Verified numerically at (y, A) = (0.1,5), (0.1,20), (0.4,5), (0.4,20), (0.8,5), (0.8,20) — **exact to
  5 decimals in all six.**
- **So the event is (1+y)-biased, and since g is a function of the same past that fixes y:**
  **P(g | event) = E[(1+y)·1{g}] / E[1+y]** — exact, computable from the object's own CF, no partner.
  Had it worked, the rate formula would have returned to DERIVED and the |det| range would open.
- **IT DOES NOT WORK. The weight is negligible.** Pooled over 8 objects per stratum with binomial
  errors, the predicted conditional sits **on top of the marginal** in every branch (|t|=13, g=13:
  marginal 0.0674, predicted 0.0682) while the measurement is **0.1057, +3.30 sem** from prediction.
  |t|=5 g=25: predicted 0.0302, measured 0.0061, **−3.59 sem**. |t|=2 is fine (within ±1.8).
- **What this buys, which is not nothing:** the y-coupling — the one mechanism I had named as the
  reason the conditional wasn't derivable — is now **eliminated by derivation plus measurement**,
  not left as a vague "they're correlated through y_n." The enrichment has a different source.
  Pattern worth noting without over-reading: the enriched branch is the **middle divisor** (g = t) and
  the depleted one is g = t², in both strata where it fires.
- **Candidate for next attempt, filed not claimed:** serial correlation. A large λ_n means a large
  a_{n+1}, which enters q_{n+1} = a_{n+1}q_n + q_{n−1} and hence g_{n+1} — so events and *subsequent*
  residues are coupled in a way no per-index conditioning captures.
- **Status:** OPEN, better localised. The formula stays CALIBRATED, |det| ≤ 289 at ±12%.

- **⚠ SUPERSEDED 2026-07-28.** The +3.30 was inflated by duplicate GL₂(ℤ) orbits (R-165) and the residual does not survive out of sample (R-166). Also: the (1+y) weight moves the prediction 0.07 sem against a 3.30 sem gap, so it was never a live candidate (R-163). CLOSED.

### R-157 — the misleading sanity-check line, corrected in place
`quadrant_marginal_test.py` printed *"the metric-sanity check confirms the metric is NOT saturated"*
directly after a clause about `rep_int`, while `metric_sanity()` checks the **agreement metric**.
Corrected in place with the measured truth: **solar 100% of q-bands at exactly 0.0000, Allen V1 16/20
units at 100%, zeta and primes at 0%** — and a pointer to `rep_int_signed_q`. **Status:** CLOSED.

### R-158 — R-077: serial correlation eliminated too, and the failure is now precisely localised
- **Block bootstrap over convergent index (blocks of 50), 600 replicates.** |t|=13, g=13:
  **z_iid +3.30 → z_block +3.07** with a properly *wider* bar (n_eff/n = 0.87). **The enrichment
  survives.** So serial correlation — the candidate filed in R-156 — **does not explain it either.**
- **⚠ Caveat on my own bootstrap, stated:** the |t|=5 rows return n_eff/n **> 1** (se_block < se_iid),
  which is the signature of **overlapping blocks under-dispersing** the replicates. Those z's are not
  trustworthy; only the |t|=13 rows, where the bar correctly widened, carry weight.
- **THE FAILURE IS NOW LOCALISED, which is the actual progress.** λ_n = α_{n+1} + y_n exactly, so the
  past enters λ **only through y**. My formula therefore *should* be exact — unless **α_{n+1} is not
  conditionally independent of the past given y.** And it is not: y = [0; a_n, …, a_1] summarises the
  past *for the Gauss map*, but **the residue (p_n, q_n) mod Δ is a function of the full past that y
  does not determine**, so conditioning on y **does not screen the residue off from the future.**
- **So the open question is sharp now:** does the residue mod Δ carry information about x beyond y?
  Two candidates eliminated by derivation-plus-measurement (y-coupling, serial correlation), and the
  third is stated in a form that can be tested rather than as "they're correlated somehow."
- **Status:** OPEN, third localisation. Formula stays CALIBRATED at |det| ≤ 289, ±12%.

- **⚠ SUPERSEDED 2026-07-28.** The localisation sentence is mathematically FALSE (y_n determines the past, hence the residue) — see R-160's findings doc. The effect it localises is a window artifact (R-166), and the n_eff/n reasoning that discarded |t|=5 was the effect size re-expressed (R-171). CLOSED.

### R-159 — the migration backlog was wrong in BOTH directions; 239 is the honest number
- **The checker classified by whether the field NAME appeared in a line, not whether it appeared in
  CODE.** So `print("... where rep_int_q varies")` was counted as a migration site — the **fourth**
  time the tooling miscounted my own text (own references → own remediation → backtick prose → a
  `print()` of a plain string that the NEEDS pattern matched before FINE could be tried).
- **Fixed generally rather than patched again:** strip string literals and test what survives. Each of
  the three previous fixes was specific to the shape that had just bitten; **code-position is the
  general test.**
- **⚠ AND THE FIX OVER-CORRECTED, caught before filing.** Stripping literals wholesale made
  `df["rep_int_q"]` and `d.get("repulsion_integral")` invisible — **genuine code sites whose field
  name lives inside a string.** The backlog fell 320 → 136, which was too good. **Subscript and
  `.get` keys are now protected before stripping**, and both directions verified:
  prose → fine; `df["rep_int_q"]` → PENDING; `pc.get("repulsion_integral", np.nan)` → PENDING.
- **HONEST COUNT: 391 references — 7 migrated, 145 fine, 129 needs-signed, 110 unreviewed = 239 open.**
  My earlier **"334 open, ~310 projected to need the signed field" (R-119) was INFLATED by prose**;
  the over-correction's 136 was **deflated** by the false negative. **239 is the number.**
- **Ratchet reset a second time, deliberately and recorded** — the classifier changed, not the
  codebase, and a count that moves because the instrument improved is not a regression.
- **Status:** CLOSED as a correction. R-119's projection is superseded.

### R-160 — ★★ R-077: the PREMISE was never tested. It holds — the estimator is clean.
- **The thread was asking the wrong question.** R-158 left a sharp *why*: does the residue mod Δ
  carry information about the future beyond y? But **that** the prediction fails was never
  established. The +3.30 sem had never been compared against an orbit on which the prediction is a
  **theorem**, so *"the formula is off by 3.3 sem on cubics"* and *"this estimator is off by 3.3 sem
  on anything"* had never been separated.
- **The control: a generic real through the identical pipeline** — same `certified_cf` at
  DIG=1200/NPQ=1400, the six |t|=13 matrices **verbatim** (so only the number is flipped), same
  A=20, same 45-tail guard, same pooling, same z. For a.e. real the Gauss natural extension is
  ergodic, so (x,y) equidistributes w.r.t. 1/(ln2(1+xy)²) **exactly** — H0 by theorem.
- **RESULT, sealed outcome B.** 200 replicates: **z(g=13) mean −0.020, sd 0.985** — N(0,1) to
  within its own sem of 0.070. **P(control ≥ +3.30) = 0/200.** Instrument gate passed first:
  n_events 482 vs the cubic's 492, CF length 1163, divisor set {1,13,169} in **every** replicate.
- **The control I rejected, recorded because it was my first design:** an i.i.d. Gauss–Kuzmin
  a-sequence. Obvious, and the **wrong density** — i.i.d. partial quotients make x = [0;a_{n+1},…]
  and y = [0;a_n,…,a_1] functions of disjoint independent blocks, hence *exactly* independent,
  where a real orbit couples them by 1/(1+xy)². It would have tested a different object.
- **POWERED FALSIFIER, and it fires.** Injecting the dependence R-158 hypothesises (a_{n+1} pushed
  into the event range with prob. δ when the residue is in the g=13 class): δ = 0.00 → **−0.04**;
  0.02 → +1.22; 0.05 → **+3.51**; 0.10 → +6.49; 0.20 → +13.30. Silent when it should be, loud when
  it should be — sensitivity *and* specificity demonstrated by construction, not asserted.
- **EFFECT SIZE, which is what a mechanism must now reproduce:** +3.30 calibrates to **δ ≈ 0.047**
  — about **4.7% of g=13-residue indices** having their next partial quotient pushed into the event
  range.
- **Stronger than the seal credited:** the seal listed "the matrices M being unusual" as *not*
  excluded. Over-cautious — M is held verbatim, so that confound **is** excluded. Recorded rather
  than silently upgraded; the seal is not edited.
- **Status:** CLOSED. The premise holds. Seals `R077_CONTROL_PRECOMMIT`, code
  `arsrh/cubic/r077_control.py`, findings `arsrh/cubic/R077_CONTROL_FINDINGS.md`.

### R-161 — R-077 survives its trials factor, which had never been stated at all
- **The defect:** +3.30 (R-156) and +3.07 (R-158) are the most interesting cell of **nine**
  (stratum, g) branches. **No multiplicity correction exists anywhere** — not in the register, not
  in a seal. A per-cell z reported as a global significance is the sem-vs-CI family in a new
  costume: correct for the quantity it measures, filed in a slot owning a different one.
- **Empirical max-|z| null** (generic reals, all three strata, 200 replicates) — exact rather than
  Bonferroni, and it handles correctly that branches within a stratum are **not** independent
  (their proportions sum to 1). **95th pct = 2.633** where a single N(0,1) gives 1.96; **that gap
  is the trials factor.** All nine per-branch control means sit in [−0.15, +0.18] with sd 0.88–1.02,
  so the estimator is unbiased on **every** branch, not just the reported one.
- **RESULT: observed T = max|z| = 3.5871, p = 0.0100** (2/200). Wilson 95% CI on the p-value itself
  **[0.0027, 0.0357]** — below 0.05 across the *whole* interval, so the verdict does not hinge on
  the coarseness of 200 replicates. **Sealed outcome LE_A.**
- **Corrected p per branch** (vs the same max-|z| null): **|t|=5 g=25 → 0.0100**; **|t|=13 g=1 →
  0.0150**; **|t|=13 g=13 → 0.0150**; every other branch ≥ 0.205. **Three survive**, but g=1 and
  g=13 within |t|=13 are the same fact, so there are **two independent surviving effects.**
- **Status:** CLOSED. Seal `R077_CONTROL_PRECOMMIT_ADDENDUM_1`.

### R-162 — ★★ and the largest effect in the table had been set aside for a reason that did not apply to it
- **R-158 discarded the |t|=5 rows** on the ground that their block bootstrap returns n_eff/n > 1,
  the signature of overlapping blocks under-dispersing. **That diagnostic is correct — and it
  impeaches `z_block` only.** Under-dispersion makes the *block* z too large; it says nothing about
  `z_iid`, which was never impeached. So the whole row was dropped on a criticism of one column.
- **Consequence:** the **largest single effect in the table** — |t|=5, g=25 at z_iid = **−3.5871**,
  look-elsewhere-corrected **p = 0.0100**, the *best* corrected p of all nine — was set aside, and
  both R-156 and R-158 built their argument on |t|=13, g=13 (z = +3.2954, corrected p = 0.0150)
  instead. **R-156's cell does survive**; it is simply not the strongest, and the strongest points
  the **other way** — depletion, not enrichment.
- **Correct-fact / wrong-slot, mine, again:** the n_eff/n diagnostic was right, and was applied to a
  slot it did not own.
- **A structural pattern, filed as a CANDIDATE and explicitly not a finding.** In both live strata
  Δ = t², so g ∈ {1, t, t²} and the transfer factor g²/Δ ∈ {1/t², **1**, t²}. The enriched branch is
  g = t in both — **exactly the branch where the transfer law λ′ = (g²/Δ)λ is neutral (λ′ = λ)**.
  This is the "it all fits together" shape, which is the signal to run discipline, not the reward:
  it is a **rhyme until proven an identity**, and it is recorded here so it can be tested rather
  than assumed.
- **Status:** OPEN. The third localisation, if pursued, must address **|t|=5 g=25 depletion**

- **⚠ PARTIALLY WITHDRAWN 2026-07-28 by R-167**, and the rest closed by R-166. The *logic* stands (a diagnostic impeaching z_block was over-applied to drop z_iid); the *conclusion* does not — |t|=5 g=25 is the most duplicated cell (4×), not the strongest effect. No third localisation is to be pursued: R-166 voided the effect.
  alongside the |t|=13 enrichment — not the enrichment alone.

### R-163 — R-156/R-158's numbers had no committed provenance, and two prose errors
- **The analysis code lived in `/tmp`.** Both entries banked numbers into this register from a
  session scratch directory; the prose was committed, the code was not. **A number whose generating
  code is in a temp directory has no provenance** — it cannot be re-run, audited, or
  regression-tested. Eighth instance of [[knowledge_does_not_propagate]], and the first where the
  stranded artifact is *the evidence for a banked claim* rather than a repair.
- **Fixed:** `arsrh/cubic/r077_conditional.py`, a **verbatim** consolidation — deliberately not an
  improved version, so it reproduces what was banked. It does: **+3.30 iid, +3.07 block, predicted
  0.0682 vs measured 0.1057, n_events 492**, and the (1+y)/A check to 1e-16. It also prints the
  **trials factor R-156 never stated: 9 branches.**
- **Prose error 1:** R-156 says "pooled over **8** objects per stratum." The |t|=13 stratum has
  **six** (`collect_cyclic`'s `per` is a cap; only 6 cubics in the box have |t|=13). The z is
  unaffected — the pooling used what was there — but the stated n is wrong.
- **Prose error 2, and it is the load-bearing one:** the **(1+y) weight moves the |t|=13 g=13
  prediction from 0.0674 to 0.0682 — 0.07 sem — against a 3.30 sem gap. It is 47× too small to have
  ever been a candidate explanation.** R-156's "the weight is negligible" is correct but
  under-stated: this apparatus has **no power to test the weight**, and the weight was never the
  live hypothesis, so it is not really *a candidate eliminated*. Stated in the seal **before** the
  run so it could not afterwards be presented as an insight.
- **Status:** CLOSED as a correction. R-156's "8 objects" and its framing of the weight-elimination
  are superseded.

### R-164 — the propagation watcher's own scope had frozen permanently
- **`_measure_shared()` returned the cache unconditionally** whenever the file existed and **never
  re-measured** — so the watcher's SHARED set froze at first run, and being **committed**, froze
  identically for every clone. The next module to cross SHARED_MIN would have been silently missed:
  the same failure the hand-curated list had when it omitted `ars_classify.py` at 51 importers.
- **Three-state honesty, and this is the middle state.** Not "broken" and not "fine" but **correct
  now and unable to stay correct.** Measured at fix time: fresh == cached exactly, 27 modules, so
  **no scope changed and no prior verdict moves.**
- **Fingerprinted on file CONTENTS, not the path set** — a module crosses SHARED_MIN when *import
  lines* change, which happens by **editing** existing files at least as often as by adding them, so
  a path-set fingerprint would have left a silent recall gap of exactly the kind this watcher exists
  to catch. Cost of hashing all 553 tracked `.py`: **0.006 s.**
- **Verified it can fire:** fingerprint moves on add, on delete, and on edit; restores on revert.
- **Status:** CLOSED.

### R-165 — ★★★★ THE POOLED STRATA CONTAIN DUPLICATE ORBITS. Every pooled z in this thread was inflated.
- **Found by the review agent; verified independently by me before acceptance.**
  `gate0e_precision.collect_cyclic` enumerates **polynomials** over a coefficient box and **dedups
  by nothing**. Many are **GL₂(ℤ) translates of the same cubic irrational** and produce *identical*
  (g, y, λ) orbits.
- **Verified exactly, not statistically.** At |t|=13, polys **(−7,0,7)** and **(−4,−11,1)** have roots
  −0.93900107534756 and −1.9390010753476 — **differing by exactly 1.0** — so their CFs agree from
  a₁ on. Two independent implementations (root-difference; CF-tail-signature search) agree on the
  orbit counts: **|t|=5: 8 polys → 2 orbits (4×). |t|=13: 6 → 3. |t|=17: 6 → 3. |t|=29: 4 → 2.**
- **The arithmetic:** duplication leaves `meas` and `pred` **unchanged** and multiplies n by k, so
  **|z| inflates by exactly √k**. |t|=13 g=13: **+3.295 → +2.378**. |t|=5 g=25: **−3.587 → −2.176**.
- **RATIOS ARE SAFE, COUNTS ARE NOT.** Duplication scales numerator and denominator together, so
  gate0e's meas/pred, bias, rms and **the sealed ±12% band are unaffected**. Every χ², every "excess
  over binomial", and every pooled z **is** affected.
- **And the fact was already in the repo, as a display label.** `gate0e_precision.py:200` prints
  *"'objs' is now DISTINCT DISCRIMINANTS: … correlated objects are one witness."* It was wired into
  a **printout** and never into the pooling or the variance. Worse, discriminant count is not even
  the right proxy — |t|=5 has **1 discriminant but 2 orbits**, |t|=13 **1 discriminant but 3**.
  **GL₂(ℤ)-orbit equivalence is the correct unit.** Ninth instance of
  [[knowledge_does_not_propagate]].
- **Repair, non-destructive:** `gl2z_orbit_reps` + `collect_cyclic_dedup`; `collect_cyclic` retained
  **bit-identical** with a warning in its docstring. Fixture
  `CYCLIC_STRATUM_POOLS_DUPLICATE_ORBITS`.
- **Status:** CLOSED as a defect; downstream recomputation tracked in R-166.

### R-166 — ★★★ THE ANOMALY DOES NOT EXIST OUT OF SAMPLE. R-077's third localisation is VOID.
- **The published numbers come from convergent indices < ~1150 — which is simply where DIG=1200 ran
  out.** That is a **window**, not a process. The same orbits extended deeper give a **disjoint**
  remainder on which the identical quantity can be measured.
- **My run, DEDUPED orbits at DIG=6000 (5× depth), remainder carrying 4.5× the statistical weight:**

  | segment | excess on the g=t branch | sem |
  |---|---|---|
  | published window (idx < 1150) | **+0.03127** | ±0.00834 → **+3.75 sem** |
  | disjoint remainder (idx ≥ 1150) | **+0.00133** | ±0.00394 → **+0.34 sem** |

  **H1** ("the window excess is real and constant") predicts +0.03127 in the remainder; observed
  +0.00133 → **rejected at 7.6 sem**. **H0** ("no excess") predicts 0; observed **+0.34 sem,
  p = 0.736 → consistent.**
- **Independently corroborated at a different depth by a different implementation:** the review
  agent, at DIG=12000, got window **+0.03119 ± 0.00833**, remainder **+0.00408 ± 0.00259**, H1
  rejected at **10.5 sem**, and the same dedup counts (2/3/3/2). Two implementations, two depths,
  one verdict.
- **So there is no residue→future coupling to localise.** R-158's third localisation is **void** —
  not because the mechanism was wrong, but because **the effect it sought to explain is a property
  of one frozen window.**
- **Status:** CLOSED. R-077 stays **CALIBRATED at |det| ≤ 289, ±12%** — that band is a ratio and
  survives. What does not survive is the claim that an unexplained third coupling had been localised.

### R-167 — ★★★ MY OWN INSTRUMENT GATE CHECKED THE QUANTITY THE DEFECT INFLATES. R-161 WITHDRAWN.
- **`R077_CONTROL_PRECOMMIT_ADDENDUM_1` verdict `LE_A_SURVIVES` (T = 3.5871, p = 0.0100) is
  WITHDRAWN.** Seal `R077_LE_A_WITHDRAWAL`. The seal is **not edited** and its acceptance rule is
  **not changed**: p ≤ 0.05 fired correctly **on corrupted input**.
- **Why the gate could not fire.** It compared control vs cubic **`n_events`** within 25% — and
  `n_events` is **exactly the quantity duplication inflates**. It passed (640/646/482 vs
  626/652/492) *because* the data was corrupted in the matched way. The control generated one
  **independent** real per matrix (6 independent orbits); the cubic side had 6 polynomials carrying
  only **3**. Same event count, different degrees of freedom.
- **This is R-157 recurring in my own new work, two days after I corrected it** — a guard pointed at
  the wrong quantity. There it was `metric_sanity()` checking the agreement metric while the prose
  claimed `rep_int`; here it is `n_events` checking the inflated statistic.
- **The violated clause has a name and a live guard: `unit_of_analysis`, clause 4.** The cubic side's
  unit was the **polynomial**; the control's was the **independent orbit**. `commensurable.py` is
  live (27/27, run by pytest), **refuses** an undeclared `unit_of_analysis`, and its own specificity
  suite contains a case distinguishing `'polynomial'` from `'field'` — *this exact distinction*.
  **Neither `r077_control.py` nor `r077_lookelsewhere.py` imports it.**
- **⚠ Honest limit on the counterfactual, because the flattering version is not established:** the
  guard would have **forced** `unit_of_analysis` to be declared on both sides. It would **not
  necessarily have caught this** — a careless declaration of "cubic object" on both sides passes,
  because the guard tests declared-metadata equality, not whether the declaration is *true*.
  **Necessary, not sufficient.** The sufficient fix is that the unit for a pooled arithmetic object
  is the **GL₂(ℤ) orbit**, and that fact now lives at the call site (R-165), not in a findings doc.
- **What survives:** R-160's control **stands and is worth more than when banked** — 200 generic-real
  replicates give z mean −0.020, sd 0.985, which **validates the (1+y) derivation as correct for
  a.e. x**. Its injection arm stands (run entirely on generic reals). What does **not** survive is
  the inference I drew from it — *"the premise survives"* — which compared duplicated cubic data
  against non-duplicated control data.
- **R-162 partially withdrawn.** Its *logic* stands: R-158's n_eff/n>1 diagnostic impeaches `z_block`
  only and was over-applied to drop `z_iid`. Its *conclusion* does not: |t|=5 g=25 is not the
  strongest surviving effect, it is **the most duplicated (4×)**. R-158 and I were both wrong about
  that row, for different reasons, and the row is weak.
- **Status:** CLOSED as a withdrawal.

### R-168 — sixth instance of tooling-counts-itself, and the polarity is inverted
- The watcher flagged **`tests/test_known_defects.py`** — the **regression-fixture file** — for
  containing repair language, and went 15 → 17 (a REGRESSION) on my own defect-10 fixture.
- **The five prior faces** were own references → own remediation → backtick prose → a `print()` of a
  plain string → one watcher flagging another watcher's comment. **This one is the opposite
  polarity:** a fixture file is not a place where repairs *strand*, it is the place they **land**.
  **R-142** established that a test file is in the shared path *by construction* — which is exactly
  why the orphaned guards were moved there. So the watcher was flagging **the one location the
  doctrine says is correct.**
- **Excluded by PATH, not filename**, so any new test file inherits it — the property that matters
  ("a test is in the shared path by construction") belongs to the directory, not the name. Scope
  verified: `tests/` excluded, `arsrh/` not, `testsuite/` not (the prefix carries its slash).
- **Status:** CLOSED. Back to 15, ratchet green.

### R-169 — the propagation backlog CLOSES: 15 → 0, and eleven of the fifteen were real
- **Six private symbols promoted to public API, non-destructively.** Signature A fires exactly when
  the public API failed to offer something and callers reached past it rather than fixing it. Each
  promotion is an **alias** — `public = _private` — so the private name stays **bit-identical**
  (banked numbers came off calls to it) and the two are the **same object**, meaning no call site
  can change behaviour. Alias identity asserted for all six, and fixtured.

  | symbol | → public | consumers |
  |---|---|---|
  | `trace_map_dimension._potential` | `potential` | **7**, across three packages |
  | `universality._ks_pvalue` | `ks_pvalue` | 2 |
  | `surrogates._fit_hawkes_exponential` | `fit_hawkes_exponential` | 1 |
  | `surrogates._simulate_hawkes` | `simulate_hawkes` | 1 |
  | `transition_diagnostic._distance_trajectory` | `distance_trajectory` | 1 |
  | `allen_depth._session_tasks` | `session_tasks` | 1 |

- **⚠ A recall limit that bit, and the check that caught it.** The repo expert returned **six**
  consumers of `_potential`; there are **seven**. `approximability/panel_A_gate.py` wraps the symbol
  onto a **continuation line**, and a line-oriented grep cannot see it. Found only because the
  post-edit check was *"no residual private reference anywhere in the repo"* rather than *"I updated
  every file on the list I was given."* **Verify against the repo, not against the inventory.**
- **`population_fingerprint._corr_eig/_fp/_f` was NOT a propagation gap — it was a watcher
  specificity gap** (fourth pass). Ten `cross_substrate/` modules share them: ordinary intra-package
  reuse. The dotted intra-package test could never fire, because `from population_fingerprint import
  _fp` is a **bare** module import resolved by a `sys.path` insert, so there was no `dst_pkg` to
  compare. The watcher now resolves the module to a **file** and asks whether it sits in the
  importer's own directory — the property the rule is actually about, independent of how the import
  is spelled. **Removed 10 false hits.**
- **`box_dim_windowed` was a GENUINE un-propagated repair, and the saturation family again.**
  `sturmian_hamiltonian_run.box_dim` (**imported by 10+ modules**) selects `m = counts > 1`, which
  **includes the fine-scale regime where every eigenvalue lands in its own box**, so counts → N and
  the log-log slope flattens toward a value set by the **sampling** rather than by the set. The
  windowed fit was written and validated in a leaf module nothing imports. **Known-answer check:**
  on uniform points (true D = 1.0), deployed reads **0.9278**, repaired **0.9666** — the deployed
  estimator is **biased low by the saturated tail**. Propagated with `box_counts`, so the fit
  **range** is a caller's choice rather than baked into the estimator; `box_dim` retained
  bit-identical. Fixture `BOX_DIM_FITS_THROUGH_SATURATED_TAIL`.
- **The two `verify/tier3_chirp_and_cap.py` hits are LOCAL-BY-DESIGN, and the locality is the
  point.** Its header declares it an *"independent verification harness (read-only)"*: it holds the
  deployed **and** fixed variants side by side to measure the difference, and re-implements
  `unfold_semicircle_R` rather than importing it **because independence from the code under test is
  what makes the verification worth anything.** Propagating either variant out of that file would
  destroy the comparison it exists to make.
- **`run_level_st_v2` is NOT-A-REPAIR** — signature C matched the `_v2` suffix, but it is a
  phase-local driver and the watcher itself reports *"shared stem: none found."* A second version of
  an **analysis** is not a repair of a shared **function**.
- **A stale manifest entry, marked rather than deleted.** `validate_fitters.py:101` sat as
  `documented-open`; R-153 re-registered that expectation through a seal on 2026-07-27, so the
  category now reads **0** because the watcher finds no hit — an entry that silently stops being
  counted is exactly the **unmarked-stale-table** pattern this repo keeps producing. Marked
  SUPERSEDED in place.
- **Ratchet 15 → 0, recorded separately from the 2026-07-27 reset** so the two causes stay
  distinguishable: that one was a **model** change with no code change; this one is **mostly code**.
- **Status:** CLOSED. Backlog empty for the first time.

### R-170 — ★★★ the |t|=5 "under-dispersion" RESOLVED: it is GENUINE, and the diagnostic inverted the ranking
- **The open item.** R-158 discarded the |t|=5 rows because their block bootstrap returns
  **n_eff/n > 1** (se_block < se_iid), read as *"overlapping blocks under-dispersing"* — a defect.
  The review agent tested orbit duplication as the rival cause and found it only partly holds
  (|t|=13 0.94→0.79, |t|=29 0.77→0.66, but |t|=5 **stays at 1.47** and |t|=2 **rises**), then
  correctly refused to turn "not refuted" into a verdict.
- **THE DIAGNOSTIC WAS NEVER CALIBRATED.** Its null was assumed to be 1.0. Measured, on the real
  data through **r077d.py's own resampler**, with a **jointly-permuted** control — same (G,Y,L)
  triples, serial order destroyed, so **the truth is 1.000 by construction**, 60 shuffles each:

  | stratum | real | shuffled null (truth 1.000) | real vs its OWN null |
  |---|---|---|---|
  | \|t\|=2 | 1.194 | 1.163 ± 0.133 | **+0.24 sd — nothing** |
  | **\|t\|=5** | **1.525** | **0.904 ± 0.142** | **+4.39 sd — GENUINE** |
  | \|t\|=13 | 1.002 | 0.711 ± 0.110 | +2.65 sd — genuine |
  | \|t\|=17 | 0.877 | 0.722 ± 0.087 | +1.77 sd — marginal |
  | \|t\|=29 | 0.723 | 0.512 ± 0.087 | +2.43 sd — genuine |

  **The null ranges from 0.51 to 1.16 and is stratum-dependent, so comparing the raw value to a
  nominal 1.0 is invalid in both directions.**
- **AND THE READING WAS EXACTLY INVERTED.** R-158 kept |t|=13 (raw 1.002 ≈ 1, *"the bar correctly
  widened"*) and discarded |t|=5 (raw 1.525 > 1, *"under-dispersing"*). Calibrated, **|t|=5 carries
  the STRONGEST genuine serial structure of all five strata (+4.39 sd) and |t|=2 carries none.**
  The row that was thrown out is the one the diagnostic most supports.
- **Third distinct error on the same discarded row**, now: R-162 (a diagnostic that impeached
  `z_block` applied to drop `z_iid`), R-165 (that row is also the **most duplicated**, 4×), and now
  R-170 (the diagnostic's null was never measured). *Three independent mistakes converging on one
  row is not bad luck — it is what happens when a row is discarded before it is understood.*
- **⚠ THIS DOES NOT REVIVE THE SUBSTANTIVE CLAIM, and must not be read as doing so.** R-166 killed
  the enrichment **out of sample** on deduped orbits at 5× depth (remainder +0.00133 ± 0.00394,
  H1 rejected at 7.6 sem). A methodological rehabilitation of one variance diagnostic changes
  nothing about an effect that does not exist beyond its own window. R-077 stays **VOID**.
- **⚠ MECHANISM OF THE INSTRUMENT'S BIAS: UNIDENTIFIED, and three candidates are ELIMINATED.**
  (i) **Block length** — synthetic i.i.d. sweep shows the estimator is clean at n/B ≥ 25 (0.90–1.23)
  and excellent at n/B ≥ 50; every stratum sits at **n/B = 44…159**, so block length is not it.
  (ii) **Event-conditioning** — synthetic i.i.d. with a rare-event subset inside each replicate
  returns 1.01–1.09, not 0.71. (iii) **Small success counts** — swept 17→101 expected successes,
  synthetic stays in **[0.92, 1.18]**. Something in the real data's structure survives joint
  shuffling and biases the diagnostic; I have not found it, and I am not going to name a mechanism
  I could not reproduce.
- **The reusable rule, which is the part that outlives this row:** *a variance diagnostic must be
  compared to its own measured null, not to its nominal value.* A shuffled surrogate costs one line
  and would have prevented all of this. Cf. [[synthetic_validate_fitters]] — the fitters got their
  rails checked; the variance estimator never did.
- **My own first pass had a defect, recorded rather than quietly fixed:** it CONCATENATED orbits
  before computing the autocorrelation, which manufactures **positive** long-range correlation from
  a difference in means. The Bartlett ratios in `r077_blockboot_diagnosis.py` are contaminated and
  are superseded by the calibration run.
- **Status:** CLOSED. Code `arsrh/cubic/r077_blockboot_calibration.py`; the superseded first pass is
  retained as `r077_blockboot_diagnosis.py` with its defect documented in place.

### R-171 — ★★★★ MECHANISM FOUND: the reliability diagnostic was the EFFECT SIZE re-expressed
- **R-170 left the mechanism unidentified after eliminating three candidates.** Found. It is not
  subtle once seen, and it invalidates the diagnostic's use entirely rather than just biasing it.
- **`r077d.py` computes** `n_eff/n = se_iid² / se_block²` with
  `se_iid = sqrt(pred·(1−pred)/n)` — evaluated at the **PREDICTED (marginal)** proportion — while the
  bootstrap's `meas` disperses around the **OBSERVED event-conditional** proportion. When those
  differ — **which is exactly when there is an effect** — the two variances are evaluated at
  different p, and their ratio is, in closed form:

  > **n_eff/n = pred(1−pred) / (meas(1−meas))**

- **Verified two independent ways.**
  1. **Closed form vs the measured shuffled null** (deduped, truth 1.000): |t|=2 predicts 1.152 vs
     measured **1.163**; |t|=5 predicts 0.862 vs **0.904**; |t|=13 predicts 0.673 vs **0.711**.
     Within 1–5%, **in both directions**.
  2. **A ladder that rebuilds the synthetic case one real property at a time**: L1 i.i.d. matched
     **1.065 / 1.138 / 1.046** → L2 + real λ marginal **1.058 / 0.945 / 1.053** → **L3 + the real
     (G,L) joint 0.687 / 0.886 / 0.547** → L4 the real permuted array **0.689 / 0.901 / 0.537**.
     **The drop is entirely at L2→L3 and L3 reproduces L4** — i.e. the within-index (G,L)
     dependence, and nothing else, is the cause.
- **THE CLINCHER.** R-158 cited **|t|=5, g=25 (n_eff/n = 4.956)** as proof the bootstrap was broken.
  The closed form gives **4.798 from the effect size alone — no bootstrap, no simulation, a 3.2%
  match.** That cell is the most strongly *depleted* branch in the whole table (meas 0.0061 vs pred
  0.0302), and its "under-dispersion" **is** that depletion, arithmetically.
- **SO IT IS NOT AN INDEPENDENT CHECK.** Enrichment (meas > pred) drives the diagnostic **below 1**;
  depletion (meas < pred) drives it **above 1**. R-158 used it as an independent verdict on whether
  a z could be trusted, and it is **algebraically the same number as the z it was judging**. A
  diagnostic that moves with the effect cannot adjudicate the effect.
- **⚠ THE Z-TEST ITSELF IS FINE, and this distinction matters.** Using the null-hypothesis p in the
  standard error is correct for testing `meas` against `pred` — textbook. What is wrong is
  **comparing that null-based se to a bootstrap se that disperses around the observed value.** Two
  different quantities, one ratio. The defect is in the diagnostic, not in the test.
- **REPAIR + verification.** `neff_calibrated` evaluates at the observed value. Shuffled control,
  truth 1.000: **deployed (at pred) 1.168 / 0.898 / 0.639 / 0.489** — spanning 0.49 to 1.17 —
  **repaired (at meas) 1.014 / 1.060 / 0.950 / 0.970**, all within 6%. Fixture
  `NEFF_DIAGNOSTIC_IS_THE_EFFECT_SIZE_RE_EXPRESSED`. **Sibling sweep done and empty**: the only two
  other bootstrap sites (`phase37/crcns_pillar2_ratematch.py`, `phase34e/run_berry_robnik.py`) read
  percentile intervals straight off the bootstrap and never form the ratio.
- **Secondary, on the ORIGINAL published values**, which were computed on duplicated orbits: the
  residual actual/formula is **~1.8 at |t|=5 (dup 4×)** and **~1.3 at |t|=13 (dup 2×)**, tracking
  **√(dup factor)** — duplication independently inflates the diagnostic, exactly as R-165 predicts,
  since identical copies make replicates more alike.
- **R-170 STANDS and is now explained.** The shuffled null already absorbs the pred/meas mismatch,
  so the residual real-vs-null (**|t|=5 at +4.39 sd**) remains genuine serial structure. And R-166
  is untouched: the enrichment still does not exist out of sample. **R-077 stays VOID.**
- **Status:** CLOSED. The last open item from the R-077 arc.

### R-172 — gate0e RE-RUN DEDUPED: three "excess over binomial" verdicts RETRACTED, the trend SURVIVES
- **The last owed action from `R077_LE_A_WITHDRAWAL`.** gate0e pooled one object per **polynomial**;
  several per stratum are GL₂(ℤ) translates of the same irrational (R-165), so `z = (K−N·pred)/sd`
  scaled as **√k** and `χ² = Σz²` as **k**.
- **Non-destructive by construction:** a `GATE0E_DEDUP` env switch, default **OFF**, writing to a
  separate file. **Verified: the default path reproduces the banked JSON bit-identically** (re-run
  and diffed, `True`), so the deployed record is intact and auditable beside the correction.

  | block | χ²/df dup → dedup | p dup | **p dedup** | |
  |---|---|---|---|---|
  | `by_a` | 1.82 → **1.03** | 1.2e−02 | **0.42** | RETRACTED |
  | `by_lambda` | 1.95 → **1.07** | 5.8e−03 | **0.38** | RETRACTED |
  | **`by_conditional_g`** | 2.63 → **1.19** | **6.4e−05** | **0.24** | **RETRACTED** |
  | `both_corrections` | 3.31 → **1.83** | 1.5e−04 | **0.043** | weakened |

  **Three of four "EXCESS over binomial" readings become "consistent with binomial."** df is
  unchanged (21→21, 11→11) — dedup removes duplicate polynomials *within* strata, never a stratum.
- **THE PREDICTION HELD TO ~1%, and it was made before the run.** Every ratio-shaped quantity is
  duplication-invariant: bias +0.0817 → **+0.0819**, rms 0.2272 → **0.2252**, precision 25.5% →
  **25.3%** (`by_a`; the other three blocks likewise). **The sealed ±12% band stands.**
- **★ AND THE SYSTEMATIC SURVIVES, which is the part that matters.** The trend on log|det| is not an
  artifact: `by_conditional_g` slope **−0.0399 ± 0.0112 (3.56 sem) → −0.0378 ± 0.0111 (3.40 sem)**.
  The slope is a regression **across strata** and its sem comes from residual scatter over the 21
  rows, not from within-stratum counts, so duplication cannot touch it.
  > **The dispersion verdict was an artifact; the systematic is real.** The formula degrading with
  > |det| is what keeps R-077's grade at **CALIBRATED rather than DERIVED**, and it is untouched.
  > What is retracted is only the claim that residual scatter *exceeds binomial*.
- **⚠ AND I WAS WRONG ABOUT gate0f — checked, not assumed.** I had told the user gate0f's measured
  JSON also carried duplicated-orbit statistics. **It does not.** gate0f computes **no pooled z or
  χ²**: its outputs are censuses over coefficient boxes plus single-object facts, and it calls
  `collect_cyclic` once to take **one** object (`by[43][:1]`). Re-ran it after a prose-only edit and
  the JSON is **identical**. It needed a claim corrected, not a re-run.
- **The corrected gate0f claim:** it reported the witness count as **distinct discriminants**. Wrong
  unit, and it **undercounts** — |t|=5 has **1 discriminant but 2 GL₂(ℤ) orbits**, |t|=13 has **1 but
  3**. Discriminant count is a **lower** bound and polynomial count an **upper** one. The direction is
  conservative for gate0f's own [W] argument (true witnesses are *more* numerous than quoted), so its
  conclusion stands and only the statistic quoted for it was wrong.
- **Status:** CLOSED. Notice `arsrh/cubic/GATE0E_DEDUP_NOTICE.md`; both JSONs retained.

### R-173 — ★★★ THE CLIP HAS AN **UPPER** RAIL TOO, AND 56% OF KURAMOTO SITS ON IT
- **Found while scoping the coordinate-store recompute.** R-093/R-094 characterised
  `np.maximum(0, 1−R₂)` as saturating to **0** for clustered processes — a *lower* rail that hides
  magnitude. It also has an **upper** rail, and nobody had looked: when **R₂ ≡ 0** (no pairs in the
  correlation range) the integrand is **1.0 across the whole mask**, so the integral returns the
  **mask width**, exactly **0.85**.
- **Measured on the banked kuramoto block: 3,538 / 6,298 values are EXACTLY 0.85 — 56.2%.**
  (Next most common: 0.75 at 3.6%, then 0.896…, a genuine measurement, at 2.5%.) Only 20 values
  (0.3%) sit on the documented *lower* rail.
- **It collapses distinct values, like the Brody two-ended saturation.** Four oscillators all
  reporting `rep_med = 0.85` have signed values **0.523, 0.689, 0.716, 0.598** — different
  substrates of behaviour mapped onto one number. **Identity-collapse, not just magnitude-loss.**
- **So the store's kuramoto coordinates are worse than the notice said.** `STALE_AXES_NOTICE.md`
  quantified `ARS.rep_med` saturation as "16.6% exactly 0" across the store and flagged pvc-11's
  79.2% zeros. **It never counted the upper rail**, because nobody knew it existed — so kuramoto,
  the single largest block, read as "mostly fine" when **56% of it is a rail**.
- **Status:** OPEN — recompute running; the repaired `rep_med_signed` is what replaces it.

### R-174 — the coordinate store's recomputability, MEASURED rather than assumed
- **436,040 records; 20,801 carry `I.8_brody_q`, 8,106 carry `ARS.rep_med`.** The question is not
  "should we recompute" but **"can we"** — and it is decided per substrate by whether the *raw
  input* survives, because **`source_artifact` points at a RESULTS TABLE, not the raw object**
  (~500 bytes/cell: `rep_int_per_q` and friends, no spike times). [[no_forbidden_recompute]]'s
  "bank the raw object" was not done, so recompute means regenerating the input.
  | tier | n | status |
  |---|---|---|
  | **kuramoto** | 6,361 | **SIMULATED** — parquet banks (K, seed, N) for all 63 cells, seeds {0,1,2}. **Exactly regenerable, no external data.** RUNNING. |
  | pvc-11 | 1,159 | needs `crcns_cache` — **present, 630 M** |
  | allen-np | 544 | needs `allen_cache` — **present, 29 G** |
  | arithmetic (zeros/primes/Maass) | ~30 | regenerable from the arithmetic |
  | **Tier B — `I.8_brody_q`** | **19,619** | `"generated (…)"` pipelines over the big caches (allen-hpf-cell 4,326; brocot.fm 4,006; buzsaki-port-cell 4,006; …). Separate job. |
- **So `rep_med` is 8,098/8,106 recomputable; `brody` is only 1,182/20,801.** The two stale axes are
  in completely different positions, which the notice did not distinguish.
- **⚠ AND A COSTING ERROR OF MINE, THE SAME SHAPE gate0f WAS WRITTEN ABOUT.** I timed `classify` on
  `sim.spikes[0]` — **n = 157, 0.23 s** — and projected the sweep at **6 minutes**. The **median**
  oscillator has **n = 2,304** and the max **11,247**, costing **2–3 s** each: the true cost is
  ~4 min/cell, **~4.5 h**. **A thin slice of the sampling frame, again.** Time the median, never
  the first element.
- **Status:** OPEN — kuramoto running, the rest scoped and unstarted.

### R-175 — kuramoto RECOMPUTE COMPLETE: the clip reported 58 clustered cells as REPULSIVE
- **Reproduction check passed first: 6,298 / 6,298 deployed values match the banked parquet, 0
  mismatches.** The simulation, seeds, unfolding and q-banding were all re-entered correctly, which
  is the only thing that licenses trusting the repaired numbers beside them. 4.0 h, 63 cells.
- **THE UPPER RAIL, now quantified.** 3,538 cells (**56.2%**) read exactly **0.85**. Their true
  signed values span **+0.403 … +0.850** — a **0.447-wide range collapsed onto a single number.**
  None of them are clustered, so this rail destroys *how repulsive*, not the sign.
- **★ AND THE SIGN INVERSION, which is worse than anything R-093/R-094 documented.** 78 cells are
  genuinely clustered (signed < 0). The deployed axis read **exactly 0.0 for only 20** of them — and
  **strictly POSITIVE for the other 58**, i.e. it reported *repulsion* for oscillators that are
  *clustering*. Their deployed median is **+0.2048** against a true signed median of **−0.6880**;
  the worst single cell reads **+0.1065 where the truth is −2.4622**, and one reads the **+0.85 rail**
  while being clustered.
  > The clip integrates only the POSITIVE excursions of (1−R₂), so a net-clustering process with any
  > repulsive range reports as repulsive. **Not magnitude loss — the opposite class.**
- **Aggregate:** 5,146 / 6,298 cells changed (**81.7%**). Deployed mean **+0.8223** vs signed
  **+0.6601** — the clip inflates by **+0.1622 (24.6%)**. Deployed min **0.0000**, signed min
  **−4.4842**. `clipped ≥ signed` on **every** cell, as the algebra requires.
- **Written to `coordinates/kuramoto.repaired.jsonl`** carrying both axes plus the banked value per
  cell; the original jsonl and parquet are untouched.
- **Status:** CLOSED for kuramoto. pvc-11 (1,159), allen-np (544) and Tier B (19,619 brody) remain.

### R-176 — pvc-11 and allen-np RECOMPUTED. 449 cells reported the OPPOSITE CLASS.
- **Reproduction passed on all three substrates before any repaired number was read:**
  kuramoto **6,298/6,298**, pvc-11 **1,159/1,159**, allen-np **544/544** — **zero mismatches**,
  and allen-np's 544 is exactly the coordinate store's allen-np count.

  | substrate | recs | at 0.0 rail | changed | clustered | **SIGN-INVERTED** | dep median | signed median | signed min |
  |---|---|---|---|---|---|---|---|---|
  | kuramoto | 6,298 | 20 | 5,146 | 78 | **58** | **+0.8500** | +0.6584 | −4.4842 |
  | pvc-11 | 1,159 | **918 (79.2%)** | **1,159 (100%)** | **1,157** | **239** | **0.0000** | −0.7015 | −5.5694 |
  | allen-np | 544 | **385 (70.8%)** | **544 (100%)** | **537** | **152** | **0.0000** | −0.7240 | −2.6722 |
  | **total** | **8,001** | | **6,849 (85.6%)** | **1,772 (22.1%)** | **449 (5.6%)** | | | |

- **★ THE HEADLINE: 449 cells were reported as REPULSIVE while genuinely CLUSTERING.** Not a lost
  magnitude — **the opposite class**, on the axis whose whole job is to tell those apart. The clip
  integrates only the positive excursions of (1−R₂), so a net-clustering process with any repulsive
  range comes out positive.
- **pvc-11 is total.** Median exactly **0.0000**, mean **+0.0049**, against a true median of
  **−0.7015** — **not one of its 1,159 values was correct**, and 1,157 of 1,159 units are clustered.
  The block the notice already flagged as worst was worse than flagged.
- **The two rails are substrate-specific, which is why one summary statistic never characterised
  this store.** kuramoto is dominated by the **UPPER** rail (56.2% at 0.85, median +0.85);
  pvc-11 and allen-np by the **LOWER** rail (79.2% / 70.8% at 0.0, median 0.0). *Same clip, opposite
  failure modes, opposite directions of bias.*
- **`clipped ≥ signed` holds on all 8,001 cells**, as the algebra requires — the one invariant that
  survives, and the reason the deployed value is usable as an **upper bound** and nothing else.
- **⚠ A miscount of my own, caught in the summary table.** My first combined roll-up read kuramoto
  as *0 clustered, 0 inverted* — because the kuramoto report JSON predates the
  `n_clustered_signed`/`n_sign_inverted` keys and my `.get(..., 0)` silently returned zero. **A
  missing field defaulted to a number that reads as a finding.** Recomputed from the record files;
  truth is 78 and 58. *Never `.get(key, 0)` on a schema that changed between runs — the default is
  indistinguishable from a measurement.*
- **Coverage:** 8,001 of the store's 8,106 `ARS.rep_med` values. The remainder are the small
  arithmetic substrates (~100) and 8 non-file-backed. **Tier B — 19,619 `I.8_brody_q` values —
  remains**, and now has a concrete reason: the Brody axis has the same two-ended rail structure
  this just made quantitative for `rep_med`.
- **Status:** CLOSED for all three. Files `coordinates/{kuramoto,pvc-11,allen-np}.repaired.jsonl`,
  each carrying both axes plus the banked value per cell; originals untouched.

### R-177 — ★★★★ THE CLASS LABEL INHERITS THE RAIL: "BL = Poisson noise" is 99.9% CLUSTERED
- **`joint_quadrant_diagnostic` assigns the `primary` label by THRESHOLDING THE CLIPPED FIELD:**
  `BL: rep_int < 0.10 → "Poisson noise"`, `TR: 0.10–0.55 → Wigner-class`, `BR: ≥ 0.55 → uniform-like`.
- **The axis floor is 0, so clustering has nowhere to go but BL.** A clustered process pins to
  0.0000 and is labelled **Poisson noise** — *the scheme has no region for clustering at all.*
- **Measured over the 8,176 recomputed cells:** of **1,660** cells labelled **BL**, **1,658 are
  genuinely clustered** (signed < 0). **BL is not "Poisson noise" — it is 99.9% clustered.**
  A further 108 clustered cells sit in **TR ("Wigner-class")** and 6 in BR.
- **This is bigger than `rep_med`.** `rep_med` is one coordinate; **`primary` is the CLASS
  ASSIGNMENT**, and it is banked in every fingerprint, every landscape view and every per-cell
  verdict downstream. The recompute fixed the coordinate; **the label is still wrong.**
- **[[soc_pair_complete]] recurring, at the classifier instead of the fitter.** That entry says
  *"one-sided fitters are blind to super-Poisson"* and records the joint-plane classifier calling
  solar flares "Poisson noise". **Same sentence, same mechanism, now on the primary label of three
  neural/oscillator substrates.** The lesson was banked and the call site never changed.
- **The repair is NOT a threshold tweak.** Adding a `rep_int_signed < 0` region is a **new
  quadrant**, i.e. a change to the class vocabulary, and every banked `primary` would need
  re-deriving. That is a sealed re-registration, not an edit.
- **Status:** OPEN — the largest single item on the board, and newly visible.

### R-178 — ★★★ THE FIFTH WATCHER: a rail audit over every axis, and it found five new rails on run one
- **The systemic move.** Rails had been found one at a time, each by accident, in three separate
  axes across three sessions: `I.8_brody_q` (R-140/R-144), `ARS.rep_med` (lower R-093/R-094, upper
  R-173), `I.9_berry_robnik_rho` (R-148). `cross_substrate/rail_audit.py` sweeps **all 42 axes** and
  turns the discovery into a check that runs by convention.
- **THE DESIGN CHOICE THAT MATTERS: it does not test a bounds checklist.** It tests **exact-value
  pileup in a continuous field** — a continuous estimator should essentially never return the same
  float twice, so a value holding a large share of cells **is** a rail whatever produced it and
  whether or not anyone has named it. *A checklist can only find rails someone already knew about,
  which is exactly why 0.85 sat undetected in 43.9% of banked values.*
- **Threshold CALIBRATED on measured data, not chosen:** known rails **72.5% / 43.9%**; repaired
  axis `ARS.rep_med_signed` **2.0%**; continuous axes `I.5_ks_gue` 0.05%, `I.1_w1_clock` 0.02%.
  A 5% cut separates these by an order of magnitude on **both** sides.
- **Recovered all three known rails with no prior knowledge** — including
  **`I.8_brody_q`'s lower rail at 6.61e-05, NOT at 0.0.** It is an optimiser floor, so **a
  `== 0.0` bounds test would have missed it entirely.**
- **Second signature for the Berry-Robnik shape:** values crowd *near* a bound without landing on it
  (78.1% within 0.02), which exact ties cannot see. Bound-proximity catches it.
- **FIVE NEW RAILS on the first run:** `III.1_p2 / p3 / p5 / p7` and `III.4_scalar_sum`, 5.1–7.7%,
  every instance **kuramoto-confined and at the low end**. **⚠ Mechanism NOT identified** — I tested
  the obvious count/N discreteness-floor hypothesis and it does **not** cleanly hold (pileups sit at
  round fractions 1/2000, 1/2400, 11/12000 while the smallest *nonzero* values have **varying**
  denominators). Filed with the evidence, left open rather than given a plausible story.
- **★ AND A NUMBER THAT REPRICES TIER B.** Per-substrate `I.8_brody_q` saturation:
  **allen-hpf-cell 100.0%, lambda-star-classes 100%, qpo-maryland 100%, buzsaki-port-cell 99.4%,
  pvc-11 99.4%, dr-port-cell 98.6%.** Those coordinates are not degraded — they are **entirely
  rail**. Recomputing Tier B is **the difference between data and no data**, not a refinement.
- **The boundary-saturation antibody is built in:** a pileup is reported as **AMBIGUOUS, never
  invalid** (q=0 is also correct for a genuinely Poisson process). Manifest + ratchet, 3 of 8
  resolved with reasons.
- **⚠ Two corrections of mine.** (i) I hand-wrote the manifest keys instead of reading the format
  the tool emits; they mismatched and the audit reported a **false regression**. Fixed by generating
  keys *from the tool*. Same shape as the `_potential` inventory miss: **verify against the thing,
  not against your model of it.** (ii) I predicted the audit would make the suite slow enough to get
  skipped and wanted to cache — **wrong: 22 tests in 47.7 s.** No caching needed.
- **Status:** CLOSED as a guard; 5 unresolved rails tracked.

### R-180 — LOCKED-FINDINGS EXPOSURE AUDIT: 2 of 4 rest on a railed axis
- **Sealed before reading any of the four sections** (`LOCKED_FINDINGS_EXPOSURE_PRECOMMIT`), with my
  priors written down so a match could not be claimed afterwards as insight.

  | locked finding | load-bearing axis | rail status | verdict |
  |---|---|---|---|
  | **H1** OSI ↔ ks_gue_med | `ks_gue_med` | 0.05% pileup | **CLEAN** |
  | **DSI** ↔ ks_gue_med | `ks_gue_med` | 0.05% pileup | **CLEAN** |
  | **F1/F0** ↔ rep_med | **`rep_med`** | **79–82% on the rail** | **EXPOSED** |
  | **H2** population-event survival | **`rep_int_per_q`** | the same clipped field | **EXPOSED** |

- **H2's exposure was NOT visible in the document** — `EPISTEMIC_STATE` describes it as
  "population-event NNS structure ... survives the surrogate conjunction at all q-bands" and names
  no statistic. I resolved it from **code** rather than defaulting to INDETERMINATE:
  `phase22b/pass_e_tighten_seeds.py:111` computes survival on `real_row['rep_int_per_q']` and
  reports `n_q_rep_survives`. **The pass criterion IS the clipped field.**
- **Outcome B (MIXED), as sealed.** My priors were right on 3 of 4 and I recorded H2 as *unknown*
  rather than guessing — the honest form, since I had picked the others from axis names.
- **Status:** CLOSED as an audit. H1 and DSI are confirmed, not merely unchallenged: the rail audit
  measured their axis and it is the cleanest class in the store.

### R-181 — ★★ THE HEADLINE +0.388 IS UNATTRIBUTED AND NOT REPRODUCIBLE
- **`phase24/run_meta_analysis.py:127` holds `('f1_f0_pref','rep_med'): +0.388` inside a hardcoded
  dict named `PVC11_REF`** — pvc-11 constants typed in so Allen can be compared against them.
  **Nothing in the repo computes it.**
- **What the repo actually computes:** `data/phase27_results/analysis1_verdict.json` stores
  `method_b_rho_pvc11_matched = 0.29834625339738835` on n=210. My independent pipeline reproduces
  that to **five decimals** (+0.298346), with n=210 matching exactly.
- **So the banked figure overstates the effect by ~30%**, and it is quoted in **three** documents —
  `EPISTEMIC_STATE.md:143` (the locked-findings inventory), `RESULTS_MATRIX.md:23`, `README.md:498`.
- **This defect is independent of the clip** and would stand even if the axis were clean. It is the
  unattributed-constant family: a number with no live derivation, propagated by transcription.
- **It also fired my own seal.** The R0 gate required reproducing +0.388 to ±0.05; I got +0.2983 and
  declared the test **VOID as sealed** rather than waving it through — which is what surfaced this.
  The reference was re-registered (`F1F0_REFERENCE_REREGISTRATION`) to the stored artifact with a
  **tighter** rule (3 decimals, not ±0.05), and the non-blindness disclosed.
- **Status:** OPEN — three documents need correcting.

### R-182 — ★★★★ F1/F0's pvc-11 ARM DOES NOT SURVIVE THE REPAIR
- **Sealed test, gate passed to the digit** (reference 0.298346 vs deployed 0.298346).

  | axis | ρ (partial, controlling mean rate) | p |
  |---|---|---|
  | **deployed** (clipped) | **+0.2983** | 1.09e−05 |
  | **repaired** (signed) | **+0.1088** | **0.116 — not significant** |

- **Per recording, and the heterogeneity is the story:** monkey1 **+0.3252 → −0.0611 (sign flips)**,
  monkey2 +0.1971 → +0.2135 (stable), monkey3 +0.2955 → +0.1457 (halved). **82.4% of the 210 cells
  sat exactly on the rail**, so the deployed correlation was carried by the 17.6% that escaped it.
- **⚠ THE CORRECT VERDICT IS "UNSUPPORTED", NOT "REFUTED", and the seal fixed that wording in
  advance.** The finding is a claim about a **sign flip between substrates** (pvc-11 positive vs
  Allen negative). The Allen arm rests on a different dataset whose `rep_med` has **not** been
  recomputed. A one-armed collapse makes the claim unsupported by its own stated evidence; it does
  not make it false.
- **Sealed outcome R2_WEAKENED.** F1/F0 must come off the "locked findings with multiple disciplines
  verified" list until the Allen arm is recomputed and the pvc-11 arm re-established.
- **What this costs:** of four locked findings, two are confirmed clean (H1, DSI), one is now
  downgraded (F1/F0), one is exposed and untested (H2).
- **Status:** OPEN — Allen-arm recompute is the deciding measurement.

### R-183 — ★★★ H2's rail bias runs the OTHER WAY: conservative, so H2 does NOT downgrade
- **R-180 established H2 is exposed** (its survival criterion is computed on the clipped
  `rep_int_per_q`). Exposure alone says nothing about **direction**, so I measured it.
- **`survives_rep` is exactly `real_rep_int > surr_rep_int_p95`** — verified, 1.000 agreement over
  1,260 rows. So survival requires the real band to be MORE repulsive than the surrogate 95th pct.
- **The measurement:**

  | | n | survives |
  |---|---|---|
  | q-bands where the real value is **railed at 0.0** | 240 (**19.0%**) | **0.0%** |
  | q-bands **not** railed | 1,020 | 57.7% |

- **Every railed band is an automatic failure.** A band whose true signed value is negative
  (clustered) gets clipped to exactly 0.0, which cannot exceed a positive p95 — so it fails by
  construction. **The clip can only make H2 harder to pass.**
- **⚠ SO H2 DOES NOT COME OFF THE LOCKED LIST.** A finding that survives a test biased **against**
  it is not undermined by that bias. If anything the repaired axis should make H2 *stronger*.
  Exposure: REAL. Direction: CONSERVATIVE. Downgrade: NOT WARRANTED on present evidence.
- **★ THE LESSON, AND IT IS THE GENERAL ONE.** The **same rail**, on the **same field**, biased
  **F1/F0 toward its claim** (79–82% railed cells carried a correlation that evaporates when
  repaired: +0.2983 → +0.1088, ns) and **H2 against its claim** (railed bands auto-fail).
  > **Exposure is not a verdict. The direction of a rail-induced bias is FINDING-SPECIFIC and must
  > be measured, never assumed** — reading "exposed" as "probably inflated" would have downgraded
  > H2 wrongly, and reading it as "probably fine" would have kept F1/F0 wrongly.
- **Also measured, and milder than F1/F0 by a lot:** in the population classifications only **20.0%**
  of real q-values sit on the lower rail (vs 79–82% of pvc-11 cells), the median is **+0.50**, and
  317 distinct values remain — the field is not collapsed the way pvc-11's is.
- **What a definitive test needs:** the Pass-E surrogate battery re-run on `rep_int_signed_q`. Not
  done; the present result bounds the risk rather than removing it.
- **Status:** OPEN-BOUNDED. H2 stays locked, flagged, with the bias direction established.

### R-184 — ★★★★ THE ALLEN ARM STRENGTHENS, AND THE SIGN-FLIP SURVIVES. R-182 WAS TOO HARSH.
- **Reproduction gate: 910/910 Allen units match the banked `rep_med` EXACTLY.** 12 sessions, 836
  units joined with functional data.
- **The Allen arm goes the OPPOSITE way from pvc-11 — it gets STRONGER on repair:**
  meta **−0.2016 → −0.2502**, and **11/12 → 12/12 sessions negative**. Every session negative.
- **★ THE FINDING'S OWN CLAIM IS A SIGN FLIP *BETWEEN* SUBSTRATES, so the between-substrate
  contrast — not either arm alone — is its statistic. It SURVIVES:**

  | axis | pvc-11 | Allen | Δρ | Fisher z | p |
  |---|---|---|---|---|---|
  | deployed | +0.2983 (n=210) | −0.2016 (n=836) | 0.4999 | +6.59 | 4.3e−11 |
  | **repaired** | **+0.1088** | **−0.2502** | **0.3590** | **+4.70** | **2.6e−06** |

  Attenuated ~28%, still **4.70σ**.
- **⚠ SO R-182'S CONCLUSION WAS WRONG AND IS CORRECTED HERE.** I wrote *"F1/F0 must come off the
  locked findings list."* That was based on **testing one arm in isolation**, which is what my seal
  scoped — and the seal's one-arm scope was a **limitation of my seal, not a licence to conclude
  about the finding.** The claim is a contrast; the contrast holds.
- **NOT post-hoc fishing, and the distinction matters:** the between-substrate contrast is the
  finding's *own* stated claim, quoted verbatim in `EPISTEMIC_STATE` as "substrate-systematic
  sign-flip". It is the original hypothesis, not one selected after seeing the arms.
- **What genuinely changed, and it is not nothing:**
  1. **The pvc-11 arm is much weaker than banked** — +0.2983 → **+0.1088, p = 0.116, not
     significant alone**. That part of R-182 stands.
  2. **The evidential structure changed.** It was presented as two mutually-confirming arms; it is
     now **carried by the Allen arm plus a significant contrast**, with pvc-11 contributing
     *direction* but not significance.
  3. **The +0.388 defect (R-181) stands regardless** — that number remains unattributed and ~30%
     overstated whatever the axis does.
- **Status:** F1/F0 **RESTORED to the locked list, with its evidential structure restated.** Both
  arms are now on the repaired instrument; the deciding measurement is done.

### R-185 — TIER B PATH PROVEN: qpo recomputed, 91% of its Brody values were rail
- **First Tier B substrate through the registry repair (R-179), end to end, 105 min, 180 cells.**
- **Reproduction gate: 180/180 bounded values BIT-IDENTICAL to the baseline file.** Adding
  `I.8_brody_q_unbounded` to `FAMILY_I` disturbed nothing — which is the whole point of adding a key
  rather than changing one.
- **The result:**

  | | median | range | railed |
  |---|---|---|---|
  | `I.8_brody_q` (deployed) | **+0.0001** | — | **164/180 = 91.1%** below 1e−3 |
  | `I.8_brody_q_unbounded` | **−0.4108** | −0.7249 … +0.1874 | — |

  **100% of cells differ.** The 164 railed cells are freed and land substantially **negative**:
  these quasiperiodic operator spectra are **clustered** relative to the Brody model — a region the
  bounded fitter could not represent at all, so it reported them as Poisson-adjacent.
- **This is the R-178 prediction confirmed on real data.** The rail audit measured qpo-gaah and
  qpo-ext_harper at **100%** pooled saturation and said those coordinates were *entirely rail, not
  degraded*. They were: the deployed median is +0.0001 and the true median is −0.41.
- **Note the sign of the correction is the opposite of the neural substrates' Brody rail.** Here the
  freed values are negative (clustering); the concern for GOE/GUE substrates is the *upper* rail.
  Two-ended saturation, and which end bites is substrate-specific — same lesson as R-183.
- **Status:** CLOSED for qpo. The remaining Tier B ports (allen-hpf-cell 4,326; buzsaki-port-cell
  4,006; ibl-port-cell 1,556; dr-port-cell 1,365; ret1-cell 325; brocot.fm 4,006) are unchanged in
  method — five of them need **no code edit at all**, only a run against their caches.

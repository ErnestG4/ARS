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

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

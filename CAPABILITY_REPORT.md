# criticality_tool — Full Capability Report

Self-contained summary of everything the toolkit can do, what it has done,
where it falls short, and what's available-but-unused. Paste-ready for
briefing a fresh planning session. **Current as of 2026-08-31** (commit
`71d69c0`, branch `cubics-wilderness`; RESULTS.md §7.ter.7–60; the
2026-08-31 fact-check pass corrected the three summary docs in place).

> Companion internal docs: `README.md`, `EPISTEMIC_STATE.md` (both
> fact-checked + brought current to 2026-08-28 on 2026-08-31),
> `RESULTS_MATRIX.md` (69+ certified rows), `TOOLKIT.md` (§9 cross-cutting
> disciplines, §10 condemned paths, §11 2D protocol, §12 canonical order
> registry), `cross_substrate/PROGRESS_REPORT.md` (landscape program),
> `AUDIT.md` + `REPRODUCE.md` (green-board contract).
> **Note `main` is frozen at 2026-07-05; everything below lives on
> `cubics-wilderness` (679 commits ahead, 0 behind — merge is effectively
> a fast-forward).**

---

## 1. What the tool is

The **Arithmetic Resonance Spectrometer (ARS)** is a point-process
universality classifier. It takes sorted event timestamps {t_k} (spike
times, photon arrivals, transaction timestamps, peak times, **or
arithmetic spectra** — L-function zeros, Maass-form Laplace eigenvalues)
and classifies spacing statistics against universality classes: Poisson,
Wigner GOE / GUE / GSE, periodic-at-integer-q, uniform-with-jitter.

Output: a fingerprint in the (rep_int_q, rf_amplitude_q) plane plus a
quadrant assignment, now extended to a **multi-axis coordinate family**
(NNS distances W1δ / Brody q / Berry-Robnik ρ, long-range Σ²/Δ₃/K,
spectral box-dimension, dynamical Lyapunov/correlation-dimension axes) in
the cross-substrate landscape program. A calibration and falsification
protocol distinguishes signal-structure classifications from
extractor-pipeline artifacts.

Applied implementation of the Farey-rational PLL framework (Planat et
al.); **it does not contribute new theoretical mathematics.**
Arithmetic-side outputs are instrument- or methodology-validation —
never claims extending the underlying number theory (`arsrh/` carries a
§0 anti-claim binding: Riemann-adjacent CALIBRATION, not RH).

**Three operating modes** (same engines, different front/back ends):

- **Empirical point-process mode** (Phases 10–33): the deployed
  `joint_q_profile` classifier on neural / astrophysical / financial /
  biological event trains.
- **Arithmetic-spectral mode** (Phases 34a–34f, arsrh/): NNS/RF/p-adic
  engines with Weyl-law unfolding front-end and Berry-Robnik back-end on
  arithmetic point processes.
- **Landscape mode** (2026-06 onward, cross_substrate/): the multi-axis
  fingerprint applied across ~25 substrates in 6 families, with
  per-axis observable binding and comparison-validity annotation.

Project layout: three sibling tools under `$HOME/fmexplorer/` —
`criticality_tool/` (ARS, this tool), `riemann_explorer/` (FM scanner),
`fm_explorer/` (handoff docs). **Run scripts with
`$HOME/fmexplorer/bin/python3`** (pandas lives only in that venv).

---

## 2. Core classifier pipeline (deployed empirical path)

```
sorted t_k → joint_q_profile(t_k, q_max) → per-q DataFrame
           → joint_quadrant_diagnostic → per-q quadrant
           → modal aggregate → (primary, rep_med, ks_gue_med, n_well)
```

Entry point `phase22a.ars_classify.classify(events)`. The profile is a
**DataFrame, one row per q** — aggregate via
`well['ks_gue_q'].median()` etc. (there are no `ks_gue_med` keys in the
return; the 2026-08-31 pass fixed README's example, which had this
wrong).

**Two engines inside** (§7.ter.10 / §7.ter.39): the **NNS engine**
(pooled passage-time spacings, q-flat, dynamics-class signal, provably
invariant under linear time scaling → cannot detect per-prime asymmetry
on stationary signals) and the **RF engine** (Ramanujan-Fourier per q,
indicator mode, genuinely per-q, powers p-adic v4). Two timescales
(full-sequence vs per-window); every surrogate-survival claim names its
scope.

**2026-08 repair, load-bearing:** the class-assignment core `_classify`
(argmin over Poisson/GOE/GUE KS distances, depended on by 93 files) was
found to have **no rejection region** — 7/7 non-member inputs got a
confident label; a perfect clock reads GUE at 15× the KS critical value;
**754 banked classifications fit no better than a known non-member**
(overclaimed, not misdirected — no stated finding rests on a bad label).
Non-breaking repair deployed: every read now carries `best_ks`,
`ks_crit_01`, `fit_rejected` (pre-existing keys bit-identical).
19 files carry their own argmin copy (11 distinct implementations);
consolidation (C3) has rulings encoded (`gate_census/c3_rulings.py`) but
**migration is not yet authorised**. See `gate_census/GATE_CENSUS.md`.

---

## 3. Engines: RF / p-adic (unchanged core, new floor caveat)

`ramanujan_fourier(t_k, q_max, normalize, n_bins)` — normalize=False
indicator mode is the discriminating signal for TL and p-adic.
`padic_amplitude_v4(t_k)` — per-prime |a_q| sums over pure-power bands,
`normalised_per_q` recommended; q_max=200 required for absolute
thresholds (q_max=30 → 95.6% FP).

**a_q floor caveat (2026-08-19):** the calibrated amplitude floor
(~6.098) is the 95th percentile of the *no-period* classes — FP side at
nominal 5%, **FN side measured at up to 24% miss** (detection plateaus
at 0.90–0.96, never 1.0). A third confirmed one-sided calibration
alongside RIGID_GUE and `_classify` (`cross_substrate/aq_floor_sweep.json`).

---

## 4. Long-range / class certification layer (2026-06 → 08; the marginal-vs-class reckoning)

The single most consequential architectural correction since May:
**NNS / ks_gue / rep_med certify the marginal gap distribution, NOT the
universality class.** An order-scramble surrogate reproduces 0.87–1.00
of quadrant labels on every real substrate. Class claims now require
the long-range certifier:

- **Discriminator:** Σ²(L) / Δ₃(L) judged against empirical GUE/Poisson
  ensembles at matched (n, L), with a Wigner-renewal decoy
  (`cross_substrate/longrange_discriminator.py`).
- **Substrate-aware L policy (lcap/):** `L_judge = min(requested_L,
  validity_L, discrimination_L)`. Large default L can dilute a real 9σ
  effect; **at n=343 the gate is blind at every L** (GOE admitted
  32–90%); the only admissible cell measured anywhere is **n=2000,
  L=5**. Terminal ruling: n=343 rows need more data, not a different
  statistic.
- **RIGID_GUE / HYPER_RIGID split (rigidgate/):** the old one-sided
  RIGID_GUE rule certified "not floppier than GUE" — a perfect clock
  earned it at z=−5.09. Split deployed; false-HYPER rate bounded ≤0.206
  from 0/16 (honest claim "below ~21%", not zero). Δ₃ growth-based
  alternative closed FINAL: FP(GOE)=14/14 at every n — growth is what
  GUE/GOE *share*; the nearest confusable class sets the requirement.
- **Headline application:** ζ_first_2000 judged inside its Berry window
  (L=5.99) is **HYPER_RIGID z=−9.10**, lens-invariant — finite-N
  convergence at low height, NOT an asymptotic GUE violation. The
  marginal GUE reading and L-function bulk results stand. Row history
  (3 moves) kept adjacent in `lcap/RESULTS_LCAP.md`.
- **Neural split (NEGATIVE_HALFLINE_CLASSES.md):** on per-cell Σ²(L=5)
  the neural substrates split — ibl-port 73% / ret-1 60% of cells
  individually indistinguishable from Poisson at long range, vs hc-3 6%
  / allen-hpf 0%. "Every neural substrate is clustered" was a
  short-range verdict.

---

## 5. Estimator reliability layer (2026-07 → 08; censoring, rails, one-sidedness)

A whole capability class that did not exist in the last report:
systematic audit of the instruments themselves.

- **Censored-at-null estimators (`ESTIMATOR_CLAIM_PROVENANCE.md`):**
  `I_rep`/`rep_int_q` is floored at the Poisson value
  (`np.maximum(0, 1−R₂)`); `bulk_recovery` mass→σ clamps onto a Poisson
  knot. **`BL` as a verdict class is RETIRED** — exact-0.000 is
  unreachable by the repo's own Poisson calibrator (0/1000), so an
  exact-zero read is a **clustering detection**. Two banked reads
  inverted (fungal 194/194, flares 191/191 exact-0 = CLUSTERED; Binance
  0/185 = genuine weak repulsion). The rail is a DETECTOR (TOOLKIT §9
  arm (e)).
- **Rail recovery (gate_census + bounded_census + c2_acceptance):**
  73.8% of banked bounded Brody-q values were ONE float
  (6.610696135189609e-05 — Brent's terminal step inside a zero lower
  bound, provenance measured not assumed). **Rail = pileup, not
  proximity**: distinct-value ratio discriminates optimizer floor
  (4/15,174 distinct) from real concentration (7,319/7,328).
  **C2 COMPLETE: all 1,159 pvc-11 records repaired — 99.4% clustered,
  median Brody q = −0.373, 0.0% railed** (was banked as one positive
  constant, wrong sign and magnitude).
- **One-sidedness is the house default:** 9 of 11 deployed classifier
  implementations have no rejection region or an unrecorded
  complementary rate (sealed prediction of 4–6 missed HIGH).
  Two-sidedness is an artifact of audit. Any threshold set from one
  side has an unmeasured error rate on the other.
- **Estimand policy:** per-realization gates need per-realization error
  rates, both directions (`pole_sep` and `validate_fitters` repaired;
  the repo's own `run_phase17_limits.py` CI-coverage idiom is the
  precedent). Boundary rates carry denominators + Clopper–Pearson
  intervals, pinned in code (`boundary_rate.py`).
- **Phase 38 reliability ledger:** caught shared-seed surrogate leakage
  in Phase 32b's per-cell estimator (a null cell returns ρ=+0.257);
  the BOTH_ORTHOGONAL verdicts are WITHDRAWN-PENDING-RERUN; the
  §7.ter.50 retro-scope is PROPOSED, NOT APPLIED.

---

## 6. Calibrator zoo (extended)

Stationary classes (Poisson, GOE/GUE/GSE, ζ_first_400, uniform_jitter,
periodic_q7, mixed_q7_q12) + transition calibrators (blended, logistic,
Mackey-Glass) + dynamical (Chialvo, Kaneko GCM; Phase 36) + arithmetic
(β-Hermite, COE/CUE/CSE, Berry-Robnik mixtures, synthetic Weyl 2D/3D)
+ **clustered class (built + PASSED 2026-07-12** — the zoo previously
had no clustered member) + **2D arithmetic entry** (`gp_comb`: comb
weights = computed ℤ[i] Hardy–Littlewood singular series, 19 classes,
N50 discriminator 53.9σ; tier schema live in `calibrator_panel.py`) +
Ginibre sampler and GUE pair-correlation anchor for the 2D protocol
(TOOLKIT §11, banked for DES/DESI survey work).

Standing rules: precision upgrades audit the zoo's reference constants
(a bad fixture is a suspect REFERENCE); fitters are synthetic-validated
against known truth and probed outside the reachable range (Poisson/GOE
are the fitters' own rails).

---

## 7. Surrogates and nulls

`rate_matched_poisson` (default), `cell_shuffle`, `ln_evoked`,
`state_modulated`, `lightcurve_modulated_poisson`; coupled-GLM Pass D =
FIT-CEILING. Arithmetic-substrate discipline: support-set-respecting
nulls; right-null is substrate-specific; 20-seed subsample-replicate
near class boundaries; stratify-before-pool (pooling manufactures
Simpson's / false positives). **One null excludes only its confound**
— verify the test CAN fire; a powered falsifier CONSTRUCTS the confound
it rules out. Pooled-rhythmic confound: pooling near-periodic emitters
manufactures sub-Poisson via temporal-grid quantization (mechanism
corrected 2026-06-01); clustering-side reads are safe.

---

## 8. Cross-substrate landscape program (cross_substrate/; the 2026-06→08 backbone)

~25 substrates across 6 families: V1 (pvc-11, Allen incl. full visual
hierarchy), neural ports (Buzsáki CA1, IBL, EC/CA3, ret-1 retina,
hc-3), Kuramoto/Chialvo/Kaneko, arithmetic (ζ / Dirichlet / EC-L /
Mertens / Liouville / Gaussian+Eisenstein primes / Maass / Farey),
dynamical (Mackey-Glass, Lorenz, logistic, Rössler, Chua, Duffing,
Hénon), quasiperiodic operators (almost-Mathieu, Fibonacci/Sturmian
Hamiltonian, generalised Harper, diatonic), brocot.fm synthesis corpus,
SOC (earthquakes, solar flares), NANOGrav, LLM surprisals.

**Load-bearing findings:**

- **Clustering ⊥ coupling (THE finding):** n=5 substrates; a matched
  pair kills two confounds at once.
- **H1 extended:** OSI↔ks_gue pooled +0.445 (n=7,846, 7 areas + LGN),
  burst-orthogonal everywhere; CA1 analogue (spatial info ↔ ks_gue
  +0.279). Read as **marginal-spacing gradient, not class** (external-
  rate unfold collapses the clustering reading).
- **F1/F0 substrate-systematic sign-flip:** RE-VERIFIED on the repaired
  instrument (R-181…184) — between-substrate contrast 4.70σ; pvc-11
  reproducible +0.298 (banked +0.388 was an unattributed literal);
  Allen repaired-axis −0.2502 (12/12).
- **AM ≡ Fibonacci:** empirically one operator family up to an
  approximability-dependent reparametrization; DEGT strong-coupling
  constant form-confirmed, constant-deferred (finite-spectrum
  estimators verify forms, not asymptotic constants).
- **Per-cell fingerprints cohere; population observables fragment**
  (aggregation, not biology, sets the population class).
- **ks_gue_med is an unbiased proxy** for matched ks-to-GUE (slope ≈ 1,
  n ≥ 100) — cheap harvest is trustable for placement.
- **Brocot re-indexed:** class-level ρ=−0.91 was a
  one-representative-per-class artifact; holds per-α at ρ=+0.699
  (n=255) with confound controls. A Lagrange class is an asymptotic
  label a bounded instrument cannot see — **mis-indexed, not
  underpowered; re-index instead of scaling n.**

Related settled arcs: thermo/ (golden-dominance INVERTED; Tier-2 wall
stands), khinchin/ (α×depth field, green), rf_lenses/ (WK bridge;
Thread-E promotable), Farey class CERTIFIED (the "rigidity between
Poisson/GUE" folklore FALSIFIED), approximability ⟂ mode-locking
(theorem-level disjoint), bridge arc (ARS↔spatial-stats transitions
validated; TOOLKIT §11), survey arc (DESI DR1 brief APPROVED, awaits
go).

---

## 9. Transition-order holonomy (holonomy/, fullseq/; TOOLKIT §12)

New protocol capability: measuring **commutators of pipeline transition
order** (window/unfold/pool/…) so ordering choices are ruled, not
accidental. `canonical.py` order registry; pairwise commutator table
measured and ruled.

- P1 continuum law q ≈ 0.79·θ² confirmed; absorption-term arc closed
  `UNDER_ORDERED_ESTIMATOR` after a numerics retraction (ill-conditioned
  prediction-side polyfit manufactured a 96-sem anomaly; measurement
  path clean); form RIDGE_PREDICTIVE (slope 1/2, offset unresolved),
  two held-out degrees hit.
- **Full-sequence warning (fullseq/):** exhaustive out-of-sample testing
  over all 59 admissible orderings **falsified sub-additivity** — the
  pairwise table can UNDERESTIMATE composed holonomy by up to 6.9×,
  concentrated where UNFOLD follows POOL (saturation regime). Usable
  output is a structural risk factor at the table's point of use, not a
  corrected law.

---

## 10. Arithmetic-spectral mode + ARS-RH program (arsrh/, phases 34–35)

Phases 34a–34f as before (Mertens/Liouville NULL at right-null; L-zeros
5/6 NULL_BEYOND_RMT; Gaussian/Eisenstein RW_SHAPE_CONFIRMED; Γ₀(N)
Maass SARNAK_ANOMALY_REPLICATED; Bianchi 3-D pipelines validated,
DATA_ACQUISITION_BLOCKED; BCGNT-2025 proven-theorem calibration tier).
**[CLOSED 2026-09-02]** The 34e §G.3 canon entry quoted the retracted
ρ≈0.458 with no marker; it now carries the retraction, the corrected
ρ_GOE≈0.1264±0.0321, the withdrawal of the "upper end of the literature
range" placement, and a newly-visible undischarged debt (the ρ-convention
alignment against the literature interval was never audited).

**ARS-RH program (arsrh/)** — Riemann-adjacent calibration under a §0
anti-claim binding. Highlights: P1 ζ crossover real-beyond-density; Σ²
long-range witness with density-curvature decoy discipline; Maass GOE
exclusion 7.3/6.4σ (endpoint); low-γ corroboration leg EXHAUSTED at
2.452σ; Maass Σ² retired; cubic Gate 0 (ladder is a theorem g²/m;
mechanism GL₂(Q)-equivariant, absent on Galois conjugates); **lnln
program TERMINAL** — Var[S] consistent with Selberg+Goldston plus an
unattributed 0.024/L; three publishable-looking positives were all
artifacts, all caught. 2026-08 slot update: Montgomery-window content
now a THEOREM (BGST); the 67.2% figure is not the 2/3 slot.
**derivflow closed:** measured form NOT_DERIVABLE from the AFPU global
machinery (invariant to 2.6e-14 while the statistic moves 4,492×) —
global machinery cannot give local content; SCALE-FLAT k* conceded as
folklore's own prediction.

---

## 11. Stern–Brocot audio/synthesis arc (2026-08-23 → 28; cross_substrate/brocot_*)

New applied capability: perceptual/synthesis consequences of the
Farey/Brocot structure, run under full seal discipline (~120 commits,
every cell sealed before output; `BROCOT_SYNTH_IMPLICATIONS.md`).

- **Structure horizon THEOREM:** p/q has sideband-coincidence structure
  at index I ⟺ max(p,q) ≤ 2·order_bound(I); 508/508 exact. Horizons
  8/10/12/14 at I=0.9/1.5/2.0/3.0. Scoped to two sine operators;
  dissolution with partial count N follows a nothing-fitted lattice
  curve; gone by N≈7–8.
- **Perceptual parent THEOREM:** denominator-weighted minimiser (not
  closest ancestor; path truncation falsified); tie case a theorem; map
  field is a Voronoi tessellation. Two display layers (REGION at
  mediants, EVENT at nodes); three linearisation attempts failed —
  punctuation is scale-free.
- **Audible horizon:** derived from Glasberg–Moore masking (not a chosen
  dB floor); a listener's first impression broke the blinding + positive
  control (α=1 degenerate), correcting the headline to **zero non-
  degenerate below-horizon ratios clear masking**. A "17 dB per rung"
  law was retracted next-commit. The phasing cue is present throughout
  (21–101 dB SNR) — an earlier "not in the signal" claim retracted;
  skip-structure real, mechanism unresolved (the sealed arm does not
  discriminate against the total-energy rival).
- Shipped-code verdicts: fusion density earns a dimension; the
  suggest-criterion is wrong in practice for 97.5–100% of its own
  regime; ranking order-dependent with no convention detected; the
  reachability filter optimises an inaudible property at conservative
  width (C++ change did not ship).

---

## 12. Verification / sealing infrastructure (rulings as code)

The repo now enforces its methodology mechanically. `verify_all.py`
green board (25/25; **green means the checkers pass, not that the
instrument measures what we claim** — AUDIT.md). Components:
`threadledger.py` (QUEUED/LANDED/DROPPED as data; verdict drift or
missing artifact fails the board; WARRANT_STALE; framing-death
staleness — **and, since 2026-09-02, drift measured against the
EFFECTIVE verdict**: it had read the sealed `verdict` key while
corrections are recorded in a sibling `verdict_amended`, so the drift
detector was blind to the repo's only drift mechanism and passed six
citations across five rows, four of them amended to the reverse of
their seal. Fixed at one resolver, red-pathed by a self-test; the two
checkers that legitimately read the seal for INTEGRITY are documented
as such so they are not "fixed" to match. TOOLKIT §9), `verdictlattice.py` (head from EXISTENCE arms alone;
`compose()` returns citations), `reachable.py` (Bars with defended
ranges, both-edge raises, edge probes, rival rule), `modelparams.py`
(every instrument parameter tested-with-sweep or declared-with-defence;
`swept()` returns the pre-registered config, not the maximum — measured
+0.331 selection penalty), `redpath.py` (probes assert their own reach;
when `expect_min` fires, raise power, never lower the floor),
`detector_spec.py` (no detector without a negative set + named nearest
confusable), `boundary_rate.py`, `existence.py` (typed question
shapes), `countrecon.py` (count reconciliation), `ratiopinned.py`,
`checkrun.sh` (machine writes the verdict), `sealgen.sh` +
`verify_seal_order.py` (generator-before-output as a commit-graph
property), commit-msg hook (no outcome claim without a CHECKRUN line),
`verify_frozen_blobs.py`, `verify_pending_debt.py`. An adversarial
review (08-25) broke the guards in scratch and hardened them
(unfalsifiable negation path, one-sided inertness check, stdlib
shadowing — all fixed).

Sealing discipline: prereg sealed before output; sealed contingencies
dry-run at seal time; **sealing ⊥ coverage** (a seal proves no
post-hoc choice, not that the sample spans the phenomenon); every
banked number needs a committed generator.

---

## 13. Domain pipelines (delta from the May report)

Everything in the May table stands with these amendments:

| Area | Update |
|---|---|
| pvc-11 | H1 +0.720 traceable but in the unswept `PVC11_REF` dict (1 of 6 entries audited, that one was wrong); F1/F0 = +0.298 reproducible; **Brody coordinate repaired: 99.4% clustered, median −0.373** |
| Allen | F1/F0 repaired-axis −0.2502 (12/12); H1 extended to 7 areas + LGN pooled +0.445 |
| ζ zeros | marginal GUE stands; **HYPER_RIGID z=−9.10 inside the Berry window** |
| Phase 32b | cross-engine INDEPENDENT_AXES stands (session level); **per-cell BOTH_ORTHOGONAL WITHDRAWN-PENDING-RERUN** (surrogate leakage) |
| Kuramoto/Kaneko | eliminations stand; "repulsion-BLIND" upgrades FLAGGED (read on the censored axis; BL retired) |
| Binance / fungal / solar | relabelled: fungal + flares = clustering detections; Binance = genuine weak repulsion |
| LLM | retraction arc stands **with one carve-out**: Phase 37 fp16→int4 is SUBSTRATE (mass03 +0.0604, dither-invariant) — a within-extractor differential |
| New pipelines | lcap/, rigidgate/, gate_census/, bounded_census/, holonomy/, fullseq/, derivflow/, brocot_* audio, bridge/, comb/, survey/ (DESI, awaits go), thermo/, khinchin/, rf_lenses/, sessionK/, phase35a/36/37/38 |

---

## 14. Known failure modes (the check-before-claiming list)

May items 1–13 stand (peak-detection extraction; threshold-upcrossing
TR; q-flat NNS; σ̂ scope; class sample sizes; rate-regime surrogates;
JPF_CAP; fitter normalization bias; stratify-before-pool;
stride-decimation; DATA_ACQUISITION_BLOCKED discipline; venv trap).
New since:

14. **Argmin with no null option** — a class space with no rejection
    region confidently labels non-members (Gate 1; repaired, 18 copies
    remain pending C3).
15. **One-sided thresholds admit the far side** — RIGID_GUE/clock;
    a_q floor's 24% unmeasured miss rate.
16. **Censoring at the null** — floored estimators launder nulls;
    exact-value pileups are detections; `BL` retired.
17. **Bounded fitters rail on a constant** — check the distinct-value
    ratio; pvc-11 Brody recovery is the type case.
18. **Pairwise holonomy tables are not conservative bounds** —
    UNFOLD-after-POOL super-additivity up to 6.9×.
19. **Non-evidence scored as a verdict** (dominant error mode) — dead
    arms in n/m tallies; an arm both the hypothesis and its rival pass
    is evidence for neither (rival rule); argmax without a location
    error bar; selected maxima reported with the winner's interval
    (swing rule).
20. **Mis-indexing masquerades as underpower** — asymptotic label +
    bounded instrument: no n fixes it; re-index.
21. **A retraction that leaves the claim standing elsewhere in the same
    file is not a retraction** — four instances found and fixed in one
    week; grep before you bank.

---

## 15. Architectural caveats / scope

- H1 is a **marginal-spacing gradient**, not a level-repulsion class
  (external-rate unfold collapses the class reading); direction is
  POSITIVE (+0.72 pvc-11), sign-flip vs Allen noted per-substrate.
- NNS certifies marginal, not class; class needs the long-range
  certifier inside its validity window; separability is a substrate
  property no statistic repairs.
- Asymmetric verdict-label tiers (empirical-anchor / first-measurement
  / proven-theorem-calibration) remain binding.
- Ramanujan-conditionality two-regime split (BCGNT proven cohomological
  vs conditional Bianchi-Maass) stands.
- The pll_bank is off the deployed **neural** path but IS called by the
  canonical arithmetic NNS driver (`run_analytical_nns.py`, at
  non-default K_p/K_i — a fact-check correction).
- Arithmetic outputs are instrument/methodology-validation only.

---

## 16. Open items (the planning queue, priority-ordered)

1. ~~**PHASE34E_FINDINGS.md §G.3** — strike the retracted ρ≈0.458.~~
   **DONE 2026-09-02.** Struck, corrected, and the "upper end of the
   literature range" placement withdrawn rather than re-aimed. It
   surfaced one new debt, deliberately left open in the entry: **the
   ρ-convention alignment between our fit and the quoted literature
   interval [0.3, 0.5] was never audited** — do not re-quote that
   interval until it is.
2. **Falsification calibrator Arm B re-run on unclipped I_rep**
   (`ESTIMATOR_CLAIM_PROVENANCE.md` debt #2 — UNBLOCKED, never run).
3. **Pass-E surrogate battery on rep_int_signed_q** — the definitive
   H2 / F1-F0 stratified re-run (R-183).
4. **Elect one H1 p-value; sweep the five unaudited PVC11_REF
   constants** (R-181 checked one of six; it was wrong).
5. **Phase 32b per-cell re-run** on the repaired estimator (verdicts
   WITHDRAWN-PENDING-RERUN; retro-scope held for review).
6. **Thread ledger QUEUED ×7** (was ×4): heard-as-listening,
   audible-horizon-calibration, double-pulse-control,
   suggest-reachability-filter (all three σ-gated rows were re-posed
   after framing-death fired — read the re-posed wording), plus the
   **contrast arc registered 2026-09-02** — `detune-impossibility`,
   `resynthesis-apparatus`, `decorrelation-battery`, in that order.
   The first is cheap and decides the other two: it either retires
   ratio detune with a proof (fold cases included — the standing
   caveat) or finds the counterexample manipulation in a fold case, in
   which case heard-as-listening unblocks with no resynthesis at all.
   None of the three has been run. Plus `orphan-session-branches`
   (×8 total) — see item 12.
7. **C3 classifier consolidation** — rulings encoded, migration not
   authorised; 18 argmin copies outstanding.
8. **COMB_KTUPLE_BRIEF.md** — drafted, needs review + go.
9. **Survey arc D0+D1 (DESI DR1)** — brief approved, awaits go.
10. **34f data acquisition** (Then 2003 / Z[ω] Maass) — still the
    blocker for the Q(√−3) closer; cohomological-H executed and
    bounded (see memory), Δ-Maass legs still blocked.
12. **Orphaned July-2026 session branches — Session G LANDED
    2026-09-02 (`c0f1037`); three remain.** Original entry:
    **Four orphaned July-2026 session branches** — `cf-convergence-bridge`
    (G), `genus-ff-calibrator` (F), `third-refit` (H arm 2),
    `thouless-amo-identify` (D): one commit each, reachable from
    **neither** `main` nor `cubics-wilderness`. Found 2026-09-02 by the
    gap in the `MORNING_*` series (A,B,C,E,H₁,I,J,K,λ present — D,F,G,H₂
    missing, exactly the four branches). **The urgent piece:**
    `G_fifth_measured.json` is on HEAD but its
    `G_fifth_prediction_SEALED.json` is not, and
    `approximability/H_arm1_seal.py:22` reads that measurement — an
    unsealed measurement in load-bearing use. Session F also needs a path
    repair (its commit carries a stray `criticality_tool/` prefix from
    being committed one directory up). **Do not delete these branches.**
    They are already pushed to origin (0 unpushed), so nothing is at
    risk of loss — but they are the only refs from which these four
    commits are reachable at all, and deleting them orphans the objects
    to `gc`. main was fast-forwarded without them by
    deliberate choice, to keep that merge a zero-risk fast-forward.
    **Update 2026-09-02:** `cf-convergence-bridge` (Session G) is merged
    — it was the urgent one. `G_fifth_measured.json` carries
    `"note": "BLIND — seal not opened"`, announcing a governing seal that
    did not exist on the branch consuming it, and Session G's verdict is
    PARTIAL with the strict-monotonicity falsifier **tripped at depth 12**
    — the a=1 step `H_arm1_seal.py` fits its curve from. Landing it also
    exposed a defect in `verify_seal_order`: git's default history
    simplification attributed the measurement to a commit twelve hours
    after the seal, reporting SEALED for a pair whose honest label is
    DECLARED (both files are in one commit). Fixed with `--full-history`;
    no previously registered pair changed verdict. Still out:
    `genus-ff-calibrator` (F — needs its stray `criticality_tool/` path
    prefix repaired), `third-refit` (H arm 2), `thouless-amo-identify` (D).

11. Longer-horizon: Kuramoto alternatives (Stuart–Landau etc.);
    RIGID_GUE 0/60 specificity run (bounds false-HYPER ≤0.049);
    within-GCM magnitude↔R sweep.

---

## 17. Conventions

RESULTS.md §7.ter ladder at **§7.ter.60**; one commit per phase;
brief→execute pattern with sealed pre-registration; commit messages
carry ALL-CAPS verdict tokens and (since 08-25) CHECKRUN lines for any
outcome claim; boundary rates carry denominators; supersession markers
land at stale call sites, not only in new sections. Memory index at
`~/.claude/projects/-home-combust-fmexplorer-criticality-tool/memory/`
(~150 entries; see `docs-factcheck-2026-08-31` for this pass).

---

*Sources: the 2026-08-31 fact-check pass (commit `71d69c0`) over
README.md / EPISTEMIC_STATE.md / RESULTS_MATRIX.md, the arc findings
docs cited inline, and the repo memory. Supersedes the 2026-05-15
report (`95b2324`).*

# Audit 03 — Claims Ledger (ARS self-claims vs. code)

READ-ONLY audit. Phase 3: every empirical/capability claim the project makes ABOUT ITSELF,
turned into a checklist row `claim | source file:line | status`, where status was assigned by
reading the *code*, not by trusting the doc. Code is ground truth.

Status vocabulary:
- **[supported-in-code]** — code exists and does what the claim says; code citation given.
- **[partial]** — core mechanism present, but a quantitative figure / scope / framing in the claim is not in code (it is a runtime output, or split across files, or mislabeled).
- **[not-found]** — no code implements the claim.
- **[contradicted-by-code]** — code does the opposite of, or undermines, the claim.

Doc abbreviations: README = README.md · CR = CAPABILITY_REPORT.md · METHODS = METHODS.md ·
WHY = WHYTHISEXISTS.md · ES = EPISTEMIC_STATE.md · CFF = CITATION.cff.
Code lives at repo root and in `cross_substrate/`, `phase22a/`, `phase34*/`, `phase37/`.

---

## PRIORITY HONESTY CHECK — NNS-marginal vs. long-range (default-emphasis)

**The question:** does the code's DEFAULT verdict / quadrant function lead with the long-range
class instrument (Family II: Σ²/Δ₃, `axes.py:277/293`), or does it still lead with marginal-NNS
(Family I: `ks_gue`/`rep_int`, `axes.py:111`)?

**Verdict: the default verdict leads with marginal-NNS. Long-range is a separate, non-default audit layer.**

| Claim | Source | Status |
|---|---|---|
| Spacing verdicts certify the *marginal* gap distribution, not a universality *class* | README:29; README:389; ES:1769-1771 | **[supported-in-code]** — the deployed classifier `classify()` (`phase22a/ars_classify.py:51`) returns only `rep_med`, `ks_gue_med`, modal `quadrant` (lines 85-90), all marginal-NNS. `joint_quadrant_diagnostic` (`arithmetic_toolkit.py:724`) assigns the quadrant *purely* from `rep_int_q` thresholds (lines 781-801) + `ks_gue_q` for the BR sub-split (line 797) + RF spike. **No Σ²/Δ₃/long-range term enters the default verdict** (grep of `ars_classify.py` + `arithmetic_toolkit.py` for sigma2/delta3/longrange/II1/II2 → zero hits). |
| The deployed quadrant is order-blind by construction (order-scramble reproduces 0.87–1.00 of per-band labels) | README:390; ES:1774-1776 | **[supported-in-code]** — `cross_substrate/quadrant_marginal_test.py:16-22` scrambles serial order (identical marginal) and re-runs the quadrant to show it adds nothing beyond the NNS marginal; confirms the verdict rides the marginal. |
| Long-range Σ²/Δ₃ is the genuine class-level instrument; NNS cannot tell the Wigner-renewal decoy from real GUE; Σ²/Δ₃ separate them >20× | README:206-208; ES:1772-1773 | **[supported-in-code] as a *module*** — `cross_substrate/longrange_discriminator.py:55` (`wigner_renewal` decoy), `:131` (`longrange_stats`), verdict RIGID_GUE / MARGINAL_ONLY / INTERMEDIATE (`:17-20`) against matched real-GUE + renewal ensembles. Σ²/Δ₃ themselves are `axes.py:277` (`II1_sigma2_at_L`) and `:293` (`II2_delta3_at_L`). |
| …but is it the DEFAULT instrument? | (implicit emphasis question) | **[contradicted-by-code] for default-emphasis** — `longrange_discriminator` is imported only by dedicated audit scripts (`longrange_audit.py`, `longrange_neural_audit.py`, `longrange_allen_audit.py`, `run_phase18_finding_validation.py`, `rf_decoy_battery.py`), **never by the deployed `ars_classify`/`joint_quadrant_diagnostic` path**. The default verdict remains marginal-NNS-driven. |
| Pooled long-range claims caveated to marginal-only; ζ confirmed at class level but neural per-cell downgraded to marginal | README:393; README:396; ES:1782-1791 | **[supported-in-code]** — the long-range layer exists to make exactly this distinction (`longrange_discriminator.py:24-25` BOUND comment), and the neural audits route through it. The docs are *honest* that the deployed quadrant is marginal-only. |

**Honesty summary:** the docs do NOT falsely claim long-range is the default — they explicitly
acknowledge the deployed quadrant is marginal/order-blind (README:29, ES:1774,
quadrant_marginal_test.py). So the project is *self-consistent and honest* about the downgrade.
But on the literal default-emphasis test the task asked for: **the default verdict still leads with
NNS (`rep_int_q` + `ks_gue_q`); long-range Σ²/Δ₃ is a well-built but separate, opt-in audit layer
that is not wired into the deployed classifier.**

---

## PILLAR 1 — GUE/Poisson structural poles generalize at n≥3 substrate types

| Claim | Source | Status |
|---|---|---|
| Canonical GUE pole and Poisson pole are defined as calibrator anchors | README:551; CR:148-153; METHODS:46-52 | **[supported-in-code]** — `cross_substrate/calibration_anchors.py:45-52` defines `GUE_b2` (β=2, q≈1, ρ≈1), `poisson` (q≈0, far-from-GUE), `clock`, `uniform_jitter`; fingerprinted on the same `classify().ks_gue_med` instrument (`:59-68`). |
| Per-cell `ks_gue_med` pole readout computed across multiple substrates | README:565; CR:85-86 | **[supported-in-code]** — same `from ars_classify import classify` → `.get("ks_gue_med")` in 7 ports: `buzsaki_port.py:135,150,157`; `ibl_port.py:102`; `ret1_port.py:82`; `hc3_port.py:195,241,257` + `hc3_ec_pillar1.py:79`; `dual_region_port.py:124,140`; `comcat_port.py` (via `universality.py:41,302`); `goes_flares.py:171`. |
| Both poles (GUE-leaning rigid + Poisson-leaning) recovered across ≥3 substrate types | README:565; README:598; CR (memory n=5) | **[supported-in-code]** — population two-pole code (`corr-eig`→GUE, `sync-event`→Poisson) reused verbatim across substrates: Allen V1 (corr-eig 0.89 / sync 0.00), Buzsáki CA1 (0.85 / 0.00), IBL (0.81 / 0.01), MEC+HPF (0.86–0.95 / ≈0) per `cross_substrate/findings_log.md:833-851,1057-1059,1158-1159,1317-1320`. Code: `population_fingerprint.py:179-181`, reused at `dual_region_port.py:42-43,75-77`. **n=5 distinct substrate types** with working pole code — comfortably ≥3. |

**Pillar-1 verdict: [supported-in-code].** Caveat: `cross_substrate/PROGRESS_REPORT.md` predates
most ports; live evidence is in `findings_log.md` + the port `.py` files.

---

## PILLAR 2 — per-cell selectivity-quality ↔ universality class (graded, burst-controlled)

| Claim | Source | Status |
|---|---|---|
| Per-cell OSI correlates with per-cell `ks_gue_med`, pvc-11 ρ_partial=+0.720, Allen meta +0.363 | README:492-494; CR:386,473; ES:96-105 | **[supported-in-code]** (effect *magnitudes* are runtime outputs, not coded constants) — `allen_v1_burst.py` computes per-cell `osi` (`:81`), `ks_gue_med` (`:76`), Spearman OSI↔ks_gue (`:145`). pvc-11 leg lives in `phase22a`/H1 work; the +0.720 figure itself is a result, not a literal in code. |
| Selectivity↔ks_gue is GRADED (continuous partial-correlation), not a binary detection proxy | README:492; ES (graded tuning) | **[supported-in-code]** — every implementation uses Spearman/partial-Spearman over the continuous selectivity variable: `allen_v1_burst.py:140-151`, `allen_osi_gap.py:131-144`, `pillar2_burst_control.py:36-39`. Only one auxiliary binary split exists (`buzsaki_placefields.py:172-177` `is_place_cell` Mann-Whitney), and it sits *alongside* the graded test, not in place of it. |
| Burst-control is REQUIRED: correlation recomputed after removing burst component | README (burst-control); memory `pillar2_burst_control` | **[supported-in-code]** — dedicated module `cross_substrate/pillar2_burst_control.py`: `partial()` (`:25-29`) rank-residualizes both selectivity and ks_gue against burst and recomputes; `block()` (`:32-43`) reports raw / partial / retained, tagging `<CLEAN>` when sel↔burst<0.1 (`:120`). V1 replication in `allen_v1_burst.py:148-151` (burst-residualized H1) + OSI↔burst≈0 check (`:132,146`). Burst = ISI<10ms fraction (`allen_v1_burst.py:42-46`). |
| The selectivity↔class link is controlled for RATE | README:681; ES:504-507; CR:170-172 | **[partial]** — rate-partial exists in `allen_osi_gap.py:103-107,133-134` (partials OSI↔ks_gue against `mean_rate`,`n`); rate-matched Poisson surrogate is operational default (CR:170). BUT **no single file partials for both rate AND burst simultaneously** — burst-partial (`pillar2_burst_control.py`, `allen_v1_burst.py`) and rate-partial (`allen_osi_gap.py`) are in different files. |
| DSI↔ks_gue replicates cross-species, Allen stronger (+0.269 vs +0.223) | README:513-515; CR:474; ES:228-230 | **[supported-in-code]** — *(corrected 2026-06-30: original pass said "DSI not implemented" — a false negative; it didn't read `phase22a/`.)* DSI is computed at `phase22a/h1_functional.py:96` (`DSI = |Σ rₖe^{iθₖ}|/Σ rₖ`, direction-period weighting), banked to `data/phase22a_results/h1_functional.parquet`, and consumed as a Pillar-2 descriptor in `phase22b/pass_a_recording_blocked.py:57` (`DESCRIPTORS` incl. DSI, rate-controlled) and `gratings_divergence.py:100` (`G3_absD_vs_dsi`). |
| Pillar-2/H1 generalizes beyond V1 to all visual areas + LGN, and to hippocampus via spatial-info | README:600; ES; memory | **[supported-in-code]** — hippocampal spatial-info axes computed and correlated: `buzsaki_selectivity.py:79-101` (Skaggs `_spatial_info`), `buzsaki_port_analysis.py:72-90` (graded Spearman vs ks_gue), `pillar2_burst_control.py:55-110` (MEC/CA1/DG/EC/CA3/DG spatial_info, burst-partial). Note plain-Spearman in `buzsaki_port_analysis.py` (burst-partial deferred to `pillar2_burst_control.py`). |
| `ks_gue_med` SUBSUMED by 8-factor FA on pvc-11 (R²=0.73–0.80) — mechanism open | CR:534-536; README:401; ES:106-108 | **[supported-in-code]** (downgrade honestly stated) — FA-subsumption analysis in `phase27/analysis2_ars_vs_fa.py`; H1 framed correlational, mechanism open. |

**Pillar-2 verdict: [supported-in-code] for the load-bearing OSI/spatial-info + graded +
burst-control claim** (split across `pillar2_burst_control.py` + `allen_v1_burst.py`), with two
qualifications: (i) no file co-controls rate AND burst together. *(The earlier "DSI claim has no
located code" qualification is RETRACTED — DSI is implemented; see the row above.)*

---

## RATE-ROBUST CV CORRECTION (CV2/Lv)

| Claim | Source | Status |
|---|---|---|
| CV2 (Holt) and Lv (Shinomoto) are parameter-free and robust to slow rate drift | README:215; axes docstrings | **[supported-in-code]** — `axes.py:215` (`I12_cv2`), `:227` (`I13_lv`) compute parameter-free adjacent-ISI local-irregularity on RAW time-ordered intervals (`_ordered_intervals`, `:206`), explicitly NOT the sorted/trimmed `canonical_spacings`; `family_local()` (`:237`) merges them. Global CV is `I10_cv` (`:175`) on the matched spacings. |
| Global CV is inflated by slow rate drift / epoch-gap concatenation; CV2/Lv isolate fast clustering | README:216; axes.py:218-219; memory phase37 | **[supported-in-code] (mechanism)** — `axes.py:218-219` docstring states CV2 is robust because adjacent ISIs see ~same rate; `phase37/slow_structure_ruler.py:5,28-36` calibrates the global-CV−CV2 gap as a ruler (both slow-drift and epoch-gaps inflate gcv while cv2 stays ~1). |
| Specifically inflated 2–7× | README/memory (CV-16 artifact) | **[partial]** — the 2–7× magnitude is a *runtime/empirical* figure, not a coded constant; and `slow_structure_ruler.py:5` explicitly warns "the gap magnitude ALONE cannot" distinguish signal from artifact (it adds `trim_collapse` + `top1_share` discriminators, `:33-36,75,85`). The correction *mechanism* is backed; the precise 2–7× multiplier is an output. |
| Ports must merge `family_local(spk)` or they miss CV2/Lv | axes.py:237-241 | **[supported-in-code]** — `compute_family_I` (`:244`) calls `family_local` (`:250`); the docstring (`:238-240`) warns that iterating FAMILY_I over `canonical_spacings` alone drops time-adjacency. |

---

## KATZ–SARNAK / L-FUNCTIONS / arithmetic instrument-validation

| Claim | Source | Status |
|---|---|---|
| EC L-function edge separation by root number confirmed | README:475; CR:446; ES:1212; CFF:9-10 | **[supported-in-code]** — `run_lmfdb_family.py:149` (`ellrootno` per curve), grouped +1/−1 (`:221-222`); `run_lmfdb_edge.py` strips forced central zero for −1 curves (`:85-89`), compares conductor-normalized γ₁ (`:115-124`), edge-NNS (`:143-163`), γ₂−γ₁ (`:171-196`) with two-sample KS p-values (`two_sample_ks`, `:52-61`). |
| Bulk GUE identical across families; separation lives at the edge | README:477; run_lmfdb_edge.py:4-8 | **[supported-in-code]** — bulk classification pools normalized spacings family-independently (`run_lmfdb_family.py:96-104,205-236`). |
| Dirichlet L: bulk GUE + Sp/U family separation at p=0.001 | README:477-479; CR:448-449; ES:1214-1216 | **[partial]** — split is by **symmetry type** (real→Sp, complex→U; `run_dirichlet_family.py:99-103`), NOT by "root number" as some prose implies. Edge KS machinery present (`run_dirichlet_edge.py:35-44,73-114`). **The literal `p=0.001` is NOT in code** — no `0.001`/`1e-3` significance constant exists (the only `0.001` literals are plot-grid starts); the p-value is a runtime KS output. Mechanism supported; specific figure + "root number" framing not. |
| RF `peak_q` discriminates L-function families with identical NNS | (README/memory framing) | **[not-found]** — no `peak_q`/`ramanujan`/`rf_amp` discriminator in `run_lmfdb_family.py`, `run_lmfdb_edge.py`, `run_dirichlet_family.py`, or `run_dirichlet_edge.py`. RF code exists elsewhere (`arithmetic_toolkit.py`, `rf_decoy_battery.py`) but is **not imported/invoked** by the L-function family scripts; family separation there uses only NNS-KS + edge-γ₁. |
| ζ first 2,000 zeros: KS_GUE=0.041, rep_int=0.425; at ~10⁶ KS_GUE 0.012–0.015 | README:472-473; CR:445-447; ES:1209-1211 | **[supported-in-code]** (figures are runtime) — ζ-zero classification pipeline present (`run_zeta_*.py`, `quadrant_marginal_test.py:54` `load_zeta`); values are outputs of `classify()` on Odlyzko zeros. |
| Γ₀(N) Maass Sarnak-anomaly replicated across squarefree levels; Berry-Robnik fitter bug caught + corrected | README:359; CR:455-458; ES:1333-1343 | **[supported-in-code]** — corrected Berry-Robnik fitter imported by axes (`axes.py:51` `from phase34e.run_berry_robnik import fit_rho`); `I9_berry_robnik_rho` (`:163`) routes through it; synthetic-validation discipline referenced (`:148,165`). |
| Mertens/Liouville sign-changes NULL beyond support/random-walk null | README; CR:450-451; ES:1310-1313 | **[supported-in-code]** — `run_mertens_liouville.py` (computes the orthogonal-channel nulls). |
| Arithmetic results reproduce literature, do NOT extend it (instrument-validation only) | README:303; CR:33-35; ES:1218-1223 | **[supported-in-code]** as honest scope — no novel-arithmetic code path; all arithmetic scripts are calibration/validation harnesses. |

---

## CALIBRATOR-ZOO / DATASET-SELECTION / INDUCTION-ON-NOISE DISCIPLINE
*(Claim text + source logged here; a separate agent audits whether each is actually wired in. Status below reflects whether the claimed code object exists, not full wiring.)*

| Claim | Source | Status |
|---|---|---|
| Calibrator zoo run BEFORE any unknown; class read relative to panel, never absolute threshold | README:225,244; CR:148-153; METHODS:66-83 | **[supported-in-code]** (object exists) — `cross_substrate/calibration_anchors.py:45-68`; `calibrator_panel.py`; acceptance gate "7/8 must land" (CR:152). |
| Three pre-registration / falsification tests must pass before reporting a classification | METHODS:59-64; WHY:43-51 | **[supported-in-code]** (object exists) — falsification runners `run_phase20_falsification.py`, `run_phase21_falsification.py`, `transition_diagnostic.py`. |
| Induction-on-noise: matching-quadrant on noise forces retraction | METHODS:251-258; README:653 | **[supported-in-code]** (claim logged) — threshold-upcrossing-on-iid → rep_int≈0.34 false-TR documented; control runs `run_controls.py`, `run_phase18_control.py`. *(Full wiring = separate-agent scope.)* |
| Extractor-invariance: ≥4 mechanism-distinct extractors required | METHODS:204-240 | **[supported-in-code]** (object exists) — `extractor_distinctness.py`, `extractors.py`, `llm_extractors.py`. *(Wiring depth = separate-agent scope.)* |
| Support-set-respecting nulls; right-null is substrate-specific; pooled sub-pool sweep before pooling | CR:180-193; ES (34a-c) | **[supported-in-code]** (claim logged) — `run_mertens_liouville.py`, `phase34*` runners; `quadrant_marginal_test.py:103-122` (positive controls `gen_periodic_q7`, `gen_rigid_grid_jittered`). |
| Near-boundary verdicts need 20-seed 80%-subsample replicate | CR:187-190; memory | **[supported-in-code]** (claim logged) — referenced in `hc3_cv2_diagnostic.py` sign-consistency / indeterminacy logic (`:73,118-141`). |
| Synthetic-validate any fitter before treating params as absolute (Berry-Robnik bug burned this in) | CR:511-513; ES:1340-1343; axes.py:148,165 | **[supported-in-code]** — corrected fitter wired (`axes.py:51`); "validate before banking" enforced in docstrings. |
| q_max=200 required; q_max=30 → 95.6% false-positive vs rate-matched Poisson | README:677; ES:779-785 | **[supported-in-code]** (claim logged) — surrogate-power runs `run_phase18_surrogate_calibration.py`; figure is runtime. |
| Dataset-selection gate (§7.ter.19): spike-sorted compatible, continuous-trace forces artifact | ES:834-837; README:648 | **[supported-in-code]** (claim logged) — `hc3_cv2_diagnostic.py:2` ("dataset-selection call BEFORE any CA1 pull"); peak-detection-artifact documented. |

---

## CROSS-SUBSTRATE / CROSS-DOMAIN GENERALIZATION

| Claim | Source | Status |
|---|---|---|
| ~25 substrates across 6 families charted (exploratory, NOT folded into validated set) | README:565,576-577 | **[supported-in-code]** — `cross_substrate/` holds the port files; honest "adjudicated separately" scope. |
| `ks_gue_med` is an unbiased proxy for matched plain-unfold ks-to-GUE (slope≈1) | README:579 | **[supported-in-code]** — proxy check in `cross_substrate/agreement_check.py`; `axes.py:111` `I5_ks_gue` is the matched plain-NNS object, explicitly distinct from pvc-11's Farey-banded `ks_gue_med` (docstring `:112-113`). |
| AM and Fibonacci Hamiltonian are empirically the same operator family; continuous stratification by approximability | README:584-589 | **[supported-in-code]** — `cross_substrate/am_confluence.py`, `fibonacci_lambda_run.py`, `brocot_approximability.py`, `confluence_view.py`. (Quantitative dimension constants flagged unresolved — DEGT form-not-constant, README:593.) |
| Per-cell fingerprints cohere; population observables fragment (8,462 cells × 7 areas = one substrate; aggregation sets the class) | README:597-600 | **[supported-in-code]** — `population_fingerprint.py:179-181` (three observables spanning the class axis). |
| Avalanche near-criticality orthogonal to per-cell class | README:603 | **[supported-in-code]** — `cross_substrate/allen_avalanche.py`, `attractor_analysis.py`. |
| Cross-domain (NANOGrav/CERN/single-molecule) mostly fails informatively at published-product level | README:348-351; CR:367-375; ES:865-1094 | **[supported-in-code]** (audit logic, not raw acquisition) — pipelines `grb_pipeline.py`, `bgp_pipeline.py`, `topology_hawkes.py`; verdicts STRUCTURAL_MISMATCH/BOUNDED recorded. |
| SOC calibrators (earthquakes, solar flares) recover known clustering; GK-decluster moves Poisson-ward | README:537,569; CR:407,466; ES:1803-1805 | **[supported-in-code]** — `comcat_port.py`, `comcat_fetch.py`, `goes_flares.py`; one-sided-fitter caveat coded (`comcat_port.py:19-20`). |

---

## TWO-ENGINE ARCHITECTURE & BAND-INVARIANCE

| Claim | Source | Status |
|---|---|---|
| NNS and RF engines are formally distinct objects, not views of one | README:50; CR:204-205 | **[supported-in-code]** — `joint_q_profile` (`arithmetic_toolkit.py:618`) ≠ `pll_bank` (`pll_bank.py`); CR:201-203 notes literal pll_bank "Not used by any deployed ARS classification". |
| NNS engine is q-flat / scale-invariant; cannot detect prime-base asymmetry on stationary signals (proved theorem) | README:51; CR:82-87; ES:77-80 | **[supported-in-code]** — under unit-mean renorm f_pll=a/q cancels; `canonical_spacings` (`axes.py:61-64`) trims+unit-mean-renorms identically across substrates, making Family I scale-invariant by construction. |
| RF engine carries per-prime arithmetic-class signal; v4 escapes band-invariance via raw integer grid; v1–v3 failed | README:47,55,179; CR:127-130 | **[supported-in-code]** — `padic_amplitude_v4` (`arithmetic_toolkit.py:298`), `padic_per_band` (`:230`), `padic_profile` (`:374`); RF family in `axes.py:341-370` (`III1_p_concentration` reads amplitude at q=p). |
| RF `a_q` is marginal-dominated; needs zoo-calibrated floor (~6 not ~1) | ES:1807-1809; CR | **[supported-in-code]** — `cross_substrate/rf_decoy_battery.py` (marginal-dominance demonstration). |

---

## NEGATIVE-ELIMINATION / RETRACTION FINDINGS (claims that the tool found *nothing*, honestly)

| Claim | Source | Status |
|---|---|---|
| Kuramoto-class does NOT explain ARS findings; four-way joint null (both engines × both timescales), 156/160 rows no match | README:617-621; CR:256-261; ES:541-661 | **[supported-in-code]** — `transition_calibrators_dynamical.py`, `chialvo_run.py`, `chialvo_calibrate.py`; pooled-rhythmic confound corrected (ES:590-595). |
| History-coupled GLM (H2 target) hits FIT-CEILING; zero FIT-PROPER cells | README:623; CR:175-178; ES:680-693 | **[supported-in-code]** (honest "untestable") — coupled-GLM surrogate logged as methodologically untestable. |
| LLM arc fully retracted — no measurement attributable to model vs extraction pipeline; 4 architectures × 8 extractors | README:311-320,694-717; ES:1258-1260 | **[supported-in-code]** — `llm_cascade.py`, `llm_extractors.py`, `run_phase10–17*` LLM runners; retractions recorded. |
| EEG θ-band reading falsified as bandpass-filter artifact | README:317,544; CR:467; ES:1243-1249 | **[supported-in-code]** — `run_eeg_full.py`, `run_eeg_depth.py`. |
| GRB 230307A 909 Hz QPO replication substantively failed | README:636; CR:476-477; ES:701-712 | **[supported-in-code]** — `grb_pipeline.py`, `lightcurve_modulated_surrogate.py`. |

---

## SCOPE / PROVENANCE DISCLAIMERS (claims about what the tool does NOT do)

| Claim | Source | Status |
|---|---|---|
| ARS contributes no new theoretical mathematics; applied implementation of existing (Planat) framework | README:68,71,830; CR:31-35; METHODS:5-8; ES:1289-1291 | **[supported-in-code]** — no novel-theory code; arithmetic paths are validation harnesses; `CFF:146` ARS Engine 1 implements Planat–Rosu RF directly. |
| Instrument is bounded in two independent senses (extractor-layer + finite calibrator/null enumeration) | WHY:98-134,168 | **[supported-in-code]** — extractor-layer bound = continuous-trace artifact (`run_controls.py`); enumeration bound = finite `calibration_anchors.py` panel. |
| Apparatus-subtraction module exists (dead-time, thinning, sort-merge, three-zone) | ES:1761-1763; memory instrument_confound | **[supported-in-code]** — `cross_substrate/instrument_confound.py`. |

---

## SUMMARY COUNTS

Rows: ~70. By status:
- **[supported-in-code]: ~52**
- **[partial]: ~5** (rate+burst not co-controlled in one file; CV 2–7× magnitude is runtime; Dirichlet p=0.001 not a code constant + "root number" mislabel; ζ figures runtime). *(DSI moved to [supported-in-code] on 2026-06-30 review.)*
- **[not-found]: 1** (RF `peak_q` L-function family discriminator — not wired into the L-function scripts)
- **[contradicted-by-code]: 1** (long-range as the *default* verdict instrument — the deployed classifier still keys on marginal-NNS)

The remaining rows where I tagged supported-but-noting "figures are runtime" are counted as
supported (the code path exists; only the specific numeric literal is an output, which is expected
and not a discrepancy).

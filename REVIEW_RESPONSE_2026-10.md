# Response to the independent review (2026-10-14)

An outside reviewer read the public repository (`main` at `fe917661`, `specarith` at `0f0c5f77`). This file records
what changes as a result. **It is additive:** no existing text is rewritten; the affected sections carry a one-line
banner pointing here, in the house style of correcting in place. Every reviewer claim used below was re-checked
against the code at `fe917661`; **all file:line references are to that commit** (the banners added with this file
shift some line numbers); where the review's framing was inaccurate, §6 says so. Edits to
README, `.zenodo.json` and `CITATION.cff` text themselves are Will's call.

## 1. What the ARS toolkit actually computes (corrected description)
- **Spacing engine.** Per Farey q-band, the inter-event spacings are pooled across numerators, normalised to unit
  mean, and compared by a Kolmogorov–Smirnov distance with the **2 × 2 Wigner surmises** (Poisson e^{−s}; β = 1, 2) —
  not with the exact GUE (Gaudin) spacing law (`arithmetic_toolkit.py:105–114`, `universality.py:35,47`). The
  headline `ks_gue_med` is the median of these distances over well-powered bands.
- **The Farey bands are band-invariant by construction.** The band spacings are `diff(t·f − 1)` with f = f_c·a/q,
  normalised by their mean (`arithmetic_toolkit.py:767–774`), so f cancels: every band sees the same raw inter-event
  spacing sequence, up to a one-period left truncation (`passage > 0`). README.md:150 states this cancellation; its
  consequence should be explicit: **the bands carry no independent frequency information, and differences between
  bands come only from the truncation and from how many numerators are pooled.**
- **`n_events_q` is not a sample size.** It sums the passage count over all coprime numerators a of q
  (`arithmetic_toolkit.py:775`), ≈ Σ_a (events), so it counts each event many times (`bulk_recovery.py:88–90` already
  notes this). Power flags gated on it (`:821`) overstate the effective sample.
- **"Embeds a sequence into a chirp signal, runs a GPU-parallel bank of Farey-rational phase-locked loops" is
  withdrawn from the abstract text** (`.zenodo.json:10`, `CITATION.cff:6–7`; RESULTS.md:65 similar). The deployed engine
  (`joint_q_profile`) is analytical and uses neither the chirp nor the PLL bank (RESULTS.md:76–78; RESULTS.md:374: "the
  chirp/PLL stack is **not** measuring eigenvalue NNS"). The legacy chirp path imports `scanner.py`, which is not in
  the repository (it lives outside it; `audit/05-runtime.md:20–21`): six direct importers, including `signal_gen.py`,
  which ~20 further files import.

## 2. Status changes
- **H1 (OSI ↔ `ks_gue_med`): "confound unaddressed"; no longer load-bearing.** Firing-rate *variance* across stimulus
  conditions moves a pooled-ISI KS statistic mechanically, and controlling for mean rate does not remove that. The
  trial-PSTH unfold that would test it was applied to Σ² only (`cross_substrate/longrange_allen_psth_audit.py:75–113`),
  where the analogous OSI correlation collapsed, +0.135 → −0.077 (`cross_substrate/INSTRUMENT_CONFOUND_FINDINGS.md:426`).
  No PSTH-unfolded or per-condition `ks_gue` exists. Until one does, H1 is a correlation with an open, specific
  confound. (A decisive rerun is designed in the review; whether to run it is Will's call.)
- **p = 7 (pvc-11 gratings): withdrawn.** The RF in `padic_amplitude_v4` bins in one-time-unit bins
  (`arithmetic_toolkit.py:203,207`, `n_bins=None` at `:364`) and event times are in seconds
  (`phase22a/population_events.py:130`), so q = 7 reads a **7 s period** — seven concatenated 1 s grating trials
  (`phase22a/loader.py:38`). RESULTS.md:6931's "q=7 period = 35 ms at bin_ms=5; 28.6 Hz" confuses the 5 ms
  event-extraction bin with the RF bin. The surrogate is a homogeneous uniform re-draw that ignores the trial schedule,
  with 3 draws for the headline z = +9.77 (`phase31b/monkey12_gratings_qmax200.py:34`; 5 in other scripts) and no
  correction across the six primes tested. The statistic depends on the choice of time unit, so it is retired, not
  repaired.
- **AM ≡ Fibonacci: exploratory.** It rests on a one-parameter sweep: Fibonacci's box dimension D_box(λ) crosses the
  critical AM value at λ ≈ 3.4, and the other fingerprint coordinates are compared at that λ
  (`cross_substrate/PROGRESS_REPORT.md:220–238`). A one-parameter curve crossing a point is not an identity of operator
  families. For the actual relation between the two families see Kraus & Zilberberg, "Topological equivalence between
  the Fibonacci quasicrystal and the Harper model", arXiv:1204.3517 (Phys. Rev. Lett. 109, 116404 (2012)).

## 3. Errata (numbers)
- **RESULTS.md:4932 and :4941.** The OSI ↔ `ks_gue_med` correlation is a Spearman partial correlation (firing rate
  partialled out; `phase22a/h1_crossval.py:133–149`), ρ = +0.720, n = 210. Its p-value is **≈ 1e-34** (t-approximation:
  t = 14.96; df = 207, as in the code: 1.1e-34; df = 208: 7.6e-35), not "< 1e-300" (:4932) or "< 1e-37" (:4941). The
  "< 1e-300" came from `2*(1 − cdf)` underflowing to 0; `EPISTEMIC_STATE.md:124–127` had already flagged the three
  inconsistent forms. (The size of ρ is unaffected; §2 is what limits H1.)
- **REPRODUCE.md:7–9.** "No data downloads are needed for any arithmetic or synthetic arc" is wrong for `specarith/`:
  it needs Odlyzko's and LMFDB/Platt zero files and computed L-function zeros (`specarith/DATA_MANIFEST.md`).

## 4. specarith Stage 2: wording and context
- **Wording.** Stage 2 is stated as: *"consistent with the Conrey–Snaith (2008) prediction (conditional on the ratios
  conjecture; one statistic; ±13%)."* The phrase "evidence for that conjecture's higher-order structure"
  (`specarith/ph2s2/PH2S_STAGE2_FINDINGS.md`, Limits) is withdrawn until the term ablation
  (`specarith/cs4/STAGE2_ABLATION_DESIGN.md`, rule declared before computing) shows which correlation class carries the
  predicted shrink. If two-point arithmetic alone reproduces it, the claim becomes "confirms two-point arithmetic
  correlations at fresh heights; does not discriminate CS08's higher-order terms". The Stage 2 verdict (PASS) and its
  numbers are unchanged.
- **Novelty paragraph: earlier work it must name.** The adopted wording (PH2S Stage 1 findings; twenty-second round)
  is about the block-length dependence of a *local pair statistic's* variance. These earlier results show that prime
  (arithmetic) structure governs long-range statistics of the zeros and belong beside it:
  - A. M. Odlyzko, "On the distribution of spacings between zeros of the zeta function", *Math. Comp.* 48, 273–308
    (1987), doi:10.1090/S0025-5718-1987-0866115-0 — long-range correlations between zero spacings, measured.
  - O. Bohigas, P. Leboeuf, M. J. Sánchez, "Spectral spacing correlations for chaotic and disordered systems",
    *Found. Phys.* 31, 489–517 (2001), doi:10.1023/A:1017569612944; arXiv:nlin/0012049 — a parameter-free prime-sum
    prediction of those spacing correlations (their Eq. 3.1), compared with Odlyzko's data.
  - M. V. Berry, "Semiclassical formula for the number variance of the Riemann zeros", *Nonlinearity* 1, 399–407
    (1988), doi:10.1088/0951-7715/1/3/001 — the prime-sum (non-universal) number variance and its saturation, a
    linear statistic.
  - (References checked against the publishers' metadata via Crossref, 2026-10-14; the papers themselves were read in
    full for `specarith/ph2s/lit/PAIRSUM_VARIANCE_LIT.md`.)
- **CS08 errata.** Before any message to the authors, the per-version printed lines are now quoted in
  `specarith/cs4/CS08_ERRATUM.md` §1.1: arXiv has v1 only; the journal prints the same A* factor and J₁₃ sign; no
  corrigendum was found.
- **Pre-decode timestamp (route (a)).** Seals are git tags with author-controlled timestamps, and history was rewritten
  once (2026-09-21). The route (a) prediction tag and rule files are now covered by an OpenTimestamps receipt
  (`specarith/cs4/timestamps/`); the route (a) seal gets its own before the F3 data is decoded. A stamp bounds *when*
  the prediction existed; it cannot show that public data was not looked at earlier — that rests on the pre-registered
  order and the recorded md5-before-decode checks.

## 5. Not done now (migration list; the legacy tree stays frozen)
`verify_all.py` to resolve cited hashes through `provenance/cited_commits.tsv` (the review's "missing" `9eb285a` is
mapped there, line 92, → `8c2d7ce`); specarith on the verify board; cupy optional (it is already guarded in
`pll_bank.py:54–59` but a hard import in 9 legacy scripts); declare `pyarrow`, `huggingface_hub` (and `pandas`, used by
the core engine at `arithmetic_toolkit.py:742`, plus `torch`, `requests`); commit or remove `scanner.py`'s importers;
replace hard-coded `/home/combust/...` paths (121 .py/.sh files; 177 files of any type) with a `paths.toml`; a one-page
outsider claim ledger (≤ 10 claims, each with its status).

## 6. Where the review's framing needed correcting
- **p = 7's "35 ms".** Not aliasing: RESULTS.md's 35 ms is a units confusion (5 ms event bin vs the RF's 1 s bins);
  the RF period is 7 s. The withdrawal stands on the units dependence and the surrogate, as the review says. Headline
  surrogate draws: 3, not 5.
- **ρ = 0.72** is a Spearman partial correlation, not Pearson; the review's p ≈ 1e-34 is right under the
  t-approximation either way.
- **The chirp/PLL text** appears in `.zenodo.json` and `CITATION.cff` (and RESULTS.md:65), not in README.md, and
  describes a legacy path the deployed engine does not use; the missing `scanner.py` breaks that path, not the engine.
- **"121 files"** with hard-coded paths is the count of .py/.sh files; across all files it is 177.

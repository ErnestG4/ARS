# Divisor Harmonics v0 — pre-registration (SEALED at the commit that adds this file; code sealed in the same commit)

Source: CC Brief "Divisor Harmonics v0" (Will, 2026-10-03; `briefs/DIVISOR_HARMONICS_V0.md`). Side project: idle GPU time
and spot CPUs only, never ahead of the main arc's queue. All operating rules carry over (GPU-only hard assert, seal before
reading, no method changes without Will, detached + resumable jobs, completion waits).

## 0. Citations (verified 2026-10-03 from arXiv)
- **Karkada, Korchinski, Nava, Wyart, Bahri, "Symmetry in language statistics shapes the geometry of model
  representations", arXiv 2602.15029 (v2, 2026-06-29).** Verified: translation symmetry of co-occurrence (Assumption 3.1,
  P_ij = P_i P_j C̃(dist)); exponential kernel C(Δx) = Σ_n exp(−|Δx + 2n|/σ) (domain period 2); Corollary 2 (periodic):
  k_n = πn, a_n = √(2σ/(1+σ²k_n²)); Proposition 3 (open): same amplitude law with self-consistent k_n
  (k_n = (n+1)π/2 − arctan(σk_n) for odd n; nπ/2 + arctan(k_n/(1+σ(1+σ)k_n²)) for even n). LLM probe: Gemma 2 2B,
  resid_post at every layer, final token; month template "The month of the year is [MONTH]"; "May" excluded only from the
  static-embedding PCA basis ("absent" for LLMs, which disambiguate from context).
- **Kantamneni & Tegmark, "Language Models Use Trigonometry to Do Addition", arXiv 2502.00873 (2025).** Verified: numbers
  (a, b ∈ [0, 99]; periodicity studied on [0, 360]) are represented as a generalized helix with Fourier features of periods
  **T = [2, 5, 10, 100]** (§4.2, §4.3, §5.4.1), in GPT-J, Pythia-6.9B and Llama-3.1-8B. The brief's citation holds. Note:
  T = 100 was chosen "by applying the inductive bias that our number system is base 10"; it is the open-lattice fundamental
  of [0, 99] and is NOT a divisor-class prediction here.

## 1. Question and hypotheses (brief §1–2, verbatim in intent)
Does real usage give the divisor classes of composite periods more amplitude than the Lorentzian (translation-symmetry)
model predicts? **H0:** no class excess after the Lorentzian fit. **H1:** some nontrivial class carries leftover power above
the null. **Prime control** (weekdays, N = 7): no nontrivial class; Lorentzian with white residuals; any excess = pipeline
broken. **Shuffled control** (12 nouns, fixed random order): no cycle, everything null. Declared directions (descriptive
bets, not tests): months d = 3 (quadrimesters) and d = 4 (quarters); hours d = 12 (am/pm) and d = 6 or 8 (shifts); numbers
d = 2, 5, 10 (frequencies 50, 20, 10 on 0–99).

**Class index.** For harmonic n of period N, the class is **d = N/gcd(n, N)** = the number of polygon vertices = the period in
items (Ramanujan sum c_d collects exactly these harmonics). The brief's "q" is this d. Nontrivial classes 1 < d < N:
months {2, 3, 4, 6}; hours {2, 3, 4, 6, 8, 12}; numbers (N = 100) {2, 4, 5, 10, 20, 25, 50}; weekdays none. Months'
harmonics: d=2 ↔ n=6; d=3 ↔ n=4; d=4 ↔ n=3; d=6 ↔ n=2; d=12 ↔ n=1, 5.

## 2. Concepts, items, templates (FROZEN in `templates.py`; tokenisation audit `results/divisor/tokenisation_audit.json`)
| Concept | N | BC | Role | Audit |
|---|---|---|---|---|
| months Jan–Dec | 12 | periodic | composite | all single-token; every template names the calendar frame before the item |
| hours "H:00", H = 0..23 | 24 | periodic | composite | **every item is 3 tokens (' H', ':', '00'); the item-final token '00' is shared by all 24** |
| weekdays Mon–Sun | 7 | periodic | PRIME CONTROL | all single-token |
| numbers 0–99 | 100 | open | composite | all single-token (no multi-token column needed) |
| nouns, fixed random order (seed 20261003) | 12 | none | SHUFFLED CONTROL | all single-token |
16 templates per concept, item last. **Hours decision (sealed):** the brief's primary read is the LAST item token, kept as
primary (the hour lives in the context seen at '00'); the FIRST item token (the hour number ' H') is stored and reported as a
declared secondary column. No alternative 24-hour rendering gives an item-specific final token ('{}h', "o'clock", "H00
hours" all end in a shared or variable token; audited). Will may amend this before extraction.

## 3. Models and data (brief §4)
Primary **Pythia-1.4B** `step143000`; replication **Pythia-410M**, **Pythia-70M** `step143000` (safetensors fetched 10-03).
Trajectory (DESCRIPTIVE): Arm B **A0** checkpoints (GPTNeoX, pythia-70m config, fp32), steps {0, 1, 2, 4, 8, 16, 32, 64,
128, 256, 512, 1000, 1500, 2000, 2500, 3000, 4000, …, 10000} (23, pulled from spot:~/llmspec_armb/ckpt/A0 to
~/llmspec_div/A0). Weights only; no Arm B bulk-vector statistic is read (split-sample rule intact).

## 4. Pipeline (sealed; `divisor_extract.py`, `divisor_spectrum.py`)
1. **Extract** (GPU): resid_post of every block (+ embedding output) at the item tokens, fp32, right-padded batches;
   `results/divisor/acts/<tag>.npz`, sha256 manifest.
2. **Primary layers:** the middle third of the blocks, indices ⌊L/3⌋ … ⌊2L/3⌉−1 (1.4B/410M: blocks 8–15; 70M: 2–3),
   averaged BEFORE the spectrum. Every other layer: descriptive (`--layers all`).
3. **Template average** per item (sealed); per-template spectra = descriptive robustness.
4. **Spectrum:** mean-centre over items; DFT along the item axis of the (N × d) matrix; P(n) = Σ_dims |F_n|² folded onto
   n = 1 … ⌊N/2⌋ (Parseval; no PCA).
5. **Lorentzian null (exponential kernel on the lattice, spacing 2/N, q = e^{−2/(σN)}):** periodic
   L(n) = s(1−q²)/(1−2q cos(2πn/N)+q²) (brief §5.4). **Open (numbers):** the exact periodogram expectation of the same
   kernel on an open segment, L(n) = (s/N) Σ_{|m|<N} (N−|m|) q^{|m|} cos(2πnm/N). This is Proposition 3's kernel read in
   the DFT basis (the brief says "treat periods as frequencies"); Proposition 3's quantised k_n are the Karhunen–Loève
   basis of the same kernel and are not used, since the statistic is the DFT. Fit: 1-D grid over σ (801 log-spaced points
   in [10^−2.5, 10^2.5], domain units), closed-form scale, least squares in log power (relative weighting).
6. **Class statistic:** E_d = Σ_{n∈d}(P(n) − L̂(n)); z_d and one-sided p from the parametric bootstrap (§5); relative excess
   R_d = E_d / Σ_{n∈d} L̂(n) reported beside it.

## 5. Nulls, gates, multiplicity, power (brief §6)
- **Item-shuffle null:** 10 000 permutations of the item order; statistic = lag-1 autocorrelation of the item sequence,
  ρ₁ = Σ_i ⟨x_i, x_{i+1}⟩ / Σ_i ‖x_i‖² (circular for periodic BC; open for numbers), permutation-exact. **Cycle gate:**
  CYCLE PRESENT iff ρ₁ exceeds the 99th percentile of the shuffles (p ≤ 0.01). The fundamental fraction f₁ = P(1)/ΣP is
  reported descriptively (the fast verifier showed it under-powered at N = 12).
- **Known limitation, declared:** the two-parameter fit has no white-noise term (brief §5.4: σ and scale only), so when the
  spectral tail is noise-dominated σ̂ reads low and the tail residuals read positive. The bootstrap goes through the same
  fit with matched noise, so the class p-values are calibrated against this (false-alarm check in the verifier); σ̂ is
  DESCRIPTIVE, never a verdict, and the smallest-detectable-excess table carries the resulting power loss.
- **Lorentzian parametric bootstrap (B = 4000):** Gaussian Fourier coefficients with per-harmonic variance L̂(n), living in
  a random k_eff-dimensional subspace of R^d (k_eff = participation ratio (Σs²)²/Σs⁴ of the real centred item matrix), plus
  isotropic noise with variance = mean across-template variance / T (the template-averaging noise); every draw goes through
  the identical fit and statistics. One-sided p_d = (#{E_d^null ≥ E_d} + 1)/(B + 1).
- **Control gates (all must pass or NOTHING is interpreted):** weekdays residual-whiteness, max_n |log P − log L̂| not above
  the bootstrap 99th percentile (p > 0.01); nouns cycle gate NULL (p > 0.01) and no class p below 0.01/#classes.
- **Multiplicity:** Holm at α = 0.05 over the 17 (concept × nontrivial class) tests of the PRIMARY model (months 4, hours 6,
  numbers 7). Replication models: the same 17 tests, reported as REPLICATES / DOES NOT REPLICATE per rejected class.
- **Power (per concept, per class, measured on the real geometry inside each run):** excess f ∈ {0.02, 0.05, 0.1, 0.2, 0.4,
  0.8} of the fitted Lorentzian power planted into the class through the same generator; detection against the unplanted
  null's 95th percentile and against the Holm first-step level 0.05/17; 200 draws each. **Smallest detectable excess** =
  smallest f with Holm-level power ≥ 0.8; none → H1 is **NOT RESOLVABLE** for that class.
- **Red paths before sealing (`verify_divisor.py`, `--redpath`):** σ recovery (periodic and open); false-alarm rate and
  zero Holm rejections on null data; prime control whiteness; planted f = 0.8 (a near-doubling of the Lorentzian power
  placed in one class) detected at the Holm level in ≥ 80 % (months d=4, hours d=12), smaller f reported as power; cycle
  gate silent on white data and firing on a Lorentzian cycle (σ = 0.6; its rate at a broad σ = 0.25 reported as information); item-shuffled planted data NOT detected; red path 1 = an identity
  "fit" must hide the planted excess; red path 2 = a mis-scaled null must inflate false alarms. CHECKRUN line in the
  sealing commit.

## 6. Reading rule (words from the memo vocabulary)
- **H1 HOLDS (class d of concept c)** iff Holm rejects (c, d) in the primary model AND all control gates pass AND the
  smallest detectable excess for (c, d) is ≤ the observed R_d (the detection is inside the instrument's range).
- **H0 HOLDS for (c, d)** iff not rejected AND the smallest detectable excess ≤ 0.2 (the instrument could have seen a 20 %
  excess); otherwise **NOT RESOLVABLE**.
- **INAPPLICABLE** for a concept whose cycle gate is NULL in the primary model (no cycle to decompose), reported as such.
- **BROKEN** (nothing interpreted) if a control gate fails. Replication words per class as in §5. The trajectory, per-layer,
  per-template and hours-first-token columns are DESCRIPTIVE. Polygon-projection figures illustrate aliasing; not evidence.
- Direction bets (§1) are scored descriptively: for each, "excess sign and rank among the concept's classes".

## 7. Deliverables and compute
`divisor/DIVISOR_FINDINGS.md`; `results/divisor/<tag>_last_primary.json` (+ `_all`, `_first`), figures under
`plots/divisor/`; open-leads section. GPU: minutes per model, only when NOTES §4 reads `GPU_STATUS: FREE` and the ext_queue
is idle. CPU nulls: spot (`~/llmspec_div/`, tmux `claude`, numpy only) or this box.

## Amendment A1 (2026-10-03, BEFORE any real activation is read; from the synthetic end-to-end run of `divisor_spectrum.py`)
- **§6 H1 HOLDS loses its third clause.** The clause "smallest detectable excess ≤ observed R_d" was self-defeating: a large
  real excess contaminates the two-parameter fit (σ̂ drops, L̂ flattens), and the planted-power table computed under that
  contaminated L̂ degrades (synthetic months with a planted f = 0.8 in d = 4: Holm rejection at z = 24 while the table read
  "none detectable"). H1 HOLDS iff Holm rejects (c, d) in the primary model AND every control gate passes. The power table
  governs ONLY the H0 HOLDS / NOT RESOLVABLE split and is reported beside every verdict.
- **σ̂ degeneracy, declared:** for σ ≳ N/2 (domain units) every lattice Lorentzian collapses onto the 1/(1 − cos(2πn/N))
  shape, so the grid maximum (316) is read as "at the 1/(1−cos) limit", not as a correlation length. The fitted SHAPE is
  what the class statistics use; σ̂ is descriptive (as already declared).
- **Power table under contamination:** the table is computed under the fitted L̂ of the real spectrum, so where a real excess
  exists it understates power. Reported as such; no re-fit excluding classes (that would be a method change).
- Figures script `divisor_plots.py` and the spot runner `run_spectrum_spot.sh` added (no analysis change).

## Amendment A2 (2026-10-03 09:30, AFTER the primary read; code fix only, no analysis change)
- The descriptive first-token pass (`--read first`, hours only) crashed in the entry point because the Holm/gates block
  assumed every concept present. Fix: Holm and gates are computed only for the sealed primary read (`--read last`,
  `--layers primary`). `run_concept` and every statistic are untouched; the 26 primary results written before the fix
  stand as read.

## Addendum A3 (2026-10-03, Will's review; SEALED at its commit, BEFORE any token count or residualised activation is read)
**Numbers: rule out token frequency first.** Round numbers dominate text (multiples of 5 and 10, even numbers, powers of
2), so an activation component that tracks an item's log-frequency produces peaks at periods 2, 4, 5, 10 with no concept
of divisibility; the trajectory's early onset (step 256, when small models learn unigram/bigram statistics) sharpens this.
- **Frequency source:** the Pile sample banked on spot (`~/llmspec_armb/data/seed1_batches`, 3002 batches × 1024 × 2049
  uint16 tokens ≈ 6.3 × 10⁹ tokens; PolyPythias seed-1 order = a uniform shuffle of the Pile, so unigram frequencies equal
  the Pile's in expectation). Counted: the exact item tokens ' 0' … ' 99' (space-prefixed, as in the frozen templates);
  the bare tokens '0' … '99' are counted beside them (descriptive). numpy bincount; `divisor_freq_control.py count`.
- **Covariate:** c_i = log(count_i + 1), mean-centred over the 100 items. **Can-fire prerequisite:** the class
  decomposition of c's own DFT must put > 10 % of its power in d ∈ {2, 4, 5, 10}; otherwise the control is INAPPLICABLE
  (a comb that is not there cannot be regressed out).
- **Residualisation (primary, linear):** on the primary numbers matrix (blocks 8–15 averaged, template mean X̄, 100 × d),
  β = OLS slope of X̄ on c; X′ = X − c βᵀ applied to every template (same β). **Secondary (quadratic):** c and c² − mean.
  Then the SEALED class test (`run_concept`, unchanged) on X′, Holm over the same 17 tests with the other concepts' p-values
  from the primary read.
- **Reading per class d ∈ {2, 4, 5, 10} (primary 1.4B; 410M / 70M beside it):** SURVIVES iff Holm still rejects after the
  linear residualisation; VANISHES iff not rejected and the smallest detectable f on the residual geometry ≤ 0.2;
  NOT RESOLVABLE otherwise. The explained fraction ‖c βᵀ‖²/‖X̄‖² and R_d before/after are reported.
- **Scope:** a linear log-frequency regression removes a rank-1 frequency component; a non-linear frequency effect is not
  excluded by it (declared; the quadratic column is the one step beyond linear taken here).
- **Verifier `verify_divisor_freq.py` (`--redpath`):** synthetic comb (profile with peaks at multiples of 10, 5, 2 and
  powers of 2) is detected before and VANISHES after residualisation; a genuine class-5 plant built orthogonal to the
  profile SURVIVES; a shuffled (wrong-instance) covariate leaves the comb; red path: oracle covariates (the class's own
  harmonics, not the sealed covariate) erase a genuine plant.
- **Citations (verified 10-03):** Zhou, Fu, Sharan, Jia, "Pre-trained Large Language Models Use Fourier Features to
  Compute Addition", arXiv 2406.03445 (NeurIPS 2024 per Will; venue not shown on the fetched arXiv page → UNVERIFIED):
  outlier Fourier components with periods 2, 2.5, 5 and 10 (§3.2, §4.1; GPT-2-XL and others; numbers ≤ 260). Period 2.5
  on the integer lattice is frequency 2/5 → class d = 5 here. Kantamneni & Tegmark 2502.00873: T = [2, 5, 10, 100]
  (verified, prereg §0). So periods 2, 5, 10 REPLICATE published findings in the divisor framing; period 4 is the part
  not in those papers and the one most exposed to the frequency comb (powers of 2 in computing text).

## Amendment A4 v2 (DRAFT for Will's seal; designed 2026-10-03 AFTER A3's descriptive result was seen → a CONFIRMATION RUN, not a blind test)
Will's refinement of the A3 follow-up: regression removes one linear frequency direction per layer, so non-linear
frequency effects survive it and a "no change" says little. A4 v2 uses a **stratified permutation null** instead.
- **H0_freq:** an item's activation depends on its corpus frequency (any function of it) plus noise, and on nothing about
  the number beyond that. Under H0_freq, items of matched corpus count are exchangeable.
- **Null:** 10 000 permutations of the item order **within frequency strata** — 10 bins of 10 items by rank of the exact
  item-token count (A3's counts, results/divisor/number_token_counts.json); the within-stratum count range is reported.
  Every permuted matrix's spectrum is scored against the OBSERVED Lorentzian fit held fixed (a permutation destroys the
  translation-symmetry structure the fit models; re-fitting per permutation biased E_d in the verifier); p_d one-sided for
  d ∈ {2, 4, 5, 10}; Holm over the four. The ordinary (unstratified) shuffle p and a 5-bin sensitivity column are
  reported beside it. Primary model 1.4B; 410M / 70M beside it. `divisor_strat_control.py`.
- **Words per class:** SURVIVES iff Holm rejects against the stratified null (frequency, linear or not, does not explain
  the excess); VANISHES iff p_strat > 0.05 while the unstratified shuffle rejects (the excess exists but is carried by
  frequency); NOT RESOLVABLE otherwise.
- **Verifier `verify_divisor_strat.py` (`--redpath`), run before the seal:** strata matched (median within-bin max/min
  count ratio < 3); a synthetic NON-LINEAR frequency feature (tanh of the detrended comb of the real counts) is detected
  by the ordinary shuffle but does not SURVIVE the stratified null; a genuine class-5 plant SURVIVES; A3's linear feature
  does not SURVIVE; red path: a single stratum makes the comb SURVIVE (stratification does the work).
- **Verifier findings before the seal (10-03):** (i) with the REAL counts, a feature that is any monotone function of
  count alone creates NO detectable class excess at any amplitude (amp 6–100: the count profile is magnitude-dominated,
  the Lorentzian fit absorbs it) — so a frequency-only feature cannot reproduce the observed comb in the first place;
  the stratified machinery is exercised on a synthetic comb-dominated count profile (detected by the ordinary shuffle,
  VANISHES under its strata, SURVIVES with one stratum). (ii) The permutation statistic must use the OBSERVED Lorentzian
  baseline held fixed (re-fitting per permutation biased E_d because permutation destroys the smooth structure).
  (iii) A feature that depends on count AND magnitude (the detrended comb, a "roundness" feature) is outside H0_freq and
  SURVIVES the stratified null by construction — A4 does not claim to control it (it is representation content).
- **Scope:** the strata are matched on the exact item token's count only; a frequency effect driven by other surface
  forms of the same number (bare digits, words) is not stratified for (declared). Hours read position: left as sealed
  (only matters on re-extraction).

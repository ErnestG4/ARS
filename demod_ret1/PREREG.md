# PRE-REG — ret-1 serial-order test (demodulation arc)

**Status: DRAFT, 2026-09-21, amended the same day (Will's amendments: cell sets, unit of replication,
population-median bars, rival covering P3, ledger, instrument). Nothing runs until Will says go. STOP 1 is
resolved by the amended cell sets; STOP 2 (instrument not received) is open; STOP 3 is folded into the
Part A cell's gate.**

- Repo: `$HOME/fmexplorer/criticality_tool/`
- Python: `$HOME/fmexplorer/bin/python3`
- Branch: `demod-ret1` from `main` (worktree `.claude/worktrees/demod-ret1`). Nothing on the ring
  worktree or its branch.
- New files: under `demod_ret1/` only. `DEMODULATION_FINDINGS.md` is not edited; findings go in
  `demod_ret1/FINDINGS.md`.
- Data: `data/ret-1` (`crcns_ret-1.zip`; the loader reads the extracted `.mat` files from
  `$HOME/fmexplorer/crcns_cache/ret1/crcns_ret-1/Data`, `cross_substrate/ret1_port.py:41`).
- Instrument: `realdata_checks.py`, to be filed under `demod_ret1/`, with `--selftest` passing in this
  environment first.

## Two things that stand unconditionally, before any run

1. **1.0 spikes/burst at a 5 ms threshold says nothing about bursts** when 5 ms is at or below the refractory
   floor (rate-free).
2. **A stationary renewal process has a long-range Σ² slope that tends to CV².** ret-1's CV² = 2.14 against a
   sub-1 slope therefore already implies **serial correlation or nonstationarity**. What is conditional is
   how that applies to the real trains; the shuffle test decides it.

## The claim under test (corrected from the prior look)

`DEMODULATION_FINDINGS.md` reads ret-1 as **strong short-range clustering + sub-Poisson long-range
rigidity** (R₂(0.1) ≈ 2.5, Σ² slope 0.44–0.78 against CV² = 2.14), calls the γ-model contradiction
"one parameter cannot set two scales", and rules out bursts from **1.01 spikes/burst at a 5 ms
threshold**. The serial-order alternative: ret-1 is a **non-renewal** process whose sub-Poisson
long-range variance is the serial-correlation factor, F∞ = CV²(1 + 2Σρ_k), with the short-range mass
from within-event intervals. Under that alternative an ISI shuffle destroys the rigidity (slope → CV²)
and the clustering exceeds a rate-matched Poisson at 20–50 ms while reading Poisson-like at 5 ms
(below the refractory floor). **A pass licenses NON_RENEWAL_SERIAL_CORRELATION, not a mechanism**
(see Rival).

## Prior look (disclosed)

`demod_ret1/prior_look/demod_labels_and_ret1_toy.py` (Will, 2026-09-21; output alongside):
- A hand-built firing-events toy, k_e tuned 6 → 8 to bring its slope into ret-1's range, read
  CV² 1.81, slope 0.69 → 1.88 after ISI shuffle, CV²(1+2Σρ) 0.68, clusters/burst 1.00 / 1.09 / 1.54
  / 2.81 at 5/10/20/50 ms. It does **not** match ret-1 on R₂(0.1) (4.1 vs ~2.5) or the 10/20 ms cluster
  counts (1.09/1.54 vs 1.24/1.78). It is a counter-model that breaks two inferences, not a fit.
- The toy's ~7 Hz ret-1 rate was **inferred** from the findings' Poisson-collapse rows, not measured.
  Measured 2026-09-21 from the committed loader over the ≥ 6k-ISI cells: **median 11.6 Hz, range
  4.1–41.4 Hz**. Whether "44 % of ISIs under 20 ms" is bursting depends on the rate (Poisson at 29 Hz
  puts 44 % under 20 ms); the rate-free point — 1.0 at 5 ms says nothing about bursts — stands.
- Part A of the toy (labels track timescale relative to W) is a **separate cell**, not this pre-reg:
  run a fast Cox and a slow intrinsic cycle through the repo's own demodulator at the findings' W
  values, then either keep the mechanism labels where the calibrators discriminate or rename them
  SLOWER_THAN_W / FASTER_THAN_W. (STOP condition 3 below applies to it too.)

## Cell sets (committed ret-1 loader `overnight_2026_07_12/loaders.py:load_ret1`; every cell ID listed in the seal)

- **PRIMARY:** all cells with ≥ 6,000 ISIs (**183**), each truncated to its **first 6,000 ISIs**.
- **TIER-2:** all cells with ≥ 18,000 ISIs (**60**), each truncated to its **first 18,000 ISIs**.
- **JULY (secondary, disclosed):** the 28 July cells, only if `demod.log` (975997c) lists their IDs.
  **Checked 2026-09-21: `demod.log`, `demod2.log` and `demodcoup.log` contain no cell IDs (0 hits for
  `ret1/`). The JULY set is OMITTED.** The July selection rule is not reconstructed.
- Full-length per-cell results: report-only.
- Why not 25: that number came from an uncommitted subsample. The gap between 25 and 183 is the finding,
  not a reason to guess the subsample.

## Unit of replication

- **Recording** = the loader's recording identifier (`ret1/{recording}/{cell}`, the `.mat` basename —
  e.g. `20080516_R1`). The loader yields **16 recordings** (2026-09-21 count), so the bootstrap applies.
- Recording is the **lineage group**: cells in one recording share the stimulus, so they are not
  independent under the stated rival.
- Population uncertainties: **bootstrap over recordings, 2,000 resamples** (declared), never over cells.
- Fallback (not needed at 16): fewer than 8 recordings → sign test over recording medians, labelled
  underpowered.

## Per cell, report

- spike count, mean rate, CV²;
- Σ² slope over L 4–12, real and under 50 ISI shuffles (z = (real − shuffled mean) / shuffled sd);
- CV²(1 + 2Σρ_k) for K ∈ {1, 3, 10, 30};
- clusters/burst at 5/10/20/50 ms against a homogeneous rate-matched Poisson 99 % band, and against a
  W = 1 s local-rate band.

The capability report puts ~60 % of ret-1 cells at individually Poisson-indistinguishable long-range
variance: renewal-like cells (CV² ≈ slope) give z ≈ 0 whatever the truth, so per-cell fractions are
reported, never barred. **The claim is about population medians; the bars are there.**

## Predictions (sealed on the amended sets)

- **P1a (instrument check):** median shuffled slope / median CV² ∈ [0.8, 1.2].
- **P1:** median shuffled slope − median real slope > 5 bootstrap SE, in PRIMARY **and** in TIER-2.
  Reported without a bar: the per-cell z distribution and the fraction of cells with real < shuffled.
- **P2:** median |CV²(1 + 2Σρ_{k≤10}) − real slope| / real slope ≤ 0.3. Report the full K curve;
  truncation is a nuisance parameter.
- **P3 at 20 and 50 ms:** median of (observed − homogeneous band-hi) > 0, by > 5 bootstrap SE.
- **P3 at 5 ms:** median of (observed − band mean) ≤ 0, reported with its SE.
- **P3 per-cell fractions:** reported without a bar.

## Rival (stated in the seal; covers P3)

P1–P3 pass equally for stimulus-locked firing events, intrinsic bursting / spike-frequency adaptation,
and fast rate modulation. A pass licenses **NON_RENEWAL_SERIAL_CORRELATION**, not a mechanism;
**RET1_CLUSTERS_EXCEED_POISSON licenses "excess short-interval clustering", not "bursts."** Separating
mechanisms needs stimulus-repeat structure and is out of scope here.

## Tokens

- `RET1_RIGIDITY_IS_SERIAL_ORDER` or `RET1_RIGIDITY_SURVIVES_SHUFFLE`
- `RET1_CLUSTERS_EXCEED_POISSON` or `RET1_CLUSTERS_AT_POISSON`

## Ledger — UNREGENERABLE (demodulation arc)

The July ret-1 values in `DEMODULATION_FINDINGS.md` have **no committed generator** (`demod.log` and
`demod2.log` entered the repo alone in 975997c; the producing script never did): **CV² 2.14, Σ² slope
0.44–0.78, R₂(0.1) ≈ 2.5, clusters/burst 1.01 / 1.24 / 1.78 / 2.72**, and the "25 cells ≥ 6k / 11 ≥ 18k"
subsample. Same class as the matrix's unattributed +0.388 (`OVERNIGHT_2026_07_29.md`,
`CAPABILITY_REPORT.md:262`). **This run's results supersede them; they are never compared against as
measurements.** The July demodulation retentions (the W-curves, Part A's subject) are in the same class
unless the Part A gate below reproduces them.

## Instrument

- `realdata_checks.py` **as delivered by Will** (shuffle test, Cox–Lewis curve, clusters against
  rate-matched nulls; each self-tested against a planted effect and a null). **Not yet received
  (2026-09-21: the message that said "attached below" carried these amendments, no Python) → STOP.**
- `--selftest` must pass in this environment before any ret-1 file is read.
- Known nit: `clusters_vs_null` draws surrogates matching the *expected* count, not the exact count
  (~1/√n, negligible). Changing it to condition on the exact count is allowed as a declared change,
  followed by a self-test re-run.

## Part A — a separate small cell (not this seal; drafted here so it is not lost)

- **Subject:** `DEMODULATION_FINDINGS.md`'s INTRINSIC/EXTRINSIC labels. The prior look showed a stand-in
  demodulator cannot tell slow-intrinsic from slow-extrinsic; the label tracks timescale relative to W.
- **Instrument:** the July demodulator has no committed generator and neither of us has the script.
  Part A therefore **declares a re-implementation** built from the findings' description (rate estimate
  at bandwidth W, time-rescale, kernel to be declared), then **gates it**: it must reproduce the file's
  **gamma CV=2 constant-rate** calibrator retentions (72 % / 94 % / 101 % at W = 1 / 5 / 100 s) within a
  declared tolerance before touching the new calibrators. The file's **Cox** calibrator has no stated
  modulation timescale, so it cannot gate; the re-implementation's Cox is declared and reported.
  **If the gate fails, the July demodulation numbers join the unregenerable ledger — itself a finding.**
- **Statistic:** the findings' own — `I_rep` = signed ∫₀¹(1 − R₂) dr (`run_overnight.py:irep_unclipped`,
  committed) — tested as `I_demod` against a **demodulated-Poisson null** (the findings' own replacement
  for the ill-conditioned retained %), **not the toy's mass03**.
- **New calibrators:** fast Cox (stimulus-locked 6.25 Hz) and slow intrinsic cycle, at the findings' W
  values {0.05, 0.2, 1, 5, 20, 100} s.
- **Outcome:** keep the mechanism labels where the four calibrators discriminate; otherwise rename them
  **SLOWER_THAN_W / FASTER_THAN_W**.

On any ambiguity about files, cells, or the instrument: STOP.

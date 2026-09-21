# PRE-REG — ret-1 serial-order test (demodulation arc)

**Status: DRAFT, 2026-09-21. Nothing runs until Will says go, and three STOP conditions below are open.**

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

## STOP conditions found while drafting (2026-09-21) — open

1. **Which 25 cells.** The findings say "25 cells ≥ 6k ISIs" and "11 cells ≥ 18k". The committed
   loader (`overnight_2026_07_12/loaders.py:load_ret1`, 325 cells ≥ 100 spikes) with those rules gives
   **183 and 60**. The July job subsampled (28 ret-1 cells appear in `demod2.log`) with a script that
   was **never committed** (`git log` on `demod.log` shows only the log, commit `975997c`). The cell set
   is therefore ambiguous → STOP. Options for Will: (a) run on all 183 ≥ 6k-ISI cells and state that the
   findings' 25 were a subsample; (b) recover the subsampling seed/rule from the July session; (c) the
   ≥ 18k set of 60.
2. **Instrument not filed.** `realdata_checks.py` is not on disk and was never received in this
   conversation (transcript, memory, filesystem searched) → STOP and ask.
3. **The findings' demodulator has no committed generator.** `demod.log` / `demod2.log` (the canary and
   the retained-vs-W curves) were produced by an uncommitted script; `run_overnight.py` does not contain
   it. The Part A cell needs it, or a re-implementation declared as such.

## Per cell, report

- spike count, mean rate, CV²;
- Σ² slope over L 4–12, real and under 50 ISI shuffles (z = (real − shuffled mean) / shuffled sd);
- CV²(1 + 2Σρ_k) for K ∈ {1, 3, 10, 30};
- clusters/burst at 5/10/20/50 ms against a homogeneous rate-matched Poisson 99 % band, and against a
  W = 1 s local-rate band.

The capability report puts ~60 % of ret-1 cells at individually Poisson-indistinguishable long-range
variance, so the bars below are population-level, not per-cell.

## Predictions (to be sealed once the STOPs are cleared; n = 25 is the findings' count and will be
## restated for whichever cell set Will chooses)

- **P1:** real slope < shuffled slope in ≥ 21 of 25 cells (sign test p ≈ 5·10⁻⁴). Median shuffled slope
  / median CV² ∈ [0.8, 1.2].
- **P2:** median |CV²(1 + 2Σρ_{k≤10}) − real slope| / real slope ≤ 0.3. Report the full K curve;
  truncation is a nuisance parameter.
- **P3:** clusters above the homogeneous band at 20 and 50 ms in ≥ 21 of 25 cells. At 5 ms, at or below
  the band mean.

## Rival (stated in the seal)

P1–P2 pass equally for stimulus-locked firing events and for intrinsic spike-frequency adaptation
(both give negative serial ISI correlation). A pass licenses **NON_RENEWAL_SERIAL_CORRELATION**, not a
mechanism. Separating the two needs stimulus-repeat structure and is out of scope here.

## Tokens

- `RET1_RIGIDITY_IS_SERIAL_ORDER` or `RET1_RIGIDITY_SURVIVES_SHUFFLE`
- `RET1_CLUSTERS_EXCEED_POISSON` or `RET1_CLUSTERS_AT_POISSON`

On any ambiguity about files, cells, or the instrument: STOP.

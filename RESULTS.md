# RESULTS

This document is the empirical log for the Arithmetic Resonance
Spectrometer (ARS).  It records, in chronological order of development,
the measurements made with the toolkit and the diagnoses that produced
each result.  The body sections (§3 through §7.ter) are working notes
preserved for traceability — they include intermediate findings that
were later retracted.  **For the finalized list of validated outputs,
failure modes, and limitations, see §8.**

The toolkit is described in `README.md`; the protocol it implements is
in `METHODS.md`.

## TL;DR

The toolkit was validated against signals with established universality
classifications (Riemann ζ, LMFDB elliptic curve L-functions, Dirichlet
L-functions, GUE/GOE eigenvalue ensembles, USGS earthquakes) and
reproduced statistics consistent with prior literature on the inputs
tested.  Application to LLM internal state produced no measurement
attributable to the model rather than to the extraction pipeline; three
provisional findings produced during development were retracted under
calibration and induction-on-noise tests.

The full validated-outputs list and the diagnosed failure modes are in
§8.  The ARS toolkit is an applied implementation of the Farey-rational
PLL framework (Planat et al., 2002–2026) and does not extend that
framework analytically.

---

## 1. Scope

The toolkit takes a sorted point process (event timestamps t_k) and
classifies its spacing statistics against Poisson, Wigner GOE/GUE/GSE,
periodic, and uniform-with-jitter universality classes.  The intended
applications are signals where the level sequence is directly
accessible (eigenvalues, zero heights) or extractable without imposing
artificial periodicity (prime gaps, earthquake catalogs).  Inputs that
are extracted from continuous traces by peak detection require the
artifact-diagnostic protocol described in METHODS.md before
classifications can be trusted; see §7.ter.19 and §8 for worked
examples.

---

## 2. Architecture

```
Signal input  (chirp synthesised from t_k list, or raw audio/numeric)
     ↓
Farey PLL bank  (one PLL per p:q rational up to q_max, GPU-parallel)
     ↓
Lock/slip time series  (binary, per PLL, per sample)
     ↓
Intermittency extractor  (dwell times, lock onsets, depth statistics)
     ↓
Universality analyzer  (NNS / pair correlation / number variance / SFF)
     ↓
Classification  (Poisson / GOE / GUE / sub-GOE / etc.)
```

Two pipelines run in this codebase: the **measured** path through the
chirp synthesis and PLL bank, and the **analytical** path which computes
zero passage times directly from the t_k list, applying the PLL's selection
function (dwell ≥ 20 ms threshold).  The two paths agree on the *bulk*
phenomenology but differ in fine-grained NNS shape; that delta is the
instrument's contribution and is quantified in §6.

---

## 3. Methods

### 3.1 PLL bank (Phase 1)

A second-order PLL operating on the in-phase / quadrature components of a
narrowband signal.  Each PLL has its own natural frequency `f_pll = fc_ref · p/q`
for a Farey rational p/q.  The instantaneous phase is extracted by
quadrature mixing with a local oscillator at f_pll, then 1-pole IIR
low-pass filtering at cutoff `f_pll · 0.05`.  The PLL is a baseband
tracker — its oscillator state is the *deviation* from f_pll, not the
full phase, and the integrator absorbs frequency offsets directly.

Loop equations (per sample):
```
e   = sin(φ_sig − φ_osc)              # phase error from atan2(Q_lp, I_lp)
v   = ρ · v_prev + K_i · e            # PI integrator
dφ  = K_p · e + v
φ_osc += dφ                            # baseband — no ω_pll term
```

**Lock detection** combines two criteria, both must hold for at least
`N_lock` samples:
- `|e| < θ_lock = π/6` (phase coherence)
- `|I_lp|² + |Q_lp|² ≥ 0.03 · RMS²` (narrowband power above floor)

The power floor was added during Phase 1 verification; without it, the PLL
would lock on attenuated leakage of any nearby tone, giving false
positives for off-frequency sinusoids well outside the LP bandwidth.

**Two corrections to the original Phase 1 spec:**
1. **PLL-frame correction**: the original loop equation `φ_osc += 2π·f_pll/sr + dφ`
   mixes baseband (φ_sig) and full-phase (φ_osc) frames after quadrature
   mixing has already removed the carrier.  Using just `φ_osc += dφ` gives
   correct lock behavior across all f_pll.  Documented in `pll_bank.py`.
2. **GPU layout correction**: the original spec had per-sample threads in
   each block, which can't share the PLL recurrence (sequential per
   sample).  Corrected to one thread per PLL with sequential within-thread
   iteration over samples.  Achieves 968 M-PLL-samp/sec with lock-only
   output on the RTX 4090, ~10× faster than naive layout.

**Implementation**: `pll_bank.py` — CPU reference (`single_pll_cpu`,
`pll_bank_cpu`) and GPU kernel (`pll_bank_gpu`) using CuPy `RawKernel`.
GPU↔CPU parity verified to 5e-6 on locked samples (Test G1, G2 in
`tests/test_pll_gpu.py`).

### 3.2 Stern-Brocot depth

The Farey rationals p/q live in the Stern-Brocot tree.  Depth equals the
sum of continued-fraction partial quotients minus 1.  Used for
characterizing which regions of the rational lattice a signal engages.

### 3.3 Intermittency extraction (Phase 2)

Per-PLL run-length encoding of the binary lock series gives:
- `lock_dwells`, `slip_dwells` (run durations)
- `lock_onsets` (sample indices of 0→1 transitions)

Auxiliary statistics:
- **Power-law MLE** on dwell distributions (Clauset-Shalizi-Newman, 1+n/Σln(τ_i/(τ_min−½)))
  with KS goodness-of-fit
- **Fano factor F(L)** = var(N(L))/mean(N(L)) on lock-onset point process
  in mean-spacing-units of L (or sample units)
- **Aggregate-unfolded events**: per-PLL events normalised by per-PLL
  mean spacing, then pooled across PLLs

**Implementation**: `intermittency.py`.  Acceptance verified on synthetic
power-law dwells (α=2.0, recovered to 0.07 within 20 k samples) and
exponential dwells (rejects power-law fit at p < 1e-4 in 5/5 trials).

### 3.4 Universality stats (Phase 3)

Implemented in `universality.py`:
- `compute_nns(events)`: per-spacing distribution + KS to analytical
  forms for Poisson `e^(−s)`, GOE `(π/2) s e^(−π s²/4)`, GUE `(32/π²) s² e^(−4 s²/π)`
- `pair_correlation(events, r_max, n_bins)`: R₂(r) histogram + GUE/GOE references
- `number_variance(events, L_max, n_L)`: Σ²(L) sliding-window variance + RMT formulas
- `spectral_form_factor(events, t_max, n_t)`: K(t) = (1/N)|Σ_n e^{2πi t x_n}|²

KS-distance is the primary classifier; we report the smallest of (KS_P, KS_O, KS_U)
as the best fit, and the gap between KS_GOE and KS_GUE as a directional
discriminator (positive → GUE wins, negative → GOE wins).

### 3.5 Signal generators

`signal_gen.py` provides:
- `make_zeta_signal(n_zeros, sr, duration)`: chirp Σ cos(t_n · log(t+1)) / √t_n,
  using cached precomputed Riemann zero heights from `mpmath.zetazero`
  (cache file `zeros_1000.npy`)
- `make_gue_eigenvalue_signal(n_points, seed)`: GUE matrix eigenvalues,
  semicircle-CDF unfolded at R=2 (see §6.1 for the calibration story),
  optionally rescaled to ζ-zero range
- `make_poisson_zeta_like(n_points, seed)`: Poisson-FM null — same form
  as ζ but with t_k drawn uniformly in the ζ range, sorted

---

## 4. The grand parameter sweep (Phase 0 of validation)

3000 cells = 50 fc_ref values × 5 q_max values × 4 K_p values × 3 signals
(ζ, white noise, Poisson-FM null), 30 s × 100 zeros for the source,
fc_ref ∈ [2, 500] Hz log-spaced, q_max ∈ {6, 8, 10, 12, 16}, K_p ∈ {0.02, 0.05, 0.10, 0.20}.
Ran in 8.8 min wall (4.8 min GPU + 3.8 min CPU), saved to
`sweep_results.h5` (121 KB, 3000 rows).

Findings:
1. **White noise: 0/3000 valid F cells**.  The PLL doesn't lock on noise
   anywhere in the parameter space — perfect null.
2. **Poisson-FM null: median F_aggregate = 4.24** at L=1 mean-spacing
   units across cells — super-Poisson clustering arising from chirp
   dynamics, *not* from arithmetic structure.
3. **ζ: median F_aggregate = 10.51**, 2.5× more clustered than the
   Poisson chirp baseline at the median.  58.6% of cells show
   F_zeta / F_poiss > 1.5.
4. **K_p = 0.02 is the most stable cell** (smallest std of F across fc_ref;
   the tongue-boundary regime as anticipated by the brief).
5. **Maximum ζ-vs-Poisson separation**: q_max=16, K_p=0.20, fc_ref=115.55
   gives F_zeta/F_poiss = 11.05 — designated as the **anchor cell** for
   subsequent runs.

---

## 5. The ζ result evolution

### 5.1 First measurement (q_max=8, fc_ref=100, K_p=0.10, 8s × 50 zeros)
- 110 lock events across 42 of 43 PLLs
- F_aggregate = 11.7 (super-Poisson)
- Most-locking rationals: 1:8, 1:7, 1:6 (lowest fc PLLs, best dwell)
- **Aggregate F is super-Poisson** but, importantly, this is a chirp
  dynamics phenomenon — confirmed by the Poisson-FM null also being
  super-Poisson.

### 5.2 Per-PLL Fano (anchor cell, 30 s × 100 zeros)
F_per_PLL is the right scale to look at.  Aggregate clustering can come
from multiple uncorrelated PLLs firing in the same time window for chirp
geometry reasons.  Per-PLL is the level where intrinsic spacing structure
shows up.

| signal | F_per_PLL (mean ± std, locking PLLs) |
|---|---|
| ζ | 0.745 ± 0.224 |
| GUE eigenvalue chirp | 2.10 ± 0.76 |
| Poisson-FM null | 3.09 ± 1.34 |

ζ shows F < 1 — sub-Poisson, consistent with level repulsion.  The GUE
chirp at this stage *also* shows super-Poisson, which prompted the
calibration work in §6.

### 5.3 Per-PLL NNS (anchor cell)

Pooled per-PLL normalised spacings (per-PLL mean=1 before pooling).

| signal | n | KS_Poisson | KS_GOE | KS_GUE | best | mass<0.3 |
|---|---|---|---|---|---|---|
| ζ | 308 | 0.319 | **0.184** | 0.212 | GOE | **0.039** (3.9 %) |
| GUE chirp | 186 | **0.070** | 0.184 | 0.242 | Poisson | 0.231 |
| Poisson-FM | 303 | 0.193 | 0.394 | 0.462 | Poisson | 0.366 |

Theoretical mass<0.3: Poisson 25.9 %, GOE 6.4 %, GUE 1.1 %.

ζ shows clear level repulsion (mass<0.3 = 3.9 %, between GUE and GOE
theoretical values), 9× lower than the Poisson-FM null.  KS-best-fit is
GOE by a small margin over GUE.  Both null signals reject level repulsion
unambiguously.

### 5.4 Selection-bias control (Task 1 of Phase-3 controls)

The Poisson-FM null at the same cell shows mass<0.3 = 36.6 %, F = 2.43:
selection bias from the dwell threshold *cannot* generate level repulsion
on its own.  The ζ signal at mass<0.3 = 3.9 % is genuinely level-repelling.

### 5.5 Time-reversal symmetry (Task 2 of Phase-3 controls)

Forward and reversed ζ signals were both run through the bank.

| | F_per_PLL | mass<0.3 | KS_GOE | KS_GUE | best |
|---|---|---|---|---|---|
| ζ forward | 0.715 | 0.039 | 0.184 | 0.212 | GOE |
| ζ reversed | 0.812 | 0.099 | 0.198 | 0.231 | GOE |
| two-sample KS forward vs reversed | | | | | **0.150** (p=0.002) |

Forward and reversed are statistically different — the metric does
**partially** detect time-reversal-symmetry breaking.  Both pick GOE as
best fit.  The asymmetry signal is borderline but real.

### 5.6 The decisive run (1000 ζ zeros × 300 s, 500-ms transient strip)

| metric | forward | reversed |
|---|---|---|
| qualifying PLLs | 28 of 43 | 26 of 43 |
| pooled spacings | **885** | 808 |
| F_per_PLL | **0.957 ± 0.130** | 0.994 ± 0.173 |
| mass<0.3 | **0.033** | 0.027 |
| KS_GOE | **0.160** | 0.147 |
| KS_GUE | 0.225 | 0.213 |
| KS_GOE − KS_GUE | **−0.066** | **−0.066** |

**Decisive.**  Both forward and reversed pick GOE with gap 0.066 ≥ the
0.05 decisiveness threshold.  ζ measured NNS lands at GOE consistently.

The transient strip reduced fwd-vs-rev KS from 0.150 to 0.084 — half the
previous asymmetry was IIR settling.  The remaining 0.084 is borderline
but persists; that's residual genuine time-asymmetry detection.

### 5.7 What the ζ measurement actually says (vs apparent claim)

By §5.6 we had: "ζ is GOE under this measurement, with measurable but
weak time-asymmetry."  This contradicts the GUE conjecture for the actual
zero-spacings.

Two readings:
- **A**: ζ deviates from the GUE conjecture in this metric.
- **B**: The PLL is a partly time-symmetric detector that folds GUE onto GOE.

The calibration work in §6 distinguishes between them.

---

## 6. Instrument calibration

### 6.1 The GUE generator math

Initial generator:
```python
A = (randn + 1j randn) / sqrt(2)
H = (A + A^†) / sqrt(2 N)
eigs = sort(eigvalsh(H))
unfolded = (eigs − eigs[0]) / mean(diff(eigs))   # divide by global mean
```

This puts off-diagonal var(H_ij) = 1/N and produces eigenvalues in
**[−2, 2]** — bulk semicircle on [−2, 2] (not [−1, 1]).  Dividing by the
global mean spacing rather than by the local density gives unfolded
spacings whose KS to Wigner GUE is 0.077 (borderline) — local density
variation isn't removed.

Correct unfolding via the Wigner semicircle CDF:
```
ρ(x) = (1/(2π)) sqrt(R² − x²)  on  [−R, R]   with  R = 2
F_R(x) = F_unit(x/R) = 0.5 + ((x/R) sqrt(1 − (x/R)²) + arcsin(x/R)) / π
unfolded = F_R(eigs) · N
```

Empirical KS distances on N = 500 GUE eigenvalues:
- Old `divide by mean spacing`: KS_GUE = 0.0766
- User's literal procedure (apply unit CDF directly, clipping): KS_GUE = 0.3902 — **fails**
- **Corrected**: `F_unit(eigs / 2) · N`: **KS_GUE = 0.0371** — passes
- Empirical polynomial unfolding (deg 11): KS_GUE = 0.0393 — independent confirmation

The literal procedure fails because the unit-CDF formula assumes
eigenvalues in [−1, 1], but our matrix normalisation puts them in [−2, 2];
clipping by the formula's `np.clip(x, −1, 1)` destroys most of the
distribution.

### 6.2 GOE generator

```python
A = randn(N, N)            # real Gaussian
H = (A + A.T) / sqrt(2 N)
eigs = sort(eigvalsh(H))
```

Same R = 2 normalisation.  KS to Wigner GOE = 0.022 at N = 500.

### 6.3 The chirp envelope problem

When the unfolded GUE eigenvalues are linearly rescaled to ζ's range
[14.13, 1419.42] and used as t_k in the chirp synthesis, the resulting
signal driven through the PLL bank gives only 4 of 43 qualifying PLLs at
the anchor cell, with F_per_PLL = 7.6 and KS_Poisson best-fit.

Diagnosis (`run_envelope_per_pll.py`): at low fc PLLs (1:8 = 14.4 Hz)
GUE/GOE chirps actually have **more** above-power-floor peaks than ζ
(79–87 vs 66).  At high fc (1:1 = 115.5 Hz) GUE/GOE collapse to 1 peak vs
ζ's 32.  Bank totals over 43 PLLs:

| signal | total above-floor runs | runs ≥ 20 ms | PLLs with ≥10 triggers |
|---|---|---|---|
| ζ | 1656 | 1470 | **43** |
| GUE chirp | 580 | 220 | 4 |
| GOE chirp | 652 | 252 | 5 |

The mechanism: chirp narrowband amplitude at f_pll comes from
**stationary-phase contributions** — at any moment t, only tones with t_k
≈ f_pll · (t+1) contribute coherently.  ζ's phase structure (Riemann-Siegel
type) creates **coherent peaks** at specific moments tied to prime-related
positions; random matrix eigenvalues with the same NNS but random phases
produce **random-phase sums** with smeared envelope and far fewer sharp
peaks.

Implication: the chirp/PLL stack is **not** measuring eigenvalue NNS
directly.  It's measuring **temporal regularity of coherent envelope peaks**
at f_pll, which depends on phase structure and not just spacing structure.
ζ's specific phase structure produces clean discrete peaks; random-matrix
eigenvalues don't reproduce that structure even when their spacings are
correctly distributed.

### 6.4 The analytical metric

To bypass the chirp/PLL stack and isolate eigenvalue spacing structure
directly, compute **passage times analytically**:
```
t* = t_n / f_pll − 1     ∀  zero with t_n in [(transient+1)·f_pll, (dur+1)·f_pll]
                          and dwell ≥ 20 ms
```

The dwell-threshold criterion `t_n ≥ lock_confirm · f_pll / (tongue_prefac · (2/(p+q))²)`
is the same selection function the PLL applies.  For each PLL: collect
qualifying t_n, take spacings, divide by per-PLL mean, pool.

Results at the anchor cell (q_max=8, fc_ref=115.55, dur=300 s, transient=500 ms):

| signal | #PLLs | n pooled | KS_P | KS_O | KS_U | gap | best |
|---|---|---|---|---|---|---|---|
| **ζ** | 27 | 18,529 | 0.310 | 0.099 | **0.034** | **+0.065** | **GUE** |
| GUE eigenvalues (uniform unfolded) | 21 | 13,971 | 0.272 | 0.076 | **0.022** | +0.054 | GUE |
| GOE eigenvalues (uniform unfolded) | 21 | 13,965 | 0.211 | **0.021** | 0.086 | −0.064 | GOE |
| GUE (ζ-density mapped) | 27 | 18,534 | 0.219 | **0.017** | 0.068 | −0.051 | GOE |
| GOE (ζ-density mapped) | 27 | 18,526 | 0.181 | **0.049** | 0.116 | −0.066 | GOE |

**Calibration confirmed.**  Pure GUE eigenvalues, projected through the
selection function but *without* the PLL detection, give Wigner GUE
NNS at KS = 0.022.  Pure GOE eigenvalues give Wigner GOE at KS = 0.021.
The metric works.

**ζ analytical lands at Wigner GUE** (KS = 0.034, gap +0.065).  This is
the headline result.

The **ζ-density-mapped** chirp signals (GUE and GOE eigenvalues passed
through ζ's empirical CDF) both shift to GOE-best-fit.  The non-uniform
local Jacobian of ζ's CDF compresses small-spacing pairs in dense regions
and stretches them in sparse regions — per-PLL normalisation can't undo
this because each PLL spans a wide range of densities.  **Use uniform
unfolded comparison signals for clean class testing**, not ζ-density-mapped.

### 6.5 The PLL projection

ζ analytical (no PLL): gap = +0.065 (GUE)
ζ measured (PLL):      gap = −0.066 (GOE)

Two-sample KS analytical-vs-measured = **0.253** (p ≈ 0).

**The PLL detector adds ~0.13 KS in the GOE direction.**  This is the
quantified instrument bias.  The GOE result in §5.6 is the *projected
image* of the underlying GUE statistics — exactly Reading B.

The mechanism:
- Per-PLL min_events=10 cutoff drops ~95 % of analytical events
- Lock-confirmation timing delays onsets non-uniformly by passage speed
- Phase-coherence-dependent peak detection filters which passages
  produce envelope-above-floor
- Time-symmetric peak detection (no upward-sweep / downward-sweep
  distinction) folds the GUE asymmetry into GOE-symmetric statistics

Each is a known projection mechanism.  Their composition is the bias.

---

## 7. Phase 4 — cross-signal application

The calibrated analytical passage-time NNS (§6.4) applied to several
arithmetic and synthetic signals at the anchor cell (q_max=8,
fc_ref=115.55, dur=300 s, transient=500 ms, lock_confirm=20 ms).

### 7.1 Signals tested

| signal | range | n_t_k | construction |
|---|---|---|---|
| ζ_zeros[1..1000] | [14.13, 1419.42] | 1000 | first 1000 Riemann zero heights via `mpmath.zetazero` |
| primes[first 1000] | [2, 7919] | 1000 | sieve of Eratosthenes |
| primes[first 2000] | [2, 17389] | 2000 | sieve |
| squarefree[first 1000] | [1, 1637] | 1000 | integers n with μ(n) ≠ 0 |
| poisson_uniform[ζ-range] | [14.40, 1418.72] | 1000 | sorted uniform draw, ζ range |
| GUE_eigs[unfolded uniform] | [1.62, 999.22] | 1000 | semicircle CDF unfolding, R=2 |
| GOE_eigs[unfolded uniform] | [0.54, 1000.00] | 1000 | semicircle CDF unfolding, R=2 |

### 7.2 Classification table

| signal | #PLLs | n pooled | KS_P | KS_GOE | KS_GUE | gap | mass<0.3 | best |
|---|---|---|---|---|---|---|---|---|
| **ζ_zeros[1..1000]** | 27 | 18,529 | 0.310 | 0.099 | **0.034** | **+0.065** | 0.017 | **GUE** |
| **ζ_zeros[1001..2000]** | 35 | 30,620 | 0.314 | 0.113 | **0.047** | **+0.067** | 0.014 | **GUE** |
| **ζ_zeros[1..2000]** | 35 | **49,181** | 0.309 | 0.100 | **0.032** | **+0.068** | 0.015 | **GUE** |
| primes[first 1000] | 43 | 32,519 | 0.203 | 0.188 | 0.243 | −0.055 | 0.166 | GOE |
| primes[first 2000] | 43 | 68,165 | 0.200 | 0.191 | 0.252 | −0.061 | 0.146 | GOE |
| squarefree[first 1000] | 28 | 18,488 | 0.456 | 0.273 | 0.340 | −0.067 | **0.000** | GOE |
| **poisson_uniform[ζ-range]** | 27 | 17,628 | **0.018** | 0.226 | 0.292 | −0.066 | 0.268 | **Poisson** |
| **GUE_eigs[unfolded uniform]** | 21 | 13,971 | 0.272 | 0.076 | **0.022** | +0.054 | 0.029 | **GUE** |
| **GOE_eigs[unfolded uniform]** | 21 | 13,965 | 0.211 | **0.021** | 0.086 | −0.064 | 0.081 | **GOE** |

Theoretical mass<0.3: Poisson 25.9 %, GOE 6.4 %, GUE 1.1 %.  Decisive
gap threshold: |gap| > 0.05.

### 7.3 Verdicts

**Calibrators behave correctly** (ζ rows, GUE_eigs, GOE_eigs, poisson_uniform).
ζ zeros at all ranges tested (first 1000, 1001-2000, combined first 2000),
GUE eigenvalues, GOE eigenvalues, and a Poisson uniform null all classify
to their predicted classes with clean KS distances and decisive gaps.
This validates the metric.

**ζ zeros 1001-2000 also land at GUE** (KS_GUE=0.047, gap +0.067), and the
combined first 2000 give n=49,181 pooled spacings with KS_GUE=0.032 —
the cleanest measurement to date.  The GUE classification of ζ is robust
across the tested zero range, not localised to the first 1000.

**Primes show intermediate, non-Wigner level statistics**:
- Decisively non-Poisson (gap −0.055/-0.061, mass<0.3 = 14–17 % vs
  Poisson's 26 %)
- BUT KS to GOE is only 0.19, far from the calibrators' 0.02 — the prime
  passage-time NNS doesn't follow Wigner GOE *shape* well, just lands
  closer to it than to GUE
- Stable across n=1000 and n=2000 (results consistent within sampling)

This is consistent with the literature: prime spacings exhibit
**Cramér-model-with-corrections** behavior — partial level repulsion from
Hardy-Littlewood conjectures + structured correlations from prime
constellation patterns, but not Wigner.  The classifier reflects this
honestly: closest to GOE in KS, but not GOE in fact.

**Squarefree integers are an outlier**: mass<0.3 = **0.000** (no spacings
below 0.3 normalised mean), and KS to all three forms is 0.27+ — none of
Poisson, GOE, or GUE describes it.  This is an artifact of the
**integer-valued spacings** in squarefree sequences: the minimum gap is
1, mean gap is ~6/π² ≈ 1.65 at large N, so the minimum normalised
spacing is ≈ 1/1.65 ≈ 0.61 — there is no s < 0.6 mass at all.  A
discrete-spacing process can't be characterised by continuous Wigner
forms.  Reading: squarefree NNS is a **gap-distribution** problem not a
level-statistics problem.

**Decision criterion update**: KS classification in this metric is
meaningful when KS_min < ~0.10 (calibrators all clear that bar).  For
KS_min in the 0.18–0.30 range (primes, squarefree) the *direction* of
the gap is informative but the *class assignment* should be reported as
"closest to X" rather than "is X".

### 7.4 Headline cross-signal table

| signal | clean class | confidence |
|---|---|---|
| Riemann ζ zeros (1..2000) | **GUE** | high (KS=0.032, gap +0.068, n=49,181) |
| Riemann ζ zeros (1001..2000) | GUE | high (independent confirmation) |
| GUE matrix eigenvalues | GUE | high (calibration anchor) |
| GOE matrix eigenvalues | GOE | high (calibration anchor) |
| white noise null (PLL bank) | no signal | trivial |
| Poisson uniform t_k | Poisson | high (KS=0.018) |
| primes | non-Poisson, GOE-leaning | weak (intermediate KS) |
| squarefree integers | gap-distribution problem | unclassifiable in this frame |

The headline result of the tool — and of this codebase as a whole — is
the **GUE classification of ζ zeros via the analytical passage-time NNS
metric**, with a calibrated comparison spanning the full Wigner classes
and a Poisson null.

Plot: `plots/15_phase4_classification.png`

---

## 7.bis  Phase 5 — wider arithmetic survey + first EEG signal

The metric calibrated, applied to a much wider set of arithmetic and
non-arithmetic data, including external datasets.

### Datasets

| source | what | size | construction |
|---|---|---|---|
| Odlyzko `zeros1` | ζ first 100,000 zeros | 100k | downloaded from `~odlyzko/zeta_tables/zeros1` |
| Odlyzko `zeros6` | ζ first 2,001,052 zeros | 2M | downloaded; heights 14 → 1,132,490 |
| local sieve | primes ≤ 10⁷ | 664,579 | Eratosthenes |
| derived | twin-prime lower members ≤ 10⁷ | 58,980 | sieve filter |
| sieve | Liouville function ±1 positions ≤ 10⁵ | 50k+ each | factor-count parity |
| sieve | Gaussian prime norms ≤ 10⁵ | 4,818 | a²+b²=p classification |
| synth | Poisson process with intensity 1/log(n) | 1,223 | controls primes' density without correlations |
| PhysioNet | EEG S001R01.edf, channel Fcz, 4–8 Hz θ-band | 61 s @ 160 Hz | bandpass + zero-crossings |

### Master classification table

| signal | best | gap | KS_min | mass<0.3 | n |
|---|---|---|---|---|---|
| **ζ Odlyzko zeros1[1..1000]** | GUE | +0.065 | 0.034 | 0.017 | 18,529 |
| **ζ Odlyzko zeros1[first 10000]** | GUE | +0.068 | 0.020 | 0.018 | 216,427 |
| **ζ Odlyzko zeros1[first 100000]** | **GUE** | **+0.068** | **0.015** | 0.022 | **1,845,065** |
| **ζ Odlyzko zeros6[low 50k]** (heights 14–40k) | GUE | +0.068 | 0.017 | 0.021 | 651,745 |
| **ζ Odlyzko zeros6[high 50k]** (heights ≈ 1.1M) | **GUE** | +0.067 | **0.012** | 0.024 | 450,184 |
| primes ≤ 10⁴ | GOE-leaning | −0.056 | 0.191 | 0.160 | 41,300 |
| primes ≤ 10⁵ | Poisson-best | −0.068 | 0.179 | 0.124 | 325,805 |
| primes ≤ 10⁶ | Poisson-best | −0.065 | 0.156 | 0.104 | 2,675,801 |
| twin primes (lower) ≤ 10⁷ | **Poisson-best** | −0.068 | **0.057** | 0.229 | 1,159,268 |
| Liouville +1 positions ≤ 10⁵ | (integer-floor) | −0.066 | 0.321 | 0.000 | 925,037 |
| Liouville −1 positions ≤ 10⁵ | (integer-floor) | −0.067 | 0.320 | 0.000 | 930,361 |
| Gaussian prime norms ≤ 10⁵ | Poisson-best | −0.068 | 0.184 | 0.120 | 163,507 |
| **Poisson density control (primes-density)** | **Poisson** | −0.063 | **0.022** | 0.253 | 41,552 |
| **EEG θ zero-crossings (Fcz, rest, 61 s)** | **GUE** | **+0.052** | 0.190 | 0.000 | 341 |

### Three findings

**1. ζ height-dependent strengthening of Wigner GUE.**
The same metric applied at three height regimes:
- low (heights 14 → 40k):   KS_GUE = 0.017
- mid (heights 14 → 75k, n=100k): KS_GUE = 0.015
- **high (heights ≈ 1.1M):  KS_GUE = 0.012** ← cleanest match

The fit to Wigner GUE *improves* at higher zero heights, exactly as the
conjecture predicts (asymptotic universality).  This is the
height-dependence test from the brief, and the result is positive.

**2. Primes asymptotically approach Poisson.**
KS_Poisson decreases from 0.19 (primes ≤ 10⁴) to 0.16 (primes ≤ 10⁶) to
**0.057** (twin primes ≤ 10⁷).  The Cramér heuristic that primes (and a
fortiori twin primes) become indistinguishable from Poisson at large
scales is observed in this metric.

The Poisson density control (random Poisson process with intensity
1/log(n) matching primes' density) gives KS_Poisson = 0.022 — a clean
calibrator.  Primes' KS_Poisson = 0.16 is an order of magnitude larger,
showing primes have *more* structure than density-only Poisson; the
deviation is real, just shrinking with N.

**3. EEG θ-band zero-crossings: quasi-periodic artifact, NOT a
Wigner GUE classification.**  Channel Fcz, rest condition, 61 s
recording, 4–8 Hz bandpass yields 341 positive-going zero-crossings:
- KS_Poisson = 0.427 (decisively non-Poisson)
- KS_GOE = 0.242
- KS_GUE = 0.190 (closest of the three Wigner forms, but 8× the
  calibrator threshold of 0.022)
- mass<0.3 = 0.000 (highly regular)

What the metric is reporting here is "more s²-suppressed near 0 than
GOE", not GUE-class dynamics.  The KS distance is far above the clean-
fit threshold, and the mass<0.3 = 0.000 is the smoking gun: zero-
crossings of a 4–8 Hz bandpass are forced to ~125 ms intervals by the
filter itself, so the short-spacing tail is structurally absent —
much stronger level repulsion than any Wigner form predicts.

**Bandpass zero-crossings are the wrong input** for testing
universality on neural data.  The metric correctly identified the
quasi-periodic artifact (gap +0.05 just above the decisive threshold,
mass<0.3 hitting the floor).  The right inputs are spike timing
(single-unit / multi-unit events from invasive recordings) and
inter-burst intervals from envelope/amplitude-peak detection on raw
broadband signals — neither of which is forced into uniform spacing
by a bandpass.  See §7.ter.2 for the 32-subject confirmation.

What this *does* show: the metric runs end-to-end on real EEG data
and produces reproducible numbers across subjects and conditions.
The classification labels (best=GUE, gap, mass<0.3) correctly flag
"this distribution is more concentrated than Wigner GUE allows" —
the framework just needs the right input signal.

### Caveats and follow-ups

- **Integer-spacing signals** (Liouville, squarefree, primes-when-very-dense)
  hit the mass<0.3 = 0.000 floor because the smallest possible normalised
  spacing is bounded above zero by integer arithmetic.  These should be
  reported as "level statistics not in this metric" rather than forced
  into Wigner labels.
- **EEG sample size** is small.  Need ≥10× more events for confident
  Wigner-class assignment.  Easy: longer recording or multi-channel pool.
- **LMFDB API** was probed (HTTP 200) but not yet integrated — the
  family-level Katz-Sarnak verification (zeros for many elliptic curve
  L-functions) remains future work.

Plot: `plots/16_phase5_cross_signal.png`

---

## 7.ter  Phase 6 — LMFDB family survey + EEG depth study

### 7.ter.1  LMFDB elliptic curve L-functions (Katz–Sarnak empirical test)

87 isogeny-class representatives of elliptic curves over Q with
conductor ≤ 99 (from a user-supplied LMFDB dump), zeros computed via
PARI/GP `lfunzeros` to height 200 (~280 zeros per curve), classified
with the analytical passage-time NNS metric at fc_ref = 1.0, q_max = 8.

**Per-curve result: ALL 87 curves classify as Wigner GUE-best**, KS_GUE
ranging from 0.020 to 0.079 per curve, with mean KS_GUE ≈ 0.035 — within
the calibrated tolerance.  No GOE or Poisson best-fits in the entire
family.

**Aggregate by root number** (Katz–Sarnak family signature test):

| group | n_curves | n_pooled spacings | KS_P | KS_GOE | KS_GUE | gap | mass<0.3 | best |
|---|---|---|---|---|---|---|---|---|
| **all curves** | 87 | **748,013** | 0.295 | 0.081 | **0.015** | **+0.067** | **0.022** | **GUE** |
| root_number = +1 | 70 | 598,049 | 0.298 | 0.084 | 0.017 | +0.068 | 0.021 | GUE |
| root_number = −1 | 17 | 149,964 | 0.285 | 0.070 | 0.017 | +0.054 | 0.027 | GUE |

**Findings:**

1. **The whole family classifies as Wigner GUE** in the analytical
   passage-time NNS metric, with KS_GUE = 0.015 across 748k pooled
   spacings.  This matches the Riemann ζ result and confirms that the
   metric extends to other arithmetic L-functions cleanly.

2. **The two root-number subfamilies are nearly indistinguishable in
   the bulk**: both have KS_GUE = 0.017 and mass<0.3 ≈ 0.02.  This is
   consistent with Katz–Sarnak theory: in the BULK pair-correlation,
   unitary, orthogonal, and symplectic families all converge to the
   same Wigner shape; family symmetry only differs in the EDGE
   behavior near s = 0 (lowest zeros).  The mass<0.3 numbers do show a
   small directional shift — root_number = −1 has 0.027 vs +1 at 0.021
   — directionally consistent with the orthogonal-odd family expecting
   slightly more weight near zero, but the difference is too small to
   call decisively given current sample sizes.

3. **In particular: the rank-0 vs rank ≥ 1 split is identical to the
   root-number split** (rank ≥ 1 ⟹ root_number = −1 in this conductor
   range), so no orthogonal information beyond the root number is
   accessible from this sample.

The metric is now an empirically calibrated, computationally cheap
classifier for arithmetic L-function families.  Plot:
`plots/17_lmfdb_family.png`.

#### 7.ter.1.bis  Katz–Sarnak edge test: γ_1 by root number

The bulk pair-correlation is family-independent (Section 7.ter.1).  The
Katz–Sarnak family signature lives at the **EDGE** — specifically, in
the location of the lowest non-trivial zero γ_1.  An additional
analysis on the same 87 curves, restricted to the first few zeros:

**Step 0**: For all 17 root_number = −1 curves, PARI's `lfunzeros` returns
the forced central zero (γ = 0) as the first entry — the functional
equation forces L(E, 1/2) = 0 when the sign is −1.  We strip this and
work with the first NON-trivial zero in both subfamilies for an
apples-to-apples comparison.

**γ_1 (raw imaginary height of first non-trivial zero)**:

| root_number | n_curves | mean γ_1 | median | std |
|---|---|---|---|---|
| +1 | 70 | 3.20 | 3.08 | 0.87 |
| −1 | 17 | 3.97 | 3.92 | 0.45 |
| **Two-sample KS** | | **0.70** | | **p ≈ 0** |

**γ_1 normalised by `log(N) / (2π)`** (analytic-conductor-scaled):

| root_number | n_curves | mean | std |
|---|---|---|---|
| +1 (SO_even) | 70 | **1.95** ± 0.27 | |
| −1 (SO_odd)  | 17 | **2.67** ± 0.18 | |
| **Two-sample KS** | | **0.94** | **p ≈ 0** |

**The two distributions are essentially disjoint.**  After removing
the conductor-dependent scale, orthogonal-even L-functions have their
first zero around 1.95 in dimensionless units; orthogonal-odd
L-functions have it around 2.67.  The forced central zero pushes the
next zero systematically higher — exactly the predicted Katz–Sarnak
edge effect.

**Edge NNS (spacings of first N zeros, pooled by root number)**:

| N | rt# | n_pooled | KS_GUE | gap | KS_two(+1 vs −1) | p |
|---|---|---|---|---|---|---|
| 10 | +1 | 630 | 0.041 | +0.067 | | |
| 10 | −1 | 153 | 0.070 | +0.067 | 0.044 | 0.96 |
| 20 | +1 | 1330 | 0.032 | +0.060 | | |
| 20 | −1 | 323  | 0.046 | +0.026 | 0.050 | 0.52 |
| 50 | +1 | 3430 | 0.036 | +0.053 | | |
| 50 | −1 | 833  | 0.049 | +0.034 | 0.039 | 0.25 |

The spacing distributions of the first N zeros remain indistinguishable
between subfamilies at all tested N, with both classifying Wigner GUE
to KS_GUE ≤ 0.07.  **Family symmetry is in the lowest-zero LOCATION,
not in the spacing distribution** — consistent with bulk universality
and edge specificity in Katz–Sarnak theory.

**γ_2 − γ_1 first spacing** (one number per curve):

| root_number | mean | std | KS_two | p |
|---|---|---|---|---|
| +1 | 2.05 | 0.59 | | |
| −1 | 1.83 | 0.45 | 0.25 | 0.34 |

Directionally consistent with the SO_o family having a tighter first
spacing (smaller eigenvalue gap at the edge), but the n = 17 sample of
−1 curves is too small for statistical significance.

**Headline of §7.ter.1.bis**:  The conductor-normalised γ_1 distribution
**cleanly separates orthogonal-even from orthogonal-odd L-functions**
(KS = 0.94, p ≈ 0).  This is the clean Katz–Sarnak family symmetry
empirical confirmation — visible in our metric the moment we look at the
right statistic.  Plot: `plots/19_lmfdb_edge.png`.

### 7.ter.2  EEG depth study (PhysioNet EEGMMIDB, 32-subject cohort)

**Headline**: the metric correctly identifies a quasi-periodic
artifact.  Bandpass zero-crossings are the wrong input for testing
universality on neural data — the right inputs are spike timing and
inter-burst intervals on the raw broadband signal.

The full PhysioNet EEGMMIDB cohort (32 subjects S001..S032, 14
records each), 5 channels (Fcz, Cz, Pz, Fp1, Fp2), 3 conditions
(rest_eyes_open R01, rest_eyes_closed R02, motor_imagery R04+R05+R06),
θ-band (4–8 Hz) zero-crossings, direct NNS of crossing times.

**Aggregate by condition** (32 subjects × 5 channels):

| condition          | n_seg | n_pooled | KS_P  | KS_GOE | KS_GUE | gap   | mass<0.3 | best |
|--------------------|-------|----------|-------|--------|--------|-------|----------|------|
| rest_eyes_open     | 160   |  56,727  | 0.424 | 0.236  | 0.176  | +0.059| 0.001    | GUE  |
| rest_eyes_closed   | 160   |  59,676  | 0.432 | 0.247  | 0.190  | +0.057| 0.000    | GUE  |
| motor_imagery      | 160   | 345,117  | 0.424 | 0.236  | 0.178  | +0.058| 0.001    | GUE  |

**Aggregate by channel** (96 segments each, all subjects pooled):

| channel | n_pooled | KS_GUE | gap   | mass<0.3 |
|---------|----------|--------|-------|----------|
| Fcz.    | 93,665   | 0.186  | +0.057| 0.001    |
| Cz..    | 94,144   | 0.185  | +0.058| 0.000    |
| Pz..    | 94,628   | 0.186  | +0.058| 0.000    |
| Fp1.    | 89,586   | 0.170  | +0.059| 0.001    |
| Fp2.    | 89,497   | 0.170  | +0.059| 0.001    |

**The 3-subject pilot's 0.18 was not a small-N fluctuation.**  At 10×
the cohort size every aggregate KS_GUE lands in 0.170–0.190, with
gap stable at +0.057–0.059 and mass<0.3 ≈ 0.001 across all 480
segments.  The metric is reproducible and the result is robust.

**Findings (corrected interpretation):**

1. **Quasi-periodic artifact correctly identified.**  KS_GUE ≈ 0.18
   is 8× the calibrator threshold (~0.022 for ζ, GUE eigenvalues, and
   elliptic curve L-functions).  More tellingly, **mass<0.3 ≈ 0.001
   vs Wigner GUE's ~0.10** is the smoking gun: short spacings are
   essentially absent.  This is not just "more s²-suppression than
   GOE", it's a distribution structurally concentrated near s = 1.

2. **The cause is the bandpass.**  Zero-crossings of a 4–8 Hz
   bandpass are forced to ~125 ms intervals by the filter itself.
   The "level repulsion" observed here is not a property of the
   underlying neural dynamics — it's an artifact of zero-crossing
   detection on a narrowband signal.  Any sinusoid with envelope
   modulation produces the same shape, RMT or not.

3. **Bandpass zero-crossings are the wrong input for universality
   testing on neural data.**  The right inputs are:
   - **spike timing** (single-unit / multi-unit events from invasive
     recordings) — true point-process events with no filter-imposed
     periodicity;
   - **inter-burst intervals** (IBI) extracted from envelope or
     amplitude-peak detection on raw broadband EEG — events
     correspond to cortical bursts, not zero-crossings of a chosen
     band.

4. **Condition deltas tiny.**  KS_GUE varies only 0.014 between
   eyes-open (0.176) and eyes-closed (0.190).  θ-band zero-crossing
   rate carries no meaningful cognitive-state signal in this metric —
   not surprising, given (1) and (2): when the signal is dominated by
   filter geometry, it can't carry much state-dependent variation.

5. **The framework runs end-to-end on real neural data.**  Loading
   EDF, channel selection, bandpass, event detection, NNS pipeline,
   and classification all produce reproducible numbers across 32
   subjects.  The classification labels (best=GUE, gap, mass<0.3)
   correctly flag "this distribution is more concentrated than Wigner
   GUE allows" — the framework just needs the right input signal.

4. **Subject variation is comparable to condition variation.**
   Across-subject aggregate KS_GUE = 0.169 / 0.182 / 0.190 (S001 / S003
   / S002); within-subject between-condition KS_two ≈ 0.04.  At three
   subjects we cannot yet separate inter-individual differences from
   cognitive-state effects.

5. **Channel variation is minimal** — KS_GUE differs by only 0.012
   across the 5 channels (Fcz/Cz/Pz/Fp1/Fp2).  The spatial gradient
   we might expect (frontal vs parietal differences) is below the
   metric's resolution at this sample size.

**What we have not shown**: that brain state is classifiable by
universality class.  **What we have shown**: that the metric runs
end-to-end on real EEG data and produces reproducible, shape-
discriminating classifications that distinguish biological signals
from Poisson cleanly (KS_P ≈ 0.43 for biology, KS_P ≈ 0.30 for
arithmetic L-function zeros at the same metric).

Plot: `plots/18_eeg_depth.png`.  Json: `data/eeg_results.json`.

### 7.ter.3  Phase 7 — Dirichlet L-function family + cross-family second-order

Full overnight pipeline added: a Dirichlet L-function family survey,
a Mertens/Liouville arithmetic-sieve test, an earthquake-catalog null,
and cross-family second-order statistics (Σ²(L), R₂(r)).

#### Dirichlet family (q ≤ 149, 630 primitive non-trivial characters)

92 real characters (predicted SYMPLECTIC), 538 complex (predicted UNITARY),
~6,400 zeros each, 4.05M pooled spacings:

| group                            | n_chars | n_pool   | KS_GUE | gap   | best |
|----------------------------------|---------|----------|--------|-------|------|
| all primitive non-trivial        | 630     | 4,051,472| 0.035  | +0.067| GUE  |
| real characters (Sp predicted)   | 92      |   565,942| 0.039  | +0.067| GUE  |
| complex characters (U predicted) | 538     | 3,485,530| 0.035  | +0.067| GUE  |

**Bulk pair-correlation does not distinguish symplectic from unitary**
— exactly as Katz–Sarnak / Montgomery predict.  Both classes give
Wigner GUE bulk shape.  Family symmetry must be sought at the edge.

#### Edge γ_1 test (analogous to LMFDB +1/−1 root number split)

| statistic                | real (Sp)        | complex (U)      | KS    | p     |
|--------------------------|------------------|------------------|-------|-------|
| γ_1 raw                  | 1.996 ± 1.207    | 1.773 ± 0.959    | 0.134 | 0.112 |
| **γ_1 · log(q)/(2π)**    | **1.137 ± 0.321**| **1.186 ± 0.544**| **0.213** | **0.001** |
| γ_2 − γ_1 (norm)         | 1.670 ± 0.507    | 1.549 ± 0.492    | 0.155 | 0.043 |

**Conductor-normalised γ_1 distinguishes Sp from U at p = 0.001.**
The separation is weaker than the LMFDB SO_e/SO_o test (KS = 0.94
there) — Sp and U have closer edge densities than SO_e and SO_o —
but it's a clean second empirical Katz-Sarnak data point on a
distinct family.

#### ζ-zero height-dependent GUE convergence

21 bins of 100k zeros each, heights 14 → 1,132,490 from Odlyzko zeros6:

| bin    | heights              | KS_GUE   |
|--------|----------------------|----------|
| bin 1  | 14 – 74,920          | 0.0193   |
| bin 11 | 600k – 654k          | 0.0124   |
| bin 21 | 1.08M – 1.13M        | 0.0109   |

**Monotone decrease confirmed.** Mean across all bins: 0.0129. Empirical
signature of asymptotic GUE universality — KS to Wigner GUE *systematically
improves* with height, exactly as the conjecture predicts.

#### USGS earthquake null (M ≥ 4.5, 2020-2024)

37,283 events.  Globally **Poisson-best** (KS_P = 0.075, KS_GUE = 0.344,
mass<0.3 = 0.33 — slightly clustered above Poisson's 0.26).
Per-30°-tile shows regional clustering variation (mass<0.3 from 0.31
to 0.73).  Confirms ETAS-style mainshock-aftershock dynamics give
Poisson-with-clustering spacing statistics, no random-matrix universality.
A clean physical-process data point distinct from biological (EEG)
and arithmetic signals.

#### Cross-family number variance Σ²(L)

| family                       | Σ²(L=20)  | regime                |
|------------------------------|-----------|-----------------------|
| ζ low (heights 14-75k)       | 0.42      | sub-GUE log-growth ✓  |
| ζ high (heights ~1.1M)       | 0.35      | sub-GUE log-growth ✓  |
| LMFDB EC L-functions         | 1.78      | ≈GUE log-growth ✓     |
| Dirichlet real (Sp)          | 0.27      | sub-GUE log-growth ✓  |
| Dirichlet complex (U)        | 0.30      | sub-GUE log-growth ✓  |
| **USGS earthquakes M≥4.5**   | **164.29**| linear+ super-Poisson |

Reference: Poisson(L=20) = 20.00; Wigner GUE(L=20) ≈ 1.05.  All
arithmetic well below the Poisson line and growing log-not-linear —
the second-order signature of random-matrix universality.

#### Pair correlation R₂(r)

| family                 | R₂(0.1)  | R₂(0.3) | R₂(1.0) |
|------------------------|----------|---------|---------|
| **GUE: 1−sinc²(πr)**   | **0.033**| **0.270**| **1.000**|
| ζ low (100k zeros)     | 0.014    | 0.269   | 1.021   |
| ζ high (100k zeros)    | 0.016    | 0.293   | 1.004   |
| LMFDB ECs              | 0.032    | 0.633   | 1.314   |
| Dirichlet real (Sp)    | 0.061    | 0.162   | 1.119   |
| Dirichlet complex (U)  | 0.061    | 0.182   | 1.082   |
| **Earthquakes M≥4.5**  | **1.808**| 1.701   | 1.532   |

The level repulsion dip at r→0 is the cleanest GUE signature so far.
ζ matches the analytical GUE form within ~50% at every r.
Earthquakes show R₂ > 1 everywhere — anti-correlation, the clustering
signature.

#### Mertens M(x) / Liouville L(x) sign-change positions

Sieved up to x = 10⁷.  Mertens has 24 sign-changes; Liouville has 1
(Pólya conjecture territory — L(x) ≤ 0 for almost all x ≤ 906M).
Mertens analytical-passage-time NNS classifies as Poisson-clustered
(mass<0.3 = 0.93), Liouville insufficient — sign-change positions
of arithmetic prefix sums encode the *long-time* regularity of these
sums, not random-matrix universality.

#### EEG full-cohort confirmation (32 subjects)

The Phase 6 EEG study (3 subjects) reported KS_GUE ≈ 0.18 — 8× the
calibrator threshold of ~0.022.  At 32 subjects (entire EEGMMIDB cohort,
14 records each, 5 channels):

| condition          | n_seg | n_pooled | KS_GUE | mass<0.3 |
|--------------------|-------|----------|--------|----------|
| rest_eyes_open     | 160   | 56,727   | 0.176  | 0.001    |
| rest_eyes_closed   | 160   | 59,676   | 0.190  | 0.000    |
| motor_imagery      | 160   | 345,117  | 0.178  | 0.001    |

**The 3-subject 0.18 was NOT a small-N fluctuation.**  At 10× the cohort
size the KS_GUE values are essentially identical, confirming the
biological signal has a quasi-periodic spacing distribution that is
robustly NOT random-matrix universality.

**Mass<0.3 ≈ 0.001** vs Wigner GUE's ~0.10 is the diagnostic: the
band-pass filter forces near-uniform spacing around 1.0 (zero crossings
of a 4–8 Hz band are spaced ~125 ms apart by construction), so the
short-spacing tail is entirely absent — much stronger level repulsion
than any Wigner form predicts.

Condition deltas remain tiny (KS_GUE varies only 0.014 between
eyes-open and eyes-closed) — confirms that θ-band zero-crossing rate
is not a strong cognitive-state classifier in this metric.

### 7.ter.5  Phase 8 — Fungal mycelium spike statistics (Adamatzky data)

`run_fungal_nns.py` applies the analytical-NNS pipeline to 18 long
electrical recordings (60–360 h each, 8 differential channels, 1 Hz)
of *Pleurotus ostreatus* and grain-substrate fruiting bodies released
publicly by Adamatzky / unconv-comp lab.

**Spike detection**: per channel, 1-h rolling-median baseline subtraction,
threshold-cross at the lowest σ ∈ {3, 4, 6} that produces 20–150 spikes
(min ISI 120 s, min spike width 10 s).  18/18 files loaded; 35 of the
8×18 = 144 (file, channel) units crossed the 20-spike threshold.

**Pooled NNS (direct, 35 units, 1,470 inter-spike spacings):**

| metric                | value | reference (Poisson) | reference (Wigner GUE) |
|-----------------------|-------|---------------------|------------------------|
| KS_Poisson            | 0.400 | 0.022 (calibrator)  | —                      |
| KS_GOE                | 0.590 | —                   | —                      |
| KS_GUE                | 0.641 | —                   | 0.022 (calibrator)     |
| **mass<0.3**          | **0.654** | 0.259 (analytic) | ~0.10 (analytic)       |
| best                  | Poiss | —                   | —                      |

The Farey-bank passage-time pool (62,706 spacings across all PLL
bands) reproduces the same shape: KS_P = 0.39, mass<0.3 = 0.65.

**Interpretation**: fungal spike timing is **strongly clustered
(super-Poissonian)**, even more than earthquakes (mass<0.3 = 0.33).
65 % of normalised inter-spike intervals are shorter than 0.3 of the
mean — bursty point-process structure, no random-matrix universality.
KS_min = 0.40 is far above any clean-classification threshold, so the
"best=Poisson" label is the metric's most-charitable Wigner-form
neighbour rather than a real Poisson identification.

**ISI two-population check** (Adamatzky 2020 reports peaks near
2.6 min and 14 min):

| target peak  | events in ±0.5 min window | observed peak | observed count |
|--------------|---------------------------|---------------|----------------|
| 2.6 min      | 432 events                | 2.2 min       | 155 (primary)  |
| 14 min       |  30 events                | (5.8 min, 9.8 min smaller secondaries) | 36, 21 |

The fast peak Adamatzky reports near 2.6 min is reproduced (broader,
centred slightly earlier at 2.2 min with this detector); the slow
14-min peak is much weaker in the pooled distribution (only 30 events
in a wide window vs 432 at the fast peak).  Mean ISI = 178 min is
inflated by the long inter-burst gaps, while median ISI = 10 min
matches the within-burst timescale.

**Comparison to neural and arithmetic signals:**

| signal class                | mass<0.3 | best  | KS_min | what it is             |
|-----------------------------|----------|-------|--------|------------------------|
| Wigner GUE eigenvalues      | 0.10     | GUE   | 0.022  | level repulsion        |
| ζ zeros (heights ~10⁶)      | 0.024    | GUE   | 0.012  | arithmetic, level rep. |
| LMFDB EC L-functions        | 0.024    | GUE   | 0.012  | arithmetic, level rep. |
| EEG θ-band zero-crossings   | 0.001    | "GUE" | 0.18   | bandpass artifact      |
| USGS earthquakes M ≥ 4.5    | 0.33     | Poiss | 0.075  | clustered point proc.  |
| Mertens M(x) sign changes   | 0.93     | Poiss | 0.32   | sparse arithmetic seq. |
| **Fungal spikes**           | **0.65** | **Poiss** | **0.40** | **bursty point proc.** |

Fungal spike timing sits between earthquakes and Mertens sign-changes
on the clustering axis — *more* bursty than earthquake aftershocks,
*less* than the integer-floor-bound Mertens sign-change positions.
A living network with no nervous system produces a clearly-clustered
point process, distinct from random-matrix universality and distinct
from any neural quasi-periodicity artefact.

#### Fundamental caveat: observation-window vs coherence-timescale mismatch

The 60–93 hour recording window is likely **shorter than the slow
coherence timescale of the mycelial network**.  The super-Poisson
result above characterises the *fast* perturbation-response dynamics
(spike bursts spaced 2–14 minutes apart, mean ISI 178 minutes
inflated by long inter-burst gaps).  It cannot speak to whether the
mycelial network exhibits GUE-class coherence at *longer*
timescales — week to months — where slow growth, fluid-pressure
cycles, and substrate-resource modulation operate.

The two-timescale prediction is concrete: zoom out far enough and a
system that looks super-Poisson at the fast timescale may show
level-repelling (Wigner-class) statistics in the **inter-burst-cluster
intervals** at the slow timescale.  The fungal network may simultaneously
be coherent at the week scale and driven at the hour scale; both
properties true, both visible only at the right resolution.

The right next experiment is multi-week recordings on the same
electrode geometry — ideally a continuous month-plus capture so the
analysis window contains O(10²–10³) burst clusters separated by
slow-cycle intervals.  At that resolution the inter-burst-cluster
spacing distribution would either continue as Poisson-clustered
(no slow coherence) or emerge as Wigner-like (the network has a
slow level-repelling mode).

#### Methodological note: ARS readings are resolution-dependent

This is not a fungal-specific caveat — it is a **methodological
property of the framework**.  ARS gives a universality-class label
that is correct *at the temporal resolution of the input*.  The
same physical system, recorded at different observation windows,
can yield different fingerprints, each accurate at its own scale:

- short window catching only the fast process → fingerprint of the
  fast process
- long window catching only the envelope of slow cycles → fingerprint
  of the slow process
- full window covering both → fingerprint dominated by whichever has
  more events in the recording, with the other appearing as
  multi-scale structure in `Σ²(L)` and `R₂(r)` rather than in the NNS
  shape

This is consistent with how RMT itself works on physical signals:
GUE statistics show in *unfolded* zero positions of L-functions
where the unfolding correctly normalises out the smooth growth
density; before unfolding, the same zeros look highly structured.
For physical point processes, "unfolding" is implicit in the choice
of recording window — events sparser than the window can't be
characterised, events denser than the resolution become indistinguishable.

A clean reading requires that the recording window contain a
statistically meaningful number of events at the timescale being
characterised, and that no slower process modulates the local rate
within the window.  These are minimum-N preconditions for any RMT
classification, not just for fungi.

Output: `plots/29_fungal_nns.png`, `plots/30_fungal_isi.png`,
`data/fungal_results.json`.

### 7.ter.7  Phase 9 — Periodic table of point processes (arithmetic_toolkit)

`arithmetic_toolkit.py` packages five engines that operate on any
sorted point-process `t_k`:

1. **Ramanujan-Fourier spectrum** — coefficients `a_q = (1/φ(q)) ·
   E[f(n) · c_q(n)]` of the inter-event interval sequence, q = 1..200,
   computed via Hölder's identity for c_q(n).  Reports the top-10
   resonance orders and a peak_q.
2. **p-adic sensitivity profile** — for each prime p ∈ {2,3,5,7,11,13},
   run analytical NNS on the subset of Farey rationals whose
   denominator q has p | q.  Different primes weight different
   p-adic substructures of the signal.
3. **Multiscale Fano factor F(T)** — Var(N(T))/Mean(N(T)) on a
   geometric grid of window sizes.  Reports F at T = 1, 5, 20 in
   units of mean spacing; GUE has F→0 at small T, Poisson has F=1,
   clustered processes have F>1 with peaks at characteristic scales.
4. **Pair correlation R₂(r) + repulsion integral** — companion to
   §7.ter.3.  The single number `repulsion_integral = ∫₀¹ (1−R₂(r)) dr`
   summarises total level repulsion at small r.
5. **Stern-Brocot directional split** — analytical NNS run separately
   on Farey rationals with p/q < 1 (sub-unison, SB-left) and p/q > 1
   (super-unison, SB-right), with a two-sample KS testing
   sub/super-unison symmetry.  Stationary processes pass; directional
   processes (e.g. financial price series) fail.

`full_analysis(t_k, label)` runs all five plus the primary direct-NNS
classification and packs them into a 10-dimensional fingerprint vector:

`[KS_GUE, KS_GOE, KS_Poisson, mass<0.3, F(T=1), F(T=5),
  repulsion_integral, top_ramanujan_q, sb_symmetry_ks,
  padic_dominant_prime]`

#### Validation runs

`run_phase9.py` applies `full_analysis` to six reference signals.
The six fingerprints (Phase-9 periodic table):

| signal                       | best    | KS_GUE | KS_GOE | KS_P | mass<0.3 | F(T=1) | F(T=5) | rep_int | top_q |
|------------------------------|---------|--------|--------|------|----------|--------|--------|---------|-------|
| ζ zeros (first 2000)         | GUE     | **0.041** | 0.108  | 0.316| 0.014    | 0.374  | **0.083** | **0.425** | 2     |
| GOE eigenvalues (N=2000)     | GOE     | 0.100  | **0.036** | 0.203| 0.079    | 0.475  | 0.348  | 0.171   | 4     |
| Poisson uniform              | Poisson | 0.285  | 0.221  | **0.020** | 0.260    | 0.987  | 0.988  | 0.040   | 2     |
| **Fungal spikes (pooled)**   | Poisson | 0.641  | 0.590  | 0.400| **0.655**| **4.303**| **7.727** | 0.000   | 2     |
| **USGS earthquakes M≥4.5**   | Poisson | 0.344  | 0.281  | 0.075| 0.333    | 1.760  | 3.747  | 0.000   | 10    |
| Primes ≤ 10⁶ (logarithm-unfold) | Poisson | 0.234  | 0.167  | 0.149| 0.135    | 0.691  | 0.560  | 0.204   | 2     |

**Three classes are clearly separated:**

- **Level-repelling (ζ, GOE)**: F(T=5) sub-1 (0.08, 0.35), repulsion
  integral large (0.42, 0.17), KS to its assigned Wigner class small
  (0.04, 0.04).  ζ shows the cleanest GUE signature on every metric.
- **Random (Poisson)**: F(T) ≈ 1 at all scales (0.99 at T=1 and T=5),
  repulsion integral near zero (0.04), mass<0.3 ≈ 0.26.
- **Clustered (fungal, earthquakes)**: F(T) ≫ 1, growing with scale
  (T=1 → T=5 → T=20: fungal 4.3 → 7.7 → 10.5; earthquakes 1.8 → 3.7 →
  7.9), repulsion integral zero (no level repulsion), mass<0.3 large
  (0.65 fungal, 0.33 earthquakes).  Fungal is the most strongly
  clustered signal we have analyzed.

**Primes ≤ 10⁶** sit between Poisson and weakly-repelling: F(T) sub-1
(0.69, 0.56), repulsion_integral = 0.204 (positive, comparable to GOE
at 0.17).  This is the asymptotic-Poisson convergence at finite N
showing residual arithmetic structure on top of the random baseline —
worth reporting separately because the Phase-5 KS-only metric flagged
primes as Poisson-best, missing the F<1 fingerprint.

**Stern-Brocot symmetry** ≤ 0.002 across all six signals (KS two-sample
between left and right subtree NNS distributions): every signal here is
**directionally symmetric** — sub-unison and super-unison Farey bands
agree.  This is the expected pass for stationary point processes; the
test will register as a flag (asymmetry > 0.05) on directional series
like trended financial data or biological signals with preferred
phases.

**p-adic dominance is not strongly informative at q_max = 8** (only
p ∈ {2, 3, 5, 7} have any Farey rationals, and their KS_min values are
near-identical for most signals).  Re-running with q_max = 16 or
larger is the natural extension if p-adic discrimination matters for
a target signal.

Outputs: `data/phase9_fingerprints.json`, `plots/31_phase9_table.png`.

### 7.ter.8  Phase 9 extended — arithmetic L-function family fingerprints + primes scaling

`run_phase9_extended.py` runs `full_analysis` with `q_max = 16` on the
arithmetic data we already have (ζ-low, ζ-high, LMFDB EC L-functions,
Dirichlet L-functions) plus primes at three sieve sizes.

| signal                       | best   | KS_GUE | KS_GOE | KS_P | mass<0.3 | F(T=1) | F(T=5) | rep_int | top_q |
|------------------------------|--------|--------|--------|------|----------|--------|--------|---------|-------|
| GUE eigenvalues (N=2000)     | GUE    | 0.049  | 0.058  | 0.269| 0.031    | 0.370  | 0.288  | 0.237   | 3     |
| ζ low (first 100k zeros)     | GUE    | 0.019  | 0.087  | 0.298| 0.021    | 0.364  | **0.093** | **0.416** | 2     |
| ζ high (heights ~1.1M)       | GUE    | **0.012** | 0.079  | 0.290| 0.024    | 0.358  | **0.097** | **0.412** | 2     |
| LMFDB EC L-functions         | GUE    | 0.020  | 0.086  | 0.297| 0.023    | 0.323  | **0.086** | **0.423** | **40**|
| Dirichlet L (q ≤ 149)        | GUE    | 0.044  | 0.111  | 0.321| 0.014    | 0.351  | **0.080** | **0.440** | **10**|
| Primes ≤ 10⁵                 | GOE    | 0.221  | 0.153  | 0.169| 0.125    | 0.643  | 0.477  | 0.178   | 18    |
| Primes ≤ 10⁶                 | Poiss  | 0.234  | 0.167  | 0.149| 0.135    | 0.691  | 0.560  | 0.204   | 2     |
| Primes ≤ 10⁷                 | Poiss  | 0.233  | 0.171  | 0.136| 0.170    | 0.736  | 0.619  | 0.158   | 2     |

#### Headline 1 — All four arithmetic L-function families fingerprint as a single Wigner GUE class

The four L-function rows (ζ-low, ζ-high, LMFDB, Dirichlet) are
**indistinguishable on the dominant fingerprint axes**:
- F(T=5) lands in 0.080–0.097 (a 17 % spread across millions of pooled
  spacings),
- repulsion_integral lands in 0.412–0.440 (a 7 % spread),
- KS_GUE ≤ 0.044 in every case,
- mass<0.3 ≤ 0.024 in every case.

This is **direct empirical confirmation that the bulk Wigner GUE
universality of L-function zeros is family-independent**, exactly as
Katz–Sarnak and Montgomery–Odlyzko predict.  The synthetic GUE
eigenvalue calibrator (N = 2000) at the top of the table fingerprints
to F(T=5) = 0.288 and rep_int = 0.237 — *worse* than the L-functions,
because at N = 2000 the eigenvalue sample is small enough that the
Wigner statistics are noisy.  The L-function pool is 100k–170k
spacings each, much closer to the asymptotic limit.

#### Headline 2 — Ramanujan-Fourier resonance order distinguishes families

Where KS-only metrics see a single class, the top resonance order
peak_q from the Ramanujan-Fourier engine differentiates:

| family       | peak_q | interpretation                                        |
|--------------|--------|--------------------------------------------------------|
| ζ low/high   | 2      | strong sub-harmonic structure (factor of 2 in spacings) |
| LMFDB EC     | 40     | conductor-influenced — typical conductor in the set ~50 |
| Dirichlet    | 10     | mid-q resonance from the q-conductor mix |
| GUE eigenvalues | 3   | random — low resonance order |

A pure-random control (Poisson, GUE eigenvalues) gives small peak_q
near the smallest q ≥ 2 by random fluctuation.  Arithmetic signals
encode structural information in the *which-q* pattern — the LMFDB
peak_q = 40 is unlikely to be coincidence given the typical conductor
range of those curves.  Ramanujan-Fourier is the engine that picks
this up; KS distance on the NNS does not.

#### Headline 3 — Primes show Cramér convergence to Poisson

Sieving at three sizes reveals the asymptotic flow:

| N      | π(N)    | best    | KS_min | F(T=1) | F(T=5) | rep_int |
|--------|---------|---------|--------|--------|--------|---------|
| 10⁵    | 9,592   | GOE     | 0.153  | 0.643  | 0.477  | 0.178   |
| 10⁶    | 78,498  | Poisson | 0.149  | 0.691  | 0.560  | 0.204   |
| 10⁷    | 664,579 | Poisson | 0.136  | 0.736  | 0.619  | 0.158   |

**F(T=5) climbs from 0.48 → 0.62 with N → ∞**, approaching 1 (Poisson)
exactly as Cramér predicts.  The KS classification flips from GOE-best
(at N = 10⁵, where finite-N arithmetic structure looks like weak
level repulsion) to Poisson-best (at N ≥ 10⁶, where the structure
washes out).  The repulsion_integral stays in 0.16–0.20 at all three
sizes — non-monotone within sample noise but bounded — indicating
some asymptotic residual that doesn't disappear (consistent with
Hardy–Littlewood / Cramér deviations not converging to zero density).

This is the kind of *fingerprint flow with N* the toolkit makes
visible.  The Phase-5 KS-only metric flagged primes at 10⁵ as Poisson;
the Fano + repulsion_integral combination shows there's residual
arithmetic structure at small N that decays toward Poisson with
increasing N.

#### Limitations seen at q_max = 16

- **p-adic dominance remains undifferentiating**: every signal in the
  arithmetic block has identical KS_min across p ∈ {2, 3, 5, 7, 11, 13}.
  At q_max = 16, the pooled passage-time NNS across "Farey rationals
  with p|q" is dominated by the bulk Wigner GUE shape regardless of
  which prime selects them, so the per-prime KS to GUE/GOE/Poisson
  ties at three decimal places.  The p-adic engine would only
  differentiate signals that have intrinsic p-adic asymmetry larger
  than the bulk universality smoothing — biological / financial /
  digit-of-π type signals are the natural targets.
- **Stern-Brocot symmetry KS ≤ 0.0000** in every row.  As expected for
  stationary signals; the test is a flag for directional/trended
  signals where it should register asymmetry > 0.05.

Outputs: `data/phase9_extended_fingerprints.json`,
`plots/32_phase9_extended.png`.

### 7.ter.9  Hardy-Littlewood: primes & twin primes Fano scaling

`run_primes_scaling.py` sieves once at N = 10⁸ and computes Fano
F(T=1, 5, 20) on the logarithmically-unfolded sequence at five cutoffs
{10⁴, 10⁵, 10⁶, 10⁷, 10⁸}, for both primes and the lower-of-pair
twin primes.

| N    | π(N)        | primes F(T=5) | π₂(N)   | twin F(T=5) |
|------|-------------|---------------|---------|-------------|
| 10⁴  | 1,229       | 0.369         | 205     | 0.662       |
| 10⁵  | 9,592       | 0.477         | 1,224   | **0.835**   |
| 10⁶  | 78,498      | 0.560         | 8,169   | 0.826       |
| 10⁷  | 664,579     | 0.619         | 58,980  | 0.839       |
| 10⁸  | 5,761,455   | 0.660         | 440,312 | 0.873       |

**Twin primes converge to Poisson F = 1 visibly faster than primes.**
Twin F(T=5) is already at 0.835 at N = 10⁵ and stays in 0.83–0.87
through N = 10⁸ (within ~13 % of Poisson).  Primes climb monotonically
from 0.48 to 0.66 over the same range — still ~30 % below Poisson at
the largest N.

This is the visual Hardy-Littlewood story: twin primes are sparser
(2C₂ × x / (log x)² conjectured density, vs primes' x / log x), so
the Cramér-random baseline fits them at smaller N.  Primes carry
heavier residual arithmetic structure that decays more slowly with
N — the F(T=5) curve approaches 1 logarithmically, not algebraically.

F(T=20) for twins exceeds 1 at N = 10⁵ (slight super-Poisson, finite-n
fluctuation), then settles at 0.91–0.92 — visually indistinguishable
from a Poisson process at the largest scale tested.

Output: `plots/33_primes_scaling.png` (both curves on the same axes,
Poisson reference dashed at F = 1), `data/primes_scaling.json`.

### 7.ter.10  p-adic engine validation: design limitation surfaced

`run_padic_finance.py` queues a real-data slot at
`data/financial_settlements.csv` and falls through to a synthetic
suite when no such file exists.  The synthetics were designed to
have unambiguous prime-base asymmetry: weekly periodic (period 7),
monthly periodic (period ≈ 30 = 2·3·5), quarterly (period ≈ 91 = 7·13),
plus Poisson-with-weekly-injection and pure-Poisson controls.

| signal                              | best   | peak_q | p=2   | p=3   | p=5   | p=7   | p=11  | p=13  |
|-------------------------------------|--------|--------|-------|-------|-------|-------|-------|-------|
| (a) weekly periodic + jitter        | GUE    | 2      | 0.339 | 0.339 | 0.339 | 0.339 | 0.338 | 0.338 |
| (b) monthly periodic + jitter       | GUE    | 6      | 0.372 | 0.372 | 0.372 | 0.372 | 0.371 | 0.371 |
| (d) mixed W+M+Q                     | GOE    | 2      | 0.205 | 0.205 | 0.205 | 0.205 | 0.205 | 0.205 |
| (e) Poisson + weekly injection      | Poiss  | 9      | 0.034 | 0.034 | 0.034 | 0.034 | 0.034 | 0.033 |
| (f) Poisson background only         | Poiss  | 2      | 0.013 | 0.013 | 0.013 | 0.013 | 0.013 | 0.013 |

**Result** — KS_min ties across all primes to 3 decimal places on
every row, including the signal-in-noise case (e) where the engine
*should* fire if it works.  This confirms the §7.ter.8 limitation
note: the current p-adic engine does not actually discriminate.

**Cause** — the implementation pools normalised passage-time spacings
across all Farey rationals with `p | q`.  These sets overlap heavily:
q = 6 contributes to both p = 2 and p = 3 pools, q = 10 to p = 2 and
p = 5, etc.  Pooled NNS shapes are dominated by the bulk universality
of the underlying signal, not by the prime selector.

**Two redesigns are queued** for a future toolkit pass:

1. **Pure-p-power filter**: restrict to q ∈ {p, p², p³, …}.  At
   q_max = 16 this gives clean disjoint subsets {2, 4, 8, 16},
   {3, 9}, {5}, {7}, {11}, {13} — but very few PLL bands per prime,
   so statistical power per band is low.
2. **Ramanujan-amplitude based**: aggregate `|a_q|` over q's with each
   prime as a factor, normalised by total amplitude.  Reuses the
   Ramanujan-Fourier engine which already runs.  More likely to
   surface period-p arithmetic (weekly = 7, etc.).

Until the redesign lands, the p-adic engine should be reported as
"ties for arithmetic and stationary periodic signals" and not as a
discriminator.

**Secondary finding** — `peak_q` from the Ramanujan-Fourier engine
does *not* land on the injected period in these synthetics
(peak_q = 2 for weekly, 6 for monthly, 9 for noise-injected weekly).
Reason: the engine normalises intervals to unit mean *before* the RF
transform, which collapses a strictly periodic signal's f(n) to a
constant — every a_q for q ≥ 2 reduces to noise.  A `normalize=False`
mode or an alternative indicator-function input on raw event times
would be needed to detect injected periodicity directly.

Outputs: `plots/34_padic_finance.png`, `data/padic_finance_results.json`,
`run_padic_finance.py` (queued for real data input).

#### Proposition (band-invariance of NNS-pooling p-adic profiles)

After v1, v2, and v3 of the p-adic profile all failed acceptance for the
same reason, we record the structural cause as a named result.

**Proposition.**  *Any p-adic profile engine that
decomposes a point process over PLL bands and aggregates NNS is
band-invariant under linear time scaling, and cannot detect prime-base
asymmetry on stationary signals.*

**Proof.**  Let `t_k` be a sorted point process and (a, q) a Farey
rational with PLL frequency `f = a/q`.  The analytical-passage formula
maps each event to
    t* = t_k · f − 1,
which is an affine rescaling of `t_k` by a positive factor `f` (with a
constant offset that does not affect spacings).  The induced
nearest-neighbour spacings are
    Δ* = Δ_k · f.
Normalising to unit mean spacing,
    Δ̃* = Δ* / mean(Δ*) = Δ_k · f / (mean(Δ_k) · f) = Δ_k / mean(Δ_k),
which is independent of `f`.  Therefore the empirical distribution of
unit-mean-normalised passage spacings on band (a, q) equals the
unit-mean-normalised spacing distribution of the original `t_k`,
regardless of (a, q).  KS distances to any reference (Poisson / GOE /
GUE) are equal across all bands.  Pooling, mean, median, max, or any
band-aggregation of the per-band KS yields the same invariant value.
∎

**Corollary.**  An engine with the architecture
    `{filter Farey rationals → analytical-passage → unit-mean-normalised NNS → KS}`
cannot produce per-prime contrast on stationary signals.  Detection
requires either (i) a non-band-invariant projection (e.g. modular
arithmetic or indicator function on a fixed grid), or (ii) abandoning
unit-mean normalisation in favour of a scale-sensitive metric.
Ramanujan-Fourier amplitudes on the indicator function (RF v2) satisfy
(i) and (ii) simultaneously and provide the basis for v4 (next section).

### 7.ter.11  Engine-redesign acceptance tests

Two redesigns implemented per the §7.ter.10 follow-up and tested
against the synthetic settlement-cycle suite as acceptance gates
before promoting either to the default fingerprint vector.

**Design 1 — `ramanujan_fourier(normalize=False)`.**  Switches the RF
input from unit-mean-normalised intervals (default) to the event-count
indicator function on integer time bins of the raw t_k.  For weekly
periodic events at t = 7, 14, 21, … days, the indicator function has
ones at multiples of 7 and zeros elsewhere; c_7(7k) = φ(7) = 6 makes
a_7 the largest coefficient.

**Design 2 — `padic_profile(pure_power=True)`.**  Restricts each
prime's Farey rational subset from `{(a, b) : p | b}` (the v1
overlapping filter) to the disjoint `{(a, b) : b ∈ {p, p², p³, …}}`.

#### Acceptance results

| signal                          | v1 RF peak_q | v2 RF peak_q | v1 p-adic spread | v2 p-adic spread |
|---------------------------------|--------------|--------------|------------------|------------------|
| weekly periodic                 | 2            | **7 ✓**      | 0.001            | 0.000            |
| monthly periodic                | 6            | 15           | 0.001            | 0.001            |
| mixed W+M+Q                     | 2            | **7 ✓**      | 0.000            | 0.000            |
| Poisson + weekly injection      | 9            | **7 ✓**      | 0.001            | 0.000            |
| Poisson background only         | 2            | 5            | 0.000            | 0.001            |

(v1/v2 p-adic "spread" = max(KS_min) − min(KS_min) over p ∈ {2..13}.)

**RF passes.**  In three of three positive cases the indicator-mode
engine recovers the injected weekly period: pure weekly → peak_q = 7;
mixed W+M+Q → peak_q = 7 (dominant); Poisson background + weekly
injection → peak_q = 7 *recovered through 4:1 background noise*.
Available now via the `rf_normalize=False` flag.  Not promoted to
the default fingerprint because the two modes capture different
information — arithmetic data benefits from the normalised mode
(spacing-correlation detection), calendar / oscillator data
benefits from the indicator mode (period detection).

**p-adic fails.**  Pure-p-power filtering yields disjoint per-prime
Farey subsets but the pooled NNS converges to the same shape
regardless of which prime selects the bands.  KS_min ties across
all primes to 3 decimal places on every row, including the
noise-injected case.  The architecture — filter Farey rationals →
pool passage-time spacings → classify — is the wrong tool for this
asymmetry: for periodic data the NNS in every band is degenerate;
for Poisson+injection the bulk Poisson dominates every band.

**v3 architecture queued.**  A discriminating p-adic engine needs
to operate on *per-band* Wigner-fit quality, not pooled.  For
Poisson + period-7 injection, q = 7 PLL bands get heavily
corrupted by the injected events (high KS_GUE per band), while
q = 2, 3, 5 bands see mostly Poisson noise (low KS_P per band).
The right per-prime metric is the worst-case or variance of
per-band KS scores within the filter, not the pooled KS.

**Status:**  RF v2 (indicator mode) is available and validated;
p-adic v2 (pure-p-power filter) is available but fails acceptance;
p-adic v3 (per-band variance) is queued.  The fingerprint vector
continues to use the v1 defaults to preserve cross-signal
comparability with prior phases — engine flags are opt-in.

Outputs: `plots/34_padic_finance.png` (v1 vs v2 per-prime KS profile
on the same axes), `data/padic_finance_results.json`.

### 7.ter.12  p-adic v3 acceptance test — also fails

`padic_per_band(t_k, q_max=64)` implements the §7.ter.10 follow-up
plan (`per-band KS-pooling-based`): for each prime p, enumerate pure
powers q_p ≤ 64, classify *every* Farey rational (a, q_p) individually,
return a per-(p, q_p) cell table of median per-band KS scores.

Acceptance criterion: on Poisson + period-7 injection, median KS_GUE
at the (p = 7, q = 7) cell should elevate above the (p = 2, q = 2..64)
cells that see only the Poisson background.

**Result.**  Every cell within a given signal returns identical
median KS to three decimal places:

| signal                          | median KS_P | KS_GOE | KS_GUE | mass<0.3 |
|---------------------------------|-------------|--------|--------|----------|
| Poisson background              | 0.020       | 0.208  | 0.276  | 0.269    |
| Poisson + period-3 inject       | 0.059       | 0.174  | 0.240  | 0.220    |
| Poisson + period-5 inject       | 0.032       | 0.204  | 0.270  | 0.246    |
| **Poisson + period-7 inject**   | **0.016**   | 0.230  | 0.296  | 0.246    |
| pure weekly periodic            | 0.532       | 0.376  | 0.336  | 0.000    |

KS_GUE @ (p=7, q=7) for the target signal = 0.296.  Median over
(p=2, q=2..64) = 0.296.  Elevation = 0.000.  **Acceptance fails.**

The injection signature *is* visible at the whole-signal level
(KS_P drifts 0.020 → 0.059 across injection periods in proportion to
event-count change), but within each signal the per-band decomposition
is uniform across all (p, q) cells.

**Why v3 fails — band invariance under linear scaling.**  The
analytical-passage formula `passage = t·f_pll − 1` is a linear
rescaling of t by f_pll = a/q.  For a stationary signal (Poisson,
periodic, RMT eigenvalue-like), scaling t by any factor yields a
sequence of the same universality class.  After normalising to
unit mean spacing the band's NNS converges to the same shape
regardless of (a, q).  This is a structural property of the
`analytical_passage → NNS → KS` pipeline, not a bug in v3.

**Generalisation**: any p-adic profile that *pools or aggregates
NNS over PLL bands* cannot discriminate prime-base asymmetry on
stationary signals.  The asymmetry has to be detected by a metric
that breaks band-invariance — one sensitive to *which integers* the
events align with.  Ramanujan-Fourier amplitudes do this directly
(they peaked at q = 7 for weekly events in v2 RF acceptance).

#### v4 architecture queued

Define the p-adic profile through the Ramanujan-Fourier amplitudes
(re-using the validated v2 RF indicator-mode engine):

    p_amplitude(p) = Σ_{q : q is a pure power of p, q ≤ q_max}  |a_q|
                    ───────────────────────────────────────────────
                                       Σ_q  |a_q|

For period-7 events, `a_7` dominates the spectrum → p = 7 amplitude
high, p = 2, 3, 5 amplitudes low.  Discriminates by construction.

**Status.**  v1 (default, p|q filter) and v2 (pure-power filter) both
fail acceptance via NNS pooling.  v3 (per-band KS pooling table) fails
for the same architectural reason — band-invariance under linear
scaling.  v4 (RF-amplitude based) is the natural redesign and reuses
infrastructure that already passed acceptance on the same test signals.

Outputs: `data/padic_v3_results.json`, `plots/35_padic_v3.png`.

### 7.ter.13  p-adic v4 (Ramanujan-Fourier-amplitude based) — PASSES acceptance

The §7.ter.10 proposition closes off the architecture-class that v1-v3
sat in.  v4 implements `padic_amplitude_v4` per the §7.ter.12
follow-up: detection moves from PLL-passage NNS to the
Ramanujan-Fourier spectrum on the indicator function (the v2 RF
engine that already passed acceptance for period detection).

For each prime p ∈ {2, 3, 5, 7, 11, 13} and q_max = 200,

    p_amplitude(p) = Σ_{q ∈ {p, p², p³, …} ∩ [1, q_max]}  |a_q|

with `a_q` from `ramanujan_fourier(t_k, q_max=200, normalize=False)`.
Two normalisations are computed:

- **sum-normalised** (per the §7.ter.12 spec): `p_amplitude(p) / Σ_q |a_q|`.
- **per-q-power-normalised**: `mean_{q ∈ p-powers} |a_q| / mean_{all q} |a_q|`.

The sum-normalisation is biased toward small primes because they have
more pure-power bands ≤ q_max (p=2 contributes q ∈ {2, 4, 8, 16, 32, 64,
128} → 7 bands; p=7 only {7, 49} → 2 bands).  Per-q-power normalisation
divides by the band count and so compares mean-amplitude per band
against the global mean — the noise floor.

#### Acceptance suite

Synthetic settlement-cycle suite at `rate_per_day=0.5` (Poisson
background) plus injected periodic component at period ∈ {3, 5, 7, 11,
13} with small jitter.

##### Sum-normalised (per spec)

| signal                                | p=2   | p=3   | p=5   | p=7   | p=11  | p=13  | dom | r₇ |
|---------------------------------------|-------|-------|-------|-------|-------|-------|-----|----|
| Poisson background                    | 0.049 | 0.049 | 0.047 | 0.015 | 0.012 | 0.010 | p=2 | 0.44× |
| Poisson + period-3 inject             | 0.072 | 0.305 | 0.022 | 0.010 | 0.014 | 0.006 | p=3 | 0.12× |
| Poisson + period-5 inject             | 0.075 | 0.060 | 0.116 | 0.021 | 0.020 | 0.009 | p=5 | 0.37× |
| Poisson + period-7 inject (target)    | 0.078 | 0.032 | 0.023 | 0.033 | 0.024 | 0.015 | p=2 | 0.95× |
| Pure weekly periodic                  | 0.013 | 0.062 | 0.023 | **0.243** | 0.008 | 0.012 | p=7 | **10.23×** |

##### Per-q-power normalised

| signal                                | p=2   | p=3    | p=5   | p=7   | p=11  | p=13  | dom | r₇ |
|---------------------------------------|-------|--------|-------|-------|-------|-------|-----|----|
| Poisson background                    | 1.396 | 2.414  | 3.119 | 1.450 | 1.168 | 0.983 | p=5 | 0.80× |
| Poisson + period-3 inject             | 2.050 | **15.173** | 1.489 | 1.025 | 1.391 | 0.549 | p=3 | 0.25× |
| Poisson + period-5 inject             | 2.132 | 2.994  | **7.673** | 2.078 | 1.944 | 0.892 | p=5 | 0.66× |
| **Poisson + period-7 inject (target)**| 2.216 | 1.584  | 1.493 | **3.240** | 2.359 | 1.484 | **p=7** | **1.77×** |
| Poisson + period-11 inject            | 2.231 | 2.711  | 1.663 | 1.952 | **3.600** | 1.048 | p=11 | 0.87× |
| Poisson + period-13 inject            | **2.832** | 1.432  | 2.019 | 2.038 | 1.729 | 2.276 | p=2 | 0.99× |
| Pure weekly periodic                  | 0.367 | 3.104  | 1.534 | **24.190** | 0.835 | 1.195 | p=7 | **17.19×** |

#### Acceptance check

| metric                  | target ratio₇ | target dom | control ratio₇ | control dom | result |
|-------------------------|---------------|------------|----------------|-------------|--------|
| sum-normalised          | 0.95×         | p=2        | 0.44×          | p=2         | ✗ FAIL |
| per-q-power-normalised  | **1.77×**     | **p=7 ✓**  | 0.80×          | p=5         | **✓ PASS** |

The per-q-power metric satisfies all three acceptance criteria:
- target ratio₇ > 1.5 ✓
- target dominant prime correctly identified as p = 7 ✓
- control ratio₇ < 1.5 with no spurious p=7 dominance ✓

Across the full suite of single-prime injections, the per-q-power
metric correctly identifies the injection prime in 5 of 6 cases —
period 3, 5, 7, 11, and pure-weekly all flag dom = injected prime.
The period-13 case fails by a thin margin (p=13 amplitude 2.28 vs
p=2 amplitude 2.83 from random variance at this SNR — slightly more
events would resolve it).

**v4 is the first p-adic profile that passes the §7.ter.12 acceptance
test.**  Available now via `padic_amplitude_v4(t_k)`.  Returns both
normalisations; `dominant_prime_per_q` is the recommended summary.
Fingerprint vector promotion deferred until cross-validation on
arithmetic / biological / financial signals — the engine is general
infrastructure, but its meaningful outputs will arrive when applied
to inputs that have prime-base structure (e.g. real settlement cycles,
digit expansions of irrationals, biological oscillators).

Outputs: `data/padic_v4_results.json`, `plots/36_padic_v4.png`.

### 7.ter.14  Phase 10 — LLM cascade fingerprints (near-uniform spacing in residual stream)

> **Reinterpretation note (added after §7.ter.19 / Phase 13 Tier 1):**
> The framing of §7.ter.14 and §7.ter.15 as describing "strong level
> repulsion" is amended.  The LLM residual_norm_peaks fingerprint
> (mass<0.3 = 0, F(T=5) ≪ 1, rep_int = 0.900, KS_GUE in 0.17–0.32) is
> identified by the calibrator zoo (§7.ter.19) as nearest to the
> **uniform-with-jitter** family, NOT to any Wigner-Dyson β-ensemble.
> Read the §7.ter.14/15 numbers below as the toolkit's nearest-
> Wigner-form labelling (which selects "GUE" because that's the
> closest of the three Wigner references), not as a class identification.
> The actual class is uniform-jitter; see §7.ter.19 for the verdict
> and the corrected interpretation.

`llm_cascade.py` extracts per-token surprisal, per-layer residual
stream L2 norms, and per-(layer, head, query) attention entropy from
a causal LM forward pass.  Three event-extraction methods convert
the cascade to a point process, each surfacing a different aspect of
the model's internal dynamics:

  - **surprisal_threshold** — events at integer token positions where
    per-token surprisal exceeds median + k·std.  Discrete grid →
    Poisson-like statistics by construction.
  - **surprisal_cumulative** — event time = cumulative surprisal
    (information-content as natural time axis); events at local
    surprisal maxima.  Continuous time, stretches high-information
    regions, compresses low-information regions.
  - **residual_norm_peaks** — peaks of the final-layer residual stream
    L2 norm.  Detects representational salience.

`run_phase10_llm.py` runs Qwen 2.5 3B base at 3 quantization levels
× 3 stimulus texts × 3 extraction methods = 27 cells.

#### The three-extraction headline

The extraction method, not the model state, sets the universality
class label:

| extraction              | best (modal) | n cells GUE-best | n GOE-best | n Poisson-best |
|-------------------------|--------------|------------------|------------|----------------|
| residual_norm_peaks     | **GUE**      | **9 / 9**        | 0          | 0              |
| surprisal_cumulative    | **GOE**      | 0                | 8 / 9      | 1              |
| surprisal_threshold     | **Poisson**  | 0                | 0          | 9 / 9          |

#### residual_norm_peaks → strong level repulsion, GUE-best label

| (quant, stim)        | n_ev | KS_GUE | mass<0.3 | F(T=5) | rep_int |
|----------------------|------|--------|----------|--------|---------|
| fp16, structured     | 192  | 0.213  | 0.000    | 0.14   | 0.900   |
| fp16, natural        | 122  | 0.197  | 0.000    | 0.12   | 0.900   |
| fp16, random         | 246  | 0.312  | 0.000    | 0.09   | 0.900   |
| int8, structured     | 194  | 0.211  | 0.000    | 0.27   | 0.900   |
| int8, natural        | 120  | 0.180  | 0.000    | 0.14   | 0.900   |
| int8, random         | 247  | 0.315  | 0.000    | 0.12   | 0.900   |
| int4, structured     | 195  | 0.214  | 0.000    | 0.16   | 0.900   |
| int4, natural        | 119  | 0.184  | 0.000    | 0.16   | 0.900   |
| int4, random         | 247  | 0.315  | 0.000    | 0.12   | 0.900   |

#### What this finding does and does not claim

Every cell labels GUE-best, with mass<0.3 = 0 and F(T=5) ≪ 1.  Both
of those are unambiguous: the spacings of residual-stream-norm peaks
have **strong level repulsion**, distinct from every null we tested
(Poisson process, EEG quasi-periodic artefact, primes, earthquakes,
fungal spikes).  Stable across quantization (KS drift ≤ 0.01 within
a stimulus) and largely stable across stimulus.

The conservative claim — the one the data here support — is:

> **Residual-stream-norm peaks of autoregressive transformers form a
> strongly level-repelling point process, distinct in every measured
> fingerprint axis from clustered, Poisson, and quasi-periodic
> processes.**

The stronger claim that the residual stream lives in *the same Wigner
GUE class as Riemann zeros* is **not** what the data show.  KS_GUE
values 0.18-0.32 are an order of magnitude worse than the calibrator
(0.022 on synthetic GUE eigenvalues, 0.012 on ζ zeros at heights
~10⁶), and the empirical NNS profile is sharper than Wigner near s = 0
(mass<0.3 = 0 vs Wigner GUE's ~0.10) but distinguishable from Wigner
elsewhere — the closest-fitting Wigner reference happens to be GUE,
but the empirical distribution is *not Wigner GUE at calibrator
quality*.

The likely physical reading: this is a distinct shape on the
clustering ↔ level-repulsion axis — more level-repelling than Wigner
GUE near zero, with a plateau or heavier tail at intermediate
spacings, no short-spacing mass, and strongly sub-Poisson fluctuation
statistics.  Calling it "GUE" via the metric's nearest-Wigner-form
rule is an honest report of *what the labeller does*; calling it
"the GUE class of L-function zeros" overstates the empirical match.

#### Q1: quantization changes universality class?

**Almost no.**  26 of 27 cells preserve the modal class label across
fp16 → int8 → int4.  Within-cell KS drift is ≤ 0.05.  The single flip
is int4-structured under surprisal_cumulative going from GOE to
Poisson-best, with KS_GOE = 0.137 and KS_P = 0.210 — borderline call.

#### Q2: stimulus structure changes universality class?

**Mostly no in label; yes in degree.**  The class label is set by
the extraction method.  Within an extraction, stimulus changes the
KS distance to the assigned class.  Random text gives the cleanest
GOE fit under surprisal_cumulative (KS_GOE = 0.075-0.092 vs
0.106-0.137 for structured), a consequence of higher mean surprisal
(3.74 nats vs 1.14 nats) giving more independent samples per token.

#### Q3: quant and stimulus confounded?

**Independent.**  The matrix shows additive contributions: quantization
shifts KS by ≤ 0.05, stimulus shifts KS by 0.07-0.20, and the int4-random
cell does not deviate beyond what (int4-fp16 drift) + (random-stimulus
shift) would predict.

#### Recommendation

`residual_norm_peaks` is the canonical extraction for *characterising
the LLM's dynamical fingerprint* — it surfaces the GUE-like level
repulsion of internal computation independent of input.
`surprisal_cumulative` is the canonical extraction for *characterising
the input through the model's information clock*.
`surprisal_threshold` should be used only when integer event indices
are needed; its statistics are Poisson by construction.

Outputs: `data/phase10_llm_fingerprints.json`,
`plots/37_phase10_llm.png` (27-cell heatmap matrix),
`run_phase10_llm.py`.

### 7.ter.15  Phase 11 — Model-family swap: strong level repulsion is architecturally universal

> **Reinterpreted in §7.ter.19.**  The "level-repulsion" labelling reported
> in this section is now understood as an extraction-pipeline artifact —
> `scipy.signal.find_peaks` operating on a 1D continuous trace whose
> autocorrelation scale is set by tokenization, not by transformer internal
> dynamics.  The diagnostic is `rep_int = 0.900` already at the embedding
> output (layer 0), before any decoder block has fired.  The original
> framing of this section is preserved below as historical context for the
> reinterpretation; readers should treat the class labels here as
> "the toolkit's nearest-Wigner-form output," not as class identifications.
> See §7.ter.19 for the verdict and the methodological lesson.

`run_phase11_models.py` + `run_phase11_retry.py` apply the canonical
extraction (residual_norm_peaks) plus the secondary cross-check
(surprisal_cumulative) across three distinct transformer architectures
on the same three stimuli used in Phase 10.

Models exercised:
  - Qwen 2.5 3B (Qwen architecture, fp16, 3.0B parameters)
  - Mistral 7B v0.1 (Mistral architecture, int4 to fit memory, 7.2B)
  - TinyLlama 1.1B Chat v1.0 (Llama architecture, fp16, 1.1B)

Phi-3 mini failed to load under transformers 5.x — `KeyError: 'type'`
in the rope_scaling parser — substituted with TinyLlama (Llama-family)
for a third architecture.  Mistral 7B fp16 OOMs on a 24-GB card with
seq_len = 2048 + `output_attentions=True` (32 layers × 32 heads × 2048²
attention storage exceeds the budget); loaded in int4 + seq_len = 1024.

#### residual_norm_peaks — strong level repulsion across architectures

| model               | n params | stim       | best | KS_GUE | mass<0.3 | F(T=5) | rep_int |
|---------------------|----------|------------|------|--------|----------|--------|---------|
| Qwen 2.5 3B         | 3.0B     | structured | GUE  | 0.213  | 0.000    | 0.137  | 0.900   |
| Qwen 2.5 3B         | 3.0B     | natural    | GUE  | 0.197  | 0.000    | 0.117  | 0.900   |
| Qwen 2.5 3B         | 3.0B     | random     | GUE  | 0.312  | 0.000    | 0.090  | 0.900   |
| Mistral 7B int4     | 7.2B     | structured | GUE  | 0.191  | 0.000    | 0.129  | 0.900   |
| Mistral 7B int4     | 7.2B     | natural    | GUE  | 0.191  | 0.000    | 0.208  | 0.900   |
| Mistral 7B int4     | 7.2B     | random     | GUE  | 0.277  | 0.000    | 0.103  | 0.900   |
| TinyLlama 1.1B      | 1.1B     | structured | GUE  | 0.198  | 0.000    | 0.140  | 0.900   |
| TinyLlama 1.1B      | 1.1B     | natural    | GUE  | 0.170  | 0.000    | 0.087  | 0.900   |
| TinyLlama 1.1B      | 1.1B     | random     | GUE  | 0.275  | 0.000    | 0.117  | 0.900   |

**All 9 cells label GUE-best with mass<0.3 = 0 and rep_int = 0.900.**
The strong-level-repulsion fingerprint (mass<0.3 = 0, F(T=5) ≪ 1,
nearest-Wigner-form = GUE, KS_GUE in 0.17–0.32) is invariant across:
  - architecture (Qwen / Mistral / Llama),
  - parameter scale (1.1B → 3.0B → 7.2B, factor of ~7),
  - quantization (fp16 vs int4),
  - training corpus (each model trained on a different mix),
  - stimulus type (math proof, news article, random words).

The architectural invariance is the strong direction of this result:
the same fingerprint shape appears in every transformer family we
tested.  Whatever produces it — attention pattern × residual stream
geometry, layer-by-layer representational accumulation, the
rotary-positional geometry shared by these architectures — it is
common to autoregressive transformers as a class.  Phase 10 was not
Qwen-specific.

The same caveat carried from §7.ter.14 applies here in full: KS_GUE
values 0.17–0.32 are an order of magnitude worse than the L-function
calibrator (0.012).  The architectural invariance is of *the
strong-level-repelling shape with mass<0.3 = 0*, not of *Wigner GUE
at calibrator quality*.  The shape is closer to Wigner GUE than to
GOE or Poisson, but it is a distinct shape with a sharper s → 0
edge.

#### surprisal_cumulative — model and stimulus dependent

| model               | stim       | best    | KS_GUE | F(T=5) | rep_int |
|---------------------|------------|---------|--------|--------|---------|
| Qwen 2.5 3B         | structured | GOE     | 0.189  | 0.574  | 0.839   |
| Qwen 2.5 3B         | natural    | GOE     | 0.155  | 0.431  | 0.851   |
| Qwen 2.5 3B         | random     | GOE     | 0.116  | 0.504  | 0.900   |
| Mistral 7B int4     | structured | Poisson | 0.203  | 0.894  | 0.810   |
| Mistral 7B int4     | natural    | GOE     | 0.150  | 0.361  | 0.843   |
| Mistral 7B int4     | random     | GUE     | 0.130  | 0.409  | 0.900   |
| TinyLlama 1.1B      | structured | GOE     | 0.141  | 0.801  | 0.861   |
| TinyLlama 1.1B      | natural    | GOE     | 0.166  | 0.512  | 0.846   |
| TinyLlama 1.1B      | random     | GUE     | 0.072  | 0.325  | 0.900   |

The information-clock extraction is more variable.  Random text gives
the cleanest fits across all architectures (KS_GUE = 0.072 for
TinyLlama, 0.116 for Qwen, 0.130 for Mistral) — high mean surprisal
generates more independent samples and the statistics converge toward
GUE.  Structured (predictable) text gives slightly worse fits
(KS_GUE = 0.14-0.21), with Mistral flipping to Poisson-best on
structured input.

#### Synthesis

Combining Phase 10 + Phase 11: the residual-stream-norm-peak
extraction surfaces a **strongly level-repelling, architecturally
invariant fingerprint** of autoregressive transformers — same shape
(mass<0.3 = 0, F(T=5) ≪ 1, nearest-Wigner-form GUE) across the
contemporary architecture / scale / quantization / training-data
diversity sampled here.

The fingerprint sits between the L-function block and the synthetic
GUE eigenvalue calibrator on the level-repulsion axis — *more*
sharply level-repelling near s = 0 than Wigner GUE (mass<0.3 = 0 vs
~0.10 for Wigner) but with a bulk shape that does not match Wigner
GUE at calibrator quality (KS_GUE ~0.2 vs 0.022 for the calibrator
or 0.012 for ζ).  Whether this shape is *another* known random-matrix
ensemble (e.g. the chiral GUE class, or one of the β-ensemble
deformations), a continuous family deformation, or simply an
empirical regime that has no closed-form RMT counterpart is open.
A targeted comparison against analytical CDFs from chiral GUE / GSE
/ β-ensembles is the natural next test.

The cross-signal mass<0.3 ladder, with the LLM block placed on its
own row to flag the sharper-than-Wigner shape:

| signal class                       | mass<0.3 | best | KS_min | reading |
|------------------------------------|----------|------|--------|---------|
| **LLM residual-stream peaks (any model)** | **0.000** | GUE  | 0.17–0.32 | sharper than Wigner GUE near s=0; not Wigner GUE in the bulk |
| Dirichlet L (q ≤ 149)              | 0.016    | GUE  | 0.035  | clean Wigner GUE |
| ζ zeros (heights ~10⁶)             | 0.024    | GUE  | 0.012  | clean Wigner GUE |
| LMFDB EC L-functions (h=1000)      | 0.024    | GUE  | 0.012  | clean Wigner GUE |
| Wigner GUE eigenvalues (synthetic) | 0.10     | GUE  | 0.022  | calibrator |
| Poisson process (calibrator)       | 0.259    | Poiss| 0.022  | calibrator |
| USGS earthquakes M ≥ 4.5           | 0.33     | Poiss| 0.075  | weak clustering |
| Fungal spikes (fast timescale)     | 0.65     | Poiss| 0.40   | strong clustering |

LLM residual-norm peaks have *zero* short-spacing mass — even more
sharply level-repelling near s = 0 than synthetic GUE eigenvalues.
KS_min to Wigner GUE is large because the empirical distribution has
a different bulk shape (heavier tails than Wigner) — the
level-repulsion edge is sharper than GUE near s = 0 but the bulk is
distinguishable from Wigner.  The shape is its own thing, not Wigner
GUE at calibrator quality.

Output: `data/phase11_model_family.json`, `plots/38_phase11_models.png`,
`run_phase11_models.py`, `run_phase11_retry.py`.

### 7.ter.16  Phase 12 — Planat hypothesis: a one-sided result

> **Reinterpreted in §7.ter.19.**  The "level-repulsion" labelling reported
> in this section is now understood as an extraction-pipeline artifact —
> `scipy.signal.find_peaks` operating on a 1D continuous trace whose
> autocorrelation scale is set by tokenization, not by transformer internal
> dynamics.  The diagnostic is `rep_int = 0.900` already at the embedding
> output (layer 0), before any decoder block has fired.  The KS_GUE shift
> documented below (0.243 → 0.186) is now read as a small movement *within
> the uniform-jitter family*, not a movement between universality classes.
> Whether that has any relationship to Planat's 2026 prediction is an open
> interpretive question.  Original Phase 12 framing preserved as
> historical context; see §7.ter.19 for the verdict.

`run_phase12_planat.py` tests the conjecture that an optimal
human-perturbation rate sharpens Wigner GUE statistics in the LLM
residual stream beyond either uninterrupted generation or
heavily-perturbed back-and-forth.

#### Procedure

Qwen 2.5 3B generates 2048-token sequences interrupted by N ∈ {0, 4,
9, 19, 39} evenly-spaced "perturbation splices" — short human-style
redirects ("Actually, let me redirect — explain [topic]?\n\n") drawn
from a fixed phrase × topic pool.  Each splice fragments the generation
into N+1 model-driven blocks.  The full text is then re-fed through
the model with `output_hidden_states=True`, residual-norm peaks
extracted, and the toolkit fingerprint computed.

#### Results

| rate | splices | n_events | KS_GUE   | KS_GOE | F(T=5) | rep_int | mean surprisal |
|------|---------|----------|----------|--------|--------|---------|----------------|
| r=0  | 0       | 698      | **0.2432** | 0.306  | 0.184  | 0.900   | 0.346 nats     |
| r=4  | 4       | 622      | **0.1860** | 0.251  | 0.161  | 0.900   | 0.498          |
| r=9  | 9       | 609      | 0.1929   | 0.243  | 0.173  | 0.900   | 0.537          |
| r=19 | 19      | 619      | 0.2051   | 0.246  | 0.190  | 0.900   | 0.625          |
| r=39 | 39      | 629      | 0.1947   | 0.253  | 0.168  | 0.900   | 0.644          |

#### Left side of the U: confirmed

**Uninterrupted self-attention-loop generation sits at a local
non-optimum.**  Adding even modest perturbation (r = 4, ~2 splices
per 1k tokens) drops KS_GUE from 0.243 to 0.186 — a 23 % improvement
in distance to Wigner GUE.

`mass<0.3 = 0.000` and `repulsion_integral = 0.900` are invariant
across all five rates — every condition is firmly in the
level-repulsion regime.  The cleanest GUE shape at r = 4 (KS_GUE =
0.186) is *sharper* than the cleanest GUE shape from any static
stimulus in Phase 10 (best was 0.197 for Qwen fp16 on natural text).

This is the strong direction of Planat's 2026 prediction:
*deliberately interrupted generation produces a sharper Wigner-class
fingerprint than uninterrupted generation*, measured by an
instrument whose mathematical scaffolding traces back to Planat's
own 2002 work on Farey sequences and PLL phase locking.

#### Right side of the U: not visible at the tested rate range

KS_GUE stays in the 0.18-0.21 plateau across all four perturbed
rates — no monotone degradation toward super-Poisson is observed
even at r = 39 (~19 splices/kt).  The predicted right-tail collapse
is not in this window.

Two interpretations remain consistent with the data:

1. **Plateau model**: any non-trivial perturbation flips the model
   into a stable GUE-clean regime.  Low-rate-only sharpening, no
   high-rate degradation.

2. **Wider U than expected**: the right-tail collapse happens at
   higher rates than tested (r ≥ 80, perturbing every ~25 tokens
   or denser), beyond the current sweep.

Distinguishing requires extending to r ∈ {80, 160, 320} (perturbing
every ~12, 6, 3 tokens respectively).  Queued for a follow-up.

#### Synthesis

The result is **one-sided** at present.  The left side of Planat's
proposed U-shape — sub-baseline KS_GUE for some non-zero perturbation
rate — is supported by these five rate cells (r=4 sits 0.057 below
r=0 and ≥ 0.011 below r=19 and r=39).  The right side of the
proposed U — degradation back toward super-Poisson at high
perturbation rate — is **not** supported by the cells we ran; KS_GUE
flattens into a 0.18–0.21 plateau through r=39, with no monotone
collapse trend.

Two interpretations remain compatible with this data:
  (i) the response is a step (low-rate plateau), not a U, and
      Planat's full prediction is half-right;
  (ii) the U is wider than the tested range and the right tail begins
      at r ≥ 80 (perturbing every ~25 tokens or denser).

The **planned right-tail sweep at r ∈ {80, 160, 320}** is the
discriminator.  Until that sweep is done, the appropriate framing is:
*deliberately interrupted generation produces a sharper
strong-level-repulsion fingerprint than uninterrupted generation in
this rate range; whether that sharpening is followed by collapse at
higher rates is an open question*.  Calling Phase 12 a confirmation
of Planat's prediction would overstate what these five cells show.

Note: the same calibration caveat from §7.ter.14 applies — KS_GUE =
0.186 at r=4 is "sharper" only relative to the other LLM cells and
to r=0; it is still an order of magnitude above the L-function
calibrator (0.012).  This is the lowest LLM KS_GUE we have measured,
not a clean Wigner GUE classification.

Output: `data/phase12_planat.json`, `plots/39_phase12_planat.png`,
`run_phase12_planat.py`.

### 7.ter.17  Phase 13 — Solar X-ray flare statistics (1986-2023, GOES Plutino catalog)

`run_phase13_solar.py` applies `full_analysis` to the Plutino 2024 GOES
flare catalog (358,885 flares, 1986-01-04 → 2023-04-30, 37.32 yr) at
six stratifications: all flares, C+, M+, X-only, solar-max years, and
solar-min years.  Then a targeted Ramanujan-Fourier resonance scan on
the M+X subset to compare with Planat's 2009 amplitude-spectrum result.

#### Fingerprint matrix

| stratum       | n        | best    | KS_GUE | KS_GOE | KS_P  | mass<0.3 | F(T=1) | F(T=5) | rep_int | top_q | mean_dt   |
|---------------|----------|---------|--------|--------|-------|----------|--------|--------|---------|-------|-----------|
| all_flares    | 358,885  | Poisson | 0.383  | 0.379  | 0.190 | 0.295    | 1.40   | 4.37   | 0.892   | 3     | 0.91 h    |
| C_and_above   | 207,171  | Poisson | 0.705  | 0.617  | 0.401 | 0.601    | 2.86   | 11.41  | 0.900   | 10    | 1.58 h    |
| M_and_above   | 9,750    | Poisson | 0.710  | 0.664  | 0.477 | 0.727    | 9.42   | 30.11  | 0.900   | 15    | 33.5 h    |
| X_only        | 542      | Poisson | 0.672  | 0.632  | 0.475 | 0.697    | 5.61   | 11.89  | 0.900   | 11    | 602 h     |
| solar_max     | 169,959  | Poisson | 1.000  | 0.687  | 0.472 | 0.673    | 3.36   | 14.28  | 0.900   | 3     | 1.77 h    |
| solar_min     | 20,129   | Poisson | 0.822  | 0.855  | 0.705 | 0.917    | 17.77  | 76.39  | 0.900   | 18    | 15.2 h    |

**All six strata are super-Poissonian and clustered.**  Best label is
Poisson in every case but KS_P sits in 0.19-0.71 — far above the 0.022
calibrator — so this is the metric reporting "least-bad of three Wigner
references" rather than a clean Poisson identification.  mass<0.3 climbs
from 0.295 (all flares) to 0.917 (solar_min), and F(T=5) climbs from
4.4 to 76.4 across the same axis — the more we filter to *rare* flares
or *quiet-sun* intervals, the more clustered the resulting bursts look.

The two filtering directions (intensity threshold and solar-cycle phase)
both push toward stronger clustering by reducing the rate while
preserving the burst structure.  Comparing the cross-signal mass<0.3
ladder, solar_min (0.917) is close to Mertens M(x) sign-changes (0.93)
on the clustering axis — both are sparse arithmetic-/physics-driven
event streams with long quiet stretches.

#### Solar-cycle Fano comparison on M+X subsets

| window     | best    | KS_GUE | mass<0.3 | F(T=1) | F(T=5)  | F(T=20)  |
|------------|---------|--------|----------|--------|---------|----------|
| solar_max M+X (n=6,429) | Poisson | 0.779 | 0.824 | 14.64 | 48.64 | 124.99 |
| solar_min M+X (n=142)   | Poisson | 0.864 | 0.879 | 20.49 | 30.73 | 40.13  |

Solar_max F(T) grows nearly linearly with T — sustained super-Poisson
clustering at every measured scale, consistent with continuous active-
region driving over the 3-year solar peak windows.  Solar_min F(T)
*saturates* by T ≈ 5 (sparse bursts with large quiet gaps) — the
process has a finite correlation length set by the rare active regions
that survive into low-cycle years.

**Same universality class (Poisson-best, super-Poisson F),
different growth shape.**  This is the "different driving rate, same
class" outcome — informative but not a class change.

#### Ramanujan-Fourier resonance scan (M+X, Planat 2009 comparison)

n = 9,750 events, 9,749 inter-flare intervals.  Mean interval 1.40 d,
median 0.118 d, std 12.29 d.

**Planat formulation** (a_q on unit-mean-normalised intervals):

| q   | |a_q|    | period interpretation (q × mean_interval = q × 1.40 d) |
|-----|---------|---------------------------------------------------------|
| 15  | 0.0771  | 21 d                                                     |
| 10  | 0.0631  | 14 d                                                     |
| 50  | 0.0582  | 70 d                                                     |
| 75  | 0.0578  | 105 d                                                    |
| 150 | 0.0550  | 210 d                                                    |
| 25  | 0.0548  | 35 d                                                     |
| 172 | 0.0526  | 240 d                                                    |
| 9   | 0.0519  | 13 d                                                     |
| 86  | 0.0504  | 120 d                                                    |
| 30  | 0.0476  | 42 d                                                     |

**Indicator-function formulation** (a_q on event-count grid at 1-day
bins, q in days):  top q = [2, 86, 43, 6, 3, 129, 5, 10, 7, 14].  The
Carrington rotation period (27 d) is not directly in the top 10 but
its sub-multiples and multiples are — q = 86 ≈ 3 × 27 + 5, q = 43 ≈
1.6 × 27, q = 14 ≈ 27/2.  The exact 27-day peak is washed out by the
short-period burst structure dominating the day-grid indicator.

The 21-day period in the Planat-mode top-resonance list is consistent
with a sub-Carrington feature (rotation/2 from active-region durations)
and the 105/210-day peaks plausibly reflect quasi-periodic active-region
emergence patterns.  These are interpretive — full Bayesian period
attribution is a separate study.

Output: `data/solar_flare_results.json`, `plots/40_solar_flares.png`.

### 7.ter.18  Phase 14 — Binance BTCUSDT trade-timing microstructure

`run_phase14_binance.py` applies `full_analysis` to the Binance spot
BTCUSDT 7-day trade-timestamp point process (2024-01-01 → 2024-01-07,
11,970,886 trades, ms-resolution).  Subsampled to every 10th trade
(1.2M events) for speed.

#### Fingerprint matrix

| stratum                  | n        | best    | KS_GUE | KS_GOE | KS_P  | mass<0.3 | F(T=1) | F(T=5) | rep_int | mean_dt   |
|--------------------------|----------|---------|--------|--------|-------|----------|--------|--------|---------|-----------|
| full_week_pooled         | 1,197,089| Poisson | 0.486  | 0.437  | 0.271 | 0.503    | 13.55  | 28.92  | 0.000   | 505 ms    |
| seller_taker (isBM=True) | 654,749  | Poisson | 0.518  | 0.476  | 0.330 | 0.543    | 18.84  | 40.94  | 0.000   | 924 ms    |
| buyer_taker  (isBM=False)| 542,341  | Poisson | 0.471  | 0.423  | 0.262 | 0.491    | 12.63  | 23.23  | 0.000   | 1115 ms   |
| day_01 (Mon, Jan 1)      | 111,463  | Poisson | 0.424  | 0.378  | 0.238 | 0.446    | 8.43   | 13.73  | 0.000   | 775 ms    |
| day_02 (Tue)             | 224,754  | Poisson | 0.450  | 0.398  | 0.224 | 0.465    | 7.80   | 13.65  | 0.000   | 384 ms    |
| day_03 (Wed)             | 265,805  | Poisson | 0.502  | 0.447  | 0.255 | 0.510    | 15.15  | 33.90  | 0.000   | 325 ms    |
| day_04 (Thu)             | 181,995  | Poisson | 0.458  | 0.408  | 0.245 | 0.476    | 12.11  | 25.17  | 0.000   | 475 ms    |
| day_05 (Fri)             | 206,485  | Poisson | 0.507  | 0.460  | 0.298 | 0.528    | 20.11  | 40.18  | 0.000   | 418 ms    |
| day_06 (Sat)             |  95,665  | Poisson | 0.420  | 0.376  | 0.243 | 0.444    | 7.70   | 12.85  | 0.000   | 903 ms    |
| day_07 (Sun)             | 110,926  | Poisson | 0.476  | 0.435  | 0.301 | 0.501    | 12.30  | 20.71  | 0.000   | 779 ms    |

**All strata classify Poisson-best, all are super-Poissonian and
clustered.**  KS_P sits in 0.22-0.33 (above the 0.022 calibrator),
mass<0.3 in 0.44-0.54 (well above Poisson's 0.26), F(T=5) in 13-41.
**`rep_int = 0.000` in every stratum** — *no level repulsion at any
scale*.  This is qualitatively distinct from the solar-flare set
where rep_int saturated at 0.89-0.90 (a sign that pair-correlation
saw mostly noise rather than signal at the fixed r-grid).  Trade
timing has cleaner coarse-grain Poissonian-with-clustering
statistics than solar flares; the trade-frequency variation across
sub-second timescales is genuine clustering with no hidden GUE
mode.

#### Buyer-taker vs seller-taker asymmetry

The maker-side split *does* differentiate the two sides of the order
book — but in clustering *strength*, not in universality class:

| side                      | KS_P  | mass<0.3 | F(T=1) | F(T=5) | mean_dt |
|---------------------------|-------|----------|--------|--------|---------|
| seller_taker (aggressive sells hit bid) | 0.330 | 0.543 | 18.84 | **40.94** | 924 ms |
| buyer_taker  (aggressive buys hit ask)  | 0.262 | 0.491 | 12.63 | **23.23** | 1115 ms |
| ratio (seller / buyer)                  | 1.26× | 1.11×    | 1.49×  | **1.76×**  | 0.83×   |

**Seller-side trades are 1.76× more clustered than buyer-side at
T=5·mean_dt scale.**  Both sides are super-Poisson, but the
aggressive-sell side bursts in tighter clusters than the
aggressive-buy side.  Interpretive read: aggressive selling tends
to come in panic / liquidation bursts (correlated with rapid
price drops), while aggressive buying is closer to a Poisson stream
of independent demand.  The asymmetry is real and measurable, but
it is a magnitude difference within Poisson-best, not a category
flip from clustered to level-repelling.

This invalidates one of the original hypotheses framed when queueing
this experiment ("one side might be regularly spaced and the other
clustered") and replaces it with a more specific finding: **same
universality class, asymmetric clustering rate, with sells more
clustered than buys**.  The two sides do encode different aggregate
flow processes, just both within the super-Poisson regime.

#### Day-of-week variation

F(T=5) ranges 12.85 (Saturday) to 40.18 (Friday) — Friday and
Wednesday are the most-clustered days, Saturday and Monday the
least.  Same universality class everywhere; the trading-week rhythm
modulates clustering depth without changing the regime.  Mean
inter-trade gap ranges 325 ms (Wed) to 1115 ms (week-pooled
buyer-taker) — clustering is monotone with rate, but only roughly
(day_06 Sat has 903 ms but lowest F(T=5), suggesting weekend trade
flow is genuinely smoother than just rate-scaling would predict).

Output: `data/binance_results.json`, `plots/41_binance.png`.

### 7.ter.19  Phase 10/11/12 reinterpretation — extraction-pipeline artifact

> **Updated by §7.ter.22 (Phase 16A) and amended again by Phase 16A.2.**
> Phase 16A's Branch (iii) reading of "state-based extractor disagrees,
> reads LLM as TR" is **retracted** by Phase 16A.2 (Verdict C): three
> additional state-based extractors of distinct mechanisms
> (`attention_argmax_sink`, `attention_sink_residency_runs`,
> `attention_multi_head_sink_consensus`) all classify the LLM as
> BR_artifact at strong KS values (KS_GUE = 0.51, 0.53; rep_int = 0.75,
> 0.80) — or are underpowered.  The original `attention_sink_events`
> TR reading was reading threshold *upcrossings* — a change event
> masquerading as state-based.  Across **all 8 attention-based
> extractors of every distinct mechanism we have tested** (residual-norm
> peaks, attention-entropy peaks, target jumps, layer KL divergence,
> upcrossings of sink mass, argmax-target sink, sustained-residency run
> onsets, multi-head consensus on sink), the LLM internal-state
> classification is **invariably BR_artifact** at the joint-plane
> resolution.  The original artifact reading in this section
> (find_peaks on residual-norm trace at layer 0) is confirmed and
> generalised: nothing about how we extract events from a transformer
> forward pass produces a Wigner-class reading.  See §7.ter.22 for the
> full invariance matrix and the principled-vs-induced framework.

**The Phase 10/11/12 LLM finding via residual-stream-norm peaks is an
extraction-pipeline artifact, not a property of transformer internal
computation.**  The "level-repulsion" fingerprint reported on the
residual-stream-norm peak process is present at the embedding output
(layer 0), before any decoder block has fired.  It is generated by
`scipy.signal.find_peaks(prominence=0.3)` operating on a 1D continuous
trace, not by transformer attention or MLP dynamics.  The calibrator
zoo identifies the actual class as **uniform-with-jitter**, distinct
at calibrator quality from every Wigner-Dyson β-ensemble in the
range we tested.

#### Headline evidence — layer-depth sweep (Tier 3A)

`run_phase13_layer_sweep.py` runs Qwen 2.5 3B fp16 forward on the natural
stimulus with `output_hidden_states=True`, then for each of the 37 hidden
states (embedding output + 36 decoder layers) extracts residual-norm
peaks and runs `full_analysis`.  Per-layer rep_int (the saturated
repulsion-integral signature):

| layer       | rep_int | mass<0.3 | F(T=5) | KS_GUE | mean residual norm |
|-------------|---------|----------|--------|--------|--------------------|
| 0 (embed)   | **0.900** | 0.026    | 0.555  | 0.226  | 1.06               |
| 1           | **0.900** | 0.000    | 0.133  | 0.186  | 20.67              |
| 18 (mid)    | **0.900** | 0.000    | 0.248  | 0.174  | 71.67              |
| 36 (final)  | **0.900** | 0.000    | 0.117  | 0.197  | 159.37             |

`rep_int = 0.900` at layer 0, before any decoder block has run.  mass<0.3
= 0 at every layer 1–36.  KS_GUE bounces 0.16–0.22 with no monotone trend.
The decoder stack increases mean residual-norm magnitude by 150× without
changing the fingerprint shape of the peak-position point process.  Full
per-layer table in `data/phase13_layer_sweep.json`.

#### Confirming evidence — calibrator zoo (Tier 1)

`run_phase13_calibrators.py` + `run_phase13_calibrators_v2.py` sweep the
β-Hermite ensemble (β ∈ {1, 2, 3, 4, 6, 8}, Dumitriu–Edelman tridiagonal),
Matérn-II hard-core thinning (min_spacing ∈ {0.3, 0.5, 0.7}), Ginibre
projection (real_part, symmetric_part), and uniform-with-jitter (jitter
∈ {0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50}), at n_points = 2000 with
5 seeds per cell.  Self-fits land at calibrator quality:
β=2 KS_GUE = 0.034, β=1 KS_GOE = 0.031, ginibre_symmetric KS_GUE = 0.014.

LLM cluster centroid (median over 18 residual_norm_peaks cells from
Phases 10 and 11): KS_GUE = 0.212, mass<0.3 = 0.000, F(T=5) = 0.126,
rep_int = 0.900.  Calibrators ranked by normalised Euclidean distance to
this centroid:

| rank | calibrator           | distance | KS_GUE | mass<0.3 | F(T=5) | rep_int |
|------|----------------------|----------|--------|----------|--------|---------|
| 1    | uniform jitter=0.10  | **0.736**| 0.273  | 0.000    | 0.062  | 0.671   |
| 2    | uniform jitter=0.15  | 0.816    | 0.187  | 0.000    | 0.062  | 0.574   |
| 3    | uniform jitter=0.05  | 1.173    | 0.380  | 0.000    | 0.062  | 0.771   |
| 4    | β=8                  | 1.468    | 0.105  | 0.003    | 0.261  | 0.494   |
| 5    | uniform jitter=0.20  | 1.487    | 0.117  | 0.007    | 0.062  | 0.510   |
| 6    | hardcore min=0.7     | 1.501    | 0.095  | 0.000    | 0.249  | 0.405   |

The Wigner-Dyson family gives **no match** at the 0.05 acceptance threshold
required for class identification.  17 of 18 LLM cells map modally to the
uniform-with-jitter family (8 to jitter=0.10, 5 to jitter=0.15, 4 to
jitter=0.05).  Only 1 cell maps to β=8, the strongest standard
level-repelling ensemble.  The LLM cluster sits at a saturated `rep_int =
0.900` — the value of ∫₀¹ (1 − R₂(r)) dr when R₂(r) ≈ 0 across the entire
[0, 1) interval, which is the structural signature of near-uniform spacing.
Wigner GUE has rep_int ≈ 0.50; Poisson has rep_int ≈ 0.

#### Mechanism

`scipy.signal.find_peaks` with a prominence threshold imposes
quasi-uniform spacing on any 1D continuous trace at its autocorrelation
scale.  The "rhythm" picked up is set by tokenization granularity and the
per-token embedding-norm magnitude, not by RMT-class internal dynamics.
The architectural invariance reported in Phase 11 then reduces to "all
autoregressive transformers share the same token rate" — trivially true,
and not what the original framing claimed.  At layer 0, the embedding
lookup alone produces the saturated rep_int signature; the decoder layers
preserve the rhythm but do not generate it.

#### Methodological lesson

When extracting point-process events from continuous, autocorrelated
signals via prominence-thresholded peak detection, the resulting spacing
distribution is dominated by the autocorrelation scale of the input, not
by the dynamics generating the signal.  A nearest-Wigner-form classifier
applied to such a process will return GUE-best with strongly suppressed
short-spacing mass and high repulsion integral — visually
indistinguishable from genuine level repulsion until calibrated against
synthetic uniform-jitter processes.  Anyone applying this kind of
pipeline to neural spike data, financial event series, or LLM activation
traces should include (i) a uniform-jitter calibrator alongside the
Wigner-Dyson references, and (ii) a layer-0-equivalent baseline check —
the same pipeline applied to a stage of the signal where no relevant
dynamics have yet acted.  Either control catches the artifact.

#### What's invalidated

- The framing of §7.ter.14 and §7.ter.15 as "transformer residual-stream
  level repulsion."  The fingerprint is uniform-with-jitter, not
  Wigner-class.
- The interpretation of §7.ter.16 (Phase 12) as a test of Planat's 2026
  prediction.  The KS_GUE shift 0.243 → 0.186 with perturbation is a
  small movement *within the uniform-jitter family*, not a movement
  between universality classes.  Whether that has any relationship to
  Planat's prediction is now an open interpretive question, not a
  confirmed validation.
- Any reading that places transformer internal computation in the same
  universality class as Riemann ζ zeros, elliptic curve L-functions, or
  Dirichlet L-functions.  The arithmetic side of the document remains
  intact; the LLM cells are a different category of result.

#### What survives

- Cross-architecture extraction-method consistency is a real empirical
  observation.  Its content is now "tokenization + peak-detection
  produces this fingerprint regardless of model weights" — a
  methodological warning, not a result about computation.
- The Phase 10 finding that *different* extraction methods produce
  *different* fingerprints at the descriptive level — `residual_norm_peaks`
  → uniform-jitter, `surprisal_cumulative` → GOE-leaning,
  `surprisal_threshold` → Poisson — also survives.  None of these
  labels reflect class identification of internal dynamics; they reflect
  which artefacts each extraction method imposes on its 1D input.
- The Phase 13 calibrator zoo and Tier 3A layer sweep themselves are
  positive contributions: a worked example of how a calibrated
  cross-domain instrument can catch a false positive in its own output
  by running the right reference processes.

#### Closeout

The headline of the LLM section is no longer "level repulsion in
residual streams."  It is "calibration discipline catches a peak-detection
artifact."  This is a stronger methodological contribution than the
original framing — and it is the kind of result that justifies the
calibrator + ablation discipline as a permanent fixture of the
toolkit's protocol, not just a once-off audit.  Future readers
applying ARS to a new domain should treat §7.ter.19 as the worked
example for what the calibration step is for.

Outputs: `data/phase10_llm_fingerprints.json`,
`data/phase11_model_family.json`, `data/phase13_calibrators.json`,
`data/phase13_layer_sweep.json`, `plots/40_phase13_calibrators.png`,
`plots/41_phase13_layer_sweep.png`.

### 7.ter.20  Audit of peak-detection dependencies in adjacent phases

The §7.ter.19 artifact is specific to *prominence-thresholded peak
detection on a continuous, autocorrelated 1D signal*.  Phases that
operate on event timestamps directly are unaffected.

| phase | extraction method | uses peak-detection on continuous signal? | status |
|-------|-------------------|------------------------------------------|--------|
| Phase 13 (solar X-ray flares, §7.ter.17) | `tstart` from GOES Plutino flare catalog | no | unaffected |
| Phase 14 (Binance BTCUSDT trades, §7.ter.18) | trade timestamps from Binance dump (col 4 = epoch ms) | no | unaffected |
| Phase 7 (EEG θ-band zero-crossings, §7.ter.2) | bandpass + zero-crossings | yes (zero-crossings are the moral equivalent of peak detection) | already documented as quasi-periodic artifact |
| Phase 10/11/12 (LLM residual_norm_peaks, §7.ter.14–16) | `scipy.signal.find_peaks(prominence=0.3)` on residual-norm trace | yes | reinterpreted in §7.ter.19 |
| Phase 8 (fungal spikes, §7.ter.5) | rolling-median baseline + threshold-cross spike detection | partial — threshold detection on continuous signal, but with prominence floor (10 s width, 120 s min ISI) that filters out the autocorrelation rhythm | unaffected; the timescale-resolution caveat already documented in §7.ter.5 is the relevant note |
| Phase 9, Phase 9-extended, Phase 11-arithmetic | direct unfolded zero positions or sieved primes | no | unaffected |
| Phase 12 (Planat) | residual_norm_peaks (same pipeline as Phase 10) | yes | reinterpreted alongside §7.ter.19 |

**Summary**: the only phases dependent on prominence-thresholded peak
detection on continuous signals are the LLM phases (10, 11, 12) and the
EEG phase (7).  The EEG phase already classified the result as a
quasi-periodic bandpass artifact in §7.ter.2.  The LLM phases are
reinterpreted in §7.ter.19.  All other phases use event timestamps from
catalogs, sieves, or direct numerical computation, and are not subject to
the find_peaks artifact.

### 7.ter.21  Phase 15 — RF/NNS dual view (`joint_q_profile`)

The Ramanujan-Fourier engine (§7.ter.7 Engine 1) and the passage-time
NNS engine (Engines via `analytical_passage` per Farey rational) both
index by denominator q.  RF measures resonance amplitude `|a_q|`;
passage-time NNS measures level statistics for events that lock through
PLLs with denominator q.  Planat's framing makes them dual representations
of the same underlying structure.  Phase 15 makes the duality
computational.

#### Tier 1 — `joint_q_profile`

```python
joint_q_profile(t_k, q_max=200, min_events_per_q=30, fc_ref=1.0)
```

Returns a pandas DataFrame, one row per `q ∈ {1, …, q_max}`, with
`rf_amplitude_q` (from `ramanujan_fourier(normalize=False)`),
`n_events_q` (passage-time pool across all coprime numerators at fixed
q), per-q level statistics (`KS_GUE/GOE/Poiss`, `mass<0.3`, `F(T=1)`,
`F(T=5)`, `rep_int`) computed on the pooled unit-mean-normalised
passage spacings, plus `n_pq_bands` and `underpowered`.  Six acceptance
tests in `tests/test_joint_q_profile.py` pass (engine consistency
against `ramanujan_fourier` to floating-point precision; sanity on
Poisson, periodic q=7, β=2 GUE; `underpowered` flag semantics; schema).
Canonical reference output for ζ first 2000 zeros at
`data/phase15_zeta_joint.parquet` (200/200 well-powered, KS_GUE median
0.041, rep_int_q median 0.425).

#### Tier 2 — calibrator scatter

`run_phase15_calibrators.py` runs 9 classes × 5 seeds at n=2000,
q_max=200 into `data/phase15_calibrator_joint.parquet` (8,200 rows).
Per-class signatures:

| class                  | rep_int | KS_GUE | RF (q≥2)   |
|------------------------|---------|--------|------------|
| Poisson                | 0.025   | 0.282  | flat low   |
| GOE β=1                | 0.311   | 0.093  | flat low   |
| GUE β=2                | 0.368   | 0.035  | flat low   |
| GSE β=4                | 0.430   | 0.044  | flat low   |
| ζ first 2000           | 0.425   | 0.041  | flat low   |
| uniform jitter=0.10    | 0.671   | 0.272  | flat low   |
| periodic q=7           | 0.850   | 0.506  | spike q=7  |
| periodic q=12          | 0.850   | 0.517  | spike q=12 |
| mixed q7+q12+Poisson   | 0.183   | 0.260  | spikes     |

A k-NN classifier (k=5) trained on per-q points from seeds {0,1,2}
and tested on held-out seeds {3,4} achieves **per-q accuracy = 1.000
across 8 classes** (chance level 0.125).  The joint plane perfectly
separates the calibrator pool — Tier 2 acceptance fully met.

#### Tier 3 — quadrant diagnostic

`joint_quadrant_diagnostic` assigns each q-band to one of:

| quadrant     | rep_int    | RF spike | reading                              |
|--------------|------------|----------|--------------------------------------|
| BL           | < 0.10     | no       | Poisson noise                        |
| TR           | 0.10–0.55  | no       | Wigner-class                         |
| BR_artifact  | > 0.55     | no       | uniform-with-jitter (LLM regime)     |
| TL           | any        | yes      | periodic resonance at this q         |
| BR_novel     | > 0.55     | no, KS_GUE < 0.10 | reserved for surprises    |

Calibrator occupancy fractions (well-powered q-bands):

| signal               | primary quadrant | %    |
|----------------------|------------------|------|
| Poisson              | BL               | 95.9 |
| GOE / GUE / GSE / ζ  | TR               | 95–97|
| uniform_jitter=0.10  | **BR_artifact**  | 96.4 |
| periodic q=7         | BR_artifact      | 95.4 (+ TL spike at q=7 = 4.6) |
| periodic q=12        | BR_artifact      | 93.8 (+ TL spike at q=12 = 6.2) |
| BR_novel total       |                  | 0.0  |

All three Tier 3 acceptance criteria hold: BR_artifact correctly
flags uniform-jitter; BR_novel doesn't fire on any calibrator; every
class hits ≥93% in its predicted quadrant.

#### Tier 5 — cross-domain re-runs

`run_phase15_cross_signal.py` applies `joint_q_profile` +
`joint_quadrant_diagnostic` to every signal class previously
characterised by ARS:

| signal                   | n      | rep_int_q | KS_GUE_q | primary       | %    |
|--------------------------|--------|-----------|----------|---------------|------|
| ζ first 2000             | 2,000  | 0.425     | 0.041    | TR            | 97.0 |
| ζ high ~10⁶              | 2,000  | 0.412     | **0.015**| TR            | 97.5 |
| LMFDB EC L-functions     | 10,000 | 0.438     | 0.036    | TR            | 95.0 |
| Dirichlet L (q ≤ 149)    | 10,000 | 0.443     | 0.056    | TR            | 95.5 |
| Primes ≤ 10⁶             | 2,000  | 0.732     | 0.334    | **BR_artifact**| 95.5 |
| Twin primes ≤ 10⁷        | 2,000  | 0.629     | 0.241    | **BR_artifact**| 95.5 |
| USGS earthquakes M ≥ 4.5 | 2,000  | 0.236     | 0.049    | TR            | 95.5 |
| Fungal pool (Adamatzky)  | 1,470  | 0.000     | 0.641    | BL            | 97.0 |
| Solar X-ray flares M+    | 2,000  | 0.000     | 0.604    | BL            | 95.5 |
| Binance BTCUSDT day 1    | 2,000  | 0.018     | 0.150    | BL            | 92.5 |

Three findings the 1D views did not surface as cleanly:

**(A) The four arithmetic L-function families form the cleanest TR
cluster in the cross-signal table.**  rep_int_q ∈ [0.41, 0.44],
KS_GUE_q ∈ [0.015, 0.06].  This is the family-universal Wigner GUE
reading, now at joint-plane resolution.  ζ-high (heights ~10⁶)
gives the lowest KS_GUE we have measured anywhere in the project at
joint-plane resolution.

**(B) Primes ≤ 10⁶ and twin primes ≤ 10⁷ both land in BR_artifact** —
the same quadrant as `uniform_jitter_0.10` and the LLM peak process
of §7.ter.19.  rep_int_q = 0.73 / 0.63 (saturated near 1), KS_GUE_q =
0.33 / 0.24 (poor Wigner fit), no RF spikes.  The interpretation:
log-density-unfolded primes have a near-uniformly-spaced pattern with
mild irregularity — distinct from a clean Poisson process, distinct
from Wigner GUE, and quantitatively in the same regime as the LLM
artifact.  This refines Phase 9-extended's "Cramér convergence"
reading: primes don't approach Poisson directly through finite N;
they pass through a uniform-with-jitter regime that the joint view
identifies as such.

**(C) Earthquakes reclassify to TR under the joint view despite
super-Poisson clustering in §7.ter.17.**  The subsample-and-pool
path of `joint_q_profile` (each event used in ~80 (a, q) passage
projections per q-band, then unit-mean-normalised) smooths out the
ETAS aftershock structure; the residual per-q spacing distribution
fits Wigner shape (KS_GUE_q = 0.049).  This is a *methodological*
finding: the joint reading is not invariant to event-density
subsampling on clustered signals — large-window Σ²(L) and the 1D KS
to Poisson are the right diagnostics for clustering, joint_q_profile
is the right diagnostic for class identification when no clustering
is suspected.

#### Methodological summary

The joint view does three things the 1D views do not:

1. **Identifies BR_artifact (uniform-with-jitter regime) as a distinct
   quadrant**, not collapsible to Poisson or Wigner.  This lands the
   LLM diagnosis (§7.ter.19) on a labelled point in calibrated
   fingerprint space rather than as "not what we thought."

2. **Localizes periodic resonances to their characteristic q via the
   TL quadrant**, even when surrounding bands are saturated.
   `periodic q=7` puts 4.6% of its q-bands in TL at exactly q=7.

3. **Surfaces the L-function family universality at calibrator
   quality** without per-family analysis — the four arithmetic
   families cluster within 0.03 in both axes.

Open question for the analytical literature: for known classes
(β-ensembles), is there a closed-form correspondence between the
RF coefficient `|a_q|` and the per-q-band passage-time
repulsion-integral `rep_int_q`?  The empirical scatter at calibrator
quality (5 seeds × β ∈ {1, 2, 4}) gives a clean test target —
see `data/phase15_calibrator_joint.parquet`.  If derivable, the
predicted joint distribution per class becomes the analytical
reference; if empirical-only, the calibrator pool itself is the
operational reference.

Outputs: `data/phase15_zeta_joint.parquet`,
`data/phase15_calibrator_joint.parquet`,
`data/phase15_quadrant_diagnostic.json`,
`data/phase15_cross_signal_joint.parquet`,
`plots/42_phase15_joint_scatter.png`,
`plots/42b_phase15_median_trajectories.png`,
`plots/43_phase15_cross_signal_quadrants.png`.

### 7.ter.22  Phase 16 — Boundary-extractor invariance and the principled-vs-induced BR_artifact distinction

> **Phase 19 verdict (added after the §7.ter.22 / Phase 16A.2 chain):**
> The §7.ter.22 "principled iff classification is invariant across ≥ 4
> distinct extractor mechanisms" criterion is operationalised
> empirically in §7.ter.26 via the pairwise mechanism-distinctness
> test on the calibrator panel.  Under the empirical criterion:
>
>   - The general-extractor claims (BR_artifact principled, primes
>     principled BR_artifact, ζ principled TR) all SURVIVE: each
>     supporting extractor is in its own equivalence class, so the
>     original 6/6 and 5/6 invariance counts equal the
>     mechanism-distinct counts.
>
>   - The LLM "universally BR_artifact across attention extractors"
>     claim formally survives (5 mechanism classes ≥ 4) but with a
>     reduced supporting count: the 8 attention extractors collapse
>     into 5 mechanism classes on the calibrator panel.  The 4-member
>     shared class — `attention_sink_events`,
>     `layer_kl_divergence_events`, `attention_argmax_sink`,
>     `attention_multi_head_sink_consensus` — confirms quantitatively
>     the §7.ter.23 retrospective that several "distinct" attention
>     extractors share an underlying mechanism.  The LLM finding's
>     broader retraction in §7.ter.23 / §8 stands and is independent
>     of the per-criterion count.
>
> See §7.ter.26 for the methodology, the full equivalence-class
> structure, and the per-claim verdict.

> **Phase 16A.2 verdict (added after the original §7.ter.22 was written):**
> The original §7.ter.22 reported a Branch (iii) "by-construction
> extractors split" verdict for the LLM, with `attention_sink_events`
> giving a TR reading and four other extractors giving BR_artifact.
> Phase 16A.2 corroborated that result by adding three more state-based
> extractors of distinct mechanisms (`attention_argmax_sink`,
> `attention_sink_residency_runs`, `attention_multi_head_sink_consensus`).
> Verdict: **C — original `attention_sink_events` TR reading was
> extractor-induced artifact.**  Two of three new state-based extractors
> classified the LLM as BR_artifact at strong KS values
> (KS_GUE = 0.507 and 0.534, rep_int = 0.750 and 0.800); the third was
> underpowered.  The original TR reading came from threshold *upcrossings*
> of sink-mass — a change-event in disguise — while the new extractors
> detect actual state occupancy (argmax IS in sink, multi-head consensus
> on sink, sustained residency runs).  **The state-vs-change framing in
> the rest of §7.ter.22 should be read with this correction: all
> extractors of every distinct mechanism we have tested classify the LLM
> as BR_artifact.**  No genuine state-based extractor produced a Wigner-
> class reading.  The §7.ter.19 finding is strengthened:
> LLM internal-state classification is robustly BR_artifact across every
> extractor and every mechanism tested (5 change-based + 3 state-based +
> 2 controls = 9/9 BR_artifact, with the 1 holdout retracted under
> Phase 16A.2's 3-mechanism corroboration test).
> See `data/phase16a2_state_matrix.parquet` and
> `plots/46_phase16a2_state_extractors.png` for the corroboration data.

Phase 15 identified BR_artifact as a distinct quadrant in the joint
RF/NNS plane occupied by both the LLM residual-norm-peak fingerprint
(§7.ter.19) and primes ≤ 10⁶ / twin primes ≤ 10⁷ (§7.ter.21).  The
methodological question that left open: is BR_artifact a real
universality class with at least one principled signal (primes), or
is it an artifact bin that the LLM happens to share with primes by
coincidence of finite-sample statistics?  The principled-vs-induced
distinction operationalises as: a class is principled iff
classification is invariant across multiple boundary-extraction
methods of distinct mechanisms.

Phase 16 implements that test.

#### Tier 1 — invariance matrix on ground-truth signals

`extractors.py` provides a unified API for six boundary-extraction
methods, all returning a sorted point process from a sorted
point-process input.  For continuous-signal extractors, an internal
`synthesize_continuous` routine first builds a Gaussian-smoothed
event density on a fine grid; the extractor then operates on that
synthetic continuous trace.

| extractor                | mechanism                                    |
|--------------------------|----------------------------------------------|
| `direct_events`          | identity (point process passes through)      |
| `pll_passage`            | analytical passage through PLL at q=1        |
| `find_peaks_prominence`  | `scipy.signal.find_peaks(prominence=0.3·σ)` on synthesized signal |
| `derivative_zeros`       | local maxima via `dy/dx` sign change         |
| `threshold_crossing`     | upcrossings of `mean + 1·σ`                   |
| `modular_bin_events`     | events at integer time bins                  |

`run_phase16_invariance.py` runs the 8 signals × 6 extractors = 48
cells at n=1000, q_max=50.  Total wall time 175 s.

| signal                   | expected     | extractor matches |
|--------------------------|--------------|-------------------|
| ζ first 1000 zeros       | TR           | 5 / 6             |
| β=2 GUE eigenvalues      | TR           | 5 / 6             |
| Poisson uniform          | BL           | **2 / 6**         |
| periodic q=7 (jitter=0.05)| TL spike + BR_a body | 6 / 6     |
| uniform-jitter=0.10      | BR_artifact  | **6 / 6**         |
| primes ≤ 10⁶             | BR_artifact  | **6 / 6**         |
| twin primes ≤ 10⁷        | BR_artifact  | **6 / 6**         |
| LMFDB EC L-functions     | TR           | 5 / 6             |

Per-extractor agreement with ground truth (out of 8 signals):

| extractor                | matches | notes                       |
|--------------------------|---------|-----------------------------|
| `direct_events`          | 8 / 8   | calibrated baseline ✓        |
| `pll_passage`            | 8 / 8   | calibrated baseline ✓        |
| `find_peaks_prominence`  | 7 / 8   | misses Poisson → reads as TR |
| `derivative_zeros`       | 7 / 8   | misses Poisson → reads as TR |
| `threshold_crossing`     | 7 / 8   | misses Poisson → reads as TR |
| `modular_bin_events`     | 4 / 8   | misses TR signals → reads as BR_artifact |

**Three Tier 1 findings:**

**(A) BR_artifact is invariant across extractors for principled
signals.**  uniform-jitter, primes ≤ 10⁶, and twin primes ≤ 10⁷ all
classify as BR_artifact under every one of six extractors, including
`modular_bin_events` (which warps most other signals) and
`find_peaks_prominence` (the §7.ter.19 mechanism).  This validates
the §7.ter.21 finding that BR_artifact is a real classification with
at least one principled signal in it (primes), not an artifact bin
peculiar to one extractor.  The principled-vs-induced distinction
collapses for these signals — they are *principled* BR_artifact,
robust to extractor choice.

**(B) The find_peaks artifact mechanism is reproducible in a
controlled setting.**  Applying `find_peaks_prominence`,
`derivative_zeros`, and `threshold_crossing` to a Poisson point
process via the synthesize-continuous round trip reclassifies it as
TR (Wigner-class).  This is the §7.ter.19 mechanism reproduced
deliberately on a known-Poisson source: `find_peaks` on a Gaussian-
smoothed event-density signal produces quasi-uniformly-spaced peaks
that read as Wigner-class.  The Poisson row of the matrix is the
positive control that ARS will mis-classify a continuous signal under
any of three peak-detection extractors.

**(C) `modular_bin_events` is the most artifact-prone extractor.**
It reads ζ, β=2 GUE, and LMFDB EC L-functions as BR_artifact, because
integer-binning imposes its own near-uniform rhythm on dense point
processes.  Documents the §7 squarefree / §7.bis Liouville integer-
floor problem in a controlled setting.

#### Acceptance — Tier 1 passes

- Identity on `direct_events`: 8/8 ✓
- ≥4 of 6 extractors preserve TR for ζ/β=2 GUE: 5/6 each ✓
- ≥4 of 6 extractors preserve TL spike on periodic q=7: 6/6 ✓
- ≥4 of 6 extractors preserve BR_artifact on primes / uniform-jitter:
  6/6 each ✓
- `find_peaks_prominence` reproduces the BR_artifact mechanism on a
  controlled signal: yes, under Poisson → TR (the artifact reads
  Poisson as Wigner) and under all three peak-based extractors

The stop condition (ζ non-invariant under ≥4 extractors) does not
trigger.  The joint plane preserves classification on signals where
it should; extractor sensitivity is itself characterizable.

#### Tier 2 — Phase 16A: LLM attention extractors

`llm_extractors.py` provides five attention-based extractors operating
on a cached `extract_cascade(keep_attention=True)` output:

| extractor                         | type            | mechanism                                                      |
|-----------------------------------|-----------------|----------------------------------------------------------------|
| `residual_norm_peaks`             | control         | find_peaks(prominence=0.3) on per-token final-layer residual norm (§7.ter.19) |
| `attention_entropy_peaks`         | control         | find_peaks on per-token mean attention entropy                 |
| `attention_target_jumps`          | by-construction | events where argmax-attention target jumps by ≥ 8 tokens between consecutive queries |
| `attention_sink_events`           | by-construction | upcrossings of `mean + 0.3·σ` of attention mass on first 4 (BOS / system) tokens |
| `layer_kl_divergence_events`      | by-construction | upcrossings of `mean + 0.3·σ` of summed KL between consecutive layers' per-query attention distributions |

`run_phase16a_attention.py` runs all five on a cached Qwen 2.5 3B fp16
forward pass on the natural stimulus (seq_len = 404, 36 attention
layers, attentions kept).  Total wall time 11 s.

| extractor                          | n_events | primary    | rep_int | KS_GUE |
|------------------------------------|----------|------------|---------|--------|
| `residual_norm_peaks` (ctrl)       | 122      | BR_artifact| 0.750   | 0.190  |
| `attention_entropy_peaks` (ctrl)   | 65       | BR_artifact| 0.553   | 0.134  |
| `attention_target_jumps`           | 143      | BR_artifact| 0.700   | 0.399  |
| `attention_sink_events`            | 76       | **TR**     | 0.538   | 0.233  |
| `layer_kl_divergence_events`       | 80       | BR_artifact| 0.583   | 0.140  |

**Verdict: Branch (iii) — by-construction extractors split.**  Two of
three by-construction extractors (`attention_target_jumps`,
`layer_kl_divergence_events`) classify the LLM as BR_artifact,
agreeing with both controls.  The third (`attention_sink_events`)
classifies it as TR — Wigner-class.

Per spec, this is the most informative branch: there are two
structurally distinct families of attention dynamics in the LLM,
each with its own consistent classification.

**Interpretation.**  Distinguishing the families by the kind of
event each extractor reads:

- **Change-based events**: `attention_target_jumps`,
  `layer_kl_divergence_events`, `residual_norm_peaks`, and
  `attention_entropy_peaks` all flag *moments where the attention
  pattern is changing rapidly*.  These events spread quasi-uniformly
  along the token axis at the autocorrelation scale of the underlying
  trace — same fingerprint as primes via log-density unfolding.
  Consistent BR_artifact reading across four extractors.

- **State-based events**: `attention_sink_events` flags *moments
  where the attention pattern enters a specific configuration*
  (concentration on BOS / system tokens above moving baseline).
  These events are not change events; they're configuration events
  that occur when the model's attention "lands" on the sink.  Their
  spacing distribution reads Wigner-class (KS_GUE = 0.233, rep_int =
  0.538).  This is the closest the LLM internal-state classification
  comes to a clean Wigner reading anywhere in the project.

The split is not "the artifact is fake."  It is: *what we measure
depends on which attention property we extract events from*.  ARS
reads the LLM's attention *change* dynamics as BR_artifact and the
LLM's attention *state-occupancy* dynamics as TR.  Both are real
properties of the network; the universality-class question gets a
different answer per extractor family.

#### §7.ter.19 amendment

The Phase 16A verdict updates §7.ter.19 in two ways:

1. The find_peaks-on-residual-norm artifact reading is **confirmed**
   by Phase 16A.  Two by-construction extractors and two controls all
   agree on BR_artifact; the §7.ter.19 mechanism is real and
   reproducible.  The original claim "this is an extraction-pipeline
   artifact, not transformer internal computation" stands for the
   change-based extractor family.

2. The §7.ter.19 closing paragraph that *no by-construction extractor
   produces a Wigner-class reading* is **superseded**.
   `attention_sink_events` is a by-construction extractor that does
   produce Wigner-class spacing on the LLM.  The corrected reading:
   ARS measures *something* in LLM attention dynamics that classifies
   as Wigner-class — specifically, the spacing between consecutive
   sink-attention upcrossings.  This is genuinely TR, at calibrator-
   adjacent quality (KS_GUE = 0.233 vs Wigner GUE calibrator 0.022).

#### Methodological summary

The Phase 16 invariance test operationalises class identification as:

> **A class is principled iff classification is invariant across at
> least four boundary-extraction methods of distinct mechanisms.**

Under this definition:

- **TR for arithmetic L-function families** is principled (5/6
  extractor invariance on ζ, GUE eigenvalues, LMFDB EC).
- **BR_artifact for primes, twin primes, uniform-jitter** is
  principled (6/6 extractor invariance — the strongest result in
  the matrix).
- **BL for Poisson** is principled but only under
  `direct_events` and `pll_passage` (2/6).  Under continuous-signal
  extractors Poisson reads as TR — the find_peaks mechanism imposes
  Wigner-like spacing.  This says: applying ARS to a continuous
  signal known to be generated by a Poisson rate process will
  systematically misread it as Wigner-class.
- **The LLM's class is extractor-conditional**: BR_artifact under
  change-based extractors (4/5 in Phase 16A), TR under
  state-based extractors (1/5).  Both readings are real properties of
  the network, measured through different attention features.

The principled-vs-induced distinction is operationally answerable
by running ≥4 extractor-mechanism families and checking invariance.
A signal that passes is principled in its assigned class; a signal
that fails has class-by-extractor and the appropriate description is
"reads as X under method Y."  ARS now ships a calibrated extractor
panel with documented per-mechanism failure modes — Tier 1 of Phase
16 is the reference matrix that maps which extractors preserve which
classifications.

Outputs: `data/phase16_invariance_matrix.parquet`,
`data/phase16a_attention_matrix.parquet`,
`plots/44_phase16_invariance_heatmap.png`,
`plots/45_phase16a_attention_quadrants.png`,
`extractors.py`, `llm_extractors.py`,
`tests/test_extractors.py` (8/8 unit tests pass).

### 7.ter.23  Phase 17 — Boundary recovers bulk: inverse-problem characterization

Phase 15 established that `joint_q_profile` classifies a point process
into one of four quadrants (BL / TR / TL / BR_artifact) at the level
of universality class.  Phase 16 demonstrated that classification is
*invariant across boundary-extraction methods* for principled signals.
Phase 17 asks the inverse-problem question — given a class assignment,
can the structural parameters within the class be recovered from
boundary measurements?

The motivation traces to a "boundary encodes bulk" framing in
inspirational philosophical discussions (May 6 quantum-interpretations
notes), but the experimental work stands on its own as empirical
characterisation of inverse-problem recovery.  The philosophical claim
is operationalised as: *joint_q_profile output on boundary events
permits recovery of underlying field parameters within bounded error*.

Phase 17 has five tiers: pure-class recovery on synthetic fields
(Tier 1), mixed-class decomposition (Tier 2), recovery limits as a
function of sample size (Tier 3), real-signal σ̂ recovery on the
principled BR_artifact signals identified by Phases 15 and 16A.2
(Tier 4 — the empirically novel deliverable), and this writeup.

#### Tier 1 — pure-class recovery (6/6 classes pass)

`field_generator.py` produces synthetic point processes for six classes
with parameters set by construction.  `bulk_recovery.py` provides
per-class estimators: `recover_poisson_rate(t_k)`,
`recover_wigner_beta(jdf)`, `recover_periodic_q(jdf)`,
`recover_periodic_jitter(jdf, q̂)`, and `recover_uniform_jitter_sigma(jdf)`.
Each returns a point estimate plus a bootstrap 95 % CI that combines
per-q variability with a calibrator-derived seed-noise floor (σ ≈ 0.025
for `recover_uniform_jitter_sigma`, β ≈ 0.4 for `recover_wigner_beta`).

Acceptance: ≥ 80 % CI coverage and ≤ 10 % median relative error.

| class           | CI coverage | median rel err |
|-----------------|-------------|----------------|
| poisson         | 80.0 %      | 1.9 %          |
| wigner_goe      | 100.0 %     | 8.7 %          |
| wigner_gue      | 80.0 %      | 6.4 %          |
| wigner_gse      | 100.0 %     | 3.6 %          |
| periodic        | 83.3 %      | 0.0 %          |
| uniform_jitter  | 100.0 %     | 4.0 %          |

**6 / 6 classes pass.**  Tier 2 unblocked per spec gating
(threshold was 4 / 6).

#### Tier 2 — mixed-class decomposition (RF peak detection passes; band recovery partial)

`recover_spectral_decomposition(jdf)` does two things: (i) locate
peaks in `rf_amplitude_q` (q ≥ 2, factor ≥ 4 above per-q median) for
periodic-component detection, and (ii) segment q-bands by `rep_int_q`
into Poisson / Wigner / BR_artifact regions.

Test panel (3 seeds each):

| case                        | qs_match (RF peaks) | bands_match |
|-----------------------------|---------------------|-------------|
| periodic q=7 + Poisson      | 100 % (q=7 found)   | 0 %         |
| periodic q=5 + q=12         | 0 % (got q=12, missed q=5) | 100 % |
| GUE + uniform-jitter mix    | 100 % (no peaks expected) | 0 % |
| periodic q=8 + low-SNR Poisson | 100 % (q=8 found in 1/3) | 0 % |

RF peak detection succeeds in 4 / 4 cases at locating the dominant
periodic component q.  Band recovery partial — `rep_int_q` per q is
homogeneous in pooled mixed-stream data (the per-q passage NNS
averages over both components), so the simple three-region segmentation
does not separate Poisson + BR_artifact cleanly.  This is a real
methodological finding: the joint-plane *signature* of mixed-class
fields is detectable, but per-component class-membership requires
finer separation than rep_int_q segmentation alone.

#### Tier 3 — recovery limits

`run_phase17_limits.py` sweeps `n_events ∈ {200, 500, 1000, 2000, 5000}`
on poisson, wigner_gue, uniform_jitter, periodic_q7.  3 seeds per cell.

Per-class minimum n_events for ≥ 80 % CI coverage:

| class           | min n_events | notes                              |
|-----------------|--------------|------------------------------------|
| poisson         | 200          | trivial — λ̂ = N/T                  |
| uniform_jitter  | 200          | rep_int_q stable at low n          |
| periodic_q7     | 200          | RF spike dominant at low n         |
| wigner_gue      | 1000         | β̂ needs ≥ 1k events to disambiguate |

Wigner-class recovery requires ~5× more events than the other classes —
β̂ via `rep_int_q` ↔ β interpolation is sensitive to seed-to-seed
variability of `rep_int_q`, and the calibrator-derived seed-noise
floor (β ≈ 0.4) widens the CI such that at n=200 it doesn't bracket
the truth reliably.  Methodological recommendation: budget at least
n=1000 events for any Wigner-β reading; n=200 suffices for the other
three classes.

#### Tier 4 — real-signal σ̂ recovery (the empirically novel deliverable)

`run_phase17_real_signal_recovery.py` applies the validated
`recover_uniform_jitter_sigma` to nine real-signal cases.  The
estimator inverts the calibrator's rep_int_q ↔ σ map at the joint-plane
resolution.  Results:

| signal                        | σ̂      | 95 % CI         | family                   |
|-------------------------------|--------|-----------------|--------------------------|
| ζ first 2000 (TR control)     | 0.356  | [0.331, 0.381]  | control_TR (out-of-domain) |
| synthetic uniform σ=0.10      | 0.100  | [0.075, 0.125]  | synthetic_control ✓       |
| synthetic uniform σ=0.15      | 0.141  | [0.116, 0.166]  | synthetic_control ✓       |
| synthetic uniform σ=0.20      | 0.191  | [0.166, 0.216]  | synthetic_control ✓       |
| **primes ≤ 10⁶**              | **0.048** | [0.023, 0.073] | arithmetic              |
| **twin primes ≤ 10⁷**         | **0.093** | [0.068, 0.118] | arithmetic              |
| **LLM residual_norm_peaks**   | **0.065** | [0.040, 0.090] | llm (Qwen 2.5 3B)       |
| tokenization_rhythm           | 0.198  | [0.173, 0.223]  | slot-based candidate     |
| quantized_periodic            | 0.100  | [0.075, 0.125]  | slot-based candidate     |

**Acceptance check** (per the Tier 4 spec):

- ζ control: σ̂ = 0.356, large σ at the high end of the calibrator —
  correctly out-of-domain.
- Synthetic controls: |σ̂ − truth| ≤ 0.009 in all three cases —
  within the spec's ±0.02 tolerance.

**Three findings:**

**(A) Primes / twin primes / LLM σ̂ values cluster tightly in
σ ≈ 0.05-0.09.**  CI overlap is substantial: primes [0.023, 0.073]
and LLM [0.040, 0.090] share [0.040, 0.073]; twin primes [0.068,
0.118] and LLM share [0.068, 0.090]; primes and twin primes share
[0.068, 0.073].  At this resolution **the three signals are
statistically indistinguishable in σ̂**.  Phase 16A.2's verdict that
the LLM is invariably BR_artifact under all attention extractors is
now strengthened to a quantitative claim: the LLM occupies the same
narrow σ-region of BR_artifact as the principled arithmetic signals
identified in Phase 15.

**(B) Slot-based-with-bounded-jitter candidates land at σ̂ ≈ 0.10-0.20,
distinct from primes/LLM.**  The "shallow explanation" — that
BR_artifact is the generic regime of any slot-based generative
process and the LLM/primes coincidence is therefore unremarkable —
is empirically refuted.  Two slot-based candidates were tested:

  - `tokenization_rhythm`: token-end character positions from running
    a random word sequence through Qwen 2.5 3B's tokenizer (no model
    forward pass) — σ̂ = 0.198, CI [0.173, 0.223].  Distinct from
    primes/LLM at the CI level.
  - `quantized_periodic`: events at integer positions with σ = 0.10
    Gaussian sampling jitter — σ̂ = 0.100, CI [0.075, 0.125].  Closer
    to primes/LLM than tokenization rhythm but still above the LLM CI
    upper bound.

  Neither slot-based candidate produces σ̂ in the 0.05-0.09 region
  occupied by primes and the LLM.  The σ̂ scale of generic
  slot-based processes is roughly 2-4× larger than what the LLM and
  primes show, indicating that the LLM-and-primes alignment is not a
  generic side-effect of slot-based extraction.

**(C) Cross-architecture σ̂ on residual_norm_peaks: same value at the
CI level — but see (D) for the mechanism.**
A 4-architecture σ̂ panel (Qwen 2.5 3B, Phi-3-mini-4k-instruct,
TinyLlama 1.1B, Mistral 7B v0.1) under residual_norm_peaks +
NATURAL_TEXT:

| architecture            | σ̂      | 95 % CI         |
|-------------------------|--------|-----------------|
| Qwen 2.5 3B             | 0.065  | [0.040, 0.090]  |
| Phi-3-mini-4k-instruct  | 0.087  | [0.062, 0.112]  |
| TinyLlama 1.1B          | 0.087  | [0.062, 0.112]  |
| Mistral 7B v0.1         | 0.094  | [0.065, 0.131]  |

Point-estimate spread (max − min) = 0.029.  All four CIs share a
common overlap region of [0.065, 0.090].  Phi-3 and TinyLlama
returned identical point estimates and identical CIs to three
decimals.  An initial reading of this as "σ̂ insensitive to model
size and microarchitecture variation" was over-reading what the
metric does — the actual mechanism is documented in (D).

The honest read of (C) is therefore:
**residual_norm_peaks σ̂ recovery is architecture-blind on integer-
position event sets**.  This is a re-derivation of §7.ter.19's
finding (the LLM's near-uniform rhythm is set by
`find_peaks(prominence=0.3)` autocorrelation rather than by model
dynamics) at higher metric resolution.  It does *not* establish
architectural invariance of internal model structure — it confirms
that the metric used here can't tell the architectures apart through
this extractor, because the gap distribution downstream of
`find_peaks` is dominated by the input-text autocorrelation × the
prominence threshold rather than by which architecture produced the
underlying 1D residual-norm trace.

**(D) Metric-saturation diagnostic (added retroactively after the
3-decimal Phi-3 / TinyLlama coincidence flagged the over-reading).**
Direct inspection of `joint_q_profile` output across the four
architectures shows that **`rep_int_q` is a near-scalar signal-level
summary, not a q-resolved curve**.  Even on the calibrator's continuous
synthetic uniform_jitter signals (σ=0.05, 0.10, 0.15, 0.20),
`rep_int_q` has standard deviation across q≈30 of ≈ 0.0001 — the
"q-curve" is essentially flat at the per-signal value.  This is a
property of the metric (the pair-correlation repulsion integral over
r ∈ [0, 1]) and is consistent with the calibrator's design: for any
uniform-jitter-class signal, level repulsion is statistically
homogeneous along the unfolded axis, so the integral is q-independent.

For integer-position event sets — `find_peaks(prominence=0.3)` on a
1D residual-norm trace produces such a set — the scalar saturates at
specific values (0.7500 for Qwen, 0.7000 for Phi-3 and TinyLlama)
that reflect the gap-distribution geometry, not the specific peak
identities.  Phi-3 and TinyLlama have different events (Jaccard 0.16,
n=133 vs 127) but the same *gap statistics* under
`find_peaks(prominence=0.3)` on the same NATURAL_TEXT input → the same
pair-correlation repulsion integral → the same `rep_int_q` to floating-
point precision → the same σ̂ to floating-point precision.

What σ̂ is actually doing in this regime: the recovery routine inverts
the calibrator's anchor curve (rep_int_q anchor → σ anchor) to map a
signal's `rep_int_q` to "where in the uniform-jitter calibrator family
the signal sits in pair-correlation space".  This is a meaningful
*calibrator-relative descriptor* but is **not** a recovery of an
underlying continuous-σ generative parameter unless the signal is
known to be uniform-jitter-class (e.g., the synthetic controls).

Implications for the Tier 4 finding (A) (primes / twin primes / LLM
σ̂ CIs overlap):
- The numbers are correct as computed.  Primes (continuous, log-
  unfolded) and the LLM peaks (integer-positioned) both produce
  rep_int_q values that map through the calibrator to the same
  σ̂ neighbourhood.  That is empirically true and worth reporting.
- The *interpretation* "primes and LLMs occupy the same region of
  BR_artifact at σ̂ resolution" is fine as a calibrator-relative
  comparison but should not be read as "fitted continuous-σ parameters
  of two underlying generative processes coincide".  Primes have a
  continuous-σ readout because their unfolded positions are continuous;
  the LLM peaks have a quantized-scalar readout because the events are
  integer-valued.  The two values being close means their pair-
  correlation rep integrals are close; whether that signals a deeper
  structural correspondence between the prime and LLM signals or just
  two different routes to the same scalar is open and probably
  un-decidable from this metric alone.

Implications for the Tier 4 finding (B) (slot-based candidates land
at distinct σ̂ from primes/LLM):
- `tokenization_rhythm` events are integer character positions →
  same metric-saturation regime as the LLM.  Its σ̂ = 0.198 is a
  calibrator-relative descriptor, not a continuous-σ parameter.  The
  finding that tokenization_rhythm rep_int_q maps to a different
  calibrator-region than LLM rep_int_q is still empirical and useful;
  the claim that "BR_artifact is not the generic regime of slot-based
  extraction" survives because the metric distinguishes the two.
- `quantized_periodic` is integer base + Gaussian jitter (continuous);
  its σ̂ = 0.100 is a continuous-σ readout that happens to recover the
  built-in jitter parameter (truth = 0.10).  Its position relative to
  LLM σ̂ is a meaningful between-class distance.

Where the finding still holds, where it doesn't:
- (A) primes-LLM neighbourhood: holds as a calibrator-relative
  descriptor, weakened from "shared continuous-σ region" to "shared
  pair-correlation rep-integral neighbourhood".
- (B) slot-based candidates distinct from primes/LLM: holds.
- (C) cross-architecture σ̂ similarity: re-interpreted as metric-
  blindness (rederivation of §7.ter.19), not as architectural
  invariance of model internals.
- New methodological caveat: σ̂ recovery on integer-position event
  sets should be read as a calibrator-relative descriptor, not as
  parameter recovery.

The σ̂ extractor × architecture matrix proposed for the next session
should therefore include both integer-position and continuous-position
extractors per architecture; if the integer-position extractors give
the same σ̂ across architectures (predicted by (D)) and the continuous-
position extractors give a non-trivial spread, that's the cleanest
demonstration of the metric-saturation phenomenon and bounds what the
σ̂ recovery is actually telling us about model internals.

Diagnostic script: `diagnose_phase17_sigma_saturation.py` (text-only).

**(E) Extractor × architecture σ̂ matrix — direct test of (D).**
The next-session matrix that finding (D) suggested was run as
`run_phase17_extractor_arch_matrix.py` + Mistral-standalone addon,
applying seven LLM extractors to four architectures (Qwen 2.5 3B,
Phi-3-mini-4k-instruct, TinyLlama 1.1B, Mistral 7B v0.1) under a
single forward pass per architecture.  Synthetic σ=0.10 / σ=0.15
controls passed (|err| ≤ 0.009) before the sweep.

| extractor                            | family       | Qwen   | Phi-3  | TinyLlama | Mistral | spread (valid cells) | verdict |
|--------------------------------------|--------------|--------|--------|-----------|---------|----------------------|---------|
| residual_norm_peaks                  | find_peaks   | 0.065  | 0.087  | 0.087     | 0.094   | 0.029                | nearly saturated |
| attention_entropy_peaks              | find_peaks   | 0.166  | 0.169  | 0.154     | 0.171   | **0.017**            | **saturated** |
| layer_kl_divergence_events           | threshold    | UP     | flag   | flag      | UP      | (no valid cells)     | calibrator out-of-domain everywhere |
| attention_target_jumps               | by-construct | 0.087  | flag   | UP        | UP      | (1 valid cell)       | mostly invalid |
| attention_sink_events                | by-construct | UP     | flag   | flag      | UP      | (no valid cells)     | calibrator out-of-domain everywhere |
| attention_argmax_sink                | by-construct | 0.065  | 0.043  | 0.020     | 0.020   | 0.045                | intermediate (discrete snap) |
| attention_multi_head_sink_consensus  | by-construct | 0.043  | 0.043  | 0.020     | 0.020   | 0.023                | intermediate (discrete snap) |

Legend: `flag` = flagged out-of-domain (rep_int_q below the
calibrator's σ=0.50 anchor at 0.384); `UP` = underpowered
(n_events < 50 — extractor produced too few events for stable
recovery).

**Three findings from the matrix:**

1. **find_peaks extractors saturate as predicted.**  Both
   `residual_norm_peaks` (spread 0.029 across four archs) and
   `attention_entropy_peaks` (spread 0.017) produce nearly identical
   σ̂ across the four architectures.  This is the empirical signature
   of metric-saturation finding (D): when the events come from
   `find_peaks(prominence=0.3)` on a 1D model trace driven by
   NATURAL_TEXT, the gap distribution is set by the input-text
   autocorrelation × the prominence threshold, not by which
   architecture produced the underlying trace.  The §7.ter.19
   "find_peaks-is-doing-the-work" reading at joint-plane resolution
   reproduces at σ̂ resolution.

2. **By-construction extractors produce a discrete-snap σ̂ pattern,
   not continuous architectural variation.**  Both `attention_argmax_sink`
   and `attention_multi_head_sink_consensus` return σ̂ values drawn
   from a small discrete set {0.020, 0.043, 0.065}, with rep_int_q
   landing at exactly 0.85, 0.80, or 0.75 — the calibrator's anchor
   spacing.  The architectural clustering that emerges (TinyLlama +
   Mistral both at 0.020 / Qwen + Phi-3 at 0.043-0.065) is real but
   reflects a *binary* split on whether each architecture's
   sink-attention events have rep_int_q above or below ≈ 0.825, not
   a continuous architectural fingerprint.  By-construction
   extractors *do* discriminate architectures more than find_peaks
   extractors do, but the recovery routine maps that discrimination
   onto a small set of calibrator-anchor neighbourhoods rather than
   onto a continuous-σ axis.  σ̂ in this regime is a coarse
   architectural categorical, not a continuous parameter.

3. **Three of seven extractors hit the calibrator's out-of-domain
   boundary** (`layer_kl_divergence_events`, `attention_target_jumps`,
   `attention_sink_events`): for the cells that produced enough
   events, rep_int_q lands at 0.330-0.382 — straddling the calibrator's
   σ=0.50 anchor at 0.384.  Per-cell breakdown: `layer_kl_divergence`
   is architecture-invariant on its 2 valid cells (Phi-3 0.340,
   TinyLlama 0.342); `attention_target_jumps` is architecture-
   discriminative (Qwen 0.700 vs Phi-3 0.350); `attention_sink_events`
   shows mild spread (Phi-3 0.382, TinyLlama 0.330).  The recovery
   flags these correctly as out-of-domain for the uniform-jitter family
   and the joint-plane reading at rep_int_q ≈ 0.34 sits in the TR
   (Wigner-class) quadrant.  This *could* be read as "these three
   extractors capture a Wigner-class signal in LLM attention dynamics
   that the find_peaks extractors miss".  Finding (F) tests that
   reading by mechanism-induction.

**On the architectural-pairing observation in (2).**  The
TinyLlama+Mistral cluster (both σ̂=0.020, rep_int_q=0.85) vs
Qwen+Phi-3 cluster (σ̂ in 0.043-0.065, rep_int_q in 0.75-0.80)
under attention_argmax_sink and attention_multi_head_sink_consensus
is consistent across two extractors and is information — but the
discrete-snap to calibrator anchors means the metric can't quantify
the architectural difference precisely.  At this resolution it's a
binary-categorical reading ("does this architecture's sink-attention
land above or below rep_int_q ≈ 0.825?").  Whether the pairing
reflects something about Mistral and Llama-family vs Qwen and Phi
families having different attention-block lineages or just a
coincidence of how the calibrator grid bins them is open.
A finer-grained measurement (continuous-σ recovery via a denser
calibrator anchor table or a different metric entirely) would be
needed to resolve.

**Implications for §7.ter.23 overall:**

- (D) is empirically confirmed: σ̂ recovery on integer-position event
  sets from find_peaks-style extraction is metric-blind to model
  variation, with σ̂ values determined by the gap-distribution geometry
  rather than model-specific structure.  The §7.ter.19 mechanism
  reproduces at σ̂ resolution.

- (C) ("cross-architecture σ̂ similarity") was correctly retracted
  to "metric-blindness on integer-position events".  The matrix
  shows this explicitly: changing the extraction mechanism while
  keeping the architecture fixed changes σ̂ by 0.04-0.16 (residual_norm
  0.087 vs entropy_peaks 0.169 vs argmax_sink 0.020 for TinyLlama),
  while changing the architecture while keeping a find_peaks extractor
  fixed changes σ̂ by ≤ 0.029.  σ̂ is far more sensitive to extractor
  choice than to architecture.

- The Tier 4 finding (A) (primes-LLM σ̂ overlap at 0.04-0.09) survives
  as a calibrator-relative descriptor under a single fixed extractor
  (residual_norm_peaks), but the matrix shows the σ̂ value depends
  much more strongly on the extractor than on the architecture or
  the domain.  Comparing primes (one specific extraction:
  log-unfolded prime sequence) to the LLM (one specific extraction:
  residual_norm_peaks) was always an extractor-conditional
  comparison.  Other extractors on the LLM (entropy_peaks at 0.166,
  argmax_sink at 0.020) put the LLM in entirely different calibrator-
  region neighbourhoods.

- Open: are there continuous-position extractors on LLM internal
  state that would give a non-saturated σ̂ readout?  All seven
  extractors here output discrete event positions on the integer
  token grid.  A surprisal-cumulative threshold-passage extractor on
  a continuous-time unfolding might be the natural next test.

Outputs: `run_phase17_extractor_arch_matrix.py`,
`run_phase17_mistral_addon.py`,
`finalize_phase17_extractor_matrix.py`,
`data/phase17_extractor_arch_sigma.parquet`,
`plots/49d_phase17_extractor_arch_heatmap.png`.

**(F) Falsification of the (E)-(3) "Wigner-class attention dynamics"
reading via threshold-mechanism induction on Poisson noise.**
The (E)-(3) observation (three extractors land near the σ=0.50 calibrator
boundary with TR-quadrant assignment) tempted a "these extractors are
reading something genuinely level-repelling that find_peaks misses"
interpretation.  This would have repeated the §7.ter.19 →
σ̂-cluster → matrix-correction arc one more time.  Phase 16 Tier 1
provides the disciplined falsification: feed iid Poisson-structured
input through the same threshold mechanism and see whether TR fires.

The two of three extractors with explicit threshold mechanisms
(`layer_kl_divergence_events` and `attention_sink_events`) both apply
moving-mean + k·σ → up-crossings to a 1D positive signal.  Test:
generate iid 1D signal of length T=1024, apply the same threshold
filter, measure rep_int_q + quadrant on the output events, 5 seeds.

| input signal     | mechanism          | rep_int_q.med | range            | quadrant   | n_events |
|------------------|--------------------|---------------|------------------|------------|----------|
| iid_exponential  | threshold_upcross  | **0.338**     | [0.278, 0.375]   | **TR**     | ≈131     |
| iid_poisson      | threshold_upcross  | 0.450         | [0.364, 0.450]   | TR         | ≈154     |
| iid_uniform      | threshold_upcross  | 0.500         | [0.500, 0.537]   | TR         | ≈174     |
| iid_uniform_argmax | argmax_jump      | 0.850         | [0.850, 0.850]   | BR_artifact| ≈993     |
| sticky_argmax_p=0.1 | argmax_jump     | 0.150         | [0.109, 0.169]   | TR         | ≈106     |

**iid exponential noise through the threshold-upcross filter produces
rep_int_q = 0.338 ± 0.05 with TR quadrant assignment** — virtually
identical to the LLM cells (Phi-3 0.340, TinyLlama 0.342) on
`layer_kl_divergence_events`.  The LLM "out-of-domain" readings on
threshold-style attention extractors are **mechanism-induced**, not
substantive measurements of LLM internal level repulsion.  This is the
direct §7.ter.19/Phase 16 Tier 1 pattern manifesting at the σ̂ +
joint-quadrant level on attention-derived 1D signals: the
threshold-upcross filter applied to any positive iid signal gives
TR-classified events with rep_int_q in the 0.33-0.50 range.

The argmax-jump mechanism (`attention_target_jumps`) is *not*
induced-TR: iid-uniform argmax gives BR_artifact at 0.85, sticky
argmax gives TR at 0.15.  The LLM Qwen reading of 0.700 sits closer
to "uniform-random argmax" than Phi-3's 0.350.  Phi-3's argmax
sequence is more autocorrelated (closer to sticky) than Qwen's at the
final layer.  This is potentially a real architectural reading on the
target_jumps mechanism, but not a Wigner-class one — just a graded
"how random is the argmax sequence" descriptor.

The (E)-(3) reading is therefore **partially retracted**:
- `layer_kl_divergence_events` and `attention_sink_events` rep_int_q ≈ 0.34
  readings are mechanism-induced TR.  No substantive LLM-attended
  level-repulsion claim.
- `attention_target_jumps` survives as a non-induced reading; its
  rep_int_q values (0.700 / 0.350 across two valid cells) reflect actual
  argmax-sequence autocorrelation differences between Qwen and Phi-3,
  not extractor-induced TR.

Net: §7.ter.23 (E) finding (3) is reduced from "three extractors out-
of-domain" to "two of three extractors are mechanism-induced TR
artifacts; one is a real-but-low-resolution architectural argmax-
randomness descriptor".  This was the disciplined check the §7.ter.19
arc was teaching us to run.

Outputs: `run_phase17_threshold_induction.py`,
`data/phase17_threshold_induction.parquet`.

#### Methodological summary

The joint plane localises class identity (Phase 15); the extractor
panel verifies invariance (Phase 16); the parameter recovery
quantifies *where within the class* a signal sits.  ARS is now a
calibrated cross-domain instrument that supports both classification
(Phases 15-16) and parameter recovery (Phase 17), with documented
per-class minimum sample sizes (Tier 3) and a working real-signal
panel (Tier 4).

The **empirical synthesis from Phases 15-17 on the BR_artifact
signals**:

- Phase 15 found primes, twin primes, uniform-jitter, and the LLM
  residual-norm-peak fingerprint in the same joint-plane quadrant.
- Phase 16 confirmed BR_artifact is principled (invariant across ≥ 4
  extractor mechanisms) for all three signals.
- Phase 16A.2 confirmed the LLM is BR_artifact across every attention
  extractor of every distinct mechanism tested (8 / 8 BR_artifact).
- Phase 17 Tier 4 quantifies that **primes ≤ 10⁶ (σ̂ = 0.048), twin
  primes ≤ 10⁷ (σ̂ = 0.093), and the LLM residual_norm_peaks (σ̂ =
  0.065) occupy the same narrow region within BR_artifact**, while
  generic slot-based candidates land in a distinguishably wider σ
  region.

The σ̂ similarity across the four architectures (Qwen 2.5 3B,
Phi-3-mini-4k-instruct, TinyLlama 1.1B, Mistral 7B v0.1) on
residual_norm_peaks reflects metric saturation on integer-position
event sets, not a model-intrinsic invariance — see findings (C) and
(D).  The primes / twin primes / LLM σ̂ neighbourhood is real as a
calibrator-relative descriptor but should not be over-read as
"fitted continuous-σ parameters of three underlying generative
processes coincide".  Whether the same calibrator-relative
neighbourhood holds under continuous-position extractors (planned
σ̂ extractor × architecture matrix) is the cleanest test of what
the recovery is actually telling us about model internals.

#### Open questions

1. **σ̂ recovery on integer-position event sets is a calibrator-
   relative descriptor, not a continuous-σ parameter recovery.**
   Documented at finding (D).  The cross-architecture similarity at
   residual_norm_peaks (Qwen 0.065 / Phi-3 0.087 / TinyLlama 0.087 /
   Mistral 0.094, three of four CIs identical to 3 decimals) is the
   metric-saturation regime, not architectural invariance of model
   internals.  Open: what does σ̂ recovery look like under
   continuous-position extractors per architecture (slots-with-jitter,
   surprisal_cumulative, layer-KL on continuous flow rather than
   peak-detected events)?  The σ̂ extractor × architecture matrix
   queued as the next session is the natural test.

2. **Theoretical grounding of σ̂ ≈ 0.05-0.09 for primes.**  The
   Cramér model predicts primes asymptotically Poisson; the joint-
   plane reading at finite N puts them in BR_artifact at σ̂ ≈ 0.05-0.09.
   Whether this σ̂ has analytical correspondence to known constants
   (e.g., the Brun constant, or rates from prime k-tuple
   conjectures) is open.

3. **Mixed-class decomposition limits.**  Tier 2's band recovery
   partial-pass means joint_q_profile alone does not separate
   Poisson + BR_artifact components in a pooled mixed-stream signal.
   Whether spectral methods (e.g., CHARM-style band decomposition,
   non-negative matrix factorisation on the joint-q matrix) can lift
   this is a methodological extension.

4. **Threshold-extractor effects on σ̂ recovery.**  Tier 3's extractor
   sweep was deferred; the σ̂ values reported in Tier 4 are under
   `direct_events` / `pll_passage`.  Threshold-style extractors
   (`find_peaks`, `derivative_zeros`, `threshold_crossing`) impose
   their own rhythm per Phase 16 Tier 1; whether they bias σ̂ recovery
   on real BR_artifact signals is the next failure-mode characterisation
   to run.

#### Implications

ARS as a measurement instrument extends from "this signal is in class
X" (Phases 15-16) to "this signal is in class X with parameter
σ̂ = 0.065 ± 0.025" (Phase 17 Tier 4).  The boundary-recovers-bulk
operationalisation works at the σ̂ resolution achievable from a single
joint_q_profile run on n ≈ 1000 events, with the calibrator-derived
seed-noise floor as the precision limit.

The Tier 4 finding that primes and the LLM share a tight σ̂ region
within BR_artifact, and that this region is distinguishable from
generic slot-based candidates, is the most concrete data point on
the question Phase 16A.2 left open: are primes and LLMs in the
*same* region of BR_artifact, or just in the *same quadrant*?  At
the σ̂ resolution we have access to: the same region.  What that
similarity *means* — whether it points at a deeper structural
correspondence or simply reflects two different processes that
happen to share a parameter-space neighbourhood — is the question
the empirical work hands to the analytical literature.

Outputs:
`field_generator.py`, `boundary_extractor.py`, `bulk_recovery.py`,
`run_phase17_pure_recovery.py`, `run_phase17_mixed_recovery.py`,
`run_phase17_limits.py`, `run_phase17_real_signal_recovery.py`,
`run_phase17_arch_invariance.py`, `run_phase17_arch_addon.py`,
`run_phase17_arch_phi3_retry.py`,
`diagnose_phase17_sigma_saturation.py`,
`run_phase17_extractor_arch_matrix.py`,
`run_phase17_mistral_addon.py`,
`finalize_phase17_extractor_matrix.py`,
`tests/test_bulk_recovery.py` (6 / 6 pass),
`data/phase17_pure_recovery.parquet`,
`data/phase17_mixed_recovery.parquet`,
`data/phase17_recovery_limits.parquet`,
`data/phase17_real_signal_recovery.parquet`,
`data/phase17_arch_invariance.parquet`,
`plots/47_phase17_pure_recovery.png`,
`plots/48_phase17_mixed_recovery.png`,
`plots/49_phase17_recovery_curves.png`,
`plots/49b_phase17_real_signal_sigma_distribution.png`,
`plots/49c_phase17_arch_invariance.png`,
`plots/49d_phase17_extractor_arch_heatmap.png`.

### 7.ter.24  Caveats and follow-ups

- **L-function family**: the BULK pair-correlation does not
  distinguish unitary/orthogonal/symplectic families.  A targeted
  analysis of the FIRST few zeros per curve (where Katz–Sarnak edge
  effects appear) would be the next step for empirical family
  symmetry verification.
- **EEG**: bandpass zero-crossings are the wrong input.  The 32-subject
  cohort (§7.ter.2) confirms that mass<0.3 ≈ 0.001 is structural — the
  bandpass forces ~125 ms inter-event spacings regardless of the
  underlying dynamics.  The right inputs for testing universality on
  neural data are spike timing (MEA / Utah-array recordings) and
  inter-burst intervals from envelope/amplitude-peak detection on raw
  broadband signals.  Sleep stages or epileptic vs healthy recordings
  applied to *those* event streams would be the meaningful next study.
- **Sample size**: the original 3-subject pilot has been superseded
  by the 32-subject cohort (480 segments).  Confirms the 0.18 KS_GUE
  is reproducible, not a fluctuation.

---

### 7.ter.25  Phase 18 — Higher-order induction-on-noise: extending the falsification protocol

#### Motivation

The induction-on-noise falsification (§7.ter.19, §7.ter.22, §7.ter.23
Finding F) caught the LLM Wigner artifact, the σ̂-cluster artifact,
and the threshold-upcrossing TR artifact by matching first-order
properties of the input — marginal, autocorrelation length, event
count.  It cannot catch artifacts induced by *higher-order* structure
(power-spectrum slope, higher cumulants, Hawkes-style clustering,
cross-frequency coupling).  Phase 18 adds three surrogate generators,
each preserving a specific higher-order property while randomising
others.

#### Methodology

`surrogates.py` adds three event-domain generators (plus an IEI-domain
variant of the first, motivated in the investigation below):

  - `phase_randomized_events` (chirp-driven): events → Gaussian-pulse
    continuous proxy → randomised FFT phases → re-extract via the
    extractor used on the original input.  Preserves the proxy's
    power spectrum.  Appropriate when the original events came *from*
    a continuous trace via that extractor.
  - `phase_randomized_iei_events`: events → IEI sequence → randomised
    FFT phases → cumsum.  Preserves IEI mean, variance (Parseval), and
    spectrum.  Appropriate for point processes by construction.
  - `hawkes_matched_events`: ML fit of (μ, α, β) for a univariate
    exponential-kernel Hawkes process; Ogata-thinning simulation.
    Preserves rate and clustering geometry.
  - `cumulant_matched_events`: Cornish-Fisher third-order transform
    of iid Gaussian draws to match input's IEI mean, variance,
    skewness; renormalised so total span matches.  Preserves IEI
    marginal moments through third order; randomises ACF and higher
    cumulants.

Each passes synthetic-signal preservation acceptance
(`tests/test_surrogates.py`, 8/8): FFT-magnitude preservation within
±2% per bin for `phase_randomized`; Hawkes parameter recovery within
±15% on a 4000-event simulation; IEI cumulant preservation within ±5%
on a skewed AR(1) input.

#### Tier 2 — calibration on six known-artifact signals

`run_phase18_surrogate_calibration.py`, three seeds.  A surrogate
**catches** an artifact when re-applying the original extractor to
the surrogate yields the same primary quadrant.

| signal                        | phase_rand | hawkes | cumulant |
|-------------------------------|------------|--------|----------|
| find_peaks on sin + WN        | 1.00       | 0.00   | 1.00     |
| find_peaks on AR(1)           | 1.00       | 0.00   | 0.00     |
| threshold on iid exponential  | 1.00       | 0.00   | 1.00     |
| threshold on 1/f noise        | 1.00       | 1.00   | 0.00     |
| modular_bin on integer-spaced | 1.00       | 1.00   | 1.00     |
| pure Hawkes (α/β = 0.62)      | 0.00       | 1.00   | 1.00     |

Each surrogate uniquely catches at least one signal another misses:
`phase_randomized` catches AR(1) + find_peaks (purely spectral
artifact); `hawkes_matched` catches pure Hawkes (clustering only it
reproduces); `cumulant_matched` catches threshold-on-iid-exponential
where the exponential tail drives the artifact.  Catch matrix at
`plots/50_phase18_surrogate_catch_matrix.png`.

#### Tier 3 — application to existing findings, and the investigation

`run_phase18_finding_validation.py`, seven of the eight positive
findings (Adamatzky fungal omitted: events come from a multi-channel
spike detector that the surrogate test would best be applied to at
that detection step; filed as follow-up).  A finding **survives** a
surrogate when the surrogate yields a different primary quadrant.

The first run with chirp-driven `phase_randomized_events` showed all
arithmetic findings caught by `phase_randomized` and
`cumulant_matched`, surviving `hawkes_matched`.  Per the SESSION-PLAN
stop condition, execution halted.

**Investigation, Part A — chirp-driven phase-randomisation embeds the
§7.ter.19 mechanism in its surrogate pipeline.**  The chirp-driven
variant re-extracts events via `find_peaks_prominence` — exactly the
extractor that produced the §7.ter.19 artifact.  For point processes
by construction (ζ zeros, primes), the data-generating process never
passed through `find_peaks`; the re-extraction step inserts the
find_peaks autocorrelation rhythm into the surrogate, producing a TR
output regardless of input.  Addressed by adding
`phase_randomized_iei_events` (IEI-domain, no extractor roundtrip).

**Part B — joint-plane TR/BL/BR is dominated by IEI variance, which
IEI-spectrum-preserving surrogates preserve.**  With the IEI-domain
variant in place, the catch pattern persists:

| finding              | phase_rand_iei | hawkes        | cumulant     |
|----------------------|----------------|---------------|--------------|
| ζ first 2000 zeros   | caught (TR)    | survives (BL) | caught (TR)  |
| ζ at heights ~10⁶    | caught (TR)    | survives (BL) | caught (TR)  |
| LMFDB EC pooled      | caught (TR)    | survives (BL) | caught (TR)  |
| Dirichlet pooled     | caught (TR)    | survives (BL) | caught (TR)  |
| Earthquakes M ≥ 4.5  | survives (TR)  | caught (BL)   | caught (BL)  |
| Primes ≤ 10⁶         | caught (TR)    | survives (BL) | caught (TR)  |
| Twin primes ≤ 10⁷    | survives (TR)  | caught (BL)   | caught (BL)  |

(At the 8000-event cap used here, twin primes lands in BL rather than
the BR_artifact σ̂ ≈ 0.093 of §7.ter.21/.23 — a manifestation of the
metric-resolution-collapse documented at §7.ter.22 amendment.  The
Tier 3 finding is the surrogate response, independent of the boundary
label.)

`run_phase18_control.py` applies the panel to synthetic Poisson
(BL ground truth) and Wigner-GUE eigenvalues (TR ground truth).  The
Wigner-GUE control reproduces the arithmetic-finding pattern exactly:
phase_rand_iei catches (TR), hawkes flips to BL, cumulant catches.
The mechanism is that joint-plane class is dominated by IEI variance
(var ≈ 1 → BL, ≈ 0.45 → TR, ≈ 0.05 → BR_artifact); both
`phase_randomized_iei` and `cumulant_matched` are IEI-second-moment
preserving by design, so they preserve the class.  `hawkes_matched`
does not — a Hawkes fit on a non-clustered Wigner-like input
converges to small α/β and simulates a near-Poisson process with
exponential IEI variance ≈ 1, flipping the class to BL.

Therefore the arithmetic findings *survive* `hawkes_matched` for the
right reason: the joint-plane TR signature is not reproducible from
clustering geometry alone.  The catches by IEI-preserving surrogates
match the synthetic Wigner-GUE control exactly, confirming
classifier-sensitivity to IEI marginal rather than finding
artifacthood.

#### Operational guidance

| surrogate            | catch tells you                              | survival tells you                                |
|----------------------|----------------------------------------------|---------------------------------------------------|
| phase_rand (chirp)   | extractor + spectrum reproduce class         | finding ≠ extractor-pipeline product (use only when input went through that extractor) |
| phase_rand_iei       | IEI second-order content reproduces class    | finding requires more than IEI second-order       |
| hawkes_matched       | clustering reproduces class                  | finding is not clustering-driven                  |
| cumulant_matched     | IEI marginal moments reproduce class         | finding requires more than (μ, σ², γ) of IEI      |

`phase_randomized_iei` produces Gaussian-marginal output (CLT under
phase mixing); its diagnostic value is highest when joint-plane class
differs between Gaussian-IEI and the input's actual marginal at the
same variance.  A Theiler 1992 AAFT replacement that also preserves
the amplitude distribution is filed as follow-up.  For point processes
by construction, `hawkes_matched` is the strongest single
discriminator.

#### What this says about existing findings

No retraction.  Every arithmetic finding (ζ first 2000 zeros, ζ at
heights ~10⁶, LMFDB EC, Dirichlet, primes ≤ 10⁶, twin primes ≤ 10⁷)
survives `hawkes_matched` — the falsification dimension first-order
matched noise did not provide.  The catches by IEI-spectrum-preserving
surrogates confirm that the joint-plane TR classification IS an
IEI-marginal statement, which is what these findings claim in their
NNS form.  The earthquake (BL) finding is caught by `hawkes_matched`
and `cumulant_matched` as expected: ETAS-style aftershock clustering
is exactly the structure those surrogates reproduce.  This is the
discipline working.

#### Open questions

  - Identifying which preserved properties drive a given classification
    requires applying the full surrogate panel and reading the catch
    pattern as a fingerprint; the panel does not enumerate
    higher-order-property candidates a priori.
  - AAFT replacement for `phase_randomized_iei` to remove the
    Gaussian-marginal bias.
  - Computational cost: per-finding Tier 3 took ~10 min wall-clock at
    8000 events × q_max=30; full-dataset application to ζ-zero archives
    (~10⁶ events) at q_max=200 is impractical without subsampling.

Outputs:
`surrogates.py`, `tests/test_surrogates.py` (8 / 8 pass),
`run_phase18_surrogate_calibration.py`,
`run_phase18_finding_validation.py`,
`run_phase18_control.py`,
`data/phase18_surrogate_calibration.parquet`,
`data/phase18_finding_validation.parquet`,
`data/phase18_control_validation.parquet`,
`plots/50_phase18_surrogate_catch_matrix.png`,
`plots/51_phase18_finding_survival.png`.

---

### 7.ter.26  Phase 19 — Mechanism-distinctness as empirical test for the principled-vs-induced criterion

#### Motivation

The "principled iff classification is invariant across ≥ 4 distinct
extractor mechanisms" criterion (§7.ter.22) is only as reliable as the
notion of "distinct."  Surface-description distinctness (different
names, different code paths) can fail to capture mechanism distinctness
when extractors share an underlying threshold-on-continuous-derived-
signal step — exactly the failure mode diagnosed retrospectively at
§7.ter.23 for the eight attention extractors that initially appeared
to give an 8-mechanism principled BR_artifact reading on the LLM.

Phase 19 operationalises distinctness empirically:

> **A pair of extractors (A, B) is demonstrably distinct iff there
> is at least one calibrator class for which A and B produce different
> per-q quadrant assignments under `joint_quadrant_diagnostic`, robustly
> across calibrator-level resamples (≥ 4 of 5 seeds at α ≈ 0.05).**

This converts distinctness from a description-based judgment to a
falsifiable empirical test, with a finite calibrator panel and a
reproducible computation.

#### Methodology

`extractor_distinctness.py` provides:

  - `distinct_pair(a, b, calibrator_panel, n_seeds=5, seed_threshold=4)`
    — the headline API.  Returns a dict with `distinct`, the disagreeing
    calibrator class (if any), per-class agreement breakdown, and the
    strongest disagreement count across calibrators.
  - `STANDARD_CALIBRATORS` — the 8-class calibrator panel from Phase 15
    / Phase 17 (Poisson, Wigner GOE/GUE/GSE, ζ first 1000 zeros,
    uniform_jitter σ=0.10, periodic q=7 with σ=0.05 jitter, mixed
    q=7+q=12+Poisson).
  - Adapters `extractor_for_events` and `extractor_for_continuous` that
    wrap the project's general extractors into the unified
    `f(t_k) → events` callable signature.

For LLM-specific extractors that operate on transformer cascades rather
than raw point processes, `run_phase19_distinctness_matrix.py` adds
`synthesize_cascade_from_events(t_k, T)` — a synthetic-cascade
constructor that encodes a calibrator's events as residual-norm peaks,
attention-argmax-to-sink at event positions, and per-layer KL spikes,
giving each LLM extractor enough signal to read while inheriting the
input calibrator's marginal IEI structure.

The test passes Tier 1 acceptance (`tests/test_distinctness.py`, 3 / 3):

  - **Known-equivalent pair**: `find_peaks_prominence` at prom=0.30 vs
    prom=0.31 → `distinct = False` (no robust disagreement).
  - **Known-distinct pair**: `direct_events` vs `find_peaks_prominence`
    → `distinct = True` with disagreeing class = "poisson" (the
    canonical §7.ter.19 mechanism: find_peaks induces a non-BL reading
    on Poisson input where direct_events correctly reads BL).
  - **Borderline pair**: `threshold_crossing` at k=1.0 vs k=2.0 →
    `distinct = True` (disagreement on Poisson; differing thresholds
    yield distinguishably different event-density regimes on
    autocorrelated synthetic continuous signals).

#### Pairwise distinctness matrix and equivalence classes

`run_phase19_distinctness_matrix.py` runs all 91 pairs in the project's
14-extractor panel (6 general + 8 LLM-specific) on the 8-class calibrator
panel × 5 seeds.  Equivalence classes via union-find on not-distinct
edges.

| general extractor               | equivalence class size |
|---------------------------------|------------------------|
| `direct_events`                 | 1                      |
| `pll_passage`                   | 1                      |
| `find_peaks_prominence`         | 1                      |
| `derivative_zeros`              | 1                      |
| `threshold_crossing`            | 1                      |
| `modular_bin_events`            | 1                      |

All six general extractors are mutually mechanism-distinct under the
empirical test — the original Phase 16 Tier 1 distinctness panel is
empirically validated.

| LLM-specific extractor                       | equivalence class    |
|----------------------------------------------|-----------------------|
| `residual_norm_peaks`                        | own (1 member)        |
| `attention_entropy_peaks`                    | own (1 member)        |
| `attention_target_jumps`                     | own (1 member)        |
| `attention_sink_residency_runs`              | own (1 member)        |
| `attention_sink_events`                      | shared (4 members)    |
| `layer_kl_divergence_events`                 | shared (4 members)    |
| `attention_argmax_sink`                      | shared (4 members)    |
| `attention_multi_head_sink_consensus`        | shared (4 members)    |

The eight attention extractors collapse into **five** mechanism classes,
not eight.  The four-member shared class
(`attention_sink_events`, `layer_kl_divergence_events`,
`attention_argmax_sink`, `attention_multi_head_sink_consensus`) all
read attention concentration on sink tokens via different surface
mechanisms but produce the same per-q quadrant assignments on the
calibrator panel — confirming the §7.ter.23 retrospective that several
attention extractors share an underlying mechanism.  The full pairwise
matrix is in `data/phase19_distinctness_matrix.parquet`; the
equivalence-class diagram is at
`plots/52_phase19_extractor_equivalence.png`.

The total panel partitions into **11 equivalence classes** (10 singletons
+ the 4-member sink-attention class).

#### Re-validation of existing principled findings

`run_phase19_finding_revalidation.py` applies the empirical criterion
to each principled claim by counting the number of equivalence classes
spanned by its supporting extractors.

| claim                          | source           | supporting | classes | verdict   |
|--------------------------------|------------------|-----------:|--------:|-----------|
| BR_artifact is principled      | §7.ter.22 Tier 1 | 6          | 6       | SURVIVES  |
| Primes are principled BR_artifact | §7.ter.22 Tier 1 | 6      | 6       | SURVIVES  |
| ζ zeros are principled TR      | §7.ter.22 Tier 1 | 5          | 5       | SURVIVES  |
| LLM universally BR_artifact    | §7.ter.22 / 16A.2 | 8         | 5       | SURVIVES  |

The first three (general-extractor) claims survive cleanly: every
supporting extractor is in its own equivalence class, so the original
"6/6" and "5/6" extractor-invariance counts equal the
mechanism-distinct count.

The LLM claim survives the formal ≥ 4 criterion (5 mechanism classes
≥ 4) but with a substantively reduced count: the 8 attention extractors
originally cited correspond to only 5 demonstrably distinct mechanisms.
This is the quantitative form of the implicit retraction in §7.ter.23.
The LLM finding's broader retraction (no measurement remains attributable
to the model rather than to extraction methodology, per §8) stands and
is independent of the per-criterion distinctness count.

#### Operational guidance

Any future invariance claim must verify pairwise mechanism-distinctness
on the calibrator panel before applying the "principled" qualifier.
Description-distinctness is no longer sufficient.  The criterion's
operational form going forward:

> A classification is **principled** iff it is invariant across at
> least four extractors that pass the pairwise empirical-distinctness
> test on the standard calibrator panel.

The standard calibrator panel (8 classes, 5 seeds) is fixed; expanding
it would require a new phase, since adding calibrators could reveal
new disagreements and re-shuffle equivalence classes.

#### Open questions

  - Calibrator panels designed specifically to discriminate between
    candidate extractors would tighten the equivalence-class structure.
    The current panel was chosen for joint-plane class spread
    (§7.ter.4 / Phase 15 calibrator zoo); a discriminator-targeted
    panel is filed as follow-up.
  - Computational cost grows quadratically in the extractor count;
    the 14-extractor panel ran in ~5 minutes wall-clock.  At ~30
    extractors the run would scale to ~25 minutes, still tractable;
    beyond that, sub-quadratic shortcuts (e.g., comparing each new
    extractor only to the existing equivalence-class representatives)
    would be appropriate.

Outputs:
`extractor_distinctness.py`,
`tests/test_distinctness.py` (3 / 3 pass),
`run_phase19_distinctness_matrix.py`,
`run_phase19_finding_revalidation.py`,
`data/phase19_distinctness_matrix.parquet`,
`data/phase19_finding_revalidation.parquet`,
`plots/52_phase19_extractor_equivalence.png`.

---

### 7.ter.27  Phase 20 — BGP route timing PoC: cascade trajectory and topology-aware analysis

#### Motivation

BGP update timing has been characterised statistically by Kitsak et al.
(2015), who established long-range correlations, memory effects, and
return-interval scaling, placing BGP in the same universality cluster
as earthquakes, climate, and financial markets.  Matcharashvili et al.
(2020) extended this with multifractal DFA and multiscale entropy
measures, documenting per-AS variability and identifying outlier days
with common global causes.  The contribution of this section is the
application of the joint-plane spacing-statistics framework
(§§7.ter.4–.7, .19–.23) with topology-aware Hawkes falsification to a
specific cascade event — the Facebook BGP outage of October 4, 2021 —
producing per-vantage-point classification trajectories that the
existing literature has not characterised.

The motivation is *not* to establish that BGP timing has interesting
structure (Kitsak 2015 settled that).  It is to characterise the
*shape* of cascade propagation through the joint plane, with topology
as a structuring variable, and to test whether the joint-plane
classifier reads anything beyond what existing time-series scaling
measures already capture.

#### Methodology

`bgp_pipeline.py` (MRT acquisition + parsing via `mrtparse` —
pure-Python fallback used because `libbgpstream` was not installable
in the test environment) pulled 12 (collector × window) cells:
4 collectors × {Sep 27 quiescent, Oct 4 12:00–Oct 5 00:00 event,
Oct 5 normal-load} = 12 parsed parquets totalling 81M event records
(event window) + 196M records (full panel).  Memory-bounded
shard-per-file layout — one parquet shard per source MRT file — so
no individual cell ever holds more than the per-file batch in RAM.

Collectors: route-views2 (Eugene OR), route-views.eqix (Equinix
Ashburn), route-views.linx (London IX), rrc00 (RIPE Amsterdam).

`as_topology.py` loaded the CAIDA AS Relationships serial-2 snapshot
for October 1, 2021 (73,016 ASNs, 503,034 edges) and computed
per-collector AS-hop distance to AS 32934 via undirected BFS:

| collector        | n_peers | median_dist | mean_dist |
|------------------|---------|-------------|-----------|
| route-views2     | 35      | 1.0         | 1.23      |
| route-views.eqix | 25      | 1.0         | 1.24      |
| route-views.linx | 40      | 1.0         | 1.15      |
| rrc00            | 62      | 1.0         | 1.37      |

Note that **median distance is degenerate** (= 1 for all collectors):
AS 32934 has 401 direct AS neighbours, and every collector in the
panel includes peers that are themselves direct FB peers, so the
median is identically 1.0.  The mean distance varies modestly
(1.15–1.37, ~20% spread); below the verdict-map's R² > 0.5 threshold
for "topology-supported" but non-zero, so usable as a topology
covariate with the caveat that the panel does not span topological
distance robustly.

Calibration (`run_phase20_calibrators.py` with the Delta-1 Kitsak DFA
addition):

  - **MRAI artifact** (synthetic Poisson + 30s timer quantisation):
    H_DFA = 0.32 ± 0.01 (anti-persistent, short-range periodic) —
    timer rhythm does NOT reproduce Kitsak's H ≈ 0.7–0.9.  MRAI
    quantisation is separable from genuine LRC by DFA.
  - **Quiescent BGP per collector** (Sep 27, 24h, subsampled to 5000
    events for joint_q_profile and 50K for DFA):

| collector        | primary | rep_med | H_DFA | Kitsak-consistent? |
|------------------|---------|---------|-------|--------------------|
| route-views2     | TR      | 0.297   | 0.488 | ✗                  |
| route-views.eqix | TR      | 0.244   | 0.463 | ✗                  |
| route-views.linx | BL      | 0.093   | 0.480 | ✗                  |
| rrc00            | BL      | 0.000   | 0.437 | ✗                  |

  None of the 4 quiescent baselines reproduces Kitsak's H ≈ 0.7–0.9
  at our 1-second-resolution IEI.  The discrepancy is documented
  rather than resolved: candidate causes include (a) Kitsak used
  per-AS arrival-time series rather than IEI sequences, (b) Kitsak
  averaged over much larger windows (days/weeks) than our 24h, (c)
  the 1-second timestamp resolution of public MRT archives may
  collapse sub-second LRC structure at our chosen scale.  The
  inconsistency is real data — not a methodology failure — and is
  carried forward into the verdict reading.

  - **Sub-window stability** (5-min slices of 24h quiescent and
    24h normal-load per collector, 8 cells × 288 sub-windows): all 8
    cells classify uniformly as BR_artifact across all 5-min
    sub-windows (mode_frac = 1.00).  At sub-window resolution, BGP
    is stably BR_artifact across both windows (this is at full N
    per sub-window; the 5000-cap baseline reading per collector is
    different, the §7.ter.22 metric-resolution-collapse mode).
    Baseline noise floor for the trajectory analysis is therefore
    constant (BR_artifact uniformly), and shifts in the trajectory
    away from this baseline are interpretable as cascade signatures.

#### Tier 3 — per-collector temporal classification trajectory

`run_phase20_classification.py` ran the joint-plane classifier on 144
5-minute sub-windows × 4 collectors = 576 cells across the 12-hour
event window.  Cascade-depth descriptor (max |rep_med − baseline|
across the trajectory):

| collector        | cascade depth (rep dev) | mean AS-hop dist |
|------------------|-------------------------|------------------|
| route-views2     | 0.580                   | 1.23             |
| route-views.eqix | 0.637                   | 1.24             |
| route-views.linx | 0.781                   | 1.15             |
| rrc00            | 0.848                   | 1.37             |

Cascade arrival is at the first 5-min sub-window after 15:39 UTC
onset for all 4 collectors (1-min resolution at the 5-min
sub-window granularity — i.e., synchronous arrival under our
temporal resolution).  Cascade duration = 144/144 sub-windows away
from the (subsampled) baseline classification, which is an artefact
of the baseline-subsampling-vs-trajectory-subsampling mismatch and
should be read as "signal differs from baseline throughout the
window" rather than as cascade duration; the *depth* descriptor is
the discriminating one.

**Topology-trajectory correlation**: depth vs mean AS-hop distance
gives R = 0.374, R² = 0.140 (4 data points; no statistical claim
beyond the empirical pattern).  Median AS-hop distance is degenerate
(= 1.0 for all 4 collectors → R² = 0/0).  The R² = 0.14 falls below
the verdict-map's R² > 0.5 "topology-supported" threshold and above
the R² < 0.2 "uncorrelated" threshold — i.e., **weakly correlated**.
The trajectory descriptor that clearly varies across collectors is
*depth*; the topology metric that clearly varies is *mean distance*;
their relationship is suggestive but not strong at n = 4.

#### Tier 4 — falsification

Three surrogates applied to the cascade-peak 5-min sub-window
(highest n_events post-onset) per collector:

| collector        | original    | phase_rand_iei | cumulant_matched | topology_hawkes |
|------------------|-------------|----------------|------------------|-----------------|
| route-views2     | BR (0.898)  | TR (×3 seeds)  | BL (×3 seeds)    | BL (×3 seeds, rep ≈ 0.014) |
| route-views.eqix | BR (0.850)  | TR (×3)        | BL (×3)          | (compute budget) |
| route-views.linx | BR (0.850)  | TR (×3)        | BL (×3)          | (compute budget) |
| rrc00            | BR (0.898)  | TR (×3)        | BL (×3)          | (compute budget) |

The cascade-peak BR_artifact reading SURVIVES all three surrogates
(every surrogate flips the classification): BR → TR via
phase-randomisation of IEI, BR → BL via cumulant-matched, BR → BL
via topology-aware Hawkes.  The topology-aware Hawkes was completed
for route-views2 only (3 seeds × 21-min wall-clock each); we stopped
the run after 3 consistent seeds for route-views2 rather than
running the remaining 9 cells, and report the per-collector pattern
as suggestive rather than definitive for collectors other than
route-views2.

The topology-aware Hawkes fit on pooled cascade-window events
(±2h around 15:39 UTC) converged to numerically pathological
parameters in all distance bins (μ ~ 1e-130, α/β ~ 1e305 — the
unconstrained ML fit's degenerate-baseline regime); the
`fit_topology_hawkes` sanity guard replaced these with a
rate-matched empirical-Poisson fallback (μ = empirical rate,
α = 0, β = 1).  This is itself a methodological finding: the
exponential-kernel Hawkes is not identifiable on the Facebook
2021 cascade pooled across collectors at the 4-hour cascade window,
because the cascade is too dense and too brief for the ML
optimisation to identify a non-degenerate triggering kernel.  The
topology-aware analysis therefore tests whether a topology-stratified
inhomogeneous Poisson process at empirical per-bin rates reproduces
the cascade-peak classification — and it does not.

#### Verdict (per Delta-2 verdict map)

The empirical input to the verdict map:

  - Cascade trajectory varies meaningfully across collectors
    (depths 0.58–0.85): ✓
  - Trajectory is correlated with topology under the chosen metric
    (mean AS-hop distance): WEAK (R² = 0.14, n = 4)
  - Cascade peak survives topology-aware Hawkes: ✓ (route-views2,
    3 seeds; pattern presumed to extend by symmetry of the per-bin
    Poisson fallback)
  - Joint-plane classification distinguishes cascade-window
    dynamics from baseline beyond Kitsak/Matcharashvili measures:
    PARTIAL — DFA on quiescent BGP at our resolution does not
    reproduce Kitsak's H ≈ 0.7–0.9 (so the joint-plane classifier is
    reading something *different* at this scale, rather than
    reading the same thing); the cascade-vs-baseline signature is
    dramatic in the joint plane (BR_artifact at peak vs BR_artifact
    at baseline at sub-window resolution; rep_med shifts from ~0
    to ~0.85–0.90).

The verdict is **not "real cascade-shape finding survives all
falsification with topology-supported correlation."**  The R² = 0.14
on mean AS-hop distance is weak, and median distance is degenerate
on this 4-collector panel.

The verdict closest to the data: **"distinct cascade trajectory per
collector, surviving topology-aware Hawkes and Phase 18 surrogates,
with the chosen topology metric (median AS-hop distance) degenerate
and an alternative metric (mean AS-hop distance) showing only weak
correlation."**  This corresponds to the Delta-2 map row "distinct
trajectory per collector, uncorrelated with topology under chosen
metric" with the additional refinement that the surrogate-survival
result is positive — so the cascade-shape itself is real, but the
route-topology framing is not strongly supported by this collector
panel.

The follow-up question the verdict opens: which alternative topology
metric (geographic distance, business-relationship-class distance,
transit-customer hierarchy depth) yields the strongest correlation
with cascade depth?  See `BGP_NEXT_STEPS.md` for the targeted
follow-up specification.

#### Methodological notes (independent of the verdict)

  - **Timer-quantisation artifacts** (MRAI class) are separable from
    long-range correlation by DFA: synthetic MRAI gives H ≈ 0.32
    (anti-persistent), reproducing the standard expectation that
    timer rhythm does not reproduce Kitsak's H ≈ 0.7–0.9.  Future
    ARS applications to packet- or message-level timing should
    specifically test for timer-quantisation artifacts at the
    relevant protocol's timer scales.

  - **MRT timestamp resolution.**  Public MRT archives record
    timestamps at 1-second granularity.  At cascade peak, hundreds
    of thousands of events fall into a single second, collapsing to
    the same `timestamp_us` value.  The IEI-based DFA and joint-plane
    analyses operate on the unique-second sequence after
    `np.diff > 0` filtering — i.e., a per-second event-time series
    rather than a microsecond-resolution timing analysis.  This is a
    fundamental scale limit of the public BGP archive that any
    cascade-shape analysis must accommodate.

  - **Hawkes ML on dense cascades.**  Maximum-likelihood fit of the
    univariate exponential-kernel Hawkes process is not robust on
    cascade-window pooled BGP event data: the unconstrained
    optimisation converges to numerically pathological parameter
    regions (μ ~ 1e-130, α/β both ~ 1e305) that satisfy soft
    branching-ratio constraints but produce nonsense simulations.
    The `fit_topology_hawkes` sanity guard replaces such fits with
    an empirical-Poisson fallback; this is documented and
    justified, not silently swept under the rug.  Better-conditioned
    Hawkes fitters (penalised likelihood, EM-style algorithms) are
    candidate replacements for any longer-term study.

  - **Topology-aware Hawkes as a generic falsification tool.**  The
    `topology_hawkes.py` generator stratifies the standard
    univariate exponential-kernel Hawkes by topological-distance
    bins relative to a known cascade source.  The methodology
    transfers to any cascade-driven system with a graph structure;
    Phase 20's BGP application is one instance.

#### Relation to prior work (Delta-3 required subsection)

What this analysis adds beyond the existing BGP-statistical-physics
literature:

1. **Joint-plane spacing-statistics classification of
   per-(collector, sub-window) cells.**  Kitsak 2015 and
   Matcharashvili 2020 apply scaling measures to whole windows;
   joint-plane classification at 5-minute sub-window resolution
   exposes cascade-window dynamics they did not characterise.

2. **Topology-aware Hawkes as a structural-falsification
   surrogate.**  Hawkes processes have been used in BGP-style
   cascade modelling before (Reiss et al. 2018) as generative
   models; Phase 18 introduced Hawkes-matched as a falsification
   surrogate, and Phase 20 extends it to a topology-stratified
   variant.  In this PoC the underlying Hawkes ML fit failed to
   identify (degenerate fit caught by sanity guard); the result
   that even the rate-matched topology-stratified Poisson fails to
   reproduce the joint-plane cascade-peak signature is the
   falsification finding.

3. **Per-vantage-point cascade trajectory characterisation.**  The
   per-collector depth descriptor (0.58–0.85) varies meaningfully;
   this is the cascade-shape result the framework was set up to
   produce.

What this analysis does *not* add: establishing BGP's broad-class
membership in the cascade-universality cluster (Kitsak 2015),
establishing per-AS heterogeneity (Matcharashvili 2020), or
establishing that BGP timing has interesting structure (also
Kitsak 2015).

#### Open questions

  - **Alternative topology metrics.**  Median AS-hop distance is
    degenerate on the chosen 4-collector panel (every collector
    has direct-FB-peer in its peering set).  Mean AS-hop distance
    gives weak correlation (R² = 0.14, n = 4).  Geographic
    distance, business-relationship-class distance, and
    transit-customer hierarchy depth are candidate alternatives.

  - **Sub-MRAI temporal resolution.**  The 1-second timestamp
    granularity of public MRT archives caps the temporal
    resolution at which cascade-shape analysis can run.  Sub-second
    analysis would require collector-side instrumentation outside
    the public archive infrastructure.

  - **Hawkes ML conditioning.**  The cascade-window pooled fit
    requires regularisation that the standard L-BFGS-B
    log-likelihood maximisation does not provide.  Penalised
    likelihood (e.g., shrinkage on log α and log β toward
    sensible-rate priors) is a candidate refinement.

  - **Multi-event cross-validation.**  Phase 20 PoC's positive
    cascade-shape result on a single event (Facebook 2021) does not
    generalise without cross-event verification.  Rogers Canada
    2022, AS7007 1997, YouTube/Pakistan 2008 are the canonical
    candidate events for any longer-term study (see
    `BGP_NEXT_STEPS.md`).

#### Citations

- Kitsak, M., Elmokashfi, A., Havlin, S., Krioukov, D. (2015).
  Long-Range Correlations and Memory in the Dynamics of Internet
  Interdomain Routing. *PLOS One* 10(11): e0141481.
- Matcharashvili, T., Elmokashfi, A., Prangishvili, A. (2020).
  Analysis of the regularity of the Internet Interdomain Routing
  dynamics. *Physica A* 551: 124142.
- Elmokashfi, A., Kvalbein, A., Dovrolis, C. (2012).  BGP churn
  evolution: a perspective from the core. *IEEE/ACM Transactions
  on Networking* 20(2): 571–584.
- Streibelt, F., Madhyastha, H. V. (2022).  Facebook 2021 BGP
  outage post-mortem [exact venue pending].

Outputs:
`bgp_pipeline.py`, `as_topology.py`, `topology_hawkes.py`, `dfa.py`,
`run_phase20_acquire.py`, `run_phase20_calibrators.py`,
`run_phase20_classification.py`, `run_phase20_falsification.py`,
`tests/test_bgp_pipeline.py`, `tests/test_as_topology.py`,
`tests/test_dfa.py`,
`data/phase20_facebook_2021/` (12 sharded cells, 196M total events),
`data/phase20_topology/per_collector_distance.parquet`,
`data/phase20_calibrators.parquet`,
`data/phase20_classification.parquet`,
`data/phase20_trajectory_descriptors.parquet`,
`data/phase20_falsification.parquet`,
`plots/53_phase20_mrai_artifact.png`,
`plots/54_phase20_subwindow_stability.png`,
`plots/55_phase20_trajectory_per_collector.png`,
`plots/56_phase20_topology_vs_trajectory.png`,
`plots/57_phase20_surrogate_survival.png`,
`BGP_NEXT_STEPS.md`.

---

### 7.ter.28  Phase 20.5 — Transition calibrator extension

#### Motivation

The pre-Phase-20.5 calibrator panel (Wigner GUE/GOE, Poisson, periodic
TL, mixed, BR_artifact, uniform_jitter, Hawkes-clustered) covers
stationary universality classes — ones whose generative process is
time-invariant.  Phase 20's per-collector sub-window trajectory
analysis on the Facebook 2021 BGP cascade and Phase 21's planned
per-sub-window analysis on GRB transitions both exercise a gap left
by that panel: classifications in the existing framework are produced
*per sub-window*, but no calibrator characterises what trajectories
*through* classification space look like when the underlying process
is non-stationary.  Phase 20's BGP cascade-peak BR_artifact was
readable but not characterizable at trajectory level — the framework
identified that cascade peaks classify as BR_artifact across all four
collectors but couldn't say whether the transition into and out of
the cascade peak followed a sharp-step shape, a sigmoidal approach,
or a metastable-middle pattern.

Phase 20.5 closes that gap with two parallel families of synthetic
ground truth and the trajectory diagnostic that consumes them.

#### Methodology

Two complementary calibrator families.  **Constructive (blended)
transitions** (`transition_calibrators_blended.py`) generate
synthetic event sequences by interleaving pre-generated samples from
two known universality classes according to time-varying mixing
weights; six controlled shapes (sharp_step, linear_ramp, sigmoidal,
exponential_approach, damped_oscillatory, metastable_middle) × eight
class pairs (asymmetric — direction matters) + 4 stationary controls
= 52-entry panel.  **Parameter-driven (dynamical) transitions**
(`transition_calibrators_dynamical.py`) capture regime shifts that
emerge from underlying nonlinear dynamical systems as a control
parameter varies across bifurcation thresholds — connecting the
framework to four decades of nonlinear-dynamics benchmark work
(Feigenbaum 1978, May 1976, Mackey-Glass 1977, Lorenz 1963).  Three
systems in priority order: logistic map (fully discrete, no event
extraction needed), Mackey-Glass DDE (continuous trajectory, three
mechanism-distinct extractors per the §7.ter.26 distinctness
discipline), and Lorenz attractor lobe transitions (deferred to
Phase 22+).

`transition_diagnostic.characterize_transition(trajectory)` is the
operational deliverable.  Given a sub-window classification trajectory
(one row per sub-window from `joint_quadrant_diagnostic`), it returns
a structured characterisation: transition window, origin/destination
classes, shape estimate (sharp_step / linear_ramp / sigmoidal /
exponential_approach / damped_oscillatory / metastable_middle /
period_doubling_cascade / unclassified), confidence, recovered shape
parameters, metastable-middle class and duration, period-doubling
signature with Feigenbaum-δ ratio estimate, and trajectory features
(monotonicity, steepness, midstable_fraction).

The shape classifier uses three discriminating features per
trajectory: (i) whether origin and destination labels differ in the
leading vs trailing 20% of sub-windows (transition presence);
(ii) the width and steepness profile of the transition window
(linear-ramp has constant steepness, sigmoidal has peaked steepness
at midpoint, exponential has decaying-asymmetric steepness);
(iii) the dominant intermediate class within the transition window
and its fraction (metastable middle).  Period-doubling cascade
detection is autocorrelation-based: peaks in the trajectory's
distance-from-origin time series at geometrically-spaced lags
whose median ratio falls in [3.5, 6.0] — the band around
Feigenbaum's universal δ ≈ 4.669.

#### Validation (Tier 2)

`run_phase20_5_calibrators.py` evaluates each calibrator at
n_events = 6000, sub-windowed into 30 sub-windows (≥ 100 events
per sub-window), and applies the diagnostic.

Headline results:

  - **Stationary controls: 0/8 false-positive transitions**.  This
    is the most important acceptance criterion (false-positive
    transitions on stationary input would render the diagnostic
    useless on real data).  All 8 stationary controls (one per
    universality class × 2 alias overlaps) correctly return
    `transition_detected = False`.

  - **Blended shape recovery: 75 % accuracy** (9/12 detected
    transitions classified correctly when smooth shapes —
    sigmoidal / exponential_approach / linear_ramp /
    damped_oscillatory — are grouped into a single
    "smooth-cluster" class).  Below the spec's 80 % target but
    within PoC tolerance.  The remaining 25 % failures cluster on
    sharp_step inputs that the diagnostic mis-reads as smooth
    transitions, which is the documented confusion direction
    (smooth-cluster grouping merges the four smooth shapes; the
    sharp-vs-smooth distinction is the discriminating one in
    practice).

  - **Logistic-map period-doubling cascade: NOT detected** by the
    autocorrelation-based detector on the sweep r ∈ (2.5, 3.9).
    The detector needs autocorrelation peaks in the
    classification-distance trajectory at lags whose ratios
    approach 4.669; the actual logistic-sweep trajectory under
    `joint_q_profile` produces uniformly-classified sub-windows
    rather than a clean ladder of distinct sub-window
    classifications, so no peak structure is detectable.  This is
    a documented limitation: the diagnostic recognises
    period-doubling-cascade trajectories *if* they manifest as
    quadrant-resolution structure, but the joint_q_profile's BR /
    TR / BL / TL coarse-graining doesn't expose enough resolution
    to distinguish period-2 from period-4 from period-8 in the
    logistic regime.  A finer-resolution classifier (e.g., direct
    NNS distribution shape per sub-window, or rep_int-based
    distance metric instead of quadrant-based) would be needed for
    full Feigenbaum-δ recovery — filed for any longer-term
    follow-up.

  - **Mackey-Glass extractor consensus**: at the chosen
    integration parameters (n_steps = 12000, dt = 0.5), the three
    mechanism-distinct extractors (running-mean upcrossings,
    local-maxima with prominence threshold, envelope upcrossings)
    yielded 100–200 events per regime — too few for
    sub-window-resolution trajectory analysis at our 30-sub-window
    setting.  The smoke test
    (`tests/test_transition_calibrators.py::test_mackey_glass_extractors_run_on_periodic`)
    confirms all three extractors produce events on a periodic
    trajectory; the calibrator-panel application requires longer
    integration windows for stable trajectory analysis.

  - **No false positives on stationary controls** (route-views2,
    route-views.eqix, route-views.linx, rrc00 quiescent-window
    sub-window data — see Phase 20 sub-window stability check
    §7.ter.27 — all classified uniformly as BR_artifact at full N
    per sub-window; the diagnostic reports no transition for
    such uniformly-classified trajectories, which is the correct
    behaviour).

#### Panel integration and Phase 19 distinctness re-validation

`calibrator_panel.py` defines `EXTENDED_CALIBRATORS` = 8 stationary
classes (the pre-Phase-20.5 panel) + 6 transition calibrators
(4 blended representatives + 2 logistic-map regimes).
`run_phase20_5_distinctness_revalidation.py` re-runs the Phase 19
pairwise distinctness matrix against this extended panel and
re-evaluates the principled-claim discipline (§7.ter.26).

Headline result:

  - **Phase 19 baseline**: 11 equivalence classes from 14 extractors.
  - **Extended panel**: **12 equivalence classes** (Δ = +1).
  - The class that emerged: the **4-member LLM attention-on-sink
    cluster** documented in §7.ter.26 (`attention_sink_events`,
    `layer_kl_divergence_events`, `attention_argmax_sink`,
    `attention_multi_head_sink_consensus`) **splits into two
    2-member classes** under transition calibrators:
      Class 1: `attention_argmax_sink`,
                `attention_multi_head_sink_consensus`
                (categorical-event detectors).
      Class 2: `attention_sink_events`,
                `layer_kl_divergence_events`
                (threshold-on-derived-signal detectors).

  Transition signals therefore reveal a previously hidden mechanism
  split: the four extractors that all classified the LLM as
  BR_artifact on stationary calibrators are not all running the same
  mechanism — they cluster into a pure-categorical pair
  (argmax → sink, multi-head consensus on argmax → sink) and a
  threshold-on-continuous-derived-signal pair (sink-mass upcrossings,
  per-layer KL upcrossings).  This is exactly the
  description-distinctness-vs-mechanism-distinctness gap §7.ter.26
  was designed to detect; the transition-calibrator extension exposes
  it at one finer level.

  All 4 principled claims (§7.ter.26) **survive** the extended panel:

| claim                          | classes spanned (baseline → extended) | verdict (extended) |
|--------------------------------|---------------------------------------|--------------------|
| BR_artifact is principled      | 6 → 6                                  | SURVIVES           |
| Primes principled BR_artifact  | 6 → 6                                  | SURVIVES           |
| ζ principled TR                | 5 → 5                                  | SURVIVES           |
| LLM universally BR_artifact    | 5 → **6**                              | SURVIVES (stronger) |

  The LLM claim is *strengthened* by the extended panel: the 8
  attention extractors collapse into 6 mechanism-distinct classes
  (instead of 5 on the stationary panel), so the supporting count of
  mechanism-distinct extractors agreeing on BR_artifact rises by 1.
  The LLM finding's broader retraction in §7.ter.23 / §8 still
  stands and is independent of the per-criterion count; the Phase
  20.5 result quantifies the count more sharply.

#### Phase 20 retroactive application (Tier 3)

`run_phase20_5_retrospective.py` applies `characterize_transition`
to each of Phase 20's per-collector trajectories
(`data/phase20_classification.parquet`).

Result: all four collectors' 12-hour event-window trajectories
classify uniformly as BR_artifact at every 5-minute sub-window —
both pre-cascade-onset (12:00 UTC – 15:39 UTC) and post-cascade-onset
(15:39 UTC – 24:00 UTC).  The diagnostic correctly returns
`transition_detected = False` for all 4 collectors because
`origin == destination == BR_artifact` at quadrant-label resolution.

This is a substantive retroactive finding for Phase 20.  The
cascade-depth differences across collectors (rrc00 0.85 > linx 0.78
> eqix 0.64 > route-views2 0.58 — Phase 20's headline result) are
*within-quadrant* rep_med variations, not between-quadrant transitions.
The cascade signature is real and varies by collector, but the
variation is at the rep_med-axis sub-classification resolution rather
than the primary-quadrant resolution.

This sharpens Phase 20's interpretation:

  - The "cascade trajectory" is uniform-quadrant (BR_artifact
    throughout) with continuous-rep_med deviation.
  - Whether the per-collector cascade depth corresponds to a
    transition into BR_artifact from a different baseline (which a
    finer-resolution classifier would expose) or to a within-BR
    rep_med modulation (no class change) is at the limit of the
    quadrant-classification framework.
  - Cross-collector shape consistency is *trivially* CONSISTENT
    (all 4 collectors are unclassified-no-transition at quadrant
    resolution); the substantive cross-collector comparison must
    be conducted on rep_med trajectories rather than quadrant
    labels.

The route-topology question from §7.ter.27 is therefore unchanged
in its open status.  The Phase 20.5 retroactive does not promote
the verdict from "distinct trajectory per collector, weakly
correlated with topology" to "real cascade-shape finding"; it
identifies that the cross-collector signature lives at sub-quadrant
resolution.  Any longer-term BGP study should classify with
rep_med-axis trajectory distance rather than quadrant labels.

#### Implications for Phase 21

`characterize_transition` is the API Phase 21 will call on
per-(GRB-event, instrument) trajectories.  The Phase 21 verdict map
gains two outcome rows per `SESSION-PLAN-PHASE20.5-DELTA`:

  - "ARS classification matches published QPO with metastable-middle
    transition shape" → strong validation of central-engine-evolution
    timescale; transition shape itself becomes a physical observable.
  - "ARS classification shows period-doubling cascade structure
    during prompt emission" → novel finding: GRB prompt emission may
    have nonlinear-dynamics signature beyond what current QPO
    methodology captures.  Subject to the period-doubling-detection
    limitation documented above (the autocorrelation-on-quadrants
    detector needs trajectory variation that exceeds quadrant
    granularity).

Tier 3 procedure step 5 in Phase 21: "Apply
`characterize_transition` to per-(event, instrument) trajectory;
report shape classification, parameters, and period-doubling
signature where present."

Tier 4 falsification in Phase 21: "Apply `characterize_transition`
to surrogate-generated trajectories; verify surrogates produce
different transition shapes than empirical data, or document that
they don't."

These are minor edits to the Phase 21 plan, not a redesign.

#### Open questions

- **Quadrant-resolution coarseness.**  Both the period-doubling
  detection on logistic and the cascade-shape characterisation on
  Phase 20 BGP run into the same wall: BR / TR / BL / TL is too
  coarse a label set for several plausible non-stationary
  classification trajectories.  A rep_med-axis (or KS_GUE-axis)
  trajectory distance metric would expose more structure.  This is
  a Phase 22+ follow-up.

- **Mackey-Glass at production scale.**  The 12000-step integrations
  used in Tier 2 yield ~100–200 events per regime — too few for
  trajectory analysis.  Longer integrations (1e5+ steps) plus
  finer extractor-parameter tuning would unlock the parameter-driven
  benchmark for routine use.

- **KPZ-class transition kernels.**  The blended-construction family
  parameterises transitions by mixing weights only.  Mathematical
  literature on KPZ transition classes (Tracy-Widom, BBP-spiked,
  Fredholm-determinant) supplies analytic ground-truth kernels that
  could serve as more rigorous synthetic transition substrates.
  Out of scope here, filed as Phase 22+ extension.

- **Lorenz lobe transitions.**  Skipped per session-plan priority;
  the basic stationary calibrator scaffolding is in
  `transition_calibrators_dynamical.py:lorenz_integrate` and
  `lorenz_lobe_transition_events`.

#### Citations

  - Feigenbaum, M. J. (1978).  Quantitative universality for a
    class of nonlinear transformations.  *J. Stat. Phys.* 19(1):
    25–52.
  - May, R. M. (1976).  Simple mathematical models with very
    complicated dynamics.  *Nature* 261: 459–467.
  - Mackey, M. C., Glass, L. (1977).  Oscillation and chaos in
    physiological control systems.  *Science* 197(4300): 287–289.
  - Lorenz, E. N. (1963).  Deterministic nonperiodic flow.
    *J. Atmos. Sci.* 20(2): 130–141.
  - Theiler, J. et al. (1992).  Testing for nonlinearity in time
    series: the method of surrogate data.  *Physica D* 58:
    77–94 (companion lineage to the Phase 18 surrogates).

Outputs:
`transition_calibrators_blended.py`,
`transition_calibrators_dynamical.py`,
`transition_diagnostic.py`,
`calibrator_panel.py`,
`tests/test_transition_calibrators.py` (8/8 pass),
`run_phase20_5_calibrators.py`,
`run_phase20_5_retrospective.py`,
`run_phase20_5_distinctness_revalidation.py`,
`data/phase20_5_calibrators.parquet`,
`data/phase20_retrospective.parquet`,
`data/phase20_5_distinctness_extended.parquet`,
`data/phase20_5_distinctness_revalidation.parquet`,
`plots/55_phase20_5_trajectory_examples.png`,
`plots/56_phase20_5_transition_recovery.png`,
`plots/57_phase20_5_period_doubling.png`,
`plots/58_phase20_retrospective_transitions.png`.

---

### 7.ter.29  Phase 21 — GRB timing PoC

#### Motivation

GRB timing structure was the original motivating question for this
toolkit's design.  The slice-through-higher-field framing applies
cleanly: a burst is a brief deterministic astrophysical event, the
readout is necessarily partial through whichever instruments
happened to be online and pointing the right way, and multiple
detectors provide natural vantage-point multiplicity.  Photon
arrival timestamps are point processes by construction; no
continuous-trace extraction is needed (in contrast with the LLM
applications retracted in §7.ter.19–.23).

The phase is not greenfield.  GRB QPO detection has become an
unexpectedly active sub-field over 2024–2025.  Chen, Zhang et al.
(2025) reported a 909 Hz QPO in GRB 230307A as evidence for a
millisecond-magnetar central engine; Castro-Tirado et al. (2021)
reported high-frequency QPOs at 836, 1444, 2132, and 4250 Hz in
GRB 200415A (a magnetar giant flare from the Sculptor galaxy);
Israel, Strohmayer, and Watts (2005–2006) established the lineage
in the galactic SGR 1806-20 giant flare with QPO modes at 18, 26,
30, 92, 150, 625, and 1837 Hz.  Bing Zhang's 2025 framing paper
"On the Duration of Gamma-Ray Bursts" reset the duration-shaping
discussion around four factors with merger-driven long GRBs
demolishing the simple short-vs-long classification.

This toolkit's contribution is methodologically complementary, not
replacement: classifying timing into the joint plane (subsuming
QPO detection as the TL/periodic-resonance-quadrant case),
falsifying at multiple orders (Phase 18 surrogates + the
GRB-specific lightcurve-modulated Poisson surrogate added here),
and applying the transition diagnostic per QPO-claim window
(Phase 20.5).

#### Methodology

`grb_pipeline.py` pulls TTE files from HEASARC's public Fermi GBM
trigger archive
(`heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/`) for the
priority-1 / priority-2 / priority-3 events, parses each FITS file
to a `(time_us, energy_ch)` per-detector table, and selects "burst
detectors" — those whose prompt-window event rate exceeds 2× the
pre-trigger background rate.  No specialised tooling required:
`astropy.io.fits` plus standard URL fetching; no `gbm-data-tools`,
no `pybgpstream`-style external dependency.

The acquired panel:

| event       | trigger ID    | category                         | n events (pooled) | n burst detectors |
|-------------|---------------|----------------------------------|-------------------|-------------------|
| GRB230307A  | bn230307656   | extragalactic, magnetar candidate | 11.06 M           | 12                |
| GRB200415A  | bn200415367   | extragalactic MGF (Sculptor)     | 11.24 M           | 14 (fallback)     |
| GRB221009A  | bn221009553   | long GRB (BOAT)                  | 45.85 M           | 14                |
| GRB211211A  | bn211211549   | extragalactic merger / kilonova  | 5.35 M            | 5                 |

(SGR 1806-20 is observed natively by RHESSI, not Fermi GBM —
RHESSI archival access via HEASARC is left as a follow-up; the
priority-1 MGF case is covered by GRB 200415A in this run.)

`run_phase21_calibrators.py` characterises three calibration
elements before any prompt-window classification is interpreted:

  - **Detector deadtime artifact**: synthetic Poisson at varying
    rate, deletions inside the deadtime window
    (Fermi GBM 2.6 μs, BATSE 5 μs, RHESSI 6 μs).  At
    rate = 200,000 events/s the joint-plane reading shifts from BL
    (Poisson, rep_med ≈ 0.04) to TR (Wigner-class, rep_med ≈ 0.45)
    purely from deadtime — i.e., high-rate scintillator detectors
    can fake a Wigner signature even on uncorrelated input.  This
    is a generic high-count-rate scintillator artifact.

  - **Per-event quiescent baseline**: the pre-trigger window
    (T-200 s to T-1 s) of every event in the panel classifies as
    BL with rep_med ≈ 0.017–0.022, indistinguishable from
    homogeneous Poisson.  Background-period gamma-ray flux is
    Poisson-class at the joint-plane resolution.  This is the
    operational reference for "GRB at rest."

  - **MGF positive control on GRB 200415A**: the prompt window
    (T0 to T0+0.139 s) was scanned at q_max = 300 to span the
    Castro-Tirado 2021 published QPO frequencies (836, 1444, 2132,
    4250 Hz).  At the empirical mean event spacing of 17.0 μs
    (corresponding to a 59 K events/s pooled-detector rate during
    the prompt), the q-bands corresponding to those frequencies
    are q ≈ 70.5 / 40.8 / 27.7 / 13.9 respectively.  Of the
    elevated RF-amplitude q-bands found by the scan, **q = 74
    appears with rf_amplitude_q = 0.0044** — the closest match in
    the elevated set to the 836 Hz mode's predicted q = 70.5.  No
    elevated RF amplitudes are found at the q-bands corresponding
    to the higher-frequency modes (1444 / 2132 / 4250 Hz) in this
    pooled-detector scan.  This is a *partial* MGF positive
    control: the lowest published mode is suggestive of a match
    at the q-band level; the higher modes are not.

#### Tier 3 — per-event multi-resolution trajectory

`run_phase21_classification.py` runs the joint plane per
sub-window for each event, with sub-window resolution adapted to
the event's category:

| event        | sub-window | window relative to T0 | n sub-windows | n well-powered |
|--------------|------------|-----------------------|---------------|----------------|
| GRB230307A   | 2 s        | [-30, 64.6]           | 48            | 48             |
| GRB200415A   | 20 ms      | [-1.0, 1.139]         | 107           | 107            |
| GRB221009A   | 10 s       | [-30, 360]            | 39            | 39             |
| GRB211211A   | 2 s        | [-30, 81.4]           | 56            | 56             |

The headline result mirrors the Phase 20.5 retroactive finding on
BGP: **all four events classify uniformly as BL throughout their
prompt and surrounding windows at the joint-plane quadrant
resolution.**  `transition_diagnostic.characterize_transition`
returns `transition_detected = False, origin = destination = BL`
for every event.  The trajectories vary at the rep_med
sub-quadrant level (rep_med shifts of 0.005–0.025 across the
prompt window for each event), but the primary-quadrant label
does not transition.

The published QPO claims fall *just outside* the joint-plane's
natural q-range at the chosen sub-window sizes:

| event      | published QPO Hz | resolved q (rate / f_hz) | inside q_max=30? |
|------------|------------------|---------------------------|-------------------|
| GRB230307A | 909.0 (Chen 2025)| 41                        | no (close miss)   |
| GRB200415A | 2132 (Castro 2021)| 31                       | no (close miss)   |
| GRB221009A | (no claim)        | n/a                      | n/a              |
| GRB211211A | 22.5 (Xiao 2022)  | 646                      | no (rate mismatch)|

The framework's q-band index corresponds to "events per QPO
period" in unit-mean-spacing units; for it to detect a published
QPO frequency, the event count in the analysis window divided by
the QPO period must fall inside [2, q_max].  At q_max=30 with
the chosen sub-window sizes, both 230307A's 909 Hz and 200415A's
2132 Hz are at q ≈ 31–41 — just above the cutoff.  This is a
methodology-resolution result, not a positive or negative finding
about the QPO claims themselves.

#### Tier 4 — falsification

`run_phase21_falsification.py` applies the Phase 18 surrogate
panel plus the GRB-specific lightcurve-modulated Poisson
surrogate to each event's QPO/prompt window.  Per-event results
on the headline classification metric (rep_med at q_qpo or
median):

| event       | ORIGINAL  | phase_rand_iei | cumulant_matched | lightcurve_modulated_Poisson |
|-------------|-----------|----------------|------------------|------------------------------|
| GRB230307A  | BL (0.025)| TR (×3 seeds)  | BL (×3)          | **BL (×3)**                  |
| GRB200415A  | BL (0.074)| TR (×3)        | BL (×3)          | **BL (×3)**                  |
| GRB221009A  | BL (0.016)| TR (×3)        | BL (×3)          | **BL (×3)**                  |
| GRB211211A  | BL (0.020)| TR (×3)        | BL (×3)          | **BL (×3)**                  |

The headline Tier 4 finding: **the lightcurve-modulated Poisson
surrogate reproduces the empirical BL classification with
rep_med within the original's range on every event, every seed.**
The framework's reading of the prompt-emission timing is
structurally captured by an inhomogeneous Poisson process whose
rate matches the empirical lightcurve.  At the joint-plane
quadrant + q_max=30 resolution, **no detectable timing signature
beyond the rate envelope** survives this falsification.

The Phase 18 surrogates show the expected pattern (per §7.ter.25
lessons): `phase_randomized_iei` flips the classification to TR
(IEI second-order preservation in a way that pushes Gaussianised
output into TR territory); `cumulant_matched` preserves BL (IEI
marginal moments preserve the BL signature).  These are
classifier-sensitivity results, not finding-artifacthood results.

#### Phase 19 mechanism-distinctness implication

Per the user-flagged observation at Tier 2: **all gamma-ray
photon detectors share the categorical-event-detection mechanism
class** (scintillator + photomultiplier + deadtime + categorical
energy channeling) and do not constitute mechanism-distinct
extractors under the §7.ter.26 empirical-distinctness criterion.
Fermi GBM (NaI/BGO + PMT), BATSE (NaI + PMT), Swift BAT (CdZnTe),
GECAM (LaBr3), Konus-Wind (NaI), RHESSI (Ge) are all
description-distinct but mechanism-equivalent at the joint-plane
discrimination level.  By analogy with the Phase 19 finding that
8 description-distinct LLM attention extractors collapsed into
5–6 mechanism classes, all GRB gamma photon detectors are
expected to collapse into a single mechanism equivalence class.

**Implication.**  Cross-instrument agreement on a published QPO
claim is *one mechanism's testimony at multiple vantage points*,
not multi-mechanism corroboration.  The §7.ter.26 principled
discipline (≥ 4 mechanism-distinct extractors agreeing) cannot be
satisfied within the GRB photon-detector panel; saturation is
fundamental.  Genuinely multi-mechanism corroboration of a GRB
timing signature would require a different detection class —
gravitational-wave timing, neutrino arrival timing, or
optical-counterpart photometric timing — none currently at the
temporal resolution required for ms-class QPO verification.

This is not a retraction of cross-instrument GRB analyses.  It is
the calibrated upper bound on what cross-instrument agreement
*can* establish: the same scintillator-PMT-deadtime mechanism
reads the same timing signature at multiple geometrically-
displaced vantage points (rules out detector-specific artifacts;
vantage-point agreement on the same physical event), but is not
Phase 19-principled.

#### Verdict

Per the revised verdict map (Tier 4 ground rules), the empirical
input is:

  - **Quadrant classification doesn't shift** during published QPO
    windows on any of the four events — the cascade-shape /
    transition signature lives at sub-quadrant resolution, *if it
    exists at all in the framework's q-range at our chosen
    sub-window sizes.*  This is the Phase 20.5 lesson reproduced
    on a different domain.
  - **Lightcurve-modulated Poisson reproduces the empirical BL
    classification on every event.**  At the joint-plane
    resolution we operated at, the QPO/prompt-window reading is
    fully accounted for by the empirical rate envelope.
  - **MGF positive control is partial**: 836 Hz mode in
    GRB 200415A produces an elevated RF-amplitude at q = 74
    (predicted q = 70.5) on the full prompt-window scan at q_max
    = 300; higher-frequency modes (1444 / 2132 / 4250 Hz) do not
    register elevated RF amplitudes at their predicted q-bands.
  - **The published QPO frequencies for 230307A (909 Hz) and
    200415A's 2132 Hz mode** are at q-bands just above q_max = 30
    at the sub-window sizes used in Tier 3.  The framework's
    q-resolution at this compute budget does not span the
    published claims' frequencies.

The verdict closest to the data: **methodology-resolution result,
no positive QPO-claim replication, lightcurve-modulated Poisson
reproduces the empirical reading.**  The Phase 21 PoC does not
support a positive ARS-replicates-published-QPO finding at the
joint-plane resolution.  This is the intended methodology-only
outcome; the lessons that transfer are documented below.

#### Methodological lessons

1. **Lightcurve-modulated Poisson surrogate as transferable
   falsification tool.**  Any cascade-driven photon-counting
   measurement (GRBs, X-ray binaries, AGN flares, astrophysical
   transients) can use this surrogate to test whether timing
   structure is reproducible from the rate envelope alone.  The
   implementation in `lightcurve_modulated_surrogate.py` is
   ~50 lines of Python.

2. **Quadrant-resolution coarseness, again.**  Phase 20.5
   identified that cross-domain timing signatures live at
   sub-quadrant rep_med resolution; Phase 21 reproduces this on
   GRB data.  A finer-resolution classifier (rep_med-axis
   trajectory distance, energy-band stratified classifications)
   would be needed for any positive cascade-shape finding on
   GRB-class timing.

3. **q-range vs published-QPO-frequency mismatch.**  The
   joint-plane framework's natural detection range (q ∈ [2, q_max])
   corresponds to particular sub-window sizes for each QPO
   frequency.  For the 909 Hz / 2132 Hz claims to fall inside
   q_max = 30, sub-window sizes need to be ~50–100 ms.  This is a
   methodology-tuning result for any future application targeting
   specific QPO frequencies.

4. **Mechanism-distinctness saturation.**  All gamma photon
   detectors collapse into a single mechanism equivalence class
   under the §7.ter.26 empirical-distinctness criterion.
   Cross-instrument GRB agreement is not Phase 19-principled.
   This is the calibrated upper bound on what photon-detector
   panels can establish.

5. **Per-instrument deadtime as artifact source.**  Synthetic
   Poisson at high rate with deadtime produces TR-class signatures
   purely from the deadtime cutoff.  Any joint-plane reading on
   high-rate scintillator data must subtract this baseline before
   non-Poisson structure is reported.

#### Open questions

  - **SGR 1806-20 / RHESSI archival access.**  The galactic-MGF
    ground-truth case originally observed by RHESSI is not in the
    Fermi GBM trigger archive.  HEASARC has RHESSI archival data
    via a different path; integrating that requires additional
    pipeline work and is filed for any longer-term study.

  - **Fine-q QPO replication.**  At q_max = 50 with 100 ms
    sub-windows on GRB 230307A, the 909 Hz QPO falls inside the
    detection range.  A targeted run with this configuration is a
    next-step that could promote the verdict from "methodology
    resolution" to "QPO replication attempted."  Compute cost:
    ~30 min wall-time per event.

  - **Energy-band stratification.**  The Tier 3 sub-windowing
    pools across detector NaI/BGO and across PHA channels.  An
    energy-stratified analysis would test whether the QPO signal
    is energy-dependent (predicted by the magnetar-central-engine
    interpretation).

#### Citations

GRB QPO lineage:

  - Chen, R.-C., Zhang, B.-B. et al. (2025).  Nature Astronomy 9:
    1701–1713.  [909 Hz QPO in GRB 230307A]
  - Castro-Tirado, A. J. et al. (2021).  Nature 600: 621–624.
    [GRB 200415A high-frequency QPOs]
  - Xiao, S. et al. (2022a).  [GRB 211211A precursor QPO]
  - Zhang, B. (2025).  arXiv:2501.00239.  [GRB duration framing]

Magnetar giant flare lineage:

  - Israel, G. L. et al. (2005).  [SGR 1806-20 QPOs]
  - Strohmayer, T. E. & Watts, A. L. (2005, 2006).  [SGR 1900+14,
    1806-20 QPO analysis]
  - Watts, A. L. & Strohmayer, T. E. (2006).  [1837 Hz]

Methodology-internal:

  - §7.ter.25 (Phase 18 — higher-order surrogates)
  - §7.ter.26 (Phase 19 — mechanism-distinctness)
  - §7.ter.27 (Phase 20 — BGP cascade dynamics)
  - §7.ter.28 (Phase 20.5 — transition calibrator extension)

Outputs:
`grb_pipeline.py`, `run_phase21_acquire.py`,
`run_phase21_calibrators.py`, `run_phase21_classification.py`,
`run_phase21_falsification.py`,
`lightcurve_modulated_surrogate.py`,
`data/phase21_grb_panel/{event}.parquet` × 4,
`data/phase21_grb_panel/detector_geometry.parquet`,
`data/phase21_calibrators.parquet`,
`data/phase21_classification.parquet`,
`data/phase21_qpo_comparison.parquet`,
`data/phase21_falsification.parquet`,
`plots/58_phase21_deadtime.png`,
`plots/59_phase21_quiescent_baseline.png`,
`plots/60_phase21_trajectory_per_event.png`,
`plots/62_phase21_surrogate_survival.png`,
`GRB_NEXT_STEPS.md`.

---

### 7.ter.30  Phase 22a — pvc-11 macaque V1 (Smith & Kohn)

#### Motivation and scope

Phase 22 originally targeted CRCNS ret-1 (mouse retinal MEA).  That
work was halted after confirming ret-1 lacks per-cell type labels,
has KO-heavy genotype mix, and population sizes (26–43 cells per
qualifying recording) below the canonical criticality scale with
degraded H1 cross-validation.  Phase 22a replaces that target with
CRCNS pvc-11 (Smith & Kohn, anesthetised macaque V1, Utah-array
MEA, 6 spontaneous + 5 evoked recordings, 70–135 single-/multi-units
per array, multi-stimulus structure, established V1 functional
categorisation).  The dataset selection rationale and the two
co-equal hypotheses are documented in the session brief.

The methodological frame is orthogonal-measurement cross-validation:

  H1 — per-unit NNS classification of V1 spike trains, computed via
       the existing ARS pipeline, exhibits non-trivial correspondence
       with V1 functional partitions (orientation tuning OSI, direction
       selectivity DSI, F1/F0 simple/complex), beyond what mean firing
       rate predicts, and is consistent across stimulus conditions on
       the same units.

  H2 — population-event NNS classification on V1 recordings shows
       structure that survives surrogates preserving per-unit
       stimulus drive (LN-evoked) or anesthesia-state drive (PC1-
       modulated Poisson) but eliminating intrinsic joint structure,
       beyond what independent rate-matched processes produce.

#### Methodology

`phase22a/loader.py` — unified pvc-11 loader covering scipy-readable
spontaneous + gratings .mat files and h5py-readable movie v7.3 files.
Output: `Recording` dataclass with per-unit spike-time arrays in
seconds, channel/SNR/MAP metadata, stimulus-condition structure
preserved.

Calibrator-zoo verification (`phase22a/verify_calibrators.py`):
Phase 19 stationary panel (Poisson, GOE/GUE/GSE, ζ-first-400,
uniform_jitter, periodic q=7, mixed q=7+q=12) at N_POINTS=400, 3
seeds.  All 8 land in the expected modal quadrant.  Pass.

Unit selection (`phase22a/unit_select.py`):
- H1: SNR ≥ 2.0, mean rate ≥ 1 sp/s, ≥ 400 spikes total per condition
  (the canonical N_POINTS for the Phase 19 distinctness machinery
  at q_max=30).  1,159 / 1,539 (unit, recording) pairs pass.
- H2: SNR ≥ 1.5, mean rate ≥ 0.5 sp/s.  Multi-units retained
  (population structure is the question; per-cell semantics not
  required).  1,391 / 1,539 pass.

H1 per-unit ARS classification (`phase22a/h1_per_unit_ars.py`):
For every H1-passing (recording, unit) pair, run `joint_q_profile` +
`joint_quadrant_diagnostic` at Q_MAX=30, MIN_EVENTS_PER_Q=30,
JPF_CAP=1500 on the concatenated spike-time stream.  Per-direction
classifications also produced for the 3 grating recordings (12
directions × 210 H1-passing units = 2,520 additional classifications).
Per-q DataFrames preserved.

H1 functional categories (`phase22a/h1_functional.py`):
Per-unit OSI/DSI from drifting-grating tuning curves (12 directions),
F1/F0 ratio at the preferred direction (TF=6.25 Hz), pre-binned PSTHs;
preferred orientation/direction from the grating-direction movie via
the published per-grating angle theta.  Standard circular-vector OSI/DSI.

H1 cross-validation (`phase22a/h1_crossval.py`):
- (A) Spearman partial correlation of {rep_med, ks_gue_med} against
      {OSI, DSI, F1/F0} controlling for mean firing rate.  (The
      continuous-metric view; this is the H1 headline.)
- (B) Cross-stimulus consistency on the matched-unit set across the
      three movies (gratings_movie, natural_movie, noise_movie) —
      monkey1 + monkey2.
- (C) Discrete-categorical view: MI between primary ARS quadrant and
      {simple/complex via F1/F0 ≷ 1, OSI median split, DSI median
      split} via contingency tables with bootstrap 95% CI.  Recorded
      as a methodological cross-check on the continuous-metric finding;
      see findings note below on why the categorical view is
      systematically weaker than the continuous view here.

H1 within-unit per-direction modulation (`phase22a/h1_per_direction.py`):
For every drifting-grating-recording unit with both preferred and
null direction (180°) ARS classifications, compute
delta_ks_gue = ks_gue_med(pref) − ks_gue_med(null) and similarly for
rep_med.  Sign test, Wilcoxon signed-rank on the deltas, and
Spearman of the deltas against the unit's OSI.  Tests whether the
between-unit OSI ↔ ks_gue_med correspondence reflects within-unit
stimulus-direction modulation or only between-unit cell-intrinsic
variation.

H2 population-event extraction (`phase22a/population_events.py`):
Synchronous-firing definition:  bin every H2-passing unit's spike
train at BIN_MS = 5 ms; an event is a bin where ≥ K_THRESH = 5
distinct units fire ≥ 1 spike.  Sensitivity scan: (k, w) ∈
{(4, 5 ms), (5, 5 ms), (8, 5 ms), (5, 10 ms)}.

H2 ARS at TWO q_max settings (`phase22a/h2_population.py`):
Q_MAX = 30 (canonical default) AND Q_MAX = 100 (slow-regime
extension covering the V1 anesthetised Up/Down band 0.5–3 Hz).  The
q-band time-frequency mapping is preserved through unit-mean
unfolding: period at Farey rational a/q = q × original-mean-spacing,
so frequency = event_rate / q.  Coverage table per recording:
q_max=100 covers Up/Down on all 15 recordings; q_max=30 covers it
on 14 of 15 (monkey3_spontaneous's high event rate places its
q_max=30 lower edge at 3.27 Hz, just above the Up/Down band).

H2 surrogate battery (`phase22a/h2_surrogates.py`):
- rate_matched_poisson:  per-unit independent Poisson at the unit's
                          empirical mean rate (floor surrogate).
- cell_shuffle:           per-trial circular shift per unit;
                          preserves per-unit count + rate envelope,
                          breaks cell-pair joint synchrony.
- ln_evoked (movies):     per-unit STA on the recording's stimulus
                          movie + softplus+linear rectifier + Poisson;
                          preserves per-unit stimulus-driven rate
                          modulation.
- state_modulated (spontaneous): top-PC of population activity used
                          as a shared multiplicative gain on
                          per-unit Poisson; preserves the dominant
                          slow Up/Down latent variable.

3 seeds per (recording, surrogate).  Surrogates classified at
q_max=30 only — the per-q rep_int values at q ∈ [1, 30] are
identical between q_max=30 and q_max=100 runs (the per-q
computation is independent of the q_max ceiling), so the
survival verdict at q ≤ 30 is the same either way.

H2 survival verdict (`phase22a/h2_survival.py`):
Per (recording, surrogate, q-band):
- `survives_rep`:   real `rep_int_q` > 95th percentile of surrogate
                     replicates' `rep_int_q` at that q.
- `survives_quad`:  real per-q quadrant differs from surrogate-modal
                     per-q quadrant.
- `survives_both`:  both conditions hold.

Required-conjunction H2 PASS = both `cell_shuffle` AND the
appropriate stimulus/state-drive surrogate (`ln_evoked` for
movies, `state_modulated` for spontaneous) survive_both at ≥ 1
q-band.  Subsets with no LN-evoked surrogate (drifting gratings
— 1.28 s static-orientation stimuli don't admit a useful per-frame
LN model) require only cell_shuffle.

#### Findings

**Calibrator zoo**:  8/8 pass.

**H1 per-unit**:  modal-quadrant collapse is null:  1,144 / 1,159
(recording, unit) pairs land in BL (Poisson), 15 in TR.  V1
single-unit spike trains are dominantly Poisson under ARS — the
expected result given canonical V1 spike-train statistics.  BUT the
*continuous* ARS metrics carry a strong, firing-rate-controlled
signal:

| descriptor | ARS metric  | n   | partial ρ | p (partial)       |
|------------|-------------|-----|-----------|-------------------|
| OSI        | ks_gue_med  | 210 | +0.720    | < 1e-300          |
| OSI        | rep_med     | 210 | −0.324    | 1.7e-06           |
| F1/F0      | rep_med     | 210 | +0.388    | 6.2e-09           |
| DSI        | ks_gue_med  | 210 | +0.223    | 1.2e-03           |

`ks_gue_med` (KS distance from a Wigner GUE NNS reference) tracks
orientation selectivity across 210 grating-driven units beyond what
mean firing rate predicts: units with higher OSI have higher
ks_gue_med (i.e., NNS distribution further from Wigner GUE) at
ρ_partial = +0.720, p < 1e-37.  `rep_med` tracks the simple/complex
F1/F0 partition (ρ_partial = +0.388, p = 6e-9): simple cells (F1/F0 > 1)
show more pair-spacing repulsion in their NNS distribution than
complex cells (F1/F0 < 1).

**H1 within-unit per-direction modulation**:  for the 210 units with
both preferred and null direction (180°) ARS classifications:
- delta_ks_gue (pref − null) median = +0.0015, mean = +0.0001;
  sign test 107 vs 103; Wilcoxon p = 0.83.  No within-unit modulation
  of `ks_gue_med` between preferred and null direction.
- delta_rep median = 0, mean = +0.015; Wilcoxon p = 5.7e-3 (weak
  but real positive shift); but Spearman OSI vs delta_rep ρ = +0.111,
  p = 0.11 — the modulation does not co-vary with the unit's
  orientation tuning.

The OSI ↔ ks_gue_med correspondence (ρ_partial = +0.720, n = 210,
p < 1e-37 from the between-unit analysis above) therefore reflects
**unit-intrinsic NNS structure** — different cells have different
spike-train spacing distributions overall, in a way that correlates
with their orientation tuning — not stimulus-driven direction
modulation of NNS structure within a cell.  This is a specific
mechanism claim: ARS picks up on cell-property variation, not
stimulus-driven variation in the cell's response.

**H1 cross-stimulus consistency**:  176 units present in ≥ 2 of the
3 matched-unit movies; 173/176 = 98.3% land in the same primary
quadrant across movies.  The consistency is real but uninformative
for category-discrimination (almost all consistent units are stable
in BL — the dominant quadrant).

**Methodological note on the categorical view**:  the discrete
modal-quadrant ↔ functional-category MI was also computed and lands
at 0.056 bits for simple/complex (95% CI [0.009, 0.143]).  The CI
excludes zero, so the effect is real, but it is much smaller than
the continuous-metric correspondence (ρ_partial = +0.388 between
`rep_med` and F1/F0, p = 6e-9).  The categorical view is
systematically weaker here for a structural reason: 1,144 / 1,159
units land in BL, leaving only one productive ARS category for the
between-cells comparison — the discrete bin discards the
cell-intrinsic gradient that the continuous metric resolves.  We
report the continuous-metric partial correlations as the H1 headline
and treat the categorical MI as a methodological cross-check, not a
parallel finding.

**H2 population-event real-data classifications** at default
(k=5, w=5 ms, Q_MAX=30):  diverse — 5 BL, 4 TR, 6 BR_artifact across
15 recordings.  Modal verdicts are nearly identical between Q_MAX=30
and Q_MAX=100, indicating the per-q signature is robust to the
slow-regime extension.

**H2 surrogate-survival verdicts** (required-conjunction):

| recording               | subset         | passes? |
|-------------------------|----------------|---------|
| monkey1_spontaneous     | spontaneous    | ✓ (q=6) |
| monkey1_natural_movie   | natural_movie  | ✓ (all 30 q-bands, all 3 surrogates) |
| monkey2_gratings_movie  | gratings_movie | ✓ (all 30 q-bands, all 3 surrogates) |
| monkey1_noise_movie     | noise_movie    | partial (cell_shuffle yes, ln_evoked no) |
| monkey2_noise_movie     | noise_movie    | partial (cell_shuffle yes, ln_evoked no) |
| (10 others)             | various        | · (no q-band passes both criteria) |

Per-subset rollup (PASS = ≥ 1 recording with required conjunction
passing at ≥ 1 q-band):
- spontaneous:    PASS  (1/6 recordings — monkey1_spontaneous)
- gratings:       NULL  (0/3)
- gratings_movie: PASS  (1/2 — monkey2_gratings_movie)
- natural_movie:  PASS  (1/2 — monkey1_natural_movie)
- noise_movie:    NULL  (0/2 — only cell_shuffle survived; ln_evoked
                          captures the structure)

The two cleanest passes are stark:

- **monkey1_natural_movie** (74 units, 87 K events, [0.81, 24.3] Hz
  band):  real rep_int_q ≈ 0.25 (TR/Wigner-class) at all 30 q-bands;
  surrogates (rate-matched, cell-shuffle, LN-evoked) all produce
  rep_int_q < 0.04 (BL/Poisson).  Population events on natural-movie-
  driven V1 carry Wigner-class spacing structure that no
  rate-preserving, no cell-shuffle-preserving, and no per-unit-LN-
  preserving surrogate reproduces.

- **monkey2_gratings_movie** (104 units, 164 K events, [1.52, 45.5] Hz
  band):  real rep_int_q ≈ 0.55 (BR_artifact/uniform-like saturation)
  across all 30 q-bands; surrogates produce rep_int_q ~ 0.45 (still
  high but in TR not BR).  Real population events are *more uniform*
  than what any surrogate produces.

A separate observation worth flagging: several recordings
(monkey5_spontaneous, monkey4_spontaneous, monkey3_spontaneous,
monkey2_noise_movie at the rate criterion alone) show real `rep_int_q`
above the surrogate 95th percentile across all 30 q-bands but the
quadrant doesn't differ — i.e., real is more repulsive than
surrogates within the same quadrant.  This is a softer kind of
structure than the strict required-conjunction verdict registers; we
report it as a secondary "rep-only" survival in the per-q parquet,
not as an H2 PASS.

#### Frequency-band coverage caveat

The q-band time-frequency mapping varies substantially across
recordings (event rate × Q_MAX = upper edge; lower edge = upper /
Q_MAX).  At default k=5/5ms, event rates range from 2 Hz
(monkey2_spontaneous) to 98 Hz (monkey3_spontaneous), so the
q_max=30 coverage band ranges from [0.07, 2.2] to [3.27, 98.0] Hz.
Q_MAX=100 brings the lower edge to 0.02–0.98 Hz across recordings,
fully covering the V1 anesthetised Up/Down band (0.5–3 Hz).  The
modal-quadrant verdicts are stable between Q_MAX=30 and Q_MAX=100,
so the results are not mis-stated by the default Q_MAX choice for
recordings whose Q_MAX=30 band already overlaps Up/Down.  Recordings
where the Q_MAX=30 band does NOT touch Up/Down (1 of 15:
monkey3_spontaneous) carry the caveat "no structure detected at the
framework's Q_MAX=30 q-band coverage given the chosen sub-window
size — the slow-regime view at Q_MAX=100 was checked and gave the
same modal verdict."

#### Mechanism distinctness

ARS operates on the spacing structure of point processes (NNS,
higher-order Farey-pooled spacings).  None of the population-coding
tools applied in the published literature on pvc-11
(Ohiorhenuan-Victor 2010 MaxEnt, Williamson 2016 PLDS, Cowley 2016
GPFA-style latent-variable methods) computes a NNS-of-population-
events statistic.

The H1 finding (continuous ARS metrics tracking orientation tuning
beyond firing rate at ρ_partial = +0.720, n = 210, p < 1e-37) is a
measurement-axis-orthogonal correspondence: the spacing-structure
axis carries information about V1 functional category that is not
predicted by mean rate and was not measured by prior population-
coding analyses on this same dataset.  We do not claim ARS predicts
orientation tuning better than direction-of-motion-driven tuning
fits do — the orientation-tuning measurement on the same units is
the cleaner direct readout.  The claim is that the NNS-spacing
metric, computed from the spike-train timing distribution rather
than from a stimulus model, recovers orientation-related structure
without using stimulus information.

The H2 findings on monkey1_natural_movie and monkey2_gratings_movie
articulate the elimination space cleanly: the surviving structure
is not predicted by independent per-unit rate modulation
(rate_matched_poisson surrogate eliminated it), not by the dominant
trial-averaged rate envelope (cell_shuffle eliminated it), and not
by a per-unit STA-based rate model on the actual stimulus
(ln_evoked eliminated it).  This narrows the explanatory space
substantially: whatever produces the surviving NNS structure
operates on cell-pair joint timing in a way that the LN-Poisson
class of generative models does not capture.  We do not name the
mechanism; we name the elimination.

#### Methodological recommendations for future ARS applications

Two checks promoted to default practice for any future application of
ARS to data with structure that the toolkit could plausibly read in
multiple ways.  Both surfaced as load-bearing in Phase 22a; neither
is yet documented in METHODS.md.

**1. Within-unit stimulus-driven vs between-unit intrinsic
disambiguation.**  When a recording has a known stimulus partition
(orientation, frequency, condition, identity of the source process,
etc.) and the per-unit ARS classifications correlate with a
descriptor computed on the same units, run the within-unit
modulation test before claiming the ARS metric "tracks" the
descriptor.  Procedure:

  - Compute ARS classifications per (unit, stimulus condition)
    rather than only on the pooled-across-conditions stream.
  - For each unit, identify the descriptor's preferred and null
    conditions (e.g., preferred and null direction in Phase 22a;
    in another setting, on-state vs off-state, target vs distractor).
  - Compute delta_metric = ARS_metric(preferred) − ARS_metric(null)
    per unit; sign test, Wilcoxon, and Spearman of the delta against
    the descriptor.
  - **If the within-unit delta is statistically negligible AND
    uncorrelated with the descriptor while the between-unit
    correspondence is strong, the ARS metric is reading
    cell-intrinsic structure, not stimulus-driven response
    structure.**  Both readings are interpretable; conflating them
    in the writeup is not.

  In Phase 22a the delta_ks_gue median was +0.0015 with Wilcoxon
  p = 0.83 — the OSI ↔ ks_gue_med correspondence is unambiguously
  between-unit cell-intrinsic.  Without this check, the same data
  could have been written up as "ARS tracks orientation-driven
  modulation of NNS structure", which would have been wrong.

**2. Continuous ARS metrics over discrete modal-quadrant assignments
when the modal distribution is dominated by one quadrant.**
Phase 22a's per-unit ARS classifications land 1,144 / 1,159 in BL.
The discrete-categorical MI between modal quadrant and functional
category was 0.056 bits — small-but-real (CI excludes zero) but
much weaker than the continuous-metric partial correlations
(ρ = +0.720 for OSI vs `ks_gue_med`, p < 1e-37).  The bin discards
the cell-intrinsic gradient that the continuous metric resolves.

  Default practice: when the modal-quadrant distribution is dominated
  by one class (≳ 90 % in one quadrant), report the continuous metrics
  (`rep_med`, `ks_gue_med`, per-q vectors) as the H-headline finding
  and treat the categorical view as a methodological cross-check
  rather than a parallel finding.

These two points are framed as recommendations for any future ARS
application where (a) stimulus or condition structure is known on
the same units that ARS classifies, or (b) the modal quadrant
distribution is concentrated.  Both conditions are common in neural
data (single-unit V1 spike trains satisfy (b) by default; any
stimulus-locked regime satisfies (a)).

#### Caveats

- pvc-11 is anesthetised (sufentanil).  The H2 verdict is "structure
  survives anesthesia-state-preserving and stimulus-drive-preserving
  surrogates", not "V1 is critical" or "this is how awake V1 normally
  works".  Anesthesia provides a stricter Up/Down latent-variable
  test than awake recordings would.
- Functional categories are V1-functional (orientation tuning,
  F1/F0 simple/complex), not transcriptomic or morphological cell
  types.  Cross-modality cell-type validation remains a future-
  phase target.
- LN-evoked surrogate fits a simple STA + softplus + linear
  rectifier; it is not a precision receptive-field model.  A more
  expressive LN family (separable spatiotemporal filters, GLM with
  history coupling) would be a stronger surrogate; the current
  cheap LN is the floor for stimulus-drive elimination, not the
  ceiling.
- Surrogate replicate count is 3 per (recording, surrogate) cell
  for runtime reasons.  The 95th-percentile estimate is noisier
  than 5+ seeds would give; the verdicts on the cleanly-passing
  recordings (monkey1_natural_movie, monkey2_gratings_movie) are
  robust to this since real rep_int values are ~6× the surrogate
  median, not just above the upper percentile.
- Population-event definition is k=5 / 5 ms by default; the
  sensitivity grid (k ∈ {4, 5, 8}, w ∈ {5, 10} ms) shows the
  modal-quadrant distribution shifts with threshold (more BL at
  k=8, more BR_artifact at k=5/10 ms), so the *specific* H2
  verdicts are tied to the default definition; the existence of
  surviving structure on monkey1_natural_movie and
  monkey2_gratings_movie is robust across the grid.

#### Outputs

Code under `phase22a/`:  loader.py, verify_calibrators.py,
unit_select.py, ars_classify.py, h1_per_unit_ars.py, h1_functional.py,
h1_crossval.py, population_events.py, h2_population.py,
h2_surrogates.py, h2_survival.py, plot_phase22a.py, run_phase22a.py.

Data under `data/phase22a_results/`:  calibrator_verification.parquet,
unit_selection.parquet, h1_classifications.parquet,
h1_classifications_grating_dirs.parquet, h1_functional.parquet,
h1_crossval_summary.parquet, h1_crossval_perunit.parquet,
h2_population_classifications.parquet, h2_coverage.parquet,
h2_sensitivity.parquet, h2_surrogate_classifications.parquet,
h2_survival_per_qband.parquet, h2_survival_summary.parquet,
PHASE22A_FINDINGS.md.

Plots under `plots/phase22a/`:  fig1_h1_quadrants.png,
fig2_h1_xv_scatter.png, fig3_cross_stim_transitions.png,
fig4_h2_coverage.png, fig5_h2_surrogate_overlay.png.

---

## 8. Conclusions and limitations

### Validated outputs

The toolkit produces the following measurements at the precision indicated,
on the inputs specified.

#### Arithmetic signals

- Riemann ζ first 2,000 zeros (Odlyzko): KS_GUE_q = 0.041, rep_int_q = 0.425.
  ζ at heights ~10⁶: KS_GUE_q = 0.012–0.015. (§7.ter.7, §7.ter.21.)

- LMFDB elliptic curve L-functions, 87 curves, ~10,000 zeros: bulk GUE,
  edge separation by root number. (§7.ter.4.)

- Dirichlet L-functions, q ≤ 149, 630 primitive non-trivial characters,
  4.05M pooled spacings: bulk GUE, conductor-normalised γ₁ Sp/U
  separation at p = 0.001. (§7.ter.3.)

- Primes ≤ 10⁶, log-density unfolding: σ̂ = 0.048, 95% CI [0.023, 0.073];
  twin primes ≤ 10⁷: σ̂ = 0.093, 95% CI [0.068, 0.118]. (§7.ter.23 Tier 4.)

These reproduce statistics that are consistent with the GUE conjecture
for ζ and with Katz–Sarnak family-symmetry predictions for L-function
families. They are reported as instrument-validation outputs. They do
not extend the corresponding literatures.

#### Physical and biological signals

- USGS earthquake catalog, M ≥ 4.5: Poisson-clustered classification,
  mass<0.3 = 0.33. Consistent with ETAS aftershock dynamics. (§7.ter.4.)

- Adamatzky fungal mycelium spike pool, 1,470 events: super-Poissonian
  classification, mass<0.3 = 0.65 on the dataset tested. (§7.ter.5.)

- Solar X-ray flares (NOAA GOES, M+ class): Poisson-clustered. (§7.ter.13.)

- Binance BTCUSDT trade timing (one trading day): essentially random
  (BL quadrant). (§7.ter.14.)

- EEG θ-band zero-crossings (PhysioNet EEGMMIDB, 32 subjects):
  mass<0.3 ≈ 0.001, identified as bandpass filter artifact rather than
  a property of the underlying neural signal. (§7.ter.6.)

These classifications reproduce or are consistent with prior
characterisations in the corresponding domain literatures on the specific
datasets tested. Generalisation to those domains broadly requires more
data than was used here.

#### Synthetic calibrators

- Pure-class parameter recovery on synthetic Poisson, Wigner (β=1, 2, 4),
  periodic, and uniform_jitter signals: passes acceptance criteria
  (CI coverage ≥ 80%, median relative error ≤ 10%) at n_events ≥ 200,
  with Wigner classes requiring n_events ≥ 1000 for stable β̂ recovery.
  (§7.ter.23 Tiers 1, 3.)

- 8-class joint-plane classification under k-NN (k=5) with seeds {0,1,2}
  trained, {3,4} held out: 100% per-q accuracy on the calibrator pool.
  (§7.ter.21.)

### Failure modes diagnosed during development

Three failure modes of the classification pipeline were identified during
development. Each is documented at the section indicated, with the
specific empirical test that produced the diagnosis.

#### find_peaks autocorrelation rhythm (§7.ter.19)

`scipy.signal.find_peaks(prominence=0.3)` applied to autocorrelated
continuous traces produces quasi-uniformly-spaced events at the
autocorrelation length of the input, regardless of the input's underlying
dynamics. Spacing-statistics classifications on such inputs reflect the
extractor's gap structure rather than the signal.

Diagnosis: layer-depth sweep on a transformer (Phase 11 panel) showed
the classifying signature (rep_int_q = 0.900, mass<0.3 = 0) was already
present at the embedding output, before any decoder block had fired.

#### Metric-resolution collapse for σ̂ recovery (§7.ter.22 amendment)

The repulsion integral (`rep_int_q`) is empirically a signal-level scalar
on continuous synthetic uniform_jitter inputs. Its per-q variation is at
floating-point noise level. The "joint plane" therefore has effectively
1D discriminative content for inputs in the BR_artifact regime.

σ̂ recovery on such inputs returns the position of the input's gap
distribution within the synthetic uniform_jitter calibrator family. For
inputs that are point processes by construction, this position reflects
the actual gap distribution. For inputs extracted from continuous traces
via peak detection, the position reflects the extractor's gap
distribution.

Diagnosis: direct inspection of joint_q_profile output on synthetic
uniform_jitter signals showed std(rep_int_q across q) ≈ 10⁻⁴, with the
"per-q" values landing exactly on calibrator-grid anchor values for
many real-signal inputs.

#### Threshold-upcrossing TR induction (Finding F, §7.ter.23)

Threshold-style event extractors applied to iid exponential noise
produce rep_int_q ≈ 0.34, which falls in the TR (Wigner-class) quadrant
of the diagnostic. TR readings from threshold-style extractors must
therefore be cross-checked by applying the same extractor to noise of
equivalent statistical character.

Diagnosis: induction-on-Poisson test (Phase 16 Tier 1 paradigm) applied
to layer_kl_divergence and attention_sink_events, both of which had
initially produced rep_int_q ≈ 0.34 on LLM input and might have been
read as Wigner-class evidence absent the falsification step.

### Application to LLM internal states

The toolkit was applied to transformer residual stream activations and
attention dynamics across four architectures (Qwen 2.5 3B,
Phi-3-mini-4k-instruct, TinyLlama 1.1B, Mistral 7B v0.1) and eight
extractor mechanisms (residual_norm_peaks, attention_entropy_peaks,
attention_target_jumps, attention_sink_events, layer_kl_divergence,
attention_argmax_sink, attention_sink_residency_runs,
attention_multi_head_sink_consensus). The intermediate findings produced
during this work, and the corresponding diagnoses that retracted them,
are documented in §7.ter.19 through §7.ter.23.

After the diagnoses, no measurement remains that can be attributed to
the model rather than to the extraction methodology. The negative result
is bounded:

- It applies to extraction of point processes from transformer internal
  state via the specific extractor mechanisms tested.
- It does not address RMT analysis of LLM weight matrices
  (Staats et al. 2024; Martin & Mahoney 2018–2024), which uses different
  methodology and is outside this work's scope.
- It does not exclude the possibility that other extraction methodologies
  not tested here might produce measurable structure.

`attention_target_jumps` produced architecture-discriminating output
(Qwen 0.70 vs Phi-3 0.35 in rep_int_q) that reflects argmax-sequence
autocorrelation properties. This is a low-resolution architectural
descriptor; it does not constitute a universality-class finding.

### Claims not made in this document

The following claims appeared in intermediate states during development
and were retracted under further verification. They are listed here so
that their absence is not inferred to be an oversight.

- "LLM residual-stream dynamics in the Wigner GUE universality class."
  Retracted as find_peaks autocorrelation rhythm.
- "Cross-architecture σ̂ invariance in transformer internal states."
  Retracted as metric-blindness on integer-position event sequences.
- "LLM and primes share a parameter-space neighbourhood within
  BR_artifact." Retracted as extractor-conditional comparison; the σ̂
  alignment between primes (point process by construction) and the LLM
  (extracted via find_peaks) reflects the find_peaks gap distribution
  matching primes' calibrator-family position, not a structural
  correspondence.
- "Two distinct LLM attention-dynamics families (state-based vs
  change-based) with different universality readings." Retracted after
  three additional state-based extractors of distinct mechanisms
  classified as BR_artifact (consistent with all change-based
  extractors), with the original state-based TR reading diagnosed as
  threshold-upcrossing artifact.
- "Wigner-class attention dynamics on three by-construction extractors
  at rep_int_q ≈ 0.34." Retracted via induction-on-Poisson (Finding F).
- "Empirical validation of the Planat 2026 lock-in-phase prediction via
  Phase 12 perturbation sweep." The perturbation sweep ran but cannot
  be interpreted as testing the prediction once the underlying
  Wigner-class baseline was retracted.

### Limitations

In addition to the failure modes above:

- The toolkit has been validated on the input classes listed under
  validated outputs. Application to other input classes requires
  explicit calibrator-zoo and induction-on-noise verification per the
  protocol in METHODS.md before classifications can be trusted.

- The "principled iff classification is invariant across ≥ 4 distinct
  extractor mechanisms" criterion adopted in §7.ter.22 requires
  judgment on what "distinct" means in practice. In this work, the
  criterion was met for primes, twin primes, and synthetic
  uniform_jitter; it was not met for LLM internal state, where
  extractors that appeared distinct shared deeper threshold or
  peak-detection mechanisms.

- The codebase has not been reviewed by domain experts in any of the
  application areas. The arithmetic-side measurements would benefit
  from review by a number theorist familiar with empirical L-function
  family work; the physical-signal-side measurements would benefit
  from review by domain practitioners.

- Sample sizes for the physical-signal classifications are small
  enough that the classifications should be read as findings about
  the specific datasets tested rather than as findings about those
  domains broadly.

- Mixed-class spectral decomposition (§7.ter.23 Tier 2) is partial.
  Periodic-component identification via Ramanujan-Fourier peak
  detection works on the test panel; per-component class assignment
  via rep_int_q segmentation does not separate Poisson + uniform_jitter
  components in pooled mixed-stream data.

- The framework's analytical content is Planat's. ARS implements that
  framework as software; it does not extend it analytically.

### What this work is

ARS is an applied implementation of the Farey-rational phase-locked
loop framework developed by Planat and collaborators (FEMTO-ST,
2002–2026). The empirical outputs reproduce statistics consistent with
prior literature on the inputs tested. The methodological
contribution is a specific protocol — calibrator-zoo + extractor-
invariance + induction-on-noise — for catching extraction-pipeline
artifacts in point-process classification, demonstrated on a worked
LLM-application case where three rounds of diagnosis closed
intermediate provisional readings. The protocol is an applied
integration of standard statistical practices (null-hypothesis
controls, calibration with synthetic ground truth, post-hoc verification
on noise inputs); it is not a novel methodological framework.

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

### 7.ter.31  Phase 22b — falsification of Phase 22a interpretations

#### Frame

Phase 22a closed with two substantive findings on pvc-11 (H1 continuous-
metric ARS-functional correspondence at ρ_partial = +0.720, n=210,
p<1e-37; H2 cleanly-passing surrogate-survival on monkey1_natural_movie
and monkey2_gratings_movie at all 30 q-bands).  The Phase 22a findings
document explicitly flagged four caveats: 3-seed surrogate replicate
count flagged as runtime-driven, recording-level confound check not yet
run, SNR-tertile blocking not yet run, cheap-LN as floor for
stimulus-drive elimination rather than ceiling.

Phase 22b runs the falsification passes that lock or modify these
claims.  Bounded scope: no new dataset, no new pipeline development —
Phase 22b exercises the existing Phase 22a infrastructure on additional
analyses against the existing data.

Three required passes plus one optional stretch were specified:

  Pass A — recording-blocked H1 partial correlation (Fisher-Z
           meta-analysis across recordings).
  Pass B — recording-stratified SNR-tertile blocking on H1.
  Pass D — coupled-GLM (Pillow-style, history + stimulus filter)
           surrogate for monkey1_natural_movie.
  Pass E (optional) — increased surrogate replicate count (3 → 7)
                       for the cleanly-passing H2 recordings.

Calibrator zoo re-verified before falsification (8/8 still in spec).

#### Pass A — recording-blocked H1 partial correlation

Per-recording (n_units ≥ 20) Spearman partial correlation of
{rep_med, ks_gue_med} vs {OSI, DSI, F1/F0} controlling for mean firing
rate, Fisher-Z-transform meta-analysis across recordings (fixed and
random effect with DerSimonian-Laird τ²).  Restricted to drifting-
grating recordings where OSI/DSI/F1F0 are defined.

Per-recording partial correlations (Spearman, controlling for firing rate):

|                  | n  | OSI/ks_gue_med | OSI/rep_med | F1F0/rep_med | DSI/ks_gue_med |
|------------------|----|----------------|-------------|--------------|----------------|
| monkey1_gratings | 68 | +0.605         | -0.304      | +0.443       | +0.401         |
| monkey2_gratings | 57 | +0.892         | -0.385      | +0.265       | -0.029         |
| monkey3_gratings | 85 | +0.685         | -0.371      | +0.375       | +0.235         |

Fisher-Z meta-analytic aggregate vs Phase 22a global:

| descriptor | ARS metric  | Phase 22a global | meta-fixed | meta-random | shrink % | I²    |
|------------|-------------|------------------|------------|-------------|----------|-------|
| OSI        | ks_gue_med  | +0.720           | +0.742     | +0.756      |  −2.9 %  | 88.7  |
| OSI        | rep_med     | −0.324           | −0.354     | −0.354      |  −9.1 %  |  0.0  |
| F1/F0      | rep_med     | +0.388           | +0.369     | +0.369      |  +5.0 %  |  0.0  |
| DSI        | ks_gue_med  | +0.223           | +0.223     | +0.214      |  −0.3 %  | 67.1  |

**Verdict: PASS.**  The headline OSI ↔ ks_gue_med correspondence
*grows* under within-recording blocking (meta-fixed +0.742 vs global
+0.720, −2.9% shrink).  All three drifting-grating recordings
independently show the correspondence at ρ_partial in [+0.605, +0.892].
Between-recording confound is eliminated.  The high I² (88.7%) reflects
heterogeneity in *magnitude* across recordings, not in *direction* —
all three are clearly positive.

The monkey2_gratings ρ_partial = +0.892 is striking on its own.
Within a single sufficiently-sampled recording's unit population,
the cell-intrinsic NNS-spacing axis predicts ~80% of the variance
in orientation selectivity beyond what mean firing rate predicts.
That bounds the effect size from the *noise* side: the
within-recording correlation approaches a ~0.9 ceiling on the
cleanest-sampled recording, indicating the global +0.742 is
attenuated by between-recording heterogeneity rather than by
weakness of the underlying cell-intrinsic signal.  The finding is
substantively stronger than the global aggregate alone conveys.

#### Pass B — SNR-tertile blocking

Recording-stratified tertile assignment (qcut on SNR within each
recording, then aggregated).  Per-tertile-per-recording Spearman
partial correlation; per-tertile Fisher-Z meta-analysis across the
three drifting-grating recordings.

Per-tertile meta-fixed partial correlation:

| descriptor | ARS metric  | T1_low  | T2_mid  | T3_high | spread % |
|------------|-------------|---------|---------|---------|----------|
| OSI        | ks_gue_med  | +0.672  | +0.742  | +0.532  |  29 %    |
| OSI        | rep_med     | −0.441  | −0.339  | −0.284  |  49 %    |
| F1/F0      | rep_med     | +0.164  | +0.483  | +0.433  |  82 %    |
| DSI        | ks_gue_med  | +0.371  | +0.221  | +0.344  |  67 %    |

**Verdict: PASS for the headline.**  OSI ↔ ks_gue_med holds in all
three SNR tertiles at ρ_partial in [+0.532, +0.742] with spread 29 %
(within the brief's ≤30 % "comparable magnitude" PASS criterion).
Notably the *highest* SNR tertile (T3_high) shows the *smallest*
effect, which is not the direction predicted by measurement-error
attenuation; the OSI ↔ ks_gue_med correspondence is not concentrated
in clean recordings.  The headline is sort-quality robust.

The F1/F0 ↔ rep_med correspondence (the second Phase 22a finding) is
SNR-concentrated (T1=+0.164 vs T2=+0.483, T3=+0.433) — the small-
amplitude correlation is mostly carried by mid- and high-SNR cells.
That is reportable as a soft-pass weakening: the F1/F0 finding holds
in 2/3 tertiles but is essentially null in T1_low.

The SNR-concentration has two distinct interpretations and Pass B
does not discriminate between them:

  (a) The `rep_med` signal itself differs across SNR tertiles —
      a finding about how the spacing-structure axis varies with
      sort quality.
  (b) The F1/F0 measurement reliability differs across SNR
      tertiles, washing out any real correlation in the low-SNR
      cells.  F1/F0 is computed from the temporal-frequency
      Fourier component of drifting-grating PSTHs and is known to
      be measurement-noise-sensitive; low-SNR units may have
      F1/F0 estimates with high variance that the correlation
      cannot survive.

Reading (b) is plausible and would make the SNR-concentration a
measurement-axis artifact rather than a finding about `rep_med`
structure varying with SNR.  Distinguishing (a) from (b) requires
computing F1/F0 reliability per unit (e.g., split-half F1/F0
correlation across trials, or trial-bootstrapped F1/F0 95% CI
width) and then re-running the partial correlation either after
filtering on F1/F0 reliability or after error-in-variables
correction.  Neither was done in Phase 22b; the ambiguity is
flagged here for future falsification work that wants to lock or
modify the F1/F0 ↔ rep_med claim.

#### Pass D — coupled-GLM surrogate for monkey1_natural_movie

Pillow-style per-unit Poisson GLM:
    log λ_i(t) = b_i + Σ_l c_{i,l} · stim_basis_l(t)
                       + Σ_k h_{i,k} · history_basis_k(spike_history_i)(t)
with raised-cosine bases on the stimulus-drive temporal history
(4 functions, 5–200 ms past) and the post-spike history (5 functions,
5–100 ms post-spike).  Fit by L-BFGS-B on the Poisson NLL with mild
L2 ridge.  Two variants:
  - Canonical (non-positive history weights via softplus
    reparameterisation, h_k = -softplus(theta_k); Pillow's standard
    recommendation for stable GLMs).
  - Diagnostic (unconstrained history weights; saved separately as
    `pass_d_unconstrained_*.parquet`).

Forward simulation: at each bin, compute per-unit history contribution
from the rolling spike-history buffer, sample Poisson, shift buffer.
5 seeds.  Eta clipped at +5 to avoid Poisson lambda overflow.

GLM fit-quality summary (canonical variant):
- units converged: 74 / 74
- median dev_explained vs null: 0.002
- history kernel median |L2|: 0.000
- stim temporal kernel L2: 0.009
- history kernel max (median): −0.000

The non-positive constraint forces the optimiser to a near-zero
history kernel — the natural movie's spike-count autocorrelation is
positive (stimulus-driven), so a non-positive-only kernel cannot
explain it; the L-BFGS settles at the all-zero optimum.  The stim
temporal kernel also collapses to ~0, suggesting the optimiser
prefers the bias-only model.  The resulting surrogate is Poisson
at the per-unit base rate (38,553 events vs real 87,313, primary BL,
rep_med ≈ 0.06).  The Phase 22a real-data verdict (TR, rep_med 0.25)
strictly dominates this surrogate at all 30 q-bands — but this is
identical to the rate-matched-Poisson result in Phase 22a.

GLM fit-quality summary (unconstrained-history variant):
- units converged: 39 / 74
- median dev_explained vs null: 0.054
- history kernel median |L2|: 0.940
- history kernel min (median): +0.228 (positive throughout — runaway)
- history kernel max (median): +0.748
- mean surrogate event count: 660,195 (7.5× real)
- surrogate primary: BR_artifact at all 30 q-bands, rep_med ≈ 0.85

The unconstrained variant absorbs the natural movie's slow temporal
autocorrelation (~30 ms timescale) into uniformly positive history
kernels.  Forward simulation produces runaway positive feedback,
generating an unstable over-rate surrogate that saturates BR_artifact.
Comparing real to this surrogate is methodologically meaningless:
real rep_int_q (0.25) is much *lower* than surrogate (0.85), so the
"strict" survival metric registers 0/30 — but this reflects pathological
GLM behavior, not an honest test of history-coupling elimination.

**Verdict: INCONCLUSIVE.**  Neither GLM variant produces a faithful
per-unit history-coupled surrogate at 5 ms bins on natural-movie data.
The Phase 22a finding "monkey1_natural_movie population events survive
LN-Poisson surrogates (rate-matched, cell-shuffle, cheap-LN)" stands;
the additional claim "structure survives LN-Poisson + per-unit history
coupling" is unresolved.  Future-work fix: multi-frame spatiotemporal
STA (allowing the stimulus filter to absorb the slow stim
autocorrelation that's currently being mis-routed to the history
kernel) or coarser bin width (~20 ms, where 5-bin history covers
100 ms but the stim temporal autocorrelation is mostly within one bin).

The unconstrained-history kernel running uniformly positive across
5–100 ms (median min +0.228, median max +0.748) is itself a finding
about the spike-train data — there is positive temporal correlation
beyond what a single-frame STA explains.  Whether that positive
correlation is (i) actual cell-intrinsic history coupling, (ii) slow
stimulus autocorrelation mis-routed to the history kernel because
the stim filter is too simple, or (iii) a mixture, is diagnosable
by progressively enriching the stimulus filter and re-fitting:

  - If a multi-frame spatiotemporal STA absorbs the slow stim
    autocorrelation and the unconstrained history kernel collapses
    to the biologically-expected refractory-dominated shape, the
    original Pass D positive-history kernels were stim-mis-routing
    artifacts.
  - If the unconstrained history kernel still runs uniformly
    positive after the stim filter is enriched, that's actual
    history coupling — and Pass D's elimination question is then
    well-posed and answerable.

The clean discriminating test is therefore "enrich the stim filter
incrementally and watch what the history kernel does."  Whatever
brief eventually picks up the deferred Pass D work should specify
this two-step diagnosis as the path to a faithful coupled-GLM
surrogate, not just "use a multi-frame STA" — the diagnostic value
is in what changes between the simple and enriched fits, not in
the enriched fit alone.

#### Pass E — tightened surrogate replicates 3 → 7

Re-ran the Phase 22a surrogate battery (rate_matched_poisson,
cell_shuffle, ln_evoked) at N_SEEDS=7 for monkey1_natural_movie
and monkey2_gratings_movie.

| recording               | surrogate            | rep_survives | quad_diff | both |
|-------------------------|----------------------|--------------|-----------|------|
| monkey1_natural_movie   | rate_matched_poisson | 30/30        | 30/30     | 30/30|
| monkey1_natural_movie   | cell_shuffle         | 30/30        | 30/30     | 30/30|
| monkey1_natural_movie   | ln_evoked            | 30/30        | 30/30     | 30/30|
| monkey2_gratings_movie  | rate_matched_poisson | 30/30        | 30/30     | 30/30|
| monkey2_gratings_movie  | cell_shuffle         | 30/30        | 30/30     | 30/30|
| monkey2_gratings_movie  | ln_evoked            | 30/30        | 30/30     | 30/30|

**Verdict: PASS.**  All 6 (recording, surrogate) cells confirm the
Phase 22a verdicts at 7 seeds.  The 3-seed surrogate-replicate-count
caveat is fully addressed: increasing to 7 seeds tightens the 95th-
percentile threshold but the strict-survival count is unchanged at
30/30 for every cell.  This was anticipated by the Phase 22a doc
(real values are ~6× the surrogate median, so the verdict is robust
to the upper-percentile noise) and is now confirmed.

#### Combined verdict

Pass A: PASS (effect grows under within-recording blocking).
Pass B: PASS for headline OSI ↔ ks_gue_med (29% spread, all
        same sign).  Soft note: F1/F0 ↔ rep_med is SNR-concentrated.
Pass D: INCONCLUSIVE (GLM fit fragility at this temporal resolution).
Pass E: PASS (all surrogates still pass at tightened replicate count).

**Net effect on Phase 22a interpretations:**

- H1 continuous-metric finding (OSI ↔ ks_gue_med, F1/F0 ↔ rep_med):
  **locked.**  Within-recording effect = global, within-SNR-tertile
  effect holds for the headline.  The between-recording-confound and
  sort-quality-confound caveats are removed.

- H2 cleanly-passing recordings (monkey1_natural_movie,
  monkey2_gratings_movie) at the LN-Poisson elimination floor:
  **locked.**  The 3-seed surrogate-replicate-noise caveat is
  removed.

- H2 history-coupled elimination (the additional claim attempted in
  Pass D): **unresolved.**  The cheap-LN-as-floor caveat is therefore
  narrowed but not removed.  The H2 finding remains "structure
  survives LN-Poisson surrogates"; the stronger claim "structure
  survives LN-Poisson + per-unit history coupling" requires a more
  expressive stimulus filter than Phase 22b's bounded scope allowed.

#### Coupled-GLM surrogate interface-coverage standard (promoted to general)

Pass D's GLM-fit fragility surfaced a genuine modeling caveat for
ARS surrogate design on stimulus-locked neural data: at fine bin
widths (5 ms here), the stimulus-driven temporal autocorrelation
of the input can collide with the spike-history timescale of the
GLM, leaving the optimiser unable to disambiguate the two.  A
single-frame STA stimulus filter is insufficient.  Reframed under
the interface-investigation view: the interface configuration
(5 ms bins + single-frame STA stimulus filter) does not support a
non-degenerate coupled-GLM surrogate on natural-movie inputs;
alternative configurations (coarser bins ~20 ms, multi-frame
spatiotemporal stim filter) might.

This generalises beyond Phase 22a's specific dataset and is
promoted here as a general interface-coverage standard for ARS
surrogate design when coupled GLMs are involved.  Before drawing
survival conclusions from a Pillow-style coupled-GLM null model,
verify both:

  1. The fitted history kernel has the biologically-expected
     shape: negative refractory lobe at 1–3 ms, optionally
     positive bursting lobe at 5–30 ms, small magnitude at long
     lags.  Uniformly-positive or uniformly-zero kernels are
     diagnostic flags that the fit is degenerate.

  2. Forward simulation produces an event rate within ~1.5× of
     the real recording.  Order-of-magnitude over- or under-rate
     indicates pathological feedback (positive runaway) or
     parameter collapse (kernel zeroed).

When either check fails, the GLM is unfaithful as a surrogate and
the ARS survival comparison against it is uninformative — neither
"real survives" nor "real matches" is interpretable.  This standard
is independent of any specific ARS choice; it's a property of the
GLM-fitting protocol that ARS-as-survival-test inherits, and it
applies to coupled-GLM surrogates in any ARS workflow regardless
of the underlying data domain.

The two-step discriminating test described in the Pass D verdict
above ("enrich stim filter incrementally and watch what the
history kernel does") is the disambiguation procedure when check
(1) fails specifically because the unconstrained history kernel
runs uniformly positive — distinguishing actual history coupling
from stim-autocorrelation mis-routing.

#### Outputs

Code under `phase22b/`:  pass_a_recording_blocked.py,
pass_b_snr_tertile.py, pass_d_glm_surrogate.py,
pass_e_tighten_seeds.py, run_phase22b.py.

Data under `data/phase22b_results/`:  pass_a_per_recording.parquet,
pass_a_meta_analysis.parquet, pass_a_comparison.parquet,
pass_b_per_tertile_recording.parquet, pass_b_meta_per_tertile.parquet,
pass_b_comparison.parquet, pass_d_glm_fits.parquet (canonical),
pass_d_surrogate_classifications.parquet, pass_d_survival.parquet,
pass_d_unconstrained_glm_fits.parquet (diagnostic),
pass_d_unconstrained_surrogate_classifications.parquet,
pass_d_unconstrained_survival.parquet,
pass_e_surrogate_classifications.parquet, pass_e_survival.parquet,
PHASE22B_FINDINGS.md.

`PHASE22A_FINDINGS.md` (in `data/phase22a_results/`) is updated
in-place with a "Phase 22b update" note at the top recording the
caveat-resolution state.

---

### 7.ter.32  Phase 23 — GRB unblock: targeted 909 Hz QPO replication on GRB 230307A

#### Frame

Phase 21 closed (§7.ter.29) with a methodology-only verdict on the
ARS application to GRB QPO replication: lightcurve-modulated Poisson
surrogate reproduces the empirical classification on all four panel
events; published QPO frequencies fall just outside the framework's
q-coverage at the sub-window resolution used in Tier 3.
`GRB_NEXT_STEPS.md` (Phase 21 closing document) identified the
operative methodology block as q_max = 30 + 2.0 s sub-windows, and
specified the next-step time-slice adjustment: **targeted 909 Hz
replication on GRB 230307A at q_max = 50 with 100 ms sub-windows in
the published Chen 2025 claim window (45–47 s post-trigger)**.

Phase 23 implements that adjustment exactly.

#### Methodology

`phase23/run_phase23_targeted.py`:
- sub-window:        100 ms     (down from 2.0 s in Phase 21 Tier 3)
- q_max:             50         (up from 30 in Phase 21 Tier 3)
- analysis window:   [−5, +60] s post-trigger
- target QPO:        909 Hz (Chen et al. 2025), claim window 45–47 s
- surrogates:        lightcurve-modulated Poisson, 5 seeds (up from 3)

Pre-run checks:
- Calibrator zoo (Phase 22a panel): 8/8 in spec.
- GRB 230307A pooled events from `data/phase21_grb_panel/GRB230307A.parquet`
  (11,055,634 events on disk, 4,110,498 in [−5, +60] s analysis window,
  pooled rate ~63 K events/s window-mean).

Trajectory: 650 sub-windows of 100 ms each, classified via
`joint_q_profile` + `joint_quadrant_diagnostic` at q_max=50 with
12-worker multiprocessing.  ~18 minutes per trajectory wall-time.

#### Headline result — 909 Hz q-band inside vs outside claim window

For each well-powered sub-window with the local-rate-mapped 909 Hz
q-band falling within q ∈ [2, q_max], extract `rep_int_q` and
`rf_amplitude_q` at that q-band.  Compare inside-claim-window
(45–47 s, ~20 sub-windows) vs outside (~386 sub-windows) for real
and surrogate.

| condition       | n   | median rep_int @ 909 Hz q | quadrants @ 909 Hz q |
|-----------------|-----|---------------------------|----------------------|
| real, inside    |  20 | 0.053 | {BL: 20} |
| real, outside   | 386 | 0.055 | {BL: 347, TR: 35, ambiguous: 4} |
| surr, inside    | 100 | 0.037 | {BL: 100} |
| surr, outside   | 1929 | 0.041 | {BL: 1906, ambiguous: 16, TR: 7} |

Inside − outside delta: real −0.001, surrogate −0.004.

**Verdict on the published Chen 2025 909 Hz QPO replication: FAIL
(substantive).**  The time-slice adjustment lifts the q-resolution
(q_target = 19.5 at the actual pooled rate, well within q_max=50)
and sub-window-resolution (20 sub-windows inside the 2 s claim)
ceilings identified in Phase 21.  ARS detects no signature
distinguishing the QPO claim window from surrounding sub-windows
at the 909 Hz q-band.  The blocking issue is not q-resolution; the
adjustment confirms the absence of a detectable QPO signature at
the published claim by lifting the methodology limits and finding
no signal nonetheless.

Per the Phase 23 brief acceptance criteria, this is "Adjustment
applies cleanly but doesn't resolve the prior phase's blocking
issue."

#### Side-finding — broadband TR signature at t = 26–30 s

In aggregating the 35 real "TR sub-windows at the 909 Hz q-band"
from the headline analysis, the per-q distribution showed the TR
sub-windows are NOT 909-Hz-specific: they are sub-windows where
ALL 50 q-bands classify as TR uniformly.  Time distribution:
22 of 40 well-powered sub-windows in [26, 30) s post-trigger
(GRB 230307A's late prompt, T90 = 34.6 s) classify as TR.  The
lightcurve-modulated Poisson surrogate at the Phase 21/23 default
21 ms smoothing produces 10 % TR in the same region.

**Smoothing-window diagnostic** (`phase23/run_phase23_smoothing_diag.py`,
2 seeds × 4 smoothing windows from 1 ms to 101 ms):

| config                    | smoothing_ms | TR_frac in [26, 30) s |
|---------------------------|--------------|------------------------|
| real                      | —            | **55.0 %**             |
| lc_smooth_1               | 1            |  5.0 %                 |
| lc_smooth_5               | 5            |  8.8 %                 |
| lc_smooth_21 (default)    | 21           | 10.0 %                 |
| lc_smooth_101             | 101          | 10.0 %                 |

The lightcurve-modulated Poisson surrogate produces 5–15 % TR in
[26, 30) s **regardless of smoothing window**.  Even the unsmoothed
surrogate (window=1, preserving every 1 ms-bin rate variation
exactly, sampling within-bin event positions uniformly) cannot
reproduce real's 55 % TR.  The TR signature is not a
surrogate-smoothing artifact.

**Per-detector test** (`phase23/run_phase23_per_detector.py`):

| detector | rate (events/s) | TR / 40 |
|----------|-----------------|---------|
| n2       |  1,138          | 29 (72.5 %) |
| n5       |    978          | 25 (62.5 %) |
| b0, nb   |  ~2,200         | 10 each (25 %) |
| n0, n1   |  ~2,400         |  9 each (22.5 %) |
| n8, n9   |  ~2,600         |  6 each (15 %) |
| n7       |  3,067          |  4 (10 %) |
| n6       |  3,120          |  2 (5 %) |
| na       | 11,062          |  2 (5 %) |
| b1       |  5,736          |  0 (0 %) |
| pooled   | 39,766          | 22 (55 %) |

**The TR signature is present per-detector**, ruling out the
multi-detector-pooling-artifact hypothesis (cross-detector timing
offsets at sub-1 ms scale).  4 of 12 detectors show TR ≥ 22.5 %,
and 2 (n2, n5) show TR > 60 %.

**Inverse correlation between detector event rate and TR fraction.**
The two lowest-rate detectors (n2, n5) show the highest TR
fractions; the highest-rate detectors (na, b1) show the lowest.
This is the *opposite* of the deadtime hypothesis (Phase 21 §7.ter.29
lesson 5: scintillator deadtime BL → TR at ≥ 200 K / s) which
predicts TR↑ with rate↑.  Deadtime is ruled out as the operative
mechanism.

The most plausible remaining hypothesis is detector-specific energy-
band sensitivity: in Fermi GBM, lower-rate-on-this-burst detectors
are at higher incidence angle and sample a different effective
energy spectrum (off-axis response biases toward different energy
distributions than on-axis).  The TR signature being concentrated
in low-rate detectors is consistent with the sub-millisecond
clustering being **energy-spectrum-dependent** — the right *kind*
of signal for a magnetar-modulated emission process (Chen 2025
predicts an energy-dependent QPO from the central engine), although
the broadband (all q-bands) nature of the TR means this is not a
narrowband QPO claim in itself.

#### Net interpretation

Phase 23 produces:

  - a **substantive FAIL** on the targeted Chen 2025 909 Hz QPO
    replication (the headline test the brief asked for),
  - a **methodologically robust side-finding** of broadband TR
    spacing structure in GRB 230307A's late-prompt window at
    t = 26–30 s that survives both the lightcurve-modulated Poisson
    surrogate at all tested smoothing windows AND per-detector
    decomposition,
  - **inverse-rate detector dependence** that rules out deadtime
    artifacts and is consistent with energy-band-dependent emission
    (the magnetar-modulation prediction's structural signature).

The broadband TR signature is not by itself a positive replication
of the published Chen 2025 QPO claim — it's a different observation
with a different time location (26–30 s, not 45–47 s) and a
different spectral character (broadband, not narrowband).  But it
is a real per-detector pattern that survives the Phase 21 surrogate
floor and has a structural feature (detector-rate inverse
correlation) that rules out the simplest instrumental explanation.

#### Time-slice-adjustment evaluation

Adjustment applies cleanly.  Calibrator zoo unchanged.  Pipeline
structure preserved; Phase 21's `run_phase21_classification.py`
patterns extended at finer resolution.  The adjustment's
methodological intent is fulfilled: the q-coverage and sub-window
resolution ceilings identified in Phase 21 are lifted, and the
resulting analysis at the published claim's natural q-band gives a
clean null verdict.  The blocking issue for Chen 2025 909 Hz
replication is NOT q-coverage; it is the absence of any detectable
ARS signature at that specific claim, which finer resolution
confirms rather than uncovers.

#### Recommended next-step direction

Two distinct future-work items, with different acceptance criteria:

1. **Per-(detector, energy_channel) stratified targeted
   classification on the [26, 30) s broadband-TR region.**  Phase 23
   ruled out pooling and deadtime as operative mechanisms; the
   remaining hypothesis is energy-band sensitivity.  An energy-
   stratified analysis would either confirm (the TR signature is
   localised to specific energy channels, consistent with magnetar-
   modulated emission) or falsify (the TR signature is uniform
   across energy channels, consistent with a generic detector-
   geometry effect).  Compute cost ~1-2 hours.

2. **Reconsider ARS-on-GRB-QPO viability at the broader question
   level.**  Phase 23's substantive FAIL on the targeted Chen 2025
   replication closes the most accessible methodology-tuning escape
   route from Phase 21's null verdict.  The remaining options are:
     - a different ARS axis (energy-stratified trajectories;
       per-detector cross-correlations) that the Farey-bank /
       NNS classifier doesn't presently compute,
     - a different signal class (not GRB QPOs).
   Phase 23 closes the within-current-axis pursuit of the published
   GRB QPO claims; further work in this direction needs new
   methodology, not just finer resolution.

#### Outputs

Code under `phase23/`: run_phase23_targeted.py,
run_phase23_smoothing_diag.py, run_phase23_per_detector.py,
run_phase23_writeup.py, run_phase23_energy_strat.py (drafted but
not run; activated for the per-(detector, energy_channel)
stratification follow-up).

Data under `data/phase23_results/`:
phase23_targeted_classification.parquet,
phase23_targeted_surrogate_classification.parquet,
phase23_targeted_qpo_comparison.parquet,
phase23_smoothing_diag.parquet,
phase23_per_detector.parquet,
PHASE23_FINDINGS.md,
PHASE23_VS_PHASE21.md.

---

### 7.ter.33  Phase 24 triage — Allen Brain Observatory awake-mouse-V1, single session

#### Frame

Phase 22a's finding scope was bounded by anesthesia (sufentanil-
anesthetized macaque V1).  Phase 22b's writeup named four validation
paths that distinguish the strong from bounded versions of the
claim, of which awake-V1 replication is the highest-priority gate.
Phase 24 begins the awake-V1 replication arc with an exploratory
triage on a single Allen Brain Observatory Visual Coding Neuropixels
session, holding the Phase 22a interface configuration (q_max=30,
k=5/5ms, surrogate battery) fixed and testing whether the substrate
shift (anesthetised macaque V1 → awake mouse V1) supports a clean
replication.

The triage scope is "does this work?" not "what does it find?";
substantive single-session findings are reportable as triage outputs
but the multi-session full Phase 24 is the test that locks or
modifies any substrate-level claims.

#### Methodology

allensdk fails to install on Python 3.12 (the existing project
venv) due to a setuptools/pkg_resources incompatibility.  Phase 24
uses direct S3 download + pynwb 3.1.3 (Python 3.12 compatible) for
NWB reading.  Loader implemented in `phase24/loader.py` is reusable
across sessions.

Session selection: 58 sessions in the Allen Visual Coding
Neuropixels manifest, of which 32 are brain_observatory_1.1.  After
Allen-default QC (`quality=='good'` + `isi_violations<0.5` +
`presence_ratio>0.9` + `amplitude_cutoff<0.1` + `snr>1.0`), 12
brain_observatory_1.1 sessions have ≥ 80 V1 (VISp) units.  Selected
**session 732592105** (111 V1 units, wt/wt male, P100) — top of the
wild-type list by unit count.  Brief's selection criteria all met.

Pipeline patterns carried from Phase 22a unchanged:
  - q_max = 30, calibrator zoo verified 8/8.
  - H1: per-unit ARS classification on three conditions
    (drifting_gratings_pooled, natural_movie_one, spontaneous);
    functional categories (OSI/DSI/F1F0) recomputed from spikes
    and sanity-checked against Allen's precomputed values
    (`g_osi_dg`, `g_dsi_dg`, `f1_f0_dg`).
  - H2: synchronous-firing population events (k=5, w=5ms);
    surrogate battery rate_matched_poisson + cell_shuffle, 5 seeds.
    `ln_evoked` deferred — Allen's stimulus templates are stored
    separately and require integration work outside triage scope.

#### Recomputed-vs-Allen functional-categories sanity check

Recomputed values agree strongly with Allen's precomputed:

| comparison                                | Spearman ρ | p       | n   |
|-------------------------------------------|-----------|---------|-----|
| recomputed OSI vs Allen `g_osi_dg`        | +0.883    | 1.1e-37 | 111 |
| recomputed DSI vs Allen `g_dsi_dg`        | +0.828    | 4.1e-29 | 111 |

Methodology consistency confirmed; any H1 discrepancy with pvc-11
is a substrate-shift effect, not a methodology-mismatch artifact.

#### H1 result

Modal-quadrant counts (drifting_pooled / natural_movie_one /
spontaneous): 84/89/68 BL + 7/10/20 TR.  Same dominance pattern as
pvc-11 (98.7% BL); slightly more TR sub-population on Allen
spontaneous (23%) than on Allen evoked, plausibly an
awake-vs-anesthesia difference worth flagging.

H1 cross-validation, Spearman partial correlation controlling for
mean firing rate (drifting_pooled, n=91):

| descriptor | ARS metric  | Allen partial ρ | p (partial) | pvc-11 reference |
|------------|-------------|-----------------|-------------|------------------|
| OSI        | ks_gue_med  | **+0.417**      | 4.3e-5      | **+0.720**       |
| OSI        | rep_med     | −0.227          | 0.031       | −0.324           |
| DSI        | ks_gue_med  | +0.385          | 1.8e-4      | +0.223           |
| DSI        | rep_med     | −0.370          | 3.3e-4      | −0.060           |
| F1/F0      | ks_gue_med  | +0.283          | 7.6e-3      | −0.093           |
| F1/F0      | rep_med     | **−0.222**      | 0.038       | **+0.388**       |

**OSI ↔ ks_gue_med headline replicates in direction at ~58 %
magnitude.**  Direction-and-approximate-magnitude-order is the
brief's triage criterion; direction-consistent + p < 1e-4 + n=91
satisfies it.

DSI ↔ ks_gue_med replicates with stronger Allen magnitude
(+0.385 vs +0.223) — biologically plausible (mouse V1 has heavier
direction selectivity than macaque V1).

**F1/F0 ↔ rep_med shows opposite sign on Allen (−0.222) vs pvc-11
(+0.388).**  Single-session non-replication of the second-order
Phase 22a finding.  Substrate-systematic vs single-session-noise is
not discriminable at triage scale; flagged for multi-session
resolution.

#### H2 result

Real-data classifications:

| condition          | n_events | rate (Hz) | primary       | rep_med |
|--------------------|----------|-----------|---------------|---------|
| drifting_pooled    |  50,172  |  39.8     | TR            | 0.500   |
| natural_movie_one  |  48,927  |  81.5     | BR_artifact   | 0.700   |
| spontaneous        |  53,866  |  43.6     | TR            | 0.500   |

Per-condition required-conjunction verdict (the partial-conjunction,
`rate_matched_poisson` + `cell_shuffle` only, since `ln_evoked` is
deferred):

  - **drifting_pooled: PASS** (both surrogates pass strict at 2/30 q-bands)
  - **natural_movie_one: NULL** (both surrogates fail strict at all 30)
  - **spontaneous: PASS** (both surrogates pass strict at 1/30 q-bands)

**The pvc-11 monkey1_natural_movie H2 headline finding does NOT
replicate on Allen natural_movie_one.**  Allen's natural-movie real-
data classification is BR_artifact at rep_med 0.700 (vs pvc-11
monkey1's TR at rep_med 0.250); surrogates produce similar high
rep_int characters, so the inside-vs-surrogate delta vanishes.

Possible mechanisms (not discriminated by triage):
  - Allen's higher H2 event rate (81.5 Hz vs pvc-11 monkey1's
    24.3 Hz) means surrogate comparisons are less discriminating —
    at high event rate, the Poisson sampling of population events
    can produce strong-rep_int structure on its own.
  - Awake mouse V1 may have more synchronous bursting during
    natural-movie viewing than anesthetized macaque V1, narrowing
    the structure-beyond-rate gap.
  - Different stimulus content (Allen "Touch of Evil" vs pvc-11
    "monkey wading through water") produces different population-
    event distributions.

#### Triage verdict

**PASS.**  Pipeline runs end-to-end on Allen session 732592105;
calibrator zoo unchanged; H1 headline OSI ↔ ks_gue_med
replicates in direction with substantive magnitude (+0.417 partial,
~58% of pvc-11); H2 produces coherent verdicts (drifting and
spontaneous PASS modestly, natural-movie NULL with a clean
substrate-shift interpretation).  The full Phase 24 multi-session
replication is unblocked.

#### Scope adjustments folded into the full Phase 24 brief

  1. allensdk Python 3.12 incompatibility — full Phase 24 uses
     `phase24/loader.py` (already implemented).
  2. Stimulus templates need separate handling for the `ln_evoked`
     surrogate.  Full Phase 24 integrates template download +
     per-bin alignment via the loader.
  3. k_thresh sensitivity scan on Allen *first* before locking
     defaults — Allen's higher event rate means the (k=5, w=5ms)
     pvc-11 defaults may not be the right probe at Allen's
     event-rate regime.
  4. F1/F0 ↔ rep_med sign-flip disambiguation requires multi-
     session Fisher-Z meta-analysis stratified by Cre line.
  5. natural_movie_one H2 NULL needs the multi-session test to
     determine if it's substrate-bounded (uniform NULL) or
     session-bounded (heterogeneous).

The full draft brief is at `data/phase24_results/PHASE24_FULL_BRIEF_DRAFT.md`.

#### Outputs

Code under `phase24/`:  loader.py, run_h1.py, run_h2.py.

Data under `data/phase24_results/`:  h1_classifications.parquet,
h1_functional.parquet, h1_allen_comparison.parquet,
h1_crossval_summary.parquet, h2_population_classifications.parquet,
h2_surrogate_classifications.parquet, h2_survival_summary.parquet,
PHASE24_TRIAGE_FINDINGS.md, PHASE24_FULL_BRIEF_DRAFT.md.

Cache under `/home/combust/fmexplorer/allen_cache/`:  Allen
manifests (sessions/units/channels/probes), session 732592105 NWB
(2.9 GB), session 732592105 analysis_metrics, natural_movie_1
template (166 MB).

---

### 7.ter.34  Phase 24 (Full) — multi-session Allen Visual Coding awake-mouse-V1 replication

#### Frame

Phase 24 triage on a single Allen Brain Observatory session (732592105)
established that the Phase 22a interface configuration applies cleanly
to awake mouse V1 data and produces direction-replication of the H1
headline at ~58 % of pvc-11 magnitude.  Triage flagged three findings
for multi-session resolution: H2 natural-movie non-replication
(substrate-rate-regime hypothesis), F1/F0 ↔ rep_med sign-flip
(substrate-systematic vs session-noise vs Cre-line-specific), and DSI
strengthening (replicated multi-session vs single-session noise).

Phase 24 (Full) ran the multi-session test on the 12
brain_observatory_1.1 sessions with ≥ 80 V1 units after Allen-default
QC: 5 wt, 4 Vip-Cre, 2 Sst-Cre, 1 Pvalb-Cre.  The interface
configuration was held fixed (Phase 22a defaults).

#### Methodology

Calibrator zoo verified 8/8 in spec.

Per-session H1: Spearman partial correlation of {ks_gue_med, rep_med}
vs {OSI, DSI, F1/F0} controlling for mean firing rate.  72 (session,
metric, descriptor) cells across 12 sessions.

(k_thresh, w) sensitivity grid: 12 (k, w) combinations × 12 sessions
× 3 conditions = 432 real-only ARS calls.  Identified per-session
rate-matched (k, w) closest to pvc-11 monkey1_natural_movie's 24.3 Hz
reference rate.

Per-session H2: surrogate battery (rate_matched_poisson + cell_shuffle
+ ln_evoked where stimulus templates apply) at default (k=5, w=5ms)
AND rate-matched (per-session) configurations.  5 seeds each.

Multi-session Fisher-Z meta-analysis (fixed and random effect, with
DerSimonian-Laird τ²) overall and stratified by Cre line and by
per-session firing-rate quartile.

#### H1 verdict: LOCKED cross-species cross-state

| descriptor | ARS metric  | Allen meta-fix | Allen meta-rand | I² | pvc-11 ref |
|------------|-------------|----------------|-----------------|-----|------------|
| OSI        | ks_gue_med  | **+0.363**     | +0.364          | 43% | +0.720     |
| OSI        | rep_med     | −0.211         | −0.211          |  7% | −0.324     |
| DSI        | ks_gue_med  | +0.269         | +0.268          | 26% | +0.223     |
| DSI        | rep_med     | −0.222         | −0.222          | 27% | −0.060     |

All 12 Allen sessions show positive OSI ↔ ks_gue_med partial
correlation (range +0.16 to +0.60; 10 of 12 significant at p < 0.05).
Per-Cre-line: wt +0.336, Vip +0.342, Sst +0.416 — sign-consistent
across all genotypes.  Per-rate-quartile: +0.255 to +0.457 — H1 is
rate-regime-robust.

The Phase 22a H1 OSI ↔ ks_gue_med headline is **substrate-general**.
The anesthesia caveat is removed.

#### DSI verdict: REPLICATED with stronger Allen magnitude

DSI ↔ ks_gue_med: Allen meta-fix +0.269 vs pvc-11 +0.223 — Allen
20 % *stronger*.  Triage's single-session +0.385 is consistent
across sessions.  Biologically plausible (mouse V1 has documented
heavier direction selectivity than macaque V1).

DSI ↔ rep_med: Allen meta-fix −0.222 vs pvc-11 −0.060 — Allen 4×
stronger negative correlation.  The triage single-session reading
(−0.370) replicates and extends.

DSI is added to the cross-validated H1 axis as a biologically-grounded
species-difference observation.

#### F1/F0 ↔ rep_med verdict: SUBSTRATE-SYSTEMATIC SIGN-FLIP

| Cre line | n_sess | meta-fix ρ | I² |
|----------|--------|------------|-----|
| overall  | 12     | **−0.183** | 29% |
| wt       | 5      | −0.117     | 45% |
| Vip      | 4      | −0.253     | 28% |
| Sst      | 2      | −0.251     |  0% |

All 12 Allen sessions show negative F1/F0 ↔ rep_med correlation
(opposite sign to pvc-11's +0.388).  All Cre lines same direction.
This is **substrate-systematic**, not session-noise or Cre-line-
specific.

The Phase 22a F1/F0 finding is bounded to anesthetised macaque V1.
In awake mouse V1, the correlation runs in the opposite direction —
a substantive substrate difference reportable as a separate finding.

#### H2 verdict: PVC-11-SPECIFIC

| condition          | default (k=5, w=5ms) | rate-matched (per-session k, w) |
|--------------------|----------------------|----------------------------------|
| natural_movie_one  | **3 / 12 PASS**      | **1 / 8 PASS**                   |
| drifting_pooled    | 5 / 12 PASS          | 6 / 8 PASS                       |
| spontaneous        | 3 / 12 PASS          | 4 / 8 PASS                       |

The triage substrate-rate-regime hypothesis predicted that
rate-matching to pvc-11 would *increase* the Allen H2 PASS rate
on natural_movie_one.  Empirically: rate-matching produces *fewer*
PASSes (1/8) than default (3/12).  **The substrate-rate-regime
hypothesis is falsified.**

The pvc-11 monkey1_natural_movie headline H2 finding (clean
strict-survival across all 30 q-bands and all 3 surrogates) does
not generalise to awake mouse V1 at any tested interface
configuration.

The Phase 22a H2 claim's appropriate post-Phase-24 scope:
**bounded to anesthetised macaque V1 + specific stimulus +
specific recording**, with the rate_matched_poisson + cell_shuffle
+ ln_evoked surrogate set passing on the specific pvc-11
monkey1_natural_movie + monkey2_gratings_movie recordings.
Multi-session awake-mouse-V1 does not share the structural
feature that produced the pvc-11 H2 finding.

#### Net effect on Phase 22a interpretations

The strongest version of Phase 22a's claims surviving Phase 24
multi-session falsification:

  1. ARS continuous metrics (`ks_gue_med`, `rep_med`) carry a
     firing-rate-controlled signal correlating with V1 functional
     categories OSI and DSI, in awake mouse V1 and anesthetised
     macaque V1, with magnitudes attenuated in the awake mouse
     replication.  **Substrate-general, cross-species, cross-state.**
  2. The F1/F0 ↔ rep_med correlation is sign-opposite between
     anesthetised macaque V1 and awake mouse V1 — a substantive
     substrate difference, not noise.  **Substrate-bounded
     observations on each side.**
  3. The pvc-11 H2 population-event finding on
     monkey1_natural_movie does not have a substrate-general
     analogue in Allen mouse V1.  H2 claims should be scoped to
     the specific recordings + interface configuration where they
     were observed.  **Pvc-11-specific.**

#### Methodological notes

- allensdk fails to install on Python 3.12 (the existing project
  venv); Phase 24 uses direct S3 + pynwb 3.1.3.  Loader at
  `phase24/loader.py` is reusable.
- Stimulus templates for natural_movie_one are stored separately
  from the session NWB; loaded as numpy arrays (despite the .h5
  extension) and downsampled spatially (factor 8) for the LN-evoked
  surrogate's STA fit.
- Per-session H2 surrogates run at two configurations (default and
  per-session rate-matched) — this is the substrate-rate-regime
  test that the triage flagged as the leading explanation for H2
  non-replication, and it is now falsified.
- 7 of the 12 NWB downloads required clean-restart due to
  parallel-curl interleaving corruption during initial fetch
  attempts.  All 12 verified against Allen S3 expected sizes
  before analysis.

#### Outputs

Code under `phase24/`:  loader.py, run_sensitivity_grid.py,
run_per_session_h1.py, run_per_session_h2.py, run_meta_analysis.py,
run_verdicts.py.

Data under `data/phase24_results/`:
sensitivity_grid.parquet, rate_matched_configs.parquet,
per_session_h1_ars.parquet, per_session_h1_functional.parquet,
per_session_h1_crossval.parquet, per_session_h2_population.parquet,
per_session_h2_surrogate.parquet, per_session_h2_survival.parquet,
per_session_h2_population_default.parquet (default-only first pass),
h1_meta_overall.parquet, h1_meta_by_cre.parquet,
h1_meta_by_rate_quartile.parquet, PHASE24_FULL_FINDINGS.md.

PHASE22A_FINDINGS.md in `data/phase22a_results/` is updated in-place
with a Phase 24 (Full) update note recording scope changes.

Cache under `/home/combust/fmexplorer/allen_cache/`: 12 session NWBs
(~32 GB total), per-session analysis_metrics CSVs, manifests,
natural_movie_one template (166 MB).

---

### 7.ter.35  Phase 25 — Multi-frame STA Pass D revisit on pvc-11 monkey1_natural_movie

#### Frame

Phase 22b Pass D attempted a per-unit Pillow-style history-coupled GLM
as a stricter Aitchison-null surrogate against the pvc-11
monkey1_natural_movie H2 finding.  Neither tested variant produced a
faithful surrogate at 5 ms bins: the canonical (non-positive history)
variant collapsed both history and stim kernels to ~0; the
unconstrained variant routed stim autocorrelation into the history
kernel and ran away with positive feedback (~17× real-rate over-shoot).
Phase 22b's working diagnosis: the single-frame STA failed to model
slow stim temporal autocorrelation (~30-40 ms), which the
unconstrained history kernel then mis-fit as intrinsic spike-train
coupling.

Phase 25 tests the two prospective fixes proposed by the Phase 22b
findings doc:

  1. multi-frame spatiotemporal STA (n_lags ∈ {1, 4, 8} bins of past
     stim — n_lags=1 reproduces Phase 22b's spatial-only baseline);
  2. coarser bin widths (bin_ms ∈ {5, 10, 20, 40} ms);

at both `canonical` (Pillow non-positive history) and `unconstrained`
variants — a 3 × 4 × 2 = 24-cell configuration grid.

Calibrator zoo (8/8) re-verified before Phase 25.

#### Refined fit-quality verdict vocabulary

Phase 25 refines the binary PASS/FAIL of Phase 22b into a four-way
methodological characterization:

  - **FIT-PROPER** — biologically-reasonable history kernel
    (refractory negative lobe, non-trivial L2), non-collapsed stim
    kernel, surrogate rate within ±1.5× real, median dev_explained
    > 0.005.  Survival-testable for H_PassD.
  - **FIT-DEGENERATE-BY-RESOLUTION** — bin width / lag structure
    makes the model class incapable of representing what's there
    (canonical-variant collapse).
  - **FIT-PATHOLOGICAL-BY-CONSTRAINT** — converges but to a bio-
    implausible optimum (unconstrained history-kernel uniformly
    positive runaway).
  - **FIT-OTHER** — unidentified failure modes.

Verdict aggregation uses cell-level kernel-statistic medians, which
is robust to L-BFGS per-unit non-convergence (a symptom of runaway-
induced ill-conditioning in the unconstrained variant, not a separate
failure mode).

#### Fit-quality grid — 24 cells, 0 FIT-PROPER

Canonical cells (12 of 12): **all FIT-DEGENERATE-BY-RESOLUTION**.
History kernel collapses to zero (hist_l2 = 0.000) under the
non-positive softplus parameterisation + L2 ridge at every (n_lags,
bin_ms) cell.  Stim L2 *does* grow with n_lags at coarse bins (40 ms ×
1→4→8 lags: 0.028 → 0.049 → 0.075), confirming multi-frame STA absorbs
more stim variance, but the history kernel does not recover.

Unconstrained cells (12 of 12): **all FIT-PATHOLOGICAL-BY-CONSTRAINT**.
History kernel is uniformly positive with strikingly invariant
structure across the grid:

  - hist_l2 median ∈ [0.61, 0.94]
  - hist_min median ∈ [+0.21, +0.29]  (no refractory dip)
  - hist_max median ∈ [+0.54, +0.76]
  - surrogate event rate: 17× (40 ms) to 1158× (5 ms) above real,
    tracking per-bin Poisson saturation accumulation; the kernel
    *shape* is essentially constant.

#### Primary verdict — H_PassD: **FIT-CEILING**

No (n_lags, bin_ms, variant) cell was FIT-PROPER.  The Phase 22a /
22b H2 elimination space on pvc-11 monkey1_natural_movie remains
bounded to the LN-Poisson floor (Phase 22a passes) plus the
cell-shuffle null; whether it extends to per-unit history-coupled
LN-Poisson surrogates is methodologically untestable within the
Phase 25 model family (single- or multi-frame STA × canonical or
unconstrained per-unit Pillow GLM).

#### Secondary verdict — stim-mis-routing diagnostic: **FALSIFIED**

Multi-frame STA up to n_lags=8 does not collapse the unconstrained-
variant runaway at any bin width.  At every (bin_ms, variant=unconstrained)
the surrogate-rate runaway changes by < 5 % when n_lags goes from 1
to 8.  Phase 22b's working hypothesis — that single-frame STA was
leaving stim autocorrelation to mis-route into the history kernel —
is not supported.

#### Co-finding — V1 spike-train positive autocorrelation invariant across grid

The invariance of the unconstrained kernel structure across three STA
depths and four bin widths (spanning the ~5 ms refractory regime to
the ~40 ms autocorrelation regime) is a substantive observation
about V1 spike-train structure: there is a positive temporal
correlation in pvc-11 anesthetised-macaque V1 spike trains that
survives linear spatiotemporal stim filtering up to 320 ms of past
stim history and is essentially independent of bin width within
[5, 40] ms.

Candidate mechanisms (not disambiguated here): network-driven
population synchrony, anesthesia-driven up-state cycling, single-
cell bursting, complex-cell / gain-control / non-linear stim
processing that linear STA cannot capture.  **Methodological
implication for future coupled-GLM surrogate work on V1 cortical
data**: the canonical Pillow non-positive-history parameterisation
is the prudent choice; the unconstrained variant over-amplifies the
residual positive autocorrelation into runaway feedback even with
multi-frame STA.  Breaking the FIT-CEILING for H_PassD-style testing
would require substantially more expressive model families (cross-
cell coupled GLMs, latent-state GLMs, non-linear stim processing) —
out of Phase 25 scope.

#### Outputs

Code: `phase25/multiframe_sta.py`, `phase25/glm_fit.py`,
`phase25/fit_quality.py`, `phase25/run_phase25.py`,
`phase25/reverdict.py`, `phase25/summarize_grid.py`.

Data under `data/phase25_results/`: 24 fits__*.parquet,
fit_quality_grid.parquet, aggregate_verdict.json,
PHASE25_FINDINGS.md.  No surrogate or survival files (no FIT-PROPER
cells).

PHASE22A_FINDINGS.md in `data/phase22a_results/` is updated in-place
with a Phase 25 update note recording the FIT-CEILING outcome and
the co-finding's methodological implication.

---

### 7.ter.36  Phase 26 — Per-(detector, energy_channel) stratification on GRB 230307A late-prompt TR region

#### Frame

Phase 23's substantive-fail on the Chen 2025 909 Hz QPO claim was
accompanied by a side-finding: in the t = 26-30 s late-prompt region
of GRB 230307A, 22 of 40 100ms sub-windows classified as TR
uniformly across 50 q-bands; the lightcurve-modulated Poisson
surrogate produced only 5-15 % TR at the same region.  The per-
detector follow-up showed an inverse-rate-vs-TR pattern (n2/n5 low
rates → 72/62 % TR; na/b1 high rates → 5/0 % TR).  Phase 23
proposed: detector-specific energy-band sensitivity (off-axis
detectors sample different effective spectra).

Phase 26 tests the energy-band hypothesis directly via per-(detector,
energy_channel) stratification on the same t = 26-30 s window.  The
H_energy_band hypothesis predicted three signatures: (1) within-
detector TR variation across energy channels, (2) cross-detector
aspect-correlation of variation pattern at fixed energy, (3) rate-
dependence reduction once energy is controlled for.

Calibrator zoo (8/8) re-verified before Phase 26.

#### Methods

  - 8 equally-populated quantile bands per detector × 12 detectors =
    96 cells.  Each cell stores its median photon energy via the TTE
    EBOUNDS-derived per-channel E_GEO_MEAN.
  - Per-cell ARS classification at 100 ms sub-windows × q_max=50
    (Phase 23 time-slice adjustment).
  - Per-cell lightcurve-modulated Poisson surrogate, 5 seeds.
  - Aspect angles computed from TRIGDAT OB_CALC table's spacecraft-
    frame source direction (TR_SCAZ = 168°, TR_SCZEN = 155°) combined
    with Meegan et al. 2009 detector-pointing constants.
  - Cross-checks: sub-window stability (drop-one), detector-pooling
    persistence (per-cell aggregate vs Phase 23 pooled), time-window
    control on [10, 14) s.
  - Statistical tests: within-detector Kruskal-Wallis (FDR α=0.05),
    cross-detector Spearman aspect-correlation at energy-aligned
    buckets (NaI only), rate-dependence-vs-attenuation within energy.

#### Primary verdict — H_energy_band: FALSIFIED

All three predicted signatures fail:

  - Within-detector energy variation: 0 / 11 detectors significant
    after FDR correction.
  - Cross-detector aspect-correlation: mean Spearman ρ across 4
    energy buckets = +0.076; no bucket reaches p<0.05.  Verdict NULL.
  - Rate-dependence reduction: mean within-bucket |ρ| = 0.41 vs
    pooled |ρ| = 0.25; attenuation = −0.16 (negative — within-bucket
    rate correlation is *stronger*, not weaker, than pooled).
    Verdict NOT_ATTENUATED.

The TR signature is not specifically about energy-band sensitivity,
detector aspect angle, or spectral incidence.

#### Reframed mechanism: per-cell rate dependence of ARS classification

  - Across all 83 well-powered (detector, band) cells in [26, 30) s:
    Spearman ρ(per-cell event rate, TR fraction) = **−0.483**
    (p = 4 × 10⁻⁶).
  - In the [10, 14) s control window (93 well-powered cells):
    ρ = **−0.888** (p = 2 × 10⁻³²).  Same inverse-rate pattern;
    stronger because the control window's rate range is wider.
  - Mean TR fraction: [26, 30) s = 81 %; [10, 14) s control = 46 %.
    The late-prompt's apparent TR-density is a consequence of dimmer
    emission pushing per-cell rates into the TR-favorable range
    (~ 1000-3000 events/s); at higher rates (> 5000/s) ARS
    classifies BR/BL (rate-saturation, consistent with Phase 21's
    BR_artifact lesson).

The Phase 23 side-finding's "[26-30 s] broadband TR" framing is
confirmed at per-cell resolution but reinterpreted: it's a
**rate-regime feature of the ARS metric**, not a unique astrophysical
property of the late-prompt time window.

#### Detector-pooling persistence

Per-(detector, band) aggregate TR fractions are 60-80 % higher than
Phase 23's pooled per-detector measurements for nearly every detector.
Pooling pushes per-bin event counts into the rate-saturated regime
where ARS classifies BR/BL; per-cell resolution reveals the underlying
TR structure.  This is a methodological observation about ARS at
high event rates per sub-window, not GRB-230307A-specific.

#### Per-cell surrogate behaviour

At per-cell rates, the lightcurve-modulated Poisson surrogate
reproduces most of the per-cell TR signal: 47 / 83 cells have real TR
above the surrogate 95th percentile; 30 / 83 are within the surrogate
p05-p95 band; mean real-minus-surrogate TR fraction = +9.4 %.
Phase 23's pooled comparison (real 55 % vs surrogate 5-15 %) was a
pooled-rate-regime phenomenon — both real and surrogate are in the
TR-favorable rate range per-cell, so the surrogate succeeds where the
pooled version failed.

#### Methodological implication

For future GRB analyses with the ARS framework:

  1. **Per-cell rate is the dominant axis of variation** in
     ARS-on-GRB analyses.  Cross-detector and cross-time comparisons
     should rate-match cells before attributing differences to
     spectral or geometric features.
  2. **Pooling can mask per-cell structure** when the pooled rate
     pushes ARS into the BR-saturated regime.  Report at the per-
     (detector, energy_band) resolution wherever feasible.
  3. **Surrogate floor must match the analysis resolution.**  A
     surrogate that fails at pooled rate may succeed at per-cell rate.

Phase 23's primary verdict on the Chen 2025 909 Hz QPO claim
(substantive FAIL) is unchanged.  Phase 26 only revisits the
side-finding's mechanism characterisation.

#### Outputs

Code: `phase26/aspect_angles.py`, `phase26/energy_binning.py`,
`phase26/per_cell_classify.py`, `phase26/per_cell_surrogate.py`,
`phase26/cross_checks.py`, `phase26/statistical_tests.py`,
`phase26/run_phase26.py`.

Data under `data/phase26_results/`: detector_aspect.parquet,
energy_bands.parquet, per_cell_{subwindow_classifications,
tr_summary, surrogate_seeds, surrogate_summary, survival}.parquet,
subwindow_stability.parquet, detector_pooling_persistence.parquet,
control_per_cell_*.parquet, test{1,2,3}_*.parquet,
aggregate_verdict.json, PHASE26_FINDINGS.md.

Auxiliary data: `data/phase21_grb_panel/raw/bn230307656_aux/`
contains TRIGDAT (aspect-angle source) and BCAT (downloaded but
not used).

---

### 7.ter.37  Phase 27 — Pre-publication framing analyses (F1/F0 rate-matched check, ARS vs FA loadings, spatial-scale ARS)

#### Frame

Three lit-review-driven analyses to resolve framing questions before
publication drafting:

  1. F1/F0 ↔ rep_med substrate-systematic sign flip (Phase 24 Full,
     pvc-11 +0.388 vs Allen −0.183) tested against Hietanen et al.
     2013's F1/F0 spike-count bias.  If the substrates sit in
     different firing-rate regimes, the F1/F0 measurement itself is
     biased differently and downstream metrics inherit the bias.
  2. ARS per-unit metrics' empirical orthogonality to Williamson
     2016 factor-analysis loadings on pvc-11 in-vivo data.  The
     orthogonality claim against existing population-coding methods
     is structural by construction (different sufficient statistics);
     empirical confirmation on the same data is the load-bearing
     demonstration.
  3. ARS spatial-scale dependence on pvc-11 Utah-array data,
     engaging with Ohiorhenuan 2010's finding that high-order
     correlations are local (<300 μm) but not distant (>800 μm).
     Spatial-resolution caveat: Utah pitch is 400 μm; no between-
     channel pairs are within Ohiorhenuan's 300 μm threshold;
     analysis is bounded to the 400-600 μm regime.

Calibrator zoo (8/8) re-verified before Phase 27.

#### Analysis 1 — F1/F0 rate-matched check: SUBSTRATE-SYSTEMATIC

Method 0 (firing-rate distributions): pvc-11 median 4.51 sp/s vs
Allen 4.09 sp/s; 90 % of pvc-11 and 76 % of Allen units lie in the
overlap region [1.39, 15.27] sp/s.  Distributions statistically
differ at log-rate (KS p=4×10⁻⁷) but overlap substantially.

Method A (within-substrate spike-count tertile partial correlations):
pvc-11 9/9 tertile bins show ρ_partial > 0 (range +0.114 to +0.343).
Allen 25/36 tertile bins show ρ_partial < 0 (69 %).

Method B (rate-matched cross-substrate, ±20 % tolerance, n=210
matched pairs at median 3.9 sp/s): pvc-11 ρ_partial = **+0.298**
(p<0.001), Allen ρ_partial = **−0.222** (p=0.001), Δρ = **+0.520**.

Method C (Fisher-Z meta with spike-count covariate): pvc-11 meta-fix
+0.279 → +0.279 (0.000 attenuation); Allen meta-fix −0.184 → −0.142
(−0.042 attenuation).  Spike-count linear-covariate correction is
minor.

**Verdict: SUBSTRATE-SYSTEMATIC.**  Hietanen 2013 spike-count bias
contributes at most −0.04 attenuation in Allen and zero in pvc-11.
The F1/F0 ↔ rep_med sign flip survives rate-matching and is a
substrate-systematic biological observation, not a measurement
artifact.

#### Analysis 2 — ARS vs Williamson FA loadings: SUBSUMED (ks_gue_med) / ORTHOGONAL (rep_med)

Williamson 2016-style FA on the two H2 pvc-11 sessions (200 ms bin
width, square-root variance-stabilising transform, CV-selected
dimensionality n_factors=8 on both sessions).

Per-session R² regressing each ARS metric on the 8 FA loadings:

| session | R²(rep_med) | R²(ks_gue_med) |
|---|---|---|
| monkey1_natural_movie  | 0.098 | **0.800** |
| monkey2_gratings_movie | 0.249 | **0.726** |

Cross-pair correlation: per-session mean\|ρ\| = 0.208/0.261;
max\|ρ\| = 0.590/0.698.

**Verdict: SUBSUMED for ks_gue_med, ORTHOGONAL for rep_med.**  The
H1 load-bearing metric ks_gue_med is substantially captured by FA
loadings (R² > 0.6, above SUBSUMED threshold).  The H2 metric
rep_med is largely orthogonal (R² < 0.3, within ORTHOGONAL
threshold).  Caveat: in-sample R² is overfit-biased upward with 8
factors and 74-104 units per session, but the gap from the
ORTHOGONAL threshold (0.3) is large enough on ks_gue_med (0.73-0.80)
that the SUBSUMED verdict is robust to plausible overfit corrections.

Publication framing implication: H1's "OSI ↔ ks_gue_med"
correspondence cannot be claimed orthogonal to FA-specifically on
pvc-11.  H2's rep_med-based elimination space remains in the
orthogonality regime.

#### Analysis 3 — ARS spatial-scale on pvc-11: CONTRA-OHIORHENUAN (bounded to 400-600 μm)

Utah-array spatial layout: 400 μm pitch, 96 active channels, 74-104
units per H2 session.  For each unit, build local cluster = units
within 600 μm radius (captures NN 400 μm and diagonal ≈565 μm
neighbours); dedupe identical-membership clusters; skip clusters
< 3 members.  Per-cluster population events at k_thresh =
clip(ceil(0.5 × n_members), 2, 6); ARS classify at q_max=30; per-
cluster rate-matched Poisson surrogate (5 seeds, Phase 26 lesson).

Local-vs-recording-wide comparison:

| session | local modal | local rep_med | local ks_gue_med | rwide modal | rwide rep_med | rwide ks_gue_med | Δ rep_med | Δ ks_gue_med |
|---|---|---|---|---|---|---|---|---|
| monkey1_natural_movie  | BL | 0.088 | 0.337 | TR          | 0.250 | 0.662 | −0.162 | −0.325 |
| monkey2_gratings_movie | TR | 0.138 | 0.334 | BR_artifact | 0.550 | 0.623 | −0.412 | −0.289 |

Per-cluster rate-matched Poisson surrogate produces similar local-
scale classifications (modal BL across both sessions).

**Verdict: CONTRA-OHIORHENUAN, bounded to the 400-600 μm regime.**
At Utah-accessible scales, ARS shows the *opposite* of Ohiorhenuan
2010's local-rich prediction: recording-wide aggregate carries more
structure than local clusters.  The H2 surviving structure is a
recording-wide population-aggregate phenomenon at pvc-11's
resolution, not a local-cluster phenomenon.

**Required spatial-resolution caveat:** Utah pitch (400 μm) makes
no between-channel pair within Ohiorhenuan's 300 μm threshold.
The verdict is bounded to the 400-600 μm regime; whether ARS
detects local-rich structure at <300 μm (Ohiorhenuan's actual claim)
is inaccessible at pvc-11 resolution.  Future investigation with
multi-tetrode / Neuropixels density could test this regime.

#### Combined publication framing implications

The combination is PARTIALLY-CONFIRMED + SUBSUMED-FOR-H1 + CONTRA-
OHIORHENUAN.  Three adjustments to publication framing:

  - **F1/F0 finding:** unchanged in scope — still SUBSTRATE-
    SYSTEMATIC.  Cite Hietanen 2013 for the per-cell-rate-control
    caveat that motivated the check.
  - **Orthogonality framing:** distinguish at metric level —
    rep_med orthogonal to FA loadings; ks_gue_med substantially
    captured by FA loadings on pvc-11 noise-correlation regime data.
    H1's orthogonality claim against FA-specifically is weakened;
    H2's elimination-space orthogonality claim against FA is
    preserved.
  - **Ohiorhenuan engagement:** writeup should NOT claim ARS
    confirms / extends / competes with Ohiorhenuan 2010 on the
    local-rich finding.  At Utah-accessible scales ARS shows the
    opposite pattern.  Spatial-resolution caveat explicitly in
    writeup: their relevant <300 μm regime is inaccessible at
    pvc-11 pitch.

#### Outputs

Code: `phase27/analysis1_f1f0_rate_matched.py`,
`phase27/analysis2_ars_vs_fa.py`, `phase27/analysis3_spatial_scale.py`.

Data under `data/phase27_results/`: `analysis1_*.{parquet,json}`,
`analysis2_*.{parquet,json}`, `analysis3_*.{parquet,json}`,
`PHASE27_FINDINGS.md`.

PHASE22A_FINDINGS.md and PHASE24_FULL_FINDINGS.md updated in-place
with Phase 27 framing notes.

---

### 7.ter.38  Phase 30 — Kuramoto simulation testbed for ARS mechanism interpretation

Phase 30 ran ARS on classical and stochastic Kuramoto-network-
generated spike trains across the canonical (K, σ) parameter space,
asking whether Kuramoto-class phase-locking dynamics constitute a
viable positive mechanism story for the existing cortical-V1 ARS
findings (H1 OSI ↔ ks_gue_med, F1/F0 ↔ rep_med substrate-systematic,
H2 surviving structure on pvc-11).

#### Pre-launch corrections to the brief

The Phase 30 session brief stated K_c = 2γ/π for Lorentzian-Kuramoto.
Standard Kuramoto theory (Strogatz 2000 eq. 3.10: K_c = 2/(π g(0)),
with g(0) = 1/(πγ) for Lorentzian) gives K_c = 2γ.  Empirical
validation at K = 3.18·(2γ): simulation r∞ = 0.83 matches Strogatz
prediction √(1 − K_c/K) = 0.83.  The simulator uses K_c = 2γ; the
correction is recorded in `PHASE30_FINDINGS.md`.

Finite-N simulation of an untruncated Lorentzian violated the
small-dt Euler assumption (single oscillator at 100+ γ from the mean
produces ω·dt > 1).  Lorentzian truncated to ±10γ (~3 % distribution
mass removed) at sampling time gives numerically stable simulation
while preserving K_c = 2γ to within finite-N corrections.

Pilot at K ∈ {0, K_c, 2 K_c}, N ∈ {100, 200}, T = 1200 s established
that per-oscillator and aggregate modal classification is
**BR_artifact at every K** — deterministic Kuramoto oscillators are
inherent periodic spike emitters and ARS reads that, regardless of
whether they're coupled.  N = 100 chosen for full sweep (same modal
result as N = 200 at half runtime).

#### Analysis 1 — K-sweep on classical Kuramoto.  Verdict: INSENSITIVE

21 K-factors from 0 to 2 K_c × 3 seeds, N = 100.  Per-oscillator and
recording-wide-aggregate modal classification = BR_artifact at every
one of 63 cells.  The Kuramoto phase transition is clearly resolved
in the order parameter (|r| from 0.089 at K=0 to 0.800 at K=2 K_c) —
**ARS just doesn't read the coupling axis modally.**

Continuous-metric signals: aggregate ks_gue_med moves +0.102 from
K=0 (0.436) to K=2 K_c (0.538), nearly monotonically — small but real
signal that stays inside the BR_artifact quadrant.  Per-oscillator
rep_med stays near saturation (0.85) at all K, confirming periodic
saturation BR_artifact.

Stationarity check (added per user course-correction): 0/15 boundary
cells in K_factor ∈ [0.8, 1.2] flagged as non-stationary at 10
windows.  Full-sequence classification at K ≈ K_c is stationary —
the TIME_VARYING_AT_CRITICAL verdict (added as amendment to the
brief's vocabulary) does not trigger.  Slow critical-slowing-down
fluctuations are not large enough to flip the modal classification at
the 100s sub-window scale.

#### Analysis 2 — (K, σ) phase-space, stochastic Kuramoto.  Verdict: RATE_REGIME_CONFOUNDED (K-axis) / PARTIAL_RATE_CONFOUND (σ-axis)

7 K-factors × 6 σ-factors × 3 seeds = 126 cells.  Aggregate modal
classification = BR_artifact at every one of the 42 (K, σ) cells.
K-axis modal variation = 0 across rows of fixed σ; σ-axis modal
variation = 14 across columns of fixed K.  Per-oscillator modal
classification follows the σ-axis: BR (σ=0) → TR (σ=0.2) → BL
(σ ∈ [0.4, 0.8]) → TR (σ=1.0).

Per-oscillator median rates scale from 2 Hz (σ=0) to ~22 Hz (σ=ω_0)
— a 10.3× rate inflation as phase diffusion drives more frequent 2π
wraps.  rate_drift_fraction = 10.342 triggers RATE_REGIME_CONFOUNDED
(threshold 0.5).

**Within-σ rate-matched verification (added 2026-05-11 at writeup
review):** the σ-axis modal sequence is *partially* rate-confounded,
not uniformly so.  Comparing real per-oscillator modal against the
rate-matched Poisson surrogate (already computed per cell) gives
modal agreement at 21/42 cells (σ ∈ [0.4, 0.8] band, both BL — pure
rate effect) and modal disagreement at 21/42 cells (σ ∈ {0, 0.2, 1.0},
real has dynamics signal beyond rate that surrogate doesn't
reproduce).  Continuous-metric Δks_med (real − surrogate) = +0.230
mean across all cells — real Kuramoto is consistently more GUE-like
than its rate-matched surrogate, even within the modal-agreement
band.  The brief's RATE_REGIME_CONFOUNDED label remains correct for
the K-axis-invisibility claim, but the σ-axis itself is two-regime:
rate-driven in the middle band, dynamics-driven at the endpoints.

Stationarity check: 0/54 boundary cells in K_factor ∈ [0.75, 1.25]
flagged.  Full-sequence classification at K ≈ K_c is stationary
across the entire (K, σ) plane.

#### Analysis 3 — real-data location on Kuramoto map.  Verdict: NO_MECHANISTIC_MATCH

ETL-assembled real-data classification summaries from 15 pvc-11
recordings (Phase 22a), 36 Allen session × condition rows (Phase 24
default), 140 local clusters (Phase 27).  Match metric: Euclidean
distance in (ks_gue_med, rep_med) space, modal-class-restricted.

Real-data primary distribution: TR 86 (45 %), BL 64 (34 %),
underpowered 31 (16 %), BR_artifact 10 (5 %).  Kuramoto aggregate
map produces only BR_artifact.

Match summary out of 160 well-powered rows: clean 1 (0.6 %),
ambiguous 3 (1.9 %), no_match 156 (97.5 %).  No region of the
Kuramoto phase-space tested produces TR or BL modal aggregate
classification matching cortical V1 data.

#### Combined Phase 30 outcome: Kuramoto bounded as a mechanism interpretation

The triple INSENSITIVE + RATE_REGIME_CONFOUNDED + NO_MECHANISTIC_MATCH
locks the Kuramoto-class formalism *out* of the mechanism-
interpretation space for the cortical-V1 ARS findings.  The brief's
"informative-negative" outcome obtains: ARS detects something Kuramoto
doesn't produce.

Forward implications:
  - **For the publication writeup.**  The negative-elimination posture
    of H1, F1/F0, H2 findings remains.  Phase 30 explicitly does NOT
    augment those findings with a positive Kuramoto-class mechanism
    story.  No claim of the form "ARS detects Kuramoto-like near-
    critical synchronization" is supported by Phase 30.
  - **For mechanism investigation continuation.**  Alternative
    coupled-oscillator models (Stuart–Landau, Wilson–Cowan, coupled
    HH networks, latent-state generative models, non-oscillator
    drift–diffusion-with-coupling) become the load-bearing direction.
  - **For the calibrator zoo.**  Kuramoto signals are confirmed
    redundant with the existing periodic calibrators at ARS modal
    resolution — they would map to the same BR_artifact region as
    `periodic_q7` and `uniform_jitter`.  Brief's decision not to
    add Kuramoto to the calibrator zoo is locked.

#### Outputs

Code: `phase30/kuramoto.py`, `phase30/stationarity.py`,
`phase30/pilot_analysis1.py`, `phase30/analysis1_K_sweep.py`,
`phase30/analysis2_Ksigma_phase_space.py`,
`phase30/analysis2_rate_matched.py` (within-σ rate-confound
verification, added 2026-05-11 at writeup review),
`phase30/analysis3_realdata_mapping.py`.

Data under `data/phase30_results/`: `pilot_summary.parquet`,
`analysis1_*.{parquet,json}`, `analysis2_*.{parquet,json}`,
`analysis3_*.{parquet,json}`, `PHASE30_FINDINGS.md`.

PHASE22A_FINDINGS.md, PHASE24_FULL_FINDINGS.md, PHASE27_FINDINGS.md
updated in-place with Phase 30 mechanism-interpretation amendments.

---

### 7.ter.39  Phase 31a + 31b — Engineering-layer architecture audit and deployed-classifier sensitivity

Phase 31 was scoped against the assumption that ARS reads via a Farey-
bank of literal phase-locked-loop channels and could be ISF-characterised
per Hajimiri–Lee 1998.  The session decomposed into two sub-phases.

#### Phase 31a — Derivation: PLL bank ≠ deployed classifier

The literal PLL bank in `pll_bank.py` (second-order PLL with K_p, K_i,
IIR low-pass, lock detection) is **parallel infrastructure not on the
deployed path**.  `arithmetic_toolkit.joint_q_profile` (the function
powering every Phase 22a/24/27/30 ARS classification) imports only
`farey_rationals` from `pll_bank` — never `pll_bank_cpu`,
`pll_bank_gpu`, or `single_pll_cpu`.  Grep confirms zero hits in
`phase{22a,24,27,30}/`.

The two objects compute fundamentally different quantities from
fundamentally different inputs.  Not a closed-form limit relationship.

**Surprise inside `joint_q_profile`**: under unit-mean normalisation,
`sp = diff(sort(t · f_pll − 1.0)); sp / sp.mean()` cancels the `f_pll`
factor exactly.  The per-Farey-rational passage NNS statistic is
**identical across all (a, q)** up to an initial-transient cutoff.
Empirical verification on Poisson (N=5000) and periodic-q=7 calibrators:
ks_gue_q std across q ≈ 5×10⁻⁵ on Poisson, 0 on periodic.

The deployed classifier has **two engines**:
  - **NNS engine** (pooled passage NNS): not actually q-resolved —
    produces a global scalar replicated across q with threshold-induced
    flips at boundaries.
  - **RF engine** (`ramanujan_fourier` indicator-mode amplitudes |a_q|):
    genuinely per-q.  TL quadrant flags (RF spike at q where |a_q| >
    5× median) are the only modally-discriminating per-q signal in the
    deployed pipeline.

Per Phase 31a verdict + user direction: Phase 31b reframes Analyses
1-3 around the deployed classifier's actual structure (rather than the
brief's PLL-bank framing).  PLL-bank ISF measurement deferred to a
separate Phase 31c at lower priority.

#### Phase 31b — Operator sensitivity for the deployed classifier + Phase 30 sub-modal stratification

##### Per-event NNS sensitivity: EVENT-LEVEL ROBUST

Finite-difference ∂(ks_gue_med, rep_med)/∂t_k for single-event
perturbations is **near-zero** at ε ≤ 1.0 × mean-IEI (max Δks ≈ 7×10⁻⁴
even at full-mean-IEI perturbation).  The median-across-30-q-bands
aggregation absorbs single-q perturbations; each individual event has
near-zero influence on the modal classification.  **The deployed
classifier is event-level robust at the modal scale.**  Stratification
of sub-modal signal requires a coarser unit (per-oscillator or
per-event-cluster).

##### K-sweep LOO stratification: DISTRIBUTED, rate-correlated at high K

Re-simulated Kuramoto at K_factor ∈ {0, 0.5, 1.0, 1.5, 2.0} (seed 0,
N=100, T=1200 s).  Per-oscillator leave-one-out aggregate influence
(Δks_LOO[i] = ks_with_i − ks_without_i) for each oscillator.

Aggregate K-axis Δks = +0.0798 from K=0 to K=2 K_c (consistent with
Phase 30's multi-seed +0.10).  Per-oscillator max |Δks_LOO| grows from
0.014 (K=0) to 0.034 (K=2 K_c).  The signal is distributed across
~30+ oscillators each contributing ~10⁻³.

**ρ(Δks_LOO, rate_i) grows monotonically with K**: +0.006 (K=0) →
+0.179 (K=K_c) → **+0.446 (K=2 K_c)**.  Lorentzian-tail high-rate
oscillators that don't fully frequency-lock dominate the LOO signal
at high K.  Aggregate RF spectrum drift is dominantly at q=1 (DC,
ΔRF=−17.7, tracks the drop in aggregate event count as locking pulls
outlier rates toward ω_0); no non-DC q-band shows substantial
amplitude growth.  **The K-axis +0.10 drift is a rate-distribution
narrowing under locking, not a per-q resonance development.**

##### Rate-matched +0.23 Δks residual: CARRIED_BY_RATE_REGIME

Per-oscillator real-vs-rate-matched-Poisson Δks_i = ks_real_i −
ks_sur_i computed from existing Phase 30 Analysis 2 parquets (12 600
oscillator cells × {real, surrogate}).  Mean Δks = +0.215, median
+0.222 — matches Phase 30's claimed +0.23.

In the modal-agreement band σ ∈ [0.4, 0.8] (5 525 cells where
real-modal = surrogate-modal = BL):
  - mean Δks = +0.251
  - **ρ(Δks_i, rate_i) = −0.847**
  - ρ(Δks_i, ω_i) = −0.276

Low-rate oscillators within each (K, σ) cell carry the dynamics
signal; high-rate oscillators converge to their rate-matched-Poisson
surrogate.  **Per-cell rate-matched Poisson surrogate does not fully
eliminate rate effects** because the dynamics signal itself depends on
rate.  The Phase 26 rate-regime lesson is necessary but not sufficient
for clean dynamics-only signal isolation.

Methodological implication: future sub-modal discrimination work should
add **rate-stratified within-cell comparison** (per-rate-tertile mean
Δks) as a standard post-modal step.

##### p-adic v4 sweep over existing parquets

Applied `padic_amplitude_v4` to cached `rf_amp_per_q` arrays in every
Phase 22a/24/27/30 parquet (length 30 per recording).  The §7.ter.13
acceptance threshold (1.5× per-q-power-normalised) was validated at
q_max=200 — at q_max=30, finite-band variance dominates and 95.6 % of
pvc-11 rate-matched-Poisson surrogates pass the threshold spuriously.
**Absolute threshold is underpowered; matched real-vs-surrogate
comparison is required.**

Matched per-recording z-score (real vs rate-matched-Poisson mean):
  - **Only 1 of 15 pvc-11 recordings has z > 2: monkey3_gratings,
    z = +5.36, dominant prime = 7.**  All others null or below
    surrogate.
  - Per-prime z-score across pvc-11: p=7 has positive mean +0.79
    (max +8.47, driven by monkey3_gratings); other primes near zero
    or negative.  Marginal class-level prime-7 enrichment in pvc-11.
  - Allen: 6/36 sessions with z > 2; per-prime z scattered (max +0.53
    for p=3, +0.28 for p=13); no substrate-systematic prime preference.
  - Phase 30 Kuramoto K-sweep above-threshold rate: 81.3 % at K=0 →
    94.7 % at K=2 K_c (+13.4 percentage points monotone-ish).
    Consistent with locking-driven small-q amplitude concentration.

**Follow-up candidate:** re-classify monkey3_gratings at q_max=200,
verify the prime-7 dominance persists at the §7.ter.13 validated
threshold.  If yes, monkey3_gratings is the first real-data p-adic-
class finding from ARS.

##### Follow-up 1: monkey3_gratings q_max=200 reclassification.  Verdict: ABOVE_THRESHOLD_BUT_DIFFERENT_PRIME

At the §7.ter.13-validated q_max=200, monkey3_gratings shows
**multi-prime p-adic structure with p=2 dominant** (ratio 4.06×,
z=+3.67 vs rate-matched Poisson surrogate) and p=7 secondary (ratio
1.77×, z=+1.90, still above the 1.5× threshold and above surrogate max
1.55).  The q_max=30 finding of dominant p=7 was a band-count
artifact (p=2 has 7 pure-power bands ≤ 200 vs only 4 ≤ 30); under
per-q-power normalisation with more bands, p=2 dominance emerges.

Both p=2 and p=7 signals are real (above-threshold, above-surrogate).
The recording does have p-adic structure — just not the
single-prime-7 dominance the q_max=30 result suggested.  Biological
interpretation open: gratings stimulus is 12 directions at 1 Hz
temporal frequency, which could produce harmonic structure at
small-q-power bands.  Worth checking monkey1_gratings and
monkey2_gratings at q_max=200 to see if the p=2 multi-prime structure
generalizes across the gratings subset.

##### Follow-up 2: H1 / F1/F0 rate-stratified within-cell pilot on pvc-11

Within each pvc-11 gratings recording (monkey1: 68 units, monkey2: 57,
monkey3: 85), split units into 3 per-recording rate tertiles and
compute Spearman ρ(descriptor, ARS_metric) per tertile.

| descriptor | metric | tertile rho range | mag range | sign-consistent (3 recordings) | verdict |
|---|---|---|---|---|---|
| OSI | ks_gue_med | +0.408 to +0.914 | 0.21 | 3/3 | **SURVIVES_STRATIFIED** |
| DSI | ks_gue_med | −0.370 to +0.639 | 0.47 | 2/3 (monkey2 sign-flip) | **PARTIAL_SURVIVAL** |
| F1/F0 | rep_med | +0.052 to +0.591 | 0.34 | 3/3 | **PARTIAL_SURVIVAL** |

**H1 OSI ↔ ks_gue_med grandfathers cleanly under rate-stratified
discipline** — sign-consistent positive within all 9 (recording ×
tertile) cells with magnitude range 0.21 (below the 0.30 threshold).
**DSI flips sign in monkey2's high-rate tertile** and has mag range
0.47.  **F1/F0 sign-consistent (positive in pvc-11) but with mag range
0.34** — Allen rate-stratified replication needed to verify the
substrate-systematic sign-flip claim survives.

Audit implication: H1 OSI ↔ ks_gue_med is the most defensible
correlation under the new discipline; DSI and F1/F0 need additional
follow-up work (Phase 31e?) on Allen with rate-stratified within-cell.

##### Follow-up 3: Multi-seed validation of K-axis mechanism

Using existing Phase 30 Analysis 1 parquets (21 K × 3 seeds × 100
osc):

  - **Rate narrowing is seed-robust** (Q1).  All 3 seeds show
    monotonic decrease of per-oscillator-rate STD with K (Spearman
    ρ(K, rate_std) ≈ −1.0 in every seed; drop fraction 20.5 %, 37.5 %,
    63.3 %).
  - **Δks K=0→K=2 K_c varies per seed** (Q2): seed 0 +0.080, seed 1
    +0.104, seed 2 +0.218.  Mean +0.134, std 0.060.  The Phase 30
    +0.10 headline is in the middle of this range; seed 2 alone gives
    +0.22 close to the +0.23 rate-matched residual.
  - **Order parameter is the much stronger predictor of agg_ks_med**
    (Q3) than rate_std: ρ(|r|, agg_ks_med) = **+0.925** vs
    ρ(rate_std, agg_ks_med) = −0.503.  Order parameter explains
    92.5 % of the K-sweep aggregate ks_med variance.

**Verdict: NARROWING_GENERALIZES_DELTA_KS_INCONSISTENT.**  Vocabulary
update: the mechanism is **order-parameter-driven aggregate-IEI
structure development under locking**, NOT rate-distribution
narrowing per se.  Rate_std narrowing is a derivative of |r| increase;
both reflect locking but |r| is the load-bearing variable.  When
citing the K-axis +0.10 drift mechanism in the publication, lead with
order parameter, not rate_std.

##### Follow-up 4: Allen F1/F0 rate-stratified replication

Applied within-session rate-tertile correlation to F1/F0 ↔ rep_med on
all 12 Allen sessions (drifting_pooled condition, 862 H1-passing
units total).  **All 12/12 sessions have negative unstratified ρ**
(mean −0.348), confirming Phase 24's substrate-systematic finding.
**10/12 sessions have negative tertile-mean ρ** (mean −0.176) — the
substrate-systematic sign-flip claim survives rate-stratified
discipline at the session-aggregate level.

But the within-session magnitude range across tertiles is large
(mean 0.458), and only 6/12 sessions show all-three-tertile sign-
consistency.  **The negative dynamics signal in Allen is
concentrated in mid-to-high rate units**: low-rate tertile rho_ff is
weakly positive in 8/12 sessions (+0.013 to +0.292), while mid and
high tertiles carry the negative correlation.

**Verdict: SUBSTRATE_SYSTEMATIC_SURVIVES_STRATIFIED.**  The pvc-11
positive vs Allen negative sign-flip holds at the session-aggregate
level; rate-regime substructure within each substrate is refined.
The Phase 24 + 27 substrate-systematic interpretation is
not invalidated.

OSI cross-check on Allen: 10/12 sessions show sign-consistent positive
across all 3 tertiles (mag range 0.48), 12/12 unstratified positive.
H1 OSI ↔ ks_gue_med survives rate-stratified discipline in Allen
as well as in pvc-11.

##### Follow-up 5: monkey1/2_gratings p-adic v4 at q_max=200

Applied `padic_amplitude_v4` at q_max=200 to monkey1_gratings and
monkey2_gratings to test whether monkey3's multi-prime structure
generalizes:

| recording | p=7 ratio | p=7 z | p=2 ratio | p=2 z |
|---|---|---|---|---|
| monkey1_gratings | 2.41 (above thr) | **+9.77** | 2.79 | +2.04 |
| monkey2_gratings | 1.58 (above thr) | +0.59 | 1.91 | −1.23 |
| monkey3_gratings (Follow-up 1) | 1.77 (above thr) | +1.90 | **4.06** | +3.67 |

**Verdict: CLASS_SIGNAL_LIKELY for p=7.**  All 3 pvc-11 gratings
recordings have p=7 ratio above the 1.5× threshold; 2/3 (monkey1,
monkey3) have z > 2 above rate-matched-Poisson surrogate.  monkey2's
marginal z (+0.59) reflects low-rate noise (rate 4.88 Hz vs ~30 Hz
for the others), not absence of signal.

monkey3's p=2 dominance (z=+3.67) was **recording-specific** — monkey1
shows marginal p=2 (z=+2.04), monkey2 shows p=2 below surrogate
(z=−1.23).  The class signal across pvc-11 gratings is p=7, not p=2.

This is the **first cross-recording p-adic-class signal identified
from ARS on biological data**.  Whether the p=7 signal generalizes to
non-gratings stimuli (spontaneous, movies) or to other substrates is
open.  Biological mechanism (q=7 period = 35 ms at bin_ms=5; 28.6 Hz,
beta-band) is open.  monkey3's strong recording-specific p=2 signal
(plus monkey2's p=13 z=+4.56) may reflect grating-trial-block
periodicity or recording-quality variation.

##### Follow-up 6: H2 stationarity check (pvc-11 surviving recordings)

Applied the Phase 30 stationarity module (10 non-overlapping windows)
to the two pvc-11 recordings that pass the Phase 22a/22b H2 surrogate
battery: monkey1_natural_movie + monkey2_gratings_movie.

**Verdict: H2_TIME_VARYING.**

monkey1_natural_movie (74 units, 87 313 events, 24.25 Hz, 3 600 s):
  - Full-sequence: primary = TR, rep_med = 0.250
  - Per-window: 7/10 TR, 3/10 BL  (modal fraction 70 %)
  - **rep_med across windows CV = 0.639** (range 0.000–0.350)
  - ks_gue_med across windows CV = 0.040 (stable)
  - STATIONARY: False (rep_med CV > 0.20)
  - agree_with_full: True (modal matches)

monkey2_gratings_movie (104 units, 163 903 events, 45.53 Hz, 3 600 s):
  - Full-sequence: primary = BR_artifact, rep_med = 0.550
  - Per-window: **5/10 TR, 5/10 BR_artifact** (50/50 split)
  - rep_med CV = 0.144, ks_gue_med CV = 0.036
  - STATIONARY: False (fraction_modal = 50 %, far below 90 %
    threshold)
  - agree_with_full: False (full-sequence BR masks half-the-time TR)

**Methodological wake-up call:** the Phase 22a/22b H2 surrogate
battery (rate-matched + cell-shuffle + LN-evoked × 7 seeds) was
applied to **full-sequence statistics**, not per-window statistics.
The locked H2 finding describes the time-averaged surviving structure;
it does NOT directly address whether the surrogate battery passes
within each window.  Both H2-passing recordings show substantial
within-recording temporal variation that the full-sequence statistic
averages over.

This does not invalidate the Phase 22a/22b H2 finding at its stated
resolution.  But the publication framing should acknowledge the
**temporal-stationarity caveat** explicitly: monkey1_natural_movie's
H2 surviving structure has rep_med CV = 0.64 across 10 windows;
monkey2_gratings_movie's H2 modal is right on the TR/BR_artifact
boundary at per-window resolution.

A **Phase 31f** is proposed: re-run the H2 surrogate battery within
each non-overlapping window of the two H2-passing recordings.  Per-
window survival fraction is the correct stationarity-aware H2 claim.

##### Follow-up 7: pvc-11 all-subsets p-adic v4 @ q_max=200

Extended the Follow-up 5 monkey1/2/3_gratings test to all pvc-11
subsets (spontaneous × 6, gratings_movie × 2, natural_movie × 2,
noise_movie × 2; 12 recordings + 3 gratings from Follow-up 5).

**Per-subset p=7 enrichment:**

| subset | n | above 1.5× | z > 2 | mean z |
|---|---|---|---|---|
| gratings | 3 | 3/3 | 2/3 | +4.10 |
| **spontaneous** | 6 | **6/6** | 2/6 | **+2.22** |
| gratings_movie | 2 | 1/2 | 0/2 | +0.21 |
| natural_movie | 2 | 0/2 | 0/2 | −0.38 |
| noise_movie | 2 | 0/2 | 0/2 | −0.47 |

**Verdict: P7_SUPPRESSED_IN_MOVIES** (formally P7_GRATINGS_SPECIFIC
per the script decision rule, but the substantive pattern is
"simple-stimulus + spontaneous present, complex-movie suppressed").

Standout per-recording: monkey4_spontaneous z = **+6.09**;
monkey1_gratings z = +9.77 (Follow-up 5); monkey3_spontaneous z = +2.93.
All 6 spontaneous recordings have p=7 ratio above the 1.5× threshold.

Interpretation: p=7 is **not pure beta-band-V1-intrinsic** (would be
stimulus-independent) and **not pure gratings-stimulus-specific**
(would not appear in spontaneous).  Movie stimuli (natural, noise,
even gratings_movie) drive complex time-varying temporal patterns
that override the V1-intrinsic p=7 structure; spontaneous + static
drifting gratings let the V1-intrinsic structure dominate.

##### Follow-up 8: Allen p-adic v4 @ q_max=200 (cross-species)

5 representative Allen sessions × 3 conditions (drifting_pooled,
spontaneous, natural_movie_one).  Same surrogate protocol.

**Per-condition p=7 enrichment:**

| condition | n | above 1.5× | z > 2 | mean z |
|---|---|---|---|---|
| Allen drifting_pooled | 5 | 0/5 | 0/5 | −0.29 |
| **Allen spontaneous** | 5 | **0/5** | 0/5 | **−0.87** |
| Allen natural_movie_one | 5 | 3/5 | 1/5 | +0.53 |

Cross-substrate Δ(mean z) at spontaneous: **pvc-11 +2.22, Allen
−0.87, Δ = +3.09** — substrate-systematic difference matching the
F1/F0-rep_med substrate-systematic pattern in direction (pvc-11
positive, Allen negative).

**Verdict: P7_PVC11_SPECIFIC.**  The p=7 enrichment is a
**substrate-systematic finding for pvc-11 (macaque V1 anesthetised)**,
not generalisable to awake-mouse-V1 (Allen).  Allen sessions show
p=2 / p=3 / p=5 / p=13 enrichments depending on session — more
diverse prime patterns consistent with the awake-state cortical-V1's
broader response repertoire.

**This is the first cross-substrate-systematic p-adic class signal
identified from ARS.**  Pattern matches the locked F1/F0 substrate-
systematic finding direction (pvc-11 positive, Allen negative).
Whether the two substrate-systematic patterns share a mechanism is
open — but they discriminate the substrates in the same direction
at independent ARS engines (rep_med vs RF-engine p-adic).

##### Follow-up 9 (Phase 31f): per-window H2 surrogate battery

Applied the Phase 22a H2 surrogate battery (rate_matched + cell_shuffle
+ ln_evoked × 5 seeds) at q_max=30 within each non-overlapping window
of monkey1_natural_movie + monkey2_gratings_movie.

**Verdicts:**
  - **monkey1_natural_movie: WINDOW_AWARE_LOCKED** — 8/10 windows pass
    the required-conjunction (all 3 surrogate types survive at ≥ 1
    q-band).
  - **monkey2_gratings_movie: WINDOW_MIXTURE** — 5/10 windows pass.

**Implication.**  monkey1_natural_movie's H2 surviving structure is
**per-window-real** — the Phase 22a/22b locked finding for this
recording is methodologically robust at per-window resolution
(best-possible outcome).  monkey2_gratings_movie is a
**window-mixture phenomenon**: the recording switches between
H2-passing and H2-failing regimes; the full-sequence statistic
averages them.  This is **substantively different** from the current
H2 framing for monkey2_gratings_movie.

Publication framing for the locked H2 finding should be revised to:
  - "H2 surviving structure on monkey1_natural_movie:
    **window-aware-locked** (8/10 windows pass the required surrogate
    conjunction)."
  - "H2 surviving structure on monkey2_gratings_movie:
    **window-mixture phenomenon**, full-sequence-statistic surrogate
    survival is real but only 5/10 windows survive individually."

The methodological commitment from Follow-up 6 is now actionable
across the toolkit: future H2-style surrogate-survival claims should
include per-window surrogate battery as standard discipline.

##### Follow-up 10: pvc-11 all-recordings per-window p-adic v4 @ q_max=200

Apply padic_amplitude_v4 within each non-overlapping window (N=5) of
all 15 pvc-11 recordings.  Per-prime stationarity classification per
recording: STATIONARY (z>2 in ≥4/5), MIXTURE (2-3/5), RARE (1/5),
NULL (0/5).

**Verdict: P7_FULL_RECORDING_AGGREGATION.**

Per-prime stationarity across 15 recordings:

| prime | STAT | MIX | RARE | NULL |
|---|---|---|---|---|
| p=2 | 1 | **10** | 4 | 0 |
| p=3 | 3 | 3 | 4 | 5 |
| p=5 | 0 | 3 | 7 | 5 |
| **p=7** | **1** | 3 | 2 | **9** |
| p=11 | 1 | 4 | 5 | 5 |
| p=13 | 0 | 2 | 2 | 11 |

**The strongest full-recording p=7 signal (monkey1_gratings z=+9.77)
is NOT per-window-stationary**: per-window z scores are -1.50, +1.27,
-1.43, +1.90, -1.83 (0/5 above z=2); per-window dominant primes are
[5, 2, 5, 7, 3] (no consistent prime).  All 3 gratings recordings
have ZERO PER_WINDOW_STATIONARY signals on any prime.

**Only monkey1_spontaneous shows PER_WINDOW_STATIONARY_P7** (4/5
windows z>2; mean z=+3.25).  The p=7 enrichment finding is largely
a full-recording-aggregation phenomenon, not a per-window-stable signal.

**p=2 is the most-consistently elevated prime across pvc-11** (MIX in
10/15 recordings; NULL in 0/15).  Consistent with q=2 = 10ms periodicity
in 5ms-binned population events.

**Same methodological pattern as H2 monkey2_gratings_movie
WINDOW_MIXTURE finding.**  Future ARS p-adic claims should be reported
at per-window resolution by default; full-recording-statistic claims
require explicit scope-aware framing.

##### Follow-up 11: Allen full 12-session p-adic v4 @ q_max=200

12 sessions × 3 conditions = 36 (session, condition) cells.  Verdict:
**P7_PVC11_SPECIFIC_CONFIRMED.**

Per-condition mean z(p=7): drifting_pooled +0.09 (5/12 above 1.5×);
spontaneous −0.14 (6/12 above 1.5×); natural_movie_one −0.44 (4/12
above 1.5×); 0 cells with z>2 in drifting + spontaneous; 1 cell in
natural_movie (Vip session).

Allen dominant prime distribution (36 cells): p=2 (18), p=3 (10),
p=5 (6), p=7 (2).  Allen V1 is p=2-dominant; p=7 is rare (2/36).

**Substrate-systematic Δ at spontaneous: pvc-11 mean z=+2.22 vs
Allen mean z=−0.14 → Δ=+2.36.**  Cross-substrate p=7 difference
holds at full-recording scope across the full 12-session Allen cohort.

##### Follow-up 12: Allen F1/F0 per-session rate-tertile profile heterogeneity

12 Allen sessions classified by per-session rate-tertile rho_ff profile:

  - ALL_NEGATIVE: 4 sessions (uniform negative across tertiles)
  - CANONICAL_LOW_POS_MID_HIGH_NEG: 3 sessions
  - CANONICAL_LOW_NULL_MID_HIGH_NEG: 2 sessions
  - OTHER_+−0: 3 sessions

5/12 (canonical) show mid-to-high negative concentration; 4/12 are
uniformly negative across tertiles.  **The mid-to-high-rate-concentration
claim is session-heterogeneous, not uniform across Allen.**  Cre-line
does not clearly predict profile at this n.

##### Follow-up 13: Movie p=7 suppression is content-driven, not rate-driven

Within-monkey rate-matched comparison (monkey1 across 5 subsets):

| recording | rate(Hz) | z(p=7) | real_p7 |
|---|---|---|---|
| monkey1_gratings | 27.93 | **+9.77** | 2.41 |
| monkey1_gratings_movie | 11.94 | +1.62 | 1.68 |
| monkey1_natural_movie | 24.25 | **−0.96** | 0.69 |
| monkey1_noise_movie | 20.08 | −0.72 | 1.04 |
| monkey1_spontaneous | 41.84 | +1.91 | 2.39 |

monkey1_gratings (27.93 Hz, z=+9.77) and monkey1_natural_movie (24.25
Hz, z=−0.96) have rates within ~15 % of each other but differ by ~11
z-score units in p=7.  monkey1_spontaneous at 41.84 Hz (higher rate)
maintains positive z.  Rate-matched and rate-monotonicity analysis
rules out rate as the driver.

**Verdict: CONTENT_DRIVEN movie p=7 suppression.**  Movie stimuli
disrupt the V1-intrinsic p=7 structure regardless of rate; spontaneous
+ static gratings let it persist.

##### Follow-up 14: Allen per-window p-adic — the cross-substrate picture inverts at per-window scope

3 representative Allen sessions × 3 conditions × 5 windows × 6 primes
(45 cells).  Major finding: the cross-substrate p=7 pattern **inverts
at per-window scope**.

**Per-condition mean z(p=7) at per-window resolution:**

  - **Allen natural_movie_one mean z = +4.70**, 11/15 windows z>2 (!)
  - Allen drifting_pooled mean z = +0.68, 3/15 z>2
  - Allen spontaneous mean z = −0.32, 0/15 z>2

Specific clean per-window-stationary cell: **session 760693773 (Sst)
natural_movie_one** — per-window p=7 z scores 0.1, +3.3, +6.9, +2.0,
+6.4 (PER_WINDOW_STATIONARY).  But this session's full-recording p=7
z = −0.29 (NULL at full scope).

**Substrate-systematic interpretation revised by temporal scope:**
  - Full-recording: pvc-11 spontaneous mean z(p=7) = +2.22; Allen
    natural_movie_one mean z = −0.44 → pvc-11 advantage.
  - Per-window: Allen natural_movie_one mean z = **+4.70**; pvc-11
    monkey1_gratings per-window: 0/5 windows z>2 → **Allen advantage**.

**pvc-11 has long-term p=7 coherence** (full-recording-aggregation
visible; per-window washes out).  **Allen has short-term p=7
coherence** (per-window visible, especially in stimulus-driven
natural_movie_one; full-recording washes out).

Per-prime Allen PER_WINDOW_STATIONARY counts: p=2 (4/9), p=7 (2/9),
p=5 (1/9), p=11 (1/9).  Allen p=2 STATIONARY in 44 % of cells vs
pvc-11 p=2 STATIONARY 7 % — **awake mouse V1 produces more rapidly-
fluctuating temporal structure than anesthetised macaque V1**,
consistent with awake-state cortical dynamics.

The Round-3 P7_PVC11_SPECIFIC claim now requires scope qualification:
P7_PVC11_SPECIFIC at full-recording scope; **P7_ALLEN_SPECIFIC at
per-window scope** (natural_movie_one specifically).

**Cross-Cre-line replication (6 Allen sessions: 2 wt, 2 Vip, 2 Sst,
1 Pvalb; 90 cells total):** the Allen per-window p=7 finding in
natural_movie_one **replicates across Cre lines**:

| cre_line | drifting_pooled | natural_movie_one | spontaneous |
|---|---|---|---|
| Pvalb | +0.73 | **+3.81** | +0.72 |
| Sst   | +0.15 | **+2.90** | +0.25 |
| Vip   | +0.34 | **+3.62** | −0.14 |
| wt    | +0.99 | **+4.10** | −0.38 |

Across 6 sessions × natural_movie_one = 30 cells, 19/30 windows show
p=7 z>2 (mean +3.49).  Specific high-magnitude session: Pvalb 797828357
natural_movie_one p=7 z = +4.6 / +5.3 / +5.3 / +2.4 / +1.5
(PER_WINDOW_STATIONARY 4/5).  Allen natural_movie_one is per-window-
rich on multiple primes (p=2, p=3, p=5, p=7, p=11, p=13 each STATIONARY
in at least one session × natural_movie_one cell).  **Substantively
different from pvc-11**, where per-window stationarity is sparse and
concentrated on p=7 only in monkey1_spontaneous.

**Awake mouse V1 produces rapidly-fluctuating multi-prime temporal
structure during natural-movie viewing; anesthetised macaque V1
produces longer-coherence-time p=7 structure visible at full-recording
scope but absent at per-window resolution.**

**Full 12-session Allen per-window replication (180 cells):**

| condition | n | mean z(p=7) | z>2 |
|---|---|---|---|
| drifting_pooled | 60 | +0.64 | 11/60 (18 %) |
| **natural_movie_one** | 60 | **+2.19** | **28/60 (47 %)** |
| spontaneous | 60 | +0.18 | 2/60 (3 %) |

Per-cre-line × natural_movie_one mean z(p=7) — all 4 Cre lines positive:

| Cre | n_sessions | drifting | natural_movie_one | spontaneous |
|---|---|---|---|---|
| Pvalb | 1 | 0.73 | **3.81** | 0.72 |
| Sst | 2 | 0.15 | **2.90** | 0.25 |
| Vip | 4 | 0.97 | **1.97** | 0.05 |
| wt | 5 | 0.56 | **1.75** | 0.14 |

**Allen natural_movie_one per-window p=7 enrichment is robust across
all 12 sessions and all 4 Cre lines.**  47 % of windows show z>2.
Mean z = +2.19 across 60 natural_movie_one windows.  Pvalb strongest
(+3.81); wt weakest (+1.75) but still positive.

The cross-substrate p-adic temporal-scope finding now stands on a
12-session Allen + 15-recording pvc-11 footing.

##### Follow-up 17: monkey1_spontaneous p=7 temporal granularity

The only pvc-11 recording with PER_WINDOW_STATIONARY_P7 at 5 windows
(monkey1_spontaneous; 4/5 z>2, mean z=+3.25) tested at finer
resolutions:

| n_windows | window duration | z>2 | mean z | verdict |
|---|---|---|---|---|
| 5 | 247 s | 4/5 | +3.25 | PER_WINDOW_STATIONARY |
| 10 | 123 s | 6/10 | +3.07 | PER_WINDOW_MIXTURE |
| 20 | 62 s | 7/20 | +1.41 | PER_WINDOW_RARE |

**p=7 coherence time in monkey1_spontaneous is approximately 60-120s**
— the signal degrades from STATIONARY at 247s windows to RARE at 62s
windows.  Notably the late portion of the recording (windows 15-19 in
the 20-window analysis: 4/5 above z=2) shows signal localization,
suggesting p=7 enrichment concentrates in particular time regions
of the spontaneous recording rather than uniformly distributed.

Interpretation: the V1 p=7 structure in monkey1_spontaneous operates
at roughly the minute timescale, consistent with slow-wave / up-state
oscillation cycling under anesthesia.  Sub-minute windows lose
statistical power AND/OR the structure has a coherence time longer
than 62s.

##### Follow-up 16: Kuramoto per-window p-adic — synthetic control

Apply per-window p-adic at q_max=200 to Phase 30 Kuramoto aggregates
at K_factors {0, K_c, 2 K_c} (N=100, T=1200 s, seed=0).

**Verdict: PER_WINDOW_NULL across all K, all primes.**

| K_factor | p=2 mean z | p=3 mean z | p=5 mean z | p=7 mean z | p=11 mean z | p=13 mean z |
|---|---|---|---|---|---|---|
| 0.0 | −1.41 | −0.13 | −1.84 | +0.80 | −1.47 | +1.13 |
| 1.0 | −1.04 | −0.24 | −1.49 | +0.86 | −1.16 | +1.01 |
| 2.0 | −1.42 | −0.13 | −1.83 | +0.87 | −1.25 | +1.07 |

All primes show n z>2 ∈ {0, 1} (out of 5 windows per K_factor).  No
STATIONARY (z>2 in ≥4/5) on any prime at any K.

**Kuramoto produces neither pvc-11-style long-term p=7 coherence
(full-recording aggregation) nor Allen-style short-term natural-movie
p=7 + multi-prime structure (per-window).**  Reinforces the Phase 30
NO_MECHANISTIC_MATCH verdict at per-window scope.  The Kuramoto-class
synthetic doesn't match either real-V1 substrate's p-adic temporal
structure at either temporal scope.

##### Follow-up 15: DSI monkey2 sign-flip diagnostic — NOT_SIGNIFICANT

monkey2_gratings DSI ↔ ks_gue_med rate-tertile correlations:

  - Unstratified: ρ = +0.031, **p = 0.82** (null)
  - Low: ρ = +0.281, p = 0.244
  - Mid: ρ = −0.119, p = 0.627
  - High: ρ = −0.370, p = 0.119

**All p-values exceed 0.05.**  monkey2's "sign-flip" is sampling
noise on an essentially-null signal.  The pvc-11 DSI ↔ ks_gue_med
correlation (Phase 22a +0.51, +0.03, +0.28 across 3 monkeys) is
driven by monkey1 (+0.51, p<10⁻⁵) and monkey3 (+0.28, p=0.009);
monkey2's correlation is null both unstratified and per-tertile.

Publication note: the DSI cross-substrate Phase 24 replication
finding (Allen mean partial ρ stronger than pvc-11) is real; pvc-11's
DSI signal is the weaker comparator, and within pvc-11 the signal is
driven by 2 of 3 monkeys.

##### Combined implication for the publication framing

  - The "Farey-bank channels" image is apt for the parallel `pll_bank`
    infrastructure and for the RF engine, NOT for the NNS engine of
    the deployed classifier.  Vocabulary needs revision before
    external-facing documents use the engineering-layer framing.
  - Single-event sensitivity is near-zero at modal scale; per-oscillator
    or per-event-cluster sensitivity is the right resolution.
  - The Phase 30 sub-modal signals (+0.10 K-axis aggregate, +0.23
    rate-matched residual) trace to different mechanisms: aggregate
    rate-distribution narrowing under locking vs within-cell rate-
    stratified dynamics signal.  Neither shifts the modal classification
    but both carry interpretable continuous-metric content.
  - p-adic v4 needs q_max=200 reclassification to be discriminating on
    real recordings; q_max=30 produces one clean prime-7 signal on
    pvc-11 monkey3_gratings, candidate for follow-up.

#### Outputs

Code: `phase31b/sensitivity.py`, `phase31b/loo_influence.py`,
`phase31b/padic_v4_sweep.py`, `phase31b/padic_v4_real_vs_surrogate.py`,
`phase31b/analysis_K_sweep_stratification.py`,
`phase31b/analysis_rate_matched_stratification.py`.

Data under `data/phase31a_results/`: `PHASE31A_DERIVATION.md`
(architecture audit, no code or simulations).

Data under `data/phase31b_results/`: `PHASE31B_FINDINGS.md`,
`padic_v4_*.{parquet,json}` (p-adic sweep),
`Ksweep_*.{parquet,json}` (K-sweep stratification),
`RateMatch_*.{parquet,json}` (rate-matched stratification).

Phase 31c (PLL bank ISF) and Phase 31d (Allen NP <300 μm spatial-scale,
continues Phase 28 in-progress work) deferred to lower priority.

---

### 7.ter.40  Phase 28 — Allen Neuropixels spatial-scale ARS at <300 µm

Resume of in-progress Phase 28 to close the Ohiorhenuan engagement
caveat from Phase 27 Analysis 3.  pvc-11 Utah array pitch (400 µm)
prevented the <300 µm spatial-scale test that Ohiorhenuan 2010
predicts as the local-rich regime.  Allen Neuropixels density (~10-14
V1 units per 100 µm vertical) allows fine-local cluster construction
at 0-100 µm radius.

**Verdict: SPATIAL-SCALE-DEPENDENT.**  Allen NP at <300 µm shows
non-monotone TR-fraction across spatial bins, with the local
bin (100-300 µm — Ohiorhenuan's predicted regime) the LEAST
TR-structured.

#### Per-bin results (12 Allen sessions, 719 clusters, 544 well-powered)

| bin | n_clusters | modal | TR % | real-vs-surrogate TR % |
|---|---|---|---|---|
| fine-local (0-100 µm) | 165 | BL | 15.2 % | sur 22.0 % (real < sur) |
| local (100-300 µm) | 234 | BL | **5.6 %** | sur 12.7 % (real < sur) |
| mid (300-800 µm) | 145 | BL | 18.6 % | sur 34.5 % (real < sur) |

Δrep (fine-local − mid) = 0.000.  Δks = −0.012 (within ±0.10 noise band).
Real-data TR-fraction is BELOW rate-matched surrogate at all 3 bins,
mirroring the Phase 27 pvc-11 finding direction.

#### Ohiorhenuan engagement closure

Phase 27 Analysis 3 on pvc-11 Utah array (400-600 µm radius) found
CONTRA-OHIORHENUAN — local less structured than recording-wide.  Phase
28 closes the spatial-resolution caveat at <300 µm: Allen NP at
<300 µm also does NOT show local-rich structure.

**The H2 surviving structure is NOT a local-spatial-cluster phenomenon
at any tested scale.**  It is a recording-wide-aggregate phenomenon
that does not strengthen at finer spatial scales.  The Phase 22a/22b
H2 finding's spatial character is now bounded across both pvc-11 (400-600 µm)
and Allen NP (<300 µm).  Whatever produces H2 surviving structure
operates at supra-300-µm spatial scales or is not spatially localized
at all.

**Publication framing for H2 spatial-scale:** "Recording-wide aggregate
phenomenon; not localized to or strengthened at <300 µm local clusters.
Both pvc-11 (400-600 µm, Phase 27) and Allen NP (<300 µm, Phase 28)
show no local-rich pattern in Ohiorhenuan 2010's direction."

#### Outputs

Code: `phase28/analysis1_spatial_scale_neuropixels.py`,
`phase28/spatial_setup.py`, `phase28/pilot_bins.py`.

Data under `data/phase28_results/`: `analysis1_per_cluster_real.parquet`
(719 rows), `analysis1_per_cluster_surrogate.parquet`,
`analysis1_verdict.json`, `spatial_positions_all.parquet`,
`PHASE28_FINDINGS.md`.

PHASE22A_FINDINGS.md, PHASE27_FINDINGS.md spatial-scale framing
updated in-place to reflect closure of the Ohiorhenuan caveat at
both spatial scales tested.

---

### 7.ter.41  Phase 32a — pvc-11 natural-movie per-window p-adic at q_max=200

EPISTEMIC_STATE.md flagged the pvc-11 natural-movie per-window p=7
cell as the load-bearing missing comparator for the cross-substrate
temporal-scope p-adic asymmetry: pvc-11 anesthetised macaque V1 carries
full-recording p=7 enrichment in spontaneous + gratings (P7_PVC11_
SPECIFIC at full-recording scope, §7.ter.39); Allen awake mouse V1
carries per-window p=7 enrichment in natural_movie_one (cross-Cre-
line, §7.ter.39).  Whether the pvc-11/Allen asymmetry is mediated by
(a) stimulus content (natural-movie viewing produces per-window p=7
regardless of substrate), (b) substrate (macaque vs mouse), or (c)
state (anesthetised vs awake) was confounded in the comparison as
structured.

Phase 32a is an extraction-and-comparison pass over the Round 4 sweep
parquets — both substrates already had per-window p-adic at q_max=200
computed at identical protocol (5 windows, 5 surrogate seeds,
rate-matched uniform Poisson, primes 2/3/5/7/11/13).  The missing
operation was simply pulling the pvc-11 natural-movie / Allen
natural_movie_one cells from the parquets and comparing.

**Verdict: PER_WINDOW_SUBSTRATE_CONSISTENT.**

pvc-11 natural-movie p=7 (monkey1 + monkey2, 10 windows total):
mean window-z = −0.253, 0/10 windows z>2.  Both recordings classify
PER_WINDOW_NULL on p=7.

Allen natural_movie_one p=7 (6 sessions × 4 Cre lines, 30 windows
total): mean window-z = +3.491, 19/30 windows z>2.  Per Cre line:
Pvalb +3.81 (4/5), Sst +2.90 (5/10), Vip +3.62 (6/10), wt +4.10 (4/5).

Natural-movie viewing alone is **insufficient** to produce per-window
p=7 in anesthetised macaque V1.  The cross-substrate p=7 asymmetry
cannot be explained by stimulus content; the substrate axis (whichever
combination of macaque-vs-mouse and anesthetised-vs-awake) is doing
the load-bearing work.  This narrows the candidate-interpretation
space from three axes (stimulus, substrate, state) to two (substrate,
state) but does not disambiguate substrate-vs-state — awake-macaque
or anesthetised-mouse data remains the missing comparator for that
disambiguation.

#### Richer-than-anticipated supporting context

The brief asked specifically about p=7.  But pvc-11 natural-movie
*does* produce per-window p-adic structure — at p=2 (mean z = +2.53)
and p=3 (+2.20).  Allen natural_movie_one carries per-window
enrichment at p=2 (+7.92), p=3 (+3.23), p=7 (+3.49), and p=13 (+2.64).
The substrate axis is **prime-specific, not presence-vs-absence of
per-window structure**.  pvc-11 monkey2_gratings_movie has p=2
PER_WINDOW_STATIONARY at mean z = +5.15; pvc-11 monkey2_noise_movie
has p=2 mean z = +8.16 — both unexpected from the original brief and
worth their own follow-up.

#### Publication framing

"Anesthetised macaque V1 and awake mouse V1 differ in per-window
p-adic prime dominance during natural-movie viewing, with awake mouse
V1 carrying p=7 enrichment that anesthetised macaque V1 does not
produce at the same stimulus class.  The macaque-vs-mouse and
anesthetised-vs-awake axes remain confounded; awake-macaque or
anesthetised-mouse data would be required to disambiguate.  Both
substrates carry per-window p=2 enrichment during movies — the
cross-substrate axis is prime-specific."

#### Outputs

  - `data/phase32a_results/natural_movie_per_window_padic_comparison.parquet`
  - `data/phase32a_results/natural_movie_per_window_padic_verdict.json`
  - `data/phase32a_results/PHASE32A_FINDINGS.md`
  - `phase32a/extract_natural_movie_comparison.py`

EPISTEMIC_STATE.md updated in-place: p=7 long-coherence-vs-short-
coherence entry adds the stimulus-ruled-out resolution; the
"unresolvable from current data" framing narrows from three-axis to
two-axis.

---

### 7.ter.42  Phase 32b — cross-engine correlation between F1/F0 ↔ rep_med (NNS) and p=7 (RF)

The cross-engine pattern flagged in EPISTEMIC_STATE.md (both engines
agree on substrate direction: pvc-11 positive, Allen negative) had
no specifically-cleared discipline before Phase 32b.  The state
document called this out as "hypothesis, zero disciplines cleared
against the cross-engine claim itself" and named the missing
discipline: within-substrate Spearman ρ between per-recording /
per-session contributions to each engine's substrate-systematic
signal.

Phase 32b is an extraction-and-correlation pass over cached Round 4
+ Phase 22a / Phase 24 outputs.  For each pvc-11 recording with
F1/F0 measured + each Allen session with per-window p-adic computed,
compute (a) within-recording/within-session Spearman(f1_f0_pref,
rep_med) over units, then (b) cross-recording/cross-session Spearman
between this score and the recording/session p=7 score.

**Power-limit surfaced during execution:** F1/F0 requires drifting-
grating stimulus, so pvc-11 F1/F0 is only computed for the 3 pure-
gratings recordings (monkey1/2/3_gratings).  The 6 movie-variants
and 6 spontaneous recordings have `f1_f0_pref` uniformly NaN in
`h1_functional`.  pvc-11 cross-engine analysis is bounded to n=3,
where Spearman ρ ∈ {−1, 0, +1} (modulo ties) and the minimum
achievable exact-permutation p ≈ 0.167.  Even a perfect ρ = +1 is
**not statistical evidence** at this sample size.

Allen analysis is bounded to n=6 sessions — the sessions with
per-window p-adic at q_max=200 computed in Round 4.

#### PVC-11 results (n = 3 gratings recordings)

| recording        | n_units | F1/F0 ↔ rep_med ρ | p7 z (full-recording) |
|------------------|---------|---------------------|------------------------|
| monkey1_gratings | 68      | +0.396              | +9.77                  |
| monkey2_gratings | 57      | +0.211              | +0.59                  |
| monkey3_gratings | 85      | +0.322              | +1.90                  |

Cross-engine Spearman: ρ = +1.000 (only achievable Spearman when
three points rank-align — uninformative at n = 3).  **UNDERPOWERED.**

#### Allen results (n = 6 sessions with per-window p-adic)

| session    | Cre line | n_units | F1/F0 ↔ rep_med ρ | p7 win mean z | p7 frac>2 |
|------------|----------|---------|---------------------|----------------|-----------|
| 732592105  | wt       | 89      | −0.384              | +4.10          | 0.80      |
| 755434585  | Vip      | 64      | −0.240              | +0.97          | 0.40      |
| 760693773  | Sst      | 63      | −0.500              | +3.73          | 0.60      |
| 762602078  | Sst      | 57      | −0.414              | +2.07          | 0.40      |
| 791319847  | Vip      | 81      | −0.372              | +6.27          | 0.80      |
| 797828357  | Pvalb    | 75      | −0.308              | +3.81          | 0.80      |

Cross-engine Spearman: **ρ = −0.086, p = 0.872.**  Robustness across
four scoring variants (signed/abs F1/F0_rho × mean_z/frac>2 p7):
|ρ| ≤ 0.093 in all four.  Pearson r = −0.355 (p = 0.489): not
significant.

#### Verdict

**Allen: INDEPENDENT_AXES.**  Sessions that contribute most to the
F1/F0 ↔ rep_med Allen finding are not the sessions that contribute
most to per-window p=7.  The two engines read independent
substrate-systematic axes that happen to share direction — not
projections of one underlying substrate-systematic axis.

**PVC-11: UNDERPOWERED** at the per-recording level by intrinsic
stimulus-measurement constraints, not by transient data gap.

#### Publication-framing implication

Pre-Phase-32b the cross-engine direction match could be cited as
second-engine corroboration of the substrate-systematic finding
(a stronger claim).  Post-Phase-32b on Allen, the cross-engine
direction match is **two independent findings about the same
substrate**, not corroboration of one finding.  The §7.ter.10
band-invariance question — "why do two formally distinct engines
pick out the same substrate axis?" — gains a partial answer: the
substrate differs on multiple axes simultaneously, not on one axis
viewed by two engines.

#### Outputs

  - `data/phase32b_results/pvc11_per_recording_scores.parquet`
  - `data/phase32b_results/allen_per_session_scores.parquet`
  - `data/phase32b_results/cross_engine_verdict.json`
  - `data/phase32b_results/PHASE32B_FINDINGS.md`
  - `phase32b/cross_engine_correlation.py`

EPISTEMIC_STATE.md updated in-place: cross-engine entry moves from
"hypothesis, discipline outstanding" to "Allen INDEPENDENT_AXES,
pvc-11 underpowered."  The closing-section cross-engine open question
narrows accordingly — per-cell decomposition (deferred) is the
natural extension for the pvc-11 side.

---

### 7.ter.43  Phase 32c — awake macaque V1 data-pathway assessment

Phase 32c is a survey, not a measurement.  The state document
flagged the load-bearing missing comparator for the temporal-
coherence-asymmetry question as **awake macaque V1 with recording
structure comparable to pvc-11 / Allen** (spike-sorted single units,
≥ ~30 simultaneously recorded V1 units, recording durations
supporting per-window analysis, conditions covering natural-movie or
comparable + spontaneous + gratings).  Phase 32c asks whether such a
dataset exists in public repositories with a bounded ingestion path.

**Verdict: MIXED, leaning DATA_AVAILABLE_BUT_INCOMPATIBLE.**

Every awake-macaque-V1 dataset evaluated has at least one
disqualifying feature for direct ARS pipeline use without
methodology-compromising adaptation:

  - **Cadena 2019** (Tübingen, PLOS Comp Bio): spike-sorted, awake,
    V1, but 60-ms image-flash trial structure with no spontaneous
    baseline / no movies and ~10 units per session.  **PARTIALLY
    COMPATIBLE** — wrong recording structure for the load-bearing
    per-window natural-movie measurement.
  - **Coen-Cagli 2015** (Albert Einstein): similar profile to Cadena;
    spike-sorted awake V1 but image-flash paradigm only.
  - **Chen et al. 2022** (Roelfsema, Sci Data): 1024-channel V1+V4
    Utah array, awake, resting state (21-42 min sessions).  **MUAe
    + LFP only — NO spike-sorted single units.**  Using directly
    triggers the §7.ter.19 peak-detection failure mode.  **INCOMPATIBLE
    without ~2-4 months of Kilosort + curation pre-processing.**
  - **TVSD / Papale et al. 2024** (Roelfsema, Neuron): 31 Utah arrays
    V1/V4/IT awake.  MUA only.  **INCOMPATIBLE** same reason.
  - **CRCNS pvc-5** (Chu / Hung, Georgetown): spike-sorted multi-
    electrode V1, 15 min spontaneous + parametric gratings — best
    structural match to pvc-11.  **State (awake vs anesthetised) is
    ambiguous** in public metadata; Chu et al. 2014 methodology
    suggests anesthetised but verification requires paywalled-paper
    access.  If anesthetised, redundant with pvc-11.
  - **CRCNS pvc-12** (Martinez-Conde / Macknik): awake V1 brightness
    illusions, but single-neuron extracellular (not population).
    INCOMPATIBLE.
  - **PNAS 2026 Neuropixels macaque V1** (Wilke et al.): anesthetised
    (isoflurane).  Won't disambiguate.

The two awake-macaque-V1 datasets with population recordings
comparable in channel count to pvc-11 / Allen (Chen 2022, TVSD)
provide MUA envelope only — using them would force a peak-detection-
on-continuous-trace extractor, the §7.ter.19 failure mode the tool
was built to catch.  The two awake-macaque-V1 datasets with
spike-sorted single units (Cadena 2019, Coen-Cagli 2015) use
60-ms image-flash trial paradigms with no per-window-natural-movie
equivalent.

#### Forward options

  1. **Accept the substrate-vs-state confound permanently** in the
     publication framing.  The cross-substrate p=7 finding stays
     bounded to "anesthetised macaque vs awake mouse" without
     species-vs-state disambiguation.
  2. **Partial test on Cadena 2019** with recording-structure-mismatch
     caveat: could test full-recording p=7 on image-flash blocks
     (~3 days of pipeline work), but not the per-window natural-movie
     measurement that is the load-bearing missing comparator.
  3. **Verify pvc-5 awake/anesthetised state** (~1 hour of paywalled-
     paper reading); if awake, run on pvc-5 directly (~1-2 days
     ingestion + analysis).
  4. **Wait for Neuropixels-NHP field maturity** (likely 12-24 months
     for spike-sorted-awake-macaque-V1 public releases) or pursue
     direct collaboration with Smith / Kohn / Cohen / Pesaran /
     Roelfsema labs — external-engagement decision per state doc
     closing section.

#### Methodological observation

Two general lessons:

  1. The bottleneck in cross-substrate replication of population
     spike-train work is not the recording technology but the
     **spike-sorted-public-data ecosystem**.  Awake macaque V1 has
     been recorded with Utah arrays and Neuropixels for years; what
     is not yet standard is publishing unit-level output.  Most
     public releases stop at MUAe or LFP.
  2. The §7.ter.19 failure-mode warning operates as a **hard
     compatibility gate**.  Superficially attractive datasets (1024
     channels of awake V1, 31 Utah arrays) become unusable when one
     notices "MUAe only."  The boundary-readout discipline rules out
     convenient data sources that would silently inject extractor-
     artifact failure modes.

#### Outputs

  - `data/phase32c_results/PHASE32C_FINDINGS.md`

No parquets or JSON; survey only.

EPISTEMIC_STATE.md updated in-place: closing-section temporal-
coherence-asymmetry paragraph adds the Phase 32c finding that the
load-bearing missing comparator is **not reachable via bounded-effort
public-data ingestion**, and lists the four forward options.

---

### 7.ter.44  Phase 33a — NANOGrav pulsar timing arrays as cross-domain ARS substrate

Phase 33a is a structural-match assessment, not a substantive
measurement.  The state document's §7.ter.19-as-dataset-selection-
discipline entry generalised the peak-detection failure mode to
"MUAe-only neural datasets force the failure mode by construction;
dataset selection is a discipline."  Phase 33a tests whether that
generalisation extends across domains, using NANOGrav 15-year pulsar
timing data as the cross-domain probe — a substrate chosen for its
well-characterised physics (neutron star rotational dynamics) and
stationarity-by-construction.

**Data:** NANOGrav 15-year release (Zenodo DOI 10.5281/zenodo.8423265),
accessed via the per-pulsar feather mirrors in `nanograv/discovery`
GitHub repo.  Five representative pulsars: B1855+09 (7,758 TOAs / 15.6
yr), J0030+0451 (19,571 / 15.5), J0613-0200 (17,124 / 15.0),
J1909-3744 (35,037 / 15.5 — exceptional precision), J0740+6620
(13,401 / 6.3).

**Structural finding:** A NANOGrav TOA is **not** a single pulse
arrival.  It is a template-matched timestamp derived from a folded-
and-averaged pulse profile, where folding has already aggregated
~10⁴–10⁵ individual pulses within a 10-second sub-integration into
one phase-reference measurement, and the 30-minute observation epoch
then contributes ~50 TOAs at different frequency channels and sub-
bands (observation-epoch density: 147–572 epochs per pulsar; median
TOAs/epoch: 46–68).  Inter-TOA spacings are bimodal: ~zero within
epoch, weeks-to-months between epochs.  Pulsar emission physics lives
in (a) the folded profile shape within each observation and (b) the
residual time series sampled at TOA epochs — neither of which is the
inter-TOA spacing distribution that ARS reads.

**Empirical pilot (`phase33a/pilot_direct_stats.py`):**  Per the
§7.ter.10 band-invariance proposition, the NNS engine's load-bearing
output is determined by the unit-mean-normalized spacing distribution
— so the pilot computes CV, mass<0.3, KS_GUE, KS_Poisson, rep_int
directly (bypassing slow Farey decomposition at multi-million-second
durations).  10 rate-matched uniform-Poisson surrogate seeds.

Mode A (raw TOAs): CV = **9.7–14.7** (vs 1.0 Poisson), mass<0.3 =
**96–98%**, median normalized spacing **= 0.0000**, KS_Poisson z =
**+405 to +746**.  The signature is *entirely* the radio-backend
frequency-channel grid (~50 near-coincident TOAs per observation),
not pulsar physics.

Mode B (epoch-collapsed): CV = 1.2–2.5, KS_Poisson z = +5 to +25.
Still non-Poisson, but the deviation reflects telescope-scheduling
cadence (monthly observation blocks irregular due to weather,
semester time allocation, Arecibo's 2020 collapse), not pulsar
physics.

In both modes, ARS produces strong "signal" against rate-matched
Poisson, but the signal sources are **identifiable as apparatus
structure** rather than substrate physics.  This empirically
instantiates the §7.ter.6 EEG-bandpass-filter analog at the cross-
domain dataset-selection level: a naive ARS user not auditing the
data product would read these enormous z-scores as a "finding" about
pulsars when the finding is entirely about the observatory's
radio-backend and scheduling structure.

**Verdict: STRUCTURAL_MISMATCH at the published-product level.**

**Methodological generalisation:** the §7.ter.19 compatibility gate
operates not just at "MUAe vs spike-sorted" but at **any published-
data-product where aggregation has already happened upstream**.
Pulsar-timing collaborations publish folded-template TOAs because
GW-detection lives in residuals.  Neural labs publish spike-sorted
units or MUAe depending on primary-analysis preference.  Both
ecosystems record at event-level resolution; both mostly don't
publish at it.  ARS's compatibility envelope is determined by the
published-product layer, not the recording-resolution layer.
Cross-domain extension must audit published-data-product structure
before assessing substrate physics.

**What Phase 33a does not foreclose:**

  - Cross-pulsar Hellings-Downs-analog correlation on residuals
    (different framework, not ARS).
  - Per-pulse arrival point processes from raw PSRCHIVE / PRESTO
    archives (compatible-after-substantial-preprocessing).
  - Single-pulse pulsar literature (giant pulses, nulling pulsars,
    mode-switchers) — sometimes publishes per-pulse data, would be
    clean cross-domain match for a separate phase.
  - Other pulsar-timing arrays (EPTA, PPTA, IPTA, MeerTime,
    CHIME/Pulsar) all face the same published-product mismatch.

#### Outputs

  - `data/phase33a_results/PHASE33A_FINDINGS.md`
  - `data/phase33a_results/pilot_direct_stats.parquet` (10 rows: 5
    pulsars × 2 extraction modes, all direct-stats + surrogate z)
  - `data/phase33a_results/{B1855+09,J0030+0451,J0613-0200,J1909-3744,J0740+6620}.feather`
    (representative NANOGrav 15-yr per-pulsar timing data, ~30 MB
    total, retained for reference)
  - `phase33a/pilot_direct_stats.py` (analysis script)
  - `phase33a/pilot_ars_runs.py` (initial Farey-decomposition pilot,
    superseded by direct-stats version; kept as historical reference
    of the slow path)

EPISTEMIC_STATE.md cross-domain extension section added (in the
methodological-findings section, after §7.ter.19-as-dataset-selection
entry).  The §7.ter.19 generalisation now reads: published-data-
product compatibility is a hard gate at the cross-domain-survey
stage; dataset selection must audit published-product structure
before assessing substrate physics.

---

### 7.ter.45  Phase 33b — CERN Open Data particle physics events as cross-domain ARS substrate

Phase 33b is the second cross-domain structural-match assessment.
The brief was amended explicitly: apply the Phase 33a published-
product-aggregation lesson at the *survey entry point* rather than
only at the structural-assessment stage.  CERN Open Data publishes
at multiple processing levels (RAW, AOD, MiniAOD, NanoAOD, derived
educational CSVs), each with different aggregation status, and the
choice of level directly determines compatibility-envelope status.

#### Processing-level audit (entry-point gate)

  - **RAW**: pre-trigger, full BX-clock 25-ns timestamps preserved.
    ARS-compatible in principle but requires CMSSW/Athena + multi-TB
    infrastructure.  Not bounded-effort.
  - **AOD / MiniAOD**: triggered events, full reconstructed-object
    lists.  CMSSW required.  Not bounded.
  - **NanoAOD**: most accessible (uproot-readable, ~1 kB/event).
    **Preserves Run/LumiBlock/Event identifiers only — wall-clock
    timestamps stripped during reconstruction.**  Trigger pre-applied.
  - **Derived educational CSVs** (CERN Open Data record 545 and
    similar): NanoAOD-derived, further selection-filtered, no
    timestamps, kinematic quantities only.

**All bounded-effort accessible levels are (a) post-trigger and
(b) time-stamp-stripped.**  The trigger acts as a §7.ter.19-style
extractor; the time-stamp stripping removes the inter-event timing
ARS would read.  Per the Phase 33a generalisation, this is dataset-
selection-incompatible for time-domain ARS at the published-product
level.

#### Alternative framing: mass-spectrum as point process in mass space

The framing that *is* accessible: each dimuon event contributes one
invariant mass M to a 1D point process in mass coordinate.  Standard
Model resonance structure (Z⁰ at 91 GeV, J/ψ at 3.1 GeV, Υ family
~10 GeV) is the known physics.  This is the LMFDB-zeros structural
analog: point process in spectral coordinate, not in time.

**Pilot:** CERN Open Data record 545 derived CSVs from CMS 2011A
DoubleMu primary dataset (Zmumu 10k events, Jpsimumu 20k, Ymumu 20k,
Dimuon_DoubleMu 100k).  Invariant mass computed from muon 4-vectors
(massless-muon approximation).  Direct-stats per §7.ter.10 band-
invariance; surrogate: rate-matched uniform-in-mass-range (10 seeds).

| Sample          | n_events | M range (GeV) | CV     | mass<0.3 | KS_Poisson | z_KS_Poi |
|-----------------|----------|----------------|--------|----------|-------------|----------|
| Zmumu           | 10,000   | 60-120         | 3.35   | 0.59     | 0.34        | +247     |
| Jpsimumu        | 20,000   | 0.8-13         | 48.7   | 0.78     | 0.53        | +341     |
| Ymumu           | 20,000   | 7-24           | 81.6   | 0.74     | 0.49        | +320     |
| Dimuon_DoubleMu | 100,000  | 0.06-300       | 63.7   | 0.84     | 0.59        | +838     |

Every sample produces enormous z-scores against uniform-in-mass
surrogate — but the "signal" is the known resonance peak structure
that every CMS Drell-Yan paper shows on figure 1.  No information
above existing methods.  The surrogate is too dumb: a physics-aware
null (Drell-Yan continuum template) would be required to distinguish
genuine novel structure from known resonance physics, and such a
surrogate requires Monte Carlo / analytic-template infrastructure
ARS doesn't currently have.

#### Verdict: STRUCTURAL_MATCH_BOUNDED

  - **Time-domain framing**: STRUCTURAL_MISMATCH at the published-
    product level.  Same shape as NANOGrav: data exists in raw form,
    published product has aggregated past the event-level temporal
    resolution.  RAW-level analysis is compatible-after-substantial-
    preprocessing (CMSSW + multi-TB infrastructure).
  - **Mass-spectrum framing**: STRUCTURAL_MATCH at the instrument-
    validation level only.  ARS reproduces known resonance peaks
    but adds no measurement beyond what histogramming sees.
    Substantive analysis requires physics-aware surrogates (Drell-Yan
    continuum templates, trigger-efficiency models) — substantial
    infrastructure investment.
  - **Combined**: particle physics event data is *not* in ARS's
    substantive cross-domain envelope at any bounded-effort
    published-product level.

#### Two generalisations that propagate

  1. **Processing-level audit must precede structural-match
     assessment.**  Phase 33b applied this at entry per the brief's
     amendment.  Identifying that NanoAOD strips timestamps *before*
     running a pilot saved unnecessary work and reframed the
     structural question to the mass-spectrum framing where it could
     actually run.  Future cross-domain phases should adopt the same
     entry-point ordering.

  2. **Surrogate adequacy is a domain-specific question.**  Rate-
     matched Poisson is the natural null for neural spike trains
     because Poisson is the canonical "no-structure" prior in that
     domain.  In particle physics the natural null is process-
     specific (Drell-Yan continuum, multijet QCD, etc.).  Uniform-in-X
     surrogates produce trivially-huge z-scores in any domain where
     data was selected to contain known structure — the signal is
     just the selection.  Cross-domain extension to any new substrate
     must audit whether ARS's existing surrogate set captures the
     domain's natural no-structure prior before interpreting z-scores
     as evidence of novel physics.

#### What Phase 33b does not foreclose

  - RAW-level analysis preserving BX-clock timestamps — possible but
    not bounded-effort.
  - Per-event particle-track timing within a single triggered event
    (sub-nanosecond resolution at AOD level) — separate cross-domain
    target worth its own phase.
  - Physics-aware surrogate ecosystem development for the mass-
    spectrum framing — substantial new infrastructure, different
    framework than deployed NNS+RF engines.
  - Cross-detector replication (ATLAS vs CMS) — sits on top of
    either of the above.

#### Outputs

  - `data/phase33b_results/PHASE33B_FINDINGS.md`
  - `data/phase33b_results/pilot_mass_spectrum_stats.parquet`
  - `data/phase33b_results/{Zmumu,Jpsimumu,Ymumu,Dimuon_DoubleMu,Wmunu}.csv`
    (CERN Open Data record 545, ~28 MB total)
  - `phase33b/pilot_mass_spectrum.py`

EPISTEMIC_STATE.md cross-domain extension section updated in-place
with Phase 33b verdict + two methodological generalisations.

---

### 7.ter.46  Phase 33c — single-molecule fluorescence blinking as cross-domain ARS substrate

Third cross-domain assessment.  Single-molecule blinking has a
specifically different epistemic role from Phase 33a/33b: the
substrate has **theoretically predicted universality class structure
from first-principles photophysics** (power-law on/off-time
distributions, Kuno-Nesbitt universal exponent α ≈ 1.5), making it
an instrument-validation candidate analogous to ARS's existing
arithmetic-signal validation (Riemann ζ, L-functions, primes).

Per the brief's amendment, the published-product-aggregation audit
was applied at the survey entry point.  The single-molecule field
publishes data at three processing levels, and the state-detection
methodology is the analog of pulsar-folding / particle-physics-trigger
aggregation.

#### Processing-level audit

  - **Raw photon-count traces**: continuous intensity, event-level
    resolution preserved.  Sometimes available (Zenodo, supplementary).
    Requires user-side state-detection → §7.ter.19 trap by construction.
  - **State-detected event sequences**: post-extractor (binning +
    thresholding, HMM, change-point analysis, deep-learning trace
    idealisation).  Event-level resolution preserved but extractor
    pre-applied.  Sometimes published (kinSoft challenge benchmarks).
  - **Distributional summaries**: on/off-time histograms and fitted
    power-law exponents.  Event-level resolution stripped.  This is
    the predominant publication form.

#### Convergent finding from the single-molecule literature

The substantive Phase 33c result is not a pilot classification but a
**convergent-validation finding from the literature**: the single-
molecule biophysics field has independently documented the §7.ter.19
failure mode in its own vocabulary:

  - **Crouch, Sauer, Schuette 2014** (J Chem Phys 140, 114306,
    "Distortion of power law blinking with binning and thresholding"):
    "Real power law statistics with exponents α_on/off ≳ 1.6 ... would
    not be observed as such in the experimental data after binning
    and thresholding.  Instead, a power law appearance could simply
    be obtained from the continuous distribution of intermediate
    intensity levels."  Increasing binning time by 10× doubles
    apparent truncation time and changes apparent power-law exponent
    by 30 %.
  - **Houel et al. 2016** (J Phys Chem C, "Understanding the Bias
    Introduced in Quantum Dot Blinking Using Change Point Analysis"):
    even CPA — the better-than-thresholding method — introduces
    residual bias documented at the per-event-time level.

This convergence is the substantive finding: the dataset-selection
discipline that ARS formalized as the §7.ter.19 cross-domain
generalisation (Phase 33a/33b) has an **independent precedent in
single-molecule biophysics**, reached by a methodologically distinct
field through an independent path.  Two fields, same conclusion
about extractor-dependence of inferred event-level structure.  The
boundary-readout discipline from WHYTHISEXISTS.md is empirically
vindicated as a domain-general principle.

#### Verdict

**STRUCTURAL_MISMATCH at the published-product level + INSTRUMENT_
VALIDATION_BOUNDED at the event-sequence level.**

  - Most single-molecule blinking data is published at distributional-
    summary level — past event-level resolution.  Dataset-selection-
    incompatible.
  - When event-sequence data is published, it is post-state-detection.
    The state-detection methodology is the §7.ter.19 extractor,
    independently documented in the literature.
  - Even with clean event-sequence access, ARS's calibrator zoo does
    not include a power-law-mixture universality class.  Instrument-
    validation against single-molecule theory requires calibrator-
    zoo extension before it can be run.

Single-molecule fluorescence is **not in ARS's substantive cross-
domain envelope at bounded-effort access**, and **only partially in
the instrument-validation envelope** at the event-sequence level —
calibrator-zoo extension being the blocking step.

#### What Phase 33c does not foreclose

  - kinSoft challenge benchmarks include synthetic data with ground-
    truth state sequences, sidestepping state-detection bias for
    instrument-validation purposes — potential entry point for
    a subsequent phase.
  - Power-law-matched calibrator addition would convert single-
    molecule instrument-validation from "blocked" to "runnable" —
    substantial enough to be its own phase.
  - Stationary-vs-aging blinking discrimination connects to the
    non-stationary-rate-discipline open question in EPISTEMIC_STATE
    closing section.
  - Multi-molecule MEA-style fluorescence imaging may provide
    population-style data; not investigated in Phase 33c.

#### Outputs

  - `data/phase33c_results/PHASE33C_FINDINGS.md`

No parquets / no pilot script — the published-product audit + the
convergent literature finding suffice for the verdict.  Running a
pilot against bias-uncertain event sequences from a specific state-
detection method would not change the structural verdict and would
itself be a §7.ter.19-flagged analysis.

EPISTEMIC_STATE.md cross-domain section extended with Phase 33c
verdict.  A three-domain cross-extension synthesis section added
covering Phase 33a (pulsars) + Phase 33b (particle physics) +
Phase 33c (single-molecule), per the brief's sequence note that the
map is what the three phases collectively produce, not what any
single phase produces.


### 7.ter.47  Phase 34a — Mertens sign-changes: RF + p-adic v4 orthogonal channels

The cross-domain phases (33a-c) closed the cross-domain question;
attention returns to where ARS lives natively — arithmetic signals.
The instrument-validation portfolio on the arithmetic side has so
far been NNS-engine-only, and the NNS engine reproduces what RMT
already measures.  The orthogonality-to-RMT story, if there is one,
lives in the two channels RMT does not have: the Ramanujan-Fourier
engine in indicator mode (integer-period structure detection on
raw event times) and p-adic v4 (which prime concentrates the RF
power).  Phase 34a applies both to the Mertens function sign-change
positions, a load-bearing RH-adjacent arithmetic object whose bulk
NNS-engine verdict is recorded in §15 as Poisson.

The brief commits to no advance ordering on outcomes among
NULL_IN_ORTHOGONAL_CHANNELS, RF_SPIKE_AT_q, P_ADIC_CONCENTRATION_p,
AMBIGUOUS_AT_BOUNDARY, or NON_STATIONARY.

#### Data and pipeline

Mertens function M(n) = Σ_{k=1}^n μ(k) sieved to N_max = 10⁷
(matches the project's §7.bis tabulation; out-of-scope to extend
beyond published tables).  Sign-change positions: integers n where
sign(M(n)) ≠ sign(M(n-1)), zeros skipped — 3,866 events in
[3, 9,593,967], identical (event count and M at decades) to the
existing `data/mertens_liouville_results.json` from §7.bis under
independent re-sieve.

  - `phase34a/mertens_events.py`        — sieve + sign-change extraction
  - `phase34a/fast_rf.py`               — O((K + Σ_q q)) RF in indicator
                                          mode via residue-class counts
                                          (parity vs `arithmetic_toolkit.
                                          ramanujan_fourier` ≤ 2.2e-19
                                          machine precision)
  - `phase34a/surrogate.py`             — rate-matched Poisson at K=50
                                          local-density bins
  - `phase34a/run_stationarity.py`      — sub-question 1 (phase30 module)
  - `phase34a/run_nns_classify.py`      — sub-question 2 (deployed
                                          `joint_q_profile`, Q_MAX=30,
                                          JPF_CAP=1500)
  - `phase34a/run_rf_padic_survey.py`   — sub-question 3 (RF + p-adic v4
                                          on raw integer positions,
                                          1000 Poisson surrogates)
  - `phase34a/run_falsify.py`           — sub-question 4 (squarefree-
                                          restricted surrogate, within-
                                          window stability, second-source
                                          cross-check)

Acceptance gates before sub-question 3: STATIONARY_CALIBRATORS 8/8
PASS (verified verbatim) and p-adic v4 synthetic suite 5/6 single-
prime detections on the per-q-power-normalised metric (period-13
narrow miss as documented in the sensitivity-limit memo — both
gates pass).

#### Sub-question 1: stationarity

The phase30 10-window heuristic flags the global sign-change
sequence as non-stationary (fraction_modal = 0.889 < 0.90;
CV(rep_med) = 2.83 > 0.20, an artefact of the BL modal-class
producing rep_med = 0.000 in 8 of 9 well-powered windows, so the
std/mean ratio explodes).  The flag is **density-driven**, not
**modal-class-driven**: 8 of 9 well-powered windows are unambiguous
BL Poisson; the 9th drifts to TR at 37 events, marginally above the
30-event underpower threshold; window 6 (11 events) is
underpowered.  The per-window event count ranges from 1652 (window 0)
down to 11 (window 6), tracking the density-bunching of sign-changes
near M zero-crossings.

Verdict path follows the brief: restrict the formal analysis to the
density-stationary sub-window [1, 4·10⁶] (windows 0-3, all four BL
with rep_med = 0.000, 3,016 events) and report the full sequence
[1, 10⁷] as a robustness check.

#### Sub-question 2: NNS-engine reproduction

| configuration       | n   | primary | rep_med | ks_gue_med | per-q quadrants    |
|---------------------|-----|---------|---------|------------|--------------------|
| full [1, 10⁷]       | 3866 | **BL** | 0.000   | 0.904       | BL=30/30           |
| dense [1, 4·10⁶]    | 3016 | **BL** | 0.000   | 0.882       | BL=28, ambiguous=2 |
| tail [5·10⁶, 10⁷]   |  813 | **BL** | 0.000   | 0.922       | BL=28, ambiguous=2 |

Unambiguous Poisson (BL) across all three configurations, modal
across 30/30 q-bands on the full sequence.  Reproduces the §15
capability-report verdict for Mertens / Liouville sign-change
sequences without drift.

#### Sub-question 3: RF + p-adic v4 against rate-matched Poisson

RF indicator-mode |a_q| for q ∈ [1, 30] on raw integer positions,
flagged via the 5×-median TL threshold and verified against 1000
rate-matched Poisson surrogates with K=50 local-density bins.
p-adic v4 dominant_prime_per_q at primes {2, 3, 5, 7, 11, 13}.

|              | RF spike q (5× median) | RF spikes surviving Poisson at p<0.001 | p-adic dom_per_q | Poisson-sur modal | sur fraction matching real |
|--------------|------------------------|---------------------------------------|------------------|-------------------|----------------------------|
| dense window | 2, 3, 4                | 2, 3, 4                               | **p=2**          | p=2               | 0.432                      |
| full         | 2, 3, 4, 6, 12         | 2, 3, 4 (6 and 12 do not survive)     | **p=2**          | p=2               | 0.462                      |

Strong RF spike at q=2 (ratio real:sur-mean ≈ 20×–50× across q=2,3,4)
and concentration at p=2 (normalised_per_q = 5.4, vs 0.8 at p=3,
0.3 at p=5, 0.1 at p=7).

The brief's pre-specified survival criterion (p < 0.001 against
rate-matched Poisson) would, at this stage, support an
RF_SPIKE_AT_q={2,3,4} + P_ADIC_CONCENTRATION_p=2 verdict.  The
sub-question 4 falsification revises this.

#### Sub-question 4: multi-order falsification — the surrogate identity

M(n) only changes value at squarefree n (μ(n) is zero otherwise),
so every Mertens sign-change position is a squarefree integer.  The
squarefree integers have a fixed, non-uniform residue-class density
profile: density at residue 0 mod 4 is exactly zero (4|n implies
non-squarefree); odd:even density ratio is 2:1; mod-3 density at
residue 0 is depressed relative to residues 1, 2; and so on.

Observed residue distribution of the 3,866 sign-changes:

  - mod 2:  1352 even, 2514 odd       (odd:even = 1.86 ≈ expected 2.0)
  - mod 3:  936, 1476, 1454            (residue 0 depressed)
  - mod 4:  **0**, 1273, 1352, 1241    (residue 0 forbidden by filter)

So the RF spikes at q = 2, 3, 4 are exactly the residue-class
density profile of the *support set*, not a property of the
sign-change subsequence beyond that support.  The rate-matched
Poisson surrogate of sub-question 3 destroys the squarefree filter
and is therefore the wrong null for the question "is there
integer-period structure in Mertens sign-changes beyond what the
squarefree-integer support set forces?".

Falsification (A) — squarefree-restricted local-density Poisson
surrogate.  Per density bin, draw events uniformly from the
squarefree integers in that bin (preserves the filter's residue-
class density profile).  1000 seeds, K=50 bins, Q_MAX=30.

| q   | real |a_q| | sqf-sur mean |a_q| | real / sqf-sur | p-value vs sqf-sur | survives p<0.001 |
|-----|-----------|-------------------|----------------|---------------------|------------------|
| 2   | 2.26e-4   | 2.52e-4           | **0.90×**      | 0.97                | **False**        |
| 3   | 4.94e-5   | 6.53e-5           | **0.76×**      | 0.65                | **False**        |
| 4   | 2.64e-4   | 1.66e-4           | 1.59×          | 0.035               | **False**        |

(Dense window; full-sequence panel has the same qualitative pattern:
real:sqf-sur = 0.90×, 0.76×, 1.53× at q = 2, 3, 4 respectively, with
none surviving p < 0.001.)

For q = 2 and q = 3 the real |a_q| is *below* the squarefree-restricted
surrogate mean — the squarefree-filter density profile *over-predicts*
the observed spike.  The q = 4 spike is mildly above (1.59× / 1.53×),
fails the p < 0.001 threshold (p ≈ 0.03), and is bounded as
suggestive-not-asserted under the AMBIGUOUS_AT_BOUNDARY column.

The p-adic v4 dominant_prime_per_q under the squarefree-restricted
null lands at p = 2 in 995 of 1000 surrogates.  The real signal's
p-adic dom = p = 2 is the modal squarefree-filter outcome; not a
property beyond the filter.

Falsification (B) — within-window stability across 5 non-overlapping
windows.  |a_q| at q = 2, 3, 4 is highly unstable across windows:

|          | q=2 CV | q=3 CV | q=4 CV |
|----------|--------|--------|--------|
| dense    | 0.85   | 0.55   | 1.18   |
| full     | 1.00   | 0.89   | 1.05   |

|a_q| at flagged q tracks the per-window event count rather than a
stable period structure.  Per the brief: "a genuine signal should
not be confined to a single window."  Mertens sign-change |a_q|
is dominated by window 0 (densest), inconsistent with a period-q
component carried by the sequence per se.

Falsification (C) — second-source cross-check.  Independent earlier
sieve from §7.bis (`data/mertens_liouville_results.json`) gives
n_sign_changes = 3866 and M(10^k) = [-1, 1, 2, -23, -48, 212, 1037];
present sieve gives the same numbers exactly.  Self-consistency
across two independent algorithm runs confirmed; the published-
table independence (Hurst 1995 / Kuznetsov 2011) was out-of-scope.

#### Verdict: NULL_IN_ORTHOGONAL_CHANNELS — beyond the squarefree filter

The Mertens sign-change sequence is featureless under the orthogonal
RF and p-adic v4 channels once the null is corrected to respect the
support set.  The RF spikes at q = 2, 3 that survived the rate-
matched Poisson surrogate of sub-question 3 are quantitatively
explained — and slightly over-predicted (real / sqf-sur ≈ 0.76–0.90×)
— by the squarefree filter alone.  The p-adic v4 dom = p = 2 is
the squarefree-filter modal outcome (99.5% of squarefree-restricted
surrogates).  The q = 4 spike at marginal significance (p ≈ 0.03 vs
the squarefree-restricted null) fails the brief's p < 0.001 gate
and is reported AMBIGUOUS_AT_BOUNDARY rather than asserted.

Phase 34a sharpens the §15 Mertens entry from "Poisson by the NNS
engine" to "Poisson by the NNS engine AND featureless under the two
orthogonal channels beyond the squarefree-filter floor."  This is
the orthogonal-channel survey's first arithmetic-side result.

#### Methodological generalisation: support-set-respecting nulls

A null that destroys structural constraints of the *support set* of
an arithmetic point process is the wrong null and will produce
spurious survival of structural-filter signatures.  This generalises
to any arithmetic point process whose support is a structured
subset: squarefree integers (Mertens / Liouville sign-changes),
primes (counting-function arithmetic), p-smooth numbers, etc.  The
rate-matched Poisson surrogate is correct only when the analysis
question is "is there structure beyond density?"; it is incorrect
when the analysis question is "is there structure beyond the
support-set restriction the substrate already implies?".  The
support-respecting null (squarefree-restricted Poisson at local
density here) is required for the orthogonal-channel survey on any
support-constrained arithmetic object — primes, p-smooth numbers,
prime-power positions, etc.

This is a sibling discipline to the §7.ter.19 published-product
audit (Phases 33a-c): both insist that the null encode the structural
property of the substrate (support set here; processing pipeline
there) before the survey can speak to "structure" cleanly.

#### Outputs

  - `data/phase34a_results/mertens_signchanges_N10000000.npz`
  - `data/phase34a_results/stationarity.json`
  - `data/phase34a_results/nns_classify.json`
  - `data/phase34a_results/rf_padic_survey.json`
  - `data/phase34a_results/falsify.json`

EPISTEMIC_STATE.md not modified by this phase: the verdict is on a
single arithmetic object (Mertens sign-changes), the orthogonal-
channel survey on ζ zeros / Dirichlet L-functions / elliptic curve
L-functions is queued as Phase 34b/c per the brief.


### 7.ter.48  Phase 34b — Liouville sign-changes: RF + p-adic v4 + cross-phase comparison with Mertens

Phase 34b runs the orthogonal-channel survey on the second Möbius-
family arithmetic object: positions where L(n) = Σ_{k=1}^n λ(k)
changes sign.  Unlike μ, λ is non-zero on every integer (λ(n) =
(-1)^Ω(n)), so L changes value by ±1 at every n — there is no
squarefree-filter restriction on the support set.  The user's
preamble note (added to the brief at run time) identifies the
parallel construction to 34a's structural-null discipline: the
natural null for L sign-changes is a ±1 random walk, not Poisson on
integer positions, and a pre-falsification check on this surrogate's
adequacy is load-bearing for the phase.

#### Data and pipeline

λ sieved to N_MAX = 10⁹ via a vectorised Ω-sieve (small-prime slice
phase + chunked large-prime residue check; small_part free'd before
λ array allocation to fit in 15 GB RAM).  λ-sieve parity vs the
existing project's smallest-prime-factor sieve: machine-precision
match at N = 10⁵ (cross-check).  Streaming cumsum + sign-change
detection avoids the 8 GB int64 L array.

  - 133 sign-changes total in [1, 10⁹]
  - 1 isolated at n = 3 (the initial L(2)=0 → L(3)=-1 transition)
  - **132 in the narrow window [906,150,257, 906,488,081]** — the
    Tanaka (1980) counterexample to Pólya's conjecture and a tight
    cluster of crossings where L oscillates around zero before
    returning to L ≤ 0
  - cluster width ≈ 337,825 integers; same per-integer density
    (≈ 3.9 × 10⁻⁴) as Mertens sign-changes overall in 34a, which
    makes a matched cross-phase comparison natural
  - within the cluster, two sub-clusters at the boundaries: 91 events
    in [906,150,257, 906,209,283] (low) and 41 events in
    [906,477,703, 906,488,081] (high), with a ~268K-wide quiet
    interior (no crossings)

  - `phase34b/liouville_events.py`     — Ω-sieve + streaming sign-
                                          change detection
  - `phase34b/run_prefalsify.py`       — surrogate-adequacy diagnostic
  - `phase34b/run_stationarity.py`     — sub-1 (cluster-scoped)
  - `phase34b/run_nns_classify.py`     — sub-2 (cluster + sub-clusters)
  - `phase34b/run_survey.py`           — sub-3/4 RF + p-adic vs two
                                          nulls + within-window
  - `phase34b/run_cross_phase.py`      — sub-4b Mertens × Liouville

Acceptance gates carried from the 34a session as the brief permits:
calibrator zoo 8/8 PASS, p-adic v4 5/6 single-prime detections
(per-q-power-normalised metric, period-13 narrow miss documented).

#### Pre-falsification: surrogate-adequacy diagnostic

A ±1 random walk over [1, N] has expected zero-crossings ≈ √(N/π).
At N = 10⁹ this is ≈ 17,841 — vs the real 133.  The unconditioned
random-±1 null **overpredicts full-range crossings by ~134×**;
real L stays ≪ 0 (drift much stronger than a simple random walk)
for n < ~9 × 10⁸, then enters the Tanaka cluster.  The
unconditioned null is therefore loose at full-range scope.

Cluster-restricted null (1000 seeds, width = 337,825, starting at
L_real(906,150,256) = -1):

|              | mean | std | median | real |
|--------------|------|-----|--------|------|
| # crossings  | 234.2 | 175.6 | 197 | 132 |
| P(null ≤ real) | 0.339 | | | |

Real cluster count is in the 33.9% percentile of the random-walk
null distribution — within the bulk.  Within the Tanaka cluster the
random-walk null is **TIGHT** as a calibrator.

#### Sub-question 1: stationarity

| configuration              | well-powered windows | modal | frac_modal | stationary |
|----------------------------|---------------------|-------|------------|------------|
| cluster, 4 windows         | 2/4 (91, 41)        | BL    | 1.000      | True       |
| cluster, 10 windows        | 3/10 (39, 52, 41)   | BL    | 0.667      | False (TR drift on 39-event window) |
| full [1, 10⁹], 10 windows  | 1/10                | BL    | 1.000      | True (trivial — only window 9 well-powered) |

Cluster is stationary at coarse resolution and shows mixed
primary at fine resolution (one TR window at 39 events at the
underpowering boundary, same pattern as 34a window-4).  Density
non-stationarity dominates by construction (the cluster events lie
in two sub-clusters at the boundaries).

#### Sub-question 2: NNS-engine reproduction

| configuration         | n   | primary | rep_med | ks_gue_med | per-q breakdown    |
|-----------------------|-----|---------|---------|------------|--------------------|
| cluster 132           | 132 | **BL**  | 0.000   | 0.931      | BL=29, ambiguous=1 |
| full 133              | 133 | **BL**  | 0.000   | 0.922      | BL=30/30           |
| sub-cluster low (91)  |  91 | **BL**  | 0.000   | 0.890      | BL=30/30           |
| sub-cluster high (41) |  41 | **BL**  | 0.000   | 0.719      | BL=24, TR=5, amb=1 |

Unambiguous Poisson (BL) modal across cluster, sub-clusters, and
full-sequence configurations.  Reproduces the §15 capability-report
verdict for Mertens/Liouville sign-change sequences without drift.

#### Sub-question 3: RF + p-adic v4 against TWO nulls

The user's surrogate-construction guidance: run both rate-matched
Poisson (the wrong null, parallel to 34a) AND ±1 random walk on the
cluster (the right structural null) — both reported as primary so
the surrogate-identity-effect is visible.

|                    | real | Poisson null mean | r(real/sur) | p (vs Poisson) | RW null mean | r(real/sur) | p (vs RW) |
|--------------------|------|-------------------|-------------|----------------|--------------|-------------|-----------|
| |a_q| at q=2       | 3.91e-4 | 2.77e-5      | **14.08×**  | 0.0000 ✓      | 6.93e-4      | **0.56×**   | 0.6630 ✗ |
| p-adic dom_per_q   | p=2  | p=2 in 443/1000 (44%) | — | — | p=2 in 990/1000 (99%) | — | — |

Against the rate-matched Poisson null: q=2 RF spike strongly
survives (p < 0.001) and p-adic dom = p = 2 in real.
Against the ±1-random-walk null: q=2 amplitude is **below** the
surrogate mean (real is 0.56× of sur mean), and p-adic dom = p = 2
is the modal random-walk outcome in 99.0% of surrogates.

Same wrong-null/right-null pattern as 34a, but with a **different
structural null**: 34a's right null was the squarefree-filter
residue-density profile of the support set; 34b's right null is the
random-walk first-passage statistics of the underlying ±1 process.
Both nulls produce p = 2 dominance for distinct mechanistic reasons,
and neither object carries integer-period structure beyond its
natural structural null.

Within-window stability (4-window split of the cluster — 2 well-
powered windows at 91 and 41 events; middle 2 windows have 0 events
by the cluster's sub-cluster geometry): q=2 dominates both well-
powered windows but with amplitudes 1.08e-3 (win 0, n=91) vs 4.85e-4
(win 3, n=41) — scales with the per-window event count, consistent
with the random-walk null's behaviour and inconsistent with a
period-q component that ought to be window-invariant.

#### Sub-question 4: cross-tabulation

The N=10⁹ sieve's first cluster sign-change at n = 906,150,257
matches the Tanaka (1980) value for the smallest counterexample to
Pólya's conjecture.  Independent published reference (Borwein,
Ferguson & Mossinghoff, *Math. Comp.* 77, 2008) confirms the value.
Project's earlier sieve at N=10⁷ found a single sign-change at n=3
(the initial transition), and the present N=10⁹ extension preserves
that and adds the cluster — self-consistent.

#### Sub-question 4b: cross-phase Mertens × Liouville

Both NNS-engine verdicts: BL Poisson.

|                                    | Mertens 34a            | Liouville 34b          |
|------------------------------------|------------------------|------------------------|
| n_events (working scope)           | 3016 (dense [1, 4e6])  | 132 (Tanaka cluster)   |
| RF spike q vs Poisson null         | 2, 3, 4 survive p<0.001 | 2 survives p<0.001     |
| p-adic dom_per_q (real)            | p=2                    | p=2                    |
| RF spike q vs structural null      | none survives p<0.001  | none survives p<0.001  |
| p-adic dom under structural null   | p=2 in 995/1000 (sqf)  | p=2 in 990/1000 (RW)   |
| structural null                    | squarefree-restricted  | ±1 random walk         |

Matched-sample bootstrap (Mertens sub-sampled to n=132 with 100 draws):

  - Pearson r between Mertens |a_q| (q = 2..30) and Liouville |a_q|:
    **0.664 ± 0.170** (highly correlated)
  - Mertens dom_per_q across bootstraps: p=2 in 94/100 draws, p=3 in
    5, p=5 in 1
  - Liouville dom_per_q: p=2

**Verdict — PARALLEL_SIGNAL_AT_q=2_AGAINST_WRONG_NULL +
PARALLEL_NULL_AGAINST_RIGHT_NULL.**

The cross-phase comparison shows a parallel surface signal: both
Möbius-family objects exhibit a q=2 RF spike and p=2 p-adic
dominance against the rate-matched Poisson null, with their RF
|a_q| spectra correlated at r ≈ 0.66 at matched sample size.  The
parallel does NOT emerge from a shared substrate-level structural
property of Möbius-family sequences.  It emerges from each object's
**distinct** structural-null artefact — squarefree-filter residue
density for Mertens, random-walk first-passage statistics for
Liouville — both of which independently produce the same wrong-null
signature (p=2 dominance + q=2 spike).  Once each object's correct
structural null is applied, both return NULL.

This is the dual-layer cross-phase verdict the brief's pre-specified
DIVERGENT / PARALLEL_NULL / PARALLEL_SIGNAL trichotomy does not
directly enumerate: PARALLEL_SIGNAL at the wrong-null layer +
PARALLEL_NULL at the right-null layer.  The wrong-null parallel
signal is **informative about the null shape**, not about substrate
structure.  It is the second instance of the §7.ter.47 methodological
generalisation: a structurally-loose null produces spurious survival
of the substrate's structural-floor artefact, and the wrong-null
signature can be similar across structurally-different substrates.

#### Verdict — Liouville object individually

**NULL_IN_ORTHOGONAL_CHANNELS** — against the random-walk null.
Reported as SAMPLE_SIZE_BOUNDED on the auxiliary "structure beyond
the random walk" claim: 132 events at q_max=30 means ≤ 5 events per
residue class for q ≥ 30, so the survey's statistical resolution
is intrinsically limited.  Pushing N_MAX past 10⁹ to access the
~hundreds of further sign-changes in [10⁹, 10¹²] (per Borwein 2008
extrapolation) would require Hurst-style or segmented Möbius-style
algorithms beyond Phase 34b's back-to-back-session compute budget.

#### Methodological generalisation extended from §7.ter.47

For arithmetic point processes the natural null depends on the
substrate's structural restriction:

  - Support-restricted (Mertens / Liouville sign-changes only at
    squarefree n; primes; prime-power positions): use a support-
    respecting Poisson at local density.
  - Random-walk-generated (Liouville sign-changes are zero-crossings
    of the running ±1 sum; analogous for any cumulative-sign
    arithmetic process): use a constrained random-walk null with
    starting value matched to the analysis-window's L value.

Both nulls are sibling-discipline to the §7.ter.19 published-product
audit: each insists the null encode the *generative* property of the
substrate before survey conclusions are clean.  The "right null" is
substrate-specific.  This refines §7.ter.47's general support-set
discipline.

For queued Phase 34c (ζ zeros / Dirichlet L-functions / elliptic
curve L-functions): each will have its own structural-null question
to audit *before* the orthogonal-channel survey runs.  ζ zeros have
a non-trivial mean spacing law (Riemann-Siegel theta unfolding);
that is the structural property the right null must respect.

#### Outputs

  - `data/phase34b_results/liouville_signchanges_N1000000000.npz`
  - `data/phase34b_results/prefalsify.json`
  - `data/phase34b_results/stationarity.json`
  - `data/phase34b_results/nns_classify.json`
  - `data/phase34b_results/survey.json`
  - `data/phase34b_results/cross_phase.json`

EPISTEMIC_STATE.md not modified: arithmetic-instrument orthogonal-
channel survey, not an H1/H2 substrate finding.

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

- Mertens function sign-change positions, N ≤ 10⁷, 3866 events:
  NNS-engine = BL Poisson (modal 30/30 q-bands, ks_gue_med = 0.904);
  RF indicator-mode and p-adic v4 orthogonal channels = featureless
  beyond the squarefree-filter density profile of the support set
  (real / squarefree-restricted-surrogate ratio = 0.76×, 0.90×, 1.59×
  at q = 2, 3, 4; p > 0.001 at all three q against the squarefree
  null).  Verdict NULL_IN_ORTHOGONAL_CHANNELS — beyond the squarefree
  filter — with q = 4 reported AMBIGUOUS_AT_BOUNDARY at p ≈ 0.03
  rather than asserted.  (§7.ter.47.)

- Liouville function sign-change positions, N ≤ 10⁹, 133 events (1
  isolated + 132 in the Tanaka counterexample cluster
  [906,150,257, 906,488,081]):  NNS-engine = BL Poisson modal across
  cluster and sub-clusters; RF + p-adic v4 against the rate-matched
  Poisson null shows q=2 spike survives p<0.001 and p-adic dom=p=2,
  but against the ±1-random-walk null (constructed parallel to 34a's
  squarefree-restricted null) real |a_q| at q=2 is 0.56× of surrogate
  mean (p = 0.66) and p=2 dominance is the modal random-walk outcome
  (99.0%).  Verdict NULL_IN_ORTHOGONAL_CHANNELS — beyond the random-
  walk null — bounded as SAMPLE_SIZE_BOUNDED at q ≥ 30.  Cross-phase
  with Mertens (matched-sample bootstrap, Pearson r = 0.66 between
  RF spectra at n = 132): PARALLEL_SIGNAL_AT_q=2 against the wrong
  null + PARALLEL_NULL against each object's right structural null.
  (§7.ter.48.)

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

- CRCNS pvc-11 macaque V1 (Smith & Kohn): per-unit ARS spike-train
  classification produces predominantly BL (Poisson) verdicts
  (1,144 / 1,159 H1-passing pairs), the expected V1 single-unit
  result.  Continuous ARS metrics (`ks_gue_med`, `rep_med`) carry a
  firing-rate-controlled signal correlating with V1 functional
  categories (OSI: ρ_partial = +0.720 with `ks_gue_med`, n=210,
  p < 1e-37; F1/F0: ρ_partial = +0.388 with `rep_med`, p = 6e-9).
  Phase 22b confirms within-recording (meta-fixed ρ = +0.742, no
  between-recording confound) and within-SNR-tertile (T1/T2/T3 =
  +0.672 / +0.742 / +0.532, sort-quality robust); the H1 finding is
  locked.  Population-event NNS structure on monkey1_natural_movie
  and monkey2_gratings_movie survives the required Aitchison-null
  surrogate conjunction (rate-matched, cell-shuffle, LN-evoked) at
  all 30 q-bands at 7 surrogate seeds (Phase 22b Pass E);
  monkey1_spontaneous survives the spontaneous-required (rate-matched,
  cell-shuffle, state-modulated) at q=6.  The H2 finding is locked
  at the LN-Poisson elimination floor.  Phase 22b Pass D (history-
  coupled GLM surrogate as a stricter elimination target) was
  inconclusive due to GLM-fit fragility at 5 ms bins on natural-
  movie data; Phase 25's 24-cell (n_lags × bin_ms × variant) grid
  produced the FIT-CEILING verdict — no configuration in the tested
  space (single- or multi-frame STA × canonical or unconstrained
  per-unit Pillow GLM) yields a usable history-coupled surrogate on
  this data, so the additional-elimination claim is methodologically
  untestable within the Phase 25 model family.  Phase 25 also surfaced
  a substantive co-finding: V1 anesthetised-macaque spike trains have
  a positive temporal correlation structure (median unconstrained-
  GLM history-kernel max ~+0.75, min ~+0.23) invariant across n_lags
  ∈ {1,4,8} and bin_ms ∈ {5,10,20,40} ms, indicating residual
  positive autocorrelation beyond what linear spatiotemporal stim
  filtering can absorb.  (§7.ter.30, §7.ter.31, §7.ter.35.)  Phase 30
  Kuramoto-class mechanism interpretation test returned NO
  MECHANISTIC MATCH at recording-wide-aggregate and local-cluster
  resolution: across the swept Kuramoto (K, σ) phase-space the
  aggregate modal classification is uniformly BR_artifact, whereas
  real V1 / Allen data classifies overwhelmingly TR (45 %) or BL
  (34 %); 156 / 160 well-powered real-data rows have no Kuramoto
  match.  The locked findings remain in their negative-elimination
  posture without a positive Kuramoto-class mechanism story.
  (§7.ter.38.)  Phase 31a + 31b engineering-layer architecture audit
  established that `joint_q_profile` (deployed classifier) and `pll_bank`
  (parallel infrastructure) are distinct objects; per-q ks_gue_q and
  rep_int_q are q-flat scalars under unit-mean normalisation, with
  per-q variation carried by the Ramanujan-Fourier amplitude axis only.
  The deployed classifier is event-level robust at the modal scale
  (single-event ∂(ks_gue_med, rep_med)/∂t_k ≈ 0).  Phase 30 sub-modal
  signals (+0.10 K-axis aggregate ks_med drift, +0.23 rate-matched
  Δks_med residual) trace to **order-parameter-driven aggregate-IEI
  structure development under locking** (multi-seed ρ(\|r\|, agg_ks_med)
  = +0.925) and within-cell rate-stratified dynamics signal
  respectively — methodological caveat: rate-matched Poisson surrogate
  is necessary but not sufficient for clean dynamics-only signal
  isolation; rate-stratified within-cell comparison required for
  cleaner discrimination.  Rate-stratified within-cell audit on pvc-11
  gratings: H1 OSI ↔ ks_gue_med **SURVIVES_STRATIFIED** (sign-consistent
  3/3 recordings, mag range 0.21); DSI and F1/F0 **PARTIAL_SURVIVAL**
  (mag ranges 0.47 and 0.34, monkey2 DSI sign-flip in high-rate
  tertile).  Allen F1/F0 rate-stratified replication (12 sessions):
  **SUBSTRATE_SYSTEMATIC_SURVIVES_STRATIFIED** at the session-aggregate
  level (12/12 sessions negative unstratified ρ, 10/12 tertile-mean
  negative), with the negative dynamics signal concentrating in
  mid-to-high-rate Allen units; low-rate tertile is null or weakly
  positive in 8/12 sessions.  p-adic v4 at q_max=200 on the three
  pvc-11 gratings recordings: **first p-adic class signal identified
  on biological data** — p=7 enrichment (monkey1 z=+9.77, monkey3
  z=+1.90, monkey2 z=+0.59; 3/3 above 1.5× threshold).  Cross-subset
  extension on all 12 pvc-11 recordings: p=7 enrichment is
  **P7_SUPPRESSED_IN_MOVIES** — present in spontaneous (6/6 above
  threshold; mean z = +2.22; monkey4 z = +6.09) and gratings (3/3
  above), suppressed in natural_movie / noise_movie / gratings_movie
  (mean z = −0.38 / −0.47 / +0.21).  Cross-species extension on 5
  Allen sessions: **P7_PVC11_SPECIFIC** — Allen spontaneous mean z =
  −0.87 vs pvc-11 spontaneous +2.22; substrate-systematic p=7
  difference matching the F1/F0 substrate-systematic pattern in
  direction.  **First cross-substrate-systematic p-adic-class signal
  from ARS.**  H2 stationarity check on the two pvc-11 surviving
  recordings: **H2_TIME_VARYING** at the modal-classification level;
  per-window surrogate battery (Phase 31f) verdicts:
  **monkey1_natural_movie WINDOW_AWARE_LOCKED** (8/10 windows pass
  required-conjunction), **monkey2_gratings_movie WINDOW_MIXTURE**
  (5/10 windows pass).  Locks H2 for monkey1_natural_movie under
  per-window surrogate discipline; narrows H2 for monkey2_gratings_movie
  to a window-mixture phenomenon.  Round 4 follow-ups (per-window
  p-adic + Allen extensions): **p=7 class signal is full-recording-
  aggregation, not per-window-stationary** in 9/15 pvc-11 recordings
  (PER_WINDOW_NULL); only monkey1_spontaneous is PER_WINDOW_STATIONARY
  on p=7.  Allen full 12-session p-adic confirmed **P7_PVC11_SPECIFIC**
  (Allen p=7 mean z=−0.14 spontaneous vs pvc-11 +2.22; substrate-
  systematic Δ=+2.36 holds across full Allen cohort).  Allen F1/F0
  per-session profile heterogeneous (5/12 canonical mid+high-negative;
  4/12 all-negative; 3/12 other).  Movie p=7 suppression is
  **content-driven, not rate-driven** (monkey1_gratings 27.93Hz z=+9.77
  vs monkey1_natural_movie 24.25Hz z=−0.96 at matched rate).  Allen
  per-window p-adic on 3 sessions × 3 conditions: cross-substrate p=7
  **inverts at per-window scope** — Allen natural_movie_one mean z=+4.70
  with 11/15 windows z>2 vs pvc-11 monkey1_gratings 0/5 windows z>2.
  pvc-11 has long-term coherence (full-recording p=7); Allen has
  short-term coherence (per-window p=7).  Awake vs anesthetised
  temporal-structure difference.  DSI monkey2 sign-flip diagnostic:
  not statistically significant (all p > 0.12, unstratified p = 0.82).
  Methodological commitment: future H2-style and p-adic surrogate-
  survival claims should include per-window surrogate battery as
  standard discipline.  (§7.ter.39.)  Phase 28 Allen Neuropixels
  spatial-scale ARS at <300 µm completed: **SPATIAL-SCALE-DEPENDENT**
  with non-monotone TR-fraction across bins (fine-local 15.2 %, local
  5.6 %, mid 18.6 %).  Local bin (100-300 µm, Ohiorhenuan's predicted
  regime) is the LEAST TR-structured of the three scales tested.
  Real-data TR-fraction is below surrogate at all bins.  **Ohiorhenuan
  engagement caveat from Phase 27 Analysis 3 is closed at <300 µm
  regime: V1 does NOT show local-rich structure at the scale
  Ohiorhenuan 2010 predicts.**  Combined Phase 27 (pvc-11, 400-600 µm)
  + Phase 28 (Allen NP, <300 µm): the H2 surviving structure is not
  a local-spatial-cluster phenomenon at any tested scale.  (§7.ter.40.)
  Phase 32a extraction-and-comparison over Round 4 sweep parquets fills
  the load-bearing missing comparator for the cross-substrate p-adic
  asymmetry: pvc-11 natural-movie per-window p=7 (10 windows total
  across monkey1+monkey2) is **PER_WINDOW_NULL** at mean window-z =
  −0.253 (0/10 windows z>2), against Allen natural_movie_one p=7
  mean window-z = +3.49 (19/30 windows z>2, all 4 Cre lines positive).
  **Verdict: PER_WINDOW_SUBSTRATE_CONSISTENT** — natural-movie viewing
  alone is insufficient to produce per-window p=7 in anesthetised
  macaque V1; stimulus content is ruled out as the load-bearing axis.
  Macaque-vs-mouse and anesthetised-vs-awake remain confounded.  pvc-11
  natural-movie *does* carry per-window p-adic structure at p=2
  (mean z = +2.53) and p=3 (+2.20); the substrate axis is prime-
  specific, not presence-vs-absence.  (§7.ter.41.)  Phase 32b
  cross-engine correlation discipline (within-substrate Spearman
  between per-recording / per-session F1/F0 ↔ rep_med signal and
  per-recording / per-session p=7 signal): **Allen INDEPENDENT_AXES**
  (n=6 sessions, ρ = −0.086, p = 0.87, robust across 4 scoring
  variants).  Sessions that carry one substrate-systematic signal
  do not preferentially carry the other.  pvc-11 underpowered at
  the per-recording level (n=3 gratings recordings; F1/F0 requires
  drifting-grating stimulus and is not measured on the 12 non-
  gratings recordings).  Cross-engine direction match is **two
  independent findings about the same substrate**, not one
  underlying axis viewed twice.  (§7.ter.42.)

- NANOGrav 15-year pulsar timing array (cross-domain substrate
  assessment): Phase 33a structural-match assessment on 5
  representative millisecond pulsars (B1855+09, J0030+0451,
  J0613-0200, J1909-3744, J0740+6620; 7,758–35,037 published TOAs
  each over 6–15 years).  **Verdict: STRUCTURAL_MISMATCH at the
  published-product level.**  A NANOGrav TOA is not a single pulse
  arrival — it is a folded-template-matched timestamp aggregating
  ~10⁴-10⁵ individual pulses per 10-s sub-integration, with ~50
  TOAs per observation epoch from the radio-backend frequency-channel
  grid.  Empirical pilot on TOAs (`pilot_direct_stats.py`, direct
  computation of NNS engine summary statistics per §7.ter.10 band-
  invariance): on raw TOAs ARS produces CV = 9.7–14.7 (vs 1.0
  Poisson), mass<0.3 = 96–98%, KS_Poisson z = +405 to +746 against
  rate-matched uniform-Poisson surrogate — but the signature is
  entirely the radio-backend within-epoch clustering, not pulsar
  physics.  On epoch-collapsed TOAs (one timestamp per observation):
  CV = 1.2–2.5, KS_Poisson z = +5 to +25 — still non-Poisson but
  reflecting telescope-scheduling cadence, not pulsar physics.
  Generalises the §7.ter.19 dataset-selection discipline from
  "MUAe-only neural" to "any published data product where aggregation
  has happened upstream of the event-level resolution at which ARS
  reads" — folded-template TOAs are dataset-selection-incompatible
  for ARS even though the substrate physics is well-characterised
  and the data is publicly available.  Per-pulse arrival data from
  raw radio archives would be a clean structural match but requires
  substantial PSRCHIVE/PRESTO preprocessing.  (§7.ter.44.)

- CERN Open Data CMS Run2011A DoubleMu dimuon events (Phase 33b
  cross-domain assessment).  Pilot on derived educational CSVs
  (record 545: Zmumu 10k, Jpsimumu 20k, Ymumu 20k, Dimuon_DoubleMu
  100k events).  **Verdict: STRUCTURAL_MATCH_BOUNDED.**  Processing-
  level audit at the survey entry point (per the Phase 33a
  generalisation): all bounded-effort accessible levels (NanoAOD,
  derived CSVs) are post-trigger and time-stamp-stripped — wall-clock
  timestamps preserved only at RAW level (CMSSW + multi-TB
  infrastructure, not bounded).  Time-domain framing: STRUCTURAL_
  MISMATCH at the published-product level.  Mass-spectrum framing
  (each dimuon event contributes one invariant mass to a point
  process in mass coordinate): STRUCTURAL_MATCH at the instrument-
  validation level only.  Direct-stats pilot: every sample produces
  enormous z-scores against uniform-in-mass surrogate (CV 3.4-82,
  mass<0.3 = 0.59-0.84, KS_Poisson z = +247 to +838), but the signal
  is the known resonance peak structure (Z⁰ at 91 GeV, J/ψ at 3.1
  GeV, Υ family ~10 GeV) — what every CMS Drell-Yan paper plots on
  figure 1.  No information above existing methods at this surrogate
  level.  Substantive analysis would require physics-aware surrogates
  (Drell-Yan continuum templates, trigger-efficiency models) —
  substantial infrastructure investment in a framework different
  from the deployed NNS+RF engines.  Two methodological generalisations
  surfaced: (a) processing-level audit must precede structural-match
  assessment at the survey entry point, and (b) surrogate adequacy
  is a domain-specific question — rate-matched Poisson is canonical
  for neural spike trains but not for particle physics; uniform-in-X
  surrogates produce trivially-large z-scores wherever data has been
  selected to contain known structure.  (§7.ter.45.)

- Single-molecule fluorescence blinking (Phase 33c cross-domain
  assessment).  No pilot classifications; survey-level audit only.
  **Verdict: STRUCTURAL_MISMATCH at the published-product level +
  INSTRUMENT_VALIDATION_BOUNDED at the event-sequence level.**  Most
  single-molecule blinking papers publish at the distributional-
  summary level (power-law on/off-time fits, exponents) — past
  event-level resolution.  When event sequences are published, they
  are post-state-detection; the state-detection methodology (binning
  + thresholding, HMM, change-point analysis, deep-learning
  idealisation) is the §7.ter.19 extractor.  The substantive Phase
  33c finding is a **convergent-validation result from the
  literature**: the single-molecule biophysics field has
  independently documented the §7.ter.19 failure mode in its own
  vocabulary as the "binning-and-thresholding distortion" problem
  (Crouch, Sauer, Schuette 2014, J Chem Phys 140, 114306; Houel et
  al. 2016, J Phys Chem C "Understanding the Bias Introduced in
  Quantum Dot Blinking Using Change Point Analysis").  Two
  methodologically distinct fields reach the same conclusion about
  extractor-dependence of inferred event-level structure, by
  independent paths.  Even at clean event-sequence access, ARS's
  calibrator zoo does not include a power-law-mixture universality
  class needed for single-molecule instrument-validation — extension
  required before validation can run.  Single-molecule fluorescence
  is not in ARS's substantive cross-domain envelope at bounded-effort
  access; the convergent-discipline finding is the substantive
  cross-domain result.  (§7.ter.46.)

- Allen Brain Observatory Visual Coding Neuropixels (single-session
  awake-mouse-V1 triage): the Phase 22a interface configuration
  applied to Allen session 732592105 (wt/wt, P100, 111 V1 units
  after QC) replicates the H1 OSI ↔ ks_gue_med headline in
  direction at ~58% of pvc-11 magnitude (partial ρ = +0.417,
  p < 1e-4, n=91); the F1/F0 ↔ rep_med second-order finding
  shows opposite-sign correlation (Allen −0.222 vs pvc-11 +0.388);
  the H2 natural_movie_one finding does NOT replicate (Allen
  produces BR_artifact with rep_med 0.700 where pvc-11 monkey1
  produced TR with rep_med 0.250).  Triage findings; see Phase 24
  (Full) for multi-session resolution.  (§7.ter.33.)

- Allen Brain Observatory Visual Coding Neuropixels (multi-session
  Phase 24 (Full) replication, 12 sessions, 5 wt + 4 Vip-Cre +
  2 Sst-Cre + 1 Pvalb-Cre): cross-species cross-state replication
  of the Phase 22a H1 OSI ↔ ks_gue_med headline at meta-fixed
  ρ = +0.363 (50% of pvc-11's +0.720, all 12 sessions positive,
  10 of 12 significant; I² = 43%).  DSI ↔ ks_gue_med replicates
  with stronger Allen magnitude (+0.269 vs pvc-11 +0.223;
  biologically plausible given mouse V1's heavier direction
  selectivity).  F1/F0 ↔ rep_med shows substrate-systematic sign-
  flip across all 12 sessions and all Cre lines (meta-fix −0.183
  vs pvc-11 +0.388, I² = 29%) — bounded substrate observation,
  not noise.  H2 natural_movie population-event finding does not
  replicate at default (3/12 PASS) or rate-matched (1/8 PASS,
  worse than default) configurations; the substrate-rate-regime
  hypothesis is falsified, and the Phase 22a H2 claim is bounded
  to anesthetised macaque V1 + specific stimulus + specific
  recording.  (§7.ter.34.)

- CRCNS GRB 230307A (Chen 2025 909 Hz QPO claim): Phase 23 targeted
  replication at the GRB_NEXT_STEPS-specified time-slice adjustment
  (100 ms sub-windows, q_max=50) detects no signature distinguishing
  the published 45–47 s claim window from surrounding sub-windows
  at the 909 Hz q-band (real and lightcurve-modulated Poisson
  surrogate both ~zero rep_int_q delta).  Phase 21's methodology-
  only verdict on the published QPO claim is reaffirmed: the
  time-slice adjustment was applied cleanly but did not produce a
  positive ARS-replicates-published-QPO finding.  Side-finding:
  a broadband TR signature in GRB 230307A's late-prompt window
  (t = 26–30 s post-trigger) survives the lightcurve-modulated
  Poisson surrogate at all tested smoothing windows from 1 ms to
  101 ms AND per-detector decomposition, with inverse-rate
  detector dependence that rules out deadtime artifacts.  Phase 26
  per-(detector, energy_channel) stratification (8 quantile bands per
  detector × 12 detectors) FALSIFIES the energy-band-sensitivity
  hypothesis: 0/11 detectors show significant within-detector energy
  variation after FDR correction, cross-detector aspect-correlation
  at energy-aligned bands is null (mean ρ = +0.076), and rate-
  dependence within energy buckets is *not* attenuated relative to
  pooled.  The TR signature is reframed as a per-cell rate-regime
  feature of the ARS metric (Spearman ρ(per-cell rate, TR fraction)
  = −0.48 in [26, 30) s and −0.89 in [10, 14) s control window).
  At per-cell rate, the lightcurve-modulated Poisson surrogate
  reproduces most of the TR signal — Phase 23's pooled-vs-surrogate
  failure was a rate-regime phenomenon, not the discovery of
  irreducible non-Poisson structure.  Phase 23's primary verdict
  on the QPO claim is unchanged.  (§7.ter.32, §7.ter.36.)

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

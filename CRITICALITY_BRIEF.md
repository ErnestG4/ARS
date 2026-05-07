# Criticality Measurement Tool — Full Specification

## Overview
A tool for measuring the universality class of dynamical criticality in arbitrary signals by analyzing the lock/slip statistics of a parallel Farey PLL bank. Primary application: determining whether the Riemann ζ zeros, neural oscillations, prime gap sequences, and related arithmetic signals share a universality class (GUE), and whether that class is detectable through their FM coupling structure.

## Architecture
```
Signal input (audio file / mic / synthesized / numeric)
        ↓
  Preprocessing (normalize, window, resample)
        ↓
  Farey PLL Bank (GPU — parallel PLLs, one per rational)
        ↓
  Lock/slip time series (binary, per rational, per sample)
        ↓
  Intermittency Extractor (dwell time distributions, lock event point process)
        ↓
  Universality Class Analyzer (NNS, pair correlation, number variance, SFF)
        ↓
  Visualization (lock map, intermittency portrait, spectral form factor)
```

All compute runs on the existing server (`server.py`) via WebSocket. GPU (5090) handles the PLL bank. CPU (24 cores, joblib) handles the statistical analysis. Browser renders all visualization.

---

## Module 1 — Farey PLL Bank

### What a PLL does here
A second-order phase-locked loop tracks the instantaneous phase of a sinusoidal component in the input signal. When the input has a component near the PLL's natural frequency, the loop **locks** — the phase error stays small and bounded. When it doesn't, the loop **slips** — phase error grows without bound (modulo 2π). The transition between these states is exactly the Arnold tongue boundary.

For a `p:q` rational ratio, we want a PLL whose natural frequency is `fc * p/q` where `fc` is a reference carrier. When the signal contains a component at that frequency with sufficient power, the PLL locks. The lock/slip record is the intermittency time series we need.

### Second-order PLL — mathematical definition

State variables per PLL:
- `φ_sig(t)` — instantaneous phase of the input signal at frequency `f_pll` (extracted via analytic signal / Hilbert transform)
- `φ_osc(t)` — phase of the PLL's internal oscillator
- `e(t) = sin(φ_sig(t) - φ_osc(t))` — phase error (nonlinear PLL detector output)
- `v(t)` — loop filter state

Loop equations (discrete, per sample at rate `sr`):
```
e[n]    = sin(φ_sig[n] - φ_osc[n])
v[n]    = ρ * v[n-1] + K_i * e[n]
dφ[n]   = K_p * e[n] + v[n]
φ_osc[n+1] = φ_osc[n] + (2π * f_pll / sr) + dφ[n]
```

Parameters:
- `K_p` — proportional gain (loop bandwidth, controls lock range)
- `K_i` — integral gain (frequency tracking, eliminates steady-state error)
- `ρ` — filter pole (0.9–0.99, controls loop filter time constant)

**Lock detection**: PLL is considered locked when the phase error magnitude stays below threshold `θ_lock` for at least `N_lock` consecutive samples:
```
locked[n] = (|e[n]| < θ_lock) AND (locked for N_lock samples)
slip[n]   = NOT locked[n]
```

### Farey rational set
For max denominator `Q_max`, the Farey sequence `F_{Q_max}` contains all fractions `p/q` in `[0,1]` with `q ≤ Q_max` in lowest terms. We use fractions in the range `[1/Q_max, Q_max]` (both sub- and super-unison ratios), giving us:
```
f_pll(p, q) = f_carrier * p / q
```

For `Q_max = 8`: rationals include `1:8, 1:7, 1:6, 1:5, 1:4, 2:7, 1:3, 2:5, 3:7, 1:2, 4:7, 3:5, 2:3, 5:7, 3:4, 4:5, 5:6, 6:7, 7:8, 1:1, 8:7, 7:6, 6:5, 5:4, 4:3, 7:5, 3:2, 5:3, 7:4, 2:1, 7:3, 5:2, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1` — approximately 80 PLLs.

For `Q_max = 12`: ~150 PLLs. Still trivially parallel on 5090.

### Analytic signal extraction (per PLL frequency)
Rather than running each PLL on the raw signal, extract a narrowband analytic signal around each PLL frequency first. This is a bandpass filter + Hilbert transform, giving instantaneous phase directly:

```python
x_bp[n]    = bandpass(x[n], f_pll, bandwidth=B)  # B = f_pll * 0.1 (10% BW)
x_analytic = x_bp + j * hilbert(x_bp)
φ_sig[n]   = angle(x_analytic[n])
```

On GPU: the bandpass can be an FIR filter applied via FFT convolution (fast for long signals). Then instantaneous phase is `atan2(imag, real)` which is embarrassingly parallel.

### GPU kernel specification — PLL bank

**Kernel name**: `pll_bank`

**Grid**: `(N_pll, N_chunks, 1)` where `N_pll` = number of PLLs, `N_chunks = ceil(signal_length / CHUNK_SIZE)`

**Block**: `(1, CHUNK_SIZE, 1)` where `CHUNK_SIZE = 256`

Each thread block processes one PLL × one chunk of signal. PLLs pass state between chunks via global memory (state array).

**Inputs:**
```c
const float* signal          // [signal_length] — input signal
const float* pll_freqs       // [N_pll] — PLL natural frequencies in Hz
const int    signal_length
const float  sr              // sample rate
const float  K_p             // proportional gain
const float  K_i             // integral gain
const float  rho             // filter pole
const float  theta_lock      // lock threshold (radians, e.g. π/6 = 0.524)
const int    N_lock          // samples required to confirm lock (e.g. sr*0.02 = 882)
const int    N_pll
```

**Outputs:**
```c
uint8_t* lock_map            // [N_pll × signal_length] — 1=locked, 0=slip
float*   phase_error         // [N_pll × signal_length] — instantaneous phase error
float*   pll_state_phi       // [N_pll] — persistent oscillator phase (between chunks)
float*   pll_state_v         // [N_pll] — persistent filter state (between chunks)
```

**Per-thread logic:**
```c
// Each thread: one PLL × one sample
int pll_idx = blockIdx.x;
int sample   = blockIdx.y * CHUNK_SIZE + threadIdx.y;
if (sample >= signal_length) return;

float f_pll  = pll_freqs[pll_idx];
float phi_osc = pll_state_phi[pll_idx];  // load persistent state
float v       = pll_state_v[pll_idx];

// Narrowband phase extraction via quadrature mixing + IIR lowpass
// (inline, avoids separate bandpass kernel)
// Mix signal with local oscillator at f_pll:
float phi_ref  = 2*PI * f_pll * sample / sr;
float I        = signal[sample] * cosf(phi_ref);   // in-phase
float Q        = signal[sample] * -sinf(phi_ref);  // quadrature
// IIR lowpass (single-pole, fc = f_pll * 0.05):
// (state carried per-PLL in separate arrays)
float alpha    = 1 - expf(-2*PI * f_pll * 0.05 / sr);
I_lp = (1-alpha)*I_lp_prev + alpha*I;   // (needs I_lp_state array)
Q_lp = (1-alpha)*Q_lp_prev + alpha*Q;
float phi_sig  = atan2f(Q_lp, I_lp);   // narrowband instantaneous phase

// PLL update
float e        = sinf(phi_sig - phi_osc);
v              = rho * v + K_i * e;
float dphi     = K_p * e + v;
phi_osc        = phi_osc + (2*PI * f_pll / sr) + dphi;

// Lock detection
uint8_t locked = (fabsf(e) < theta_lock) ? 1 : 0;
lock_map[pll_idx * signal_length + sample] = locked;
phase_error[pll_idx * signal_length + sample] = e;

// Write back state
pll_state_phi[pll_idx] = phi_osc;
pll_state_v[pll_idx]   = v;
```

**Note**: the IIR lowpass requires per-PLL state arrays `I_lp_state[N_pll]` and `Q_lp_state[N_pll]`. These are initialized to zero and updated each chunk, serialized within each PLL's thread block.

**Important**: because chunks are sequential (each chunk depends on previous state), launch chunks in sequence with state passing, not all at once. Within each chunk, all PLLs run in parallel.

### Parameter guidelines

| Parameter | Value | Rationale |
|---|---|---|
| `K_p` | 0.05–0.2 | Loop bandwidth ~1–5% of `f_pll` |
| `K_i` | 0.001–0.01 | Slow frequency tracking |
| `ρ` | 0.95 | ~20 sample time constant |
| `θ_lock` | π/6 (0.524 rad) | 30° phase error = locked |
| `N_lock` | 0.02 × sr | 20ms confirmation window |
| `Q_max` | 8 (start), 12 (fine) | ~80 / ~150 PLLs |
| `f_carrier` | tunable | User sets reference carrier |

---

## Module 2 — Intermittency Extractor

### Inputs
- `lock_map[N_pll × T]` — binary lock/slip per PLL per sample
- `pll_freqs[N_pll]` — frequency of each PLL
- `farey_rationals[N_pll]` — `(p, q)` pair for each PLL

### Outputs per PLL

**Dwell time sequences:**
```python
lock_dwells[i]  = [duration of each locked period, in samples]
slip_dwells[i]  = [duration of each slip period, in samples]
```

**Lock event point process:**
```python
lock_events[i]  = [sample index of each lock onset]
```

**Per-PLL statistics:**
```python
lock_fraction[i]    = fraction of time spent locked
mean_lock_dwell[i]  = mean locked period duration
mean_slip_dwell[i]  = mean slip period duration
dwell_exponent[i]   = power law exponent α fitted to dwell distribution
```

### Dwell time extraction
```python
def extract_dwells(lock_series):
    # Run-length encoding of binary series
    events = []
    current_state = lock_series[0]
    count = 1
    for i in range(1, len(lock_series)):
        if lock_series[i] == current_state:
            count += 1
        else:
            events.append((current_state, count))
            current_state = lock_series[i]
            count = 1
    events.append((current_state, count))

    lock_dwells = [e[1] for e in events if e[0] == 1]
    slip_dwells = [e[1] for e in events if e[0] == 0]
    lock_onsets = [sum(e[1] for e in events[:i])
                   for i, e in enumerate(events) if e[0] == 1]
    return lock_dwells, slip_dwells, lock_onsets
```

### Power law fitting
For dwell time distribution `P(τ)`, fit `P(τ) ~ τ^(-α)` using maximum likelihood on the discrete power law (Clauset-Shalizi-Newman method, not histogram fitting):

```python
def fit_power_law(dwells, tau_min=10):
    # MLE estimate of α for discrete power law
    # α_hat = 1 + n * [Σ ln(τ_i / (τ_min - 0.5))]^(-1)
    dwells = np.array([d for d in dwells if d >= tau_min])
    if len(dwells) < 20:
        return None, None
    n = len(dwells)
    alpha = 1 + n / np.sum(np.log(dwells / (tau_min - 0.5)))
    # KS test for goodness of fit
    ks_stat = power_law_ks_test(dwells, alpha, tau_min)
    return alpha, ks_stat
```

**Criticality signature**: `α` in range `[1.5, 2.5]` with good KS fit indicates power-law dwell times consistent with criticality. `α >> 3` or exponential fit = non-critical. `α < 1.5` = supercritical (too much locking).

---

## Module 3 — Universality Class Analyzer

This is the heart of the tool. Takes the lock event point processes and determines which random matrix ensemble their statistics match.

### Input
`lock_events` — for a chosen PLL or aggregate across PLLs: sorted list of lock onset times `{t_1, t_2, ..., t_N}`.

### Statistic 1 — Nearest neighbor spacing distribution (NNS)
```python
def compute_nns(lock_events):
    # Unfold spacings to unit mean (remove local density variation)
    spacings = np.diff(lock_events)
    # Unfold: divide by local mean spacing
    mean_spacing = np.mean(spacings)
    s = spacings / mean_spacing  # normalized spacings
    return s
```

**Comparison distributions:**
```python
# Poisson (integrable, non-critical)
P_poisson(s) = exp(-s)

# GOE (time-reversal symmetric chaotic)
P_GOE(s) = (π/2) * s * exp(-π*s²/4)

# GUE (quantum chaotic, no time-reversal — what Riemann zeros follow)
P_GUE(s) = (32/π²) * s² * exp(-4*s²/π)

# Wigner surmise — standard approximation for GUE
P_Wigner(s) = (32/π²) * s² * exp(-4s²/π)
```

Fit each via KS test, report best fit and p-value.

### Statistic 2 — Pair correlation function
```python
def pair_correlation(lock_events, r_max=5.0, n_bins=50):
    # Two-point correlation: density of pairs at separation r
    # R2(r) = 1 - (sin(πr)/(πr))² for GUE
    # R2(r) = 1 for Poisson (no correlations)
    N = len(lock_events)
    mean_spacing = np.mean(np.diff(lock_events))

    r_vals = np.linspace(0, r_max, n_bins)
    R2 = np.zeros(n_bins)

    for i, r in enumerate(r_vals):
        window = r * mean_spacing * 0.1  # bin width
        count = sum(1 for j in range(N) for k in range(j+1, N)
                    if abs(abs(lock_events[k]-lock_events[j])/mean_spacing - r) < window)
        R2[i] = count / (N * (N-1) / 2 * 2 * window)

    return r_vals, R2

# GUE analytical form:
R2_GUE(r)    = 1 - (sin(π*r)/(π*r))²
# GOE analytical form:
R2_GOE(r)    = 1 - (sin(π*r)/(π*r))² - d/dr[(sin(π*r)/(π*r)) * Si(π*r)]
# Poisson:
R2_Poisson(r) = 1  (flat — no correlations)
```

**GUE signature**: characteristic dip near `r=0` (level repulsion — lock events avoid each other at short separations), oscillations at larger `r`.

### Statistic 3 — Number variance
```python
def number_variance(lock_events, L_max=20):
    # Σ²(L) = variance of count of events in windows of length L
    mean_spacing = np.mean(np.diff(lock_events))
    L_vals = np.linspace(0.5, L_max, 50)
    sigma2 = np.zeros(len(L_vals))

    T = lock_events[-1] - lock_events[0]
    for i, L in enumerate(L_vals):
        window = L * mean_spacing
        # Slide window, count events in each position
        counts = []
        for t0 in np.arange(lock_events[0], lock_events[-1] - window, window * 0.1):
            n = np.sum((lock_events >= t0) & (lock_events < t0 + window))
            counts.append(n)
        sigma2[i] = np.var(counts)

    return L_vals, sigma2

# Analytical forms:
Sigma2_GUE(L)    = (2/π²) * (log(2π*L) + γ_E + 1 - π²/8)   # γ_E = Euler-Mascheroni
Sigma2_GOE(L)    = (1/π²) * (log(2π*L) + γ_E + 1)
Sigma2_Poisson(L) = L  # linear
```

**GUE signature**: logarithmic growth (much slower than Poisson's linear growth), indicating strong long-range correlations between lock events.

### Statistic 4 — Spectral form factor
```python
def spectral_form_factor(lock_events, t_max=5.0, n_t=200):
    # K(t) = |Σ_n exp(2πi * t_n * t / mean_spacing)|² / N
    # For GUE: K(t) = t for t < 1, K(t) = 1 for t > 1 (with oscillations)
    # For Poisson: K(t) = 1 (flat)
    N = len(lock_events)
    mean_spacing = np.mean(np.diff(lock_events))
    unfolded = lock_events / mean_spacing

    t_vals = np.linspace(0.01, t_max, n_t)
    K = np.zeros(n_t)

    for i, t in enumerate(t_vals):
        phases = 2 * np.pi * unfolded * t
        K[i] = abs(np.sum(np.exp(1j * phases)))**2 / N

    return t_vals, K
```

**GUE signature**: linear ramp from 0 at `t=0`, transitioning to plateau at `K=1` near `t=1` (the "ramp-plateau" transition). The ramp slope and transition point are universal for GUE.

---

## Module 4 — Cross-signal Comparison

Running the full analysis on multiple signals and comparing their universality class assignments:

```python
signals = {
    'zeta_zeros':   make_zeta_signal(n_zeros=50),
    'prime_gaps':   make_prime_gap_signal(),
    'mobius':       make_mobius_signal(),
    'white_noise':  make_white_noise(),   # null hypothesis — should give Poisson
    'eeg_theta':    load_eeg_segment(),   # if available
    'pure_fm_gue':  synthesize_gue_fm(),  # synthetic GUE signal for calibration
}

# For each signal:
# 1. Run PLL bank → lock_map
# 2. Extract intermittency → lock_events
# 3. Compute NNS, pair correlation, number variance, SFF
# 4. Fit universality class
# 5. Record: (signal_name, class, KS_p_value, alpha_exponent)

# Output table:
# Signal        | Class  | NNS fit | Pair corr | Num var | SFF shape
# zeta_zeros    | GUE?   | p=?     | dip at 0? | log?    | ramp?
# white_noise   | Poisson| p>0.05  | flat      | linear  | flat
# prime_gaps    | ?      | ?       | ?         | ?       | ?
```

### Synthetic GUE calibration signal
To verify the analysis pipeline works, generate a signal whose lock event statistics are analytically known to be GUE:

```python
def make_gue_fm_signal(sr=44100, duration=8.0, N_zeros=200):
    """
    Synthesize a signal whose frequency content is driven by
    GUE random matrix eigenvalues — known ground truth for GUE statistics.
    Uses GOE/GUE eigenvalues from random matrix generation.
    """
    from numpy.random import default_rng
    rng = default_rng(42)

    # Generate GUE matrix eigenvalues
    # GUE: Hermitian matrix with complex Gaussian entries
    N = N_zeros
    A = (rng.standard_normal((N, N)) +
         1j * rng.standard_normal((N, N))) / np.sqrt(2)
    H = (A + A.conj().T) / np.sqrt(2 * N)
    eigenvalues = np.sort(np.linalg.eigvalsh(H))

    # Unfold to unit mean spacing
    unfolded = eigenvalues / np.mean(np.diff(eigenvalues))

    # Synthesize as sum of sinusoids (same structure as zeta signal)
    t = np.arange(int(sr * duration)) / sr
    signal = np.zeros(len(t), dtype=np.float32)
    for lam in unfolded[:N_zeros]:
        signal += np.cos(lam * np.log(t + 1)) / np.sqrt(abs(lam) + 1)

    return signal / np.std(signal)
```

This gives us a signal with analytically guaranteed GUE statistics to validate the pipeline end-to-end before making any claims about the ζ zeros.

---

## Module 5 — Visualization

### Display 1 — The Lock Map
**Canvas**: full width × `N_pll` height (each PLL is one pixel row)

**X axis**: time through signal
**Y axis**: Farey rational index, ordered by `p+q` then `p/q` value
**Color**: locked=bright (hue by rational: simple rationals warm, complex cool), slip=dark

**Overlays:**
- Horizontal lines separating rational families (same denominator)
- Vertical markers at known zero frequencies (scaled by current sr)
- Diagonal brush strokes indicate frequency sweeps in signal

**Interaction**: click on a cell → zoom into that PLL's phase error trace

### Display 2 — Dwell Time Portrait
Two panels: lock dwell times (left) and slip dwell times (right)

**X axis**: log(dwell time in ms)
**Y axis**: log(count)
**Overlay**: fitted power law line, exponential comparison

Per PLL or aggregate: selector for which PLLs to include

### Display 3 — Universality Class Panel
Four sub-plots, one per statistic:
1. NNS histogram + GUE/GOE/Poisson analytical curves
2. Pair correlation `R2(r)` + GUE/Poisson curves
3. Number variance `Σ²(L)` + GUE/GOE/Poisson curves
4. Spectral form factor `K(t)` + GUE ramp-plateau

Summary box: best-fit universality class, KS p-values for each, confidence statement

### Display 4 — Cross-signal Comparison Table
Signal × statistic matrix, color-coded by p-value of GUE fit. Highlights cells where ζ zeros and EEG signals agree.

---

## File Structure

```
criticality_tool/
├── server.py              # FastAPI + WebSocket (extend existing)
├── pll_bank.py            # PLL bank: GPU kernel + Python wrapper
├── intermittency.py       # Dwell time extraction + power law fitting
├── universality.py        # NNS, pair correlation, number variance, SFF
├── signal_gen.py          # All signal generators (extend scanner.py generators)
├── comparison.py          # Cross-signal analysis pipeline
├── static/
│   └── index.html         # Full visualization UI
├── tests/
│   ├── test_pll.py        # Verify PLL locks on pure FM (unit test)
│   ├── test_stats.py      # Verify GUE stats on synthetic GUE signal
│   └── test_pipeline.py   # End-to-end: GUE signal → GUE classification
└── README.md
```

---

## Implementation Order for Claude Code

### Phase 1 — PLL bank (foundation)
1. Implement `pll_bank.py` with CPU version first (pure numpy, one PLL, verify lock behavior on pure FM)
2. Verify: pure FM signal → single PLL at correct frequency → locks within 50ms
3. Implement GPU kernel
4. Verify GPU matches CPU output
5. Scale to full Farey set, verify parallelism

### Phase 2 — Intermittency extraction
1. Implement `intermittency.py` with synthetic test: generate known power-law dwell times, verify recovery
2. Wire to PLL output
3. Verify power law exponent recovery on synthetic data

### Phase 3 — Universality class analysis
1. Implement `universality.py`
2. Critical test: generate GUE matrix eigenvalues → synthesize GUE FM signal → run full pipeline → verify GUE classification
3. Same for Poisson (white noise) — must classify as Poisson
4. These two tests are the acceptance criteria for the pipeline

### Phase 4 — Signal comparison
1. Run all signal sources through verified pipeline
2. Record classifications
3. Report

### Phase 5 — Visualization and UI
1. Lock map canvas
2. Dwell time portrait
3. Universality class panel
4. Cross-signal table

---

## Acceptance Criteria

The tool is working when:

1. A pure FM signal with known `fc` and `fm` locks the corresponding Farey PLL within 50ms with >80% lock fraction
2. White noise produces Poisson classification (p > 0.05 on KS test) for NNS, pair correlation, and number variance
3. A synthetic GUE FM signal (from random matrix eigenvalues) produces GUE classification (p > 0.05)
4. The ζ zeros signal produces a definitive classification (either GUE or not) with p < 0.01

Criteria 1–3 validate the pipeline. Criterion 4 is the experiment.

# Arithmetic Resonance Spectrograph (ARS)

A calibrated multi-scale RMT readout for arbitrary time series.

ARS classifies the universality class of a signal's level statistics — Poisson
(integrable), GOE (time-reversal symmetric chaotic), or GUE (quantum chaotic) —
for inputs where the level sequence is either directly accessible or extractable
without imposing artificial periodicity. It embeds a sequence into a chirp signal,
runs a GPU-parallel bank of Farey-rational phase-locked loops against it, and
extracts passage-time spacings that are unfolded and compared against random
matrix theory predictions.

Continuous signals processed via prominence-thresholded peak detection are
subject to extraction-pipeline artifacts that imitate Wigner-class level
repulsion at the autocorrelation scale of the input — see §7.ter.19 of
RESULTS.md for a worked example (LLM residual streams) and the diagnostic
protocol (uniform-jitter calibrator + pre-processing-stage baseline).

The instrument is validated against the Riemann ζ zeros, whose universality class
(GUE, per the Montgomery-Odlyzko conjecture) is established to extraordinary
confidence by direct methods. Reproducing that result via a novel measurement chain
is the calibration. The intended application is signals where direct level-sequence
access is unavailable — audio, neural spike trains, sensor streams — and where
the underlying arithmetic or dynamical structure is unknown.

---

## Architecture

```
Sequence t_k  (zero heights, prime gaps, spike times, ...)
     ↓
Chirp:  x(t) = Σ_k cos(t_k · log(t+1)) / √t_k
     ↓
Farey PLL bank  (one PLL per rational p:q ≤ Q_max, GPU-parallel via CuPy)
     ↓
Two pipelines:

  ANALYTICAL (primary, calibrated)
  Passage times  t*_{k,p/q} = t_k / (f_ref · p/q) − 1
  → unfolded NNS → KS distances → universality class

  MEASURED (secondary, subject to instrument bias)
  Lock-onset times → NNS → classification
  Note: time-symmetric peak detection folds GUE onto GOE (~0.13 KS shift,
  observed empirically; consistent with Dyson's threefold way but not
  proven rigorously here)
```

---

## Calibration

All three calibration anchors classify correctly with KS ≤ 0.025:

| signal | best fit | KS_min | n spacings |
|---|---|---|---|
| GUE eigenvalues (R=2 semicircle unfolding) | GUE | 0.022 | 13,971 |
| GOE eigenvalues | GOE | 0.021 | 13,965 |
| Poisson uniform | Poisson | 0.018 | 17,628 |

ζ zeros — validation target (GUE fit tightens with height, consistent with
asymptotic universality):

| zeros | n spacings | KS_GUE | KS_GOE |
|---|---|---|---|
| first 2,000 | 49,181 | 0.032 | 0.100 |
| first 100,000 (Odlyzko zeros1) | 1,845,065 | 0.015 | 0.081 |
| heights ≈ 1.1M (Odlyzko zeros6) | 450,184 | 0.012 | 0.079 |

This replicates the Montgomery-Odlyzko result via the passage-time metric.
Odlyzko's direct computation remains the authoritative result; these numbers
confirm the instrument reads correctly on a known system.

---

## Cross-signal survey

| signal | best fit | KS_min | n | notes |
|---|---|---|---|---|
| primes ≤ 10⁶ | Poisson | 0.156 | 2.68M | Cramér heuristic reproduced |
| twin primes ≤ 10⁷ | Poisson | 0.057 | 1.16M | faster convergence than primes |
| Gaussian prime norms ≤ 10⁵ | Poisson | 0.184 | 164k | |
| Liouville ±1 support | unclassifiable | — | — | integer-floor spacing problem |
| EEG θ zero-crossings | quasi-periodic bandpass artifact | KS_GUE = 0.190 | 461,520 (32-subject cohort) | not Wigner-class — see below |

**EEG caveat**: the original 1-channel, 1-subject pilot was extended to the full
32-subject EEGMMIDB cohort × 5 channels × 3 conditions (480 segments, 461,520
pooled spacings, RESULTS §7.ter.2). KS_GUE ≈ 0.18 across the entire cohort —
not a small-N fluctuation, but also **not** a Wigner-class identification. The
diagnostic is mass<0.3 ≈ 0.001: zero-crossings of a 4–8 Hz bandpass are forced
to ~125 ms intervals by the filter itself, so the short-spacing tail is
structurally absent. The metric correctly identifies this as a quasi-periodic
artifact, not as random-matrix dynamics. Same family of finding as the LLM
residual-stream artifact in §7.ter.19 — both cases are level-repulsion-by-
construction at the autocorrelation scale of the extraction method, not of the
underlying dynamics. Right inputs for testing universality on neural data are
spike timing or inter-burst intervals on the raw broadband signal.

---

## When to use this vs. direct NNS

Direct NNS on the unfolded sequence is simpler, faster, and gives better statistics
when the level sequence is directly accessible. Use ARS when:

- The sequence is embedded in a continuous signal and levels are not directly
  observable
- Multi-scale rational structure is of interest (different Farey rationals probe
  different frequency neighborhoods simultaneously)
- You want to compare heterogeneous signal types on a common metric

For ζ zeros specifically, Odlyzko's direct approach is preferable. ARS is
validated here because the answer is known; it is designed for cases where it
isn't.

---

## Quickstart

```bash
pip install -r requirements.txt

# Fast demo: ζ + GUE/GOE/Poisson controls (~30s, no external data needed)
python3 run_analytical_nns.py
# → GUE classification of ζ, KS=0.034, n=18,529 spacings

# Full cross-signal survey (requires external data — see RESULTS.md §9)
python3 run_phase5.py
```

---

## External data

Place in `data/` before running large-scale analyses:

- **Odlyzko ζ tables**: `zeros1`, `zeros6` from
  https://www-users.cse.umn.edu/~odlyzko/zeta_tables/
- **PhysioNet EEG**: `S001R01.edf` etc. from
  https://physionet.org/files/eegmmidb/1.0.0/

ζ zeros can also be computed on demand via `mpmath.zetazero` (used by the
quickstart demo).

---

## File layout

```
├── README.md
├── RESULTS.md              # full methods, calibration, all results, limitations
├── CRITICALITY_BRIEF.md    # original specification
├── CITATION.cff
├── LICENSE                 # AGPL-3.0-or-later
├── requirements.txt
│
├── pll_bank.py             # Farey PLL bank, CPU + CuPy GPU
├── intermittency.py        # dwell extraction, power-law MLE, Stern-Brocot depth
├── universality.py         # NNS, Σ²(L), pair correlation, SFF
├── arithmetic_toolkit.py   # 5-engine fingerprint: Ramanujan-Fourier, p-adic
│                           #   profile, multiscale Fano, R₂(r), SB-split
├── signal_gen.py           # signal generators
│
├── run_analytical_nns.py   # primary calibrated metric — start here
├── run_full_sweep.py       # 3000-cell parameter sweep
├── run_decisive.py         # 1000-zero × 300s PLL run
├── run_controls.py         # selection-bias + time-reversal controls
├── run_calibration.py      # GUE/GOE chirp calibration
├── run_phase3.py           # NNS / Σ² / SFF
├── run_phase4.py           # cross-signal first batch
├── run_phase5.py           # cross-signal wider batch + EEG
│
├── tests/
│   ├── test_pll.py         # Phase 1 acceptance
│   ├── test_pll_gpu.py     # GPU↔CPU parity
│   └── test_intermittency.py
```

---

## Hardware

- **CPU**: AMD Ryzen 9 5900x, 24 threads (joblib parallel)
- **GPU**: NVIDIA RTX 4090, CuPy + CUDA 12

PLL bank throughput: ~82M PLL-samples/sec on the 4090. CPU fallback available.

---

## Related work

The connection between phase-locking, the Riemann zeta function, and prime
number theory has been developed analytically by M. Planat and collaborators
(FEMTO-ST), with the foundational results that ARS rests on appearing across:

- **Planat & Henry 2002** — phase-noise of PLLs analyzed via Farey arithmetic
  and continued-fraction expansions, the Stern–Brocot organization of mode
  locking that ARS reuses as the PLL bank parameterization;
- **Planat & Rosu 2002** — Ramanujan-sum / Ramanujan-Fourier expansion of
  arithmetical functions, the formulation that ARS Engine 1
  (`ramanujan_fourier`) implements directly;
- **Planat 2006** — connection between Farey-rational phase locking and the
  Mangoldt arithmetic function / Riemann ζ;
- **Planat 2026** — recent work on Bost-Connes quantum statistical mechanics,
  KMS states, and the relationship between phase coherence at rational
  frequencies and prime-theoretic invariants;

(See `CITATION.cff` for full reference metadata as it becomes available.)
ARS provides a complementary empirical approach: the Farey PLL bank as a
measurement instrument applied to external signals, rather than as an
oscillator whose noise is being analyzed.

ARS was developed independently of Planat's published work; the author had no 
prior exposure to it. Convergence on the Farey-rational-PLL framework as an 
arithmetic instrument arose through extended collaboration with Claude 
(Anthropic), whose training corpus includes Planat's papers from 2002 onward. 
Reading those papers after the fact (correspondence with M. Planat, May 2026) 
confirmed that the analytical scaffolding ARS rests on — phase-locking as a 
number-theoretic phenomenon, Ramanujan-Fourier analysis of arithmetical 
signals, the connection of Farey rationals to ζ — was developed by Planat and 
collaborators over the preceding two decades. We cite his work as the 
originating analytical framework. ARS is the empirical-instrument 
complement: it does not derive from those papers in the conventional 
read-then-build sense, but it would not exist in its current form without 
them, transmitted through the training data of a language model.

---

## License

AGPL-3.0-or-later. See LICENSE.

## Citation

See CITATION.cff.

## Status

Research code. Calibrated and reproducible; see RESULTS.md §10 for known
limitations. In-progress writeup. Issues, reproductions, and patches welcome.

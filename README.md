# criticality_tool

A measurement instrument for **dynamical level statistics** of arithmetic
signals.  Built around a parallel Farey bank of phase-locked loops driven
by chirp synthesis from a sequence of "frequencies" `t_k` (zero heights,
prime gaps, random matrix eigenvalues, neural zero-crossings, ...).

The intended question:  **do the Riemann ζ zeros — and other arithmetic
structures — exhibit the universality class of quantum chaos (GUE), and
can that be detected through their FM coupling structure with a real
instrument?**

The answer found by this tool: yes for ζ.  See `RESULTS.md` for the
methods, calibration, and full cross-signal table.

## Headline result

Riemann ζ zeros' **analytical passage-time NNS through the calibrated
metric follows the Wigner GUE distribution**, and the fit *improves*
at higher zero heights as the GUE conjecture predicts:

| zeros sampled | n pooled spacings | KS to Wigner GUE |
|---|---|---|
| first 2,000 | 49,181 | 0.032 |
| first 100,000 | 1,845,065 | 0.015 |
| heights ≈ 1,100,000 (Odlyzko zeros6 high chunk) | 450,184 | **0.012** |

GUE eigenvalues, GOE eigenvalues, Poisson uniform, and a Poisson density
control all classify to their predicted classes with KS ≤ 0.025 — the
metric is calibrated.

The same instrument is also applied to primes (Cramér-asymptotic Poisson
behaviour observed), Liouville function support, twin primes, Gaussian
prime norms, and a sample of resting-state EEG θ-band zero-crossings.
Full table in `RESULTS.md` §7.

## Architecture

```
Signal input  (chirp from a t_k list, or raw audio / numeric)
     ↓
Farey PLL bank  (one PLL per p:q ≤ Q_max, GPU-parallel via CuPy)
     ↓
Lock/slip time series  (binary, per PLL, per sample)
     ↓
Intermittency extractor  (dwell times, lock onsets, Stern-Brocot depth)
     ↓
Universality analyzer  (NNS / Σ²(L) / pair correlation / SFF)
     ↓
Classification  (Wigner GOE / GUE / Poisson / sub-class)
```

Two parallel pipelines:
- **Measured**: chirp → PLL bank → lock-onset NNS.  Subject to
  instrument bias (folds GUE → GOE through time-symmetric peak detection;
  see RESULTS.md §6.5).
- **Analytical**: t_k list → passage-time NNS via PLL selection function.
  Bypasses chirp/PLL dynamics; **this is the calibrated primary metric**.

## Quickstart

```bash
# Install dependencies (CuPy is optional but recommended for GPU)
pip install -r requirements.txt

# Compute first 1000 Riemann zeros via mpmath (~3 min, cached afterwards)
python3 -c "import mpmath, numpy as np; mpmath.mp.dps = 16; \
  np.save('zeros_1000.npy', np.array([float(mpmath.zetazero(n).imag) for n in range(1, 1001)]))"

# Run the analytical NNS classification on ζ + GUE/GOE/Poisson controls
python3 run_analytical_nns.py
# → Wigner GUE classification of ζ, with KS = 0.034 at n = 18,529 spacings

# Apply to a wider survey — primes, twin primes, Liouville, Gaussian
# prime norms, EEG (requires data from external sources, see §9 of RESULTS.md)
python3 run_phase5.py
```

## File layout

```
criticality_tool/
├── README.md                   # this file
├── RESULTS.md                  # full methods, calibration, results
├── CRITICALITY_BRIEF.md        # original spec the tool was built against
├── CITATION.md                 # contact / how to cite
├── LICENSE                     # MIT
├── requirements.txt            # Python deps
│
├── pll_bank.py                 # PLL bank — CPU + CuPy GPU
├── intermittency.py            # dwell extraction, power-law MLE, Stern-Brocot depth
├── universality.py             # NNS / Σ²(L) / pair correlation / SFF + analytical refs
├── signal_gen.py               # ζ, GUE/GOE chirps, Poisson-FM null
│
├── run_full_sweep.py           # 3000-cell parameter sweep (Phase 0)
├── analyze_sweep.py            # post-process sweep_results.h5
├── run_zeta_phase2.py          # Phase 2 sanity on ζ
├── run_phase3.py               # Phase 3 NNS / Σ² / SFF
├── run_decisive.py             # 1000-zero × 300 s headline run
├── run_controls.py             # selection-bias + time-reversal controls
├── fix_gue_generator.py        # diagnose + fix the GUE generator (R = 2 issue)
├── run_calibration.py          # GUE/GOE chirp calibration
├── run_envelope_diagnosis.py   # chirp envelope at fc=115.55
├── run_envelope_per_pll.py     # envelope across the full PLL bank
├── run_analytical_nns.py       # the calibrated metric (primary)
├── run_phase4.py               # cross-signal application — first batch
├── run_phase5.py               # cross-signal application — wider batch + EEG
│
├── tests/
│   ├── test_pll.py             # Phase 1 acceptance (single-PLL behaviour)
│   ├── test_pll_gpu.py         # GPU↔CPU parity
│   └── test_intermittency.py   # Phase 2 acceptance (RLE / power-law / Fano)
└── plots/                      # research figures (16 panels, see RESULTS.md)
```

The runner scripts each produce a section of the results in `RESULTS.md`.
They are idempotent (caching where useful) and can be re-run independently.

## External data (not included in the tarball)

These need to be downloaded separately:

- **Odlyzko ζ-zero tables**: `zeros1` (100k zeros) and `zeros6` (2M zeros)
  from <https://www-users.cse.umn.edu/~odlyzko/zeta_tables/>.  Place in
  `data/`.  Used by `run_phase5.py`.
- **PhysioNet EEG sample**: e.g. `S001R01.edf` from
  <https://physionet.org/files/eegmmidb/1.0.0/S001/S001R01.edf>.  Place
  in `data/`.

Or compute on demand via `mpmath.zetazero` for ζ zeros and the
generators in `signal_gen.py` for synthetic signals.

## Hardware

Tested on:
- CPU: Xeon-class 24-core (joblib parallel)
- GPU: NVIDIA RTX 4090 (CuPy 14.0, CUDA 12)

The PLL bank kernel (`pll_bank_gpu`) achieves ~968 M-PLL-samp/sec in
lock-only mode on the 4090.  CPU fallback works on any modern x86_64 host.

## License

MIT.  See `LICENSE`.

## Citation

See `CITATION.md`.

## Status

Research code.  The metric is calibrated; the headline ζ result is
robust across multiple zero-height regimes and consistent with the
random matrix theory conjecture.  See `RESULTS.md` §10 for known
limitations.

This codebase is the basis for an in-progress writeup.  Issues, patches,
and reproductions welcome.

# Arithmetic Resonance Spectrograph (ARS)

Most signal analysis tools ask "what frequencies are present?" This tool asks a different question: **what universality class of randomness does this signal exhibit?** It converts arbitrary sequences — zero heights, prime gaps, neural spike times — into a spectrum via Farey rational passage-time analysis, then classifies that spectrum against the predictions of random matrix theory (Poisson, GOE, GUE). The Farey PLL bank is the spectrograph; the RMT classifier is the readout.

A measurement instrument for dynamical level statistics of arithmetic signals. Built around a parallel Farey bank of phase-locked loops driven by chirp synthesis from a sequence of "frequencies" t_k (zero heights, prime gaps, random matrix eigenvalues, neural zero-crossings, ...).

The intended question: do the Riemann ζ zeros — and other arithmetic structures — exhibit the universality class of quantum chaos (GUE), and can that be detected through their FM coupling structure with a real instrument?

The answer found by this tool: **yes for ζ**. See RESULTS.md for the methods, calibration, and full cross-signal table.

---

## Headline result

Riemann ζ zeros' analytical passage-time NNS through the calibrated metric follows the Wigner GUE distribution, and the fit improves at higher zero heights as the GUE conjecture predicts:

| zeros sampled | n pooled spacings | KS to Wigner GUE |
|---|---|---|
| first 2,000 | 49,181 | 0.032 |
| first 100,000 | 1,845,065 | 0.015 |
| heights ≈ 1,100,000 (Odlyzko zeros6 high chunk) | 450,184 | 0.012 |

GUE eigenvalues, GOE eigenvalues, Poisson uniform, and a Poisson density control all classify to their predicted classes with KS ≤ 0.025 — the metric is calibrated.

The same instrument is also applied to primes (Cramér-asymptotic Poisson behaviour observed), Liouville function support, twin primes, Gaussian prime norms, and a sample of resting-state EEG θ-band zero-crossings. Full table in RESULTS.md §7.

### Secondary result: GUE→GOE projection theorem

A time-symmetric detector (the Farey PLL bank operating on lock-onset times) folds GUE statistics onto GOE statistics, quantified at ~0.13 KS shift. This is characterized analytically and confirmed experimentally. The measured NNS reports GOE; the underlying eigenvalue statistics are GUE. See RESULTS.md §6.5.

---

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

- **Measured**: chirp → PLL bank → lock-onset NNS. Subject to instrument bias (folds GUE → GOE through time-symmetric peak detection; see RESULTS.md §6.5).
- **Analytical**: t_k list → passage-time NNS via PLL selection function. Bypasses chirp/PLL dynamics; this is the calibrated primary metric.

---

## Quickstart

```bash
# Install dependencies (CuPy optional but recommended for GPU)
pip install -r requirements.txt

# Fast demo: classify ζ zeros + GUE/GOE/Poisson controls
# Uses first 2000 zeros from mpmath (synthesized in ~30s)
python3 run_analytical_nns.py

# → Wigner GUE classification of ζ, KS = 0.034 at n = 18,529 spacings

# Full survey — primes, twin primes, Liouville, Gaussian prime norms, EEG
# (requires external data, see below)
python3 run_phase5.py
```

For the large-scale results (n = 1.84M spacings), download the Odlyzko tables first — see External data below.

---

## File layout

```
criticality_tool/
├── README.md                   # this file
├── RESULTS.md                  # full methods, calibration, results
├── CRITICALITY_BRIEF.md        # original spec the tool was built against
├── CITATION.cff                # machine-readable citation
├── LICENSE                     # AGPL-3.0-or-later
├── requirements.txt
│
├── pll_bank.py                 # PLL bank — CPU + CuPy GPU
├── intermittency.py            # dwell extraction, power-law MLE, Stern-Brocot depth
├── universality.py             # NNS / Σ²(L) / pair correlation / SFF
├── signal_gen.py               # ζ, GUE/GOE chirps, Poisson-FM null
│
├── run_analytical_nns.py       # calibrated primary metric (start here)
├── run_full_sweep.py           # 3000-cell parameter sweep
├── run_zeta_phase2.py          # Phase 2 intermittency on ζ
├── run_phase3.py               # NNS / Σ² / SFF
├── run_decisive.py             # 1000-zero × 300s headline run
├── run_controls.py             # selection-bias + time-reversal controls
├── run_calibration.py          # GUE/GOE chirp calibration
├── run_envelope_diagnosis.py   # chirp envelope analysis
├── run_analytical_nns.py       # the calibrated metric (primary)
├── run_phase4.py               # cross-signal — first batch
├── run_phase5.py               # cross-signal — wider batch + EEG
│
├── tests/
│   ├── test_pll.py             # Phase 1 acceptance
│   ├── test_pll_gpu.py         # GPU↔CPU parity
│   └── test_intermittency.py   # Phase 2 acceptance
└── plots/                      # research figures (16 panels, see RESULTS.md)
```

Runner scripts are idempotent and can be re-run independently.

---

## External data

Not included — download separately and place in `data/`:

- **Odlyzko ζ-zero tables**: `zeros1` (100k zeros) and `zeros6` (2M zeros) from https://www-users.cse.umn.edu/~odlyzko/zeta_tables/
- **PhysioNet EEG**: e.g. `S001R01.edf` from https://physionet.org/files/eegmmidb/1.0.0/S001/

Or compute ζ zeros on demand via `mpmath.zetazero` — the quickstart demo uses this path.

---

## Hardware

Tested on:
- **CPU**: AMD Ryzen 9 5900x 24-thread (joblib parallel)
- **GPU**: NVIDIA RTX 4090 (CuPy, CUDA 12)

The PLL bank GPU kernel achieves ~82M PLL-samples/sec on the 4090. CPU fallback works on any modern x86_64 host.

---

## License

AGPL-3.0-or-later. See LICENSE.

---

## Citation

See CITATION.cff. If you use this tool in research, please cite it — it helps establish provenance for the metric.

---

## Status

Research code. The metric is calibrated; the headline ζ result is robust across multiple zero-height regimes and consistent with the random matrix theory conjecture. See RESULTS.md §10 for known limitations.

This codebase is the basis for an in-progress writeup. Issues, patches, and reproductions welcome.

---

## Related work

The connection between phase-locking, the Riemann zeta function, and prime number theory has been developed analytically by M. Planat and collaborators (FEMTO-ST, 2002–2026). This tool provides a complementary empirical approach: rather than deriving the arithmetic structure of PLL noise analytically, it uses the Farey PLL bank as a measurement instrument applied to external signals.
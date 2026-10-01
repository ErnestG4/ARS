# Arm B (exploratory) — multifractality of bulk singular vectors: IMPRESSIONS, no verdicts

**Scope (Will, 2026-10-01):** exploratory, split-sample. Read: pythia-1.4b and PolyPythias 410M seeds 1–5 (26 checkpoints
each). UNREAD and untouched: seeds 6–9, pythia-410m (standard), 1B, 70M, every Arm B run. Nothing here is a test; every
number is paired with its norm-preserving null (G = c·D_r Z D_c, one draw per matrix) and with the exact Haar expectation.
Generators: `stage3_extract_mf.py` (banked on spot, `~/llmspec_mf/cache/mf`, 40 GB) → `mf_explore.py` →
`results/mf_explore/` (CSV tables, SUMMARY.md and figures committed; the per-model JSON, 34 MB, is kept locally and on spot).
Statistic: M_q = Σ|ψ_i|^{2q} per unit singular vector, band-mean, reported as log(trained / null) with the null's and the
trained value's ratio to E_Haar[M_q](n). Bands by singular-value index: spike [0, 32), then octaves [32, 64), … .

## 1. Sanity
- Step 0: every band, side, matrix, q: log(trained/null) = 0.0, trained/Haar = 1.00, box departures 0. The pipeline reads a
  random matrix as random (figures fig_a / fig_b, lightest curves; CSV rows step0).

## 2. The bulk octaves are Porter–Thomas-like, throughout training
- Octaves [32, 512) from the spike edge, q = 4, step 143000, max |log(trained/null)| over the six octaves:
  1.4B — V u/v 0.22/0.09, O u/v 0.08/0.19, MLP_IN v 0.11, MLP_OUT u 0.70, K u/v 1.18/2.24, Q u/v 3.90/1.58; 410M seed
  mean — V 0.14/0.12, O 0.20/0.30, MLP_IN v 0.09, K 0.50/0.15, Q 3.09/1.49. The larger Q/K values sit in the [32, 64)
  octave next to the spike (and are NEGATIVE: trained less concentrated than the null, whose vectors follow the row-norm
  profile).
- Reading (impression): bulk singular vectors look delocalised/Porter–Thomas on both sides. As declared in advance, this is
  what BOTH "smooth distributed function" and "no function" predict; it supports neither and refutes only "localised".

## 3. The deepest octave of the MLP matrices, on the NEURON side, localises late in training
The band of smallest singular values (1024–2048 at 1.4B; 512–1024 at 410M), hidden (neuron) index: MLP_IN left vectors
(u, n = 8192 / 4096) and MLP_OUT right vectors (v).

| | MLP_IN u | MLP_OUT v |
|---|---|---|
| 1.4B, log(trained/null), q = 4, step 143000 | **+8.9** (trained/Haar 7.7e3, null/Haar 1.02) | **+7.4** |
| 410M seeds 1–5, same, mean ± sd | **+5.5 ± 3.2** | **+4.2 ± 2.5** |
| the NEXT octave up (512–1024 / 256–512) | +0.1 / +0.07 ± 0.07 | +0.1 / +0.10 ± 0.09 |

- Timeline (MLP_IN u, 410M, per seed): 0.0 through step 4000; +0.2…0.5 at 6000; +1.4…2.6 at 8000; +3…4 at 12000; +5…7 by
  32000–64000; seeds 1, 2, 5 end at +6.9 / +6.9 / +8.0. 1.4B: 0 → +1.1 (8000) → +3.1 (32000) → +8.9 (143000).
- **Seeds 3 and 4, the two PolyPythias runs with late loss spikes (3: 64k–96k; 4: 96k–128k), lose it:** seed 3 drops
  from 6.1 (64000) to 2.7 (96000), recovers to 5.5; seed 4 drops from 8.4 (96000) to **0.0 at 128000 and 143000** — the
  bottom of its MLP spectrum reads as random after the spike. (A natural experiment for open lead 6; impression only.)
- q-dependence at 1.4B, MLP_IN u, deepest band, step 143000: q = 1.5: +0.01; q = 2: +0.11; q = 3: +3.2; q = 4: +8.9. The
  low moments barely move while the high ones explode: a SMALL subset of vectors/entries carries it, i.e. the band mean
  is dominated by a few strongly localised vectors, not by mild localisation of all of them (band-mean M_4 ≈ 1.5e-6 at
  n = 8192; a vector uniform on k entries has M_4 = k^{-3}).
- The null preserves every neuron's norm and stays at Haar (null/Haar 1.02), so this is NOT neuron-norm heterogeneity
  (dead or tiny neurons would show in the null).
- The same band on the RESIDUAL side of MLP_OUT (u) goes the other way at 1.4B (−3.1: the null's row-norm profile makes
  localisation the trained matrix does not have); at 410M −0.5.
- Candidate readings, untested: (a) groups of near-collinear neurons (duplicated features) whose difference directions
  sit at the bottom of the spectrum and are supported on those neurons; (b) a subset of neurons with low-entropy input
  weights. Either would make the bottom of the MLP spectrum a place where "function" is concentrated rather than
  distributed — which matters for arm A's scale axis (below).
- Also at 1.4B only: V v (residual) +1.9 and O v (head-nested) +4.5 in the deepest band at the end (410M seed mean −0.2 ±
  0.6 and +0.2 ± 0.2): size- or seed-dependent; not an impression I would carry.

## 4. Head-nested side: no scale-dependent concentration beyond the norm profile
- Box moments at ℓ = 2 / 8 / 32 / d_head (fig_b): trained departures from exact finite-ℓ Haar are flat in ℓ (0.1–0.5 for
  the near-spike bands, ≈ 0 for the deep bulk) and SMALLER than the null's, whose ℓ-dependence (steeper) is the row-norm
  profile (rotary rows etc.). No kink at ℓ = d_head in any trained curve.
- Head-mass concentration (max_h μ_h from the 16-vector subsamples, 1.4B, step 143000): bulk octaves trained 0.08–0.14 vs
  null 0.08–0.13 vs Haar 0.077 — almost all of the head concentration in bulk vectors is the norm profile.
- Impression: in VECTOR statistics the bulk shows no head-scale structure. (CC's "head-scale knee" was a prediction about
  functional COST; this is a point against a vector-side counterpart of it.)

## 5. |ψ|² tails (fraction of entries with n·ψ² > 10; Porter–Thomas 1.56e-3)
- Head-nested sides (Q/K/V u, O v) rise 3–6× above PT after step ~1000, with the null tracking the trained curve (norm
  profile); residual sides stay at PT; MLP hidden sides: trained > null late (consistent with §3).

## 6. What this changes for arm A (design notes, not results)
- Include MLP_IN / MLP_OUT, and treat the DEEPEST octave on the neuron side as its own regime: it is not Haar-like, so a
  "self-similar across octaves" fit that includes it would be fitting a knee that vector statistics already show. The
  minimum-octaves rule should be evaluated on the Haar-like octaves ([32, r/2)) and the deep band reported separately.
- The norm-preserving null is the right reference for Q/K/V/O head-nested sides (where it absorbs most departures) and
  a poor one for the spike (its top vectors are artefacts of the row-norm profile: trained/null −5…−13 there).
- Nothing in §2–§5 bears on whether the Haar-like bulk carries smooth distributed function; that remains the functional
  test's question.

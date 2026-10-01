# llmspec/ — Shapes of LLM weights and transforms over training

Governing brief: CC Brief v1.1 (Will, 2026-09-25; supersedes v1). Will's answers to §8 (2026-09-25):
1. Stage 1 peak criterion = MP-calibrated KDE (sealed: seals/stage1_peak_criterion.json, stage1_calibrate.py).
2. Arm B (AdamW vs Muon) = HOLD.
3. Bulk NNS / <r~> beta=1 null = ADOPTED as a pre-registered instrument check (sealed before Stage 3).
Download budget: no cap (stream single tensors by HTTP range; remote_st.py).

Brief corrections found at execution (G4): Pythia `stepN` revisions store F32 safetensors (only `main` is F16);
OLMo 2 1B checkpoints are stored F32, not bf16. Whether the F32 values sit on an fp16/bf16 grid is measured per
tensor (specs.grid_audit) and reported with every result.

Interrupt: `touch llmspec/STOP` (clean exit between tensors). Resume: rerun the same command (per-layer cache).

## Bulk-vector arm — scope (Will, 2026-10-01, verbatim)

> A. SEALED: spectral-scale self-similarity of bulk function.
>    k-sweep (geometric), perturbations matched on ‖δW·X‖, antithetic ±δ;
>    power vs broken vs cutoff by likelihood ratio; exponent vs calibrator's;
>    red path (plant uniform / self-similar / characteristic-scale) must
>    classify correctly before sealing; minimum-decades rule sealed.
> B. EXPLORATORY (impressions, no verdicts): multifractality of bulk
>    singular vectors.
>    |ψ|² distributions vs Porter–Thomas; τ(q), q∈[0.5,4]; head-nested
>    box-counting for output-side vectors; size scaling for residual-side.
>    Null preserves row/column norms. Across training time (step 0 = sanity)
>    and across bulk position.
>    Split-sample: explore on 1.4B + PolyPythias seeds 1–5 only; seeds 6–9
>    and other sizes stay unread for any later sealed test.
> Shared: co-adapted random-bulk calibrator

**Operating notes (CC, 2026-10-01).**
- The held-out set is read conservatively: pythia-410m (standard), pythia-1b, pythia-70m and every Arm B run are
  UNREAD for bulk-vector statistics until a sealed test names them, as are seeds 6–9.
- Banked per-vector IPR / Porter–Thomas KS (cache/s3/<run>/<step>/L*.npz, `ipr_*`, `pt_*`, one scalar per singular
  vector) count as bulk-vector statistics: readable on 1.4B + seeds 1–5 only.
- |ψ|² distributions, τ(q) and box-counting need the vectors themselves; only the top 32 are banked, so arm B needs
  a GPU re-extraction pass on 1.4B + seeds 1–5 (after A0r), banking bulk-vector subsamples + moments, and the
  row/column norms for the profile-preserving null.
- Arm A's calibrator and red-path plants need training: last in Will's GPU order (A0r → Q4 extension + third Muon
  seed → calibrator).

### Arm A corrections (Will, 2026-10-01, later the same day)
- **Scale axis flaw (Will's own):** "random bulk subspaces of size k" cannot discriminate — a uniform perturbation over a
  random k-subspace at fixed size costs the bulk-average curvature for every k, under every hypothesis.
  - **Self-similarity across spectral scale → perturb spectral BANDS:** octave bands of the bulk by singular-value index,
    [2ʲ, 2ʲ⁺¹) counted from the spike edge; read per-direction cost vs spectral position. Power law across octaves =
    self-similar; knee = characteristic scale.
  - **Smoothness → the random-subspace sweep is kept, but reads the DISPERSION across random subspaces of the same k:**
    smooth distributed function gives low dispersion falling as 1/k; concentrated function gives high, lumpy dispersion.
- **Matching conflict:** matching on ‖δW·X‖ divides out the input-projection factor ‖vₖᵀX‖², which is where CC predicts
  any data-imprinted self-similarity would live. **Report three things per band:** (1) the input-projection profile
  ‖vₖᵀX‖ across octaves vs the calibrator; (2) the output-matched cost (output-side curvature); (3) the raw size-matched
  cost (the product). Caution: LLM activation covariances already have power-law spectra, so a power law in (1) is not new
  by itself — the question is whether the trained bulk directions align with that structure MORE than the calibrator's.
- **Decisions:** arm-B re-extraction runs on spot's CPUs (not beside A0r); held-out set CONFIRMED (explore on 1.4B +
  seeds 1–5; seeds 6–9 and other sizes unread); prediction figure + prereg skeleton with decision regions per panel
  (including CC's head-scale knee) BEFORE any arm-A code.

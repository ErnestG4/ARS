# Track 0 — Regression Gate · Configuration Justification

**Authored before execution** (brief non-negotiable). Phase 36 (Torus-Breakdown Extension).
Date: 2026-05-31.

## Purpose
Confirm banked verdicts reproduce *before* any new substrate touches the instrument. If any
banked verdict fails to reproduce within tolerance → STOP, diagnose drift, do not proceed to
Tracks 1–4.

## What the gate re-runs, and why at these configurations

The AM regression path (`am_eigs` → `unfold_rotnum` → `joint_q_profile` →
`joint_quadrant_diagnostic` / `characterize_transition`) is **deterministic**: golden-mean θ,
fixed phase φ, deterministic tridiagonal eigensolve, deterministic Sturm/rotation-number count.
There is no RNG anywhere in the AM leg. Two probe cells (λ=0.5, λ=1.05 at the banked
N=2584 / L=10⁶ config) reproduced the banked JSON values to 5 decimal places **bit-exact**
before this gate was authored. Determinism + bit-exact reproduction means a full re-run of the
expensive original sweeps is not required to detect drift — any code drift would perturb the
N=2584 cells, which are cheap (~14 s/cell). Therefore:

| Item | Config | Cost | Rationale |
|---|---|---|---|
| 1. IDS-unfold leg ratio-free | N=2584, L∈{10⁵,10⁶}, λ=0.5 | ~30s | Re-confirm bit-exact reproduction + the §5 ratio-invariance property: unfolded W1δ stable across L_iter (≥1 decade), and structurally no N_ref in `unfold_rotnum` (the leg's only error parameter is L, decoupled from N). |
| 2. Zoo-gap ratio-clean | N=2584, λ=0.5 vs 1.5, fixed ref | ~30s | Re-confirm the sub-vs-sup W1δ contrast at fixed cell-N / identical ratio — a contrast a ratio-function cannot produce at fixed ratio (banked: real substrate difference, ≥6×). |
| 3. 35b no-false-positive | full `run_35b_diagnostic.run()` — 8 signal λ + 8 α-null φ, N=2584 | ~4 min | Cheap enough to re-run in full. Confirm: all signal+null = BR_artifact (NO quadrant flip), signal rep_med drifts (≈0.847→0.674 across λ=1) while α-null rep_med stays flat. The banked NFP verdict is quadrant-level at N=2584. |
| 4. Sensitivity floor N≳5×10⁴ | confirmatory points N=50000, λ∈{0.5,1.5}, φ=0 | ~4 min | The original floor was a ~20-point dense-in-log-N sweep up to N≳5×10⁴ (multi-hour, the original phase-35a overnight compute). Re-running it wholesale as a *gate* is wasteful given determinism. Instead: re-run one high-N point each side and confirm the floor persists (sub→floor W1δ≪sup, gap ≥ max spread). N=50000 sub already reproduced W1δ=0.00052 (floor) in the timing probe. |
| 5. Logistic + Mackey-Glass loci | banked-locus Lyapunov-sign re-check | ~1 min | Re-confirm transition-locus detection: logistic r=3.7 (chaos, λ₁>0) vs r=3.83 (period-3 window, λ₁<0); Mackey-Glass τ=23 (chaos, λ₁>0) vs τ=10 (periodic, λ₁≈0). Family-V Benettin/finite-difference Lyapunov is the validated tool for known-equation substrates. |

## Pass criteria (pre-registered)
- **(1)** L-swing in unfolded W1δ ≤ ~1× the φ-ensemble sampling SE (banked ~5×10⁻³ scale at sub);
  and `unfold_rotnum`/`ids_rotnum` contain no N_ref term (structural). → `IDS_LEG_RATIO_FREE`.
- **(2)** sub W1δ and sup W1δ disjoint by ≥6× at fixed N/ref. → `ZOO_GAP_RATIO_CLEAN`.
- **(3)** every signal and null cell classifies BR_artifact (no flip) AND signal rep_med
  monotone-ish drop through λ=1 while α-null rep_med flat (spread ≪ signal drop). → `NFP_VALIDATED`.
- **(4)** at N=50000: sub W1δ ≪ sup W1δ with gap ≥ max(sub_spread, sup_spread) order-of-magnitude
  (banked gap/sup-spread ≥ 2). → `SENSITIVITY_FLOOR_PRESENT`.
- **(5)** Lyapunov signs match banked at all four loci. → `DYNAMICAL_LOCI_REPRODUCED`.

**Overall PASS** = all five reproduce within the margins above. Any FAIL → HALT, do not enter Tracks 1–4.

## Out of scope / seams left open (do NOT close here)
- §3-(A) `S3A_REDUCED` (analytic anchor constructible, not closed) — untouched.
- The NFP-N (2584, quadrant) vs sensitivity-N (≳5×10⁴, sub-quadrant) resolution: per
  `SEAM_CLOSURE_FINDINGS` this was reported **closed at the use regime** (both halves cohere at
  N≳5×10⁴). The gate reproduces that closure; if it does not, flag — do NOT silently re-open.
- No-false-positive N and sensitivity N remain tracked as **separate** numbers.

## Engine attribution note
The AM transition is read on the **NNS/spacing axis** (`rep_int_q` → rep_med drift; W1δ). The
Ramanujan-Fourier axis (`rf_amplitude_q`) is computed by `joint_q_profile` but the AM transition
does not load on it (no RF spike — AM is not periodic-at-q). This per-axis attribution is recorded
and carried forward as the template for Track-1 calibrator engine-attribution.

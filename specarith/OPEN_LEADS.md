# specarith — open leads (descriptive; no verdicts)

Listed together at Will's instruction (2026-10-08), **not merged**: each was found on its own data with its own
statistic, and any connection between them is a hypothesis for a future sealed test, not a finding.

## L1 — low-height excess of the gap ratio ⟨r̃⟩ above GUE
- First 3·10⁴ zeros: ⟨r̃⟩ = 0.6129 (thirds 0.6147 / 0.6121 / 0.6120), **+8.5 SD** above the matched-size GUE band
  (W = 3·10⁴, mean 0.59991, SD 0.00153; `ph6/results/preread61/redpaths61.json`).
- Earlier, independently: ARS-RH Phase 1 resolved the same excess and its fall with height (+0.012 at γ ≈ 5·10³,
  +0.008 at 3.7·10⁴, +0.006 at 1.4·10⁵ against the surmise reference; +0.003 more against large N —
  `arsrh/PHASE1_FINDINGS.md` and its 2026-10-08 erratum).
- Context: Nishigaki (2025) finds the ⟨r̃⟩ CUE_N correction O(N⁻⁴) (the O(N⁻²) term cancels) and the ζ deviation
  ∝ N_e^{−3.08} (fitted) — `ph2/lit/NEXT_ORDER_LIT.md` §2.4.

## L2 — Phase 2: the zeros' spacing law sits closer to the sine kernel than CUE(N_eff) predicts
- κ̂ > 1 in all 8 resolvable bins, falling with height (SECONDARY 1.21 → 1.045 for N_eff 2.3 → 5.1); post hoc,
  (κ̂ − 1)·N_eff² ≈ const (SECONDARY 1.14–1.33); κ̂ depends on the fit window; against exact CUE(N_eff) the zeros move
  the other way from CUE's own higher-order terms (PRIMARY) — `ph2/PH2_FINDINGS.md` §3–§4,
  `ph2/results/run/CUE_EXACT_COMPARE.md`. Below N_eff = 2 (descriptive): κ̂ keeps rising as N_eff falls
  (`ph2/results/lowheight/LOWHEIGHT.md`).

## L3 — CS08's long-range four-point connected function does not decay (descriptive; twenty-fourth round)
- The assembled non-oscillating long-range C(r) of the Stage 2 statistic (pair bump (0.5, 0.3)) is almost periodic,
  with RMS 0.053 constant from r ≈ 20 to 4.8·10⁴ spacings at ℓ = 16.50. Its 2000-spacing block means are ±5·10⁻⁵. Only
  the sine-kernel part decays. Source: `cs4/diag_wincov_edge.py`, `cs4/GS_ZETA_RESULTS.md` §5.

## L4 — neighbouring windows of the zeros are anti-correlated; GUE's are not (seen data; descriptive)
- Lag-1 correlation of the tapered window sums (b = 100, centres 3b apart):
  - F1, all six bins: −0.03 to −0.04 (n ≈ 2·10⁴ each; about 5σ per bin);
  - Stage 1 GUE: ≈ 0;
  - CS08's prediction: −0.031 to −0.034.
- Source: `cs4/diag_f1_wincorr.py`, `cs4/results/diag_wincov/`. Not a test: F1 is seen data.

## L5 — does CS08 explain Coram–Diaconis's lag-1 anti-correlation (−0.2)?
- CD (2000 report; `ph2s/lit/PAIRSUM_VARIANCE_LIT.md` §1.8) found −0.2 between consecutive blocks' values of
  |Σ_j e^{iθ_j}|². Their blocks are n = 42 zeros, sharp and adjacent, each rescaled to its own length.
- To do: the theory's ρ₁ in their configuration, with the per-block-rescaling effect measured separately on GUE
  (Will's caution: rescaling alone anti-correlates neighbours in any rigid sequence). If the GUE part accounts for
  −0.2, CS08's arithmetic part is what is left to compare.
- **First step done (2026-10-10, descriptive; F1 is seen data): `ph2s2/cd_lag1.py`, `ph2s2/results/cd_lag1/`.**
  - **GUE does not do it.** On the Stage 1 GUE sequences (16 × 10⁶ unfolded levels, a long rigid sine-kernel
    sequence), CD's construction with own-length wrapping gives ρ₁ = +0.00 to +0.04 for every n = 4…64 (SE ≈ 0.002).
    Unit-length wrapping gives +0.01. So per-block rescaling plus rigidity does **not** produce −0.2.
  - **The zeros do.** On F1 with CD's rule n = ⌊ℓ⌋, ρ₁ = −0.23 to −0.27 in all six bins (SE 0.0017), against CD's
    −0.2 ± 0.03 at ℓ ≈ 42.
  - **ρ₁ is a function of u = ℓ/n alone.** u is the frequency, in t, that the block-scale mode e^{2πiΔ/n} probes; the
    block is one period, 2π/u in t. F1b (ℓ = 15.47) and F1x (ℓ = 22.10) fall on one curve:

    | u | ≈ 1.0 | ≈ 0.7 | ≈ 0.55 | ≈ 0.45 | ≈ 0.38 | ≈ 0.35 |
    |---|---|---|---|---|---|---|
    | ρ₁ | −0.24 to −0.26 | −0.32 to −0.37 (minimum) | ≈ 0 | +0.55 (peak) | ≈ 0 | +0.2 (second peak) |

    At n = 42 on F1 (u ≈ 0.35–0.53) it therefore swings from +0.10 to +0.54.
  - **Bearing on the twenty-second-round novelty wording:** it says CD's −0.2 "may be a generic rigidity effect". On
    this evidence it is not; it is arithmetic in origin. Wording change: Will's call.
  - **Still to do:** the theory curve ρ₁(u) from CS08 (or the explicit formula) in CD's configuration.

## Status
L1 and L2 have no theory-fixed prediction yet. The routes in progress: the R₂ phase (`ph2r2/`, pair correlation with
the arithmetic lower-order terms, fresh heights) and the Conrey–Snaith next-order spacing project
(`ph2/SCOPE_CS_SPACING.md`, GO after the R₂ seal).

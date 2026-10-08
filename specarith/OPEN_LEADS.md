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

## Status
Neither lead has a theory-fixed prediction yet. The routes in progress: the R₂ phase (`ph2r2/`, pair correlation with
the arithmetic lower-order terms, fresh heights) and the Conrey–Snaith next-order spacing project
(`ph2/SCOPE_CS_SPACING.md`, GO after the R₂ seal).

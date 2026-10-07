# specarith — running notes (spectral–arithmetic programme)

Worktree `.claude/worktrees/ph6-xp`, branch `ph6-xp` (from main 94f32da). Order (Will, 2026-10-07): Phase 6 gates
(6.0, G0–G4) → Phase 2's first item (CUE(N_eff)) → the 6.1 candidates → Phase 1 (may run alongside on spot) → rest.
Briefs and decisions: `cc-brief-ars-spectral-arithmetic-v1.md`, `ph6/PH6_BRIEF_v1.md`, `ph6/PH6_DECISIONS_2026-10-07.md`.
Inputs: `DATA_MANIFEST.md`.

## 2026-10-07

- Worktree created; briefs and both rounds of Will's decisions filed (0092955, a1cb9f2); data manifest (2eced53).
- Primary-source fetch for Phase 6 dispatched to three agents (explicit formulas; Selberg incl. desymmetrised +
  Mayer; xp candidates incl. BBM disputes and the dilation BC). Reports land in `ph6/lit/`; nothing is sealed yet.
- spot: new conda env `specarith` (python 3.12; numpy 2.4.5, scipy 1.17.1, mpmath 1.4.1; pip cypari2 2.2.4 =
  PARI 2.17.2, the same PARI as the local WSL venv). The `ars` env was not touched. Logged in spot's ~/claude-work.log.
- PARI timing on spot (lfunzeros, chi_-4 = lfuncreate(-4), realprecision 38): T=250: 162 zeros 1.6 s; T=500: 379
  zeros 4.7 s; T=1000: 868 zeros 18.5 s (≈ T² scaling) → ~10⁴ zeros (T ≈ 10⁴) in the order of half an hour.
  First zero 6.020948904697596655.

## §0 slot checks (read 2026-10-07; for Phase 1, not acted on)

- RESULTS §7.ter.1: "87 curves … ~280 zeros per curve" but "748,013 pooled spacings" — 87 × 280 ≈ 24k. One of the
  two numbers does not belong to this dataset, or "pooled spacings" means something other than adjacent spacings.
  Unresolved; check `run_lmfdb_family.py` before Phase 1 reproduces §7.ter.1.
- RESULTS §7.ter.3: "~6,400 zeros each, 4.05M pooled spacings" for 630 characters, but the stored
  `data/dirichlet_zeros.json` holds 114–238 zeros per character, to height ≈ 200. Same question.
- RESULTS §7.ter.3 Σ²(L=20): EC L-functions 1.78 (above GUE ≈ 1.05) while every other arithmetic family is sub-GUE;
  unexplained in the record.
- §0's "KS ≈ 0.94" (§7.ter.1.bis, conductor-normalised γ₁) and "630 primitive characters (92 real)" match the record.
- arsrh Phase 1 never compared the ζ height crossover with CUE(N_eff) (it names Bogomolny but asserts no law) →
  programme Phase 2's first item is live.

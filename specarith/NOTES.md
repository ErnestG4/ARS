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

## §0 slot checks (2026-10-07; first pass read the RESULTS prose only — corrected the same day from the result files)

Checked against `data/*_results.json`, the zero files and the generating scripts (Will asked: memory or results files?).

1. **RESULTS §7.ter.1 "748,013 pooled spacings" — CORRECT; my first-pass flag was wrong.** `lmfdb_results.json`
   aggregates n = 748013; per-curve n_zeros at height 200 total 24,789 (median 289), n_plls = 32 for every curve.
   "Pooled" = spacings of the analytical passage-time NNS pooled over 32 Farey-frequency PLL bands
   (`run_lmfdb_family.py:66-85`), not adjacent zero spacings. I had read "pooled spacings" as adjacent spacings.
2. **Data-file defect (new):** `data/lmfdb_zeros.json`, `data/lmfdb_zeros.json.bak_h200` and
   `data/lmfdb_zeros_h1000.json` are byte-identical (sha256 60c13ae9…), all height-1000 zeros (median 1,955/curve).
   The file named `.bak_h200` is not a height-200 backup; `run_lmfdb_extend.py` output replaced the height-200 list.
   Recoverable: truncating at γ ≤ 200 gives exactly 24,789 zeros, the §7.ter.1 count. Scripts that read
   `lmfdb_zeros.json` now get height-1000 data (`run_lmfdb_edge.py` uses only the lowest zeros, so §7.ter.1.bis is
   unaffected in substance; a re-run of §7.ter.1 would not reproduce without truncation).
3. **RESULTS §7.ter.3 "~6,400 zeros each" — WRONG in the prose.** `dirichlet_results.json` n = 4,051,472 is the
   PLL-pooled sample (4,051,472 / 630 = 6,431 per character); the characters have 114–238 zeros each (median 222,
   height 200). The pooled count was mislabelled as a zero count.
4. **RESULTS §7.ter.3 Σ²(L=20) = 1.78 for EC L-functions (and the EC R₂ row) — UNFOLDING DEFECT.**
   `run_second_order.py:43-56` and `run_pair_correlation.py:35-40` unfold every L-function with the DEGREE-1 count
   (T/2π)(log(qT/2π) − 1). Elliptic-curve L-functions are degree 2: N(T) ≈ (T/π)(log(√N·T/2π) − 1). Measured on the
   height-200 zeros: mean unfolded spacing under the script's formula 0.725 (range 0.659–0.740); under the degree-2
   formula 0.999 (0.997–1.010). Dirichlet under the script's formula: 0.999 (correct, degree 1). So the EC rows of
   the Σ² and R₂ tables were computed at ~0.72 of unit density; "≈GUE log-growth ✓" for EC is not supported as
   computed. The passage-time NNS classification (§7.ter.1) normalises per band and is not affected by this.
   Not re-computed here (Phase 1 territory); correction is a RESULTS erratum for Will.
5. §0's "KS ≈ 0.94" (§7.ter.1.bis, conductor-normalised γ₁) and "630 primitive characters (92 real)" match the record.
6. arsrh Phase 1 never compared the ζ height crossover with CUE(N_eff) → programme Phase 2's first item is live.

## Odlyzko high-height tables (for programme Phase 2)

Tables are labelled by zero NUMBER, not height (upstream headers, read 2026-10-07):
- `zeros3`: zeros # 10¹²+1 … 10¹²+10⁴, γ ≈ 2.677·10¹¹; "accurate only to within 10⁻⁸".
- `zeros4`: # 10²¹+1 … 10²¹+10⁴, γ ≈ 1.442·10²⁰; "not guaranteed … probably accurate to within 10⁻⁶".
- `zeros5`: # 10²²+1 … 10²²+10⁴, γ ≈ 1.371·10²¹; same accuracy statement.
The brief's "around 10¹², 10²¹, 10²², 10²³" mixes index labels; in height the tables sit at ≈10^11.4, 10^20.2,
10^21.1. N_eff = log(E/2π)/√(12Λ) needs heights E. Files are stored as offsets from a base value given in the header.

## Overnight 2026-10-07 (Will 02:00: "run this as an overnight with a timer for yourself every 20 minutes until 8am. Use your best judgment and a review agent to navigate the work.")

**Scope = the seal's remaining pre-seal steps (PH6_SEAL_6.0.md status line, §9, §11), and nothing past the seal commit.**
The approved seal text says the red-path reachability result "is reported to Will before the seal commit", so the
seal commit and every gate run wait for Will in the morning. No gate statistic (S(τ) / C(τ) / c_n on G0, G0-s, G0-c,
G1, G2 data) is computed overnight; null draws, bands, tolerances and RHS-only quantities are pre-read and allowed.

Work list (mark each with time + commit):
1. χ₋₄ zeros, T ≤ 2·10⁴, realprecision 38, 128-bit via GP strings (cypari2 library calls are 64-bit — found 02:00);
   plus the realprecision-57 check on [0,1000] and [19000,20000]. On spot, tmux `claude`, out ~/tmp/claude/specarith/.
2. G1-pre: three class enumerations (reduced cycles; Mayer/Efrat CF cycles; PARI narrow class numbers) to t = 30.
3. Code: specarith/ph6/ primespec.py (statistics, readout), known_answers.py (RHS: ζ/χ, Selberg per sector, picket),
   nulls.py (GUE tridiagonal + Poisson, N̄⁻¹ map), bounds.py (ε(τ)), gates.py (verdicts, red paths; refuses to run
   without the seal JSON), verify_ph6.py (synthetic known answers + red paths on synthetic data only).
4. Independent REVIEW AGENT on the code vs the seal text (formulas, conventions, verdict rules) before any pre-read
   output is used; fix what it finds; second pass if needed.
5. Pre-read on spot: ε(τ) tables, null draws + bands at G0 / G0-c / G2 configurations, null known answers, red-path
   reachability table, design table → seals/PH6_SEAL_6.0.json (draft, uncommitted until Will).
6. Dry run on the disclosed pilot scale (T₀ = 60, σ = 6) through the full gates.py path.
7. Side (no data reading): programme Phase 2 literature fetch (BBLM 2006 N_eff and Λ; Bogomolny–Keating 1995–96)
   into specarith/ph2/lit/.
Morning: report to Will — reachability table, anything the review agent found, what is ready to seal.

Overnight log:
- 02:05 plan written; cron check-ins every 20 min to 07:47, morning report 07:57.

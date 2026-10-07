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
- 02:06 χ₋₄ zeros: 22 PARI jobs launched on spot (20 equal-cost chunks at p38 + check windows [0,1000] and
  [19900,20000] at p57; the top check window was narrowed from [19000,20000], which alone would cost hours at p57).
  One call over [0,20000] would take ~13 h (128-bit cost per unit height ~T^1.7), hence the chunks.
- 02:20 G1-pre (seal §9.2) PASS: `ph6/classes.py` → `ph6/results/g1pre_classes.json`. Hyperbolic t ≤ 30 and glide
  t ≤ 30 (58 rows): Gauss cycles = CF necklaces = PARI Σ h⁺ exactly; Σ log N(P0) CF = PARI to ≤ 1e-15. DISCLOSED: the
  first run FAILED on glide length sums (exactly ½ at every t) because CC's check used the hyperbolic factor 2
  (Lemma 2.10) for glides too; for det −1, N(T0) = ((t+√(t²+4))/2)² (BS07 (2.50)), so the factor is 1 (t = 1: 2 log φ
  = log ε₁). The RHS uses C(t)·log ε₁ from (2.39)/(2.40) directly and was never affected.
- 02:15 ph6lib.py committed. RHS verified WITHOUT data: reproduces the EF agent's 30-digit pilot identity values to
  ≤ 6e-14 (ζ and χ₋₄); Selberg RHS at τ = 0 matches the parity Weyl integrals to ~1e-4 (dropped O(1/r²) terms).
- 02:18 Review agent launched on ph6lib/preread/classes/chi4_zeros vs the seal (report → ph6/REVIEW_code_v1.md).
- 02:22 preread tables + gates.py + dry run committed (1f9d3f4). **Reachability finding for Will: at the sealed G1
  window (T₀ = 49.4, σ = 5.8) the elliptic terms are ~e⁻³⁶ (h is negligible near r = 0), so RP5 (elliptic ×2) is
  INAPPLICABLE in both sectors (ratio 1e-10) — G1 cannot test the elliptic weights Will's ladder names first.** A
  small-window G1 (like G0-s) would; that is an amendment for Will. Other reachability: every ζ smooth-term class
  fires in at least one G0-s window (pole only at (10,4); mirror only at (10,4), marginal 2.2× by upper bound).
- 02:24 null calibration draws launched on spot (G0-c, G2, G0; 100 GUE + 100 Poisson each, 16 procs).
- 02:24 check-in: χ₋₄ 20/22 PARI jobs done (2 low chunks running); null draws G0-c in progress (16 workers); review + Phase 2 lit agents running. Nothing new to commit.
- 02:35 Phase 2 lit (side item 7) DONE → `specarith/ph2/lit/bblm_bk.md` (agent report, unreviewed). N_eff =
  log(E/2π)/√(12Λ) CONFIRMED (BBLM eq. 19); Λ printed 1.57314 in BBLM, correct 1.5731510713… (BFM 2017; cite BFM).
  Lower-order terms come from BK PRL 77 (1996), NOT the Nonlinearity 1995/96 papers (brief attribution wrong).
  BBLM's α should be ᾱ = 2α − 1 if the N⁻³ term goes in the kernel (BFM 2017 footnote) — Phase 2 must fix this before
  reading. Data: BBLM compared at E = 2.5·10¹⁵ and 1.3·10²² — the 1.3·10²² set (index ~10²³) is NOT among Odlyzko's
  public tables (those stop at index 10²², height 1.37·10²¹): Phase 2's "10²³" needs a data source. Unfolding trap:
  Forrester–Mays eq. (1.1) density misprint (log(E/2πe) vs log(E/2π)) is ~2%, bigger than the whole 1/N² effect.
- 02:42 Will's Phase 2 decisions filed (ph2/PH2_DECISIONS_2026-10-07.md). Added overnight side items: 8. Phase 2 primary-source verification of ph2/lit/bblm_bk.md (agent; no zero data); 9. Platt's LMFDB zeros — which heights, how fetched, hashable? (scoping only, no statistics).
- 02:32 check-in: nulls G0-c and G2 DONE — null known answers PASS (GUE s/pred 0.90–1.15, Poisson 0.86–1.10; GUE <r~> 0.5998/0.5996, Poisson 0.3866); G0 nulls running; χ₋₄ 21/22 done (chunk [0,6594] still running, 25 min). Results copied back when G0 finishes.
- 02:58 Phase 2 verification (side item 8+9) DONE → ph2/lit/VERIFY_bblm_bk_and_platt.md: BBLM eqs. 16/19/24 VERIFIED; Λ = 1.573151071324955227…, Q = 2.315846384958803289… recomputed independently (exact prime-zeta series) = BFM to 2e-16; BFM footnote 5 (ᾱ = 2α − 1) VERIFIED, secondary model fully defined in BFM eqs. 4.3–4.6; the α/ᾱ slip is in BBLM's JOURNAL eq. 28, not arXiv v1. **For Will (4a): 'N_eff alone' and 'BBLM's own scale convention' are two different BBLM curves (eq. 24 includes α; 'N_eff alone' is their dashed comparison) — the prereg must name one or carry both.** Heights: public Odlyzko spans log(E/2π) 0.81–46.83 (not ~9–46); high tables have only 1e4 zeros at 24.48, 44.58, 46.83. Platt/LMFDB: all 1.04e11 zeros to height 3.06e10 (log(E/2π) ≤ 22.31), rigorous ±2^-102, bulk binary files with md5.txt (1.29 TB, range requests OK), CC BY-SA 4.0 — fills 9–22.3; nothing public in 24.5–44.6. BK PRL full text unreadable (paywalled; quote the formula from BBLM eqs. 9–12 / Les Houches eq. 57).

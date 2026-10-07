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
- 03:00 Review fixes committed (3992fd2). Amendment proposals A3–A11 written (PH6_PROPOSED_AMENDMENTS.md) with EMPIRICAL bands: G0-c R = 24/34 ⊇ M (sealed [22,30] MET — the review's B2 prediction of ~21 did not materialise); G2 R = 15/28, 9 ∉ R (log-9 sign arm not scoreable at T = 2e4 — A4 options: keep and report NOT RESOLVABLE, or T = 4e4 with contingency zeros computing); sealed null known answer FAILS literally (√2; median 1.41) and per-n even with the LS prediction (2–4 n of 89 outside 20% = sampling noise) → A5; ⟨r̃⟩ in the arsrh band (0.5998/0.5996). preread v2 tables running locally; G0 nulls + χ₋₄ last chunk + contingency on spot.
- 02:52 check-in: preread v2 FOUND A BUG — negative tolerance at G0-s (40,3): local grids at small σ reach τ < 0 (log 2 − 3/σ) and the bounds used τ, not |τ|. Fixed in ph6lib/preread/gates (|τ| everywhere a bound uses τ); preread v3 rerunning. Spot: χ₋₄ 21/22 (chunk [0,6594] still running), contingency 13/41, G0 nulls running. Second review agent running.
- 02:55 G0 nulls DONE: R = 29/34 (not 16,27,32,64,81) ⊇ M; null known answers as G0-c/G2 (literal FAIL median 1.36–1.40; LS median 0.96–0.99, 2 n outside 20%); ⟨r̃⟩ 0.5999 in band. All three null configurations banked in results/preread/.
- 03:17 χ₋₄ v1 (default divz 8) merge FAILED its count assertion: 26,893 zeros vs MV 14.5's 26,903.37. Cause: lfunzeros' default sampling MISSES CLOSE ZERO PAIRS — the 4 widest gaps (3.0–3.5 mean spacings) each hid a pair 0.016–0.07 apart (found with divz 64); divz 16 still misses the closest, divz 32 finds all. Contingency [20000,40000] (divz 8) stopped. v2 recipe (chi4_zeros_v2.py: divz 64, cost-balanced 40 chunks, Turing-style S-block check + count + min-gap assertions) launched on spot (34 parallel). Second review (REVIEW_code_v2.md) committed: no new BLOCKER; N1 (signed τ) already fixed; minors to apply next.
- 03:20 REVIEW_code_v2 minors applied (1fc3552): bounds (both lines, |τ|, pairwise sums, provable Selberg tail), ε > 0 asserts, fail-closed RP4/RP17, rulings per sealed rows (G0-c, G3-c), A4(a) marked PROPOSED, shared picket tolerance, nulls ≤ 100 guard, ⟨r̃⟩ per draw, cross-reading margins. Dry run + ruling unit tests pass. A12 wording items added to proposals. Stale preread v3 stopped (note: a pgrep -f kill loop matched its own shell again — use explicit PIDs). Final pre-read waits for χ₋₄ v2 (divz 64) on spot.
- 03:21 check-in: χ₋₄ v2 running (2/42 done, 34 active, ~45 min expected). Wrote make_seal_json.py (pins text, code, inputs and every pre-read output; refuses without --decisions or with missing outputs) — tool only, not run.
- 03:31 check-in: χ₋₄ v2 3/42 done, 34 running (15 min in). Nothing else unblocked; the [20000,40000] contingency (divz 64) will start when the base run frees cores.
- 03:52 check-in: χ₋₄ v2 base 34/42 done (0 failed), 8 running. Contingency [20000,40000] relaunched at divz 64 (50 chunks, 24 parallel; chi4_zeros_v2 plan/launcher take T_LO).
- 04:16 χ₋₄ v2 (divz 64) COMPLETE and verified: 26,903 zeros (smooth 26,903.37, dev −0.374), S-block means within ±0.003, min gap 0.0161, p57 agreement 5.5e-34 → δ_χ = 1e-30; sha256 285222a0…3550 in DATA_MANIFEST. FINAL pre-read in results/preread (tables incl. G2, nulls, design, known answers; RP17 reach 10.5): all ε > 0; G2 RP10 reachable (2.8e9), RP11 INAPPLICABLE (as review M3 predicted → A6). Everything the seal JSON pins now exists; seal waits for Will's decisions.
- 04:17 synth_run.py started locally: full-size crash/timing test of the sealed gate code (G0, G0-s, G0-c, G2, G1) on SYNTHETIC GUE/uniform levels (seeds 7000+) with the real pre-read tables; G3/G3-c and G4 (sealed objects) not run. Output dry_out/synth_run.json.
- 04:32 synth_run DONE: every sealed code path (G0, G0-s ×3, G0-c, G2, G1 even/odd, red paths, Layer B rulings, fail-closed reachability) completes at full size on synthetic spectra; timings G0 340 s, G0-c 104 s, G2 101 s, G1 15 s, G0-s ~5 s. Layer A FAILs on synthetic levels as it should (a GUE spectrum does not satisfy ζ's explicit formula). Contingency χ₋₄ [20000,40000]: 24/51.
- 04:52 check-in: χ₋₄ contingency [20000,40000] 49/51 done (0 failed). Launched CONTINGENCY null draws for proposed A4(b) (G2 at T = 4e4: T0 20000, σ 2352.9; 100 GUE + 100 Poisson) on spot into preread_A4b — gives Will the measured R (incl. whether 9 ∈ R) before he chooses; not sealed.
- 05:02 χ₋₄ contingency merged to [0,40000]: 58,220 zeros (smooth 58,219.33, dev +0.666), S-blocks ±0.004, min gap 0.0089 (divz 64 margin was needed), p57 6.3e-34 → δ 1e-30; sha256 8f134679…01be in DATA_MANIFEST. A4(b) null draws running on spot.
- 05:12 A4(b) contingency bands DONE: at T = 4e4, R = 24/28 with 9 ∈ R (2B₉/|a₉| = 0.78), vs-ζ cross-reading weakest margin 1.385 (was 1.014); null known answers same pattern (literal FAIL ~√2; LS median 1.01/1.00); ⟨r̃⟩ in band 100%. A4 updated with the measured table and a recommendation for (b). preread.known_answers skips absent configs.
- 05:12 Draft morning report written (ph6/MORNING_2026-10-07.md); the 07:57 wrap-up re-checks it against anything later.
- 05:42 Proposed amendments A1/A6/A4(b) implemented as OPT-IN (preread tables --proposed; gates runs G1-s/G2-s only if sealed): refactor of the G1/G2 blocks reproduces the as-sealed pre-read bit-identically; results/preread_proposed built (G1-s RP5 reach 1.7e5/1.3e3; G2-s (10,4) RP11 1.9e9; G2 at 4e4 R 24/28); synthetic crash check of the new paths passes; make_seal_json --pre selects the pre-read. Morning report updated.
- 05:52 check-in: all overnight work items done; third review agent launched on the 1fc3552..HEAD diff (opt-in proposals refactor, make_seal_json, chi4_zeros_v2) → ph6/REVIEW_code_v3.md. Spot idle.
- 06:09 REVIEW_code_v3 (no BLOCKER) majors fixed: gates.check_inputs (sealed pre-read dir; data by role: sha256 + level counts); seal JSON paths relative to ph6/; separate --A1/--A6/--A4b flags with make_seal_json refusing unless configs = sealed set + approved windows and G2 height ↔ A4b; chi coverage from merge.json; synth_run covers G1s/G2s; env versions pinned; BANDS_PROVENANCE.json per pre-read dir; make_seal_json --dry. Regenerated proposed tables with the separate flags: all 16 byte-identical. Dry runs pass (31+5 / 34+5 pinned); both mismatch cases refused; no seal file written.
- 06:12 check-in: all work items done; memories written (PARI close-pair/64-bit lesson; pgrep -f kill-loop variant; next-session pointer → MORNING report). Spot idle; nothing running.
- 06:14 memory index compacted (166→119 lines, 22.3→15.9 KB; every link preserved, verified by diff of link sets). Nothing running; awaiting the 07:57 wrap-up.
- 06:32 check-in: idle (nothing running on spot or locally; worktree clean). No unblocked items remain before Will's decisions.
- 06:51 check-in: idle; nothing running; awaiting Will.

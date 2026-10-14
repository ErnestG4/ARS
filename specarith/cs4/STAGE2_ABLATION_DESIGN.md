# Stage 2 term ablation: which correlation classes carry the predicted shrink (design; declared before computing)

Review response item 2 (independent review, 2026-10-14). **Descriptive: model against model.** No F2 (or any) zero
data is read. The Stage 2 verdict (PASS, `ph2s/PH2S_STAGE2_FINDINGS.md`) is not touched by anything here; only the
*wording* of what it confirms depends on the outcome (reading rule, §4).

## 0. Step 0: is there a per-term ledger? No — but every term is already visited
- The prediction's integral split is stored: I₂, I₃, I₄ short-range, I₄ long-range non-oscillating
  (`GS_ZETA_RESULTS.md` §1; the long-range part carries almost all the b-dependence: +0.017 → −0.036 over the ladder at
  ℓ = 15.75, against < 1e-4 for I₂, I₃ and < 2e-3 for short-range I₄).
- There is **no ledger by correlation class.** `cs4lr.LongRangeZeta.connected` (and `cs4fastc`) loop over every CS08
  term — the (P, M) index sets of `cs4lib.index_terms(4)`, then each J* piece from `Jq` — but accumulate into two arrays
  only (oscillating, non-oscillating).
- **Cost.** The model switch is a small code change (blocks zeroed or replaced by a flag; see §2). The expense is the
  re-run: the J₁₃-fix recompute used 158 CPU-h for the pair grids (`results/gs_zeta_fix4/`, 5 heights × 136 pairs),
  plus the lag-1 extension and ρ₃ — about 4–5 h wall at 40 processes on spot per full-CS08-cost model. M1 needs no
  four-point arithmetic blocks and should be several times cheaper. **Runs only after the E₁₁ fresh-range run frees
  spot** (and after the route (a) calibration declaration).

## 1. Notation (as transcribed in `cs4lib.Zeta`, corrected J₁₃ sign)
Unit-density coordinates; at height ℓ = log(t/2π) the CS08 arguments are i·2πx/ℓ. Two-point blocks:
  P1(x) = e^{−ℓx} A(x) ζ(1+x) ζ(1−x)   (oscillating),   P2(x) = (ζ′/ζ)′(1+x) − B(x)   (non-oscillating),
  J₁₁(a, b) = P1(a+b) + P2(a+b)   ⇒   ρ₂^ζ (Bogomolny–Keating form; `cs4lib.R2`).
Higher-order blocks: P3(a,b,c) = B1(a+b, a+c) + ζ′/ζ(1+a+c) − ζ′/ζ(1+c−b); the prime sums/products **Q, B1, B2, B3,
B4, S13** and the four-point Euler product **A***. J₁₂, J₁₃, J₂₂ as in `cs4lib.Zeta` (note J₂₂ contains
P2(a₁+b₁)P2(a₂+b₂) + P2(a₁+b₂)P2(a₂+b₁), i.e. products of two-point blocks, explicitly).
Cumulants (connected correlations) T_k, defined by ρ_n = Σ_{set partitions π of {1..n}} Π_{B∈π} T_{|B|}(x_B), T₁ = 1.
Sine kernel K(u) = sin(πu)/(πu); its cumulants T_k^sine = (−1)^{k−1} Σ_{k-cycles σ} Π_i K(x_i − x_{σ(i)}).

## 2. Models (each computed through the identical pipeline: same heights, grids, prime cutoff 3·10⁵, short/long split,
file-averaged definition (amendment 7), estimator B (amendment 8), weights C for the pool)
- **M0 — sine kernel** (existing, `gs_unitary_lag1.py`): ρ_n = det[K(x_i − x_j)]. **Known-answer gate:** must
  reproduce g_GUE,B = 0.9591 (0.9606 under §1). Re-run through the ablation code path with all arithmetic switched off.
- **M3 — full CS08** (existing): ρ₂^ζ, ρ₃^ζ, ρ₄^ζ as transcribed. **Known-answer gate:** must reproduce the sealed
  pooled 0.6830 (per file 0.6703, 0.6656, 0.6646, 0.6829, 0.7201) to ≤ 1e-6 through the ablation code path.
- **M1 — two-point arithmetic only (cumulant cut):** T₂ = T₂^ζ = ρ₂^ζ − 1 (CS08 / Bogomolny–Keating R₂), T₃ = T₃^sine,
  T₄ = T₄^sine:
    ρ₃^{M1} = 1 + Σ_{3 pairs} T₂^ζ + T₃^sine,
    ρ₄^{M1} = 1 + Σ_{6 pairs} T₂^ζ + Σ_{3 pairings} T₂^ζ T₂^ζ + Σ_{4 triples} T₃^sine + T₄^sine.
  I₂ is identical to M3's. Every arithmetic effect in M1 is a two-point one (single cross-pair T₂^ζ and products of
  two T₂^ζ).
- **M2 — full CS08 with its irreducible higher-order arithmetic blocks set to zero (block cut):** in J₁₂, J₁₃, J₂₂ set
  Q ≡ B1 ≡ B2 ≡ B3 ≡ B4 ≡ S13 ≡ 0 and A* ≡ 1; keep everything built from ζ, ζ′/ζ, (ζ′/ζ)′, A and B (the two-point
  arithmetic, including its products inside J₁₂, J₁₃, J₂₂).
  - **M2′ (sensitivity, reported, not in the rule):** as M2 but A* kept (only the additive blocks zeroed). A* → 1 is a
    definitional choice (A* contains two-point Euler factors as well as irreducible ones); M2′ brackets it.
  - M1 and M2 differ by the arithmetic that sits inside T₃, T₄ as products of two-point blocks (e.g. P1·P3 with ζ′/ζ's
    Laurent terms); the cumulant cut drops it, the block cut keeps it.
- **Optional (if cheap, descriptive only):** the diagonal approximation (B ≡ 0 inside P2 and A ≡ 1 inside P1, i.e.
  Bogomolny–Keating's diagonal R₂, with M1's structure); Stage 1's few-prime model (`ph2s` Stage 1 form factor), if its
  v(b) can be put on the same ladder without new code.
- **Validity is not required.** M1 and M2 need not be valid point processes (positivity, coincidence limits); the
  positivity guard and the coincidence probe (`diag_coinc.py`) are run on each and reported, not gated.

## 3. Output
`results/ablation/ABLATION.json` — this file's §4 rule is written into it (verbatim, with this file's sha256) **before**
any model is computed; then per model: v_B(b) on the ladder and ĝ_B per F2 file, the pooled ĝ_B (weights C), the
integral split (I₂, I₃, I₄ short, I₄ long), positivity, and the differences M1−M3, M2−M3 (and M2′−M3, M0−M3) in units of
Stage 2's CI half-width h = 0.125 (`PH2S_STAGE2_FINDINGS.md`).

## 4. Reading rule (declared now, before computing)
Let Δ₁ = |ĝ_pool(M1) − ĝ_pool(M3)| / h and Δ₂ = |ĝ_pool(M2) − ĝ_pool(M3)| / h (h = 0.125, pooled with weights C).
- **Both < 0.25:** Stage 2 is worded "confirms two-point arithmetic correlations at fresh heights; does not
  discriminate CS08's higher-order terms".
- **Otherwise:** report which class carries the separation: Δ₁ ≥ 0.25 ⇒ the arithmetic inside T₃/T₄ matters (cumulant
  cut); Δ₂ ≥ 0.25 ⇒ CS08's irreducible blocks (Q, B1–B4, S13, A*) matter. The wording then names that class, and states
  that the Stage 2 PASS discriminates it from two-point-only arithmetic only to the extent Δ exceeds Stage 2's
  resolution (Δ in half-widths is reported as is).
- The gates (M0 → 0.9591, M3 → 0.6830) must pass first; if either fails, nothing is read.
- The Stage 2 verdict is not changed in any case; no F2 data is re-read.

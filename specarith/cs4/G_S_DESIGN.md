# Stage 2 statistic and the short/long split for V(b) (design, declared before any ζ variance is computed)

Decisions: nineteenth round (tapered statistic, analyticity) and twentieth round (split plan; sparse direct check;
positivity guard; U(N) first). Code: `cs4lib.py` (CS08 n ≤ 4, gated), `gate_*.py`.

## 1. The statistic (Will, nineteenth round (a))
In unit-mean-spacing coordinates x (zeros: unfolded by N̄; GUE: by the semicircle; locally x = t·ℓ/2π):
  S(c; b) = Σ_{i≠j} F(x_i − x_j) · W_b((x_i + x_j)/2 − c),   W_b(y) = exp(−π y²/b²)   (∫W_b = b),
with F the R₂ family bump (primary (0.5, 0.3)). F and W_b are entire, so the test function F(x₁ − x₂)W_b(·)F(x₃ − x₄)W_b(·)
satisfies CS08's condition (holomorphic for |Im x| < 2, in raw t-units after scaling).
- **Variance across window centres:** V(b) = Var_c S(c; b) for a stationary process.
- **Measured:** sample variance over centres spaced ≥ 3b apart, so windows are effectively independent.
- **Reported:** v(b) = V(b)/b at b = 100 and 10⁴ (and a ladder in between), and g = √(v(10⁴)/v(100)).

## 2. V(b) from the correlations
Let m be the pair midpoint, d the in-pair offset, and r the separation of the two pair midpoints. With
(W⋆W)(r) = ∫W_b(m)W_b(m + r)dm = (b/√2)·exp(−π r²/(2b²)):
  V(b) = ∫W_b² · [2∫F²ρ₂ + 4·(3-point terms)] + ∫dr (W⋆W)(r) · C(r),
  C(r) = ∫∫ F(d₁)F(d₂) [ρ₄(pair at 0 with d₁; pair at r with d₂) − ρ₂(d₁)ρ₂(d₂)] dd₁ dd₂   (plus the midpoint-weight
          corrections of the 3-point terms, which are local).
G-ass verified this assembly for CUE on the circle (W ≡ 1) to 1e-13.

## 3. The split (twentieth round: GO)
CS08's terms come as pieces (coefficient) × e^{−L·Φ}, where Φ is a linear combination of the points.
- **ℓ-oscillating pieces:** Φ depends on r. They oscillate once per mean spacing in r.
- **Non-oscillating pieces:** Φ is independent of r. Their r-dependence is through Dirichlet series and Euler
  products in p^{±ir} (ζ), or through z(±ir) factors (U(N)).

The split, with a smooth partition of unity χ(r) (χ = 1 for |r| ≤ r_c, smooth fall to 0 over [r_c, 2r_c];
r_c = 10 spacings):
- **Short range** (χ·C): the full connected function, integrated directly, oscillating pieces included.
- **Long range** ((1 − χ)·C): the non-oscillating pieces only. The ℓ-oscillating pieces times the smooth (1 − χ)·(W⋆W)
  integrate to ≈ e^{−(ℓ·scale)²}, which is negligible; checked numerically at b = 100, where it matters most.
- **Long-range non-oscillating part:**
  - C_no(r) = c∞ + (almost-periodic, mean-zero part) + (decaying part: ~1/r², the sine-kernel tail).
  - **c∞** is the Bohr mean over r. For ζ it is computed analytically: Euler-product pieces as Π_p E_θ[local factor
    with p^{ir} = e^{iθ}] (the p^{ir} are linearly independent); Dirichlet-series products as diagonal sums.
  - The decaying and almost-periodic parts are integrated numerically against (W⋆W)(r)(1 − χ(r)) for each b.
  - ~~Large-b behaviour: v(b) ≈ K + c∞·b. **c∞ < 0 is a shrink.**~~ **Superseded (twenty-first round, §6):** no
    functional form; v(b) and g are computed directly from the evaluated integrals.

## 4. The constant-part approximation: declared range and guards (twentieth round (2))
- **Validity.** "c∞ constant" is the large-r mean of CS08's formula, which holds for r ≪ t (CS08's error
  O(T^{1/2+ε}); the windows here span ≤ 3·10⁴ spacings ≈ 10⁴ t-units, against t ≥ 10⁷). It is used only for
  1 ≤ b ≤ 10⁴.
- **Positivity guard (gate).** The predicted v(b) must be > 0 for every b ≤ 10⁴ on a log ladder. Otherwise G-s FAILS. (Twenty-first round: checked on the computed values, not on a fitted form.)
- **Sparse direct check (twentieth round (1)).** At a few hundred r on a log grid (r = 10–10⁴ spacings), the full
  connected C(r) is evaluated directly (parallel on spot), locally averaged over one spacing to remove the
  ℓ-oscillation. It must match the evaluated non-oscillating part, and its long-run mean must match the analytic c∞,
  within its sampling error. Run before c∞ is used.

## 5. Order (twentieth round (3))
1. U(N)/sine kernel through the same split: c∞ = 0 (decay only). Then:
   - (i) v(b) flat, matching the measured long-GUE baseline (g = 0.97–0.99 at L = 10⁶);
   - (ii) small-N exact CUE_N Monte Carlo of S(c; b) variances.
2. ζ: the sparse direct check, then c∞(t) and v(b) per F2 height.
3. Seen data (R1–R5, F1): descriptive comparison only.
4. Seal on F2.

## 6. Amendments (twenty-first round, Will, 2026-10-10)
1. **No functional form for v(b).** K + c∞·b is dropped. The predicted v(b), and g = √(v(10⁴)/v(100)), are computed
   directly at the sealed block lengths and the sealed taper W_b, from the evaluated integrals of §2 (short range: the
   full connected function; long range: the non-oscillating part, numerically against (W⋆W)(r)(1 − χ(r))). c∞ is
   still computed and reported, but no prediction is extrapolated from it.
2. **Positivity guard** on the computed v(b) at every rung of the b ladder ≤ 10⁴ (§4).
3. **log b behaviour** of v(b) (seen on F1, `ph2s2/results/tapered/TAPERED_SUMMARY.md`) is reported descriptively,
   for both prediction and data; it does not enter any criterion.
4. **Prime cutoff ≥ 3·10⁵.** The cutoff diagnostic (`diag_pmax.py`, t = 4.12e8, d = 0.5/0.5) converges: the change per
   ~3× cutoff step falls 5–80× (I(100): 8.8e-5, 1.9e-5, 1.7e-6, 2.2e-8 over 1e4 → 1e6). **The hypothesis that the
   cutoff drift was logarithmic was wrong**, and the analytic rewrite of the Re s = 1 factors in ζ, ζ′/ζ and log ζ is
   dropped.
5. **Evaluator precision is sufficient.** The sparse check v2 passed (worst 5.36e-10; `SPARSE_CHECK_RECORD.md` §4.2).
   Stage 2 needs about 1e-3 relative, so the evaluator error is irrelevant at that scale. No further work on the
   residual; r > 2·10⁴ spacings is unchecked.
6. **Route (a) window s ≤ 1.8** (`../ph2/SCOPE_CS_SPACING.md` amendment). The U(N) gate, read on s ≤ 1.8: max
   |p₄ − p_N| = 5.0e-5 (N = 10) and 6.9e-5 (N = 50), below the ~1e-4 bin resolution, so no n = 5 term is needed.
7. **(Proposed, 2026-10-10; for Will.) The prediction is the file-averaged one; the oscillating-part check is done on
   a fine grid and averaged over ℓ.** Evidence in `GS_ZETA_RESULTS.md` §3:
   - The ℓ-oscillating long-range part is not negligible at a fixed ℓ: up to 9e-3 of v at b = 10⁴ for one pair at
     ℓ ≈ 15.75. The §3 claim "≈ 0" holds only after averaging over a file's ℓ range, where it is (1.3 ± 5.3)e-4 of v.
   - The kept part's mean-ℓ value equals its file average to ≤ 5e-6 of v.
   - Proposed wording: "The prediction for each F2 file is CS08's correlation averaged over the file's heights
     (zero-weighted). It is evaluated as the kept part at the zero-weighted mean ℓ, with the ℓ-oscillating long-range
     part dropped. That drop is justified by the file-averaged check, done on a Δr ≤ 0.1 grid; the Δr = 0.5 production
     grid aliases the e^{∓4πir} pieces."


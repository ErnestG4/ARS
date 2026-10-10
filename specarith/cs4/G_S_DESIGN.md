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
  - Large-b behaviour: v(b) ≈ K + c∞·b. **c∞ < 0 is a shrink.**

## 4. The constant-part approximation: declared range and guards (twentieth round (2))
- **Validity.** "c∞ constant" is the large-r mean of CS08's formula, which holds for r ≪ t (CS08's error
  O(T^{1/2+ε}); the windows here span ≤ 3·10⁴ spacings ≈ 10⁴ t-units, against t ≥ 10⁷). It is used only for
  1 ≤ b ≤ 10⁴.
- **Positivity guard (gate).** The predicted v(b) must be > 0 for every b ≤ 10⁴ on a log ladder. Otherwise G-s FAILS.
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

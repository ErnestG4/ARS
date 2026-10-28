# GEO-CM1 follow-ups (Will, 2026-10-28) — POST HOC, labelled; no sealed verdict changes

## 1. The a = 4 SE (2.3·10⁻⁵): diagnosis
Script `geocm1_a4_diag.py` (committed before it ran), output `results/A4_SE_DIAG.json`, on the sealed read's existing
per-level values (READ1) plus one new double-precision check (item 3).

1. **The driving level is the shallowest one, q = 17.** a = 4 has 5 levels with q ≥ 10 (17, 72, 305, 1292, 5473; the
   next, 23,184, is above the cap), so 4 ratios δ_n and exactly the minimum for an SE: SE = |Aitken(last three) −
   Aitken(the three before)|. The earlier triple contains w₁₇/w₇₂ = 24.6095570, whose correction is not yet geometric:
   the ratio of successive differences is −0.036 there and −0.101 one step later (the geometric model assumes it
   constant). Aitken triples: 24.6203257 (with q = 17) and 24.6203485 (without); their difference is the SE.
   For comparison, a = 5 has the same level count but its ratios are already steady (−0.009, −0.012): SE 1.3·10⁻⁷.
   a = 3 has 6 ratios, so its SE uses later triples (ratios −0.15, −0.17).
2. **Brackets and precision are clean at every a = 4 level:** 0 bracket fixes at both precisions; bisection–Newton
   agreement ≤ 1.0·10⁻¹¹ of the width; 30 vs 50 digits agree to ≤ 2.7·10⁻²³ relative; edge tolerance 2.5·10⁻¹¹ of the
   width.
3. **Global extremum (new check, double precision):** at Ω = edge ∓ 0.05·w, the maximum (minimum) of G = Fᵠ(x) − x − p
   over a 256q grid with refinement has the required sign at both edges of every level of a = 3, 4, 5 (19 levels, all
   pass). So no edge was found on a local extremum that is not global.
4. **Golden-path tongues:** none near. The a = 4 tongues are at Ω ≈ 0.2715; the golden path converges to Ω₁ = 0.60666,
   ≥ 524 widths away even at q = 4 (≥ 1.9·10⁸ widths at q = 5473). What the a = 4 brackets do contain are Fibonacci-
   denominator tongues: level n's bracket (between convergents n−2 and n−1) holds the intermediate fractions
   (k p_{n−1} + p_{n−2}) / (k q_{n−1} + q_{n−2}); for k = 1 and k = 3 these are F_m / F_{m+3} (e.g. 5/21 and 13/55 in
   the 17/72 bracket; the levels themselves are F_{3n−3}/F_{3n} reduced by 2). They are larger tongues of different
   rotation number; the sign checks (item 2) and the global-extremum check (item 3) show none captured an edge search.
5. **External check:** Cvitanović–Gunaratne–Vinson (Nonlinearity 3 (1990), Table 1, values from A. Eriksson) give
   |δ₄| = 24.620 347 98 (uncertainty printed as 7·10⁻⁸). The sealed estimate 24.62034847 is 4.9·10⁻⁷ above it, 0.02 of
   the sealed SE: the SE is conservative by about 50× here, because it measures the q = 17 transient, not the error of
   the last triple. f(4) from their value: 1.10955061 (ours 1.10955062).

**P1 pairs stand.** (3,4): f(4) − f(3) = 0.012352 against sd 1.0·10⁻⁶ (z ≈ 12,000); (4,5): 0.013093 against
1.25·10⁻⁶ (z ≈ 10,500). With SE(4) inflated 10× or 100× both remain SUPPORT (z ≥ 122). Dropping the q = 17 level leaves
f(4) = 1.10955065 (no SE possible), within 1·10⁻⁶ of the sealed estimate.

All of our |δ_a| sit slightly above CGV's: 3.9·10⁻⁹ (a = 1), 3.7·10⁻⁸ (2), 1.9·10⁻⁷ (3), 4.9·10⁻⁷ (4), 3.9·10⁻⁷ (5),
4.6·10⁻⁶ (6), 4.3·10⁻⁶ (7), 1.3·10⁻⁵ (8); a = 10 is 1.7·10⁻⁴ below (CGV ± 2·10⁻³). At a ≤ 5 each is inside our SE.

## 2. The limit: h_a (descriptive; the h_a clause stays UNPOWERED as sealed)
Step 0: `GEOCM1_LIMIT_STEP0.md`. Known only as a heuristic: δ for a large continued-fraction entry n grows as n³
(CGV eq. (9), citing Jensen–Bak–Bohr, Cvitanović–Shraiman–Söderberg, Kaneko), i.e. h_a → 3/2. No prefactor or
correction terms are published; Epstein–Yampolsky's universal parabolic map is a rigorous framework in which the
asymptotic could be computed, but it has not been.

| pair | (1,2) | (2,3) | (3,4) | (4,5) | (5,6) | (6,7) | (7,8) | (8,9)* | (9,10)* |
|---|---|---|---|---|---|---|---|---|---|
| h_a | 1.0936 | 1.1248 | 1.1688 | 1.2155 | 1.2583 | 1.2949 | 1.3250 | 1.3494 | 1.3691 |

\* uses CGV's δ₉ = 174.5198 (our a = 9 path has too few levels for an estimate).

h_a rises steadily and is 1.37 at the last pair. The simple extrapolation forms disagree (≈ 1.5 against ≈ 1.7), and
the Step 0 agent's own fits span 1.43–1.60; corrections at a ≤ 10 are 20–30%, and f(a) approaches its limit only like
1/ln λ_a. The data up to a = 10 do not fix the limit; the n³ heuristic says 1.5.

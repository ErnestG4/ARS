# GEO1 Step 1 — price (2026-10-30; desktop timings, single thread)

> **Correction (2026-10-30, before any run):** the explicit-enumeration figures below used T³/24; the benchmark loop is
> 0.39·t² steps per trace (0.13·T³ in all: 3·10⁴ ≈ 70 min desktop), and the production loop ≈ 0.071·t² (≈ T³/42:
> 3·10⁴ ≈ 13 min desktop, ≈ 0.5 spot core-h). See `GEO1_STEP1_PLAN.md` §2.

Benchmarks (scratch code, not committed; desktop WSL, one thread; spot ≈ 2.3× slower per core):
- **Explicit enumeration** of positive matrices (a b; c d), a, b, c, d ≥ 1, a + d = t, ad − bc = 1 (one per rotation of
  each class's L/R word; needed for the brute-force gate, the cycle words and Gauss–Kuzmin): ≈ T³/24 divisor steps at
  ≈ 1.2 ns (t = 3,000: 4.2 ms). For all t ≤ T: T = 10⁴ ≈ 1 min, 3·10⁴ ≈ 25 min, 10⁵ ≈ 13 h desktop (≈ 30 spot core-h).
- **Class numbers via PARI 2.17** (h(d) for d = (t² − 4)/u², about 1.5 discriminants per t):
  - `quadclassunit`: 0.6 / 1.1 / 2.0 ms per d at d ≈ 10⁸ / 10¹⁰ / 10¹² (GRH-conditional for large d unless certified).
    All t ≤ 10⁶ (d ≤ 10¹²) ≈ 1.5·10⁶ calls ≈ 0.8 core-h; t ≤ 10⁷ ≈ 15–20 core-h (extrapolated, not timed at 10¹⁴).
  - `qfbclassno`: 55 / 608 / 7,779 ms per d at 10⁸ / 10¹⁰ / 10¹² (≈ d^0.55): unusable beyond small d; usable as an
    unconditional-route cross-check at small d only.
- Primitive classes from all classes: g_prim(t) = g_all(t) − Σ_{k ≥ 2, V_k(t′) = t} g_prim(t′) (powers of primitive
  classes; t′ ≤ √(t + 2)); negligible cost.

Suggested shape (for Will, not decided): words and Gauss–Kuzmin by explicit enumeration to t ≤ 3·10⁴; multiplicities
g(t) by `quadclassunit` to t ≤ 10⁶ (cross-checked against the explicit counts for t ≤ 3·10⁴ and `qfbclassno` at small
d); total ≈ 2–3 spot core-h. t ≤ 10⁷ for the multiplicity correlations (Peter 2002) would add ≈ 15–20 core-h.

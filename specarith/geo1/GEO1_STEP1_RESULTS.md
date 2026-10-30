# GEO1 Step 1 results (2026-10-30): all gates pass

Plan and tolerances: `GEO1_STEP1_PLAN.md` (committed before any run; run log §5). Launch 3 on spot, 12:15–12:25 PDT.
Gate outputs `results/GATES1.json` = `GATES2.json` (two separate processes, `cmp` identical). Data (gitignored,
`data/`): `words_3e4.npz` sha256 d5f0e66b…977c, `pari_1e6.npz` c72380f9…3258 (also `results/HASHES.txt`).

| gate | criterion | result |
|---|---|---|
| G1 class counts | words = PARI Σ_u h⁺ (all and primitive) at every t ≤ 3·10⁴; forms = both at t ≤ 40 | **PASS**: 0 mismatches in 29,998 t; forms agree; red path: the wide sum differs at 29,997 of 29,998 t |
| G2 R²L² | t = 6: exactly [4,1], [1,4], [2,2]; R²L² has (u, d) = (2, 8); g(6) = 3 | **PASS**: PARI h(32) = 1 with N(ε) = +1 (h⁺ = 2), h(8) = 1 with N(ε) = −1 (h⁺ = 1) |
| G3 Sarnak / PGT | \|Π(T)/Li(ε(T)²) − 1\| ≤ x^(−3/5) ln(x²) at T = 10⁴, 10⁵, 10⁶ | **PASS**: −3.0·10⁻⁴, +5.7·10⁻⁶, +4.6·10⁻⁷ (tol 0.073, 0.023, 0.0069); red path (wide sum) −0.500 at every T: fails |
| G4 Gauss–Kuzmin | pooled digits of primitive classes, t ≤ 3·10⁴, TV ≤ 0.05 | **PASS**: TV = 2.5·10⁻⁵ over 379,256,184 digits; P(1) 0.415051 vs 0.415037 |
| witness | random words: TV from GK > 0.10 and from 2^−k ≤ 0.02 | **PASS**: 0.200 and 0.00025 (8.75·10⁶ runs, 300 t) |

Π(10⁶) = 37,607,967,545 primitive oriented classes with t ≤ 10⁶, against Li(ε²) = 37,607,950,280 (difference
1.7·10⁴ ≈ 0.017·x). The class numbers beyond t = 3·10⁴ (d > 9·10⁸) are GRH-conditional (PARI `quadclassunit`); up to
there they are confirmed by the exact word count. The wide-sum red path sits at exactly −50%: for d = (t² − 4)/u² the
fundamental unit almost always has norm +1, so the narrow factor is 2 (descriptive).

Cost: words 0.756 spot core-h (0.91× the corrected model; checks 0.91, 0.90, 0.90, 0.90); pari 1.580 core-h (checks
0.35, 0.83, 0.93, 1.05 of 5.2 ms per t); total 2.34 against ≈ 2.4 priced. Launches 1–2 stopped before any output
(import; words cost check at 1.667× the first model).

Step 2 (descriptive: length spectrum with multiplicities, multiplicity growth against t/log t, the partial-quotient
histogram by length, mean period against (6 log 2/π²)·ℓ) is next, on Will's word.

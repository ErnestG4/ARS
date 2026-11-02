# FN1 post-hoc lead: stage-1 residuals against L′/L(1,χ_D) and Chen et al.'s C_Φ,L form

**Status:** POST HOC, DESCRIPTIVE, n = 9. No verdict, nothing sealed. Brief: Will, 2026-11-02 (filed verbatim in
`ph2/PH2_DECISIONS_2026-10-07.md`).

**Input:** the sealed stage-1 read `results/read/READ1.json` (sha256 47c19dd2…).

**Scripts → outputs (all in this directory):**
- `fn1_lprime.py` → `FN1_LPRIME.json`
- `fn1_resid_lprime.py` → `FN1_RESID_LPRIME.json`
- `fn1_chen_lterm.py` → `FN1_CHEN_LTERM.json`
- `fn1_segnoise_b045.py` → `SEGNOISE_B045.json` (run on spot, 621 s)
- `fn1_power_b045_readnoise.py` → `FN1_POWER_B045_READNOISE.json`
- `fn1_stage2_power_sketch.py` → `FN1_STAGE2_POWER_SKETCH.json`

## 1. L′/L(1,χ_D) for the nine fields

**Method:** Hurwitz–Stieltjes form, L′/L(1) = −log q − Σχ(a)γ₁(a/q) / Σχ(a)γ₀(a/q).

**Checks (all hold):**
- L(1,χ) = 2π/(w√|D|) to 10⁻³⁰, the class number formula with h = 1;
- a second route, a central difference of log L, agrees to 10⁻¹⁵;
- for χ₋₄, the closed form γ + 2 log 2 + 3 log π − 4 log Γ(¼) agrees to 10⁻³⁰.

| Field | χ_D(2) | L(1,χ) | L′/L(1,χ) | L′/L(2,χ) (§3) | C_F |
|---|---|---|---|---|---|
| −7 | **+1 (2 split)** | 1.1874 | +0.0156 | −0.0528 | 1.946 |
| −8 | 0 (ramified) | 1.1107 | −0.0207 | −0.0454 | 2.079 |
| −11 | −1 | 0.9472 | −0.0842 | −0.0003 | 2.398 |
| ℤ[i] (−4) | 0 | 0.7854 | +0.2456 | +0.0891 | 2.773 |
| −19 | −1 | 0.7207 | −0.0849 | +0.1330 | 2.944 |
| ℤ[ω] (−3) | −1 | 0.6046 | +0.3683 | +0.1727 | 3.296 |
| −43 | −1 | 0.4791 | +0.2495 | +0.3029 | 3.761 |
| −67 | −1 | 0.3838 | +0.6584 | +0.3581 | 4.205 |
| −163 | −1 | 0.2461 | +2.1683 | +0.4140 | 5.094 |

As the brief says, only D = −7 has 2 split. L′/L(1) is strongly tied to C_F: Pearson r = 0.86 (exact p = 0.001),
Spearman 0.75. A residual from a C_F fit therefore has little room left to track it.

## 2. Residual correlations with L′/L(1,χ_D) (brief item 2)

**Residual definitions.** The brief says "R against the C_F rank fit", which I read two ways and report both:
- **lin:** R − (a + b·C_F), by OLS at each β;
- **rank:** rank(R) − rank(C_F).

The p values are two-sided exact permutation p over 9!.

| β | lin: Pearson r (p) | lin: Spearman (p) | rank: Pearson r (p) | rank: Spearman (p) |
|---|---|---|---|---|
| 0.55 | +0.435 (0.26) | +0.150 (0.71) | +0.036 (0.90) | +0.717 (0.037) |
| 0.45 | +0.299 (0.32) | +0.067 (0.88) | −0.254 (0.34) | −0.183 (0.64) |
| 0.40 | +0.109 (0.70) | +0.083 (0.84) | −0.250 (0.31) | −0.133 (0.74) |

**Reading.** No consistent association. The only p < 0.05 is the rank-residual Spearman at β 0.55. The same residuals
give Pearson r = 0.04, it does not appear at the other β, and it is one of 12 descriptive numbers, so it is not
robust to the definition. Without −7 (n = 8) the picture is the same (`FN1_RESID_LPRIME.json`).

**The 10¹⁰ linear residuals at β 0.55:**

| −7 | −8 | −11 | ℤ[i] | −19 | ℤ[ω] | −43 | −67 | −163 |
|---|---|---|---|---|---|---|---|---|
| +0.035 | +0.009 | −0.005 | −0.010 | −0.025 | −0.015 | −0.011 | −0.008 | +0.029 |

The pattern is U-shaped in C_F, with both ends high. That reads as curvature of R in C_F, not a field-specific effect.
−7, the field with the largest residual, has a middling L′/L(1) (+0.016).

**Item 2 does not support a residual-by-L′/L prediction.**

## 3. Chen et al.'s C_Φ,L piece: sign and form for imaginary quadratic fields (brief item 3)

**Source.** Chen, Kim, Lichtman, Miller, Shubina, Sweitzer, Waxman, Winsor, Yang, arXiv:1901.07386. The local PDF
sha256 is 920b212b…9162, the same file `rq1/CHEN_XCHECK.md` pins. This uses Conjecture 1.2, eqs. (1.14) and (9.23)–(9.26),
and Appendix A. The generalisation to other fields is RQ1-b's (`rq1/RQ1B_STEP0.md` §2), labelled UNVERIFIED there:
ζ_K = ζ·L(s,χ_D), F's inert primes in A′_Φ, and log(4π²) − C_F for the Γ-ratio term.

### Form

For λ = log K/log X < ½, the field-dependent part of Var/(⟨ψ⟩ log X) is, in units of 1/log X:

  P_F = C_F + (C_Φ,L(D) + A′_Φ(D))/C_Φ,  with C_Φ = 4π².

For Chen's numerical test function Φ = 1_(0,1], Φ̃(s) = 1/s, so the weight in (9.26) on the line β = it is 1/(¼ + t²).
After s = 1 + 2it, that is the Poisson kernel of the half-plane Re s > 1 at s = 2. L′/L(s,χ) is holomorphic there, has
log growth on the line and tends to 0 as Re s → ∞. So:

  **C_Φ,L = −8π²·L′/L(2,χ_D)**, i.e. the L-piece of P_F is −2·L′/L(2,χ_D).

- The field dependence comes through **L′/L at s = 2, not at s = 1.** For a general Φ it is a Φ-weighted average of
  L′/L along Re s = 1, never the point value L′/L(1).
- **Verified numerically:**
  - against RQ1-b's independent contour integrals (Re β = 0.1, |t| ≤ 200): ℤ[i] −7.0323 against −7.0321, ℤ[√2]
    −12.8088 against −12.8089, ℤ[ω] −13.6318 against −13.6319, all within 2.3·10⁻⁴ (tail bounds 0.014–0.11);
  - by a direct contour on the same grid for −7 (+4.1713 against +4.1716) and −11 (+0.0235 against +0.0232).

### Sign

- **As printed:** the derivation chain is internally consistent. In h⁽¹⁾ (9.23) ζ′/ζ enters with −, L′/L with +;
  (9.24) has +C_Φ,ζ − C_Φ,L; (9.26) defines C_Φ,L with +2πi; (1.14) has K_Φ ∋ −C_Φ,L.
- **The Appendix-A Mathematica cell for C_Φ,L computes −2πi(i∫…).** That is the negative of (9.26), while the C_Φ,ζ
  cell uses +2πi(i∫…).
- I have not re-derived (9.23), so the sign is **as printed, with a recorded discrepancy in their own code**.
- RQ1-b used the printed sign. On Chen's own ℤ[i] statistic at X = 10⁹ the sign changes the prediction by
  2·7.03/(4π² log X) = 0.017, inside RQ1-b's residual range (−0.037 to +0.021). So that check does not decide it.

**Under the printed sign:**
- A larger L′/L(2,χ_D) means a lower variance ratio.
- L′/L(2) rises with |D|, so the L-piece compresses the C_F slope. The P_F range is 0.64 (P_full) to 0.70 (P_noA) of the C_F range.
- −7 and −8, with negative L′/L(2), are pushed **up** the most: by +0.106 and +0.091 in units of 1/log X, i.e. +0.0046
  and +0.0039 in the ratio at 10¹⁰. −7's L′/L(2) is the most negative of the nine because 2 splits (the −χ(2)log 2/4
  Euler term).

The A′_Φ (inert-prime) piece ranges from −0.014 (−8, whose inert primes start at 5) to −0.255 (−163). It has no
direct counterpart in our statistic, which excludes inert primes; Chen's includes them at θ = 0. So P_F is reported
both with A′ (P_full) and without it (P_noA).

| Field | C_Φ,L | L-piece −2L′/L(2) | A′_Φ/C_Φ | P_noA | P_full |
|---|---|---|---|---|---|
| −7 | +4.171 | +0.106 | −0.066 | 2.052 | 1.986 |
| −8 | +3.581 | +0.091 | −0.014 | 2.170 | 2.156 |
| −11 | +0.024 | +0.001 | −0.189 | 2.398 | 2.210 |
| ℤ[i] | −7.032 | −0.178 | −0.059 | 2.594 | 2.535 |
| −19 | −10.503 | −0.266 | −0.240 | 2.678 | 2.438 |
| ℤ[ω] | −13.632 | −0.345 | −0.196 | 2.951 | 2.755 |
| −43 | −23.913 | −0.606 | −0.254 | 3.155 | 2.902 |
| −67 | −28.272 | −0.716 | −0.254 | 3.489 | 3.234 |
| −163 | −32.688 | −0.828 | −0.255 | 4.266 | 4.011 |

### Against the 10¹⁰ residuals (descriptive)

**Where FN1's cells sit.** In Chen's λ = log K/log X at X = 10¹⁰, the three cells are λ = 0.476 (β 0.55), 0.390 (β 0.45)
and 0.346 (β 0.40). All are below ½, so the L-term applies to all of them. β 0.55 is close to the bifurcation, where
RQ1-b found the two-regime form non-uniform.

| β | OLS slope of R on C_F (form: 1/log X = 0.0434) | r(lin residual, L-piece), p | r(lin residual, L + A′), p | residual SD: C_F / P_noA / P_full |
|---|---|---|---|---|
| 0.55 | 0.0455 | +0.11, 0.77 | +0.16, 0.66 | 0.0218 / 0.0194 / 0.0173 |
| 0.45 | 0.0139 | +0.12, 0.79 | +0.11, 0.80 | 0.0160 / 0.0151 / 0.0149 |
| 0.40 | 0.0132 | +0.04, 0.93 | +0.05, 0.91 | 0.0154 / 0.0152 / 0.0151 |

**Reading.**
- At β 0.55 the R-on-C_F slope is close to the form's 1/log X: 0.0455 against 0.0434.
- At β 0.40 and 0.45 it is about a third of that. This matches RQ1-b's finding that the formula's field difference is
  too large in the rigidity range.
- The C_Φ,L piece does not explain the residuals: |r| ≤ 0.16, p > 0.6. Replacing C_F by P_F lowers the β 0.55
  residual SD from 0.022 to 0.017–0.019, with the same single slope, and barely changes the other two β.
- **On −7:** the form pushes it the right way (up), but by about 0.005 against the observed +0.035, roughly 13%.

**Item 3 summary.**
- **Form:** −2·L′/L(2,χ_D)/log X, below λ = ½ only, collinear with C_F to first order.
- **Sign:** as printed, it lowers the variance of large-|D| fields and raises −7 and −8. The paper's code carries the
  opposite sign, unresolved.
- **Size:** too small to account for the −7 displacement at 10¹⁰.

## 4. Status for stage 2

Neither L′/L(1) (item 2) nor Chen's L′/L(2) form (item 3) supports a residual-by-L′/L prediction. Per the brief
("a residual-by-L′/L prediction if item 2 supports one"), the proposed stage-2 seal carries none. It keeps P_F as a
descriptive comparison only. See `../FN1_STAGE2_SEAL.md`.

## 5. Process note

`fn1_chen_lterm.py`'s first run imported `fn1_lprime.py`, whose module-level code then wrote its output over
`sys.argv[1]`. That was `rq1/results/RQ1B_CONSTANTS.json`, so a committed RQ1-b result file was overwritten.
- It was restored from git and confirmed identical to HEAD (`git diff --quiet`).
- `fn1_lprime.py` now has a `__main__` guard, and its output was confirmed byte-identical after the change.
- No RQ1 file is modified in this commit.

# L17 prerequisites: h = 2 fields, the C_F term for h > 1, and an out-of-sample test of L16 (desk work)

**Brief:** Will, 2026-11-03, filed verbatim in `ph2/PH2_DECISIONS_2026-10-07.md`. Desk work only: no archive, no
angle data, no statistic. **For Will's review before any seal draft.** Nothing here is a design.

## (a) The 18 class-number-2 imaginary quadratic fields, with w = 2

**Source.** The LMFDB number-field search (degree 2, signature [0, 1], class number 2;
<https://www.lmfdb.org/NumberField/?degree=2&signature=%5B0%2C1%5D&class_number=2>) returns **18 matches**. The page
states that the results are complete: "the LMFDB contains all number fields with signature [0,1], class number at most
100 (except 98)". Every match has class group [2] and Galois group C₂.

**w.**
- **Read from LMFDB:** −15 and −20. Both field pages give torsion generator −1 (order 2), and the class-number-formula
  line substitutes w = 2, e.g. `\frac{2^{0}\cdot(2\pi)^{1}\cdot 1 \cdot 2}{2\cdot\sqrt{15}}`.
- **Not read from LMFDB:** the other 16 field pages served a reCAPTCHA bot check to automated fetches, and so did the
  API. If you want LMFDB-sourced w for those 16, the pages need a browser.
- **The other 16, by theorem:** for an imaginary quadratic field the unit group is the roots of unity in K, and
  w > 2 only for ℚ(i) (w = 4) and ℚ(√−3) (w = 6). Neither is among the 18, so w = 2 for all of them.
- **Local cross-check** (PARI via cypari2, run on the 18 polynomials; no data): `bnfinit` gives h = 2 and w = 2 for each
  of the 18, with field discriminants equal to the LMFDB values. `qfbclassno` independently lists the fundamental
  discriminants with |D| ≤ 500 and h = 2: exactly these 18.

| D | LMFDB label | Polynomial | |D| | Class group | w | C_F = log(\|D\|(w/2)²) | P_L = C_F − log 4 | D mod 8 |
|---|---|---|---|---|---|---|---|---|
| −15 | 2.0.15.1 | x² − x + 4 | 3·5 | [2] | 2 (LMFDB page) | 2.7081 | 1.3218 | 1 |
| −20 | 2.0.20.1 | x² + 5 | 2²·5 | [2] | 2 (LMFDB page) | 2.9957 | 1.6094 | 4 |
| −24 | 2.0.24.1 | x² + 6 | 2³·3 | [2] | 2 (theorem; PARI) | 3.1781 | 1.7918 | 0 |
| −35 | 2.0.35.1 | x² − x + 9 | 5·7 | [2] | 2 (theorem; PARI) | 3.5553 | 2.1691 | 5 |
| −40 | 2.0.40.1 | x² + 10 | 2³·5 | [2] | 2 (theorem; PARI) | 3.6889 | 2.3026 | 0 |
| −51 | 2.0.51.1 | x² − x + 13 | 3·17 | [2] | 2 (theorem; PARI) | 3.9318 | 2.5455 | 5 |
| −52 | 2.0.52.1 | x² + 13 | 2²·13 | [2] | 2 (theorem; PARI) | 3.9512 | 2.5649 | 4 |
| −88 | 2.0.88.1 | x² + 22 | 2³·11 | [2] | 2 (theorem; PARI) | 4.4773 | 3.0910 | 0 |
| −91 | 2.0.91.1 | x² − x + 23 | 7·13 | [2] | 2 (theorem; PARI) | 4.5109 | 3.1246 | 5 |
| −115 | 2.0.115.1 | x² − x + 29 | 5·23 | [2] | 2 (theorem; PARI) | 4.7449 | 3.3586 | 5 |
| −123 | 2.0.123.1 | x² − x + 31 | 3·41 | [2] | 2 (theorem; PARI) | 4.8122 | 3.4259 | 5 |
| −148 | 2.0.148.1 | x² + 37 | 2²·37 | [2] | 2 (theorem; PARI) | 4.9972 | 3.6109 | 4 |
| −187 | 2.0.187.1 | x² − x + 47 | 11·17 | [2] | 2 (theorem; PARI) | 5.2311 | 3.8448 | 5 |
| −232 | 2.0.232.1 | x² + 58 | 2³·29 | [2] | 2 (theorem; PARI) | 5.4467 | 4.0604 | 0 |
| −235 | 2.0.235.1 | x² − x + 59 | 5·47 | [2] | 2 (theorem; PARI) | 5.4596 | 4.0733 | 5 |
| −267 | 2.0.267.1 | x² − x + 67 | 3·89 | [2] | 2 (theorem; PARI) | 5.5872 | 4.2010 | 5 |
| −403 | 2.0.403.1 | x² − x + 101 | 13·31 | [2] | 2 (theorem; PARI) | 5.9989 | 4.6126 | 5 |
| −427 | 2.0.427.1 | x² − x + 107 | 7·61 | [2] | 2 (theorem; PARI) | 6.0568 | 4.6705 | 5 |

Every |D| has exactly two prime factors. This is genus theory's condition for a 2-rank-1 class group, and it is used in
(b).

## (b) The C_F term for h > 1, principal prime ideals only

**The h = 1 derivation** (`fn1/FN1_STEP0.md` §1, from `rq1/C_OMEGA_VERIFY.md`):
- The angle is θ = (arg π mod 2π/w)/(2π/w), well defined on ideals because every ideal (π) is principal.
- Its harmonics e^{2πikθ} = (π/|π|)^{wk} are Hecke characters λ_k of frequency wk, conductor 1.
- Λ(s, λ_k) = |D|^{s/2}(2π)^{−s}Γ(s + wk/2)·L(s, λ_k), so the analytic conductor is ≍ |D|(wk/2)², and
  C_F = log(|D|(w/2)²).

**h = 2, principal prime ideals only (w = 2).**
1. **The angle set.** For a principal ideal 𝔞 = (α), θ(𝔞) = (arg α mod π)/π is well defined (units ±1). Non-principal
   prime ideals have no generator and are excluded. As in FN1, the set is the split primes, one prime ideal 𝔭 per
   split p with θ and its conjugate mirrored. Now only those 𝔭 that are principal enter.
2. **Which primes.** With h = 2 and two prime factors of |D|, the class group equals the genus group. So a split prime
   p has principal factors iff all genus characters are +1 at p: p splits completely in the genus field ℚ(√d₁, √d₂),
   D = d₁d₂. That is a congruence condition on p mod |D|. For example, D = −20: p = x² + 5y² ⇔ p ≡ 1, 9 (mod 20). By
   Chebotarev the principal split primes have density 1/(2h) = 1/4 of all primes, against 1/2 at h = 1.
3. **The harmonics.** ξ_k((α)) = (α/|α|)^{2k} is a character of the principal ideals with infinity type of frequency
   wk = 2k. Because I/P has order 2, ξ_k extends to a Hecke character on all ideals in exactly h = 2 ways, ξ̃_k and
   ξ̃_k·ψ, where ψ is the nontrivial class-group (genus) character. On a non-principal 𝔭, 𝔭² = (β) is principal and
   ξ̃_k(𝔭) = ±(β/|β|)^k. Both extensions are unramified, with conductor 1 and the same infinity type.
4. **The selection as characters.** 1_P(𝔞) = (1/h)Σ_{ψ ∈ Ĉl} ψ(𝔞). So the angle sum over principal primes is
   Σ_{𝔭 principal} e^{2πikθ_𝔭} = (1/h)Σ_ψ Σ_𝔭 (ξ̃_kψ)(𝔭), an average of h Hecke L-functions.
5. **Their conductors.** Each ξ̃_kψ has the same Γ-factor and the same |D| as at h = 1:
   Λ(s) = |D|^{s/2}(2π)^{−s}Γ(s + wk/2)·L(s, ξ̃_kψ). So each has analytic conductor ≍ |D|(wk/2)².

**Result: C_F^{(h)} = log(|D|(w/2)²), unchanged, with no h term.** For the 18 fields (w = 2) that is C_F = log|D|. The
class number enters the angle set only through its density (1/4 instead of 1/2 of primes), and the read's matched-N
normalisation R = var/(N/K) is built to absorb that.

**What this derivation assumes (open, to check before any design).** The conductor-rescaling picture,
R_F(K) ≈ R₀(K·e^{C_F/2}), was supported for a single L-function family per field. Here the angle set is a 1/h average
over two families of equal conductor. The cross terms ψ ≠ ψ′ are sums of the genus character over primes, which is
lower order by the prime ideal theorem for that character. At finite X, though, they are a Chebyshev-bias-type
principal-versus-non-principal term. How large they are at the read's X is not derived here.

**The two hypotheses for the pooled set (9 h = 1 + 18 h = 2 fields, matched N and K).** The class number formula gives
L(1,χ_D) = 2πh/(w√|D|). Define P_L = log(1/L(1,χ_D)²) + 2 log π = log(w²|D|/(4h²)) = C_F − 2 log h.
- At h = 1, P_L = C_F exactly (Will's identity), so stages 1–2 cannot separate them.
- At h = 2, P_L = C_F − log 4 (log 4 = 1.386). Within h = 2 the two are tied again (a constant shift), as Will notes.

| | Conductor hypothesis | L-value hypothesis |
|---|---|---|
| Predictor | C_F = log(\|D\|(w/2)²) | P_L = C_F − 2 log h |
| h = 2 fields relative to the h = 1 curve R = f(C_F) | **on it** | **displaced by −log 4 along C**: R_F = f(C_F − 1.386) |
| Size of the gap at β 0.55, linear f | 0 | −b·log 4: **−0.063** (stage-1 b 0.0455) to **−0.076** (stage-2 b 0.0548) |
| Ordering within h = 2 | by \|D\| | by \|D\| (the same) |
| Range of the predictor | 2.71–6.06; six fields (−187 … −427) lie above the h = 1 range (max 5.09) | 1.32–4.67; three fields (−15, −20, −24) lie below the h = 1 range (min 1.95) |

**Descriptive scale only, not a power calculation.** The field-specific offset SD at β 0.55 is about 0.021 in R (L16).
So the L-value gap is about 3.0–3.6× that per field, and about 13–15× the standard error of an 18-field mean, if h = 2
fields scatter like h = 1. Each hypothesis needs extrapolation for some fields, and the stage-1/2 residuals are U-shaped
(curvature). So how to treat f outside the shared range is a design question, not settled here.

**Design obligations this surfaces (for Will; none decided):**
1. **Matched N against matched X.** At density 1/4 against 1/2, an h = 2 set reaches matched N at about 2× the X of an
   h = 1 set.
   - R drifts along prime order in every h = 1 field: −7% to −11% across the stage-2 slice (10¹⁰ → 10¹¹) at β 0.55.
   - If that drift is log-linear in X, a factor of 2 is ≈ 0.3 of it, about 0.02–0.03 relative. That is a rough scale,
     not a measurement. It matches the field scatter in size and is about a third of the L-value gap. The X confound
     is aligned with h.
2. **The principal selection is a residue-class selection mod |D|** (point 2). That is the kind of subset L13's report
   flagged as possibly carrying class-dependent (Chebyshev-type) secondary terms.
3. **Ramified primes and the prime above 2:** FN1's conventions carry over, but they need restating for non-principal
   ramified ideals (e.g. D = −20: the prime above 2 is non-principal).
4. **Cost:** 18 new archives at about 2× the X per point. Not estimated (no compute).

## (c) Testing L16 out of sample: fit on h = 1, predict onto h = 2

The candidates are named here from theory, before any h = 2 data exist; none has been generated. The h = 1 offsets are
seen data: stages 1 and 2, nine fields.

**One point for Will first.** A field-specific pattern that reproduces at +0.977 shows the offsets are systematic. It
does not by itself show a second variable. Any nonlinear f(C_F) also reproduces exactly across stages, and the stage-1
residuals were U-shaped. So the C-only alternative has to be in the candidate set, as the null for "a second variable
is acting". The h = 2 set tests it, because it puts fields at new C values.

**Candidates, in declared order:**

| # | Covariate | Theory rationale | Fit on h = 1 | Prediction onto h = 2 | Status |
|---|---|---|---|---|---|
| K0 | **Curvature in C_F** (quadratic, or a monotone spline with declared knots) | The C-only alternative: the offsets could be f(C_F) − linear | a + bC + cC², 6 df | Each h = 2 field from its C_F (conductor) or P_L (L-value); no free parameter | Ready to declare |
| K1 | **The small-prime arithmetic term**: a lower-order term in the angle pair correlation weighted by local splitting, e.g. A_F = Σ_p (1 + χ_D(p))·log²p / p² (the prime-ideal-square contribution) | After the log-conductor term, the next term in Hecke-angle variance (Rudnick–Waxman; Bogomolny–Keating-type lower-order terms) carries an arithmetic sum over primes that depends on χ_D(p) at small p | a + bC + γA_F | Each h = 2 field from its χ_D. For principal-only sets, derive which Euler factors enter (both ξ̃_kψ carry every prime's local factor) | **The form is not derived yet.** The A_F above is a placeholder, and deriving it is itself a prerequisite |
| K2 | **χ_D(2) = +1** (2 split): the largest-weight, one-prime truncation of K1 | As K1 | a + bC + γ·1[χ_D(2) = 1]. Degenerate: −7 is the only h = 1 field with 2 split, so γ is −7's offset | Only −15 has 2 split (D ≡ 1 mod 8). There, **both primes above 2 are non-principal** (PARI `bnfisprincipal`), so they are not in the angle set, but their Euler factor is in both L-functions | Not theory-blind on h = 1: suggested by −7 at stage 1 (L15). On h = 2 it is one field, so descriptive only |

- **Controls, already tested on h = 1 (L15, not supported):** L′/L(1,χ_D) and Chen's L′/L(2,χ_D) term. Report them
  as controls, not candidates.
- **Excluded, with reasons:**
  - Finite-k Γ-factor corrections: they depend on w only, so they are constant across all w = 2 fields and cannot
    produce w = 2 scatter.
  - Ramified-prime points: one point per field, against N ~ 10⁹.
  - X mismatch among the h = 1 fields: equal split density.

**How the out-of-sample reading could separate the questions (a sketch for Will, not a design).**
- **Fit on h = 1:** each candidate is fitted on the nine fields' offsets, averaged over stages 1–2 with L16's noise.
  Then the coefficients are frozen.
- **Two questions read from different features of the h = 2 data:**
  - The **group shift** (the h = 2 mean against the h = 1 curve) decides conductor against L-value.
  - The **within-h = 2 pattern** (h = 2 offsets after removing the group mean, against each candidate's frozen
    prediction) tests the second variable.

  Within h = 2 the conductor and L-value predictors differ by a constant. So the second-variable test does not depend
  on which hypothesis holds, except through f's curvature (K0).
- **Multiplicity:** three candidates (K0, K1, K2) in the declared order. K2 rests on one field.
- **Dependencies:** K1 needs its form derived first. Obligation 1 in (b), the X confound, applies to both questions.

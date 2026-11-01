# FN1 (field ladder), Step 0: conductor constants, angle maps, a sealed rank-test design, and price

Brief: Will, 2026-10-31, filed verbatim in `ph2/PH2_DECISIONS_2026-10-07.md`. Step 0 only. **No archive is generated
and no statistic is computed until Will reviews this.** The only computation so far:
- the coefficients a_p = 2·Re(π²) for p ≤ 50, solved by hand-sized Cornacchia (`_mine/predicted_ap.json`);
- the exact Spearman null and a parametric power table (§4), which use no data.

## 1. The nine fields and their conductor constants

**Derivation.** It follows `rq1/C_OMEGA_VERIFY.md`, which established C_ω = log 27 and C_i = log 16 from Holm (JTNB 2025),
Rudnick–Waxman and LMFDB.
- For a class-number-1 imaginary quadratic field K with w units, the sector angle θ = (arg π mod 2π/w)/(2π/w) ∈ [0, 1)
  is well defined on ideals.
- Its harmonics are e^{2πikθ} = (π/|π|)^{wk}: the Hecke characters λ_k of frequency ℓ = wk, conductor 1, trivial
  finite part.
- Hecke's functional equation (Holm p. 245, via IK Thm 3.8) gives Λ(s, λ_k) = L(s, λ_k)·|D|^{s/2}·(2π)^{−s}·Γ(s + wk/2).
- So the analytic conductor is ≍ |D|·(wk/2)², and

  **C_F = log(|D|·(w/2)²)** in the k-indexing (the asymptotic constant in log q ≈ 2 log k + C_F).

**Checks against the known cases.**
- w = 6, |D| = 3: log 27. ✓
- w = 4, |D| = 4: log 16. ✓
- **w = 2: C_F = log|D|**, as Will expected by analogy. This is verified for each field in §2.

| Field | D | w | C_F | value |
|---|---|---|---|---|
| ℚ(√−7) | −7 | 2 | log 7 | 1.9459 |
| ℚ(√−2) = ℤ[√−2] | −8 | 2 | log 8 | 2.0794 |
| ℚ(√−11) | −11 | 2 | log 11 | 2.3979 |
| ℤ[i] | −4 | 4 | log 16 | 2.7726 |
| ℚ(√−19) | −19 | 2 | log 19 | 2.9444 |
| ℤ[ω] | −3 | 6 | log 27 | 3.2958 |
| ℚ(√−43) | −43 | 2 | log 43 | 3.7612 |
| ℚ(√−67) | −67 | 2 | log 67 | 4.2047 |
| ℚ(√−163) | −163 | 2 | log 163 | 5.0938 |

**Convention caveats** (from `C_OMEGA_VERIFY.md` item 7; they apply here unchanged):
- Constants common to all fields (−2 log 2π, the "+3") cancel in a rank test.
- The O(1/k) finite-k corrections are field-specific but negligible at the read's K (10³–10⁶ harmonics).
- Indexing by ℓ instead of k would shift C by −2 log w. That would reorder the w = 4 and w = 6 fields relative to the
  w = 2 ones, so the k-indexing must match the angle map exactly. It does here: θ is normalised over the sector 2π/w in
  every field.

## 2. Verification (LMFDB)

For w = 2 the smallest character is λ₁ = (π/|π|)², of infinity type 2. Its newform has weight 3, level |D| and CM by K,
with Λ(s) = |D|^{s/2} Γ_ℂ(s + 1) L(s) and a_p = π² + π̄² = 2·Re(π²) at split p, and 0 at inert p. These are the
analogues of 3.7.b.a (ℤ[ω]) and 4.5.b.a (ℤ[i]).

A web-reading agent looked up the pages blind: it was not given my a_p values. Its report is `LMFDB_WEIGHT3_CM.md`. The
comparison with `_mine/predicted_ap.json` is filled in below once that report is in.

**Result: VERIFIED for all seven w = 2 fields** (`LMFDB_WEIGHT3_CM.md`).

**The forms.** At each level |D| there is exactly one weight-3 newform orbit with CM. Each has dimension 1 and rational
coefficients, and its page states CM by the right field:

| D | Label |
|---|---|
| −7 | 7.3.b.a |
| −8 | 8.3.d.a |
| −11 | 11.3.b.a |
| −19 | 19.3.b.a |
| −43 | 43.3.b.a |
| −67 | 67.3.b.a |
| −163 | 163.3.b.a |

The search pages state that they are complete.

**Functional equation.** For levels 7–67 the L-function pages give Λ(s) = N^{s/2} Γ_ℂ(s + 1) L(s) = Λ(1 − s) with
conductor N = |D|, sign 1 and Selberg data (2, N, ( :1), 1). That is μ = 1 = wk/2 at k = 1, so log q ≈ log|D| + 2 log k
and C_F = log|D|.

**Coefficients.** a_p for p ≤ 47 at all seven levels, 105 values, equal the independently computed values
(`_mine/predicted_ap.json`; the agent was not given them):
- 2·Re(π²) at split p;
- 0 at inert p;
- π_ram² at the ramified prime: −7, −2 (for ℚ(√−2), since π_ram = √−2), −11, −19, −43, −67.

One apparent mismatch, at D = −8 and p = 2, was my comparison rule using D in place of π_ram² = −2. It is not a
discrepancy.

**This identifies each form with λ₁ = (π/|π|)²** and confirms the angle map's sector convention: θ over π for w = 2.

**What was not loaded.**
- *163.3.b.a's L-function page* did not load (reCAPTCHA). Its form, CM field and a_p (0 up to 37, then −81, −77, −69 at
  41, 43, 47, matching mine) were read from the newform page, which gives analytic conductor 4.441. So for D = −163 the
  functional-equation line is inferred from the six that loaded, not read.
- *Item 4, the Hecke character,* is not stated on any page. The identification rests on the coefficient match.
- *4.5.b.a and 3.7.b.a,* the ℤ[i] and ℤ[ω] analogues, were re-read: their a_p match the earlier verification. Their
  L-function pages did not load this time. They were VERIFIED in `rq1/C_OMEGA_VERIFY.md`.

## 3. The angle map (w = 2) and the archives

**Split primes.** p with (D/p) = +1, i.e. p splits in K. Ramified p | D and inert p are excluded, as in the RQ1
archives (N counts prime ideals above split primes).

**Generator.**
- D ≡ 1 (mod 4) (−7, −11, −19, −43, −67, −163): O_K = ℤ[(1 + √D)/2]. Solve x² + |D|·y² = 4p with x, y > 0 (modified
  Cornacchia: r² ≡ D (mod 4p), Euclid on (2p, r) to below 2√p). Then π = (x + y√D)/2.
- D = −8: O_K = ℤ[√−2]. Solve x² + 2y² = p, x, y > 0 (plain Cornacchia). Then π = x + y√−2.
- The solution is unique up to the units ±1 and conjugation (class number 1).

**θ map.** With x, y > 0, arg π lies in (0, π/2):
- θ = (arg π mod π)/π = atan2(y√|D|, x)/π for D ≡ 1 (mod 4), or atan2(y√2, x)/π for D = −8, so θ ∈ (0, ½);
- the conjugate ideal π̄ sits at 1 − θ (the mirror), exactly as for ℤ[i] (θ over π/2) and ℤ[ω] (θ over π/3).

**Archives.**
- Rows stored as int32 (x, y), segments of 10⁸ with per-segment sha256 and a manifest, as `rq1_zw.py`.
- The new module will be `fn1_archive.py`. It will not touch the RQ1 code.
- Generation runs to 1.01·10¹¹, so every field has at least n rows at both X.

**Matched N.** n = the ℤ[√2] split-prime count below X, as in RQ1: 227,524,967 at 10¹⁰ and 2,059,026,114 at 10¹¹.
N = 2n, and each field uses its first n split primes.

**Pre-archive checks.**
1. For p < 10⁶, Cornacchia agrees with brute force.
2. Segment 0 regenerates bit for bit.
3. The θ map is checked on hand cases. For D = −7, p = 2: π = (1 + √−7)/2, so θ = atan2(√7, 1)/π = 0.3850.

## 4. The sealed rank test (design)

**Prediction (zero parameters).** At matched N, R_F increases with C_F.
- The basis is the conductor-rescaling picture R_F(K) ≈ R₀(K·e^{C_F/2}). It is supported in RQ1 / RQ1-c by the SE-free
  patterns (`rq1/RQ1C_FINDINGS.md` §0): the ℤ[ω] ratio, the crossover location, and the sign of D across X.
- The predicted ranking of the nine R_F is the ranking of C_F in §1.

**Statistic.** Spearman ρ between C_F and R_F across the nine fields.
- Primary: (X = 10¹¹, β = 0.55).
- Secondary: (10¹⁰, 0.55), and the B2 cells β 0.40 and 0.45 at both X.

**Null: exact permutation.** All 9! = 362,880 orderings are equally likely if R_F is unrelated to C_F. The test is
one-sided, and the null needs no SE model.
- Primary at α = 0.01: PASS iff ρ ≥ 0.7833 (exact p = 0.0086). Otherwise FAIL.
- Secondary cells at α = 0.05 (ρ ≥ 0.600), each reported separately, with no family claim.

**Power.** This is the crux. A parametric model R_F = b·C_F + ε_F with ε ~ N(0, σ²) gives:

| Cell | b per unit C | σ = model SE | 3× | 7× | 10× | 20× | 30× |
|---|---|---|---|---|---|---|---|
| 10¹¹, β 0.55 (primary) | 0.035 | **1.00** | 1.00 | 0.69 | 0.39 | 0.10 | 0.05 |
| 10¹⁰, β 0.55 | 0.041 | 1.00 | 0.94 | 0.33 | 0.16 | 0.05 | 0.03 |
| 10¹¹, β 0.45 | 0.013 | 0.77 | 0.12 | 0.03 | 0.02 | 0.02 | 0.01 |
| 10¹¹, β 0.40 | 0.012 | 0.38 | 0.05 | 0.02 | 0.02 | 0.01 | 0.01 |

- b comes from the read ℤ[√2]–ℤ[i] slope per unit C at matched N. σ is in multiples of the sealed SE model.
- L13's empirical fluctuation measures at β 0.55 lie at about 4–11× (residue subsets) and about 8–30× (block arcs),
  across both X.

**Therefore:**
- **A PASS is informative** under any noise model: the null is exact.
- **A FAIL is informative only if the noise is near the sealed model.** At L13's levels, the primary test has power
  from about 0.97 (4×) down to 0.05 (30×). The attribution must say so in advance: a FAIL would not distinguish "R is not ordered by C" from "the
  fluctuations L13 measured are real noise".
- **The B2 cells are underpowered** even at the model SE, so they are reported but declared UNPOWERED (power < 0.8)
  before the read.

**Descriptive same-conductor check** (no verdict). These pairs have nearly equal C:
- **ℚ(√−7) / ℚ(√−8):** ΔC = 0.134, same w.
- **ℤ[i] / ℚ(√−19):** ΔC = 0.172, **different w (4 against 2)**. This is the informative pair: by log|D| alone ℤ[i]
  would sit with −7 / −8, but by C_F it sits with −19.

For each pair, |R_F − R_G| is reported against the ladder spacing b·ΔC and against the full ladder spread.

**Also descriptive.** ρ against log|D|, which ignores w, set beside ρ against C_F. The two orderings differ only in where
ℤ[i] and ℤ[ω] sit, so this shows whether the w factor in C_F is needed.

**Seen data.** ℤ[i] and ℤ[ω] at 10¹⁰ and 10¹¹ were read in RQ1 / RQ1-c. Two of the nine values in each cell are therefore
known. The other seven fields have never been generated. The predicted ranking is fixed by C_F alone, so knowing two
values does not tune anything. The fact is recorded in the seal.

**Witnesses** (before the seal; synthetic, at reduced N):
- *Planted ladder:* nine mirror-symmetric mixture sets whose R levels follow b·C_F, at noise levels 1×, 3× and 7×. The
  rule must PASS at the rate the power table predicts. This checks the pipeline and the table.
- *Shuffled C:* the same sets with C permuted. The rule must FAIL, at about 1 − α.
- *Null ladder:* nine sets at equal R. False PASS must be ≤ α (it is exact; this checks the code).

**Procedure.** §9.F dry run on the seen ℤ[i] / ℤ[ω] cells plus one synthetic field, then seal → stamp → attest →
double read → `cmp`. Timings go in sidecars.

## 5. Price (cost model; spot core-hours)

| Item | Core-h | Wall / disk |
|---|---|---|
| 7 new archives to 1.01·10¹¹ (Cornacchia per split prime; scaled from ℤ[i]'s measured 27.9 core-h to 1.01·10¹¹ and ℤ[ω]'s 0.84× per-prime ratio) | 175–210 | about 7 h at 28 processes; about 115 GB on `/mnt/data` (415 GB free) |
| Pre-archive checks | under 0.5 | |
| Witnesses (9 sets × 3 noise levels × 100 replicates at N = 10⁸; null and shuffled-C) | about 10 | |
| Read, double (9 fields × 2 X; exact R at β 0.40, 0.45, 0.55, plus 0.60 descriptive) | about 4.5 | under the 80 GB cap |
| **Total** | **about 190–225** | dominated by the archives |

**A cheaper staged option.** Archives only to 1.01·10¹⁰ first, about 20–25 core-hours, with the primary cell moved to
(10¹⁰, β 0.55). That cell's power is 0.94 at 3× and 0.33 at 7×. The archive could be extended to 10¹¹ afterwards
without regenerating, since the segments are contiguous.

**Provenance (round 55).** Written by a research subagent of the main session (literature + estimate), then checked in
the main session before commit: all eight cited arXiv IDs resolve to papers whose abstracts match the topics attributed
to them; the estimate code is committed as `diag_d3_nearres.py` with its output in `results/diag_d3/nearres_output.txt`
(desktop, numpy only, 151 s). Its exact-resonance sum reproduces the sealed Δκ₃ to within 3% at all four F5 heights
(−0.0158/−0.0141/−0.0122/−0.0110 vs −0.0154/−0.0140/−0.0123/−0.0114), an independent consistency check on its
normalisation. The near-resonant estimate is a random-phase model of our own, not a published result. Sources marked
NOT OPENED below were not opened by anyone in this session; no formula is attributed to them directly.

# Diagnostic D3 (draft): could near-resonant prime terms give each file its own κ₃ offset?

Date: 2026-10-18. Status: DRAFT, literature check plus our own estimate. No verdict changes. Nothing in the repo was run or
edited except this file. The estimate code ran on the desktop in about 150 s using numpy only (Appendix A).

**Labels used below.** **[SRC]** marks a statement taken from a source that I opened; the access level is given in
§5. **[OURS]** marks our own derivation or computation. A source I could not open is named with what was seen and
nothing more is attributed to it.

---

## 0. Bottom line

1. **Size of the mechanism.** In the standard prime-sum model of ΔS = S(t+h) − S(t), the near-resonant
   (off-diagonal) prime triples change k₃ at L = 3, over a window of H = 2.1·10⁶, by an RMS of about
   **2–4·10⁻⁵**. This uses the cutoff n ≤ T/2π. With no cutoff the RMS is at most about **7·10⁻⁵**. [OURS]
2. **Comparison with the data.** The observed between-file scatter is about 4–7·10⁻³. The model estimate is
   **about 60–200 times too small in amplitude**, or about 10⁴ times in variance. It is also only 0.05–0.2 of the
   per-file statistical SE (≈ 4.5·10⁻⁴). Even an order-of-magnitude error in the model leaves it far short.
   [OURS]
3. **Exact resonances.** These are the (p^a, p^b, p^{a+b}) triples, mainly (p, p, p²), and they survive any
   averaging. In the same model they sum to **−0.0158, −0.0141, −0.0122, −0.0110** at the four heights. That is
   within about 3% of the sealed Δκ₃ (−0.0154, −0.0140, −0.0123, −0.0114). So the model's normalisation is right,
   and the arithmetic correction in the prediction is, to leading order, these exact resonances. [OURS]
4. **Literature.** I found no published result on the window dependence of odd moments of S(t + h) − S(t). The
   sources fix the structure:
   - Near-resonance needs the product of the prime powers involved to exceed about H (Hughes–Rudnick's argument).
   - Exact resonances in the third moment come only from (p, p, p²)-type matchings.
   - The ratios conjecture, as stated, allows window-dependent errors of O(|I|^{1/2+ε}).

   [SRC]
5. **Predictions for D1 and D2.** The same mechanism gives κ₂(3) offsets of RMS 1–5·10⁻⁵, which is negligible.
   It gives an offset variance that falls like 1/H or slightly faster. So between-sub-block excess should be
   **flat (R_j ≈ 1.01), not growing** with sub-block size. **A scale-growing excess in D1 would therefore point away
   from this mechanism.** [OURS]

---

## 1. What the sources say [SRC]

**Selberg (1944, 1946); statements as quoted by Goldston (2004), §10, Theorem 8.** For k ≥ 1:

- (10.5): ∫₀ᵀ |S(t) + (1/π) Σ_{p ≤ T^{1/k}} sin(t log p)/√p|^{2k} dt ≪_k T.
- (10.6): ∫₀ᵀ |S(t)|^{2k} dt = (2k)!/(k!(2π)^{2k}) · T (log log T)^k + O_k(T (log log T)^{k−1/2}).

Goldston notes the following about these results:
- Selberg proved them on intervals (T, T+H] with T^a ≤ H ≤ T and a > 1/2.
- Selberg had earlier proved them on RH, with error O_k(T (log log T)^{k−1}).

Goldston's Theorem 9 gives Selberg's approximation on RH. For t ≥ 2 and 4 ≤ x ≤ t²:

S(t) = −Σ_{n<x²} Λ_x(n) sin(t log n)/(n^{σ₁} log n) + O((1/log x)|Σ_{n≤x²} Λ_x(n) n^{−σ₁−it}|) + O(log t / log x),

with:
- σ₁ = 1/2 + 1/log x (eq. 10.13);
- Λ_x(n) = Λ(n) for n ≤ x, and Λ(n) log(x²/n)/log n for x ≤ n ≤ x² (eq. 10.11).

Note that the remainder in (10.5) is O(1) in L^{2k}. It is bounded, not small, which matters at h ≍ 1/log T. I could
not open Selberg's own papers (Arch. Math. Naturvid. 47 (1944) and 48 (1946) 89–155).

**Tsang (1984 thesis, Thm 13.2; 1986 Acta Arith. 46, Thm 4); statements as quoted.** Simonič–Trudgian–Turnage-Butterbaugh
(2020, Thm 2) quote Tsang's Theorem 4: for a > 1/2, T^a < H ≤ T, 0 < h < 1 and k ≥ 1,

∫_T^{T+H} |S(t+h) − S(t)|^{2k} dt = (2k)!/(2^k π^{2k} k!) · H log^k(2 + h log T) + O(H (ck)^k (k^k + log^{k−1/2}(2 + h log T))).

Goldston–Lee–Schettler–Suriajaya (2025, eq. 1.2) quote the same formula from Tsang's thesis, Theorem 13.2. They state
that it "refines a result of Fujii [Fuj74, Fuj81]". Both quote **only even moments**. I could not open Tsang 1986 (only
its IMPAN catalogue entry) or the thesis.

**Fujii (1975, Bull. AMS 81, 139–142).** I opened the AMS full text through an OCR extraction. The note announces "a
mean value theorem for the number of the zeros in short intervals" for Δ_hN(t) = N(t+h) − N(t), obtained by modifying
Selberg's approach, with "details [to] appear later". The OCR of the lemma and theorems is too garbled to quote, so I
attribute no formula to it directly.

Hughes–Rudnick (2002, §1) summarise Fujii as follows (in their words). If h log T → ∞ and h ≪ 1, then

(1/T)∫_T^{2T} ((S(t+h) − S(t))/σ)^{2k} dt = (2k)!/(2^k k!) + O(1/σ), with σ² = (1/π²)∫₀^{h log T} (1 − cos t)/t dt.

They note that for h = O(1/log T), the case relevant here, "the main term is the same size as the error term". Rodgers
(2012, Thm 1.1) states Fujii's mesoscopic CLT: Var(Δ) ∼ (1/π²) log n(T) for n(T) → ∞ with n(T) = o(log T).

**Ghosh (1983, J. Number Theory 17, 93–102).** Only the ScienceDirect landing page was seen. Chirre–Quesada-Herrera
(2021, §1.2) report that Ghosh obtained the asymptotics of all moments of |S(t)|^λ (λ > −1). They report that
Goldston (1987, on RH) found the second-order term of ∫|S|² in terms of Montgomery's F(α).

**Odd moments.** Fazzari–Gerspach (2024, Thm 1.1) assume RH, the pair and triple correlation conjectures, and a
"twisted pair correlation" conjecture. Under these they prove (1/T)∫_T^{2T} (Im log ζ(1/2+it))³ dt = O(1/log T),
while the Re part has an O(1) constant c_P + c_Z. They state that the Keating–Snaith conjecture implies all odd moments
of Im log ζ are o(1).

Consistency note [OURS]: for S(t) the (p, p, p²) term carries ⟨sin²x · sin 2x⟩ = 0, which is why it vanishes. For ΔS the
difference turns each sin into 2 cos(τ log n) sin(h log n/2), and ⟨cos²x · cos 2x⟩ = 1/4 ≠ 0. That is why κ₃ of window
counts has an O(1) arithmetic term while the third moment of S(t) itself does not.

**Hughes–Rudnick (2002), structure of off-diagonal terms (full text read).** They average with a weight of width
H = T^a (with ŵ compactly supported) a smooth count with supp f̂ ⊂ (−α, α). In the proof of Thm 2.6, a term survives
only if |Σ ε_j log n_j| ≪ 1/H. Write M = Π_{ε=+} n_j and N = Π_{ε=−} n_j. If M ≠ N, then 1/H ≫ log(M/N) ≫ 1/N, so
**H ≪ N**. By unique factorisation, exact equality M = N without a perfect matching reduces (up to O(1/log T)) to
**n₁n₂ = n₃ with n₁ = n₂ = p, n₃ = p²**. That gives terms (1/log³T) Σ_p (log p)³/p² · f̂(·)² f̂(·). This is the
skeleton of §2 below. Their sharp-count normalisation differs (their f̂ is compactly supported), so their O(1/log T)
bound does not carry over to the box count at L = 3.

**Conrey–Snaith (2008).** Full text read from the local copy `ph2s/lit/CNTP.2008.v2.n3.a1.pdf`. In the Ratios
Conjecture 4.1 (eq. 4.5), the averaged ratio equals ∫_I R_{ζ,t} dt + **O(|I|^{1/2+ε}) for any interval I ⊂ [−T, T]**.
The n-correlation formula, Theorem 4.3 / eq. 4.64, carries O(T^{1/2+ε}).

Heuristic reading [OURS]: this permits window-dependent deviations from the predicted correlations of relative size
about H^{−1/2+ε}. For H = 2.1·10⁶, H^{−1/2} = 6.9·10⁻⁴. Neither H^ε nor the implied constant is specified, so the
conjecture by itself does not exclude a 4–7·10⁻³ offset.

**Bogomolny–Keating (2013, J. Phys. A 46, 305203; full arXiv text read).** Their three-point function averages
over a window ΔE with a prime cutoff p*, under **1 ≪ p* ≪ ΔE ≪ E** (eq. 30). This makes phases of distinct primes
"independent random phases" (eqs. 31–34). Their result "agrees with" Conrey–Snaith's triple correlation. The
near-resonances studied here are exactly the products of primes that break the condition p* ≪ ΔE.

I did not open Bogomolny–Keating 1995/1996 (*Nonlinearity* 8, 9). They are cited above only as listed in Goldston's
references.

---

## 2. Structure of the third moment [OURS]

**Model.** S(t) ≈ −(1/π) Σ_{n≤X} Λ(n) sin(t log n)/(√n log n). Then

ΔS = Σ_n b_n cos(τ log n), with τ = t + h/2 and b_n = −(2/π) Λ(n) sin(h log n/2)/(√n log n).

Here h = 2πL/log(t/2π), so h ≈ 1.21, 1.08, 0.95, 0.89 at the four heights. For n = p^k,
b_{p^k} = −(2/π) sin(kh log p/2)/(k p^{k/2}).

**Expansion.** Use cos a cos b cos c = ¼[cos(a+b−c) + cos(a−b+c) + cos(−a+b+c) + cos(a+b+c)]. Then

(ΔS)³ = ¼ Σ_{n₁,n₂,n₃} b₁b₂b₃ [3 sign patterns with one minus + the all-plus pattern],

with frequencies ω = log n₁ + log n₂ − log n₃ (and permutations), or ω = Σ log n_j.

**Window average.** Over τ ∈ [T, T+H]: cos(ωτ) → cos(ωT_c) · sinc(ωH/2), where T_c is the window centre. All-plus
terms and "partially diagonal" terms (n₁ = n₃, which gives ω = log n₂ ≥ log 2) are suppressed by
sinc ≤ 2/(0.69 H) ≈ 10⁻⁶. The partially diagonal terms are also removed by the k-statistic, being the 3κ₂·mean piece.

**(a) Exact resonance, ω = 0.** Here n₁n₂ = n₃, so (p^a, p^b, p^{a+b}). The weight is 3/4 (a = b) or 6/4 (a ≠ b)
times b b b. These terms are independent of T and H. The leading one is

(p, p, p²): −(3/π³) Σ_p sin²(h log p/2) sin(h log p)/p².

This sum is dominated by p ≤ 7, is negative for h ≈ 1, and gives −0.007 to −0.010. The higher (p, p², p³) terms add
about 30% more.

**(b) Near resonance, 0 < |ω| ≲ few/H.** This needs n₃ ≈ m = n₁n₂ with |n₃ − m| ≲ m/H. Because n₃ ≠ m are integers,
|ω| ≥ ~1/m, so **m ≳ H ≈ 2·10⁶**. This is Hughes–Rudnick's condition H ≪ N. Examples: (2, 1 048 583, 2 097 169)-type
triples and any p₁p₂ ± small = p₃ with p₁p₂ > 10⁶.

Each such triple contributes about (3/2)|b₁b₂b₃| ≲ (12/π³)/m ≈ 2·10⁻⁷ or less. It enters with phase cos(ωT_c) and a
"period" in height of 2π/|ω| ≈ 2πH/(|ω|H). The variance is dominated by 1 ≤ |ω|H ≤ 10 (Appendix B), so the period is
about 1–13·10⁶ in t, comparable to the file width.

**(c) What sets the size.** Two things set the size: the number of near-resonant triples and their 1/m weights. In a
random-phase model (phases ωT_c independent across triples, which holds for files 10⁸–10¹⁰ apart in height), the
variance is

Var = Σ_ω (c_ω sinc(ωH/2))²/2.

Let s(x) = sin(hx/2). Using the PNT density for n₃ near m:

Σ_{n₃} b₃² sinc² ≈ (4/π²) s²(log m)/(m log m) · (2πm/H) = 8 s²(log m)/(πH log m).

So **Var ≈ (9/8)·(1/H) Σ_{n₁<n₂, m>~H} b₁²b₂² · 8 s²(log m)/(π log m) ∝ h/H**. The double sum converges like
∫∫ du₁du₂/(u₁u₂(u₁+u₂)). Hence the **RMS scales as H^{−1/2}**, has no 1/f component, and depends only logarithmically on
the cutoff X.

In this model the near-resonant terms are part of the ordinary sampling fluctuation of a time average, coming from the
arithmetic part of the spectrum. Their periods (≳ H) are longer than a 100-window bootstrap block, so they would show up
as between-file excess. That is why their size matters.

---

## 3. Numerical estimate [OURS]

**Method** (Appendix A). The prime-power list contains primes and prime squares up to 2.1·10⁷.

- **m = n₁n₂ ≤ min(X, 2·10⁷).** Exact enumeration of all n₁ ≤ n₂, with the 24 nearest prime powers n₃ on each side
  of m and the exact sinc².
- **m above 2·10⁷.** PNT-density approximation for the n₃ sum, with the sinc² integrated exactly. As a check, on the
  enumerated range the density version agrees with enumeration within 10–25%.
- **Cutoffs.** X = T/2π, which is the Heisenberg-time cutoff natural to the Bogomolny–Keating picture, then X² and no
  cutoff (X → 10⁴⁰) as sensitivity checks.
- **Window.** H = 2.1·10⁶ and L = 3.

**Results** (all rows are [OURS]; units are k₃ units, except Var_diag which is in squared count units)

| log(t/2π) | 15.60 | 17.50 | 19.75 | 21.25 |
|---|---|---|---|---|
| h | 1.208 | 1.077 | 0.954 | 0.887 |
| Var_diag = Σ b²/2, n ≤ T/2π (sanity check: GUE Σ²(3) ≈ 0.33) | 0.318 | 0.321 | 0.325 | 0.327 |
| **exact resonance, all (p^a, p^b, p^{a+b})** | **−0.01577** | **−0.01405** | **−0.01217** | **−0.01103** |
| … of which (p, p, p²) | −0.01019 | −0.00899 | −0.00777 | −0.00706 |
| sealed Δκ₃ (for comparison) | −0.0154 | −0.0140 | −0.0123 | −0.0114 |
| **near-resonant RMS, cutoff T/2π** | **2.1e−5** | **3.2e−5** | **3.6e−5** | **3.8e−5** |
| near-resonant RMS, cutoff (T/2π)² | 5.2e−5 | 5.5e−5 | 5.6e−5 | 5.6e−5 |
| near-resonant RMS, no cutoff | 6.7e−5 | 6.8e−5 | 6.6e−5 | 6.5e−5 |
| observed k₃ − prediction | +0.0070 | +0.0057 | −0.0032 | −0.0012 |

**Scale for comparison.**
- The per-file SE is 4–5·10⁻⁴. A Gaussian i.i.d. value from 6σ⁶/N with σ² = 0.32 and N = 1.74·10⁶ windows is
  3.4·10⁻⁴.
- The excess between-file SD implied by χ² = 282.7 on 3 df is about √(282.7/3 − 1) × 4.5·10⁻⁴ ≈ 4.3·10⁻³.
- The model's largest value, 6.8·10⁻⁵, is **≈ 1/65 of that**. With the cutoff it is about 1/120.

**Dependence on window width H** (log(t/2π) = 19.75, cutoff T/2π):

| H | 2.1e4 | 2.1e5 | 2.1e6 | 2.1e7 |
|---|---|---|---|---|
| RMS | 5.5e−4 | 1.36e−4 | 3.6e−5 | 9.2e−6 |
| RMS·√H | 0.080 | 0.063 | 0.053 | 0.042 |

To reach 0.007 at H = 2.1·10⁶ in this model, RMS·√H would need to be about 10 rather than about 0.05.

**Approximations and their likely error.**

1. **The prime-sum model at h ≍ 1/log T is heuristic.** Selberg's remainder is O(1) in L^{2k} (§1). The model's
   justification is the Bogomolny–Keating / ratios picture: the arithmetic part comes from primes, while the
   discreteness of the zeros is universal and carries no low-frequency T-dependence. That discreteness is what the
   CUE null calibrates. The exact-resonance row matching the sealed Δκ₃ within about 3% supports the normalisation.
2. **The sharp cutoff X is uncertain.** It changes the RMS by up to a factor of 3, and all variants are in the table.
3. **Random-phase assumption.** This gives the expected mean square over window positions. An individual file can sit
   at 2–3× RMS with small probability, which is not enough.
4. **Neglected terms.** These are prime cubes and higher among n₁, n₂ (weight ≤ p^{−3/2}), the n₃ tail beyond ±24
   neighbours (a few %, see the ">100" band in Appendix B), and the PNT density error for m > 2·10⁷ (10–25%).

Overall I would put the near-resonant RMS at **10⁻⁵ to 2·10⁻⁴**, which is within a factor of 3 of the central value
(≈ 5·10⁻⁵). **The estimate is not uncertain by the factor of about 100 needed.**

---

## 4. Conclusion and implications for D1/D2 [OURS]

- **Plausibility.** Near-resonant or off-diagonal prime terms reaching about 0.007 in k₃ at L = 3 over H ≈ 2·10⁶ is
  **not plausible within the standard (Selberg / Bogomolny–Keating / ratios) picture**. The estimate falls short by
  about two orders of magnitude in amplitude. These terms also add only about 1% to the variance already covered by the
  per-file SE. The sources do not supply a mechanism that would enhance them. The one sourced caveat is that the ratios
  conjecture allows O(|I|^{1/2+ε}) deviations with an unspecified constant (§1).
- **Within-file drift.** The prediction itself changes across a file by at most |dΔκ₃/dlog t| · H/t ≈ 7·10⁻⁴ × 0.058 ≈
  4·10⁻⁵ (lowest file). This uses the sealed Δκ₃ values, and it is also negligible.
- **κ₂(3), number variance.** The same mechanism uses pairs n₁ ≈ n₂, which needs n ≳ H. It gives between-file offsets
  of RMS **1.2–3.2·10⁻⁵** (cutoff T/2π) or **4.0–4.6·10⁻⁵** (cutoff (T/2π)²). The κ₂ SE is about
  √(2σ⁴/N) ≈ 3.4·10⁻⁴, so these offsets are at most about 0.15 SE. **Prediction: D2 should show no between-file κ₂
  excess from this source.** If D2 does show a κ₂ excess comparable in relative size to κ₃'s, the cause is more likely
  a shared one such as the pipeline, unfolding or zero completeness than arithmetic.
- **Dependence on sub-block size.** The offset variance from this mechanism goes as about 1/H_j, slightly faster at
  large H_j (RMS·√H falls from 0.080 to 0.042 between H = 2·10⁴ and 2·10⁷). The low-frequency spectral density of the
  cubic is flat near ω = 0, with no 1/f component.
  - It therefore predicts an excess ratio **R_j ≈ 1 + O(10⁻²), flat or slightly decreasing** with sub-block size.
  - The two halves of a file should differ by about √2 × RMS ≈ 5·10⁻⁵ from this source, which is below the SE.
  - **A scale-growing R_j in D1 is not what this mechanism predicts.** It would need low-frequency power at
    |ω| ≲ 1/H_j that is far larger than the prime model supplies.

---

## 5. References and access level

- **Selberg 1944, 1946.** A. Selberg, "On the remainder in the formula for N(T)", Avh. Norske Vid.-Akad. Oslo (1944);
  and "Contributions to the theory of the Riemann zeta-function", Arch. Math. Naturvid. 48 (1946) 89–155.
  NOT OPENED. Statements are as quoted in Goldston 2004; the bibliographic details are from the reference lists of
  Fujii 1975 and Hughes–Rudnick 2002.
- **Goldston 2004.** D. A. Goldston, "Notes on pair correlation of zeros and prime numbers" (2004),
  https://arxiv.org/abs/math/0412313. FULL PDF text; §10, Thm 8 (10.5–10.6) and Thm 9 (10.11–10.16).
- **Tsang 1986.** K.-M. Tsang, "Some Ω-theorems for the Riemann zeta-function", Acta Arith. 46 (1986) 369–395,
  https://www.impan.pl/en/publishing-house/journals-and-series/acta-arithmetica/all/46/4/105022/some-theorems-for-the-riemann-zeta-function.
  Catalogue entry only. Thm 4 is as quoted by Simonič–Trudgian–Turnage-Butterbaugh. The 1984 Princeton thesis was NOT
  OPENED; Thm 13.2 is as quoted by Goldston–Lee–Schettler–Suriajaya.
- **Simonič–Trudgian–Turnage-Butterbaugh.** A. Simonič, T. S. Trudgian, C. L. Turnage-Butterbaugh, "Some explicit and
  unconditional results on gaps between zeroes of the Riemann zeta-function", Trans. AMS (2021),
  https://arxiv.org/abs/2010.10675. FULL PDF text; Thm 2.
- **Goldston–Lee–Schettler–Suriajaya.** D. A. Goldston, J. Lee, J. Schettler, A. I. Suriajaya, "Pair correlation
  conjecture for the zeros of the Riemann zeta-function I", https://arxiv.org/abs/2503.15449 (v3, 2025). Read
  through §4 (eqs. 1.2, 3.3, 3.7).
- **Fujii 1975.** A. Fujii, "On the distribution of the zeros of the Riemann zeta function in short intervals", Bull.
  AMS 81 (1975) 139–142,
  https://www.ams.org/journals/bull/1975-81-01/S0002-9904-1975-13674-3/S0002-9904-1975-13674-3.pdf. OCR full text,
  but the formulas are illegible. No formula is attributed to it directly.
- **Hughes–Rudnick 2002.** C. P. Hughes, Z. Rudnick, "Linear statistics for zeros of Riemann's zeta function",
  C. R. Acad. Sci. Paris (2002), https://arxiv.org/abs/math/0208220. FULL text; §1, Thm 1.1, Thm 2.6 and its proof,
  Lemma 2.7.
- **Rodgers 2012.** B. Rodgers, "A central limit theorem for the zeroes of the zeta function",
  https://arxiv.org/abs/1205.0303. Abstract and §1, Thm 1.1 (Fujii's CLT).
- **Ghosh 1983.** A. Ghosh, "On the Riemann zeta function — mean value theorems and the distribution of |S(T)|",
  J. Number Theory 17 (1983) 93–102, https://www.sciencedirect.com/science/article/pii/0022314X83900100. Landing page
  only; content is as reported by Chirre–Quesada-Herrera.
- **Chirre–Quesada-Herrera.** A. Chirre, O. E. Quesada-Herrera, "The second moment of S_n(t) on the Riemann
  hypothesis", Int. J. Number Theory (2022), https://arxiv.org/html/2006.08503v2. §1.1–1.2 read.
- **Fazzari–Gerspach.** A. Fazzari, M. Gerspach, "The third moment of the logarithm of zeta and a twisted pair
  correlation conjecture", https://arxiv.org/abs/2412.20099. Abstract, §1 and Thm 1.1 read.
- **Conrey–Snaith 2008.** J. B. Conrey, N. C. Snaith, "Correlations of eigenvalues and Riemann zeros", Commun. Number
  Theory Phys. 2 (2008) 477–536. FULL text, from the local `specarith/ph2s/lit/CNTP.2008.v2.n3.a1.pdf`; Conj. 4.1
  (4.5), Thm 4.1, (4.64).
- **Bogomolny–Keating 2013.** E. Bogomolny, J. P. Keating, "A method for calculating spectral statistics based on
  random-matrix universality with an application to the three-point correlations of the Riemann zeros", J. Phys. A 46
  (2013) 305203, https://arxiv.org/abs/1307.6012. FULL text; §IV, eqs. 28–34.
- **Bogomolny–Keating 1995/1996.** *Nonlinearity* 8, 1115 and 9, 911. NOT OPENED.
- **Odd moments of S(t + h) − S(t).** Searched for directly; no source found.

---

## Appendix A — code (`nearres.py`, run with `/home/combust/fmexplorer/bin/python3`, numpy 2.4.4; sha256 prefix 14cf6ca9847e027b)

The full script is reproduced verbatim below, because the scratchpad copy does not survive a reboot.

```python
"""Near-resonant (off-diagonal) prime-triple contribution to the third moment of
DeltaS = S(t+h) - S(t), averaged over t in a window of width H (our derivation).

Model: S(t) ~ -(1/pi) sum_n Lambda(n) sin(t log n) / (sqrt(n) log n), n <= X.
DeltaS(tau) = sum_n b_n cos(tau log n), tau = t + h/2,
b_n = -(2/pi) Lambda(n)/(sqrt(n) log n) * sin(h log n / 2).
(DeltaS)^3 -> (1/4) sum_{n1,n2,n3} b1 b2 b3 [cos(tau(l1+l2-l3)) + 2 perms + cos(tau(l1+l2+l3))].
Window average of cos(omega tau + phi) over width H = cos(omega Tc + phi) sinc(omega H/2).
Random-phase model: RMS^2 over window centres = sum_omega (c_omega sinc)^2 / 2.
numpy only.
"""
import numpy as np, time, sys

PI = np.pi
TRAP = getattr(np, "trapezoid", None) or np.trapz
H = 2.1e6
L = 3.0
ELLS = [15.6, 17.5, 19.75, 21.25]          # log(t/2pi) of the four files
PMAX = 21_000_000                           # sieve limit for exact enumeration
ME = 20_000_000                             # m = n1 n2 enumerated exactly up to here
J = 24                                      # nearest prime powers on each side of m


def sieve(n):
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.nonzero(s)[0]


def sinc(x):
    return np.sinc(x / PI)                  # sin(x)/x


t0 = time.time()
P = sieve(PMAX)
print(f"primes <= {PMAX}: {len(P)}  ({time.time()-t0:.1f}s)")

# prime-power list (k = 1, 2) with log p, k
sq = P[P * P <= PMAX]
NV = np.concatenate([P, sq * sq]).astype(np.int64)
KV = np.concatenate([np.ones(len(P)), 2 * np.ones(len(sq))])
LP = np.concatenate([np.log(P), np.log(sq)])
o = np.argsort(NV); NV, KV, LP = NV[o], KV[o], LP[o]


def amp(h, lp, k):
    """b_{p^k} = -(2/pi) sin(h k log p / 2) / (k p^{k/2})"""
    return -(2 / PI) * np.sin(h * k * lp / 2) / (k * np.exp(k * lp / 2))


def exact_resonance(h, X):
    """sum over (p^a, p^b, p^{a+b}) triples: weight 3/4 (a=b) or 6/4 (a!=b)."""
    tot = 0.0; parts = {}
    lp = np.log(P[P <= 10**6]).astype(float)
    for a in range(1, 6):
        for b in range(a, 6):
            if a + b > 8:
                continue
            w = 0.75 if a == b else 1.5
            m = (a + b) * lp <= np.log(X)
            v = w * np.sum((amp(h, lp, a) * amp(h, lp, b) * amp(h, lp, a + b))[m])
            parts[(a, b)] = v; tot += v
    return tot, parts


def diag_var(h, X):
    """sum_n b_n^2 / 2 over prime powers n <= X: model Var(DeltaS) (diagonal)."""
    lp = np.log(P.astype(float)); s = 0.0
    for k in (1, 2, 3, 4):
        m = k * lp <= np.log(X)
        s += 0.5 * np.sum(amp(h, lp[m], k) ** 2)
    if X > PMAX:   # primes in (PMAX, X] by PNT density: sum b^2 ~ int (4/pi^2) sin^2(hu/2)/u du
        u = np.linspace(np.log(PMAX), np.log(X), 200001)
        f = (4 / PI**2) * np.sin(h * u / 2) ** 2 / u
        s += 0.5 * TRAP(f, u)
    return s


def enum_triples(h, Mmax, Hw, bands):
    """Exact enumeration: n1 <= n2 prime powers (k<=2), m = n1 n2 <= Mmax,
    n3 = the J nearest prime powers to m on each side (n3 != m).
    Returns variance contributions binned by |omega| H."""
    acc = np.zeros(len(bands) + 1)
    b_all = amp(h, LP, KV)
    nmax = int(np.searchsorted(NV, int(np.sqrt(Mmax)), side='right'))
    for i in range(nmax):
        n1 = NV[i]
        jhi = int(np.searchsorted(NV, Mmax // n1, side='right'))
        if jhi <= i:
            continue
        idx2 = np.arange(i, jhi)
        m = n1 * NV[idx2]
        c = np.where(idx2 == i, 0.75, 1.5)
        w12 = c * b_all[i] * b_all[idx2]
        pos = np.searchsorted(NV, m)
        offs = np.concatenate([np.arange(-J, 0), np.arange(0, J)])
        k3 = pos[:, None] + offs[None, :]
        k3 = np.clip(k3, 0, len(NV) - 1)
        n3 = NV[k3]
        valid = n3 != m[:, None]
        om = np.log1p((m[:, None] - n3) / n3.astype(float))
        w = w12[:, None] * b_all[k3] * sinc(om * Hw / 2)
        contrib = np.where(valid, 0.5 * w * w, 0.0)
        xb = np.abs(om) * Hw
        bi = np.searchsorted(bands, xb)
        acc += np.bincount(bi.ravel(), weights=contrib.ravel(), minlength=len(bands) + 1)
    return acc


def density_part(h, Mlo, Mhi, Hw, P1=10**5):
    """m in (Mlo, Mhi]: inner n3-sum by PNT density (sinc^2 integrated exactly):
    per unordered pair (n1<n2): (9/4)(1/2) b1^2 b2^2 * 8 sin^2(h log m/2)/(pi Hw log m).
    n1 exact primes <= P1, n2 by density; n1 > P1 both by density."""
    if Mhi <= Mlo:
        return 0.0
    lMlo, lMhi = np.log(Mlo), np.log(Mhi)
    def inner(u1, b1sq):                      # integrate over u2 >= u1, u1+u2 in (lMlo, lMhi]
        lo = max(u1, lMlo - u1); hi = lMhi - u1
        if hi <= lo:
            return 0.0
        u2 = np.linspace(lo, hi, max(2001, int((hi - lo) / 0.005)))
        f = (4 / PI**2) * np.sin(h * u2 / 2) ** 2 / u2 \
            * 8 * np.sin(h * (u1 + u2) / 2) ** 2 / (PI * Hw * (u1 + u2))
        return (9 / 8) * b1sq * TRAP(f, u2)
    tot = 0.0
    for p in P[P <= P1]:
        u1 = np.log(p)
        tot += inner(u1, amp(h, u1, 1) ** 2)
    # n1 > P1, density
    u1max = lMhi / 2
    if u1max > np.log(P1):
        u1g = np.linspace(np.log(P1), u1max, 400)
        vals = [inner(u1, 1.0) * (4 / PI**2) * np.sin(h * u1 / 2) ** 2 / u1 for u1 in u1g]
        tot += TRAP(vals, u1g)
    return tot


def pair_var_kappa2(h, X, Hw):
    """kappa2 analogue: unordered pairs n1 != n2 (primes), coefficient b1 b2 on
    cos(tau(l1-l2)); variance sum (b1 b2 sinc)^2/2. Exact for p <= min(X,PMAX),
    density for p in (PMAX, X]."""
    Pm = P[P <= min(X, PMAX)].astype(float)
    b = amp(h, np.log(Pm), 1)
    tot = 0.0
    for d in range(1, 4 * J):
        om = np.log(Pm[d:] / Pm[:-d])
        tot += np.sum(0.5 * (b[d:] * b[:-d] * sinc(om * Hw / 2)) ** 2)
    if X > PMAX:   # per p: (1/2) b_p^2 * sum_q b_q^2 sinc^2 ~ (1/2) b_p^2 (4/pi^2) s^2 (1/log p)(2 pi /Hw) ; /2 unordered
        u = np.linspace(np.log(PMAX), np.log(X), 20001)
        f = (4 / PI**2) * np.sin(h * u / 2) ** 2 / u * 0.5 * (4 / PI**2) * np.sin(h * u / 2) ** 2 \
            * (2 * PI / Hw) / u * 0.5
        tot += TRAP(f, u)
    return tot


bands = np.array([1.0, PI, 10.0, 100.0])
print("\n=== per height: h, X=T/2pi, diag Var(DeltaS), exact-resonance E3 ===")
for ell in ELLS:
    h = 2 * PI * L / ell; X = np.exp(ell)
    e3, parts = exact_resonance(h, X)
    print(f"ell={ell:5.2f} h={h:.4f} X={X:.3e}  Var_diag={diag_var(h, X):.4f}  "
          f"E3_exact={e3:+.5f}  (p,p,p^2)={parts[(1,1)]:+.5f}  (p,p^2,p^3)={parts[(1,2)]:+.5f}")

print("\n=== near-resonant triple RMS (random phase), H = %.2e ===" % H)
for ell in ELLS:
    h = 2 * PI * L / ell; X = np.exp(ell)
    t1 = time.time()
    Mx = min(X, ME)
    acc = enum_triples(h, Mx, H, bands)
    dens_in = density_part(h, Mx, X, H) if X > Mx else 0.0
    dens_x2 = density_part(h, max(Mx, X), X**2, H)
    dens_inf = density_part(h, max(Mx, X), 1e40, H)
    dens_chk = density_part(h, 1e6, Mx, H)           # density approx on the enumerated range (check)
    acc_chk = enum_triples(h, Mx, H, bands) if False else None
    var_cut = acc.sum() + dens_in
    print(f"ell={ell:5.2f}: enum m<={Mx:.2e}: var={acc.sum():.3e}  bands|w|H<1,<pi,<10,<100,>100: "
          + " ".join(f"{v:.2e}" for v in acc)
          + f"\n           density m in ({Mx:.1e},{X:.1e}]: {dens_in:.3e};  density check on (1e6,{Mx:.1e}]: {dens_chk:.3e}"
          + f"\n           RMS(cut X=T/2pi) = {np.sqrt(var_cut):.2e};  +extra to X^2: {dens_x2:.2e} -> RMS {np.sqrt(var_cut+dens_x2):.2e};"
          + f"  no cutoff: RMS {np.sqrt(var_cut+dens_inf):.2e}   ({time.time()-t1:.0f}s)")
    sys.stdout.flush()

print("\n=== scaling with window width (ell=19.75, cutoff X=T/2pi) ===")
ell = 19.75; h = 2 * PI * L / ell; X = np.exp(ell)
for Hw in [2.1e4, 2.1e5, 2.1e6, 2.1e7]:
    acc = enum_triples(h, min(X, ME), Hw, bands)
    v = acc.sum() + density_part(h, min(X, ME), X, Hw)
    print(f"H={Hw:.1e}: RMS={np.sqrt(v):.3e}  RMS*sqrt(H)={np.sqrt(v*Hw):.3f}")

print("\n=== kappa2 analogue (pairs p1 != p2), H=2.1e6 ===")
for ell in ELLS:
    h = 2 * PI * L / ell; X = np.exp(ell)
    v = pair_var_kappa2(h, X, H)
    vinf = pair_var_kappa2(h, X**2, H)
    print(f"ell={ell:5.2f}: RMS(kappa2 offsets, cut X)={np.sqrt(v):.2e}; cut X^2: {np.sqrt(vinf):.2e}")
print(f"total {time.time()-t0:.0f}s")
```

## Appendix B — raw output (excerpt, verbatim)

```
ell=15.60 h=1.2083 X=5.957e+06  Var_diag=0.3178  E3_exact=-0.01577  (p,p,p^2)=-0.01019  (p,p^2,p^3)=-0.00366
ell=17.50 h=1.0771 X=3.982e+07  Var_diag=0.3214  E3_exact=-0.01405  (p,p,p^2)=-0.00899  (p,p^2,p^3)=-0.00318
ell=19.75 h=0.9544 X=3.778e+08  Var_diag=0.3250  E3_exact=-0.01217  (p,p,p^2)=-0.00777  (p,p^2,p^3)=-0.00268
ell=21.25 h=0.8870 X=1.693e+09  Var_diag=0.3272  E3_exact=-0.01103  (p,p,p^2)=-0.00706  (p,p^2,p^3)=-0.00238
ell=15.60: enum m<=5.96e+06: var=4.509e-10  bands|w|H<1,<pi,<10,<100,>100: 4.74e-12 1.87e-10 1.59e-10 8.45e-11 1.59e-11
           density check on (1e6,6.0e+06]: 4.922e-10
           RMS(cut X=T/2pi) = 2.12e-05;  +extra to X^2 -> RMS 5.15e-05;  no cutoff: RMS 6.72e-05
ell=17.50: enum m<=2.00e+07: var=9.724e-10  bands: 1.40e-10 5.03e-10 2.22e-10 9.16e-11 1.68e-11
           density m in (2.0e+07,4.0e+07]: 2.524e-11;  density check on (1e6,2.0e+07]: 1.135e-09
           RMS(cut X=T/2pi) = 3.16e-05;  X^2: 5.47e-05;  no cutoff: 6.75e-05
ell=19.75: enum var=6.589e-10  bands: 1.11e-10 3.28e-10 1.35e-10 6.84e-11 1.68e-11
           density m in (2.0e+07,3.8e+08]: 6.571e-10;  density check: 8.020e-10
           RMS(cut X=T/2pi) = 3.63e-05;  X^2: 5.58e-05;  no cutoff: 6.63e-05
ell=21.25: enum var=4.289e-10  bands: 6.91e-11 1.86e-10 8.34e-11 7.40e-11 1.65e-11
           density m in (2.0e+07,1.7e+09]: 9.739e-10;  density check: 4.212e-10
           RMS(cut X=T/2pi) = 3.75e-05;  X^2: 5.56e-05;  no cutoff: 6.49e-05
H=2.1e+04: RMS=5.501e-04 ; 2.1e+05: 1.364e-04 ; 2.1e+06: 3.628e-05 ; 2.1e+07: 9.200e-06
kappa2: ell=15.60 1.24e-05 (X^2: 4.01e-05); 17.50 2.41e-05 (4.34e-05); 19.75 3.12e-05 (4.61e-05); 21.25 3.23e-05 (4.60e-05)
total 151s
```

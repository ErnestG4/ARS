<!-- Provenance: targeted search for the depth second-order term (Will, 2026-10-28). Drafted by a literature agent;
filed unedited below. Main-session check: Panov, Mat. Zametki 32(5) (1982), p. 594 read from the scanned page — eq. (9)
c_i = (1/(2−i)!) Σ_{l+h+q=i} [2/(l!h!q!)] γ^l 2^h b_h d_q (b_h = (1/ζ)^{(h)}(2), d_q = (1/Γ)^{(q)}(2), c₀ = 6/π²) and
Theorem 2, eq. (10), H(N) = c₀φ ln²N + c₁φ ln N + (c₂ + 1)φ + 2c₀φ Σ_{p|N} p(p−1)⁻²(1 − p^{−α(p)}) ln²p + O(N^{7/8+ε}).
CONFIRMED. Evaluating eq. (9) at i = 1 by hand: c₁ = (6/π²)(4γ − 2) − 4ζ′(2)/ζ(2)² = (12/π²)(2γ − 1 − 2ζ′(2)/ζ(2))
= 1.5737449. So the 1.574 ln q term is Panov's c₁ (1982); the "no published fixed-q source" wording in commit e7952706 /
GEOTOT1_PP_STEP0.md §5 is superseded. TAOCP §4.5.3 remains unread (no legitimate copy reached). -->

# DEPTH-TERM literature search: second coefficient β of the fixed-q mean of S(a/q)

**Short answer: yes, β is published, and it matches ours exactly.** A. A. Panov, "О среднем для суммы элементов по одному классу конечных непрерывных дробей", *Mat. Zametki* 32(5) (1982) 593–600 (Engl. *Math. Notes* 32 (1982) 781–785, doi 10.1007/BF01358470), gives a three-term formula for the coprime, fixed-N sum with explicit constants. Evaluating his c₁ gives exactly (12/π²)(2γ − 1 − 2ζ′(2)/ζ(2)) = 1.5737449203. His constant term gives our residual constant too. The prior search missed it because the paper is in Russian and later citers write "A₁, absolute constant".

## 1. Panov 1982: VERIFIED (scanned PDF from mathnet.ru, pp. 593–594, eqs. (2), (7)–(10))
- **Set and sum.** D(N) = {k/N : 1 ≤ k ≤ N, (k,N) = 1}, so the average is coprime and N is fixed. H(N) = Σ_{D(N)} Σ_{1≤i≤l} a_i, and the proof uses the canonical last quotient a_l ≥ 2 (eq. (12)).
- **Theorem 1 (eq. 7).** H(N) = φ(N) + s(N). Here s(N) counts solutions of N = xx′ + yy′ in naturals with (x,y) = (x′,y′) = 1. The proof shows Σ_k [h(k,N) − 1] = s(N). This is exactly the Stern–Brocot-depth sum.
- **Estermann input (eq. 8).** S(N) = N Σ_{d|N} d⁻¹ [c₀ ln²(N/d) + c₁ ln(N/d) + c₂] + O(N^{7/8+ε}).
  - The print reads "c₀ ln(N/d²)". I read it as a misprint for ln²(N/d), and the numerical check below supports that reading.
  - **Eq. (9).** c_i = (1/(2−i)!) Σ_{l+h+q=i} (2/(l! h! q!)) γ^l 2^h b_h d_q, with b_h = (1/ζ)^{(h)}(2) and d_q = (1/Γ)^{(q)}(2). The paper states c₀ = 6/π².
- **Theorem 2 (eq. 10).** H(N) = c₀φ(N) ln²N + c₁φ(N) ln N + (c₂+1)φ(N) + 2c₀φ(N) Σ_{p|N} p(p−1)⁻²(1 − p^{−α(p)}) ln²p + O(N^{7/8+ε}).
- **c₁ evaluated (INFERENCE: my evaluation of the VERIFIED eq. (9)).** c₁ = 2[γb₀d₀ + 2b₁d₀ + b₀d₁], with b₀ = 1/ζ(2), b₁ = −ζ′(2)/ζ(2)², d₀ = 1 and d₁ = γ − 1. So c₁ = (2/ζ(2))(2γ − 1 − 2ζ′(2)/ζ(2)) = **1.573744920**, identical to our β to all digits (mpmath, 30 digits).
- **c₂ evaluated (INFERENCE).** c₂ = −1.524384, so c₂ + 1 = **−0.524384**.
  - For prime q the divisor term is 2c₀ ln²p/(p−1) → 0. The predicted constant is therefore −0.5244 for Σa_i and −1.5244 for the depth Σa_i − 1.
  - Our fit gave −0.528 / −1.528, which is consistent given the ±0.001 uncertainty on β multiplied by ln q ≈ 10–15.
- **Numerical check (mine, exact enumeration, scratch only).**
  - Primes 100003, 200003, 500009 and 1000003: mean minus Panov prediction = −9.6e−4, +1.3e−4, +4.5e−5, +2.9e−4.
  - Composites 317², 331², 2¹⁷, 3¹¹, 210210 and 510510, with the divisor term included (it is 0.12–4.8 here): residuals within ±0.008.
- **Prime-power note (relevant to GEO-TOT).** For N = p^k the Panov divisor term is 2c₀ p(p−1)⁻²(1 − p^{−k}) ln²p, which is about 2c₀ ln²p/p for p². It has a closed form, and this paper is a published source for it. I have not checked whether it relates to the c_N q/φ(q) "excess" quantity.

## 2. Other sources
- **Panov 1980**, *Uspekhi Mat. Nauk* 35(4) 201–202 (announcement): VERIFIED (p. 201, Thms 1–2). It gives the same form with "A₁, A₂, A₃ absolute constants" and no values. Theorem 4: S_n(p) ~ 2p ζ(n)/ζ(2n) for Σa_iⁿ, n > 1, p prime.
- **Popov 1979**, *Zap. Nauchn. Sem. LOMI* 91, 81–93: VERIFIED (p. 81 eq. (1); p. 90 eqs. (39)–(40)). This is the fixed-prime result: Σ_{a=1}^{p−1} Σa_i = (6/π²) p ln²p + O(p ln p), with no second term. Eqs. (39)–(40) state, without proof, ≃ (6/π²)φ(q) ln²q (coprime) and ≃ (6/π²) q ln²q (all a).
- **Zhabitskaya 2011**, *Mat. Zametki* 89(3) 472–476: VERIFIED (pp. 472–473).
  - Quotes Knuth for the all-a mean (1/b)Σ_{a≤b} s(a/b) = (6/π²) log²b + O(log b (log log b)²).
  - Quotes Panov's three-term coprime formula with "A₁, A₂ absolute constants" (no value) and error O(b^{7/8+ε}/φ(b)).
  - Her own results are double (Farey) averages for s₁ and s₂. Her Thm 2 C₁ is the source of our derivation.
- **Minelli–Sourmelidis–Technau**, arXiv 2301.00441: VERIFIED (p. 4, eq. (1.5)). It gives the Farey-averaged C₂ = (1/ζ(2))(2γ − 3/2 − 2ζ′(2)/ζ(2)) for the minus-CF length, and Myerson's lemma (1.6). Fixed denominator is not treated.
- **Aistleitner–Borda–Hauke**, arXiv 2210.14095v2: VERIFIED (p. 2, eq. (1)). It states only (1/φ(N)) Σ S(a/N) ~ (6/π²)(log N)², attributes it to Panov and Liehl "independently", and points to Knuth's book, Section 4.5. No second term.
- **Yao–Knuth 1975**, PNAS 72, 4720: VERIFIED (abstract only, via PMC). Σ over all 1 ≤ m ≤ n of the partial-quotient sums = 6π⁻² n(ln n)² + O(n log n (log log n)²). No second term.
- **Porter 1975** (length, not sum): SECONDARY (quoted in Panov eq. (6)). L(N) = (12 ln 2/π²) φ(N) ln N + Aφ(N) + O(N^{5/6+ε}).
- **Estermann 1930**, Proc. LMS (2) 31: the origin of c₁ and c₂. SECONDARY via Panov; not read.
- **UNVERIFIED (content not reached):**
  - Liehl 1983, *Arch. Math.* 40, 139–147.
  - Zheng Zhiyong 1994, *Acta Math. Sinica* 37(2), 191–202, "On a theorem of Yao and Knuth" (said to "improve" Yao–Knuth; only bibliographic records found).
  - Vallée, Baladi–Vallée, Bettin–Drappeau and Avdeeva–Bykovskii. These were not read for this question. Their published scope is Farey or double averages, distributions, or moderate-growth costs; that last point is an INFERENCE.

## 3. Knuth TAOCP vol. 2, §4.5.3: UNVERIFIED
- §4.5.3 "Analysis of Euclid's Algorithm" starts at p. 356 of the 3rd edition (VERIFIED from the publisher-preview table of contents).
- I could not read the section text, its exercises or its answers. Google Books API quota was exhausted. The only full copies found were unauthorized uploads, which I did not use.
- So I cannot give the exercise number or confirm the exact wording. Secondary sources (ABH, Zhabitskaya 2011) say only that Knuth discusses the Yao–Knuth all-m result. None quotes a second-order term from Knuth.

## Bottom line
- β is stated in closed form, and is equivalent to (12/π²)(2γ − 1 − 2ζ′(2)/ζ(2)), in Panov 1982, eqs. (9)–(10). It is c₁ from Estermann's divisor-problem expansion. The match is exact: my evaluation of his eq. (9) agrees to 30 digits.
- The constant term c₂ + 1 = −0.5244 is also published in that closed form. It agrees with our fitted −0.528.
- β should be cited to Panov 1982, not as "no published fixed-q source". The 1.574 sentence in commit e7952706 is now superseded.
- Files: the downloaded PDFs and text are in /tmp/claude-1000/-home-combust-fmexplorer-criticality-tool--claude-worktrees-ph6-xp/a91f0f2e-c26b-4e53-81dc-2feedac9a4b5/scratchpad/lit_depth/. The key ones are mzm5989.pdf (Panov 1982), rm3789.pdf (Panov 1980), znsl3178.pdf (Popov 1979) and mzm9054.pdf (Zhabitskaya 2011).

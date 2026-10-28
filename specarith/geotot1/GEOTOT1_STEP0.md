> **Provenance.** Drafted by a literature subagent (2026-10-27; literature only), filed unedited below this note.
> Spot-checked by the main session against primary pages: OEIS A375066 (κ = 0.51606240889999180681…, Lhote 2004 eq.
> 1.8; Hensley 1994), A195901 (data 6, 54, 150; "No other terms below 10^7", Pawlik, Mar 04 2026) and A141822 (PARI
> `contfrac`, i.e. the canonical form). The seen-range enumeration (results/SEEN_RANGE.json) independently reproduces
> the canonical {6, 54, 150}, the existential {54, 150}, the 31.54 = Σa_i − 1 depth at q = 360, and dVar(L)/d ln q ≈
> 0.517 on q ≤ 2000. Items tagged SECONDARY / UNVERIFIED / INFERENCE keep that status.

# GEO-TOT1 step 0: literature check (continued fractions, Zaremba, E_N counts)

Date 2026-10-27. Literature only. The only computation was trivial arithmetic: a few
one-line checks over at most a few hundred fractions, each labelled **[trivial check]**.

Tags:
- **VERIFIED**: I read the statement in the primary source; the location is given.
- **SECONDARY (via X)**: I saw the claim only as quoted by X.
- **UNVERIFIED**: no source read.
- **INFERENCE**: my own algebra on verified statements. It is not in any source.

Sources read (arXiv versions unless stated):
- [ABH] Aistleitner, Borda, Hauke, "On the distribution of partial quotients of reduced fractions with fixed denominator", arXiv:2210.14095v2; Trans. AMS 377 (2024) 1371–1408.
- [BK] Bourgain, Kontorovich, "On Zaremba's conjecture", arXiv:1107.3776v2; Annals of Math. 180 (2014).
- [Hu] Huang, "An improvement to Zaremba's conjecture", arXiv:1310.3772v4; GAFA 25 (2015) 860–914.
- [MOW] Magee, Oh, Winter (appendix by Bourgain, Kontorovich, Magee), "Uniform congruence counting for Schottky semigroups in SL2(Z)", arXiv:1601.03705v3; Crelle.
- [Ko] Kontorovich, "From Apollonius to Zaremba", arXiv:1208.5460; Bull. AMS 50 (2013) 187–228.
- [BD] Bettin, Drappeau, "Limit laws for rational continued fractions and value distribution of quantum modular forms", arXiv:1903.00457v2.
- [BV] Baladi, Vallée, "Euclidean algorithms are Gaussian", arXiv:cs/0307062; J. Number Theory 2005.
- [JP18] Jenkinson, Pollicott, "Rigorous effective bounds on the Hausdorff dimension of continued fraction Cantor sets: a hundred decimal digits for the dimension of E2", arXiv:1611.09276; Adv. Math. 2018.
- [JP20] Jenkinson, Pollicott, "Rigorous dimension estimates for Cantor sets arising in Zaremba theory", Contemp. Math. 744 (2020) 83–107. Read as the accepted manuscript, WRAP 117105.
- [PV] Pollicott, Vytnova, "Hausdorff dimension estimates applied to Lagrange and Markov spectra, Zaremba theory, and limit sets of Fuchsian groups", arXiv:2012.07083v3.
- [FN] Falk, Nussbaum, "C^m eigenfunctions of Perron–Frobenius operators … applications in R^1", arXiv:1612.00870v2.
- [Hen94] Hensley, "The distribution mod n of fractions with bounded partial quotients", Pacific J. Math. 166 (1994) 43–54. Read as the MSP PDF; the OCR of the displayed formulas is partly garbled.
- [Ust08] Ustinov, "Asymptotic behaviour of the first and second moments for the number of steps in the Euclidean algorithm", Izvestiya Math. 72:5 (2008) 1023–1059.
- [MST] Minelli, Sourmelidis, Technau, "On restricted averages of Dedekind sums", arXiv:2301.00441; IMRN 2024.
- [Lh] Lhote, "Computation of a class of continued fraction constants", ALENEX/ANALCO 2004, HAL hal-00263891. Read as full text through a fetch tool.
- [YK] Yao, Knuth, PNAS 72(12) (1975) 4720–4722. Only the abstract on PMC388801 could be read. The PDF is a scanned image behind a bot wall.
- OEIS entries A141822, A141823, A141832, A141833, A195901 and A375066, read 2026-10-27.

---

## 1. Yao–Knuth and the mean depth

**1a. Statement (VERIFIED, abstract only; [YK] PMC388801 abstract).**
"The sum of all partial quotients in the regular continued fraction expansions of m/n, for 1 ≤ m ≤ n, is shown to be 6π⁻² n (ln n)² + O(n log n (log log n)²)."
- The average is over **all** m with 1 ≤ m ≤ n, with no coprimality condition. [ABH] p.2 confirms this: Yao and Knuth treat "the average over all 1 ≤ a ≤ N (without the coprimality condition)".
- The mean is therefore (6/π²)(ln n)² + O(log n (log log n)²).
- The abstract gives no explicit second-order term.
- The paper body (convention for m = n, and any explicit constants) is UNVERIFIED, because the scan could not be read.

**1b. Coprime average (SECONDARY via [ABH] eq. (1), p.2).** Panov (Mat. Zametki 32 (1982) 593–600) and Liehl (Arch. Math. 40 (1983) 139–147) showed independently that
(1/φ(N)) Σ_{a∈Z*_N} S(a/N) ~ (6/π²)(log N)².
- [ABH] quote only "~". The error terms of Panov and Liehl are UNVERIFIED.
- [ABH] convention: a_r > 1 (canonical), and Z*_N = {1 ≤ a ≤ N, (a,N) = 1}.

**1c. Explicit second-order terms.** I found none for a **fixed** denominator; that is UNVERIFIED and possibly open. There is one for the Farey (double) average:
- VERIFIED: [MST] p.4 eq. (1.5), quoting Zhabitskaya (Sb. Math. 200 (2009) 1181–1214; SECONDARY for Zhabitskaya). Let ℓ(x) be the length of the minus (by-excess) continued fraction and F(Q) = {v/w ∈ [0,1], w ≤ Q}. Then
  (1/#F(Q)) Σ_{x∈F(Q)} ℓ(x) = C1 log²Q + C2 log Q + C3 + O(log⁶Q/Q),
  with C1 = 1/(2ζ(2)) and C2 = (1/ζ(2))(2γ − 3/2 − 2ζ′(2)/ζ(2)).
- VERIFIED: [MST] eq. (1.6), Myerson's lemma: ℓ(x) = Σ_odd(x) − ε(x) and ℓ(1−x) = Σ_even(x) + ε(x).
- **INFERENCE.** Add the two halves of Myerson's lemma and sum over the symmetric set F(Q). The Farey mean of the depth S is then
  2C1 log²Q + 2C2 log Q + O(1) = (6/π²) log²Q + 0.9658 log Q + O(1).
  - 2C2 = (12/π²)(2γ − 3/2 − 2ζ′(2)/ζ(2)) = 1.2159 × 0.79435 = 0.9658.
  - Converting to a fixed-q average α log²q + β log q, with the weights φ(q) ≈ q over q ≤ Q, gives β − α = 2C2, so β ≈ 0.9658 + 0.6079 = **1.574**.
  - This ignores any dependence of the fixed-q mean on the arithmetic of q.
- MaRDI/zbMATH review of Zhabitskaya, Math. Notes 2011 (SECONDARY): the double averages of odd-index and even-index partial-quotient sums are E(R) ± 1/2 + O(R⁻¹), both with and without coprimality.
- About Vardi: Vardi (IMRN 1993) is the limiting **Cauchy** law for Dedekind sums ([ABH] p.4; [BD] Thm 2.7). It is not a refinement of the Yao–Knuth mean.

**1d. The gap at q = 360 (31.5 against 21.06).**
- The leading term (6/π²)(ln 360)² = 0.60793 × 34.646 = **21.06** **[trivial check]**.
- **Convention offset [trivial check].** With S = Σ a_i (canonical), the mean over the φ(360) = 96 coprime a in 1..359 is **32.54** and the median is 21. The value 31.5 equals S − 1. So "depth" in the notes is evidently Σa_i − 1, which is consistent with "a = 1 gives depth q − 1": with S, 1/q = [0;q] has S = q.
  - Σa_i is identical under [..., a_k] and [..., a_k − 1, 1], so the choice of last-quotient convention does not move S. Only the length L moves, by 1.
  - The Yao–Knuth all-m average at n = 360 (m = 1..360) is **21.90** **[trivial check]**. It is close to the leading term because it is diluted by the small denominators n/gcd.
- **Lower-order terms (INFERENCE).**
  - 21.06 + 1.574 × ln 360 = 21.06 + 9.26 ≈ **30.3**, before an O(1) constant and before q-arithmetic effects.
  - So most of the gap of about 11.5 is the expected log q term. The second-order term is large at q = 360 because log q is only 5.9.
- **Arithmetic and heavy tail [trivial check].**
  - a = 1 and a = q − 1 each have S = q. Together they add 2q/φ(q) = 720/96 = **7.5** to the coprime mean.
  - q/φ(q) depends on the factorisation (3.75 for 360), so fixed-q lower-order terms are not smooth in log q. Highly composite q are inflated relative to primes.
  - This does not make the term extra to the asymptotic. It is a q/φ(q) = O(log log q) contribution inside the lower-order terms.
- **Heavy tail (VERIFIED, [ABH] p.2 and Thm 1).** The typical size is (12/π²) log N log log N = 12.69 at N = 360 **[trivial check]**. The mean of order (log N)² comes from a small proportion of fractions with large partial quotients ("heavy-tailed").
  - So the gap between the mean (≈ 32.5) and the median (21) is expected.
  - **The mean is the wrong summary statistic for a per-q depth law. Use the median or a trimmed mean, or centre with BD/ABH (item 6).**

## 2. δ_N for N = 2..6

All five values requested are consistent with the sources.

| N | value as printed | source and location | status |
|---|---|---|---|
| 2 | 0.5312805062 7720514162 4468647368 4717854930 5910901839 8779888397 … ± 10⁻²⁰¹ | [PV] Thm 1.5, p.2 (100 digits in [JP18] p.3, rigorous) | VERIFIED |
| 2 | bracketed 0.53128050598142 to 0.53128050632077 (and finer) | [FN] tables, p.~20 | VERIFIED (consistent) |
| 3 | 0.7056609080 2873823060 7 (± 10⁻²⁰) | [PV] Table 3, p.47, row {1,2,3} | VERIFIED |
| 4 | 0.7889455574 83 ± 10⁻¹²; table 0.7889455574 8315397254 0 (± 10⁻²⁰) | [PV] Thm 4.14, p.33; Table 3 | VERIFIED |
| 5 | 0.836829443680 ± 10⁻¹²; table 0.8368294436 8120882244 2 (± 10⁻²⁰) | [PV] Thm 4.12, p.32; Table 3 | VERIFIED |
| 5 | rigorous (0.83682944, 0.83682945); periodic-point value 0.8368294436812 | [JP20] Thm 8 and Table 2, §5 | VERIFIED |
| 6 | **0.8676191732 4015 ± 10⁻¹³** | [PV] Thm 4.22, p.36 | VERIFIED |
| 6 | rigorous (0.8676191, 0.8676192); periodic-point value 0.8676191732401 | [JP20] Thm 9 and Table 3, §6 | VERIFIED |

- The checked values hold: δ_2 = 0.5312805…, δ_3 = 0.7056609…, δ_4 = 0.7889455…, δ_5 = 0.8368294…. And **δ_6 = 0.86761917324…**.
- **Inconsistency inside [PV].** Table 4, p.48, row {1,…,6} prints 0.8676191730 6718378091 2243 (± 2·10⁻²⁴). That disagrees with their own Thm 4.22 and with [JP20] from the 10th decimal on. Treat the Table 4 row as a typo and use 0.86761917324015.
  - A minor one: the [PV] Thm 4.12 interval for δ_5 (0.836829443680 ± 10⁻¹²) sits about 2·10⁻¹³ below the Table 3 value. That is immaterial.
- Hensley's older values (SECONDARY):
  - Via [PV] Table 3 (attributed there to Hensley 1992, JNT 40): 0.5312805062 772051416, 0.7056609080, 0.788946, 0.8368294437.
  - Via [Lh] §1.6 (attributed to Hensley 1996): s_{1,2} ≈ 0.5312805062772051416.
  - Via [JP20] fn. 3 (Hensley 1996 p.16): 0.8368294437, "first 9 digits correct, final digit rounded up".
- Jenkinson 2004 (Texan conjecture, Stoch. Dyn. 4, 63–76): only its 4-digit estimates are visible, as quoted in [PV] Table 4 (e.g. 0.8676 for {1..6}). SECONDARY.
- Useful asymptotic (VERIFIED as quoted in [BK] (1.12) and [Hu] (1.3), from Hensley 1992):
  δ_{1..A} = 1 − 6/(π²A) − 72 log A/(π⁴A²) + O(1/A²).
- Exponents for later use **[trivial check]**:
  - 2δ_N − 1 = 0.06256, 0.41132, 0.57789, 0.67366, 0.73524 for N = 2..6.
  - 2δ_N − 2 = −0.93744, −0.58868, −0.42211, −0.32634, −0.26476.

## 3. The cumulative count #{a/q : q ≤ Q, all a_i ≤ N}

- **Up to constants (VERIFIED as cited; SECONDARY for Hensley 1989 itself).**
  - [BK] Remark 1.13 (p.4), citing Hensley 1989 (Théorie des nombres, Québec 1987, de Gruyter, 371–385): R_A(N) = {b/d ∈ R_A : (b,d) = 1, 0 < b < d < N} has #R_A(N) ≍ N^{2δ_A}.
  - Bourgain, CRAS 2011 (arXiv:1103.0422) states the same as two-sided bounds c·N^{2δ_A} < #{p/q ∈ R_A, 1 ≤ p < q ≤ N} < C·N^{2δ_A}. Bourgain's CRAS density-one result had A = 2189.
- **Asymptotic with a constant.**
  - VERIFIED: [Hen94] §1, p.44. "the number of such fractions, with denominator d < x, is given asymptotically by C_m x^{D(m)} where C_m, D(m) > 0. As D(m) ≈ 1.06256 for m = 2 …". This cites Hensley 1989 [3] and Hensley 1990 [4].
    - D(2) = 2δ_2 = 1.062561 **[trivial check]**.
    - [Hen94] Lemma 1 (from [4]) gives lim x^{−D(m)} #F_m(x,u) = K(m)·(…) for sequences with a fixed prefix.
  - SECONDARY (via the zbMATH/MaRDI review of Hensley, "… II", J. Number Theory 34 (1990) 293–334), Theorem 1: lim_{x→∞} x^{−2E_n} Q_n(x) = C_n, where E_n = dim E_n.
- **The set counted ([Hen94] eq. (2), VERIFIED).** Q_m(x) = {c/d : 0 < c < d < x, gcd(c,d) = 1, c/d = [0; v_1..v_r], 1 ≤ v_i ≤ m, v_r > 1}.
  - The last quotient is canonical (≥ 2).
  - The count is of pairs (c,d), with each reduced fraction counted once, over all denominators d < x.
  - [Hen94] p.47 notes explicitly that digit sequences ending in "m, 1" correspond to fractions whose final quotient is m+1. **The "exists a representation" set is therefore strictly larger than Q_m**, and it also has asymptotic order x^{2δ}.
- The [BK] definition of R_A ("b/d = [a_1..a_k] with all a_j ∈ A") and the [MOW] definition (R_A := {[a_1..a_k] : k ∈ N, a_i ∈ A}) are existential.
- Matrix norm-ball count (VERIFIED, [MOW] Thm 1 and Thm 2, p.2): #(Γ_A(q) ∩ B_R) = c_Γ R^{2δ}/#SL₂(Z/q) + O(q^C R^{2δ−ε}), for q coprime to some Q_0.
  - This is an asymptotic with a power saving.
  - With q = 1 it counts matrices of Γ_A = G_A ∩ SL₂ (even-length words) by Frobenius norm. It does not count fractions by denominator.

## 4. A per-q law with local factors

**4a. Hensley's conjecture as recorded (SECONDARY via [BK] Conj. 1.3, p.2, citing Hensley 1996, J. Number Theory 58, Conjecture 3, p.16).** "The set of denominators D_A contains every sufficiently large integer if and only if δ_A > 1/2."
- This is a **set** statement. I found no Hensley statement of the form #{a : a/q ∈ E_N} ~ c_N(q) q^{2δ_N−1}. **UNVERIFIED as a Hensley attribution.**

**4b. Status and the counterexample (VERIFIED, [BK] p.2–3, (1.4), Remarks 1.17 and 1.31).**
- Hensley's conjecture "is false": A = {2,4,6,8,10} has δ_A ≈ 0.517 > 1/2, yet D_A (mod 4) ⊆ {0,1,2}.
  - [JP20] §4 proves rigorously that dim E_{2,4,6,8,10} > 1/2 (empirically 0.5173570309…).
- **The premise "it fails for N = 2 because δ_2 < 1/2" is wrong.** δ_2 = 0.53128 > 1/2.
  - For {1,2} there are no local obstructions: the bad modulus is B = 1 and Γ_A mod q = SL₂(q) for all q ([BK] Remark 1.31).
  - Hensley's conjecture for {1,2}, i.e. D_2 ⊇ all large integers, is **open** ([BK] Remark 1.17; [Ko] (2.9)).
  - [Hen94] p.45: for m = 2 the exponent 1.06256 is "barely sufficient", and "the heuristic … predicts no early end of exceptions".
- The replacement conjecture ([BK] Conj. 1.7): if δ_A > 1/2, D_A contains every sufficiently large **admissible** integer. Admissible means passing every congruence obstruction, and this is checkable with one modulus q(A).
- For {1,…,A} with A ≥ 2 every integer is admissible ([BK] Remark 1.17). [PV] Thm 4.11, after Huang, records this for {1..5}.

**4c. Size and local factors of the multiplicity (VERIFIED; the simplification is INFERENCE).**
- The heuristic size: [BK] p.7 (1.34). Almost every d ≍ N "should occur with multiplicity roughly N^{2δ−1}".
- The circle-method main term ([BK] p.7 and eq. (4.33), p.~26) is M_N(d) ~ 𝔖(d) Π_N(d), with Π_N(d) ≫ N^{2δ−1}. In the no-obstruction case:
  𝔖(d) = Π_{p∤d}(1 + 1/(p²−1)) · Π_{p|d}(1 − 1/(p+1)).
  - **INFERENCE (two lines of algebra):** 1 + 1/(p²−1) = p²/(p²−1), and (1 − 1/(p+1))/(p²/(p²−1)) = (p−1)/p. Hence
    **𝔖(d) = ζ(2) · φ(d)/d.**
  - So the predicted per-denominator multiplicity is ∝ (φ(q)/q) q^{2δ−1}. Equivalently, the fraction of the φ(q) coprime numerators that lie in the set is ∝ q^{2δ−2}, with no further dependence on q mod small numbers beyond φ(q)/q.
  - This is a main-term heuristic only. BK prove multiplicity lower bounds, not this asymptotic.
- **Proven residue-class version (VERIFIED, [Hen94] abstract and Thm 1, Cor. 1–3).**
  - For every m ≥ 2 and n ≥ 1, the matrices Γ_n(c/d) (all classes of determinant ±1 mod n) are asymptotically equidistributed over Q_m(x).
  - Corollary: the relative frequency of d ≡ b (mod n) in Q_m(x) is n⁻¹ Π_{p|gcd(b,n)}(1 − p⁻¹) · Π_{p|n}(1 − p⁻²)⁻¹. The OCR is garbled; this is my reconstruction, and it passes the normalisation check Σ_b = 1 for n = p **[trivial check]**.
  - The same local factor Π_{p|d}(1 − 1/p) as 𝔖(d) appears here, so the BK and Hensley pictures agree.
  - [Hen94] p.44 cautionary example: for the alphabet {16, 21} and n = 30, only 480 of the 576 admissible residue pairs occur. Local obstructions are real for general alphabets.
- **Proven multiplicity bounds (VERIFIED).**
  - [BK] Thm 1.8: each d produced has multiplicity ≫ N^{2δ_A − 1001/1000}.
  - [Hu] Thm 1.6 (1.5): ≫ N^{2δ_A − 1 − r} for 0 < r < (δ_A − 5/6)/9.
- **Status.** A per-q asymptotic #{a : a/q ∈ E_N} ~ c_N(q) q^{2δ_N−1} for **fixed** q is not proven in any source I read. Its main-term heuristic, ζ(2)(φ(q)/q) × (archimedean factor), follows from [BK] (4.33).

## 5. Zaremba: density one, exception lists, convention

**Density-one and related theorems (VERIFIED unless marked).**
- **[BK]** Thm 1.2 and Thm 1.8 (Annals 2014):
  - If δ_A > δ_0 = 307/312 ≈ 0.984, then D_A contains almost every admissible integer, with #(D_A ∩ [N/2,N]) / #(A_A ∩ [N/2,N]) = 1 + O(N^{−c/log log N}).
  - {1..50} has δ ≈ 0.986, so A = 50.
  - Thm 1.25: infinitely many primes d with primitive roots b such that b/d is absolutely Diophantine.
- **Frolenkov–Kan** (arXiv:1303.3968): a positive proportion when δ_A > 5/6. SECONDARY via [BK] Remark 1.20 and [Hu] Thm 1.5.
- **[Hu]** Thm 1.6: density one, with 1 + O(e^{−c√log N}), whenever δ_A > 5/6. Since δ_5 = 0.8368 > 5/6, **A = 5 has density one**.
- **Kan**, Proc. Steklov 296 (2017): a positive proportion for {1,2,3,4}, conditional on dim E_4 > (√19 − 2)/3 ≈ 0.7863. [PV] Thm 4.14 confirms that bound (SECONDARY via [PV] Thm 1.7, p.6).
- **[MOW]** p.3, (1.2): combining BK, Huang and their uniform congruence counting gives #D_{1..5} ∩ [1,N] = N + O(N^{1−ε}). This is stated as derivable, not written out in full. They also mention a short alternative argument by Bourgain.

**Exception lists (OEIS, read directly).** A141822(n) is the minimum over coprime k of the largest canonical partial quotient of k/n.
- The PARI program uses `contfrac`, i.e. the canonical expansion.
- The b-file covers n ≤ 10⁴ (Robin Visser; T. D. Noe for n ≤ 2000).

| OEIS | content | data and search range stated |
|---|---|---|
| A195901 | n with a(n) = 5 | 6, 54, 150. "No other terms below 10^6"; "No other terms below 10^7" (B. Pawlik, Mar 04 2026). Cites [Ko]. |
| A141823 | n with a(n) = 4 | 20, 28, …, 3618, 5052, 6234 (35 terms). "No other terms below 10^7" (Pawlik, 2026). A141822 comment: "6234 may be the largest integer with a(n)=4". |
| A141833 | n with a(n) = 3 | b-file of 5563 terms up to 10000. Infinite or finite is posed as open. |
| A141832 | n with a(n) = 2 | b-file of 4398 terms up to 9999. |

- Read off these entries: **bound 5 (canonical) holds for all 1 < n < 10⁷**, with a(n) = 5 only at 6, 54 and 150. The OEIS comment is the only source for this range; the original search is UNVERIFIED.
- Under the canonical convention, bound 2 fails for most n ≤ 10⁴: 5563 + 35 + 3 of the 9999 integers in 2..10⁴ need at least 3.
- Background (SECONDARY):
  - Niederreiter 1986 (Monatsh. Math. 101): {2^j}, {3^k} ⊂ D_3 (via Bourgain CRAS 2011 and [Hen94] p.45).
  - Niederreiter 1978 conjectured that D_3 contains all sufficiently large n (via [Ko] p.9).
  - Borosh 1976 reported computational evidence for bounds 5, 4 and perhaps 3, with "a multitude of exceptions" for 2 (via [Hen94] p.44).
  - Kan, "Is Zaremba's conjecture true?" (Sb. Math. 210 (2019)): not read. UNVERIFIED.

**Convention (VERIFIED, with a [trivial check]).** The literature does not use a single convention.
- **Existential**, i.e. "there exists a representation [a_1..a_k] with all a_j ≤ A":
  - [MOW] p.3 defines R_A := {[a_1,…,a_k] : k ∈ N, a_i ∈ A}.
  - [BK] p.2 defines R_A by "b/d = [a_1,…,a_k] … ∀j, a_j ∈ A", with no last-digit restriction.
- **Canonical** (a_r ≥ 2):
  - [Hen94] eq. (2), and [ABH] and [BD] for their statistics.
  - [Ko] p.9 argues 6 ∉ D_4 using canonical expansions only ("1/6 = [6], 5/6 = [1,5]").
- **This changes the bound-4 list.**
  - 5/6 = [0;1,5] = [0;1,4,1], so **under the existential convention 6 ∈ D_4**.
  - Recomputing the minimal max under the existential convention **[trivial check]**:
    - 6 → 4; 54 → 5; 150 → 5.
    - The A141823 entries 90, 252, 336, 386, 442, 508, 922, 978, 1450, 1692 and 3618 drop from 4 to 3. The rest stay at 4.
  - The existential exception set is a subset of the canonical one. Within the OEIS range, **the bound-4 exceptions are {6, 54, 150} under the canonical convention and {54, 150} under the existential one.**
  - Our notes' "{6, 54, 150}" is the canonical, OEIS-convention list.
- Zaremba's own wording (Zaremba 1972, p.76) is UNVERIFIED.

## 6. Limit law for the depth (sum of partial quotients)

- **Double average, stable law (VERIFIED, [BD] Thm 2.5, eq. (2.6), p.6; Thm 9.4 (9.16)).**
  - Uniform measure on Ω_Q = {a/q : 1 ≤ a ≤ q ≤ Q, (a,q) = 1}. Canonical a_r > 1, so Σ_1(x) = Σ a_j.
  - P_Q( Σ_1(x)/log Q − (log log Q − γ_0)/(π²/12) ≤ v ) = G_1(v) + O((log Q)^{−1+ε}).
  - The centring term is read from the arXiv HTML LaTeX `\frac{\log\log Q-\gamma_{0}}{\pi^{2}/12}`.
  - G_1 is the stable law S_1(6/π, 1, 0): index 1, totally skewed, scale 6/π. Its density is g_1(x) = (1/2π)∫ e^{−itx} e^{−(6/π)|t| − (12/π²) i t log|t|} dt.
  - So the typical size is (12/π²) log Q log log Q. [BD] p.7: the average is (6/π²)(log Q)², "known even with a single average over numerators, see [YK75]". The divergent first moment of S_1 explains the gap between mean and typical size.
- **Fixed denominator, concentration only (VERIFIED, [ABH] Thm 1, p.2).**
  - For N ≥ 3 and 0 < t ≤ (log N)^C: (1/φ(N)) #{a ∈ Z*_N : |S(a/N) − (12/π²) log N log log N| ≥ t log N} ≪ 1/t.
  - Cor. 2: some a has S ≤ (12/π²) log N log log N + O(log N).
  - [ABH] p.3: whether S(a/N) has a limit law at fixed N, and whether it must reflect the arithmetic of N, "remains unclear". **Open.**
  - Rukavishnikova (Math. Notes 90 (2011)) proved the upper tail ≪ 1/t and a law of large numbers (SECONDARY via [ABH] p.2).
- **[BV] does not cover the depth (VERIFIED, [BV] Thm 3, p.17).** Their CLT (Gaussian) is for digit costs of moderate growth, c(m) = O(log m).
  - The sum of partial quotients (c(m) = m) is outside it. [BD] p.~12 notes that such costs give stable, not Gaussian, laws ([BV05a] p.384).
  - [BV] Thm 3 averages over Ω_N = coprime pairs (u,v) with v ≤ N, and "also hold[s] … on ~Ω_N" (all pairs).
  - **Terminology clash:** in [BV] p.2 "depth" P(x) means the **number of steps** (the length L), not Σa_i.
- Max partial quotient: [ABH] Thm 3 (fixed N) gives a tail ≤ 12/(π²t) + …, and Hensley [ABH ref 14, Thm 1] gives a limit law under the double average (SECONDARY via [ABH] p.3).

## 7. Length variance constant κ

- **Value.**
  - VERIFIED: [Lh] §1.5 gives the "Hensley constant" γ_H ≈ **0.5160624…**. It was previously computed by the Daudé–Flajolet–Vallée method. On pairs (u,v) with 0 ≤ u ≤ v ≤ N, Var_N[P] ~ γ_H log N, where γ_H = 2(λ″(1) − λ′(1)²)/|λ′(1)|³.
  - VERIFIED: OEIS **A375066**: 0.51606240889999180681…, "pairs (a,b), with 0 ≤ a ≤ b ≤ x … variance … H·log(x)".
  - VERIFIED: [Ust08] Cor. 5 and Remark 1, pp.1057–1058:
    D(R) = (2/([R]([R]+1))) Σ_{d≤R} Σ_{c≤d} (s(c/d) − E(R))² = δ_1 log R + δ_0 + O_ε(R^{−1/4+ε}).
    - The pairs are all 1 ≤ c ≤ d ≤ R, **not** restricted to coprime pairs.
    - δ_1 = (8 log²2/ζ²(2))(γ − ζ′(2)/ζ(2) − (log 2)/2 − 1) + (4/ζ(2))(C_1 + 3 log 2/2), with C_1 from his eq. (32).
    - "Computer computations give … δ_1 = 0.51606…".
    - The same δ_1 is the variance constant of the count N(α,R) of convergent denominators ≤ R, for Lebesgue-random α.
  - **κ ≈ 0.516062.** "0.5160…" in the question is right.
  - One online source (T. Freiberg's web book "An Analysis of Euclid's Algorithm", ch. 4) prints 0.5160524… (SECONDARY). That conflicts with Lhote, OEIS and Ustinov and is probably a transcription slip.
- **Averaging set.**
  - Hensley 1994 (J. Number Theory 49, 142–182) gave the first-order variance and a CLT. SECONDARY via [BV] p.42 and [Ust08] p.1025; his exact sampling set is UNVERIFIED.
  - All proven asymptotics for κ that I found are **double averages over pairs**:
    - [Lh]: 0 ≤ u ≤ v ≤ N.
    - [Ust08]: 1 ≤ c ≤ d ≤ R.
    - [BV]: coprime pairs with v ≤ N, and all pairs, with the same leading constant δ².
  - For a **fixed** denominator only an upper bound is known: (1/d) Σ_{c=1}^{d} (s(c/d) − (2 log 2/ζ(2)) log d)² ≪ log d (Bykovskii; SECONDARY via [Ust08] p.1025 and [ABH] p.4). I found no fixed-q variance asymptotic.
- **Context for the mean (SECONDARY via [Ust08] p.1024, quoting Porter 1975 and Wrench).**
  - (1/φ(d)) Σ_{(c,d)=1} s(c/d) = (2 log 2/ζ(2)) log d + C_P − 1 + O(d^{−1/6+ε}).
  - Porter's constant C_P = (log 2/ζ(2))(3 log 2 + 4γ − 4ζ′(2)/ζ(2) − 2) − 1/2.
  - The convention is canonical, with s counting quotients and t_s ≥ 2. The existential [..., a_k − 1, 1] form adds 1 to L.
  - Bykovskii–Frolenkov (Sb. Math. 208 (2017) 644–683) improve the remainder (abstract only; SECONDARY).

---

**Who would know whether per-q E_N counts with local factors are already known:**
- **A. Kontorovich** and **M. Magee** (the singular series and uniform congruence counting, [BK] and [MOW]).
- **S. Huang**; **H. Oh**; **D. Hensley** ([Hen94] mod-n equidistribution, Hensley 1990 asymptotic).
- **O. Jenkinson** and **M. Pollicott**; **P. Vytnova** (dimensions).
- **C. Aistleitner**, **B. Borda** and **M. Hauke** (fixed-denominator statistics).
- **S. Bettin** and **S. Drappeau**; **B. Vallée** and **V. Baladi**; **L. Lhote**.
- **I. D. Kan**, **D. A. Frolenkov**, **V. A. Bykovskii** and **A. V. Ustinov** (Khabarovsk school: Zaremba, Kan's bound-4 work, moments).
- (J. Bourgain †2018.)

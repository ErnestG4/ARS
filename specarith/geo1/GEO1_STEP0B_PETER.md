<!-- Provenance: Step 0b for the GEO1 Peter-correlation seal (Will, 2026-10-30). Drafted by a literature agent from
the arXiv LaTeX sources; filed unedited below. Main-session check: Peter's theorem block (arXiv math/0104234 v1, e-print
lines 156–200: g(n), α(n) = g(n) log n/n, α̃ = α − 1, γ(r) as the plain mean, the Euler product, A_r(p), A_r(p^b) for odd
p, and A_r(2), A_r(4), A_r(8) = 0, A_r(16), A_r(32) = 0, A_r(2^b) for b ≥ 6) read verbatim: CONFIRMED as transcribed.
The agent's check scripts are in step0b_scripts/ (they ran from its scratch directory). The γ(r) table is the agent's
evaluation, to be reproduced independently by geo1_peter.py before use. -->

# Peter (CMP 225, 2002) transcription, BLS comparison, and the PGT exponent

Source read: the arXiv e-print LaTeX `ccg.tex` for math/0104234, **v1 only** (25 Apr 2001, the only version). The CMP version (DOI 10.1007/s002201000574; Crossref gives CMP 225(1), 171–189, 2002) was not read. Numbering below is reconstructed from the LaTeX counters (`\theequation` = section.eq, theorems numbered within section), so printed page numbers are not given. Downloads are in `/tmp/claude-1000/-home-combust-fmexplorer-criticality-tool--claude-worktrees-ph6-xp/a91f0f2e-c26b-4e53-81dc-2feedac9a4b5/scratchpad/lit_peter/`. Check scripts are in `/tmp/claude-1000/-home-combust-fmexplorer-criticality-tool--claude-worktrees-ph6-xp/a91f0f2e-c26b-4e53-81dc-2feedac9a4b5/scratchpad/peter_check/`.

## Task 1: Peter

### (a) Definitions (VERIFIED, §1 Introduction and §2)

> "let $\HH$ be the complex upper half plane and $\Gamma:=\SL(2,\Z)$ … The closed geodesics on $F$ are in one-to-one correspondence to conjugacy classes of primitive hyperbolic elements in $\Gamma$. For $n\in\N$, $n>2$, let $g(n)$ be the number of closed geodesics on $F$ which correspond to primitive conjugacy classes with trace $n$. Set $\alpha(n):=g(n)\log n/n$. Then the function $\alpha$ has mean value $1$. Set $\tilde{\alpha}(n):=\alpha(n)-1$."

- **Primitive only.** g(n) counts closed geodesics (primitive classes), with n > 2. Your summary α(n) = g(n) log n / n is **confirmed**: there is no extra normalising constant. M(α) = 1 is proved in §5 (Case 1: $\wh{\beta_{(p)}}(0)=1$).
- **Class-number form**, eq. (2.1), `\label{1}`: $\alpha(n) = \frac{\log n}{n} \sum_{d:\,\tr(\eps_d)=n} h(d)$. This comes from Prop. 2.1 ([Sarnak 1982], Cor. 1.5): "the lengths of closed geodesics on $F$ are the numbers $2\log\eps_d$ with multiplicities $h(d)$". Here d runs over positive non-square discriminants. h(d) is the number of SL(2,ℤ)-classes of primitive forms of discriminant d (the narrow class number), $\eps_d=(u_d+v_d\sqrt d)/2$ is the fundamental solution of $u^2-dv^2=4$, and $\tr(\eps_d)=u_d$.
- **INFERENCE: PSL and orientation.** Because g counts geodesics on F, ±P count once, so this is effectively PSL(2,ℤ) with |trace| = n. Because h(d) counts SL(2,ℤ)-classes of forms, geodesics are **oriented** (a geodesic and its reverse are counted separately).
- Peter's text has a typo: it says $\cosh(l/2)=|\Tr P|$, but it should be $2\cosh(l/2)$. Bogomolny's notes use $|\mathrm{Tr}M|=2\cosh l_p/2$.
- **INFERENCE: implementation freedom from Lemma 3.1 (`\label{102}`).** The lemma shows $\|\alpha-\beta\|_q=0$, with $\beta(n):=\sum_{d,v\ge1:\,dv^2=n^2-4}\frac1v L(1,\chi_d)$. Here β includes non-primitive classes (l ≥ 2) and the normalisation log ε / √(n²−4). The pointwise difference is $|\beta(n)-\alpha(n)|\ll n^{-1/2+\eps}$. So γ(r) is the same whether you use primitive classes or all classes, and log n/n or the exact normalisation.

### (b) Main theorem (VERIFIED; unnumbered `theoremwithout`, §1)

```latex
For $r\in \N_0$, the limit
\[ \gamma(r):=\lim_{N\to\infty} \frac{1}{N} \sum_{2<n\le N} \tilde{\alpha}(n)\tilde{\alpha}(n+r) \]
exists. Its value is given by
\[ \gamma(r)+1=\prod_p \Big( 1+\sum_{b\ge 1} A_r(p^b) \Big) , \]
```

- It is **α̃**, not α.
- It is a plain unweighted Cesàro mean over 2 < n ≤ N.
- The Euler product form you gave is **confirmed**.
- The local factors are defined in §4 (end) as $A_r(p^b) := \sum_{1\le a\le p^b,\, p\nmid a} |\wh{\beta_{(p)}}(a/p^b)|^2 e^{2\pi iar/p^b}$.
- The route is: α is limit periodic in every $\calD^q$ (Cor. 4.2), then Parseval (eq. (3.1), `\label{2}`) gives $\gamma(r)=\sum_{b\ge1}\sum_{(a,b)=1}|\wh\alpha(a/b)|^2e^{2\pi iar/b}-1$, and $\wh\alpha$ is multiplicative (Lemma 4.3).

### (c) Local factors (VERIFIED, verbatim from the theorem)

```latex
where for a prime $p>2$ and $b\ge 2$, we have
A_r(p) &= \frac{1}{(p^2-1)^2} \bigg( p\sum_{n\,\bmod\,p} \Big(\frac{(n^2-4)((n+r)^2-4)}{p}\Big)-1 \bigg),\\
A_r(p^b) &= \frac{1}{(p^2-1)^2 \, p^{3b-4}} \left\{\begin{array}{ll}
  2p^b(1-1/p) , & r\equiv 0\,(p^b) \\
  -2p^{b-1} , & r\not\equiv 0\,(p^b),\, r\equiv 0\,(p^{b-1}) \\
  \big(\frac{-1}{p}\big)^bp^b(1-1/p) , & r\equiv \pm 4\,(p^b) \\
  -\big(\frac{-1}{p}\big)^bp^{b-1} , & r\not\equiv \pm 4\,(p^b),\, r\equiv\pm 4\, (p^{b-1}) \\
  0 , & \text{otherwise} \end{array}\right\} .
Furthermore, for $b\ge 6$, we have
A_r(2) = \frac{1}{9}\{ 1, r\equiv 0\,(2);\ -1, r\equiv 1\,(2)\},\quad
A_r(4) = \frac{1}{18}\{ 1, r\equiv 0\,(4);\ -1, r\equiv 2\,(4);\ 0, r\equiv 1\,(2)\},
A_r(8)=0,\quad
A_r(16) = \frac{1}{9\cdot 16}\{ 1, r\equiv 0\,(16);\ -1, r\equiv 8\,(16);\ 0, r\not\equiv 0\,(8)\},\quad
A_r(32)=0,
A_r(2^b) = \frac{1}{9\cdot 2^{2b-4}}\{ 2, r\equiv 0\,(2^b);\ -2, r\equiv 2^{b-1}\,(2^b);\
  1, r\equiv\pm(4+2^{b-2})\,(2^b);\ -1, r\equiv\pm(4+2^{b-2}+2^{b-1})\,(2^b);\ 0, \text{otherwise}\}.
```

(The p = 2 `array` environments are condensed to braces here; the values and conditions are verbatim.)

- The Legendre symbol is the ordinary one. §5 also uses $\sum_{n \bmod p}\big(\frac{n^2-4}{p}\big)=-1$, and finds that the counts of n mod p with $\chi_{n^2-4}(p)=+1$ and $-1$ are (p−3)/2 and (p−1)/2.
- §5 gives, for c ≥ 2, $|\wh{\beta_{(p)}}(a/p^c)|=\frac{|1+(\frac{-1}{p})^c e^{-8\pi ia/p^c}|}{(p^2-1)p^{3c/2-2}}$. Then $A_r(p^c)=\frac{1}{(p^2-1)^2p^{3c-4}}\sum_{p\nmid a}e^{2\pi iar/p^c}\big(2+2(\frac{-1}{p})^c\cos\frac{8\pi a}{p^c}\big)$, which is two Ramanujan sums.
- **p = 2 is stated, not derived.** Peter writes: "The calculation will only be done for $p>2$. The case $p=2$ is similar but somewhat more elaborate."
- There is a harmless typo in §5 Case 4.1: cos(2πa/p^c) should be cos(4πa/p^c).
- **Independent check (INFERENCE, my computation).** I computed A_r(q) a second way, from BLS's own formula: $\alpha(q;r)=q|M_{q,r}|/|M_q|$ (counting SL₂(ℤ/q) elements by trace), $\beta(a,q)=q^{-1}\sum_r\alpha(q;r)e(ar/q)$, $A_r(q)=\sum_{(a,q)=1}|\beta|^2e(ar/q)$. Peter's closed forms match to ≤ 2e-16 for every r and:
  - q = 2^b, b = 1..7 (this covers the zeros at 8 and 32 and the b ≥ 6 rule);
  - 3^b, b ≤ 4;
  - 5^b, b ≤ 3;
  - 7², 11², 13².
- **No γ values in Peter** (VERIFIED: the paper has no numbers, tables or figures).
- **My evaluation of Peter's product (INFERENCE; for checking your implementation).** Primes up to 10⁵, all relevant b; P = 10⁴ and P = 10⁵ agree to 1e-5:

  | r | γ(r) |
  |---|---|
  | 0 | 0.32836 (= Var α; tail beyond 10⁵ ≈ 1e-6) |
  | 1 | −0.148608 |
  | 2 | 0.033126 |
  | 3 | −0.089954 |
  | 4 | 0.138080 |
  | 5 | −0.096516 |
  | 6 | 0.053178 |
  | 7 | −0.115483 |
  | 8 | 0.135079 |
  | 9 | −0.092211 |
  | 10 | 0.060336 |
  | 11 | −0.140516 |
  | 12 | 0.195118 |

  For r = 0, $A_0(p)=(p(p-2)-1)/(p^2-1)^2$. These values come only from the formula; I computed no multiplicity data.

### (d) Rate, error terms, conditionality (VERIFIED)

- **No rate of convergence is given for γ(r).** The argument is qualitative: $\lim_P\|\alpha-\beta_P\|_q=0$ (Prop. 3.7 and Cor. 4.2), with bounds such as $(\sum_{v>P}v^{-q'})^{1/q'}+(\sum_{l>P^{2q}}\tau_{2q}(l)/(lK(l)))^{1/(2q)}$ and no N-rate. The only explicit pointwise error is $|\beta-\alpha|\ll n^{-1/2+\eps}$ (Lemma 3.1).
- **Limit distribution and moments.** Peter only says limit periodic functions "have mean values and limit distributions". Nothing is computed beyond M(α) = 1 and $\alpha\in\calD^q$ for all q ≥ 1, so all moments exist. INFERENCE: γ(0) is the variance.
- **Unconditional.** GRH appears only to "see the principle" (eq. (3.7)). Lemma 3.6 (`\label{107}`) "can be proved unconditionally" using zero-density estimates (eq. (3.9), citing Peter, Acta Arith. 70 (1995), Lemma 4.11).

### (e) Numerics

- **Peter: none** (VERIFIED).
- **BLS** (VERIFIED from the arXiv chao-dyn/9509019 source):
  - Fig. 2 shows γ(r) "computed from the knowledge of [classes] whose corresponding matrices have traces up to 8000".
  - "Table 1" gives α(q;r) for q ≤ 11. The table is not in the e-print source, so I did not see it (UNVERIFIED).
  - The smoothed $\tilde f(x)=\frac1N\sum_{k=0}^N\gamma(k)e^{-\lambda k^2}\cos kx$ uses λ = 3/N² and N = 1000.
  - $C=\prod_p(1-\frac{1}{p(p+1)})\approx .704$.
  - As x → 0, $f(x)\to\frac{\pi}{12}x$ and $G(x)\to\frac{\pi}{24}x^2$.

### BLS (CMP 176, 1996) and Bogomolny (nlin/0312061) versus Peter

- **Same object and same Euler product.** BLS (VERIFIED) define $\gamma(r)=\lim\frac1N\sum_{n=1}^N\tilde\alpha(n)\tilde\alpha(n+r)$ (eq. "gr", §2) and $\gamma(r)=\sum_{(p,q)=1}|\beta(p,q)|^2e^{2\pi ipr/q}$, where $\beta(p,q)=q^{-1}\sum_r\alpha(q;r)e^{2\pi ipr/q}$ and $\alpha(q;r)=q|M_{q,r}|/|M_q|$ (§3, Hardy–Littlewood heuristic). Their A_r(p) and all p = 2 formulas are **identical to Peter's**. Their $\epsilon(n,p)$ (−1 iff n is odd and p ≡ 3 mod 4) equals $(\frac{-1}{p})^n$. Bogomolny's notes say "In [Peter] these formulas were proved by a different method."
- **Misprint in BLS and the notes for odd p, n ≥ 2 (INFERENCE, verified numerically).** Both print
  $A_r(p^n)=\frac{1}{p^{2n}(1-p^{-2})}\{2(1-1/p);\ -2/p\ (r\equiv tp^{n-1});\ \epsilon(n,p)(1-1/p)\ (r\equiv\pm4);\ -\epsilon(n,p)/p\ (r\equiv\pm4+tp^{n-1})\}$.
  This is smaller than Peter's value **by exactly the factor (1−p⁻²)**: the prefactor should be $(1-p^{-2})^2$. BLS's own $|M_{q,r}|$ route gives Peter's value, not the printed one (ratio 1.125 at p = 3, 1.0417 at p = 5, …). **Do not code the BLS/Bogomolny printed odd-prime-power formula.**
- **Other differences:**
  - BLS write $\prod_p(1+\sum_{k=0}^\infty A_r(p^k))-1$, where k = 0 is a typo for k ≥ 1.
  - The notes define γ with α instead of α̃ and write $\gamma(r)=\prod_p(1+\sum_{k\ge1}A_r(p^k))$ with no −1. So the notes' γ equals Peter's γ + 1.
- **Kloosterman form (notes §"Explicit Formulas"; VERIFIED and numerically checked for q ≤ 49 including composites):** $\beta(p,q)=\frac{S(p,p;q)}{q^2\prod_{\omega|q}(1-\omega^{-2})}$.
- **Form factor:**
  - BLS: $K(t)=\frac{1}{\pi^2w}f(w)$ with $w=2ke^{-k|t|/2}$, and $K\to\frac1{2\pi}\langle d\rangle$ with ⟨d⟩ = 1/6.
  - The notes: $K(t)\to A/(4\pi)$ with A = π/3, and $t_{p,q}=\frac1k\ln\frac{kq}{\pi p}$.
  - The two use different normalisations (UNVERIFIED which one is consistent).
- Neither BLS nor the notes give a numerical γ(0) or variance (VERIFIED by grep of both sources; the BLS figures themselves were not viewed).

## Task 2: prime geodesic theorem

- **Soundararajan–Young** (VERIFIED, arXiv:1011.5486 source).
  - Theorem 1.1: $\pi_\Gamma(x)={\rm li}(x)+O(x^{25/36+\varepsilon})$ and $\Psi_\Gamma(x)=x+O(x^{25/36+\varepsilon})$, with Γ = PSL(2,ℤ).
  - **x is the norm** $NP=\lambda^2$. INFERENCE: in trace t ≈ √x, the error is $O(t^{25/18+\varepsilon})$.
  - **Unconditional.** The general bound is $2/3+\theta/6$, with Conrey–Iwaniec θ = 1/6. Their source has "li", not "Li".
  - **Bibliographic details.** Journal (J. reine angew. Math.), volume 676 and year 2013 are confirmed by Crossref (DOI 10.1515/crelle.2012.002; Crossref gives no pages). Pages 105–120 are SECONDARY: they come from the bibliographies of Kaneko 2024 and Acosta Reche 2026, and Kaneko's also gives MR3028757.
  - A **corrections note** (Harcos, via Young; read from the Wayback copy, VERIFIED) fixes eq. (16)/(17) and says "the exponents in the main Theorem 1.1 are unaffected".
- **Earlier bounds** (VERIFIED, SY introduction):
  - Iwaniec 35/48 (Crelle 349 (1984) 136–159); 2/3 under GLH (Iwaniec's remark);
  - Luo–Sarnak 7/10;
  - Cai 71/102 (JTNB 14 (2002) 59–72).
- **Later claims** (VERIFIED from arXiv metadata and sources):
  - **Kaneko, arXiv:2402.12133.** v1/v2 claimed 113/164; v3 (1 Apr 2024) claims **2/3+ε unconditional**, and 5/8+ε under GLH for quadratic L-functions. arXiv shows no journal reference.
  - **Acosta Reche, arXiv:2610.01998 v2** (14 Oct 2026, UCL). It says 25/36 "remains to this day the best unconditional asymptotic". It claims $\eta(1/6)\approx0.69359$, where $\eta(y)=\tfrac12+\frac{\sqrt{81y^2+106y+33}-5-9y}{4}$. Kaneko is in its .bib file but is not cited in the text.
  - **Hashimoto, arXiv:1912.01223 (9/13): withdrawn** ("includes errors", flagged by Frolenkov).
  - **Avdispahić:** 2/3 for a Gallagher-type statement, and 5/8 under GLH outside a set of finite logarithmic measure. These are not pointwise bounds.
  - **Balkanova–Frolenkov** gave an alternative proof of 25/36 (SECONDARY).
  - **Cherubini–Guerreiro:** mean-square bounds (ANT 12 (2018)). SECONDARY: the square-mean exponent 7/12 is from a search snippet.
- **Best current unconditional exponent.** The established, refereed bound is **25/36** (SY 2013). Better exponents are claimed only in preprints: Kaneko's 2/3 (2024) and Acosta Reche's ≈0.69359 (2026). The 2026 paper treats 25/36 as still the record, so Kaneko's 2/3 should be cited as "claimed (preprint)". Whether Kaneko's paper was published or confirmed is UNVERIFIED.
- **Conjectured exponent.** SY (VERIFIED, §1): "it is believed that $E(x)\ll x^{1/2+\epsilon}$, and this remains an outstanding open problem". SY give no attribution for this; the original source is UNVERIFIED.

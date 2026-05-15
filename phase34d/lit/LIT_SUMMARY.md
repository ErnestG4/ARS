# Phase 34d Literature Summary

Transcribed from Rudnick-Waxman 2019 (Isr. J. Math. 232, 159–199; arXiv:1705.07498)
and Katz 2017 (IMRN 2017:11, 3377–3412; "Witt vectors and a question of Rudnick
and Waxman"). Pulled 2026-05-14 for Phase 34d pre-pilot lit-lock.

PDFs cached locally: `rudnick_waxman_2019.pdf` and `katz_2017.pdf`.

---

## 1. Rudnick-Waxman 2019 — angle definition (Gaussian)

For a Gaussian prime ideal **p ⊂ Z[i]** with generator α = a + ib (a > 0, b ≥ 0,
chosen unique representative), the angle is

```
θ_p = arg(α)   ∈   [0, π/2)
```

Unit-orbit coordinate (unit group Z[i]× = {±1, ±i}, order 4):

```
u(p) := (α/ᾱ)² = e^{i·4θ_p}   ∈   S¹
```

The factor 4 is the unit-group order; u(p) is well-defined on the ideal regardless
of which of the 8 representations (a + ib, ±a ± ib, ±b ± ia) is chosen.

Hecke characters: **Ξ_k(p) = e^{i·4k·θ_p}**, indexed by k ∈ Z; the k=0 mode is
the trivial character. Hecke 1918–1920 proved equidistribution of θ_p on [0, π/2)
via the non-vanishing of L(s, Ξ_k) on Re(s) = 1.

## 2. The variance counting function

Divide [0, π/2) into K disjoint arcs of length π/(2K) centered at θ_j:

```
I_K(θ) = [θ − π/(4K), θ + π/(4K)]
N_{K,X}(θ) = #{ p prime ideal in Z[i] : Norm p ≤ X,  θ_p ∈ I_K(θ) }
N = #{ p prime : Norm p ≤ X } ~ X / log X     [Prime Ideal Theorem for Q(i)]
⟨N_{K,X}⟩ = N / K
```

Variance is the second moment over the K arc centers:

```
Var(N_{K,X}) = ∫_0^{π/2} |N_{K,X}(θ) − ⟨N_{K,X}⟩|² · dθ / (π/2)
```

## 3. **Conjecture 1.2 (Rudnick-Waxman 2019)** — THE main target

```
For 1 ≪ K ≪ N^{1−o(1)},

    Var(N_{K,X}) ~ (N/K) · min(1,  2 log K / log N)
```

Three regimes:

| regime               | K vs N             | Var(N_{K,X})                         | character        |
| -------------------- | ------------------ | ------------------------------------ | ---------------- |
| trivial / empty      | K ≫ N              | ~ N/K                                | empty sectors    |
| Poisson              | √N ≪ K ≪ N         | ~ N/K  (saturates min at 1)          | random           |
| RMT / rigidity       | 1 ≪ K ≪ √N         | ~ (N/K) · 2 log K / log N            | suppressed       |

**Crossover at K ≈ √N** (i.e., 2 log K = log N). For arcs **narrower** than that
(K > √N), behavior is Poisson; for arcs **wider** than that (K < √N), variance
is suppressed below Poisson by factor 2 log K / log N — this is the rigidity
signature.

Smoothed version (Conjecture 5.1):

```
Var(ψ_{K,X}) ~ c_2(f, Φ) · (X/K) · min(log X, 2 log K)
c_2(f, Φ) = ∫ f(y)² dy · ∫ Φ(t)² dt
```

## 4. Random matrix model (Section 5)

The model replaces zeros of L(s, Ξ_k) with eigenphases of a random unitary
matrix U ∈ G(N) where **N ≈ (log K)/π** (matrix size grows with K, not X).

Set n := (α/2) · (log K)/π where α := log X / log K (so X = K^α).

The linear statistic is

```
S_n(U) = Σ_{j=1..N} w(γ_j) e^{2πi n γ_j}    [γ_j = eigenphases / 2π of U]
       = Σ_m  ŵ(m − n) · tr(U^m)            [Fourier series of w]
```

**Proposition 5.3 (RW2019):** For **G(N) = U(N), USp(2N), or SO(2N)**, with
n ≈ N as N → ∞:

```
∫_{G(N)} |S_n(U)|² dU  ~  min(n, N) · ∫_0^1 |w(γ)|² dγ
```

The three families **all give the same min(n,N) bulk variance** — they only
differ in O(1) and O(log N) corrections. This is *bulk universality*: the
RMT model cannot distinguish CUE from USp from SO at the variance level —
consistent with Katz-Sarnak.

Why min(n, N):
- For G = U(N): Dyson's lemma — ∫ tr(U^m) tr(U^{m'})* dU = δ_{m,m'} min(|m|, N)
  for (m, m') ≠ (0, 0). Diagonal-only contribution, hence min(n, N).
- For G = USp(2g) and SO(2N): same diagonal asymptotics, with O(1) and O(log N)
  off-diagonal corrections that vanish in the leading order.

**Critical implication for ARS:** because bulk pair-correlation R₂(r) is family-
universal in the Wigner-Dyson β-class, NNS / RF mode B / p-adic v4 will read
"TR-best-fit" but cannot cleanly separate CUE-from-GUE — only auxiliary global
moments (the σ²(K, X) variance computation itself) discriminate at the family
level. This is the Katz-Sarnak architectural property, not an ARS limitation.

## 5. Katz 2017 — function-field analog (proved)

The function-field setting:
- F_q[T] with q odd
- P(T) = A(T)² + T·B(T)² irreducible monic ↔ "Gaussian prime in F_q[√-T]"
- N = #{such P of degree ν} ~ q^ν / ν   [Prime Polynomial Theorem]
- Sectors parameterized by S¹_k = {f ∈ F_q[S]/(S^k) : f(0)=1, Norm(f)=1 mod S^k}
  where S = √(-T); |S¹_k| = q^κ with κ = ⌊k/2⌋ (k odd) or κ = k/2 (k even).
- Number of sectors K := q^κ.

The Hecke characters are *super-even characters* mod S^k (Dirichlet characters
of (F_q[S]/(S^k))× trivial on the even-polynomial subgroup H_k). Each non-trivial
super-even character Ξ has L-function:

```
L(z, Ξ) = (1 − z) · det(I − z · q^{1/2} Θ_Ξ)         (eq. 6.3)
```

with **Θ_Ξ ∈ U(N), N = d(Ξ) − 1** (d(Ξ) = Swan conductor).

**Theorem 1.3 (RW2019, proved via Katz's equidistribution):**
For κ ≥ 3 (or κ = 2, 5 ∤ q), as q → ∞:

```
Var(N_{k,ν}) ~ (q^{ν−κ} / ν²) · M(κ, ν)
where M(κ, ν) = 2κ − 2                    if ν ≥ 2κ − 2
              = ν − 1 + η(ν)               if κ ≤ ν ≤ 2κ − 2
η(ν) = 1 if ν even, 0 otherwise.
```

Translated to RW's normalization (K = q^κ sectors, N ~ q^ν/ν directions),
Var(N_{k,ν}) / (N/K) matches the **number-field conjecture's min(1, 2 log K / log N)
shape** in the q → ∞ limit.

Katz's contribution is to prove that the matrices Θ_Ξ become equidistributed in
**U(N)** (for super-even characters) and in **USp(2κ−2)** (for quadratic-twisted
super-even characters) as Ξ varies — i.e., the unitary monodromy is full.

## 6. Eisenstein analog — literature status

**Result of targeted lit search 2026-05-14:**

| paper / author                         | covers Eisenstein angles? |
| -------------------------------------- | ------------------------- |
| Rudnick-Waxman 2019                    | No (Z[i] only)            |
| Katz 2017 IMRN                         | No (F_q[√-T] only)        |
| Chen-Kim-Lichtman-Miller-Shubina-      | No (refines Z[i] case)    |
| Sweitzer-Waxman-Winsor-Yang 2019       |                           |
| Harman-Lewis 2001 (narrow sectors)     | No (Z[i] only)            |
| Bombieri-Vinogradov short-int paper    | General imaginary         |
| (ScienceDirect 2021)                   | quadratic — *upper bound* |
|                                        | only, no variance         |
| arXiv search Q(ω)/Eisenstein/sector    | No dedicated paper found  |

**Outcome:** The Eisenstein-prime-angle Rudnick-Waxman analog has **NOT** been
published as a dedicated paper. The conjecture extends by structural analogy
(same Hecke L-function machinery, same random matrix model, just unit group
order 6 instead of 4 and fundamental sector [0, π/3) instead of [0, π/2)):

```
Predicted Eisenstein conjecture (extends RW 2019 by analogy):

For Gaussian → Eisenstein, replace:
   Z[i] → Z[ω],   ω = e^{2πi/3}
   unit group Z[ω]× = {±1, ±ω, ±ω²} (order 6)
   u(p) = (α/ᾱ)^3 = e^{i·6 θ_p}                   [order-6 in exponent]
   Hecke characters Ξ_k(p) = e^{i·6k·θ_p}
   fundamental sector [0, π/3), arc length π/(3K)
   N = #{p prime in Z[ω] : Norm p ≤ X} ~ X / log X

Predicted:   Var(N_{K,X}^Eisenstein) ~ (N/K) · min(1, 2 log K / log N)

with the SAME functional form as Rudnick-Waxman, including the same RMT/Poisson
crossover at K ≈ √N. This is testable, not proved.
```

Phase 34d-E is therefore a **first-measurement** against an *implicit* analytical
prediction (structural analog of RW), not against an explicit published conjecture.
Katz 2017's framework provides the analytical scaffolding (super-even characters
→ U(N) monodromy) but has not been worked out for the F_q[√(-3T)] analog.

## 7. Implementation pointers for the brief

- **Direct variance test pre-spec:** at X = 10⁶ (N ~ 10⁴ Gaussian primes
  ≡ 1 mod 4), the Poisson/RMT crossover is at K ≈ √N ≈ 100. To see the
  RMT-side suppression, scan K ∈ {10, 30, 100, 300, 1000}; to see the
  Poisson saturation, scan K ∈ {1000, 3000, 10000}. At X = 10⁷ (N ~ 6×10⁴),
  crossover at K ≈ 245.

- **CUE/COE/CSE samplers** for the calibrator zoo: Mezzadri 2007 (Notices
  AMS 54:5, "How to generate random matrices from the classical compact
  groups"). The QR-with-phase-normalization recipe gives Haar measure on
  U(N); COE = U(N)/O(N) (symmetric U·U^T), CSE = U(2N)/Sp(2N) (Hermitian
  symplectic).

- **Per Prop 5.3, U(N) = USp(2N) = SO(2N) at variance leading order.** The
  three Circular ensembles will be indistinguishable on RF/NNS/p-adic by
  bulk universality. The discriminating test is σ²(K, X) directly, not ARS
  family classification.

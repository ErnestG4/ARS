# FN1-h2: E[R] for the principal-prime subset, and decisions D1–D5 (for Will's review)

**Brief:** Will, 2026-11-03, filed verbatim in `ph2/PH2_DECISIONS_2026-10-07.md`: "D1's matched-X primary is accepted in
principle, conditional on the R derivation showing the finite-size term runs in X. Send me D1–D5 and that derivation
for review." The seal draft is `fn1/FN1H2_SEAL.md` (aa4afbf2). Desk work only; nothing has been computed for this note.

## 1. The statistic

- For a set of half-angles θ ∈ [0, ½), the read mirror-symmetrises (θ and 1 − θ), cuts the circle into K equal bins and
  takes R = Var_bins(counts) / (N/K). N is the mirrored point count, so for Poisson R = 1.
- For h = 1 the set is one θ per split prime ideal 𝔭 with N𝔭 = p ≤ X. The conjugate 𝔭̄ gives the mirror point.
- For h = 2 it is the same, restricted to principal 𝔭. Since (α)‾ = (ᾱ), 𝔭̄ is principal whenever 𝔭 is, so the mirror
  convention is unchanged.

**Parseval.** With Î_K(k) = sin(πk/K)/(πk), Var_bins = Σ_{k≠0} |Î_K(k)|²·|S_k|², so

  R = (K/N) · Σ_{k≠0} |Î_K(k)|² · |S_k|²,  S_k = Σ_{𝔭 in the set} e(k θ_𝔭),

up to the aliasing and O(1/K) bin-edge terms the read shares with every set. The window weights w_K(k) = K|Î_K(k)|² sum to
1 − 1/K over k ≠ 0, and confine the sum to |k| ≲ K. So **R is a w_K-average of the normalised form factor |S_k|²/N.**

## 2. h = 1 (the order kept in FN1 and RQ1)

- **Harmonics.** e(kθ_𝔭) = λ_k(𝔭), a Hecke character with frequency wk and conductor 1. The analytic conductor is
  q_k ≍ |D|(wk/2)², so log q_k = C_F + 2 log|k| + O(1/k) (`fn1/FN1_STEP0.md` §1).
- **The sum is a prime sum cut at X.** S_k = Σ_{N𝔭 ≤ X} λ_k(𝔭).
- **The explicit formula** writes the Λ-weighted version as −Σ_ρ X^ρ/ρ + (lower terms), a sum over the zeros of
  L(s, λ_k). Its mean square involves the zeros' pair correlation at the scale (log q_k)⁻¹, against the length log X of
  the prime sum.
- **RW's heuristic** (their §5, RMT pair correlation for the zeros, prime ideal theorem; `rq1/RQ1_STEP0.md` §3):

  **E|S_k|² ≈ N · min(1, log q_k / log X).**

  This is the Montgomery form factor min(1, τ) evaluated at τ = log q_k / log X: the ratio of the conductor scale to
  the prime-sum length.
- **Therefore**

  **E[R] ≈ ⟨ min(1, (C_F + 2 log|k|) / log X) ⟩_{w_K}.**   (★)

- **This is the order kept:** RW's leading form plus the field's conductor constant. Chen et al.'s lower-order
  constants (C_Φ,ζ, C_Φ,L, A′) are O(1/log X) too, but are not kept at h = 1 (RQ1-b found they do not carry over to our
  statistic; L15 found the L-term small). They are not kept here either.

**Where N and X enter.**
- **X:** the cutoff of the prime sum. It sets the denominator log X in (★): the length of the explicit formula, against
  the conductor.
- **N:** only as the normalisation. RW's |S_k|² ∝ N comes from the diagonal Σ|λ_k(𝔭)|² = N, and the read divides by
  N/K, so N cancels from (★).
- **K:** through the weights.
- **So at fixed K, E[R] depends on X, not on N: the finite-size term runs in X.**

At h = 1, N and X are locked, N ≈ π(X)·(split fraction)·2, so no h = 1 data can tell log X from log N. RQ1 Step 0
wrote "min(1, 2 log K / log N)", which uses log N ≈ log X at leading order. The difference, log log X + O(1) ≈ 3, is the
same order as C_F, so at this order the correct variable is X.

## 3. h = 2, principal primes

- **Projector.** With Cl = {1, ψ} (ψ the genus character), 1_principal(𝔞) = (1 + ψ(𝔞))/2. On principal 𝔭,
  e(kθ_𝔭) = ξ̃_k(𝔭), where ξ̃_k is either Hecke extension of ξ_k((α)) = (α/|α|)^{2k}; both have conductor 1 and
  frequency wk (`FN1_L17_PREREQS.md` (b)). So

  S^P_k = Σ_{N𝔭 ≤ X} ½(1 + ψ(𝔭)) ξ̃_k(𝔭) = ½ (S_k^{(1)} + S_k^{(ψ)}),  S_k^{(χ)} = Σ_{N𝔭 ≤ X, split} (ξ̃_kχ)(𝔭).

  Both sums run over all split prime ideals up to the same X.
- **Each family.** ξ̃_k and ξ̃_kψ are primitive Hecke characters with the same infinity type and conductor 1 (ψ is
  unramified over K). So both have analytic conductor q_k ≍ |D|(wk/2)², and RW's heuristic gives
  E|S^{(1)}|² ≈ E|S^{(ψ)}|² ≈ N_all·min(1, log q_k / log X).
- **The cross term** E[S^{(1)} S̄^{(ψ)}]:
  - **Diagonal:** Σ_𝔭 |ξ̃_k(𝔭)|² ψ(𝔭) = Σ_𝔭 ψ(𝔭) = (#principal − #non-principal) = o(N_all), by the prime ideal theorem
    for ψ. Under GRH it is O(√X log X), relative size X^{−1/2+ε}. There is also a Chebyshev-type bias of the same small
    order.
  - **Off-diagonal:** the pair correlation between the zeros of two distinct primitive L-functions, L(s, ξ̃_k) and
    L(s, ξ̃_kψ). It has no main term (the zeros are independent at leading order: Rudnick–Sarnak). Its lower-order
    arithmetic terms are of Chen's type, which are not kept.
- **Result.** E|S^P_k|² ≈ ¼ · 2 · N_all · min(1, log q_k/log X) = N_P · min(1, log q_k/log X), since N_P ≈ N_all/2. So

  **E[R_P] ≈ ⟨ min(1, (C_F + 2 log|k|) / log X) ⟩_{w_K}**: exactly (★), with the same C_F, the same X and the same K.

- **General h:** S^P = (1/h)Σ_ψ S^{(ψ)} gives E|S^P|² ≈ (h/h²)·N_all·min(…) = N_P·min(…); the same result.

**Answers to Will.**
- **The finite-size term runs in X.** The class number changes N at given X (N_P ≈ N_all/h) but not the cutoff, so at
  matched X and K the h = 2 set has the h = 1 expectation.
- **The (1 + ψ)/2 projection does not change the expected excess at this order.** That holds because ψ is unramified
  over K.
- **The contrasts, by the same algebra:**
  - **Random thinning with keep probability p** (Will's formula): E|S|² → p²·E|S|² + p(1 − p)N, normalised by pN, so
    R_thin = p·R + (1 − p). That is ½(R + 1) at p = ½.
  - **Thinning by a rational character χ′ unrelated to K:** χ′∘N ramifies over K (conductor norm D′²), so the twisted
    family's conductor is q·D′². That gives R → ½[R(C) + R(C + 2 log|D′|)].
  - **For an h = 1 field there is no nontrivial unramified character,** so no thinning of an h = 1 set reproduces the
    principal projection.

**Status.** This is the same standing as the h = 1 C_F derivation and RQ1 Step 0: it holds conditional on RW's RMT
heuristic for the zeros, and is not proved. The new step for h = 2 is the cross term. Its diagonal is controlled by the
prime ideal theorem for ψ; its off-diagonal part rests on the independence of distinct L-functions' zeros, a standard
heuristic (Rudnick–Sarnak), also not proved.

## 4. If the term ran in N instead: what the read would show (robustness)

A doubling of X at fixed K shifts (★) by about −R·log 2 / log X in R. That is about −0.024 at X = 2·10¹⁰ (R ≈ 0.82),
about −0.5 to −0.6 along C (on the empirical slope b ≈ 0.0455, or the formula's 1/log X). The h = 2 sets reach matched N
at 2× the X of h = 1. So the four combinations give:

| Hypothesis | s against the matched-X reference (primary) | s against matched N (descriptive) | Primary verdict (cuts −0.554 / −0.832) |
|---|---|---|---|
| Conductor, runs in X (§2–3) | **0** | ≈ −0.55 | CONDUCTOR, D23 ≈ 0.97 |
| Conductor, runs in N | ≈ +0.55 | 0 | CONDUCTOR, D23 ≈ 1.0 |
| L-value, runs in X | **−1.39** | ≈ −1.94 | L-VALUE, D23 ≈ 0.97 |
| L-value, runs in N | ≈ −0.84 | −1.39 | **L-VALUE ≈ 0.51, INCONCLUSIVE ≈ 0.33, CONDUCTOR (wrong) ≈ 0.16** |

- **Reading.** A true conductor effect reads CONDUCTOR under either variable.
- Both informative branches need the derivation's "runs in X". If the term ran in N, a true L-value effect would read
  L-VALUE only about half the time, and **wrongly CONDUCTOR about 16%** (P(s > −0.554 | mean −0.84) at SE 0.285).
- **So the conductor verdict is not fully robust either:** its false rate under a true L-value rises from about 0.00 to
  about 0.16 if the term ran in N. Recorded as a §9.J / D23 consideration under D1.
- **Update 2026-11-04 (exact (★) instead of the linearisation; `FN1H2_PRED.json`, ec4f3ac8; simulation d5cf401b):**
  under "runs in N" the primary mean s is +0.66 (conductor) and −0.73 (L-value). A true L-value effect then reads
  L-VALUE 0.34, INCONCLUSIVE 0.43 and CONDUCTOR 0.24, not the 0.51 / 0.33 / 0.16 above.
- **The read can check it descriptively.** s_X − s_N is ≈ +0.55 under "runs in X" and under "runs in N" alike, so the
  difference does not separate them. The level does: under "runs in X" the matched-N displacement is −0.55 for
  conductor and −1.94 for L-value.

## 5. Decisions D1–D5 (updated after Will's 2026-11-03 rulings)

- **D1: primary reference (accepted in principle, conditional on §2–3).**
  - The primary is the matched-X, matched-K unthinned h = 1 reference (`FN1H2_SEAL.md` §4). Will has withdrawn the
    thinned-control requirement.
  - **Proposed consequences for the draft:**
    - control (i) is dropped as a reported control;
    - the §9.D planted witness is built directly on the nine h = 1 matched-X references (leave-one-out, with the
      predicted −log 4 shift planted on each stand-in), so no thinning is needed;
    - matched N stays descriptive with its §4 predictions.
  - **New §9.J item from §4:** if the term ran in N, the L-VALUE branch's power falls to about 0.5, and a true L-value
    effect reads CONDUCTOR about 16% of the time. Both informative verdicts therefore rest on §2–3, and the seal's
    attribution would say so.
  - Pre-seal simulation (a) would carry the "runs in N" variant as a named stress case.
- **D2: pre-seal compute (go or no-go for each).**
  - (a) Parametric D23 / §9.J / power simulations, no data, under 0.3 core-h. They include the §4 "runs in N" variant
    and the σ_μ × 1.5 stress.
  - (b) The nine h = 1 references at X* and K_P on seen data, about 0.5 core-h, for the planted witness.
  - (c) The generator selftest (brute force, no data) and the §9.F fixture dry run, about 1 core-h.
  - D2b: if the σ_μ × 1.5 stress puts D23 below 0.95 (closed form 0.90), widen the cuts or accept it.
- **D3: K1.** Drop (recommended: its only theory form, Chen's A′, arises from inert primes our statistic excludes), or
  keep with the A′ form in `FN1H2_SEAL.md` §7 and Holm over K0 and K1.
- **D4: X* = 2·10¹⁰.** Matched N to stage 1, about 61 core-h of archives. A larger X* buys little, because the field
  scatter dominates SE(s).
- **D5: control (ii), χ′-thinning (D′ = 5), as a descriptive test of the twist-conductor mechanism** (§3: R moves to
  ½[R(C) + R(C + 2 log 5)]). Keep it at about 0.3 core-h, add D′ = 13, or drop it now that the requirement is withdrawn.
  Recommendation: keep D′ = 5 only, descriptive. It is the one available test of the mechanism the conductor
  prediction rests on.

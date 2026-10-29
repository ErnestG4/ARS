<!-- Provenance: C_ω verification (Will, 2026-10-29). Drafted by a literature agent; filed unedited below. Main-session
checks: the LMFDB coefficients identifying the CM forms with λ₁, λ₂ (ℤ[ω]) and the ℤ[i] analogue recomputed:
2·Re((2+√−3)⁶) = −286 (3.7.b.a a₇), 2·Re((2+√−3)¹²) = −153,502 (3.13.b.a a₇), 2·Re((2+i)⁴) = −14 (4.5.b.a a₅). CONFIRMED.
Indexing: our sector angle θ = (arg π mod π/3)/(π/3) ∈ [0, 1) (RQ1C_SEAL §1) gives e^{2πikθ} = (π/|π|)^{6k}, i.e. the
k-indexing (ℓ = 6k) for which C_ω = log 27 holds (item 7); ℤ[i]'s θ over π/2 gives ℓ = 4k and log 16, as RW/Chen.
The finite-k corrections of item 7 (field-specific, O(1/k) in the IK "+3" convention; ≤ 0.011 in the zero-density
form at k = 1) are negligible at the read's K (10⁴–10⁶ terms), and the heuristic uses the asymptotic 2 log|k| + C_F.
Not read: Neukirch, Miyake, Iwaniec–Kowalski itself (IK's functional equation is quoted via Holm). -->

# C_omega literature verification (read-only)

**Verdict: CONFIRMED.** The published sources give Γ_ℂ(s+3|k|) and conductor 3 for λ_k = (π/|π|)^{6k} on ℤ[ω]. That makes the analytic conductor ≍ 27k², so C_ω = log 27 = 3.2958. The ℤ[i] analogue, log 16, is also confirmed. The field difference C_ω − C_i = log(27/16) = 0.5232. One caveat, item 7, is about convention and finite k; it is not a contradiction.

Downloads are in `/tmp/claude-1000/-home-combust-fmexplorer-criticality-tool--claude-worktrees-ph6-xp/a91f0f2e-c26b-4e53-81dc-2feedac9a4b5/scratchpad/lit_cw/` (rw.pdf, holm2.pdf, chen.pdf, akbary_ipm.pdf).

## Sources

1. **Holm, "The 1-level density for zeros of Hecke L-functions of imaginary quadratic number fields of class number 1", JTNB 37 (2025) 237–283 (arXiv 2309.10018). VERIFIED (read).**
   - It covers all class-number-1 fields, including d = 3. §2.1 (p. 242) states that O_K^× ≅ ℤ/6ℤ when d = 3.
   - p. 243: ψ_k(⟨α⟩) = (α/ᾱ)^{Nk} with N a multiple of |O_K^×|. It is "well-defined since any two generators … differ by a factor in O_K^× where χ_∞,k ≡ 1". It is angular, with trivial Dirichlet part and modulus m = O_K. Holm writes ψ_k = (α/|α|)^{2Nk} with **frequency ℓ = 2Nk**. The ideal angle is defined in [0, 2π/|O_K^×|).
   - p. 245, citing IK Thm 3.8 and eq. (3.86): Λ(s,ψ) = L(s,ψ)·(|D|·N(m))^{s/2}·(2π)^{−s}·Γ(s+|ℓ|/2). Eq. (2.3) gives Λ_k(s) = L_k(s)|D|^{s/2}(2π)^{−s}Γ(s+Nk). The text extraction garbled the sign of the (2π) exponent; I read it as (2π)^{−s} because (2.5) has X_k ∝ |D|^{1/2−s}(2π)^{2s−1} (INFERENCE). The root number is 1.
   - **Mapping to our claim:** λ_k = (π/|π|)^{6k} has ℓ = 6k, so the gamma factor is (2π)^{−s}Γ(s+3|k|) ∝ Γ_ℂ(s+3|k|) and the conductor is |D| = 3. The claim follows from the general formula.
   - Holm's condition "N a multiple of |O^×|" is sufficient but not necessary. What is actually needed is ℓ ≡ 0 (mod w). His N = 6 family is our even k only. Odd k is covered by item 2.
   - Holm's lower-order constant ℓ₀ contains log√|D| + log N, which equals ½·log(|D|·N²). With N = 3 (our normalisation) this is ½·log 27 (INFERENCE, consistent).

2. **LMFDB CM newforms for ℚ(√−3). VERIFIED (pages read).**
   - **3.7.b.a** (level 3, weight 7, CM by −3). L-page: "Λ(s) = 3^{s/2} Γ_ℂ(s+3) L(s) = Λ(1−s)", conductor 3, sign 1, Selberg data (2, 3, (:3), 1). I checked a₇ = −286 = 2·Re((2+√−3)⁶) and a₃ = −27 = (√−3)⁶. So this L-function is L(s, λ₁) (my computation). This settles odd k: λ₁ is well defined, has conductor 1, and level 3 = |D|·N𝔣.
   - **3.13.b.a**: "Λ(s) = 3^{s/2} Γ_ℂ(s+6) L(s)", conductor 3, sign 1. Its a₇ = −153502 = 2·Re((2+√−3)¹²), so this is λ₂.
   - **ℤ[i] analogue, 4.5.b.a**: "Λ(s) = 4^{s/2} Γ_ℂ(s+2) L(s)", conductor 4. Its a₅ = −14 = 2·Re((2+i)⁴).

3. **Rudnick–Waxman, arXiv 1705.07498 v2, §4.1. VERIFIED.**
   - Ξ_k = (α/ᾱ)^{2k} = e^{i4kθ}, with θ ∈ [0, π/2), "well defined functions on the ideals of ℤ[i]".
   - Eq. (4.1): ξ_k(s) = π^{−(s+2|k|)}Γ(s+2|k|)L(s,Ξ_k). Since π^{−s} = 4^{s/2}(2π)^{−s}, this is conductor 4 with Γ_ℂ(s+2|k|).
   - Eq. (4.2): zero density (log|k|)/π.

4. **Chen et al., arXiv 1901.07386, eq. (3.12). VERIFIED.** ξ_k(s) := π^{−(s+|2k|)}Γ(s+|2k|)L_k(s), identical to item 3.

5. **Iwaniec–Kowalski. SECONDARY (the book itself was not read).**
   - Hecke's functional equation, Thm 3.8 and (3.86), is known here only as quoted in item 1.
   - The analytic conductor is known from Akbary's IPM 2006 lecture notes, which follow IK Ch. 5 (pp. 6–8). There γ(f,s) = π^{−ds/2}∏Γ((s+κ_j)/2) and "Q(f,s) = q(f)∏(|s+κ_j|+3)", attributed to Iwaniec–Sarnak.
   - By duplication, Γ_ℂ(s+μ) ∝ Γ_ℝ(s+μ)Γ_ℝ(s+μ+1), so κ = μ, μ+1. That gives q(½) = 3·(3|k|+3.5)(3|k|+4.5) ~ 27k² (INFERENCE).

6. **Neukirch VII §8, Miyake, and any "angles / sectors of Eisenstein primes" paper: UNVERIFIED.** No dedicated Eisenstein-angle paper was found in two searches.

## What would and would not change C_ω

7. **Convention and finite-k effects (my computation; INFERENCE).**

   | k | IK "+3": C_ω | IK "+3": C_i | IK "+3": difference | digamma: difference |
   |---|---|---|---|---|
   | 1 | 4.985 | 4.963 | 0.022 | 0.512 |
   | 10 | 3.546 | 3.137 | 0.409 | 0.523 |
   | 100 | 3.322 | 2.812 | 0.510 | 0.523 |
   | 1000 | 3.299 | 2.777 | 0.522 | 0.523 |

   - **IK "+3" form.** log q − 2 log k converges to log 27 and log 16 only slowly: the corrections are O(1/k) and **field-specific** (≈ 7/(6k) for ω, ≈ 2/k for i), as the table shows. So C_ω = log 27 is exact only asymptotically in this convention.
   - **Digamma form.** This is the zero-counting density (1/2π)[log|D| + 2 Re ψ(½+μ) − 2 log 2π]. It is the convention LMFDB's "analytic conductor" uses: I reproduced LMFDB's 0.690162, 2.741981 and 0.413480 exactly. Its constant is log|D| + 2 log(μ/k) − 2 log 2π, and the error is already tiny at k = 1. The difference is 0.512 at k = 1 and 0.523 from k ≥ 2, against log(27/16) = 0.5232.
   - **Which kind of discrepancy each is.** The −2 log 2π, and dropping or keeping "+3" asymptotically, are **common additive** changes and cancel in field differences. The O(1/k) "+3" corrections are **field-specific**.
   - **Indexing.** Indexing by the per-field frequency ℓ = wk, the angle e^{iwkθ} with θ ∈ [0, 2π/w), instead of k shifts C by −2 log w. That is **field-specific**: log 27 becomes log(3/4), and log 16 becomes log(1). Our C_ω = log 27 is correct only for the k-indexing λ_k = (π/|π|)^{6k}, i.e. ℓ = 6k.
   - **Character conductor.** No source suggests a conductor larger than 1 for these angular characters. Items 1 and 2 both give modulus O_K.

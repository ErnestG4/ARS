# FN1-h2 seal: conductor or L-value, using the class-number-2 fields. DRAFT for Will's review, NOT SEALED

**Briefs:** Will, 2026-11-03 ×2 (L17 prerequisites; "seal draft may begin"), filed verbatim in
`ph2/PH2_DECISIONS_2026-10-07.md`. Prerequisites: `lead/FN1_L17_PREREQS.md` (accepted).

**Status: draft.** No h = 2 data exist, and no compute has been run for this seal. The numbers in §5 are closed-form
estimates from committed stage-1 values, to be replaced by the pre-seal simulations listed in §5. **§10 lists the
decisions this draft needs from Will. The first one changes Will's control predictions, so please read §2 and §10
first.**

## 1. Question

At h = 1, C_F = log(|D|(w/2)²) and P_L = log(1/L(1,χ_D)²) + 2 log π are identical, so FN1 stages 1–2 could not tell
the conductor from the L-value. At h = 2, P_L = C_F − log 4 (`lead/FN1_L17_PREREQS.md` (b)). Pooling h = 1 and h = 2
separates them:
- **conductor:** the h = 2 fields sit on the h = 1 curve;
- **L-value:** the h = 2 fields sit −log 4 = −1.386 along C from it.

## 2. Theory: E[R] for the principal-prime subset (the (b) derivation extended to R; Will's brief)

**The order kept is the order of the h = 1 C_F derivation:** Rudnick–Waxman's leading form plus the conductor
constant (`rq1/RQ1_STEP0.md` §3, `fn1/FN1_STEP0.md` §1). Lower-order arithmetic terms (the C_Φ,L, A′ and C_Φ,ζ type in
Chen et al.) are not kept at h = 1, and are not kept here either.

**h = 1.** The read's statistic is R = Var_bins/(N/K), with K equal bins of the mirror-symmetrised set (Poisson ⇒ R = 1).
1. Parseval: Var = Σ_{k≠0}|Î_K(k)|²·|S_k|², with S_k = Σ_𝔭 e(kθ_𝔭) over the split prime ideals of norm ≤ X
   (conjugates included).
2. RW's heuristic (explicit formula + RMT for the zeros of L(s, λ_k)): E|S_k|² ≈ N·min(1, log q_k / log X), with
   q_k ≍ e^{C_F}k² in the k-indexing.
3. So **E[R] ≈ ⟨min(1, (C_F + 2 log|k|) / log X)⟩_K**, an average over k ≠ 0 with the window weights
   w_K(k) = K·|Î_K(k)|² (these sum to 1 − 1/K).

**Answer to Will's first question: the finite-size term runs in X, not N.** N cancels from E[R]. The cutoff is the
prime-norm bound X of the explicit formula.
- RQ1's earlier "min(1, 2 log K / log N)" replaced log X by log N at leading order. The two differ by
  log log X + O(1) ≈ 3. That is the same order as C_F, so at this order it must be X.
- Consequence: two sets with the same K and X have the same E[R], whatever their N.

**h = 2, principal primes.**
- **The decomposition** (prerequisites (b), point 4): S^P_k = ½(S_k^{(1)} + S_k^{(ψ)}). Here
  S_k^{(χ)} = Σ_{all split 𝔭} (ξ̃_k χ)(𝔭), ψ is the genus (class-group) character, and N_P ≈ N_all/2.
- **The two families:** E|S^{(1)}|² ≈ E|S^{(ψ)}|² ≈ N_all·min(1, log q_k/log X). Both have the same conductor,
  because ψ is unramified over K.
- **The cross term** E[S^{(1)} S̄^{(ψ)}]:
  - its diagonal is Σ_𝔭 ψ(𝔭) = (principal − non-principal count) = o(N) by the prime ideal theorem for ψ;
  - its off-diagonal part is the pair correlation between the zeros of two distinct primitive L-functions, which is
    absent at leading order (Rudnick–Sarnak independence);
  - what remains is of Chen's lower-order type, which this order does not keep (L15 put Chen's L-term at about 0.005
    in R for −7).
- So E|S^P_k|² ≈ ¼·2·N_all·min(…) = N_P·min(1, log q_k/log X).

**Answer to Will's second question: the (1 + ψ)/2 projection does not change the expected excess at this order.**
**E[R_P] = ⟨min(1, (C_F + 2 log|k|) / log X)⟩_K, the h = 1 expression with the same C_F, at the same X and K.** The
class number enters only through X(N): N_P(X) ≈ N_all(X)/2.

**The two thinnings Will specified are not neutral.** They differ from the principal projection, and the difference
follows from the same algebra.

| Selection (half of the split primes) | Weight | E[R] at the same X and K | Excess 1 − R |
|---|---|---|---|
| Principal primes (h = 2) | (1 + ψ)/2, ψ unramified over K | R(C) | unchanged |
| (i) Seeded random half-thinning | Bernoulli ½ per split p | **(R(C) + 1)/2: exact in expectation** (binomial thinning adds ¼·mean to the bin variance) | **halved** |
| (ii) Half-thinning by χ′ = (D′/·), D′ coprime to D | (1 + χ′(p))/2; twist λ_k·(χ′∘N) has conductor norm D′² | ½[R(C) + R(C + 2 log\|D′\|)] ≈ R(C + log\|D′\|) where R is linear in C | reduced, by an amount set by log\|D′\| |

So under the conductor hypothesis the h = 2 displacement against these controls is **not 0**. At this order, a selection
leaves R unchanged only when its character is unramified over K, and for an h = 1 field no such nontrivial character
exists.

**Predicted displacements** (β 0.55, X = 2·10¹⁰; linearised with b ≈ 0.0455 and R ≈ 0.82; indicative, since RQ1-b found
that the leading form plus the conductor constant misfits our statistic's level):

| Reference | Conductor hypothesis | L-value hypothesis |
|---|---|---|
| **h = 1 unthinned, matched X, at the h = 2 K** (proposed primary, §4) | **0** | **−log 4 = −1.39 along C** |
| (i) Random half-thinned h = 1, matched N and X | ΔR = (R − 1)/2 ≈ −0.09 (≈ −4 along C on the control's halved slope) | ≈ −0.15 in R |
| (ii) χ′-thinned h = 1 (D′ = 5), matched N and X | ≈ −log 5 = −1.61 along C | ≈ −3.0 along C |
| h = 1 unthinned at matched N (X half; stage-1 values) | ≈ −R·log 2/log X ≈ −0.024 in R, i.e. ≈ −0.5 along C | ≈ −1.9 along C |

Against either thinned control, a true conductor hypothesis would land on or beyond the L-value prediction. **So this
draft does not use the thinned controls as the primary reference (decision D1).** It runs them as Will specified, and
uses them as follows:
- **(i) is a witness known by construction:** 2R_rand − 1 is an unbiased stand-in for R at matched X (§7).
- **(ii) tests the twist-conductor mechanism itself,** the thing the conductor prediction rests on. Under §9.D it is a
  hypothesis test, reported whichever way it comes out.

Their displacements, and matched N and matched X, are reported as Will asked (§6).

## 3. Data

**h = 2 sets (new).** All 18 fields (`lead/FN1_L17_PREREQS.md` (a)): principal split primes p ≤ X* = 2·10¹⁰.
- Generator `fn1h2_archive.py` (to be written; FN1's `fn1_archive.py` structure):
  - split iff (D/p) = +1;
  - principal iff χ_{d₁}(p) = +1 (genus; D = d₁d₂);
  - D ≡ 1 (mod 4): x² + |D|y² = 4p (principal form x² + xy + ((1 + |D|)/4)y²);
  - D ≡ 0 (mod 4): x² + (|D|/4)y² = p;
  - θ = atan2(y√|D|, x)/π, or atan2(y√(|D|/4), x)/π;
  - ramified primes and 2 handled as FN1 (split primes only; for −15 the primes above 2 are non-principal and drop out).
- Selftest: brute-force representability for p < 2·10⁵ against the genus rule, Cornacchia succeeding exactly on the
  principal primes, and hand cases.
- **Matched N:** every set is cut to the common n_P = min over the 18 h = 2 sets of the principal count below X*, about
  2.2·10⁸ (π(2·10¹⁰)/4). That matches stage 1's n (2.28·10⁸). Then N_P = 2n_P and K_P = round(N_P^0.55) ≈ 5.7·10⁴.

**h = 1 sets (existing archives; seen data).** The nine fields, rows with p ≤ X*: the FN1 archives for w = 2, and
`rq1/archive_1e12_zi` / `_zw`.
- **Reference (primary):** unthinned, rows ≤ X*, R at K = K_P (not its own N^β), normalised by its own N/K.
- **(i) Random half-thinned:** each split p kept with probability ½ (seed 20261103 + field index), cut to n_P.
- **(ii) χ′-thinned:** p kept iff (5/p) = +1; D′ = 5 is coprime to all nine D. Cut to n_P.
- **Matched N (descriptive):** stage-1 R at 10¹⁰ (n 2.28·10⁸), already read.

**β:** 0.55 primary. β 0.45 and 0.40 descriptive, at no extra load.

**Primary set (Will):** the nine h = 2 fields with 28 ≤ |D| ≤ 163: −35, −40, −51, −52, −88, −91, −115, −123, −148.
- C ∈ [3.56, 5.00] and P_L ∈ [2.17, 3.61], both inside the h = 1 range [1.95, 5.09].
- The other nine (−15, −20, −24, −187, −232, −235, −267, −403, −427) are descriptive.

## 4. Primary test: the displacement s along C

- **Reference curve:** R_ref(C) = OLS line of the nine h = 1 reference R on C_F. The line, not K0's quadratic, keeps
  the primary free of the out-of-sample arm.
- **Statistic:** s = argmin_s Σ_{primary h = 2} (R_h2,j − R_ref(C_j + s))², i.e. s = mean_j(R_h2,j − R_ref(C_j)) / b̂.
  - Conductor predicts s = 0.
  - L-value predicts s = −log 4 = −1.386.
- **Three-way rule, cuts at 0.4 and 0.6 of log 4:**
  - **CONDUCTOR** iff s > −0.554;
  - **L-VALUE** iff s < −0.832;
  - else **INCONCLUSIVE**.
  - Cuts at a third and two thirds were tried first; they give D23 ≈ 0.95 at the closed-form noise (§5), too
    marginal.
  - Both informative outcomes are two-way claims (§9.J).
- **Noise for the D23 and §9.J simulations:**
  - h = 2 field-specific scatter σ_μ = 0.0213 (L16; taken equal to h = 1);
  - the reference line's error from nine h = 1 points with the same σ_μ;
  - b̂ from the line;
  - read noise at the SE model (L16: 0.69×, so ≤ 1× is conservative).
  - Stress variants: σ_μ × 1.5, and the h = 1 −7 field excluded from the reference.

## 5. D23, §9.J, power: closed-form estimates now, simulations before the seal

**Closed form** (desk arithmetic from committed stage-1 numbers; not the sealed figures):
- SE of the mean h = 2 offset: 0.0213/3 = 0.0071.
- Reference-line error at the h = 2 primary fields' mean C (4.30, against the h = 1 mean 3.17;
  S_xx = 8.63): 0.0213 × √(1/9 + 1.13²/8.63) ≈ 0.0108.
- Combined about 0.0129 in R, so SE(s) ≈ 0.0129/0.0455 ≈ 0.28 along C. The slope's own error is left to the
  simulation.
- The cuts are 1.95 SE from 0 and from −log 4:
  - P(CONDUCTOR | conductor exact) ≈ 0.974;
  - P(L-VALUE | L-value exact) ≈ 0.974;
  - P(INCONCLUSIVE | s = −0.69) ≈ 0.37.
- So D23 ≥ 0.95 holds for both informative branches, and every §9.J branch is reachable, under this noise.
- At σ_μ × 1.5: SE(s) ≈ 0.43, so D23 ≈ 0.90 for each. Below 0.95: decision D2b.

**Pre-seal simulations (to run only on Will's go, decision D2):**
- **(a) Parametric:** 200,000 draws per scenario (s = 0, −log 4, −log 4/2, and the stress variants). D23 for each
  informative branch, §9.J reachability, false-classification rates. No data.
- **(b) Planted witness (§9.D), on seen h = 1 data** (about 2 core-h, §8):
  - compute the nine h = 1 references and both thinned controls at X* and K_P;
  - each h = 1 field j stands in for an h = 2 field via 2R_rand,j − 1 (unbiased for R at matched X, by construction),
    against a reference line fitted on the other eight (leave-one-out, so the real field-specific scatter enters);
  - **unplanted** (s should read about 0), and **planted:** subtract R_ref(C_j) − R_ref(C_j − log 4), the predicted
    −log 4 shift, injected into the thinned controls as Will asked;
  - the gate must return CONDUCTOR unplanted and L-VALUE planted;
  - its power is shown by repeating over 200 thinning seeds and by the parametric run at the measured scatter.
- **(c)** the generator selftest (brute force, no data) and the §9.F dry double read on fixtures.

## 6. Reported, descriptive (no verdict)

- s and R against each reference:
  - (i) random-thinned: raw, and after the exact inverse 2R − 1;
  - (ii) χ′-thinned;
  - matched N (stage 1);
  - matched X (the primary).
- Each beside its §2 predictions under both hypotheses. The (ii) result is the hypothesis test of the twist mechanism.
- The descriptive nine h = 2 fields: their s (extrapolation, flagged), and the all-18 s.
- **K2:** −15's offset (2 split, primes above 2 non-principal).
- **Controls:** the correlation of the h = 2 offsets with L′/L(1,χ_D) and with Chen's L′/L(2,χ_D) term.
- β 0.45 and 0.40; the h = 2 within-field drift along prime order; the exact Spearman ρ of R_h2 on C over the 18.

## 7. Out-of-sample arm: L16 (one-way)

Will's L16, as amended: the h = 1 offsets are systematic and field-specific, either curvature in C_F (K0) or a second
variable.
- **K0 (the C-only null), declared form:** R = a + bC + cC² fitted on the nine h = 1 references, then frozen.
  - The prediction for each primary h = 2 field is K0's offset from the reference line at C_j + s, with s from §4.
  - **Statistic:** Spearman ρ between the predicted and observed within-h = 2 offsets (observed: R_h2,j − R_ref(C_j + s),
    minus their mean), over the nine primary fields, with an exact permutation p (9!).
  - **PASS iff p < α_K0 and ρ > 0.** One-way: a PASS is informative (the h = 2 pattern follows h = 1's curvature out
    of sample); a FAIL reads "FAIL (one-way arm: FAIL not informative)".
- **K1, decision D3.** Will: commit its functional form before any h = 2 compute, or drop it.
  - **Recommendation: drop it.** Its only theory-derived form in our framework is Chen's inert-prime constant A′_Φ(F)
    (eq. 9.27 with F's inert primes; RQ1B_STEP0 §4). That term comes from Chen's statistic including inert primes at
    θ = 0. Ours excludes them, so its rationale does not carry over. The L-term C_Φ,L is already a control (L15).
  - **If kept,** the form is K1 = A′_Φ(F)/C_Φ (Φ = 1_(0,1], contour Re β = 0.1, primes < 10⁵, `rq1b_constants.py`'s
    method), as a + bC + γ·K1, frozen on h = 1, the same statistic as K0.
- **Multiplicity:**
  - with K1 dropped, α_K0 = 0.05;
  - with K1 kept, Holm over K0 and K1 at familywise 0.05.
- **Power and §9.J:** the PASS branch's reachability and the null false-PASS rate (≤ 0.05; the exact permutation null
  holds by construction) are shown in pre-seal simulation (a). The planted case: h = 2 offsets that follow K0's
  frozen curvature, with h = 1 scatter in the residual.

## 8. Cost (model; §9.H stratified first wave)

| Item | Core-h (model) |
|---|---|
| h = 2 archives, 18 fields to 2·10¹⁰: 3,600 segments of 10⁸ at ≤ 51 s (FN1's measured, flat in k; the genus test skips Tonelli/Cornacchia on half the split primes, so this is an upper bound), × 1.2 queue contention (stage-2 measured) | **≈ 61** (range 40–61) |
| Pre-seal (b): h = 1 references + both thinned controls at X*, 9 fields (about 4× stage 1's single read, 0.2) | ≈ 1 |
| Pre-seal (a) parametric, (c) selftest | < 0.3 |
| §9.F dry double read on fixtures | ≈ 1 |
| Sealed double read (18 h = 2 sets + the nine h = 1 reference/control sets) | ≈ 2.5 |
| **Total** | **≈ 66** |

**§9.H first wave (timing only, before the bulk):**
- Covariates: segment index k (p size), the Cornacchia type (4p for D ≡ 1 mod 4, p for D ≡ 0 mod 4), and |D|.
- Cases: for each type, the smallest, median and largest |D| (type 1: −15, −115, −427; type 0: −20, −52, −232) × k ∈
  {1, 100, 199}. That is 18 tasks.
- Each task's model is interpolated in k per field, flat beyond.
- Stop rule: 1.25× at the mid and final checks, CPU-costed under pueue (`specarith-filler`).

## 9. Attribution, fixed before the read

- **CONDUCTOR:** at matched X and K, the h = 2 principal-prime sets sit on the h = 1 curve. R follows the analytic
  conductor |D|(w/2)², not L(1,χ_D), which differs from it by log 4 at these fields. This holds within the order kept
  in §2 (RW leading form + conductor constant).
- **L-VALUE:** a displacement of about −log 4. The class number enters R, through L(1,χ_D) or something equivalent.
- **INCONCLUSIVE:** no conclusion.
- **Either informative result assumes** the §2 statement that the genus projection leaves the excess unchanged.
  Thinned control (ii) tests the mechanism behind it, and is reported either way.
- **K0 PASS:** h = 1's curvature in C predicts the h = 2 pattern out of sample. It does not exclude a second variable
  in addition. A K0 FAIL carries no conclusion.
- **K2, the descriptive nine and the controls** carry no conclusion.

## 10. Decisions needed from Will

- **D1: the primary reference.**
  - The brief asks to measure the h = 2 displacement against the thinned h = 1 controls, with conductor → 0.
  - §2 shows that random half-thinning halves the excess exactly, and χ′-thinning raises R by about log|D′| along C,
    while the principal projection changes neither.
  - So against either thinned control a true conductor hypothesis would read near or beyond the L-value prediction.
  - **Proposed:** the primary uses the matched-X, matched-K unthinned h = 1 reference (conductor → 0 holds there at
    the order kept). The thinned controls run as specified: (i) as the by-construction witness and the planted-witness
    carrier, (ii) as the mechanism test. All displacements are reported with their derived predictions.
  - The alternative is to keep the thinned controls primary, with the §2 predictions replacing "0".
- **D2: pre-seal compute.** "No compute before the seal" is read here as no h = 2 data before the seal. The standards
  Will asked for need:
  - (a) parametric simulation, no data;
  - (b) about 1 core-h on seen h = 1 data;
  - (c) the generator selftest and the fixture dry run.
  - Go or no-go for each? (D2b: if the σ_μ × 1.5 stress puts D23 below 0.95, widen the cuts or accept it.)
- **D3: K1.** Drop (recommended), or keep with the A′ form in §7.
- **D4: X* = 2·10¹⁰.** That is matched N to stage 1 and about 61 core-h. A larger X* shrinks nothing that matters
  here (the field scatter dominates), at roughly proportional cost.
- **D5: D′ = 5 for control (ii).** A second D′ (e.g. 13) would test the log|D′| dependence, descriptively, at about
  0.3 core-h.

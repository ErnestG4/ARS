# Phase 6 — 6.0 seal: prime-spectroscopy instrument and gates G0–G4

**Status: TEXT APPROVED by Will (2026-10-07, fourth round, with the two additions G0-s and G0-c, now §8a–§8b).
The seal is not complete yet.** Remaining steps, in order: the code this text names is written and committed → the
pre-read computations of §9 run (tolerances, bands, χ₋₄ zeros, class lists; none computes a gate statistic) → a dry
run on the disclosed pilot scale (§11) → one seal commit carrying the code hashes and `seals/PH6_SEAL_6.0.json`
(sha256 of every file and input) → only then the gate run on spot. Any change to this text after today goes in a
dated amendment section at the end, never as an edit.

Sources: `PH6_BRIEF_v1.md`, `PH6_DECISIONS_2026-10-07.md` (three rounds; they win where they differ from the brief),
`lit/explicit_formulas.md` (EF), `lit/selberg.md` (SB), `lit/xp_candidates.md` (XP), `../DATA_MANIFEST.md`.
Design arithmetic quoted below comes from densities and theory only (no spectrum read); the sealed numbers come
from §9's pre-read computation.

---

## 0. A correction carried into this seal (CC's error, 2026-10-07)

CC told Will that "G1b's even − odd sum has no scattering term at all", and the third-round note repeats it. **That is
wrong.** SB §1.4 / §3.3: the whole continuous-spectrum term (φ′/φ, the h(0)/2, the ψ(1+ir) integral and the
ζ-prime lines 2Σ Λ(n)/n · g(2 log n)) sits in the EVEN sector. The difference even − odd therefore contains all of it.
What cancels in the difference is what both sectors share: the identity term, the elliptic terms and the hyperbolic
sum H. So:
- **even − odd (G1b) = reflection orbits R + the scattering/parabolic part (incl. ζ-lines at τ = 2 log n) + smooth terms.**
- **The scattering-free object is the ODD sector alone:** (1/24)∫r h tanh(πr) + (E2+E3)/2 + H/2 − R/2 − (3g(0)/4) ln 2
  − (1/4π)∫h ψ(½+ir).
The anchoring Will listed for G1b (Booker–Lee agreement to 2e-32 on even − odd; the Mayer cross-check) is unaffected.
§6 below gates each sector separately, so the cleanest single object (odd) is a gate of its own.

---

## 1. Inputs (pinned; fail closed on mismatch)

| input | pin | used by |
|---|---|---|
| `data/odlyzko_zeros1.txt` | sha256 3436c916…1632; 100,000 zeros, γ ≤ 74920.827498994; accuracy δ_ζ = 3·10⁻⁹ (upstream) | G0, G3 (density only) |
| `sessionK/maass_level1_partial.csv` | sha256 c6134f0b…a2; 600 forms, sym0 = even (266), sym1 = odd (334); complete to r_max = 98.76496727 | G1 |
| χ₋₄ zeros, computed (§9.1) | PARI 2.17.2 (cypari2 2.2.4), `lfunzeros(lfuncreate(-4), 20000)`, realprecision 38; file sha256 recorded at computation | G2 |
| `data/odlyzko_zeros6.txt` | sha256 2ef7b752…e7c6 | descriptive replication only (§10), not a gate |

---

## 2. The statistics, and why G0/G2 and G1 look different

**Zero sets (G0 ζ, G2 χ₋₄, G3 nulls, G4 picket fences, later the candidates).** Raw heights, never unfolded:

  S(τ) = Σ_{γ_k > 0} w(γ_k) e^{iτγ_k},   τ ∈ [0.5, 4.5].

This is the explicit formula's own variable (decision 2; Task B reconciled: S ≠ F(α), whose variable is scaled to the
Heisenberg time). The smooth part is taken from the exact θ (EF §7: the conductor and Γ terms together are
∫h dN_smooth with N_smooth = θ(T)/π + 1 for ζ, MV Thm 14.5 for χ).

**Maass spectrum (G1).** C_ε(τ) = Σ_{j ∈ sector ε} h_τ(r_j), with the EVEN test function
  h_τ(r) = [w(r) + w(−r)] · cos(τ r),
plus h_τ(i/2) for the constant eigenfunction in the even sector.

**Why they differ (Will's request, so nobody reads it as an inconsistency).** The two trace formulas admit different
test functions. The Guinand–Weil formula for ζ and for L(s,χ) holds for any h analytic in the strip with decay — h
need not be even (EF §3a: CCM 2015 Lemma 4; CMQR Lemma 9), and the prime side then carries g(+log n) and g(−log n)
separately. So the one-sided complex S(τ) is itself a legitimate test function: it keeps sign and phase in one line
per prime power, and the mirror zeros (−γ) enter as an exactly computed term M(τ). The Selberg trace formula for
PSL(2,ℤ) is proved only for EVEN h (BS07 Thm 2, hypothesis (b); SB §1.1), so G1 must use an even pair × cos(τr).
Both read the same thing: the even part of ζ's test function would give exactly Re-type information at each line.
Different-looking statistics, one principle: each gate uses the most informative test function its theorem admits.

---

## 3. Window and configuration rule (one rule for every spectrum)

Gaussian window w(E) = exp(−(E − T₀)²/(2σ²)) (entire, so EF §7 and SB §1.1 hypotheses hold).

For a spectrum complete on [E_lo, E_hi]: **T₀ = (E_lo + E_hi)/2, σ = (E_hi − E_lo)/(2·K_edge), K_edge = 8.5.**
E_lo = 0 when the list is complete from the bottom (ζ, χ, Maass: no levels are missing below the first one).

| gate | E_hi | T₀ | σ | line width 1/σ | w at the edge |
|---|---|---|---|---|---|
| G0 ζ | 74920.827 | 37460.41 | 4407.11 | 2.27·10⁻⁴ | 2·10⁻¹⁶ |
| G1 Maass (r) | 98.765 (r_max; decision: window inside r ≤ 98.76) | 49.38 | 5.81 | 0.172 | 2·10⁻¹⁶ |
| G2 χ₋₄ | 20000 (proposed; §12 Q1) | 10000 | 1176.5 | 8.5·10⁻⁴ | 2·10⁻¹⁶ |
| G0-s ζ small windows (§8a) | fixed, not by the rule: (T₀, σ) ∈ {(10, 4), (40, 3), (150, 10)} | | | | |
| G0-c ζ first 30,000 zeros (§8b) | γ₃₀₀₀₀ (≈ 25755; the exact value is read from the pinned file) | ≈ 12878 | ≈ 1515 | ≈ 6.6·10⁻⁴ | 2·10⁻¹⁶ |
| G3 nulls, G4 pickets | same as the gate they are read against (G0's configuration unless stated; G3-c at G0-c's) | | | | |
| candidates (6.1) | from the candidate's T1-rescaled range; **≥ 3·10⁴ levels, else NOT RESOLVABLE** (Will, round 4) | rule | rule | | |

**Where the smooth term Sm matters.** Sm(τ)/(σ/√2π) ≈ 2πρ̄·e^{−σ²τ²/2} at τ ≥ 0.5: it exceeds 10⁻⁶ only for
σ ≲ 12, i.e. spectra of order 10² levels. Every rule-configured gate and every ≥ 3·10⁴-level candidate has σ ≥ ~1500,
where Sm is negligible. G0-s (§8a) is therefore the exact test of the smooth/pole/θ code path, not of a configuration
candidates reach.

---

## 4. τ grids

- **Identity grid (Layer A):** τ = 0.5 + 0.001·j, j = 0…4000, PLUS the 13-point local grid of every line centre below.
- **Local grids (Layer B readout):** for each declared line position x: τ = x + (j/2)/σ, j = −6…6.
  Zero sets: x = log n, n = 2…90 (e^{4.5} = 90.02). G1: no Layer B (see §6.2).
- **Fine grid (exploratory free search, 6.2 only):** step 0.2/σ over [0.5, 4.5].

---

## 5. Layer A — exact identities (the gates' bar; decisions 3 and round 2)

For each gate, LHS = the statistic computed from the data; RHS = the identity's other side, evaluated independently.

- **ζ and χ₋₄ (EF §7, boxed identity; numerically verified to ≤ 4.7e-29 in EF §9):**
  S(τ) = −M(τ) + δ_{q,1}[h_τ(i/2) + h_τ(−i/2)] + g_τ(0) log(q/π) + (1/2π)∫w(u)e^{iτu} Re ψ(¼ + a/2 + iu/2) du
         − Σ_{n≥2} Λ(n)/√n [χ(n) g_τ(log n) + χ̄(n) g_τ(−log n)],
  g_τ(u) = (σ/√2π) e^{−σ²(u−τ)²/2} e^{−i(u−τ)T₀}; ζ: q = 1, a = 0, χ ≡ 1; χ₋₄: q = 4, a = 1.
  M(τ) = Σ_{γ_k>0} w(−γ_k)e^{−iτγ_k} from the same zeros. Prime sum to n ≤ 10⁴ (tail bounded, §5.1).
- **Maass, per sector (SB §1.4, from BS07 (2.39) at N = 1, χ = 1):**
  even: Σ_even h + h(i/2) = (1/24)∫r h tanh(πr) dr + (E2+E3)/2 + H/2 + R/2 + (g(0)/4) log(π⁴/2)
        − (1/4π)∫h(r)[ψ(½+ir) + 2ψ(1+ir)] dr + 2Σ_{n≥2} Λ(n)/n · g(2 log n)
  odd:  Σ_odd h = (1/24)∫r h tanh(πr) dr + (E2+E3)/2 + H/2 − R/2 − (g(0)/4) log 8 − (1/4π)∫h(r) ψ(½+ir) dr
  E2 = (1/8)∫h/cosh(πr), E3 = (1/(3√3))∫h cosh(πr/3)/cosh(πr); H = 2Σ_{t≥3} W(t²−4), R = 2Σ_{t≥1} W(t²+4),
  W(D) = Σ_{f|ℓ} h⁺(r[f]) [r[1]¹ : r[f]¹] · log ε₁/√D · g(2 log((t+√D)/2)), D = dℓ². Classes to t ≤ 30.
- **Picket fence (G4), Poisson summation (exact):** levels E_n = (θ + 2πn)/λ, λ = log(L/l), n ∈ ℤ;
  Σ_n w(E_n)e^{iτE_n} = (λ/2π) Σ_k e^{ikθ} W(τ − kλ), W(ν) = σ√(2π) e^{−σ²ν²/2} e^{iνT₀}.
  (BC per decision 4 and Endres–Steiner 2010 eqs. (149)–(150): √L ψ(L) = e^{iθ}√l ψ(l). θ = 0 sealed.)

### 5.1 Tolerance (decision 3: declared numerical error + window-truncation bound, computed in advance)

ε(τ) = 2 × [ε_data(τ) + ε_float(τ) + ε_trunc + ε_rhs(τ)]   (factor 2 = declared safety margin)
- ε_data(τ) = δ · Σ_k (τ·w(γ_k) + |w′(γ_k)|) — the worst-case effect of input inaccuracy δ on the LHS. This is a
  non-oscillatory sum over the positions; it does not compute or reveal S(τ). δ: ζ 3·10⁻⁹ (Odlyzko); Maass 5·10⁻⁹
  (8-decimal rounding of certified values); χ₋₄: 10× the max |difference| between realprecision 38 and 57 runs (§9.1).
- ε_float(τ) = Σ_k w(γ_k)(|τγ_k| + 1)·2⁻⁵¹ + summation term (compensated summation, `math.fsum` on real/imag parts).
- ε_trunc = bound on Σ over levels above E_hi of |h_τ|: ρ̄_max · ∫_{E_hi}^∞ w · (1 + margin for S(T)); ≈ 10⁻¹³ (G0).
- ε_rhs(τ) = mpmath quadrature error estimates (dps 30) + prime-sum tail beyond n = 10⁴ + class-sum tail beyond t = 30.

Design value at G0: ε_data ≈ 2·10⁻⁴ at τ = 4.5 dominates. The smallest term a red path removes is ≈ 152 (the k = 6
line at log 64), so the bar has ~10⁶ headroom.

**Layer A verdict:** PASS iff max over the identity grid of |LHS − RHS|/ε(τ) ≤ 1; else FAIL (as sealed, §8 ladder).

---

## 6. Layer B — the spectroscopy readout (this is T3's instrument)

### 6.1 Readout
P(τ) := S(τ) + M(τ) − Sm(τ), and r(τ) := P(τ)/(σ/√2π). Sm is the smooth part of the spectrum's own known answer:
for ζ/χ₋₄ the pole, conductor and Γ terms of §5 (θ-exact); for nulls mapped by N̄⁻¹, the target's θ-term; for a
picket, its k = 0 Poisson term. (At G0's σ, Sm is below 10⁻³⁰⁰ for τ ≥ 0.5; it matters only for small σ.)
By §5, for ζ/χ: P(τ) = −Σ_n Λ(n)/√n [χ(n) g_τ(log n) + χ̄(n) g_τ(−log n)], and the g_τ(−log n) lines sit at τ < 0.
On the local grids of all n = 2…90 jointly, least-squares fit r(τ) = Σ_n c_n · e^{−σ²(τ−log n)²/2} e^{i(τ−log n)T₀}
(complex c_n). The theorem predicts c_n = a_n with
  ζ: a_n = −Λ(n)/√n;   χ₋₄: a_n = −χ₋₄(n)Λ(n)/√n;   "silence" reference: a_n = 0.

### 6.2 Band, resolvable set, arms
- **Band B_n** for a configuration: from GUE null draws at that configuration (§7), s_n² = mean |c_n|² over the
  calibration draws; B_n = s_n·√ln(89/α), α = 0.01 (complex-Gaussian tail, Bonferroni over 89 positions).
- **Resolvable set R** = {prime powers n ≤ 90 : |a_n| ≥ 2B_n}. Design values (theory K(t) = |t|, to be replaced by the
  draws): G0 29/34 (not 16, 27, 32, 64, 81); G2 at T = 2·10⁴ 22/28 (not 25, 27, 49, 81, 83, 89; 3, 5, 7, 9 all in R);
  a 10⁴-level candidate 10/34; a 3·10⁴-level candidate 26/34.
- **Arms:** POSITION (|c_n| > B_n for n ∈ R), WEIGHT (|c_n − a_n| ≤ B_n for n ∈ R), SIGN (Re c_n · a_n > 0 for n ∈ R),
  SILENCE (|c_n| ≤ B_n for every non-prime-power n ≤ 90, and for every n with a_n = 0, e.g. powers of 2 under χ₋₄).
- **G1 has no Layer B.** At G1's resolution (line width 0.17) hyperbolic, glide and 2 log n lines overlap
  (4.127/4.159/4.189; 3.850/3.892); a per-line readout would be ill-conditioned. G1's gate is Layer A only.

### 6.3 T3 verdict rule (sealed here; applied to candidates in 6.1)
Minimum resolvable set M = {2, 3, 4, 5, 7}.
- **NOT RESOLVABLE** if M ⊄ R at the candidate's configuration (too few levels to tell primes from GUE noise).
- **PASS** if POSITION, WEIGHT, SIGN hold for every n ∈ R and SILENCE holds.
- **FAIL** otherwise; attribution = the list of failed arms and n's (e.g. "POSITION absent at all n ∈ R").
- **INAPPLICABLE** if the candidate's levels are defined by the zeros (circular; e.g. BBM per decision 7) or T1 gives
  no energy scale. The energy scale is fixed from T1 before T3 is read (decision 8).
- Prime powers outside R are reported descriptively, never scored.

---

## 7. Nulls (G3) and their own known answers

- **GUE:** Dumitriu–Edelman β = 2 Hermite tridiagonal (as arsrh Phase 1), size 1.25 × the target count, central 80%,
  unfolded by the semicircle CDF, then mapped onto the target's θ-exact smooth count by N̄⁻¹ (decision 2) so its smooth
  density equals ζ's (or χ₋₄'s) exactly. **Poisson:** i.i.d. uniform in the unfolded variable, same count, same map.
- Draws per configuration: 200 GUE + 200 Poisson; the first 100 of each = calibration (bands), the second 100 =
  held-out (G3 test). Seeds sealed (`numpy.random.default_rng(seed)`, seeds 1000–1199 GUE, 2000–2199 Poisson).
- **Null known answers (the null must pass its own before it calibrates anything):** mean |c_n|² over the
  calibration draws within 20% of the form-factor prediction (GUE: Σw²·(log n/τ_H)/(σ/√2π)², τ_H = log(T₀/2π);
  Poisson: Σw²/(σ/√2π)²); unfolded GUE ⟨r̃⟩ within the arsrh Phase-1 tridiagonal band of 0.6027.
- CUE omitted: in the unfolded bulk it carries the same sine-kernel statistics as GUE (§12 Q5).

---

## 8. Gates (all must PASS before any candidate is read)

| gate | Layer A (exact) | Layer B (readout) | red paths — each MUST FAIL |
|---|---|---|---|
| **G0** ζ, zeros1 | identity holds on the grid | vs ζ weights: PASS (all arms, R from G3 band); vs χ₋₄ weights: FAIL | RP1 drop all k ≥ 2 terms from RHS; RP2 flip the prime-sum sign; RP3 data shifted γ + 100δ; RP4 plant a line of 2B at log 6 in r(τ) → SILENCE flags |
| **G1-even**, **G1-odd** Maass | identity holds per sector (window inside r ≤ 98.76) | none (§6.2) | RP5 elliptic weights ×2; RP6 drop R; RP7 swap parity labels; RP8 drop the scattering terms from even; RP9 hyperbolic class counts from the wrong discriminant (t²+4 ↔ t²−4) |
| **G1a / G1b** | implied by the sector gates (tolerance = sum); reported | — | — |
| **G1-pre** class lists | three enumerations agree exactly for t ≤ 30: (i) Gauss-reduced cycles of discriminant t²∓4; (ii) Mayer/Efrat continued-fraction cycles (even period ↔ hyperbolic, odd period ↔ glide); (iii) PARI Σ_{f\|ℓ} h⁺(df²) | — | — |
| **G2** χ₋₄ to T = 2·10⁴ | identity holds | vs χ weights: PASS, incl. SILENCE at 2, 4, 8, 16, 32, 64 (χ(2) = 0) and SIGN at 3 (+), 5 (−), 7 (+), 9 (−: χ(9) = +1); vs ζ weights: FAIL | RP10 use χ ≡ 1 on the RHS; RP11 use a = 0 (wrong Γ parity) |
| **G3** nulls (held-out) | — | vs zero weights: GUE exceed-any-B_n rate ≤ α + binomial 99% allowance (Poisson against its own band, same rule); vs ζ weights: T3 = FAIL or NOT RESOLVABLE in 100% of draws (FAIL expected at G0's configuration) | positive control: GUE + planted ζ lines (c_n = a_n added to r(τ)) → T3 PASS in ≥ 95% of draws (the readout can pass) |
| **G4** pickets at G0's configuration | Poisson-summation identity holds, both pickets | λ = log 2 (confusable): POSITION fires at 2, 4, 8, 16, 32, 64 (c = +log 2 each); T3 vs ζ = FAIL with WEIGHT/SIGN attribution; SILENCE holds at 3, 5, 7. λ = 1.2345 (incommensurate; multiples ≥ 0.0101 from every log n ≤ 90 = 44 line widths): silent at all n ≤ 90; T3 vs ζ = FAIL (POSITION absent) | RP12 picket RHS with the brief-v1 BC (E − i/2) → FAIL |

| **G0-s** ζ small windows (§8a) | identity holds at each of the three (T₀, σ) | none | RP13 drop the Γ term; RP14 drop the pole term h(±i/2) (bites at T₀ = 10); RP15 replace Re ψ(¼+iu/2) by its leading asymptotic log(u/2); RP16 drop the mirror term M |
| **G0-c** ζ first 30,000 zeros (§8b) | identity holds | vs ζ weights: T3 = PASS; M ⊆ R; \|R\| ∈ [22, 30] (design 26/34) | RP17 the G0-c spectrum read vs χ₋₄ weights → FAIL |
| **G3-c** nulls at G0-c's configuration | — | held-out GUE vs zero weights: same silence rule as G3; vs ζ weights: T3 = FAIL in 100% of draws (power at candidate size) | positive control as in G3, at this configuration |

### 8a. G0-s — small-window ζ identity (Will, round 4)
Data: the first zeros of `odlyzko_zeros1.txt` (all zeros with γ ≤ T₀ + 8.5σ are present). Configurations
(T₀, σ) = (10, 4), (40, 3), (150, 10) — none equal to the disclosed pilot's (60, 6). Layer A only, same tolerance
construction (§5.1), τ on the identity grid.
**Red-path reachability (applies to every red path in this seal):** before the seal commit, §9 computes from the RHS
alone (no LHS, no gate statistic) the magnitude of the term each red path removes, at each configuration. A red path
counts only where that term exceeds 2ε(τ) at some τ on the grid; where it cannot fire it is reported INAPPLICABLE at
that configuration, never as passed. (Design estimate: the pole term is ≈ 0.04 at T₀ = 10 and negligible at the other
two; the mirror term is ≈ 10⁻⁸ at T₀ = 10, comparable to ε there, so RP16 may be INAPPLICABLE as configured — §9 decides,
and the result is reported to Will before the seal commit.)
Purpose, stated honestly: this is the only gate in which Sm, the pole term and the exact-θ Γ integral are tested
exactly. Under §3's rule no ≥ 3·10⁴-level candidate reaches σ this small (§3 note); G0-s protects the code path.

### 8b. G0-c — real-zero positive control at candidate size (Will, round 4)
Data: zeros 1–30,000 of `odlyzko_zeros1.txt` (a ζ spectrum of exactly the minimum candidate size, complete from the
bottom, so the §3 rule configures it the way a T1-rescaled candidate is configured). Band B_n from GUE nulls at this
configuration (§7, G3-c draws).
- T3 vs ζ weights must read PASS; M = {2,3,4,5,7} ⊆ R; |R| ∈ [22, 30] (design value 26/34, from K(t) = |t|).
- What it can and cannot show: on real zeros the explicit formula makes c_n = a_n at any size, so G0-c tests that the
  T3 rule does not reject the truth at candidate size, and that the band built from the draws agrees with the design
  theory (R depends only on the band). It cannot show power; G3-c does (GUE at the same configuration must FAIL).
- If |R| falls outside [22, 30], the ≥ 3·10⁴ minimum (§3) is revisited by a written amendment before any candidate is
  read; it is never adjusted silently.

Gate verdicts: PASS / FAIL (as sealed). A FAIL is reported as FAIL with attribution; no re-run with changed rules
without a written amendment.

**Failure ladder (Will, round 3; applies to every Layer A FAIL, in this order):**
1. Each RHS term's weight against its source equation — G1: BS07 eq. (2.39) term by term (identity 1/24 per sector;
   E2, E3 halves; the ± on R; g(0) constants; ψ coefficients; 2Λ(n)/n at 2 log n) BEFORE anything else; ζ/χ: EF §7
   against CCM 2015 Lemma 4 / CMQR Lemma 9.
2. RHS numerics: quadrature error estimates, prime/class-sum tails, the closed form of g_τ.
3. Inputs: hash, completeness (G1: Weyl per sector), parity labels, accuracy δ.
4. LHS numerics: summation, the mirror term, the h(i/2) term.
A third source for the elliptic weights (Iwaniec Thm 10.2 or Hejhal Vol. 2) is added when reachable.

---

## 9. Pre-read computations (before the seal commit; none computes a gate statistic)

1. **χ₋₄ zeros** on spot (env `specarith`): T ≤ 20000 at realprecision 38 (~2 h), then a subset re-run at
   realprecision 57; δ_χ = 10 × max |difference|. Count checked against MV Thm 14.5 within |S| < 2.
2. **G1-pre**: the three class enumerations to t = 30.
3. **Tolerances ε(τ)** for G0, G1-even, G1-odd, G2, G4 on the identity grid (§5.1).
4. **Null draws and bands** at G0's, G0-c's and G2's configurations; null known answers (§7).
5. **Design table** (R per configuration; the T3 minimum-set check) written to `seals/PH6_SEAL_6.0.json`.

## 10. Descriptive, not gates
- zeros6 (2·10⁶ zeros) through the same pipeline (all 34 prime powers expected resolvable there).
- Plots: S(τ) or C_ε(τ) for ζ, Maass (each sector), χ₋₄, one GUE and one Poisson draw, both pickets, on the same axes.

## 11. Disclosed pilots (before this seal)
- EF agent (2026-10-07): the §5 ζ/χ identity on 50 ζ zeros and 81 χ₋₄ zeros (T₀ = 60, σ = 6), agreement ≤ 4.7·10⁻²⁹.
  No gate configuration, no Layer B.
- SB agent (2026-10-07): per-parity Weyl counts on the Maass list (completeness), and transcription identities that use
  no eigenvalues.
- CC (2026-10-07): PARI timing on χ₋₄ to T = 1000 (counts and the first zero only).
Will (round 3): fine as disclosed — identities that cannot be tuned, small subsets, no gate statistic.

## 12. Decisions on the draft's open questions (Will, round 4; `PH6_DECISIONS_2026-10-07.md`)
1. **G2 height: T = 2·10⁴** (keeps all four sign arms, incl. log 9).
2. **Candidates: ≥ 3·10⁴ levels, NOT RESOLVABLE otherwise**, validated empirically by G0-c (§8b).
3. **G1: gated per sector**; G1a (sum) and G1b (difference) reported as implied.
4. **α = 0.01, K_edge = 8.5, safety factor 2: accepted.**
5. **CUE left out of G3: accepted.** It is kept separate from Phase 2's finite-size CUE(N_eff), which is a different
   question and stays with T2.
6. **T3 uses the GUE band: accepted.**
7. Added: **G0-s** (§8a) and **G0-c** with **G3-c** (§8b).

## Amendments
(none yet; any change after 2026-10-07 is appended here with date, reason and Will's approval)

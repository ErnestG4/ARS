# GEO-CM1 seal: Ford exponent of critical circle-map tongues along metallic paths — STATUS: DRAFT (Will's five corrections applied). Not sealed; nothing computed

Map F(θ) = θ + Ω − (1/2π) sin 2πθ (K = 1, cubic critical point), lifted to ℝ. Paths: convergents p_n/q_n of
ω_a = [0; ā], a = 1…10; cusp path 1/N, N = 2…200. Desktop CPU only (spot is on RQ1-c).

## 1. What traces to what (derivation status)

| Statement | Basis | Status |
|---|---|---|
| f(a) = ln\|δ_a\| / (2 ln λ_a) | definitional: if w_n ∝ \|δ_a\|^{−n} and q_n ∝ λ_a^n, then ln(w_n/w_{n+1}) / (2 ln(q_{n+1}/q_n)) → ln\|δ_a\|/(2 ln λ_a) | derived here; reproduces the gate values (ln 2.833612 / 2 ln φ = 1.0822; ln 6.79924 / 2 ln(1+√2) = 1.0874) |
| golden \|δ\| = 2.833612, silver 6.79924 | Ostlund–Rand–Sethna–Siggia 1983 (Physica D 8) | UNVERIFIED here (not read this session) |
| cusp path w ∝ q^{−3}, i.e. f_N → 1.5 | Cvitanović–Shraiman–Söderberg 1985; Ecke–Farmer–Umberger 1989 | UNVERIFIED here (not read this session) |
| f(a) strictly increasing, f(a) < 1.5, f(a) → 1.5 as a → ∞ | the PI's conjecture (browser preview), motivated by the metallic paths approaching the cusp 0 as a → ∞ | **no derivation**; these are predictions, not consequences |

## 2. Method and its gates
1. **Seed** each tongue edge's extremum from a plain-double grid of M = 16q points (numba).
2. **Bracket check in high precision (correction 1).** Before any bisection, each bracket end is evaluated at 30 digits
   with the extremum polished there: at the lower end the edge condition must have the "not locked" sign, at the upper
   end the "locked" sign. A wrong sign → widen the bracket ×2 about its centre and re-seed (at most 5 times; then the
   level is reported as failed and excluded). **The number of brackets needing a fix is reported per path and level.**
3. **Edges** by bisection in Ω (extremum tracked by Newton at each step) and independently by Newton on the
   saddle-node system F^q(x) − x − p = 0, (F^q)′(x) = 1; they must agree to ≤ 10⁻³ of the width (method gate).
4. **Two precisions,** 30 and 50 digits (mpmath): widths must agree to ≤ 10⁻⁶ relative, else the level stops the path.
5. Levels run while the edge precision is ≤ 10⁻⁶ of the width and q ≤ 2·10⁴.

## 3. Per-path estimate and its SE (correction 2), committed before any a ≥ 3 value is read
- **Levels in each fit:** all levels with q ≥ 10 that pass §2; f_n from consecutive pairs.
- **Correction model:** geometric, f_n = f + c·ρⁿ. The estimate f̂(a) is the three-point (Aitken) extrapolation from
  the last three f_n; **SE(a) = |Aitken(last three) − Aitken(the three before)|** (needs ≥ 4 f_n, i.e. ≥ 5 widths).
  A path with fewer f_n has no SE and is UNPOWERED for every clause that needs it.
- **Levels expected at q ≤ 2·10⁴:** a = 1: ≈ 20; a = 2: 11; a = 3: 8; a = 10: 5 (q = 1, 10, 101, 1020, 10301), so a = 10
  has 4 f_n of which those from q ≥ 10 are 3: one Aitken triple and **no SE → UNPOWERED** unless the q = 1 level
  passes as a usable start. This is stated before reading.

## 4. The sealed predictions and how they are judged (correction 3)
Per a: SE_d(a) = √(SE(a)² + SE(a+1)²).
- **P1, monotonic:** each pair (a, a+1) is SUPPORT if f̂(a+1) − f̂(a) > 2·SE_d, CONTRADICT if < −2·SE_d, else UNPOWERED.
  FAIL iff any pair CONTRADICTs; PASS iff every pair SUPPORTs; otherwise PASS on the supporting pairs, UNPOWERED on the
  rest (listed).
- **P2, f(a) < 1.5:** per a, SUPPORT if f̂(a) + 2·SE(a) < 1.5, CONTRADICT if f̂(a) − 2·SE(a) > 1.5, else UNPOWERED.
  Same aggregation.
- **P3, f(∞) = 1.5** (correction 4): extrapolation form, declared now, f(a) = f∞ + c₁·x + c₂·x², x = 1/ln λ_a,
  weighted least squares over the a with an SE. **Validation on the cusp path:** the same form in x = 1/ln N applied to
  f_N (N = 24…200) must give 1.5 ± 0.02 (the PI's cusp gate); the form counts as validated only then. **Tolerance
  basis:** 0.02 (the form's validated accuracy on a known limit) + 2·SE(f∞) from the fit, with PASS iff
  |f∞ − 1.5| ≤ 0.02 + 2·SE(f∞). If 2·SE(f∞) > 0.03 (tolerance above the PI's 0.05) the clause is UNPOWERED.
- **New values:** bronze |δ₃| and f(3) with SE(3).

## 5. Witnesses (correction 5)
- **Quintic map (z = 5), golden path — expected, not guaranteed.** Different inflection orders are different
  universality classes, so f(1; z = 5) is expected to differ from 1.0822, but no published quintic golden |δ| was found
  (UNVERIFIED) and no theorem fixes the size of the difference. **Reported, not a must-fail:** the committed check is
  |f̂(1; z=5) − 1.0822| > 5·SE(1; z=5), and its outcome is descriptive.
- **Proposed clean must-fail (for Will):** the subcritical map K = 0.5, golden path. For an analytic circle
  diffeomorphism the tongue widths decay exponentially in q (Arnold; UNVERIFIED in source here), so f_n grows without
  bound. Must FAIL the geometric-convergence check: committed as f_n increasing at every one of the last three levels
  and the last f_n > 3. If it does not fail, the pipeline cannot tell power-law from exponential scaling.

## 6. Standing rules (a ≥ 3 is unseen)
- The seal file is committed, hashed and OpenTimestamps-stamped; **a ≥ 3 is read only after the Bitcoin attestation is
  verified on two explorers.**
- Pinned environment (desktop WSL): Python, numpy, numba, mpmath versions and the kernel, recorded in §7.
- **Double read:** two separate processes from a clean start; result JSONs must `cmp` bit-identical (mpmath and the
  numba grid are deterministic; the grid's parallel reduction is per-point, no reordering).
- Gates (golden, silver, cusp) run and pass before the seal is stamped; their values may be read.

## 7. Cost (priced): ≈ 4–5 core-h, ≈ 30–45 min wall on the desktop's 12 cores (round "price" message). The bracket
checks add ≈ 2 high-precision extremum polishes per edge and level (minor). Pins: PENDING.

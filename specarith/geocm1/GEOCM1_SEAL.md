# GEO-CM1 seal: Ford exponent of critical circle-map tongues along metallic paths — STATUS: SEALED as of the tag geocm1-seal (final: section 11). a ≥ 3 not computed

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

## 8. Additions at go (Will, 2026-10-27)
- **K = 0.5 must-fail:** the path is capped at q ≤ 34 (golden convergents 13, 21, 34 within the q ≥ 10 rule, plus the
  smaller ones for the f_n trend) and run at a fixed 50 digits, which exceeds q·log₁₀(1/K) + 20 = 30.2 at the cap.
  The fail condition is as in §5, evaluated on all its f_n (the q ≥ 10 rule does not apply to this witness).
- **f(∞) fit:** an a with no SE is **excluded** (no borrowed SE).
- **Power, counted from the denominators alone (no width computed), under §3's rule 10 ≤ q ≤ 2·10⁴:**

| a | denominators in the fit | f_n | status |
|---|---|---|---|
| 1 | 13 … 17711 (16) | 15 | estimate + SE |
| 2 | 12 … 13860 (9) | 8 | estimate + SE |
| 3 | 10, 33, 109, 360, 1189, 3927, 12970 | 6 | estimate + SE |
| 4 | 17, 72, 305, 1292, 5473 | 4 | estimate + SE |
| 5 | 26, 135, 701, 3640, 18901 | 4 | estimate + SE |
| 6 | 37, 228, 1405, 8658 | 3 | estimate, no SE → UNPOWERED |
| 7 | 50, 357, 2549, 18200 | 3 | estimate, no SE → UNPOWERED |
| 8 | 65, 528, 4289 | 2 | no estimate → UNPOWERED |
| 9 | 82, 747, 6805 | 2 | no estimate → UNPOWERED |
| 10 | 10, 101, 1020, 10301 | 3 | estimate, no SE → UNPOWERED |

  So the UNPOWERED range is a = 6–10, wider than the a = 8–10 expected, and the f(∞) fit would rest on a = 1–5
  (x = 1/ln λ_a from 2.08 to 0.61), so P3 is likely UNPOWERED as committed. **Open for Will before the read:** keep
  as committed, or raise the q cap for a ≥ 6 (e.g. to 2·10⁵, two more levels each: about 10× the cost of those paths).

## 7. Cost (priced): ≈ 4–5 core-h, ≈ 30–45 min wall on the desktop's 12 cores (round "price" message). The bracket
checks add ≈ 2 high-precision extremum polishes per edge and level (minor). Pins: PENDING.

## 9. Gate results (2026-10-27): **FAILED as committed**; nothing stamped, no a ≥ 3 path run
`geocm1_analyze.py gates` → `results/GATES.json` (desktop; Python and mpmath versions in each GATE_*.json). Every level
used passed both precisions (≤ 10⁻⁶) and the Newton cross-check (≤ 10⁻³ of the width); no bracket needed a fix.

| Gate | Result | Committed criterion | Outcome |
|---|---|---|---|
| golden | f̂ = 1.0822175 ± 1.2·10⁻⁹; \|δ̂\| = 2.8336107 ± 6.5·10⁻⁹ (q ≤ 17711) | within 3·SE and 6·10⁻⁴ of 1.0822 / 2.833612 | 6·10⁻⁴ met; 3·SE not → FAIL |
| silver | f̂ = 1.0873985 ± 2.3·10⁻⁹; \|δ̂\| = 6.7992252 ± 2.0·10⁻⁷ (q ≤ 13860) | same, against 1.0874 / 6.79924 | 6·10⁻⁴ met; 3·SE not → FAIL |
| cusp | f∞ = 1.4595 ± 0.0001 (1/ln N quadratic, N 24–199) | 1.5 ± 0.02 | FAIL |
| K = 0.5 must-fail | f_n = 1.88, 2.43, 3.32, 4.78, 7.10 | increasing, last > 3 | fails as required ✓ |
| quintic (descriptive) | f̂(1; z=5) = 1.1564231 ± 6·10⁻⁷ | \|f̂ − 1.0822\| > 5·SE | yes |

**Diagnosis (post hoc, no verdict changed):**
- **Golden / silver: the 3·SE clause was ill-posed.** The SEs (~10⁻⁹) are far below the precision of the quoted
  literature values (f to 10⁻⁴; |δ| to 10⁻⁶ and 10⁻⁵), so the clause can fail on rounding alone. f matches 1.0822 and
  1.0874 to every quoted digit. Golden |δ̂| = 2.8336107 is 1.3·10⁻⁶ from the quoted 2.833612; the published value is
  recalled as 2.8336106559 (UNVERIFIED, from memory), 4·10⁻⁹ ≈ 1 SE from the estimate, so the quoted value may be a
  rounding slip; it must be checked against ORSS 1983 before any re-gate. The golden δ_n alternate (period-2 corrections:
  2.8336125, 2.8336097, 2.8336112, 2.8336104), which the Aitken step handles, but the SE may still be optimistic.
- **Cusp: the declared extrapolation form was wrong.** f_N rises monotonically (1.4466 at N = 24, 1.4885 at 100, 1.4943
  at 199), and the 1/ln N quadratic extrapolates below its own last value. A 1/N quadratic (post hoc, not a gate) gives
  1.50007. The data are consistent with the q⁻³ law; the committed form is not validated, so the f(∞) clause (P3),
  which uses the same form family in 1/ln λ_a, is invalid as committed.
- Re-gating with corrected criteria is Will's call; nothing is redefined here.

## 10. Re-gate (Will, 2026-10-27; post hoc, labelled; the §9 FAILs stay filed)
**Golden / silver against the primary texts** (verified by a delegated read of ORSS 1983 and the de la Llave–Olvera–Petrov
(dLOP) preprint, mp_arc 07-104; the published J. Phys. A version not read). Tolerance: half a unit in the last quoted
digit + 3·SE.

| | estimate | ORSS 1983 | dLOP preprint | quoted f |
|---|---|---|---|---|
| golden \|δ\| | 2.8336106599 ± 6.5·10⁻⁹ | 2.83361 ± 0.00001 (Table I): PASS | 2.8336106559: PASS (4.0·10⁻⁹) | f 1.0822: PASS |
| silver \|δ\| | 6.7992251981 ± 2.0·10⁻⁷ | 6.79924 ± 2·10⁻⁵ (RG, p. 319), 6.79925 ± 5·10⁻⁵ (Table I): FAIL under the half-unit rule (1.5·10⁻⁵, 2.5·10⁻⁵), within ORSS's own stated errors | 6.79922516: PASS (3.8·10⁻⁸) | f 1.0874: PASS |

- The quoted golden 2.833612 is not in ORSS; it appears only via a 2003 preprint citing Shenker 1982 (not read); FAIL
  against it (1.3·10⁻⁶). **Which source governs the silver gate is Will's call.**
- **Quintic (descriptive):** golden |δ| = 3.0433806 ± 1.8·10⁻⁶, against dLOP's 3.04337774 for their standard quintic
  family (a different map): 2.8·10⁻⁶ ≈ 1.6 SE, a universality check; f(1; z = 5) = 1.1564 is a property of the z = 5
  class.

**Cusp form validation on fresh N: NOT VALIDATED** (`geocm1_cuspfresh.py`; predictions 687ec95e committed before the
computation). The first fresh run was void (my bug, absolute tolerance; de4adbe1). The corrected run is clean (edges
≤ 10⁻¹² of the width; Newton within 5·10⁻¹³; no bracket fixes). The fit on N ≤ 199 recovers 1.500067 (inside
1.5 ± 0.002), but the fresh f_N fall below their predictions by z = −1.3, −1.7, −2.1, −2.8, −3.2, −3.6, −3.8, −4.1 at
N = 220 … 1000: only N = 220 and 250 are inside the 2·SE band. The deficit grows smoothly (2·10⁻⁵ → 5·10⁻⁵): the
1/N + 1/N² form misses a slower correction, and its residual-based band is too narrow to absorb it. **As specified,
the form family does not count for h_a: the h_a clause cannot be judged** (UNPOWERED as an untested-form clause).

**Power:** of the a ≥ 6 paths, only a = 8 can gain a level within ≤ 1 core-hour (q = 34,840, 0.78 core-h; a = 6 1.19,
a = 9 1.38, a = 10 2.32; a = 7 none below 1.1·10⁵); a = 8 then has an estimate but still no SE: UNPOWERED either way.

**Remaining judgeable clauses:** monotonic and f(a) < 1.5, powered at a = 1–5 only. Whether to seal and read with those
alone is Will's call.

## 11. FINAL (Will, 2026-10-27; post hoc refinement, labelled) — the seal as stamped
**Tolerance rule:** the source's stated uncertainty where it gives one, otherwise half a unit in the last quoted digit,
plus 3·SE. **Primary gate values: dLOP** (preprint mp_arc 07-104 as read; the published J. Phys. A 40 (2007) F427
version is unread). ORSS 1983 is a cross-check under the same rule. The 2.833612 reference is dropped (it reaches us only
through a citing preprint).

| Comparison | estimate | reference (uncertainty used) | \|diff\| | tolerance | |
|---|---|---|---|---|---|
| golden vs dLOP | 2.8336106599 | 2.8336106559 (½ unit: 5·10⁻¹¹) | 4.0·10⁻⁹ | 2.0·10⁻⁸ | PASS |
| golden vs ORSS Table I | 2.8336106599 | 2.83361 (stated ±1·10⁻⁵) | 6.6·10⁻⁷ | 1.0·10⁻⁵ | PASS |
| silver vs dLOP | 6.7992251981 | 6.79922516 (stated ≤ 2 in the last digit: 2·10⁻⁸) | 3.8·10⁻⁸ | 6.1·10⁻⁷ | PASS |
| silver vs ORSS (RG, p. 319) | 6.7992251981 | 6.79924 (stated ±2·10⁻⁵) | 1.5·10⁻⁵ | 2.1·10⁻⁵ | PASS |

(ORSS Table I silver 6.79925 ± 5·10⁻⁵: 2.5·10⁻⁵, also PASS.) f(1) = 1.0822175 and f(2) = 1.0873985 agree with 1.0822 and
1.0874. **Quintic universality cross-check (not a gate):** golden |δ| = 3.0433806 ± 1.8·10⁻⁶ against dLOP's 3.04337774
for their standard quintic family, a different map: 1.6 SE.

**Cusp form:** NOT VALIDATED on fresh N (§10). **Cap:** a = 8 raised to q = 34,840 (0.78 core-h); a = 8 stays without an
SE.

**Sealed clauses for the read of a = 3 … 10** (`geocm1_analyze.py read`):
- **P1 monotonic** and **P2 f(a) < 1.5:** as §4 (SUPPORT / CONTRADICT / UNPOWERED at ±2·SE). Powered at a = 1–5 only
  (a = 6, 7, 8, 10 have an estimate without SE; a = 9 none): pairs (1,2) … (4,5) and a = 1 … 5.
- **P3 → h_a clause** (re-gate): h_a = ln(δ_{a+1}/δ_a) / (2 ln(λ_{a+1}/λ_a)), prediction h_a → 1.5 via
  h∞ + c₁/λ + c₂/λ². **UNPOWERED as sealed** (the form family failed its fresh-N validation); h_a reported descriptively.
- **New values:** bronze |δ₃| and f(3) with SE(3).

**Pins.** `geocm1.py` sha256 c42634a21113259dd0aefdb0a57d2bbbdd10d262f000458806297bb47d26cbc5; `geocm1_analyze.py` sha256 424f8686d76c643967255b6119d51a2c3011f399253c9eae6c54aa1498528246; `results/GATES.json` sha256 9019471c2e0126a09dd73697b158d8248062ab8b822adccbb7112cddf8e2ea81.
Environment (desktop WSL): {'python': '3.12.3', 'numpy': '2.4.4', 'numba': '0.66.0', 'mpmath': '1.3.0', 'kernel': '6.18.54.1-microsoft-standard-WSL2'}.
**Read procedure (after the OpenTimestamps receipt is Bitcoin-attested and verified on two explorers):** compute a3 … a10
twice, in two separate process sets from a clean start (`geocm1.py path aN READ{1,2}/READ_aN.json`); every pair of
JSONs must `cmp` byte-identical, else VOID; then `geocm1_analyze.py read` on READ1 (with GATES.json and GATE_a1/a2
copied in for a = 1, 2). Cost: ≈ 0.5–1 core-h per path per read, ≈ 6–12 core-h for the double read, on the desktop.

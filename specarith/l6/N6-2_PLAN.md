# N6-2: the n = 6 extraction across corrected (B)'s full estimator sum (round 81; plan, committed before computing)

**Arc.** N6-2 resumes n = 6 as a new arc (round 81). Time box: two sessions. Session 1 starts with this plan
(2026-10-25). Predecessor: `N6_CLOSEOUT.md`, paused at the time box with "extraction viable under the estimator's
kernel" at two points (§3.3, 739ccde4).

**Status of step 1: NOT STARTED.** Its cost (§2) exceeds the 300 core-h cap, so per round 81 the cost is reported
first.

## 1. Corrected (B)'s full estimator sum, and its pieces
- **The sum (derived from `../cs4/b2_est.py`; `N6_CLOSEOUT.md` §3.3):**
  W(G) = Δ Σ_k c_k C(kΔ), with Δ = 1/8 and c_k the Bartlett weights, over lags 0 ≤ kΔ < G. G is 300, 1,000, 3,000 or
  10,000. Every G ≤ 10,000 uses lags inside [0, 10,000), so the pieces of the G = 10,000 sum cover all four.
- **The r-partition.**
  - The partition of unity τ(x) = cos²(π/2·β(|x|/5)) (frozen, `../cs4/n6b_settle.py`) splits the lag axis into
    members centred at r₀ = 0, 5, 10, …, 10,000. Each member covers r₀ ± 5, i.e. 79 grid points.
  - Neighbouring members share grid points, so each grid point is computed once.
- **Long-range region (where the extraction is used).** The sealed extraction is defined for r ≥ R₀ = 20
  (`N6_STAGE_B_GATE.md`, "What is extracted"). The extraction pieces are the members whose support lies in [20, G):
  r₀ = 25, 30, …, 10,000, i.e. **1,996 members over 79,840 grid points**.
- **Short-range region (not extracted).** Members r₀ ≤ 20 (r < 25; 160 grid points, including the overlapping-window
  lags r < 4) are computed directly as brute force in any prediction. They are not gate pieces. Stage (c)'s connected
  term lives here.
- **The (a, b) split.** At each long-range grid point, C(r) = Σ_{a,b=1..3} c_a c_b ∫_{A^a×B^b} K_ab: nine (a, b)
  pieces. The extraction replaces each K_ab by its phase-filtered (class 0) part. The settling test gated only (3, 3).
  "Every piece" is therefore 1,996 members × 9 (a, b) pieces.

## 2. Cost of each piece (measured; ζ, ℓ = 15.75, PMAX 10³, 4 in-window nodes, distinct-node rule)
- Per grid point, all classes at once (brute and extraction come from the same evaluation). Measured locally on
  2026-10-25 at r = 100 (`rho_cls`, one call per piece).
- Spot = local × 4.08: the settling test's (3, 3) mean of 2,163 s per point on spot, against 530 s locally.
- Mirrored pieces, e.g. (2, 1) for (1, 2), are assumed to cost the same as the measured one.

| (a, b) piece | local s / point | spot core-h / point | spot core-h, all 79,840 points |
|---|---|---|---|
| (1, 1) | 0.1 | 1.1·10⁻⁴ | 9 |
| (1, 2) + (2, 1) | 2 × 1.1 | 2.5·10⁻³ | 200 |
| (2, 2) | 13.6 | 0.015 | 1,230 |
| (1, 3) + (3, 1) | 2 × 6.7 | 0.015 | 1,210 |
| (2, 3) + (3, 2) | 2 × 82.4 | 0.19 | 14,900 |
| (3, 3) | 530 | 0.60 | 47,960 |
| **all nine** | **724** | **0.82** | **≈ 65,500** (≈ 49 days on spot's 56 vCPUs) |

- Per member (79 points, shared with neighbours): ~33 spot core-h for all nine pieces, ~24 for (3, 3) alone.
- **Restricted sums, for scale only (not a re-scoping):**
  - G = 300 alone needs [20, 300): 2,240 points, ≈ 1,840 spot core-h.
  - The (3, 3) piece alone over G ≤ 10,000 is ≈ 48,000.
- **Every version exceeds the 300 core-h cap. Step 1 is not started.**
- **What would change the cost (Will's call; none is adopted):**
  - **A GPU port of the class-resolved jets** to the local 4090 (CuPy installed). Speed-up unmeasured, and it is
    engineering inside a two-session box.
  - **An amendment to the cap or the piece list.**
- **A structural note.** Running the gate on every piece at 4 nodes and PMAX 10³ computes brute force on the whole
  grid, and that is itself a (low-resolution, low-cutoff) evaluation of the sum. The extraction earns its keep only at
  production settings, where brute force is unaffordable. That is where a fresh-height confirmation (step 2) and the
  decision point sit.

## 3. The gate, frozen as in 739ccde4 (`../cs4/n6b_settle.py`; `N6_CLOSEOUT.md` §3.3)
- **Kernel:** corrected (B)'s exact weighting (lag counts of the estimator's window starts = Bartlett on the 1/8 grid).
  Each member uses the local partition weight w(r) = c(r)·τ(r − r₀), normalised, with c at G = 10,000.
- **Known answer:** re-run before any ζ point. The kernel applied to stage (a)'s exact U(N) C(kΔ) must reproduce W_B at
  G = 300, 1,000, 3,000 and 10,000 to 10⁻⁹ relative, or the run is void.
- **Witnesses, per member and piece, unchanged:**
  - **Tone:** 16·e^{±2πi·1.04(r − r₀)} in classes ±1 must move the gap by its predicted 2·16·T(1.04) within 1%, and by
    ≤ 10% of the tolerance.
  - **Slow:** 3 × tolerance, with the gap's sign, at 0.02 cycles per unit, must move it by its predicted transfer within
    1%, and must turn the reading to FAIL.
- **Tolerance:** |brute − extraction| ≤ 0.01·|brute|.
  - It derives from G-b3's seal line, `N6_STAGE_B_GATE.md` lines 61–62 (49d88b46, round 75): "Agreement: within the
    brute-force quadrature's own error, estimated by 4 against 6 Gauss–Legendre nodes per coordinate, or 1% of the
    brute-force value if that is larger."
  - G-b3 and the settling test applied the 1% branch alone. That is at least as strict as the sealed max(quadrature
    error, 1%).
- **Code needed before step 1 (no rule change):** `n6b_settle.py` evaluates the (3, 3) piece only. Step 1 needs the
  same task for each (a, b): brute = Σ classes of ρ_{a+b} − ρ_aρ_b, and extraction = class 0 − ρ_aρ_b. It also needs
  the member list of §1. Kernel, known answer, witnesses and tolerance are unchanged.
- **Hazards of the frozen rules, declared now, before any value is seen:**
  - **Small brute values.** The tone witness's "≤ 10% of tolerance" requires |brute| ≥ 2·16·|T(1.04)|/10⁻³ ≈ 0.115 in
    that member and piece. The amplitude 16 was set from the (3, 3) piece at r = 100. Small pieces ((1, 1), (1, 2)) and
    far members, where |brute| may be below 0.115, would then read VOID by the frozen rule, not PASS or FAIL.
  - **Zero crossings.** A member where brute passes near zero has a near-zero 1% tolerance, so a genuine sub-10⁻⁴ gap
    reads FAIL.
  - Both are recorded as they fall, per member and piece. They are not adjusted.

## 4. Reading
- **The extraction holds at ℓ = 15.75 only if every piece passes:** all 1,996 members × 9 (a, b) pieces, each with the
  known answer and WITNESS_OK.
- **Any failing (or VOID) piece is recorded,** with its r₀, (a, b), gap, tolerance and slow-content share, **and step 2
  does not start.**

## 5. Step 1
Run the frozen gate across all pieces at ℓ = 15.75. **Cost ≈ 65,500 spot core-h, above the 300 core-h cap, so it is
reported first (round 81). Not started.**

## 6. Step 2 (only if step 1 passes; rules committed now, before anything is computed)
### 6.1 G-b1 convergence for U(N) at 8, 10 and 12 nodes
- **Quantity:** G-b1 as sealed (`N6_STAGE_B_GATE.md`, "The gate"): C_long^ext(r), the extraction's U(N) value, at the
  60 log-spaced r in [20, 1000]. Each is evaluated at 8, 10 and 12 in-window nodes per coordinate. The distinct-node
  rule is valid there: K_ab = ρ^{non-osc} − ρρ vanishes at in-cluster coincidence.
- **Convergence criterion (committed now):** at every r, |X₁₂ − X₁₀| ≤ 0.1·max(0.01·|C̄(r)|, 10⁻¹¹). That is 10% of G-b1's
  own pointwise tolerance. X₈ is reported, not gated.
- **If converged,** G-b1 is read at 12 nodes against its sealed criteria 1–3, including both wrong variants failing.
- **If not converged,** G-b1 is recorded as unresolved at 12 nodes, and step 2 stops there.
- **Cost (from measured U(N) ρ₆ at ~0.39 s per configuration locally):**
  - configurations per r: 3,136 (8 nodes), 14,400 (10) and 48,400 (12) for (3, 3); the lower pieces are smaller;
  - ≈ 7.2 local core-h per r for all three node counts, so ≈ 430 local core-h ≈ 1,750 spot core-h for 60 r.
- **Kernel caveat:** G-b1 compares with C̄, the one-period average sealed in round 74. For U(N) that is adequate:
  its oscillating content is carrier × smooth envelope, with no small-prime offsets, removed to O(r⁻³). This is unlike
  ζ (`N6_CLOSEOUT.md` §3.2).

### 6.2 Fresh-height confirmation (rule committed now)
- **Height rule:** among corrected (B)'s four files, take the one whose ℓ̄ = ln(t_mid/2π) is farthest from every height
  used so far (15.75, 15.8202–15.8643, 21.75).
  - The result is zeros_2365046000, with ℓ̄ = 19.7466 (min distance 2.00; the others are 0.02, 1.67 and 0.50).
- **r rule:** numpy `default_rng(8102)`. Draw 2 members without replacement from {25, 30, …, 1000} ∖ {100, 300}, and 2
  from {1005, …, 10,000}.
  - The result is r₀ = 360, 995, 2465 and 2780.
- **Test:** the frozen gate (§3) on all nine (a, b) pieces at those four members, ℓ = 19.7466, PMAX 10³, 4 nodes.
  Every piece must pass.
- **Cost:** 4 members × ~33 spot core-h ≈ 130 spot core-h.

## 7. Decision point after step 2
Report to Will before anything else is funded: the full stage (c) run, the production cutoffs, and the sealed
prediction of corrected (B).

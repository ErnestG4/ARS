# N6-2: the n = 6 extraction across corrected (B)'s full estimator sum (round 81; plan, committed before computing)

**Arc.** N6-2 resumes n = 6 as a new arc (round 81). Time box: two sessions. Session 1 starts with this plan
(2026-10-25). Predecessor: `N6_CLOSEOUT.md`, paused at the time box with "extraction viable under the estimator's
kernel" at two points (§3.3, 739ccde4).

**Round 82: the every-piece gate (step 1, §§1–5) is WITHDRAWN.** It would be a full-grid brute force, which defeats the
extraction's purpose. The reasons on record are the cost table (§2) and the structural point at the end of §2.
- **Replaced by:**
  - the node check on the settling pass (§8, first);
  - then a sampled gate (§9), which runs only if the node check passes.
- **Step 2** (G-b1 at 12 nodes) stays queued behind the sampled gate. It is not funded.
- §§1–5 are kept below as the record of the withdrawn design.

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

## 5. Step 1 (WITHDRAWN, round 82)
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

## 8. Item 3 (round 82): node check on the settling pass. Cost reported first; NOT RUN
**What (round 82).**
- Recompute the brute − extraction gap at r₀ = 100 and 300 with the frozen kernel (79 points each, ℓ = 15.75,
  PMAX 10³) at 6 and 8 in-window nodes.
- Report the sealed G-b3 rule's 4-vs-6 quadrature-error branch: q = |brute₆ − brute₄| under the kernel, giving the
  sealed tolerance max(q, 0.01·|brute|).

**Reading (Will, round 82, committed now).** The settling pass stands only if the gap stays within tolerance at 6 and 8
nodes. Otherwise it is recorded as a 4-node artifact and N6-2 pauses.

**Cost (measured locally on 2026-10-25, (3, 3) `rho_cls` at r = 100; spot = local × 4.08 as in §2).**

| nodes | configurations per point | local s per configuration (batch) | local core-h per point | spot core-h, 158 points |
|---|---|---|---|---|
| 4 (settling) | 16 | 33 (16) | 0.15 | 95 (measured: 2,163 s per point) |
| 6 | 400 | 24.4 (64); 34.5 (16) | 2.7 | ≈ 1,750 |
| 8 | 3,136 | 26.4 (64) | 23 | ≈ 14,900 |

- **Total for the node check ≈ 16,600 spot core-h.** 6 nodes alone is ≈ 1,750, which is also the cost of the 4-vs-6
  branch. Both exceed the 300 core-h cap.
- **Per round 82, the estimate is reported before running.** Nothing has run.
- **Why it is this expensive.** Per-configuration cost is flat in batch size beyond ~64, and the configuration count
  grows as C(nq, 3)². No cheaper exact route is available at the same kernel: the kernel fixes 79 points per r₀, and
  the 4-vs-6 branch needs the full 6-node brute.

## 9. Item 4 (round 82): sampled gate. WITHDRAWN AS DESIGNED (round 83)
**Why withdrawn:**
- The 0.5% denominator, the extraction's full-grid total, is uncomputable within any cap.
- The projection as issued lacked ψ's weights.

The |c_a c_b| weights below are kept for any successor design. The rest of this section is the record.
**The extraction's full-grid cost (confirmed as round 82 asks).**
- The extraction is the phase-filtered class-0 part, evaluated by the same jets (`FilteredModel.rho_f`, NONOSC).
- Measured in the same local run on 16 (3, 3) configurations: 329 s, against 719 s for all classes. **That is 0.46 of
  the brute-force cost per point, not orders of magnitude less.**
- Full grid at 4 nodes (79,840 points, all nine (a, b) pieces): ≈ 0.46 × 65,500 ≈ 30,000 spot core-h. At 6 or 8 nodes
  it is ×25 or ×196.
- **So for ζ, the phase filter does not by itself make the evaluation affordable.** As S2.3 found, it separates for
  U(N) but not for ζ. Affordability needs a faster evaluator, such as the 4090 port asked for at the decision point.
- This also bears on the sampled gate's denominator, the "extraction's full-grid total". It cannot be computed within
  the cap. It would have to be estimated from the stratified sample itself, and that is a design point for Will.

**Weights the projection must carry.** The (a, b) pieces enter C(r) with ψ's falling-factorial coefficients c_a c_b
(`n6a_trace.psi_coeffs`): c₁ = 37 − 3σ² ≈ 35.7, c₂ = −9 and c₃ = 1. So |c_a c_b| ≈ 1,270 for (1, 1), 321 for (1, 2),
81 for (2, 2), 36 for (1, 3), 9 for (2, 3) and 1 for (3, 3). A stratum's projected gap is max|gap| × its summed
kernel weight × |c_a c_b|.

**Sizing at the node count item 3 supports.**
- Not determined: item 3 has not run.
- For scale: at 4 nodes (0.82 spot core-h per point, 79 points per member), 300 core-h buys ~4.6 members' worth of
  all-piece evaluations. At 6 nodes it buys less than one member's worth. A stratified sample across 6 piece groups ×
  several r bins × 2 heights does not fit in 300 core-h at any node count above 4.

## 10. Cost model (round 83; every proposed step is priced with it before it is issued)

  **spot core-h = C(n, 3)² configurations per point × points × s per configuration × 4.08 / 3600**

**Terms.**
- **C(n, 3)²:** the (3, 3) piece's distinct-node configurations at n in-window nodes per coordinate: 16, 400, 3,136,
  14,400 and 48,400 at n = 4, 6, 8, 10 and 12. Lower (a, b) pieces use C(n, a)·C(n, b).
- **s per configuration:** measured locally at ζ PMAX 10³ (`N6-2_PLAN.md` §8): ~33 s at batch 16 and ~25 s at
  batch ≥ 64 for (3, 3). For other pieces, scale by §2's per-point ratios. U(N) ρ₆ costs ~0.39 s per configuration at
  batch 2,048.
- **4.08:** spot's per-process slowdown against local. Measured as 2,163 s per (3, 3) point on spot against 530 s
  locally (the settling run).

**Checks against measured runs.**
- The settling test: 158 × 16 × 33 s × 4.08 ≈ 95 core-h predicted, against 95 measured.
- The (c) pilot is T₆ at PMAX 10², ζ part. It uses the product rule over node multisets, so its configuration count is
  (C(n + 2, 3))²: 14,400 at 8 nodes and 48,400 at 10, 62,800 in all.
  - Predicted: 62,800 × ~7 s (local, batch 128) × 4.08 / 3600 ≈ 500 core-h.
  - Measured: 487 core-h, i.e. 27.9 s per configuration on spot, or 6.8 s locally after the spot factor.
  - **So the configuration count must match the quadrature rule:** C(n, 3)² for the distinct-node rule, C(n + 2, 3)²
    for multisets.

## 11. Node diagnostic (round 83; a diagnostic, not a gate; asymmetric; committed before computing; `../cs4/n6b_nodediag.py`)
**Points (selected by the rule alone).**
- The rule: at each r₀ ∈ {100, 300}, the 12 kernel points with the largest |kernel weight × ψ weight|.
  - The kernel is the frozen settling kernel.
  - The (3, 3) piece's ψ weight is |c₃c₃| = 1, so the rule reduces to the 12 largest kernel weights.
  - The kernel's (1 − r/G) slope breaks the ±6 tie toward k = −6.
- The result is k = −6…+5 at both r₀, 24 points in all.
- **They carry 30.0% of each member's kernel weight.** The other 67 points (70%) are not checked.

**Compute.**
- The (3, 3) piece by class at 6 nodes: 400 configurations per point in 8 chunks of 50, as in `n6b_settle.task`
  (ℓ = 15.75, PMAX 10³, distinct-node rule). Brute = Σ classes; extraction = class 0; gap = brute − extraction.
- The 4-node values are reused from the settling run (`results/n6b/settle/tasks.tgz`).
- **Validation before launch (local, done):** the task code at 4 nodes reproduces the stored settling value at
  (r₀ = 100, k = 0) to 1.1·10⁻¹³ absolute (local against spot arithmetic; the value is −12.194).

**Report, per r₀.**
- The kernel-weighted partial sums over the 12 points, P_brute and P_gap, at 4 and 6 nodes, and their 4→6 changes.
- |ΔP_brute| as the sealed G-b3 rule's 4-vs-6 quadrature-error estimate, restricted to these points.

**Reading (Will, round 83).**
- **ARTIFACT:** |ΔP_gap| > 0.01·|P_brute(6)| at either r₀. The settling pass is then recorded as a 4-node artifact, and
  N6-2 pauses.
- **Otherwise:** "no 4→6 movement at the dominant points". That makes no claim of convergence.

**Cost (§10):** 24 × 400 × 24.4 s × 4.08 / 3600 ≈ 265 spot core-h, under the 300 cap. That is 192 tasks of ~1.4
spot core-h each (~4–5 h on spot at 48 processes).

**After it:** if it does not trigger a pause, Will decides on sharing the 4090 with the ARSv2 session before a one-piece
port benchmark is measured. No port before that.

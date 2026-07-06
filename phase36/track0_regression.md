# Track 0 — Regression Gate · Result

**Overall: PASS — Tracks 1-4 unblocked**

Config-justification: `TRACK0_CONFIG_JUSTIFICATION.md` (pre-authored).
Non-destructive (banked JSONs not overwritten). Deterministic AM leg — reproductions are bit-exact.

### 1. IDS-unfold leg ratio-free — **PASS** → `IDS_LEG_RATIO_FREE`
- λ=0.5 cell reproduces banked bit-exact: primary=BR_artifact, rep_med=0.8469, W1δ(L=10⁶)=0.00497 (banked 0.00497).
- L-convergence: W1δ(L=3×10⁵)=0.005263 → (10⁶)=0.00497 → (3×10⁶)=0.004831; last-decade swing=4.32e-04 ≤ φ-ensemble spread 5e-03 ✓ (only error param is L, decoupled from N; cf. old ref-N leg's 200–4000× swing).
- structural: no `N_ref` term in `unfold_rotnum`/`ids_rotnum` signatures → ratio-free by construction = True.

### 2. Zoo-gap ratio-clean — **PASS** → `ZOO_GAP_RATIO_CLEAN`
- at fixed N=2584/identical reference: sub W1δ(λ=0.5)=0.00497 vs sup W1δ(λ=1.5)=0.27686, contrast=56× ≥ 6× ✓ — a contrast a ratio-function cannot produce at fixed ratio.

### 3. 35b no-false-positive (N=2584, quadrant) — **PASS** → `NFP_NO_FLIP_REPRODUCED` (no-flip reproduced; banked auto-verdict UNRESOLVED; sub-quadrant sensitivity certified separately in item 4 — the gate certifies the no-FP half, and says so)
- signal primaries=['BR_artifact'], α-null primaries=['BR_artifact'] → no quadrant flip = True.
- characterize_transition: signal transition_detected=False, α-null=False → both flat (no false positive) = True.
- banked-cell bit-match (8 signal cells) = True.
- descriptive: signal sub-quadrant W1δ steps at λ=1 (max/min>10, Δ=0.281) vs α-null φ-noise (Δ=0.115) = True.
- banked auto-verdict reproduced honestly: `UNRESOLVED — neither pre-specified branch cleanl` — the no-FP property (the human-adjudicated banked claim) is what passes; the auto sub-quad branch is φ-noise-limited at N=2584 (separable only at N≳5×10⁴, item 4).

### 4. Sensitivity floor N≳5×10⁴ — **PASS** → `SENSITIVITY_FLOOR_PRESENT`
- N=50000: sub W1δ(λ=0.5)=0.00052 (→floor), sup W1δ(λ=1.5)=0.23546, gap=0.2349 ≫ spread ✓ — floor persists, sub≠sup separable at the use regime.
- **Margin-robustness to item-1's residual L-drift:** item 1's sub W1δ is still decelerating-but-not-pinned (≤4.3×10⁻⁴/decade, limit somewhere ≤0.0048). At the N=5×10⁴ use regime the sub side is 0.00052 — an order of magnitude below any such limit — and the separation gap is 0.235. Even if the true sub limit sat at 0.0048, gap→0.231 (margin essentially unchanged, ≫2.3). The N≳5×10⁴ separation does NOT consume the un-pinned tail; verdict robust.

### 5. Logistic + Mackey-Glass loci — **PASS** → `DYNAMICAL_LOCI_REPRODUCED`
- logistic λ₁: r=3.7 (chaos)=+0.3549 (banked +0.3555), r=3.83 (period-3 window)=-0.3697 (banked −0.3697).
- Mackey-Glass λ₁: τ=23 (chaos)=+0.01009 (banked +0.0101), τ=10 (periodic)=+0.000042 (banked ~+4e-5).
- signs reproduced=True, magnitudes within tol=True.

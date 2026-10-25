# RQ1 reading seal — STATUS: DRAFT for Will (round 85). Not sealed; no OpenTimestamps receipt; nothing read

**Step 3 runs only after:** Will approves this seal, its OTS receipt is Bitcoin-attested and verified on two explorers,
the environment is pinned, and the double read is in place.

**Archive.** The ℤ[√2] reduced generators, one per split prime, from `rq1_archive.py`.
- Its hash goes in §6 when Step 2 finishes: the sha256 over the 1,000 segment hashes, plus per-segment hashes in
  `MANIFEST.json`.
- No statistic of the angles has been computed from it.

## 1. Statistic
R(β, X) = Var(N_{K,X}) / (N/K):
- **Var:** RW's eq. 1.2 (window-centre average over θ ∈ [0, 1), window 1/K), computed exactly (`rq1_angles.var_exact`).
- **N:** the number of prime ideals above split p with N𝔭 ≤ X (both ideals: θ and 1 − θ). Inert primes and 2 are
  excluded; RW's N would include them, which differs by ≤ √X points at θ = 0.
- **K = round(N^β).**

## 2. X values and K grid
- **X:** 10¹⁰ (N ≈ 4.6·10⁸) and 10¹¹ (N ≈ 4.1·10⁹), both from the one archive.
- **β grid:** {0.20, 0.30, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90}, the same at both X.

## 3. Prediction (Step 0 §3)
- **Leading order, at the level of RW's heuristic:** R → min(1, 2β).
- **Lower-order terms are not derived.**
- **A heuristic next-order statement** (not a derivation):
  - With log q(λ^k) = 2 log k + C_F, the field enters only through C_F: C_ℤ[√2] = log(8π²/log²ε) = 4.62 and
    C_ℤ[i] = log 16 = 2.77.
  - So at matched N and β, ℤ[√2] should sit above ℤ[i] in the rigidity regime by roughly
    (C_ℤ[√2] − C_ℤ[i])/log N ≈ 1.85/log N (≈ 0.09 at X = 10¹⁰).
  - The difference should vanish in the saturation regime.

## 4. Why a direct test against min(1, 2β) is not proposed
- **The finite-X correction is not small.** On ℤ[i], descriptively and unsealed (Step 1, G3), the same statistic at
  x = 10⁸ is 0.24 at β = 0.3 (prediction 0.60), 0.61 at β = 0.5 (1.0) and 0.92 at β = 0.8 (1.0). At x = 10⁷ it is
  lower still.
- **Scaled to X = 10¹⁰–10¹¹** by 1/log X, the deviation near β = ½ is still tens of percent.
- **So the direct test would fail on the known finite-X effect,** not on anything about ℤ[√2]. A tolerance wide
  enough to pass it would make it uninformative.

## 5. Reading options (Will's choice; one to be sealed)
- **(A) Exploratory gallery, no verdict.** R(β, X) for ℤ[√2] at both X, beside min(1, 2β), reported descriptively.
- **(B) A matched-field comparison** (proposed as the sharpest available test).
  - **What runs:** the same statistic on ℤ[i], at an X chosen so that N_ℤ[i] = N_ℤ[√2] (to 0.1%), on the same β grid.
    The ℤ[i] archive needs the same generation and hashing (≈ 30 spot core-h; not yet run).
  - **Arm B1, the leading-order universality claim:** |R_ℤ[√2] − R_ℤ[i]| ≤ 0.05 for every β ≥ 0.6, at both X.
  - **Arm B2, the conductor-constant sign:** R_ℤ[√2] − R_ℤ[i] > 0 at every β ≤ 0.45, at both X. It also reports the
    size against 1.85/log N, descriptively; the size is not gated.
  - **Arm B3, §9.E stability:** each field's R must move by less than its distance to the other field's R between
    X = 10¹⁰ and 10¹¹, at the β where B1 and B2 are read. Otherwise that β is UNRESOLVED.
  - **Power:**
    - A planted witness: uniform i.i.d. angles at matched N, which must fail B2's sign pattern (R = 1 − 1/K,
      β-independent).
    - A shuffled-pairs control: ℤ[√2] with each θ replaced by an independent uniform draw, which must fail B1.
- **(C) Derive the lower-order terms first** (Chen et al.'s ratios route adapted to ℤ[√2]), then seal a direct test.
  Not costed; a derivation project.

## 6. To be filled when Step 2 finishes
The archive manifest hash, the row counts at X = 10¹⁰ and 10¹¹, and the pinned environment (python, numpy and the
`rq1_angles.py` sha256).

# FN1-h2 seal: conductor or L-value, using the class-number-2 fields. DRAFT 2 for Will's review, NOT SEALED

**Briefs:** Will, 2026-11-03 ×4 (L17 prerequisites; "seal draft may begin"; thinned controls withdrawn; D1–D5 rulings),
filed verbatim in `ph2/PH2_DECISIONS_2026-10-07.md`. Prerequisites: `lead/FN1_L17_PREREQS.md` (accepted). Derivation:
`lead/FN1H2_R_DERIVATION.md` (D1 accepted). Draft 1: aa4afbf2.

**Status: draft 2.** Will's rulings D1–D5 are applied (§11). Under D2, the pre-seal compute has been run: (a) the
parametric simulations, (b) the h = 1 references, committed and hashed, and (c) the generator selftest and the §9.F dry
run. **No h = 2 statistic has been computed.** The h = 2 archives are being generated under the stage-2 archive rule
(generation, integrity, counts and hashes only), started per Will's overnight instruction. **§12 lists what changed
from draft 1 and what needs Will's review.**

## 1. Question

At h = 1, C_F = log(|D|(w/2)²) and P_L = log(1/L(1,χ_D)²) + 2 log π are identical, so FN1 stages 1–2 could not tell
the conductor from the L-value. At h = 2, P_L = C_F − log 4 (`lead/FN1_L17_PREREQS.md` (b); asserted numerically for
all 18 fields in `lead/FN1H2_CONTROLS.json`). Pooling h = 1 and h = 2 separates them:
- **conductor:** at matched X and K, the h = 2 fields sit on the h = 1 curve;
- **L-value:** they sit −log 4 = −1.386 along C from it.

## 2. Theory (full text: `lead/FN1H2_R_DERIVATION.md`)

- **(★)** E[R] ≈ ⟨min(1, (C_F + 2 log|k|) / log X)⟩, averaged over k ≠ 0 with the window weights
  w_K(k) = K sin²(πk/K)/(πk)².
- **The finite-size term runs in X**, the prime-norm cutoff of the explicit formula. N cancels.
- **The principal projection** (1 + ψ)/2, with ψ the genus character (unramified over K), leaves E[R] unchanged at this
  order. So at matched X and K the h = 2 principal-prime set has the h = 1 expectation at its own C_F.
- **Two heuristics carry this (D1, as ruled):**
  1. Rudnick–Waxman's RMT form for the prime-sum mean square, E|S_k|² ≈ N·min(1, log q_k / log X), as at h = 1.
  2. Rudnick–Sarnak independence of the zeros of the two distinct primitive L-functions L(s, ξ̃_k) and L(s, ξ̃_kψ),
     for the cross term's off-diagonal part. The cross term's diagonal is controlled by the prime ideal theorem for ψ.
  - Neither is proved.
- **Predictions committed before any compute** (ec4f3ac8, `lead/FN1H2_PRED.json`, sha256 7cf50f19…0cda): (★) per field
  at X* and K_P, under "runs in X" and under "runs in N".
  - Under "runs in N", X_N = li⁻¹(N), so a half-size set sits at X_N = li⁻¹(li(X*)/2) = 9.68·10⁹.
  - Evaluated exactly rather than linearised, the primary mean displacement under "runs in N" at β 0.55 is **+0.66
    (conductor) and −0.73 (L-value)**, against the derivation's linearised +0.55 and −0.84.
- **Thinning.** Will withdrew the thinned-control requirement (random thinning gives pR + (1 − p); character thinning
  adds a twisted conductor). Only the χ′ control remains (D5, descriptive, §6).

## 3. Data

**h = 2 sets (new).** All 18 fields (`lead/FN1_L17_PREREQS.md` (a)): every principal split prime p ≤ X* = 2·10¹⁰ (D4),
one row per p, with θ and 1 − θ mirrored.
- **Generator** `fn1h2_archive.py` (076c2f5e):
  - split by the Kronecker symbol mod |D|;
  - principal by the genus character of the smallest odd prime factor of |D|;
  - Cornacchia on the principal form (x² + |D|y² = 4p for D ≡ 1 mod 4; x² + (|D|/4)y² = p for D ≡ 0 mod 4).
- **Selftest** (D2 (c); `results/h2/GENERATOR_SELFTEST.txt`; CHECKRUN EXIT=0), all passing:
  - for p < 2·10⁵, brute-force representability equals split ∧ genus, for all 18 fields;
  - Cornacchia equals the unique brute-force solution;
  - the split rule equals Euler's criterion for p < 10⁶;
  - principal density 0.247–0.251;
  - FN1's h = 1 rows are reproduced exactly for −7, −11 and −19;
  - six hand cases.
  - **Red path:** with the genus test removed, the selftest raises on −15's prime above 2.
- **Archive rule:** generation, integrity, counts and hashes only, with no statistic of the angles. Manifests carry
  per-segment sha256, row counts, split counts and an integrity flag (each norm equals the segment's principal split
  primes).
- **Pins:** the 18 manifest sha256s go into `fn1h2_pins.json` before the seal, with the code hashes.

**h = 1 references (seen data).** The nine class-number-1 fields, every split prime p ≤ X*:
- the w = 2 fields from the stage-2 archives (`fn1_pins2.json`, as sealed for stage 2);
- ℤ[i] and ℤ[ω] from the RQ1-c 10¹² archives.

Their R at X* and K_P was computed before the seal as D2 (b), committed and hashed (§5). The read recomputes them and
must reproduce that file bit for bit.

**K_P (changed from draft 1).** The fixed K = 57,801 / 7,873 / 2,906 at β 0.55 / 0.45 / 0.40, i.e. stage 1's K, for
every set, with each set normalised by its own N/K.
- Draft 1 had K_P = round(N_P^0.55) from the h = 2 count. That would make K depend on h = 2 data, or on a π(X*) value
  I would have had to source.
- N_P ≈ π(X*)/2 ≈ 4.4·10⁸ is within 3% of stage 1's N (4.55·10⁸), so stage 1's K is the matched choice, and it is
  already committed.

**β:** 0.55 primary. β 0.45 and 0.40 are descriptive, at no extra load.

**Primary set (Will):** the nine h = 2 fields with 28 ≤ |D| ≤ 163: −35, −40, −51, −52, −88, −91, −115, −123, −148.
- Their C ∈ [3.56, 5.00] and P_L ∈ [2.17, 3.61] both lie inside the h = 1 range [1.95, 5.09].
- The other nine (−15, −20, −24, −187, −232, −235, −267, −403, −427) are descriptive.

## 4. Primary test: the displacement s along C (β 0.55)

- **Reference line:** OLS of the nine h = 1 references' R on C_F, R = a + b·C.
- **Statistic:** s = mean over the nine primary fields of (R_h2,j − a − b·C_j), divided by b.
  - Conductor predicts s = 0.
  - L-value predicts s = −log 4 = −1.386.
- **Three-way rule, cuts at 0.4 and 0.6 of log 4:**
  - **CONDUCTOR** iff s > −0.5545;
  - **L-VALUE** iff s < −0.8318;
  - else **INCONCLUSIVE**;
  - **VOID (reference slope ≤ 0)** if b ≤ 0.
  - Both informative outcomes are two-way claims (§9.J).
- **Code:** `fn1h2_read.py` (read mode, locked to X*).

## 5. D23, §9.J, power: pre-seal results (D2)

**(b) The h = 1 references** (pueue 1418; wall 34 min, about 0.45 core-h): `results/h2/FN1H2_REFS.json`, sha256
f2d390cf…d4bd, committed c0ee6cb5 before the seal. No h = 2 data touched. The read must reproduce it bit for bit.

| Field | C_F | n (split p ≤ X*) | R, β 0.55 | R, β 0.45 | R, β 0.40 |
|---|---|---|---|---|---|
| −7 | 1.946 | 441,101,150 | 0.76512 | 0.58578 | 0.49650 |
| −8 | 2.079 | 441,102,027 | 0.75881 | 0.60520 | 0.52311 |
| −11 | 2.398 | 441,098,741 | 0.76807 | 0.60848 | 0.52165 |
| ℤ[i] | 2.773 | 441,101,890 | 0.78025 | 0.61728 | 0.52864 |
| −19 | 2.944 | 441,106,912 | 0.75954 | 0.61025 | 0.53850 |
| ℤ[ω] | 3.296 | 441,098,662 | 0.78646 | 0.61381 | 0.51367 |
| −43 | 3.761 | 441,094,321 | 0.80565 | 0.63431 | 0.55192 |
| −67 | 4.205 | 441,095,731 | 0.84394 | 0.60805 | 0.52429 |
| −163 | 5.094 | 441,100,823 | 0.96012 | 0.64059 | 0.54982 |

**What the references show (seen data, pre-seal; descriptive).** At β 0.55 they are clearly convex in C:
- the OLS quadratic has c₂ = 0.0272, with residual SD 0.0090;
- about the line, the leave-one-out residuals have SD 0.046, dominated by −163 (+0.106).
- So at X* most of the h = 1 "offset" scatter about a line is curvature. That bears on L16's two candidates (curvature
  or a second variable), on h = 1 data only.

**§9.D witness on those references (leave-one-out; D1 as accepted).** Each h = 1 field stands in for an h = 2 field,
against the line fitted on the other eight.

- **Unplanted:** s = +0.27, which reads **CONDUCTOR**.
- **Planted** (the predicted −log 4 shift injected on each stand-in): s = −1.12, which reads **L-VALUE**.
- The gate returns the right branch both ways.
- **Its power** is not this single realisation but the "curved truth" and "measured scatter" rows of (a) below.
- The stand-ins span h = 1's C range (1.95–5.09), not the primary h = 2 range (3.56–5.00).

**(a) Parametric simulations** (`lead/fn1h2_sim.py`, dd033d5d; inputs pinned; 200,000 draws per scenario;
`results/h2/FN1H2_SIM.json`, d5cf401b). The model:
- h = 1: R = b·C + μ + e, b = 0.0455;
- h = 2: R = b·(C + s_true) + μ + e;
- μ field scatter; e read noise at the SE model (1×).

| Scenario | s_true | median ŝ | SD(ŝ) (robust) | P(CONDUCTOR) | P(L-VALUE) | P(INCONCLUSIVE) | P(VOID) |
|---|---|---|---|---|---|---|---|
| **Nominal, σ_μ 0.0213 (L16): conductor** | 0 | 0.00 | 0.30 | **0.988** | 0.000 | 0.012 | 0 |
| **Nominal: L-value** | −1.386 | −1.39 | 0.23 | 0.000 | **0.991** | 0.008 | 0 |
| Nominal: midpoint | −0.693 | −0.69 | 0.24 | 0.288 | 0.277 | 0.435 | 0 |
| Stress σ_μ × 1.5: conductor | 0 | 0.00 | 0.44 | 0.937 | 0.008 | 0.055 | 0 |
| Stress σ_μ × 1.5: L-value | −1.386 | −1.39 | 0.35 | 0.011 | 0.947 | 0.042 | 0 |
| Line's LOO scatter (0.046) as field noise: conductor | 0 | 0.00 | 0.65 | 0.852 | 0.046 | 0.099 | 0.002 |
| Line's LOO scatter as field noise: L-value | −1.386 | −1.39 | 0.51 | 0.055 | 0.868 | 0.076 | 0.002 |
| −7 excluded from the reference: conductor | 0 | 0.00 | 0.30 | 0.987 | 0.000 | 0.013 | 0 |
| −7 excluded: L-value | −1.386 | −1.39 | 0.25 | 0.000 | 0.990 | 0.010 | 0 |
| Curved truth (the references' quadratic, residual SD 0.009): conductor | 0 | −0.04 | 0.12 | 1.000 | 0 | 0 | 0 |
| Curved truth: L-value | −1.386 | −1.63 | 0.10 | 0 | 1.000 | 0 | 0 |
| Curved truth, σ_μ 0.0213: conductor (added 11-04, 4(a)) | 0 | −0.04 | 0.24 | 0.995 | 0 | 0.005 | 0 |
| Curved truth, σ_μ 0.0213: L-value | −1.386 | −1.63 | 0.20 | 0 | 1.000 | 0 | 0 |
| Curved truth, σ_μ × 1.5: conductor | 0 | −0.04 | 0.35 | 0.961 | 0.002 | 0.038 | 0 |
| Curved truth, σ_μ × 1.5: L-value | −1.386 | −1.63 | 0.29 | 0 | 0.998 | 0.002 | 0 |
| **Runs in N: conductor** | +0.662 | +0.66 | 0.38 | 1.000 | 0 | 0 | 0 |
| **Runs in N: L-value** | −0.731 | −0.73 | 0.24 | **0.238** | 0.335 | 0.427 | 0 |
| Zero slope (VOID reachability) | 0 | — | — | 0.187 | 0.284 | 0.029 | 0.500 |

**Will's 4(a): which σ the cuts rest on, and what the 0.85–0.87 case means.**
- **The cuts do not rest on a σ.** They sit at fixed fractions of the hypothesis gap, −0.4 and −0.6 of log 4. Only
  their D23 depends on the noise.
- **The declared nominal noise** is σ_μ = 0.0213: L16's field-specific scatter, measured about a straight line on C at
  stage-1/2 N. On top of it is read noise at the SE model (1×; L16 measured 0.69×). That gives SD(ŝ) ≈ 0.30 / 0.23 and
  D23 0.988 / 0.991 under a straight-line truth.
- **What the references showed after that choice:** at X* and K_P they are curved (c₂ 0.027). About the line, their
  leave-one-out residual SD is 0.046; about the quadratic it is 0.009.
- **The 0.85–0.87 case** puts that 0.046 in as independent random field scatter on every h = 1 and h = 2 field, with a
  straight-line truth.
  - So it treats the references' curvature as noise. It is what D23 would be if the h = 2 fields carried their own
    unexplained offsets as large as h = 1's line residuals, unrelated to C.
  - The references do not show that: their line residuals are a smooth function of C (−163 +0.106, the middle fields
    negative), which the quadratic absorbs to 0.009.
- **The scenario that matches the references** is the curved truth: the line-based rule with the line's misfit
  entering as a bias (−0.04 conductor, −0.24 L-value), plus random field scatter.
  - At the quadratic's own residual SD (0.009): 1.000 / 1.000.
  - At L16's σ_μ (0.0213): 0.995 / 1.000.
  - At 1.5 σ_μ: 0.961 / 0.998.
- **So in plain terms:** the cuts meet D23 under both readings of nominal, the declared straight-line one and the curved
  one the references show. The 0.85–0.87 case is the pessimistic bound in which the curvature is not real structure.
  It stays disclosed (D2b).

**K0 (t form, §7):** null false PASS 0.0498 (target 0.05). Planted PASS **0.32** at the references' quadratic and
residual SD, and **0.14** with residual SD σ_μ. The two rejected Spearman forms: draft (about the h = 1 line) null
0.065, planted 0.997; detrended null 0.061, planted 0.34.

**D23 is judged at nominal (D2b).** A stress result below 0.95 is disclosed here, and the cuts are not widened.

- **D23 at nominal: 0.988 (CONDUCTOR | conductor) and 0.991 (L-VALUE | L-value).** Both meet 0.95.
- **Disclosed below 0.95:**
  - the σ_μ × 1.5 stress: 0.937 and 0.947;
  - the line's leave-one-out scatter taken as random field noise: 0.852 and 0.868.
  - That second scenario counts the references' curvature as noise. Under the curved truth the references actually
    show, the rule reads correctly at 1.000 and 1.000, with the line's misfit giving biases of −0.04 (conductor) and
    −0.24 (L-value).
- **§9.J:** CONDUCTOR, L-VALUE, INCONCLUSIVE and VOID are all reached.
- **"Runs in N":** a true L-value effect reads L-VALUE 0.34, INCONCLUSIVE 0.43 and **CONDUCTOR 0.24**. Both informative
  verdicts rest on "runs in X" (§9).

**(c) The §9.F dry run** (`run_fn1h2_dry.sh`, ab7a757f; pueue 1616–1623; records in `results/h2/dry/`). The whole read
pipeline ran at X = 2·10⁹, with synthetic h = 2 fixtures and the real h = 1 archives cut there.
- **Double read:** two separate processes, both exit 0; outputs byte-identical (sha256 058d6c5e…2956, `cmp` rc 0).
- **References:** each read recomputed its references and matched its pinned refs file bit for bit.
- **Red paths:**
  - with the −7 manifest pin zeroed: `AssertionError ('manifest pin', …archive_1e11_D7)`, rc 1, no output;
  - with the refs pin zeroed: `AssertionError ('refs pin', …)`, rc 1, no output.
- **Cost:** 347 CPU-seconds per read; about 0.2 core-h for the chain including fixtures and red paths.
- The fixture s (9,287) is meaningless by construction (random rows) and is not a result.
- **Will's 4(b): what data the dry run read** (pins file `results/h2/dry/fn1h2_pins_dry.json`, committed):
  - **h = 2: only the synthetic fixtures** in `/mnt/data/fn1h2_dry` (18 directories): seeded random int32 rows, no
    primes. The read takes h = 2 directories only from the pins file's block (`fn1h2_read.py`, the `h2pins` line);
    the dry block lists only those fixtures. **No real h = 2 archive was opened**, and the real archives are not in
    that pins file.
  - **h = 1: the real archives, at X = 2·10⁹ only.**
    - The w = 2 fields from the stage-2 archives (`/mnt/data/fn1/archive_1e11_D*`, manifests pinned as in
      `fn1_pins2.json`).
    - ℤ[i] and ℤ[ω] from the RQ1-c 10¹² archives, with segments k < 20.
    - Every row lies inside stage 1's already-read range (p ≤ 2·10⁹ < 10¹⁰).
    - That covers the references, the χ′ control and the matched-N reference.
  - **Inputs by file:** its own refs file at 2·10⁹ (`DRY_REFS.json`, from the same h = 1 rows), the committed (★)
    predictions and the committed controls.
- **Selftest:** §3 (CHECKRUN EXIT=0).

## 6. Reported, descriptive (no verdict)

- **The χ′ control (D5; D′ = 5).** Each h = 1 reference restricted to (5/p) = +1. ΔR = R_thin − R_ref per field and
  β, beside (★)'s committed values under "runs in X" (β 0.55: +0.013 to +0.046) and "runs in N" (+0.018 to +0.062).
  - It tests the twist-conductor mechanism and, through the level, X against N.
  - The field-specific offsets of L16 cancel to first order in ΔR. The absolute level of (★) misfits our statistic
    (RQ1-b), so ΔR is what is compared.
- **The matched-N reference:** each h = 1 field's first n̄ rows, with n̄ the mean primary h = 2 count, and s against it
  (predicted ≈ −0.55 under conductor/X).
- **Other β:** s at β 0.45 and 0.40.
- **Per field:** s_j for all 18 fields; the mean over all 18 and over the descriptive nine (outside the h = 1 C range,
  so extrapolation, flagged); **K2:** −15's s_j.
- **Within-field drift** of each h = 2 set (eight prime-order segments).
- **Spearman ρ** of R_h2 on C over the 18 (seeded permutation p).
- **Controls (Will):** Pearson r of s_j with L′/L(1, χ_D) and with Chen's L-term −2·L′/L(2, χ_D). Constants committed
  before the seal (e4e7bf3e, `lead/FN1H2_CONTROLS.json`, sha256 77afddaa…c4b9; the h = 1 values reproduce
  FN1_LPRIME.json exactly). Exact 9! permutation p over the primary nine.

## 7. Out-of-sample arm K0 (one-way; Will D3: K1 dropped, K0 alone, no multiplicity correction)

Will's L16, as amended: the h = 1 offsets are systematic and field-specific, either curvature in C_F (K0) or a second
variable. K0 is the C-only null.
- **Frozen form:** q(C) = a₂ + b₂C + c₂C², OLS over the nine h = 1 references.
- **What is out of sample.** Inside the nine primary h = 2 fields, once their own level and slope are removed, the
  prediction's pattern is c₂·(C² minus its line on C), whatever s is. So K0's testable content there is the sign of c₂.
- **Statistic (amended, §12):** an OLS quadratic over the nine primary (C_j, R_h2,j), and
  t = sign(c₂)·ĉ₂,h2 / SE(ĉ₂,h2), with 6 df.
  - **PASS iff t > 1.9432** (one-sided 5%). A PASS is informative: the h = 2 curvature follows h = 1's, out of sample.
  - Otherwise "FAIL (one-way arm: FAIL not informative)".
  - c₂ = 0 exactly gives VOID.
- **Null and power:** from (a), §5.

## 8. Cost

| Item | Model | Measured |
|---|---|---|
| h = 2 archives, 3,600 segments of 10⁸ | 61.2 core-h (51 s × 1.2 contention per segment) | §9.H first wave: 51.3 s per segment (0.84×); bulk projected 51.4 core-h. Stopped at the mid check (01:34 PST 11-04) after 1,809 of 3,600 segments; relaunched at 24 tasks (Will, 11-04), see below the table. |
| D2 (b) references | 0.5 core-h | about 0.45 core-h (wall 34 min) |
| D2 (a) simulations, controls, predictions | < 0.3 core-h | local, minutes |
| D2 (c) selftest; dry run at 2·10⁹ | ≈ 0.4 core-h | about 0.2 core-h |
| Sealed double read (references, 18 h = 2 sets, χ′ control, matched N; ×2) | ≈ 3 core-h | — |

**Archive midpoint stop (Will, 2026-11-04, verbatim):** "Midpoint stop at 1.33× the first-wave rate. Cause: CPU
inflation from VM contention, uniform across fields. Check rebased to the approved price, which already prices
contention. Against it the build was at 0.92×. This is a process fix with no effect on any statistic."
- **Rebased rule** (`fn1h2_costs.py price`): cumulative CPU over all completed segments ≤ 1.25 × 61.2 s × their
  count; the cap for 3,600 segments is about 76.5 core-h. Checked at three quarters and at the end.
- **Resume safety, checked before relaunch:**
  - no generator process;
  - no partial or temp files;
  - all 1,809 segment files load whole (size = header + rows × 8) and equal the done list;
  - the second half generates only missing segments.
- **Counts:** the final step writes the 18 manifests and a count report (`fn1h2_counts.py`), with −148 explicit:
  - rows against li(X*)/4 and against the field's split count;
  - per-segment rows against the cross-field median;
  - an independent Euler-criterion recount at segments 0, 100 and 199 for −148 (and −52 for comparison).

## 9. Attribution, fixed before the read (D1 as ruled)

- **CONDUCTOR:** at matched X and K, the h = 2 principal-prime sets sit on the h = 1 curve. R follows the analytic
  conductor |D|(w/2)², not L(1, χ_D), which differs from it by log 4 at these fields. This holds within the order kept
  (Rudnick–Waxman's leading form plus the conductor constant).
- **L-VALUE:** a displacement of about −log 4. The class number enters R, through L(1, χ_D) or something equivalent.
- **INCONCLUSIVE:** no conclusion.
- **Both informative verdicts rest on "runs in X"** (§2), which rests on two heuristics: Rudnick–Waxman's RMT form, and
  Rudnick–Sarnak independence for the cross term.
  - If the term ran in N instead, a true conductor effect would sit at s ≈ +0.66 and still read CONDUCTOR.
  - A true L-value effect would sit at s ≈ −0.73, inside the INCONCLUSIVE band, and would read CONDUCTOR 24% of the
    time (§5).
  - The χ′ control (§6) is the read's own descriptive check of X against N.
- **K0 PASS:** h = 1's curvature in C predicts the sign of the h = 2 curvature out of sample. It does not exclude a
  second variable in addition. A K0 FAIL carries no conclusion.
- **K2, the descriptive nine, the χ′ control, matched N and the controls** carry no conclusion.

## 10. Seal procedure (as stages 1–2)

1. Archives complete, all 18 manifests integrity-true, counts recorded. `fn1h2_pins.json` written:
   - the archive manifests;
   - `fn1_pins2.json`'s h = 1 manifests;
   - the D2 (b) references, (★) predictions and controls files, by sha256;
   - the sha256 of `fn1h2_read.py`, `fn1h2_archive.py`, `fn1_read2.py`, `fn1_archive.py`, `rq1_read.py` and
     `rq1_zw.py`.
2. This document is finalised and tagged `fn1h2-seal`.
3. OpenTimestamps stamp manifest, then Bitcoin attestation verified on two explorers. **No read before attestation.**
4. Double read: two separate processes. The output JSON has sorted keys and no timings (timings go to a sidecar).
   `cmp` must be byte-identical.
5. **VOID conditions:**
   - any pin mismatch;
   - the references differing from the committed D2 (b) file;
   - `cmp` not identical;
   - the reference slope ≤ 0 (primary).

## 11. Will's rulings (2026-11-03), as applied

- **D1 accepted.** The matched-X, matched-K unthinned h = 1 reference is primary. The attribution names both
  heuristics and states that both informative verdicts rest on "runs in X" (§9).
- **D2: go on (a), (b), (c).**
  - (b) is committed and hashed before the seal, with no h = 2 data touched.
  - D2b: D23 is judged at nominal; a stress result below 0.95 is disclosed and the cuts are not widened (§5).
- **D3:** K1 dropped; K0 alone; no multiplicity correction (§7).
- **D4:** X* = 2·10¹⁰.
- **D5:** χ′ with D′ = 5, descriptive. (★)'s predictions for each h = 1 field under "runs in X" and "runs in N" were
  committed before computing (ec4f3ac8).

## 12. Changes from draft 1, and what needs Will's review

**Changed from draft 1 (aa4afbf2):**
1. **Thinned controls removed** (Will's withdrawal). Control (i) and its witness role are gone. The §9.D witness is the
   leave-one-out stand-in on the h = 1 references (D1 as accepted).
2. **K1 dropped; K0 alone, α 0.05, no multiplicity correction** (D3).
3. **K_P fixed at stage 1's K** (57,801 / 7,873 / 2,906), not round(N_P^0.55) from the h = 2 count (§3).
4. **h = 2 sets use every principal p ≤ X*,** not a cut to the minimum count. That is matched X, as D1 requires.
5. **K0's statistic was replaced** after pre-seal simulation (a) showed that draft 1's form did not hold its size:
   - draft 1's Spearman of predicted against observed offsets about the h = 1 line had null false PASS 0.065, because
     the h = 1 slope error enters the observed offsets linearly in C;
   - detrending both within the nine left 0.061, because the residuals are not exchangeable;
   - the replacement is a one-sided t on the within-h = 2 quadratic coefficient, with the sign of h = 1's: null 0.0498,
     exact under Gaussian scatter.
6. **VOID on a reference slope ≤ 0** added as an explicit branch (reachable, §5).
7. **Controls constants committed** (L′/L(1), Chen's −2·L′/L(2)), and the χ′ predictions committed (D5).
8. **"Runs in N" re-evaluated exactly:** under it, a true L-value effect reads CONDUCTOR 0.24, not the derivation's
   linearised 0.16.

**For Will's review:**
- **K0's power.** The exact t form fires on a planted h = 1-like curvature only 0.32 of the time (0.14 at σ_μ), because
  the primary C range (3.56–5.00) is narrow for a curvature test. A K0 FAIL is declared uninformative, but with this
  power the arm can rarely say anything.
  - **Options:**
    1. keep it as is;
    2. use draft 1's Spearman form with its cut calibrated by simulation (power 0.997 at the uncalibrated cut; the
       calibrated cut is not yet computed). Its size would then rest on the simulated noise model, not on an exact
       null;
    3. drop K0 and keep the curvature reading descriptive.
  - My recommendation is 3: the arm cannot reach §9.J's reachability with useful power.
- **The references' curvature.** The h = 1 references at X* are convex in C (c₂ 0.027, residual SD 0.009, against a
  line LOO scatter of 0.046).
  - The primary still uses the line, as draft 1 declared, to keep it free of K0's form. Under the references' own
    quadratic as truth, the line-based rule classifies correctly at 1.000 both ways, with an L-value bias of −0.24.
  - A quadratic reference would remove that bias but import K0's form into the primary. I recommend keeping the line.
- **D23 below 0.95 under two disclosed scenarios** (stress 0.94; line scatter as noise 0.85–0.87). Per D2b these are
  disclosed and the cuts are unchanged.
- **The archive stop (§8):** resolved by Will (relaunch at 24 tasks, check rebased to the approved price).
- **The h = 2 archives** were started overnight under the stage-2 archive rule (Will's overnight instruction). They are
  pinned only at the seal.

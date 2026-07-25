# ARS Look Arc — §0b Provenance Table

**§0 binding:** nothing here estimates Λ; nothing bears on RH. Riemann-adjacent objects are calibrator
substrates for the ARS point-process classifier.

Every number inherited from the continuation brief / session spec, resolved against the repo at `06caf2f`.
Two independent passes were run per row: **fact-check** (does the value exist?) and **slot-check** (does the
claimed criterion/row/statistic/L-scale/γ-block own it?). §0d says slot error is this program's dominant
failure mode; three rows below are fact-RESOLVED / slot-WRONG.

## A. Resolved clean

| # | Inherited value | Claimed source | Repo location | Status |
|---|---|---|---|---|
| 1 | σ-column block-1 = 2.04 (t=0), 2.23 (t=0.22) | Phase 2 residual | `phase2_residual_measured.json` → 2.0414, 2.2281 | **RESOLVED** |
| 2 | σ-column block-2 = 1.26 (t=0), 2.29 (t=0.22) | Phase 2 fresh block | `phase2_thetacert_freshblock.json` → 1.2604, 2.2860 | **RESOLVED** |
| 3 | A₁ ≈ 1.09, A₂ ≈ 1.82 | brief arithmetic | 2.2281/2.0414 = 1.0914; 2.2860/1.2604 = 1.8137 | **RESOLVED** |
| 4 | block-2 at γ ≈ 33920 | Phase 2 fresh block | `gamma_mid = 33923.0999` (`zeros1[40000:42000]`) | **RESOLVED** |
| 5 | "+0.30 forward rise" over [0, 0.22] | Phase 2 | `rise_over_bracket_0_0.22 = 0.29643` | **RESOLVED** |
| 6 | "resolution 0.0016 in dBN t" | Phase 2 | `CLASSIFIER_t_RESOLUTION_dBN = 0.0016229` | **RESOLVED** (but see #12) |
| 7 | CP1 "7–8σ" GOE exclusion | Session K | `maass_analysis_measured.json` z_vs GOE = −8.45 (even), −6.98 (odd) | **RESOLVED** |
| 8 | Phase 4 "+2.27σ above Poisson" | Phase 4, parity=1 | `phase4_maass_endpoint_measured.json` sector "1" `z_vs_poisson = 2.27385` | **RESOLVED** |
| 9 | fungal `#4259167` (brief flags as possible paste artifact) | — | **Real git commit** `4259167` (fungal I_rep false-positive on pooled+floored); cited in `fungal_surrogate_port.py:3` | **RESOLVED** — value genuine, slot wrong (commit hash, not an issue id). *Filed as a one-line row and nothing more:* that the brief's fabrication warning was itself mis-slotted is a coincidence, not a lesson, and is deliberately not written up as one. |

## B. Fact-resolved, slot WRONG — do not reuse as stated

| # | Inherited statement | What the repo actually says | Status |
|---|---|---|---|
| 10 | "block-1 at γ ≈ 2500" | `phase2_dbn_flow_measured.json` window `gamma_mid = 2516.571`. Close enough to use, but note this is a **different block** from Phase 1's density-check low-γ block (γ = 1420.417, `zeros6[:2000]`) and from Phase 3's low-γ block (also γ = 1420.417). Three distinct "low-γ" blocks are in play across P1/P2/P3. | **RESOLVED-WITH-AMBIGUITY** — "low γ" is not one slot |
| 11 | "Phase 3's sign flip: −4.5σ anti-rigid at order-3 vs −17σ rigid at poly9" | **Both quoted numbers are poly9.** `phase3b_curvature_measured.json` poly9 `dev_over_sd` = [−4.49, −5.95, −10.86, **−17.50**, −14.92, −9.98] at L=[1,2,4,8,16,32]. So −4.5σ is poly9@L=1 and −17.5σ is poly9@L=8 — the *same* estimator at two L. Also **sign convention inverted in the brief**: negative = Σ² *below* GUE = **more rigid**, so −4.5σ is not "anti-rigid". The actual order-3-vs-poly9 sign flip is at **large L**: order-3 gives `dev_over_sd` = [−4.80, −5.22, −4.75, −0.21, **+15.27, +45.76**] at L=[1…32] (`phase3_sigma2_measured.json`, block `low_gamma`) — i.e. order-3 says wildly *anti*-rigid at L=16/32 where poly9 says rigid (−14.9σ / −9.98σ). | **MISFILED** — corrected value: the flip is +45.8σ → −9.98σ at L=32 |
| 12 | jitter floor "sd(W) ~ 0.2/√W (verify against repo)" | Verified — **and it does not hold.** Phase 1 measured null sd: W=2000 → 0.005442, W=5000 → 0.003800, W=10000 → 0.003030. Implied constant c = sd·√W = **0.243, 0.269, 0.303** — c is not constant, it *grows*. **What is earned: the exponent is not −1/2.** What is NOT earned: any particular exponent — the log-log fit gives −0.365 from **three points**, each an sd estimated from n_real = 80/60/40 draws (8–11% relative error), so a three-digit exponent is unsupported precision and is quoted below only to propagate the correction, never as a measured constant. | **UNRESOLVED AS STATED** — see below |

### Downstream of #12 — this is a different scaling law, not a constant offset

Three consequences, the first two of which the first draft of this table missed:

1. **The error is W-dependent** (22% / 34% / 51% at W = 2000 / 5000 / 10000), so any two results
   compared across *different* W were compared against a wrongly-**shaped** floor, not a uniformly
   shifted one. Cross-W comparisons that used the rule are not rescued by a single scale factor.
2. **The direction is backwards from expectation.** √W is what independent sampling gives; a
   *repulsive* spectrum should suppress variance **faster** than that, not slower. Slower-than-√W
   decay points at residual correlation in the ⟨r̃⟩ sequence itself — which would be a fact about the
   statistic, not about the null, and is worth knowing independently of this program. Untested.
3. The filed magnitudes move. Every "×floor" and "resolution" number built on `0.2/√W` is inflated:

| Quantity | As filed (0.2/√W floor) | With measured floor (0.005442 at W=2000) |
|---|---|---|
| Phase 2 forward rise over [0,0.22] | 66× floor | **54× floor** |
| Phase 2 dev/floor at t=0.22 | 69.5× | **57×** |
| Phase 2 classifier t-resolution | 0.00162 in t | **0.00197 in t** |
| Phase 2 t=0 ⟨r̃⟩ dev/floor | 3.2× | **2.6×** |

**Enumerated, not asserted** (`taskB_kernel_check.py` K2). Every filed number that consumes the rule:

| # | item | filed | corrected | binary it feeds | flips? |
|---|---|---|---|---|---|
| a | P2 forward rise in floor units | 66.3× | 54.5× | "the flow rigidifies resolvably" (needs >1×) | **no** — 54.5× above 1 |
| b | P2 t=0 ⟨r̃⟩ dev in floor units | 3.2× | 2.6× | "the t=0 offset is resolvable" (needs >1×) | **no** — 2.6× above 1 |
| c | P2 classifier t-resolution | 0.00162 | **0.00197** | none — it *is* the deliverable | **n/a**, the deliverable moves +22% |
| d | P1 "W needed to resolve 1e-3" | 59 220 zeros | **≈202 000 zeros** | "a 1e-3 effect is reachable at accessible W" | **no**, but a **3.4× feasibility cost** |

The rule appears **nowhere** in Phase 1's `by_W` table (which uses measured per-W sd), nowhere in
Phase 3 (empirical GUE band), nowhere in Phase 4 (hand-built bands). So: three items feed a binary and
none flips; two items *are* magnitudes and both move. The earlier line "no verdict flips" was an
unenumerated global claim of exactly the shape this gate exists to catch, and is replaced by this table.

## C. Unresolved — construction not reproducible from the repo

| # | Item | Problem |
|---|---|---|
| 13 | `phase2_residual_measured.json` and `phase2_thetacert_freshblock.json` | **PHASE 2'S GRADE DROPS, not just Task A's status.** The σ-shape result — filed as the strongest single result in the arc — sits in the category **RECORDED, NOT REPRODUCIBLE**: it cannot be regenerated, re-run at a different W, or slot-verified. That is a worse epistemic category than "resolved, not robust" and it must be visible in any arc summary, not buried as a blocker on a downstream task. **No generating script exists in the repo.** `grep -rl "control_flow_rows\|thetacert_freshblock" --include=*.py` returns nothing. Both were produced inline and only the JSON was committed. The matched-density GUE-flow control's construction is described in `PHASE2_FINDINGS.md` prose but cannot be re-run or slot-verified. |
| 14 | Interior window size of block-2 | Block-1 is 4000 zeros → `interior(frac=0.5)` → **W_int = 2000** (`phase2_dbn_flow.py`, and the file's own comment "W_interior ~ 1500" is wrong). Block-2 is `zeros1[40000:42000]` = 2000 zeros → interior would be **W_int = 1000**. If so the two blocks are **not construction-matched**, and Task A.3's "match block-1/block-2 construction exactly" cannot be satisfied without first fixing which W block-2 actually used. Unverifiable because of #13. |
| 15 | Parity labelling in CP1 | `sessionK/maass_analysis.py:45` fixes the convention **sym0 = EVEN**, and `names = {0:"even", 1:"odd"}` (line 179) follows it. But the completeness block at lines 96–97 computes `even_count = (sym==1).sum()` = 334 and `odd_count = (sym==0).sum()` = 266 — **inverted relative to the file's own convention**. The *statistics* are unaffected (sectors split on the raw symmetry field and sector "even" correctly carries n=266), so this is a reporting-label bug, not a result bug. But it is exactly the correct-fact/wrong-slot mode, sitting inside the file CP1 rests on. |

## D. Consequences for the three tasks

- **Task A** — its power requirement is stated against `0.2/√W`. That rule is wrong (#12); the separation
  check must use `sd ≈ 0.0868·W^(−0.365)`, which gives a **larger** floor and therefore a **harder** power
  test than specified. Additionally, A.3's "match construction exactly" is currently **not executable**:
  the prior blocks' control construction has no script (#13) and block-2's W is unknown (#14). Task A is
  **blocked on reconstructing the Phase-2 control before any third block is generated**, not on compute.
- **Task B** — unaffected by the above; proceeds.
- **Task C** — CP1's numbers resolve (#7); the label bug (#15) should be fixed but does not block.

## E. Numbers this session must not inherit

`−4.5σ at order-3` (use +45.8σ at L=32, or state the L), `0.2/√W`, `66×`, `0.0016`, and any claim that
block-1 and block-2 are construction-matched.

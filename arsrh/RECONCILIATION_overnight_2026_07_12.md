# Reconciliation — `overnight_2026_07_12` against the 2026-07-26 session

**Why:** R-134 found that the signed-I_rep repair was built on 2026-07-12, used to overturn a claim,
and never propagated into `arithmetic_toolkit.py`. Two independent derivations of the same repair
need reconciling before either is built on further.

**Verdict: the two agree where they overlap, each corrects the other in one place, and the overnight
holds three things this session lacked.**

---

## 1. THE DUPLICATED WORK — and it is the same quantity, verified not assumed

| | overnight (`irep_unclipped`) | this session (`repulsion_integral_signed`) |
|---|---|---|
| definition | ∫₀¹(1−R₂)dr, no `maximum(0,·)` | identical |
| parameters | `r_max=5.0, n_bins=50` | caller's; defaults `10.0, 100` |
| bin width | 0.1 | 0.1 |

**Checked rather than assumed** (this is a five-clause question and it was answered by running it):
fungal signed I_rep = **−2.21198** under *both* parameterisations, to five decimals. **Commensurable.**
Also matches the deployed `joint_q_profile` path, which itself calls `(5.0, 50)`.

## 2. WHERE THEY CORROBORATE — two independent certifications of one estimator

The overnight certified the repair against a **calibrator zoo with a pre-committed HARD STOP**
(VERDICT_B: *"if the clustered class fails its reading, the REPAIR is wrong, not the class"*).
This session certified it against an **analytic Neyman–Scott target**. Different methods, same verdict.

| reference | overnight VERDICT_B | this session |
|---|---|---|
| Poisson | **−0.0094** | **−0.00000** |
| GOE / GUE | +0.3277 / +0.3857 | (not measured) |
| clustered, monotone in CV | −0.13 → −22.1 across 15 configs | −0.51 → −2.98, recovery 0.899 ± 0.033 vs analytic |

**Two independent certifications is stronger than either.** And the overnight's ladder gives what this
session could not: **units**. Fungal's −2.21 sits between their `neyman_scott` strength 2.0 (−1.376)
and 5.0 (−4.951), and beside `cox` 1.5–2.0 (−1.349, −2.900) and `gamma_renewal` 3.0 (−1.789).
**Fungal is moderately-to-strongly clustered on an independently calibrated scale** — a real upgrade,
since this session could only say "outside the null range."

## 3. WHERE THE OVERNIGHT CORRECTS ME — I cited a superseded table

**My compilation quoted VERDICT_A lines 85–87** (allen −5.003, hc3 −2.841, ret1 −4.767). **That table
is pre-fix and the same document supersedes it.**

VERDICT_A POST-RUN #2(a) records a bug the overnight caught in itself: `irep_unclipped` was called on
**raw spike times**, and the integration window r ∈ [0,1] is *in the input's own units* — so it meant a
different number of mean-ISIs per cell. Caught because a threshold-free predictor returned
ρ(log-ISI CV, I_rep) = **+0.68**, physically backwards. *"A sign that cannot be right is worth more
than a magnitude that looks plausible."*

**Current numbers, rate-corrected (VERDICT_A POST-RUN #2b):**

| substrate | n | median signed I_rep | % < 0 |
|---|---|---|---|
| **allen-hpf** | 400 | **−7.99** | **100%** |
| hc3-port | 400 | −1.44 | 98% |
| ret1 | 325 | −0.32 | 77% |

**This strengthens R-134/R-124 rather than weakening it:** Allen's true I_rep is **−7.99**, not −5.00,
and **100%** of its cells read negative — so clipping pins **every one** to exactly 0. The saturation
premise for Allen is not merely confirmed, it is confirmed at the maximum.

**And my fungal −2.212 is NOT touched by that bug:** the pooled fungal spacings have mean
**1.000000** by construction, so r ∈ [0,1] is exactly one mean-ISI. Checked.

## 4. WHERE THIS SESSION CORRECTS THE OVERNIGHT — VERDICT_C is stale

**`VERDICT_C.md` (written 02:37) carries the pre-rate-fix census** — allen −4.8526, hc3 −2.4727,
ret1 −4.7427 — and **VERDICT_A (updated 20:15) supersedes it with −7.99 / −1.44 / −0.32.**
**VERDICT_C was never updated.**

So the overnight's own record contains **three tables of the same quantity, two of them stale**, with
nothing marking which is current. That is the same defect that caught me one paragraph up, and it is
why I made it: a reader taking VERDICT_C at face value gets a number the project has retracted.

**ACTION: mark VERDICT_C superseded in place.** Not deleted — the SUPERSEDED discipline.

## 5. WHAT THE OVERNIGHT HOLDS THAT THIS SESSION LACKED

1. **Reference poles and a clustered ladder for the signed scale** — Poisson/GOE/GUE plus 15 swept
   clustered configs. This session's fungal number had no units until now.
2. **The rate-contamination lesson** — `pair_correlation_full` integrates r ∈ [0,1] *in the input's own
   units*, so the input must be unit-mean-normalised or the window means something different per
   object. **This is a live trap for the 18-site sweep** and it was not on that sweep's list.
3. **The grading discipline, which my compilation loosened.** The overnight banks
   ρ(burst, I_rep) < 0 as **INSTRUMENT VALIDATION, not a discovery** — *"Banking it as a discovery is
   how the next twenty messages get spent defending it."* My compilation presented those rows as a
   substrate finding. **The overnight's slot is the correct one.**

## 6. WHAT THIS SESSION HOLDS THAT THE OVERNIGHT LACKED

1. **The attenuation universality theorem** — ρ(x_c,y)/ρ(x,y) = ρ(x_c,x), so one field-level
   characterisation corrects every statistic that field enters.
2. **The corrector** — `recover_rho`, ±0.002 at 30–90%, refusing at 100%.
3. **The guard, the ratchet, the precondition** — three watchers with declared power.
4. **The propagation finding itself** — that the repair existed and did not reach the toolkit.

---

## 7. NET EFFECT ON THE BOARD

- **Allen's premise: confirmed at maximum** (−7.99, 100% of cells negative). R-124's residual question
  shrinks to "was ρ(rep_int, ks_gue) computed on those saturated bands," which is nearly rhetorical.
- **Fungal's −2.21 now has units** — moderately-to-strongly clustered against an independent ladder.
- **The 18-site sweep gains a precondition it did not have:** check unit-mean normalisation before
  trusting any I_rep, per the overnight's own bug.
- **Two stale tables to mark** — VERDICT_C (theirs), and my compilation's citation (mine, already fixed).
- **The propagation channel is the standing defect.** Two correct derivations, neither reaching the
  shared toolkit until the second one was forced to. The repair is now *in* `arithmetic_toolkit.py`,
  which is the first time it has been where it can fire.

# Estimator → Claim provenance table (STANDING ARTIFACT)

**Why this file exists.** Five times in one session, a lesson was found, written down, and filed where
it could not fire ([[knowledge_does_not_propagate]]). The fifth was the worst *and* is the reason for
this file: **Phase 37 found the CV-16 drift artifact, built CV2/LV to remove it, and the
cross-substrate programme's flagship claim went on running on the contaminated axis for months.**

> **A FIX IS NOT LANDED UNTIL EVERY CLAIM THAT DEPENDS ON THE BROKEN AXIS HAS BEEN RE-RUN.**
> Building the replacement estimator is the easy half. **The hard half is the recompute list.**

This table *is* the recompute list. It is the direct structural fix for the systemic failure — not
vigilance, which failed five times. **Maintain it: when an estimator changes, every claim in its row
is presumed STALE until re-run.**

---

## Axis status

| axis | status | why |
|---|---|---|
| `I.5_ks_gue`, `I.7_ks_poisson` | **SAFE (boundary ≠ null)** but **MARGINAL** | KS is bounded [0,1] by construction; boundary is not a null value. **BUT: contaminated by rate-nonstationarity** — see CV-16 row. |
| `I.10_cv` | **MARGINAL — DRIFT-CONTAMINATED** | global CV is inflated by slow rate-nonstationarity / epoch-gap concatenation (Phase 37, "CV-16") |
| `I.12_cv2`, `I.13_lv` | **SAFE + RATE-ROBUST (PAIR domain)** | adjacent ISIs see ~the same rate; nulls (1.0) sit in the **interior** |
| `⟨r̃⟩` (sessionK) | **SAFE — the design pattern** | bounded [0,1] but the **Poisson null (0.386) is INTERIOR** |
| `I.8_brody_q` | **CENSORED AT BOTH BOUNDS** | `bounds=(0,1)` = Poisson→GOE. Clustering → lower rail; **GUE/GSE → upper rail**. Only **25.2 %** of banked values are interior. |
| `I.9_berry_robnik_rho` | **CENSORED AT BOTH BOUNDS** | same; 63.8 % interior (degrades more gracefully — ρ has a genuine interior null) |
| `I_rep` / `rep_int_q` / **all `BL` verdicts** | **CENSORED AT THE NULL** | `np.maximum(0, 1−R₂)` floors at the Poisson value |
| `bulk_recovery` mass→σ | **CENSORED AT THE NULL** | `np.interp` clamps onto a knot its own comment labels "(Poisson regime)" |

---

## Claims by the estimator they rest on

| estimator | claim | status |
|---|---|---|
| **`I.10_cv` / marginal axes (CV-16 drift)** | **substrate-relativity ladder** ρ(ks_gue, burst): hc-3 > ret-1 > dr > Allen-HPF | **RETRACTED** (`002d834`). Dies on a change of **domain**. Bottom rung = Allen-HPF CV=16.2, CV/LV=13.5. On rate-robust axes the ordering **inverts** (Allen at top). |
| ″ | "Allen-HPF sits at the bottom / near zero coupling" | **RETRACTED.** Its marginal axes are dead; its **pair** axes are **top of the zoo**. |
| **`I.8_brody_q` (lower rail)** | "pvc-11 forms an arc hugging the Poisson axis" | **INVERTED** (`bc81ac6`). pvc-11 is 99.4 % railed ⇒ **CLUSTERED**. |
| ″ | "pvc-11 and Mertens/Liouville collapse together at the Poisson corner" (viewpoint-dependence exhibit) | **MANUFACTURED.** Both censored onto the same bound. *Lesson right, exhibit artifactual.* |
| **`I.8_brody_q` (BOTH rails)** | "L-zeros is internally bimodal: ζ = GUE (q=1), Dirichlet/EC = Poisson-leaning (q≈0)" | **RETRACTED, BOTH LEGS** (`38aadc5`). Modes at 0.0001 and 0.9999 = **the fitter's two bounds**. ζ's q=0.9999 means "≥ GOE", *nothing more*. |
| **`I_rep` / `BL`** | "Fungal pool / Solar flares = BL = Poisson noise" | **INVERTED** → **CLUSTERING DETECTIONS** (exact-0.000 unreachable by the null, 0/200). |
| ″ | `BL` as a verdict class | **RETIRED** (`d20f2b9`). It is a **partition**: 79.2 % exact-0.000 (**detected clustered**) / 20.8 % interior (**real weak repulsion**) — splitting essentially **biological vs not**. |
| **`I_rep` (clustered-side silence)** | `phase36/falsification_calibrator.py`: "ALL BL: near-Poisson transition INVISIBLE to both (taxonomy holds)" | **FLAGGED, NOT RETRACTED.** The silence is manufactured by the clip. Must be re-run on an unclipped `I_rep`. |
| **`I.12_cv2` / `I.13_lv` (rate-robust)** | **NEW:** burst ↔ pair-structure coupling, all 4 neural substrates | **LIVE** (`f0a5c1e`). Real, narrow band; see below. |
| **Brody rail + `I_rep` exact-zero (2 independent detectors)** | **NEW:** every neural CELL substrate is **CLUSTERED** | **LIVE.** Undecimated arm 95.7–100 % railed at conservative P₀=0.60; decimation-immune *by mechanism*. |
| **Palm–Khintchine (theorem)** | pooled/population arms read Poisson-consistent | **LIVE — and the load-bearing calibrator**, because it comes from a theorem about the data, not a synthetic generator. |

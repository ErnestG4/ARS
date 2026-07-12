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
| ″ | `BL` as a verdict class | **RETIRED** (`d20f2b9`, swept in full). A **partition**, never a class: per-cell **79.2 %** exact-0.000; cross-signal **67.5 %**. **Detector validated on the repo's own calibrator: Poisson is 100 % BL and 0/1000 exact-zero.** Full sweep = PERFECT separation: fungal **194/194**, flares **191/191** exact-0 (**CLUSTERED**); binance **0/185** (**genuine weak repulsion**). |
| **`I_rep` (clustered-side silence)** | `phase36/falsification_calibrator.py`: "ALL BL: near-Poisson transition INVISIBLE to both (taxonomy holds)" | **FLAGGED, NOT RETRACTED.** The silence is manufactured by the clip. Must be re-run on an unclipped `I_rep`. |
| **`I.12_cv2` / `I.13_lv` (rate-robust)** | **NEW:** Allen-HPF **marginal/pair dissociation** — burst invisible to every marginal axis (−0.277 / +0.005 / +0.036), strongly coupled to the pair axis (+0.540; partial-on-rate **+0.770**) | **LIVE — LOAD-BEARING** (`002d834`, `7543de6`). **WITHIN-substrate**: same cells, same predictor, two domains. Immune to the quantile, rate, pole, and compression confounds *by construction*. Survived every falsifier aimed at it. |
| ″ | **cross-substrate ORDERING** on pair axes (allen > hc3 > dr > ret1) | **NOT CERTIFIED — UNRESOLVED** (`7543de6`). Gradient is real (4.9 SE) but `burst_frac`'s fixed 10 ms threshold is a **substrate-dependent quantile** (0.5 % in hc-3 → 6.2 % in retina), so it compares correlations of **different predictors**. **Closer pinned:** three-way vs a *threshold-free, marginal-domain* predictor (change of DOMAIN, not of parameter). Needs the raw-ISI recompute. |
| **Brody rail + `I_rep` exact-zero (2 independent detectors)** | **NEW:** every neural CELL substrate is **CLUSTERED** | **LIVE.** Undecimated arm 95.7–100 % railed at conservative P₀=0.60; decimation-immune *by mechanism*. |
| **Palm–Khintchine (theorem)** | pooled/population arms read Poisson-consistent | **LIVE — and the load-bearing calibrator**, because it comes from a theorem about the data, not a synthetic generator. |

---

## Maintenance rules (learned the hard way, in this file, on its first day)

1. **Every hash in this table must resolve.** I wrote a fabricated commit hash (`f0a5c1e`) into the
   first version of this file. `git cat-file -t` caught it. **A provenance table with an unverifiable
   citation is worse than none** — it launders a claim into looking tracked. **Verify every hash before
   committing this file.**
2. **A row's STATUS goes stale faster than its claim.** The CV2/LV row said "LIVE" for one commit after
   `7543de6` had already un-certified half of it. **When a claim is qualified, update its row in the
   same commit.**
3. **This file is the recompute list, not the filing cabinet.** Its failure mode is becoming the place
   where work goes to be *tracked instead of run*. **A row that has sat in NOT-CERTIFIED without its
   closer being attempted is a debt, not a record.**

## Open debts (as of 2026-07-12)

| # | debt | closer | status |
|---|---|---|---|
| 1 | cross-substrate pair-ladder **ordering** | three-way predictor test: fixed-10 ms vs own-quantile vs **threshold-free marginal-domain** predictor. *Only the third is a change of domain; the first two are the same threshold family.* Needs raw-ISI recompute. | **OPEN** |
| 2 | `phase36/falsification_calibrator.py` "taxonomy holds" | re-run against an **unclipped** `I_rep` | **OPEN** |
| 3 | §8 backfill (`rep_med`/`ks_gue_med`) | unclip **+** fix the self-rate normalizer **+** lift the `s<10` truncation **+** calibrate the freed negative half-line (Farey positive anchor; **Cox/Neyman–Scott negative anchor** — the calibrator zoo has **no clustered class at all**) | **OPEN** |
| 4 | *"the whole ladder is a drift gradient"* (Spearman −0.80, **p≈0.20, n=4**) | rebuild on CV2/LV across **all** substrates carrying `burst`; regress ordering on CV/LV | **OPEN — underpowered, not wrong** |

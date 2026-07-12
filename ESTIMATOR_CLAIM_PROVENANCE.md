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
| `I.5_ks_gue`, `I.7_ks_poisson` | **MARGINAL — THREE INDEPENDENT DEFECTS** | boundary ≠ null (safe on *that* axis), but: (1) **CV-16 drift**; (2) **global** unit-mean normalization does not remove within-cell drift; (3) ⚠ **the "2–98% tail trim" (`phase35a/unfold_rotnum.py:70`) is a POSITIONAL slice — it removes NO outliers.** Measured: value-trimming drops Allen `ks_gue` **0.854 → 0.416**; hc-3 0.532→0.494; ret-1 0.477→0.464. **The effect scales with CV. The guard was built for exactly this and does nothing.** |
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
| **`I.12_cv2` / `I.13_lv`** | Allen-HPF "marginal/pair dissociation" | **RETRACTED — ADJUDICATED BY THE SHUFFLE** (overnight Job A, n=4203, 200 shuffles). `ρ(burst, LV_shuf)` = **+0.517** ≈ `ρ(burst, LV_obs)` = **+0.576**. **LV carried essentially no order information.** The dissociation is **global-vs-local NORMALIZATION**, not marginal-vs-pair. What survives, smaller: *`ks_gue` is drift-destroyed at HPF; LV is not; **both are marginal**.* A small genuine order residual remains (`ρ(burst, LV_resid)` = **+0.173** [+0.141,+0.203]) but it is **not** the coupling, and its **sign flips across substrates** (hc-3 **−0.158**, ret-1 **+0.286**) — no consistent story. |
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
| ~~0~~ | ✅ **CLOSED — Allen-HPF dissociation: DRIFT.** Shuffle ran; verdict **RETRACT**. | **within-cell ISI shuffle** (destroys order+drift, preserves the marginal exactly = the renewal null with the observed marginal; a theorem about the data, like Palm–Khintchine). Decompose ρ(burst, LV_shuf) vs ρ(burst, LV_obs−LV_shuf). **Run against `ks_gue` too** — if `ks_gue_shuf ≈ ks_gue_obs`, the old ladder was a **marginal-shape ranking** ⇒ recording-quality hypothesis confirmed from the estimator side. Needs raw-ISI recompute. | **OPEN — BLOCKS the session's load-bearing claim** |
| 1 | cross-substrate ladder **ordering** | **3×2 matrix** (predictor domain × axis domain), NOT the 3-way I specced — *fixed-threshold and own-quantile are the SAME domain (row 1)*. Rows: **global marginal** (log-ISI CV, gamma *k*) / **local marginal** (LV, CV2) / **correlational** (ISI serial corr ρ₁, autocorr excess over shuffle — **the only true order arm, never measured in this project**). | **OPEN — downstream of #0** |
| 2 | `phase36/falsification_calibrator.py` "taxonomy holds" | re-run against an **unclipped** `I_rep` | **UNBLOCKED** — the unclipped `I_rep` now exists and is calibrated (overnight Job B) |
| 3 | §8 backfill (`rep_med`/`ks_gue_med`) | unclip + fix the self-rate normalizer + lift `s<10` + calibrate the negative half-line | **HALF DONE** — overnight Job B built and PASSED the **clustered calibrator class** (Cox/Neyman–Scott/gamma, swept). Unclipped `I_rep` and both-bounds Brody now have a **sign convention and a scale**. Remaining: the self-rate normalizer and `s<10`. |
| 4 | *"the whole ladder is a drift gradient"* (Spearman −0.80, **p≈0.20, n=4**) | rebuild on CV2/LV across **all** substrates carrying `burst`; regress ordering on CV/LV | **OPEN — underpowered, not wrong** |

# The census, demodulated — clustering is RATE MODULATION in 4 of 6 substrates

**Status: FINDING. The census's "every neural substrate is clustered" is CORRECT AS A MEASUREMENT and
FALSE AS A CLAIM ABOUT NEURONS, for allen-hpf, buzsaki, ibl and hc-3.**
2026-07-13. `overnight_2026_07_12/demod*.log`.

## The prediction, from the literature

Brenner, Agam, Bialek & de Ruyter van Steveninck (1998): one dimensionless parameter **γ** spans
**rigid → RMT → Poisson → clustered**, with closed forms for the ISI distribution, the autocorrelation
**and the number variance**. Two consequences:

1. **The intrinsic generator is REPULSIVE.** `P(τ) ~ exp(−1/2γτ)` as τ→0 — an **essential singularity**,
   vanishing faster than any power of τ, hence **faster than any Brody β, faster than GSE, faster than
   any RMT class**. *That is a hard gap — the same species as the class Farey certified.*
2. **The autocorrelation FACTORISES** (Eq. 6) into a **rate-correlation** term × a **universal repulsive**
   term. **Whenever the rate varies you get a Cox process — and that is clustering.**
   ⇒ **The clustering does not come from the neuron. It comes from the rate.**

And ARS's `unfold_unit_mean` is a **global** normalisation. It never removed **within-cell** rate
modulation — so rate-driven clustering passed straight through the instrument into the census.

## THE CANARY — and it is the reason this result is interpretable

The rate-estimator **bandwidth W determines the answer**, so it is **swept, never chosen**. Two ground
truths through the identical pipeline:

| W | **Cox** (rate-modulated Poisson — EXTRINSIC) | **gamma CV=2, constant rate** (INTRINSIC) |
|---|---|---|
| raw | −2.770 | −0.870 |
| **0.05 s** | +0.233 | **−0.037** ← intrinsic clustering **DESTROYED** |
| 1.0 s | **−0.056** (2 % retained) | **−0.626** (72 % retained) |
| 5.0 s | −0.550 (20 %) | −0.814 (94 %) |
| 100 s | −2.327 (84 %) | −0.877 (101 %) |

**At small W the demodulator eats everything** — gamma's *constant-rate* clustering collapses and its
Σ² falls to **1.68, BELOW Poisson**. **Picking W = 0.2 s would have "shown" that every substrate is
rate-driven, and it would have been an artifact of the knob.**
**So the answer is a CURVE SHAPE, not a number** — compare each substrate to the two calibrator curves.
*A change of domain, not a choice of parameter.*

## THE RESULT — the census SPLITS, and it inverts for four substrates

**Retained clustering** = `I_rep(demodulated) / I_rep(raw)`. **Low ⇒ the clustering was rate-driven.**

| substrate | raw `I_rep` | **retained @ W=1 s** | @5 s | @100 s | verdict |
|---|---|---|---|---|---|
| *Cox (EXTRINSIC calibrator)* | −2.770 | **2 %** | 20 % | 84 % | — |
| **allen-hpf** | −7.347 | **1 %** | 4 % | **30 %** | **EXTRINSIC** (beyond Cox) |
| **buzsaki** | −1.879 | **9 %** | 23 % | 62 % | **EXTRINSIC** |
| **ibl-port** | −0.193 | **10 %** | 66 % | 99 % | **EXTRINSIC** |
| **hc3-port** | −1.891 | **11 %** | 44 % | 91 % | **EXTRINSIC** |
| *gamma (INTRINSIC calibrator)* | −0.870 | **72 %** | 94 % | 101 % | — |
| **pvc-11** | −1.281 | **63 %** | 90 % | 100 % | **INTRINSIC** |
| **ret-1** | −0.460 | **93 %** | 98 % | 100 % | **INTRINSIC** (beyond gamma) |

> **For allen-hpf, buzsaki, ibl and hc-3, the clustering is RATE MODULATION, not spike generation.**
> **Allen is the extreme case: even at a 100-SECOND bandwidth only 30 % survives** — its clustering
> lives on timescales **longer than 100 s** (sleep/wake, state).
> **Only ret-1 and pvc-11 have clustering intrinsic to the spike train.**

**Bialek's prediction is confirmed on 4 of 6 substrates.** The measurement was right; **the
interpretation as a property of the neuron is what falls.**

## NOT BANKED — the 6th candidate explanation for the dissociation

| substrate | intrinsic % (W=1 s) | \|coupling\| |
|---|---|---|
| allen-hpf | 1 % | 0.429 |
| buzsaki | 9 % | 0.482 |
| ibl-port | 10 % | **0.694** |
| hc3-port | 11 % | 0.604 |
| pvc-11 | **63 %** | **0.076** |
| ret-1 | **93 %** | **0.187** |

**Qualitatively striking: the two INTRINSIC substrates are the two WEAKEST coupled.** But
`Spearman = −0.429, p = 0.397` (n=6), and **it is not monotone** — allen is the *most* extrinsic (1 %)
and only middling-coupled, while ibl (10 %) is the *strongest*. **A look, not a test. I have refused
weaker this session. NOT BANKED.** The qualitative split is real; the ordering is not.

## The "Allen is state-driven" hypothesis — a LEGITIMATE RESURRECTION, filed as NEW

The retraction **was correct and stays correct**: the *evidence* (low split-half ρ) was **tail-variance
in the estimator** (`ρ(|I_rep|, |split-half error|) = +0.643`). **That evidence is dead.**

**But retracted evidence is not a retracted hypothesis.** The hypothesis now has:
(a) a **mechanistic derivation** (Bialek Eq. 6 — rate variation ⇒ Cox ⇒ clustering);
(b) a **quantitative ceiling** (single-neuron CV saturates ≈ 2–4 as γ→∞; Allen's raw CV is **19**, far
past what is intrinsically reachable);
(c) a **new test touching none of the discredited measurements** — and **it passed**: Allen retains
**1 %** at W=1 s and only **30 %** at W=100 s.

**Filed as a NEW hypothesis with a new closer, NOT as a reinstatement of the old one.**

## Open

- **Three estimators of the same γ** (ISI fit · ACF peak count ∝ 1/γ · Σ² slope). **If they disagree on
  a substrate, the model is wrong for that substrate — and the disagreement IS the measurement.**
  *Arm (e)'s positive form, handed over for free: not a parameter check, a domain check.* **Not yet run.**
- **What is the demodulated class?** If the intrinsic generator has a hard gap (essential singularity),
  the demodulated trains should read **repulsive**, not Poisson. *(Suggestive: ibl and hc-3 go
  **negative-retained** — i.e. `I_rep` flips POSITIVE — at W=0.05 s. But **the Cox calibrator does the
  same (−8 %)**, so this is confounded with over-demodulation and **cannot be read as evidence yet.**)*

---

# ⚠ POST-RUN — THE DECISIVE TEST IS **VOID** (its canary failed), AND THE NUISANCE SWEEP KILLS MATCHED PAIR 2

## 1. The demodulated-coupling test: **CANARY FAILED ⇒ TEST VOID**

The hypothesis under test (Will's): in an **extrinsic** substrate, the predictor (`logCV`) and the axis
(`I_rep`) are **driven by the same rate-modulation term**, so `ρ(logCV, I_rep)` is *rate modulation
correlating with itself through two instruments.* Decisive test: **recompute the coupling on
demodulated trains.**

**Canary first** — a ground truth at each end:

| ensemble | raw | **demod W=1 s** | W=5 s |
|---|---|---|---|
| **COX** — cells differ ONLY in rate-modulation strength ⇒ coupling is a **PURE CONFOUND** ⇒ **must collapse** | −0.999 | **−0.950** | **−0.989** |
| **GAMMA** — cells differ ONLY in intrinsic CV, constant rate ⇒ coupling is **REAL** ⇒ must survive | −0.995 | −0.997 | −0.998 |

> **THE PURE-CONFOUND ENSEMBLE'S COUPLING DOES NOT COLLAPSE.** The demodulator **cannot separate a
> confound from a real relationship.**

**Why:** demodulation is never perfect. It leaves a **residual proportional to the original modulation
strength**, and **both** axes still respond to that residual — so the cross-cell gradient survives in
both, and the correlation survives with it. **A pure-confound ensemble passes the test as if it were
real.**

**⇒ THE TEST HAS NO DISCRIMINATING POWER. NEITHER THE FINDING NOR THE CONFOUND HYPOTHESIS IS
ADJUDICATED.**

*The neural numbers (coupling largely **survives** demodulation, 5 of 6) would have read as outcome 2 —
"the finding is stronger than before" — and **I would have been reporting an artifact of an instrument
that returns that answer regardless**. An instrument that cannot fail cannot pass.*

## 2. The nuisance sweep — and it kills MATCHED PAIR 2

The run used a different cell-inclusion threshold, and the raw couplings **moved**. So the threshold
got swept (it should have been, from the start):

| substrate | minISI=200 | 400 | 1000 | 2000 | 5000 | |
|---|---|---|---|---|---|---|
| **pvc-11** | **+0.121** | **+0.076** | **−0.086** | **−0.226** | **−0.399** | ⚠ **SIGN FLIPS, monotonically** |
| hc3-port | −0.580 | −0.607 | −0.711 | −0.848 | −0.798 | ⚠ drifts 0.27 |
| **ibl-port** | −0.691 | −0.694 | −0.709 | −0.728 | −0.733 | ✓ **STABLE** |
| **ret-1** | −0.185 | −0.187 | −0.166 | −0.210 | −0.190 | ✓ **STABLE** |
| allen-hpf | −0.432 | −0.433 | −0.433 | −0.408 | −0.412 | ✓ stable |
| buzsaki | −0.482 | −0.482 | −0.482 | −0.482 | −0.502 | ✓ stable |

### ⚠ RETRACTED

- **MATCHED PAIR 2 (dr-port vs pvc-11) is DEAD.** Its decisiveness rested on pvc-11 having coupling
  **≈ 0 (+0.076)**. That number is **an artifact of a cell-inclusion threshold nobody registered.**
  **pvc-11's coupling is not an object.**
- **"pvc-11 has NO coupling" is RETRACTED** — and with it, **the death of the sensory/feedforward
  hypothesis**, which rested entirely on *"pvc-11 is sensory AND cortical and couples LESS than
  retina."* At minISI=400 that is true (+0.076 vs −0.187); **at minISI=5000 it REVERSES** (−0.399 vs
  −0.190). **Explanation #5 returns to UNRESOLVED — not re-established, but no longer excluded.**

### ✓ SURVIVES

- **MATCHED PAIR 1 (ibl vs ret-1) SURVIVES EVERY THRESHOLD.** Both are rock-stable
  (−0.69→−0.73; −0.185→−0.210) and the **3.7× gap holds at all five settings.** **The spine holds** —
  and it is now the *only* matched pair.
- The **coupling range** and the **clustering ⊥ coupling** dissociation are unaffected by pvc-11's
  instability in sign (its |coupling| stays small-to-moderate at every threshold).

### The disease, again, one level up

**A cell-inclusion threshold is a nuisance parameter that determines the answer, and it was never
swept.** Same shape as the bandwidth W, the cell-cap, the 10 ms `burst_frac` threshold, the `s<10`
truncation, and `bounds=(0,1)`. **Every one was well-behaved in the region it was chosen for.**

**Standing rule, added:** *any inclusion threshold is a nuisance parameter. Sweep it and report the
curve, or the number is not an object.*

---

# PART 2 — dr-port DEMODULATED, and THE γ DOMAIN CHECK (two validated estimators, one broken one)

## dr-port: **EXTRINSIC** — Will's prediction CONFIRMED

| substrate | raw `I_rep` | **W=1 s** | W=5 s | W=20 s |
|---|---|---|---|---|
| *Cox (EXTRINSIC calibrator)* | −2.770 | **2 %** | 20 % | — |
| allen-hpf | −7.513 | **1 %** | 4 % | 7 % |
| **dr-port** | **−0.639** | **2 %** | 37 % | 56 % |
| buzsaki | −2.219 | **2 %** | 22 % | 43 % |
| hc3-port | −2.540 | 13 % | 45 % | 73 % |
| *gamma (INTRINSIC calibrator)* | −0.870 | **72 %** | 94 % | — |
| pvc-11 | −1.358 | **65 %** | 90 % | 97 % |
| ret-1 | −0.490 | **92 %** | 97 % | 100 % |

**dr-port lands on the Cox calibrator to the percent.** Prediction (*"given its coupling −0.549, it
should come back extrinsic"*) — **confirmed.**

### ⚠ BUT `ibl`'s classification is ILL-CONDITIONED — and `ibl` is half the surviving matched pair

`ibl` reads **−136 %** at W=0.2 s, **−18 %** at W=1 s, **62 %** at W=5 s. Its raw `I_rep` is **−0.176**,
so `retained% = demod/raw` is **a ratio with a near-zero denominator.** **This is the EXACT metric
defect diagnosed two messages ago (retained%) and then RE-COMMITTED here.**
**`ibl`'s intrinsic/extrinsic call is not an object.** The reliable calls are the substrates with
substantial raw clustering: **allen (−7.5), hc3 (−2.5), buzsaki (−2.2), pvc-11 (−1.36), dr-port (−0.64)**.
**ret-1 (−0.49) is marginal; ibl (−0.18) is unusable.**

## The γ domain check — **THE CANARY I SHOULD HAVE RUN FIRST**

Three estimators of one parameter, against **known γ** (gamma renewal, `CV = √γ`):

| TRUE γ | **g_CV** | **g_Σ²** | **g_ACF** |
|---|---|---|---|
| 0.05 | **0.050** ✓ | **0.048** ✓ | 0.091 ✗ |
| 0.50 | **0.503** ✓ | **0.482** ✓ | 0.083 ✗ |
| 2.00 | **1.972** ✓ | **2.050** ✓ | 0.077 ✗ |
| 4.00 | **3.903** ✓ | **4.183** ✓ | 0.077 ✗ |

**`g_CV` and `g_Σ²` recover γ across two orders of magnitude. `g_ACF` returns ≈0.08 for EVERY input.**
**My peak-counter is broken — Bialek is not.** The "DISAGREE (119×)" verdicts were **my own code**, and
without this canary I would have reported *"the model is falsified on every substrate."*
*(A parameter that takes the same value on every input is not measuring anything. Second time this
session an estimator announced itself by being constant.)*

### On the TWO VALIDATED domains, the model HOLDS — and the ceiling argument lands

| substrate | train | CV | g_CV | g_Σ² | verdict |
|---|---|---|---|---|---|
| **allen-hpf** | **RAW** | **19.95** | 397.9 | 90.96 | **MODEL INAPPLICABLE — CV 10× past the intrinsic ceiling** |
| **allen-hpf** | **demod W=5 s** | **1.68** | 2.84 | 1.80 | **1.6× — AGREE, now INSIDE the ceiling** |
| buzsaki | RAW | **2.48** | 6.16 | 11.31 | past ceiling |
| buzsaki | demod | **1.62** | 2.62 | 1.47 | 1.8× — AGREE |
| hc3-port | demod | 1.51 | 2.27 | 2.85 | 1.3× — AGREE |
| ibl-port | demod | 1.03 | 1.07 | 1.09 | **1.02× — AGREE** |
| pvc-11 | demod | 1.86 | 3.45 | 2.96 | 1.2× — AGREE |
| **ret-1** | demod | 1.46 | 2.14 | 0.47 | **4.6× — DISAGREE** |

> **Allen's CV goes 19.95 → 1.68 under demodulation.** Bialek's single-neuron ceiling is ≈ 2.
> **Raw Allen is TEN TIMES past what a neuron can intrinsically produce. Demodulated, it lands inside**
> — and two independent domains then agree on γ to 1.6×.
> **The excess CV is rate modulation. The quantitative ceiling argument is confirmed on the substrate it
> was aimed at.**

**And the one DISAGREEMENT is `ret-1` — the MOST INTRINSIC substrate (92 % retained).** The model
should be *most* applicable there and it is *least* self-consistent (4.6×). **That is the
"disagreement IS the measurement" case, firing.** **Flagged, not chased.** *(Closer: is ret-1's
generator outside the γ-family entirely — i.e. a hard-gap/refractory class the model does not span?
Retina's Σ²(5) = 6.45 is near-Poisson while its `I_rep` is clustered — an unusual combination.)*

# VERDICT A — the within-cell ISI shuffle

> **If ρ(burst, LV_shuf) ≈ ρ(burst, LV_obs), the load-bearing claim of 2026-07-12 is
> retracted to a drift-robustness result. SAY SO OUT LOUD BEFORE READING ANYTHING ELSE.**

git SHA `6da3f807bb` · seed 20260712 · 200 shuffles/cell

The shuffle destroys **all order and all drift** and preserves the **ISI marginal exactly**.
It is the **renewal null with the observed marginal** — analytic ground truth, no generator,
nothing to unfold wrong. Same class of instrument as Palm–Khintchine.

## ks_gue — order-(non)invariance, and the SHIPPED-vs-CORRECT trim

See VERDICT_GATE.md: the shipped `spacings()` does a **positional** slice, not a value-tail
trim, so `ks_gue` is weakly order-dependent **by accident** and **removes no outliers**.

| substrate | max\|ks_obs−ks_shuf\| | median ks_gue (SHIPPED) | median ks_gue (VALUE-TRIMMED) | Δ |
|---|---|---|---|---|
| `allen-hpf-cell` | 7.65e-01 | **0.8541** | **0.4155** | -0.4386 |
| `hc3-port-cell` | 1.90e-01 | **0.5320** | **0.4944** | -0.0375 |
| `ret1-cell` | 3.36e-02 | **0.4766** | **0.4642** | -0.0124 |

**If the value-trimmed ks_gue collapses toward the RMT range at Allen-HPF, then Allen's
'far-from-GUE' marginal was the OUTLIER-INFLATED NORMALISER — a third mechanism, and the
shipped trim was supposed to prevent exactly it.**

`burst_frac` is a pure multiset functional (order-invariant) — so the old ladder's
*predictor* carries no order information regardless.

## The LV decomposition — the real experiment

| substrate | n | ρ(burst, LV_obs) | ρ(burst, LV_shuf) | ρ(burst, LV_resid) | LV_obs−LV_shuf (median) |
|---|---|---|---|---|---|
| **allen-hpf-cell** | 4203 | **+0.576** [+0.552,+0.599] | **+0.517** [+0.492,+0.542] | **+0.173** [+0.141,+0.203] | -0.1165 |
| **hc3-port-cell** | 875 | **+0.479** [+0.426,+0.530] | **+0.475** [+0.423,+0.525] | **-0.158** [-0.222,-0.093] | -0.1796 |
| **ret1-cell** | 325 | **+0.418** [+0.328,+0.508] | **+0.350** [+0.254,+0.440] | **+0.286** [+0.188,+0.388] | -0.0063 |

## VERDICT: **RETRACT**

ρ(burst, LV_shuf) = **+0.517** ≈ ρ(burst, LV_obs) = **+0.576**. **LV carried no order information.** The Allen dissociation is **global-vs-local drift-robustness, NOT marginal-vs-pair.** The finding survives in a smaller form: *ks_gue is drift-destroyed at HPF; LV is not; **both are marginal**.* The 'domain change' was a change of normalization.

---

## POST-RUN (three follow-ups, from banked overnight data)

### 1. The row-3 sign flip — **CLOSED** by its own pre-registered closer

| substrate | median ρ₁ | ρ(burst, LV_resid) | sign match? |
|---|---|---|---|
| allen-hpf | **+0.124** | **+0.173** | ✓ |
| hc3-port | **+0.202** | **−0.158** | ✗ |
| ret1 | **+0.036** | **+0.286** | ✓ |

**Median ρ₁ is POSITIVE in all three — it does not flip.** The residual's sign does. So
`sign(ρ(burst, LV_resid))` **does not track** `sign(median ρ₁)`. Pre-committed closer: *"if it
doesn't, it's residual-subtraction noise and you can close it as such."* **CLOSED.**

*(A `Spearman(median ρ₁, ρ(burst, LV_resid)) = −1.000` appears across the three. **n=3 ⇒ p ≈ 0.33 —
one chance in six.** Recorded and REFUSED. This is precisely the object the session learned not to
bank.)*

### 2. The epitaph — coherent, mechanistically supported, **NOT established**

| substrate | median unclipped `I_rep` | **OLD ladder ρ(ks_gue, burst)** |
|---|---|---|
| **allen-hpf** | **−4.85** ← most clustered | **−0.277** ← bottom of the old ladder |
| ret1 | −4.74 | +0.529 |
| **hc3-port** | **−2.47** ← least clustered | **+0.697** ← top of the old ladder |

`Spearman = +1.000`: **the more clustered the substrate, the lower it sat on the old ladder.**

> **The substrate-relativity ladder was a clustering gradient, measured by an instrument whose defects
> scale with clustering, and reported with the sign reversed.**

**n=3 ⇒ p ≈ 0.33. The rank correlation carries NO weight.** What supports the account is the
**mechanism**, which *is* measured: the value-trim correction scales with clustering (allen **−0.44**,
hc-3 **−0.04**). **Filed as inference-from-form with mechanistic support. Closer: more substrates.**

### 3. THE LADDER, REBUILT ON THE CALIBRATED AXIS

`ρ(burst, unclipped signed I_rep)` — an axis that can **represent** clustering:

| substrate | n | median `I_rep` | **ρ(burst, I_rep)** | 95% CI |
|---|---|---|---|---|
| allen-hpf | 482 | −5.003 | **−0.121** | [−0.217, −0.031] |
| **hc3-port** | 444 | −2.841 | **−0.445** | [−0.512, −0.365] |
| ret1 | 324 | −4.767 | **−0.154** | [−0.259, −0.040] |

**All three NEGATIVE.** `I_rep` < 0 = clustered ⇒ **burstier cells are more clustered**, on every
substrate, CIs excluding zero. **The physically expected direction, for the first time.** Allen is no
longer an inverted outlier — just the weakest coupling. **The sign pathology was the instrument.**

**Ordering (hc3 > ret1 > allen) matches the OLD ks_gue ladder — and CONTRADICTS the LV ladder**
(allen > hc3 > ret1). Two now-valid instruments disagree. **NOT resolved here:** the cross-substrate
ordering on *any* axis remains uncertified while `burst_frac` is a substrate-dependent quantile
(debt #1). **The within-substrate result is solid; the ordering is not.**

---

## POST-RUN #2 — MY OWN BUG, caught by the threshold-free predictor. And the ordering changes.

### (a) The bug: `I_rep` on RAW spike times is RATE-CONTAMINATED

`irep_unclipped(spk)` was called on **raw spike times**, and `pair_correlation_full` integrates over
`r ∈ [0,1]` **in the input's own units — i.e. ONE SECOND.** For a 300 ms-mean-ISI cell that is ~3
mean-ISIs; for a 2000 ms cell it is 0.5. **The integration window meant a different thing per cell.**

**Job B was fine** (synthetic trains were unit-mean by construction). **Job C's census and the first
rebuilt ladder were NOT.**

**How it was caught:** the threshold-free predictor returned `ρ(log-ISI CV, I_rep) = +0.68` — *more
dispersed ISIs ⇒ LESS clustered*, which is **physically backwards**. A sign that cannot be right is
worth more than a magnitude that looks plausible. *(Ninth defect this session, and the first one that
is mine.)*

Fixed: unit-mean-normalise the ISIs before `cumsum`. Calibrators then read correctly —
**poisson +0.004 · clustered −1.182 · GOE +0.281.**

### (b) The census SURVIVES my bug (re-run on rate-corrected `I_rep`)

| substrate | n | median `I_rep` | **% `I_rep` < 0** | verdict |
|---|---|---|---|---|
| allen-hpf | 400 | **−7.99** | **100 %** | **CLUSTERED** ✓ |
| hc3-port | 400 | −1.44 | **98 %** | **CLUSTERED** ✓ |
| ret1 | 325 | −0.32 | **77 %** | **CLUSTERED** ✓ |

Unchanged, as pre-committed: its null is **Poisson**, and no normalisation error touches that.
But the **grading** changes materially: **Allen is now BY FAR the most clustered (−7.99)**, hc-3
middle, ret-1 weakest — where the buggy version had allen ≈ ret-1.

### (c) THE THRESHOLD-FREE LADDER — the ordering CHANGES, and the two threshold-free predictors AGREE

Every ordering in the project was downstream of a **10 ms constant**. `burst_frac`, `ks_gue` and
`I_rep` ladders all shared **the same predictor** — so they were never three instruments, they were
**one contaminated predictor viewed through three axes**, and they could not adjudicate each other.

| substrate | ρ(**burst_frac**, I) *(10 ms threshold)* | ρ(**log-ISI CV**, I) *(free)* | ρ(**gamma shape k**, I) *(free)* |
|---|---|---|---|
| allen-hpf | −0.264 | **−0.398** | **+0.688** |
| **hc3-port** | **−0.581** | **−0.684** | **+0.873** |
| ret1 | −0.291 | **−0.170** | **+0.454** |

**All three agree in SIGN** (log-CV ↑ ⇒ more clustered ⇒ `I_rep` ↓ ✓; gamma k ↑ ⇒ more regular ⇒
`I_rep` ↑ ✓). **And BOTH threshold-free predictors give the same ordering: hc-3 > allen > ret-1.**

**`burst_frac` gave hc-3 > ret-1 > allen. THE ALLEN/RET-1 SWAP WAS THE 10 ms CONSTANT.**

**And the predicted mechanism is confirmed:** Allen's `burst_frac` has the **narrowest IQR**
(**0.132** vs hc-3 0.224, ret-1 0.208) — a **compressed predictor**, hence an **attenuated**
correlation. Move to a threshold-free predictor and Allen climbs from **bottom to middle**. *A range
mismatch was being read as a substrate property — the session's own disease, one level up, in the
predictor.*

### (d) What is banked, and in which register

- **VALIDATION (not a discovery):** *burstier / more-irregular cells are more clustered* — negative on
  every substrate, every predictor, CIs excluding zero, **physically expected direction**. This is the
  **repaired axis passing a consistency check**. It would have been alarming otherwise. **Banked as
  instrument validation.** Banking it as a discovery is how the next twenty messages get spent
  defending it.
- **CANDIDATE FINDING (the strengths):** hc-3 ≈ −0.68/+0.87 ≫ allen ≈ −0.40/+0.69 > ret-1 ≈ −0.17/+0.45,
  **consistent across two independent threshold-free predictors**. This is the **first cross-substrate
  ordering in the project not downstream of the 10 ms constant.** Still n=3 substrates. **Closer:**
  extend to dr-port / ibl / buzsaki / pvc-11 with the same threshold-free predictors.

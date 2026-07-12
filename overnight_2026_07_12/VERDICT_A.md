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

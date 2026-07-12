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

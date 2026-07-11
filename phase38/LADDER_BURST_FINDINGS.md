# Phase 38 on the ladder — burst-side reliability of the substrate-relativity ladder

**Question (from the certified matrix caveat):** the burst↔ks_gue substrate-relativity
ladder is labelled a modality/state axis, and per-cell reliability was UNMEASURED — so
"the ladder could still be a reliability gradient wearing a biological costume." This
measures the neural per-unit (burst) side and tests that directly.

**Protocol** — replicated from the Allen Phase 38 run (`build_ledger.py`): per-unit
statistic split into 5 equal-time windows, odd{0,2,4} vs even{1,3}, Spearman-Brown
`ρ=2r/(1+r)`, rank-robust. Per-unit statistic = `burst_frac = mean(ISI < 10 ms)` (repo
convention, `allen_hpf.py:81`). `phase38/ladder_burst_reliability.py`.

## Result — ρ_burst is FLAT-HIGH across the ladder

| rung | ladder r | R²_obs | ρ_burst | n | median rate | gate |
|---|---|---|---|---|---|---|
| hc-3 EC | **+0.78** | 0.61 | **0.980** | 334 | 0.51 Hz | ρ≫R²_obs → verdictable |
| Allen V1 | **+0.25** | 0.06 | **0.984** | 465 | 4.42 Hz | ρ≫R²_obs → verdictable |

**The diagnostic (regress ρ_burst vs ladder position): FLAT.** ρ_burst ≈ 0.98 at both the
top (+0.78) and a low (+0.25) rung — and flat *despite* hc-3 firing 8× slower than V1. A
reliability gradient would require ρ_burst to rise with the ladder r; it does not.

## The rate confound (the user's watch-out) — DISARMED

Low firing rate mechanically depresses split-half ρ, and that is exactly the confound the
regression tests. Pooled hc-3+V1 (n=884), ρ_burst by firing-rate quartile:

| quartile | rate | ρ_burst |
|---|---|---|
| Q1 | 0.03–0.54 Hz | 0.964 |
| Q2 | 0.54–1.94 Hz | 0.987 |
| Q3 | 1.94–6.17 Hz | 0.984 |
| Q4 | 6.29–51.8 Hz | 0.990 |

Flat. Even the 0.03–0.54 Hz bottom quartile is ρ=0.964. **burst_frac is an intrinsic,
stable per-cell property** — bursty cells are consistently bursty even when sparse —
unlike the `p7_mean_z` z-score (ρ=0.281) that motivated Phase 38. The rate confound does
not fire for this statistic.

## Verdict

**On the two measured rungs (spanning +0.25 → +0.78), the ladder is NOT a reliability
gradient in a biological costume.** Both sides of the burst↔ks_gue correlation are highly
reliable — burst ρ≈0.98 here, ks_gue ρ=0.978 (Phase 38, Allen) — so the correlation is
**not attenuation-limited**, and the ladder ordering is not explained by differential
burst reliability. This upgrades the matrix caveat from "could be a reliability gradient"
to "reliability-verified on the burst side, ordering survives as structure."

## Scope / open

- **2 of 5 rungs measured.** ret-1 (+0.53, CRCNS MATLAB zip in `crcns_cache/ret1`), 000638
  (+0.44, DANDI), Allen-HPF (~0) not yet run — each a distinct loader. The two measured
  rungs span most of the ladder's range and both give ρ≈0.98, so the flat pattern is
  well-anchored, but the null rung (HPF ~0) is the most valuable remaining point.
- The diagnostic has an intrinsic ceiling: because burst_frac is reliable everywhere
  (ρ≈0.98 flat), the ρ-vs-ladder regression is flat by construction — which IS the
  informative negative (reliability cannot be what orders the ladder), but it means this
  statistic can't produce a *positive* reliability-gradient finding no matter the rung.
- Measures burst_frac reliability specifically (the statistic the ladder rests on). Rungs
  whose *other* headline claims rest on a different per-cell statistic (spatial_info for
  000638 pillar-2, OSI for V1 H1) would need that statistic's own reliability measured.

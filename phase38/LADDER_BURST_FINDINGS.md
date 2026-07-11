# Phase 38 on the ladder — burst-side reliability of the substrate-relativity ladder

**Question (from the certified matrix caveat):** the burst↔ks_gue substrate-relativity
ladder is labelled a modality/state axis, and per-cell reliability was UNMEASURED — so
"the ladder could still be a reliability gradient wearing a biological costume." This
measures the neural per-unit (burst) side and tests that directly.

**Protocol** — replicated from the Allen Phase 38 run (`build_ledger.py`): per-unit
statistic split into 5 equal-time windows, odd{0,2,4} vs even{1,3}, Spearman-Brown
`ρ=2r/(1+r)`, rank-robust. Per-unit statistic = `burst_frac = mean(ISI < 10 ms)` (repo
convention, `allen_hpf.py:81`). `phase38/ladder_burst_reliability.py`.

## Result — ρ_burst is FLAT-HIGH across four of five rungs, incl. the null

| rung | ladder r | R²_obs | ρ_burst | n | median rate | gate |
|---|---|---|---|---|---|---|
| hc-3 EC | **+0.78** | 0.61 | **0.980** | 334 | 0.51 Hz | ρ≫R²_obs → verdictable |
| ret-1 retina | **+0.53** | 0.28 | **0.996** | 325 | 6.42 Hz | ρ≫R²_obs → verdictable |
| Allen V1 | **+0.25** | 0.06 | **0.984** | 465 | 4.42 Hz | ρ≫R²_obs → verdictable |
| **Allen-HPF** | **~0** | ~0 | **0.970** | 4397 | 3.16 Hz | reliable → **null is STRUCTURAL** |
| 000638 MEC | +0.44 | 0.19 | — | — | — | skipped (interpolation; see below) |

**The diagnostic (regress ρ_burst vs ladder position): FLAT-HIGH, ρ≈0.97–0.996.** A
reliability gradient would require ρ_burst to rise with the ladder r; it does not — flat
even though hc-3 fires 8× slower than V1.

### The estimator is SATURATED — which changes what the remaining rungs could tell you
ρ_burst ≈ 0.98 flat, *including the 0.03–0.54 Hz bottom quartile* (the regime where
attenuation should bite hardest, ρ=0.964). A split-half estimator pinned at its ceiling
cannot discriminate: it will return ~0.98 on any rung. So the interior rungs (ret-1 +0.53,
000638 +0.44) are **interpolation inside the already-bracketed 0.25→0.78 span** — they
confirm (ret-1 did: 0.996) but cannot change the verdict. **ret-1 was run and confirms;
000638 is skippable bookkeeping.**

### HPF is the one rung that could have surprised — and didn't (the informative negative)
Every signal-bearing rung has a correlation to explain; **HPF has an *absence* (~0), and an
absence is the only place a reliability floor could hide** — a washed-out signal and a
genuinely-absent signal look identical in the correlation alone. Saturation *predicted*
HPF would return ρ≈0.98, meaning its null is structural. It did: **ρ_burst=0.970 (n=4397),
flat across rate (0.942 even at the bottom quartile).** burst_frac is fully reliable in
HPF, so its zero burst↔ks_gue correlation is **genuinely absent, not attenuation-destroyed.**
Had HPF come back low, that is the single outcome that would have reopened the question —
and the saturation result said it wouldn't. It didn't. Falsification test passed.

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

## Verdict — reliability is RULED OUT as the ordering mechanism (all reachable rungs, incl. null)

Across four rungs spanning +0.78 → ~0, including the structural null, ρ_burst is flat at
0.97–0.996. Both sides of burst↔ks_gue are reliable (burst ≈0.98 here, ks_gue 0.978 from
Phase 38 Allen), so the correlation is **not attenuation-limited** at any rung, and the
ladder ordering is **not** explained by differential burst reliability. The HPF null is
structural, not washed out.

## What this does and does NOT establish — stated plainly

**Ruling out a confound promotes nothing.** This removes *one* competing explanation
(reliability) for the ladder ordering; it does not put biology in. The ordering is still
unexplained. The answered question is "is it reliable" (yes, everywhere). The *unanswered*
question is now the right next one:

> **What does `burst_frac` covary with across substrates that isn't biology?**
> — recording depth, spike-sorting pipeline, session length, stimulus condition, probe
> type. These are the confounds the reliability gate never touched **and cannot** — they
> need a different instrument (a covariate-matched cross-substrate contrast), not Phase 38.

That is the next axis to look down if the goal is seeing what can be seen. Phase 38 has
said all it can about this ladder.

## Scope

- **4 of 5 rungs; 000638 (+0.44) skipped by design** — the saturation result makes it
  interpolation inside the 0.25→0.78 bracket (DANDI-stream, bookkeeping-whenever). The
  informative rung (HPF null) is done.
- **Saturation ceiling is intrinsic:** because burst_frac is reliable everywhere, this
  statistic can only ever return the negative (reliability can't order the ladder). It
  structurally cannot produce a *positive* reliability-gradient finding — which is why the
  HPF null, not another signal-bearing rung, was the only remaining informative point.
- Measures burst_frac reliability specifically. Rungs whose *other* claims rest on a
  different per-cell statistic (spatial_info for 000638 pillar-2, OSI for V1 H1) would
  need that statistic's own reliability measured — a separate question from this ladder.

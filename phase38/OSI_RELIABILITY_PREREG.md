# Pre-registration — OSI split-half reliability (H1 axis), Allen V1

**Written before running. Timestamp: 2026-07-11.** The falsification test the burst-axis
result could not be: OSI is a stimulus-tuning fit with a known low-count upward bias (noise
reads as selectivity), so unlike `burst_frac` it has a *live* chance of failing.

## Method (fixed before results)
- Recompute **global OSI** from per-presentation drifting-gratings responses:
  `gOSI = |Σ_k R_k e^{2iθ_k}| / Σ_k R_k`, R_k = mean spike-count response at orientation θ_k.
  (g_osi_dg is a precomputed Allen scalar and cannot be split; recomputation is required.)
- **Split-half = odd vs even presentations** (interleaved by presentation index within each
  orientation), gOSI computed on each half, ρ_OSI = Spearman-Brown `2r/(1+r)`, rank-robust
  (Spearman), across the same 6 Phase 38 Allen sessions / VISp cohort.
- Regress ρ_OSI against firing-rate quartile (pooled), matching the burst-axis diagnostic.

## Pre-registered predictions
- **P1 — ρ_OSI does NOT saturate.** ρ_OSI materially below the burst ceiling (predict
  ρ_OSI < 0.85; burst was 0.97–0.996). Falsified if ρ_OSI ≥ 0.95.
- **P2 — ρ_OSI DECLINES with firing rate.** Bottom-rate quartile ρ_OSI well below top
  quartile (predict a clear monotone rise with rate; Spearman(quartile, ρ_OSI) > +0.5).
  Falsified if flat.

## Consequences (fixed before results)
- **If P1 ∧ P2 fire:** H1's already-downgraded OSI↔ks_gue (+0.363, marginal) is *partly
  attenuation structure*. Given the bias sign (low counts → inflated OSI *and* noisier
  ks_gue), the mandatory follow-up is **whether OSI↔ks_gue survives conditioning on firing
  rate** (partial correlation / within-rate-stratum). If it doesn't, the marginal H1 gradient
  is itself a joint-rate artifact.
- **If ρ_OSI saturates (P1 falsified) — a genuine surprise:** H1's downgrade rests **purely
  on the PSTH-unfold null** (OSI↔Σ² → null, 0/100 rigid), not on any reliability story. A
  cleaner place for the downgrade to rest.

## Scope guard
This gates the **OSI** statistic on Allen V1 only. It does not touch spatial_info (000638
pillar-2), which is the same protocol afterward and the one predicted to fail hardest — but a
single rung, so it moves less. The burst-axis closure does NOT generalize past burst; this is
the test of whether it does.

---

# OUTCOME (2026-07-11) — both predictions FALSIFIED as stated; the deeper structure is selectivity-gating

n=465 Allen V1 (VISp, 6 Phase 38 sessions), recomputed gOSI, odd/even trial split.

- **ρ_OSI (population) = 0.957.** **P1 FALSIFIED** (predicted <0.85; not saturated-vs-burst,
  but reliable).
- **ρ_OSI by firing rate:** 0.972 / 0.969 / 0.967 / **0.859** (Q1→Q4). **P2 FALSIFIED** —
  trend is −1.000 (declines at HIGH rate, opposite of the predicted low-rate count-bias).

**The real result — OSI reliability is SELECTIVITY-GATED, not flat** (ρ_OSI by OSI quartile):

| OSI | ρ_OSI | median rate |
|---|---|---|
| 0.01–0.10 | 0.499 | 9.1 Hz |
| 0.10–0.17 | **0.000** | 5.9 Hz |
| 0.17–0.37 | 0.685 | 4.0 Hz |
| 0.38–0.99 | 0.974 | 2.1 Hz |

The population 0.957 is an **aggregation illusion** — carried by the selective tail; unselective
cells have ~zero OSI reliability (a near-zero tuning vector has no reproducible phase).
`corr(rate, OSI) = −0.49`: high-rate cells are broadly-tuned/low-OSI, so the Q4 rate-drop is a
**selectivity floor**, not a count-bias — the predicted rate effect exists but is *mediated by
selectivity*, not raw rate. So OSI does NOT saturate like burst (burst was intrinsic and flat);
the burst-axis closure genuinely does not transfer.

**Consequence for H1 (OSI↔ks_gue = selective cells read away from GUE):**
- The claim lives in the **selective cells** (high OSI → the correlation's load-bearing end),
  and those cells have **reliable OSI (ρ=0.974)**. So H1's marginal gradient is
  reliability-supported *where it matters*; it is not a pure attenuation artifact. Gate: overall
  ρ_OSI=0.957 ≫ attenuation floor 0.135 (R²_obs=0.132/ρ_ksgue) → **not attenuation-limited**.
- OSI is nonetheless a **noisy per-cell statistic across the unselective majority** (ρ=0 near
  the mode), so population OSI reliability *overstates* per-cell reliability — a caveat for any
  future per-cell OSI orthogonality claim, though not for the marginal H1.
- **H1's downgrade (level-repulsion class → marginal gradient) rests on the PSTH-unfold null,
  as before** — this test neither rescues nor worsens it; it confirms the residual marginal H1
  is reliability-supported at the selective end. The cleaner resting place predicted for the
  P1-falsified branch, with the added precision that OSI reliability is selectivity-gated.

**Pre-registration honesty:** I predicted the wrong sign and both predictions failed as
written. The stratification (run *after* seeing the falsification) is the diagnostic that
recovered the real structure — flagged as post-hoc, but it explains both failures coherently
and is itself testable (predicts ρ_OSI floors wherever OSI is low, any substrate).

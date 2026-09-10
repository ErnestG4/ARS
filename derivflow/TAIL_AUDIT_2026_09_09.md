# Tail audit, 2026-09-09 — the finding survives, the argument for it did not

Adversarial audit, commissioned to KILL a claim made earlier the same day: that the
sealed F3 fit fails out of sample past its window, that the data there follow a power
law, and that the tail is real **because it is n-independent**. Read-only; the auditor
re-ran the repo's own `reference_cdf` pipeline and verified it bit-identical
(max|ΔF| = 0) before varying anything.

## Confirmed

- **The out-of-sample failure is real and exactly as reported.** Sealed `shape_params`
  extrapolated to k = 24/32/48/64 under-predict by up to **3.5 decades (iid)** and
  **4.2 decades (GUE)**. Reproduced by per-n refits at all three n.
- **The tail itself could not be killed.** The ε → 0 limit exists, is nonzero, and the
  raw and Richardson arms agree there to 1.1%. No n-independent floor mechanism was
  found. Quadrature (rms 8.6e-12), solver roundoff after 64 compositions (4.3e-14),
  outliers (top 1% of pairs carry 1.4%) and the bulk window (a fixed FRACTION, 190
  gaps at n=1024 to 806 at n=4096) were each tested and excluded.
- **n-independence survives** the corrections below.

## The argument was worthless — two independent ways

**`1 − <r̃>` is a LOCATION statistic, not a fluctuation statistic.** For gaps
`s = 1 + η·z`, `1 − <r̃> = (2/√π)·η`, independent of window size. Verified here
directly: at η = 1e-4 the statistic reads 1.122/1.129/1.130/1.128/1.128 e-4 at
W = 200/800/3200/12800/51200, against the predicted 1.1284e-4. **Averaging more roots
shrinks the error ON the mean, never the mean.** There is therefore no n^(-1/2)
sampling floor in this estimator for n-independence to falsify. The test had nothing
to test.

**And the bandwidth is n-independent by construction.** `eps_rule_v15` is
`Δ_s·√(0.25 + 16(n−k)/(kn))`, i.e. pinned to the LOCAL MEAN SPACING and tending to
0.5·Δ at large k. At k = 64 it gives ε/Δ_s = **0.696 / 0.702 / 0.704** at
n = 1024/2048/4096 — n-independent to 1.2%. Any bias it induces is n-independent by
design, so the test had **zero power against the leading artifact candidate**.

Both are checkable from the repo's own source in minutes, and neither was checked
before the claim was made. This is [[null-excludes-only-its-confound]] and
[[witness-must-be-able-to-fail]]: a null that cannot fire is not evidence.

## The bigger finding: the sealed readout is biased over this k range

At the sealed setting ε is **0.70–4.03 mean spacings** — far outside the asymptotic
O(ε²) regime that the Richardson pair `2F(ε) − F(2ε)` assumes. The raw S(ε) curve is
**non-monotone** (minimum near ε ≈ 0.25–0.5 Δ), so at c = 1 the pair OVER-corrects.
Scaling the bandwidth by c and pushing c → 0, both arms converge cleanly and agree.
Converged / sealed ratios:

| k | 16 | 24 | 32 | 48 | 64 |
|---|---|---|---|---|---|
| iid n=1024, 9 reps | 1.396±0.074 | 1.593±0.042 | 1.463±0.016 | 1.262±0.010 | 1.169±0.009 |
| GUE n=1024, rep0 | **3.71** | **3.04** | 2.03 | 1.43 | 1.27 |

Because the bias is **k-dependent** it biases the fitted exponent shallow by
**0.157 ± 0.047** (iid, paired per-replicate) and by ≈ **0.9** (GUE).

**Corrected tail exponents:** iid **−2.489 ± 0.052** (local slopes constant within
error, so a power law is a good description); GUE **≈ −3.0 ± 0.1** (mild steepening).
**iid decays MORE SLOWLY than GUE** — the opposite of the ordering claimed earlier,
and the GUE value was off by ~0.9. GUE's apparent "shoulder" at k = 24→32 (local slope
−1.22, reproducible at all three n) **disappears** with the converged instrument
(−2.85/−2.89/−3.06/−3.24): that shape was instrument-generated.

**The σ counting was invalid.** `sigma_mean` is a 16-replicate spread SHARED across k,
so per-k errors are strongly correlated — the sealed F3 fit to GUE gives χ² = 0.1 on
8 dof, eleven points reproduced to 0.02σ, impossible for independent errors. It also
carries no instrument systematic, which is +17% to +271% at these k. The 3–4 decade
discrepancy stands; the "20–63σ" does not.

## Why the known-answer gate could not see it

The Richardson primary was certified on the **picket fence** and Hermite. An exactly
periodic configuration makes any bandwidth bias **translation-invariant**, so it
cancels identically in a gap-RATIO statistic — every gap is distorted the same way and
r̃ ≡ 1 regardless. The gate is **structurally incapable** of detecting this class of
defect. Measured: picket primary readouts are 1e-9…1e-11, four to six orders below the
disorder-dependent bias. [[gate-certifies-half-say-so]].

## What this touches, and what it does not

**OPEN AND SERIOUS — the fit windows may be instrument-set, and class-dependently so.**
The window rule is `mean > 1e-3`. GUE's window ends at k=11 and iid's at k=16.
Converged GUE k=16 = 1.035e-3 and converged iid k=24 = 1.266e-3 — both ABOVE the floor.
`TRACK0_FINDINGS.md` records the symptom ("Richardson lowers k=8 to 0.00455 and pushes
k=16 under the 1e-3 floor") and reads it as the correction working. If the windows are
set by a seed-class-dependent bias, then a verdict that the seed classes DIFFER has a
confound at its centre: τ and β are compared across 16 points vs 11
([[commensurability-check]]), and the sealed z = 20.4 / 9.3 are fitted on those windows.
The in-window misfit is separately real (iid n=4096 χ²/dof = 3.76, structured residuals),
which alone would take z(τ) from 20.4 to ~10.

**NOT established:** that `RATE-SEED-DEPENDENT` is wrong. Nothing here refits the
science. What is established is that the instrument has a documented bias over the k
range that sets the windows, and that this has not been accounted for.

**Scope limit of the audit itself:** the converged comparison used 9 iid replicates at
n=1024 and single replicates at n=2048/4096, and 3 GUE replicates at n=1024 — not full
16-replicate ensembles at all three n.

## Consequence

The repo's post-change protocol already covers this: an instrument modification triggers
re-certification of the known-answer gates before science is recomputed. This is the same
shape as the v1 retraction (reference-grid aliasing, `c235861`), and it needs the same
treatment — with one addition, since the picket-fence gate is now known to be blind to
this defect class: **a new gate on a DISORDERED known-answer configuration**, where a
translation-invariant bandwidth bias does not cancel.

Nothing in the paper should be re-worded until that runs. The Campbell letter's tail
paragraph is already pulled.

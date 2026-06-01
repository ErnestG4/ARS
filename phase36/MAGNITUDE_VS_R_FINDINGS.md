# Within-GCM Magnitude↔R · Findings (guardrail item: coherence → evidence)

**Phase 36, 2026-06-01.** `phase36/magnitude_vs_R.py`. The banked guardrail held the cross-substrate
magnitude comparison ("Kuramoto 2.87 vs Kaneko ~50") as COHERENCE not evidence for "clustering magnitude
tracks the order-parameter R," because (a) Kaneko≠Kuramoto in family/topology/N and (b) the within-Kaneko
Δ-sweep used Δ as the knob, and Δ co-varies more than ΔR (Δ is the natural-frequency heterogeneity — it
changes the substrate itself). The clean test (Will's spec): vary **coupling ε** at fixed (family, topology,
N) — ε enters only through the sync term ε·R·sin(·), the purest R-knob — and trace the N-robust clustering
magnitude (**mass<τ** on the snapshot; CV is the √N H-D trap) vs the **directly-measured R**, at two N.

## Result (K=0.6, Δ=0.04, ε-sweep densely resolving the transition, 5 seeds, snapshot observable)

| R (measured) | mass<τ (N=1500) | mass<τ (N=3000) |
|---|---|---|
| 0.11 | 0.301 | 0.301 |
| 0.18–0.19 | 0.329 | 0.331 |
| 0.28–0.30 | 0.363 | 0.372 |
| 0.46–0.47 | 0.440 | 0.442 |
| 0.69–0.71 | 0.578 | 0.588 |
| 0.85–0.86 | 0.704 | 0.715 |
| 0.92 | 0.817 | 0.822 |
| 0.96–0.99 (sat) | 0.944–0.999 | 0.945–1.000 |

- **Monotone:** rank-corr(mass<τ, R) = **+0.995** at both N. mass<τ rises smoothly and monotonically with R.
- **N-invariant:** the mass<τ-vs-R curve OVERLAYS across N to **|Δmass| = 0.0020** (avg over the
  densely-sampled R∈[0.1,0.85]). The magnitude is a function of R (physical), not N (artifact).
- **√N-trap contrast (confirms mass<τ is the right measure):** in the saturated regime CV = 38.3 (N=1500)
  vs 54.2 (N=3000) — ratio √2 = √(3000/1500), the exact H-D √N inflation — while mass<τ saturates at 0.999
  at BOTH N. CV would have manufactured a spurious "bigger magnitude at bigger N"; mass<τ does not.

## Verdict
**magnitude↔R is now WITHIN-SUBSTRATE EVIDENCE** (upgraded from coherence): within Kaneko GCM, on the
N-robust mass<τ measure with R driven cleanly by ε, the clustering magnitude is a monotone, N-invariant
function of the order parameter R.

## Scope / what is still NOT claimed
- This is WITHIN Kaneko GCM. The CROSS-substrate claim (Kuramoto-vs-Kaneko magnitudes reflect their ΔR
  difference) is still not directly tested. Two sharpenings of the guardrail:
  1. The old "2.87 vs 50" was a **CV** comparison — i.e., on the √N-contaminated measure this test shows is
     the WRONG one to compare across different-N substrates. A valid cross-substrate magnitude comparison
     needs **mass<τ at matched τ** on both substrates' matched snapshot observable, not CV.
  2. Even with mass<τ, a cross-substrate comparison must control family/topology; the within-substrate law
     established here is the reference the cross-substrate question should be posed against.
- Establishes a within-substrate magnitude LAW; the cross-substrate magnitude question remains open but is
  now well-posed (compare mass<τ-vs-R laws, not raw CV values).

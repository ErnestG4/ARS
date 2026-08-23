# Brocot — the D_Q–rigidity relation SATURATES, and it saturates by class

**2026-08-23.** Closes the question `overnight_2026_08_22/RESULTS_B1_B2.md` left open:
*"whether the attenuation is SUBSTANTIVE (the relation genuinely saturates as approximability runs
out) or INSTRUMENTAL (less dynamic range in q up there)."*

Three sealed measurements, each generator committed before its output.

---

## 1. The attenuation is SUBSTANTIVE (`brocot_attenuation.json`)

B2 split on **terciles of the predictor** D_Q, deliberately never the outcome. That choice — made
to avoid manufacturing a correlation — is what makes the question decidable: **under restriction on
X the OLS slope is unbiased while the correlation attenuates by a known formula.** So correlation
and slope come apart, and which one moves says which story is true.

Both moved, and the slope moved decisively:

| tercile | n | SD(D_Q) | SD(u) | pearson | spearman | **slope** |
|---|---|---|---|---|---|---|
| bottom | 85 | 0.0469 | 0.4822 | 0.698 | 0.830 | **+7.167** |
| middle | 85 | 0.0105 | 0.2876 | 0.068 | 0.128 | +1.854 |
| top (rigid) | 85 | 0.0472 | 0.2279 | 0.240 | 0.362 | **+1.162** |
| full | 255 | 0.0732 | 0.4661 | 0.703 | 0.658 | +4.477 |

- **Slope difference −3.32, bootstrap CI [−4.39, −2.29]** — excludes zero.
- Pure X-restriction predicts r_top = **+0.537**; observed **+0.240**. The drop is 0.297 beyond
  what removing predictor variance can account for (sealed threshold 0.15).
- **The SD ratio is 0.644, not below 0.5** — predictor range barely narrowed while the correlation
  more than halved. That is the *opposite* of the range-restriction story.

**A ceiling artifact is excluded by construction:** B1/B2 chose the **unbounded** Brody axis
precisely so the outcome has no rail to pile against.

**All four scored predictions missed.** I sealed A4 = INSTRUMENTAL and named COMPOSITIONAL as the
informative failure; the answer was neither.

## 2. It is not merely a between-class effect (`brocot_within_between.json`)

The attenuation run left within-class slopes in the top tercile disagreeing in **sign** — golden
−1.79, ln2 +3.98 — so the pooled relation had to be decomposed. This repo's own rule, *within
before pooled*, had been applied to substrates and never to this population's own classes.

By the law of total covariance: **between carries 0.636**, within 0.364. Between dominates, but not
overwhelmingly — and the decisive cell is the one class that can actually be tested:

> **`generic`** — n=39, the widest within-class D_Q range (SD 0.083) — slope **+4.94**,
> pearson **+0.662**, against a pooled **+4.48**, **+0.703**.

Where a within-class test is well powered, the dose-response reproduces **at full strength inside a
single class**. The sealed re-scoping clause therefore does **not** fire: this is not an ecological
artifact.

## 3. The two findings are ONE (`brocot_slope_by_class.json`)

Larger D_Q means harder to approximate, so the top tercile *is* the rigid end. If the flat classes
are the ones sitting there, the two results are the same statement on two cuts. They are:

| class | mean D_Q | SD(D_Q) | within-class slope |
|---|---|---|---|
| generic | 0.106 | 0.083 | **+4.94** |
| liouville | 0.113 | 0.031 | **+8.63** |
| pi_minus_3 | 0.141 | 0.051 | **+7.86** |
| metallic5 | 0.186 | 0.019 | +5.14 |
| metallic4 | 0.207 | 0.016 | −0.81 |
| ln2 | 0.212 | 0.031 | +0.81 |
| bronze | 0.220 | 0.037 | +1.48 |
| e_minus_2 | 0.227 | 0.065 | **+0.28** |
| golden | 0.231 | 0.066 | **+0.31** |
| silver | 0.238 | 0.072 | +0.82 |

- ρ(class-mean D_Q, within-class slope) = **−0.636**, CI [−0.925, **−0.005**]
- **partial ρ controlling for within-class SD(D_Q) = −0.651, CI [−0.961, −0.271]**

**The control strengthens it.** That was the pre-registered arm that mattered: without it, "rigid
classes have flat slopes" could have been "rigid classes are narrow, so their slopes are noise
centred on zero". It is not — `golden` and `e_minus_2` are flat at *large* within-class D_Q spread
(0.066, 0.065), so they are **well-powered nulls**.

**Say S1's weakness plainly:** its CI upper bound is −0.005 on 10 classes. S1 alone would be
marginal. S2 carries the result.

---

## The finding

> **The D_Q–rigidity dose-response exists at the approximable end and vanishes at the rigid end.**
> It is a real saturation, not a measurement limit and not a change of class composition — and the
> population-level attenuation B2 measured is the same phenomenon as the class-level split.

## What is ruled out

| candidate | how |
|---|---|
| range restriction (instrumental) | slope moves, CI excludes 0; SD ratio 0.644 is too mild |
| outcome ceiling / rail artifact | unbounded Brody axis, by construction |
| class composition | top tercile not class-skewed (largest class 16%) |
| purely ecological | `generic` reproduces the pooled relation within one class |
| power artifact in the class result | partial ρ controlling for within-class spread is *stronger* |

## Open — with the promotion condition pinned

1. **Mechanism.** *Why* the dose-response vanishes at the rigid end is unmeasured. Saturation is
   described, not explained.
2. **The metallics are underpowered.** `metallic4` (SD 0.016) and `metallic5` (SD 0.019) have
   slopes that carry little weight either way. **Promotes when:** a targeted α sample widens their
   within-class D_Q range to ≳0.05, comparable to golden's.
3. **n = 10 classes is small.** **Promotes when:** more classes, or a resampling scheme over α
   within class rather than over classes, tightens S1's CI away from zero on its own.
4. ~~**Everything here is at DEPTH = 8.**~~ **CLOSED 2026-08-23 — `brocot_depth_sweep.json`.**
   Swept at depths {4, 6, 8, 10, 12, 14}, a 6-fold change in partial count (130 → 790). The
   slope-difference CI **excludes zero at every depth**; verdict `DEPTH_INVARIANT`. The magnitude
   moves only 1.6× (I predicted >2× and was wrong in the favourable direction), and the class-level
   partial ρ is negative at every depth and **strengthens monotonically with it**, −0.655 at depth 4
   to −0.851 at depth 14.

   Two patterns fell out. The pooled ρ *declines* with depth (0.679 → 0.547) while the
   class-position result *strengthens* — more partials sharpen the class-level structure while
   blurring the pooled one. And at depth 14 the top-tercile slope goes slightly **negative**
   (−0.29), so at high resolution the rigid end is not merely flat.

   The caveat named here as "most likely to matter" is the one that most strengthened the finding.

## Verification

`verify_brocot.py` extended with pins 5–8, each red-pathed: perturbing the slope-difference CI,
`generic`'s within-class slope, the partial-ρ CI, and the depth-sweep verdict each turn the checker
red with the diagnosis naming which reading would return.

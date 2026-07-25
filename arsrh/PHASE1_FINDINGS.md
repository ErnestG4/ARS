# ARS-RH Phase 1 — ζ height crossover: sealed prediction falsified, a real resolvable crossover

Prereg: `arsrh/PHASE1_PREREG_SEALED.json`. **§0 anti-claim BINDING and maintained:** this is an
instrument-resolution result — whether the ARS ⟨r̃⟩ classifier can *resolve* the finite-height
approach of ζ spacing statistics to GUE above its own noise floor. It is **not** evidence about RH.
Artifacts: `phase1_zeta_crossover.py`, `phase1_zeta_crossover_measured.json`.

## The deterministic-noise null (the blocking prerequisite), built right

ζ zeros have no measurement noise, so the only legitimate error bar on ⟨r̃⟩ in a window is the
**finite-window sampling spread of ⟨r̃⟩ over a stationary GUE spectrum** of the same window W. Built
from the Dumitriu–Edelman β=2 Hermite **tridiagonal** ensemble (exact GUE eigenvalue statistics,
`eigh_tridiagonal`, O(W²), no dense eig / no GPU — the algorithmic fix that beats brute-forcing dense
eig on any machine). Normalization matters: diag ~ N(0,2) (= √2·randn), the correct DE form — diag ~
N(0,1) gave a wrong ⟨r̃⟩=0.633 (caught against a dense-GUE reference). Central flat window, raw ratio.
Swept W to map the jitter floor sd(W) ~ c/√W — that map *is* the Skewes "what scale is needed" answer.

| W | GUE null mean | null sd (jitter floor) | 95% band |
|---|---|---|---|
| 2,000 | 0.60064 | 0.00544 | [0.5910, 0.6109] |
| 5,000 | 0.59933 | 0.00380 | [0.5923, 0.6056] |
| 10,000 | 0.60036 | 0.00303 | [0.5952, 0.6065] |

(The tridiagonal central-window mean sits ~0.002 below the true Atas 0.60266 — finite-W/edge; it
makes the ζ deviation vs the null ~0.002 larger than vs true GUE, negligible against the effect.)

## The sealed prediction was FALSIFIED — on both counts

I sealed: deviation **~1e-3, below the floor → not resolvable**; and if resolvable, **negative** sign.
Measured: **~+1.2e-2 at γ~5e3, above the floor → resolvable**, and **positive** — ζ ⟨r̃⟩ approaches GUE
**from above**. Wrong by 10× in magnitude and wrong in sign. The data overrode the hypothesis (the
second sealed prediction this session to falsify cleanly — the good outcome).

ζ ⟨r̃⟩ vs height (unfolded by Riemann–von Mangoldt; W=10,000):

| γ_mid | 1/log(γ/2π) | ζ ⟨r̃⟩ | dev vs GUE | inside GUE band? |
|---|---|---|---|---|
| 5.45e3 | 0.148 | 0.6147 | +0.0121 | no |
| 3.68e4 | 0.115 | 0.6109 | +0.0082 | no |
| 1.43e5 | 0.100 | 0.6085 | +0.0058 | no |
| 4.36e5 | 0.090 | 0.6078 | +0.0051 | no |
| 1.13e6 | 0.083 | 0.6031 | +0.0004 | yes |

Monotone decrease toward GUE, consistent across W=2000/5000/10000. The percentile (immunity) test —
assumption-light, no fit — puts every height except the highest **outside** the matched-window GUE
95% band.

## The confound the discipline demanded — RUN and EXCLUDED

The effect is largest at low γ, exactly where (a) the R–vM *asymptotic* density is least accurate and
(b) the window spans the most density variation — so a density-gradient / unfolding artifact would
produce a positive r̃ bias with the **same sign and the same low-γ location** (the solar situation one
level over). Falsifier: recompute ⟨r̃⟩ on each block three ways — R–vM asymptotic unfold, local
empirical `unfold_poly`, and **raw** (no unfold):

| γ_mid | R–vM | unfold_poly | raw |
|---|---|---|---|
| 5.45e3 | 0.61474 | 0.61449 | 0.61474 |
| 3.68e4 | 0.61087 | 0.61134 | 0.61087 |
| 1.43e5 | 0.60846 | 0.60898 | 0.60846 |
| 1.13e6 | 0.60306 | 0.60313 | 0.60306 |

**All three agree to ~4 digits, and raw == unfolded exactly.** That confirms r̃ is intrinsically
unfolding-free here — a smooth density does not bias the adjacent-gap ratio — so the deviation is
**robust to the unfold choice and is NOT an unfolding/density-gradient artifact. Confound excluded;
the crossover is real ζ finite-height behavior.**

## Verdict (in-scope)

**The ARS ⟨r̃⟩ classifier RESOLVES the finite-height approach of ζ spacing statistics to GUE above its
own finite-window noise floor:** ζ ⟨r̃⟩ falls from ~0.615 (γ~5e3) to ~0.603 = GUE (γ~10⁶), from above,
robust to unfolding, exceeding the jitter floor at all but the highest height. That is the calibration
deliverable — the instrument can localize a known crossover, and its resolution here is set by the
floor sd(W) ~ 0.2/√W (≈0.003 at W=10⁴). **§0 anti-claim: this says nothing about RH.**

**Held frame-agnostic (spec open decision #2):** no 1/log law is asserted — the high-γ point falls
faster than linear-in-1/log, so the functional form is not pinned, and the g̃(a,f) surface is **not**
imposed. **Honest scope:** the ζ approach to GUE at finite height is known (Odlyzko / Berry–Keating /
Bogomolny); Phase 1's contribution is that the ARS classifier resolves it above a properly-built
deterministic-noise floor, not a novel ζ claim. **Verification status:** reviewed against reported
numbers, not independently audited; the claim is as good as `phase1_zeta_crossover.py` being faithful
to the deployed ⟨r̃⟩ path (scripts committed + deterministic).

## ⚠ CORRECTION (reviewer) — the unfold falsifier was POWERLESS; the matched-density null is the right test (and vindicates the crossover)

The reviewer caught a real error in the confound-exclusion above. **"raw == unfolded exactly" proves
r̃ is unfold-*invariant* — so the unfold test had *zero power* to detect a density confound**
(unfolding is a no-op on r̃; I ran a falsifier that structurally could not fire). The three-way
agreement was one fact (r̃ ignores unfolding) shown three ways, orthogonal to whether the raw
low-γ density gradient inflates ⟨r̃⟩. And my Dumitriu–Edelman null was built at **uniform** density
(central flat window), **not** matched to the ζ window's gradient — so it could not have caught a
density contribution either. Both true.

The test that *has* power is the **matched-density null** (`phase1_density_check.py`): GUE local
fluctuations placed on the ζ window's R–vM density backbone, then r̃.

| γ_mid | ζ ⟨r̃⟩ | matched-density GUE null | uniform GUE null | ζ − matched |
|---|---|---|---|---|
| 1.42e3 (steep gradient) | 0.6172 | 0.5999 ± 0.0071 | 0.6013 | **+0.0173 (2.4σ)** |
| 1.13e6 (flat control) | 0.5990 | 0.5999 | 0.6013 | −0.001 |

**Imposing the ζ density gradient on GUE does NOT inflate r̃** (matched null 0.600 ≡ uniform null) —
so r̃ ignores the smooth density gradient just as it ignores unfolding; it is a *purely local
adjacent-gap statistic*, invariant to both. And ζ **exceeds the density-matched null by 2.4σ** at
low γ, clean at high γ. **The crossover is vindicated — real finite-height behavior beyond density —
now on the test that had power.** (The earlier "confound excluded via unfold agreement" is corrected
to "excluded via matched-density null"; the unfold agreement excludes only the unfolding artifact,
which is a no-op.)

**Reusable fact banked:** on ζ, r̃ is invariant to *both* unfolding and smooth density gradient
(local statistic) — therefore **unfold tests and uniform-density nulls are both powerless against a
density confound; only a matched-density null can clear it.** This is a property of the statistic,
reusable on every finite-window ⟨r̃⟩ claim.

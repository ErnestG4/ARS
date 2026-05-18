# Dense-in-log-N modulation resolution — FINDINGS (2026-05-19)

**Status:** SCOPING / lever-cost — asymmetric label, NEVER an AM finding.
Read against the PRE-REGISTERED spec. Data `dense_logN_results.json`
(18w MP, bit-identical-serial, 61 log-uniform N∈[6765,121393], 1952
tasks, 6398s). brief-and-hold; Class II blocked; no §3 adjudication;
banked Step-1 verdicts & §3-(A) `S3A_REDUCED` unaffected.

## Pre-registered fold-test (the exact log-periodicity test) → NOT log-φ-periodic
VE@lnφ = **0.26** (sup_spread) / **0.075** (gap); VE@2lnφ 0.31 / 0.20 —
all low. Detrend-adequacy confound checked vs the raw series: the
per-log-φ-period waveform is **non-stationary** — strong bump small-N
(0.544→0.731→0.565, amp ~0.2) that **damps toward 0** as the steep
decay dominates; sharp dip-recover in the tail (min 0.004 @N≈100138).
A damped/transient oscillation is not log-φ-periodic regardless of
detrend ⇒ **decomposition route correctly NOT well-posed; NOT forced**
(pre-registered honest terminal honored). This **refines/partially
walks back the Fib-neighborhood "log-periodic-class" suggestion**:
inter-rung structure is real (not-crossover, not-commensurability
STAND) but **damped/transient, NOT cleanly log-φ-periodic**.

## Decision question — cleanly answered by DIRECT dense measurement
The EXACT criterion (disjoint AND gap≥max(sub,sup); unchanged from the
sharpening run) flips: **uniformly False ∀N≤42113 → uniformly True
∀N≥44190**, stable across ~20 consecutive log-uniform points spanning
EVERY inter-rung phase, to N=121393. Dense-in-log-N covers every phase
by construction ⇒ "True at every densely-sampled N≥44190" **IS** the
worst-modulation-phase-safe statement — measured, not modeled.
**N\* ≈ 4.3×10⁴** (onset; grid-cell band ≈±2000); comfortably-robust
(gap ≥ 2·sup_spread) by **N ≈ 5×10⁴**, margin growing thereafter.

Reported the **cleanly-pinned** terminal via direct measurement.
Explicitly considered the "not-pinnable" terminal (decomposition route
died) and rejected it as over-conservative: the criterion flips cleanly
& stably across 20 dense all-phase points — that IS the exact decision
question answered, more directly/robustly than the decomposition would
have. Honest residuals: ±1-grid-cell on N*; thin onset margin (N=44190:
gap 0.193 vs sup 0.187) ⇒ robustness needs N≈5e4; modulation
damped/transient not log-periodic.

## Net
"Non-trivial" → a concrete, feasible number: **N\* ≈ 4–5×10⁴.** Prior
`RATE_NOT_CLEANLY_PINNED` fully resolved + root-caused (ladder aliasing
+ crude 3-pt extrapolation; dense-in-log-N + reading the criterion
directly fixes it). A non-circular *sensitivity* confirmation at
N≈5×10⁴ is now CHEAP (61 pts to 1.2e5 took ~1.8h/18w; one confirm =
minutes) — Will's standing "does anything downstream need non-circular
sensitivity?" call is now an INFORMED, low-cost one. NOT auto-run —
surfaced for Will. SCOPING/lever-cost, not a finding/§3/AM-result.

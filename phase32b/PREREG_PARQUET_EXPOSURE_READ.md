# Pre-registration — banked-parquet exposure read (32b row set)

**Sealed before the read.** Source: `data/phase24_results/per_session_h1_ars.parquet` (939 rows),
which is *also* the direct input to the §7.ter.50 regression (`per_cell_decomposition.py:303-305`).
Companion to `UNFOLD_LEG2_EXPOSURE_AUDIT.md`. Doctrine: `TOOLKIT.md` §9 Leg 2;
[[gate_certifies_half_say_so]], [[no_forbidden_recompute]].

**This is an exposure audit, not a gate.** Its output is a *count of which rows were touched*.
It is not licensed to move the 32b verdict in either direction, and specifically not toward reprieve.

---

## 1. What the read CAN establish

**(E1) Exposure on the exact 32b analysis rows.** The audit's 58.1% was computed over all 939 rows.
32b regresses on a *subset* (condition-filtered, FA-merged). E1 recomputes stride
(`n_events_in // JPF_CAP`, cap=1500) restricted to the rows that actually entered the §7.ter.50
regression, and reports: n rows, % stride≥2, stride distribution, retained-spacing fraction.
This is a **count over a known row set** — descriptive, assumption-free, unconfoundable.

**(E2) Descriptive distributions** of `rep_med` / `ks_gue_med` per arm, reported *as description*,
carrying the identifiability warning in §2 inline.

**(E3) One structural surprise it could deliver:** if 32b's rows turn out to be ~0% decimated, the
**Mode-2** story for 32b changes (Mode 2 would be a non-issue *for this claim*). It would not touch
Mode 1. See §3.

---

## 2. What the read CANNOT establish — the contrast is UNIDENTIFIABLE, not merely confounded

The decimated arm is *defined* by `n_events_in ≳ 3000` (stride = n//1500 ≥ 2). The arms therefore
have **exactly zero common support in n**: it is a hard threshold, not a correlation. This is a
**positivity violation** — the confounder perfectly predicts treatment assignment. No adjustment,
matching, stratification, or covariate regression can separate a stride effect from an n effect
across that boundary; doing so is pure extrapolation across a discontinuity. Phase 38 already caught
n as a hidden driver once.

Consequence, pre-committed:

> **Neither a positive nor a null between-arm contrast on this table is admissible causal evidence
> about the decimation bug.** Not as inculpation, not as exoneration.

This **demotes my own claim** in `UNFOLD_LEG2_EXPOSURE_AUDIT.md` §4(c), which called the
rep_med/ks_gue_med asymmetry "testable." It is testable — **in the backfill, not in this table.**
I am striking the implication that the banked parquet can test it, *before* seeing whether the split
would have flattered me. (Second claim of mine killed in this audit; the "lower bound" was the first.)

---

## 3. The null-to-reprieve laundering route, named in advance so it is closed

A tempting inference on seeing no rep_med difference across the split: *"the decimation didn't
actually hurt anything — 32b is fine."* **That inference is barred.** Three reasons, at least two of
which the Farey calibrator affirmatively *predicts* a null under full corruption:

- **(a) Saturation — a null is the signature of the cliff, not of safety.** Farey showed corruption
  is a **cliff at stride 2** (115% of the correlation gap destroyed), pulling the consecutive-pair
  statistic **to and past its iid value**. Mode 1 (`sp / sp.mean()`, line 48) is **unconditional** —
  it fires on 100% of rows, including the un-decimated arm. If both arms are already sitting at the
  same iid attractor, **the contrast is zero precisely because everything is corrupted.**
- **(b) Masking.** n moves both the axis and the arm; an opposing n-gradient can cancel a real stride
  effect. Unfixable here (§2, no common support).
- **(c) Wrong contrast geometry.** The Farey effect is **within-unit** (same data, decimated vs not).
  A **between-cell** comparison pits it against between-cell variance in rep_med, which may dwarf it.
  Absence of a between-cell shift does not imply absence of a within-cell bias.

**Standing rule for this read:** a null result is reported as **UNINFORMATIVE**, never as
`NO_EFFECT`, and never in a sentence that also contains the word "reprieve," "spared," or "clean."

---

## 4. What is unmoved by *any* outcome of this read

**Mode 1 is unconditional.** `ars_classify.py:48` divides spacings by a mean **self-derived from the
data being classified**, on **100% of cells, at every n, at every stride.** `rep_med` and
`ks_gue_med` therefore **fail Leg 2 at the call site** — a fact already CONFIRMED by code read, and
one that no row-count can undo. Even an E1 result of **0% decimated** leaves 32b Leg-2-failing.

Only the **§8 backfill** — within-cell recompute, decimation **off** AND normalizer fixed (external
rate, not `sp.mean()`), same cells — can move the verdict. Nothing read from this table substitutes
for it. This read **cannot shorten that queue**; at most it re-prices its urgency.

## 5. Committed output vocabulary

- E1 → a number, reported plainly (e.g. "X/Y of 32b's rows decimated, median stride S").
- Any between-arm number → tagged `DESCRIPTIVE / UNIDENTIFIABLE` at the point of use.
- Verdict on 32b → **unchanged: Leg-2-failing, magnitude bounded below, backfill still required.**

---
---

# OUTCOME (written after the read; pre-registration above unedited)

## E1 — exposure on the 465 rows that entered §7.ter.50

| | |
|---|---|
| rows in the 32b regression | **465** (`drifting_pooled` ∩ H1 ∩ 6 sessions) |
| if-guard fires (nsp > 1500) | 354 (76.1%) — 68 are stride-1 no-ops |
| **genuinely decimated (stride ≥ 2)** | **286 / 465 = 61.5%** |
| stride | median **5**, mean 7.1, **max 48**; 57 rows (12.3%) at stride ≥ 10 |
| decimated cell retains | median **20%** of spacings; worst **2.1%** |

**Exposure on 32b's own rows is WORSE than the 58.1% all-rows headline: 61.5%.** The all-939 number
under-reports the claim-bearing subset. §7.ter.50's retro-scope must quote **61.5%**, not 58.1%.

## E2 — the positivity violation, now measured rather than argued

| arm | `n_events_in` range |
|---|---|
| undecimated (n=179) | [407, **2981**] |
| decimated (n=286) | [**3073**, 72985] |

**Zero common support.** A hard gap at the cap boundary, exactly as pre-registered §2. The
between-arm contrast is **UNIDENTIFIABLE**, not merely confounded. Both arms' numbers are recorded
as `DESCRIPTIVE` and carry no causal weight in either direction.

## The pre-registered null-laundering branch FIRED — and §3(a) was mechanically right

Observed: `rep_med` median **0.0000** (undecimated) vs **0.0002** (decimated), Δ = +0.0002 — a flat
null. Under the barred inference this reads "decimation didn't hurt rep_med." **It is barred, and
the estimator read shows why it is not merely barred but actively wrong:**

**`arithmetic_toolkit.py:507` — `I_rep = trapezoid(np.maximum(0, 1 - R2), r)`.** The integrand is
**clipped at zero**. So:

- `I_rep` is **one-sided censored**; it can never go negative. The docstring two lines up
  (line 494: *"negative → clustering"*) is **false of the implementation** — that branch is
  unreachable.
- **The floor sits exactly at the Poisson/iid value** (R₂ ≡ 1 ⟹ integrand ≡ 0 ⟹ `I_rep` = 0).
- Farey (VERDICT (i)) showed decimation drives the consecutive-pair statistic **to and past its iid
  value**. "Past" is precisely the region `I_rep` **cannot represent**.

⇒ **The corruption's signature on `rep_med` is pushed into the censored region and disappears.** The
flat null is not evidence of no harm; it is the *predicted appearance* of maximal harm against a
floor. Pre-reg §3(a) ("a null is the signature of the cliff, not of safety") is upgraded from *a
possible explanation* to *a mechanically forced one*.

**And the axis is sitting on that floor:** `rep_med` is **exactly 0.0 for 293/465 = 63.0%** of the
rows entering §7.ter.50 (83.8% of the undecimated arm, 50.0% of the decimated arm). This is a
**marginal** fact — not a between-arm contrast — so it is untouched by the positivity violation.

Note the arm-wise zero-rates run *opposite* to a naive "decimation manufactures zeros" story. That
does **not** rescue anything: per §2 the arms cannot be compared, and per §3(b) the n-gradient and
any stride effect push against each other with no way to separate them. The correct reading is the
pre-committed one: **UNINFORMATIVE.**

## Two consequences (one new, one load-bearing)

**(N1) NEW, independent of the unfold bug — `rep_med` is a censored axis, 63% railed.**
§7.ter.50 classifies `rep_med` as ORTHOGONAL using a regression on a predictor that is a **point mass
at its floor for nearly two-thirds of its rows**, and that floor is *the null value it is supposed to
discriminate against*. Poisson and clustering are **mapped to the same number**. This is the same
failure class as [[soc_pair_complete]] ("one-sided fitters blind to super-Poisson") and
[[instrument_confound_thinning_asymmetry]] ("railed axes indeterminate"). It requires its own audit
line — it is **not** downstream of Leg 2.

**(N2) The §8 backfill spec is INSUFFICIENT AS WRITTEN.** It currently says: re-run with decimation
off AND the normalizer fixed. **That is not enough.** With the clip still in place, the recompute
lands on the same floor for a majority of cells and returns another uninterpretable "no change."
**Added mandatory item: the backfill must bank the UNCLIPPED, signed integral** `∫₀¹(1 − R₂) dr`
(drop `np.maximum(0, ·)`), so the clustering half-line is representable and the bias actually has
somewhere to show up. Without this the backfill cannot measure the thing it exists to measure.

## Verdict — unchanged, as pre-committed

**32b remains Leg-2-failing at the call site.** Mode 1 (`sp / sp.mean()`, unconditional, 100% of
cells) is untouched by every number above. No reprieve. The read did what it was licensed to do —
count exposure (**61.5%**) — and it delivered no gate, in either direction.

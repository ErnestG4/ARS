# ⚠ `gate0e_precision_measured.json` — which of its numbers survive orbit dedup

**Re-run 2026-07-28 (R-172).** `gate0e_precision.py` pooled one object per **polynomial**;
`collect_cyclic` enumerates a coefficient box and dedups by nothing, so several polynomials per
stratum are **GL₂(ℤ) translates of the same cubic irrational** (R-165). Deduped counts: |t|=5 8→2,
|t|=13 6→3, |t|=17 6→3, |t|=29 4→2.

Both files are retained. `gate0e_precision_measured.json` is **bit-identical** to the banked version
(verified by re-running the default path and diffing); `gate0e_precision_dedup_measured.json` is the
corrected read. Reproduce either with:

```
                       $HOME/fmexplorer/bin/python3 arsrh/cubic/gate0e_precision.py   # deployed
GATE0E_DEDUP=1         $HOME/fmexplorer/bin/python3 arsrh/cubic/gate0e_precision.py   # deduped
```

---

## RETRACTED — the "EXCESS over binomial" verdicts were duplication

`z = (K − N·pred)/sd` scales as **√k** under k-fold duplication, so `χ² = Σz²` scales as **k**.

| block | χ² (dup) | χ² (dedup) | χ²/df | p (dup) | p (dedup) | verdict |
|---|---|---|---|---|---|---|
| `by_a` | 38.2 | **21.6** | 1.82 → **1.03** | 1.2e−02 | **0.42** | RETRACTED |
| `by_lambda` | 40.9 | **22.4** | 1.95 → **1.07** | 5.8e−03 | **0.38** | RETRACTED |
| **`by_conditional_g`** | **55.3** | **25.1** | 2.63 → **1.19** | **6.4e−05** | **0.24** | **RETRACTED** |
| `both_corrections` | 36.4 | **20.2** | 3.31 → **1.83** | 1.5e−04 | **0.043** | weakened, still <0.05 |

**Three of the four "EXCESS over binomial" readings become "consistent with binomial."** The
headline one — `by_conditional_g` at p = 6.4e−05 — becomes **p = 0.24**. Degrees of freedom are
unchanged (21→21, 11→11): dedup removes duplicate polynomials *within* strata, never a whole stratum.

## UNCHANGED — everything ratio-shaped, exactly as predicted

Duplication scales numerator and denominator together, so these are invariant by construction. The
prediction was made **before** the re-run and is confirmed to ~1%:

| block | bias (dup → dedup) | rms | precision % |
|---|---|---|---|
| `by_a` | +0.0817 → +0.0819 | 0.2272 → 0.2252 | 25.5 → 25.3 |
| `by_lambda` | +0.0797 → +0.0781 | 0.2357 → 0.2324 | 26.6 → 26.2 |
| `by_conditional_g` | +0.0130 → +0.0178 | 0.0877 → 0.0868 | 9.2 → 9.1 |
| `both_corrections` | −0.0203 → −0.0163 | 0.1114 → 0.1107 | 11.8 → 11.7 |

**The sealed ±12% band stands.**

## SURVIVES — and this is the part that matters scientifically

The **trend on log|det|** is *not* an artifact:

| block | slope (dup) | slope (dedup) |
|---|---|---|
| `by_conditional_g` | −0.0399 ± 0.0112 (**3.56 sem**) | −0.0378 ± 0.0111 (**3.40 sem**) |
| `both_corrections` | −0.0509 ± 0.0224 (2.27 sem) | −0.0519 ± 0.0223 (2.33 sem) |

The slope is a regression across **strata**, and its sem comes from residual scatter over the 21
rows rather than from within-stratum counts — so duplication cannot touch it.

> **The dispersion verdict was an artifact; the systematic is real.** The formula degrading with
> |det| is what keeps R-077's grade at **CALIBRATED rather than DERIVED**, and that finding is
> untouched. What is retracted is only the claim that the residual scatter *exceeds binomial*.

## `gate0f_frame_measured.json` needs NO re-run

Checked rather than assumed: gate0f computes **no pooled z or χ²**. Its outputs are censuses over
coefficient boxes (`frame`, `t_values_monic_box26`) plus single-object facts, and it calls
`collect_cyclic` once to take **one** object (`by[43][:1]`). Nothing in it pools across duplicated
orbits. One *claim* in it is corrected in place — see below.

**The corrected claim:** gate0f reported the witness count as **distinct discriminants**. That is the
wrong unit and it **undercounts**: |t|=5 has **1 discriminant but 2 GL₂(ℤ) orbits**, |t|=13 has
**1 discriminant but 3**. The right unit is the GL₂(ℤ) orbit; discriminant count is a lower bound and
polynomial count an upper one.

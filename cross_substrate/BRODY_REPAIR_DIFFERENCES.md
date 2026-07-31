# `I8_brody_q_unbounded` changes THREE things, not one — and what each is worth

Measured 2026-07-31 during the Tier B propagation. Raised by an adversarial
synthetic-validation pass, then quantified on real data before being believed.

## The three differences

`cross_substrate/axes.py`:

| | deployed `I8_brody_q` (:149) | repaired `I8_brody_q_unbounded` (:165) |
|---|---|---|
| fit bounds | `(0.0, 1.0)` | `(-1.0, 4.0)` |
| outlier filter | `s[(s > 0) & (s < 10.0)]` | `s[s > 0]` — **cut dropped** |
| minimum n | `MIN_N_FIT` = **50** | `MIN_N_NNS` = **20** |

Only the first is the intended repair. The docstring describes only the first.
The dropped `s < 10` cut is recorded in `arsrh/LOOK_REGISTER.md:2538` as
"already bundled", quantified there on **one** substrate (qpo: −0.4872 with the
cut vs −0.4976 without). It was not silent, but it was also not measured
anywhere the headline neural numbers are read.

## Why it matters

The mechanism is real and sharp. On synthetic spectra a **single** spacing at
200× the mean turns a perfect GOE sample (true q = +1) into q ≈ −0.13, and 0.2%
contamination does the same; replicate scatter stays 0.02–0.04, so the wrong
answer arrives looking *confident*. Left unmeasured, "87.6% of cells are
clustered" could have been "a few long gaps per cell".

## What it is actually worth — measured on 1,141 real IBL cells

Refit of the same spacings a third way (bounds opened, `s < 10` **retained**),
`/tmp/brody_cut_diagnostic.py`:

```
cells having >=1 spacing s>10 : 1065 (93.3%)   total outlier spacings: 120,561
median q  repaired (no cut)   : -0.1708
median q  repaired (s<10)     : -0.1544        median shift  +0.0067
negative fraction  no cut     : 87.6%
negative fraction  s<10       : 86.5%
sign flips (neg -> non-neg)   : 13 cells (1.1%)
```

Exposure is high (93.3% of cells contain at least one outlier spacing) but
**leverage is low**: the median shifts by +0.007 and 1.1% of sign calls flip.
The reason is n — IBL cells carry thousands of spacings, so a handful of long
gaps cannot dominate the likelihood. The synthetic demonstration used a fixed
small n, where the same contamination *fraction* has far more leverage.

The `MIN_N_FIT` 50 → 20 change affected **zero** IBL cells: the reproduction
gate found 1,139 cells with both fits non-null and 2 with both null, i.e. no
cell gained a value purely from the lowered n gate.

## Status

- **The IBL clustering direction survives**: 86.5% negative with the outlier
  filter retained. The conclusion is not an artifact of the dropped cut.
- **The magnitude is not a clustering scale.** Independently established in the
  same validation pass: Brody is KS-rejected for every non-Brody clustered
  process tested (Hawkes, 2-exp mixtures, gamma, lognormal, pooled rhythmic),
  and processes with identical CV returned q̂ from +0.04 to −0.32 — one
  genuinely over-dispersed lognormal (CV 1.213) returned **positive** q̂.
  So q ≈ 0 is not evidence of Poisson, and ranking cells by q̂ does not rank
  them by clustering. Read the sign, not the value.
- **The estimator itself is sound.** Against ground-truth inverse-CDF Brody
  samples the repaired fitter is unbiased across q ∈ [−0.8, +3.0] (bias ≤ 0.03,
  → 0 with n), and negative-q Brody is a proper density for all q > −1 (Weibull,
  shape k = q+1 < 1), not an out-of-domain extrapolation. `lo = -1.0` is the
  true singular boundary; `hi = 4.0` is arbitrary and **can rail** — anything
  with spacing CV ≲ 0.29 pins near 3.99996.
- **Not yet measured on the other substrates.** The dual_region, buzsaki and
  hc3 exposure to the dropped cut is unquantified; only IBL has been refit.

## If this is revisited

Retaining `s < 10` in the repaired fitter would make it a one-change repair and
remove the confound at its source. That is a change to a deployed axis and is
Will's call, not one to make mid-propagation — every value banked this session
used the as-written fitter, and mixing two definitions across substrates would
be worse than the confound.

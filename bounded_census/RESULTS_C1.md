# C1 — bounded-solver census: results against the sealed classification

Classification was committed **before** these numbers were read
(`CLASSIFICATION_SEALED.md`, its own commit). Commit order is the evidence.

| site | sealed class | n | near lo | near hi | TRUE rail? | sealed prediction | met? |
|---|---|---|---|---|---|---|---|
| `brody_q` | CONVENTION | 20,558 | **73.8%** | 1.7% | **YES (lo)** | substantial rail | **✓** |
| `brody_q_unbounded` | CONVENTION (wider) | 20,725 | 0.0% | 0.2% | no | little/none | **✓** |
| `berry_robnik_rho` | MATHEMATICAL | 20,290 | 36.1% | 0.2% | **NO** | rare, and real answers | **✓** |
| `alpha` (DPP) | MIXED, lower CONVENTION | 558 | 0.0% | — | no | only if non-repulsive data | **✓** |
| `kappa` (Thomas) | CONVENTION both ends | 17 | 0.0% | 11.8% | no (n=17) | only if non-clustered data | **✓** |

**Scoreboard, stated with its provenance: 4/5 clean, 1 resolved via a corrected measurement under a
discriminator adopted AFTER apparent falsification.** Same number of true predictions; honest lineage
on the fifth. The distance-only pass put ρ at 36.1% "railed" and appeared to falsify its sealed
`MATHEMATICAL` call; the distinct-ratio rule was then introduced and resolved the contradiction **in
the seal's favour**. The sealing did its job — it forced the contradiction into the open rather than
letting the classification drift — **but the resolution rule was chosen after seeing the result it
resolves.** That is a rationalisation surface one level up, and "almost certainly correct" does not
exempt it.

## A rail is a PILEUP, not a PROXIMITY

The first pass measured Berry–Robnik ρ at **36.1% "railed" at 0** and appeared to falsify the sealed
`MATHEMATICAL / rails-are-rare` classification. It did not. Checking the **distinct-value ratio**
among near-bound values:

| parameter | n near 0 | distinct | ratio | reading |
|---|---|---|---|---|
| `brody_q` | 15,174 | **4** | **0.0003** | **TRUE RAIL** — an optimizer floor emits one number |
| `berry_robnik_rho` | 7,328 | **7,319** | **0.9988** | **CONCENTRATION** — real distinct measurements |

**Distance alone conflates "pinned at the optimizer's floor" with "genuinely small."** ρ is a fraction
of phase space; a strongly chaotic system legitimately reports ρ near 0, and 7,319 distinct such
values are 7,319 measurements, not one artifact repeated. The sealed classification was right and my
first measurement was wrong — which is the ordering working as intended, since the classification
could not be retrofitted to the number.

**New criterion, now in the generator:** a bound counts as railed only if values are near it **and**
the distinct-value ratio among them is **< 1%** — *and* the near-bound sample is at least **1/ratio =
100**, below which the test cannot fire at all.

### Red-path of the post-hoc rule (required, because it was adopted post-contradiction)

Applied to **every** classified site, asking whether it moves any verdict other than ρ's:

| site @ bound | near | distinct | ratio | distance-only | discriminator | changed |
|---|---|---|---|---|---|---|
| `brody_q` @ 0 | 15,174 | 4 | 0.0003 | rail | **rail** | no |
| `brody_q` @ 1 | 352 | 11 | 0.0312 | no | no | no |
| `brody_q_unbounded` @ 4 | 34 | 3 | 0.0882 | no | INDETERMINATE (n<100) | no |
| **`berry_robnik` @ 0** | 7,328 | 7,319 | 0.9988 | rail | **not a rail** | **YES** |
| `berry_robnik` @ 1 | 33 | 2 | 0.0606 | no | INDETERMINATE (n<100) | no |
| `kappa` @ 100 | 2 | 2 | 1.0000 | rail | INDETERMINATE (n<100) | no |

**The first red-path FAILED**, and usefully: `kappa@hi` also flipped. Diagnosis — it has **n=2**, and a
2-sample distinct-ratio cannot discriminate a pileup from a concentration in either direction. That
exposed a real defect in the rule rather than in the census: **below n = 1/RAIL_RATIO = 100 the ratio
can never fall under the threshold, so the arm cannot fire and was being scored as a verdict** — the
non-inertness rule, applied to my own discriminator. The minimum-n guard is *derived from the
threshold*, not chosen to make the test pass.

**With the guard: `DISCRIMINATOR_SCOPED`** — it moves only the ρ verdict it was adopted to resolve.
It was not tuned into existence at the cost of the rest of the census.

## DPP / Thomas — the latent one-sided reporting gap

`alpha` 0.0% at its lower bound (min 0.022, **22×** it) and `kappa` 0.0% at its lower bound (min 1.2,
**12,000×** it). The one-sided boundary *reporting* defect in `fit_dpp` (checks the upper bound only)
and `fit_thomas` (checks neither) is **real and unexercised** — worth fixing as cheap and latent, not
because it is producing wrong numbers. `kappa` shows 11.8% near its **upper** bound of 100.0, but that
is **2 of 17** — reported with its denominator rather than as a rate.

## Coverage — a LOWER BOUND

Key-pattern matching flags **251** banked keys these names would miss. The largest, **`rho1`
(1,439 values)**, was checked and **excluded by measurement**: it ranges −0.79…0.59, so it is a
correlation coefficient, not a bounded fit. **The other 250 are unchecked.** This census does not
claim exhaustive coverage.

## Out of scope, as briefed

No bound was moved.

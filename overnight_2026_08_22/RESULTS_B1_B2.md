# B1 / B2 — results, scored against criteria sealed at `82e408e`

## B1 — the per-class ordering SURVIVES

**The finding is the ORDERING. ρ is its test statistic, not the headline.**

> **Perfect monotone ordering across all five metallic classes, sealed prediction met at ρ ≤ −0.60.**

| class | max CF quotient | median unbounded q (full population) |
|---|---|---|
| golden | 1 | **+1.2472** |
| silver | 2 | +1.0535 |
| bronze | 3 | +1.0450 |
| metallic4 | 4 | +0.7739 |
| metallic5 | 5 | **+0.6407** |

ρ(maxq, median q) = **−1.000**, 95% CI [−1.000, −0.800]. **Read this correctly:** it is a rank test on
**five** medians that came out perfectly ordered — under randomness that is 1/120, real evidence, but
**not** a continuous-data correlation of implausible strength. Quoting "−1.000" alone invites exactly
that misreading, which is why the ordering headlines and ρ is reported as the test.

**Complementary number, for the scatter the ordering lives above:** at the **cell** level, all 255 α
with D_Q continuous against unbounded q, **ρ = +0.658**. So the class-median test establishes the
*ordering*; the cell-level ρ says how much scatter individual α show around it. Secondary 9-class
version (4 classes tie at maxq = 99), reported not scored: ρ = −0.670 [−0.757, −0.444].

## B2 — the reversal DOES NOT survive, and leaves one real fact behind

Split on **terciles of the predictor** D_Q (never the outcome): ρ within the top-D_Q tercile =
**+0.362, CI [+0.132, +0.565]**, n = 85. Positive, excluding zero in the wrong direction. The −0.209
subgroup result was a range-restriction artifact of selecting on q. **Retired.**

**BANKED SEPARATELY, because it would otherwise be lost inside a negative result:**

> **ATTENUATION WITHOUT REVERSAL.** The D_Q–rigidity relation **weakens substantially toward the rigid
> end** — **ρ = 0.362 in the top-D_Q tercile against 0.658 overall, roughly halved — direction
> preserved.**

**Open, noted and not pursued:** whether the attenuation is **substantive** (the relation genuinely
saturates as approximability runs out) or **instrumental** (less dynamic range in q up there). That is
answerable later; the measured gradient does not wait on it.

## Provenance

Criteria (`82e408e`) → generator → output, each in its own commit, **machine-confirmed by
`verify_seal_order.py`** rather than asserted. First result in this arc whose provenance needs no
narrative.

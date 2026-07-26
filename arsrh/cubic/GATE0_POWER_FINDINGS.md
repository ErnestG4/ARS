# Gate 0e–0h — the arm's own numbers, the sampling frame, and the two-axis power floor

**Status:** the four items owed before the seals, **delivered**. `gate0e_precision.py`,
`gate0f_frame.py`, `gate0g_marginals.py`, `gate0h_injection.py` (+ `*_measured.json`).
**No pair of stratum-A objects was ever brought together.** Gate 0g measures marginals only; gate 0h
is entirely synthetic.

---

## 1 — The rate formula, quoted at the precision it has (gate 0e)

The defect: "ratio 1.00, 1.00, 0.99, 1.35" reads as validation with a footnote, and the worst value sat
at the largest |det| — i.e. accuracy degrading in the direction the licensing sentence pointed.
Pooling more objects and separating the three questions:

| version | precision (1 sd) | χ²/df | trend on log\|det\| |
|---|---|---|---|
| marginal P(g), events by `a` | ±26% | 1.82 | 0.75 sem |
| marginal P(g), events by λ | ±27% | 1.95 | 0.77 sem |
| **P(g \| event), events by λ** | **±12%** | 3.31 | 2.27 sem |

**Two causes found, both mine, both in the derivation rather than the data.**

1. **P(g | event) ≠ P(g)** — an assumption I never stated. The g = t branch has factor t²/t² = 1 and
   transfers everything, and events are *enriched* in it: at |t|=13, P(g=13) = 0.0674 overall but
   **0.1077 among events**; at |t|=29, 0.0365 → **0.0750**. Those were exactly the two anomalous strata.
   The conditional histogram is a **within-object** quantity — it needs α₁'s CF and M, no partner — so
   it is free at design time.
2. **The event definition.** λ = a + δ with δ ∈ [0,2), so `a ≥ A` and `λ ≥ A` disagree at order 2/A. The
   four misses at |t|=17 were **one event seen in four polynomials**: λ = 20.534 → λ′ = 20.534 exactly,
   but a = 20 on one side and 19 on the other.

**And my error bar was wrong in both directions.** The per-event success probability is *heterogeneous*
(p = 1 on the g = t branch, 1/Δ on g = 1), so the variance is Σ_g n_g p_g(1−p_g), not N·p̄(1−p̄) — the
pooled form overstates it and deflates χ². Corrected, the p = 1 branches have *zero* model variance, so
a single miss gives an unbounded z; the pooled z is not usable there either. **Per-branch validation is
the only honest form**, and it is clean: every g < t branch agrees (p = 0.06–1.00, no pattern).

**What is licensed.** After both corrections, every stratum agrees except |t| = 43 — whose deciding
branch holds **2 events on 1 field** (g=43: n=2, k=1). So:

> The apparent large-|det| systematic is an **empty calibration set, not a trend**. The formula is
> verified over |det| = 1…289 at ±12%; **above |det| ≈ 300 the coefficient box supplies one field and a
> handful of events, so the formula there is UNCALIBRATED — not contradicted, uncalibrated.**
> "Sizes any |det| without running" is withdrawn and replaced by that sentence.

**The structurally interesting part stands:** the rate does not fall like 1/|Δ| because the g = |Δ|
branch caps at 1 and sets the floor.

## 2 — The census is a property of the enumeration (gate 0f)

The frame was **monic x³+Ax²+Bx+C, |A|,|B|,|C| ≤ 12, irreducible, disc > 0**. Varying it:

| box N | totally real irred. | cyclic | fraction | distinct discs |
|---|---|---|---|---|
| 6 | 484 | 36 | 7.438% | 6 |
| 12 | 5388 | 162 | **3.007%** | 29 |
| 24 | 51436 | 486 | 0.945% | 83 |
| 40 | 258382 | 1196 | 0.463% | 184 |

**Measured log-log exponent −1.46** (I predicted −2; quote the measurement). The fraction *falls* as the
box grows, and by Davenport–Heilbronn vs the cyclic count, **cyclic cubic fields have density zero**
among cubic fields. So "97% of cubics are S₃" would be a slot error; the correct sentence names the box.

**And the witness count is far below the object count**: at N = 40, **184 distinct discriminants back
1196 polynomials**. This bit gate 0e directly — its 8-objects-per-stratum pooling was mostly **one
field counted eight times**, which is how the four |t|=17 "misses" turned out to be one event.

## 3 — |t| ≡ 0 mod 3: a sampling artifact, not a theorem (gate 0f)

**Realizable as a Möbius map:** M = (0,1;−9,3) has t = 3, det 9 = t², and M³ = −27·I (verified) — order 3
in PGL₂(Q). **Realizable as a cubic:** yes — the monic search at N = 26 finds **|t| ∈ {3, 9, 15}**. The
N = 12 census simply did not reach one. My hypothesis that integrality excludes 3 | t is **falsified**.

**A second construction makes the reason structural.** The orbit invariant for that M gives
27x³ − 27sx² − 9(1−s)x + 1; at s = 0 that is 27x³ − 9x + 1, whose roots are **α/3 for α a root of
y³ − 3y + 1** — the Shanks a = 0 cubic, t = 1. So the **same field carries t = 1 on its algebraic
integers and t = 3 on their thirds.** |t| is *not* a field invariant, exactly as expected from it being
a GL₂(ℤ)-invariant of the **object**: x ↦ x/3 is not in GL₂(ℤ).

## 4 — Does the floor transfer from cyclic to S₃? (gate 0g) — YES, and the check was powered

The floor depends on **events per unit u** = P(λ≥A) / Lévy, and nothing else. 24 objects per stratum,
**distinct discriminants**, events at λ ≥ 20:

| anchor | theory | A: S₃ | B: \|t\|=1 | C: \|t\|>1 |
|---|---|---|---|---|
| Lévy | 1.18657 | 1.19491 ± 0.00675 | 1.18361 ± 0.00605 | 1.18629 ± 0.00694 |
| P(λ≥20) | 0.07039 | 0.07325 ± 0.00173 | 0.07081 ± 0.00146 | 0.07159 ± 0.00159 |
| **ev / unit u** | 0.05932 | **0.06119 ± 0.00113** | 0.05976 ± 0.00103 | 0.06023 ± 0.00103 |
| Khinchin | 2.68545 | 2.71682 ± 0.02169 | 2.68221 ± 0.02016 | 2.68910 ± 0.02295 |

**Worst |z| across all anchors and all stratum pairs: 1.25.** On the anchor that matters, A vs B is
**+0.94** and A vs C **+0.63** sem. The sem is **1.8% of the value**, so the test could have caught a
**4% difference** — this is a floor/ceiling-clean check, not an underpowered pass.

**TRANSFER LICENSED.** *Not* claimed: that the strata are identical in every respect. Only that the one
quantity a coincidence floor depends on agrees to 0.9 sem at 4% sensitivity.

*(Note: all four A-vs-theory z's are positive, +1.24 to +1.66 — a small common excess in stratum A
against theory. Since the strata agree with **each other**, it does not affect the transfer; it looks
like a shared finite-n estimator bias and is not chased here.)*

## 5 — The injection arm: axis 2 (gate 0h)

Synthetic Gauss–Kuzmin processes, calibrated to gate 0g's anchors (0.0602 events/unit u vs measured
0.06119 ± 0.00113). Inject a fraction **f** of one object's events into the partner at a fixed lag plus
**Uniform(−J, J)** jitter; detect with

> S(w) = max over lag L of #{(i,j) : |u_i − v_j − L| ≤ w}, computed exactly by sliding a 2w window over
> the sorted pairwise-difference multiset (the candidate lags *are* the differences).
> Null: permutation over object pairings.

**The single-w floor is post-hoc** — choosing w with hindsight is a look-elsewhere the floor does not
pay for. The **sealable** statistic fixes the ladder in advance: T = min over a pre-registered w-ladder
of the null-tail probability of S(w), with T's own null from the same permutation. Its 5% threshold is
**T ≤ 0.0368** rather than 0.05 — that gap *is* the multiplicity cost.

**DETECTION FLOOR (80% power, w-ladder scanned and paid for):**

| | J = 0 | J = 0.05 | J = 0.2 | J = 1.0 |
|---|---|---|---|---|
| **f_min** | **0.05** | **0.10** | **0.10** | **0.20** |

Identical to the post-hoc row at this grid resolution, so the multiplicity cost is **smaller than one
step of the f-grid** — not zero, smaller than resolved.

**Where the ladder arm sits on this grid: the J = 0 column, and only that column** — at
f = 1.00, 0.48, 0.21, 0.12, 0.08 for |det| = 1, 4, 25, 169, 841. Everything to the right is reachable
only by injection. That is why axis 2 could not be earned from real data, and it is now earned.

## 6 — What is now discharged, and what is not

- **§5's margin requirement: DISCHARGEABLE.** The floor is stated jointly on both axes, the transfer to
  stratum A is licensed on the anchor it depends on, and the detector is multiplicity-corrected.
- **Still open:** the formula is uncalibrated above |det| ≈ 300 (§1); whether 3 | t has any structural
  meaning (§3 says no exclusion, nothing more); the small common A-vs-theory offset in §4.
- **Not addressed here and still owed:** the seals themselves — A, the coordinate, the statistic, the
  w-ladder, and the permutation count all need to be fixed in writing before any arm runs.

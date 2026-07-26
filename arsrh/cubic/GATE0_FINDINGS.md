# GATE 0 — the (∛m, ∛m²) ladder is FULLY DERIVABLE

**Status:** BLOCKING gate, **RESOLVED**. Branch 1 of §2 ("ladder is fully derivable → it is a theorem,
and measuring it is a calibrator, not a finding").
**Grade:** derivation is `SESSION` and self-contained — no `LIT` input, verified end-to-end against each
object's own continued fraction. The *mapping to the literature sentence* is separately graded and is
**not** resolved (see §5).
**Script:** `gate0_ladder.py` → `gate0_ladder_measured.json`. Run with `/home/combust/fmexplorer/bin/python3`.
**No arm was run. No seal was written. Nothing here is a measurement of a cubic family.**

---

## 1 — The transfer law

α = ∛m, β = ∛m² = m/α. For a convergent p/q of α (gcd(p,q)=1), the induced approximation to β is
mq/p. Since gcd(q,p)=1, **gcd(mq,p) = gcd(m,p) =: g**, so in lowest terms

    P/Q = (mq/g)/(p/g),        Q = p/g.

Exactly: β − mq/p = m(p − qα)/(αp). Writing λ(P/Q) := 1/(Q²·|x − P/Q|) for the *implied partial
quotient* of any fraction (for a convergent this is x_{n+1} + q_{n−1}/q_n ∈ [a_{n+1}, a_{n+1}+2)):

> **λ′ = (g²/m)·λ·(αq/p),  αq/p = 1 + 1/(αλq²)**
>
> i.e. **λ′ = (g²/m)·λ, g = gcd(m,p)**, exact to relative O(q⁻²)
> and **log Q = log q + (1/3)log m − log g** — a **deterministic translation** on the log-denominator line.

**Involution:** the map sends g → m/g, so the factor composes as (m/g)²/m · g²/m = 1. Self-inverse.
Verified: 399/399 round trips return the original convergent (m=6).

## 2 — Measured, against each object's own CF (not against the algebra)

Certified CFs of ∛m and ∛m² computed by interval (both endpoints of a 10⁻ᴰ bracket, common prefix
minus two terms). λ′ predicted from α's convergent, compared to the value read off **β's own continued
fraction** at the matching denominator.

| m | induced frac. is a β-convergent | max &#124;meas/pred − 1&#124; | median | max &#124;location err&#124; |
|---|---|---|---|---|
| 2 | 66.2% | 5.5e−02 | 0 | 5.7e−02 |
| 3 | 50.3% | 4.0e−05 | 0 | 3.9e−02 |
| 5 | 31.7% | 2.6e−02 | 0 | — |
| 7 | 26.8% | 4.4e−02 | 0 | 4.5e−02 |
| 10 | 32.7% | 2.7e−04 | 0 | 5.7e−03 |
| 12 | 42.8% | 1.6e−03 | 0 | 1.9e−02 |

**The residual is the derived term, not slop.** Measured relative error vs the predicted 1/(αλq²), at
matched n: ratio **1.008, 1.000, 1.000, 1.000, …** falling to the double-precision floor by log q ≈ 30.
There is no height-independent component. The law is exact.

**Per-gcd branch** (m=12): g = 1, 2, 3, 4, 6, 12 → factor 0.083, 0.333, 0.750, 1.333, 3.000, 12.000, each
with max relative error 4e−16 … 2e−03. The gcd branch is not a nuisance — it is the law.

## 3 — The three questions §2 asked

1. **Exact transfer law** — derived and verified above.
2. **Does it reproduce "roughly half," and does the factor depend on m?** The factor is **g²/m**.
   "Roughly half" is the **m = 2, g = 1 case and only that case**. Verified on the canonical instance:
   ∛2 has a_{n+1} = **534**, and the corresponding ∛4 partial quotient is **266** (predicted λ′ = 267.376,
   measured 267.376). For m = 3, 5, 7, 12 the g=1 factor is 1/3, 1/5, 1/7, 1/12 — measured, not asserted.
   **The relation is also direction-asymmetric:** α→β at g=1 gives λ/2, and β→α gives 2λ. There is no
   symmetric "half" reading.
3. **Does gcd(mq,p) > 1 matter?** **Yes, decisively** — it is the whole second half of the law. For m=2,
   **33.1%** of convergents have p even, and those map with factor **2**, not 1/2. A ladder stated as
   "roughly half" is wrong on a third of the events, by a factor of four.

**This closes the discrepancy §2 flagged as unresolved.** The factor involving m is correct; 1/2 is the
m=2 specialisation; and the reduction step matters exactly as suspected.

## 4 — The generalisation (this is the part that reframes the phase)

The reason the ladder exists is **not** that β is algebraically related to α. It is that
β = m/α is a **fractional-linear map of α over Q**. Testing three maps on α = ∛2:

| map | degree | λ at n = 5, 10, 20, 40, 80 |
|---|---|---|
| x ↦ x² | 2 | 8.0e−04, 2.7e−07, 1.2e−19, 9.0e−41, 7.0e−91 |
| x ↦ x²+x+1 | 2 | 5.8e−04, 1.9e−07, 8.3e−20, 6.4e−41, 5.0e−91 |
| x ↦ (3x+1)/(x+2) | 1 | 1.013, 79.04, 8.740, 24.45, 0.2564 |

λ(α) at those n is 5.07, 15.81, 1.75, 122.25, 1.28. The fractional-linear image reproduces them with
factor **1/5 or 5** — and det(3,1;1,2) = **5**. So the law is general:

> **For M ∈ GL₂(Q) with integer entries and determinant Δ, the induced approximation transfers with
> factor g²/|Δ|, g the gcd removed in reduction. For any rational map of degree ≥ 2, λ′ ~ λ/q² → 0:
> good approximations do not transfer at all.**

**Consequence for the design.** Correlated exceptional approximations arise by a derivable mechanism
**iff the two objects are GL₂(Q)-equivalent** — the classical "equivalent numbers have eventually equal
CF tails," in its non-unimodular form where |Δ| ≠ 1 turns equality of tails into a graded distortion.
The (∛m, ∛m²) "anomaly" is that fact and nothing else.

And **Galois conjugates of a cubic are not GL₂(Q)-equivalent.** For an S₃ cubic, α₂ ∉ Q(α₁) at all. For
a *cyclic* cubic α₂ = f(α₁) with f ∈ Q[x] of degree 2 — which by the table above transfers **nothing**.
So the derivable mechanism is **absent by theorem** on the target arm, in both sub-cases. That is a
much sharper target than "no obvious reason": a positive would have to come from somewhere with no
candidate source, and a negative is what the theory says.

## 5 — What is NOT resolved

- **The mapping to the literature sentence.** The spec's cite (`LIT`, index 41-1) says a big partial
  quotient "is connected to roughly half that quotient in the other." My derivation says the factor is
  g²/m. Two readings survive and I cannot separate them without the source: (a) the source was about
  **∛2/∛4 specifically**, in which case it is right and incomplete (it omits the g=2 branch, a third of
  events); (b) the source stated 1/2 for general m, in which case it is wrong for m ≠ 2. **Unresolved —
  and it does not block anything**, since the derivation stands on its own.
- **Nothing here touches boundedness of partial quotients** (§0). The law relates *finite* convergents of
  two objects; it says nothing about the tail of either sequence, at any depth.

## 6 — Correction to §6's cost table

§6's arithmetic checks out where it is checkable: P(a≥A) = log₂(1+1/A) is right (the 1.4427/A form runs
+1.0% high at A=50, +0.1% at A=500 — immaterial); Lévy gives **0.51532** decimal digits/PQ; the event
counts (289, 29, 2885, 289) reproduce.

**But the digit budget is short by a factor of 2.** Certifying a CF by interval pins terms only while
q_n² < 10^D, i.e. **n < 0.970·D**, not n < 1.94·D. Measured: D = 700 → 659 PQs, D = 1400 → 1365,
D = 2800 → 2738 (predicted 679 / 1358 / 2716). So **≈ 1.03 digits per *certified* PQ**, and
10⁴ PQs/object needs **~10,300 digits**, not ~5,200. Cost is still negligible at 10⁴; it is the sort of
factor that bites at 10⁵ where §6 already flags the O(n²) extraction.

## 7 — What Gate 0 hands to the design

1. **The (∛m, ∛m²) arm is a calibrator, filed as instrument certification, never as a finding** (§8.3).
2. **It is a better positive control than the Galois/quadratic arm** — derived here rather than `LIT`,
   predicting a specific lag *and* a specific per-branch amplitude, and living on the same substrate
   class (aperiodic cubic irrationals) as the target. The quadratic-conjugate arm certifies the
   instrument on *periodic* CFs, which is not the target's regime.
3. **But it is a ceiling arm, not a floor.** The ladder is a **deterministic translation** — ρ = 1, a
   delta at a known lag. Firing on it proves the instrument can see an infinitely strong signal and
   licenses **nothing** about a weak one. Per the banked floor/ceiling doctrine and the
   unquantified-power antibody, §5's "positive arm must clear the permutation null by a stated margin"
   **cannot be discharged by this arm as it stands.**
4. **The knob that fixes (3) is |Δ|, and it comes from theory.** For threshold A, an α-event survives
   into β's event set only if λ′ = (g²/m)λ ≥ A, i.e. λ ≥ mA/g² — so the *observable* coincidence rate at
   the g=1 branch falls like ≈1/m while the g=m branch transfers everything. Varying m therefore gives a
   **family of known-answer pairs of computable and graded coupling strength**, from which the
   instrument's detection floor is read off directly rather than assumed. That is the powered falsifier
   §7 asks for, stated as a number, built from theory instead of by dilution.

**Open before any arm runs:** items 3–4 are a design change, not a result, and the sensitivity floor
they define has to be tabulated before the seals are written.

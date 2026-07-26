# GATE 0b/c/d — stratification of the target arm, and the coupling dial

**Status:** owed before the seals, **delivered**. Corrects `GATE0_FINDINGS.md` §4.
**Scripts:** `gate0b_stratify.py`, `gate0c_verify_strata.py`, `gate0d_dial.py` (+ `*_measured.json`).
**No S₃ object was read.** Strata B and C are calibrators by construction; the clean target is untouched.

---

## 1 — The correction that forced this

`GATE0_FINDINGS.md` §4 claimed the derivable mechanism is absent on the target arm "in both
sub-cases." **The cyclic sub-case is false.** Shanks's simplest cubics x³ − ax² − (a+3)x − 1 have their
roots permuted by a Möbius map over Q. Verified here for a = 0…11: **M = (1,1;−1,0), t = 1, |det| = 1**,
disc = 81, 169, 361, … all perfect squares, all > 0 — totally real and cyclic, i.e. **members of the
target arm's population**, and unimodular, i.e. Serret-equivalent with a shared CF tail and ρ = 1.

**My error was testing a representative rather than the class.** "α₂ = f(α₁) with deg f = 2" is true and
irrelevant: two rational functions can agree on the three roots while differing as functions, and it is
the Möbius representative that transfers approximation quality.

**The consequence is a pooling error, not a scope trim.** A target arm that pools totally real cubic
conjugates averages a ρ = 1 subfamily against a presumed-ρ = 0 subfamily — an inhomogeneous population,
the same defect shape as the Palm–Khintchine null and the Maass desymmetrization.

## 2 — Stratum 3 as defined is EMPTY, and why

"Cyclic **without** an order-3 element of PGL₂(Q)" cannot occur. Over Q̄ a 3-cycle on three distinct
points determines M uniquely. If σ generates Gal = C₃ with α_i ↦ α_{i+1}, then σ(M) is the unique map
sending σ(α_i) ↦ σ(α_{i+1}), i.e. α_{i+1} ↦ α_{i+2} — which **is** M. So σ(M) = M, and
PGL₂(Q̄)^Gal = PGL₂(Q) by Hilbert 90. **Every cyclic cubic has its 3-cycle realised over Q.**

**Verified: 0 of 162 cyclic cubics in the census lacked a rational Möbius map.**

## 3 — The replacement stratum is the determinant, and the classification is gapless

For a coprime-integer representative, M³ = λI forces (Cayley–Hamilton, M² = tM − ΔI):
**Δ = t²**, λ = −t³. So |det| = 1 iff |t| = 1.

**There is no escape via a different unimodular matrix.** If M and M′ both send α₁ ↦ α₂, then M⁻¹M′
fixes α₁; a non-identity Möbius map over Q has fixed points satisfying a rational quadratic, so it
cannot fix a cubic irrational. Hence **M is the unique rational Möbius map sending α₁ to α₂**, and
α₁ ~ α₂ under Serret **iff |Δ| = 1**. And |Δ| is a GL₂(Z)-conjugation invariant (if d divides every
entry of UMU⁻¹ it divides every entry of M = U⁻¹(UMU⁻¹)U), so it is an invariant of the *object* up to
CF-tail equivalence, not merely of the polynomial.

| stratum | criterion | mechanism | role |
|---|---|---|---|
| **A** | disc not a square (S₃) | α₂ ∉ Q(α₁) ⇒ **no** rational Möbius map | **clean target** |
| **B** | cyclic, \|t\| = 1 | M ∈ GL₂(Z): shared CF tail, ρ = 1 | **ceiling** control |
| **C** | cyclic, \|t\| > 1 | unique M, non-unimodular: attenuated by g²/t² | **graded** control |

**Census** (x³+Ax²+Bx+C irreducible, |A|,|B|,|C| ≤ 12, disc > 0; 5388 cubics):
S₃ **5226 (96.99%)**, cyclic **162 (3.01%)** — of which **|t| = 1: 80** and **|t| > 1: 82**, with
|t| ∈ {2, 4, 5, 7, 11, 13, 17} (counts 56, 2, 6, 4, 2, 6, 6). Δ = t² verified on all 162.

**So stratum C is not a curiosity — it is half the cyclic population.** The "interesting middle" exists;
it is just not where it was expected. It is not "cyclic with no map," it is "cyclic with |det| > 1."

## 4 — The law holds on the strata, verified against each conjugate's own CF

General form, same derivation as §1 of Gate 0: for integer M = (a,b;c,d), g = gcd(ap+bq, cp+dq) — and
**g | Δ**, since Δp = d(ap+bq) − b(cp+dq) and Δq = −c(ap+bq) + a(cp+dq) —

  **λ′ = (g²/|Δ|)·λ**,  **log Q = log q + log|cα+d| − log g**.

| stratum | \|det\| | induced frac. is a conjugate convergent | max \|meas/pred − 1\| | median |
|---|---|---|---|---|
| B, \|t\|=1 | 1 | **100.0%** | 2e−16 | 0 |
| C, \|t\|=2 | 4 | 47.7% | 1.7e−01 | 0 |
| C, \|t\|=5 | 25 | 17.8% | 6.5e−06 | 0 |
| C, \|t\|=13 | 169 | 6.9% | 2.2e−16 | 0 |

Stratum B gives λ′ = λ exactly (a = 88 → a = 88): the shared tail, as Serret requires. `g | Δ` held on
every convergent of every object tested. Residuals are the derived O(q⁻²) term, concentrated at the
smallest q (median 0).

## 5 — The dial (R-066, axis 1) — and it is a formula, not a lookup table

A transferred *convergent* is not a transferred *event*. At threshold A a partner is itself an event
only when λ′ ≥ A, i.e. **λ ≥ |Δ|A/g²**. With the Gauss–Kuzmin tail P(λ≥A) ~ 1/A:

> **predicted coincidence rate = Σ_g P(g)·min(1, g²/|Δ|)**

| pair | \|det\| | predicted | measured (A=20, n≈100) | ratio |
|---|---|---|---|---|
| cyclic \|t\|=1 | 1 | 100.0% | 100.0% | 1.00 |
| cyclic \|t\|=2 | 4 | 49.9% | 50.0% | 1.00 |
| cyclic \|t\|=5 | 25 | 20.1% | 19.8% | 0.99 |
| cyclic \|t\|=13 | 169 | 7.5% | 10.1% | 1.35 |
| ∛2 / ∛4 | 2 | 66.6% | 67.6% | 1.02 |
| ∛3 / ∛9 | 3 | 50.2% | 49.5% | 0.99 |
| ∛5 / ∛25 | 5 | 33.3% | 39.0% | 1.17 |
| ∛7 / ∛49 | 7 | 25.6% | 21.0% | 0.82 |
| ∛12 / ∛144 | 12 | 42.1% | 38.0% | 0.90 |

**Any |det| can therefore be sized without running it.** Note the rate does *not* fall like 1/|Δ| —
the g = |Δ| branch transfers everything, and it is the g-histogram that sets the floor. Range covered:
**100% down to ~7%, a factor of 15–20**, on both families.

## 6 — Axis 2 has no handle in this data, and that is the binding limitation

The ladder places a partner at an **exact** lag: measured asymptotic (n ≥ 200) lag spread is
**2–5×10⁻¹³** per g-branch — the numerical floor. Full-range spreads of 1e−2 … 1e−1 are a small-q
transient, not jitter.

So real data offers **zero** jitter axis. The target's plausible weak signal has the opposite shape —
**many events, partially coincident, smeared in u** — and a detector calibrated on "few but perfect" is
uncalibrated for "many but smeared." The Dirichlet precedent is exact: the amplitude gate was unpowered
until the injected control fired, and the injection is what earned the argument.

**Owed before the seals, and not delivered here:** injection at controlled coincidence fraction *and*
controlled jitter width, with the detection floor reported on both axes jointly. Axis 1 alone is a
count-sensitivity curve and does **not** discharge §5's margin requirement.

## 7 — Consequences for the spec

1. **§4's target row splits.** "Totally real cubic conjugate triples" is not a population — it is three,
   and pooling them is the defect in §2 above. Classification is computable per object before any
   measurement: discriminant square-or-not, then |t| of the Möbius map. **Cheap: 0.4 s for 5388 cubics.**
2. **Stratum B replaces the ∛m ladder as the positive control** — same ρ = 1 ceiling, but *inside the
   target's own construction*, so it controls for construction rather than sitting beside it.
3. **Stratum C is the graded control**, and it is better than the m-dial for the same reason.
4. **Only stratum A is a clean target**, and there the mechanism is absent by theorem: α₂ ∉ Q(α₁)
   forbids any Q-rational Möbius map, since a Möbius image of α₁ lands inside Q(α₁).
5. **§5's halt-on-positive-arm-failure gate still cannot be discharged** until axis 2 exists.

## 8 — Provenance corrections, both the reviewer's

- **Digit rate.** 0.515 was the information-theoretic rate; the certified rate is **1.03 digits/PQ**, the
  factor of exactly 2 being the square in q_n² < 10^D. R-067 supersedes the spec's figure.
- **Ladder scope.** The `LIT` sentence describes the (∛2, ∛4) figure in context, so **"right but
  incomplete"** is the resolution and the over-scoping was in the spec's restatement, not the source.
  R-064's "two readings survive" is closed in favour of reading (a).
- **Still unresolved, non-blocking:** whether the g-factor appears in the source or is new here.

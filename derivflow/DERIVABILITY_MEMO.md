# Is the measured relaxation form derivable from the machinery Campbell pointed at?

**Verdict: NO — not from that machinery alone, and the reason is structural rather
than a matter of effort.** Grade: argued from the sources in full text plus our own
banked data; the central step is demonstrated, not asserted. Not a theorem.

**Depth of this read, stated up front.** arXiv:2408.09337 (Arizmendi–Fujie–Perales–
Ueda, *S-transform in Finite Free Probability*) read in full — 45 pages extracted to
text and searched exhaustively. doi:10.4171/dm/1071 (Campbell, *Free infinite
divisibility, fractional convolution powers, and Appell polynomials*) read at
abstract-and-structure level only. arXiv:2506.08910 (Arizmendi–Campbell–Fujie) at
abstract level.

## 1. What the S-transform paper contains

Exhaustive search of the full text for local-statistics vocabulary:

| term | hits |
|---|---|
| spacing, gap, microscopic, consecutive roots | **0** |
| fluctuation, rigidity, point process, pair correlation, universality | **0** |
| local | 4 — all of them "locally uniform convergence", a topology statement |

The paper is entirely about the global empirical root measure, its coefficients and
its cumulants. Two exact results matter to us:

- **Lemma 3.2.** With `∂_{k|d} p := p^(d−k)/(d)_{d−k}`, the normalized coefficients are
  *invariant*: `ẽ_j^{(k)}(∂_{k|d} p) = ẽ_j^{(d)}(p)` for `j ≤ k ≤ d`, where
  `ẽ_j = e_j(roots)/C(d,j)`.
- **Cumulant flow.** `κ_r(∂_{j|d} p) = (j/d)^{r−1} κ_r(p)`.

Both are exact, deterministic, and hold on `P_d(R)`. (The S-transform half of the
paper is restricted to `P_d(R≥0)` — nonnegative roots. Our seeds are sign-symmetric,
so that half does not directly apply to us; the coefficient and cumulant lemmas do.)

## 2. The decisive argument

We implemented Lemma 3.2 as a gate (`cumulant_gate.py`) and ran it on our own flow.
It passes at machine precision. That is what makes the point:

> Along the *same* flow, at n = 4096 on an iid seed, the quantity this machinery
> controls is **constant to 2.6×10⁻¹⁴** in relative terms, while the quantity we
> measure moves from 0.366 to 8.15×10⁻⁵ — **a factor of 4,492.**

A quantity that is exactly invariant cannot determine a quantity that changes by
three and a half orders of magnitude over the same interval. No function of the
finite free cumulants — hence no function of the empirical measure they determine —
can be the relaxation curve. This is not "the derivation would be hard"; it is that
the target is not in the image of the machinery.

The underlying reason is the ordinary global/local seam: two root configurations
with identical normalized coefficients to all orders share an empirical measure and
may still have arbitrarily different local spacing. Our arc has lived on that seam
from the start; it is now visible inside Campbell's own references.

## 3. What would supply the missing bridge, and its status

An equilibration or fluctuation theory on top of the deterministic flow. The natural
candidate is the Dyson-Brownian-motion analogy: differentiation-as-free-convolution-
semigroup is the polynomial cousin of DBM, and DBM's signature fact is local
equilibration after `t ≫ 1/N`. In our variables `s = k/n`, that translates to `k ≫ 1`
with no dependence on n.

**That is our SCALE-FLAT verdict.** k* ≈ 11 (iid) and 6 (GUE), flat across a 16×
range in n, is the quantitative content of exactly that expectation. Two consequences,
both of which cost us something:

- The flat scale should be presented as **the folklore's own prediction, measured** —
  not as a surprise the field has to be argued into.
- The DBM route is an **analogy, not a theorem here**. A literature check found no
  result connecting DBM local equilibration to the differentiation flow; the nearest
  work (e.g. arXiv:2602.06826) concerns the limiting global flow. And there is a
  material disanalogy: DBM is stochastic, the derivative flow is deterministic — the
  same objection PROSE already concedes about the isoconfigurational ensemble having
  no momentum-like variable.

## 4. A correction to an earlier internal reading

It was suggested in-session that DBM-style equilibration predicts a *single universal
relaxation*, so our 20σ/9σ seed-dependence of (τ, β) counts against the folklore.
**We think that is wrong and should not go in the note.** DBM universality is a
statement about the *limit* — the local statistics the flow converges to — not about
the *rate* of approach. Both our seed classes do converge to the same crystalline
limit. Seed-dependent rates are entirely compatible with equilibration folklore.

What the folklore does **not** predict is the **stretch**: β ≈ 0.70–0.79 rather than
β = 1. A plain equilibration picture gives an exponential. That, and not the scale or
the seed-dependence, is the part of our measurement nothing on offer accounts for —
and it is the part our own conditioning experiments (Step 2 at k = 0, Step 2b at
k = 2) failed to explain away as a mixture.

## 5. Consequence for the note

The claim narrows and sharpens at the same time. Retire: "the local regime is open."
Retire: the flat scale as headline novelty. Keep, and lead with:

> A stretched exponential, β < 1, in a deterministic system with no thermal bath, no
> quenched disorder, and a certified error model — where the two standard conditioning
> moves fail to decompose it into a mixture.

The scale confirms the folklore. The form is what the folklore does not reach.

## 6. What would overturn this memo

A written result deriving a *rate* or *form* for a local statistic from finite free
cumulant flow, without an added fluctuation theory. We could not construct one and
argue in §2 that none exists. If Campbell's "follows from work that's out there"
refers to such a bridge, it is the thing worth asking about — and the only question
in this exchange worth spending a reply on.

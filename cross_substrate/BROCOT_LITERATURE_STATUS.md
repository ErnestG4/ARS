# Brocot — literature status, swept 2026-09-09

**Protocol.** Three independent sweeps, run in parallel, each instructed to treat
SILENCE on named terms as a first-class result and to cite only sources actually
retrieved. ~90 distinct search strings, ~140 tool calls. Domain A: Diophantine
approximation and spacing statistics. Domain B: FM synthesis / computer music.
Domain C: mode locking, Planat's corpus, quasiperiodic operators.

**Why it ran.** Before this date the brocot line contained **zero citations** — no
arXiv reference, no named prior work, no dated sweep, across ~60 sealed cells and
both findings docs. Its novelty had therefore never been asked in a form the record
could answer. derivflow carries `TRACK0_SCOPE §9` plus two adversarial audits; this
line carried nothing.

The claim below is always "as of 2026-09-09, by this protocol," never a standing fact.

---

## 1. The object is not new, and the prior art is direct

`brocot_perAlpha.py:68` calls `predict_partials([1.0, alpha], [8.0, 8.0])` — **two
modulators, ratios 1 and alpha**. The partial set is therefore

    { 1 + n1 + n2*alpha : |n_i| <= order_bound(8) }, amplitude-pruned and folded,

i.e. a **bounded-height two-dimensional lattice projection**. Up to the truncation
shape (box-with-Bessel-pruning here, energy simplex there) this is the spectrum of
two harmonic oscillators with frequency ratio alpha — an object with a named
literature since 1977.

| source | what it establishes |
|---|---|
| Berry & Tabor, Proc. R. Soc. A **356** (1977) 375 | for incommensurable frequencies P(S) is peaked away from zero — level repulsion — and "the precise form of P(S) depends on the arithmetic nature of the irrational frequency ratios" |
| Pandey, Bohigas & Giannoni, J. Phys. A **22** (1989) 4083 | "Level repulsion in the spectrum of two-dimensional harmonic oscillators" — dedicated study of this exact set |
| Bleher, J. Stat. Phys. **61** (1990) 869 | golden-mean ratio: spacing distribution depends **periodically on log E**; no limit |
| Bleher, J. Stat. Phys. **63** (1991) 261 | generic ratio: **no limit distribution exists at all** |
| Greenman, J. Phys. A **29** (1996) 4065 | averaged distribution unstable under perturbation of the ratio; delta function for a **dense** class of ratios |
| Haynes & Roeder, arXiv:2006.06157 | algebraic case, multi-dimensional: asymptotically **quasiperiodic in log E** |

**Consequence.** "Spacing statistics of an alpha-generated frequency set depend on the
arithmetic of alpha" is **1977 material**. `brocot_perAlpha`'s rho = +0.699 is not the
discovery of an effect; it is a quantification, across 255 alphas, of an effect whose
sign and existence have been in print for ~half a century. Any writeup must cite
Berry-Tabor and Pandey-Bohigas-Giannoni as priority holders.

## 2. Two live threats to results the repo currently holds

**(a) SATURATION may be a theorem, not a finding.** Boshernitzan-Dyson, as stated in
Bleher-Homma-Ji-Roeder-Shen (arXiv:1107.4134): the number of **distinct** nearest-
neighbour spacings in `{m.omega : |m| <= E}` is **uniformly bounded in E iff omega is
badly approximable**, and unbounded otherwise. That is saturation at the badly-
approximable end, as a theorem, at bounded scale — the shape `BROCOT_SATURATION.md`
reports as an empirical finding. Both sweeps found this independently.

This is [[dont-fit-what-a-theorem-fixes]]. In 1D the same structure is the three-distance
theorem: at bounded N the gap set of `{n.alpha}` has <= 3 values with multiplicities that
are known functions of the continued-fraction convergents. If the Brody fit is reading
three-gap multiplicity weights, the saturation is a re-expression of arithmetic that was
already fixed.

**THE DECISIVE TEST, and it is cheap:** count DISTINCT spacings per alpha on the banked
point sets. Boshernitzan-Dyson predicts that count stays bounded at the rigid end and
grows at the approximable end. If our data show that, the saturation is theorem-fixed and
must be reported as a measurement OF a known structure. If they do not, the finding
survives and is sharper for having been attacked. Not yet run.

**(b) DEPTH-INVARIANCE is threatened by Bleher.** If no limit distribution exists for a
generic ratio and the golden-mean case is periodic in log E, then invariance over a
factor ~3.5 in B (delta log E ~ 1.25) may be sampling less than one period of a predicted
oscillation. Fix: extend B over several decades, using the golden mean — where Bleher
gives an exact periodic answer — as a known-answer rail.

## 3. Two objections that DO NOT survive, checked against the banked artifacts

Recorded because they are the objections a referee will reach for first, and both fail.

- **"D_Q is bounded by Hurwitz and the Markov spectrum is discrete above 1/3, so the
  predictor is quantised at the rigid end — range restriction."** Aimed at the wrong
  quantity. Those theorems govern `liminf_{q->inf} q||q.alpha||`; `brocot_perAlpha.approx_D`
  computes `min_{1<=q<=Q}` at **finite Q = 2*depth**, which varies continuously. Re-indexing
  from the asymptotic label to the bounded-scale one was the whole point of
  [[mis-indexed-not-underpowered]].
- **"The correlation vanishes at the rigid end because predictor variance collapses
  there."** Contradicted by our own numbers: `brocot_attenuation.json` gives SD(D_Q) =
  0.0469 (bottom tercile) vs **0.0472** (top tercile), ratio **1.004**. The predictor has
  the same spread at both ends; it is the OUTCOME spread that falls (0.4822 -> 0.2279).
  B2's design — split on the predictor, so the OLS slope stays unbiased while correlation
  attenuates by a known formula — was the right instrument and it already answered this.

## 4. What is genuinely unoccupied

- **Point-process / RMT classification of synthesis spectra.** Domains A and B both probed
  this (5 independent queries in B, 3 in A); zero hits. arXiv metadata search returns
  literally zero for `"frequency modulation synthesis" AND "sideband"`. Nearest neighbours
  are Weaver (JASA **85** (1989) 1005) and Ellegaard et al. (PRL **75** (1995) 1546) on
  *mechanical* resonances — not synthesis spectra, no ratios, no timbre.
- **Brody on Farey/Stern-Brocot locking sets.** Planat's corpus was checked four ways —
  full-abstract pull of all arXiv "Planat + phase locking" entries, full author listing, the
  14-item Watkins bibliography, direct fetch of the two likeliest candidates. **Zero**
  occurrences of spacing distribution, Wigner, GOE/GUE, Brody, spectral rigidity, Delta_3 or
  number variance. His observables are S(f), Allan deviation, Farey-tree discrepancy,
  Ramanujan-Fourier coefficients. His zeta connection is the Mangoldt/Mobius error term, NOT
  Montgomery-Odlyzko spacing statistics. The Farey-locking and RMT literatures do not cite
  each other.
- **A bounded-scale continuous Diophantine covariate.** The classical literature uses
  asymptotic *classes* (type gamma, badly approximable, algebraic of degree d+1) as a
  categorical hypothesis. `D_Q` at a scale matched to the instrument is not a construction
  found in the sweep.
- **The index-coupled coincidence horizon.** Chowning (JAES **21** (1973) 526; CMJ **1**(2)
  1977) states the factorisation explicitly — "the ratio ... determines the position of the
  components ... while the modulation index determines the number of components which will
  have significant amplitude" — and never couples them. His Fig. 8 nomogram is an
  `order_bound(I)` construction, drawn rather than formulated.

## 5. One reconciliation the sweep raised and this doc closes

Domain B flagged an apparent contradiction with **Truax, CMJ 1(4) (1978) 39**, whose
criterion for FM sideband coincidence is exhaustive and index-free: N:1 and odd N:2 only,
i.e. N2 | 2. Under `max(p,q) <= 2B` a ratio p=3, q=1 with B >= 2 would be admitted.

**Different objects.** Truax treats classic single-modulator FM (`c + n*m`, one index).
Brocot's lattice carries a second modulator at ratio 1, giving `1 + n1 + n2*alpha` with two
free indices. Direct coincidence there needs `(n1-n1')*q = -(n2-n2')*p`, hence `q |
(n2-n2')` and `p | (n1-n1')`; with `|delta n| <= 2B` that is exactly `max(p,q) <= 2B`. The
horizon is correct for the object it is stated over, and Truax's rule is the right
antecedent to cite for the single-modulator case, not a contradiction.

Note the horizon is elementary — the derivation above is two lines. Elementary and
unreported is worth something, but it is not worth much dressed up.

## 6. Unswept surface

Roads, *The Computer Music Tutorial*; Moore, *Elements of Computer Music*; Dodge & Jerse,
*Computer Music*; Chowning & Bristow, *FM Theory and Applications* (1986). All offline-only,
all plausible homes for a folklore statement of an index-bounded coincidence rule. Truax's
paper was reprinted in Roads & Strawn's *Foundations of Computer Music*, so Roads certainly
knew the falls-against rule. A web sweep cannot settle whether anyone extended it. **Physical
check required before any novelty claim on the horizon.**

## 7. Process note

A WebFetch summariser pass returned two **fabricated** verbatim quotations from the Chowning
PDF and reversed the sign of the reflection phase. Caught by re-extracting the PDF text
locally. Nothing in this document is quoted from a summariser pass.

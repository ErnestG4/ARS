# Phase 5d — R-016 fires harder than expected, and the invariance one-liner pays off clean

`phase5d_maass_gate.py`, `phase5d_maass_gate_measured.json`. §0 held.

## 0. §0b on the gate's own motivation

R-016 was ranked as the gate on **Luo–Sarnak number variance for arithmetic hyperbolic surfaces**, cited
as "flagged in the long-range brief as the only theorem-grade long-range calibrator in the arc."

**`Luo` appears nowhere in this repository.** `grep -rni "luo"` over all `.md`/`.py`/`.json`/`.txt`
returns only "fluorescence". No brief flags it. The closest in-repo reference is Rudnick–Sarnak 1994
(eigenstate behaviour, not number variance) in `PHASE34E_BRIEF.md`'s bibliography.

The paper is real — Luo & Sarnak, *Number variance for arithmetic hyperbolic surfaces*, CMP **161**
(1994) 419–432. **The substance stands; the attribution does not.** Filed as the third inherited pointer
this session that fails §0b, and tested below on its merits rather than on its provenance.

## 1. The invariance one-liner — CP1's transferred assumption is now MEASURED

CP1/Phase 4 survives Phase 5c's Maass misfit finding because ⟨r̃⟩ is unfold-invariant. That invariance
was measured on ζ and transferred to Maass **by argument**. Measured directly, across four treatments
(raw R, pipeline unfold, theory-affine without the final rescale, trend-removed):

| sector | raw R | pipeline | theory-affine | detrended | **max spread** | Phase-4 bracket sd | **spread in σ** |
|---|---|---|---|---|---|---|---|
| parity 0 (n=266) | 0.39922 | 0.39972 | 0.39972 | 0.39986 | **0.00063** | 0.02133 (Poisson) | **0.03σ** |
| parity 1 (n=334) | 0.42665 | 0.42565 | 0.42565 | 0.42679 | **0.00114** | 0.01821 (Poisson) | **0.06σ** |

Banked CP1 values (0.39922 / 0.42665) reproduce the **raw** column exactly, confirming Phase 4's
unfold-free path.

This is not a trivial test: the Maass density varies **~10×** across the sector (dN/dR ≈ R/12, R from 9.5
to 98.8), so the unfold is a substantial smooth reparameterisation. ⟨r̃⟩ moved by **0.03–0.06σ** of the
bracket width against a **7.3σ / 6.4σ** verdict.

**CP1's load-bearing assumption converts from argument to measurement, and holds with ~100× margin.**
Cheap insurance, and it paid as a clean confirmation rather than a catch.

## 2. R-016 — the bracket is unreachable, and detrending cannot repair it

Σ² per sector (L = 1, 2, 4, 8, 15), three unfolding treatments against both references:

**parity 0 (n=266)**

| path | L=1 | 2 | 4 | 8 | 15 |
|---|---|---|---|---|---|
| pipeline (the banked path) | 0.6979 | 0.8507 | 0.6898 | 0.8269 | **0.8876** |
| trend removed | 0.6828 | 0.8383 | 0.6863 | 0.7691 | **0.7348** |
| no final rescale | 0.6758 | 0.8365 | 0.7083 | 0.8264 | 0.8666 |
| **Poisson reference (= L)** | 1.0 | 2.0 | 4.0 | 8.0 | **15.0** |
| GOE reference | 0.442 | 0.583 | 0.723 | 0.863 | 0.991 |

**parity 1 (n=334)**: pipeline 0.598 / 0.695 / 0.675 / 0.677 / **0.750**; trend removed 0.604 / 0.696 /
0.673 / 0.640 / **0.669**.

Three things fall out, and the third is the important one.

**(a) The banked Σ² leg is 17–20× short of its own reference.** Σ²(15) measures 0.888 (parity 0) and
0.750 (parity 1) where Poisson predicts 15.0. The leg does not weakly support the Poisson classification
— it is nowhere near it, and reads *flatter than GOE* at L=8 and L=15. That inconsistency with the ⟨r̃⟩
leg sits in the banked Session K record unreconciled.

**(b) The final `sp/sp.mean()` rescale is not the culprit.** "No final rescale" reproduces the pipeline
to within 2% at every L. I had this as a candidate mechanism; it is excluded.

**(c) Detrending moves Σ² AWAY from Poisson, not toward it — and that is the finding.**
Var[S] falls 0.6620 → 0.2808 (parity 0) and 0.7711 → 0.2388 (parity 1), i.e. the 58%/69% from Phase 5c,
and Σ²(15) falls with it. **The removed trend was contributing long-range variance.** But long-range
variance is exactly what a long-range statistic is *for*.

> **Unabsorbed Weyl-remainder systematic and genuine long-range spectral fluctuation occupy the same
> low-α band, and at N = 266/334 they are not separable.** Detrending removes both. There is no operation
> on this data that takes one out and leaves the other.

So R-016's answer is not "the trend contaminates the bracket, remove it and proceed." It is: **the Maass
Σ² leg is not repairable by detrending, because the repair and the signal are the same object.**

**(d) There is no L window where the Poisson prediction is testable at all.** After detrending, Σ²
saturates near 2·Var[S] = **0.562** (parity 0) / **0.478** (parity 1) — *below one mean spacing*. No L in
{1, 2, 4, 8, 15} puts the measured Σ² within 20% of Poisson's L. The linear regime the theorem describes
begins below the resolution of the level sequence.

**Verdict on the calibrator: the Luo–Sarnak bracket is UNREACHABLE with 600 level-1 eigenvalues**, and
the obstruction is structural rather than a matter of sample size — more eigenvalues at the same heights
would extend the L range but not separate the trend from the signal.

## 3. Reach, amplitude, separability — the named triple for the long-range brief

The pair generalises to three independent gates. A statistic can pass any subset:

| gate | bounds | test | ζ | Maass level-1 | `unfold_emp(order)` substrates |
|---|---|---|---|---|---|
| **Reach** | how far out in L a fitted unfold can see | L_max ≈ N/(2(p+1)), p = fitted density params | p=0, **no cap** | p=2, cap **66–84** ✅ (read to L=15) | 250 (order 3) / 100 (order 9) |
| **Amplitude** | how much of the reading inside that reach is systematic | fraction of Var[S] that is smooth low-order trend | 0 (θ exact) | **58–71%** ❌ | measured per substrate |
| **Separability** | whether systematic and signal can be told apart at all | is the smooth counting known **exactly**, or only asymptotically? | **exact** ✅ | **asymptotic** ❌ | asymptotic/absent ❌ |

**Maass passes reach and fails the other two** — which is precisely the "pass one, fail another" case the
pair was named to catch, and the third gate is why the failure is terminal rather than repairable.
ζ passes all three, and that — not the choice of statistic — is why ζ's long-range readout works.

This closes the long-range brief's vague "log the L-to-window ratio" slot with three computed gates.

## 4. The 3.18–3.20σ boundary — withdrawn, wrong slot, mine

Asked to record which estimator achieves the permanent ceiling, the answer is that **the ceiling figure
was computed against the wrong null.**

| quantity | value |
|---|---|
| effect: ζ⟨r̃⟩ − matched-density GUE null | 0.017316 |
| **floor: matched-density null sd** (the null the effect is measured against) | **0.007063** |
| ⇒ | **2.452σ** — which is P1's banked figure |
| the 3.18σ figure used the **uniform** GUE null sd | 0.005442 |

The uniform null is 1.30× narrower — and it is **the null P1's own reviewer showed to be powerless**
against the density confound. Dividing the matched-null effect by the uniform-null floor mixes two nulls.

**Corrected terminal line: P1's low-γ leg is at 100% of the available data, and 2.452σ is the final
number — not 77% of a 3.2σ ceiling.** W=2000 is the entire population below γ=2515 (1999 zeros exist),
so there is no larger W to buy. The leg is **exhausted**, which is the same conclusion, arrived at
without an invented headroom figure.

**Estimator of record for the boundary:** ⟨r̃⟩ = mean over consecutive spacings of
min(sᵢ, sᵢ₊₁)/max(sᵢ, sᵢ₊₁), on raw γ (unfold-invariant), block `zeros6[:2000]`, against the
matched-density GUE null of `phase1_density_check.py::matched_density_null` — Dumitriu–Edelman β=2
tridiagonal central-window levels imposed on the R–vM density backbone, W=2000, n_real=30, null sd
0.007063.

This is my **fifth** slot error of the session and it landed in the one number flagged as "will get
cited." The instinct to ask for the estimator was what caught it.

## 5. Terminal line, merged

Both permanent boundaries have one root — **1999 zeros exist below γ = 2515**:

- P1's excess there is measured against all of them, at 2.452σ, with no larger W available.
- P1's predicted *internal* variation (~0.005) sits at the noise floor of that same population, so the
  structure test is permanently underpowered.

**The low-γ end of P1 is exhausted.** Not expensive, not self-defeating, not awaiting compute — finished.
Any further movement on P1 must come from high γ, where the effect is smaller and the data unbounded.
That is a terminal line for a leg that has been ambiguous for several phases.

## 6. Defect ledger

Mine this session: seal tautology (caught pre-run), Var[S] on the wrong branch, an inert arm in a sealed
conjunction, a gate arm at 0.3% contrast, an unweighted-vs-weighted mean, and now a ceiling divided by a
different null's floor — **six**, five of them one defect: *a number compared against a differently-defined
number, or a test whose power was never computed.*

Reviewer-side, self-declared: three constructed inferences with defective support, plus recommending the
flatness test as "the sharpest unrun thing" without computing its power — one message after naming that
exact defect. **The rule has to fire at recommendation time, not only at seal time.** Filed to R-012.

Ten defects between us. **Every one caught by a gate; none reached a banked claim.** The continuation
brief asserted that the protocol is durable and the findings perishable. This session measured that, in
both directions, including against review.

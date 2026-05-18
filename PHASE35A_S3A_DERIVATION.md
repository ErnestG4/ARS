# §3-(A) — Fibonacci-Cantor IDS-unfolded NNS: DERIVATION (reduction) (2026-05-18)

**Status:** THEORY, parallel Step-2 track (Will "execute these"). Gate
`745b215` passed ((A) §5b-anchor constructible + rational-θ-validatable).
Lit-lock discipline: DGY facts and the thermodynamic-formalism map are
**cited, not independently verified here** — to be lit-locked at execution.
Honest verdict up front: **§3-(A) is REDUCED, not closed and not
intractable.** No closed-form P(s) is asserted (that would be the
assert-not-derive failure this whole arc guards against). No instrument
run; brief-and-hold on stamping; Class II blocked; not a §3 adjudication.

## 1. Object (rigorous)

Fibonacci Hamiltonian (BAR-scoped: DGY is *Fibonacci-specific*; AM-critical
exponents are a separate cited-not-verified input, **no silent
Fibonacci→AM transfer** — §7.ter.48). Spectrum Σ = zero-Lebesgue Cantor
set; DOS measure μ (eigenvalue distribution) supported on Σ; IDS
N(E)=μ((−∞,E]) is a devil's staircase (flat on the dense gaps).
Finite truncation E_1<…<E_{Nc}; **unfold** x_i = Nc·N(E_i); unfolded
spacing s_i = Nc·μ((E_i,E_{i+1}]), mean spacing 1 by construction.

## 2. DGY input (rigorous, cited-not-verified)

μ is exact-dimensional and multifractal; its Rényi spectrum τ(q) (⇔
generalized dimensions D_q=τ(q)/(q−1), ⇔ singularity spectrum f(α) by
Legendre transform) is **computable exactly** from the Fibonacci trace-map
thermodynamic formalism on the Fricke–Vogt hyperbolic set (DGY;
Damanik–Gorodetski 2012: the DOS measure's local scaling exponent is
strictly below the spectrum's Hausdorff dimension; τ(q) real-analytic).
This input is obtained by a route **entirely independent of any direct
NNS construction** — the property §5b non-circularity needs.

## 3. The reduction (the derivational step actually taken)

Small unfolded spacing s_i = Nc·μ((E_i,E_{i+1}]) is small ⇔ consecutive
finite-Nc eigenvalues are close in **μ-measure** ⇔ they sit where μ is
most concentrated, i.e. where the **local Hölder exponent** α of μ
(μ(B(E,r))~r^α) is small. The distribution of local α over Σ **is** f(α).
Hence the IDS-unfolded NNS is, structurally, the *re-expressed
distribution of local scaling exponents of μ*. The standard
thermodynamic-formalism correspondence (multifractal measure ⇄ its
nearest-neighbour / box-mass statistics) gives the moment scaling

  ⟨s^q⟩  ↔  the partition function Σ μ(I_k)^q over the Nc-quantile
  partition  ↔  governed by **τ(q)** (cited-not-verified: a *known class*
  of result; its **specific exact form for the IDS-unfolded NNS** — vs
  the textbook box-mass formulation — is the to-pin step, §6).

This *reduces* "derive the unfolded Fibonacci-Cantor NNS" to: **[DGY-exact
τ(q)] ⊕ [the multifractal→unfolded-spacing-moment map (known class; exact
form to pin)] ⊕ [rational-θ exact validator (§5)].** That is a genuine
reduction — not a closure (the map's exact form is open) and not
intractable (it lies in a known class with an exact validator).

## 4. The §5b independent anchor — now EXPLICIT

Two features predicted from DGY-τ(q)/f(α) **without constructing P(s)**,
which the eventual direct NNS derivation must reproduce (non-circular):

- **(i) small-spacing exponent** β: P(s)~s^β as s→0, set by the
  most-concentrated part of μ (the q→∞ end) ⇒ β ↔ α_min / D_∞.
- **(ii) low-moment ratios** ⟨s^q⟩/⟨s⟩^q for small q ↔ D_2 (correlation
  dimension) and the local τ(q) slope.

§5b = derived-NNS's (β, low moments) **vs** the DGY-τ(q)-predicted
(β, moments), on the §7.ter.59 floor. Non-circular: the τ(q) side is
trace-map thermodynamic formalism, not the NNS derivation.

## 5. Rational-θ exact validator (constructible & rigorous — built here in spec)

For θ=p/q (golden-mean convergents F_{n}/F_{n+1}) the operator is
**q-periodic**: Σ = ≤q Bloch bands (NOT Cantor — exactly solvable), DOS
absolutely continuous with √-van-Hove edges, IDS plateaus **exactly** at
k/q (gap-labelling, exact). Both sides are then elementary in closed form:
the band-DOS τ(q) AND the IDS-unfolded q-band NNS. **Validator:** the
f(α)/τ(q)→(β,moments) map must hold *exactly* on every convergent
F_n/F_{n+1}; holding on all convergents validates the map for use in the
irrational (Cantor) limit. This is concretely buildable (a q-periodic
tridiagonal operator; closed-form Bloch bands) — its *execution* is a
gated run, not done here; the construction/spec is complete.

## 6. Open / cited-not-verified (honest boundary)

- The **exact closed form** of the multifractal→IDS-unfolded-spacing map
  (§3) — reducible to a known class, not closed here; the genuine
  remaining mathematics.
- DGY exact τ(q) statements and the map class are **cited-not-verified**
  (lit-lock at execution; the brief's standing discipline).
- **BAR scope** stays attached: this is the *Fibonacci* substrate; AM-
  critical needs AM's own (non-DGY-rigorous, cited-not-verified)
  exponents — no silent transfer.

## 7. Verdict (asymmetric — derivation, never a discovery)

`S3A_REDUCED` — reduced to [DGY-exact input] ⊕ [known-class map, exact
form to pin] ⊕ [constructible rigorous rational-θ validator], with the
§5b independent anchor made **explicit** (β↔D_∞, low-moments↔D_2). NOT
`DERIVATION_INTRACTABLE` (it reduces cleanly with an exact validator),
NOT closed (the map's exact form is the open step), NOT asserted. Returns
for full adjudication with its own derived result (or an honest
`INTRACTABLE`) when the §6 step is pinned and rational-θ-validated — its
own focused effort, not stamped here.

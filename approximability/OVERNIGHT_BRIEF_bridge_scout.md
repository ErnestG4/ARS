# SEALED OVERNIGHT BRIEF — post-J/λ: bridge, scout, class, divergence

**Status of the arc.** The finite-depth `g̃(a,f)` program is **complete and banked** (G→H→I→J + λ-addendum, commit
`8535033`). Direction law closed-form (17/17 special + 68/68 generic cubics); magnitude one substrate-universal
surface `g̃(a,f)` at λ=8, no substrate memory in the marginal; λ→∞ layer reconciled with Panel A (golden anchor
θ_∞ = logφ/log(1+√2) = 0.54598; metallic C-ladder + liminf-K order parameter DONE). This brief consolidates the seam
the λ-excursion still owes, then opens the **off-trajectory** frontiers — new observables, not more CF depth.

**Discipline (applies to every arm).** `main` and refsuite stay untouched; each night runs on its own branch off the
current head. Every quantitative claim is **byte-locked before measurement** — the SEALED json files are written
*now*, unsealed only at readout. Reproduce a known-answer calibrator before trusting any fitter
([[synthetic_validate_fitters]]). The morning gives a **verdict**, not a pile to interpret.

**Sequencing (two nights, four arms).**
- **Night 1** — the G/F-style paired independent jobs: **O1 consolidates what just closed** (verify the bridge before
  it enters the record), **O2 opens the next thing cleanly** (measure the scout). Both cheap, both verdict-shaped.
- **Night 2** — Arm 1 (primary) + Arm 2 (secondary), one job each, run together.

---

# NIGHT 1 — the G/F-style paired independent jobs

## O1 (consolidate) — bank the seam: verify the θ_∞ = L_a / C_a bridge before it enters the record

**Frame.** The θ_∞ = L_a/C_a bridge (Lévy CF-growth over DEGT dimension-constant) is the real deliverable of the
λ-excursion — the connective law between the finite-λ surface and the DEGT ladder. Right now it rests on **three
metallic points**. Before it goes in the record as *the seam*, it gets the discipline everything else got: extend the
ladder to a=4,5 and pre-register whether the bridge **holds within propagated bands** or **drifts**.

**Why cheap.** L_a is closed-form exact for every metallic mean (L_a = log((a+√(a²+4))/2)). Panel A **already has**
C for a=4 (1.021607). So the only new heavy run is **C(a=5)** via the validated Panel A growth-rate engine
(dim·lnλ, λ→∞ extrapolation of λ≥16 points — **not** single-λ box-counting, which fails its own gate). a=4 gets a
**confirmation run to attach an error bar**; a=1 is the anchor.

**The load-bearing pre-registration (this is where an artifact would hide).** a=1 (golden) is the **only** rung with
a published closed-form C (log(1+√2)); every a≥2 rung uses a **measured** C carrying its own error. Propagate that
error into θ_∞ = L/C and **do not let a clean-looking θ_∞ ladder be an artifact of correlated C-measurement noise**
— the way the ⅓ CI nearly was. Report the C-measurement covariance across rungs, not just point values.

**Built-in calibration (the golden self-check).** Measured-C bridge at golden gives θ_∞ = logφ/C_meas = **0.54862**;
the closed form logφ/log(1+√2) = **0.54598**. The +0.48% gap **is** the known −0.4% C-measurement error. So the
golden rung *calibrates the bridge's own error budget* before a≥2 is trusted.

**SEALED bridge table** (θ_∞^pred = L_a / C_a; L exact, C from Panel A; a=5 C to be measured):

| a | mean | L_a (exact) | C_a (Panel A) | θ_∞^pred = L/C |
|---|---|---|---|---|
| 1 | golden | 0.481212 | 0.877140 | **0.548615** (vs closed-form 0.545979) |
| 2 | silver | 0.881374 | 0.866711 | **1.016917** |
| 3 | bronze | 1.194763 | 0.913349 | **1.308113** |
| 4 | metallic-4 | 1.443635 | 1.021607 | **1.413103** |
| 5 | metallic-5 | 1.647231 | *MEASURE* | *L/C₅* |

**Pre-registered gate.** Where an independent θ_∞ (direct bandwidth-exponent extrapolation) is obtainable, the bridge
prediction must match it within propagated bands at every rung a=1–5. Golden is the closed-form anchor. VERDICT is
one of:
- **CONFIRMED a=1–5** — bridge banked as the seam between the finite-λ surface and the DEGT ladder, with error budget
  set by the golden self-check; or
- **GOLDEN-ONLY** — a≥2 flagged as *measured-not-derived*, bridge downgraded to a golden coincidence pending closed-
  form C for a≥2 (Liu–Wen frames these via liminf-K with no closed forms — that would be the honest ceiling).

**Deliverable.** Either verdict is clean. Byte-locked in `O1_bridge_prereg_SEALED.json`.

## O2 (open) — the scout's near-optimality dimension, measured for free on data we already have

**Frame.** The theory read closed with a concrete, cheap gate: the Farey scout is **efficient iff the near-optimal-
cell count grows sub-polynomially with depth** — and that count is **directly measurable without building the scout**,
just a counting loop over CF prefixes. This is the *measure-it-don't-assume-it* move ([[validate_scale_convergence_before_asymptotic_constant]])
applied to the **tool** instead of the physics: it converts the scout question from "provably efficient in theory"
to "measured efficient (or not) on real substrates."

**Substrate pool (banked, no new data).** The 13 J-cubics are generic-CF — exactly the wilderness the scout is for —
and their CF prefixes to the depths already computed *are* the depth-h cells whose near-optimal count is the whole
question. Controls: φ (self-similar → maximally sparse, the trivial-green case), the fifth, π, e.

**Method.** For each substrate and depth h: over the depth-h Stern-Brocot / Farey cells, count N(h) = number of cells
whose **fingerprint reward** is **near-maximal** (within the pre-set threshold of the depth-h max). Read off the
**near-optimality dimension** d\* = lim log N(h) / (h·log 2) (fraction of the ~2^h cells that stay near-optimal):
- **d\* → 0** (sub-polynomial N(h)) → scout **GREEN** (prunable, efficient);
- **d\* > 0** (exponential N(h)) → scout **RED** (can't prune, inefficient) — and we learned it for a counting loop.

**The load-bearing pre-registration (byte-locked BEFORE any counting — this is exactly where an unpinned threshold
manufactures a favorable count).** Sealed in `O2_scout_prereg_SEALED.json`:
- **Fingerprint reward** for a cell (rational p/q approximating target α at depth h): the scaled approximation
  quality R = −log( q·|qα − p| ) (larger = closer to the best-approximation Lagrange frontier; this is the scout's
  own objective, not an ad-hoc score).
- **Near-maximal threshold**: a cell counts iff R ≥ R_max(h) − Δ with **Δ = log 2** locked (within a factor-2 of the
  depth-h best — the natural Farey-mediant band). Both R and Δ are fixed here and not tuned after seeing counts.

**Pre-registered fork.** For the generic-cubic pool, d\* clusters near 0 (scout **measured-efficient** on real
wilderness) vs d\* bounded away from 0 (scout **measured-inefficient**). φ must return d\* = 0 (N(h)=O(1)) as the
sanity control; if it doesn't, the counting harness is wrong, not the scout.

**Deliverable.** An empirically measured near-optimality dimension per substrate + the pooled cubic verdict
GREEN/RED. The scout question moves from theory to measurement. Byte-locked; φ-control gates the harness.

---

# NIGHT 2

## Arm 1 (PRIMARY) — Does the long-range spectral *class* carry the substrate memory the marginal `g̃` erased?

**Frame.** The marginal (NNS / `g̃`) collapsed π + fifth + e + 13 cubics onto one curve. But the marginal **cannot
certify the universality class** ([[nns_certifies_marginal_not_class]], [[longrange_lens_discipline]]). The long-range
statistics of the *band spectrum itself* (not the spacings) can. So we ask the sharpest possible version: is the
universality we just proved **marginal-only**, or does it go all the way to the class?

**Object.** Band-edge spectra of the metallic Schrödinger operator at **λ=8** (the resolvable regime — MORNING_λ:
the double-precision band-resolution wall bites at λ≥16, so we stay at λ=8). Substrate pool: golden + metallic
ladder + the fifth + the 13 J-cubics, at **matched q-reach** (matched depth budget so L-ranges are comparable). Band
edges for depth-4/5 golden-neighbourhood and the fifth at λ=8 are already banked (`*_edges.npy`); the cubic pool is
generated overnight (embarrassingly parallel, numba solver).

**Statistics.** Unfold the integrated density of states to unit mean density, then compute **number variance Σ²(L)**
and **spectral rigidity Δ₃(L)** across a pre-set L-window.

**Layer-zero calibration (run first, must pass).**
1. GUE surrogate → Σ²(L) ~ (1/π²)ln L ; Poisson surrogate → Σ²(L) = L. Both recovered before any band spectrum is
   touched ([[synthetic_validate_fitters]]).
2. Band-resolution adequacy at λ=8: n_bands_below_prec small enough that the IDS is not corrupted by railed bands
   (carry the MORNING_λ precision lesson; report the fraction of unresolved bands per substrate).

**Pre-registered fork (SEALED — the substantive question, not a proxy [[discriminant_exact_question_check]]).**
These are singular-continuous / Cantor spectra: expect **neither** Poisson (Σ²~L) **nor** Wigner-Dyson (Σ²~ln L),
but multifractal Σ²(L) ~ L^γ with 0<γ<1. The discriminant is whether γ (and the Δ₃ slope) **COLLAPSES** across
substrates:
- **COLLAPSE** — γ universal within propagated bands → the universality deepens from marginal to class. Major.
- **SPLIT** — γ substrate-ordered (e.g. tracks a or the CF tail) → `g̃`-universality is **marginal-only**;
  substrate memory lives in the class, exactly as the discipline warned. Also major, and the more likely prior.

**Deliverable.** A one-line verdict COLLAPSE vs SPLIT with the γ-ladder and its error bars, plus the Δ₃
cross-check. Either is a clean morning. If it graduates to the heavy generation run, seal its json before measuring.

## Arm 2 (SECONDARY, cheap, parallel) — the `e` divergence law

**Frame.** `e` has liminf-K = ∞ (theorem) ⇒ dim·lnλ diverges ⇒ **no finite C** (Panel A order parameter). We have
W only at n=13,14 (`e_W_deep.json`). Measure **how** C_k ≡ dim_k·lnλ climbs.

**Method.** Extend the e depth-ladder (deeper W_k via the same deep measure path), form running
dim_k = log q_k /(log q_k − log W_k), C_k = dim_k·ln8. e's CF is [2;1,2,1,1,4,1,1,6,…] — the growing even entries
drive (a_1···a_k)^{1/k} → ∞ slowly; that sets the predicted C_k growth rate.

**Pre-registered fork (SEALED).** C_k grows without bound at the liminf-K-implied slow rate (**confirm divergence**)
vs saturates (**would contradict the theorem → flag loudly**, likely a resolution artifact to chase).

**Deliverable.** The measured divergence form of C_k for e, checked against the liminf-K = ∞ prediction. Self-
contained; parks against the class run for free.

---

## Commitments / out-of-scope
- **In scope, authorized:** O1 + O2 (Night 1); Arm 1 + Arm 2 (Night 2). All four are cheap, pre-registered,
  verdict-shaped, and touch no `main`/refsuite state.
- **Out of scope (parked, NOT overnight compute):** analytic derivation of `g̃(a,f)` (a thinking task, not
  unattended compute); λ≥16 deep band spectra (precision wall); cubic deep tails q>60k (O(q²) wall); non-metallic /
  general-frequency C beyond the metallic line (queued behind O1, not tonight).
- **Byte-locked artifacts written now:** `O1_bridge_prereg_SEALED.json`, `O2_scout_prereg_SEALED.json`. Arm 1 / Arm 2
  forks are sealed in-prose above; if either graduates to a heavy run, seal its json before measuring.

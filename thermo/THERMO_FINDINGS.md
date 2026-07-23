# THERMO — Thermodynamic Formalism of the Gauss Operator (session 2026-07-21)

Brief: the handoff "ARS — Thermodynamic Formalism of the Gauss Operator". Findings perishable;
the protocol is the product.

Artifacts: `gauss_thermo.py`, `gate_fixtures.py`, `pressure_sweep.py`, `farey_orbit_check.py`,
`PRESSURE_PREREG_SEALED.json`, `*_measured.json`.

---

## 0. Reconciliation — the handoff was written against an older repo than the one that exists

The authoring model had not seen source and said so. Reconciling §9's suggested order against
`sessionK/` and `approximability/`:

| §9 step | handoff assumed | actually in-repo | status |
|---|---|---|---|
| 1. generalize CP2 to `L_s`, confirm s=1 | to build | `gkw_matrix(N, s)` **already s-parameterized**, `coprimary2_transfer_operator.py` | **already done**, re-verified PASS this session |
| 2. route (B) determinant, dim E₂, Lyapunov | to build | `approximability/thread3_constants.py` is **already** an mpmath periodic-orbit Fredholm determinant vs Jenkinson–Pollicott; Lyapunov already at 1e-6 | **already done** |
| 3. §5 Mayer bridge, reproduce t₁ | "the whole thesis made numerical" | `sessionK/mayer_run1.py` **already** locates parity-resolved det(1∓L_s) zeros; t₁ = 9.5354 vs LMFDB 9.5337; **70 zeros matched**, median err 0.0013; parity convention already settled (sym0=even) | **already done** (Session K Run 1, KEYSTONE, PASS) |
| 4. `P(s)` sweep + §7 transition | to build | **absent** | **built this session** |
| 5. multifractal `f(α)` | to build | **absent** | not started |
| 6. Tier-1 payoff | to build | partial (dim E₂ is a *fixture*, not a sealed prediction) | not started |
| 7. Tier-2 weld-test | "build the trace-map operator too" | `cross_substrate/trace_map_dimension.py` **already is** the trace-map Bowen-pressure machinery | see §5 below — **this needs care** |

So §1–§3 and §5 of the handoff were already built and passing. The genuine gaps were
**precision** (everything was float64, ~8 digits) and **the thermodynamics itself**.

---

## 1. New instrument — arbitrary-precision `L_s` (`gauss_thermo.py`)

Same operator, new precision path. Not a new instrument.

The float64 CP2 path caps near 1e-8 because it truncates the `n`-sum at `nmax` and patches a
one-term `f(0)·nmax^{1-2s}/(2s-1)` tail. The new path removes the truncation entirely: the
collocation interpolant through N+1 Chebyshev–Lobatto nodes is *exactly* a degree-N polynomial,
so for each Lagrange basis polynomial `L_i(y) = Σ_k c[i,k] y^k`

```
Σ_{n>Ne} (n+x)^{-2s} L_i(1/(n+x))  =  Σ_k c[i,k] · ζ(2s+k, Ne+1+x)      EXACT
```

The tail is summed in **closed form** in Hurwitz zeta rather than approximated.

**The one subtle part, recorded because it is the kind of thing that silently caps precision.**
The monomial coefficients `c[i,k]` grow like `4^N` — intrinsic to *any* polynomial basis composed
with `y = 1/(n+x)`, which compresses [0,1] into a short interval near 0. Routing the whole sum
through them would cancel ~0.6N digits off the answer. Confining them to the `n>Ne` tail fixes it
twice: `y < 1/Ne` kills the `4^k` growth term-by-term, and the tail is only an `O(Ne^{1-2s})`
correction, so the lost digits land on a small correction instead of on the answer. The head
`n ≤ Ne` uses stable barycentric evaluation.

Measured convergence **0.86 decimal digits per node** (predicted 0.77 from the Bernstein ellipse
through the `x = -1` singularity of `1/(1+x)`, ρ = 3+√8 = 5.83).

### Gate — `gate_fixtures.py`, **GATE_PASS = True** (N=32, dps=55)

| fixture | source | agreement | float64 path was |
|---|---|---|---|
| λ₀(s=1) = 1 | definitional | **29.1 digits** | 8.3 |
| GKW constant λ₁(s=1) | Wirsing (20 dig) + arXiv 2602.19435 Thm 1.1 (certified, err<1e-175) | **24.2 digits** | 8.2 |
| Gauss Lyapunov −P′(1) = π²/(6 ln2) | closed form | **27.0 digits** | 6.0 |
| dim E₂, alphabet {1,2} | Jenkinson–Pollicott | **21.7 digits** | 7 |

Scales as advertised: N=56/dps=95 gives **42.7 digits** on the GKW constant.

**Canonical GKW reference is now Briggs 2003** (n=800 at 1300 bits, confirmed at n=1000/1600,
"probably accurate to 385 decimals"), with digits taken from the PDF's own text layer via
`pdftotext` — **not** through a fetch summariser. Cross-checked against Wirsing's classical 20
digits, and independently confirmed by this session's operator to **66.5 digits** (N=88).

> ### ⚠ AMENDED — the earlier entry here cleared the source too early, and was wrong to
>
> **What v1 of this document said:** an early comparison saturated at exactly 18.3 digits
> regardless of N *and* dps; I suspected a corrupted reference (this repo has been burned by
> WebFetch's summariser before), found instead that the reference literal was parsed at the
> *ambient* dps (15) before precision was raised, and recorded "**It was wrong.** … Cost: one
> wrong hypothesis about a source that was in fact faithful."
>
> **What is actually true: there were TWO defects, not one.** The parse bug was real and was the
> cause of the 18.3-digit saturation. But the reference string **was also corrupt** — and I
> cleared it on the strength of having found the first bug.
>
> The string I had extracted from arXiv 2602.19435 (Nisoli — a **real paper**, correctly cited,
> genuinely certified) is byte-identical to Briggs **with the digit `6` at index 98 deleted**.
> The fetch summariser dropped one digit. Confirmed constructively: deleting Briggs' index-98
> digit reproduces the extracted string to all 170 of its digits.
>
> This is nasty in a specific way: everything after the drop is *correct but shifted one place
> left*, so the tail still looks like plausible GKW digits. And because the gate only validated
> to ~24–43 digits, the corruption sat **55 digits beyond anything that could detect it**. It
> would have surfaced only when someone pushed past 98 digits and trusted the wrong string.
>
> **The generating pattern is [[flag_is_a_floor_not_a_ceiling]]:** a confirmed mechanism-flag
> (the parse bug) absorbed the search and hid a second defect underneath. Finding the cause of
> the symptom is not the same as clearing the hypothesis the symptom raised. The parse bug
> explained the *saturation*; it never explained the *string*, and I stopped looking.
>
> **Protocol, corrected and strengthened.** A constant saturating at a fixed digit count
> independent of both N and dps has (at least) two candidate owners — your own reference literal
> parsed at ambient dps, and a corrupted reference. Check your parse first *because it is
> cheaper*, **not because it is exclusive**. Then still adjudicate the string: cross-check
> against a second independent source at full length, and prefer digits pulled from a primary
> document's text layer over any summarised fetch. `gate_fixtures.py` now keeps the corrupted
> string as a live regression assert pinned at digit 99.

---

## 2. Pressure function `P(s)` — sealed, then measured

`P(s) = log(leading eigenvalue of L_s)`, `β = s` the inverse temperature for the geometric
potential `−β log|G′|`. Predictions sealed in `PRESSURE_PREREG_SEALED.json` **before** running.
All four confirmed.

- **P1 (closed-form control) — PASS.** Golden subsystem `A={1}`: `P(s) = −2s·log φ` exactly,
  ≥22.9 digits at every `s` tested. Validates the restricted-alphabet code path against a closed
  form, independently of any measured constant.
- **P2 — PASS.** Full alphabet: strictly decreasing and analytic on (1/2, 3]; `P(1) = 0` to
  **25.8 digits**.
- **P3 (parameter-free) — PASS.** `P(s) + log(2s−1) → 0` as `s → 1/2⁺`:
  residual **0.0634 → 0.0108 → 0.00115 → 0.000115** at `s−1/2 = 1e-1…1e-4` — linear in ε, exactly
  the predicted `O(2s−1)` correction. Derivation: `(L_s 1)(x) = ζ(2s, 1+x) = 1/(2s−1) − ψ(1+x) + …`
  with the divergent part **x-independent**, so positivity pins `λ(s)·(2s−1) → 1`.

---

## 3. **§7 CORRECTION — the phase transition is NOT golden-mean-dominated** (headline)

The handoff §7 states: *"The slowest orbits are the golden-tail continued fractions […,1,1,1], so
the transition is golden-mean-dominated."* It flags this as a hypothesis to verify, not a citation.

**Verdict: INVERTED. The transition is driven by the LARGE-partial-quotient tail. The golden tail
is the orbit farthest from the intermittent region — it never enters it at all.**

Two independent legs, sealed before measurement:

**(a) Operator leg** (`pressure_sweep.py` P4). For any *finite* alphabet {1..A} the operator is a
finite sum, hence **entire in s** — `P_A` is analytic at `s=1/2` with a finite value. The
singularity exists only in the `A → ∞` limit, so it is manufactured by the large-`a` tail and
nothing else.

| A | 1 | 2 | 3 | 5 | 10 | 20 | 40 | 80 |
|---|---|---|---|---|---|---|---|---|
| λ_A(1/2) | 0.618034 | 1.0404 | 1.3545 | 1.8059 | 2.4827 | 3.1953 | 3.9197 | 4.6452 |

All finite; unbounded in A; fit `λ_A(1/2) = 1.0266·log A + 0.134` against the predicted slope ~1.
(Golden's `λ₁(1/2) = 0.618034 = 1/φ`, matching the P1 closed form `φ^{-2s}` at `s=1/2`.)

**(b) Dynamical leg** (`farey_orbit_check.py`), on the Farey map directly, iterating the continued
fraction **symbolically** so the result carries no precision decay:

| start | a | left-branch (intermittent) steps of 400 | min\|x\| | dwell runs |
|---|---|---|---|---|
| golden [1,1,1,…] | 1 | **0** (0%) | 0.618034 | — |
| silver [2,2,2,…] | 2 | 200 (50%) | 0.414214 | 1,1,1,… |
| [5,5,5,…] | 5 | 320 (80%) | 0.192582 | 4,4,4,… |
| [20,20,…] | 20 | 380 (95%) | 0.049876 | 19,19,… |
| [50,50,…] | 50 | 392 (**98%**) | 0.019992 | 49,49,… |

The Farey map decrements `a₁` until it reaches 1 and then drops it, so an excursion at partial
quotient `a` takes **exactly `a−1`** left-branch steps and reaches `min|x| ~ 1/a` — deeper into the
cusp as `a` grows. The golden tail has every `a=1`, so it takes the left branch **never**.

**Why the handoff got it backwards — a slot error, not a value error.** Golden *is* the extremal
continued fraction, but for **bounded-type / approximability** reasons (`K=1`, the Panel A order
parameter `liminf (a₁···a_k)^{1/k}`) — a *different arc*. Intermittency is governed by the
*opposite* end of the same alphabet. This is the [[filing_discipline_attribution_slot]] pattern:
a real object attributed to the wrong owner. Both arcs live in this repo, which is exactly what
makes the confusion available.

> **Method note.** The dynamical leg's first version returned INCONCLUSIVE for two reasons, both
> mine, both worth keeping: (1) it iterated a *finite* CF `[1]*60`, which is a **rational** — once
> the expansion is exhausted the orbit is absorbed by the neutral fixed point, so golden falsely
> showed 341 left-branch steps in a single 340-long dwell run, which is the absorption artifact,
> not the dynamics; (2) the predicted dwell was `a`, but it is `a−1`. Symbolic CF iteration removes
> failure mode (1) by construction. A prediction that is off by one and a test that measures the
> wrong object fail *the same way* — as INCONCLUSIVE — and had I only fixed the off-by-one the
> rational-absorption bug would have survived.

**Not claimed:** nothing about the *order* of the Farey transition. Prellberg–Slawny 1992 (*Maps
of intervals with indifferent fixed points: thermodynamic formalism and phase transitions*,
J. Stat. Phys. **66** 503–514) is confirmed to exist as cited and to report a second-order
transition with specific-heat divergence, but that concerns the **Farey** pressure, not the induced
**Gauss** pressure measured here. Order/location of the Farey transition is untested.

---

## 4. Discipline ledger

- Two-quantization wall (§8.1): **respected.** Nothing here touches the almost-Mathieu door.
- Approximability criteria (§8.2): kept distinct; §3 above turns on exactly that distinction.
- Sealed-then-checked (§8.3): all four pressure predictions sealed before measurement.
- Filing (§8.4): full alphabet, restricted alphabet, and the trace-map operator are named as
  different objects throughout; the gate reports dim E₂ under an explicit "restricted alphabet —
  NOT the full Gauss operator" label.
- Precision hygiene (§8.5): mpmath throughout; every reference digit traced to a source; the one
  near-miss logged in §1.

---

## 5. ⚠ Carry-forward — the Tier-2 weld is NOT a greenfield build, and that changes the risk

The handoff frames Tier 2 as "build the trace-map transfer operator too, then test whether the two
formalisms relate", with expected default *no coincidence*. **But both halves already exist and
have already been divided by one another.**

- `cross_substrate/trace_map_dimension.py` is the trace-map Bowen-pressure machinery → `C_a`.
- `sessionK/coprimary2_transfer_operator.py` gives the Gauss periodic-orbit invariant → `L_a`.
- `approximability/` banks the ladder **θ_∞ = L_a / C_a** for a=1..5 (MORNING_K, O1), described
  there as "an empirical connective law, not yet mechanism-derived above golden", with the golden
  rung matching a closed form and the a=4 rung calibrated to −0.0002%.

So a **cross-door ratio is already banked**. That is not a violation — it is labelled honestly as
empirical — but it means the Tier-2 wall is being leaned on by an existing artifact, and the
handoff's "seal the prediction first, expect non-coincidence" protocol cannot be run naively on a
quantity whose value is already known and banked. **Anyone running Tier 2 must seal against the
already-measured ladder, not pretend to a blind first look.** MORNING_K's open question — θ_∞
plateaus at ~1.42 for a=4,5 rather than climbing — is the natural sealed target, since
`L_a ~ log a` and `C_a ~ log a` would force a finite ratio for structural reasons.

Other queued items, unchanged: multifractal `f(α)` (§3 of the handoff, not started); Tier-1 sealed
payoff on a Gauss-generated ARS substrate exponent (not started).

---

# v2 SESSION — the Mayer bridge at full precision, and three corrupt reference constants

Executed against handoff v2 §9 item 1.

## 6. `t₁`: the CP1↔CP2 weld goes from 3.7 digits to 26.5 (`maass_t1.py`)

`sessionK/mayer_run1.py` welded the two fronts but at float64 with a `dr=0.02` grid scan:
t₁ = 9.5354 vs LMFDB 9.5337, **~3.7 digits — a 4-digit weld under a 24-digit operator.**

Re-solved as a root of `det(I + L_{1/2+ir})` (odd sector — `det(1+L)=0` ⇔ eigenvalue −1 ⇔ LMFDB
sym1) using the arbitrary-precision operator, by **secant in the complex r-plane**. `F` is
complex-valued for real `r`, so minimising `|F|` would halve the digits and forcing `r` real would
require dividing out the phase; letting `r` be complex avoids both.

| N | dps | t₁ | \|Im r\| | secs |
|---|---|---|---|---|
| 24 | 40 | 9.5336952613535474795384658 | 1.5e-13 | 13 |
| 32 | 55 | 9.5336952613535575543139978 | 1.7e-20 | 30 |
| 40 | 70 | 9.5336952613535575543442352 | 2.0e-26 | 66 |
| 52 | 85 | 9.5336952613535575543442352 | **2.1e-36** | 148 |

**t₁ = 9.533695261353557554344235236**, N-ladder self-consistent to **26.5 digits**
(N=40 vs N=52), matching the Booker/LMFDB reference to 21.4 digits — i.e. to the full length of
the reference, which it now extends.

> **The free check fired.** `Im(r) < 1e-36` is **nowhere imposed** — the solver ranges over the
> whole complex plane. Recovering the critical line to 36 digits is independent confirmation that
> the Selberg-zeta zero is where the arithmetic says it is. Dynamics and arithmetic are two slots
> for one fact (handoff §5); this verifies the slots separately and only then asserts the identity.

### Second Mayer zero — converged, and my first value was noise past digit 17 (v3 §4 audit)

The v3 handoff flagged that the even-sector second zero had been run once (N=32) and never
converged — its trailing digits were solver output, not a claim — and that a remembered Booker
string `13.779751351890738944243673…` appeared to diverge from my `…8949793919` around digit 20.
**The handoff's suspicion was correct.** N-ladder:

| N | 24 | 32 | 40 | 52 | 64 |
|---|---|---|---|---|---|
| r (even) | …186898765 | …**979391**909 | …**424372**399 | …424367328 | …424367328 |
| \|Im r\| | 7.9e-12 | 3.7e-18 | 3.1e-23 | 3.9e-32 | 3.4e-41 |

Converged value **r = 13.77975135189073894424367328151771**, self-consistent to **32.4 digits**
(N=52 vs 64), `|Im r| = 3.4e-41`. My earlier N=32 figure was correct only to ~17 digits: its tail
`…979391…` was solver noise, and the true continuation is `…424367…` — which matches the
handoff's remembered Booker string, *but I did not adjudicate it from that string.* It was settled
by the ladder converging, exactly the discipline v3 §4 asks for. `maass_t1.py` now runs this zero
as a ladder rather than a single shot. Same lesson as the calibrator audit, one level down: **a
computed value is trustworthy only to the precision an N-ladder — not a single run — certifies.**

**Parity independently confirmed.** t₁ was solved in the odd sector (`det(1+L)=0` ⇔ eigenvalue −1).
LMFDB's own symmetry labels for level 1 list r₁ = 9.53369526 as **odd**, and 13.7797513 /
17.7385633 / 19.4234814 as **even** — matching `mayer_run1.py`'s even-sector finds (13.7799,
17.7392, 19.4222) and odd-sector finds (9.5354, 12.1746, 14.3592, …). So Session K's convention
(eigenvalue +1 = even = sym0; eigenvalue −1 = odd = sym1) is corroborated from a source
independent of the operator. Still worth confirming the `∓` assignment against Lewis–Zagier
(arXiv math/0101270) before quoting parity in prose, per handoff §5 — LMFDB confirms *which
eigenvalues are odd*, not the derivation of the factorisation.

## 7. THREE reference constants were wrong — and each failed in a different way

This session found corruption in *three* of the calibrator zoo's reference values. None changed a
verdict, because all three sat beyond the precision anything had been validated to — which is
exactly why they survived.

| constant | defect | correct to | found by |
|---|---|---|---|
| GKW (from arXiv 2602.19435 via WebFetch) | **dropped digit** `6` at index 98 | 98 digits | cross-check vs Briggs 2003 |
| dim E₂ (banked in `thread3_constants.py`) | **digit transposition** at 21–22 | 21 digits | cross-check vs arXiv 1611.09276 |
| — my own comparison harness — | reference literal parsed at ambient dps=15 | 18 digits | N/dps-invariant saturation |

**(a) GKW — the summariser dropped a digit.** arXiv 2602.19435 (Nisoli) is a **real, correctly
cited, genuinely certified** paper; both it and arXiv 2606.13958 (Pollicott) resolve. The *fetch*
was the problem. The extracted string is byte-identical to Briggs with index-98 `6` deleted —
proved constructively (deleting it reproduces all 170 extracted digits). Everything after the drop
is correct but **shifted one place left**, so the tail still looks like plausible GKW digits.

Adjudicated *independently of the string argument* by pushing the operator past the divergence
point: at **N=148 / dps=250 the computation agrees with Briggs to 112.1 digits**, and digit 99 is
`6` in both. So Briggs is confirmed where the fetched string is missing a digit — by computation,
not only by inference. (An earlier N=124 run reached 93.9 digits, five short of witnessing digit
99, and could not settle it; that is why the larger run was worth doing.)

**(b) dim E₂ — the repo's own banked constant is transposed.** `thread3_constants.py`'s
`JP_PUBLISHED` reads `...41624 64 86473` for the true `...41624 46 86473` (arXiv 1611.09276, PDF
text layer). Correct to only 21 digits. **The tell was in the gate all along and I misread it:**
dim E₂ was the *worst* fixture at 21.7 digits while λ₀ hit 29.1 — I attributed that to the
restricted-alphabet subsystem converging more slowly. It was the reference terminating. With the
correct constant the same computation scores **29.6 digits**, in line with the others.
`thread3_constants.py`'s convergence table was measuring distance to a typo, so its accuracy
ceiling was artificial; its 21-digit confirmation of dim E₂ stands.

**Re-running it with the corrected constant recovers 17 digits that were always there.** The
periodic-orbit Fredholm determinant's own convergence ladder, unchanged except for the reference:

| N | 6 | 8 | 10 | 12 | 14 |
|---|---|---|---|---|---|
| Δ vs published | 1.3e-10 | −3.2e-17 | 1.6e-25 | −1.7e-35 | **−3.3e-38** |

Against the transposed constant this could never have read below ~2e-21. The route was in fact
converging to **38 digits** — saturating its own `dps=40` setting. So the correction does not just
tidy a literal: it restores a banked instrument's demonstrated accuracy, and confirms the two
independent routes (periodic-orbit determinant here, Chebyshev collocation in `thermo/`) agree on
dim E₂ far past where either was previously credited.

**(c) The near-miss I logged wrongly in v1** — see the amended box in §1. I found a real parse bug,
and then cleared the source on the strength of it. Both defects were real.

### The generating pattern, and the protocol that follows

All three are the same shape: **a reference constant is only ever exercised to the precision your
instrument has reached, so corruption hides in the digits beyond it and is invisible until the
instrument improves.** Raising precision is therefore not just a better measurement — it is an
*audit of the calibrator zoo*, and it will surface defects that were latent the whole time.

And (b) is [[flag_is_a_floor_not_a_ceiling]] twice over: in (c) a confirmed parse bug absorbed the
search; in (b) a plausible physical story ("the subsystem converges slower") absorbed an anomaly
that was really a broken reference.

**Protocol now enforced in `gate_fixtures.py`:**
1. Prefer digits from a primary document's **text layer** (`pdftotext`/`pypdf`) over any summarised
   fetch. Every reference here now comes from one.
2. Cross-check each constant against a **second independent source at full length**, not just on
   leading digits.
3. Parse reference literals at full precision **before** comparing.
4. Keep every retracted string as a **live regression assert** pinned at its divergence digit
   (98 for GKW, 21 for dim E₂), so a silent swap-back fails the gate.
5. Treat a fixture that scores conspicuously *worse* than its siblings as a suspect **reference**,
   not only as a suspect computation.

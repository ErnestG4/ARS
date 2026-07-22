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

**Two independent GKW sources** (Wirsing 1974 analytic; arXiv 2602.19435 certified interval
arithmetic) agree on their common 20 digits, so the long reference string is cross-checked rather
than taken on one authority — and the gate asserts that cross-check before using either.

> **Precision-hygiene trap, logged.** An early comparison "saturated" at exactly 18.3 digits
> regardless of N *and* dps. That is the exact signature of a corrupted reference string, and this
> repo has been burned by WebFetch's summariser corrupting a long column before — so it was the
> live hypothesis. **It was wrong.** The reference literal was being parsed at the *ambient* dps
> (15) before precision was raised. Parse reference constants at full precision BEFORE comparing.
> Cost: one wrong hypothesis about a source that was in fact faithful.

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
payoff on a Gauss-generated ARS substrate exponent (not started); pushing the Mayer bridge's t₁
from 4 digits to ~20 using this session's operator (now cheap — `mayer_run1.py` is float64 with a
2-term Taylor tail, and `gauss_thermo.matrix` already accepts complex `s`).

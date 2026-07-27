# Session compilation — 2026-07-26/27. Results, and where the lessons must be applied

**55 commits, `06caf2f` → `f60f2aa`.** Register R-064…R-133. Two arcs plus a toolchain.
Compiled from the repo, not from recollection.

---

# PART 1 — RESULTS

## Arc A — ARS cubic family, between-object axis (R-064…R-092)

**Gate 0 resolved, and it generalised past the phase.** For α=∛m, β=∛m², convergent p/q, g=gcd(m,p):
**λ′ = (g²/m)·λ**, exact to O(q⁻²), with a deterministic lag. Generalises to **g²/|det|** for integer
M ∈ GL₂(ℚ); **any rational map of degree ≥ 2 transfers nothing** (λ′ ~ λ/q²). So correlated exceptional
approximations arise by a derivable mechanism **iff the objects are GL₂(ℚ)-equivalent** — the classical
equivalent-numbers fact in non-unimodular form.

**The target arm was not a population — it was three.** S₃ (α₂ ∉ ℚ(α₁), clean target) / cyclic |t|=1
(Serret-equivalent, ρ=1, smoke test) / cyclic |t|>1 (attenuated g²/t², graded). Pooling them is a
Palm–Khintchine-shaped inhomogeneity error. "Cyclic without a Möbius map" is **empty** (elementary
proof, no cohomology needed).

**RESULT — sealed in advance, run, target empty:**
> Totally real S₃ cubic conjugates show **no coincidence of exceptional approximations above f = 0.05
> at zero jitter** (0.10 at J ≤ 0.2, 0.20 at J = 1.0), per conjugate pair, floor demonstrated by
> injection rather than argued.

1/24 fields vs 1.2 expected, binomial p = 0.708. All four instrument checks passed — *that* is what
makes the negative a result. **The seal halted the first run** on a broken check of mine that would not
have changed the answer (p = 0.708 either way, verified twice).

## Arc B — the clip pathology, and the toolchain it forced (R-093…R-133)

**The bug:** `arithmetic_toolkit.py:504`, `np.maximum(0, 1−R2)` clipping the **integrand**, three lines
under a docstring reading *"negative → clustering."* Two biases in **opposite directions**: saturation
on the observed side (conservative, large), rectification on the null side (+0.018, sd compressed 2.3×).

**Measured, real fungal:** clipped **+0.00000**, signed **−2.21224**. Existence on solar's footing
(outside the entire null range, **no z quoted** — 74 sd on a 12-draw null is a 25× extrapolation).
Recovery calibration is **not licensed** (k-slope CI admits drift 0.117 > the 0.101 correction), so the
supported claim is **|true I_rep| ≥ 2.21**, not −2.46.

**mass03 is clip-immune** (pure spacing count) — its real exposure is **unfolding**, sized: solar needs
**+181% / −55%** rescale (exact CDF, not an expansion) to move its 0.20 floor; **fungal's is TERMINAL**
— 0.655 + 0.410 > 1, unreachable by any rescale. Solar's local channel is bounded **by cancellation**
(the rate-preserving null reproduces the c-variation to 1.6 null sd) and measured **exactly** at
−0.0060 ± 0.0023 = 3% of floor.

**Theorem (attenuation universality):** ρ(x_c, y)/ρ(x, y) = **ρ(x_c, x)**, independent of the partner.
So saturation attenuation is a property of **the clipped field alone** — characterise a field once,
know its effect on every statistic it ever enters.

## Arc C — three watchers, each stating its own power

| tool | watches | power stated |
|---|---|---|
| `arsrh/rep_int_migration.py` | migration backlog | ratchet: fires on **increase** only, high-water moves down |
| `commensurable.py` — 5 clauses | comparability | refuses on unstated clause; 27/27 (sens 11, spec 9, iface 7) |
| `commensurable.py` — `require_varying` | degeneracy | fires above **39%** saturation at 10% loss tolerance |
| `commensurable.py` — `recover_rho` | correction | ±0.002 across 30–90%; **refuses at 100%** |

**Ten-instance unification:** the two sides of a comparison were not commensurable — same **quantity,
units, domain, unit of analysis, conditioning**. Mechanised because a memory file with ten instances
behind it was in exactly the state the sem/CI rule was in at its **fourth** failure.

---

# PART 2 — WHERE THE LESSONS MUST BE APPLIED

## ★ 1. THE PROPAGATION FAILURE — found today, and it is the largest item

**`overnight_2026_07_12/run_overnight.py:325` defines `irep_unclipped` — "The repair: signed
∫₀¹(1−R₂)dr — NO np.maximum(0,·)".** Built **two weeks before this session**, used in `VERDICT_A.md`
to overturn a load-bearing claim — **and never propagated into `arithmetic_toolkit.py`.** The deployed
detector kept clipping. This session rediscovered it from scratch.

**Fifth instance of [[knowledge_does_not_propagate]]** — a fix filed where it could not fire.

**And it already carries the Allen answer.** From `VERDICT_A.md`, on the unclipped axis:

⚠ **CORRECTED 2026-07-27** — I first cited VERDICT_A lines 85–87 (allen −5.003), which **that same
document supersedes**: those were computed before the overnight caught its own rate-contamination bug.
The current, rate-corrected census (VERDICT_A POST-RUN #2b):

| substrate | n | median signed I_rep | % < 0 |
|---|---|---|---|
| **allen-hpf** | 400 | **−7.99** | **100%** |
| hc3-port | 400 | −1.44 | 98% |
| ret1 | 325 | −0.32 | 77% |

*"the physically expected direction, for the first time. Allen is no longer an inverted outlier.
**The sign pathology was the instrument.**"* — filed by the overnight as **instrument validation,
NOT a discovery**, and that is the correct slot.

**This upgrades R-124, and by more than I said.** Allen's true I_rep is **−7.99** with **100% of cells
negative** ⇒ clipping pins **every one** to exactly 0 ⇒ **saturation confirmed at the maximum**, from
banked data rather than assumed. The saturation *premise* for Allen V1 is established. What
remains is only whether the specific ρ(rep_int, ks_gue) was computed on saturated bands — a much
smaller question than "recompute Allen V1."

**ACTION:** reconcile `overnight_2026_07_12` against this session before doing any further work on
this axis. Two independent derivations of the same repair is evidence the repair is right; it is also
evidence the propagation channel is broken.

## 2. The migration — 334 open, ~310 projected to need the signed field
4 of 401 sites migrated. Triage moved, deployment did not. Ratchet is green (non-increasing), so this
is a tracked backlog rather than a decay — but it is the largest *volume* item on the board.

## 3. The 18-site variance sweep — pre-committed, unrun
`seals/SATURATION_SWEEP_PRECOMMIT.json`. Now a **corrector**, not a flag-raiser: `joint_q_profile`
emits `rep_int_signed_q`, so per-site attenuation is measurable and magnitudes are recoverable at
30–90%. **Outcome C (nulls stand) must be reported at equal prominence**; **outcome D (100% saturation,
no signed field) is UNRECOVERABLE, not null.**

## 4. Newly flagged, ranked by severity

| site | shape | grade |
|---|---|---|
| `phase36/kpm_dos.py:74` | `np.clip(rho_x, 0, None)` on a KPM density, then `cumsum` → CDF → unfolding. Gibbs ringing is exactly what goes negative; clipping **rectifies** it. | **Same shape, low severity** — Jackson damping already mitigates Gibbs, and **no callers found**. Verify before spending effort. |
| `universality.py:92`, `intermittency.py:155` | p-values clipped to [0,1], then `np.nanmedian(ks_p)` — a **rank** statistic on a clipped field | **Lower grade**: the clip enforces a *definition* rather than destroying sign information. Check only if `median_ks_p` ever carries a comparison. |
| `cross_substrate/validate_fitters.py:35` | `np.clip(F, 0, 1)` on a CDF | Legitimate; flagged for completeness. |

**Checked and CLEAR:** `arsrh/solar_gap_checks.py:54` — `gap_ci = 1.96*nse` is reported as
`GAP_95CI` alongside `GAP`, i.e. a half-width used and labelled as a half-width. Correct usage.
No other `1.96·se`-as-a-bound instances found in the repo.

## 5. Research items — genuinely open, not debt
- **R-044** — the far block at 10²² tests the F-integral (SPCC predicts exactly 1) to 0.33%. Still the
  only item pointing at a conjecture rather than a theorem.
- **R-077/R-084** — the marginal P(g) is derived (finite count over (p,q) mod Δ); **P(g | event) is
  not.** Quantifying the q/λ coupling through y_n = q_{n−1}/q_n opens the |det| range.
- **Dirichlet between-object** — the cubic phase's machinery (permutation null over pairings, events as
  a point process on an intrinsic coordinate, injection-calibrated floor) transports; 630 characters
  are in the repo and the pairings are theory-specified.

---

# PART 3 — THE METHOD LESSONS, AND WHERE THEY NOW LIVE

| lesson | where it lives now |
|---|---|
| five-clause commensurability | `commensurable.py` — refuses, not remembers |
| bound ≠ half-width | `Bound`/`HalfWidth`, no `__float__` — usage collision closed, not just naming |
| exact ties are a mechanism | `saturation()` — **refuses without a declared continuous field type** |
| the witness must be structurally independent | one family, four faces: SOC catalogue, shared source, tool-as-its-own-unit, **tool-scoring-its-own-remediation** |
| decay vs choice | ratchet: a decay gets a **failing** check; a static backlog does not fire |
| pre-commit the unflattering outcome | `SATURATION_SWEEP_PRECOMMIT.json`, outcome C at equal prominence |
| which artifact was wrong | code / prose / neither — this session had one of each |
| review-of-prose ≠ review-of-code | prose/code divergence is the code-holder's to audit |

**The last catch of the session is the one to keep:** the ratchet was firing on its **own
remediation** — adding the signed field raised the match count, so the tool scored its fix as a
regression. Fourth face of witness-independence, **recognised rather than rediscovered**, in the same
session the family was merged. That is the only available evidence that a banked principle is a
principle rather than a description of what already happened.

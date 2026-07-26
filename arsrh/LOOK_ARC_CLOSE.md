# ARS Look Arc — close

Three principles the arc's last correction produced, one accounting note, and the honest summary line.
§0 held throughout: nothing in this arc estimates Λ or bears on RH.

## 1. When a claim outgrows its verification artifact, extend the artifact

The brief's status line said "71 values verified by `verify_brief_v2.py` (commit 44f4c56)" after content
had been added past that commit. Two repairs were available:

- **Rescope the claim** — narrow the sentence until it is true again. Cheap. It also shrinks what is
  checked and leaves the new content unverified *in perpetuity*, because nothing afterwards will notice.
- **Extend the artifact** — make the checker cover what the claim covers. More work, and the only version
  that holds.

**Take the second.** This is rule 13's underclaim face one level up: *do not downgrade a claim to match a
stale checker.* Downgrading for absence of verification is correct; downgrading because the verifier
lagged is the same filing error as overclaiming, wearing a modest hat.

## 2. The inert-gate defect recurs at every layer, and the fix is the same each time

Extending the harness surfaced a row that read a key from the wrong file and returned a silent `?`
rather than failing. **That is an inert gate — a check with no power to fail — inside the checker of the
method that catalogued inert gates.**

| layer | instance |
|---|---|
| **findings** | the unfold falsifier on an unfold-invariant statistic; the θ-cert on ⟨r̃⟩ |
| **method** | a sealed conjunction with a powerless arm; a gate at 0.3% of available contrast |
| **verifier** | a silent `?` on an unresolved read, passing as a clean run |

Same failure, same fix at all three: **make the power to fail explicit.** The separated
OK / MISMATCH / SUPERSEDED / UNRESOLVED verdict is the durable form of it — an unresolved read can no
longer be mistaken for a pass. The harness is now stronger than the document it checks, which is the
correct direction.

## 3. Alarm fatigue converts a live harness into a decorative one

Four rows were reporting MISMATCH against wording the brief no longer contains. That is not an untidy
output — **a permanently-failing row gets learned as noise, and a check learned as noise is inert
regardless of what it prints.** The `SUPERSEDED` status is a power fix, not a cosmetic one.

**And the two dispositions are not interchangeable.** The four rows split 2/2, on a distinction worth
keeping:

- **Replaced claim → `SUPERSEDED`.** The `N/(2(p+1))` form no longer appears anywhere; there is nothing
  live to check. The row is retained purely to document the correction, and is excluded from the failure
  count.
- **Revised number → re-point, do not retire.** "Rescale reproduces to 2%" became "3.2% max"; that is
  still a live claim in the brief. The check was re-pointed at the corrected value and continues to run.

Marking the second pair `SUPERSEDED` would have quietly dropped two live checks — retiring a check is
itself an act that needs the same scrutiny as adding one.

## 4. Accounting

94 values = **92 OK + 2 SUPERSEDED + 0 MISMATCH + 0 UNRESOLVED**. It closes. The earlier description
"four rows testing superseded wording" conflated the two dispositions in §3; the four rows are two
`SUPERSEDED` and two re-pointed-and-passing.

## 5. The honest summary line

The closing summary listed what the arc removed — Phase 2's grade, Phase 3's order-3 reading, the
Luo–Sarnak bracket, the 3.18σ ceiling, the `0.2/√W` floor, P1's low-γ ⟨r̃⟩ leg — and called the findings
column *smaller*. True in count, and an **underclaim**, which is the same filing error as an overclaim.

Five things moved **up**, and they moved up *because* they were checked:

| | before | after |
|---|---|---|
| P1's Σ² leg | −4.49σ against a **flat** band through a **fitted** poly9 unfold | **−6.69σ** against a curvature-matched bracket through the exact θ path |
| CP1's unfold-invariance | **transferred by argument** from ζ | **measured** on Maass, 0.03–0.06σ spread, ~100× margin |
| Berry saturation | **attributed** by name | **bracketed** — 2·Var[S] = 0.3077 vs plateau 0.2829, 8% |
| Dirichlet L long-range | **"expect pass"** in a decision table | **measured**, trend ≤ 0.0033 levels, 47× below the resolution floor |
| the reach formula | four caps agreeing | **entailed** by the mass relation `2·L·α_c = 1` |

> **The summary is not "smaller." It is fewer claims, better supported, with the supports now
> regenerable.**

That distinction is the entire argument for auditing. A count of retirements measures only the first
half of what an audit does; the second half is that what survives is load-bearing in a way it was not
before, and can be re-derived by running a script rather than by trusting a document.

Sixteen defects between reviewer and CC across the arc. **Every one caught by a gate; none reached a
banked claim.** The continuation brief asserted that the protocol is the durable output and the findings
perishable. This arc measured that, in both directions, including against review — and the protocol now
verifies itself.

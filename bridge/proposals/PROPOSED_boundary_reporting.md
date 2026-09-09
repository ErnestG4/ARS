# PROPOSAL to the bridge arc — two-sided boundary reporting in `dpp_python.py`

**NOT APPLIED. `dpp_python.py` is under blob-SHA freeze** (`verify_bridge.py` checks it against the
addendum). I edited it during the 2026-08-19 overnight, the seal fired, and the edit was reverted.
Registering the change here instead: modifying a frozen file is the owning arc's call.

**The defect (latent, not live).** `fit_dpp` records
`at_boundary = bool(res.x > 0.995 * amax)` — it checks the **upper** bound, which is a genuine DPP
existence condition, and **never the lower one** (`1e-3`), which is a numerical guard that a
Poisson-like *no-repulsion* field legitimately wants to reach. So a fit railed at "no repulsion" is
reported as **a small but measured α**, and `1e-3` does not announce itself the way `0.0` does.
`fit_thomas` has **no boundary check at all** on `(1e-4, 100.0)`, where both ends are practical guards.

**Currently unexercised — measured, not assumed.** 558 banked α values, **min 0.022 (22× the bound)**;
17 banked κ values, **min 1.2 (12,000× the bound)**. Zero at a lower bound. So this is worth fixing as
cheap and latent, *not* because it is producing wrong numbers.

**Proposed change — reporting only, no bound moves:**

```python
LO_A = 1e-3
cand = dict(..., at_boundary=bool(res.x > 0.995 * amax),
            at_lower_boundary=bool(res.x < 1.05 * LO_A), alpha_min=float(LO_A))
# fit_thomas: at_lower_boundary / at_upper_boundary + kappa_bounds
```

**Why it needs the arc's sign-off rather than a drive-by:** the freeze exists so banked bridge numbers
stay reproducible from frozen code. Adding keys does not change any fitted value, but it does change
the blob, so the addendum hash must be re-derived deliberately as part of the arc's own re-seal — not
silently updated to make a checker pass, which would defeat the freeze it exists to enforce.


---

## UPDATE 2026-09-08 — one clause above is wrong: the `fit_thomas` half is LIVE, not latent

Re-checked against the banked artifacts rather than re-asserted. The "currently
unexercised" finding above is true **only of the lower bounds**. The upper bound of
`fit_thomas` is railed on **2 of 2** Thomas fits in `bridge_b_measured.json`:

| record | kappa | bound | sigma | D |
|---|---|---|---|---|
| `/B1/python_fits/thomas` | 99.99999455050113 | 100.0 | 10.0 (grid max) | 0.3863 |
| `/B2/python_fits/thomas` | 99.99999215812713 | 100.0 | 0.05 (grid min) | 13.2796 |

Both sit at 99.99999% of the bound, and in each case `sigma` lands on an endpoint
of its own `geomspace(0.05, 10.0)` grid — the signature of a fit with nothing to
find in either coordinate.

**The rail is CORRECT and its meaning is already understood.** For Thomas,
g(r) = 1 + exp(−r²/4σ²)/(4πκσ²), so κ → ∞ *is* the Poisson limit; a rail at the
upper bound is the fit saying "no clustering", not failing. `RESULTS_BRIDGE.md`
line 102 says exactly this — "Thomas degenerates to Poisson in both
implementations (python: κ→bound; spatstat: κ=256, scale=239 → flat)" — and B2's
D = 13.2796 is bit-for-bit the Poisson contrast that the same section quotes as
the 13.28 baseline. Nothing here is mis-reported and no banked conclusion moves.

**What IS wrong is the division of labour.** A human wrote "κ→bound" into prose;
the artifact carries no flag, because `fit_thomas` has no boundary check at all.
So the only record that a rail occurred lives in a sentence, and every machine
consumer of `bridge_b_measured.json` sees `kappa = 99.99999455` as an ordinary
fitted value. That is the exact gap `railed.py` exists to close, and this repo's
own rule — a rail is a DETECTOR, not a nuisance — applies to the arc that
predates it.

**Consequence for the proposal.** The `fit_dpp` lower-bound half remains latent
and cheap. The `fit_thomas` half should be re-graded: it is not a hypothetical
guard against a future railed fit, it is a missing machine record of two railed
fits that already exist and are already load-bearing (they carry the
"degenerates to Poisson" clause of a banked class-level finding). The proposed
`at_lower_boundary` / `at_upper_boundary` keys would make the prose and the
artifact agree.

Still **NOT APPLIED**, and still the owning arc's call: the change adds keys and
moves no fitted value, but it changes a frozen blob, and re-deriving that hash is
a deliberate re-seal rather than an overnight edit. What this update supplies is
the evidence for making that call — the half that looked optional is the half
with two live instances behind it.


---

## RESOLVED 2026-09-09 — as a SUCCESSOR, not an edit. The frozen file is untouched.

Operator decision: recreate rather than re-seal. That is the better call, and the
reason is the proposal's own objection turned around. The freeze exists so the
banked bridge numbers stay reproducible **from frozen code**. Editing
`dpp_python.py` and re-deriving the addendum hash would have preserved the
numbers while destroying the property the freeze was protecting — the frozen
artifact would no longer be the thing that produced them.

**What was built instead.**

- **`dpp_boundary.py`** — the boundary reporting the proposal asked for, as a
  module future fits import. It declares the bounds and then **parses them back
  out of the frozen source and compares values**, so a successor that silently
  described a different bound than the fitter it audits fails loudly. (The first
  version only checked the source still *contained* certain literals; a red path
  showed that editing a constant here left the check passing, so it now compares
  numbers.)
- **`dpp_boundary_audit.py` / `.json`** — applies it retrospectively to the
  already-banked fits, which is where the missing machine record was actually
  needed.
- **`verify_dpp_boundary.py`** — board row. Asserts, first, that
  `dpp_python.py`'s blob still matches the seal addendum.

**What the audit found, including one thing this proposal did not know.**

| | |
|---|---|
| successor vs frozen fitter | **8 agree, 0 disagree**, 4 the fitter does not report at all |
| rails with no machine record | **B1/thomas, B2/thomas** — κ = 99.99999 of 100.0 |
| *and a second coordinate* | **σ is scanned, not optimised**, and both fits land on a `geomspace(0.05, 10.0)` **grid endpoint** (10.0 in B1, 0.05 in B2). Landing on the edge of a scan is a different statement from a bounded optimiser railing, and neither was recorded. |
| DPP lower bound | **0 of 8** — unexercised, as measured above. Smallest α = 0.3535, 350× the bound. That half stays latent. |
| DPP upper bound | **4 of 8** railed — all four of B1's families — and this **is** flagged by the frozen fitter. Since α_max is a DPP *existence* condition, it means B1 wants more repulsion than any of these families can express: the family may be the wrong shape for the data. Disclosed, but it reads as a footnote. |

The 8/8 agreement is the premise: an independent tolerance that disagreed would
mean the successor measures something else. It uses a **relative** tolerance,
because an absolute one that works at κ ≈ 100 is meaningless at α ≈ 0.35.

**And this is `railed.py`'s first call site.** `guard_usage_census` (2026-09-09)
found that module had no importers — a codified rule with no call site. It was
written so a railed value refuses silent float use, and the bridge's Thomas
κ values have been read as ordinary floats since August. The guard and its case
were two directories apart. The checker now asserts the refusal actually fires:
without it this would be a document rather than a guard.

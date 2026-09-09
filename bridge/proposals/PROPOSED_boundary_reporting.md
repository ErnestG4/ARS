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

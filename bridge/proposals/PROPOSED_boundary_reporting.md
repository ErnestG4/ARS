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

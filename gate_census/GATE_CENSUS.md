# Gate census — "what should this NOT fire on, and was that ever measured?"

**The question, sharpened by the owner 2026-08-19.** The earlier framing was "find one-sided
calibrations", and the syntactic sweep for that failed its own known-positive self-test twice (see
`lcap/ESTIMAND_CENSUS.md`). The better question is per-gate and semantic:

> **Is there a NAMED SET of things this gate should not fire on, and was that set ever measured?**

A gate can have a two-sided-*looking* threshold and still never have been run against its nearest
confusable class. This census is a manual enumeration, not a grep — the deployed forms of this defect
are bare literals and single-letter variables, invisible to search and obvious to a reader.

Population: functions that assign a class or verdict from a numeric comparison. ~30 sites, many of
them the same classifier copied across `run_*.py`.

---

## GATE 1 — `arithmetic_toolkit._classify` — **FAILS, and it is the widest-blast-radius gate in the repo**

**Depended on by 93 files.** Verdict assignment is:

```python
best = min([('Poisson', ks_p), ('GOE', ks_o), ('GUE', ks_u)], key=lambda x: x[1])[0]
```

**Named negative set: NONE.** The only refusal is `n < 5` → `'insufficient'`. There is no
goodness-of-fit threshold and **no 'none of the above' branch**. So its specificity against a
non-member distribution is not merely unmeasured — it is **structurally zero by construction**. Every
input with n ≥ 5 is assigned one of three classes.

**Ever measured: no.** Measured now (`gate1_specificity.py`, n = 2000 each):

| input (none of the three classes) | verdict | best-fit KS | vs KS crit (α=0.01) |
|---|---|---|---|
| **perfect clock** (all spacings equal) | **GUE** | 0.533 | **15× the critical value** |
| uniform spacings U(0,2) | GOE | 0.091 | 2.5× |
| lognormal spacings | Poisson | 0.104 | 2.9× |
| bimodal (0.2 / 1.8) | Poisson | 0.334 | 9× |
| clustered (Neyman–Scott-ish) | Poisson | 0.535 | 15× |
| constant 0.5 + noise | **GUE** | 0.533 | 15× |
| *true Poisson (contrast)* | *Poisson* | *0.012* | *FITS* |

**7/7 non-members received a confident class label, and every best fit is rejected by a standard KS
test.** Note the first row: **a perfect clock reads GUE.** That is the RIGID_GUE failure — a clock
earning the GUE pole — reached through an entirely different gate by an entirely different mechanism.
The same wrong answer arrived at twice independently is a statement about the *question* these gates
are asked, not about either implementation.

**This is a distinct defect class from one-sided calibration: an ARGMIN WITH NO NULL OPTION.** A
selection among candidates is not a test. It has no rejection region, so it cannot be wrong in the
direction of "none of these" — and that direction is where every non-member lives. Same shape as the
argmax-has-no-location-error-bar lesson banked earlier the same day: *a selection reported as a
verdict.*

**Repair applied, non-breaking.** The information needed to refuse was **already computed** — the
function returns all three KS distances. Added `best_ks`, `ks_crit_01`, `fit_rejected`; `best` and
every pre-existing key are **bit-identical**, so no banked number moves and callers gain a refusal
they can consult. Verified: pre-existing keys unchanged on a true-Poisson input; perfect clock now
reports `fit_rejected = True` alongside its unchanged `best = 'GUE'`.

**Not yet done — the downstream question this opens.** 93 files consume `best`; none of them checked
fit quality because none was exposed. **How many banked classifications sit on a rejected fit?** That
is now a cheap sweep and it is the natural next step of this census.

**Contrast — `sessionK/nns_stats.classify_empirical` PASSES the precondition half.** It refuses on
`n < 200` and on mean spacing outside (0.7, 1.4) — *"not a unit-density point process"* — a genuinely
named negative set. But it still ends in a bare `min(scores, ...)` with no fit-quality rejection, so
it refuses on **preconditions** and not on **goodness of fit**. Partial pass: the negative set exists
and is named, but does not cover the non-member case.

# C1 — bounded-solver classification, SEALED BEFORE ANY RAIL FRACTION IS READ

**Ordering is the point.** The convention-vs-mathematical call is the one genuine judgement in this
cell, and it is exactly where post-hoc rationalisation lives: classifying a bound as "mathematical"
*after* seeing it rails 40% of the time is motivated reasoning with a clean audit trail. So each site
is classified **from its parameter's definition alone**, with the reason recorded, and this file is
committed in its own commit **before** rail fractions are measured. Commit order is the evidence, not
the existence of two files.

**The criterion (same one asked of class spaces):** *what lies beyond this endpoint, and can data
legitimately go there?*

- **CONVENTION** — the endpoint is a modelling choice; data can legitimately lie beyond it. Fix is to
  move or remove the bound. *(Not this session — no bounds move.)*
- **MATHEMATICAL** — the endpoint is a real limit of the parameter's definition. Saturation there is a
  substantive answer. Still needs the rail **reported**, because a value *at* a true bound and a value
  *near* it mean different things.

| # | site | parameter | bound | what lies beyond | class | reason |
|---|---|---|---|---|---|---|
| 1 | `axes.py:160` | Brody q | (0.0, 1.0) | **q<0 = super-Poisson / clustering; q>1 = GUE≈2, GSE≈4** | **CONVENTION** | Brody's interpolation was *defined* on [0,1] to span Poisson→GOE. That is the model's historical range, not a constraint on the parameter — clustered and higher-β data are physically ordinary and lie outside it. |
| 2 | `axes.py:191` | Brody q (repaired) | (−1.0, 4.0) | q<−1 for extreme clustering | **CONVENTION (wider)** | "Unbounded" is a misnomer; the bound moved, it did not vanish. Same class as #1, chosen wide enough to contain observed data. |
| 3 | `axes.py:246` | Berry–Robnik ρ | (0.0, 1.0) | **nothing** | **MATHEMATICAL** | ρ is the *fraction of phase space* that is regular. A fraction outside [0,1] is undefined, not merely unobserved. ρ=0 and ρ=1 are the pure limits (fully chaotic / fully regular) and are real answers. |
| 4 | `phase34e/run_berry_robnik.py:128,144` | Berry–Robnik ρ | (0.0, 1.0) | nothing | **MATHEMATICAL** | as #3, same parameter. |
| 5 | `brody_cut_diagnostic.py:34` | Brody q | `(lo, hi)` **required args** | caller's choice | **CALLER-DETERMINED** | No default exists; the classification belongs to each call site, not to this function. |
| 6 | `overnight_2026_07_12/run_overnight.py:346` | Brody q | (−1.0, 4.0) default | as #2 | **CONVENTION (wider)** | already the repaired form. |
| 7 | `bridge/dpp_python.py:72` | DPP α | (1e-3, `amax`) | **α→0 = no repulsion — reachable**; α>amax is a genuine DPP existence violation | **MIXED: lower CONVENTION, upper MATHEMATICAL** | The upper bound is a real existence condition. The lower is a numerical guard: a Poisson-like (no-repulsion) field legitimately wants α→0. |
| 8 | `bridge/dpp_python.py:86` | Thomas κ | (1e-4, 100.0) | **κ→0 = no clustering — reachable**; κ=100 is arbitrary | **CONVENTION both ends** | Both are numerical/practical guards; a non-clustered field wants κ→0 and a very clustered one can exceed 100. |

**Prediction committed with the classification** (so the rail fractions are a test, not a description):
sites 1/2/6 (Brody) should show substantial rails; sites 3/4 (ρ) should show rails only rarely, and
those rails should be *real answers* rather than artifacts; sites 7/8 should show rails only if the
data actually contains non-repulsive / non-clustered fields.

**Out of scope this session:** moving any bound. Classification and reporting only.

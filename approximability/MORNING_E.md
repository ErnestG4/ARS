# MORNING_E — sparse π-292 eigensolve: certified module, but depths 6–8 blocked on COMPUTE (not RAM)

Branch `pi292-sparse-eigensolve` off `main`. `$HOME/fmexplorer/bin/python3`, `PYTHONPATH=…/riemann_explorer`,
`BASE_SEED=20240517`. New machinery (a new sparse module); the certified dense Floquet engine and the refsuite are
untouched. **The seal `pi292_prediction_SEALED.json` was NOT opened — no measurement ran, so there is nothing to
compare and opening it would only bias a future run.**

## Pre-flight + layer-zero
- **q confirmed against fresh CF:** π = [3;7,15,1,292,…]; q₅=33215, q₆=66317, q₇=99532, q₈=265381 (asserted, not taken
  from the spec).
- **GATE 1 (operator identity):** the on-site term is the Sturmian step `λ·χ_{[1−p/q,1)}` from `task1_pi_depth5.potential`
  — same certified assembly as through depth 5, periodic+antiperiodic corners as in the dense engine. No operator drift.
  (Consistent with Session D: Sturmian, not AMO.)

## The correctness core — a CERTIFIED completeness oracle (real deliverable)
Artifacts: `sparse_floquet.py`, `certify_sparse.py`.
- **Cyclic-tridiagonal inertia (Sturm) count** `inertia_cyclic(V,E,corner)`: exact number of eigenvalues below E via
  LDL pivot signs of (H−E·I), derived for the tridiagonal-plus-corner (periodic/antiperiodic) operator, **O(q) memory**.
  Guaranteed complete by Sylvester's law of inertia — this makes **`count_eq_q` rigorous, not hopeful** (the central
  risk the spec named). Certified: exact match to dense eigenvalue counts at q=113, both BCs, across 40 energies.
- **Identity used:** `W = ∫|N_P(E) − N_A(E)| dE` — the periodic/antiperiodic counting functions differ by exactly 1 on
  the spectrum, so band widths are anchored to the same complete counts.
- **Complete solver** `bands_W(V)`: inertia-guided (stebz-style) bisection finds all q edges for each BC, pairs the
  sorted 2q edges exactly as the dense engine (`edges[1::2]−edges[0::2]`), enforces `count_eq_q` by assertion.

## GATE 3 (make-or-break certification vs dense on the overlap) — PASS
| substrate | q | count_eq_q | W rel-err vs dense | dim sparse / dense |
|---|---|---|---|---|
| π | 113 | ✓ | 2.9e-12 | 0.62761 / 0.62761 |
| fifth | 306 | ✓ | 2.0e-08 | 0.43154 / 0.43154 |
| fifth | 665 | ✓ | 1.8e-08 | 0.42016 / 0.42016 |

The new module **reproduces the certified dense engine** — W to ~1e-8, **dim exact to 5 digits**, completeness
rigorous. The sparse path is *trusted*. (Certified on the overlap; the earlier eigsh-shift-invert prototype was
abandoned — it **timed out at q=15601**, too slow for all-eigenvalue extraction.)

## The wall — and it is NOT the RAM wall the block targeted
The banked blocker was "dense storage q²·8 = 35/79/563 GB > 15 GB." The inertia route **solves that** — it is O(q)
memory, so q₈=265381 fits easily. The real blocker **moved to COMPUTE**: the inertia recurrence is O(q) *per eval* and
**un-vectorizable across its own sequential (recurrence) dimension**, so full extraction is O(q²·bisection-depth).
Measured: q=665 → 7.7 s ⇒ **q₆=66317 ~20 h, q₈=265381 ~weeks**. And **no JIT is available** (numba and cython both
absent in this env); the one compiled complete tool, `eigvalsh_tridiagonal` (LAPACK stebz), **cannot handle the cyclic
corner**. So a fast complete solve is out of reach in-session.

## Verdict — machinery outcome, banked plainly
**Depths 6–8 do NOT run this session.** But this is *not* "sparse path uncertified": the module **is certified on the
overlap (gate 3 PASS)** and the completeness core is correct. The precise status is:
**certified-and-trusted, but compute-bound at scale, blocked on the absence of a compiled inner loop.**
- **Refined blocker (durable):** π-292 depths 6–8 are **compute-bound, not RAM-bound**. The RAM wall is defeated by the
  O(q)-memory inertia oracle; what remains is an O(q²) pure-Python recurrence with no JIT.
- **Exact unblock for the dedicated run:** install **numba** (JIT `inertia_cyclic` → ~100–1000× → q₆ in seconds, q₈ in
  minutes), or drop the recurrence into cython/C, or find a compiled cyclic-tridiagonal routine. The correctness core
  and the certification harness are already built here — the future session is then a pure execute-then-unseal run.
- **Seal stays locked.** The Session-D prediction (flat 4→5 ≈0.680, then monotone retreat 0.680→0.636→0.622→0.591,
  depth-7 softest, falsifier sealed) is untouched, awaiting the compiled run.

## Close
- Committed on branch; main + refsuite untouched. Carry-forward: the π-292 dedicated run now needs only a **compiled
  inertia backend** (numba/cython) — the RAM wall is gone, the operator/completeness/certification are done, and the
  sealed prediction is ready to test. Still queued unchanged: genus>0 FF calibrator (+β≈⅓·ln q), Gauss/Kloosterman
  concentration axis, the CF-cusp divergence-profile candidate.

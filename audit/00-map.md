# 00 — Cartography

**Audit target:** working tree at `$HOME/fmexplorer/criticality_tool`, which **is** the repo
`https://codeberg.org/Combust/ARS.git` (confirmed `git remote -v`). Branch **`master`** (HEAD `1a6c7a1`).
`origin/main` exists and has diverged; this audit targets `master` as-is (where README/RESULTS/CAPABILITY_REPORT live).

**Scope decision (ratified with the user):** *canonical + drift-diff.* Audit the canonical/live tool surface in full;
treat the ~30 `phaseNN/` dirs as application drivers + claim-sources, and diff the duplicate estimator copies for drift
rather than re-auditing every copy's math line-by-line.

**Completeness note:** This map tags the *core tool surface* per-file and the `phaseNN/` experiment dirs at a coarser
group grain (one row per dir). That is deliberate, not theater: 402 `.py` files / ~88k LOC, and the phase dirs are
mostly per-experiment scratch that re-imports the core. Role tags: `[code]` read from executable code, `[documented]`
from a docstring/comment, `[inferred]` deduced.

---

## Scale

| metric | value |
|---|---|
| `.py` files (excl. `.git`, `__pycache__`) | 402 |
| total Python LOC | ~87,800 |
| top-level `.py` files | 102 |
| `phaseNN/` + `cross_substrate/` dirs | ~31 |
| files with `if __name__=="__main__"` | 41 (top-level) |
| package manifest (`setup.py`/`pyproject`/`Makefile`) | **none** |
| CLI / argparse | 1 top-level file uses argparse — **no unified CLI** |

## Directory tree (depth 1, by Python LOC)

```
cross_substrate/   93 py  18,872 LOC   the LIVE program: axes.py instrument + ~30 substrate ports
phase35a/          32 py   6,891 LOC   AM slicing-comparison arc
phase31b/          26 py   4,749 LOC   engineering audit / classifier
tests/             14 py   1,849 LOC   pytest suite (14 test files)
phase22a/          14 py   3,092 LOC
phase24/            8 py   2,121 LOC
phase34d/          11 py   2,085 LOC   RW-variance / Eisenstein
phase30/            7 py   1,824 LOC   Kuramoto
phase34e/           9 py   1,630 LOC   Maass forms
phase34c/           9 py   1,656 LOC   ζ/Dirichlet/EC L-zeros
phase22b/ … phase37/  (~20 more phase dirs, 174–1,586 LOC each)
internaldocs/       1 py      91 LOC   (git pre-commit denylisted — not committed)
data/ plots/ signals_cache/ allen_cache/ … (data + artifact dirs, 0 py)
```

## Core tool surface (per-file, `[code]` unless noted)

| file | LOC | role |
|---|---|---|
| `arithmetic_toolkit.py` | 812 | **RF engine + deployed classifier.** `ramanujan_fourier:130`, `joint_q_profile` (produces `rf_amp_per_q`), `joint_quadrant_diagnostic:724` (the deployed marginal verdict). |
| `cross_substrate/axes.py` | ~470 | **LIVE multi-axis instrument.** Family I (I.1–I.13 marginal NNS/CV/CV2/Lv), Family II (Σ²/Δ₃/K long-range), Family III (RF), Family V/VI (chaos). Bare estimator bank — emits floats, no verdict, no guard. |
| `universality.py` | — | Canonical reference forms: `number_variance:126`, `spectral_form_factor:173`, `pair_correlation`, Wigner GUE/GOE surmises. Source of the GOE/GUE curves fixed in `1a6c7a1`. |
| `pll_bank.py` | 396 | PLL lock-extraction instrument (the FM front-end). |
| `surrogates.py` | 477 | Surrogate / induction-on-noise null generators. |
| `run_analytical_nns.py` | 327 | Canonical arithmetic NNS driver (`analytical_nns:84`). |
| `intermittency.py`, `signal_gen.py`, `bulk_recovery.py`, `extractors.py`, `llm_cascade.py`, `field_generator.py` | — | supporting front-ends (signal gen, extraction, LLM-cascade substrate). |
| `cross_substrate/longrange_discriminator.py` | — | Family-II long-range verdict (`longrange_verdict`) — the **only** runtime-guarded verdict path. |
| `cross_substrate/calibration_anchors.py` | — | Canonical "GUE/Poisson/clock → live axes" self-validation — **zero importers** (see 04-guardrails). |
| `instrument_confound.py` | — | Apparatus-subtraction stage. |

Most-imported internal modules (the real dependency hubs): `arithmetic_toolkit` (41 importers),
`universality` (26), `pll_bank` (24), `signal_gen` (16), `intermittency` (11), `bulk_recovery` (9).

## Entry points

- **No unified CLI / no package.** Each analysis is a hand-run top-level script: `run_phaseNN_*.py`, `run_<substrate>_nns.py`, `run_<thing>.py` (102 top-level scripts, 41 with `__main__`).
- **Public library surface** (imported, not run): `arithmetic_toolkit`, `universality`, `pll_bank`, `cross_substrate/axes.py`, `surrogates`, `signal_gen`.
- **Tests:** `tests/` (14 `test_*.py`) — runnable via pytest; covers `as_topology, bgp_pipeline, bulk_recovery, dfa, distinctness, extractors, intermittency, joint_q_profile, llm_extractors, pll(+gpu), surrogates, transition_calibrators`. **No test imports `cross_substrate/axes.py` or `universality.number_variance`** — the live instrument + long-range kernels are untested by the suite (`[inferred]` from test-file import scan; spot-verify in Phase 5).
- **Notebooks:** none found.

## How you run this thing

```bash
# deps (no package install — scripts are run in place)
pip install -r requirements.txt          # numpy scipy matplotlib h5py mpmath joblib cupy-cuda12x pyedflib
# run an analysis (per-script, from repo root) — MUST use the project venv (pandas/numpy live there):
$HOME/fmexplorer/bin/python3 run_analytical_nns.py
$HOME/fmexplorer/bin/python3 cross_substrate/<port>.py
# tests
$HOME/fmexplorer/bin/python3 -m pytest tests/
```

- GPU optional (CuPy/`cupy-cuda12x`); code falls back to CPU if CuPy not importable `[documented]` (requirements.txt comment).
- **Git guardrail (active):** `.githooks/pre-commit` + `core.hooksPath=.githooks` — a content denylist that aborts commits touching `_tentative_review/`, `internaldocs/`, `*-allfrm-contaminated.jsonl`, `*.zip`. This is a **provenance** guard (never-commit hold), **not** an estimator-validation guard. `[code]` `.githooks/pre-commit:1-37`.

## Calibrator/test harness wiring (preview — full trace in `04-guardrails.md`)

Calibrators and falsification harnesses exist and are mostly **runnable but disconnected** hand-run scripts. The live
instrument `cross_substrate/axes.py` runs **no** calibrator / surrogate / decoy check at compute time. Only the
Family-II `longrange_verdict` builds calibrator references at call time. See `04-guardrails.md`.

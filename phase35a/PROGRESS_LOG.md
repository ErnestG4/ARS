# PHASE 35 SLICING — PROGRESS LOG (work-in-progress; NOT validated results)

**Status:** progress logging only (Will 2026-05-19: "log our progress …
not … overall results"). These artifacts are **instrument-diagnosis /
HALT-class, SURFACED not adjudicated.** They are **not** validated
results, **not** RESULTS.md/§8 material, and do **not** adjudicate
(A)/(B), §D, or Step-1. The **decision record** (`memory/
phase35_am_arc_design.md`) is authoritative for interpretation and
status. (A)/(B) discrimination, §D-DGY, the Step-1 exposure, and any
verdict remain **open and Will's**.

## Artifacts (factual manifest only — no interpretation here)

| Artifact | What it is | Factual terminal / state |
|---|---|---|
| `slicing_outer_t0_t2core.py` | outer-rung T0+T2-core run script (WORKERS=50 = faithful record of the completed server run) | — |
| `slicing_outer_t0_t2core_results.json` | that run's result (server, 768 tasks, 0 err) | `T0_NO_OUTER_PAIRS`; all 8 sub→INNER, all 8 sup→OUTER; δ_res=ladder-max — a clean HALT (apparatus refused to stamp uncertifiable vary-N) |
| `run.log` | the `slicing_outer` server run log (pulled local) | completed 9193 s, detachment held |
| `sub_resolution_probe.py` (+`_results.json`,`_rawtable.json`) | pre-DGY probe, sub N∈{100k,125k,150k} (local, bxtbmjoqv) | `SUB_NONFLAT_OR_PLATEAU_INDETERMINATE`; W1δ 0.01→0.40→0.667 δ-independent; cross-env determinism exact |
| `sub_cliff_L_robustness.py` (+`_results.json`,`_rawtable.json`) | local-repro + L-robustness (local, b626clevu) | Q1=`CLIFF_REPRODUCES_LOCAL`; Q2=`PLATEAU_L_SENSITIVE` (the ≈0.34 plateau is L_iter-underconverged) |
| `sub_Liter_convergence.py` | L_iter-convergence sweep script (server run **in progress**, 48w, PID 877391; results pending — not yet local) | run not finished at commit time |
| `fib_neighborhood_log.txt`, `fib_neighborhood_results.json` | earlier overnight-explorer sub-phase (Fibonacci-neighborhood structure run) progress data | prior sub-phase; committed for the log |

## Discipline carried (unchanged)

- `_HALT`/INDETERMINATE over stamp; pre-registered + full-coverage
  smoke-verified before each run; hardened (rawtable persist + 64-ckpt
  + analyze-only); §5 apparatus-invariance; never proves (A)/(B) (only
  §D/DGY); no §3, no Class-II.
- **Banked Step-1 untouched / not retro-adjudicated.** The (A)-flavor
  evidence (`PLATEAU_L_SENSITIVE`) raises the Step-1 exposure Will
  identified — **flagged, open, Will's to adjudicate**, not concluded.
- **Excluded from the repo deliberately:** `_tentative_review/` (Will's
  standing not-in-repo instruction); `phase28/*` (pre-existing,
  unrelated to this arc — left untracked for Will).

This log is a progress checkpoint, not a findings doc. No verdicts.

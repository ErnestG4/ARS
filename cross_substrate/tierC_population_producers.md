# Tier C — producers + reproduction commands for the five remaining Brody files

Recon only, 2026-07-31. No producer was run; nothing in `coordinates/` was written.
Repo: `/home/combust/fmexplorer/criticality_tool`. Python: `/home/combust/fmexplorer/bin/python3`.

## Headline

| file | rows | producer | object set matches today | determinism | FAMILY_I | verdict |
|---|---|---|---|---|---|---|
| `population-strat.jsonl` | 1456 (1454 q) | `cross_substrate/population_strat.py` | **EXACT** | I.8 exact expected | **iterates** | REPRODUCIBLE (must move bank aside first) |
| `pvc-11.jsonl` | 1159 | `cross_substrate/phase2b_recompute.py` | **EXACT (same order)** | fully deterministic | **iterates** | **BLOCKED — fitter gate now False** |
| `quasiperiodic-operators.jsonl` | 216 | `cross_substrate/quasiperiodic_operators.py` | **EXACT** | I.8 exact expected | **iterates** | REPRODUCIBLE (~1 h) |
| `population-fingerprint-all.jsonl` | 96 | `cross_substrate/population_fingerprint.py` | **EXACT** | I.8 exact expected | **iterates** | REPRODUCIBLE (must move bank aside first) |
| `population-fingerprint.jsonl` | 8 | `cross_substrate/population_fingerprint.py` | **EXACT** | I.8 exact expected | **iterates** | REPRODUCIBLE (mode `"w"`, always truncates) |

**All five files are git-TRACKED** (checked each individually, per the
`UNTRACKED_FILES_NOTICE.md` lesson) — an accidental overwrite is git-recoverable.
Take the out-of-repo baseline anyway.

**None of the five is derived from another coordinate file.** The `source_artifact:
"generated (... aggregation)"` string on `population-*` means *aggregated across units
within a raw Allen NWB*, not *aggregated from other jsonl*. There is no run-order
dependency between these five files. (`pvc-11.jsonl` is the one with a real ordering
constraint — see below.)

---

## 1. `population-strat.jsonl` — 1456 rows, 1454 with `I.8_brody_q`

### Producer
`cross_substrate/population_strat.py`
- `open(...)` at **`population_strat.py:153`** — `fh = open(out, "a" if done else "w")`,
  where `out` is built at `population_strat.py:140`.
- Sole writer (grepped the whole repo for the literal string). `population_strat_analysis.py:37`
  and `population_ratematch.py` only *read* it.

### Command
```bash
/home/combust/fmexplorer/bin/python3 cross_substrate/population_strat.py --run --all --workers 8
```
- `--run` — required, used (`main():180`).
- `--all` — **genuinely used**: `run(a.sessions, all_sessions=a.all, ...)` at `:181`, and
  `all_sessions` is dereferenced in the body at `:138`. Omitting it truncates `files` to
  `files[:1]` → 1 session (~40 rows), not 12. This is the buzsaki-style direction of the flag.
- `--sessions N` — used only when `--all` is absent.
- `--workers` — used; affects speed only (results are per-task pure, `ex.map` preserves order).

### ⚠ The resume logic makes a naive re-run a NO-OP, then a silent APPEND
`run()` reads the existing `population-strat.jsonl` into `done` keyed by
`(session, area, block)` (`:141-147`), filters every task against it (`:148-149`), and
then opens the file with `"a"` because `done` is non-empty. With the bank in place the
run computes **0 tasks and writes nothing** — it will *look* like it succeeded.
If the bank is only partially removed you get an **append**, i.e. duplicate rows.

**Correct procedure:** move the banked file out of `coordinates/` first (`mv`, not `cp`,
so `done` is empty and the mode is `"w"`), run, then gate the new file against the moved copy.

### Object set — **EXACT MATCH, verified**
Determined by `build_targets()` + `NWB_GLOB` from `cross_substrate/allen_depth.py:54`
(`$HOME/fmexplorer/allen_cache/session_*/session_*.nwb`), then filtered by
`MIN_UNITS = 30` per `(session, area)` and the fixed 8-element `BLOCKS` list.

Re-derived `build_targets()` today (read-only) and compared to the bank:

- NWB glob matches **12** files today; bank covers **12** sessions — identical id lists.
- `(session, area)` pairs with ≥30 good units: **61 today, 61 banked, zero difference
  in either direction.**
- `n_units` per `(session, area)`: **0 mismatches across all 61 pairs.**
- Distinct `(session, area, block)` triples: 488 banked = 61 × 8.
- **Row order:** I reconstructed the producer's emission order
  (`sorted(glob)` → `BLOCKS` in listed order → `sorted(areas)` → dict order
  `corr-eig, avl-onset, sync-event`) and it is **byte-for-byte the banked order**.
  This is strong independent evidence the identified producer is the actual one and
  that the bank came from a single uninterrupted 12-session run.

`allen_cache/units.csv`, `probes.csv`, `channels.csv` are all dated 2026-05-10, i.e.
*before* the 2026-05-24 bank and unchanged since. No Allen session has been acquired since.

### Determinism
- `np.polyfit` (deg 10, emits `RankWarning`) is in the path — `population_fingerprint.py:74`,
  reached via `_corr_eig` — but **only for the `corr-eig` rows (480 of 1456)**.
  The 976 `avl-onset` / `sync-event` rows go straight through `canonical_spacings` with
  no polyfit at all.
- `I9_berry_robnik_rho` calls `_fit_br_rho(s, n_bootstrap=1)`; the bootstrap RNG is
  `np.random.default_rng(b)` with `b=0` (`phase34e/run_berry_robnik.py:136`) and only
  `rho_mle` — computed *before* the bootstrap — is banked. So I.9 has no RNG of its own;
  its observed 3rd-decimal drift comes from the ill-conditioned polyfit upstream.
- **`I.8_brody_q` should reproduce EXACTLY.** Empirically it did not move on any ibl
  population row (`RESUME_TIER_B.md` item 4). `I8_brody_q` is a bounded `minimize_scalar`
  with `xatol=1e-4` — coarse enough to absorb the polyfit jitter.
- **Expect `I.9_berry_robnik_rho` (and possibly Family II) to move in the 3rd decimal on
  some `corr-eig` rows.** That is not a gate failure; the gate is on I.8.

### FAMILY_I
**Iterates.** `population_strat._task:94` → `population_fingerprint._fp:86` →
`{k: _f(fn(s)) for k, fn in FAMILY_I.items()}`. The repaired axis arrives with no code edit.
The re-run will also add `I.10_cv` and `I.11_mass03` (added to `FAMILY_I` after the bank).
It will **not** add `I.12_cv2` / `I.13_lv` — `_fp` does not merge `family_local()`.

### Gate power ⚠
1454 non-null values, but **606 (41.7%) sit on an exact-value pileup** (the optimiser rail
at `6.610696135189609e-05` ×471 and `0.9999338930386481` ×135). **848 rows carry a unique
value** — that is where the gate's discriminating power actually lives. Adequate.

### Feasibility
Raw data present: 29 GB Allen NWB cache, 12 sessions, ~2.4 GB each. Disk has 738 GB free.
**This is the expensive one.** Each of the 488 tasks re-opens its NWB and, for every unit in
its area, slices the *full* `units/spike_times` range before windowing — so the same session
is read once per (block × area). Expect **many hours, I/O-bound on a rotational disk**;
the module docstring itself says "Incremental + resumable per session (I/O-bound)".
Memory is small per worker (count matrix + pooled spikes); `--workers 8` is safe under the
15 GB budget, and more workers will not help (single-stream disk).

**Extend the verifier:** `cross_substrate/verify_brody_repair.py` has no `KEYS` entry for
this substrate. Add `"population-strat": ("session", "area", "block", "aggregation")`.

---

## 2. `pvc-11.jsonl` — 1159 rows — ⚠ **BLOCKED**

### Producer (two-stage; the Brody axis comes from stage 2)
1. `cross_substrate/harvest.py::harvest_pvc11:134` writes the file from
   `data/phase22a_results/h1_classifications.parquet`. `open(...)` at
   **`harvest.py:333`** (`write_jsonl`, mode `"w"`). It emits **only** `I.5q_ks_gue_med`,
   `ARS.rep_med`, and Family III — **no Family I at all**.
2. `cross_substrate/phase2b_recompute.py::recompute_pvc11:69` reads the file back,
   recomputes Family I + II from raw spikes, merges in place, and rewrites.
   `open(...)` at **`phase2b_recompute.py:109`** (`_write`, mode `"w"`).

**The banked Brody values are stage 2.** Confirmed: commit `015f758` (2026-05-23 17:21)
"Family-II consistency re-run: pvc-11 + arithmetic … Re-ran phase2b_recompute (pvc-11, 1159)",
matching the banked `extraction_audit.object_a_recompute.date == "2026-05-23"`.
(`cross_substrate/phase2b_pvc11.log` is the *earlier* 2026-05-21 run: 336.9 s, 1159 cells.)

**Run order matters:** `harvest.py` opens `pvc-11.jsonl` with `"w"` and would erase every
Family I/II axis. **Do not run `harvest.py`.** Run stage 2 only.

### Command
```bash
/home/combust/fmexplorer/bin/python3 cross_substrate/phase2b_recompute.py pvc-11
```
- positional `substrate` — used (`:128`).
- `--dry-run` — used (`:147`); computes and reports without writing. Useful, but it prints
  only one example row, so it cannot serve as the gate.
- **`--limit N` — used, and it is a DATA-DESTROYING flag.** `recompute_pvc11` does
  `recs = recs[:limit]` (`:72-73`) and `main` then calls `_write(path, recs)` unconditionally
  (`:150`) — so `--limit 10` **truncates `pvc-11.jsonl` from 1159 rows to 10.**
  Never use `--limit` without `--dry-run`.

### ⚠⚠ BLOCKER — the fitter gate is now `False` and would NULL the banked axis
`_matched_axes:59-66`:
```python
if not gate_pass:
    fI["I.8_brody_q"] = None
    fI["I.9_berry_robnik_rho"] = None
```
`_fitter_gate()` reads `cross_substrate/fitter_validation.json["all_pass"]`.
- Banked rows record `"fitter_gate_pass": true` (2026-05-23).
- **That file today has `"all_pass": false`** (mtime 2026-07-27, commits `38aadc5` /
  `762a56c` added `clustered`, `clustered_extreme` and re-registered the GUE expectation
  at 1.53 — the bounded fitter fails 3 of 5 cases, which is exactly the defect the repair
  addresses).

So a re-run today would write `I.8_brody_q = None` for **all 1159 rows**, destroy the
banked axis, and fail the reproduction gate by construction — while still emitting
`I.8_brody_q_unbounded` (the gate does not null the repaired key). **Repaired values from a
run that cannot reproduce its own bank are exactly what the gate exists to reject.**

Resolutions, all requiring a decision that is not mine to make:
- (a) Write a read-only reproducer modelled on `cross_substrate/hc3_reproduce_bank.py`
  and `cross_substrate/recompute_coordinates_pvc11.py` — recompute into a **new**
  `pvc-11.repaired.jsonl`, reproduce the deployed `I.8_brody_q` *bypassing* the gate,
  and only merge after it matches 1159/1159. This is the pattern the repo already uses
  for the `rep_med` repair and it is non-destructive by construction.
- (b) Scope the gate to the axis it is about (it currently gates the *bounded* fitter on
  a validation suite the *bounded* fitter is now known to fail). A change to deployed
  gate semantics — Will's call.

### Object set — **EXACT MATCH, verified**
Identity comes from the bank/parquet itself, not from a glob — the strongest possible
position. Compared `data/phase22a_results/h1_classifications.parquet` to the bank:
- 1159 rows both sides; `{recording}/{unit_id}/{condition}` cell_ids **identical as sets
  AND in identical order**; zero rows on either side only.
- 15 recordings, per-recording counts identical.
- `condition` is `pooled` for all 1159 — consistent with `recompute_pvc11:92` calling
  `recording.concatenated_spikes(u)` with no condition argument.
- Raw data present: `data/pvc-11/data_and_scripts` (416 MB incl. the tarball).

Note the loader maps `cell_id → unit` via `recording.unit_id(u)`; a unit not found is
flagged, not dropped, so the row count cannot shrink.

### Determinism
**Fully deterministic. No RNG, no bootstrap, no polyfit anywhere in this path.**
`concatenated_spikes` → `unfold_unit_mean` → `canonical_spacings` → bounded
`minimize_scalar` fits. `I.8_brody_q` must reproduce bit-identically.

Family II *values* are post-`ef98c28` (capped-window Σ²/Δ₃) because of the 2026-05-23
consistency re-run, so they should reproduce too.

### FAMILY_I
**Iterates**, via `compute_family_I` (`axes.py:349`). Also merges `family_local`, so the
re-run adds `I.10_cv`, `I.11_mass03`, `I.12_cv2`, `I.13_lv` alongside the repaired axis.

### Gate power ⚠⚠ — nearly vacuous on I.8 alone
**1152 of 1159 values (99.4%) are the single rail value `6.610696135189609e-05`.**
Only **7 rows carry a unique value.** Any clustered spike train returns that rail, so
"I.8 reproduced" would pass even on a materially different object set.
**Gate pvc-11 on the full `axes_computed` vector** (`I.1_w1_clock`, `I.2_w1_gue`,
`I.5_ks_gue`, `II.1_sigma2_L`, `II.2_delta3_L` are all continuous and cell-specific),
not on I.8. Add `"pvc-11": ("cell_id",)` to `verify_brody_repair.KEYS` and extend its
comparison set.

### Feasibility
337 s single-process for the 2026-05-21 run (290 ms/cell, serial — no pool in this script).
Expect ~450–700 s now with 5 extra Family I axes (two Brody fits instead of one).
Memory: one `Recording` at a time (rebound each loop iteration), well under 15 GB.

---

## 3. `quasiperiodic-operators.jsonl` — 216 rows

### Producer
`cross_substrate/quasiperiodic_operators.py`
- `open(...)` at **`quasiperiodic_operators.py:137`** — `with open(os.path.join(COORD,
  "quasiperiodic-operators.jsonl"), "w")`. **Unconditional mode `"w"`, no resume logic.**
- Sole writer. `cf_mechanism.py:85` and `cf_discriminator.py` only read it.

### Command
```bash
/home/combust/fmexplorer/bin/python3 cross_substrate/quasiperiodic_operators.py --sweep --workers 8
```
- `--sweep` — required and used (`main():213`).
- `--workers` — used; speed only.
- `--probe` — prints 8 cells, writes nothing. Good pre-flight.

Note `sweep()` also calls `_figure(by)` at `:167`, which overwrites
`cross_substrate/figures/P_qpo_approx.png`. Harmless but not a no-op on disk.

### Object set — **EXACT MATCH, fully in-code**
No data files, no glob, no seed. Pure enumeration at `:121`:
`4 OPERATORS × 9 CLASSES × 6 COUPLINGS = 216`, with `N = 50_000`, `N_PHI = 8`.
Bank: 216 rows, 54 per operator, operator/class/coupling sets identical to the constants
in the file today, `extraction_audit == {"irrationality_measure": …, "N": 50000, "n_phi": 8}`.
`ex.map` preserves task order, so row order is reproducible too.

The θ constants are computed from `np.sqrt`/`np.log`/`np.e` at import — bit-stable.

### Determinism
- **No RNG.** But `poly_unfold` (`sturmian_hamiltonian_run.py:61`, `np.polyfit` **deg 12**)
  runs on **every one of the 8 φ-realisations of every row** — the polyfit exposure here is
  100%, higher than the population files. LAPACK `eigvalsh_tridiagonal` / `eig_banded` are
  deterministic for a fixed thread count; the module pins `OMP/OPENBLAS/MKL/NUMEXPR/VECLIB`
  to 1 at `:23-25` before importing numpy, so the pinning is effective.
- `I.8_brody_q` fits pooled spacings from 8×50 000 eigenvalues — enormous n, `xatol=1e-4`.
  **It should reproduce exactly**, and 193/216 rows are already pinned at the rail so they
  cannot move at all. The residual risk is confined to the ~23 interior rows.
- If any row does drift here, suspect the ill-conditioned deg-12 polyfit, not the fitter.

### FAMILY_I
**Iterates** — `_fingerprint:109`, `{k: _f(fn(pooled)) for k, fn in FAMILY_I.items()}`.
Re-run also adds `I.10_cv`, `I.11_mass03`. `IV.2_spectral_box_dim` is appended separately
and is unaffected.

### Gate power ⚠
193/216 (89.4%) on a pileup; **23 rows uniquely valued**. Weak but not vacuous — and it is
backstopped by `IV.2_spectral_box_dim`, which is continuous on all 216 rows and should be
included in the comparison.

### Feasibility — the only one with no external data dependency
Nothing to fetch; it is a pure eigensolve. I timed the two solvers on this box
(single-threaded, n = 5 k/10 k/20 k) and got clean ~n² scaling:
`eigvalsh_tridiagonal` 0.16 / 0.63 / 2.46 s, `eig_banded` 0.24 / 0.91 / 3.63 s.
Extrapolating to n = 50 000: ~15 s and ~23 s per solve, ×8 φ ⇒ ~2 min per tridiagonal
row, ~3 min per `ext_harper` row.
**Total ≈ 8–9 core-hours ⇒ ~55–70 min wall at `--workers 8`.**
Peak RSS measured at 0.06 GB per solve; 8 workers ≈ 1–2 GB. Safe on the 15 GB box.

Add `"qpo-*": ("operator", "lagrange_class", "coupling")` to `verify_brody_repair.KEYS`
(note the `substrate` field is per-operator `qpo-maryland` etc., so the verifier's
one-file-per-substrate assumption needs a small tweak: the file is
`quasiperiodic-operators.jsonl`, not `<substrate>.jsonl`).

---

## 4. `population-fingerprint-all.jsonl` — 96 rows

### Producer
`cross_substrate/population_fingerprint.py`
- Path selected at **`population_fingerprint.py:148-149`**; `open(...)` at
  **`population_fingerprint.py:157`** — `fh = open(out, "a" if (all_sessions and done) else "w")`.
- Sole writer.

### Command
```bash
/home/combust/fmexplorer/bin/python3 cross_substrate/population_fingerprint.py --run --all
```
- `--run` — used (`:220`).
- `--all` — **genuinely used**, twice: `run(a.session, all_sessions=a.all)` at `:221`, and
  `all_sessions` is dereferenced at `:146`, `:148`, `:151`, `:157`. Without it you get the
  8-row single-session file instead (and overwrite *that* bank).
- `--session N` — used (`:143-144`); mutually exclusive in effect with `--all`
  (`if only_session: … elif not all_sessions: …`), so **do not pass both**.
- No `--workers`; this leg is single-process.

### ⚠ Same resume trap as `population-strat`
With the 12-session bank present, `done` contains all 12 sessions, every session prints
"already banked, skip", and the file is opened `"a"` and gets nothing. **Move the bank aside
first** so `done` is empty and the mode is `"w"`.

### Object set — **EXACT MATCH, verified**
`sorted(glob(NWB_GLOB))`, all 12 → 2 `BLOCKS` (`spontaneous`, `drifting_gratings`) → 4
aggregations. Verified:
- 12 sessions banked, 12 NWBs present, identical id list.
- `extraction_audit.n_units` per session, banked vs `build_targets()` today:
  **12/12 identical** (947, 638, 603, 887, 643, 704, 771, 574, 416, 753, 761, 886).
- Banked session order == `sorted(glob)` order; block order == `BLOCKS`; aggregation order
  == the `aggs` dict order (`corr-eig, avl-onset, sync-event, rate-peak`). Full row order
  reproduces.
- 96 = 12 × 2 × 4, no row dropped by the `len(obj) < 50` guard.

### Determinism
Same as §1: polyfit is in the path for the 24 `corr-eig` rows only; the other 72 have none.
`I.8_brody_q` expected exact. Expect `I.9` (and Family II) 3rd-decimal drift on `corr-eig`.

### FAMILY_I
**Iterates** (`_fp:86`). Adds `I.10_cv`, `I.11_mass03`; no `family_local`.

### Gate power
47/96 railed (24 `sync-event` at the low rail, 23 `rate-peak` at the high rail);
**49 rows uniquely valued** — the `corr-eig` and `avl-onset` rows carry the gate. Fine.

### Feasibility
12 NWBs × 2 blocks; each block reads every target unit's full spike train once
(`_pop_spike_matrix` slices `units/spike_times` per unit). Single-process, I/O-bound.
Estimate **1–3 hours** on the rotational disk; memory bounded by the largest count matrix
(≈ 947 units × ~4 800 bins ≈ 36 MB) plus pooled spikes — well under 1 GB.
Far cheaper than `population-strat` (2 blocks, not 8, and no per-area re-read).

---

## 5. `population-fingerprint.jsonl` — 8 rows

### Producer
Same script, same `open` at **`population_fingerprint.py:157`**. For the non-`--all` path
the mode is **unconditionally `"w"`** — no resume, no `done` check. **This one truncates
the bank the instant the process starts, before any compute.** Highest-risk file of the five
per byte written.

### Command
```bash
/home/combust/fmexplorer/bin/python3 cross_substrate/population_fingerprint.py --run
```
Deliberately **no `--session`**: the bank is session `732592105`, which is what
`files[:1]` selects from `sorted(glob(NWB_GLOB))` (9-digit ids, so lexicographic ==
numeric order). Confirmed against the bank.
`--session 732592105` would select the same file and is the safer, explicit form — the
`if only_session:` branch (`:143-144`) is a substring match on `f"session_{only_session}"`
and hits exactly one path. Either works; prefer the explicit one.

### Object set — **EXACT MATCH, verified**
1 session (`732592105`) × 2 blocks × 4 aggregations = 8. `n_units` banked 947 == today 947.
Row order reproduces.

### Determinism
Polyfit on 2 of 8 rows (`corr-eig`). `I.8_brody_q` expected exact.

### FAMILY_I
**Iterates.** Adds `I.10_cv`, `I.11_mass03`.

### Gate power
2/8 railed, **6 uniquely valued**. Small but genuinely discriminating.

### Feasibility
One 2.9 GB NWB, 2 blocks, single-process. **Minutes.** This is the natural smoke test for
the whole population channel — run it first, gate it, and only then commit to the
multi-hour `population-strat` job.

---

## Cross-cutting hazards to carry into execution

1. **Baseline before anything.** All five are tracked, but take the out-of-repo copy anyway:
   ```bash
   B=$HOME/fmexplorer/coordinate_baselines_$(date +%F)
   mkdir -p $B && cp cross_substrate/coordinates/*.jsonl $B/
   (cd $B && sha256sum *.jsonl > SHA256SUMS)
   ```
   Note the two existing baseline dirs (`…2026-07-31`, `…2026_07_29`) do not sort
   chronologically — select by mtime.

2. **Two opposite failure modes on the same `"w"`.**
   `population_strat` / `population_fingerprint --all` **silently do nothing** if the bank
   is in place (resume skips everything). `population_fingerprint` (no `--all`),
   `quasiperiodic_operators --sweep` and `phase2b_recompute` **truncate immediately**.
   Move the target aside first in every case — it fixes both.

3. **`--limit` on `phase2b_recompute.py` truncates the bank to N rows.** Only ever with
   `--dry-run`.

4. **Never run `harvest.py`** during this arc — it rewrites `pvc-11.jsonl` (and
   `allen-np`, `kuramoto`, `pulsar-nanograv`, and the arithmetic files) with `"w"` from the
   parquets, discarding every Family I/II axis merged by `phase2b_recompute`.

5. **`verify_brody_repair.py` has no `KEYS` entry for any of these five substrates** and
   assumes the file is named `<substrate>.jsonl` (false for `quasiperiodic-operators`).
   Extend the checker before the runs, not after — and extend the compared-axis set for
   `pvc-11` (99.4% railed) and `quasiperiodic-operators` (89.4% railed), where I.8 alone
   is close to an inert gate.

6. **Expect three new axes everywhere** (`I.8_brody_q_unbounded`, `I.10_cv`,
   `I.11_mass03`), five on `pvc-11` (`+I.12_cv2`, `+I.13_lv`). Additions, not movements.

7. **Suggested order:** `population-fingerprint` (minutes, smoke test) →
   `quasiperiodic-operators` (~1 h, no external data) → `population-fingerprint-all`
   (1–3 h) → `population-strat` (many hours) → `pvc-11` **only after the fitter-gate
   blocker is resolved**.

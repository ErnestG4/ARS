# Tier C — arithmetic / dynamical coordinate files: producers + reproduction commands

Recon date 2026-07-31. READ-ONLY: nothing was run that writes to `cross_substrate/coordinates/`.
All paths absolute-from `/home/combust/fmexplorer/criticality_tool/`.
Interpreter: `/home/combust/fmexplorer/bin/python3`. All commands assume `cd /home/combust/fmexplorer/criticality_tool`.

24 files / 338 brody-carrying values map onto **15 producer scripts**. Every one of the 15
reaches `I.8_brody_q_unbounded` with **no code edit** (all build Family I either by
`for k, fn in FAMILY_I.items()` or via `compute_family_I`). **No file in this set hardcodes an
axis list.** One producer (`phase2b_arith.py`) is nevertheless **BLOCKED** by a validation gate.

---

## Empirically verified this session (read-only recomputes, nothing written)

1. **`sturmian-hamiltonian` golden cell, full re-derivation** — all 8 pre-existing Family I axes
   reproduce **bit-identically**, including `I.8_brody_q = 6.610696135189609e-05`.
   New keys appear: `I.8_brody_q_unbounded = -0.6428808551406513` (informative — the old axis was
   at the bottom rail), plus `I.10_cv`, `I.11_mass03`.
2. **`mertens` all 3 cells via `compute_family_I`** — `I.8_brody_q` bit-identical on all three;
   `I.9_berry_robnik_rho` **MOVES** (e.g. 5.555e-05 → 4.281e-05) because `axes.py` now imports
   `phase34e.run_berry_robnik.fit_rho` (marked `# CORRECTED fitter`). Both values are at the
   bottom rail; the movement is a known fitter repair, not nondeterminism.
   New: `I.8_brody_q_unbounded = -0.7195…` etc.
3. All 15 producer modules import cleanly; all external inputs load (see per-producer notes).

**Expect on EVERY re-run in this set:** three-to-five NEW keys, not one.
`I.8_brody_q_unbounded`, `I.10_cv`, `I.11_mass03` are added everywhere; `I.12_cv2` + `I.13_lv`
additionally where `compute_family_I` (not raw `FAMILY_I`) is used. `I.9_berry_robnik_rho` may move.
The gate is on `I.8_brody_q` only, and that reproduces.

**Determinism / thread pinning.** `poly_unfold` is `np.polyfit(deg=12)` → LAPACK lstsq. Most
scripts pin `OMP/OPENBLAS/MKL/NUMEXPR/VECLIB_NUM_THREADS=1` at module import. **Three do not:**
`sturmian_hamiltonian_run.py`, `sturmian_run.py`, `mackey_glass_run.py`. Prefix those commands with
`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`. No RNG anywhere in this set
(`V2_correlation_dim` subsamples by deterministic stride, not `np.random`).

**Timing basis (measured, 1 thread):** `eigvalsh_tridiagonal` N=8k 0.55 s · 16k 2.2 s ·
→ N=50k ≈ 21 s · N=100k ≈ 85 s · N=200k ≈ 340 s. `eig_banded` (ext_harper) N=50k ≈ 27 s.
`compute_family_II` ≤ 0.4 s and `polyfit` ≤ 0.03 s — **negligible**; eigensolve dominates entirely.
Costs below are core-hours; divide by the worker count actually used.

---

# A. THE ONE BLOCKER — arithmetic harvest group

## P1 · `cross_substrate/phase2b_arith.py`  → **8 files, 23 values**

```
cd /home/combust/fmexplorer/criticality_tool
/home/combust/fmexplorer/bin/python3 -m cross_substrate.phase2b_arith
```

* **NO argparse at all.** `main()` takes no arguments and no substrate selection is exposed —
  it always does all eight files in one pass.
* Writes (`_write` → `open(path,"w")` at `cross_substrate/phase2b_arith.py:146`), but is a
  **MERGE**: `_merge` reads the existing jsonl, updates `axes_computed` per `cell_id`, rewrites.
  Non-matching rows keep their content.
  * `maass-gamma0.jsonl` 6 · `mertens.jsonl` 3 · `liouville.jsonl` 3 (of 4 rows; `sub_high` n=… below MIN_N_FIT)
  * `L-zeros-zeta.jsonl` 2 · `L-zeros-dirichlet.jsonl` 2 · `L-zeros-ec.jsonl` 4
  * `gaussian-primes.jsonl` 2 · `eisenstein-primes.jsonl` 1
* **FAMILY_I verdict: ITERATES** (`compute_family_I` → `FAMILY_I.items()` + `family_local`). Gains
  the repaired axis with no edit. ✅
* **Determinism: `I.8_brody_q` reproduces bit-identically** (verified on mertens).

### 🚨 BLOCKER — the fitter gate is now FALSE

`_fitter_gate()` (`phase2b_arith.py:46-49`) reads `cross_substrate/fitter_validation.json`.
That file (mtime 2026-07-27, commit `762a56c`) now has **`"all_pass": false`**: the *old*
`I8_brody_q` fitter FAILS 3 of the 5 calibrator cases (`clustered`, `clustered_extreme`, `gue`),
while the parallel `brody_q_REPAIRED_*` column passes **5/5**.

Consequence in `_matched_axes` (`phase2b_arith.py:52-58`):

```python
    if not gate:
        fI["I.8_brody_q"] = None
        fI["I.9_berry_robnik_rho"] = None
```

Running the command **as-is today would NULL OUT the banked `I.8_brody_q` on all 23 values**
instead of reproducing it. `I.8_brody_q_unbounded` would still be written (it is not name-checked
by the gate), so the file would gain the repaired axis and lose the axis the gate is supposed to
certify against. **The reproduce-gate cannot pass without a code edit.**

Minimal correct edit (do NOT just force `gate=True`): key the two fitters to their own validation
columns — `I.8_brody_q` on `cases[*].brody_q_pass`, `I.8_brody_q_unbounded` on
`cases[*].brody_q_REPAIRED_pass` — and record in the row's `object_a_recompute` block which fitter
passed. That is a substantive decision for Will, not a mechanical propagation.

### 🚨 COLLISION — never run `harvest.py`

`cross_substrate/harvest.py:340` (`write_jsonl`, `open(path,"w")`) is the **Phase-2a** producer of
these same 8 files, and it **truncates and rewrites them with q-banded axes only** — it would
destroy every object-(a) Family I/II value including `I.8_brody_q`. It additionally writes four
files **outside this list**: `pvc-11.jsonl`, `allen-np.jsonl`, `kuramoto.jsonl`,
`pulsar-nanograv.jsonl`. `phase2b_arith.py` is strictly downstream of it. **Do not run `harvest.py`.**

### Object set / inputs — all present, all verified loadable this session

| generator | input | status |
|---|---|---|
| maass (6 levels 91,95,85,77,93,87) | `phase34e/data/maassdata/` 33 214 files | present; **70 s per level** → ~7 min of the run; level 91 → n=1317 = banked 1317 ✅ |
| mertens (3 cells) | `data/phase34a_results/mertens_signchanges_N10000000.npz` | cached; n=3866 = banked ✅ |
| liouville (4 cells) | `data/phase34b_results/liouville_signchanges_N1000000000.npz` | cached; n=133 = banked ✅ (uncached this would be a 10⁹ sieve) |
| L-zeros (8 cells over 3 files) | `data/odlyzko_zeros6.txt` (36 MB, n=2 001 052), `data/dirichlet_zeros.json` (630), `data/lmfdb_zeros.json` (87 EC) | all present, load in <0.5 s |
| gaussian / eisenstein | computed on the fly from `cell_id` X | X=1e5 → 9 567 (0.0 s); X=1e6 → 78 463 (0.3 s) ✅ |

Object set is **fixed literal lists** in the positions functions — no globs, no growth risk, no
network. **Total runtime ~15–20 min, single-threaded, dominated by the Maass loader.**

---

# B. AM / Fibonacci / Sturmian spectral group (7 producers, deterministic eigensolve)

All use the identical instrument: `am_eigs` or `sturmian_eigs` (tridiagonal) → `poly_unfold(deg 12)`
→ `canonical_spacings` → pooled over 8 φ → `FAMILY_I.items()`. All pin threads at import. All
object sets are hardcoded literal lists — no globs, no external data, no network. All
`source_artifact: "generated (deterministic eigensolve)"`. **`I.8_brody_q` should reproduce
bit-identically** (directly verified on the P6 instrument).

## P2 · `cross_substrate/lambda_star_classes.py` → `lambda-star-classes.jsonl` (108)
```
/home/combust/fmexplorer/bin/python3 -m cross_substrate.lambda_star_classes --run --workers 2
```
`open(...)` at `lambda_star_classes.py:143`. Both flags **used** (`--run` gates `run()`, `--workers`
→ `ProcessPoolExecutor(max_workers=)`). Object set: 9 CLASSES × (1 AM cell @λ=1 + 11 LAM_GRID Fib
cells) = 108. N=50 000, 8φ. **≈5.0 core-hours** — the most expensive job in the set.
Also writes `cross_substrate/figures/P10_lambda_star_classes.png`.

## P3 · `cross_substrate/theta_class_correspondence.py` → **TWO files**: `am-confluence-theta.jsonl` (4) + `fibonacci-lambda-theta.jsonl` (44)
```
/home/combust/fmexplorer/bin/python3 -m cross_substrate.theta_class_correspondence --run --workers 2
```
`_write` at `theta_class_correspondence.py:159`, called twice (lines 128–129). **ONE run rewrites
BOTH files — they must be gated together.** 4 CLASSES × (1 AM + 11 FIB_LAMBDAS) = 48 cells,
N=50 000, 8φ. **≈2.2 core-hours.** Also writes figure `P8_theta_class_correspondence.png`.

## P4 · `cross_substrate/am_confluence.py` → `am-confluence.jsonl` (15)
```
/home/combust/fmexplorer/bin/python3 -m cross_substrate.am_confluence --sweep --workers 2
```
`open(out,"w")` at `am_confluence.py:186`. **`--sweep` is the only mode that writes**; `--hedge`
and `--probe` are read-only diagnostics. Object set = 11 `LAMBDAS` @ N=50 000 **plus** the
`N_CONV = {1.0:[50k,100k,200k], 0.99:[100k], 1.01:[100k]}` convergence cells = 15 — matches the
banked cell_ids exactly. **≈1.8 core-hours** (the single N=200 000 cell alone is ~45 min).

## P5 · `cross_substrate/fibonacci_lambda_run.py` → `fibonacci-lambda.jsonl` (13)
```
/home/combust/fmexplorer/bin/python3 -m cross_substrate.fibonacci_lambda_run --sweep --workers 2
```
`open(out,"w")` at `fibonacci_lambda_run.py:127`. 11 `LAMBDAS` @ N=50 000 + `N_CONV={2.0:[8k,100k]}`
= 13, matches banked. **≈0.7 core-hours.**

## P6 · `cross_substrate/lambda_star_nconv.py` → `lambda-star-nconv.jsonl` (9)
```
/home/combust/fmexplorer/bin/python3 -m cross_substrate.lambda_star_nconv --run --workers 2
```
`open(...)` at `lambda_star_nconv.py:124`. `CELLS = {e_minus_2: 1 AM + 4 fib, pi_minus_3: 1 AM + 3
fib}` = 9, matches banked. **N=100 000** throughout → **≈1.7 core-hours.**

## P7 · `cross_substrate/liouville_nconv.py` → `liouville-nconv.jsonl` (8)
```
/home/combust/fmexplorer/bin/python3 -m cross_substrate.liouville_nconv --run --workers 2
```
`open(out,"w")` at `liouville_nconv.py:115`. `--figure` is a separate read-only mode.
`AM_TASKS` (N=100k,200k) + `FIB_TASKS` (λ=8 @100k,200k; λ=6,10,12,16 @100k) = 8, matches banked.
**≈2.6 core-hours** — two N=200 000 cells dominate.

## P8 · `cross_substrate/sturmian_hamiltonian_run.py` → `sturmian-hamiltonian.jsonl` (7)
```
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /home/combust/fmexplorer/bin/python3 -m cross_substrate.sturmian_hamiltonian_run
```
`open(...)` at `sturmian_hamiltonian_run.py:155`. **No argparse — `__main__` calls `run()` directly.**
7 `_ALPHAS` @ N=8 000, λ=2.0, 8φ. **≈2 minutes.** ⚠️ This module does **not** pin BLAS threads
itself — pin them on the command line (I did, and got bit-identical reproduction).
**This is the ideal first gate run: cheapest, and already verified to reproduce exactly.**

---

# C. Brocot / continued-fraction group (2 producers, sibling-repo dependency)

Both depend on the **sibling repo `/home/combust/fmexplorer/brocot`**
(`phase3.partial_prediction.predict_partials`, `phase3.ars.arithmetic_toolkit`), added to
`sys.path` by `brocot_approximability.py:41-46`. Verified present and importable.

## P9 · `cross_substrate/brocot_approximability.py` → `brocot-approximability.jsonl` (63 rows / **54** brody values)
```
/home/combust/fmexplorer/bin/python3 -m cross_substrate.brocot_approximability --run
```
`open(...)` at `brocot_approximability.py:144`. **`--run` only; no `--workers` (serial).**
Object set: 9 `CLASSES` × 7 `DEPTHS` = 63. The 9 `depth1` rows carry `I.8_brody_q: null`
(n_partials=31 < `MIN_N_FIT`=50) → 54 values, matching the brief. `_fingerprint` iterates
`FAMILY_I.items()` at line 81. ✅ Cheap (no eigensolve; `predict_partials` + RF only) — minutes.
Also writes a figure.

## P10 · `cross_substrate/cf_discriminator.py` → `cf-discriminator.jsonl` (7)
```
/home/combust/fmexplorer/bin/python3 -m cross_substrate.cf_discriminator --run --workers 2
```
`open(...)` at `cf_discriminator.py:179`. Reuses P9's `_fingerprint` (imported at line 49) → **iterates
FAMILY_I** ✅. 7 `TARGETS`. Cost is entirely the `operator_dbox` control: 7 targets × 2 OPS
(`gaah` tridiagonal ≈21 s, `ext_harper` `eig_banded` ≈27 s) × 8 φ at N_OP=50 000 ⇒ **≈0.75
core-hours**. Deterministic. Also writes a figure.
⚠️ `thue_morse_12` / `fib_word_12` α values are built from `alpha_from_cf(...)` at import — pure
arithmetic, stable.

---

# D. Dynamical-systems group (3 producers, deterministic integration)

## P11 · `cross_substrate/lorenz_logistic_run.py` → **TWO files**: `lorenz.jsonl` (4 rows / 3 values) + `logistic.jsonl` (5 rows / 4 values)
```
/home/combust/fmexplorer/bin/python3 -m cross_substrate.lorenz_logistic_run
```
`_write` at `lorenz_logistic_run.py:143`; `__main__` calls `run_lorenz()` then `run_logistic()`.
**No argparse — one run rewrites BOTH files; gate them together.** Object sets: `LORENZ_RHO`
(4 ρ) and `LOGISTIC_REGIMES` (5 r). The null-brody rows are the ones with too few events
(`rho20_stable` n_events=0; `r2.5_stable_fp` n_events=1) — reproduces structurally.
Deterministic: RK4 from fixed `s=[1,1,1]`, logistic from fixed `x0=0.5`. Uses `compute_family_I` ✅.
**Minutes** (200k RK4 steps + Benettin per ρ, pure Python loops — call it 10–20 min).

## P12 · `cross_substrate/mackey_glass_run.py` → `mackey-glass.jsonl` (5 rows / 4 values)
```
OMP_NUM_THREADS=1 /home/combust/fmexplorer/bin/python3 -m cross_substrate.mackey_glass_run
```
`open(...)` at `mackey_glass_run.py:115`. **No argparse.** `MACKEY_GLASS_REGIMES` (5 τ),
DDE Euler dt=0.1, N_STEPS=300 000, fixed history → deterministic. `compute_family_I` ✅.
⚠️ Does not pin BLAS threads itself. **Minutes.**

## P13 · `cross_substrate/dynamical_breadth.py` → `dynamical-breadth.jsonl` (17 rows / **16** values)
```
/home/combust/fmexplorer/bin/python3 -m cross_substrate.dynamical_breadth --sweep --workers 2
```
`open(...)` at `dynamical_breadth.py:179`. **`--sweep` writes; `--probe` is read-only.** Object set:
`SWEEPS` rossler(5) + chua(4) + duffing(4) + hénon(4) = 17. `duffing_gamma0.37` carries
`I.8_brody_q: null` → 16 values. Fixed initial conditions, RK4 / tangent-space; no RNG.
`compute_family_I` ✅. Note the `substrate` field is the *system* name (rossler/chua/duffing/henon),
not `dynamical-breadth`. **~20–40 min.**

---

# E. AM re-aggregation — cheapest big win

## P14 · `cross_substrate/am_reextract.py` → `am.jsonl` (11)
```
/home/combust/fmexplorer/bin/python3 -m cross_substrate.am_reextract --agg --cells all
```
`open(path,"w")` at `am_reextract.py:225` — but it **MERGES by `cell_id`** into the existing file
(reads it first, overlays, rewrites), so a partial run does not lose rows.

* `--cells all` = `CELLS + C1_CELLS + SUBC1_CELLS` = 11 cells = exactly the 11 banked rows.
  **`--cells core` (the DEFAULT) would only touch 6 — you must pass `--cells all`.**
* `--Lcap` and `--workers` are accepted; **`aggregate()` uses `Lcap` only** (leave it unset to keep
  the banked `Lconv…` cell_ids); `--workers` is **not referenced** by the `--agg` path.
* **NO recompute of the expensive stages.** Stage A (eigensolve) and Stage B (O(N·L) Sturm unfold,
  "hours") are checkpointed under `cross_substrate/coordinates/am_work/`. I verified **all 176
  `unf_*` checkpoints are present** (11 cells × 16 φ), covering all 11 stems. `--agg` only loads
  `.npy` → `canonical_spacings` → `FAMILY_I.items()` (line 159-163) → `compute_family_II`.
* **FAMILY_I: ITERATES** ✅. Deterministic (no fit, no RNG — reads banked positions).
  `VI.1`/`VI.2` come from hardcoded banked Phase-35 constants, unchanged.
* **Cost: a few minutes.** Best value-per-minute job in the whole set after P8.
* ⚠️ Do **not** run `--stage A` / `--stage B`; they would rewrite the `am_work` checkpoints.

---

# Summary table

| # | Producer (command) | Files written (values) | Cost | I.8 reproduces | FAMILY_I | Risk |
|---|---|---|---|---|---|---|
| P1 | `-m cross_substrate.phase2b_arith` | maass-gamma0 6, mertens 3, liouville 3, L-zeros-zeta 2, L-zeros-dirichlet 2, L-zeros-ec 4, gaussian-primes 2, eisenstein-primes 1 | ~20 min | ✅ verified | iterates | 🚨 **BLOCKED: `fitter_validation.json all_pass=false` ⇒ nulls I.8_brody_q**. Never run `harvest.py`. |
| P2 | `-m …lambda_star_classes --run --workers N` | lambda-star-classes 108 | 5.0 ch | ✅ expected | iterates | — |
| P3 | `-m …theta_class_correspondence --run --workers N` | am-confluence-theta 4 **+** fibonacci-lambda-theta 44 | 2.2 ch | ✅ expected | iterates | **2 files, one run — gate together** |
| P4 | `-m …am_confluence --sweep --workers N` | am-confluence 15 | 1.8 ch | ✅ expected | iterates | — |
| P5 | `-m …fibonacci_lambda_run --sweep --workers N` | fibonacci-lambda 13 | 0.7 ch | ✅ expected | iterates | — |
| P6 | `-m …lambda_star_nconv --run --workers N` | lambda-star-nconv 9 | 1.7 ch | ✅ expected | iterates | — |
| P7 | `-m …liouville_nconv --run --workers N` | liouville-nconv 8 | 2.6 ch | ✅ expected | iterates | — |
| P8 | `OMP=1 -m …sturmian_hamiltonian_run` | sturmian-hamiltonian 7 | 2 min | ✅ **verified** | iterates | pin BLAS threads |
| P9 | `-m …brocot_approximability --run` | brocot-approximability 54 | minutes | ✅ expected | iterates | needs sibling repo `~/fmexplorer/brocot` |
| P10 | `-m …cf_discriminator --run --workers N` | cf-discriminator 7 | 0.75 ch | ✅ expected | iterates | needs `~/fmexplorer/brocot` |
| P11 | `-m …lorenz_logistic_run` | lorenz 3 **+** logistic 4 | ~15 min | ✅ expected | compute_family_I | **2 files, one run — gate together** |
| P12 | `OMP=1 -m …mackey_glass_run` | mackey-glass 4 | minutes | ✅ expected | compute_family_I | pin BLAS threads |
| P13 | `-m …dynamical_breadth --sweep --workers N` | dynamical-breadth 16 | ~30 min | ✅ expected | compute_family_I | — |
| P14 | `-m …am_reextract --agg --cells all` | am 11 | minutes | ✅ expected | iterates | **must pass `--cells all`**; never `--stage A/B` |

**Not covered / cannot be reproduced today: none.** Every file has a live producer with present
inputs. The single obstruction is P1's validation gate, which is a policy decision, not a
missing capability.

**No producer in this set writes any coordinate file outside the 24 listed** — with the single
exception of `harvest.py`, which is *not* the producer of the banked versions and must not be run.
No file already carrying the repaired axis (allen-hpf-*, buzsaki-port-*, ibl-port-*, ret1-*,
dr-port-*, pvc-11) is touched by any of P1–P14.

**Suggested order** (cheap-and-verified first, so the gate discipline is proven before spending
core-hours): P8 → P14 → P9 → P12 → P11 → P13 → P10 → P5 → P6 → P4 → P3 → P7 → P2, with P1
held pending the fitter-gate decision.

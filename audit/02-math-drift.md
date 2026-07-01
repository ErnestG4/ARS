# Phase 2b — Cross-Copy Drift Diff

READ-ONLY audit. Tags: `[code]` = read from source, `[inferred]` = my reasoning from
the code, `[documented]` = from a docstring/comment. Nothing was edited. Classification
vocabulary: `[cosmetic]` / `[parameter-drift]` / `[semantic-drift]` / `[likely bug]`.

---

## KEY QUESTION (answered up front)

**Do the 9 `analytical_nns` copies and the (≥9) `unfold_unit_mean` copies actually agree,
or has a constant/cap drifted so two phases' "same" estimator computed different things?**

- **`analytical_nns`: PARTIAL — DRIFT.** 8 of 9 share a byte-identical core summation
  (the tongue-threshold passage-time band). But the PLL **frequency admission guard
  drifted** across phases: the reference admits `5.0 < f_pll < SR*0.45`; five phases
  relaxed the lower bound to `f_pll > 0.5` **and dropped the upper Nyquist cap entirely**;
  one phase (`run_phase5`) sits at `f_pll > 5.0` with the cap off-by-default. Different
  phases therefore pool over **different sets of PLL bands** from the same input. The 9th
  copy (`run_fungal_nns`) is **different math** — no time-band, no tongue threshold at all.
  `[code]`
- **`unfold_unit_mean`: DRIFT.** The core unit-mean cumsum is identical, but the copies
  split into a **no-cap generation** and a **cap-and-decimate generation**, and the cap
  value itself drifted **5000 vs 1500**. Two drivers *in the same phase* disagree (Phase 20
  classification has no cap, Phase 20 falsification caps at 5000; Phase 21 classification
  caps at 1500 while Phase 21 calibrators cap at 5000). Because the cap triggers a stride
  decimation `sp[::max(1, sp.size//cap)]`, a different cap → a different decimated series →
  potentially a different verdict on the same input. `[code]` `[inferred]`

---

## GROUP 1 — `analytical_nns` (9 copies)

| # | file:line | f_pll guard | min-events gate | param style |
|---|-----------|-------------|-----------------|-------------|
| ref | `run_analytical_nns.py:84` | `5.0 < f_pll < SR*0.45` | `< min_events+1` (=11) | full kwargs |
| 2 | `run_phase4.py:52` | `5.0 < f_pll < SR*0.45` | `< min_events+1` | full kwargs |
| 3 | `run_phase5.py:53` | `f_pll <= 5.0` skip; cap `f_pll>=sr*0.45` **off by default** | `< min_events+1` | + `enforce_sr_cap=False` |
| 4 | `run_lmfdb_family.py:66` | `f_pll <= 0.5` skip | `< min_events+1` | full kwargs + `sr` |
| 5 | `run_lmfdb_postprocess.py:23` | `f_pll <= 0.5` skip | `< min_events+1` | module-const defaults |
| 6 | `run_dirichlet_family.py:52` | `f_pll <= 0.5` skip | hardcoded `< 11` | reads module globals |
| 7 | `run_lmfdb_extend.py:36` | `f_pll <= 0.5` skip | hardcoded `< 11` | reads module globals |
| 8 | `run_mertens_liouville.py:120` | `f_pll <= 0.5` skip | hardcoded `< 11` | reads module globals |
| 9 | `run_fungal_nns.py:119` | **none** (only `q==0`/`f_pll<=0`) | `< 5` | **different algorithm** |

### Reference core arithmetic — `run_analytical_nns.py:84` `[code]`

```python
for p, q in pairs:
    f_pll = fc_ref * p / q
    if not (5.0 < f_pll < SR * 0.45): continue
    elig = ((t_n_array >= (transient_s + 1.0) * f_pll) &
            (t_n_array <= (dur_s + 1.0) * f_pll))
    elig_t = np.sort(t_n_array[elig])
    threshold = lock_confirm_s * f_pll / (tongue_prefac * (2.0 / (p + q)) ** 2)
    qualifying = elig_t[elig_t >= threshold]
    if qualifying.size < min_events + 1:   # +1 because spacings = events − 1
        continue
    spacings = np.diff(qualifying) / f_pll
    if spacings.size == 0 or spacings.mean() <= 0:
        continue
    sp_norm = spacings / spacings.mean()
    pooled.append(sp_norm)
```

The four load-bearing lines — the `elig` band, the `threshold` formula, `np.diff/f_pll`,
and `/spacings.mean()` — are **byte-identical** in copies 2–8. `[code]`

### Per-copy DIFFERING lines only

**`run_phase4.py:52`** — IDENTICAL logic (guard, band, threshold, normalisation all match
the reference). Only the `ks_to` helper below it is trimmed. `[code]`

**`run_phase5.py:53`** — guard line replaced; the Nyquist cap is now opt-in: `[code]`
```python
if f_pll <= 5.0: continue
if enforce_sr_cap and f_pll >= sr * 0.45: continue   # off by default for analytical
```
→ **[parameter-drift]**: same 5.0 lower bound as ref, but the `SR*0.45` upper cap that the
reference applies unconditionally is **off by default here**, so high-frequency PLL bands
the reference discards are admitted. `[inferred]`

**`run_lmfdb_family.py:66` / `run_lmfdb_postprocess.py:23` / `run_dirichlet_family.py:52` /
`run_lmfdb_extend.py:36` / `run_mertens_liouville.py:120`** — all share one guard change: `[code]`
```python
if f_pll <= 0.5: continue        # vs ref:  if not (5.0 < f_pll < SR*0.45)
```
→ **[parameter-drift]**: lower admission bound dropped 5.0 → 0.5 **and** the `SR*0.45`
upper cap removed. These five pool over a **wider PLL band set** than the reference
(everything with `f_pll` in `(0.5, ∞)`). For the L-function/arithmetic inputs `FC_REF=1.0`,
so `f_pll = p/q` and the 0.5 bound is the live admission line. The threshold summation
itself is unchanged. `[inferred]`

Within that group, copies 6/7/8 also hardcode `if qual.size < 11` instead of
`min_events+1`; numerically identical (`min_events=10`). **[cosmetic]**. `[code]`

**`run_fungal_nns.py:119`** — **[semantic-drift / different math]**. No eligibility band,
no tongue threshold; the passage index is computed directly and positives kept: `[code]`
```python
passage = t_n_array * f_pll - 1.0            # passage-time integer index
passage = np.sort(passage[passage > 0])
if passage.size < 5: continue
sp = np.diff(passage)
...
pooled.append(sp / sp.mean())
```
This is a **structurally different estimator** that happens to share the name. It omits the
`transient_s/dur_s` time-band and the `lock_confirm_s/tongue_prefac` dwell threshold that
define the analytical NNS in every other copy. Spacings here are in *passage-index* units,
not `/f_pll` seconds. **Do not treat fungal output as comparable to the other 8.** `[inferred]`

### Constants (confirm no silent constant drift) `[code]`
All copies that define them agree: `Q_MAX=8`, `DUR=300.0`, `LOCK_CONFIRM_S=20e-3`,
`TONGUE_PREFAC=0.05`, `TRANSIENT_S=0.5`, `SR=44100.0`. **`FC_REF` legitimately differs by
domain** (`115.55` audio in analytical/phase4; `1.0` for L-function zeros in
lmfdb/dirichlet; passed explicitly in mertens) — this is by-design, not drift. So the
**only** real Group-1 divergence among the 8 same-shape copies is the **`f_pll` guard**.

---

## GROUP 2 — `unfold_unit_mean` (10 copies found; task listed 5)

| file:line | cap param | JPF_CAP | decimates? |
|-----------|-----------|---------|------------|
| `run_phase20_classification.py:56` | none | — | **NO** |
| `run_phase20_calibrators.py:71` | none (JPF_CAP=5000 defined at :211 but **unused by unfold**) | 5000 | **NO** |
| `phase22a/verify_calibrators.py:77` | none | — | **NO** |
| `run_phase20_falsification.py:79` | `cap=JPF_CAP` | **5000** | yes |
| `run_phase21_falsification.py:71` | `cap=JPF_CAP` | **5000** | yes |
| `run_phase21_calibrators.py:61` | `cap=JPF_CAP` | **5000** | yes |
| `phase23/run_phase23_targeted.py:78` | `cap=JPF_CAP` | **5000** | yes |
| `run_phase21_classification.py:59` | `cap=JPF_CAP` | **1500** | yes |
| `phase22a/ars_classify.py:37` | `cap=JPF_CAP` | **1500** | yes |

### Reference core — `phase21_calibrators.py:61` (the capped form) `[code]`
```python
def unfold_unit_mean(t: np.ndarray, cap: int = JPF_CAP) -> np.ndarray:
    if t.size < 2: return t.copy()
    sp = np.diff(t)
    sp = sp[sp > 0]
    if sp.size == 0 or sp.mean() <= 0: return t.copy()
    if sp.size > cap:
        sp = sp[::max(1, sp.size // cap)]
    return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))
```

### DIFFERING lines

**No-cap generation** (`phase20_classification:56`, `phase20_calibrators:71`,
`phase22a/verify_calibrators:77`) — the two cap lines are **absent**: `[code]`
```python
    # (no `cap` parameter, no `if sp.size > cap: sp = sp[::...]`)
    return np.cumsum(np.concatenate([[0.0], sp / sp.mean()]))
```
→ **[semantic-drift]**: on inputs with `>cap` spacings these return the **full**
unfolded series; the capped copies return a **stride-decimated** series. Per the project's
own `stride_decimation_destroys_prime_angle_structure` note, decimation is not lossless,
so capped vs uncapped is a genuine behavioural fork, not cosmetic. `[inferred]`

**JPF_CAP value drift** among the capped copies: `[code]`
```
phase20_falsification.py:76   JPF_CAP = 5000
phase21_falsification.py:68   JPF_CAP = 5000
phase21_calibrators.py:58     JPF_CAP = 5000
phase23/run_phase23_targeted:73 JPF_CAP = 5000
phase21_classification.py:56  JPF_CAP = 1500     <-- drift
phase22a/ars_classify.py:34   JPF_CAP = 1500     <-- drift
```
→ **[parameter-drift]**. The cap line is byte-identical everywhere; only the threshold/stride
moves. `1500` vs `5000` → different decimation stride on large trains → different unfolded
series. `phase22a/ars_classify.py:33` has a header comment documenting `JPF_CAP = 1500`, so
that value is intentional there, but it differs from the 5000-family it shares a pipeline with.

### Worst divergence in this group `[inferred]`
- **Same-phase fork (Phase 20):** `classification` (no cap) vs `falsification` (cap=5000) —
  two drivers of the *same* phase unfold differently.
- **Calibrator/classifier mismatch (Phase 21):** `classification` caps at **1500** while its
  sibling `calibrators` caps at **5000** — i.e. the reference baselines were decimated at a
  *different stride* than the data they calibrate. This is the highest-risk instance because
  it can bias the classification-vs-calibrator comparison the phase is built on.

---

## GROUP 3 — Other `unfold_*` variants (method tabulation)

| function | file:line | method | key constant |
|----------|-----------|--------|--------------|
| `unfold_global_mean` | `fix_gue_generator.py:60` | **global-mean** (`(e-e[0])/sp.mean()`) | — *("OLD broken" per docstring `[documented]`)* |
| `unfold_semicircle_R` | `fix_gue_generator.py:67` | semicircle CDF | `R=2.0` |
| `unfold_R2` | `run_calibration.py:82` | semicircle CDF | `R=2.0` (hardcoded `/2.0`) |
| `unfold_empirical` | `fix_gue_generator.py:77` | polyfit staircase | **deg=11** |
| `unfold_empirical` | `cross_substrate/longrange_discriminator.py:73` | polyfit staircase (x rescaled to [0,1]) | **deg=6** |
| `unfold_poly` | `phase35a/regated_instrument.py:53` | polyfit staircase | deg=param |
| `unfold_poly` | `phase35a/unfolding_invariance_campaign.py:62` | polyfit staircase | deg=param |
| `unfold_arcsine` | `phase35a/regated_instrument.py:67` | **arcsine** CDF `0.5+arcsin(e/2)/π` | N |
| `unfold_ids_ref` | `phase35a/regated_instrument.py:61` + `:q3_*`, `:unfold_rotnum.py:64` | integrated-density-of-states vs reference (searchsorted) | — |
| `unfold_gamma0` | `phase34e/maass_loader.py:171` | Γ₀(N) Weyl law `c·r²` | level-dep `c` |
| `unfolded_spacings_zeta` | `run_second_order.py:36` | Riemann–vM density | **+7/8** |
| `_unfold_zeta_zeros` | `run_phase18_finding_validation.py:92` | Riemann–vM density | **+7/8** |
| `load_zeta_band` (inline) | `run_phase9_extended.py:~48` | Riemann–vM density | **+7/8** |
| `unfolded_spacings` | `run_zeta_height_convergence.py:43` | Riemann–vM density | **+7/8** |
| `unfolded_spacings_lfunction` | `run_second_order.py:43` | L-fn conductor density `(z/2π)(log(Cz/2π)−1)` | no 7/8 |
| L-fn pool (inline) | `run_phase9_extended.py:~62`, `run_phase16_invariance.py:~77` | same `(z/2π)(log(Cz/2π)−1)` | no 7/8 |

### Flags

- **ζ unfolding is consistent.** `run_second_order:36`, `run_phase18:92`,
  `run_phase9_extended` (inline), `run_zeta_height_convergence:43` all use the **identical**
  Riemann–von Mangoldt formula `(z/2π)·log(z/2πe) + 7/8`. **AGREE.** `[code]`
- **L-function unfolding is consistent.** `run_second_order:43`, `run_phase9_extended`,
  `run_phase16` all use `(z/2π)(log(C·z/2π) − 1)`. **AGREE.** `[code]`
- **Naming hazard, not a bug:** `unfolded_spacings_zeta`/`unfolded_spacings_lfunction`
  (`run_second_order.py:36,43`) return **unfolded positions, not spacings** (`return N_smooth`,
  no `np.diff`), and are stored as `events_by_family[...]` for downstream second-order code.
  `run_zeta_height_convergence.unfolded_spacings:43` with the *same* name **does** diff and
  normalise (`sp/sp.mean()`). Same formula, opposite output convention. **[cosmetic]** (misnomer)
  — flagged because a reader splicing the two would feed positions where spacings are expected. `[inferred]`
- **`unfold_arcsine` vs `unfold_semicircle_R` are different distributions**, correctly named:
  arcsine `0.5+arcsin(x)/π` omits the `x√(1−x²)` term of the semicircle CDF. Both map `eigs/2`
  → `[0,N]` so they look interchangeable but are not. No path uses one where it claims the
  other; recorded as a tabulation, **not** a drift. `[code]`
- **Empirical-poly degree differs by path:** `deg=11` (fix_gue), `deg=6` (longrange), `param`
  (phase35a). The docstrings call `deg` a *lens parameter*, so this is intended per-substrate
  tuning, **[parameter-drift]** only if two paths claiming the same comparison use different
  deg — not observed across the GUE-reference paths (all semicircle, not empirical). `[inferred]`

---

## GROUP 4 — `direct_nns` (3 copies)

### Reference — `run_phase5.py:77` `[code]`
```python
def direct_nns(events):
    e = np.sort(np.asarray(events, dtype=np.float64))
    sp = np.diff(e)
    if sp.size == 0 or sp.mean() <= 0: return np.zeros(0)
    return sp / sp.mean()
```

- **`run_mertens_liouville.py:183`** — **IDENTICAL** (byte-equivalent; same 5 lines). `[code]`
- **`run_fungal_nns.py:152`** — same core (`np.diff(np.sort(...)) / mean`) but **wraps the
  result in `classify(...)` and returns a dict**, with a `<5` guard returning an
  `'insufficient'` dict instead of an empty array. **[cosmetic]** (interface only — the
  arithmetic that produces the normalised spacings is the same). `[code]`

**Verdict: AGREE.** The spacing math is identical in all three; fungal differs only in
return type. `[inferred]`

---

## GROUP 5 — `peak_q` / RF

**Single canonical source.** All the `run_phase9/10/11/12/13/14`, `run_padic_finance`
references **read `peak_q` out of the toolkit dict**; they do not re-implement selection. `[code]`

### Canonical — `arithmetic_toolkit.py:177-190` (`ramanujan_fourier`) `[code]`
```python
a = np.zeros(q_max)
for q in range(1, q_max + 1):
    c = ramanujan_sum_array(q, N)
    a[q - 1] = float(np.mean(f * c)) / _phi(q)
abs_a = np.abs(a)
if q_max >= 2:
    order = np.argsort(abs_a[1:])[::-1] + 2     # rank q≥2 by RAW |a_q|
    top10_q = order[:10].tolist()
    peak_q = int(top10_q[0])
```
Selection basis = **raw `|a_q|`**, q≥2 excluded DC, argmax.

### Re-implementations
- **`cross_substrate/rf_decoy_battery.py:104-115`** — selects peak by
  `rf_amplitude_q_normalized` (the **normalised** a_q), not raw `|a_q|`: `[code]`
  ```python
  amps = sub.rf_amplitude_q_normalized.to_numpy()   # vs canonical raw abs_a
  i = int(np.nanargmax(amps))
  return int(sub.q.to_numpy()[i]), ...
  ```
  → **[semantic-drift]** (intentional): ranks by floor-normalised amplitude, which can pick a
  *different* q than the raw-amplitude canonical. Consistent with the project's
  `rf_aq_marginal_dominated` note (the normalised/floor-calibrated reading is the deliberate
  decoy-battery statistic), but it is **not** the same `peak_q` the phase drivers report. `[inferred]`
- **`cross_substrate/gratings_divergence.py:180`** — `peak_q = argmax(|ph − pl|) + 1` is the
  **q of maximal KS-GUE profile divergence between two cell groups**, a different quantity
  entirely (labelled `peak_divergence_q` in the output). **[different-math]**, not a copy. `[code]`

**Verdict: AGREE for the RF a_q `peak_q` used by phase drivers** (one source). The two
`cross_substrate` functions compute deliberately different statistics under similar names. `[inferred]`

---

## GROUP 6 — GUE generators

| file:line | matrix norm | unfold method | reference dist |
|-----------|-------------|---------------|----------------|
| `signal_gen.py:71` `make_gue_eigenvalue_signal` | `H=(A+A†)/√(2N)`, `A_ij~CN(0,1)` | **semicircle CDF**, R=2 | Wigner (KS≈0.04 @N=500) `[documented]` |
| `fix_gue_generator.py:~55` `gen_gue_eigenvalues`+`unfold_semicircle_R` | `A=(randn+i·randn)/√2`, H=…, R=2 | **semicircle CDF** | Wigner |
| `run_phase9_extended.py:35` `gen_gue_unfolded` | `A=randn+i·randn`, `H=(A+A†)/2/√2` | **semicircle CDF**, R=2√N | Wigner |
| `run_phase9.py:48` `gen_goe_unfolded` | real symmetric `(M+Mᵀ)/√2` | semicircle CDF, R=2√N | Wigner GOE (different ensemble) |
| `run_chirp_prediction.py:111` (inline) | `A=(randn+i·randn)/√2`, `H=(A+A†)/√(2N)` | **GLOBAL-MEAN** `(e-e[0])/sp.mean()` | **NOT Wigner-unfolded** |

### Reference — semicircle path (`run_phase9_extended.py:35`) `[code]`
```python
eigs = np.sort(np.linalg.eigvalsh(H))
R = 2 * np.sqrt(N)
x = np.clip(eigs / R, -1, 1)
cdf = (x * np.sqrt(1 - x**2) + np.arcsin(x)) / np.pi + 0.5   # semicircle CDF
return cdf * N
```
The semicircle copies (`signal_gen`, `fix_gue_generator`, `run_phase9_extended`,
`run_phase9` GOE) differ only in matrix-normalisation constant (`/√2` and `/√(2N)` vs
`R=2√N`), which the semicircle `eigs/R` rescale absorbs → **same reference distribution**.
**[cosmetic / parameter-drift]** in the matrix prefactor only. `[inferred]`

### Likely bug — `run_chirp_prediction.py:111-116` `[code]`
```python
# GUE eigenvalues — same generation as signal_gen.make_gue_eigenvalue_signal   <-- comment
H = (A + A.conj().T) / np.sqrt(2 * ACTUAL_NZ)
eig = np.sort(np.linalg.eigvalsh(H).real)
spacings = np.diff(eig)
eig_unfolded = (eig - eig[0]) / spacings.mean()      # <-- GLOBAL-MEAN unfold
```
→ **[likely bug / semantic-drift]**. The comment claims parity with
`signal_gen.make_gue_eigenvalue_signal`, but `signal_gen` unfolds by the **semicircle CDF**
while this unfolds by the **global mean spacing** — the exact procedure
`fix_gue_generator.py:60` labels *"OLD broken procedure"* and whose docstring records that
global-mean unfolding leaves non-stationary local spacing and produced super-Poisson Fano
≈2.10 instead of Wigner repulsion. The `gue_zeros` built here (`ZEROS_BY_SIGNAL['gue']`)
are therefore **not** Wigner-distributed in the bulk, contradicting the in-file comment. `[inferred]`

**Verdict: DRIFT.** Four generators converge on the semicircle reference; `run_chirp_prediction`
uses the deprecated global-mean unfold while asserting it matches `signal_gen`.

---

## Incompleteness / caveats

- I diffed function bodies and the constants they reference; I did **not** execute any code,
  so "produces a different series" is `[inferred]` from the arithmetic, not measured.
- Group 3 phase35a copies (`unfolding_invariance_campaign.py`, `q3_*.py`,
  `unfold_rotnum.py`) were tabulated by signature + the one representative body
  (`regated_instrument.py`); I did not byte-diff every phase35a sibling against each other.
- `run_phase9_extended.load_lmfdb_pool` / `run_phase16._lmfdb_pool` L-fn unfold confirmed
  identical to `run_second_order`; other inline unfolds elsewhere in the tree may exist
  beyond the grep scope used here.
- FC_REF and per-domain f_pll bounds: I treated FC_REF differences as by-design (audio vs
  arithmetic). If any two phases intend to be *directly comparable* on the same substrate,
  the f_pll-guard drift (Group 1) would make them not strictly comparable — that scoping call
  is the user's, not mine.

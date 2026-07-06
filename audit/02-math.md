# 02 — Mathematics Extraction (canonical estimator implementations)

READ-ONLY ground-truth audit. Phase 2a. No edits performed.

> **Companion:** cross-copy drift (the same estimator re-implemented across phase drivers, and whether
> the copies agree) is audited in **`02-math-drift.md`**. Read both together — this file covers the
> canonical/live implementation; the companion covers divergence between duplicates.

## Incompleteness (stated up front)

- **Fully read as ground truth:** `cross_substrate/axes.py` (all 507 lines),
  `universality.py` (all 232 lines), `run_analytical_nns.py` (all 328 lines),
  `arithmetic_toolkit.py` lines 40–250 (factorization → RF engine → p-adic head)
  + symbol map via grep over the full 812 LOC, `phase35a/unfold_rotnum.py`
  lines 38–80 (the upstream unfolder + matched `spacings` extractor).
- **NOT read in full (delegated / out of required surface):**
  - `phase34e/run_berry_robnik.py::fit_rho` — the Berry-Robnik ρ MLE is
    imported and called by `I9_berry_robnik_rho`; I quote the call site and
    its arguments, not the fitter internals. [boundary]
  - `pll_bank.farey_rationals`, `intermittency.extract_dwells` — used by
    `run_analytical_nns.py`; treated as black boxes (event lists in).
  - `arithmetic_toolkit.py` lines 250–812 (p-adic per-band aggregation,
    `padic_profile`, summary assembler) — beyond the RF-core required surface;
    grep-confirmed the only `peak_q`/`ramanujan` definitions are at 88–197.
  - Family V (`V1_lyapunov`, `V2_correlation_dim`) is present in axes.py but is
    NOT on the canonical-estimator list; noted only in passing at the end.
- I did not execute any code; all claims are static reads.

A recurring structural fact that drives several entries below:
**axes.py never unfolds.** It is handed positions that the contract (axes.py:9–22)
says are already unit-mean unfolded. `canonical_spacings` only diffs, edge-trims,
and renormalizes. The actual mean-density removal lives upstream, per-substrate
(for AM: `ids_rotnum`, quoted in §UNFOLDING).

---

## FAMILY I — NNS marginal distances

### canonical_spacings (axes.py:61) — the matched spacing extractor

**(1) Canonical.** Nearest-neighbour spacings of an unfolded spectrum:
`s_i = x_{i+1} − x_i` with the sequence pre-unfolded so `⟨s⟩ = 1`.

**(2) As-implemented.** axes.py:61–64 delegates to `phase35a.unfold_rotnum.spacings`:
```
def canonical_spacings(positions):
    return _trim_spacings(np.asarray(positions, dtype=np.float64))
```
unfold_rotnum.py:70–74:
```
def spacings(unf):
    u = np.sort(unf); d = np.diff(u)
    d = d[int(0.02 * len(d)):int(0.98 * len(d))]
    m = d.mean()
    return d / m if m > 0 else d
```

**(3) Deviations.**
- The trim `d[int(0.02*len(d)):int(0.98*len(d))]` slices `d` **in position
  order** (d = diff of *sorted* positions, but d itself is not sorted by
  magnitude), so it drops the first 2% and last 2% spacings at the **edges of
  the spectrum**, i.e. a boundary-effect trim — NOT a magnitude tail trim.
  The axes.py docstring (axes.py:13–14) and the contract block call it a
  "2–98% **tail** trim," which reads as a magnitude/outlier trim. The code is
  an ordinal edge trim. **[intentional+undocumented]** (mismatch between the
  word "tail" and the ordinal slice; behaviour is a boundary trim).
- Unit-mean renorm is applied **after** trimming (`d/m` on the trimmed array),
  so ⟨s⟩=1 holds over the retained interior, consistent with canonical. [code]

### _w1_cdf (axes.py:67) and I2_w1_gue (axes.py:96)

**(1) Canonical.** 1-Wasserstein between empirical and reference spacing laws:
`W1 = ∫₀^∞ |F_emp(s) − F_ref(s)| ds`.

**(2) As-implemented.** axes.py:71–77:
```
s = np.sort(np.asarray(s, dtype=np.float64))
grid = np.linspace(0.0, max(grid_max, float(s[-1])), n_grid)   # grid_max=8.0, n_grid=2000
f_emp = np.searchsorted(s, grid, side="right") / s.size
f_ref = np.asarray(cdf_func(grid), dtype=np.float64)
return float(np.trapezoid(np.abs(f_emp - f_ref), grid))
```
I2/I3/I4 (axes.py:96–108) pass `nns_cdf_gue / nns_cdf_goe / nns_cdf_poisson`.

**(3) Deviations.**
- Integral truncated at `max(8.0, s_max)`; the GUE/GOE/Poisson tails beyond are
  negligible. **[approximation]** (deterministic, accurate).
- Trapezoid on a 2000-point grid; F_emp via `searchsorted/size`. Faithful to W1. [code]

### _ks_cdf (axes.py:80) and I5_ks_gue (axes.py:111)

**(1) Canonical.** KS statistic `D = sup_s |F_emp(s) − F_ref(s)|`.

**(2) As-implemented.** axes.py:81–84:
```
s = np.sort(np.asarray(s, dtype=np.float64))
n = s.size
emp = np.arange(1, n + 1) / n
return float(np.max(np.abs(emp - np.asarray(cdf_func(s), dtype=np.float64))))
```

**(3) Deviations.**
- Uses the upper step `emp = arange(1,n+1)/n` only; the standard two-sided KS
  takes `max` over both `i/n − F` and `F − (i−1)/n`. Here only `|i/n − F|` is
  evaluated, slightly under-counting D by up to 1/n. **[approximation]**
  (negligible at n≥20; same convention used in `compute_nns`, universality.py:113–117,
  and in `run_analytical_nns.ks_to`, line 122 — consistent across the codebase).

### Reference CDFs (universality.py)

**(2) As-implemented.**
- Poisson PDF/CDF (universality.py:24–25, 38–39): `exp(−s)`, `1 − exp(−s)`. ✔ canonical.
- GOE Wigner surmise (universality.py:28–30, 42–44):
  `(π/2)·s·exp(−π s²/4)`, CDF `1 − exp(−π s²/4)`. ✔ canonical.
- GUE Wigner surmise (universality.py:33–35): `(32/π²)·s²·exp(−4 s²/π)`. ✔ canonical.
- GUE CDF (universality.py:59–64): **no closed form** — numerically integrated:
  ```
  grid = np.linspace(0, max(float(s.max()) if s.size else 1.0, 5.0), 4001)
  pdf = nns_gue(grid)
  cdf_grid = np.concatenate([[0.0], np.cumsum(0.5*(pdf[:-1]+pdf[1:])*np.diff(grid))])
  return np.interp(s, grid, cdf_grid)
  ```

**(3) Deviations.**
- GUE CDF by trapezoidal cumulative integration over a grid whose top is
  `max(s.max, 5.0)`. **[approximation]** Subtle point: when `_w1_cdf` calls this
  on `grid` reaching up to `max(8.0, s_max)`, the internal grid auto-extends to
  cover it, so no truncation mismatch. The docstring (universality.py:48–57) sketches
  a closed form then explicitly says "just integrate trapezoidally … We use that
  here." **[intentional+documented]**

### _brody_b (axes.py:134), brody_pdf (axes.py:139), I8_brody_q (axes.py:147)

**(1) Canonical.** Brody P(s;q) = (q+1) b s^q exp(−b s^{q+1}),
`b = [Γ((q+2)/(q+1))]^{q+1}`; q=0 Poisson, q=1 GOE-Wigner. Fit q by MLE.

**(2) As-implemented.** axes.py:136, 142–144:
```
return float(_gamma((q + 2.0) / (q + 1.0)) ** (q + 1.0))           # _brody_b
b = _brody_b(q)
return (q + 1.0) * b * np.power(s, q) * np.exp(-b * np.power(s, q + 1.0))
```
MLE (axes.py:150–160):
```
s = s[(s > 0) & (s < 10.0)]
def nll(q):
    p = np.maximum(brody_pdf(s, q), 1e-300)
    return -np.sum(np.log(p))
res = minimize_scalar(nll, bounds=(0.0, 1.0), method="bounded", options={"xatol":1e-4})
```

**(3) Deviations.**
- b(q) formula exactly canonical. ✔
- q is bounded to **[0, 1]** (axes.py:158), so the fitter cannot express
  super-GOE (q>1) repulsion. **[intentional+documented]** (docstring axes.py:148
  "Brody q ∈ [0,1]"). This is a one-sided fitter — relevant to the known
  "one-sided fitters blind to super-Poisson" lesson, but here the cap is the
  upper (repulsive) side.
- Spacings hard-clipped to s<10 before the fit (axes.py:150). **[approximation]**

### I9_berry_robnik_rho (axes.py:163)

**(1) Canonical.** Berry-Robnik: gap density mixing a Poisson fraction (1−ρ)
and a GOE fraction ρ; ρ by MLE.

**(2) As-implemented.** axes.py:166–172 — delegated:
```
s = s[s > 0]
return float(_fit_br_rho(s, n_bootstrap=1)["rho_mle"])
```
`_fit_br_rho = phase34e.run_berry_robnik.fit_rho` (axes.py:51, "CORRECTED fitter").

**(3) Deviations.**
- Math lives in `phase34e/run_berry_robnik.py` — **not read here** [boundary]. The
  axes.py call sets `n_bootstrap=1` purely "to keep the percentile step non-empty
  while staying cheap" (axes.py:170–171) and discards the bootstrap σ. The fitter
  was the subject of the "synthetic-validate fitters" Berry-Robnik bug fix; that
  fix is in phase34e, not audited in this pass. **[boundary — verify in phase34e]**

### I10_cv (axes.py:175), I11_mass03 (axes.py:191)

**(1) Canonical.** CV = σ/μ of spacings (Poisson→1, GUE≈0.42, GOE≈0.52, clock→0);
mass<0.3 = fraction of spacings below 0.3 (clustering indicator).

**(2) As-implemented.** axes.py:183–184, 193:
```
m = s.mean(); return float(s.std() / m) if m > 0 else None      # CV
return float(np.mean(s < 0.3))                                  # mass03
```

**(3) Deviations.**
- `s` here is the unit-mean trimmed `canonical_spacings`, so CV ≈ σ(s) (μ≈1).
  Computed on the **trimmed** array → the 2%/98% edge trim slightly shrinks CV
  relative to the full spacing set. **[approximation]**
- Docstring (axes.py:176) gives "GUE≈0.42" — **CORRECT.** GUE Wigner-surmise CV =
  √(⟨s²⟩−1) = √(3π/8 − 1) = √0.1781 = **0.422**. (0.522 is the *GOE* value, √(4/π−1).)
  **[NOT a deviation — corrected 2026-06-30 after reviewer catch; the original audit
  pass miscomputed √0.178 as 0.522 and wrongly flagged this as a bug. Empirically
  confirmed live: GUE β=2 I.10_cv=0.448, GOE β=1=0.558, both converging to the
  surmise values.]**

### _ordered_intervals (axes.py:206), I12_cv2 (axes.py:215), I13_lv (axes.py:227)

**(1) Canonical.**
- CV2 (Holt 1996): `⟨ 2|I_i − I_{i+1}| / (I_i + I_{i+1}) ⟩` over adjacent ISI pairs.
- Lv (Shinomoto 2003): `⟨ 3 ( (I_i − I_{i+1})/(I_i + I_{i+1}) )² ⟩`.
Both rate-drift-robust, parameter-free; Poisson→1.

**(2) As-implemented.** axes.py:210–212, 223–224, 233–234:
```
p = np.sort(np.asarray(positions)); d = np.diff(p); return d[d > 0]   # _ordered_intervals
a, b = d[:-1], d[1:]
return float(np.mean(2.0 * np.abs(a - b) / (a + b)))                  # CV2
return float(np.mean(3.0 * ((a - b) / (a + b)) ** 2))                 # Lv
```

**(3) Deviations.**
- CV2 and Lv match Holt 1996 / Shinomoto 2003 **exactly**. ✔ CONFIRMED rate-robust forms.
- `_ordered_intervals` **sorts** positions before diffing (axes.py:210). For a
  genuine temporal spike train the times are already monotone so this is a
  no-op; for a non-monotone "position" sequence it would re-order, but the
  docstring states these need raw time-ordered positions and the contract feeds
  spike times. NOT trimmed / NOT unit-mean — adjacency preserved (correct for
  local measures). **[intentional+documented]** (axes.py:207–209, 238–240).
- Burst handling: these are the explicit Phase-37 fix for the CV-16
  slow-drift/epoch-gap artifact (docstrings axes.py:218–219). Matches the memory
  note. No separate burst-removal; rate-robustness is intrinsic to the adjacent-pair form.

---

## FAMILY II — long-range

### UNFOLDING / NORMALIZATION note (load-bearing)

axes.py Family II consumes `positions` **directly, no trim** (contract axes.py:16–17).
The mean-density unfold is upstream and substrate-specific. For AM it is the
rotation-number IDS (unfold_rotnum.py:38–53, quoted in §UNFOLDING below). Σ²/Δ₃
windows are placed in **position units**; only if positions are unit-mean does
`L` read as "mean-spacing units." No re-normalization to unit mean happens inside
Family II — so if a caller hands Family II non-unit-mean positions, the L scale
is silently off. **[intentional+undocumented risk]**

### matched_L (axes.py:255), _window_starts (axes.py:269)

**(1) Canonical.** Σ²(L)/Δ₃(L) are functions of window length L (mean spacings),
averaged over many window placements / an ensemble.

**(2) As-implemented.** axes.py:260, 271–274:
```
return float(np.clip(n_events * frac, lo, hi))           # frac=0.02, lo=5.0, hi=50.0
...
span = float(e[-1] - e[0])
if L >= span: return None
n_win = int(np.clip(span / L, 5, N_WIN_CAP))             # N_WIN_CAP=400
return np.linspace(e[0], e[-1] - L, n_win)
```

**(3) Deviations.**
- L is chosen as a **fraction of event count** (0.02·n, clamped [5,50]), not a
  fixed physical L or a swept L-curve — a single scalar per cell. Self-flagged
  (axes.py:257–259 "Flagged choice"). **[intentional+documented]**
- `n_win = clip(span/L, 5, 400)`: windows tile with stride L (≈non-overlapping at
  the floor) up to a cap of 400 placements. Capped for speed (axes.py:263–265).
  Number-variance averaging over ≤400 windows. **[intentional+documented]**

### II1_sigma2_at_L (axes.py:277)

**(1) Canonical.** Σ²(L) = Var(number of points in a window of length L).

**(2) As-implemented.** axes.py:288–290:
```
counts = (np.searchsorted(e, x0 + L, "left")
          - np.searchsorted(e, x0, "left")).astype(np.float64)
return float(np.var(counts, ddof=1)) if counts.size > 1 else None
```

**(3) Deviations.**
- Exact sample variance (ddof=1) of window counts. ✔ canonical.
- No reference GUE/Poisson curve computed here — II1 returns the raw observed
  Σ². Comparison to references is done downstream (the commit message notes the
  load-bearing long-range verdict uses **Monte-Carlo** ensembles, not the
  analytic curves). [code]

### II2_delta3_at_L (axes.py:293)

**(1) Canonical.** `Δ₃(L) = (1/L) · min_{a,b} ∫₀^L [N(x) − ax − b]² dx`,
averaged over placements. Poisson Δ₃ = L/15; GUE ≈ (1/2π²)(ln L + …).

**(2) As-implemented.** axes.py:304–312:
```
for x0 in starts:
    xs = np.linspace(x0, x0 + L, DELTA3_EVAL)            # DELTA3_EVAL=64
    Nx = np.searchsorted(e, xs, side="right").astype(np.float64)
    A = np.vstack([xs, np.ones_like(xs)]).T
    coef, *_ = np.linalg.lstsq(A, Nx, rcond=None)
    resid = Nx - A @ coef
    vals.append(np.mean(resid ** 2))
return float(np.mean(vals))
```

**(3) Deviations.**
- The canonical `(1/L)∫[…]²dx` is approximated by `mean(resid²)` over 64
  uniform sample points on [x0, x0+L]. Since the points are uniform,
  `mean(resid²) ≈ (1/L)∫ resid² dx`, so the implicit 1/L normalization is
  **present and correct**. **[approximation]** (the integral → 64-point average).
- The best-fit line is by ordinary least squares on the staircase samples
  (canonical Δ₃ minimizes the continuous L²; the discrete lstsq is the
  consistent estimator). **[approximation]**
- No analytic reference curve invoked. [code]

### II3_K_at_tau (axes.py:315) + spectral_form_factor (universality.py:173)

**(1) Canonical.** `K(τ) = (1/N)|Σ_n e^{2πi τ x_n}|²`; GUE ramp K≈τ (τ<1)
then plateau 1; Poisson flat ≈1.

**(2) As-implemented.** universality.py:187–189:
```
z = np.exp(2j * np.pi * t * e)
K[i] = float(np.abs(z.sum()) ** 2 / N)
```
axes.py:320–324 evaluates the SFF on a 120-point t-grid to t_max=max(1.2τ,2) and
returns `K[argmin|t−τ|]` at τ=1.

**(3) Deviations.**
- Form-factor formula exactly canonical. ✔
- Returns a single nearest-grid sample at τ=1 (no smoothing/τ-averaging), so K(1)
  is noisy (the SFF is notoriously self-averaging only over a τ-window). Lower
  priority per docstring (axes.py:316). **[approximation]**

### pair_correlation (universality.py:194) — present, not on Family II axis path

R₂(r) histogram of pair separations / Poisson expectation (universality.py:221–230).
GUE reference `1 − sinc²(πr)` (universality.py:230) ✔ canonical; GOE reference
mentioned in docstring (universality.py:204) but **not computed** (only `gue` and
`poisson` returned, universality.py:231). **[intentional+undocumented]** (docstring
lists a GOE form the return dict omits). Neighbour cap `e[i+1:i+1+200]` (universality.py:215)
truncates long-range pairs → R₂ biased low at large r. **[approximation]**

---

## FAMILY III — RF / Ramanujan

### ramanujan_sum_array (arithmetic_toolkit.py:88)

**(1) Canonical.** Ramanujan sum `c_q(n) = Σ_{a:(a,q)=1} e^{2πi a n/q}`; Hölder:
`c_q(n) = μ(q/d)·φ(q)/φ(q/d)`, `d = gcd(n,q)`.

**(2) As-implemented.** arithmetic_toolkit.py:92–100:
```
g = np.gcd(n_arr, q); phi_q = _phi(q)
for d in np.unique(g):
    m = q // d_int
    out[g == d_int] = _mu(m) * phi_q / _phi(m)
```
with `euler_phi` (55–60) and `mobius` (63–69) by trial-division factorization. ✔ exactly Hölder's identity.

**(3) Deviations.** None — canonical. φ, μ correct. [code]

### ramanujan_fourier a_q (arithmetic_toolkit.py:130)

**(1) Canonical.** RF coefficient `a_q = (1/φ(q)) · lim_{N→∞}(1/N) Σ_{n≤N} f(n) c_q(n)`.

**(2) As-implemented.** arithmetic_toolkit.py:177–180:
```
for q in range(1, q_max + 1):
    c = ramanujan_sum_array(q, N)
    a[q - 1] = float(np.mean(f * c)) / _phi(q)
```
where `f` is either unit-mean spacings (normalize=True, lines 154–163) or an
integer-bin occupancy indicator (normalize=False, lines 164–175).

**(3) Deviations.**
- Finite-N mean replaces the Cesàro/density limit → the c_q are only
  **approximately orthogonal**; inter-band leakage at finite window, worst at
  high q. **[intentional+documented]** (the 1a6c7a1 commit / README caveat #1
  explicitly added this). **[approximation]**

### peak_q selection (arithmetic_toolkit.py:182–190)

**(2) As-implemented.**
```
abs_a = np.abs(a)
if q_max >= 2:
    order = np.argsort(abs_a[1:])[::-1] + 2
    top10_q = order[:10].tolist()
    peak_q = int(top10_q[0])
```
`peak_q` = the q≥2 with largest |a_q|; **q=1 (DC, mean of intervals) excluded**
(comment line 183). [code] No deviation — sound choice, documented.

### III1_p_concentration (axes.py:341), III2 (axes.py:351), III4 (axes.py:356)

**(1) Canonical (intended).** "Concentration at prime p" would naturally be
power at q a multiple of p, e.g. Σ_{k} |a_{kp}|.

**(2) As-implemented.** axes.py:345–348:
```
v = np.asarray(rf_amp_per_q); if v.size < p: return None
return float(v[p - 1])                                   # |a_p|, 1-indexed
```
III2 = `[|a_2|,|a_3|,|a_5|,|a_7|]` (SMALL_PRIMES, axes.py:338); III4 = `sum`(III2) (axes.py:359).

**(3) Deviations.**
- Reduction is **"amplitude at q=p" (the single peak), NOT a sum over multiples
  of p**. Self-flagged (axes.py:343–344 "FLAGGED reduction"). **[intentional+documented]**
- 1-index `v[p-1]` correctly maps to |a_p| since `amplitudes` is q=1..q_max. ✔

---

## ARITHMETIC ANALYTICAL-NNS (run_analytical_nns.py)

### to_zeta_density (run_analytical_nns.py:77)

**(2) As-implemented.** lines 78–81:
```
return np.interp(unfolded_uniform_in_0_N,
                 np.linspace(0.5, N - 0.5, N),
                 np.asarray(zeta_sorted, dtype=np.float64))
```
Maps uniform-density unfolded positions (in [0,N]) onto the ζ-zero density via
linear interpolation against the ζ ordinates at half-integer ranks. **[code]**
(half-integer rank grid is the standard mid-point quantile convention.)

### analytical_nns (run_analytical_nns.py:84)

**(1) Canonical.** Passage-time spacings of zeros through each PLL frequency,
normalized per-band and pooled (the "matched leg" contract).

**(2) As-implemented.** lines 96–110:
```
elig = ((t_n_array >= (transient_s + 1.0) * f_pll) &
        (t_n_array <= (dur_s + 1.0) * f_pll))
elig_t = np.sort(t_n_array[elig])
threshold = lock_confirm_s * f_pll / (tongue_prefac * (2.0 / (p + q)) ** 2)
qualifying = elig_t[elig_t >= threshold]
spacings = np.diff(qualifying) / f_pll
sp_norm = spacings / spacings.mean()
```

**(3) Deviations.**
- Passage time `t* = t_n/f_pll − 1` is a **one-period left-truncation**; the −1
  offset cancels under `np.diff`, making spacings band-frequency invariant after
  the `/f_pll` rescale + unit-mean norm. **[intentional+documented]** (README
  caveat #2 from commit 1a6c7a1). [code]
- Dwell threshold derives from a tongue-width model
  `Δf = tongue_prefac·f_pll·(2/(p+q))²` (lines 100–103) — a modelled detector
  gate, not a pure mathematical spacing operation. **[intentional+documented]**
  (this is the analytical surrogate for the PLL detector).

### measured_nns (run_analytical_nns.py:224)

**(2) As-implemented.** lines 230–235: per PLL, `extract_dwells` → `np.diff(lock_onsets)`
→ `/mean` → pool. Same per-band unit-mean-then-pool as analytical. KS via `ks_to`
(line 117, same one-sided convention as `_ks_cdf`). [code] No deviation in the
NNS arithmetic itself; the comparison is the load-bearing object.

---

## UNFOLDING (where mean density is removed) — summary

- **axes.py performs NO unfolding.** Contract (axes.py:9–22): substrates hand in
  already-unfolded unit-mean positions.
- **AM leg unfolder** (`ids_rotnum`, unfold_rotnum.py:38–53): reference-free
  rotation-number / Sturm-count IDS over L sites, φ-ergodic-averaged, then
  `×len(e)` (unfold_rotnum.py:60) to give unit-mean positions. This is a
  **local/spectral-staircase** unfold, not a polynomial fit, not arcsine.
- For non-AM substrates (neural, ζ, arithmetic) the unfold is done in their own
  ports / by `to_zeta_density`. Type of unfold is therefore **substrate-specific
  and NOT centralized** — a structural finding, not a bug.

## NORMALIZATION — summary

- NNS path: unit-mean enforced inside `spacings` (`d/m`, unfold_rotnum.py:73) and
  redundantly in `compute_nns` (`s/s.mean()`, universality.py:110).
- Family II: **no** internal unit-mean renorm; relies on upstream. L scale is
  event-count-fraction (matched_L). Σ² ddof=1; Δ₃ has the implicit 1/L via the
  64-point mean.
- RF: f normalized to unit mean (normalize=True) before the c_q projection.

## REFERENCE CURVES — provenance and the GOE/GUE fix

- **Marginal NNS** (GUE/GOE/Poisson surmises + CDFs, universality.py:24–64): analytic
  closed forms (GUE CDF trapezoidal). Used by axes.py Family I, run_analytical_nns,
  arithmetic_toolkit `_classify`. **All consistent.** ✔
- **Number-variance analytic Σ²(L) curves** (universality.py:158–169): the object of
  commit 1a6c7a1. Post-fix:
  ```
  gue_curve = (1/π²)(log_term + γ + 1)
  goe_curve = (2/π²)(log_term + γ + 1 + log2 − π²/8)
  ```
  Leading coefficient 2/(βπ²): GOE(β=1)=2/π², GUE(β=2)=1/π², so GOE/GUE→2. ✔ correct.
- **Fix consistency across files:** grep over the whole tree shows the swapped-curve
  pattern lived in **exactly one place** — `universality.number_variance`. axes.py
  Family II does **NOT** import or use `goe_curve`/`gue_curve`; `II1_sigma2_at_L`
  returns the raw observed Σ² and the load-bearing long-range verdict compares to
  Monte-Carlo ensembles (per commit msg). The only consumers of the analytic
  curves are `run_phase3.py` (plot lines) and `run_second_order.py` (printed table),
  both calling the single fixed function. **⇒ the fix is fully consistent; there is
  no second copy to drift, and axes.py was never affected.** ✔
- **Δ₃ analytic log-law:** NOT hard-coded anywhere on the live axis path (Δ₃
  returns raw observed value); no out-of-range asymptotic is applied. ✔
- **SFF / R₂** references: GUE forms analytic and canonical; R₂ GOE form is in a
  docstring but not returned (noted above).

---

## FINDINGS INDEX (by severity)

- **[RETRACTED 2026-06-30 — audit error, not a code bug]** axes.py:176 — `I10_cv`
  docstring "GUE≈0.42" is CORRECT (GUE surmise CV = √(3π/8−1) = 0.422; 0.522 is GOE).
  The original pass miscomputed the surmise and wrongly flagged the docstring. Empirically
  confirmed: GUE β=2 I.10_cv=0.448, GOE=0.558. No fix needed.
- **[intentional+undocumented]** axes.py:13–14 / unfold_rotnum.py:72 — "2–98% **tail**
  trim" is actually an **ordinal edge trim** (boundary spacings), not a magnitude trim.
- **[intentional+undocumented]** universality.py:204 vs 231 — `pair_correlation`
  docstring promises a GOE R₂ form the return dict omits.
- **[intentional+undocumented risk]** Family II applies no internal unit-mean
  renorm; L scale is silently wrong if upstream positions are not unit-mean.
- **[boundary]** Berry-Robnik ρ MLE (axes.py:163→phase34e) not audited here.
- **[approximation, benign]** one-sided KS (max over i/n only) used uniformly;
  GUE CDF & Δ₃ integral & W1 all grid-discretized; Brody q∈[0,1] one-sided cap.
- **Reference-curve fix: FULLY CONSISTENT** — single source, no axes.py impact.

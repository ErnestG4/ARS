# MORNING — overnight task block (honesty ledger)

Executed against the pre-registered brief. **Honest framing:** this ran in a *bounded interactive session*, not a
literal 5-hour unattended daemon — so the "night budget" was the session. Task 1 was executed to its pre-registered
gate outcome; Task 3-D3 completed; the remaining heavy jobs (Task 2, Part-I M=2000, D1 λ→128/256) are **pending/resumable
parameter turns**, not completed — with exact run commands below. Failures and no-gos appear at the same prominence as
passes. Seeds: 20240517 throughout. No gate was changed after launch.

**Citation correction (found during Task 1 cite-and-verify):** the band-splitting work is **Raymond *1995*** (not 1997);
the reconstructable combinatorics live in the 2024 review [arXiv:2409.10920](https://arxiv.org/abs/2409.10920) and require
coupling **V>4** (all λ∈{8,24,32} qualify).

---

## Task 1 — π spectral dimension at depth 5 (q=33102) → **HARD STOP (no-go), no dimension banked**
Artifacts: `task1_pi_depth5.py`, `task1_pi_depth5.json`, `task1_checkpoint.json`.

- **K-jump pre-registration CONFIRMED (exact arithmetic):** with the 292 included, K jumps **4.21 (depth-4) → 9.83
  (depth-5)** — `(3·7·15·1)^{1/4}=4.213`, `(3·7·15·1·292)^{1/5}=9.834`. Direction of the registered prediction
  (thinner spectrum ⇒ lower dim) could NOT be measured (see below).
- **Fast trace-map recursion FAILED its validation gate** (`max_trace_err ≈ 3.7e159` vs the direct O(q) product at
  q=113). The Sturmian substitution convention `T_k=T_{k-2}T_{k-1}^{a_k}` with single-letter seeds does not reproduce
  the true period-q approximant (the substitution is subtler than literal word-powers). Per the hard rule, the fast
  accelerator was **not trusted**; fell back to the direct product (trusted by construction).
- **Structural gate (band-count == q_k) FAILED at level 1:** the direct-product + multi-level nested refinement found
  **1 band at q=7** (expected 7), cascading (λ=8: counts 1/3/6/53; λ=24: 1/0/2/5; λ=32: 1/0/0/0). Root cause: at low
  approximant level the 7 bands are **barely split — the gaps are sub-grid-resolution** — so a uniform grid merges them.
  Resolving band-count==q at every level robustly needs the **Raymond band-splitting combinatorics** (to place bands
  without relying on grid resolution) or careful edge root-finding + extended precision — none achievable this session
  (Raymond source un-fetchable at 10MB; fast recursion unverified).
- **Verdict:** pre-registered hard-stop ("any band-count mismatch is a hard stop"). **No π depth-5 dimension is banked.**
  The un-banked dim numbers in the json (0.4–1.2, non-monotone, estimators disagreeing) are **untrustworthy artifacts of
  the unresolved spectrum** and are explicitly NOT results. Face-1's "insufficient depth" for π therefore **stands** —
  converting it requires a dedicated clean-room session implementing Raymond-1995 band bookkeeping.

## Task 2 — π's Khinchin trajectory to N=10⁵ → **PENDING (not run this session)**
Not executed — π to 10⁵ needs ≳55k decimal digits (Lévy `log₁₀ q_N ≈ 0.515·N`) and the orbit-MC bands; a heavy job left
for a compute window. It is a clean parameter turn on the frozen refsuite (`cf_two_precision`, `running_geomean`,
`gauss_orbit_quotients`, `iid_gk_quotients` all take N as an argument; `DEPTHS` already includes 10⁵). **Resumable** via a
driver in `approximability/` importing those frozen functions with the two-precision gate (bank quotients up to first
disagreement between D and 1.1·D digits). *Prior banked point stands:* geomean 2.683 @N=100, inside the iid-GK band.

## Task 3 — certainty upgrades
### D3 → Q=10⁶ window-scaling → **RAN** (`task3_d3_windowscaling.py`, `task3_d3.json`)
- **Invariant `p'q − pq' = 1` held on every consecutive pair, all targets, all Q** (frozen refsuite gate). ✅
- **e pre-registration CONFIRMED:** e's max quotient with q≤Q grows **8 → 8 → 10** across Q∈{10⁴,10⁵,10⁶}.
- **CORRECTION (this replaces my first-pass "noisy/inconclusive" verdict — I mislabelled deterministic structure as
  noise; the mirror of a flattering error, corrected the same way).** The `max_gap/mean` statistic has a **closed form**,
  verified against tonight's own numbers to median ratio **1.004** (range 1.000–1.023, all 15 cells):
  > **`max_gap/mean ≈ 3Q / (π² · q_min)`**, where `q_min` = smallest denominator in the aperture.
  (Flanking gap of `p/q_min` ≈ `1/(q_min·Q)`; Farey mean gap ≈ `π²/(3Q²)`.) The window width `w ∝ Q⁻²` (fixed count), so
  as Q grows the aperture **slides across each target's own convergent ladder** and `q_min` jumps at each convergent —
  a **deterministic sawtooth**, not noise. The extracted `q_min` proves the mechanism: golden `55,610,6765` (Fibonacci),
  √2 `70,985,5741` (Pell), π `99,113,30955`. The "31→269→10" sequence is the aperture crossing π's convergents
  (q_min: 99→113→~33102). **Panel B's banked π detection 403 = 3·(1.5×10⁵)/(π²·113) = 403.5 EXACTLY** — it was never
  just "an anomaly"; it was a q_min=113 reading.
- **Two confirmations inside the confirmation:**
  - *One-sided bound (proves floor, not fit):* all 15 ratios are **≥1** (1.000–1.023) because `gap≈1/(q_min·Q)` takes the
    neighbor denom at its ceiling `q'≤Q`, so the true gap `≥1/(q_min·Q)` — the prediction is a hard floor; measured sits
    at/above it and converges down as `q'→Q`. Generic scatter would straddle 1; a floor sits on one side.
  - *π's ladder is SEMICONVERGENTS, not convergents (verified arithmetic):* `99`,`30955` are NOT π convergents.
    `99=1+14·7` (j=14 on the a₂=15 staircase), `30955=106+273·113` (j=273 on the a₄=292 staircase). A Q-sweep 380k→1.6M
    shows q_min = `106+j·113` with **j=194,235,263,279,285** — exact semiconvergents climbing toward the full 33102 (j=292).
- **UPGRADE (one notch further):** the max-gap is a **q_min detector** = smallest denominator in the aperture = best
  *one-sided* approximant = (mid-quotient) a **semiconvergent**. So during the long climb inside a large quotient, q_min
  creeps up the semiconvergent staircase ~linearly with the aperture — **the instrument watches the 292 being built step
  by step in real time as Q slides. It resolves the INTERIOR of a quotient** — something none of the arc's three axes
  (K-dimension, Λ-Farey-detection, Λ-record) can do. Converts Panel-B Face-2 from *qualitative detection* to *predicted
  quantitative curve*.
### D3 REDO (semiconvergent sawtooth, PREDICT→measure) → **DONE** (`task3_d3_redo.py`, `.json`, `.png`)
Predictions computed FIRST from α + aperture only (Stern–Brocot minimal-denominator descent = best one-sided approximant
= semiconvergent), zero enumeration; then measured against the frozen `enumerate_window` and overlaid.
- **q_min prediction match = 100.0% of 230 windows, all 5 targets.** The semiconvergent precompute predicts *every tooth*
  of the sawtooth with zero simulation. `max_gap/mean = 3Q/(π²·q_min)` holds to meas/pred median **1.003–1.005**.
- **π's predicted ladder is semiconvergents** (`99,106,113,18525,20333,22141,…` = `106+j·113` climbing the 292), verified
  `⊄ π convergents`; golden = Fibonacci, √2 = Pell. A convergent-list precompute would miss all of π's interior teeth —
  the semiconvergent Stern–Brocot descent is the correct precompute.
- **One-sided floor:** holds exactly on the `max_gap` term (`q'≤Q`); a few windows dip to 0.980–0.985 (≤2%) from
  **finite-window fluctuation of the *mean* gap** (not exactly `π²/(3Q²)` at 12k fractions) — not a mechanism failure.
- **Net:** the Λ-instrument is now a **quantitative predicted curve** (100% q_min-predicted, zero-sim), and it **resolves
  the interior of a quotient** — Face-2 upgraded from qualitative detection to a pre-registered, more-falsifiable
  (more-teeth) prediction. *(Bug found & fixed mid-run: frozen `enumerate_window` uses `[α−w,α+w]` (w = half-width); my
  first predictor used `[α−w/2,α+w/2]` → 44% match; corrected to the frozen convention → 100%.)*

### Part I M=2000 → **PENDING** (heavy, ~10× the 300s baseline). Run: `REFSUITE_M=2000 .venv/bin/python run_all.py` in `mathtest/` (parameter turn, env-exposed).
### D1 λ→{128,256} → **PENDING.** Resumable via a driver importing frozen `refsuite.d1_fibonacci.discriminant/find_bands_nested` with lam∈{128,256} (the functions take `lam`; only the default `LAMBDAS` grid is hardcoded — no refsuite edit).

---

## Constitution compliance
- Gates fixed pre-launch; **none changed** overnight. Task-1's band-count gate and fast-validation gate both **fired and
  were obeyed** (→ hard stop), not tuned away.
- Hard-fail preserved state: `task1_checkpoint.json` written per-λ; no retry loops.
- Deterministic seed 20240517 logged in every artifact.
- No logic edits to the frozen refsuite; Task-3-D3 imported its functions unchanged (the one mismatch — `window_gap_stats`
  returns a tuple, not a dict — was adapted in the *panel-side* driver, not the refsuite).
- This `MORNING.md` written unconditionally.

## NEXT / QUEUE (sorted)
1. **Task-1 completion — clean-room session.** Raymond-*1995* band-splitting combinatorics + edge root-finding + extended
   precision. **Hardened rule (earned by tonight's failure):** *derive the transfer-matrix recursion from the substitution
   structure in-session and validate it against the direct product at q=7 AND q=113 before any deep run — treat the
   brief's `T_k=T_{k-2}T_{k-1}^{a_k}` as a HYPOTHESIS, not an answer* (it failed validation tonight, trace-err 10¹⁵⁹).
2. **D3 redo — pre-registered semiconvergent sawtooths → ✅ DONE** (`task3_d3_redo.py/.json/.png`). See result below.
3. **Pending parameter turns** (whenever a session has the hours): Task-2 55k-digit π trajectory, Part-I M=2000,
   D1 λ→{128,256}. Commands are above; they keep.

## One-line status
Task 1 **NO-GO / hard-stop** (band-count gate unresolvable without Raymond combinatorics — π depth-5 stays "insufficient
depth", honestly; the spec's recursion was a hypothesis that failed validation); Task 3-D3 **ran and OVER-delivered** —
the "noise" is a **deterministic `q_min` detector**, closed form `3Q/(π²·q_min)` verified to ratio 1.004 across all cells
and exact on Panel-B's 403; the Λ-instrument is now **quantitative/precomputable**. Task 2 + Part-I-M2000 + D1-λ128/256
**pending/resumable** (parameter turns). Nothing faked; the one verdict I got wrong (D3 "noisy") is corrected above with
its proof.

# The rail is a detector — reading arm (e)'s bug instead of only fixing it

**Zero unclipping. Zero backfill. Zero negative-side calibration.** Everything here is read off the
*existing, broken* estimators plus synthetic ground truth. The repair is still required; it is no
longer a precondition for a result.

> **Doctrine (new, §9 arm (e) dispersion clause): at a rail, the confidence interval is the signal
> and the point estimate is noise.** A railed estimator's *dispersion* is informative even when its
> *location* is not. This is what makes (e) survivable rather than merely fatal.

---

## 1. `I_rep`: exactly-0.000 is unreachable by the null — at the table's own n

Three-row table through the **unmodified clipped** estimator, then the n-matched null distribution
(200 seeds/cell, at the cross-signal table's own n):

| n | process | min `I_rep` | median | **frac EXACTLY 0.000** |
|---|---|---|---|---|
| 1470 | **Poisson (null)** | 0.00238 | 0.0279 | **0.0 %** |
| 1470 | clustered σ=1.8 | 0.000000 | 0.000000 | **100.0 %** |
| 2000 | **Poisson (null)** | 0.00125 | 0.0241 | **0.0 %** |
| 2000 | clustered σ=1.8 | 0.000000 | 0.000000 | **100.0 %** |

**0/200 false positives on the null; 200/200 detections on strong clustering.** The mechanism is
general, not lognormal-specific: `I_rep` = 0 requires **R₂(r) ≥ 1 for *every* r ≤ 1** — no repulsion
at *any* scale — and Poisson's sampling fluctuations always dip below 1 somewhere.

⇒ **The cross-signal `0.000` entries are CLUSTERING DETECTIONS, not "undetermined."**

| signal | `rep_int_q` | old reading | **new reading** |
|---|---|---|---|
| Solar X-ray flares M+ | **0.000** | BL = "Poisson noise" | **CLUSTERED (detected)** |
| Fungal pool (Adamatzky) | **0.000** | BL = "Poisson noise" | **CLUSTERED (detected)** |
| Binance BTCUSDT day 1 | 0.018 | BL | **undetermined** (inside the Poisson range, median 0.024) |

Solar flares are **independently known-clustered from our own SOC phase**. The detector's first
firing is corroborated by ground truth we already held.

**Limit, stated:** one-sided and conservative. Mild clustering (σ=1.15) does **not** reach the floor
(0.0097 ≠ 0). `0.000 ⇒ clustered` is **sufficient, not necessary**. A nonzero `I_rep` licenses
nothing.

---

## 2. Brody/BR: the point estimate CANNOT do it — which is why the CI must

The tempting shortcut (railed value 6.6e-05 « Poisson's typical 2e-3, so just read the point
estimate) is **dead on measurement**:

| n | process | frac at rail (q < 5e-4) |
|---|---|---|
| 2000 | **POISSON (true null)** | **43.3 %** |
| 2000 | clustered σ=1.8 | 100 % |
| 2000 | GUE-ish (repulsive) | 0 % |

**True Poisson rails ~40 % of the time** (stable 38–43 % across n=200–2000). The rail is produced by
*both* processes. **The point estimate carries no verdict.** *(Recorded because I proposed the
shortcut and it was wrong — the CI route was not the fallback, it was the only route.)*

### The inverted discriminant — validated, and it is *better* than what it rescues

**Among railed cells only** (that restriction is the whole trick), bootstrap dispersion:

| true process | railed | boot_sd median | boot_sd max |
|---|---|---|---|
| **POISSON (true null)** | 22/40 | **0.00447** | **0.01119** — always **> 0** |
| clustered σ=1.15 | **40/40** | **0.00000** | **0.00000** |
| clustered σ=1.8 | **40/40** | **0.00000** | **0.00000** |

**Zero overlap. Perfect separation.** `boot_sd == 0` ⇒ pinned outside the reachable range ⇒
**clustered**. `boot_sd > 0` ⇒ sampling noise around a genuine null ⇒ **Poisson**.

And it **catches mild clustering (σ=1.15) at 40/40, which the `I_rep` zero-detector misses entirely
(≈0 %).** *The rescued instrument is strictly more sensitive than the one it rescues.*

---

## 3. The rail census — and a population verdict that needs NO bootstrap at all

**15,073 / 20,801 = 72.5 % of every banked `brody_q` in the zoo sits at the rail.**

Because P(rail | true Poisson) ≈ 0.40 is *measured*, excess railing is a **binomial test on the
banked scalars** — free, no recompute, no bootstrap:

| substrate | n | railed | obs P | binom p (1-sided) | verdict |
|---|---|---|---|---|---|
| **allen-hpf-cell** | 4326 | 4325 | **100.0 %** | < 1e-300 | **CLUSTERED** |
| **buzsaki-port-cell** | 4006 | 3983 | 99.4 % | < 1e-300 | **CLUSTERED** |
| **pvc-11** | 1159 | 1152 | 99.4 % | < 1e-300 | **CLUSTERED** |
| **dr-port-cell** | 1365 | 1346 | 98.6 % | < 1e-300 | **CLUSTERED** |
| **hc3-port-cell** | 916 | 868 | 94.8 % | 3.1e-276 | **CLUSTERED** |
| **ibl-port-cell** | 1556 | 1349 | 86.7 % | 5.6e-320 | **CLUSTERED** |
| **ret1-cell** | 325 | 278 | 85.5 % | 1.3e-64 | **CLUSTERED** |
| allen-hpf-pop / buzsaki-pop | 252 / 340 | 189 / 216 | 75 % / 63.5 % | 1.7e-29 / 1.9e-18 | **CLUSTERED** |
| qpo-* (4 variants) | 54–144 | — | 87–100 % | ≤ 3e-18 | **CLUSTERED** |
| lambda-star-classes | 108 | 108 | 100 % | 1.1e-43 | **CLUSTERED** |
| population-strat | 1454 | 471 | 32.4 % | 1.00 | — (Poisson-consistent) |
| **brocot.fm** | 4006 | 191 | **4.8 %** | 1.00 | — (**repulsive/structured**, rails *below* chance) |

**Every neural substrate in the zoo rejects Poisson.** Exactly as "neurons burst" predicts — and they
have all been sitting in the Poisson bin.

**Robust to a badly mis-specified P0** (the one number the test depends on): `allen-hpf-cell` rejects
even at **P0 = 0.99** (p = 5.9e-18); `pvc-11` survives to P0 = 0.95. The verdict does not rest on the
0.40 estimate being right.

### 3b. The decimation confound — RAISED, TESTED, DEFEATED (and the path claim was wrong)

**The challenge:** the census null (P(rail|Poisson)) was measured on clean synthetic Poisson, while
the banked cells came through a decimating unfold. Decimation *decorrelates*, which drives Brody q
**toward 0 = toward the rail** — so it could **manufacture** the railing. And the trigger is n>1500,
which is the same **hard gap / zero-common-support** that made E2 unidentifiable. If true, "every
neural substrate rejects Poisson" is partly *the instrument rejecting Poisson on their behalf*.

**(i) The path premise is FALSE.** `I.8_brody_q` is **not** on the decimating path. `axes.py:408,448`
(`Y[::len(Y)//max_pts]`) live inside **`V1_lyapunov` / `V2_correlation_dim`** — different axes.
`harvest.py:130`'s `JPF_CAP=1500` annotation is attached to **`QBAND_METHOD`**, which governs the
**q-band ARS axes** (`I.5q_ks_gue_med`, `ARS.rep_med`) — **not** Family-I. *Verify the path before
inheriting a confound from a sibling.*

**(ii) The null WAS instrument-matched all along.** The synthetic null was pushed through
**`I8_brody_q` itself**, so it inherited the same self-mean normalization (Mode-1-style circularity)
**and** the same `s < 10.0` spacing truncation. Decimation was the *only* unmatched leg.

**(iii) The decisive control — cells that were NEVER decimated.** Rail rate restricted to `n ≤ 1500`:

| substrate | undecimated cells | **% railed (undec)** | *(decimated arm)* |
|---|---|---|---|
| buzsaki-port-cell | 1341 | **100.0 %** | 99.1 % |
| dr-port-cell | 147 | **100.0 %** | 98.4 % |
| allen-hpf-cell | 1004 | **99.9 %** | 100.0 % |
| hc3-port-cell | 506 | **99.6 %** | **88.8 %** |
| ibl-port-cell | 200 | **97.0 %** | **85.2 %** |
| ret1-cell | 23 | **95.7 %** | 84.8 % |

**Cells that were never decimated rail at 95.7–100 %.** Decimation cannot manufacture what it never
touched. And where it *does* act it runs the **wrong way** — hc3 and ibl rail **less** when
decimated. **Decimation slightly *reduces* railing.** *(The within-substrate cell/pop pairs say the
same: `hc3-port-pop` and `dr-port-pop` are* more *decimated than their cell arms (93.9 %, 93.8 %) and
rail* far less *(48.7 %, 31.2 %). If decimation drove railing this is impossible.)*

**(iv) Palm–Khintchine is the free theoretical check, and it passes.** Superposition of many
independent point processes → **Poisson**. So the **pop/pooled** arms *should* read Poisson-consistent
— and they do (19.2 %, 0 %, 44.5 %) while single cells rail. **The cell↔pop contrast goes exactly the
way the theorem demands, with decimation held constant or inverted.** An independent ground truth the
detector was never fitted to.

**(v) P0 does NOT fall with n — so 0.40 was optimistic.** Measured P(rail|Poisson): 40.0 % (n=500),
52.5 % (2000), 47.5 % (10k), 57.5 % (30k), 47.5 % (70k). The MLE never resolves away from the bound
under Poisson. **Final census re-run at a conservative P0 = 0.60** (above *every* measured value),
**undecimated cells only**:

| substrate | undec | railed | % | binom p | verdict |
|---|---|---|---|---|---|
| buzsaki-port-cell | 1341 | 1341 | 100.0 % | 3.2e-298 | **CLUSTERED** |
| allen-hpf-cell | 1004 | 1003 | 99.9 % | 1.2e-220 | **CLUSTERED** |
| hc3-port-cell | 506 | 504 | 99.6 % | 3.2e-108 | **CLUSTERED** |
| ibl-port-cell | 200 | 194 | 97.0 % | 3.2e-35 | **CLUSTERED** |
| dr-port-cell | 147 | 147 | 100.0 % | 2.4e-33 | **CLUSTERED** |
| ret1-cell | 23 | 22 | 95.7 % | 1.3e-04 | **CLUSTERED** |
| allen-hpf-pop / buzsaki-pop / population-strat / -fingerprint | — | — | 64.6 / 44.5 / 19.2 / 0 % | ≥ 0.14 | — (Poisson-consistent) |

**Every neural CELL substrate: CLUSTERED. Every pooled/population object: Poisson-consistent.**
Identifiable, instrument-matched, decimation-controlled, conservative null. **The headline stands.**

*Caveat to quote in RESULTS:* cells within a session/animal are **not independent**, so these binomial
p-values are optimistic. At these counts no design effect rescues Poisson — but **quote the count and
the substrate, not the p-value.**

*New observation, banked not chased:* `I8_brody_q:150` also does `s = s[(s > 0) & (s < 10.0)]` —
**it discards every spacing > 10× the mean**, i.e. exactly the heavy tail that *is* the clustering
signature. It is applied to null and data alike (so it does not bias the test above), but it is a
**third** censoring at the same call site.

The arithmetic substrates behave **correctly** (`brocot.fm` rails at 4.8 %, *below* chance — genuine
repulsion). **The bug's damage is concentrated exactly where clustering is the substrate's expected
state.** The instrument failed precisely where the biology lives.

---

## 4. Two faces of arm (e) — name the second or it gets rediscovered

- **Face 1 (a censored instrument launders a NULL).** The `I_rep` flat null in the 32b audit.
- **Face 2 (a censored instrument MANUFACTURES a CONFIRMATION).** `phase36/falsification_calibrator.py`
  :140,164 reads the repulsion axis's *silence* on the clustered side as a **confirmed prediction**
  (*"ALL BL: near-Poisson transition INVISIBLE to both (taxonomy holds)"*). But the axis is
  **constructed unable to leave BL there.** The confirmation was manufactured by the clip.

**Same disease, opposite sign — and the confirming direction is the one nobody audits.** Arm (c) said
a *gate* can launder a null; (e) says an *instrument* can launder a null **and forge a confirmation**.
One arm, two faces.

## 5. The validation lesson, in its strongest form

Not "add a case outside the range." The general rule:

> **Probing at the endpoints of an instrument's reachable range cannot detect that the range is the
> bug. A gate built from the instrument's own vocabulary is a tautology with a PASS attached.**

`validate_fitters.py` was **structurally incapable of failing** — and it said **MANDATORY**. This
belongs beside arm (c)'s conjunction rule: *the same shape — a test whose failure mode is unreachable
by construction.*

## 6. Provenance map — which verdicts are safe, which are uncertified

| status | axes |
|---|---|
| **SAFE** (boundary ≠ null, or null in the interior) | `ks_gue`, `ks_poisson` (sign-blind but nonzero), `⟨r̃⟩` (null 0.386, **interior**), `I10_cv`, `I11_mass03`, `I12_cv2`, `I13_lv` |
| **UNCERTIFIED** (floor == null) | `I8_brody_q`, `I9_berry_robnik_rho`, `I_rep`/`rep_int_q`/**all BL verdicts**, `bulk_recovery` mass→σ |

**Open (next):** every claim of the form *"substrate X sits at the Poisson pivot"* must be traced to
its estimator. If it came through Brody/BR/`I_rep`, it is **not merely uncertified — it is in the
direction the rail manufactures**, and the substrates most likely to be misfiled there are **the most
clustered ones.** Same rank inversion as BL, one level up.

---

## 7. The pivot trace — three claims, and a correction to my own path claim

**Target found.** The claims resting on the railed axes are in `cross_substrate/findings_log.md`
§P2 / viewpoint-dependence / L-zeros caveat — all on the **Brody q × BR ρ** plane. Per-claim, with
the corroboration structure recorded (arm (d)):

### (a) "pvc-11 forms an arc hugging the Poisson axis" — **INVERTED, not merely uncertified**
pvc-11 is **99.4 % railed**. The arc *is* the rail. The census says pvc-11 is **CLUSTERED**. The
banked claim states the opposite of the measurement.

### (b) "pvc-11 and Mertens/Liouville COLLAPSE together at the Poisson corner (all q≈0, ρ≈0), but W1δ separates them sharply" — **the exhibit is MANUFACTURED**
They did not *collapse together*. **They were both censored onto the same bound.** Two substrates
sitting on a rail are not "alike"; they are **both unmeasured**. And W1δ "separating them" is simply
the *uncensored* axis doing its job.

**The lesson drawn (carry many viewpoints) is RIGHT. The exhibit for it is an ARTIFACT.** This is the
purest arm-(d) instance yet: *a real conclusion, corroborated into the ledger by a broken exhibit* —
and the agreement between the two viewpoints is exactly why nobody looked again.

### (c) "L-zeros is internally bimodal: ζ cells GUE (q=1), Dirichlet/EC cells Poisson-leaning (q≈0)" — **a property of the CONSTRUCTION, not of L-functions**

Katz–Sarnak: Dirichlet and EC L-functions are **GUE in the bulk**. They cannot be Poisson-leaning.
And the **uncensored** axis agrees they are not GUE *as constructed*:

| cell | brody_q | **ks_gue (SAFE)** |
|---|---|---|
| zeta-low-height-bulk | 0.9999 | **0.027** ✓ |
| dirichlet-real-Sp | **0.0001** railed | **0.3042** ✗ |
| ec-root-plus-SO-even | **0.0001** railed | **0.2928** ✗ |

**The repo contains two constructions of EC L-zeros that disagree**, and the disagreement is the
proof:

| construction | ks_gue | reading |
|---|---|---|
| RESULTS.md cross-signal *LMFDB EC L-functions* (n=10,000) | **0.036** | **TR — GUE** ✓ |
| coordinates cell `ec-root-plus-SO-even` | **0.2928** | railed → "Poisson corner" |

**Same substrate; one is broken; theory says which.** The coordinate cells are pooled-by-symmetry-type
objects (`dirichlet-real-Sp`, `ec-root-plus-SO-even`) whose marginal is far from GUE on an axis that
*cannot* be blamed on the rail. **Mechanism (hypothesis, testable, NOT established):** imperfect
per-conductor unfolding leaves residual density variation ⇒ mixture ⇒ super-Poisson ⇒ rails.
(`phase34c` already flagged a *"pooling-null gap"*.) **The bimodality must not be quoted as a fact
about L-functions.**

## 8. CORRECTION to my own claim — "Brody is not on the decimating path" was TOO BROAD

It is **path-dependent per substrate.** `pvc-11` and the arithmetic L-zeros cells **are** on the
`ARS joint_q_profile` / `JPF_CAP=1500` path, and their `extraction_audit` shows savage decimation:
`ec-root-plus-SO-even` **134,848 → 1,517 (stride ≈ 88)**; `dirichlet-real-Sp` 18,993 → 1,584
(stride ≈ 12); `zeta-low-height-bulk` 10,000 → 1,668 (stride ≈ 6). The neural cell substrates are
*not* on it (no `extraction_method`, and their banked `n` runs to 557,142 — i.e. `n` is the **raw,
pre-decimation** count, so the `n ≤ 1500` control was valid).

**But the census survives regardless, on a stronger footing than the control:**

> **STRIDE DECIMATION CANNOT RAIL BRODY — BY MECHANISM.** `sp[::k]` **subsamples spacings**, so the
> **marginal is preserved**. Decimation destroys **correlations**; Brody is a **marginal** fitter.
> Measured on GUE ground truth: q = 0.246 (stride 1) → 0.230 (2) → 0.201 (12) → **0.248 (stride 48)**.
> **GUE stays GUE at stride 48.**

⇒ The census is **decimation-immune by mechanism**, which also covers `pvc-11` and the `qpo-*` /
`lambda-star` cells that bank no `n` and were silently outside the n≤1500 control. And ⇒ the
Dirichlet/EC rail is **not** decimation — it is the construction (§7c).

*This also sharpens the Farey result rather than contradicting it: Farey said decimation is
**correlation-specific** and leaves **the marginal untouched**. Brody being immune is that same fact,
observed on a second estimator. The two audits agree.*

## 9. `s < 10.0` is a DIFFERENT disease — dynamic-range, not null-collapsing

`I8_brody_q:150` discards every spacing > 10× the mean. This does **not** threaten a CLUSTERED verdict
(it is applied to null and data alike, and the rail survives it). What it does is **cap the dynamic
range of every clustering MAGNITUDE measured on a repaired axis**: an unclipped signed integral run on
truncated spacings **cannot see how clustered anything is beyond 10× mean**, so any ladder rebuilt on
it would sit on a **compressed scale**.
**Backfill spec item (not a retraction):** the unclipped recompute must **also lift the `s<10`
truncation, or measure its effect.** Cheap pre-check: *what fraction of spacings does it discard, per
substrate?* If it is 0.1 % on arithmetic and 5 % on hc-3, the truncation is **substrate-dependent** and
any ladder inherits that dependence.

## 10. Palm–Khintchine is the negative-side anchor — bank the pooled arms as CALIBRATION ROWS

The clustered→Poisson transition is exactly the leg the calibrator zoo lacked (§4's demand for a
Cox/Neyman–Scott negative anchor). **The pooled arms supply it for free, and better than synthetic:**
a **structural null the data itself generates**, per substrate, through the *actual* instrument.
**Bank `allen-hpf-pop` / `buzsaki-port-pop` / `population-strat` / `population-fingerprint` as
calibration rows, not merely as controls** — they are the in-repo answer to *"this is what Poisson
looks like through this instrument, on this data."*

---

## 11. THE TOP RAIL — my §7(c) was half-right, and the ζ leg is artifactual too

**Brody's `q` is the level-repulsion exponent β**, `P_q(s) ∝ s^q exp(−b s^(q+1))`
(`axes.py:140` docstring: *"q=0 → Poisson; q=1 → Wigner **GOE**"*):

| class | true q |
|---|---|
| Poisson | 0 |
| **GOE** | **1** ← the upper bound |
| **GUE** | **≈ 2** ← **UNREACHABLE** |
| GSE | ≈ 4 ← unreachable |

**`bounds=(0.0, 1.0)` censors BOTH ends.** Clustering dumps onto the Poisson value; **GUE and GSE
dump onto the GOE value.**

**Therefore the L-zeros "bimodality" is the fitter's two bounds.** Modes at 0.0001 and 0.9999 are
**not a substrate property — they are a histogram of where a bounded optimizer parks.** I retracted
the Dirichlet/EC leg (§7c); **the ζ leg must go too.** `zeta-low-height-bulk` = 0.9999,
`zeta-mid-height` = 0.9999, BR_ρ = 0.9985 — **top rails.**

**And this is the purest arm-(d) trap in the project, because the top rail happens to be RIGHT.**
ζ zeros *really are* GUE (Montgomery–Odlyzko), and `ks_gue` = 0.027 confirms it on a **safe** axis.
So: **a railed estimator returned the correct verdict, was corroborated by a sound axis, and the
corroboration is exactly why the rail was never noticed.** *A right answer from a railed instrument
is still a rail.* **`q = 0.9999` means "≥ GOE" and nothing more** — it cannot separate GOE from GUE
from GSE. Verified: the *correct* inverse-transform GUE reference reads **q = 0.9999**; GOE reads
**0.9886**. Indistinguishable.

### Free zoo-wide diagnostic (no compute): endpoint mass

| axis | at LOWER bound | at UPPER bound | **INTERIOR (carries a measurement)** |
|---|---|---|---|
| `I.8_brody_q` (n=20,801) | **72.5 %** | 2.4 % | **25.2 %** |
| `I.9_berry_robnik_rho` (n=20,631) | 35.6 % | 0.6 % | 63.8 % |

**Only a quarter of the zoo's `brody_q` cells carry a measurement at all.**

> **Standing rule: histogram every bounded axis. Mass at a bound is a railing signature; bimodality
> at the bounds is a railing signature wearing a finding's clothes.**

## 12. SELF-CORRECTION — the broken RMT reference was MINE, not the repo's

The escalation "your RMT calibrators are broken ⇒ the zoo's repulsive pole is mis-anchored" was a
sound inference from my reported numbers (GOE reading CV=0.62, q=0.489 — both under-repulsive), **but
it does not hold against the repo.** Measured:

| reference | CV | brody_q | |
|---|---|---|---|
| `validate_fitters` inverse-transform **GOE** | **0.525** (true 0.523) | **0.9886** | ✅ correct |
| `validate_fitters` inverse-transform **GUE** | **0.424** (true 0.42) | **0.9999** | ⚠️ top rail |
| **my ad-hoc session sweep** (eigvals / global mean) | **0.723** | **0.5819** | ❌ **broken — mine** |
| eigvals + semicircle unfold | 0.543 | 0.9203 | ✅ correct |

`validate_fitters` samples by **inverse transform from the exact GOE/GUE NNS CDF** — no density
gradient, nothing to unfold. **Its PASS is not vacuous** (0.9886 vs expected 1.0). `sessionK/
calibrator_zoo.py` unfolds properly (`st.unfold_poly(gen_gue())`). **The zoo's repulsive pole is
correctly anchored.**

**I generated eigenvalues and normalized by the GLOBAL mean, leaving the Wigner-semicircle gradient
in** — a density mixture ⇒ super-Poisson contamination ⇒ depressed q, inflated CV. **This is exactly
the mechanism I had hypothesized for the Dirichlet/EC cells, running in my own synthetic.**

**And the repo had already found this bug.** `fix_gue_generator.py`, header, verbatim: *"the
'unfolding' step … just divides eigenvalues by the **GLOBAL mean spacing** — but the bulk density …
follows the Wigner semicircle … Without proper local unfolding the resulting frequencies have
non-stationary spacing and don't follow Wigner surmise."* Symptom recorded there: **super-Poisson
Fano F ≈ 2.10.** *Third time the knowledge was already in the repo and the failure was to apply it.*

**What this does NOT touch** (all three independent of any RMT reference):
- **The census stands.** Its null is **Poisson**, which has **no density structure to unfold** — the
  mechanism that corrupted my RMT samples **cannot touch it**. P(rail|Poisson) is measured on the
  honest end of the axis. Neural cells 95.7–100 % railed, undecimated, at P₀ = 0.60.
- **Decimation-immunity stands**, and on mechanism (`sp[::k]` preserves the **marginal**; Brody is a
  **marginal** fitter) — **substrate-independent**, so it holds whether or not my test sample was
  truly GUE.
- **Palm–Khintchine stands**, and is now doing more work than anything else here: it is the one
  calibrator that comes from **a theorem about the data**, not from a synthetic generator I might
  have unfolded wrong.

## 13. SCOPE STATEMENT — Brody-with-those-bounds is not a discovery axis

`bounds=(0.0, 1.0)` is **a model assertion**: *"this substrate lies between Poisson and GOE."*
Everything below (clustering) and everything above (GUE, GSE) is **unrepresentable by construction**.

**ARS exists to find and certify universality classes — including ones outside the known corridor.
An instrument that can only speak inside the segment it assumes cannot do that job.**
**Brody-with-those-bounds is a within-corridor interpolator, not a discovery axis.** This is not a bug
to patch; it is a **scope statement**, and it belongs in the doctrine next to arm (e).

*The existence proof that the corridor is the wrong prior is already banked:* the **Farey
certification** — hard gap at `s_min = 3/π²` plus a Poisson tail — **sits outside every RMT class.**
The project has already certified a class the corridor cannot express.

**Gate repaired symmetrically** (`validate_fitters.py`): added `gue` (q_true ≈ 2, **above** the upper
bound) alongside `clustered`/`clustered_extreme` (**below** the lower). It now correctly **FAILS** —
GOE 0.9875 (PASS) vs GUE 0.9999 (FAIL, expect 2.0): **indistinguishable, exactly as predicted.**

---

## 14. Ladder pole-robustness — pre-committed prediction, RESOLVED, and it SPLITS

`burst_frac = mean(ISI < 10 ms)` (`allen_v1_burst.py:42`) — a **hard-threshold short-ISI fraction**,
**not** CV. So ρ(CV, burst) is not tautological by construction; but the clean contrast is still the
**two-pole** one: same substrate, same burst, **opposite pole**.

| substrate | **ρ(ks_GUE, burst)** | **ρ(ks_POISSON, burst)** | ρ(CV, burst) | ρ(LV, burst) |
|---|---|---|---|---|
| hc3-port-cell (n=923) | **+0.697** | **+0.733** | +0.552 | +0.461 |
| ret1-cell (n=325) | **+0.529** | **+0.522** | +0.518 | +0.418 |
| dr-port-cell (n=1365) | **+0.389** | **+0.484** | +0.233 | +0.445 |
| **allen-hpf-cell (n=4358)** | **−0.277** | **+0.005** | +0.036 | **+0.540** |

**(a) THE ORDERING SURVIVES THE POLE CHANGE.** hc-3 > ret-1 > dr > Allen-HPF under **both** poles.
**The ladder is real. It was not the pole.**

**(b) THE COMPRESSION MECHANISM IS FALSIFIED — by its own pre-committed falsifier.** The prediction
was: *"if it survives and the magnitudes barely move, my compression mechanism is wrong."* Magnitudes
move by **+0.036 / −0.007 / +0.095** on the top three rungs. **They barely move.** ks_gue is *not*
meaningfully compressed as a burst-proxy for these populations. (Raised, tested, retracted — the
proposer's own falsifier.)

**(c) BUT THE BOTTOM RUNG IS POLE-DEPENDENT — and it is exactly the rung under dispute.**
Allen-HPF is the **only** substrate where the two poles disagree: **−0.277 (GUE) vs +0.005
(Poisson).** **"Allen ≈ 0" is not a stable reading.** It is *zero* on one pole and *negative* on the
other. Whatever the bottom of the ladder is, it is **not** "no coupling, robustly measured."

**(d) THE BOTTOM RUNG IS AN OBSERVABLE MISMATCH, NOT AN ABSENCE OF COUPLING — this answers the
standing question.** Allen-HPF: ρ(LV, burst) = **+0.540** (strong) while ρ(CV, burst) = +0.036 and
ρ(ks_gue, burst) = −0.277. **Allen-HPF burstiness is tightly coupled — to LV, not to GUE-distance.**
The coupling did not vanish at the bottom of the ladder; **it moved to a different observable.**
(Exactly [[observable_choice_is_per_axis]]: the optimal observable differs *by axis*.)

> **What was the substrate-relativity ladder a ladder OF?**
> **How much a cell's burstiness registers on the GUE-distance axis** — *not* how Poisson a substrate
> is (every neural substrate is clustered), and *not* whether its cells' burstiness couples to
> anything (at the bottom rung it couples strongly, to LV). It is a ladder of **observable-alignment**,
> and its bottom rung is where the alignment fails, not where the biology stops.

## 15. Two doctrine items from the self-inflicted error

**(A) THE SCRATCH CALIBRATOR HAS NO GATE — a new face of arm (e).**
`validate_fitters` is MANDATORY *for banked values*. My in-session GOE synthetic **never touched it**,
and its numbers (CV 0.723, q 0.582) **drove three messages of reasoning and nearly triggered a
re-anchoring of the zoo's repulsive pole.** **The gate guards the ledger, and the ledger was never at
risk. What is ungated is the reasoning path.**

> **A synthetic reference built in-session to check an instrument is itself an uncalibrated
> instrument. RULE: any synthetic reference used in an argument must pass `validate_fitters` before
> its numbers are quoted.**

One line, and it would have killed this in the first message. Same shape as (e) — *the audit tool
needs the audit* — but a new face: **not the banked estimator, the ad-hoc one built to test it.**

**(B) THE SYSTEMIC PATTERN — knowledge in this project does not propagate from where it is found to
where it is needed.** Four instances, this session alone:

| the knowledge | where it was banked | where it needed to fire |
|---|---|---|
| global-mean normalization leaves the semicircle gradient (Fano F≈2.10) | `fix_gue_generator.py` header | **every eigenvalue path** |
| `"I.8_brody_q": (0.0, 1.0) # 0 Poisson rail, 1 GUE rail` + the KPM-floor lesson, **by name** | `instrument_confound.py:64-78` | **the estimator's primary read** |
| the `$HOME` import bug | survived a truth audit **that reported success** | `phase24/loader.py:49` |
| *"one-sided fitters are blind to super-Poisson"* | the SOC phase | **the joint-plane classifier calling flares "Poisson noise"** |

**That is not four bugs. It is one property.** Arm (d) names the *error*; it does not name the
*systemic* version. **The fix is not vigilance — vigilance is what failed four times.** The fix is
structural:

> **A lesson is not banked until it is attached to the CALL SITE it constrains, not to the phase that
> discovered it.** `fix_gue_generator.py` knew. Nothing in the eigenvalue path had to read it.

**(C) REPORT THE INTERIOR FRACTION, ALWAYS.** For any bounded axis, publish the fraction of values
strictly inside the bounds alongside the values themselves. Brody: **25.2 %**. Berry-Robnik:
**63.8 %**. *Three-quarters of Brody's banked values are the optimizer's parking lot.* And BR's much
larger interior is itself informative — **ρ has a genuine interior null, so it degrades more
gracefully.** This is a free, permanent diagnostic, and it would have made all of this visible **at a
glance, years earlier.**

---

## 16. THE LADDER DIES ON A CHANGE OF DOMAIN — the bottom rung is the CV-16 drift artifact

**My §14 "observable-alignment ladder" reframing is FALSIFIED.** (Flagged provisional; it was worse.)

**The tautology check first (it clears):** `I13_lv` (`axes.py:228`) is a **consecutive-pair** statistic
(`mean 3((Iᵢ−Iᵢ₊₁)/(Iᵢ+Iᵢ₊₁))²`); `burst_frac` is `mean(ISI < 10 ms)` — a **marginal** statistic, no
adjacency. **Not definitional.** But the classification it forces is the whole finding:

| axis | domain |
|---|---|
| `burst_frac`, `CV`, `ks_gue`, `ks_poisson` | **MARGINAL** |
| `LV`, `CV2` | **CONSECUTIVE-PAIR** |

### The 2×2 — ρ(axis, burst)

| substrate | CV | ks_gue | ks_pois | **↑MARGINAL** | CV2 | LV | **↑PAIR** |
|---|---|---|---|---|---|---|---|
| hc3-port-cell | +0.552 | **+0.697** | +0.733 | | +0.434 | +0.461 | |
| ret1-cell | +0.518 | **+0.529** | +0.522 | | +0.336 | +0.418 | |
| dr-port-cell | +0.233 | **+0.389** | +0.484 | | +0.426 | +0.445 | |
| **allen-hpf-cell** | **+0.036** | **−0.277** | **+0.005** | | **+0.524** | **+0.540** | |

**Allen-HPF is the ONLY substrate whose MARGINAL axes are dead while its PAIR axes are alive — and on
the pair axes it is at the TOP, not the bottom. The ladder does not reorder. It INVERTS.**
On rate-robust axes there is **no ladder at all**: CV2 = 0.52 / 0.43 / 0.43 / 0.34 — a flat band.

### The mechanism, confirmed directly — and the repo named it by number

`I12_cv2` docstring, verbatim: *"robust to SLOW rate drift (adjacent ISIs see ~the same rate) — so it
isolates FAST burst-clustering from the **slow rate-nonstationarity / epoch-gap concatenation that
inflates global CV**." — Added Phase 37 (**the CV-16 artifact fix**).*

Poisson has CV = 1 **and** LV = 1. Slow drift inflates the **global CV** but **not** the rate-robust LV:

| substrate | **med CV** | med LV | **CV/LV** |
|---|---|---|---|
| **allen-hpf-cell** | **16.21** | 1.20 | **13.49** |
| dr-port-cell | 2.38 | 1.26 | 1.88 |
| hc3-port-cell | 1.92 | 1.38 | 1.39 |
| ret1-cell | 1.35 | 1.19 | 1.13 |

**Allen-HPF's global CV is 16.2. That IS "CV-16."** Phase 37 identified it, named it, and built CV2/LV
to fix it — **and the ladder was never rebuilt on the fixed axes.** Hippocampal formation has exactly
the expected generator: sleep/wake and theta/SWR state mixtures ⇒ the **marginal** spacing
distribution is a mixture across rate epochs ⇒ every marginal axis is contaminated, while the true
burst coupling (visible to the pair axes) is **entirely normal, indeed the strongest in the zoo.**

### WHY THE POLE TEST MISSED IT — arm (e), one level up

**`ks_gue` and `ks_poisson` are BOTH marginal statistics.** Changing the **pole** while staying in the
**same domain** cannot detect a **domain-level** contaminant. The ladder survived a change of pole and
**died on a change of domain**.

> **This is arm (e)'s lesson at the level of an ANALYSIS rather than an ESTIMATOR: probing within the
> instrument's own vocabulary cannot detect that the vocabulary is the bug.** The two-pole test was
> *the right instinct executed inside the broken frame* — and it returned a reassuring PASS.

### Scope — do NOT overclaim

- **The BOTTOM RUNG is a drift artifact: ESTABLISHED** (CV=16.2; marginal axes dead, pair axes
  top-of-class; mechanism named in the repo).
- **"The WHOLE ladder is a drift gradient": NOT ESTABLISHED.** Spearman(ladder ρ, CV/LV) = **−0.80,
  p ≈ 0.20, n = 4 substrates** — suggestive, **underpowered**. Bank as a hypothesis with a named
  closer: rebuild the ladder on CV2/LV across **all** substrates with burst, and test whether any
  gradient survives.
- **What IS established:** the substrate-relativity ladder as banked (ρ(ks_gue, burst)) **does not
  survive the domain change**, and its bottom rung is an instrument artifact the project had already
  diagnosed.

**FIFTH instance of [[knowledge_does_not_propagate]] — and the most expensive one yet, because it is
load-bearing for the cross-substrate programme.** Phase 37 banked *"CV-16 was a drift artifact;
rate-robust CV2/Lv reveal the real gradient"* — and the ladder, the programme's headline
cross-substrate claim, was left standing on the contaminated axis.

---

## 17. BL — not a re-read, a PARTITION. Prediction pre-committed, and CONFIRMED.

`BL` (`rep_int_q < 0.10`, docstring'd **"Poisson noise"**) has been fusing two populations that have
**nothing to do with each other**:

- **exact 0.000** → a **CLUSTERING DETECTION** (0/200 false positives on the n-matched Poisson null)
- **interior (0 < rep < 0.10)** → a **real, weak-repulsion measurement**

**Will's pre-committed prediction:** *"most of BL is exact-0.000, and the interior fraction is small —
because the substrates that land there are the biological ones, and every biological substrate in the
zoo is clustered. If BL turns out to be mostly interior, my whole detector reading of BL's population
is wrong and I want to know that immediately."*

| substrate | in BL | **exact 0.000** | interior | % of BL exact-0 |
|---|---|---|---|---|
| **pvc-11** (biological) | 1144 | **918** | 226 | **80.2 %** |
| **allen-np** (biological) | 477 | **385** | 92 | **80.7 %** |
| kuramoto (synthetic) | 39 | 20 | 19 | 51.3 % |
| **maass-gamma0** (arithmetic) | 6 | **0** | **6** | **0.0 %** |
| **pulsar-nanograv** | 5 | **0** | **5** | **0.0 %** |
| **ALL BL** | **1671** | **1323** | **348** | **79.2 %** |

**CONFIRMED: BL is 79.2 % exact-0.000, 20.8 % interior.**

**And the split is cleaner than predicted — it is essentially BIOLOGICAL vs NOT.** Both biological
substrates are ~80 % clustering-detections. Both arithmetic/astro substrates are **100 % interior** —
genuine, correctly-measured weak repulsion. **The class name was doing all the work of hiding that.**

### Independent corroboration on pvc-11 (and it is NOT the arm-(d) trap)

`pvc-11` reads **CLUSTERED** on **two independent censored axes**:
- `I_rep` exact-zero: **80.2 %** of its BL cells
- Brody rail: **99.4 %** of its cells

These are **different censoring mechanisms** (a pointwise integrand clip vs an optimizer bound) on
**different statistics**, and **each was separately validated against ground truth** before being
trusted. That is not two agreeing measurements corroborating an artifact — it is **two instruments,
each independently calibrated, agreeing.** The arm-(d) trap is corroboration *substituting* for
calibration; here the calibration came first.

### The doctrine line

> **`BL` must be retired as a class.** Report the partition: **`BL-detected` (exact-0.000 ⇒ clustered)**
> and **`BL-interior` (a weak-repulsion measurement)**. A verdict class whose members are 79 % "the
> instrument ran out of range" and 21 % "a real reading" is not a class — it is a **bin**, and its name
> ("Poisson noise") is **wrong for four out of five of its members.**

---

## 18. ERROR BARS ON THE FLAT BAND — "is it flat, or four numbers that happen to be close?"

**ANSWER: NEITHER. It is a REAL but NARROW band.** Bootstrap 95 % CIs (2000 resamples) + Fisher-z
heterogeneity:

| axis | span | Q (df=3) | p | I² |
|---|---|---|---|---|
| `ks_gue` (**marginal**, the old ladder) | **0.974** (−0.277 → +0.697) | **1364.1** | ~0 | 100 % |
| `LV` (**pair**) | **0.122** (+0.418 → +0.540) | **25.4** | 1.3e-05 | 88 % |
| `CV2` (**pair**) | 0.188 (+0.336 → +0.524) | 34.0 | 2.0e-07 | 91 % |

**It is NOT flat** (homogeneity rejected, p ≈ 1e-5) — with n=4358 even tiny true differences are
detectable, which is why I² stays high. **But the DYNAMIC RANGE collapses ~8×.**

> **The old ladder's span was ~87 % contaminant.** What remains is a **real, small gradient running
> the OTHER WAY**: **allen > hc3 > dr > ret1**, consistent across **both** rate-robust axes.

**So it is not a candidate invariant.** It is **a different, much smaller ladder, in the opposite
direction.** (Retract the "flat band / candidate invariant" reading before it is quoted.)

### The predictor-side confound — raised, MEASURED, defused

`burst_frac = mean(ISI < 10 ms)` is an **absolute threshold**, so a high-rate cell scores high
regardless of burstiness — and Allen-HPF is exactly the substrate with CV/LV = 13.5. **The residual
ordering could be the same artifact entering through the PREDICTOR instead of the axis.** Measured:

| substrate | **ρ(burst, RATE)** | ρ(LV, burst) | **partial ρ(LV, burst \| rate)** |
|---|---|---|---|
| allen-hpf-cell | **+0.028** | +0.540 | **+0.770** |
| dr-port-cell | +0.197 | +0.445 | **+0.688** |
| hc3-port-cell | **+0.053** | +0.461 | **+0.646** |
| ret1-cell | +0.156 | +0.418 | **+0.606** |

**`burst_frac` is NOT rate-contaminated** (ρ ≤ 0.20 everywhere; 0.028 at Allen, the worst-drift
substrate). And **controlling for rate makes the coupling STRONGER** (0.61–0.77) with the **ordering
intact**. **The residual gradient survives rate-control.** Confound raised, measured, defused — *not
assumed away.*

### What is now standing where the ladder was

**A real, rate-robust, burst ↔ pair-structure coupling in all four neural substrates (ρ ≈ 0.61–0.77
partialled on rate), with a small residual gradient running opposite to the retracted ladder.**

The clean separation this implies — **worth stating, worth testing, NOT yet established**:
- **burst → PAIR-structure coupling**: strong, narrow-band across hippocampus, retina, V1, HPF ⇒
  **candidate biology**.
- **burst → MARGINAL coupling**: entirely a function of how nonstationary the recording is ⇒
  **rig-and-behaviour, not tissue**.

**Named closer for the open hypothesis** (*"the whole ladder is a drift gradient"*, Spearman −0.80,
**p ≈ 0.20, n = 4 — underpowered**): rebuild the ladder on CV2/LV across **all** substrates carrying
`burst`, and regress the ordering on CV/LV. **If the ordering is predicted by CV/LV, the ladder was a
RECORDING-QUALITY RANKING** — and it will reproduce in any lab's data as a function of **session
length and behavioural state, not tissue.** That is a falsifiable prediction about **other people's
data**, which is the only kind that makes the discipline forkable.

---

## 19. Standardized effect size, and the predictor-comparability residual that cost me the headline

### (a) Demotion or inversion? — **BOTH**, and the premise for "scale artifact" doesn't apply

The proposed standardizer (within-substrate SD of the axis) is **the wrong one for a correlation.**
We are comparing spans of **Spearman ρ**, which is **already unit-free AND monotone-invariant** — LV's
narrow natural range **cannot** compress ρ(LV, burst), because Spearman sees only ranks. The right
standardizer is the **sampling SE of ρ** (Fisher-z):

| axis | ρ span | Fisher-z span | **gradient in SE units** | ordering |
|---|---|---|---|---|
| `ks_gue` (marginal) | 0.975 | 1.147 | **35.0 SE** | hc3 > ret1 > dr > allen |
| `LV` (pair) | 0.123 | 0.160 | **4.9 SE** | **allen > hc3 > dr > ret1** |
| `CV2` (pair) | 0.189 | 0.233 | **7.1 SE** | **allen > hc3 > dr > ret1** |

**The ~7× collapse SURVIVES standardization.** So it is **both, not either/or**: a real **demotion in
magnitude** (35 SE → 5 SE) *and* a **rank inversion**. The pair gradient is **real** (4.9 SE is not
noise) — it is simply **small**, and it points the other way. *The demotion applies to the OLD ladder;
the new one is small but genuine.*

### (b) THE PREDICTOR IS NOT THE SAME STATISTIC ACROSS SUBSTRATES — and it costs me the headline

`burst_frac = mean(ISI < 10 ms)` is an **absolute** threshold. Under Poisson, `P(ISI<10ms) =
1 − exp(−rate·0.01)`:

| substrate | med rate | mean ISI | **P(ISI<10ms) \| Poisson** | observed `burst_frac` | enrichment |
|---|---|---|---|---|---|
| ret1-cell | 6.36 Hz | 157 ms | **6.2 %** | 0.133 | 2.1× |
| **hc3-port-cell** | **0.49 Hz** | **2021 ms** | **0.5 %** | 0.092 | **18.4×** |
| dr-port-cell | 0.74 Hz | 1353 ms | 0.7 % | 0.068 | 9.7× |
| allen-hpf-cell | 3.30 Hz | 303 ms | 3.3 % | 0.119 | 3.6× |

**The 10 ms threshold is the 0.5th percentile in hc-3 and the 6.2nd in retina — a 12× difference.**
**`burst_frac` is NOT the same statistic in each substrate**, so the cross-substrate ordering compares
correlations of **different predictors**. *(Note: this is NOT the rate confound — that was measured and
defused, ρ(burst, rate) ≤ 0.20. This is a distinct, quantile-position confound that survives rate-control,
because controlling for rate within a substrate does not make the threshold mean the same thing across
substrates.)*

### (c) The partition this forces — and it is the one that matters

- **SAFE — Allen's marginal/pair dissociation is WITHIN-substrate.** Same cells, same `burst_frac`, two
  axes: **marginal dead** (ks_gue −0.277, ks_pois +0.005, CV +0.036), **pair alive** (LV +0.540; partial
  on rate **+0.770**). **A per-substrate quantile artifact cannot produce this** — one substrate, one
  predictor, two domains. **This is the load-bearing claim and it stands.**
- **NOT CERTIFIED — the cross-substrate ORDERING** (allen > hc3 > dr > ret1). It requires `burst_frac`
  to be comparable across substrates, and it is not. **I was about to bank the reversal's ordering as
  the headline. It is not certified.**

**UNRESOLVED, with the named closer (§9 c-companion):**
**Gap** — `burst_frac`'s fixed 10 ms threshold is a substrate-dependent quantile (0.5 % → 6.2 %), so
cross-substrate ρ comparisons are not like-for-like. **Closer** — recompute `burst_frac` at a
**per-substrate quantile threshold** (e.g. ISI < 10th percentile of that substrate's own ISI
distribution) and re-run the ordering. **Instrument pinned in advance:** same LV/CV2 axes, same partial-
on-rate, same bootstrap CIs — *only* the predictor's threshold changes. Requires the **raw-ISI
recompute** (banked coordinates carry summary statistics only). **If the ordering survives a quantile-
matched predictor, the pair ladder is real; if it reorders, the ordering was a quantile artifact and
only the within-substrate dissociation survives.**

*Same falsifier structure as the pole change — and it earned its keep again: it caught a headline
before it was banked, not after.*

---

## 20. BL — THE FULL POPULATION SWEEP. Arc closed.

The earlier read (§17) covered only the 5 substrates carrying `ARS.rep_med` in the coordinates. **The
cross-signal rows — including flares and fungal, the two exhibits that started this thread — were
unswept.** Now swept, from `data/phase15_*_joint.parquet`.

### (a) The detector, validated on THE REPO'S OWN CALIBRATOR ZOO — not my synthetic

`data/phase15_calibrator_joint.parquet`, underpowered rows dropped:

| calibrator class | n | **exact-0.000** | **% in BL** | median `rep_int_q` |
|---|---|---|---|---|
| **poisson (THE NULL)** | 1000 | **0** | **100.0 %** | 0.0238 |
| beta=1_GOE | 1000 | 0 | 0.0 % | 0.312 |
| beta=2_GUE | 1000 | 0 | 0.0 % | 0.368 |
| beta=4_GSE | 1000 | 0 | 0.0 % | 0.431 |
| periodic_q7 / q12 | 2000 | 0 | 0.0 % | 0.850 |
| mixed_q7_q12 | 1000 | 0 | 0.0 % | 0.182 |
| uniform_jitter_0.10 | 1000 | 0 | 0.0 % | 0.671 |
| zeta_first_2000 | 200 | 0 | 0.0 % | 0.425 |

> **POISSON LANDS IN BL 100 % OF THE TIME — AND NEVER AT THE FLOOR. 0/1000.**

**That is the partition, stated by the repo's own ground truth**: BL contains **Poisson (interior)** and
**clustered (exact-0)**, and **they never overlap**. My synthetic said 0/200 false positives; an
artifact **I did not generate** says **0/1000**. Detector specificity is now confirmed on banked
ground truth.

*(And note what the calibrator zoo contains: GOE, GUE, GSE, periodic, mixed, jitter, ζ — and **no
clustered class at all.** Poisson is the most-clustered object in it. The missing negative anchor,
confirmed from the other side.)*

### (b) The full BL population — PERFECT SEPARATION, no mixed cases

`data/phase15_cross_signal_joint.parquet`, `quadrant == 'BL'`:

| signal_class | BL rows | **exact 0.000** | interior | verdict |
|---|---|---|---|---|
| **fungal_pool** | 194 | **194** | 0 | **100 % — CLUSTERING DETECTED** |
| **solar_flares_MX** | 191 | **191** | 0 | **100 % — CLUSTERING DETECTED** |
| **binance_BTCUSDT_d1** | 185 | **0** | **185** | **0 % — genuine weak-repulsion reading** |
| **ALL BL** | **570** | **385** | **185** | **67.5 %** |

**The two exhibits that started this thread are exact-zero on EVERY ONE of their q-bands** (194/194,
191/191). **Binance is 100 % interior** — and is exactly what it always looked like. **No mixed
cases anywhere.**

Solar flares are **independently known-clustered from our own SOC phase.** The detector's headline
targets are now counted, and they came in **unanimous.**

### (c) Prediction ledger

Will's pre-committed prediction — *"most of BL is exact-0.000, and the interior fraction is small,
because the substrates that land there are the biological ones... If BL turns out to be mostly
interior, my whole detector reading of BL's population is wrong and I want to know that immediately."*

**CONFIRMED on both populations:** per-cell 79.2 % exact-0 (§17); cross-signal **67.5 %** exact-0, with
a **perfect** biological/physical vs financial split. **BL is retired as a class.** It is a **bin**
holding two populations that never overlap, under a name (*"Poisson noise"*) that is **wrong for
two-thirds of its members** — including **both** of the ones the project cared about.

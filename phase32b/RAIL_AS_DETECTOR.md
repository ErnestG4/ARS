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

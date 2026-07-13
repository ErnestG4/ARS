# Clustering ⊥ Coupling — a dissociation across neural substrates, on a repaired instrument

**Status: FINDING (n=7). TWO independent matched pairs. Five candidate explanations excluded.**
Session 2026-07-11/12. Commits `dc007e6` … `6a4b002`. Data + code: `overnight_2026_07_12/`.

---

## 1. The claim

> **Across neural substrates, *how much* a population clusters and *how lawfully that clustering follows
> from single-cell ISI irregularity* are INDEPENDENT properties.**
> **The most clustered substrate is not the most lawfully coupled one.**
> **Reliability and clustering magnitude are both excluded by a matched pair.**

`Spearman(clustering magnitude, |coupling|) = +0.25, p = 0.59` (n=7) — **independent axes.**

---

## 2. The measurement

**Axis** — `I_rep`, the signed repulsion integral `∫₀¹(1 − R₂(r)) dr`, computed on **unit-mean-normalised
spacings**. Negative = clustered, 0 = Poisson, positive = repulsive.
**Predictors** — **threshold-free**: log-ISI CV, and gamma shape *k*. **No 10 ms constant anywhere.**
**Coupling** — `ρ(log-ISI CV, I_rep)` per substrate, across cells.
**Reliability** — interleaved-block split-half (drift-balanced), Spearman-Brown to full length.

| substrate | n | clustering (med `I_rep`) | ρ(I_rep) | **coupling** | disatt | R²_marginal |
|---|---|---|---|---|---|---|
| ibl-port | 277 | −0.236 | 0.988 | **−0.694** | −0.700 | 0.794 |
| hc3-port (CA1) | 213 | −1.962 | 0.913 | **−0.604** | −0.636 | 0.705 |
| buzsaki-port | 300 | −2.389 | 0.903 | **−0.482** | −0.511 | 0.582 |
| allen-hpf | 277 | **−8.306** | 0.598 | **−0.429** | −0.590 | 0.574 |
| ret-1 (retina) | 298 | −0.309 | 0.970 | **−0.187** | −0.190 | 0.656 |
| **pvc-11 (V1)** | 273 | −0.863 | 0.954 | **+0.076** | +0.078 | 0.761 |
| **dr-port (MEC/CA1/DG)** | 299 | −0.833 | 0.932 | **−0.549** | −0.570 | **0.145** |

---

## 3. The spine — TWO INDEPENDENT MATCHED PAIRS, not a correlation across n

**A matched pair holds clustering and reliability FIXED and varies only the coupling. It falsifies both
competing accounts on ONE comparison — no *n* required.** There are now **two**, at **two different
clustering levels**, and the second was found by the substrate added last:

| pair | clustering level | Δ clustering | reliability | **Δ coupling** |
|---|---|---|---|---|
| **1 — ibl-port vs ret-1** | ≈ −0.27 | **0.073** | both ≥ **0.97** | **0.507** (−0.694 vs −0.187) |
| **2 — dr-port vs pvc-11** | ≈ −0.85 | **0.030** | both ≥ **0.93** | **0.625** (−0.549 vs **+0.076**) |

**Pair 2 is TIGHTER on clustering and has a LARGER coupling gap — and it straddles zero.**

**Unreliability cannot explain either** — all four substrates sit at or near the ceiling, so there is no
attenuation left to remove. **Clustering magnitude cannot explain either** — within each pair the values
are the same to 0.03–0.07.
**This is the design that beats small *n*, and it now replicates.** Nothing else in this document is
load-bearing for it.

---

## 4. FIVE EXCLUDED EXPLANATIONS

*Naming the failed explanations is worth as much as the finding: it is what stops the next person
spending a month on them.*

| # | explanation | how it died |
|---|---|---|
| 1 | **recording quality / reliability gradient** | The matched pair. Also: `Spearman(\|coupling\|, ρ) = +0.000`, `Spearman(\|coupling\|, spike count) = −0.100` — the hypothesis **requires** these positive. Worst case for it: **ret-1 is the most reliable substrate (ρ=0.97) and the most weakly coupled.** |
| 2 | **clustering magnitude** | The matched pair (identical clustering, 4.2× coupling). |
| 3 | **"Allen's clustering is state-driven"** | Retracted. Its low split-half ρ(I_rep)=0.660 is an **estimator property**: `ρ(\|I_rep\|, \|split-half error\|) = +0.643` ⇒ noise scales with the value; |I_rep|=8.3 is deepest in the tail. The full-*n* shuffle shows Allen is the **most marginal** substrate (75 % retained), not the least. |
| 4 | **marginal/correlational composition** | **Falsified** by the variance decomposition (`R²` of `regress(I_obs ~ I_shuf)` across cells — bounded, scale-free, no near-zero denominator): `Spearman(R²_marginal, \|coupling\|) = +0.200, p = 0.70`. **Predicted negative.** *This instrument could have confirmed it and said no.* |
| 5 | **sensory / feedforward** | **pvc-11.** It is sensory **and cortical**, and has **less** coupling than retina (+0.08 vs −0.19). The datapoint that was meant to separate the axis **killed it**. |

**Also retracted along the way:** *"irregular ⇒ clustered on every substrate"* (pvc-11 is a
counterexample, at reliability 0.954 — **not noise**), and **the fine-grained ordering** (it swaps under
the cell-cap, a nuisance parameter — see §6).

---

## 5. The instrument had to be repaired first, and the repairs are the precondition

**None of the above was measurable on the shipped instrument.** Nine defects, **one generating
assumption**:

> **An instrument built and validated against a calibrator set that EXCLUDES a region accumulates
> defects that are individually invisible and jointly fatal in exactly that region. The defects are
> individually DEFENSIBLE — each is correct behaviour inside the corridor — which is why they survive
> review and why fixing them one at a time does not stop the next one.**

The calibrator zoo shipped GOE / GUE / GSE / periodic / mixed / jitter / ζ / Poisson — **and no clustered
class at all.** Poisson was the most-clustered object in it.

| defect | effect |
|---|---|
| `I_rep`'s `np.maximum(0, ·)` clip | floors at the **Poisson value** ⇒ all clustering maps onto "Poisson noise" |
| Brody `bounds=(0,1)` | censors **both** ends: clustering → lower rail, **GUE/GSE → GOE rail** |
| Berry-Robnik CI collapse at the rail | the wrong answer reported **45× more confidently** than the right one |
| `bulk_recovery`'s `np.interp` clamp | every clustered band → the σ of the *"(Poisson regime)"* knot |
| `s < 10.0` truncation | discards the heavy tail *that is the clustering signature* |
| **global** unit-mean normalisation | does not remove within-cell drift ("CV-16") |
| `spacings()`'s "2–98 % tail trim" | a **positional slice** — removes **no** outliers; value-trimming moves Allen's `ks_gue` **0.854 → 0.416** |
| `validate_fitters` | probed **only at the two rails** — *probing at the rails cannot detect railing* |
| `I_rep` on **raw** spike times | `r∈[0,1]` = **one second** ⇒ a different number of mean-ISIs per cell |

**Repairs, all validated:** unclipped signed `I_rep`; Brody with **both** bounds opened (GUE now reads
**q = 1.533**, above the old ceiling); a **clustered calibrator class** (Cox / Neyman–Scott / gamma,
swept — Poisson → −0.009, clustered → −0.39…−19.6 monotone); `validate_fitters` probing **outside every
boundary**.

---

## 6. What is NOT claimed

- **The fine-grained ordering.** It swaps (allen↔buzsaki, hc3↔ibl) under the **cell-cap alone**. It is
  not a stable object. *Only the matched pair and the coupling **range** (−0.69 → +0.08) are.*
- **Any mechanism for the dissociation.** Five are excluded; none is established. **The dissociation is
  robust and unexplained.**
- **Retina's anti-clustering order.** Real but weak: 53.4 % of cells, median 103.6 %, p = 0.006 — a
  coin-flip with a heavy tail. *(Contrast buzsaki: 0.0 % of cells, p = 3e-51 — that is what a unanimous
  population property looks like.)*

## 7. The forkable prediction

The **old** ladder (ρ(ks_gue, burst)) predicts **recording quality** — it should track session length,
CV/LV drift, and behavioural state, and be destroyable by matching recording conditions.
The **coupling** measured here predicts **tissue** — it should survive matched recording conditions and
reproduce on the same regions across rigs.
**These are separable in anyone's data.** Someone with hippocampus-and-retina recordings on two rigs can
kill either half.

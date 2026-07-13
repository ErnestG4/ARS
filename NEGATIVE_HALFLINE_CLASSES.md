# The negative half-line — walking through the corridor

**Status: ONE FINDING (the neural long-range partition), ONE OPEN QUESTION (do clustered generative
families form classes?).** 2026-07-13. `overnight_2026_07_12/classes*.log`.

## The question

The census said **"every neural substrate is clustered."** That verdict was produced by `I_rep` —
which, until this session, was **clipped at the Poisson value and could emit only one bit.** We
unclipped it; it now emits a real number. **Nobody had asked whether that number has structure.**

Standing doctrine: **a CLASS claim needs LONG-RANGE statistics (Σ², Δ₃), not the marginal.** So the
discriminant is **Σ²(L)**, not `I_rep`.

---

## ✓ FINDING — the neural substrates SPLIT on the class certifier

Per-cell **Σ²(L=5)**, computed on the first 5000 ISIs. **Poisson reference: 5.00 [4.63, 5.33]** (25 reps).

| substrate | n | median Σ² | IQR | **% cells near-Poisson (Σ² < 8)** |
|---|---|---|---|---|
| **ibl-port** | 52 | **6.42** | [4.93, 8.11] | **73 %** |
| **ret-1** | 57 | **6.45** | [4.73, 13.51] | **60 %** |
| pvc-11 | — | 19.59 | — | — |
| buzsaki | — | 37.15 | — | — |
| hc3-port | 35 | **43.12** | [20.14, 73.84] | **6 %** |
| **allen-hpf** | 51 | **183.54** | [153.19, 250.93] | **0 %** |

> **A MAJORITY of `ibl` and `ret-1` cells are INDIVIDUALLY INDISTINGUISHABLE FROM POISSON AT LONG
> RANGE. Essentially NO `hc-3` or `allen` cell is.**
>
> **The census's "every neural substrate is clustered" was a SHORT-RANGE verdict. On the class
> certifier the substrates split in two — and half of them are long-range Poisson.**

**This is the same disease one level up: a one-bit readout naming a bin and hiding a partition.**
`BL` did it three days ago; `clustered` was doing it here.

### It also hands the matched pair a THIRD control

`ibl` and `ret-1` are now matched on **clustering** (−0.24 / −0.31), **reliability** (0.99 / 0.97),
**AND long-range class** (Σ² 6.42 / 6.45, both majority-Poisson) — **and their coupling still differs
4.2×** (−0.694 vs −0.187). The dissociation survives a control it was never designed to pass.

---

## ✗ OPEN — do clustered generative families form distinct classes?

At **matched `I_rep` = −2.0**, the families are **not identical on the other axes**:

| family | I_rep | CV | **LV** | Σ²(5) |
|---|---|---|---|---|
| cox | −2.007 | 2.47 | **1.02** | 45.40 |
| neyman_scott | −1.874 | 2.95 | **1.56** | 29.11 |
| lognormal | −2.109 | **7.30** | 1.64 | 44.05 |
| gamma_renewal | −1.934 | 3.07 | **2.47** | 36.55 |

**LV spans 1.02 → 2.47 and CV spans 2.47 → 7.30 at identical `I_rep`.** A Cox process and a gamma
renewal at the same clustering magnitude are **not the same object**, and `I_rep` cannot tell them
apart. **"Clustered" is a one-bit readout of a structured space.**

**BUT THE CLASS CLAIM IS NOT ESTABLISHED, and the failure is mine:**
- With 25 reps: `neyman_scott` **32.42 [30.33, 35.29]** vs `gamma_renewal` **35.81 [33.80, 37.99]` —
  **the 95 % ranges OVERLAP.** Not separated.
- `cox` read **91.73** — but **I hardcoded its strength from the previous run's tuning instead of
  re-tuning under the new seed, so its `I_rep` was never verified to be −2.** **The cox comparison is
  void.** *(A matched-condition experiment in which the matching was not checked. Exactly the error
  this session has been cataloguing, committed in the run designed to find it.)*

**CLOSER (pre-registered):** re-tune every family under the run's own seed, **assert `|I_rep − (−2)| <
0.12` per replicate before it enters the table**, and report Σ² and LV with CIs. If families separate
on Σ² with non-overlapping intervals at matched `I_rep`, **the negative half-line has classes.**

---

## The larger programme this opens

**The corridor (Poisson → GSE) was the calibrator zoo's assumption, and it was wrong about biology in
a specific direction.** The instruments are now repaired to see past it, and **Farey** is the existence
proof that a real, certified class lives outside every RMT class (hard gap at `s_min = 3/π²` + Poisson
tail — and it was found by *pointing ARS at a real arithmetic object*, not by synthesising one).

**The search that implies, and which nobody has run:**
1. **Arithmetic substrates with structural gaps.** Farey's hard gap comes from a *coprimality
   constraint*. What else has a **mechanical short-range exclusion**? Gaps between **squarefree**
   numbers; gaps between **smooth** numbers; the **Stern–Brocot depth** sequence. Each has a known
   combinatorial constraint ⇒ **a predictable hard gap, derivable before it is measured.**
2. **The negative half-line, now that it has units** — the open question above.

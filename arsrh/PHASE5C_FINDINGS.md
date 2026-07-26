# Phase 5c — four follow-ups. One gate fires, one status line becomes permanent.

`phase5c_followups.py`, `phase5c_followups_measured.json`. §0 held. **No per-sub-block brackets were
built** — those are the halted Phase 5 measurement and stay withheld for its re-seal.

## 1. The averaging argument is a theorem, and it holds in the safe direction

Upgraded from "empirical fact from one designed mixture" to what it actually is. Over window positions
in a heterogeneous block, the law of total variance gives

> Var(N) = E_g[Var(N|g)] + Var_g(E[N|g])

With θ equalizing density, E[N|g] = L for every group, the second term vanishes, and the whole is the
**window-count-weighted** mean of the parts. Any residual density mismatch makes that term **positive,
never negative**. So:

> whole ≥ weighted mean of parts ≥ min part

**The entailment is a priori and conservative.** whole < bracket ⟹ min part < bracket, *a fortiori*.
Phase 5b's demonstration was a check on the arithmetic, not the ground of the claim; the ground is the
decomposition. Filed accordingly.

## 2. The +0.0117 excess pinned — it was my arithmetic, not a between-group term

Exact decomposition (L=1, designed mixture [lattice η=0.1 | GUE | GUE | Poisson]):

| term | value |
|---|---|
| whole-block Var(N) | 0.457959 |
| E_g[Var(N\|g)] (within, **window-count-weighted**) | 0.457652 |
| Var_g(E[N\|g]) (between) | 0.000934 |
| residual after both | −0.000626 |

The decomposition closes to **0.14%**. Both candidate explanations named in Phase 5b were indeed orders
off — and so was the premise that there was anything to explain. **The +0.0117 was an unweighted mean of
four part-values compared against a quantity that requires window-count weighting.** The parts have
unequal lengths in unfolded units (part means 1.00050 / 1.00000 / 1.00000 / **0.93081** — the Poisson
part's realized density is 7% low, a legitimate 1.5σ fluctuation of a 500-point Exp(1) sum), so the
weights differ by ~7% across values spanning 0.107 → 0.914. That is the whole discrepancy.

The genuine between-group term is **9.3×10⁻⁴**, arising from those realized density fluctuations of the
*synthetic*, not from any θ failure. 12 of 8143 windows (0.15%) straddle group boundaries and belong to
no part, which is the sign of the small negative residual.

**This is a fourth slot error of mine this session** (with the seal tautology, the Var[S] sampling
branch, and the G2 gate arm). Same family: I compared a number against a differently-defined number.

## 3. The underclaim, corrected — the positive half of the sentence

Phase 5b wrote only the negative half: "not two independent witnesses (one block read twice)". True and
incomplete. The positive half:

**⟨r̃⟩ and Σ² sit in different correlation families** — r̃ reaches higher-order correlations, Σ² is
determined by the two-point function alone. Their agreement therefore **retires statistic-artifact as an
explanation** for the rigidity excess: no single estimator pathology produces both. That is the same slot
shape as CP1 — *two mechanistically independent analyses of one dataset* — and it is not nothing. What it
does not do is reach anything **upstream of the data**: block choice, catalogue provenance, and the
attribution question are all untouched, because there is one block underneath both.

## 4. Flatness vs P1's crossover — UNDERPOWERED, and permanently so

The sharpest unrun item. Measured on ⟨r̃⟩ (the statistic P1 is stated in), shape only, no brackets:

| sub-block | γ_mid | 1/ln(γ/2π) | ⟨r̃⟩ |
|---|---|---|---|
| 1 | 472.8 | 0.2314 | 0.61616 |
| 2 | 1125.3 | 0.1928 | 0.61739 |
| 3 | 1706.3 | 0.1784 | 0.61667 |
| 4 | 2251.8 | 0.1700 | 0.61691 |

P1's local slope d(dev)/d(1/lnγ), taken from its two lowest-γ W=2000 rows, is **+0.0892**. The sub-blocks
span 1/ln = 0.1700–0.2314, entirely **above** P1's mapped range (which tops out at 0.1845) — so this is
extrapolation below the measured heights, as anticipated.

- P1 extrapolated **predicts** a ⟨r̃⟩ span of **+0.00548** across these sub-blocks.
- **Observed** span **0.00123**; fitted slope **−0.0114** (opposite sign, but tiny).
- Per-sub-block ⟨r̃⟩ jitter at N=500: **0.0090–0.0109**.
- **Predicted span = 0.50–0.61 sd.**

**Verdict: UNDERPOWERED. No tension is established between the flat profile and P1's mechanism, and none
is excluded.** The opposite-sign fitted slope is not evidence of anything at this N.

And the underpower is not a design flaw that a better split would fix — it is §6's data limit appearing
in a second place. P1's predicted *internal* variation across γ ∈ [14, 2515] is ~0.005, while the noise
floor using **every zero that exists** below that height is ~0.0054. **The internal slope test at low γ
is permanently underpowered**: the effect to be resolved sits at the floor of the entire available
population, regardless of how the block is cut.

## 5. Maass companion gate — **IT FIRES**

Cap-clear was done (L_max ≈ 66–84, Σ² read to L=15, within by ~4×). Misfit-clear was not, and fixing the
Weyl R² and R·lnR terms from theory does not absorb misfit — it leaves it as **unabsorbed systematic**.
Measured: residual S(R) after the theory-fixed fit, decomposed into smooth trend vs fluctuation.

| sector | n | S(R) sd (levels) | deg-2 trend | deg-3 | deg-5 | **% of Var[S] that is smooth trend** |
|---|---|---|---|---|---|---|
| parity 0 | 266 | 0.8136 | 0.6174 | 0.6243 | 0.6247 | **57.6 → 58.9%** |
| parity 1 | 334 | 0.8781 | 0.7296 | 0.7386 | 0.7392 | **69.0 → 70.9%** |

**Between 58% and 71% of the "fluctuation" in each parity sector is a smooth low-order trend** —
saturating by degree 3, so it is genuinely low-frequency and not a fitting artifact of the probe.
Amplitude **0.62–0.74 levels** of unabsorbed systematic. (ζ's poly3 misfits the *exact* counting function
by 2.764 levels; Maass has no exact counting function, so the trend in S(R) is the available analogue.)

**Scope of the damage, stated precisely:**
- **CP1 / Phase 4's endpoint verdict is UNTOUCHED.** It rests on ⟨r̃⟩, which is unfold-invariant — this
  systematic cannot reach it. The 7.3σ / 6.4σ GOE exclusions stand.
- **Any Σ²-based or long-range Maass reading is touched**, including the supporting `sigma2_slope_vs_L`
  leg in `maass_analysis_measured.json`. Being under the L_max cap does not help: the cap bounds
  *contamination reach in L*, and this is an *amplitude* problem inside the cap.
- **Cap-clear and misfit-clear are a pair, and only one passes.** That was the prediction and it is
  confirmed.

## 6. Feasibility is permanent, not self-defeating

Below the block's top (γ = 2515.3) there are **1999 zeros in the entire catalogue** — R-vM smooth
predicts 1999.4. The arithmetic checks. **`zeros6[:2000]` is not a window choice; it is the whole
population below its own top.**

| region | zeros available | best-ever ⟨r̃⟩ floor |
|---|---|---|
| γ < 2515 | 2000 | 0.00542–0.00544 |
| γ < 5000 | 4520 | 0.00362–0.00402 |
| γ < 10000 | 10142 | 0.00242–0.00299 |

P1's excess here is 0.01732, so the **permanent ceiling is 3.18–3.20σ**, and P1's measured **2.45σ is 77%
of everything that can ever exist at that height.** No future compute moves it.

**Status line, replacing both "expensive" and "available but self-defeating": PERMANENTLY DATA-LIMITED.**
The prior framing was still wrong in kind — it implied a tradeoff to be navigated. There is no tradeoff;
there is a boundary.

## 7. Reciprocal self-audit

Symmetry is owed. My constructed-mechanism errors this session: a tautology in my own seal (caught
pre-run), Var[S] sampled on the wrong branch of a jump process, an inert Poisson arm inside a sealed
conjunction, a gate arm at 0.3% of available contrast compounded by a decoy η that sat on the bracket,
and an unweighted mean compared against a weighted one. **Five, of which four are the same defect: a
number compared against a differently-defined number, or a test whose power was never computed.** The
auditing held; the construction did not. Same asymmetry, both directions — which is the argument for
keeping the gates rather than for trusting either party's mechanism-building.

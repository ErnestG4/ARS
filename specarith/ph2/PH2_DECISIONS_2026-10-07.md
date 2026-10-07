# Phase 2 decisions (Will, 2026-10-07, ~02:40) — on the BBLM / Bogomolny–Keating literature report

Filed verbatim. They answer `lit/bblm_bk.md` (agent report). Phase 2 is not sealed; these bind its pre-registration.

```
check these against the primary sources before anything is sealed.

1. Λ: adopt the corrected value, but it doesn't change anything you'd measure. Citing Bornemann–Forrester–Mays (2017) with Λ = 1.5731510713… is right. The size of the effect, though: N_eff scales as 1/√Λ, so a change in the fifth decimal moves N_eff by about 3.5 parts per million, far below anything the data could resolve. Record it as a citation correction, not a risk.

2. Bogomolny–Keating: accept. My brief cited "Bogomolny–Keating (1995–96)" without saying which paper. The pair correlation with arithmetic lower-order terms is the 1996 PRL; the Nonlinearity papers are about higher correlations. Cite the PRL for Phase 2 and the comb leg.

3. The heights: this is a real error in my brief. I listed Odlyzko tables "around 10¹², 10²¹, 10²², 10²³" and mixed up zero number with height. The public tables reach zero number 10²², which is height about 1.37×10²¹, as the report says. But Phase 2 doesn't need the 10²³ data:

The finite-size law depends on log(E/2π), and the public tables already span it from about 9 (low zeros) to about 46 (zero number 10²²).
That's enough heights to test the N_eff law across a wide range.
Have CC check whether David Platt's rigorously verified zeros, available through the LMFDB, add useful intermediate heights.
Re-scope "10²³" to "any additional height with a public, hashable source." Don't block on it.

4a. α versus ᾱ: decide by source, before data. I can't verify the ᾱ = 2α − 1 relation from here. The clean rule:

primary model: BBLM's leading correction (N_eff alone), with BBLM's own scale convention;
secondary model: the higher-order kernel, with whatever scale convention its own source (Bornemann–Forrester–Mays) defines, verified there.

Mixing a scale factor from one paper with a kernel from another is exactly the wrong-slot error.

4b. Unfolding density: avoid both formulas and use the exact one. The density of zeros is (1/2π)·log(E/2π). The log(E/2πe) form belongs to the counting function N(E), so the "misprint" is likely a mix-up between N and its derivative. The two differ by about 1/log(E/2π), around 2% at the top heights, larger than the effect itself, as the report says. Sidestep the issue the same way the Phase 6 seal does: unfold with the exact smooth count, θ(E)/π + 1, from the Riemann–Siegel theta function, not with either density approximation. That also keeps Phase 2 and Phase 6 consistent.
```

Actions (CC): Phase 2 to-dos added to `../NOTES.md`'s overnight plan — (a) verify the report's load-bearing claims
against the primary sources (Λ digits, BBLM eqs. 16/19/24, BFM's ᾱ and its scale convention, the sine/CUE_N determinant
method); (b) scope Platt's LMFDB zeros as additional public, hashable heights.

## Second round (Will, 2026-10-07 morning) — 4a and data

Filed verbatim:

```
Phase 2 4a: both arms declared; PRIMARY = "N_eff alone" (BBLM convention);
SECONDARY = BBLM eq. 24 / BFM higher-order with ᾱ = 2α − 1 per BFM. No mixing.
Data: Platt blocks by md5 at heights declared pre-data (log(E/2π) 9–22.3,
not the full 1.29 TB) + Odlyzko top tables; 24.5–44.6 gap stated as a limit.
```

## Third round (Will, 2026-10-07 midday) — guidance for the Phase 2 seal

Filed verbatim:

```
Phase 2, a few things for its seal, on top of your decisions (both curves, with "N_eff alone" primary; exact-θ unfolding; heights declared before data; BFM's Λ):

Use the known misprint as a red path. Unfolding with the log(E/2πe) form is a real error from the literature, about 2% at the top heights, larger than the effect being measured. The gate should fail on it. That shows the instrument is sensitive to precisely the mistake that's already caught people. Declare the Λ correction (about 3.5 ppm in N_eff) as an unreachable red path in the pre-read, the way Phase 6 listed its unreachable red paths.
Expect a huge effect at low heights. N_eff = log(E/2π)/√(12Λ) is only about 2 at the lowest zeros, rising to about 10.6 near zero number 10²². The finite-size correction is enormous at the bottom and subtle at the top, so per-height results matter more than a pooled one.
Gate structure per height bin:
G0: CUE draws at N_eff reproduce BBLM's published curves. The known answer, run before any zeros are read.
G1: the real zeros match CUE(N_eff) within the sealed tolerance.
Power arm: asymptotic GUE (N = ∞) must be rejected, at least at low heights where the gap is large.
Resolution arm: CUE at N_eff × 0.8 and × 1.2 should also be rejected where the data has the power. That turns "consistent with N_eff" into "N_eff pinned to within ±20%," a much stronger statement.
One witness, not three. Per Task B, F(α), Σ² and Δ₃ count as a single witness. Pick the primary statistic, the ⟨r̃⟩ distribution or the nearest-neighbour spacing, and seal it.
```

CC notes (checked before drafting; carried into PH2_SEAL_DRAFT):
- ⟨r̃⟩ cannot be the primary: Nishigaki 2025 (lit/bblm_bk.md) — the CUE_N gap-ratio correction is O(N⁻⁴) (the O(N⁻²)
  term cancels), so ⟨r̃⟩ is blind to the N_eff⁻² effect. Primary = the consecutive-spacing distribution (BBLM's).
- N_eff at the very lowest zeros is ≈ 0.19 (first zero), 1.17 at γ = 10³, 2.16 at the top of zeros1 (log(E/2π) = 9.39);
  10.78 at zero number 10²² (log 46.83). Below N_eff ≈ 2 the p₀ + p₁N⁻² expansion is not meaningful.
- CUE(N) is defined by matrices only for integer N; BBLM/BFM evaluate it at real N_eff via the Fredholm determinant
  det(I − K^N) (K^N = sin πx/(N sin(πx/N)), real N) and the closed form p₁ = −(1/12)(s²p₀)″ (Forrester–Shen).
- Release v2026.10.07 published by Will: "checkpoint for the specarith branch taken before the work begins".

## Fourth round (Will, 2026-10-07) — answers to PH2_SEAL_DRAFT §9

Filed verbatim:

```
Phase 2 decisions (Will):
1. Primary = p(s); ⟨r̃⟩/Σ²/F(α)/Δ₃ descriptive, one witness.
2. Seal bins with N_eff ≥ 2; justify the cutoff in the seal from the
   pre-read's next-order-term estimate. Lower bins descriptive.
3. Truncation allowance: adopt for the PRIMARY only (leading-order law).
   Per bin, if the widened tolerance prevents rejecting N=∞ or makes the
   resolution arm meaningless → primary NOT RESOLVABLE there. SECONDARY
   (BFM higher-order) uses statistical tolerance only — the sharp test.
4. Platt heights ≈13, 15, 17, 19, 21, 22.3 (one file each), md5-pinned in
   the seal before download.
5. Per-bin resolution target sealed from the pre-read (e.g. 3× predicted
   SD of N̂); ±20% remains the floor target; achieved intervals always
   reported.
```

## Fifth round (Will, 2026-10-07) — seal text approved with amendment A1

Filed verbatim:

```
Phase 2 seal text: APPROVED with one amendment (A1):
A1. CI robustness: add a moving-block bootstrap of each bin's own
spacings (block lengths declared pre-data, e.g. sweep 10/30/100 × N_eff
levels). G1 uses the WIDER of the CUE-calibrated CI and the bootstrap CI.
G0d also validates bootstrap coverage on CUE surrogates. Reason: concatenated
CUE_N blocks impose a within-block sum constraint and zero between-block
correlation that the zero sequence does not share.
κ = N/N_eff estimand: approved.
Commit as PH2_SEAL text; proceed to code + pre-read.
```

## Sixth round (Will, 2026-10-07 afternoon) — the pre-read's proposed amendments PA1–PA4

Filed verbatim:

```
Phase 2 amendment decisions (Will):
PA1 adopt: fit window s ≤ 2.0, model normalised over the window, every bin,
both arms. Report windows 1.8 and 2.2 descriptively (sensitivity).
PA2: allowance = MAX of the two shifts. Rationale for the seal: the
exact-CUE_N shift and the secondary shift measure distance to two
ALTERNATIVE references for the truth (ζ = CUE(N_eff) vs ζ = BFM higher-
order); only one can hold, so the allowance must cover the larger, not
their sum. Sum-based verdicts for bins A and B reported descriptively.
PA3 adopt.
PA4: Will downloads the six Platt files manually into
specarith/ph2/data/platt/; verify with fetch_data.sh against pinned md5s.
```

Status at filing: PA4 done (all six md5 OK, results/logs/fetch_data.log, commit "all six Platt files … verified").

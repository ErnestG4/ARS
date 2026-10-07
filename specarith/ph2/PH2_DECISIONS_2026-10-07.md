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

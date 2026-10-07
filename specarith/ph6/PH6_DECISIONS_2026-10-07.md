# Phase 6 decisions (Will, 2026-10-07)

Filed verbatim from Will's message. These amend `PH6_BRIEF_v1.md` and take precedence where they differ. They answer
the review given at the start of the 2026-10-07 session (raw-γ statistic; exact Weil bar; G4 boundary condition; G1
parity split + completeness; G2 arms; BBM circularity; INAPPLICABLE; 6.3 leak and reachability).

```
Phase 6 decisions (Will):
1. Programme brief v1 → copied into the repo now (file: cc-brief-ars-
   spectral-arithmetic-v1.md). Phase 2 = that brief's finite-height
   CUE(N_eff) work, not arsrh's de Bruijn–Newman phase.
2. Adopt raw-γ S(τ) + smooth-term subtraction; nulls mapped through N̄⁻¹.
3. Exact Weil-formula bar REPLACES "within tolerance" for G0; tolerance =
   declared float error + window-truncation bound. Landau stays as the
   cited sign/weight statement. Template regression with zero
   non-prime-power coefficients = silence arm.
4. G4: corrected BC √L ψ(L) = e^{iθ}√l ψ(l); run L/l = 2 (confusable:
   positions fire, weights must FAIL, 3/5/7 silent) + an incommensurate
   ratio as plain null.
5. G1a (sum) / G1b (difference, reflection-orbit sign witness) after
   fetching the desymmetrised Selberg formula; Weyl completeness is a gate.
6. G2: compute more zeros with cypari2; add the χ(2)=0 silence and the
   log 9 sign arms.
7. BBM: INAPPLICABLE unless an independent finite-basis discretisation
   exists in the literature. Do not invent one post hoc.
8. Verdicts gain INAPPLICABLE. Energy scale fixed from T1 before T3 is read.
9. 6.3: family may be ≥2D chaotic or a quantum graph. Held-out baseline
   = truncated explicit-formula reconstruction from the training primes;
   only prediction beyond it counts. Silence arm + fake-prime FLEXIBLE
   null both sealed.
10. Work in a new worktree off main: ph6-xp.
```

## Filing notes (CC)

- Item 1: the file was not found on disk on 2026-10-07 (searched /home/combust and the Windows Downloads/Desktop);
  it was filed from Will's paste as `specarith/cc-brief-ars-spectral-arithmetic-v1.md`.
- Item 3 names G0 only. G1 (Selberg) and G2 (Dirichlet explicit formula) are exact identities of the same kind; whether
  the exact bar also replaces "within tolerance" there is an OPEN question for Will (not assumed).
- Item 10: worktree `.claude/worktrees/ph6-xp`, branch `ph6-xp`, created from main 94f32da.

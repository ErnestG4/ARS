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

## Second round (Will, 2026-10-07, later)

Filed verbatim:

```
Phase 6's gates, then Phase 2's first item, then the rest.

6.0 (the G0–G4 gates): exact known answers, cheap, independent of every other phase, and the first exercise you wanted.
Phase 2, first item: the CUE(N_eff) comparison. It unblocks Phase 6's T2, so it should come before the 6.1 candidates are read rather than leaving T2 pending for long.
Phase 1 (Katz–Sarnak): can follow, or run alongside on spot, since it touches neither.

2. The exact bar beyond G0: yes, for G1 and G2. They're exact identities of the same kind, so use the same structure: tolerance = declared numerical error plus the window-truncation bound, both computed in advance. Each has a specific caution:

G1 (Selberg). "Exact" means every term has to be present: identity, hyperbolic, elliptic, and the cusp's scattering term. The scattering term involves ζ'/ζ, and it's computable. That's a feature: if any term is mishandled, the exact bar exposes it immediately. The r < 100 cap sets a coarse resolution of about 2π/100 ≈ 0.06. That's still enough, because the shortest closed geodesics have lengths 1.925 (trace 3), 2.634 (trace 4) and 3.13 (trace 5), well separated. Declare the cap and the truncation bound in the seal. The Mayer cross-check for G1b is a real gift: two independent derivations of the parity-difference sum.
G2 (Dirichlet). The tolerance follows from the precision of the PARI-computed zeros plus the height cutoff. Declare both.

Two of CC's reconciliations to accept as stated:

Task B versus raw γ: S(τ) works in the explicit formula's own variable, so S ≠ F, with the smooth term taken from the exact θ.
The parity-label correction: sym0 = even, sym1 = odd. G1 is capped at r < 100, where the Weyl gate passed.

The next steps CC listed are right: fetch and file the primary sources (including Bellissard's comment on Bender, Brody and Müller, and any reply), hash both Odlyzko files, then draft the 6.0 seal for your review.
```

Filing note (CC): the "Filing notes" question above (exact bar for G1/G2) is answered YES here. The programme brief
Will later dropped as a file (`cc-brief-ars-spectral-arithmetic-v1.md`, Downloads 00:55) is byte-identical to the
copy filed from the paste (sha256 aa460691…8188); the duplicate at the worktree root was removed.

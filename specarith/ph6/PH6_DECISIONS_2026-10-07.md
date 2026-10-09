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
Will later copied into the ph6-xp worktree root (`cc-brief-ars-spectral-arithmetic-v1.md`, also in Downloads, 00:55) is byte-identical to the
copy filed from the paste (sha256 aa460691…8188); the duplicate at the worktree root was removed.

## Third round (Will, 2026-10-07) — G1 window and seal notes

Filed verbatim:

```
Go with (a). Keep G1's window inside r ≤ 98.76 and declare the truncation bound there. Resolution barely changes, and fetching 17 forms through LMFDB's captcha, with a column-corrupting summariser in the path, isn't worth the risk. Correcting "complete below 100" to "nothing missing below 98.765" was the right fix: that's what the evidence actually supports.

Three notes for the seal:

The exact bar will check the elliptic weights itself. Both sources for the 1/8 and 1/(3√3) weights come from Booker's group, so they're two derivations but not fully independent. That's fine, because G1 is an exact identity: a wrong weight can't hide, it makes G1 fail. Write the failure ladder so that if G1 fails, the first thing checked is each term's weight against Booker–Strömbergsson eq. (2.39), before anything else. Add Iwaniec or Hejhal as a third source later, if one becomes reachable.
G1b is the cleanest gate in the battery. With the whole continuous-spectrum term in the even sector, the even-minus-odd difference has no scattering term at all: just reflection orbits with lengths 2·arcsinh(t/2) and a sign. Together with the Mayer cross-check and Booker–Lee's agreement to 2×10⁻³², it's well anchored.
The pilots are fine as disclosed. They checked an identity that can't be tuned, on small subsets, without the gate statistic, so they can't have biased the gates. Disclosing them in the seal is the right level of caution.

The even-pair Gaussian times cos(τr) is the right form for G1, and it's worth the seal saying explicitly why G0 and G1 use different-looking statistics, so nobody later reads that as an inconsistency.
```

## Fourth round (Will, 2026-10-07) — review of PH6_SEAL_6.0_DRAFT v0

Filed verbatim:

```
This draft is very good, and the §0 correction is right. I repeated the "G1b is scattering-free" claim without checking it. The continuous-spectrum term lives entirely in the even sector, so it survives into even − odd, and the clean object is the odd sector alone. Gating each sector separately is the right response.

Answers to §12:

G2 height: 2×10⁴. Two hours of PARI is cheap, and it keeps all four sign arms, including log 9.
Candidates: ≥ 3×10⁴ levels, NOT RESOLVABLE otherwise. Validate those numbers per addition 2 below.
G1: gate per sector; G1a and G1b reported as implied.
α = 0.01, K_edge = 8.5, safety factor 2: accept.
CUE left out of G3: accept. Keep it separate from Phase 2's finite-size CUE(N_eff), which is a different question and stays with T2.
The GUE band for T3: accept.
Two additions before sealing, both about covering the configurations candidates will actually be in:

A small-window ζ identity gate (G0-s). At G0's and G2's window widths, the smooth Γ/θ term is below 10⁻³⁰⁰ for τ ≥ 0.5, so neither gate ever exercises it. Candidates with around 3×10⁴ levels, rescaled through T1, may land in the small-σ regime where Sm actually matters. Add a sub-gate running the ζ identity with a small window, for example on the low zeros at a σ comparable to the pilot's, so the smooth-term machinery is tested exactly before any candidate's readout depends on it.
A real-zero positive control at candidate size. The G3 positive control plants lines directly in r(τ), which tests the readout's linearity but not a real spectrum. Promote one slice of 3×10⁴ consecutive real zeros (from zeros6, or a block of zeros1), run at the candidate configuration rule, to a gate:
T3 must read PASS;
R must contain M;
R must match the design table's ~26/34.
That checks the Q2 numbers empirically on actual arithmetic data, at exactly the size candidates will be judged at.
Everything else reads right:

the raw-γ statistic, with S ≠ F stated;
the corrected boundary condition;
the λ = log 2 confusable with its WEIGHT/SIGN attribution;
the triple class enumeration as G1-pre;
the red paths;
the failure ladder;
the disclosed pilots.
With those two additions, it's ready to commit as PH6_SEAL_6.0.md.
```

CC notes on the two additions (written into the seal, §8a/§8b):
- G0-s: under the §3 configuration rule a ≥ 3·10⁴-level candidate has σ ≈ 1515 (ζ scale), where Sm ≈ 2πρ̄·e^{−σ²τ²/2}
  is negligible; Sm is visible only for σ ≲ 15 (~100-level spectra). G0-s is kept as the only exact test of the
  smooth/pole/θ machinery (the code path), not as a candidate-configuration test.
- G0-c: on real zeros the readout is exact (c_n = a_n by the explicit formula at any size), so G0-c tests that the T3
  rule does not reject the truth at candidate size; R depends only on the band (the null draws), so "R ≈ 26/34" is a
  check of the band against the design theory. Power at candidate size is added as G3-c (GUE nulls at G0-c's
  configuration read against ζ weights must FAIL).

## Fifth round (Will, 2026-10-07 morning) — decisions on PH6_PROPOSED_AMENDMENTS.md

Filed verbatim:

```
Phase 6 decisions (Will):
A1 adopt. A3 adopt. A4: (b) T = 4·10⁴. A5 adopt — Gamma-law band derived
analytically from the LS coefficient null distribution, not fitted to the
seen calibration draws; disclose the original bar's failure on those draws.
A6 adopt. A7, A8, A9, A10, A12 adopt. A11: adopt only if pre-read shows RP3
@100δ below the sealed firing margin; otherwise keep 100δ.
Seal with --A1 --A6 --A4b and results/preread_proposed.

Process: pre-commit hook rejecting `pgrep -f` in repo scripts.
```

## 6.1 decisions (Will, 2026-10-08) on PH6_1_SEAL_DRAFT D1–D6

Filed verbatim:

```
Phase 6.1:
D1 both ϑ variants declared, verdict per variant. D2 N = 3·10⁴; E-linked
torus as declared secondary variant. D3 accept max(5·block SD, 0.02).
D4 large-N ⟨r̃⟩ refs (Atas 2013: GUE 0.5996, GOE 0.5307, Poisson 0.386) as
labels; verdict bands from matched-size GUE/Poisson draws; fix repo tables.
D5 accept: zeros at matched height. D6 accept: nearest class by ⟨r̃⟩ with
matched-size bands; NNS-KS and Σ²+Δ₃ descriptive; INAPPLICABLE for
integrable crystals.
```
Accompanying note (Will): at 3·10⁴ levels finite-size offsets in ⟨r̃⟩ are comparable to the 0.003 surmise/large-N gap,
hence bands from matched-size draws with the large-N constants as labels; choosing one ϑ now would be a needless fork.

## 6.1 decisions, second round (Will, 2026-10-08 morning) — on MORNING_2026-10-08.md

Filed verbatim:

```
6.1 decisions (Will):
1. C3b INAPPLICABLE (paper defines no single spectrum; stitching = new construction).
2. C3a: N = 6·10⁴; convergence check = agreement of low-|E| levels between
   N = 3·10⁴ and 6·10⁴ runs where both valid. (b) rejected (mirror half adds no
   independent info). (c) fallback if 6·10⁴ fails convergence.
3. PA-6.1-1 ADOPT with change:
   T4 as proposed (nearest class, ≥3 SD separation else ambiguous/NR;
   integrable crystals INAPPLICABLE).
   T2: PASS iff |r̃_cand − r̃_zeros| ≤ 3·√(SD_cand² + SD_zeros²), both SDs by
   block bootstrap over T1-matched ranges; GUE band descriptive.
Open lead (descriptive): low-height ⟨r̃⟩ excess (0.6129, falling with height) and
Phase 2 κ̂ > 1 — list together; do not merge post hoc.
```

## 6.1 pre-seal confirmations (Will, 2026-10-08 midday)

Filed verbatim:

```
6.1 pre-seal confirmations (Will):
- T1: seal text states T1 tests mean density + zeros-level count rigidity
  (global offset); report T1's density/slope component separately,
  descriptive, for attribution.
- Crystal criterion ⟨r̃⟩ ≥ 0.9: accept. Add T4 rule: outside all bands by
  > 15 SD and < 0.9 → "intermediate, no standard class" (T4 NOT RESOLVABLE).
  Margin chosen so zeros (8.5 SD from GUE) still classify.
- T2 bootstrap: block sweep {30, 100, 300} ratios, widest CI; 2000 replicates.
- Read candidates at res2: accept.
Then: per-candidate T3 bands → make_seal_json61.py → seal on go.
```

## 6.1 GO (Will, 2026-10-08 evening)

Filed verbatim:

```
GO: commit PH6_SEAL_6.1.json as the seal commit, tag ph6.1-seal (Will pushes).
Then read C1a, C1b, C2, C4 via tests61.py read; report every test and variant,
T3 per-prime-power failed arms per model, and the decided-in-advance statuses
for C3a, C3b, BBM and the Sierra mirror.
```
Will's sanity checks before the go: C1a/C1b bands identical (the band depends on configuration only, which the two
variants share to within 0.09 in E_hi); C4's band ≈ 4× tighter over a 14× wider range, as √14 ≈ 3.7 sampling predicts.

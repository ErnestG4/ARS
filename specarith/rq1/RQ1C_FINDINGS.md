# RQ1-c findings: theory-light predictions at X = 10¹² (ℤ[√2], ℤ[i], ℤ[ω] prime angles at matched N)

**Status: PASS-under-ruling on P1, P3 and P4; the literal VOID stands.** The sealed double read failed its byte-for-byte
`cmp` (VOID condition 1) because the read code wrote CPU timings into its output JSON. Will's post-hoc ruling (2026-10-29)
accepts double-read equivalence on all non-timing fields, verified by identical stripped-file sha256s. Before the ruling,
only the P1 / P3 / P4 verdict lines had been seen. Details: `RQ1C_READ_VOID.md`. Numbers: `RQ1C_READ_REPORT.md`. Seal:
`RQ1C_SEAL.md` (tag `rq1c-seal`; Bitcoin blocks 973605 / 973607).

Every verdict is conditional on the sealed SE model (calibrated on synthetic mirror-symmetric sets; its validity for
arithmetic data is assumed, not tested), as in RQ1.

## 1. The headline: P4, ℤ[ω] between the other two fields, by about the predicted amount

ℤ[ω] prime angles had never been examined above X = 10⁸ (Phase 34d). At β = 0.55, at matched N, R_ℤ[√2] > R_ℤ[ω] >
R_ℤ[i] at all three X, as the conductor constants predict (C_ℤ[√2] = 4.62 > C_ℤ[ω] = 3.30 > C_ℤ[i] = 2.77):

| X | ℤ[√2] − ℤ[ω] | ℤ[ω] − ℤ[i] | ω–i as a fraction of the predicted separation | D_ωi / D_√2i (predicted 0.283) |
|---|---|---|---|---|
| 10¹⁰ | 6.4 SE | 2.3 SE | 93% | 0.254 ± 0.100 |
| 10¹¹ | 10.1 SE | 3.1 SE | 82% | 0.226 ± 0.067 |
| 10¹² | 13.8 SE | 5.0 SE | 79% | 0.261 ± 0.047 |

The field's arithmetic sets both the order of the fields and roughly the size of the gaps, and it held for a field that
had not been looked at. Each ratio is within 1σ of 0.283. All three sit a little low, consistent with the ≈ 10%
shortfall the conductor-shift picture already showed near the crossover (RQ1 §5: there the observed ℤ[√2]–ℤ[i]
difference exceeded the conductor shift by 1–30%, an excess in the ratio's denominator). This is the fields-and-couplings
result in its cleanest form so far.

**Caveats.**
- **C_ω = log 27** is derived (`RQ1B_STEP0.md` §3), from the d·(wk/2)² rule with w = 6. It has not been checked against
  a published ℤ[ω] Hecke L-function source; that check is in progress.
- **The SE model** is assumed for arithmetic data.
- **The rigidity cells** (β 0.40, 0.45) were unpowered as sealed (predicted separations 0.4–1.1 SE). Four of the six
  are ordered; both exceptions are within 0.4 SE of a tie.

## 2. P1: the B2 direction replicates at 10¹², narrowly

T = 4.41 against the frozen t = 3.93, and the guard holds. Almost all of T comes from the β = 0.45 cell (D/SE 3.01). At
β = 0.40, D/SE is 1.40. That matches the power analysis: power 0.87 / 0.79 / 0.32 under the 1/log X, 1/log² X and
X^{−δ} laws. ℤ[√2] stays above ℤ[i] in the rigidity regime at 10¹² as at 10¹⁰ and 10¹¹ (direction only).

## 3. P3: PASS, but the trend matters more than the PASS

The crossover lies at β = 0.538 ± 0.006 at 10¹², inside the sealed window [0.51, 0.54]. Attribution as sealed: the
crossover stays pinned near β ≈ ½. **Stated next to the PASS:**
- The location has risen at every step: 0.525 ± 0.009 (10¹⁰), 0.529 ± 0.005 (10¹¹), 0.538 ± 0.006 (10¹²).
- It now sits 0.3 resolution units inside the window's upper edge.
- No single step is significant (10¹¹ → 10¹²: 0.009 ± 0.008).
- "Pinned near ½" is therefore less secure than the PASS suggests. If the drift continues, the next decade could
  leave the window (lead L10).

## 4. P2 (descriptive): the field difference may decay as a power of X

At β 0.40, 0.45 and 0.55, D(10¹²) is inside every law's consistency window. At β = 0.60, D = 0.0181 ± 0.0015 falls
below both logarithmic windows (1/log X and 1/log² X) and inside only the X^{−δ} window. The power law is therefore the
only one of the three consistent with all four cells. If that holds, the difference between fields shrinks like a power
of X and vanishes in the limit: all the fields eventually look alike at this scale. It rests on one cell of a
descriptive comparison, so it is a lead, not a finding (L11).

## 5. Process

- **Seal and stamp:** sealed, OTS-stamped, Bitcoin-attested and verified on two explorers before any 10¹² value was
  computed.
- **Pre-read checks:** pins, 30,200 segment hashes and the mount guard all passed.
- **Literal VOID:** caused by timing fields in the cmp'd output, a read-code defect that was not caught because the
  `read` mode had never been run twice.
- **New rule (TOOLKIT §9.F):** dry-run the full double read and its `cmp` on a cheap input before sealing; timings go
  to a sidecar file.
- **Cost:** 19.5 spot core-h per read, 0.69× the model. Wall 8.3 / 8.7 h, more than twice the estimate.

## 6. Leads (recorded, not pursued)

- **L10:** the upward drift of the crossover location.
- **L11:** the possible power-law decay of the field difference.

Testing either needs another decade of X, about 5,000+ spot core-hours of archives (Will, 2026-10-29). They are
recorded only.

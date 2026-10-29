# RQ1-c read report (2026-10-29) — results reported as PASS-under-ruling

**Status.** Literal VOID (cmp, condition 1) stands (`RQ1C_READ_VOID.md`). Post-hoc ruling (Will, 2026-10-29): double-read
equivalence on all non-timing fields, verified by the stripped-file sha256 (b0200f8c…01fa, identical for both reads;
3b353d47, committed before any value below was opened). Before the ruling only the P1 / P3 / P4 verdict lines had been
seen. Every verdict below is **PASS-under-ruling**, not a clean PASS.

Seal `RQ1C_SEAL.md` (tag `rq1c-seal`, b936b358; Bitcoin blocks 973605 / 973607). Matched N at 10¹²: n = 18,803,945,053,
N = 37,607,890,106; binned estimator B = 36; ℤ[ω] and the 10¹⁰ / 10¹¹ cells exact. Source: `results/rq1c_read_void/
read1.json` (= read2.json on every non-timing field). Pre-read checks all passed: mount guard, 18 pins, 30,200
segment hashes. The 10¹⁰ / 10¹¹ ℤ[√2] and ℤ[i] cells recomputed inside the read equal the sealed `read1.json` (asserted
in the code).

## P1 — B2 replication at 10¹²: PASS-under-ruling
| β | K | D = R_ℤ[√2] − R_ℤ[i] | SE_diff | D/SE |
|---|---|---|---|---|
| 0.40 | 16,987 | +0.01586 | 0.01129 | 1.40 |
| 0.45 | 57,395 | +0.02157 | 0.00717 | 3.01 |

T = 4.412 against the frozen t = 3.928 (scales 1.0 at both cells); guard holds (no D < −2·SE). Attribution as sealed:
the field difference's direction replicates at 10¹² (power at the frozen t was 0.87 / 0.79 / 0.32 under the three decay
laws).

## P2 — scaling of D (descriptive; no verdict)
D(10¹²) against each law's committed prediction and consistency window (prediction ± 2·SE_resid incl. the 10¹² SE):

| β | D(10¹²) ± SE | 1/log X: pred [window] | 1/log² X | X^{−δ} |
|---|---|---|---|---|
| 0.40 | 0.0159 ± 0.0113 | 0.0244 [−0.0090, 0.0578] **in** | 0.0219 [−0.0094, 0.0531] **in** | 0.0131 [−0.0332, 0.0593] **in** |
| 0.45 | 0.0216 ± 0.0072 | 0.0277 [0.0055, 0.0499] **in** | 0.0250 [0.0043, 0.0456] **in** | 0.0128 [−0.0151, 0.0407] **in** |
| 0.55 | 0.0510 ± 0.0027 | 0.0598 [0.0507, 0.0690] **in** (at the edge) | 0.0535 [0.0450, 0.0620] **in** | 0.0538 [0.0338, 0.0737] **in** |
| 0.60 | 0.0181 ± 0.0015 | 0.0283 [0.0228, 0.0337] **out** (below) | 0.0253 [0.0203, 0.0304] **out** (below) | 0.0238 [0.0124, 0.0353] **in** |

At β 0.40–0.55, D lands inside every window (the laws were not separable there, as sealed). At β 0.60, D falls below
both logarithmic windows and inside only the X^{−δ} window: the steepest decay law is the only one of the three
consistent with all four cells. Descriptive, as sealed.

## P3 — crossover location: PASS-under-ruling
Residual R_ℤ[√2](K) − R_ℤ[i](aK) on the fine grid (a = 2.5204): −0.00397 ± 0.00288 at β 0.53, +0.00082 ± 0.00259 at
0.54; first ≤ 0 → > 0 crossing by linear interpolation at **β = 0.5383, resolution ± 0.0057**: inside [0.51, 0.54].
Attribution (Will): the crossover stays pinned near β ≈ ½ at 10¹².

Recorded alongside (descriptive):
- The location is 0.0017 (0.3 resolution units) inside the upper edge of the window.
- Across X: 0.525 ± 0.009 (10¹⁰), 0.529 ± 0.005 (10¹¹), 0.538 ± 0.006 (10¹²); the 10¹¹ → 10¹² shift is 0.009 ± 0.008
  (1.2σ), upward in both steps.
- The resolution, 0.0057, is about twice the ≈ 0.003 the seal expected at 10¹².
- Beyond the crossing the residual peaks at β 0.56 (+0.0072) and decays towards zero by 0.65; there is no second
  crossing on the grid.

## P4 — ℤ[ω] ordering at β = 0.55: PASS-under-ruling
Both inequalities at all three X (SEs from the sealed model, each R independent):

| X | K | R_ℤ[√2] − R_ℤ[ω] | R_ℤ[ω] − R_ℤ[i] | sealed predicted ω–i separation |
|---|---|---|---|---|
| 10¹⁰ | 57,801 | +0.0567 (6.4 SE) | +0.0193 (2.3 SE) | 2.47 SE |
| 10¹¹ | 194,125 | +0.0495 (10.1 SE) | +0.0144 (3.1 SE) | 3.72 SE |
| 10¹² | 655,245 | +0.0377 (13.8 SE) | +0.0133 (5.0 SE) | 6.39 SE |

R_ℤ[√2] > R_ℤ[ω] > R_ℤ[i] at every X. Attribution (Will): ℤ[ω] falls between the other two fields, as its conductor
constant predicts. The observed ω–i separations are 79–93% of the predicted ones.

**Rigidity cells (β 0.40, 0.45; descriptive, predicted separations 0.4–1.1 SE, i.e. unpowered as sealed):**
| X | β 0.40: √2−ω / ω−i | ordered | β 0.45: √2−ω / ω−i | ordered |
|---|---|---|---|---|
| 10¹⁰ | +1.17 / +0.30 SE | yes | +2.26 / +0.29 SE | yes |
| 10¹¹ | +0.51 / +0.79 SE | yes | +2.19 / −0.07 SE | no |
| 10¹² | −0.37 / +1.77 SE | no | +1.22 / +1.79 SE | yes |
Four of six ordered; both exceptions are within 0.4 SE of a tie, as the sealed power implied.

**Ratio D_ωi / D_√2i at β 0.55 against 0.283** (delta-method SE): 0.254 ± 0.100 (10¹⁰), 0.226 ± 0.067 (10¹¹), 0.261 ±
0.047 (10¹²); each within 1σ of 0.283 (10¹²: −0.5σ). C_ω = log 27 was verified after the read against published sources (`C_OMEGA_VERIFY.md`, 2026-10-29).

## Cost
CPU 70,304 s per read (19.5 spot core-h), 0.69× the coded model (28.2); 39 core-h for the double read against the seal's
≈ 56.5 (as coded) / ≈ 75 (§3). Wall 8.3 h and 8.7 h per read, against my 3–4 h estimate: the passes averaged about
2.4 busy cores, not 16 (the thread pool was under-filled; the histogram builds are serial). The wall-time estimate was
wrong; the CPU price held.

## Process record
- **Literal VOID:** timing fields in the cmp'd JSON, a read-code defect (`RQ1C_READ_VOID.md`).
- **Ruling:** Will's post-hoc ruling, and its stripped-hash verification.
- **New rule:** TOOLKIT §9.F (dry-run the double read and cmp before sealing; timings to a sidecar).

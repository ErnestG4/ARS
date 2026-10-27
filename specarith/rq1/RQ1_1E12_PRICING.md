# RQ1 at X = 10¹²: pricing (round 92; nothing generated)

Priced with the cost model and the measured RQ1 runs (N6-2_PLAN §10; rounds 83–84 first-wave rule and round-88
mid-run check apply to every run below). Spot as of 2026-10-26 evening: 56 vCPU, 117 GB RAM, root (NVMe, btrfs)
798 GB with 238 GB free, `/mnt/data` (900 GB virtual disk on spinning storage, ext4) 840 GB free. `/mnt/data` is
`root:root` 755 and not in `/etc/fstab` yet (needs a `combust`-owned directory and a `nofail` fstab line).

## 1. Sizes

- π(10¹²) = 37,607,912,018, 9.13× π(10¹¹). Split primes per field ≈ 1.88·10¹⁰ (half of the primes for ℤ[√2],
  ℤ[i] and ℤ[ω] alike), so N ≈ 3.76·10¹⁰ ideals per field.
- K_max for β ≤ 0.70 is N^0.70 = 2.53·10⁷, so 1/K_max = 3.96·10⁻⁸. The model's relative SE there is 3.5·10⁻⁴.

## 2. Archive generation (both fields; ℤ[ω] optional)

Measured at 10¹¹ (pure-Python integer arithmetic, 28 processes): ℤ[√2] 28.0 spot core-h, ℤ[i] (to 1.01·10¹¹) 27.9.
Scaled by rows (9.13×) and by about 1.08 for the longer modular exponentiations:

| Field | Spot core-h | Wall at 28 processes | Archive size (int32 pairs) |
|---|---|---|---|
| ℤ[√2] to 10¹² | ≈ 275 | ≈ 10 h | ≈ 150 GB (10,000 segments of 10⁸) |
| ℤ[i] to 1.01·10¹² | ≈ 280 | ≈ 10 h | ≈ 152 GB |
| ℤ[ω] to 1.01·10¹² (optional; new generator and gates) | ≈ 280 | ≈ 10 h | ≈ 152 GB |

- Two fields: ≈ 555 spot core-h, ≈ 20 h wall, ≈ 300 GB on `/mnt/data`. With ℤ[ω]: ≈ 835 core-h, ≈ 455 GB.
- The archives' first waves understated the whole run before (0.43 → 0.56 and 0.75 → 1.21), so both checks apply.
- The (a, b) pairs fit int32 at 10¹² (generators ≈ √p·ε^{1/2} ≲ 2.4·10⁶).

## 3. Storage for the read: raw against binned

The read needs θ sorted (or counted). At 10¹² that does not fit in memory raw:

| Form | Per field | Fits in 117 GB RAM | Error |
|---|---|---|---|
| Sorted θ, float64, full set (as at 10¹¹) | 301 GB | no | none |
| Sorted θ, float64, half-set θ ≤ ½ (mirror used) | 150 GB | no: external sort and a new out-of-core estimator | none |
| Gap-coded sorted half-set (2⁻⁴⁸ units, ≈ 2 B/point) | ≈ 38 GB | yes | negligible; needs a new codec |
| **Binned counts on [0, ½], δ = 2⁻³⁶, uint8** | **34 GB** | **yes (both fields: 69 GB)** | **below 0.14 SE at β ≤ 0.70** |
| Binned counts, δ = 2⁻³⁸, uint8 | 137 GB | no | below 0.01 SE |

**Binning error.** Rounding θ to bin centres biases R upward by about N·δ²·K at most. Measured on mirror-symmetric
uniform sets (N = 10⁸, K = 2·10⁴ and 2·10⁵, three δ each), the bias was 0.08–0.25 of N·δ²·K. At δ = 2⁻³⁶ (δ = 1.5·10⁻¹¹,
δ·K_max = 3.7·10⁻⁴):

| β | K | 1/K | bound N·δ²·K | in SE (relative SE at K) |
|---|---|---|---|---|
| 0.60 | 2.2·10⁶ | 4.5·10⁻⁷ | 1.8·10⁻⁵ | 0.01 |
| 0.65 | 7.5·10⁶ | 1.3·10⁻⁷ | 6.0·10⁻⁵ | 0.09 |
| 0.70 | 2.5·10⁷ | 4.0·10⁻⁸ | 2.0·10⁻⁴ | 0.57 (measured fraction 0.25: 0.14) |

- For the collapse, the bias enters at K and at a·K, so its effect on the residual is about (a − 1) times one bias,
  well below the residual's SE.
- **Recommended: binned at 2⁻³⁶.** The histogram is a counting sort: built in one streaming pass over each archive
  (≈ 150 GB read from `/mnt/data`, ≈ 25 min at HDD speed), held in RAM, no external sort. It needs a weighted
  estimator (points with multiplicities at bin centres) — new code, which can be validated on the read archives at
  10¹⁰ and 10¹¹ against the exact values, at a δ chosen to give the same N·δ²·K as at 10¹².

## 4. The read at 10¹²

- A pass over a binned field streams 6.9·10¹⁰ bin entries (full circle; ≈ 45% empty), modelled at
  1.6·10⁻⁸ s per entry locally × 2.3 ≈ 2,540 spot core-s.
- A collapse statistic on m values of β needs 2m passes (ℤ[√2] at K, ℤ[i] at a·K; 3m if D against ℤ[i] at K is also
  reported). With m = 11 (β 0.40–0.65 in steps of 0.025): 22–33 passes, ≈ 16–23 spot core-h per read, ≈ 32–46 for
  the double read. Building both histograms: ≈ 1 h wall, I/O-bound.

## 5. Witnesses at 10¹² (the expensive part)

- Synthetic binned sets need no disk: Poisson counts per bin, or a lattice fraction plus Poisson counts, generated in
  RAM (≈ 34 GB per set).
- Each replicate needs the same 2m passes on two sets: ≈ 16 spot core-h at m = 11.
- 100 null + 100 planted at full N: ≈ 3,100 core-h. Too expensive as it stands. Options for Will:
  - (i) fewer β in the statistic (m = 5: ≈ 1,400 core-h);
  - (ii) fewer replicates with the same bars (50 + 50: ≈ 1,550 at m = 11);
  - (iii) witnesses at a smaller N with the same K values. The SE at fixed K was N-independent in the 10¹¹ witness
    (empirical/model 0.82–1.04), but at the 10¹¹-size N the largest K would leave N/K ≈ 160, so this needs its own
    check.
  - These can combine (e.g. m = 7 and 60 + 60 replicates: ≈ 700 core-h).

## 6. Totals (two fields, m = 11, option (ii))

| Item | Spot core-h | Disk |
|---|---|---|
| Archives ℤ[√2], ℤ[i] | ≈ 555 | 300 GB on `/mnt/data` |
| Histograms (2⁻³⁶) | ≈ 2 | 69 GB (RAM; kept on NVMe) |
| Estimator validation on the 10¹⁰ / 10¹¹ archives | ≈ 5 | — |
| Witness (50 + 50) | ≈ 1,550 | — |
| Double read | ≈ 32–46 | — |
| **Total** | **≈ 2,150** | **≈ 370 GB** |

With ℤ[ω]: about +280 core-h for its archive, +34 GB of histogram, and its share of the witness and read.

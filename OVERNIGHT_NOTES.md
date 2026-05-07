# Overnight notes — 2026-05-07

Two background runs were kicked off before bed.  Both write logs to
`/tmp/`, results to `data/` and `plots/`, and finish without further
intervention.

## Running tasks

| pid | script | log | expected runtime | output |
|---|---|---|---|---|
| 13451 | `run_lmfdb_extend.py` | `/tmp/lmfdb_extend.log` | ~3.5 h (~150 s/curve × 87 curves at height=1000) | `data/lmfdb_zeros_h1000.json`, `data/lmfdb_extend_results.json`, `plots/20_lmfdb_extend.png` |
| ~~13964~~ ✅ done @ 04:46 | `run_mertens_liouville.py` | `/tmp/mertens_liouville.log` | finished in <1 min | `data/mertens_liouville_results.json`, `plots/21_mertens_liouville.png` |

### Mertens / Liouville result summary

- **M(x) for x ≤ 10⁷**: 3,866 sign-changes; range [-1,078, 1,143];
  M(10⁷) = 1,037.
- **L(x) for x ≤ 10⁷**: **1 sign-change** — Pólya conjecture territory;
  L stays negative for almost all x ≤ 906,150,257.  Insufficient
  events for level statistics at this N.
- **M(x) sign-change spacings**: classify as **Poisson-best**, KS_P = 0.79
  (analytical), KS_P = 0.79 (direct), mass<0.3 = 0.93.  "Mass<0.3 ≈ 1"
  means almost all normalised spacings are tiny — most sign-changes
  come in tight clusters with a few large gaps dominating the mean.
  This is the small-N signature of an arithmetic running-sum process,
  not a random matrix.

Quick status check in the morning:
```bash
tail -10 /tmp/lmfdb_extend.log /tmp/mertens_liouville.log
ps -ef | grep -E 'run_lmfdb_extend|run_mertens' | grep -v grep
```

## What each is doing

### `run_lmfdb_extend.py` — deeper LMFDB zeros
The Phase 6 LMFDB family run computed ~280 zeros per curve to imaginary
height 200.  This run pushes the height limit to 1000, giving roughly
1400 zeros per curve (≈ 5× more data per curve, and ~700× more total
spacings via the per-PLL framework).

The deeper data lets us:
- Re-test the bulk Wigner-GUE classification with much sharper KS,
- Re-run the Katz–Sarnak edge analysis (γ_1, γ_2 − γ_1, low-N spacings)
  with better statistics on the +1 vs −1 split.

### `run_mertens_liouville.py` — Mertens M(x) and Liouville L(x) sign changes
Two classical arithmetic functions:
- M(x) = Σ_{n ≤ x} μ(n)         — Mertens function (Möbius partial sum)
- L(x) = Σ_{n ≤ x} λ(n)         — Liouville function partial sum

Both flip sign at irregular integer values of x.  The locations of
those sign changes form a point process whose level statistics are
*not* predicted by any standard random-matrix theory — this is genuinely
novel data.  Sieved up to x = 10⁷ (~30 MB of state).

These running sums are arithmetically related to ζ on the critical
line: the Riemann hypothesis is equivalent to M(x) = O(x^(½+ε)).  The
sign-change density is part of that story.

## Things you can grab in the morning if you want more data

A shopping list, ordered by interestingness × ease:

### A. **More elliptic curve L-functions** (easy)
LMFDB UI → search elliptic curves with `conductor=100-1000` (or
`100-10000`), download in the same format as
`lmfdb_ec_curvedata_0507_1029.txt`.  Place in repo root.

This extends our 87-curve sample to ~500–3,000 curves and gives much
sharper Katz–Sarnak family statistics (the +1 vs −1 KS = 0.94 result on
γ_1 currently rests on n = 17 odd curves; conductor ≤ 1000 would
multiply that by ~5×).

### B. **Dirichlet L-function zeros** (very interesting, different family)
LMFDB → `https://www.lmfdb.org/L/Dirichlet/`.  Real Dirichlet
characters χ have *symplectic* family symmetry (Sp), distinct from
the orthogonal class of elliptic curves.  Katz–Sarnak predicts
genuinely different edge behaviour than elliptic curves.  This would
add a third family symmetry class to the empirical table.

A few dozen Dirichlet characters mod q ≤ 100 with a list of their first
few hundred zeros each would be plenty.

### C. **Modular form L-functions** (LMFDB)
A different family of degree-2 L-functions; Katz–Sarnak predicts the
same orthogonal class as elliptic curves, but the spectral parameter is
the weight rather than the conductor.  Different scaling regime.
Search by weight ≤ 8 on LMFDB.

### D. **Sleep EEG** (PhysioNet Sleep-EDF, larger event yields)
The motor-imagery dataset gives only ~340 events per channel-condition
segment.  Sleep recordings are 8 h long; pooling θ-band zero-crossings
across one full night yields ~150,000+ events per channel — enough to
get KS distance down to the calibrator level if a real GUE-like signal
is present.

`https://physionet.org/content/sleep-edfx/1.0.0/`

### E. **Pulsar timing residuals** (NANOGrav 15-yr or EPTA DR2)
Residuals from millisecond-pulsar timing arrays.  Public, structured
ASCII files.  Predicted to show specific spectral colour (red noise)
with a known power-law slope; level statistics of inter-residual
spacings would be a fresh test of the metric on a clean physical
signal with rigorous expected behaviour.

`https://nanograv.org/data` (data products → public releases)

### F. **Earthquake event times** (USGS catalog)
Public CSV download of earthquake event times for any region/timespan.
Predicted by ETAS (epidemic-type aftershock sequence) models to follow
specific clustering statistics.  Direct test of "biological
quasi-periodic vs. self-organised criticality" framing.

`https://earthquake.usgs.gov/earthquakes/search/`

### G. **More EEG subjects** (currently downloading)
Once your overnight EEGMMIDB pull completes, re-run `run_eeg_depth.py`;
it will pick up additional subjects automatically.  At 20+ subjects we
can start asking population-level questions instead of single-subject
demos.

## What's still on the implementation TODO

Not blocking, but worth noting:

1. **Modular form / Dirichlet L-function support in PARI** — `lfunmf()`
   and `lfunchargen()` work analogously to `ellinit/lfuncreate` but
   need a parameter tweak to integrate cleanly with `run_lmfdb_extend.py`.

2. **Edge γ_1 distribution at conductor ≤ 1000** — once you grab the
   bigger curve table (item A above), the 7.ter.1.bis edge KS test
   would jump from n = 17 odd curves to ~150 odd curves.  Big precision
   gain on the Katz–Sarnak result.

3. **Per-curve Σ²(L) and pair-correlation** (not just NNS) — the
   second-order statistics are where Katz–Sarnak family symmetry shows
   most clearly in the bulk.  Code is in `universality.py` already; just
   need a runner that aggregates per family.

4. **Tarball refresh**: when overnight runs complete, regenerate the
   release tarball with new artefacts.  See bottom of README.md for the
   command.

## Quick start in the morning

```bash
cd /home/combust/fmexplorer/criticality_tool

# Check that the overnight runs finished
tail -25 /tmp/lmfdb_extend.log   /tmp/mertens_liouville.log

# Look at the new outputs
ls -la data/lmfdb_zeros_h1000.json   data/lmfdb_extend_results.json \
       data/mertens_liouville_results.json
ls plots/20_lmfdb_extend.png  plots/21_mertens_liouville.png

# If LMFDB extended ran cleanly, also re-run the edge test on the deeper data:
#   (run_lmfdb_edge.py reads lmfdb_zeros.json by default; either copy the
#   extended file over it or edit the path.  Easiest:)
cp data/lmfdb_zeros_h1000.json data/lmfdb_zeros.json
python3 run_lmfdb_edge.py     # ~10 sec
```

Sleep well.

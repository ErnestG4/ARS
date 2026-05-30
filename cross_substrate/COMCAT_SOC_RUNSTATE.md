# ComCat + GOES SOC overnight — RUN STATE (2026-05-30)

## Channel note
Foreground Bash/Read exec has been intermittently stalled all session (the known
thinking-blocks recovery glitch). Tool results queue and flush in bursts a few turns
later. File **Write/Edit confirm reliably**, so the build below is solid; execution
confirmation is what's lagging.

## Built & ready (all syntax-plausible; self-test written into comcat_port import path)
- `COMCAT_SOC_BRIEF.md` — phase brief (Frame/Goals G1-G5/Acceptance/Out-of-scope/Commitments)
- `comcat_fetch.py` — self-sizing sequential paged FDSN downloader (adaptive time-bisection
  under the 18k/req cap, resume, byte+row verify, dedupe by id). NO parallel curls.
- `comcat_port.py` — G1 clustered fingerprint + Poisson surrogate; G2 Gardner-Knopoff
  decluster (×0.5/×1/×2 window sensitivity); G3 single-fault (N-LIMITED flag); G4
  directionality (pooled-NNS forward≡reversed + irreversibility skew/lagprod vs shuffle
  surrogate + magnitude-conditioned Omori after/before ratio).
- `goes_flares.py` — G5 GOES/SWPC flare list via HEK (paged JSON), same fingerprint +
  data-driven solar-cycle MAX-vs-MIN split.

## Launched in background (network; sandbox disabled) — verify on channel recovery
1. global M4.5 quakes 2000-2025  -> coordinates/comcat/global_m45.csv
   log: coordinates/comcat_global_fetch.log
2. central-SAF M2.5 1990-2025 (lat35-37, lon -122..-119) -> coordinates/comcat/saf_central_m25.csv
   log: coordinates/comcat_saf_fetch.log
3. GOES flares 1996-2025 -> coordinates/goes-flares.jsonl
   log: coordinates/goes_fetch.log

## To run analysis once data lands
```
cd /home/combust/fmexplorer/criticality_tool
/home/combust/fmexplorer/bin/python3 cross_substrate/comcat_port.py \
    --csv cross_substrate/coordinates/comcat/global_m45.csv \
    --fault-csv cross_substrate/coordinates/comcat/saf_central_m25.csv \
    --main-min-mag 6.0
/home/combust/fmexplorer/bin/python3 cross_substrate/goes_flares.py --analyze
```
Outputs: coordinates/comcat-fingerprint.jsonl, coordinates/goes-fingerprint.jsonl

## A-priori expectations (the calibration)
- G1: full catalog far from GUE, on the CLUSTERED side of Poisson — mass<0.3 ≫ Poisson-surrogate,
  CV > 1. Brody q / Berry-Robnik ρ rail at 0 (one-sided: blind to super-Poisson) — that's a finding.
- G2: declustering moves ks_poisson DOWN and mass<0.3 / CV toward the Poisson floor; motion monotone
  in window scale. Direction known a priori = the calibration check.
- G3: single-fault N too small for a repulsion claim; report no-false-positive-only.
- G4: pooled-NNS forward≡reversed (max|Δ|≈1e-12) AND strong clustering, while Omori after/before ≫ 1
  and irreversibility z ≫ 0. The gap = directionality the spacing engine cannot see.
- G5: flares clustered > Poisson floor; solar MAX more clustered than solar MIN.

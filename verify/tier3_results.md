# Tier-3 verification: chirp GUE unfold (FIX-3) + JPF_CAP drift (FIX-5)

Run: `PYTHONPATH=$HOME/fmexplorer/riemann_explorer $HOME/fmexplorer/bin/python3 verify/tier3_chirp_and_cap.py`

```
==============================================================================
CHECK A — chirp GUE unfold bug (audit FIX-3)
==============================================================================
Source: run_chirp_prediction.py:112-120 builds the GUE reference and
        unfolds via eig_unfolded=(eig-eig[0])/spacings.mean()  (line 117)
        = fix_gue_generator.py:60 'OLD broken procedure' (unfold_global_mean).
        Fix = semicircle-CDF unfold, fix_gue_generator.py:45-48 & 67-74.
        (fix_gue_generator NOT imported: its module body runs a GPU PLL
         diagnostic on import; the two pure helpers are replicated verbatim.)

--- N=500 (seed 42), eig range [-1.9812, 1.9717] ---
  (a) GLOBAL-MEAN : I5_ks_gue=0.0688  I10_cv=0.5761  I8_brody_q=0.856  (n=499)
  (b) SEMICIRCLE  : I5_ks_gue=0.0377  I10_cv=0.4088  I8_brody_q=1.000  (n=499)
      [canonical-trim x-check] global I5=0.0370 cv=0.4805 | semi I5=0.0372 cv=0.4107
      delta I5_ks_gue (global - semi) = +0.0311  (>0 => global-mean reads FURTHER from GUE)
      delta CV (global - semi)        = +0.1673  (GUE-surmise CV ~= 0.523; global CV inflated toward semicircle if larger)
      -> CORRUPTS: global-mean is measurably further from Wigner-GUE

--- N=100 (seed 42), eig range [-1.9833, 1.9062] ---
  (a) GLOBAL-MEAN : I5_ks_gue=0.1027  I10_cv=0.5936  I8_brody_q=0.802  (n=99)
  (b) SEMICIRCLE  : I5_ks_gue=0.0681  I10_cv=0.4435  I8_brody_q=1.000  (n=99)
      [canonical-trim x-check] global I5=0.0812 cv=0.5540 | semi I5=0.0627 cv=0.4396
      delta I5_ks_gue (global - semi) = +0.0347  (>0 => global-mean reads FURTHER from GUE)
      delta CV (global - semi)        = +0.1501  (GUE-surmise CV ~= 0.523; global CV inflated toward semicircle if larger)
      -> CORRUPTS: global-mean is measurably further from Wigner-GUE

==============================================================================
CHECK B — phase20/21 JPF_CAP drift materiality (audit FIX-5)
==============================================================================
classification cap=1500 (run_phase21_classification.py:57 JPF_CAP);
calibrators   cap=5000 (run_phase21_calibrators.py:58 JPF_CAP);
phase20 unfold has NO cap (run_phase20_classification.py:56-62).
The cap decimates spacings sp[::sp.size//cap] only when sp.size>cap,
i.e. only windows with more events than the cap are affected.

-- item 1/2: n_events screen (banked classification parquets) --
  phase20: 576 windows | n_events [35727, 1091083] | >1500: 576 | >5000: 576
  phase21: 250 windows | n_events [321, 3751497] | >1500: 146 | >5000: 143
  phase20: all windows are far above the cap; but phase20's deployed
           unfold applies NO cap, so the 1500-vs-5000 drift is absent
           from its banked result (tested below as uncapped vs cap).
  MATERIALITY: 146 phase21 windows exceed 1500 -> decimation happens; proceed to re-run.

-- item 3: phase21 re-run at cap=1500 vs cap=5000 (affected windows) --
  affected windows re-run: 146
  n_events reconstruction mismatch (>1 off banked): 0/146
  quadrant CHANGES cap1500 vs cap5000: 3/146
  quadrant differs from banked (cap1500 re-run vs banked primary): 0/146
  windows changing quadrant (1500 vs 5000):
    GRB230307A @26s n=77020 bank=BL cap1500=BL cap5000=TR
    GRB230307A @28s n=82047 bank=BL cap1500=BL cap5000=TR
    GRB221009A @180s n=712547 bank=BL cap1500=BL cap5000=TR
  banked primary among affected: {'BL': np.int64(121), 'TR': np.int64(19), 'BR_artifact': np.int64(6)}

-- phase20 re-run: uncapped (deployed) vs cap=1500 vs cap=5000 --
  (deployed phase20 = uncapped; its banked 'primary' IS the uncapped
   result, so we use banked as the uncapped reference and only recompute
   the capped variants — recomputing uncapped on full 35k-1M-event windows
   is what the deployed run already did.)
  NOTE: phase20 classify is Q_MAX=60 over ~1500/5000 capped points; the full
  576-window x 2-cap grid is O(hours). This is a bounded STRATIFIED SAMPLE
  (SAMPLE_PER_COLLECTOR windows evenly spaced in time per collector) — a
  materiality screen, not exhaustive.
  phase20 windows re-run (well-powered, capped variants only): 64
  quadrant CHANGES cap1500 vs cap5000: 0/64
  quadrant CHANGES banked-uncapped vs cap1500: 0/64
  (no phase20 window changes quadrant across uncapped/1500/5000)

```

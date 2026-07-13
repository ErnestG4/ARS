# VERDICT B — POSITIVE DATA-ROOT AUDIT

**Every filesystem root the repo declares, TOUCHED.** Not grepped for a pattern — resolved.

## **DENOMINATOR: 50 roots enumerated. 48 resolve. 2 DO NOT.**

| file:line | constant | raw | status | detail |
|---|---|---|---|---|
| `internaldocs/make_onepager.py:7` | `OUT` | `/home/combust/fmexplorer/criticality_tool/phase37/CRCNS_SUMMARY_1PAGE.pdf` | **DEAD** | does not exist: /home/combust/fmexplorer/criticality_tool/phase37/CRCNS_SUMMARY_1PAGE.pdf |
| `cross_substrate/crcns_fetch.py:12` | `RAW` | `$HOME/fmexplorer/crcns_cache/raw` | **EMPTY** | dir exists but is EMPTY: /home/combust/fmexplorer/crcns_cache/raw |

<details><summary>All roots (full table)</summary>

| file:line | constant | status | detail |
|---|---|---|---|
| `approximability/panel_C.py:18` | `_ROOT` | OK | 191 entries, 23954 MB |
| `approximability/task3_d3_windowscaling.py:14` | `MATHTEST` | OK | 14 entries, 248 MB |
| `cross_substrate/allen_avalanche.py:38` | `CACHE` | OK | 26 entries, 30844 MB |
| `cross_substrate/allen_depth.py:52` | `CACHE` | OK | 26 entries, 30844 MB |
| `cross_substrate/allen_depth_spatial.py:31` | `CACHE` | OK | 26 entries, 30844 MB |
| `cross_substrate/allen_hpf.py:46` | `CACHE` | OK | 26 entries, 30844 MB |
| `cross_substrate/allen_osi_gap.py:42` | `NWB_GLOB` | OK | 12 files |
| `cross_substrate/brocot_approximability.py:41` | `_BROCOT` | OK | 18 entries, 35660 MB |
| `cross_substrate/brocot_audio_harness.py:35` | `_BROCOT` | OK | 18 entries, 35660 MB |
| `cross_substrate/brocot_landscape.py:27` | `_BROCOT` | OK | 18 entries, 35660 MB |
| `cross_substrate/brocot_landscape.py:112` | `rf` | OK | 25 entries, -0 MB |
| `cross_substrate/buzsaki_placefields.py:38` | `BUZ_GLOB` | OK | 8 files |
| `cross_substrate/buzsaki_port.py:43` | `BUZ_GLOB` | OK | 8 files |
| `cross_substrate/buzsaki_selectivity.py:33` | `BUZ_GLOB` | OK | 8 files |
| `cross_substrate/buzsaki_swr.py:40` | `BUZ_GLOB` | OK | 8 files |
| `cross_substrate/buzsaki_thetagamma.py:42` | `BUZ_GLOB` | OK | 8 files |
| `cross_substrate/crcns_fetch.py:14` | `SESS` | OK | 20 entries, 509 MB |
| `cross_substrate/hc3_instrument_pass.py:36` | `CACHE` | OK | 4 entries, 657 MB |
| `cross_substrate/hc3_port.py:48` | `SESS_ROOT` | OK | 20 entries, 509 MB |
| `cross_substrate/hc3_port.py:50` | `META` | OK | file, 0.6 MB |
| `cross_substrate/hc3_port.py:51` | `SESS_META` | OK | file, 0.0 MB |
| `cross_substrate/ibl_port.py:42` | `IBL_GLOB` | OK | 8 files |
| `cross_substrate/longrange_allen_audit.py:43` | `NWB_GLOB` | OK | 12 files |
| `cross_substrate/longrange_allen_psth_audit.py:32` | `NWB_GLOB` | OK | 12 files |
| `cross_substrate/longrange_neural_audit.py:36` | `root` | OK | 20 entries, 509 MB |
| `cross_substrate/ret1_port.py:40` | `DATA` | OK | 16 entries, 34 MB |
| `cross_substrate/ret1_rf.py:30` | `RET` | OK | 5 entries, 72 MB |
| `cross_substrate/ret1_surrogate.py:39` | `DATA` | OK | 16 entries, 34 MB |
| `phase22a/loader.py:30` | `PVC11_ROOT` | OK | 13 entries, 247 MB |
| `phase24/loader.py:47` | `ALLEN_CACHE` | OK | 26 entries, 30844 MB |
| `phase24/run_meta_analysis.py:33` | `CV_PATH` | OK | file, 0.0 MB |
| `phase24/run_meta_analysis.py:36` | `FUNC_PATH` | OK | file, 0.1 MB |
| `phase24/run_meta_analysis.py:37` | `OUT_DIR` | OK | 31 entries, 2 MB |
| `phase24/run_per_session_h1.py:37` | `CANDIDATE_PATH` | OK | file, 0.0 MB |
| `phase24/run_per_session_h2.py:42` | `CANDIDATE_PATH` | OK | file, 0.0 MB |
| `phase24/run_per_session_h2.py:45` | `RATE_MATCHED_PATH` | OK | file, 0.0 MB |
| `phase24/run_per_session_h2.py:46` | `OUT_DIR` | OK | 31 entries, 2 MB |
| `phase24/run_sensitivity_grid.py:37` | `CANDIDATE_PATH` | OK | file, 0.0 MB |
| `phase31b/allen_full_12session_padic.py:43` | `CANDIDATE_CSV` | OK | file, 0.0 MB |
| `phase31b/p7_content_vs_rate_check.py:19` | `OUT_DIR` | OK | 58 entries, 2 MB |
| `phase33a/pilot_ars_runs.py:29` | `ROOT` | OK | 191 entries, 23954 MB |
| `phase33a/pilot_direct_stats.py:33` | `ROOT` | OK | 191 entries, 23954 MB |
| `phase33b/pilot_mass_spectrum.py:38` | `ROOT` | OK | 191 entries, 23954 MB |
| `phase34d/run_rw_variance_direct.py:60` | `OUT_DIR` | OK | 7 entries, 0 MB |
| `phase34e/maass_loader.py:37` | `PHASE34E_DATA` | OK | 33214 entries, 3453 MB |
| `phase37/crcns_pillar2.py:18` | `ROOT` | OK | 191 entries, 23954 MB |
| `phase37/crcns_pillar2_ratematch.py:18` | `ROOT` | OK | 191 entries, 23954 MB |
| `phase38/ladder_burst_reliability.py:101` | `SESS` | OK | 20 entries, 509 MB |
| `cross_substrate/crcns_fetch.py:12` | `RAW` | EMPTY | dir exists but is EMPTY: /home/combust/fmexplorer/crcns_cache/raw |
| `internaldocs/make_onepager.py:7` | `OUT` | DEAD | does not exist: /home/combust/fmexplorer/criticality_tool/phase37/CRCNS_SUMMARY_1PAGE.pdf |

</details>
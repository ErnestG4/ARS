# VERDICT D — SILENT DROPS (an unlogged exclusion is an ABSENCE)

**Any filter that drops a cell/session/dataset without logging the count converts an**
**exclusion into an absence.** The output then looks like a complete analysis of a smaller
population. `Path('$HOME/...')` was one instance of this class; `except: continue` around a
loader is the same disease with better manners.

## **DENOMINATOR: 482 .py files. 70 silent `except→pass/continue` handlers.**

| file | line | shape | context |
|---|---|---|---|
| `run_pair_correlation.py` | 81 | `except→pass/continue` | `except Exception:` |
| `run_phase18_finding_validation.py` | 180 | `except→pass/continue` | `except Exception:` |
| `run_phase17_arch_invariance.py` | 99 | `except→pass/continue` | `except Exception:` |
| `run_phase17_arch_invariance.py` | 200 | `except→pass/continue` | `except Exception:` |
| `extractor_distinctness.py` | 202 | `except→pass/continue` | `except Exception:` |
| `as_topology.py` | 93 | `except→pass/continue` | `except ValueError:` |
| `run_second_order.py` | 122 | `except→pass/continue` | `except Exception:` |
| `run_phase11_retry.py` | 139 | `except→pass/continue` | `except Exception: pass` |
| `run_phase11_retry.py` | 102 | `except→pass/continue` | `except Exception: pass` |
| `run_phase9.py` | 86 | `except→pass/continue` | `except Exception:` |
| `run_phase15_cross_signal.py` | 173 | `except→pass/continue` | `except Exception:` |
| `run_phase10_llm.py` | 131 | `except→pass/continue` | `except Exception:` |
| `run_earthquake_nns.py` | 63 | `except→pass/continue` | `except Exception:` |
| `run_phase11_models.py` | 127 | `except→pass/continue` | `except Exception: pass` |
| `run_phase11_models.py` | 91 | `except→pass/continue` | `except Exception: pass` |
| `bgp_pipeline.py` | 189 | `except→pass/continue` | `except ValueError:` |
| `bgp_pipeline.py` | 195 | `except→pass/continue` | `except ValueError:` |
| `bgp_pipeline.py` | 238 | `except→pass/continue` | `except (TypeError, ValueError):` |
| `bgp_pipeline.py` | 242 | `except→pass/continue` | `except (TypeError, ValueError):` |
| `bgp_pipeline.py` | 323 | `except→pass/continue` | `except Exception:` |
| `bgp_pipeline.py` | 367 | `except→pass/continue` | `except Exception:` |
| `run_dirichlet_family.py` | 91 | `except→pass/continue` | `except Exception as e:` |
| `run_dirichlet_family.py` | 104 | `except→pass/continue` | `except Exception:` |
| `run_morning_summary.py` | 256 | `except→pass/continue` | `except Exception:` |
| `run_morning_summary.py` | 194 | `except→pass/continue` | `except StopIteration:` |
| `phase37/llm_quant_extract.py` | 98 | `except→pass/continue` | `except Exception:` |
| `phase37/llm_quant_reaudit.py` | 31 | `except→pass/continue` | `except KeyError:` |
| `phase37/set3_discriminator.py` | 72 | `except→pass/continue` | `except Exception:` |
| `phase37/crcns_pillar2.py` | 37 | `except→pass/continue` | `except Exception: pass` |
| `phase37/calibrator_family_map.py` | 36 | `except→pass/continue` | `except Exception:` |
| `phase37/reaudit_summary.py` | 51 | `except→pass/continue` | `except Exception:` |
| `phase37/crcns_pillar2_ratematch.py` | 65 | `except→pass/continue` | `except Exception: pass` |
| `phase32b/per_cell_decomposition.py` | 265 | `except→pass/continue` | `except Exception:` |
| `phase35a/zoo_gap_recheck.py` | 57 | `except→pass/continue` | `except Exception:` |
| `phase35a/tier2_sup_L_extend_N50k.py` | 240 | `except→pass/continue` | `except Exception: pass` |
| `phase35a/test2_sup_L_extend.py` | 268 | `except→pass/continue` | `except Exception:` |
| `phase35a/tier2_sup_L_extend_N100k.py` | 265 | `except→pass/continue` | `except Exception: pass` |
| `phase34d/run_x_rate_scan.py` | 143 | `except→pass/continue` | `except Exception:` |
| `cross_substrate/allen_depth_fam2.py` | 64 | `except→pass/continue` | `except Exception:` |
| `cross_substrate/allen_depth.py` | 169 | `except→pass/continue` | `except Exception:` |
| `cross_substrate/goes_flares.py` | 119 | `except→pass/continue` | `except Exception:                      # noqa: BLE001` |
| `cross_substrate/comcat_port.py` | 61 | `except→pass/continue` | `except Exception:                         # noqa: BLE001` |
| `cross_substrate/allen_depth_spatial.py` | 56 | `except→pass/continue` | `except json.JSONDecodeError:` |
| `cross_substrate/allen_fam2_analysis.py` | 35 | `except→pass/continue` | `except json.JSONDecodeError:` |
| `cross_substrate/population_fingerprint.py` | 155 | `except→pass/continue` | `except Exception:` |
| `cross_substrate/attractor_analysis.py` | 47 | `except→pass/continue` | `except Exception:` |
| `cross_substrate/brocot_approximability.py` | 90 | `except→pass/continue` | `except Exception:` |
| `cross_substrate/allen_depth_analysis.py` | 44 | `except→pass/continue` | `except json.JSONDecodeError:` |
| `cross_substrate/population_strat_analysis.py` | 159 | `except→pass/continue` | `except Exception:` |
| `cross_substrate/population_strat.py` | 146 | `except→pass/continue` | `except Exception:` |
| `cross_substrate/chialvo_run.py` | 109 | `except→pass/continue` | `except Exception:` |
| `cross_substrate/brocot_landscape.py` | 58 | `except→pass/continue` | `except Exception:` |
| `phase36/kuramoto_clustering_recheck.py` | 47 | `except→pass/continue` | `except Exception:` |
| `phase36/falsification_calibrator.py` | 59 | `except→pass/continue` | `except Exception:` |
| `phase36/kaneko_gcm.py` | 98 | `except→pass/continue` | `except Exception:` |
| `phase36/track4_frontend.py` | 113 | `except→pass/continue` | `except Exception:` |
| `phase36/kuramoto_snapshot_repulsion.py` | 68 | `except→pass/continue` | `except Exception:` |
| `phase31b/padic_v4_sweep.py` | 144 | `except→pass/continue` | `except Exception:` |
| `phase27/analysis1_f1f0_rate_matched.py` | 189 | `except→pass/continue` | `except ValueError:` |
| `phase27/analysis2_ars_vs_fa.py` | 232 | `except→pass/continue` | `except Exception:` |
| … | | | *(10 more)* |

## Loader n_in/n_used logging — **DENOMINATOR: 13 loaders**

**2 log a count. 11 DO NOT.**

| loader | logs n_in / n_used? |
|---|---|
| `phase34f_cohh/bianchi_data_loader.py` | **NO** |
| `cross_substrate/ibl_port.py` | **NO** |
| `cross_substrate/comcat_port.py` | **NO** |
| `cross_substrate/ret1_port.py` | **NO** |
| `cross_substrate/hc3_port.py` | **NO** |
| `cross_substrate/allen_hpf.py` | **NO** |
| `cross_substrate/dual_region_port.py` | **NO** |
| `cross_substrate/buzsaki_port.py` | **NO** |
| `phase34f/zomega_loader.py` | **NO** |
| `phase22a/loader.py` | **NO** |
| `phase34e/maass_loader.py` | **NO** |
| `phase24/loader.py` | yes |
| `cross_substrate/harvest.py` | yes |
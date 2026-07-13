# VERDICT 0 — THE CANARY

**An instrument that cannot fail cannot pass.** Two deliberately dead roots were planted
(one `$HOME`-literal, one `~`-literal) and the sweep run against them.

**Planted: 2. Detected: 2.**

| constant | raw | status | detail |
|---|---|---|---|
| `CANARY_DEAD_ROOT` | `$HOME/fmexplorer/THIS_DOES_NOT_EXIST_canary` | **DEAD** | does not exist: /home/combust/fmexplorer/THIS_DOES_NOT_EXIST_canary |
| `CANARY_TILDE_ROOT` | `~/fmexplorer/ALSO_DOES_NOT_EXIST_canary` | **DEAD** | does not exist: /home/combust/fmexplorer/ALSO_DOES_NOT_EXIST_canary |

## GATE: **PASS** — the sweep fires on known-dead roots. Its clean results are interpretable.
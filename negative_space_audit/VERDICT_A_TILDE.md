# VERDICT A — THE TILDE SIBLING (and other non-expanding path idioms)

`Path('$HOME/...')` doesn't expand. **`Path('~/...')` doesn't expand either** — same failure,
same silence, different string. **No `$HOME` grep would have caught it.**

**DENOMINATOR: 482 .py files scanned. 5 idiom hits. 5 UNWRAPPED.**

| file | line | idiom | context |
|---|---|---|---|
| `phase24/run_sensitivity_grid.py` | 105 | f-string with $HOME | `nwb_path = Path(f'$HOME/fmexplorer/allen_cache/session_{sid}/session_{sid}.nwb')` |
| `phase24/run_per_session_h2.py` | 162 | f-string with $HOME | `nwb_path = Path(f'$HOME/fmexplorer/allen_cache/session_{sid}/session_{sid}.nwb')` |
| `phase24/run_per_session_h2.py` | 318 | f-string with $HOME | `nwb_path = Path(f'$HOME/fmexplorer/allen_cache/session_{sid}/session_{sid}.nwb')` |
| `phase24/run_per_session_h1.py` | 45 | f-string with $HOME | `nwb_path = Path(f'$HOME/fmexplorer/allen_cache/session_{sid}/session_{sid}.nwb')` |
| `phase24/run_per_session_h1.py` | 115 | f-string with $HOME | `nwb_path = Path(f'$HOME/fmexplorer/allen_cache/session_{sid}/session_{sid}.nwb')` |
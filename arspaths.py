"""arspaths — the single source of truth for every data root in ARS.

WHY THIS EXISTS
---------------
Commit 95b2324 ("Repo hygiene: de-identify hardcoded $HOME paths", 72 files) find-replaced a
literal home path -> `$HOME` **without wrapping anything in expandvars**. The intent was correct —
don't publish a home directory to codeberg.org/Combust/ARS. The execution was one function call
short, in 72 files.

The reason it went undetected for six weeks is subtle and worth stating: **a scrubbed path and a
dead path are the same string.** An audit reading `Path('$HOME/...')` cannot tell "intentionally
redacted" from "broken". So the 2026-06-30 truth audit fixed one instance, read it as cosmetic, and
moved on. The silence was not negligence — it was *ambiguity by construction*.

And the failure mode made it worse: `if not path.exists(): print("NWB not ready; skip"); continue`
— **a scrub that fails politely.** pvc-11's 416 MB of raw V1 sat unreachable for six weeks and cost
two claims when it finally came back.

THE FIX (two rules, and they close the class rather than the instances)
----------------------------------------------------------------------
1. **De-identify at the BOUNDARY, not in the working tree.**  Source references a *name*
   (`ARS_DATA_ROOT`), never a location. There is nothing to scrub, so nothing to break.
2. **FAIL LOUDLY at the root.**  A missing root raises. It does not print, skip, continue, or
   return None. If a root had thrown on day one, none of the above would have happened.

USAGE
-----
    from arspaths import root, data
    CACHE    = data("allen_cache")          # raises if absent
    NWB_GLOB = data("allen_cache", "session_*", "session_*.nwb", must_exist=False)

CONFIG (first hit wins)
-----------------------
    1. env  ARS_DATA_ROOT=/path/to/fmexplorer
    2. ./paths.toml           (gitignored; copy from paths.example.toml)
    3. $HOME/fmexplorer       (the historical default; still de-identified in source)
"""
from __future__ import annotations

import os
from pathlib import Path

_CACHED: Path | None = None


class DataRootError(RuntimeError):
    """A data root is missing or unconfigured. RAISED — never printed and skipped."""


def _from_toml() -> str | None:
    p = Path(__file__).resolve().parent / "paths.toml"
    if not p.is_file():
        return None
    try:
        import tomllib
        with p.open("rb") as f:
            return tomllib.load(f).get("data_root")
    except Exception as e:                                    # loud, not silent
        raise DataRootError(f"paths.toml exists but could not be parsed: {e}") from e


def root() -> Path:
    """The ARS data root. RAISES if it cannot be resolved — never returns a broken path."""
    global _CACHED
    if _CACHED is not None:
        return _CACHED

    src = "env ARS_DATA_ROOT"
    raw = os.environ.get("ARS_DATA_ROOT")
    if not raw:
        raw, src = _from_toml(), "paths.toml"
    if not raw:
        raw, src = os.path.expandvars("$HOME/fmexplorer"), "default $HOME/fmexplorer"

    p = Path(os.path.expandvars(os.path.expanduser(str(raw))))
    if "$" in str(p) or str(p).startswith("~"):
        raise DataRootError(
            f"data root did not expand: {p!r} (from {src}).\n"
            "  This is the 95b2324 bug: a de-identified string that was never expanded.\n"
            "  Set ARS_DATA_ROOT, or create paths.toml from paths.example.toml.")
    if not p.is_dir():
        raise DataRootError(
            f"ARS data root does not exist: {p}  (from {src})\n"
            "  Set ARS_DATA_ROOT=/path/to/fmexplorer, or copy paths.example.toml -> paths.toml.\n"
            "  (Raising, not skipping. A root that fails politely is how pvc-11 went missing for six weeks.)")
    _CACHED = p
    return p


def data(*parts: str, must_exist: bool = True) -> Path:
    """A path under the data root. RAISES if it is absent (unless must_exist=False, for globs)."""
    p = root().joinpath(*parts)
    if must_exist and not p.exists():
        raise DataRootError(
            f"required data path is missing: {p}\n"
            "  (Raising, not skipping. If this is a legitimately absent dataset, the CALLER must\n"
            "   say so explicitly and log the denominator — an unlogged exclusion is an absence.)")
    return p


def venv_python() -> Path:
    return root() / "bin" / "python3"

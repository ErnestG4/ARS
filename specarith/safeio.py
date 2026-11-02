# SPDX-License-Identifier: AGPL-3.0-or-later
"""safeio — TOOLKIT §9.I (Will, 2026-11-02): lead and diagnostic scripts open committed results read-only and write
only to scratch, enforced in code.

Usage, first lines of a lead / diagnostic script:

    import safeio; safeio.enforce()          # from here on, every write outside scratch raises
    data = safeio.read_json(path, expect_sha256=None)   # read-only; optional pin
    safeio.write_json(safeio.scratch("fn1/x.json"), obj)

What enforce() does (process-wide, irreversible for the process):
- wraps builtins.open / io.open: any mode containing w, a, x or + is allowed only if the resolved path (realpath,
  so symlinks cannot escape) is under a scratch root AND not inside a git work tree;
- wraps os.replace / os.rename (destination), os.remove / os.unlink, shutil is covered through open + os.replace;
- read modes are always allowed.

Scratch roots: $SPECARITH_SCRATCH (os.pathsep-separated) if set, else ~/tmp/claude. Results that belong in the repo
are copied there by an explicit, separate step (cp + git add), never written by the script.
Not covered (documented limits): os.open with raw flags, subprocess writes, C extensions writing by path.
"""
import builtins
import hashlib
import io
import json
import os

_ENFORCED = False
_orig = {}


def scratch_roots():
    env = os.environ.get("SPECARITH_SCRATCH")
    roots = env.split(os.pathsep) if env else [os.path.expanduser("~/tmp/claude")]
    return [os.path.realpath(r) for r in roots if r]


def _in_git_tree(p):
    d = os.path.dirname(p)
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return True
        nd = os.path.dirname(d)
        if nd == d:
            return False
        d = nd


def check_write(path):
    if isinstance(path, int):
        raise PermissionError("safeio: write to a raw file descriptor is not allowed under enforce()")
    p = os.path.realpath(os.fspath(path))
    if not any(p == r or p.startswith(r + os.sep) for r in scratch_roots()):
        raise PermissionError(f"safeio: write outside scratch refused: {p} (roots {scratch_roots()})")
    if _in_git_tree(p):
        raise PermissionError(f"safeio: write inside a git work tree refused: {p}")
    return p


def scratch(rel):
    """Path under the first scratch root; parent directories are created."""
    p = os.path.join(scratch_roots()[0], rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return check_write(p)


def _is_write_mode(mode):
    return any(c in mode for c in "wax+")


def enforce():
    global _ENFORCED
    if _ENFORCED:
        return
    _orig.update(open=builtins.open, io_open=io.open, replace=os.replace, rename=os.rename, remove=os.remove,
                 unlink=os.unlink)

    def guarded_open(file, mode="r", *a, **k):
        if _is_write_mode(mode):
            check_write(file)
        return _orig["open"](file, mode, *a, **k)

    def guarded_replace(src, dst, *a, **k):
        check_write(dst)
        return _orig["replace"](src, dst, *a, **k)

    def guarded_rename(src, dst, *a, **k):
        check_write(dst)
        return _orig["rename"](src, dst, *a, **k)

    def guarded_remove(path, *a, **k):
        check_write(path)
        return _orig["remove"](path, *a, **k)

    builtins.open = guarded_open
    io.open = guarded_open
    os.replace = guarded_replace
    os.rename = guarded_rename
    os.remove = guarded_remove
    os.unlink = guarded_remove
    _ENFORCED = True


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def read_json(path, expect_sha256=None):
    if expect_sha256 is not None and sha256_file(path) != expect_sha256:
        raise AssertionError(("safeio: pinned input mismatch", path))
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, obj, overwrite=False):
    p = check_write(path)
    if os.path.exists(p) and not overwrite:
        raise FileExistsError(f"safeio: refusing to overwrite {p} (pass overwrite=True)")
    with open(p, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    return p

"""
propagation_watch.py — the fourth watcher. Fires on RIGHT results filed where they cannot act.

THE DEFECT IT WATCHES, and it is the most-attested in the repo with SIX instances and, until now,
no guard at all:

    A fix is written, validated, used to overturn a claim -- and lands in an analysis script or an
    overnight directory instead of the shared module the deployed path imports. The deployed path
    keeps the broken version. Nobody notices, because nothing is wrong with the fix.

The other three watchers guard against WRONG results (commensurability, degeneracy, backlog decay).
This one guards against RIGHT results that cannot fire. Instance 5 was `irep_unclipped` (signed
I_rep, built 2026-07-12, propagated 2026-07-27 after a fresh session rebuilt it from scratch).
Instance 6 was `brody_unbounded`, from THE SAME NIGHT, still unpropagated when this watcher was
written -- which is the argument for the watcher in one sentence.

THREE MECHANICAL SIGNATURES
  A  a leaf module imports a PRIVATE symbol (`_foo`) from a shared module. The public API did not
     offer what was needed, which usually means someone wrapped it locally instead of fixing it.
  B  repair language ("the repair", "fixed", "corrected", "proper", "unclipped", "unbounded") in a
     docstring or comment OUTSIDE the shared modules.
  C  a leaf module defines a function whose name is a REPAIR VARIANT of a shared-module function
     (`X_unclipped`, `X_unbounded`, `X_fixed`, `X_v2`, `X_proper`, ...).

A hit is a CANDIDATE, not a verdict. Each must be resolved in the manifest as
`propagated` | `local-by-design` | `not-a-repair`, with a reason. Ratcheted like the migration
checker: fires on INCREASE, so a static backlog does not train anyone to ignore it.

Usage:  python3 propagation_watch.py [--summary]
"""
from __future__ import annotations
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "propagation_watch_manifest.json")
p_ = lambda *a: print(*a, flush=True)

# "Shared" is MEASURED, not guessed. My first hand-curated list omitted `ars_classify.py`
# (imported by 51 modules) and `unfold_rotnum.py` (33) -- so the watcher was under-scoped and
# would have called a repair landing in either of them "unpropagated" when it had in fact reached
# the deployed path for dozens of consumers. A module imported by >= SHARED_MIN others IS shared,
# whatever anyone intended it to be.
SHARED_MIN = 8
_SHARED_SEED = {"arithmetic_toolkit.py", "universality.py", "extractors.py", "signal_gen.py",
                "intermittency.py", "commensurable.py", "axes.py", "bulk_recovery.py"}


_SHARED_CACHE = os.path.join(HERE, ".propagation_shared_cache.json")


def _measure_shared():
    import collections
    if os.path.exists(_SHARED_CACHE):
        try:
            return set(json.load(open(_SHARED_CACHE)))
        except Exception:
            pass
    out = subprocess.run(["git", "ls-files", "*.py"], capture_output=True, text=True,
                         cwd=HERE).stdout.split()
    names = {os.path.splitext(os.path.basename(p))[0]: os.path.basename(p) for p in out}
    n = collections.Counter()
    for p in out:
        try:
            txt = open(os.path.join(HERE, p)).read()
        except Exception:
            continue
        for stem, base in names.items():
            if base == os.path.basename(p):
                continue
            if re.search(rf"^\s*(from\s+[\w.]*\b{re.escape(stem)}\s+import|import\s+{re.escape(stem)}\b)",
                         txt, re.M):
                n[base] += 1
    out_set = _SHARED_SEED | {b for b, c in n.items() if c >= SHARED_MIN}
    json.dump(sorted(out_set), open(_SHARED_CACHE, "w"))
    return out_set


SHARED = None  # populated at scan time

# SPECIFICITY: the first draft matched "bounded"/"unbounded"/"proper" as MATHEMATICAL terms
# (bounded CF, unbounded partial quotients, proper dimension) and returned 41 hits, mostly false.
# A watcher with a mostly-false hit list is the alarm-fatigue failure it exists to prevent, so
# signature B is restricted to phrases that can ONLY mean a repair. Precision over recall here:
# signatures A and C carry the recall, and both are structural rather than lexical.
REPAIR_WORD = re.compile(
    r"\b(the repair|the fix\b|repaired version|fixed version|was wrong|is wrong|"
    r"bug in|unclipped|previously banked|now superseded)\b", re.I)
# RECALL LIMIT, recorded rather than papered over: signature C is a FIXED suffix list, so it only
# catches repairs named with suffixes I thought of. It MISSED my own 2026-07-27 repairs
# (`_value_trimmed`, `_windowed`, `_railaware`) until they were added below. A lexical signature
# has bounded recall by construction; A (private imports) and B (repair phrasing) are the structural
# ones, and the manifest is what carries anything all three miss.
VARIANT = re.compile(
    r"^\s*def\s+(\w+?)(_unclipped|_unbounded|_fixed|_corrected|_proper|_signed|_v2|_repaired"
    r"|_value_trimmed|_windowed|_railaware|_nonclamped)\b")
PRIVATE_IMPORT = re.compile(r"^\s*from\s+([\w.]+)\s+import\s+(.*)")


def _sh(*args):
    return subprocess.run(args, capture_output=True, text=True, cwd=HERE).stdout


def scan():
    global SHARED
    if SHARED is None:
        SHARED = _measure_shared()
    files = [f for f in _sh("git", "ls-files", "*.py").strip().split("\n") if f]
    shared_defs = {}
    for f in files:
        if os.path.basename(f) in SHARED:
            for m in re.finditer(r"^def\s+(\w+)", open(os.path.join(HERE, f)).read(), re.M):
                shared_defs.setdefault(m.group(1), f)
    hits = []
    for f in files:
        base = os.path.basename(f)
        if base in SHARED or base in ("propagation_watch.py",):
            continue
        try:
            lines = open(os.path.join(HERE, f)).read().split("\n")
        except Exception:
            continue
        for i, ln in enumerate(lines, 1):
            m = PRIVATE_IMPORT.match(ln)
            if m and os.path.basename(m.group(1).split(".")[-1] + ".py") in SHARED:
                # SPECIFICITY, third pass on this watcher: an INTRA-package private import is
                # ordinary internal reuse (cross_substrate/allen_hpf <- cross_substrate/
                # population_fingerprint), not a public-API gap. Only a CROSS-package private
                # import carries the "the public API didn't offer it" signal. Widening SHARED from
                # 8 hand-picked modules to 27 measured ones exposed this: hits went 5 -> 27, almost
                # all intra-package.
                src_pkg = f.split("/")[0] if "/" in f else ""
                dst_pkg = m.group(1).split(".")[0] if "." in m.group(1) else ""
                if src_pkg and dst_pkg and src_pkg == dst_pkg:
                    pass
                else:
                    priv = [x.strip() for x in m.group(2).split(",") if x.strip().startswith("_")]
                    if priv:
                        hits.append((f, i, "A private-import",
                                     f"{', '.join(priv)} from {m.group(1)}"))
            v = VARIANT.match(ln)
            if v:
                stem = v.group(1)
                where = shared_defs.get(stem) or next(
                    (p for n, p in shared_defs.items() if n.endswith(stem) or stem in n), None)
                hits.append((f, i, "C repair-variant",
                             f"def {stem}{v.group(2)}  (shared stem: {where or 'none found'})"))
            if REPAIR_WORD.search(ln) and ('"""' in ln or ln.lstrip().startswith("#")):
                hits.append((f, i, "B repair-language", ln.strip()[:70]))
    return hits


if __name__ == "__main__":
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {"resolved": {}}
    hits = scan()
    cats = {"propagated": [], "local-by-design": [], "not-a-repair": [],
            "documented-open": [], "UNRESOLVED": []}
    for f, ln, sig, detail in hits:
        cats[man["resolved"].get(f"{f}:{ln}", "UNRESOLVED")].append((f, ln, sig, detail))

    p_("=== propagation watch — right results filed where they cannot fire ===")
    for k in ("propagated", "local-by-design", "not-a-repair", "documented-open", "UNRESOLVED"):
        p_(f"  {k:>16s}: {len(cats[k]):>3d}")
    if "--summary" not in sys.argv and cats["UNRESOLVED"]:
        p_(f"\n  UNRESOLVED candidates ({len(cats['UNRESOLVED'])}):")
        for f, ln, sig, detail in cats["UNRESOLVED"][:20]:
            p_(f"    [{sig:<17s}] {f}:{ln}")
            p_(f"        {detail}")

    n = len(cats["UNRESOLVED"])
    hw = man.get("high_water")
    if hw is None:
        hw = n
    regress = n > hw
    p_(f"\n  unresolved = {n}, high-water = {hw} (moves DOWN only)")
    if regress:
        p_("  *** REGRESSION *** a new candidate un-propagated repair appeared.")
    else:
        if n < hw or "high_water" not in man:
            man["high_water"] = n
            json.dump(man, open(MANIFEST, "w"), indent=2)
            p_(f"  ratcheted to {n}.")
        p_("  NO REGRESSION — tracked backlog, not a permanent red light.")
    sys.exit(1 if regress else 0)

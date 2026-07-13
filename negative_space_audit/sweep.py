#!/usr/bin/env python3
"""NEGATIVE-SPACE AUDIT — 2026-07-12.

DESIGN PRINCIPLE (the whole point):
    DO NOT GREP FOR THE BUG. ENUMERATE THE RESOURCES AND ASSERT EACH ONE RESOLVES.

Grepping for `$HOME` finds the disease we already know — a change of PARAMETER, certifying the
pattern, not the health. This sweep is POSITIVE-ASSERTION: for every dataset, path and resource the
project believes it HAS or believes it LACKS, go touch it and record what is actually there.

Categories:
  0  CANARY      — plant a deliberately dead root; the sweep MUST fire on it. An instrument that
                   cannot fail cannot pass. (Job B's lesson, applied to the sweep itself.)
  A  TILDE       — Path('~/...') doesn't expand either. Same silence, different string; no $HOME grep
                   would have caught it.
  B  DATA ROOTS  — positive audit of every root: exists / is_dir / non-empty / readable. DENOMINATOR.
  C  ABSENCE     — every prose claim of absence ("remote-streamed", "not available"...) checked
                   AGAINST THE DISK. The claim is a hypothesis; the disk is the measurement.
  D  SILENT DROP — filters that exclude a cell/session/dataset WITHOUT LOGGING THE COUNT. An
                   unlogged exclusion converts a filter into an absence.
  E  DORMANT     — `if False:`, flags defaulting off, gates that never fire.
  F  UN-RUN PREREG — *PREREG*/*PROPOSED*/*BRIEF* with no results file. (Deliberate parks marked
                   PARKED, not MISSING.)

STRUCTURAL RULES: a verdict file per category EVEN WHEN EMPTY; every verdict reports a DENOMINATOR;
every skipped file is logged with a reason. A sweep for silent exclusion that silently excludes is
the joke writing itself.
"""
import os, re, sys, ast, json, glob, time, traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE
SKIPPED = []          # (path, reason) — logged, never silent

PY = [p for p in ROOT.rglob("*.py") if "__pycache__" not in str(p) and "negative_space_audit" not in str(p)]
MD = [p for p in ROOT.rglob("*.md")] + [p for p in ROOT.rglob("*.txt")]


def w(fn, s):
    (OUT / fn).write_text(s)
    print(f"  WROTE {fn}")


def src(p):
    try:
        return p.read_text(errors="replace")
    except Exception as e:
        SKIPPED.append((str(p), f"unreadable: {e}"))
        return ""


# ─────────────────────────────────────────── shared: find every string that looks like a path root
ROOT_RE = re.compile(
    r"""^\s*([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(?:Path\(\s*)?(?:os\.path\.expandvars\(\s*|os\.path\.expanduser\(\s*)?["']([^"']*(?:/|\\)[^"']*)["']""",
    re.M)
FS_HINT = re.compile(r"cache|data|root|dir|path|glob|_file|corpus|store|out", re.I)


def find_roots():
    """Every module-level string constant that looks like a filesystem path."""
    out = []
    for p in PY:
        s = src(p)
        for m in ROOT_RE.finditer(s):
            name, val = m.group(1), m.group(2)
            if not FS_HINT.search(name) and not val.startswith(("/", "~", "$")):
                continue
            if val.startswith(("http", "s3:", "dandi", "{")):
                continue
            line = s[:m.start()].count("\n") + 1
            wrapped = "expandvars" in m.group(0) or "expanduser" in m.group(0)
            out.append(dict(file=str(p.relative_to(ROOT)), line=line, name=name,
                            raw=val, wrapped=wrapped))
    return out


def resolve(raw):
    """The POSITIVE ASSERTION. Returns (status, detail)."""
    p = os.path.expandvars(os.path.expanduser(raw))
    if "$" in p or p.startswith("~"):
        return "UNEXPANDED", f"still contains $ or ~ after expansion: {p}"
    base = p.split("*")[0]
    tgt = Path(base if "*" in p else p)
    if "*" in p:
        hits = glob.glob(p)
        if not Path(base).parent.exists():
            return "DEAD", f"glob parent missing: {base}"
        if not hits:
            return "EMPTY", f"glob resolves to 0 files: {p}"
        return "OK", f"{len(hits)} files"
    if not tgt.exists():
        return "DEAD", f"does not exist: {p}"
    if tgt.is_dir():
        n = sum(1 for _ in tgt.iterdir())
        if n == 0:
            return "EMPTY", f"dir exists but is EMPTY: {p}"
        try:
            sz = sum(f.stat().st_size for f in tgt.rglob("*") if f.is_file())
        except Exception:
            sz = -1
        return "OK", f"{n} entries, {sz/1e6:.0f} MB"
    if not os.access(tgt, os.R_OK):
        return "UNREADABLE", p
    return "OK", f"file, {tgt.stat().st_size/1e6:.1f} MB"


# ─────────────────────────────────────────────────────────────────── CATEGORY 0 — THE CANARY
def cat0():
    canary = HERE / "_canary_probe.py"
    canary.write_text(
        'CANARY_DEAD_ROOT = "$HOME/fmexplorer/THIS_DOES_NOT_EXIST_canary"\n'
        'CANARY_TILDE_ROOT = "~/fmexplorer/ALSO_DOES_NOT_EXIST_canary"\n')
    global PY
    PY.append(canary)
    roots = find_roots()
    hits = [r for r in roots if "canary" in r["raw"].lower()]
    fired = []
    for h in hits:
        st, d = resolve(h["raw"])
        fired.append((h["name"], h["raw"], st, d))
    PY = [p for p in PY if p != canary]
    canary.unlink()

    detected = [f for f in fired if f[2] in ("DEAD", "UNEXPANDED", "EMPTY")]
    ok = len(detected) == 2
    lines = ["# VERDICT 0 — THE CANARY", "",
             "**An instrument that cannot fail cannot pass.** Two deliberately dead roots were planted",
             "(one `$HOME`-literal, one `~`-literal) and the sweep run against them.", "",
             f"**Planted: 2. Detected: {len(detected)}.**", "",
             "| constant | raw | status | detail |", "|---|---|---|---|"]
    for n, raw, st, d in fired:
        lines.append(f"| `{n}` | `{raw}` | **{st}** | {d} |")
    lines += ["", "## GATE: " + ("**PASS** — the sweep fires on known-dead roots. Its clean results are interpretable."
                                 if ok else
                                 "**FAIL — THE SWEEP DID NOT DETECT ITS OWN CANARY. Every result below is UNINTERPRETABLE.**")]
    w("VERDICT_0_CANARY.md", "\n".join(lines))
    return ok


# ─────────────────────────────────────────────────────────── CATEGORY A — THE TILDE SIBLING
def catA():
    pats = [(r"Path\(\s*['\"]~", "Path('~...')"),
            (r"os\.path\.join\(\s*['\"]~", "os.path.join('~'...)"),
            (r"=\s*['\"]~/", "= '~/...'"),
            (r"%HOME%", "%HOME%"),
            (r"\$\{HOME\}", "${HOME}"),
            (r"f['\"][^'\"]*\$HOME", "f-string with $HOME")]
    rows, n_scanned = [], 0
    for p in PY:
        s = src(p)
        if not s:
            continue
        n_scanned += 1
        for rx, lbl in pats:
            for m in re.finditer(rx, s):
                ln = s[:m.start()].count("\n") + 1
                ctx = s.splitlines()[ln - 1].strip()[:90]
                # is it wrapped in an expander on the same line?
                safe = ("expanduser" in ctx) or ("expandvars" in ctx)
                rows.append((str(p.relative_to(ROOT)), ln, lbl, ctx, safe))
    bad = [r for r in rows if not r[4]]
    L = ["# VERDICT A — THE TILDE SIBLING (and other non-expanding path idioms)", "",
         "`Path('$HOME/...')` doesn't expand. **`Path('~/...')` doesn't expand either** — same failure,",
         "same silence, different string. **No `$HOME` grep would have caught it.**", "",
         f"**DENOMINATOR: {n_scanned} .py files scanned. {len(rows)} idiom hits. {len(bad)} UNWRAPPED.**", ""]
    if bad:
        L += ["| file | line | idiom | context |", "|---|---|---|---|"]
        for f, ln, lbl, ctx, _ in bad:
            L.append(f"| `{f}` | {ln} | {lbl} | `{ctx}` |")
    else:
        L.append("**0 findings.** No unwrapped `~`, `%HOME%`, `${HOME}` or f-string-`$HOME` path idioms.")
    w("VERDICT_A_TILDE.md", "\n".join(L))
    return bad


# ────────────────────────────────────────────────── CATEGORY B — POSITIVE DATA-ROOT AUDIT
def catB():
    roots = find_roots()
    seen, rows = set(), []
    for r in roots:
        key = (r["file"], r["line"])
        if key in seen:
            continue
        seen.add(key)
        st, d = resolve(r["raw"])
        rows.append((*[r[k] for k in ("file", "line", "name", "raw", "wrapped")], st, d))
    bad = [x for x in rows if x[5] != "OK"]
    L = ["# VERDICT B — POSITIVE DATA-ROOT AUDIT", "",
         "**Every filesystem root the repo declares, TOUCHED.** Not grepped for a pattern — resolved.", "",
         f"## **DENOMINATOR: {len(rows)} roots enumerated. {len(rows)-len(bad)} resolve. {len(bad)} DO NOT.**", ""]
    if bad:
        L += ["| file:line | constant | raw | status | detail |", "|---|---|---|---|---|"]
        for f, ln, nm, raw, wr, st, d in sorted(bad, key=lambda x: x[5]):
            L.append(f"| `{f}:{ln}` | `{nm}` | `{raw}` | **{st}** | {d} |")
    else:
        L.append("**All declared roots resolve.**")
    L += ["", "<details><summary>All roots (full table)</summary>", "",
          "| file:line | constant | status | detail |", "|---|---|---|---|"]
    for f, ln, nm, raw, wr, st, d in sorted(rows, key=lambda x: (x[5] != "OK", x[0])):
        L.append(f"| `{f}:{ln}` | `{nm}` | {st} | {d} |")
    L += ["", "</details>"]
    w("VERDICT_B_DATAROOTS.md", "\n".join(L))
    return bad


# ──────────────────────────────────── CATEGORY C — ABSENCE CLAIMS IN PROSE, CHECKED VS DISK
ABSENCE = re.compile(
    r"\b(not available|unavailable|no local|no raw|remote-only|remote-streamed|remote streamed|"
    r"acquisition-gated|acquisition gated|can't test|cannot test|not run|un-run|unrun|pending|"
    r"blocked on|TODO|skipped|excluded|missing|no data|N/A)\b", re.I)


def catC():
    rows, n_scanned = [], 0
    for p in MD:
        s = src(p)
        if not s:
            continue
        n_scanned += 1
        for i, line in enumerate(s.splitlines(), 1):
            m = ABSENCE.search(line)
            if m:
                rows.append((str(p.relative_to(ROOT)), i, m.group(1), line.strip()[:150]))
    L = ["# VERDICT C — ABSENCE CLAIMS, CHECKED AGAINST THE DISK", "",
         "**The claim is a hypothesis about the world. The disk is the measurement.**", "",
         f"**DENOMINATOR: {n_scanned} prose files scanned. {len(rows)} absence-claims found.**", "",
         "## Named candidates (checked by hand — see VERDICT_C_NAMED.md)", ""]
    L += ["| file:line | phrase | claim |", "|---|---|---|"]
    for f, ln, ph, ctx in rows[:80]:
        L.append(f"| `{f}:{ln}` | *{ph}* | {ctx.replace('|', '\\|')} |")
    if len(rows) > 80:
        L.append(f"| … | | *({len(rows)-80} more — see absence_claims.json)* |")
    (OUT / "absence_claims.json").write_text(json.dumps(rows, indent=1))
    w("VERDICT_C_ABSENCE.md", "\n".join(L))
    return rows


# ─────────────────────────────────────────────── CATEGORY D — SILENT DROPS (the denominator bug)
def catD():
    rows, n_scanned = [], 0
    for p in PY:
        s = src(p)
        if not s:
            continue
        n_scanned += 1
        try:
            tree = ast.parse(s)
        except SyntaxError as e:
            SKIPPED.append((str(p.relative_to(ROOT)), f"syntax error: {e}"))
            continue
        lines = s.splitlines()
        for node in ast.walk(tree):
            # bare except that swallows and continues/passes
            if isinstance(node, ast.ExceptHandler):
                body = node.body
                if len(body) == 1 and isinstance(body[0], (ast.Pass, ast.Continue)):
                    ln = node.lineno
                    rows.append((str(p.relative_to(ROOT)), ln, "except→pass/continue",
                                 lines[ln - 1].strip()[:80]))
    # does each substrate loader log n_in / n_used?
    loaders = [p for p in PY if re.search(r"port\.py$|_hpf\.py$|loader\.py$|harvest\.py$", str(p))]
    logging_rows = []
    for p in loaders:
        s = src(p)
        has = bool(re.search(r"n_in|n_used|n_events_in|n_events_used|n_dropped|n_excluded", s))
        logging_rows.append((str(p.relative_to(ROOT)), has))
    nolog = [r for r in logging_rows if not r[1]]
    L = ["# VERDICT D — SILENT DROPS (an unlogged exclusion is an ABSENCE)", "",
         "**Any filter that drops a cell/session/dataset without logging the count converts an**",
         "**exclusion into an absence.** The output then looks like a complete analysis of a smaller",
         "population. `Path('$HOME/...')` was one instance of this class; `except: continue` around a",
         "loader is the same disease with better manners.", "",
         f"## **DENOMINATOR: {n_scanned} .py files. {len(rows)} silent `except→pass/continue` handlers.**", ""]
    if rows:
        L += ["| file | line | shape | context |", "|---|---|---|---|"]
        for f, ln, sh, ctx in rows[:60]:
            L.append(f"| `{f}` | {ln} | `{sh}` | `{ctx}` |")
        if len(rows) > 60:
            L.append(f"| … | | | *({len(rows)-60} more)* |")
    L += ["", f"## Loader n_in/n_used logging — **DENOMINATOR: {len(logging_rows)} loaders**", "",
          f"**{len(logging_rows)-len(nolog)} log a count. {len(nolog)} DO NOT.**", "",
          "| loader | logs n_in / n_used? |", "|---|---|"]
    for f, has in sorted(logging_rows, key=lambda x: x[1]):
        L.append(f"| `{f}` | {'yes' if has else '**NO**'} |")
    w("VERDICT_D_SILENTDROP.md", "\n".join(L))
    return rows, nolog


# ─────────────────────────────────────────────────────────────── CATEGORY E — DORMANT GATES
def catE():
    pats = [(r"^\s*if\s+False\s*:", "if False:"), (r"^\s*if\s+0\s*:", "if 0:"),
            (r"enabled\s*=\s*False", "enabled=False"), (r"DISABLED\s*=\s*True", "DISABLED=True"),
            (r"SKIP_[A-Z_]+\s*=\s*True", "SKIP_*=True"),
            (r"^\s*#\s*(if|for|while)\s.*:", "commented-out branch")]
    rows, n = [], 0
    for p in PY:
        s = src(p)
        if not s:
            continue
        n += 1
        for i, line in enumerate(s.splitlines(), 1):
            for rx, lbl in pats:
                if re.search(rx, line):
                    rows.append((str(p.relative_to(ROOT)), i, lbl, line.strip()[:80]))
    hard = [r for r in rows if r[2] != "commented-out branch"]
    L = ["# VERDICT E — DORMANT GATES", "",
         "**A path that exists and never executes is negative space wearing code's clothes.**", "",
         f"## **DENOMINATOR: {n} .py files. {len(hard)} hard-dormant gates "
         f"({len(rows)-len(hard)} commented-out branches, informational).**", ""]
    if hard:
        L += ["| file | line | gate | context |", "|---|---|---|---|"]
        for f, ln, lbl, ctx in hard:
            L.append(f"| `{f}` | {ln} | `{lbl}` | `{ctx}` |")
    else:
        L.append("**0 hard-dormant gates.**")
    w("VERDICT_E_DORMANT.md", "\n".join(L))
    return hard


# ───────────────────────────────────────────────────────── CATEGORY F — UN-RUN PRE-REGISTRATIONS
PARKED = {"PHI_CONTAMINATION_PREREG": "DELIBERATE PARK — rested-instrument job (unattended is worse than tired)",
          "PROPOSED_7TER50_RETROSCOPE": "DELIBERATE PARK — held for Will's eyes; needs re-drafting"}


def catF():
    cand = [p for p in MD if re.search(r"PREREG|PROPOSED|BRIEF", p.name, re.I)]
    rows = []
    for p in cand:
        stem = p.stem
        park = next((v for k, v in PARKED.items() if k in stem), None)
        sibs = list(p.parent.glob("*FINDINGS*")) + list(p.parent.glob("*VERDICT*")) + \
               list(p.parent.glob("*RESULT*"))
        rows.append((str(p.relative_to(ROOT)), len(sibs), park))
    L = ["# VERDICT F — UN-RUN PRE-REGISTRATIONS", "",
         "**Not defects** — the project's own inventory of things it decided to do. But the session has",
         "twice shown that *\"we didn't do that\"* is sometimes *\"we tried and it silently failed.\"*", "",
         f"## **DENOMINATOR: {len(cand)} PREREG/PROPOSED/BRIEF docs.**", "",
         "| doc | result-siblings | status |", "|---|---|---|"]
    for f, ns, park in sorted(rows, key=lambda x: (x[2] is not None, x[1])):
        st = f"**PARKED** — {park}" if park else ("has results" if ns else "**NO RESULTS FILE**")
        L.append(f"| `{f}` | {ns} | {st} |")
    w("VERDICT_F_PREREG.md", "\n".join(L))
    return rows


# ──────────────────────────────────────────────────────────────────────────────────── main
def main():
    t0 = time.time()
    print("NEGATIVE-SPACE AUDIT — positive assertion, not pattern-grep")
    print("=" * 70)
    print("[0] canary…")
    if not cat0():
        w("VERDICT_SUMMARY.md", "# SWEEP ABORTED — THE CANARY DID NOT FIRE.\n\n"
                                "Every other result is UNINTERPRETABLE. See VERDICT_0_CANARY.md.\n")
        print("  *** CANARY FAILED — ABORTING. ***")
        return
    print("[A] tilde siblings…");    A = catA()
    print("[B] data roots…");        B = catB()
    print("[C] absence claims…");    C = catC()
    print("[D] silent drops…");      D, Dn = catD()
    print("[E] dormant gates…");     E = catE()
    print("[F] un-run preregs…");    F = catF()

    w("VERDICT_SKIPPED.md",
      "# FILES THE SWEEP SKIPPED (a sweep for silent exclusion that silently excludes is the joke writing itself)\n\n"
      + (f"**{len(SKIPPED)} skipped.**\n\n" + "\n".join(f"- `{f}` — {r}" for f, r in SKIPPED)
         if SKIPPED else "**0 files skipped.** Every file was read and parsed."))

    w("VERDICT_SUMMARY.md", "\n".join([
        "# NEGATIVE-SPACE AUDIT — SUMMARY", "",
        "**Design principle: DO NOT GREP FOR THE BUG. ENUMERATE THE RESOURCES AND ASSERT EACH RESOLVES.**",
        "", "| cat | what | denominator | findings |", "|---|---|---|---|",
        "| **0** | canary | 2 planted | **2 detected — GATE PASS** |",
        f"| **A** | tilde/non-expanding idioms | {len(PY)} .py | **{len(A)}** |",
        f"| **B** | data roots (positive) | {len(find_roots())} roots | **{len(B)} dead/empty** |",
        f"| **C** | absence claims in prose | {len(MD)} docs | **{len(C)} to verify vs disk** |",
        f"| **D** | silent drops | {len(PY)} .py | **{len(D)}** handlers, **{len(Dn)}** loaders w/o counts |",
        f"| **E** | dormant gates | {len(PY)} .py | **{len(E)}** |",
        f"| **F** | un-run preregs | — | see VERDICT_F |",
        "", f"*{time.time()-t0:.1f}s*"]))
    print(f"\nDONE in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()

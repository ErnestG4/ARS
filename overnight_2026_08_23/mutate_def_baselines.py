"""THE DISCRIMINATION REQUIREMENT — SEALED_CRITERIA §2, executed.

COMMITTED GENERATOR of overnight_2026_08_23/mutations_def.json.
Mutates SOURCE STRINGS IN MEMORY. No repo file is read-write, none is edited,
and nothing outside this directory is written.

A captured artifact that would not change when the site changes protects
nothing. So each baseline is attacked with perturbations drawn from the
divergence axes the census actually measured — not invented ones — and a site
whose baseline survives every applicable attack is CAPTURED_INERT, which the
sealed vocabulary does NOT count as captured.

The attacks are applied to the extracted closure source and rebuilt through the
SHIPPED builder (`build_from_source`), so what is tested is the machinery that
produced the baseline, not a re-implementation of it.

WHY "APPLICABLE" IS DECIDED FROM THE INVENTORY ROW
--------------------------------------------------
A mutation that cannot be applied to a site — no label of that spelling, no
guard constant to flip — is INAPPLICABLE and leaves the denominator, rather than
being scored as a survival. An attack that could never land is not evidence the
baseline is strong, and counting it as one is the inert-arm defect wearing the
mutation-testing shirt. Every INAPPLICABLE carries the reason it could not land.
"""
import copy
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import numpy as np                                            # noqa: E402
from capture_def_baselines import (closure_source, build_from_source,   # noqa: E402
                                   ser, adapt)
from redpath import redpath                                   # noqa: E402

INV = json.load(open(f"{ROOT}/gate_census/c3_inline_divergences.json"))
BASE = json.load(open(f"{HERE}/baselines_def.json"))
INPUTS = json.load(open(f"{HERE}/inputs.json"))["vectors"]

NOT_APPLICABLE = "INAPPLICABLE"


# ── the attacks, one per measured divergence axis ────────────────────────────
# SIZE_EXPR widened 2026-08-23 after an audit found FOUR FALSE INAPPLICABLEs.
# The first version required `.size` or `len(...)` ADJACENT to the comparison,
# so run_phase4's guard -- `n = s.size` on one line and `if n < 5:` on the next --
# was invisible, and the harness reported "no size guard constant in this site's
# closure" about a closure that contains one. An attack silently not run and an
# attack that found nothing produce identical reports.
#
# This is the arc's spelling blind spot for the FOURTH time, one level further
# in each time: which files, which code counts as the classifier, which syntax
# the values arrive in, and now which syntax the GUARD is written in -- inside
# the instrument built to audit the instrument.
SIZE_EXPR = r"(?:\.size|len\([^)]*\)|\bn\b)"


def m_guard_flip(code):
    """D1: change the guard constant. 50<->5, else 5->50."""
    if re.search(SIZE_EXPR + r"\s*<\s*50", code):
        return re.sub("(" + SIZE_EXPR + r"\s*<\s*)50", r"\g<1>5", code, count=1), None
    if re.search(SIZE_EXPR + r"\s*<\s*5\b", code):
        return re.sub("(" + SIZE_EXPR + r"\s*<\s*)5\b", r"\g<1>50", code, count=1), None
    return None, "no size guard constant in this site's closure to flip"


def m_guard_boundary(code):
    """D1 off-by-one: `< K` -> `<= K`. Differs on exactly one input size."""
    if re.search(SIZE_EXPR + r"\s*<\s*\d+", code):
        return re.sub("(" + SIZE_EXPR + r"\s*)<(\s*\d+)", r"\g<1><=\g<2>", code, count=1), None
    return None, "no strict size comparison to loosen"


def m_label_flip(code):
    """D5: change the class vocabulary the site emits."""
    for a, b in (("'Poiss'", "'Poisson'"), ("'Poisson'", "'Poiss'"),
                 ("'poisson'", "'Poisson'")):
        if a in code:
            return code.replace(a, b, 1), None
    return None, "site emits no Poisson-family label literal"


def m_key_drop(code):
    """D4: drop an emitted key from the returned dict."""
    for key in ("mass03", "gap", "ks_u"):
        m = re.search(rf"\b{key}\s*=\s*[^,)]+,\s*", code)
        if m:
            return code[:m.start()] + code[m.end():], None
    return None, "no droppable keyword in a returned dict (site may not return one)"


def m_argmin_swap(code):
    """The decision itself: swap two arms so the winner can change."""
    swapped = re.sub(r"\('GOE',\s*ks_o\),\s*\('GUE',\s*ks_u\)",
                     "('GOE', ks_u), ('GUE', ks_o)", code, count=1)
    if swapped != code:
        return swapped, None
    swapped = re.sub(r"\('goe',\s*ks_o\),\s*\('gue',\s*ks_u\)",
                     "('goe', ks_u), ('gue', ks_o)", code, count=1)
    if swapped != code:
        return swapped, None
    return None, "decision arms are not a literal (GOE, ks_o), (GUE, ks_u) pair"


def m_statistic_perturb(code):
    """Numerical, not structural: nudge the empirical CDF by one rank.
    The subtlest attack here — it changes every KS distance in the last decimal
    places without touching control flow, so a baseline that rounds, truncates,
    or compares only labels will miss it."""
    # Spelling-independent: match arange(1, <anything> + 1) / <same thing>.
    # run_eeg_depth and run_eeg_full write `np.arange(1, spacings.size + 1) /
    # spacings.size`, which the literal form missed -- reported INAPPLICABLE at
    # two sites where the corrected attack is DETECTED on 39 inputs.
    m = re.search(r"np\.arange\(1,\s*([^)]+?)\s*\+\s*1\)\s*/\s*(\S+)", code)
    if m and m.group(1).strip() == m.group(2).strip().rstrip(")"):
        return code[:m.end()] + code[m.end():], None
    m2 = re.search(r"(np\.arange\(1,\s*[^)]+?\s*\+\s*1\)\s*/\s*)(\S+?)(\s|$|\))", code)
    if m2:
        return code[:m2.start(2)] + f"({m2.group(2)} + 1e-12)" + code[m2.end(2):], None
    return None, "site does not build an empirical CDF as arange(1, k+1)/k"


ATTACKS = {"guard_flip": m_guard_flip, "guard_boundary": m_guard_boundary,
           "label_flip": m_label_flip, "key_drop": m_key_drop,
           "argmin_swap": m_argmin_swap, "statistic_perturb": m_statistic_perturb}


def observe(fn, key):
    out = {}
    for vname, vec in INPUTS.items():
        try:
            out[vname] = {"ok": True, "value": ser(fn(adapt(key, vec)))}
        except Exception as exc:                              # noqa: BLE001
            out[vname] = {"ok": False, "raised": f"{type(exc).__name__}: {exc}"}
    return out


rows = {}
for key, b in sorted(BASE["baselines"].items()):
    code, _pulled, needed = closure_source(b["path"], b["callable"])
    baseline = b["results"]
    per_attack = {}
    for aname, attack in ATTACKS.items():
        mutated, why_not = attack(code)
        if mutated is None:
            per_attack[aname] = {"verdict": NOT_APPLICABLE, "reason": why_not}
            continue
        try:
            fn, _inj = build_from_source(mutated, needed, b["callable"])
        except Exception as exc:                              # noqa: BLE001
            per_attack[aname] = {"verdict": "MUTANT_UNBUILDABLE",
                                 "reason": f"{type(exc).__name__}: {exc}"}
            continue
        obs = observe(fn, key)
        differing = [v for v in baseline if obs.get(v) != baseline[v]]
        per_attack[aname] = {"verdict": "DETECTED" if differing else "SURVIVED",
                             "inputs_differing": len(differing),
                             "example": sorted(differing)[:3]}
    applicable = {k: v for k, v in per_attack.items()
                  if v["verdict"] not in (NOT_APPLICABLE, "MUTANT_UNBUILDABLE")}
    detected = {k: v for k, v in applicable.items() if v["verdict"] == "DETECTED"}
    rows[key] = dict(path=b["path"], line=b["line"],
                     attacks=per_attack,
                     n_applicable=len(applicable), n_detected=len(detected),
                     verdict=("CAPTURED" if applicable and len(detected) >= 1
                              else "CAPTURED_INERT" if applicable
                              else "CAPTURED_UNATTACKED"))

print(f"{'site':38s} {'appl':>5s} {'det':>4s}  verdict")
for key in sorted(rows):
    r = rows[key]
    print(f"  {key:36s} {r['n_applicable']:>5d} {r['n_detected']:>4d}  {r['verdict']}")

verdicts = {}
for r in rows.values():
    verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1
print(f"\nverdict tally: {verdicts}")

print("\nATTACK REACH — how often each attack could even be applied:")
for aname in ATTACKS:
    appl = sum(1 for r in rows.values()
               if r["attacks"][aname]["verdict"] not in (NOT_APPLICABLE, "MUTANT_UNBUILDABLE"))
    det = sum(1 for r in rows.values() if r["attacks"][aname]["verdict"] == "DETECTED")
    surv = sum(1 for r in rows.values() if r["attacks"][aname]["verdict"] == "SURVIVED")
    print(f"  {aname:20s} applicable {appl:>3d}/{len(rows)}   detected {det:>3d}   SURVIVED {surv:>3d}")

survivors = {k: [a for a, v in r["attacks"].items() if v["verdict"] == "SURVIVED"]
             for k, r in rows.items()}
survivors = {k: v for k, v in survivors.items() if v}
if survivors:
    print("\nSURVIVING MUTANTS — a real change these baselines would NOT see:")
    for k, v in sorted(survivors.items()):
        print(f"  {k:36s} {v}")

# NON-VACUITY, both directions. An attack suite that lands nowhere proves
# nothing; one that is detected everywhere on the first try is more likely to be
# comparing something trivial than to have found a uniformly strong population.
with redpath("attacks that could be applied to at least one site", expect_min=4) as rp:
    rp.observed(sum(1 for a in ATTACKS
                    if any(rows[k]["attacks"][a]["verdict"] not in
                           (NOT_APPLICABLE, "MUTANT_UNBUILDABLE") for k in rows)))

json.dump(dict(n_sites=len(rows), verdicts=verdicts, rows=rows),
          open(f"{HERE}/mutations_def.json", "w"), indent=1)
print("\nwritten -> overnight_2026_08_23/mutations_def.json")

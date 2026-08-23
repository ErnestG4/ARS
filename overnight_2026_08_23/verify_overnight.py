"""Board checker for the R3 baseline arc.

WHAT TURNS THIS RED — named up front, because a checker whose failure mode nobody
can state has not been red-pathed:

  (a) the sealed input set no longer regenerates identically (the RULER moved)
  (b) a def-site baseline no longer reproduces from its committed generator
  (c) any site's mutation verdict weakens — a baseline that used to detect an
      attack and now survives it has gone blind, and that is the whole point of
      the discrimination requirement
  (d) the pre-registered discrimination claim fails: the input set stops making
      sites disagree, which would make every baseline bit-identical and the
      instrument silently useless

NOT CHECKED HERE: the module-site scripts. They take ~40s of GPU time and
overwrite untracked PNGs; a board row that runs them would make the board
expensive AND mutating. Their baseline is verified by its own generator on
demand. That is a real coverage gap in this row and it is stated rather than
papered over — the module sites are precisely the stratum this arc has twice
found to be where the hard cases live.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable
CHECKS = []


def _iter_pairs(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k, v
            yield from _iter_pairs(v)
    elif isinstance(o, list):
        for v in o:
            yield from _iter_pairs(v)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def run(label, script):
    p = subprocess.run([PY, os.path.join(HERE, script)],
                       capture_output=True, text=True, cwd=ROOT)
    CHECKS.append((label, p.returncode == 0,
                   "" if p.returncode == 0 else
                   (p.stderr.strip().splitlines() or ["(no stderr)"])[-1]))


inp, base, mut = (os.path.join(HERE, f) for f in
                  ("inputs.json", "baselines_def.json", "mutations_def.json"))

# read BANKED content before regenerating — otherwise the content rows check the
# generator against itself, which is how verify_c3's first draft was inert
banked_base = json.load(open(base))
banked_mut = json.load(open(mut))
before = sha(inp), sha(base), sha(mut)

run("sealed input set regenerates", "make_inputs.py")
run("def baselines reproduce", "capture_def_baselines.py")
run("mutation suite reproduces", "mutate_def_baselines.py")

after = sha(inp), sha(base), sha(mut)
CHECKS.append(("inputs, baselines and mutations bit-identical", before == after,
               "" if before == after else "regenerated output differs from banked"))

# ── content: the verdicts themselves ────────────────────────────────────────
verdicts = banked_mut["verdicts"]
n_sites = banked_mut["n_sites"]
CHECKS.append((f"every one of {n_sites} def sites is CAPTURED",
               verdicts.get("CAPTURED") == n_sites,
               "" if verdicts.get("CAPTURED") == n_sites else f"verdicts={verdicts}"))

# KNOWN-BLIND SPOTS, pinned with their causes. The first version of this row
# asserted ZERO survivals -- true when written, false once the guard regex was
# widened and three genuine, structurally explained survivals appeared. Weakening
# it to pass would launder them; leaving it permanently red would make it inert.
# So the row pins WHAT IS KNOWN BLIND and fails on any deviation.
#
# It fails in BOTH directions on purpose. A survival that DISAPPEARS is also news:
# it means the attack changed meaning, which is exactly what happened when the
# widened regex silently moved guard_boundary's target from the body guard to the
# helper's n<5.
EXPECTED_BLIND = {
    "run_lmfdb_family.py:102": ["guard_boundary"],
    "verify/tier1_lfunction_guard.py:73": ["guard_boundary"],
    # both: the edit lands on `if n <= 5` inside ks_to, which the body guard at
    # 50 SHADOWS -- the inner layer of the two-layer guard is unreachable
    # wherever the outer layer is stricter
    "universality.py:129": ["guard_boundary"],
    # the edit lands inside _ks_pvalue, whose output nothing compares: the
    # COMPUTED_UNUSED finding showing up as a hole in the baseline
}
blind = {k: sorted(a for a, v in r["attacks"].items() if v["verdict"] == "SURVIVED")
         for k, r in banked_mut["rows"].items()}
blind = {k: v for k, v in blind.items() if v}
expected = {k: sorted(v) for k, v in EXPECTED_BLIND.items()}
new_blind = {k: [a for a in v if a not in expected.get(k, [])] for k, v in blind.items()}
new_blind = {k: v for k, v in new_blind.items() if v}
healed = {k: [a for a in v if a not in blind.get(k, [])] for k, v in expected.items()}
healed = {k: v for k, v in healed.items() if v}
CHECKS.append(("no NEW blind spot beyond the three pinned", not new_blind,
               "" if not new_blind else f"new: {new_blind}"))
CHECKS.append(("the three pinned blind spots are still blind", not healed,
               "" if not healed else
               f"no longer surviving: {healed} — the attack may have changed meaning"))

# an attack that lands nowhere is not evidence; require reach, not just success
reach = {}
for a in next(iter(banked_mut["rows"].values()))["attacks"]:
    reach[a] = sum(1 for r in banked_mut["rows"].values()
                   if r["attacks"][a]["verdict"] not in ("INAPPLICABLE", "MUTANT_UNBUILDABLE"))
CHECKS.append(("every attack is applicable at 10+ sites", min(reach.values()) >= 10,
               "" if min(reach.values()) >= 10 else f"reach={reach}"))

# the pre-registered claim about the RULER (SEALED_CRITERIA §3)
n_dis = len(banked_base.get("disagreeing_inputs_canonical",
                            banked_base["disagreeing_inputs"]))
CHECKS.append(("input set still makes sites disagree on the CANONICAL class",
               n_dis >= 1,
               "" if n_dis >= 1 else "zero disagreement: the ruler has gone blind"))
n_lab = banked_base.get("sites_contributing_a_label", 0)
CHECKS.append(("every site contributes a class label to the rate",
               n_lab == banked_base["n_sites"],
               "" if n_lab == banked_base["n_sites"]
               else f"only {n_lab} of {banked_base['n_sites']} — the rate is over an unnamed stratum"))
run("serialiser sensitivity reproduces", "serialiser_sensitivity.py")

# Full-precision serialisation is load-bearing. The first version of this row
# sampled ONE record and asked whether it contained a hex float -- and drew
# clock_n0, a sentinel result of {"best": "insufficient", "n": 0} with no floats
# in it at all. It reported the serialiser broken when the serialiser was fine.
# The property that actually matters is universal, so assert it universally:
# NO bare JSON float may appear anywhere, and hex floats must actually occur.
def _walk(o):
    if isinstance(o, dict):
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)
    else:
        yield o

bare = [x for x in _walk(banked_base["baselines"]) if isinstance(x, float)]
n_hex = sum(1 for k, v in _iter_pairs(banked_base["baselines"]) if k == "__f")
CHECKS.append(("no float is stored as a bare JSON number", not bare,
               "" if not bare else f"{len(bare)} bare float(s), e.g. {bare[:3]}"))
CHECKS.append(("hex-encoded floats actually present", n_hex > 100,
               "" if n_hex > 100 else f"only {n_hex} hex floats — serialiser may be bypassed"))

print("R3 baseline arc verification\n")
for label, ok, why in CHECKS:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"   [{why}]" if why else ""))
bad = [c for c in CHECKS if not c[1]]
print(f"\n  {len(CHECKS) - len(bad)}/{len(CHECKS)} passed")
print(f"  attack reach: {reach}")
if bad:
    print("\nVERIFY_OVERNIGHT: FAIL")
    sys.exit(1)
print(f"\nVERIFY_OVERNIGHT: PASS — ruler reproduces, baselines reproduce, and the "
      f"blind-spot set is exactly the {sum(len(v) for v in EXPECTED_BLIND.values())} "
      f"pinned and explained ones. NOT 'everything is detected': three attacks "
      f"survive, by construction, and this row exists to notice a fourth.")

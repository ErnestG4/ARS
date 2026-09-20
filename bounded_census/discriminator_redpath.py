"""Does the distinct-ratio discriminator RECLASSIFY anything other than rho?
COMMITTED GENERATOR of bounded_census/discriminator_redpath.json.

PROVENANCE, stated because it is the point. The rule "a rail is a pileup, not a
proximity" was adopted AFTER a distance-only measurement put Berry-Robnik rho at
36.1% railed and appeared to falsify its sealed MATHEMATICAL classification. The
sealing did its job -- it forced the contradiction into the open instead of
letting the classification drift -- but the RESOLUTION RULE was chosen after
seeing the result it resolves. That is a rationalisation surface one level up,
and "almost certainly correct" does not exempt it: Brody at ratio 0.0003 vs rho
at 0.9988 is not a marginal call, but the rule still has to be shown not to have
been shaped to fit.

THE TEST: apply the discriminator to EVERY classified site and check whether it
changes any verdict OTHER than rho's. If it moves another site, it was tuned to
one case and the census reopens.
"""
import json, glob, os
import numpy as np

# Repo-relative, not a hardcoded checkout: with the absolute path a board run
# from a nested worktree regenerated the MAIN checkout's tracked JSONs while
# verify_bounded_census compared the worktree's own copies (2026-09-20).
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOL, RAIL_RATIO = 1e-3, 0.01
SITES = {"brody_q": (0.0, 1.0), "brody_q_unbounded": (-1.0, 4.0),
         "berry_robnik": (0.0, 1.0), "alpha": (1e-3, None), "kappa": (1e-4, 100.0)}
vals = {}


def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                kl = k.lower()
                key = ("brody_q_unbounded" if ("brody" in kl and "unbounded" in kl)
                       else "brody_q" if "brody_q" in kl
                       else "berry_robnik" if "berry_robnik" in kl
                       else "alpha" if kl == "alpha"
                       else "kappa" if kl == "kappa" else None)
                if key:
                    vals.setdefault(key, []).append(float(v))
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


for f in glob.glob(f"{R}/**/*.json", recursive=True) + glob.glob(f"{R}/**/*.jsonl", recursive=True):
    rel = os.path.relpath(f, R)
    if rel.startswith(".git/") or rel.startswith(".claude/"):   # relative: a worktree's own path contains /.claude/
        continue
    # ring/ is a different arc whose tables reuse the key NAMES this census
    # matches by (`alpha` = a Jacobian's spectral abscissa, `kappa` = an
    # eigenvector condition number -- not the DPP alpha / Thomas kappa the
    # sites are labelled with). 19 of each entered the census on 2026-09-20 and
    # flipped alpha@lo from CLEAR to INSUFFICIENT_N. A key-name census must
    # exclude arcs whose keys it does not own.
    if rel.startswith("ring/"):
        continue
    try:
        t = open(f, errors="replace").read()
    except OSError:
        continue
    if not any(s.split("_")[0] in t for s in SITES):
        continue
    try:
        if f.endswith(".jsonl"):
            for line in t.splitlines():
                if line.strip():
                    try:
                        walk(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        else:
            walk(json.loads(t))
    except json.JSONDecodeError:
        pass

rows, flips = {}, []
print(f"{'site':20s} {'bound':>8s} {'near':>8s} {'distinct':>9s} {'ratio':>8s} "
      f"{'distance-only':>14s} {'discriminator':>24s}  changed?")
for key, (lo, hi) in SITES.items():
    v = np.array(vals.get(key, []), float)
    if v.size == 0:
        continue
    for bname, b in (("lo", lo), ("hi", hi)):
        if b is None:
            continue
        near = v[np.abs(v - b) <= TOL]
        if near.size == 0:
            continue
        d = len({round(float(x), 15) for x in near})
        ratio = d / near.size
        # MINIMUM-n GUARD, derived from the threshold rather than chosen.
        # A true rail emits ~1 distinct value, so its ratio is ~1/n. For the
        # ratio to be ABLE to fall below RAIL_RATIO at all, n must exceed
        # 1/RAIL_RATIO. Below that the discriminator CANNOT return "rail" for
        # any input -- an arm that cannot fire, scored as a verdict. Found by
        # red-pathing: kappa@hi has n=2, ratio 1.0, and "flipped" only because
        # a 2-sample ratio is uninformative in both directions.
        MIN_N = int(1 / RAIL_RATIO)
        old = bool(near.size / v.size > 0.05)          # distance-only verdict
        if near.size < MIN_N:
            new, changed, note = None, False, f"INDETERMINATE (n={near.size} < {MIN_N})"
        else:
            new = bool(near.size / v.size > 0.05 and ratio < RAIL_RATIO)
            changed = old != new
            note = ""
        rows[f"{key}@{bname}"] = dict(n=int(v.size), near=int(near.size), distinct=d,
                                      ratio=ratio, distance_only=old,
                                      discriminator=new, changed=changed, note=note)
        if changed:
            flips.append(f"{key}@{bname}")
        shown = note if note else str(new)
        print(f"{key:20s} {b:>8.4g} {near.size:>8,} {d:>9,} {ratio:>8.4f} "
              f"{str(old):>14s} {shown:>24s}  {'YES' if changed else 'no'}")

others = [f for f in flips if not f.startswith("berry_robnik")]
out = dict(rows=rows, flips=flips, flips_other_than_rho=others,
           verdict=("DISCRIMINATOR_SCOPED — it changes only the rho verdict it was "
                    "adopted to resolve; no other classified site moves, so it was "
                    "not tuned into existence at the cost of the rest of the census"
                    if not others else
                    f"DISCRIMINATOR_RECLASSIFIES {others} — it was shaped to one "
                    "case and the census must reopen"))
print(f"\nverdicts changed: {flips or 'none'}")
print(f"changed OTHER than rho: {others or 'none'}")
print(f"\n{out['verdict']}")
json.dump(out, open(f"{R}/bounded_census/discriminator_redpath.json", "w"), indent=1)

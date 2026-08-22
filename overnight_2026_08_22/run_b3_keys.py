"""B3 — classify the unmatched banked keys. COMMITTED GENERATOR of b3_keys.json.
Scored against SEALED_CRITERIA.md (82e408e): categories fixed, DISTINCT KEY NAMES,
integer count, predicted BOUNDED_FIT <= 15.
"""
import glob, json, os, re, sys
import numpy as np
R = "/home/combust/fmexplorer/criticality_tool"
COVERED = ("brody_q", "berry_robnik", "rep_int")
PAT = re.compile(r'"([A-Za-z0-9_.]{2,60})"\s*:\s*(-?\d+\.?\d*(?:[eE][-+]?\d+)?)')

vals = {}
for f in glob.glob(f"{R}/**/*.json", recursive=True) + glob.glob(f"{R}/**/*.jsonl", recursive=True):
    if "/.git/" in f:
        continue
    try:
        t = open(f, errors="replace").read()
    except OSError:
        continue
    for k, v in PAT.findall(t):
        if any(c in k.lower() for c in COVERED):
            continue
        try:
            vals.setdefault(k, []).append(float(v))
        except ValueError:
            pass

def categorise(name, v):
    a = np.asarray(v, float); a = a[np.isfinite(a)]
    if a.size == 0:
        return "UNCLASSIFIABLE", "no finite values"
    lo, hi = float(a.min()), float(a.max())
    integral = bool(np.all(np.abs(a - np.round(a)) < 1e-12))
    nm = name.lower()
    if integral and (lo >= 0) and not re.search(r"rho|corr|q\b|alpha|beta|frac|rate|ratio", nm):
        return "COUNT_OR_ID", f"all-integer, non-negative ({lo:.0f}..{hi:.0f})"
    if -1.0001 <= lo and hi <= 1.0001 and lo < -1e-9:
        return "CORRELATION_LIKE", f"spans negative into [-1,1] ({lo:+.3f}..{hi:+.3f})"
    if re.search(r"_q$|^q$|brody|robnik|rho|alpha|kappa|_fit$|theta", nm) and not integral \
            and (lo >= -1.5 and hi <= 5.0):
        return "BOUNDED_FIT", f"fit-parameter-shaped, range {lo:+.3f}..{hi:+.3f}"
    return "OTHER", f"range {lo:.4g}..{hi:.4g}"

rows = {}
for k, v in vals.items():
    c, why = categorise(k, v)
    rows[k] = dict(category=c, n_occurrences=len(v), why=why)
counts = {}
for r in rows.values():
    counts[r["category"]] = counts.get(r["category"], 0) + 1
nbf = counts.get("BOUNDED_FIT", 0)
print(f"distinct unmatched key NAMES: {len(rows)}")
for c, n in sorted(counts.items(), key=lambda kv: -kv[1]):
    print(f"  {c:18s} {n:>5}")
print(f"\nSEALED: BOUNDED_FIT <= 15  ->  measured {nbf}  ->  "
      f"{'MET' if nbf <= 15 else 'MISSED — rail-census coverage was materially worse than reported'}")
if nbf:
    print("\nBOUNDED_FIT keys (the ones that would extend the rail census):")
    for k, r in sorted(rows.items()):
        if r["category"] == "BOUNDED_FIT":
            print(f"  {k:34s} n={r['n_occurrences']:>6}  {r['why']}")
json.dump(dict(n_distinct_keys=len(rows), counts=counts, predicted_max_bounded_fit=15,
               measured_bounded_fit=nbf, passes=bool(nbf <= 15), rows=rows),
          open(f"{R}/overnight_2026_08_22/b3_keys.json", "w"), indent=1)

"""
rail_audit.py — the FIFTH watcher. Sweeps EVERY axis in the coordinate store for rails.

WHY THIS EXISTS. Rails have now been found, one at a time and each by accident, in three separate
axes: `I.8_brody_q` (both ends, R-140/R-144), `ARS.rep_med` (lower end R-093/R-094, and the UPPER
end at the mask width found only on 2026-07-28, R-173), and `I.9_berry_robnik_rho` (all four
calibrators rail-proximate, R-148). Each discovery cost a session. This converts the discovery into
a check that runs by convention.

THE DESIGN CHOICE THAT MATTERS. It does NOT test "is this value at a known bound" -- a checklist
only finds rails someone already knew about, and the 0.85 rail sat undetected in 43.9% of the
banked `ARS.rep_med` values precisely because nobody had it on a list. Instead it tests

    EXACT-VALUE PILEUP IN A CONTINUOUS FIELD

which is mechanism-agnostic: a continuous estimator should essentially never return the same float
twice, so a value holding a large share of the cells IS a rail, whatever produced it and whether or
not anyone has named it. Verified: with no prior knowledge it recovers `I.8_brody_q`'s lower rail
at 6.61e-05 (72.5%) and `ARS.rep_med`'s upper rail at 0.85 (43.9%).

THRESHOLD, CALIBRATED ON MEASURED DATA rather than chosen:
    known rails      I.8_brody_q 72.5%   ARS.rep_med 43.9%
    repaired axis    ARS.rep_med_signed  2.0%
    continuous axes  I.5_ks_gue 0.05%   I.1_w1_clock 0.02%   I.10_cv 0.02%
A 5% threshold separates these by an order of magnitude on both sides.

SECOND SIGNATURE. Exact ties miss the Berry-Robnik shape, where values crowd NEAR a bound without
landing exactly on it (poisson 0.0015, clustered 0.0045, goe 0.9965, gue 0.9975 -- all
rail-proximate, none tied). So axes with a DECLARED bound also get a proximity test.

⚠ THE BOUNDARY-SATURATION ANTIBODY IS BUILT IN: a value at a bound is AMBIGUOUS, NOT INVALID.
q = 0 is also the correct reading for a genuinely Poisson process, and rho ≈ 0 is legitimately
Poisson. This audit therefore REPORTS AND DISAMBIGUATES; it never rejects, and it never calls a
pileup a defect on its own. Resolution goes in the manifest with a reason, exactly like
propagation_watch.

⚠ AND RAILS ARE SUBSTRATE-SPECIFIC, which is why the per-substrate breakdown is not optional:
kuramoto rails HIGH on rep_med (56% at 0.85) while pvc-11 rails LOW (79% at 0.0). A store-wide
average cancelled the two against each other and read as "16.6% saturated".

Usage:  python3 cross_substrate/rail_audit.py [--summary] [--axis NAME]
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
COORD = os.path.join(HERE, "coordinates")
MANIFEST = os.path.join(HERE, "rail_audit_manifest.json")

PILEUP_FRAC = 0.05      # calibrated above
MIN_N = 40              # below this a pileup is not evidence of anything
PROX_BAND = 0.02        # for declared-bound proximity
p_ = lambda *a: print(*a, flush=True)

# Declared bounds, ONLY where the bound is actually known. Everything else is left undeclared on
# purpose: an undeclared pileup is the INTERESTING case (that is what 0.85 was), and pre-populating
# this table with guesses would convert discoveries into "expected" rows.
AXIS_BOUNDS = {
    "I.8_brody_q": (0.0, 1.0),            # fitter bounds -- a MODEL ASSERTION, not a fact (R-144)
    "I.9_berry_robnik_rho": (0.0, 1.0),   # rho is a GOE FRACTION -- definitionally correct
    "I.5_ks_gue": (0.0, 1.0),
    "I.6_ks_clock": (0.0, 1.0),
    "I.7_ks_poisson": (0.0, 1.0),
}


def load():
    rows = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in sorted(glob.glob(os.path.join(COORD, "*.jsonl"))):
        for line in open(f):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            sub = d.get("substrate") or os.path.basename(f)
            for k, v in (d.get("axes_computed") or {}).items():
                if isinstance(v, (int, float)) and v == v:
                    rows[k][sub].append(float(v))
    return rows


def audit_axis(values):
    """(top_value, count, frac, n_distinct) for the largest exact-value pileup."""
    n = len(values)
    c = collections.Counter(values)
    val, cnt = c.most_common(1)[0]
    return val, cnt, cnt / n, len(c)


def proximity(values, bounds, band=PROX_BAND):
    lo, hi = bounds
    n = len(values)
    near = sum(1 for v in values if abs(v - lo) <= band or abs(v - hi) <= band)
    return near / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--axis", default=None)
    args = ap.parse_args()

    data = load()
    man = json.load(open(MANIFEST)) if os.path.exists(MANIFEST) else {"resolved": {}}
    resolved = man.get("resolved", {})

    findings = []
    for axis in sorted(data):
        pooled = [v for vs in data[axis].values() for v in vs]
        if len(pooled) < MIN_N:
            continue
        val, cnt, frac, ndist = audit_axis(pooled)
        prox = (proximity(pooled, AXIS_BOUNDS[axis]) if axis in AXIS_BOUNDS else None)
        declared = axis in AXIS_BOUNDS and any(abs(val - b) < 1e-9 for b in AXIS_BOUNDS[axis])
        hit_p = frac >= PILEUP_FRAC
        hit_b = prox is not None and prox >= 0.5 and not hit_p
        if not (hit_p or hit_b):
            continue
        per_sub = {}
        for sub, vs in data[axis].items():
            if len(vs) < MIN_N:
                continue
            v2, c2, f2, _ = audit_axis(vs)
            if f2 >= PILEUP_FRAC:
                per_sub[sub] = (v2, c2, f2)
        findings.append(dict(axis=axis, n=len(pooled), n_distinct=ndist, value=val,
                             count=cnt, frac=frac, prox=prox, declared=declared,
                             sig="P" if hit_p else "B", per_sub=per_sub))

    if args.axis:
        findings = [f for f in findings if f["axis"] == args.axis]

    p_("=" * 88)
    p_("RAIL AUDIT — exact-value pileups in continuous axes, across the coordinate store")
    p_(f"  axes scanned {len(data)}   pileup threshold {PILEUP_FRAC:.0%}   min n {MIN_N}")
    p_("  a pileup is AMBIGUOUS, not invalid: q=0 is also correct for a genuinely Poisson process")
    p_("=" * 88)

    unresolved = []
    for f in findings:
        key = f"{f['axis']}@{f['value']:.10g}"
        state = resolved.get(key, "UNRESOLVED")
        if state == "UNRESOLVED":
            unresolved.append(key)
        tag = ("declared bound" if f["declared"] else
               "UNDECLARED VALUE" if f["sig"] == "P" else "bound-proximate")
        p_(f"\n  [{f['sig']}] {f['axis']}   n={f['n']}  distinct={f['n_distinct']}   [{state}]")
        p_(f"      pileup at {f['value']:.6g}  ->  {f['count']}/{f['n']} = {f['frac']:.1%}   ({tag})")
        if f["prox"] is not None:
            p_(f"      within {PROX_BAND} of a declared bound: {f['prox']:.1%}")
        if f["per_sub"] and not args.summary:
            p_("      per substrate (rails are substrate-specific):")
            for sub, (v2, c2, f2) in sorted(f["per_sub"].items(), key=lambda kv: -kv[1][2])[:6]:
                p_(f"        {sub:<22s} {v2:>10.6g}  {c2:>6d}  {f2:>6.1%}")

    n = len(unresolved)
    hw = man.get("high_water")
    hw = n if hw is None else hw
    regress = n > hw
    p_("\n" + "-" * 88)
    p_(f"  flagged axes {len(findings)}   unresolved {n}   high-water {hw} (moves DOWN only)")
    if regress:
        p_("  *** REGRESSION *** a new unresolved rail appeared.")
    else:
        if n < hw or "high_water" not in man:
            man["high_water"] = n
            man.setdefault("resolved", resolved)
            json.dump(man, open(MANIFEST, "w"), indent=2)
            p_(f"  ratcheted to {n}.")
        p_("  NO REGRESSION — tracked, not a permanent red light.")
    return 1 if regress else 0


if __name__ == "__main__":
    sys.exit(main())

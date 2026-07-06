"""Panel C decisive test — digit-multiset-matched arrangements (the '[V7] three ways' as three ORDERINGS).

The n=16 three-ways correlations are confounded: C rises ~0.5 with Λ, K, meandig, maxdig alike because those
functionals co-vary with digit size. To separate them, apply decompose_confound_with_designed_instance: hold the
digit MULTISET fixed (=> K, meandig, maxdig, mdens ALL identical) and vary only the ARRANGEMENT (=> only Λ and the
actual spectrum change). If C moves within a family, C is NOT a function of digit-statistics — the CF ARRANGEMENT
(hence Λ/spectrum) controls it, sharpening Panel A's 'K is the order parameter' to 'K alone does not determine C'.
"""
import sys, json, math
from itertools import permutations
sys.path.insert(0, ".")
import numpy as np
import panel_C as pc   # reuse degt_C, lagrange_const, periodic_alpha (clean Floquet pipeline)

# base multisets that admit >=2 distinct primitive-period arrangements with the SAME geomean
MULTISETS = [
    [1, 1, 2, 2],
    [1, 1, 1, 2, 2],
    [1, 1, 3, 3],
    [1, 1, 2, 2, 3, 3],
    [1, 2, 2, 3],
    [1, 1, 2, 3],
]

def primitive_period(seq):
    """Reduce a periodic sequence to its primitive (shortest) period."""
    n = len(seq)
    for d in range(1, n + 1):
        if n % d == 0 and seq[:d] * (n // d) == list(seq):
            return tuple(seq[:d])
    return tuple(seq)

def distinct_arrangements(multiset):
    """Distinct periodic CFs from permutations of the multiset, deduped by alpha value (rotation/period)."""
    seen = {}
    for perm in set(permutations(multiset)):
        prim = primitive_period(list(perm))
        a = pc.periodic_alpha(list(prim))
        key = round(a, 12)
        if key not in seen:
            seen[key] = prim
    return list(seen.values())

fams = []
for ms in MULTISETS:
    K = float(np.prod(np.array(ms, float)) ** (1.0 / len(ms)))
    arrs = distinct_arrangements(ms)
    members = []
    for prim in arrs:
        C, pts = pc.degt_C(list(prim))
        if C is None:
            continue
        members.append({"period": list(prim), "alpha": pc.periodic_alpha(list(prim)),
                        "lagrange": pc.lagrange_const(list(prim)), "C": C, "nlam": len(pts)})
    members.sort(key=lambda m: m["lagrange"])
    fam = {"multiset": ms, "K": K, "n_arrangements": len(members), "members": members}
    fams.append(fam)
    Cs = [m["C"] for m in members]
    print(f"\nmultiset {ms}  K={K:.3f}  ({len(members)} distinct arrangements)")
    print(f"  {'period':16s} {'Λ':>7s} {'C':>7s}")
    for m in members:
        print(f"  {str(m['period']):16s} {m['lagrange']:>7.3f} {m['C']:>7.4f}")
    if len(Cs) >= 2:
        print(f"  --> C spread within family (K,digits FIXED): ΔC = {max(Cs)-min(Cs):+.4f}  "
              f"(sd={np.std(Cs):.4f})")

# pooled: within-family C vs Λ (K held fixed within each family)
pairs = []
for fam in fams:
    ms = fam["members"]
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            dL = ms[j]["lagrange"] - ms[i]["lagrange"]
            dC = ms[j]["C"] - ms[i]["C"]
            if abs(dL) > 1e-6:
                pairs.append((dL, dC))
print("\n=== POOLED within-family (K fixed) arrangement test ===")
print(f"  {len(pairs)} arrangement pairs across families (each pair: same digits, different order)")
if pairs:
    dL = np.array([p[0] for p in pairs]); dC = np.array([p[1] for p in pairs])
    agree = int(np.sum(np.sign(dL) == np.sign(dC)))
    from scipy.stats import pearsonr
    r = pearsonr(dL, dC)[0] if len(pairs) > 2 else float('nan')
    print(f"  sign(ΔΛ)==sign(ΔC): {agree}/{len(pairs)} pairs  (does higher-Λ arrangement have higher C?)")
    print(f"  pearson(ΔΛ, ΔC) = {r:+.3f}")
    print(f"  mean |ΔC| within family = {np.mean(np.abs(dC)):.4f}  (0 => C is a digit-statistic; >0 => arrangement matters)")

json.dump(fams, open("panel_C_designed.json", "w"), indent=1)
print("\nwrote panel_C_designed.json")

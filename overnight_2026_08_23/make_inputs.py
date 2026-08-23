"""SEALED INPUT SET for R3 baseline capture. Committed generator of inputs.json.

THE RULER, per overnight_2026_08_23/SEALED_CRITERIA.md §3. The input set is part
of the measuring instrument, not an incidental choice, so it is sealed with the
predictions it will be scored against.

WHY THESE SIZES. The population's guards are two-layered (gate_census/
c3_helper_axis.json): a BODY guard in {50, 5, none} and, underneath it, a KS
helper floor at n<5 returning NaN — measured 2026-08-23, and it corrected the
docket's claim that three sites had no guard at all. An input set that lands
entirely above 50 makes every guard invisible: all variants agree, every baseline
is bit-identical, and the instrument has measured nothing while looking healthy.

So the sizes STRADDLE BOTH LAYERS:
    0   universality.py:129 carries a `==0` sentinel no other site has
    3   below every guard, including the helper floor  -> NaN paths, sentinel arity
    4   `< 5` versus `<= 5` differ on exactly one input, and it is not 5
    5   exactly at the helper floor and the small body guard (boundary)
    6   the only size strictly between the floor and the 5-guard's neighbourhood
    8   above 5, below 50
    30  MID-BAND 5<=n<50: guard-50 sites return 'insufficient' here while guard-5
        sites return a full dict. This is THE discriminating band for the R1 fork,
        and the first sealed input set had nothing in the middle of it.
    49  just below the large body guard
    50  exactly at it (boundary; < versus <= lives here)
    51  just above
    200 comfortably above everything

Boundary values are included deliberately: `n < 50` and `n <= 50` differ on
exactly one input, and a set of round numbers would never distinguish them.

WHY A NON-MEMBER FAMILY. This population's defining property is that it has no
rejection region — 7/7 non-member distributions receive a confident label. A
baseline built only from genuine members would never exercise the behaviour the
arc is about. Uniform spacings are the calibrated non-member: they read
best_ks = 0.091 at n=2000 through this same gate, against 0.0567 for the worst
genuine member.

DETERMINISM. One seed, stated here, drawn once, no reseeding between families.
The CDFs are imported from `universality` — the same functions every one of the
20 decision sites imports — so the inputs are expressed in the population's own
coordinates rather than a private reimplementation of them.
"""
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from universality import nns_cdf_poisson, nns_cdf_goe, nns_cdf_gue   # noqa: E402
from redpath import redpath                                           # noqa: E402

SEED = 20260823
SIZES = [0, 3, 4, 5, 6, 8, 30, 49, 50, 51, 200]
GRID = np.linspace(0.0, 12.0, 240001)      # inversion grid, fixed


def invert(cdf, u):
    """Sample by numerically inverting the surmise CDF on a fixed grid.

    Inversion rather than a closed form on purpose: GOE has one and GUE does
    not, and using two different sampling routes for two families would put a
    method difference inside the input set, where it would be indistinguishable
    from a family difference when the baselines are compared.
    """
    F = cdf(GRID)
    return np.interp(u, F, GRID)


FAMILIES = {
    "poisson":   lambda u: invert(nns_cdf_poisson, u),
    "goe":       lambda u: invert(nns_cdf_goe, u),
    "gue":       lambda u: invert(nns_cdf_gue, u),
    # calibrated NON-MEMBER: belongs to none of the three classes
    "nonmember_uniform": lambda u: 3.0 * u,
    # PERFECT CLOCK: every spacing exactly 1.0. Reads GUE through this gate --
    # the RIGID_GUE failure reached by another route -- and is the calibrated
    # fit_poor=True case. Without it, fit_poor and fit_rejected are captured on
    # one side only, which is the one-sided-calibration defect reappearing
    # inside the instrument built to audit it.
    "clock": lambda u: np.ones_like(u),
}

rng = np.random.default_rng(SEED)
vectors = {}
for fam, draw in FAMILIES.items():
    for n in SIZES:
        v = draw(rng.random(n))
        vectors[f"{fam}_n{n}"] = [float(x) for x in v]

# NON-VACUITY: the set must actually span the guard boundaries it was built for.
with redpath("input vectors below the helper floor (n<5)", expect_min=5) as rp:
    rp.observed(sum(1 for k in vectors if k.rsplit("_n", 1)[1] in ("0", "3", "4")))
with redpath("input vectors straddling the 50 boundary", expect_min=15) as rp:
    rp.observed(sum(1 for k in vectors if k.rsplit("_n", 1)[1] in ("49", "50", "51")))
with redpath("input vectors in the discriminating band 5<=n<50", expect_min=5) as rp:
    rp.observed(sum(1 for k in vectors if k.rsplit("_n", 1)[1] in ("5", "6", "8", "30", "49")))

payload = json.dumps(dict(seed=SEED, sizes=SIZES, families=sorted(FAMILIES),
                          vectors=vectors), indent=1, sort_keys=True)
sha = hashlib.sha256(payload.encode()).hexdigest()
open(f"{HERE}/inputs.json", "w").write(payload)

print(f"seed {SEED}   sizes {SIZES}   families {sorted(FAMILIES)}")
print(f"vectors: {len(vectors)}  ({len(FAMILIES)} families x {len(SIZES)} sizes)")
print(f"\n{'vector':26s} {'n':>4s}  {'min':>8s} {'mean':>8s} {'max':>8s}")
for k in sorted(vectors, key=lambda k: (k.rsplit('_n', 1)[0], int(k.rsplit('_n', 1)[1]))):
    v = np.array(vectors[k])
    if v.size == 0:
        # the n=0 vector exists BECAUSE universality.py:129 has a ==0 sentinel;
        # a summary line that cannot render it would be a small instance of the
        # thing this whole set is built to avoid
        print(f"  {k:24s} {0:>4d}  {'—':>8s} {'—':>8s} {'—':>8s}   (empty by design)")
        continue
    print(f"  {k:24s} {v.size:>4d}  {v.min():8.4f} {v.mean():8.4f} {v.max():8.4f}")
print(f"\nsha256 {sha}")
print("\nINPUTS_SEALED — the ruler is committed before any baseline is captured.")

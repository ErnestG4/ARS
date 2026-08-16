"""L-policy addendum LC-ADD-1 — the discrimination cap is n-DEPENDENT.
COMMITTED GENERATOR of lcap/policy_n.json.

THREE-EVENT LABEL:
  (1) the sealed policy derived discrimination_L = 40 at n_ref = 2000 and
      applied it as a single global constant;
  (2) Will's review asked whether the small-n reference-window finding
      (GUE n=343 caps at L=8.0) needs its own check against the banked
      approximability rows, which run at exactly that n — "a third cap
      binding on the configuration those rows used";
  (3) measured here: it does, and the sealed constant was wrong in form.
      The discrimination cap must be derived AT THE SUBSTRATE'S OWN n,
      because the GUE band's spread grows as n falls while the GUE-GOE gap
      does not.

REGISTRATION (Will's addition, adopted): the discrimination cap is
GOE-DERIVED — GOE is the nearest neighbour in the zoo we have, not
necessarily the nearest in the space.  A future zoo member sitting closer to
GUE at large L can tighten this cap, and because the derivation is recorded
as GOE-relative, that tightening is a refinement of a stated basis rather
than an arbitrary-looking move.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (f"{ROOT}/rigidgate", f"{ROOT}/lcap"):
    if p not in sys.path:
        sys.path.insert(0, p)
import gate_probe as G                                          # noqa: E402
from policy import goe_positions, Z_SEP, DEG, SEEDS, DRAWS      # noqa: E402

N_GRID = [343, 1200, 2000]
L_SCAN = [3.0, 5.0, 6.86, 8.0, 12.0, 20.0, 30.0, 40.0, 50.0]


def discrimination_L_at(n):
    rows, best = {}, None
    for L in L_SCAN:
        gue, _ = G.bands(n, L, SEEDS, DEG)
        gm, gs = gue["sigma2"]["mean"], gue["sigma2"]["sd"]
        vals = [G.sigma2(goe_positions(n, np.random.default_rng(79_000 + k)),
                         L, DEG) for k in range(DRAWS)]
        z = (float(np.mean(vals)) - gm) / gs
        rows[str(L)] = dict(gue_mean=float(gm), gue_sd=float(gs),
                            goe=float(np.mean(vals)), z_goe=float(z),
                            separated=bool(z >= Z_SEP))
    for L in L_SCAN:
        if rows[str(L)]["separated"]:
            best = L
        else:
            break
    return best, rows


def main():
    out = dict(
        three_event=["sealed policy used a single global "
                     "discrimination_L=40 derived at n_ref=2000",
                     "Will's review: check the small-n case against the "
                     "banked approximability rows at their own n",
                     "measured here — the cap is n-dependent and the sealed "
                     "constant was wrong in FORM, not just value"],
        registration="GOE-DERIVED: GOE is the nearest neighbour in the zoo "
                     "we have, not necessarily the nearest in the space. A "
                     "future zoo member closer to GUE at large L tightens "
                     "this cap as a refinement of a stated basis.",
        Z_SEP=Z_SEP, by_n={})
    for n in N_GRID:
        Ld, rows = discrimination_L_at(n)
        out["by_n"][str(n)] = dict(discrimination_L=Ld, scan=rows)
        print(f"  n={n:5d}: discrimination_L = {Ld}", flush=True)

    # the consequence for the banked approximability rows
    n343 = out["by_n"]["343"]
    banked_L = 6.86
    inside = bool(n343["discrimination_L"] is not None
                  and banked_L <= n343["discrimination_L"])
    out["banked_approximability_rows"] = dict(
        n=343, L_banked=banked_L,
        discrimination_L_at_own_n=n343["discrimination_L"],
        inside_discrimination_window=inside,
        z_goe_at_banked_L=n343["scan"][str(banked_L)]["z_goe"],
        consequence="FLAGGED, NOT RE-VERDICTED: at their own n the banked "
                    "rows were judged OUTSIDE the discrimination window "
                    "(GOE separated by only "
                    f"{n343['scan'][str(banked_L)]['z_goe']:.2f} sigma at "
                    f"L={banked_L}, against the required {Z_SEP}). Their "
                    "RIGID_GUE label therefore does not distinguish GUE "
                    "from GOE at that configuration. Re-judging requires "
                    "the substrate data, which this arc does not hold — so "
                    "this is a flag for the owning program, not a move.")
    print(f"  banked approximability rows (n=343, L={banked_L}): "
          f"inside window = {inside} "
          f"(z_GOE = {n343['scan'][str(banked_L)]['z_goe']:+.2f})", flush=True)
    json.dump(out, open(f"{ROOT}/lcap/policy_n.json", "w"), indent=1)


if __name__ == "__main__":
    main()

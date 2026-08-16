"""The L policy — COMMITTED GENERATOR of lcap/policy.json.

    L_judge(substrate) = min( deployed_L , validity_L , discrimination_L )

TWO INDEPENDENT CAPS, both derived without reference to zeta:

  * VALIDITY cap (substrate physics, from validity.py): beyond it the GUE
    form is not expected to describe the substrate at all — Berry saturation
    ln(T/2pi) for L-functions, finite-n departure from the Mehta asymptotic
    for random-matrix spectra.

  * DISCRIMINATION cap (instrument power, derived HERE from the calibrator
    zoo): the largest L at which the nearest CONFUSABLE KNOWN CLASS stays
    excluded from the GUE band by >= Z_SEP.  Discovered while running Will's
    condition-1 zoo gate: GOE — a genuinely different universality class —
    reads RIGID_GUE at the deployed L=50, because across L=3..50 the GUE
    band's spread grows ~5.7x while the GUE-GOE gap grows only ~1.4x.  So
    judging at large L destroys class discrimination even where the GUE form
    is perfectly valid.  This cap is a POWER argument and is independent of
    the validity argument; either can bind first.

The discrimination cap is derived from GOE, whose class is independently
known and which is the nearest confusable member of the zoo.  Nothing about
zeta enters this file.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (f"{ROOT}/rigidgate", f"{ROOT}/lcap"):
    if p not in sys.path:
        sys.path.insert(0, p)
import gate_probe as G                                          # noqa: E402

Z_SEP = 3.0                       # sealed: required GOE exclusion margin
L_SCAN = [3.0, 5.0, 8.0, 12.0, 20.0, 30.0, 40.0, 50.0]
N_REF = 2000
DEG = 6
SEEDS = 24
DRAWS = 6
DEPLOYED_L = 50.0                 # longrange_audit.py AUDIT_L


def goe_positions(n, rng):
    A = rng.standard_normal((n, n))
    H = (A + A.T) / np.sqrt(2.0 * n)
    ev = np.sort(np.linalg.eigvalsh(H))
    x = np.clip(ev / 2.0, -1, 1)
    return (0.5 + (x * np.sqrt(1 - x * x) + np.arcsin(x)) / np.pi) * n


def discrimination_L():
    """Largest scanned L such that GOE is excluded by >= Z_SEP at that L AND
    at every smaller scanned L (a cap must not be justified by a lucky
    single point)."""
    rows, best = {}, None
    for L in L_SCAN:
        gue, _ = G.bands(N_REF, L, SEEDS, DEG)
        gm, gs = gue["sigma2"]["mean"], gue["sigma2"]["sd"]
        vals = [G.sigma2(goe_positions(N_REF, np.random.default_rng(78_000 + k)),
                         L, DEG) for k in range(DRAWS)]
        z = (float(np.mean(vals)) - gm) / gs
        rows[str(L)] = dict(gue_mean=float(gm), gue_sd=float(gs),
                            goe_mean=float(np.mean(vals)), z_goe=float(z),
                            separated=bool(z >= Z_SEP))
        print(f"  L={L:5.1f}: GUE {gm:.4f}+-{gs:.4f}  GOE {np.mean(vals):.4f} "
              f"-> z={z:+.2f} {'ok' if z >= Z_SEP else 'FAILS SEPARATION'}",
              flush=True)
    for L in L_SCAN:
        if rows[str(L)]["separated"]:
            best = L
        else:
            break
    return best, rows


def main():
    VAL = json.load(open(f"{ROOT}/lcap/validity_scales.json"))
    print("discrimination cap (zoo-derived, GOE as nearest confusable class)",
          flush=True)
    L_disc, rows = discrimination_L()
    print(f"  -> discrimination_L = {L_disc}", flush=True)

    policy = {}
    for tag, row in VAL["substrates"].items():
        v = row.get("validity_L")
        caps = {"deployed": DEPLOYED_L, "discrimination": L_disc}
        if v is not None:
            caps["validity"] = v
        L_judge = min(caps.values())
        binding = [k for k, x in caps.items() if x == L_judge]
        policy[tag] = dict(L_judge=float(L_judge), caps=caps,
                           binding=binding, basis=row["basis"])
        print(f"  {tag:18s} L_judge={L_judge:6.2f}  binding={binding}",
              flush=True)

    out = dict(Z_SEP=Z_SEP, deployed_L=DEPLOYED_L, n_ref=N_REF, deg=DEG,
               discrimination_L=L_disc, discrimination_scan=rows,
               policy=policy,
               rule="L_judge = min(deployed_L, validity_L, discrimination_L)",
               derived_without_zeta=True)
    json.dump(out, open(f"{ROOT}/lcap/policy.json", "w"), indent=1)


if __name__ == "__main__":
    main()

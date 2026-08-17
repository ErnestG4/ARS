"""The operationally correct separation quantity — COMMITTED GENERATOR of
lcap/misclass_rate.json.

A specification error surfaced by the cap re-derivation, in MY OWN cap
definition: I defined separation as

    z = (mean_GOE - mean_GUE) / sd_GUE  >=  3

which is a statement about POPULATION MEANS.  But the gate does not classify
populations — it classifies ONE point set, via |o - gue_mean| <= 2.5*gue_sd.
The operationally correct quantity is therefore the MISCLASSIFICATION RATE:
the fraction of individual GOE realizations that land inside the GUE band and
so earn RIGID_GUE.  Separation-of-means ignores the GOE spread entirely and
can look comfortable while individual realizations are misclassified half the
time (or vice versa).

This also re-opens the arc's FOUNDATIONAL finding.  The original zoo gate used
per-draw modal verdicts — the RIGHT question — but at only 6 draws.  The cap
re-derivation used separation-of-means — the WRONG question — at 32 draws.
Neither has yet answered the right question at adequate power.  This does.
"""

import json
import sys

import numpy as np

ROOT = "/home/combust/fmexplorer/criticality_tool"
for p in (f"{ROOT}/rigidgate", f"{ROOT}/lcap"):
    if p not in sys.path:
        sys.path.insert(0, p)
import gate_probe as G                                          # noqa: E402
from policy import goe_positions                                # noqa: E402

N, DEG, MULT = 2000, 6, 2.5
N_DRAWS = 40
L_LIST = [8.0, 20.0, 40.0, 50.0]


def main():
    print(f"generating {N_DRAWS} GUE + {N_DRAWS} GOE realizations at n={N}",
          flush=True)
    gue = np.empty((N_DRAWS, len(L_LIST)))
    goe = np.empty((N_DRAWS, len(L_LIST)))
    for k in range(N_DRAWS):
        pg = G.gue_positions(N, np.random.default_rng(86_000 + k))
        po = goe_positions(N, np.random.default_rng(87_000 + k))
        for j, L in enumerate(L_LIST):
            gue[k, j] = G.sigma2(pg, L, DEG)
            goe[k, j] = G.sigma2(po, L, DEG)
        if (k + 1) % 10 == 0:
            print(f"  {k + 1}/{N_DRAWS}", flush=True)

    out = dict(n=N, deg=DEG, mult=MULT, n_draws=N_DRAWS, rows={})
    for j, L in enumerate(L_LIST):
        gm, gs = gue[:, j].mean(), gue[:, j].std(ddof=1)
        lo, hi = gm - MULT * gs, gm + MULT * gs
        # a GOE realization is MISCLASSIFIED if it lands inside the band
        mis = float(np.mean((goe[:, j] >= lo) & (goe[:, j] <= hi)))
        # bootstrap CI on the rate
        rng = np.random.default_rng(88_000 + j)
        boot = []
        for _ in range(2000):
            ig = rng.integers(0, N_DRAWS, N_DRAWS)
            io = rng.integers(0, N_DRAWS, N_DRAWS)
            g2, s2 = gue[ig, j].mean(), gue[ig, j].std(ddof=1)
            boot.append(np.mean((goe[io, j] >= g2 - MULT * s2)
                                & (goe[io, j] <= g2 + MULT * s2)))
        boot = np.array(boot)
        z_means = (goe[:, j].mean() - gm) / gs
        out["rows"][str(L)] = dict(
            gue_mean=float(gm), gue_sd=float(gs), goe_mean=float(goe[:, j].mean()),
            goe_sd=float(goe[:, j].std(ddof=1)),
            band=[float(lo), float(hi)],
            misclass_rate=mis,
            misclass_p05=float(np.percentile(boot, 5)),
            misclass_p95=float(np.percentile(boot, 95)),
            z_of_means=float(z_means))
        print(f"  L={L:5.1f}: band [{lo:.3f},{hi:.3f}] | GOE "
              f"{goe[:, j].mean():.3f}+-{goe[:, j].std(ddof=1):.3f} | "
              f"z_of_means={z_means:+.2f} | MISCLASS RATE {mis:.2f} "
              f"[{np.percentile(boot, 5):.2f},{np.percentile(boot, 95):.2f}]",
              flush=True)

    worst = max(v["misclass_rate"] for v in out["rows"].values())
    out["finding"] = dict(
        worst_misclass_rate=worst,
        goe_defect_stands=bool(worst > 0.05),
        note="the arc's FOUNDATIONAL claim is that GOE can earn RIGID_GUE at "
             "the deployed configuration. The operationally correct test is "
             "the per-realization misclassification rate, not "
             "separation-of-means.")
    json.dump(out, open(f"{ROOT}/lcap/misclass_rate.json", "w"), indent=1)
    print(f"\nworst misclassification rate {worst:.2f} -> GOE defect stands: "
          f"{out['finding']['goe_defect_stands']}", flush=True)


if __name__ == "__main__":
    main()

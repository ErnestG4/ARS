"""Sparse KDE grid (v2) == dense grid (sealed v1 form) on mode counts, for every spectrum where the dense
grid is feasible: MP nulls of both shapes, two-peak power spectra, and synthetic outlier/dead-row spectra.
Exit 1 on any disagreement.
--redpath: shrink the sparse pad to 0.3h (a real defect) and INVERT the verdict: exit 0 iff mismatches are found,
i.e. the check demonstrably fires on a broken grid (witness-must-be-able-to-fail)."""
import sys
import numpy as np
import peaks as P
import json
from pathlib import Path
seal = json.loads((Path(__file__).resolve().parent / "seals" / "stage1_peak_criterion.json").read_text())
REDPATH = "--redpath" in sys.argv
if REDPATH:
    P.SPARSE_PAD = 0.3
rng = np.random.default_rng(11)
bad = 0; n = 0
for unit, (p_, q_) in (("per_head", (128, 2048)), ("full_matrix", (256, 2048))):
    u = seal["units"][unit]
    for kind in ("mp", "twopeak", "outlier", "deadrows"):
        for r in range(150 if unit == "per_head" else 20):
            if kind == "mp" or kind in ("outlier", "deadrows"):
                W = rng.standard_normal((p_, q_))
                if kind == "outlier":
                    W[:3] *= rng.uniform(3, 30)
                if kind == "deadrows":
                    W[: rng.integers(1, p_ // 2)] *= 10.0 ** rng.uniform(-12, -3)
                x = P.normalise(P.singvals(W))[0]
            else:
                x = np.where(rng.random(p_) < 0.5, 0.94, 1.06) + 0.01 * rng.standard_normal(p_)
            if x.max() / u["h_shape"] > 2e5:
                continue
            for pf in (u["p_star_all"], u["p_star_massive"], 0.05):
                gd, dd = P.kde(x, u["h_shape"], dense=True)
                gs, ds = P.kde(x, u["h_shape"])
                a = P.modes(gd, dd, x, pf, u["m_min"]); b = P.modes(gs, ds, x, pf, u["m_min"])
                n += 1
                if a[:2] != b[:2]:
                    bad += 1
                    print("MISMATCH", unit, kind, r, pf, a[:2], b[:2])
print(f"sparse-vs-dense mode counts: {n - bad}/{n} agree" + (" [REDPATH pad=0.3h]" if REDPATH else ""))
sys.exit((0 if bad else 1) if REDPATH else (1 if bad else 0))

"""Pilot 3 (pre-seal): G-B1 tolerance under the gate configuration.

Diagnosis filed: the first pilot's 0.12 max-abs pcf deviation was pair-count
noise (two-sided, clean asymptote), inflated by the 12.5-unit border erosion
that the GLUING grid needs but the G-B1 window (r ≤ 4) does not.  Gate config:
erosion 4.0, bins 0.1, pooled seeds.  Sealed metric: RMS deviation over
r ∈ [0.25, 4] (noise-robust); max-abs is reported descriptively only.
"""

import json
import sys
import numpy as np

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool/bridge")
from observer_b import DiskWindow, pcf_2d
from ginibre_sampler import sample_ginibre, central_points

bins = np.arange(0.0, 4.0 + 1e-9, 0.1)
gs = []
for s in (910, 911, 912, 913, 914, 915):
    ev = sample_ginibre(2048, s)
    pts, R = central_points(ev, 2048)
    c, g = pcf_2d(pts, DiskWindow(R), bins, lam=1.0 / np.pi)
    gs.append(g)
    print(f"  seed {s} done", flush=True)
g_pool = np.mean(gs, axis=0)
m = c >= 0.25
dev = g_pool[m] - (1.0 - np.exp(-c[m] ** 2))
out = dict(n_seeds=6, erosion=4.0, bin_width=0.1, window=[0.25, 4.0],
           rms_dev=float(np.sqrt((dev ** 2).mean())),
           max_abs_dev=float(np.abs(dev).max()))
json.dump(out, open("/home/combust/fmexplorer/criticality_tool/bridge/pilot3_gb1.json", "w"), indent=1)
print("PILOT3:", out, flush=True)

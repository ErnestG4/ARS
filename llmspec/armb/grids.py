"""Arm B checkpoint grids -- ONE definition used by the trainer and by B4 (extraction + analysis).
Base grid (B1a §2): every 10 steps over 0-500, Pythia's log steps {1, 2, 4, ..., 512}, every 25 over 500-3000, every 100
over 3000-5000 (q1_licence.grid). Amendment B1a-A8 (2026-09-28 ~14:00, pre-data for A2: A2 had not started): A2 adds
every 10 steps over 1000-2200 (Will: 'no-regret; disk only')."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import q1_licence as QL  # noqa: E402

STOPS = {"A0": 3000, "A1": 5000, "A2": 3000, "M0s1": 3000, "M0s2": 3000}
DENSE = {"A2": range(1000, 2201, 10)}


def arm_grid(arm, stop=None):
    g = set(int(x) for x in QL.grid(stop or STOPS[arm]))
    g |= set(t for t in DENSE.get(arm, ()) if t <= (stop or STOPS[arm]))
    return sorted(g)

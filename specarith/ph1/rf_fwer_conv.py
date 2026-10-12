"""Out-of-sample family-wise false-fail of rfwire's band calibration vs the number of calibration replicates (toy)."""
import sys

import numpy as np

sys.path.insert(0, "/home/combust/fmexplorer/criticality_tool/.claude/worktrees/ph6-xp/specarith/ph1")
import rfwire as R  # noqa: E402

rng = np.random.default_rng(7)
fam = {k: ("U", [(16, 7)] * 60) for k in "ABCD"}
fresh = R.calibrate_bands(rng, fam, 3000)["table"]
for reps in (200, 500, 1000, 2000):
    out = []
    for _ in range(3):
        b = R.calibrate_bands(rng, fam, reps)
        out.append(R.fwer_on(fresh, b["thresholds"]))
    print(reps, "reps: out-of-sample family-wise", [round(x, 3) for x in out], flush=True)

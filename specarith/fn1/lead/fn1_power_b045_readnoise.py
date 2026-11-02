# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 POST-HOC, descriptive: power of the beta 0.45 secondary at the post-hoc segment-noise scale (SEGNOISE_B045.json),
using the sealed power model's beta 0.45 slope and model SE (results/FN1_POWER.json) and the same rule (sum d^2 <= 26).
Not a sealed rule; nothing here relabels the sealed beta 0.45 FAIL."""
import json, sys
import numpy as np
pw = json.load(open(sys.argv[1]))["cells"]["0.45"]; sn = json.load(open(sys.argv[2]))["0.45"]
C = np.array(sorted(json.load(open(sys.argv[1]))["C"].values()))
assert len(C) == 9
rng = np.random.default_rng(20261102)
out = {"slope_b": pw["slope_b"], "model_SE": pw["model_SE"], "sealed_power_at_model": pw["power"]["model"]}
for nm, s in (("model_1x_recheck", 1.0), ("raw_segment_ratio", sn["noise_ratio_to_sealed_model"]),
              ("detrended_ratio", sn["noise_ratio_detrended"])):
    R = pw["slope_b"] * C[None, :] + pw["model_SE"] * s * rng.standard_normal((200_000, 9))
    d2 = ((R.argsort(1).argsort(1) - np.arange(9)) ** 2).sum(1)
    out[nm] = {"scale": s, "power": float((d2 <= 26).mean())}
json.dump(out, open(sys.argv[3], "w"), indent=1, sort_keys=True); print(json.dumps(out, indent=1))

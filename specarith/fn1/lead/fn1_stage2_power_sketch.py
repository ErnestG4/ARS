# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 DESIGN SKETCH (parametric, no data beyond the stage-1 read values): power of the proposed stage-2
primary (fresh slice (1e10, 1e11], beta 0.55, nine fields, sum d^2 <= 26) and of the proposed -7 displacement
prediction, at the stage-2 model SE and the stage-1 measured noise scales (1x, 1.71x detrended, 3.37x raw).
Model: R_F = a + b C_F (+ delta on -7 under H1) + sigma eps; b = stage-1 OLS slope at beta 0.55 (0.0455) and,
as a check, Chen's 1/log X at X = 1e11 (0.0395). delta = stage-1 linear residual of -7 (+0.0352).
-7 prediction (proposed): R_-7 > R_-8 AND R_-7 > R_-11 at beta 0.55 on the fresh slice."""
import json, math, sys
import numpy as np
rd = json.load(open(sys.argv[1])); ch = json.load(open(sys.argv[2]))
F = ["-7", "-8", "-11", "zi", "-19", "zw", "-43", "-67", "-163"]
C = np.array([math.log(7), math.log(8), math.log(11), math.log(16), math.log(19), math.log(27), math.log(43), math.log(67), math.log(163)])
delta = ch["beta_0.55"]["resid"]["-7"]
Rbar = float(np.mean([rd["R"][k]["0.55"] for k in F]))
K2 = 182016; se2 = Rbar * math.sqrt(2 / (0.6271633049515984 * K2))
rng = np.random.default_rng(20261103); REPS = 200_000
out = {"model_SE_stage2": se2, "Rbar": Rbar, "K": K2, "delta_-7": delta, "cells": {}}
for bname, b in (("ols_stage1", ch["beta_0.55"]["ols_slope_per_C"]), ("chen_1_over_log1e11", 1 / math.log(1e11))):
    for sname, s in (("1x", 1.0), ("1.71x_detrended", 1.708), ("3.37x_raw", 3.373)):
        E = rng.standard_normal((REPS, 9)) * se2 * s
        for h, d in (("H0_no_displacement", 0.0), ("H1_displacement_persists", delta)):
            R = b * C[None, :] + E; R[:, 0] += d
            d2 = ((R.argsort(1).argsort(1) - np.arange(9)) ** 2).sum(1)
            prim = float((d2 <= 26).mean())
            m7 = float(((R[:, 0] > R[:, 1]) & (R[:, 0] > R[:, 2])).mean())
            out["cells"][f"{bname}|{sname}|{h}"] = dict(primary_power=prim, minus7_pred_rate=m7)
json.dump(out, open(sys.argv[3], "w"), indent=1, sort_keys=True)
print("stage-2 model SE %.5f (stage-1 0.00615 scale: x%.2f)" % (se2, se2 / 0.006148))
for k, v in out["cells"].items(): print("%-58s primary %.3f   -7 pred %.3f" % (k, v["primary_power"], v["minus7_pred_rate"]))

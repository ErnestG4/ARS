# SPDX-License-Identifier: AGPL-3.0-or-later
"""FN1 stage-2 −7 arm: power under persistence for several trend models near −7. POST-HOC, DESCRIPTIVE, no bar; run
after witness run 3 showed W-persist (DELTA7 on the global slope) at 0.34 against the tabled 0.752 (flat trend +
DELTA7). Read-only; TOOLKIT §9.I. The read's own margin (flat null, design σ from witness run 3) and the read's seeded
draws (SEED_M7 + 1).

  python fn1_m7_persist_models.py READ1.json WITNESS_RUN3.json OUT_REL
"""
import math, os, sys
_H = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(_H, ".."), os.path.join(_H, "..", "..")]
import safeio
safeio.enforce()
import numpy as np
import fn1_read2 as R2

rd = safeio.read_json(sys.argv[1], expect_sha256="47c19dd26aaf3e892c01928f708c6b7032b61a5a8012dbdce7e3198dcfac4c76")
w = safeio.read_json(sys.argv[2])
sig = w["design_noise"]["sigma"]; m = R2.m7_margin(0.0, sig); C = R2.C; D7 = R2.CONST["DELTA7"]
e = R2.m7_draws(R2.SEED_M7 + 1) * sig
R = {f: rd["R"][f]["0.55"] for f in R2.FIELDS}; cv = w["convex_fit"]["curve"]
exc = R["-7"] - cv["-7"]
rows = [("flat trend + DELTA7 (tabled)", D7, D7),
        ("stage-1 local slope + DELTA7", D7 - 0.010141 * (C["-8"] - C["-7"]), D7 - 0.010141 * (C["-11"] - C["-7"])),
        ("stage-1 global slope + DELTA7", D7 - R2.CONST["B"]["0.55"] * (C["-8"] - C["-7"]),
         D7 - R2.CONST["B"]["0.55"] * (C["-11"] - C["-7"])),
        ("stage-1 configuration as observed", R["-7"] - R["-8"], R["-7"] - R["-11"]),
        ("convex curve + stage-1 excess over it", cv["-7"] - cv["-8"] + exc, cv["-7"] - cv["-11"] + exc)]
out = dict(label="−7 power under persistence, alternative trend models (post-hoc, descriptive)", margin=m, sigma=sig,
           models={nm: dict(gap_m8=a, gap_m11=b, power=float((np.minimum(a + e[:, 0] - e[:, 1], b + e[:, 0] - e[:, 2]) > m).mean()))
                   for nm, a, b in rows})
print("written", safeio.write_json(safeio.scratch(sys.argv[3]), out, overwrite=True))
for k, v in out["models"].items():
    print("%-40s gaps %+.4f %+.4f power %.3f" % (k, v["gap_m8"], v["gap_m11"], v["power"]))

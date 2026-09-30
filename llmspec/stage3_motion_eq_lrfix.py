"""Correct lr_integral and dW_fro_per_lr in banked equal-interval files written with 1.4B's LR peak hard-coded (the defect is
described in stage3_motion_eq.lr's docstring). Recomputes both from the raw dW_fro_rel (never affected) and the model's own
schedule. Idempotent (records 'lr_fixed'). Usage: LLMSPEC_MODEL=<model> stage3_motion_eq_lrfix.py"""
import numpy as np
from pathlib import Path
import mcfg, remote_st as R
import stage3_motion_eq as ME
ROOT = Path(__file__).resolve().parent
d = ROOT / "cache" / f"s3_motion_eq{mcfg.suffix()}"
NL = mcfg.get()["n_layer"]
for f in sorted(d.glob("*__*.npz")):
    z = dict(np.load(f))
    if "lr_fixed" in z:
        print(f.name, "already fixed"); continue
    a, b = [int(x[4:]) for x in f.stem.split("__")]
    lri = float(ME.lr(np.arange(a, b)).sum())
    old = float(z["lr_integral"])
    z["lr_integral"] = np.array(lri)
    for L in range(NL):
        for M in ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT"):
            z[f"L{L:02d}_{M}_dW_fro_per_lr"] = np.array(float(z[f"L{L:02d}_{M}_dW_fro_rel"]) / lri)
    z["lr_fixed"] = np.array(f"lr_integral {old:.6g} -> {lri:.6g} (own schedule)")
    R.durable_save(f, lambda p: np.savez(p, **z))
    print(f.name, f"lr_integral {old:.4f} -> {lri:.4f} (ratio {lri/old:.3f})")

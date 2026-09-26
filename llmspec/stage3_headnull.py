"""POST-HOC (2026-09-26 ~00:20): the within-head OUTPUT rotation null used in stage3_confounds2 (g) is DEGENERATE for the
head-concentration statistic: a head's share of a left singular vector is exactly invariant under rotations inside that
head's output space (observed == null to all digits). The test of "head concentration = head-norm differences" is an
independent random rotation of each head's INPUT side, W_h -> W_h O_h with O_h Haar 2048 x 2048. That keeps every
head's spectrum and norm and randomises the cross-head alignment of input directions. If the observed top-head mass of
the top-8 left vectors matches this null, the concentration is explained by per-head spectra/norms alone.
Step 143000, Q/K/V, 24 layers, 2 draws."""
import json
from pathlib import Path
import numpy as np, torch
import remote_st as R
ROOT = Path(__file__).resolve().parent
DEV = "cuda"
gen = torch.Generator(device=DEV).manual_seed(12)
def haar(n):
    Q, Rr = torch.linalg.qr(torch.randn((n, n), generator=gen, device=DEV, dtype=torch.float64))
    return Q * torch.sign(torch.diagonal(Rr))[None, :]
def top_head_mass(W):
    U = torch.linalg.eigh(W @ W.T)[1][:, -8:] ** 2
    return float(U.reshape(16, 128, 8).sum(1).max(0).values.mean())
idx = R.index("EleutherAI/pythia-1.4b", "step143000")
out = {"doc": __doc__, "layers": []}
for L in range(24):
    R.check_stop()
    a, _ = R.fetch(idx, f"gpt_neox.layers.{L}.attention.query_key_value.weight")
    qkv = torch.from_numpy(a.astype(np.float64)).to(DEV).reshape(16, 3, 128, 2048)
    rec = {"layer": L}
    for j, M in enumerate("QKV"):
        Wh = qkv[:, j]
        obs = top_head_mass(Wh.reshape(2048, 2048))
        nul = [top_head_mass(torch.stack([Wh[h] @ haar(2048) for h in range(16)]).reshape(2048, 2048)) for _ in range(2)]
        rec[M] = {"observed": obs, "input_rotation_null": float(np.mean(nul))}
    out["layers"].append(rec)
    print(L, {M: (round(rec[M]["observed"], 3), round(rec[M]["input_rotation_null"], 3)) for M in "QKV"}, flush=True)
for M in "QKV":
    o = np.mean([r[M]["observed"] for r in out["layers"]]); n = np.mean([r[M]["input_rotation_null"] for r in out["layers"]])
    out[M] = {"observed_mean": o, "null_mean": n}
    print(f"{M}: observed {o:.4f}  input-rotation null {n:.4f}  (isotropic 0.0625)")
(ROOT / "results" / "stage3_headnull.json").write_text(json.dumps(out, indent=1))

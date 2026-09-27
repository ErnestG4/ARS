"""B1b item (review 09-27, point 5): power of the sealed bulk null at Pythia-70M shapes. SYNTHETIC ONLY (pre-data).
Pooled-null witness exactly as stage3_witness (fp16-rounded Gaussians, same s3stats bulk band), at 70M shapes:
full Q/K/V/O 512x512 x 6 layers, MLP_IN/OUT 2048x512 x 6, per-head Q/K/V 64x512 x 48, per-head O 512x64 x 48.
R = 40 pools per cell type -> SD of bulk <r~>; minimum detectable departure (one-sided alpha 0.05, power 0.80, one pool
vs a precise witness mean) MDD = (1.645 + 0.842) * SD. Output: results/armb_bulk_power_70m.json."""
import json, sys
from pathlib import Path
import numpy as np, torch
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import s3stats as S
assert torch.cuda.is_available(); DEV = "cuda"
g = torch.Generator(device=DEV).manual_seed(20260928)
CELLS = {"full_sq": (6, 512, 512), "full_mlp": (6, 2048, 512), "head_qkv": (48, 64, 512), "head_O": (48, 512, 64)}
out = {"doc": __doc__}
for name, (k, m, n) in CELLS.items():
    rts = []
    for r in range(40):
        W = torch.randn((k, m, n), generator=g, device=DEV).half().double()
        sv = torch.linalg.svdvals(W).cpu().numpy()
        rts.append(S.local_stats(list(sv), "bulk")["rt"])
    sd = float(np.std(rts, ddof=1)); n_ratios = S.local_stats(list(sv), "bulk")["n_ratios"]
    out[name] = {"mean_rt": float(np.mean(rts)), "sd_rt": sd, "n_ratios_per_pool": n_ratios, "MDD": 2.487 * sd,
                 "tolerance": 0.010, "POWERED": bool(2.487 * sd <= 0.010)}
    print(name, out[name], flush=True)
(ROOT / "results" / "armb_bulk_power_70m.json").write_text(json.dumps(out, indent=1))

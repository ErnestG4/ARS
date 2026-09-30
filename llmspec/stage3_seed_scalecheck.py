"""Declared check for witness reuse in the seed leg (STAGE3_SEED_PREREG.md): each seed's mean entry rms per type at step 0
and step 143000 must lie within +-20% of the pythia-410m witness scales. Writes results/stage3_seed_scalecheck.json;
seeds that fail are listed and need their own witness before their null is read."""
import json
from pathlib import Path
import numpy as np
import mcfg
ROOT = Path(__file__).resolve().parent
w = json.loads((ROOT / "results" / "stage3_witness_pythia-410m.json").read_text())["scales"]
out = {}
for k in range(1, 10):
    m = f"pythia-410m-seed{k}"; res = {}
    for tag, rev in (("step0", "step0"), ("final", "step143000")):
        d = ROOT / "cache" / "s3" / m / rev
        if not (d / "DONE").exists():
            res[tag] = "MISSING"; continue
        for M in ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT"):
            r = float(np.mean([float(np.load(d / f"L{l:02d}.npz")[f"rms_{M}"]) for l in range(24)]))
            res[f"{tag}:{M}"] = {"rms": r, "ratio": r / w[tag][M]}
    ok = all(isinstance(v, dict) and 0.8 <= v["ratio"] <= 1.2 for v in res.values())
    out[m] = {"within_20pct": ok, "detail": res}
    print(m, "OK" if ok else "FAIL -> needs own witness")
(ROOT / "results" / "stage3_seed_scalecheck.json").write_text(json.dumps(out, indent=1))

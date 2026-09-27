"""Per-seed witness gate (STAGE3_SEED_PREREG.md, declared reuse): check the seed's mean entry rms per type at step 0 and
step 143000 against the pythia-410m witness scales (+-20%). Within -> reuse (nothing to do). Outside -> generate the seed's
OWN witness (stage3_witness.py), which mcfg.witness_suffix() then prefers. Decision recorded in
results/stage3_seed_witness_gate.json. Usage: stage3_seed_witness_gate.py <model>"""
import json, os, subprocess, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent
m = sys.argv[1]
w = json.loads((ROOT / "results" / "stage3_witness_pythia-410m.json").read_text())["scales"]
det = {}
for tag, rev in (("step0", "step0"), ("final", "step143000")):
    d = ROOT / "cache" / "s3" / m / rev
    assert (d / "DONE").exists(), f"{m} {rev} not extracted"
    for M in ("Q", "K", "V", "O", "MLP_IN", "MLP_OUT"):
        r = float(np.mean([float(np.load(d / f"L{l:02d}.npz")[f"rms_{M}"]) for l in range(24)]))
        det[f"{tag}:{M}"] = r / w[tag][M]
ok = all(0.8 <= v <= 1.2 for v in det.values())
fp = ROOT / "results" / "stage3_seed_witness_gate.json"
allr = json.loads(fp.read_text()) if fp.exists() else {}
allr[m] = {"within_20pct": ok, "ratios": det, "action": "reuse pythia-410m witness" if ok else "own witness generated"}
fp.write_text(json.dumps(allr, indent=1))
print(m, allr[m]["action"], {k: round(v, 3) for k, v in det.items() if not 0.8 <= v <= 1.2})
if not ok and not (ROOT / "results" / f"stage3_witness_{m}.json").exists() or (not ok and "--force" in sys.argv):
    subprocess.run([sys.executable, "-u", str(ROOT / "stage3_witness.py")], env=dict(os.environ, LLMSPEC_MODEL=m), check=True)

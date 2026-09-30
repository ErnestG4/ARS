"""Run ladder step 2 (stage3_ladder.py) on every VIOLATED cell of the active model's sealed-null table. Idempotent."""
import json, os, subprocess, sys
from pathlib import Path
import mcfg
ROOT = Path(__file__).resolve().parent
cells = json.loads((ROOT / "results" / f"stage3_null{mcfg.suffix()}.json").read_text())["cells"]
done = json.loads((ROOT / "results" / "stage3_ladder.json").read_text()) if (ROOT / "results" / "stage3_ladder.json").exists() else {}
viol = [c for c in cells if c["verdict"] == "VIOLATED"]
print(mcfg.name(), "VIOLATED cells:", [(c["type"], c["step"]) for c in viol])
for c in viol:
    if f"{mcfg.name()}|{c['type']}|{c['step']}" in done:
        continue
    subprocess.run([sys.executable, str(ROOT / "stage3_ladder.py"), c["type"], str(c["step"])], check=True)

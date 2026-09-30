"""Block until a seed's witness decision is final: the gate has recorded it AND (reuse, OR the seed's own witness file holds
all 10 types). stage3_witness writes its JSON after each type, so a partial own file must not be used. Honours STOP."""
import json, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent
m = sys.argv[1]
while True:
    if (ROOT / "STOP").exists():
        sys.exit(3)
    g = ROOT / "results" / "stage3_seed_witness_gate.json"
    if g.exists() and m in json.loads(g.read_text()):
        if json.loads(g.read_text())[m]["within_20pct"]:
            print(m, "reuse"); break
        w = ROOT / "results" / f"stage3_witness_{m}.json"
        if w.exists() and len(json.loads(w.read_text()).get("types", {})) == 10:
            print(m, "own witness complete"); break
    time.sleep(60)

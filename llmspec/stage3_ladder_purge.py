"""Remove a model's stage3_ladder.json entries (they were computed against a witness later replaced by the model's own)."""
import json, sys
from pathlib import Path
fp = Path(__file__).resolve().parent / "results" / "stage3_ladder.json"
d = json.loads(fp.read_text()); keep = {k: v for k, v in d.items() if not k.startswith(sys.argv[1] + "|")}
print("purged", len(d) - len(keep), "entries for", sys.argv[1]); fp.write_text(json.dumps(keep, indent=1))

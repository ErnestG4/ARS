"""Write armb/B4_SEAL.json: sha256 of every file b4_analyze.verify_seal() checks. Run only at a seal commit."""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import b4_analyze as B
man = {"files": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in B.SEAL_FILES}}
(HERE / "B4_SEAL.json").write_text(json.dumps(man, indent=1))
print(len(man["files"]), "files sealed")

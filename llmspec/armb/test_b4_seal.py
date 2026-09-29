"""The B4 seal check must HALT on a mismatch or a missing manifest (exit 4, nothing written) and pass on the real one.
Runs `b4_analyze.py q3` as a subprocess with $B4_SEAL pointing at: (a) the real manifest -> only the seal check is
exercised here via verify_seal(); (b) a copy with one hash altered; (c) a nonexistent path."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parent
PY = sys.executable
real = HERE / "B4_SEAL.json"
ok = True
r = subprocess.run([PY, "-c", "import sys; sys.path.insert(0,'armb'); import b4_analyze as B; B.verify_seal()"], cwd=ROOT,
                   capture_output=True, text=True)
good = r.returncode == 0 and "seal check OK" in r.stdout; ok &= good
print("real manifest:", "OK" if good else "BAD", r.stdout.strip()[-60:])
man = json.loads(real.read_text()); k = "armb/b4_analyze.py"; man["files"][k] = "0" * 64
bad_fp = Path(tempfile.mkdtemp()) / "tampered.json"; bad_fp.write_text(json.dumps(man))
before = {p.name: p.stat().st_mtime for p in (ROOT / "results").glob("armb_b4_*.json")}
for name, path in (("tampered", str(bad_fp)), ("missing", "/nonexistent/B4_SEAL.json")):
    r = subprocess.run([PY, "armb/b4_analyze.py", "q3"], cwd=ROOT, env=dict(os.environ, B4_SEAL=path), capture_output=True, text=True)
    after = {p.name: p.stat().st_mtime for p in (ROOT / "results").glob("armb_b4_*.json")}
    good = r.returncode == 4 and "SEAL CHECK FAILED" in r.stdout and after == before; ok &= good
    print(f"{name} manifest: exit {r.returncode}, nothing written: {after == before} ->", "OK (halts)" if good else "BAD")
print("SEAL TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)

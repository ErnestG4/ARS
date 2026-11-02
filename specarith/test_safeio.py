# SPDX-License-Identifier: AGPL-3.0-or-later
"""Red-path test for safeio (TOOLKIT §9.I). Runs in a subprocess so enforce() cannot leak into the caller.

  python test_safeio.py        -> prints SAFEIO_TEST_PASS True/False

Cases: (1) read of a committed file works; (2) write to a committed path raises and leaves it byte-identical;
(3) the FN1 2026-11-02 incident — a module whose import-time code writes to sys.argv[1] while sys.argv[1] is a
committed file — raises; (4) write to scratch works; (5) write via os.replace into the repo raises; (6) symlink in
scratch pointing into the repo raises; (7) overwrite without overwrite=True raises; (8) numpy.save into the repo
raises.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHILD = r'''
import os, sys, json, hashlib, importlib.util
sys.path.insert(0, HERE)
import safeio
safeio.enforce()
res = {}
target = os.path.join(HERE, "OPEN_LEADS.md")
before = hashlib.sha256(open(target, "rb").read()).hexdigest()
res["1_read_committed"] = len(open(target).read()) > 0
def raises(fn):
    try:
        fn(); return False
    except (PermissionError, FileExistsError):
        return True
res["2_write_committed_raises"] = raises(lambda: open(target, "w"))
res["2_unchanged"] = hashlib.sha256(open(target, "rb").read()).hexdigest() == before
mod = os.path.join(SCR, "sidefx_mod.py")
with open(mod, "w") as f:
    f.write("import sys, json\njson.dump({}, open(sys.argv[1], 'w'))\n")
sys.argv = ["x", target]
spec = importlib.util.spec_from_file_location("sidefx_mod", mod)
res["3_import_side_effect_raises"] = raises(lambda: spec.loader.exec_module(importlib.util.module_from_spec(spec)))
res["3_unchanged"] = hashlib.sha256(open(target, "rb").read()).hexdigest() == before
p = safeio.write_json(os.path.join(SCR, "ok.json"), {"a": 1})
res["4_scratch_write"] = json.load(open(p)) == {"a": 1}
res["5_replace_into_repo_raises"] = raises(lambda: os.replace(p, os.path.join(HERE, "should_not_exist.json")))
link = os.path.join(SCR, "link_to_repo")
os.symlink(HERE, link)
res["6_symlink_escape_raises"] = raises(lambda: open(os.path.join(link, "evil.txt"), "w"))
res["7_overwrite_needs_flag"] = raises(lambda: safeio.write_json(p, {"b": 2}))
import numpy as np
res["8_numpy_save_repo_raises"] = raises(lambda: np.save(os.path.join(HERE, "evil.npy"), np.zeros(2)))
res["no_files_created_in_repo"] = not any(os.path.exists(os.path.join(HERE, n)) for n in ("should_not_exist.json", "evil.npy"))
print(json.dumps(res))
print("SAFEIO_TEST_PASS", all(res.values()))
'''


def main():
    root = os.path.expanduser("~/tmp/claude")
    os.makedirs(root, exist_ok=True)
    scr = tempfile.mkdtemp(prefix="safeio_test_", dir=root)
    code = f"HERE = {HERE!r}\nSCR = {scr!r}\n" + CHILD
    env = dict(os.environ, SPECARITH_SCRATCH=scr)
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    sys.stdout.write(r.stdout + r.stderr)
    return 0 if "SAFEIO_TEST_PASS True" in r.stdout else 1


if __name__ == "__main__":
    sys.exit(main())

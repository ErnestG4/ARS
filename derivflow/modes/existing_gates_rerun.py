#!/usr/bin/env python3
"""Re-run the existing derivflow gates UNCHANGED (BRIEF ML: Hermite self-map, lattice gate, picket
fence / Hermite-through-reference, Gate D) and record their verdicts. COMMITTED GENERATOR of
derivflow/modes/existing_gates_rerun.json.

The gate scripts write their JSON to hard-coded paths relative to the cwd, so they are executed
in a scratch cwd (derivflow/modes/gates_scratch/derivflow/...) and the frozen committed artifacts
are never rewritten. Each re-run's numbers are compared with the committed artifact's numbers:
a changed number would mean the instrument moved since it was certified.
"""
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modes_common as M                     # noqa: E402

SCRATCH = os.path.join(HERE, "gates_scratch")
PY = sys.executable


def numbers(o, path="", out=None):
    out = {} if out is None else out
    if isinstance(o, dict):
        for k, v in o.items():
            numbers(v, f"{path}/{k}", out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            numbers(v, f"{path}[{i}]", out)
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        out[path] = o
    return out


def compare(new, old, skip=("runtime",)):
    a, b = numbers(new), numbers(old)
    diffs = []
    for k in set(a) | set(b):
        if any(s in k for s in skip):
            continue
        if k not in a or k not in b:
            diffs.append((k, a.get(k), b.get(k)))
        elif a[k] != b[k] and not (abs(a[k] - b[k]) <= 1e-12 * max(abs(a[k]), abs(b[k]), 1e-300)):
            diffs.append((k, a[k], b[k]))
    return diffs


if __name__ == "__main__":
    t0 = time.time()
    os.makedirs(os.path.join(SCRATCH, "derivflow"), exist_ok=True)
    res = {}
    env = dict(os.environ, PYTHONPATH=M.DF + os.pathsep + M.ROOT)
    for label, script, artifact in (
            ("hermite_selfmap", "track0_harness.py", "track0_hermite_gate.json"),
            ("reference_v2_gates(lattice+hermite-through-reference)", "reference_v2_gates.py", "reference_v2_gates.json")):
        t = time.time()
        r = subprocess.run([PY, os.path.join(M.DF, script)], cwd=SCRATCH, env=env, capture_output=True, text=True)
        new = json.load(open(os.path.join(SCRATCH, "derivflow", artifact)))
        old = json.load(open(os.path.join(M.DF, artifact)))
        d = compare(new, old)
        res[label] = {"exit": r.returncode, "verdict": new.get("verdict"),
                      "numbers_differing_from_committed": len(d), "first_diffs": d[:10],
                      "stdout_tail": r.stdout.strip().splitlines()[-6:], "runtime_s": time.time() - t}
    t = time.time()
    r = subprocess.run([PY, os.path.join(M.ROOT, "verify_knownanswer.py")], cwd=SCRATCH, env=env,
                       capture_output=True, text=True)
    res["gate_D_knownanswer"] = {"exit": r.returncode, "stdout_tail": r.stdout.strip().splitlines()[-8:],
                                 "runtime_s": time.time() - t}
    shutil.rmtree(SCRATCH)
    ok = all(v["exit"] == 0 for v in res.values()) and \
        all(v.get("numbers_differing_from_committed", 0) == 0 for v in res.values())
    res["ALL_GATES_GREEN_AND_UNCHANGED"] = bool(ok)
    res["runtime_s"] = time.time() - t0
    json.dump(res, open(os.path.join(HERE, "existing_gates_rerun.json"), "w"), indent=1)
    for k, v in res.items():
        if isinstance(v, dict):
            print(f"{k}: exit={v['exit']} verdict={v.get('verdict')} diffs={v.get('numbers_differing_from_committed')}")
    print("ALL_GATES_GREEN_AND_UNCHANGED:", ok)
    sys.exit(0 if ok else 1)

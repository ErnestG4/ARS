"""RQ1-c post-hoc ruling (Will, 2026-10-29): double-read equivalence on all non-timing fields.

  python rq1c_strip_compare.py READ1_JSON READ2_JSON OUT_DIR

Removes a fixed list of timing fields (by path; nothing else), canonicalises (sorted keys, separators (",", ":"),
Python's shortest round-trip float repr, ensure_ascii), writes OUT_DIR/read{1,2}.stripped.json and their sha256s to
OUT_DIR/STRIPPED_SHA256.txt, and exits 0 only if the two stripped files are byte-identical. Prints no value.

Timing fields of `rq1c_read.py read` (the only calls to a clock in that mode: Cost.add's time.process_time() and the
final cpu_core_h; `wall_s` belongs to zw34d mode and is listed so that its absence is checked):
  cost[*].cpu_s     cumulative CPU seconds at each stage
  cost[*].ratio     cpu_s / model_s
  cpu_core_h        total CPU core-hours
  wall_s            (zw34d mode only; must be absent here)
Kept: cost[*].stage and cost[*].model_s (the cost model, deterministic).
"""
import hashlib
import json
import os
import sys

STRIP_COST = ("cpu_s", "ratio")
STRIP_TOP = ("cpu_core_h", "wall_s")


def strip(d):
    d = dict(d)
    for k in STRIP_TOP:
        d.pop(k, None)
    d["cost"] = [{k: v for k, v in c.items() if k not in STRIP_COST} for c in d["cost"]]
    return d


def canon(d):
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


def main(r1, r2, out):
    os.makedirs(out, exist_ok=True)
    a, b = json.load(open(r1)), json.load(open(r2))
    assert "wall_s" not in a and "wall_s" not in b
    assert all(set(c) == {"stage", "cpu_s", "model_s", "ratio"} for c in a["cost"] + b["cost"])
    lines = []
    for name, d in (("read1", a), ("read2", b)):
        raw = canon(strip(d))
        p = os.path.join(out, f"{name}.stripped.json")
        open(p, "wb").write(raw)
        lines.append(f"{hashlib.sha256(raw).hexdigest()}  {name}.stripped.json")
    open(os.path.join(out, "STRIPPED_SHA256.txt"), "w").write("\n".join(lines) + "\n")
    same = lines[0].split()[0] == lines[1].split()[0]
    print("\n".join(lines))
    print("stripped files identical:", same)
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))

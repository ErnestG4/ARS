"""Where do the 15,195 railed Brody q values LIVE, and is the mass concentrated?
COMMITTED GENERATOR of gate_census/rail_concentration.json.

The owner's question before any migration decision: if R-178's numbers are
representative -- three cell datasets at ~100% rail -- the mass may sit in a few
programs whose conclusions were already drawn WITH the rail known, which would
make this far smaller than 37.9% suggests.
"""
import json, os, glob
from collections import defaultdict

ROOT = "/home/combust/fmexplorer/criticality_tool"
TOL = 1e-3


def walk(o, path, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if "brody_q" in k.lower() and isinstance(v, (int, float)) \
                    and not isinstance(v, bool):
                out.append((path, k, float(v)))
            walk(v, path, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, path, out)


def main():
    files = [f for pat in ("**/*.json", "**/*.jsonl")
             for f in glob.glob(os.path.join(ROOT, pat), recursive=True)
             if "/.git/" not in f]
    hits = []
    for f in files:
        try:
            txt = open(f, "r", errors="replace").read()
        except OSError:
            continue
        if "brody_q" not in txt:
            continue
        rel = os.path.relpath(f, ROOT)
        try:
            if f.endswith(".jsonl"):
                for line in txt.splitlines():
                    if line.strip():
                        try:
                            walk(json.loads(line), rel, hits)
                        except json.JSONDecodeError:
                            pass
            else:
                walk(json.loads(txt), rel, hits)
        except json.JSONDecodeError:
            pass

    per = defaultdict(lambda: [0, 0])
    unbounded_present = defaultdict(int)
    for path, k, v in hits:
        if "unbounded" in k.lower():
            unbounded_present[path] += 1
            continue
        per[path][0] += 1
        if abs(v) <= TOL:
            per[path][1] += 1
    rows = sorted(((p, n, r) for p, (n, r) in per.items()), key=lambda x: -x[2])
    tot_n = sum(n for _, n, _ in rows)
    tot_r = sum(r for _, _, r in rows)
    cum, top_files = 0, []
    for p, n, r in rows:
        if r == 0:
            continue
        cum += r
        top_files.append(dict(file=p, n=n, railed=r, frac=r / n,
                              cum_share=cum / tot_r,
                              has_unbounded_companion=bool(unbounded_present.get(p))))
    out = dict(total_values=tot_n, total_railed=tot_r,
               files_with_any_rail=len(top_files), per_file=top_files)
    print(f"total brody_q values {tot_n:,}   railed {tot_r:,} ({tot_r/tot_n:.1%})")
    print(f"files containing a railed value: {len(top_files)}\n")
    print(f"{'railed':>7} {'of':>7} {'frac':>6} {'cum%':>6} {'unb?':>5}  file")
    for r in top_files[:14]:
        print(f"{r['railed']:>7,} {r['n']:>7,} {r['frac']:>6.1%} "
              f"{r['cum_share']:>6.1%} {'yes' if r['has_unbounded_companion'] else '  -':>5}  {r['file']}")
    n80 = next((i + 1 for i, r in enumerate(top_files) if r["cum_share"] >= 0.8), len(top_files))
    out["files_covering_80pct"] = n80
    print(f"\n  {n80} file(s) carry 80% of all railed values "
          f"(of {len(top_files)} with any)")
    withunb = sum(r["railed"] for r in top_files if r["has_unbounded_companion"])
    out["railed_with_unbounded_companion"] = withunb
    print(f"  {withunb:,} of {tot_r:,} ({withunb/tot_r:.1%}) sit in artifacts that ALSO "
          "carry an unbounded-estimator value —\n  for those the repair is already "
          "banked alongside and needs no recompute, only a read-through change")
    json.dump(out, open(f"{ROOT}/gate_census/rail_concentration.json", "w"), indent=1)


if __name__ == "__main__":
    main()

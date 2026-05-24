"""
cross_substrate/lzeros_split.py — one-shot: split the pooled L-zeros.jsonl into
ζ / Dirichlet / EC substrate files so the visuals don't plot a misleading bimodal
median (open thread, PROGRESS_REPORT §6).

The 8 pooled cells span two universality readings: ζ → GUE (q≈1), Dirichlet/EC →
Poisson-leaning (q≈0). The Poisson reading on Dirichlet/EC is CONFOUNDED by
cross-conductor pooling (positions_lzeros pools many conductors' zeros via
pool_unfolded) — superposing independent L-function spectra drives toward Poisson
regardless of each one's true symmetry class (Sp/U/SO all repel). Carried as a
caveat on those cells, NOT interpreted. (phase34c; false_positive_equivalence_classes.)

Preserves the already-banked matched-leg values byte-for-byte (no recompute);
only relabels substrate + routes to per-class files. Removes the pooled file.
"""
from __future__ import annotations

import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
SRC = os.path.join(COORD, "L-zeros.jsonl")

POOL_CAVEAT = ("Poisson-leaning reading (q≈0, BRρ≈0) is confounded by cross-conductor "
               "pooling: positions_lzeros superposes many conductors' zeros, and "
               "superposed independent spectra → Poisson regardless of each L-function's "
               "true symmetry class (Sp/U/SO all repel). Single-conductor extraction "
               "needed to read the true class. See phase34c / false_positive_equivalence_classes.")


def _classify(cell_id):
    if cell_id.startswith("zeta"):
        return "L-zeros-zeta", None
    if cell_id.startswith("dirichlet"):
        return "L-zeros-dirichlet", POOL_CAVEAT
    if cell_id.startswith("ec"):
        return "L-zeros-ec", POOL_CAVEAT
    return "L-zeros-other", None


def main():
    if not os.path.exists(SRC):
        print(f"already split (no {os.path.basename(SRC)}); nothing to do")
        return
    buckets = {}
    n_in = 0
    for line in open(SRC):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        n_in += 1
        sub, caveat = _classify(r["cell_id"])
        r["substrate"] = sub
        if caveat:
            r.setdefault("extraction_audit", {})["class_caveat"] = caveat
        buckets.setdefault(sub, []).append(r)

    n_out = 0
    for sub, recs in sorted(buckets.items()):
        path = os.path.join(COORD, f"{sub}.jsonl")
        with open(path, "w") as f:
            for r in recs:
                f.write(json.dumps(r) + "\n")
        n_out += len(recs)
        print(f"  {sub:20s} {len(recs)} cells → {os.path.basename(path)}")

    assert n_out == n_in, f"cell count mismatch: {n_in} in, {n_out} out"
    os.remove(SRC)
    print(f"→ split {n_in} cells into {len(buckets)} files; removed {os.path.basename(SRC)}")


if __name__ == "__main__":
    main()

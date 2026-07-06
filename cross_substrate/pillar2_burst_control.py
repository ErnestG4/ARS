"""
cross_substrate/pillar2_burst_control.py — systematic burst-control of every banked pillar-2 instance.

Pillar-2 = per-cell EXTRINSIC selectivity-quality ↔ universality-class (ks_gue). Question: is the link
genuine selectivity↔class, or is it mediated by intrinsic burstiness (especially in spatial-coding circuits
where place/grid cells happen to be bursty)? Computes the PARTIAL Spearman correlation controlling for
burst_frac on BOTH sides (rank residuals; corr(selectivity, ks_gue | burst)).

Substrates: V1 (OSI, drifting_gratings), 000638 (MEC/CA1 spatial_info), hc-3 (EC/CA3 spatial_info; pending
the ele+clu re-run). Out: stdout table (banked findings_log; figures P_pillar2_burst_control.png).
"""
from __future__ import annotations

import json
import os

import numpy as np
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
load = lambda n: [json.loads(l) for l in open(os.path.join(COORD, n)) if l.strip()] if os.path.exists(os.path.join(COORD, n)) else []


def partial(x, y, z):
    rx = stats.rankdata(x); ry = stats.rankdata(y); rz = stats.rankdata(z)
    bx = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    by = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return stats.pearsonr(bx, by)


def block(label, rows, sel_name):
    if len(rows) < 12:
        return {"label": label, "n": len(rows), "note": "underpowered"}
    a = np.array(rows); sel, bf, ks = a[:, 0], a[:, 1], a[:, 2]
    r_raw, p_raw = stats.spearmanr(sel, ks)
    r_sb, p_sb = stats.spearmanr(sel, bf)
    r_bk, p_bk = stats.spearmanr(bf, ks)
    r_part, p_part = partial(sel, ks, bf)
    return {"label": label, "sel": sel_name, "n": len(rows),
            "raw": (r_raw, p_raw), "sel_burst": (r_sb, p_sb),
            "burst_ks": (r_bk, p_bk), "partial": (r_part, p_part),
            "retained": float(r_part / r_raw) if r_raw else None}


def v1_rows():
    out = []
    for r in load("v1-burst-osi.jsonl"):
        o = r.get("osi"); k = r["axes_computed"].get("I.5q_ks_gue_med"); b = r.get("burst_frac")
        if None not in (o, k, b) and all(np.isfinite(x) for x in (o, k, b)):
            out.append((o, b, k))
    return out


def dr_rows(region):
    cells = {(c["session"], c["unit"]): c for c in load("dr-port-cell.jsonl")}
    pf = load("dr-placefields.jsonl")
    out = []
    for p in pf:
        if p["region"] != region or p.get("cell_type") != "excitatory":
            continue
        c = cells.get((p["session"], p["unit"]))
        if c is None:
            continue
        bf = (c.get("burst") or {}).get("burst_frac")
        si = p["spatial_info_bits_per_spike"]; ks = p["ks_gue_med"]
        if None not in (si, bf, ks) and all(np.isfinite(x) for x in (si, bf, ks)):
            out.append((si, bf, ks))
    return out


def buzsaki_rows():
    """Buzsáki CA1 cycle-2a: spatial_coherence ↔ ks_gue (Maze-Awake), controlled for burst_index.
    Joins port-cell (ks_gue, Maze-Awake) + placefields (spatial_coherence) + selectivity (burst_index)."""
    pc = {(c["session"], c["unit"]): c for c in load("buzsaki-port-cell.jsonl")
          if c.get("natural_cell") == "Maze-Awake" and c.get("cell_type") == "excitatory"}
    pf = {(c["session"], c["unit"]): c for c in load("buzsaki-placefields.jsonl")
          if c.get("cell_type") == "excitatory"}
    sel = {(c["session"], c["unit"]): c for c in load("buzsaki-selectivity.jsonl")
           if c.get("cell_type") == "excitatory"}
    keys = set(pc) & set(pf) & set(sel)
    out = []
    for k in keys:
        sc = pf[k].get("spatial_coherence"); bi = sel[k].get("burst_index")
        ks = pc[k]["axes_computed"].get("I.5q_ks_gue_med")
        if None not in (sc, bi, ks) and all(np.isfinite(x) for x in (sc, bi, ks)):
            out.append((sc, bi, ks))
    return out


def hc3_rows(region):
    cells = {(c["topdir"], c.get("ele"), c.get("clu")): c for c in load("hc3-port-cell.jsonl")}
    pf = load("hc3-placefields.jsonl")
    if not pf:
        return []
    has_keys = "ele" in pf[0]
    if not has_keys:
        return []  # placefields lacks ele+clu, can't match
    out = []
    for p in pf:
        if p["region"] != region or p.get("cell_type", p.get("celltype")) != "excitatory":
            continue
        c = cells.get((p["topdir"], p.get("ele"), p.get("clu")))
        if c is None:
            continue
        bf = (c.get("burst") or {}).get("burst_frac")
        si = p["spatial_info_bits_per_spike"]; ks = p["ks_gue_med"]
        if None not in (si, bf, ks) and all(np.isfinite(x) for x in (si, bf, ks)):
            out.append((si, bf, ks))
    return out


def fmt(d):
    if "note" in d:
        return f"  {d['label']:30s} n={d['n']:4d}  {d['note']}"
    r, p = d["raw"]; sb, _ = d["sel_burst"]; bk, _ = d["burst_ks"]; pr, pp = d["partial"]
    ret = d["retained"]
    return (f"  {d['label']:30s} n={d['n']:4d}  raw={r:+.3f}***  sel↔burst={sb:+.3f}  "
            f"burst↔ks={bk:+.3f}  PARTIAL(|burst)={pr:+.3f} p={pp:.1e}  retained={ret:.0%}" +
            ("  <CLEAN>" if abs(sb) < 0.1 else ""))


def main():
    print("=" * 100)
    print("PILLAR-2 BURST-CONTROL — does the per-cell extrinsic selectivity↔class link survive")
    print("controlling for intrinsic burstiness? Partial Spearman corr(selectivity, ks_gue | burst).")
    print("=" * 100 + "\n")
    print("V1 (Allen VISp / drifting_gratings, OSI):")
    print(fmt(block("OSI ↔ ks_gue", v1_rows(), "OSI")))
    print("\nBuzsáki CA1 (tetrode, Maze; spatial_coherence ↔ ks_gue, controlled for burst_index):")
    print(fmt(block("CA1 spatial_coherence ↔ ks_gue", buzsaki_rows(), "spatial_coherence")))
    print("\n000638 (NPx, track task; spatial_info):")
    for reg in ("MEC", "CA1", "DG"):
        print(fmt(block(f"{reg} spatial_info ↔ ks_gue", dr_rows(reg), "spatial_info")))
    print("\nhc-3 (tetrode, task; spatial_info):")
    for reg in ("EC", "CA3", "DG"):
        rows = hc3_rows(reg)
        if not rows:
            print(f"  {reg + ' spatial_info ↔ ks_gue':30s} (waiting on hc3-placefields ele+clu re-run)")
        else:
            print(fmt(block(f"{reg} spatial_info ↔ ks_gue", rows, "spatial_info")))
    print("\nKey: <CLEAN> = extrinsic axis is burst-orthogonal (sel↔burst<0.1). retained = partial/raw.")


if __name__ == "__main__":
    main()

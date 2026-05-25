"""
cross_substrate/buzsaki_port_analysis.py — the 4 framework-port goals for CA1.

Reads buzsaki-port-pop.jsonl + buzsaki-port-cell.jsonl + buzsaki-selectivity.jsonl and reports:
  G1 FRAGMENTATION HIERARCHY — do the 3 observables show Allen's structural-high(corr-eig)/biological(avl)/
     structural-low(sync) split? mean q per observable + ordering; verdict GENERALISES / DIVERGES.
  G2 H1-ANALOGUE — which CA1 selectivity property (spatial_info / theta_mrl / burst_index / rate) correlates
     with per-cell ks_gue (Maze-Awake)? Spearman ρ overall + by cell-type. (OSI↔ks_gue analogue search.)
  G3 STATE/EPOCH — named biological contrasts (PRE-NonREM vs POST-NonREM = NonREM consolidation; PRE-REM vs
     POST-REM; Maze-Awake vs Awake-in-sleep; all-NonREM vs all-REM) on the structured observable + corr-eig;
     marginal η² on EPOCH and STATE with the structural-confound flagged. Effects warranting rate-match noted.
  G4 CELL-TYPE — pyramidal(exc) vs interneuron(inh): population position + per-cell ks_gue.

Out: prints + figure P_buzsaki_port.png. Run: --run.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict

import numpy as np
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
OBS = ["corr-eig", "avl-onset", "sync-event"]
NCELL_ORDER = ["PRE-NonREM", "PRE-REM", "Maze-Awake", "POST-NonREM", "POST-REM", "Awake-in-sleep"]


def _load(name):
    p = os.path.join(COORD, name)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def _epoch(nc):
    return nc.split("-")[0]


def _state(nc):
    return nc.split("-", 1)[1] if "-" in nc else nc


def run():
    pop = _load("buzsaki-port-pop.jsonl")
    cell = _load("buzsaki-port-cell.jsonl")
    sel = _load("buzsaki-selectivity.jsonl")
    print(f"BUZSAKI PORT ANALYSIS — pop={len(pop)}, per-cell={len(cell)}, selectivity={len(sel)}; "
          f"{len(set(r['session'] for r in pop))} session(s)\n")

    def q(r):
        return r["axes_computed"].get("I.8_brody_q")

    # ---- G1 fragmentation hierarchy ----
    print("(G1) FRAGMENTATION HIERARCHY — mean Brody q per observable (cell_type=all, across natural cells):")
    for o in OBS:
        v = [q(r) for r in pop if r["aggregation"] == o and r["cell_type"] == "all" and isinstance(q(r), float)]
        if v:
            print(f"     {o:11s} q = {np.mean(v):.3f} ± {np.std(v):.3f}  (n={len(v)})  [Allen: "
                  f"{'corr-eig 0.89' if o=='corr-eig' else 'avl 0.61' if o=='avl-onset' else 'sync 0.00'}]")
    cells = defaultdict(dict)
    for r in pop:
        if r["cell_type"] == "all":
            cells[(r["session"], r["natural_cell"])][r["aggregation"]] = q(r)
    full = [c for c in cells.values() if all(isinstance(c.get(o), float) for o in OBS)]
    if full:
        canon = sum(1 for c in full if c["corr-eig"] > c["avl-onset"] > c["sync-event"])
        print(f"     canonical corr-eig>avl>sync ordering: {canon}/{len(full)} natural-cell×session "
              f"({100*canon/len(full):.0f}%) ⇒ {'GENERALISES' if canon/len(full) > 0.7 else 'DIVERGES'}\n")

    # ---- G2 H1-analogue ----
    print("(G2) H1-ANALOGUE — Spearman ρ(per-cell ks_gue [Maze-Awake], selectivity property):")
    ks = {(r["session"], r["unit"]): r["axes_computed"].get("I.5q_ks_gue_med")
          for r in cell if r["natural_cell"] == "Maze-Awake"}
    selmap = {(r["session"], r["unit"]): r for r in sel}
    props = ["spatial_info", "theta_mrl", "burst_index", "rate"]
    merged = [(ks[k], selmap[k]) for k in ks if k in selmap and isinstance(ks[k], float)]
    print(f"     merged {len(merged)} cells (ks_gue ∩ selectivity)")
    for pr in props:
        pairs = [(g, s[pr]) for g, s in merged if isinstance(s.get(pr), float)]
        if len(pairs) >= 8:
            rho, p = stats.spearmanr([a for a, _ in pairs], [b for _, b in pairs])
            print(f"     ks_gue vs {pr:12s}: ρ={rho:+.3f} (p={p:.3g}, n={len(pairs)})"
                  f"{'  ← H1-ANALOGUE CANDIDATE' if abs(rho) > 0.3 and p < 0.05 else ''}")
    # by cell-type (excitatory only — the place-coding population)
    for pr in ["spatial_info", "theta_mrl"]:
        pairs = [(g, s[pr]) for g, s in merged if s.get("cell_type") == "excitatory" and isinstance(s.get(pr), float)]
        if len(pairs) >= 8:
            rho, p = stats.spearmanr([a for a, _ in pairs], [b for _, b in pairs])
            print(f"     [exc only] ks_gue vs {pr:12s}: ρ={rho:+.3f} (p={p:.3g}, n={len(pairs)})")
    print()

    # ---- G3 state/epoch named contrasts ----
    print("(G3) STATE/EPOCH — named biological contrasts on each observable (mean q, all cell_type):")
    by = defaultdict(lambda: defaultdict(list))
    for r in pop:
        if r["cell_type"] == "all" and isinstance(q(r), float):
            by[r["aggregation"]][r["natural_cell"]].append(q(r))
    contrasts = [("NonREM consolidation", "PRE-NonREM", "POST-NonREM"),
                 ("REM consolidation", "PRE-REM", "POST-REM"),
                 ("wake state", "Maze-Awake", "Awake-in-sleep")]
    for o in OBS:
        d = by[o]
        line = []
        for lab, a, b in contrasts:
            if d.get(a) and d.get(b):
                line.append(f"{lab}: {np.mean(d[a]):.2f}→{np.mean(d[b]):.2f}")
        print(f"     {o:11s} " + "  |  ".join(line) if line else f"     {o:11s} (insufficient)")
    # marginal eta2 with confound caveat (avl-onset = the structured observable)
    sub = [r for r in pop if r["aggregation"] == "avl-onset" and r["cell_type"] == "all" and isinstance(q(r), float)]
    if len(sub) >= 6:
        def _eta2(vals, grp):
            vals = np.asarray(vals); gr = grand = vals.mean()
            sst = np.sum((vals - grand) ** 2)
            if sst < 1e-12:
                return 0.0
            ssb = sum(m.size * (m.mean() - grand) ** 2 for m in
                      (vals[np.array(grp) == g] for g in set(grp)))
            return float(ssb / sst)
        vals = [q(r) for r in sub]
        print(f"     [avl-onset marginal η² — CONFOUND-FLAGGED] epoch={_eta2(vals,[_epoch(r['natural_cell']) for r in sub]):.2f} "
              f"state={_eta2(vals,[_state(r['natural_cell']) for r in sub]):.2f} "
              f"(marginal mixes confounded conditions; named contrasts above are the clean reads)")
    print("     → effects that appear warrant the rate-match de-confound (buzsaki_ratematch, next).\n")

    # ---- G4 cell-type ----
    print("(G4) CELL-TYPE — population q by cell_type, and per-cell ks_gue exc vs inh:")
    for o in OBS:
        ev = [q(r) for r in pop if r["aggregation"] == o and r["cell_type"] == "excitatory" and isinstance(q(r), float)]
        iv = [q(r) for r in pop if r["aggregation"] == o and r["cell_type"] == "inhibitory" and isinstance(q(r), float)]
        if ev and iv:
            print(f"     {o:11s} exc q={np.mean(ev):.3f} (n={len(ev)})  vs  inh q={np.mean(iv):.3f} (n={len(iv)})")
    ek = [r["axes_computed"].get("I.5q_ks_gue_med") for r in cell if r["cell_type"] == "excitatory"]
    ik = [r["axes_computed"].get("I.5q_ks_gue_med") for r in cell if r["cell_type"] == "inhibitory"]
    ek = [x for x in ek if isinstance(x, float)]; ik = [x for x in ik if isinstance(x, float)]
    if ek and ik:
        print(f"     per-cell ks_gue: exc med={np.median(ek):.3f} (n={len(ek)})  vs  inh med={np.median(ik):.3f} (n={len(ik)})")
    print("\nFlag, don't interpret — verdicts are Will's.")
    _figure(pop, merged)


def _figure(pop, merged):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    # G1: q by natural cell, line per observable
    for o in OBS:
        d = defaultdict(list)
        for r in pop:
            if r["aggregation"] == o and r["cell_type"] == "all" and isinstance(r["axes_computed"].get("I.8_brody_q"), float):
                d[r["natural_cell"]].append(r["axes_computed"]["I.8_brody_q"])
        ncs = [n for n in NCELL_ORDER if n in d]
        a1.plot(range(len(ncs)), [np.mean(d[n]) for n in ncs], "o-", label=o, ms=5)
    a1.set_xticks(range(len([n for n in NCELL_ORDER if any(r['natural_cell']==n for r in pop)])))
    a1.set_xticklabels([n for n in NCELL_ORDER if any(r['natural_cell']==n for r in pop)], rotation=35, ha="right", fontsize=7)
    a1.set_ylabel("Brody q"); a1.set_title("G1/G3: observable q by natural cell (CA1)"); a1.legend(fontsize=7); a1.grid(alpha=0.2)
    # G2: ks_gue vs spatial_info
    if merged:
        xs = [s.get("spatial_info") for _, s in merged]; ys = [g for g, _ in merged]
        ok = [(x, y) for x, y in zip(xs, ys) if isinstance(x, float)]
        if ok:
            a2.scatter([x for x, _ in ok], [y for _, y in ok], s=24, alpha=0.6, edgecolor="k", linewidth=0.3)
            a2.set_xlabel("spatial information (bits/spike)"); a2.set_ylabel("per-cell ks_gue (Maze-Awake)")
            a2.set_title("G2: H1-analogue — ks_gue vs spatial info"); a2.grid(alpha=0.2)
    p = os.path.join(_HERE, "figures", "P_buzsaki_port.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.run:
        run()
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()

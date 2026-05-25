"""
cross_substrate/population_strat_analysis.py — analyse the stratified population fingerprints.

Reads coordinates/population-strat.jsonl (population_strat.py) and asks, for each of the 3 trustable
observables (corr-eig / avl-onset / sync-event), what STRUCTURES the population landscape position:

  (0) FRAGMENTATION ROBUSTNESS — does the corr-eig→repulsive / avl→intermediate / sync→Poisson split
      hold within every area×stimulus cell (i.e. is fragmentation a real per-cell property, not a
      pooling artifact)?
  (A) STIMULUS trajectory — do the 8 blocks rank-order CONSISTENTLY across (session,area) groups
      (Kendall's W concordance)? A coherent stimulus trajectory ⇒ high W + a stable block ordering.
  (B) AREA — does cortical area set the position (Kendall's W of area rankings across session×block)?
      Cross-referenced against the per-cell ks_gue area pattern (allen-depth.jsonl) — does the
      POPULATION corr-eig area gradient reproduce the PER-CELL one (the H1-across-areas analogue)?
  (C) SESSION stability — marginal variance explained (one-way η²) by area / stimulus / session for
      each observable's Brody q: what fraction of the position is set by each factor.

Primary axis: Brody q (and I.5q as the extractor-independent cross-check). Out: prints the analysis +
figure P_population_strat.png. Run: --run.
"""
from __future__ import annotations

import json
import os

import numpy as np
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")
OBS = ["corr-eig", "avl-onset", "sync-event"]
BLOCK_ORDER = ["spontaneous", "drifting_gratings", "static_gratings", "natural_scenes",
               "natural_movie_one", "natural_movie_three", "gabors", "flashes"]


def _load():
    return [json.loads(l) for l in open(os.path.join(COORD, "population-strat.jsonl"))]


def _eta2(values, groups):
    """One-way η² (marginal variance explained by the grouping factor)."""
    vals = np.asarray(values, float)
    grand = vals.mean()
    ss_tot = float(np.sum((vals - grand) ** 2))
    if ss_tot < 1e-12:
        return 0.0
    ss_bet = 0.0
    for g in set(groups):
        m = vals[np.array(groups) == g]
        ss_bet += m.size * (m.mean() - grand) ** 2
    return float(ss_bet / ss_tot)


def _kendall_w(rank_matrix):
    """Kendall's W concordance over an (n_raters × n_items) rank matrix (rows=groups, cols=conditions)."""
    R = np.asarray(rank_matrix, float)
    n, k = R.shape          # n groups rank k conditions
    if n < 2 or k < 2:
        return None
    col_rank_sums = R.sum(axis=0)
    S = np.sum((col_rank_sums - col_rank_sums.mean()) ** 2)
    return float(12 * S / (n ** 2 * (k ** 3 - k)))


def run():
    recs = _load()
    print(f"STRATIFIED POPULATION ANALYSIS — {len(recs)} cells, "
          f"{len(set(r['session'] for r in recs))} sessions, "
          f"{len(set(r['area'] for r in recs))} areas, {len(set(r['block'] for r in recs))} blocks\n")

    def q(r):
        return r["axes_computed"].get("I.8_brody_q")

    # (0) fragmentation robustness: mean Brody q per observable, and the within-cell ordering
    print("(0) FRAGMENTATION across observables (mean Brody q ± sd, over all area×stim×session cells):")
    qby = {o: [q(r) for r in recs if r["aggregation"] == o and isinstance(q(r), float)] for o in OBS}
    for o in OBS:
        v = qby[o]
        print(f"    {o:11s} q = {np.mean(v):.3f} ± {np.std(v):.3f}  (n={len(v)})")
    # fraction of (session,area,block) cells where corr-eig q > avl q > sync q (the canonical ordering)
    cells = {}
    for r in recs:
        cells.setdefault((r["session"], r["area"], r["block"]), {})[r["aggregation"]] = q(r)
    full = [c for c in cells.values() if all(isinstance(c.get(o), float) for o in OBS)]
    canon = sum(1 for c in full if c["corr-eig"] > c["avl-onset"] > c["sync-event"])
    print(f"    canonical ordering corr-eig>avl>sync holds in {canon}/{len(full)} fully-populated cells "
          f"({100*canon/max(1,len(full)):.0f}%)\n")

    # (A) stimulus trajectory — Kendall's W of block rankings across (session,area) groups, per observable
    print("(A) STIMULUS trajectory — Kendall's W of block-q rankings across (session,area) groups:")
    for o in OBS:
        groups, blocks_seen = {}, set()
        for r in recs:
            if r["aggregation"] != o or not isinstance(q(r), float):
                continue
            groups.setdefault((r["session"], r["area"]), {})[r["block"]] = q(r)
            blocks_seen.add(r["block"])
        blocks = [b for b in BLOCK_ORDER if b in blocks_seen]
        rm = [[g[b] for b in blocks] for g in groups.values() if all(b in g for b in blocks)]
        if len(rm) >= 2 and len(blocks) >= 2:
            ranks = np.array([stats.rankdata(row) for row in rm])
            W = _kendall_w(ranks)
            meanq = {b: np.mean([row[i] for row in rm]) for i, b in enumerate(blocks)}
            order = sorted(meanq, key=meanq.get)
            print(f"    {o:11s} W={W:.3f} (n={len(rm)} groups)  low→high q: "
                  f"{' < '.join(f'{b}({meanq[b]:.2f})' for b in order)}")
        else:
            print(f"    {o:11s} insufficient complete groups")
    print("    (high W ⇒ consistent stimulus ordering ⇒ coherent trajectory; low W ⇒ scatter)\n")

    # (B) area — Kendall's W of area rankings across (session,block); + per-cell cross-ref
    print("(B) AREA — Kendall's W of area-q rankings across (session,block) groups:")
    for o in OBS:
        groups, areas_seen = {}, set()
        for r in recs:
            if r["aggregation"] != o or not isinstance(q(r), float):
                continue
            groups.setdefault((r["session"], r["block"]), {})[r["area"]] = q(r)
            areas_seen.add(r["area"])
        areas = sorted(areas_seen)
        rm = [[g[a] for a in areas] for g in groups.values() if all(a in g for a in areas)]
        if len(rm) >= 2 and len(areas) >= 2:
            ranks = np.array([stats.rankdata(row) for row in rm])
            W = _kendall_w(ranks)
            meanq = {a: np.mean([row[i] for row in rm]) for i, a in enumerate(areas)}
            order = sorted(meanq, key=meanq.get)
            print(f"    {o:11s} W={W:.3f} (n={len(rm)} groups)  low→high q: "
                  f"{' < '.join(f'{a}({meanq[a]:.2f})' for a in order)}")
        else:
            print(f"    {o:11s} insufficient complete groups")
    _per_cell_crossref(recs)
    print()

    # (C) session stability — marginal η² by factor for each observable's Brody q
    print("(C) MARGINAL VARIANCE EXPLAINED (one-way η²) for Brody q — what structures the position:")
    print(f"    {'observable':11s} {'area':>7s} {'stimulus':>9s} {'session':>8s}")
    for o in OBS:
        sub = [r for r in recs if r["aggregation"] == o and isinstance(q(r), float)]
        if len(sub) < 8:
            print(f"    {o:11s} (too few)"); continue
        vals = [q(r) for r in sub]
        e_area = _eta2(vals, [r["area"] for r in sub])
        e_blk = _eta2(vals, [r["block"] for r in sub])
        e_sess = _eta2(vals, [r["session"] for r in sub])
        print(f"    {o:11s} {e_area:>7.2f} {e_blk:>9.2f} {e_sess:>8.2f}")
    print("    (marginal, not a partition — factors correlate; reads 'how much each factor structures q')")
    _figure(recs)


def _per_cell_crossref(recs):
    """Does the POPULATION corr-eig area gradient reproduce the PER-CELL ks_gue area pattern (H1 analogue)?"""
    path = os.path.join(COORD, "allen-depth.jsonl")
    if not os.path.exists(path):
        print("    (per-cell cross-ref skipped: allen-depth.jsonl absent)"); return
    pc = {}
    for line in open(path):
        try:
            r = json.loads(line)
        except Exception:
            continue
        v = r.get("axes_computed", {}).get("I.5_ks_gue")
        if isinstance(v, (int, float)) and r.get("area"):
            pc.setdefault(r["area"], []).append(v)
    pc_mean = {a: float(np.mean(v)) for a, v in pc.items() if len(v) >= 20}
    pop = {}
    for r in recs:
        if r["aggregation"] == "corr-eig":
            qv = r["axes_computed"].get("I.8_brody_q")
            if isinstance(qv, float):
                pop.setdefault(r["area"], []).append(qv)
    pop_mean = {a: float(np.mean(v)) for a, v in pop.items()}
    common = sorted(set(pc_mean) & set(pop_mean))
    if len(common) >= 4:
        rho = stats.spearmanr([pc_mean[a] for a in common], [pop_mean[a] for a in common])[0]
        print(f"    per-cell cross-ref: ρ(population corr-eig q, per-cell ks_gue) over {len(common)} areas "
              f"= {rho:+.3f}  [{'reproduces' if abs(rho)>0.5 else 'does NOT track'} the per-cell area pattern]")
    else:
        print(f"    per-cell cross-ref: only {len(common)} common areas (need ≥4)")


def _figure(recs):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(16, 5))
    # A: stimulus trajectory of corr-eig q (one line per session-area, mean over)
    for o, ax, ttl in [("corr-eig", a1, "corr-eig (spectral)"), ("avl-onset", a2, "avl-onset (point proc)")]:
        by = {}
        for r in recs:
            if r["aggregation"] == o and isinstance(r["axes_computed"].get("I.8_brody_q"), float):
                by.setdefault(r["area"], {}).setdefault(r["block"], []).append(r["axes_computed"]["I.8_brody_q"])
        blocks = [b for b in BLOCK_ORDER if any(b in v for v in by.values())]
        for area, d in sorted(by.items()):
            ys = [np.mean(d[b]) if b in d else np.nan for b in blocks]
            ax.plot(range(len(blocks)), ys, "o-", ms=4, label=area)
        ax.set_xticks(range(len(blocks))); ax.set_xticklabels(blocks, rotation=40, ha="right", fontsize=7)
        ax.set_ylabel("Brody q"); ax.set_title(f"{ttl}: q across stimuli by area"); ax.grid(alpha=0.2)
    a1.legend(fontsize=6, ncol=2)
    # C: marginal eta2 bars
    facs = ["area", "block", "session"]
    width = 0.25
    for i, o in enumerate(OBS):
        sub = [r for r in recs if r["aggregation"] == o and isinstance(r["axes_computed"].get("I.8_brody_q"), float)]
        if len(sub) < 8:
            continue
        vals = [r["axes_computed"]["I.8_brody_q"] for r in sub]
        es = [_eta2(vals, [r[f] for r in sub]) for f in facs]
        a3.bar(np.arange(len(facs)) + i * width, es, width, label=o)
    a3.set_xticks(np.arange(len(facs)) + width); a3.set_xticklabels(facs)
    a3.set_ylabel("marginal η² (Brody q)"); a3.set_title("What structures the position?"); a3.legend(fontsize=7)
    a3.grid(alpha=0.2)
    p = os.path.join(_HERE, "figures", "P_population_strat.png")
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

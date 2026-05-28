"""
cross_substrate/attractor_analysis.py — P2/P3 of the EC-vs-CA3 attractor-topology brief.

Loads the two ports:
  • dr-port-cell/pop.jsonl    — 000638: MEC (continuous-attractor grid) + CA1 + DG
  • allen-hpf-cell/pop.jsonl  — Allen : CA3 (discrete attractor) + CA1 + DG (+CA2/SUB/ProS)

Produces:
  P2.1 per-cell distribution comparisons (ks_gue, Brody q, W1, burst, rate) per region, within each
       substrate (KS test + Cliff's delta), cell-type-controlled (excitatory-only) where applicable.
  P2.2 population-observable comparison per region (corr-eig / avl-onset / sync-event Brody q + BRrho).
  P2.4 burst-structure comparison per region.
  BRIDGE: cross-substrate consistency of the SHARED anchors CA1 and DG (Allen vs 000638). The MEC-vs-CA3
       headline is interpretable only to the extent CA1/DG agree across substrates (else substrate/prep
       confound dominates).
  P3   attractor-topology engagement table: continuous (MEC) vs discrete (CA3), honestly bounded.

Read-only on the banked coordinates. Run: python3 attractor_analysis.py [--rate-match].
Flag, don't interpret — verdicts are Will's.
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
COORD = os.path.join(_HERE, "coordinates")

AX = {"ks_gue": "I.5q_ks_gue_med", "brody_q": "I.8_brody_q",
      "w1": "I.1_w1_clock", "brho": "I.9_berry_robnik_rho"}


def _load(name):
    p = os.path.join(COORD, name)
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def cliffs_delta(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if a.size < 3 or b.size < 3:
        return None, None, (a.size, b.size)
    # Cliff's delta via rank-sum (Mann-Whitney U)
    try:
        U, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    except ValueError:
        return None, None, (a.size, b.size)
    delta = 2 * U / (a.size * b.size) - 1
    return float(delta), float(p), (a.size, b.size)


def _vals(cells, region, axis, ctype=None, max_rate=None):
    out = []
    for c in cells:
        if c.get("region") != region:
            continue
        if ctype and c.get("cell_type") != ctype:
            continue
        if max_rate is not None and (c.get("rate_hz") is None or c["rate_hz"] > max_rate):
            continue
        v = c.get("axes_computed", {}).get(axis)
        if v is not None and np.isfinite(v):
            out.append(v)
    return np.array(out, float)


def _burstvals(cells, region, key, ctype=None):
    out = []
    for c in cells:
        if c.get("region") != region:
            continue
        if ctype and c.get("cell_type") != ctype:
            continue
        v = (c.get("burst") or {}).get(key)
        if v is not None and np.isfinite(v):
            out.append(v)
    return np.array(out, float)


def fmt_delta(d, p, ns):
    if d is None:
        return f"  n/a (n={ns})"
    mag = abs(d)
    tag = "negligible" if mag < 0.147 else "small" if mag < 0.33 else "medium" if mag < 0.474 else "LARGE"
    star = "***" if p < 1e-3 else "**" if p < 1e-2 else "*" if p < 0.05 else " "
    return f"δ={d:+.3f} {tag:10s} p={p:.1e}{star} n={ns[0]}v{ns[1]}"


def region_table(cells, regions, label, ctype=None):
    print(f"\n### {label}" + (f"  (cell_type={ctype})" if ctype else "  (all cell-types)"))
    hdr = f"{'region':6s} {'nCell':>5s} " + " ".join(f"{k:>14s}" for k in ("ks_gue", "brody_q", "w1", "burst_frac", "cv2", "rate_hz"))
    print(hdr)
    for r in regions:
        ks = _vals(cells, r, AX["ks_gue"], ctype)
        bq = _vals(cells, r, AX["brody_q"], ctype)
        w1 = _vals(cells, r, AX["w1"], ctype)
        bf = _burstvals(cells, r, "burst_frac", ctype)
        cv2 = _burstvals(cells, r, "cv2", ctype)
        rt = np.array([c["rate_hz"] for c in cells if c.get("region") == r
                       and (not ctype or c.get("cell_type") == ctype) and c.get("rate_hz") is not None], float)
        def m(x):
            return f"{np.median(x):6.3f}" if x.size else "   -  "
        print(f"{r:6s} {ks.size:>5d} " + " ".join(f"{m(x):>14s}" for x in (ks, bq, w1, bf, cv2, rt)))


def pairwise(cells, ref, others, label, ctype=None, max_rate=None):
    print(f"\n### {label} — pairwise vs {ref}" + (f" (ct={ctype})" if ctype else "")
          + (f" [rate<= {max_rate}Hz]" if max_rate else ""))
    for axis_name, axkey in AX.items():
        rv = _vals(cells, ref, axkey, ctype, max_rate)
        line = f"  {axis_name:8s}: "
        cmps = []
        for o in others:
            ov = _vals(cells, o, axkey, ctype, max_rate)
            d, p, ns = cliffs_delta(ov, rv)
            cmps.append(f"{o}: {fmt_delta(d, p, ns)}")
        print(line + "   ".join(cmps))
    # burst
    for bk in ("burst_frac", "cv2"):
        rv = _burstvals(cells, ref, bk, ctype)
        cmps = []
        for o in others:
            ov = _burstvals(cells, o, bk, ctype)
            d, p, ns = cliffs_delta(ov, rv)
            cmps.append(f"{o}: {fmt_delta(d, p, ns)}")
        print(f"  {bk:8s}: " + "   ".join(cmps))


def pop_table(pop, regions, label):
    print(f"\n### {label} — population observables (cell_type=all, median over sessions)")
    print(f"{'region':6s} {'agg':11s} {'nRec':>4s} {'brody_q':>9s} {'brho':>9s} {'ks_gue':>9s}")
    for r in regions:
        for agg in ("corr-eig", "avl-onset", "sync-event"):
            recs = [x for x in pop if x.get("region") == r and x.get("aggregation") == agg
                    and x.get("cell_type") == "all"]
            if not recs:
                continue
            def med(k):
                vs = [x["axes_computed"].get(k) for x in recs]
                vs = [v for v in vs if v is not None and np.isfinite(v)]
                return f"{np.median(vs):9.3f}" if vs else "    -    "
            print(f"{r:6s} {agg:11s} {len(recs):>4d} {med('I.8_brody_q')} "
                  f"{med('I.9_berry_robnik_rho')} {med('I.5q_ks_gue_med')}")


def bridge(dr_cells, allen_cells):
    print("\n" + "=" * 78)
    print("CROSS-SUBSTRATE VALIDITY BRIDGE — do the SHARED anchors (CA1, DG) agree across substrates?")
    print("  (000638 vs Allen; large delta => substrate/prep confound dominates => MEC-vs-CA3 NOT clean)")
    print("=" * 78)
    for r in ("CA1", "DG"):
        print(f"\n  [{r}] 000638 vs Allen (excitatory-only):")
        for axis_name, axkey in AX.items():
            dv = _vals(dr_cells, r, axkey, "excitatory")
            av = _vals(allen_cells, r, axkey, "excitatory")
            d, p, ns = cliffs_delta(dv, av)
            print(f"     {axis_name:8s}: {fmt_delta(d, p, ns)}  med 000638={np.median(dv) if dv.size else float('nan'):.3f} Allen={np.median(av) if av.size else float('nan'):.3f}")


def headline(dr_cells, allen_cells, max_rate=None):
    print("\n" + "=" * 78)
    print("P3 HEADLINE — MEC (000638, continuous-attractor grid) vs CA3 (Allen, discrete attractor)")
    print("  INTERPRETIVE NOT MEASURED: different animals/prep/task; read THROUGH the CA1/DG bridge above.")
    print("=" * 78)
    print(f"  excitatory-only" + (f", rate<= {max_rate}Hz" if max_rate else "") + ":")
    for axis_name, axkey in AX.items():
        mec = _vals(dr_cells, "MEC", axkey, "excitatory", max_rate)
        ca3 = _vals(allen_cells, "CA3", axkey, "excitatory", max_rate)
        d, p, ns = cliffs_delta(mec, ca3)
        mm = np.median(mec) if mec.size else float("nan")
        cm = np.median(ca3) if ca3.size else float("nan")
        print(f"     {axis_name:8s}: {fmt_delta(d, p, ns)}  med MEC={mm:.3f} CA3={cm:.3f}")
    for bk in ("burst_frac", "cv2"):
        mec = _burstvals(dr_cells, "MEC", bk, "excitatory")
        ca3 = _burstvals(allen_cells, "CA3", bk, "excitatory")
        d, p, ns = cliffs_delta(mec, ca3)
        print(f"     {bk:8s}: {fmt_delta(d, p, ns)}  med MEC={np.median(mec) if mec.size else float('nan'):.3f} "
              f"CA3={np.median(ca3) if ca3.size else float('nan'):.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate-match", action="store_true", help="cap rate at the lower-region 90th pct")
    a = ap.parse_args()

    dr_cells = _load("dr-port-cell.jsonl"); dr_pop = _load("dr-port-pop.jsonl")
    allen_cells = _load("allen-hpf-cell.jsonl"); allen_pop = _load("allen-hpf-pop.jsonl")
    print(f"loaded: 000638 {len(dr_cells)} cells / {len(dr_pop)} pop ;  "
          f"Allen {len(allen_cells)} cells / {len(allen_pop)} pop")

    # ── within-substrate per-cell ──
    print("\n" + "#" * 78 + "\n# P2.1 PER-CELL DISTRIBUTIONS (median)\n" + "#" * 78)
    region_table(dr_cells, ["MEC", "CA1", "DG"], "000638  (MEC/CA1/DG)")
    region_table(dr_cells, ["MEC", "CA1", "DG"], "000638  (MEC/CA1/DG)", ctype="excitatory")
    region_table(allen_cells, ["CA3", "CA1", "DG"], "Allen   (CA3/CA1/DG)")
    region_table(allen_cells, ["CA3", "CA1", "DG"], "Allen   (CA3/CA1/DG)", ctype="excitatory")

    # ── within-substrate pairwise (effect sizes) ──
    print("\n" + "#" * 78 + "\n# P2.1 PAIRWISE EFFECT SIZES (Cliff's delta, Mann-Whitney p)\n" + "#" * 78)
    mr_dr = mr_al = None
    if a.rate_match:
        # rate-match cap = min over regions of 90th pct rate, per substrate
        def cap(cells, regs):
            caps = []
            for r in regs:
                rt = np.array([c["rate_hz"] for c in cells if c.get("region") == r
                               and c.get("cell_type") == "excitatory" and c.get("rate_hz") is not None], float)
                if rt.size:
                    caps.append(np.percentile(rt, 90))
            return min(caps) if caps else None
        mr_dr = cap(dr_cells, ["MEC", "CA1", "DG"]); mr_al = cap(allen_cells, ["CA3", "CA1", "DG"])
        print(f"  [rate-match caps] 000638={mr_dr:.2f}Hz  Allen={mr_al:.2f}Hz")
    pairwise(dr_cells, "CA1", ["MEC", "DG"], "000638", ctype="excitatory", max_rate=mr_dr)
    pairwise(allen_cells, "CA1", ["CA3", "DG"], "Allen", ctype="excitatory", max_rate=mr_al)

    # ── population ──
    print("\n" + "#" * 78 + "\n# P2.2 POPULATION OBSERVABLES\n" + "#" * 78)
    pop_table(dr_pop, ["MEC", "CA1", "DG"], "000638")
    pop_table(allen_pop, ["CA3", "CA1", "DG"], "Allen")

    # ── bridge + headline ──
    bridge(dr_cells, allen_cells)
    headline(dr_cells, allen_cells, max_rate=mr_dr if a.rate_match else None)


if __name__ == "__main__":
    main()

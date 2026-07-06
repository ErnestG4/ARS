"""
cross_substrate/hc3_analysis.py — the DE-CONFOUNDED EC-vs-CA3 test on CRCNS hc-3 (within one dataset).

Tonight's 000638-vs-Allen MEC-vs-CA3 was confounded-out by the cross-dataset validity bridge (CA1/DG
differed δ≈−0.9 across datasets). hc-3 records EC + CA3 (+DG) SIMULTANEOUSLY in one implant, so this
contrast has NO cross-dataset confound. Question: does the within-dataset EC-vs-CA3 fingerprint contrast
CONFIRM tonight's bounded-negative (no difference) or reveal a signal the cross-dataset confound masked?

P2.1 per-cell distributions (ks_gue/brody_q/w1/burst) per region; EC-vs-CA3 Cliff's delta (rate-matched,
excitatory-only). P2.2 population (pillar-1: corr-eig GUE in EC & CA3?). Pillar-2: place_coherence/
spatial_info↔ks_gue per region. Read-only. Run: python3 hc3_analysis.py [--rate-match].
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
    return [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []


def cliffs_delta(a, b):
    a = np.asarray(a, float); a = a[np.isfinite(a)]
    b = np.asarray(b, float); b = b[np.isfinite(b)]
    if a.size < 3 or b.size < 3:
        return None, None, (a.size, b.size)
    U, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    return float(2 * U / (a.size * b.size) - 1), float(p), (a.size, b.size)


def fmt(d, p, ns):
    if d is None:
        return f"n/a (n={ns})"
    mag = abs(d)
    tag = "negligible" if mag < 0.147 else "small" if mag < 0.33 else "medium" if mag < 0.474 else "LARGE"
    star = "***" if p < 1e-3 else "**" if p < 1e-2 else "*" if p < 0.05 else " "
    return f"δ={d:+.3f} {tag:10s} p={p:.1e}{star} n={ns[0]}v{ns[1]}"


def vals(cells, region, axkey, ct=None, max_rate=None):
    out = []
    for c in cells:
        if c.get("region") != region:
            continue
        if ct and c.get("cell_type") != ct:
            continue
        if max_rate is not None and (c.get("rate_hz") is None or c["rate_hz"] > max_rate):
            continue
        v = c.get("axes_computed", {}).get(axkey)
        if v is not None and np.isfinite(v):
            out.append(v)
    return np.array(out, float)


def burstvals(cells, region, key, ct=None):
    out = []
    for c in cells:
        if c.get("region") != region or (ct and c.get("cell_type") != ct):
            continue
        v = (c.get("burst") or {}).get(key)
        if v is not None and np.isfinite(v):
            out.append(v)
    return np.array(out, float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rate-match", action="store_true")
    a = ap.parse_args()
    cells = _load("hc3-port-cell.jsonl"); pop = _load("hc3-port-pop.jsonl"); pf = _load("hc3-placefields.jsonl")
    print(f"hc-3: {len(cells)} per-cell, {len(pop)} pop, {len(pf)} placefield records")
    import collections
    print("per-cell by region:", dict(collections.Counter(c["region"] for c in cells)))
    print("topdirs:", sorted(set(c["topdir"] for c in cells)))

    print("\n" + "#" * 76 + "\n# P2.1 PER-CELL DISTRIBUTIONS (median) — hc-3 within-dataset\n" + "#" * 76)
    for ct in (None, "excitatory"):
        print(f"\n  cell_type={ct or 'all'}")
        print(f"  {'region':5s} {'nCell':>5s} " + " ".join(f"{k:>11s}" for k in ("ks_gue","brody_q","w1","burst_frac","cv2","rate_hz")))
        for r in ("EC", "CA3", "DG", "CA1"):
            ks = vals(cells, r, AX["ks_gue"], ct)
            if ks.size == 0:
                continue
            bq = vals(cells, r, AX["brody_q"], ct); w1 = vals(cells, r, AX["w1"], ct)
            bf = burstvals(cells, r, "burst_frac", ct); cv2 = burstvals(cells, r, "cv2", ct)
            rt = np.array([c["rate_hz"] for c in cells if c.get("region") == r
                           and (not ct or c.get("cell_type") == ct) and c.get("rate_hz") is not None], float)
            m = lambda x: f"{np.median(x):11.3f}" if x.size else f"{'-':>11s}"
            print(f"  {r:5s} {ks.size:>5d} " + " ".join(m(x) for x in (ks, bq, w1, bf, cv2, rt)))

    # rate-match cap
    mr = None
    if a.rate_match:
        caps = []
        for r in ("EC", "CA3"):
            rt = np.array([c["rate_hz"] for c in cells if c.get("region") == r
                           and c.get("cell_type") == "excitatory" and c.get("rate_hz") is not None], float)
            if rt.size:
                caps.append(np.percentile(rt, 90))
        mr = min(caps) if caps else None
        print(f"\n  [rate-match cap = {mr:.2f} Hz]" if mr else "")

    print("\n" + "#" * 76 + "\n# DE-CONFOUNDED EC-vs-CA3 (excitatory, within-dataset — NO bridge confound)\n" + "#" * 76)
    for axis_name, axkey in AX.items():
        ec = vals(cells, "EC", axkey, "excitatory", mr); ca3 = vals(cells, "CA3", axkey, "excitatory", mr)
        d, p, ns = cliffs_delta(ec, ca3)
        me = np.median(ec) if ec.size else float("nan"); mc = np.median(ca3) if ca3.size else float("nan")
        print(f"  {axis_name:8s}: {fmt(d,p,ns)}  med EC={me:.3f} CA3={mc:.3f}")
    for bk in ("burst_frac", "cv2"):
        ec = burstvals(cells, "EC", bk, "excitatory"); ca3 = burstvals(cells, "CA3", bk, "excitatory")
        d, p, ns = cliffs_delta(ec, ca3)
        print(f"  {bk:8s}: {fmt(d,p,ns)}  med EC={np.median(ec) if ec.size else float('nan'):.3f} CA3={np.median(ca3) if ca3.size else float('nan'):.3f}")

    print("\n" + "#" * 76 + "\n# P2.2 POPULATION (pillar-1: corr-eig GUE in EC & CA3?)\n" + "#" * 76)
    print(f"  {'region':5s} {'agg':11s} {'nRec':>4s} {'brody_q':>9s} {'brho':>9s} {'ks_gue':>9s}")
    for r in ("EC", "CA3", "DG"):
        for agg in ("corr-eig", "avl-onset", "sync-event"):
            recs = [x for x in pop if x.get("region") == r and x.get("aggregation") == agg and x.get("cell_type") == "all"]
            if not recs:
                continue
            med = lambda k: (lambda vs: f"{np.median(vs):9.3f}" if vs else f"{'-':>9s}")([x["axes_computed"].get(k) for x in recs if x["axes_computed"].get(k) is not None and np.isfinite(x["axes_computed"].get(k))])
            print(f"  {r:5s} {agg:11s} {len(recs):>4d} {med('I.8_brody_q')} {med('I.9_berry_robnik_rho')} {med('I.5q_ks_gue_med')}")

    # ── burst-control: is the EC-vs-CA3 ks_gue difference INDEPENDENT of the intrinsic burst axis? ──
    print("\n" + "#" * 76 + "\n# BURST-CONTROL (intrinsic-vs-extrinsic): does EC-vs-CA3 ks_gue survive\n"
          "# removing the burst_frac trend? (CA3 pyramidal complex-spike bursting -> clustered ISI)\n" + "#" * 76)
    # pool EC+CA3 excitatory cells with BOTH ks_gue and burst_frac
    rows = []
    for c in cells:
        if c.get("region") in ("EC", "CA3") and c.get("cell_type") == "excitatory":
            k = c.get("axes_computed", {}).get(AX["ks_gue"]); bfv = (c.get("burst") or {}).get("burst_frac")
            if k is not None and bfv is not None and np.isfinite(k) and np.isfinite(bfv):
                rows.append((c["region"], k, bfv))
    if len(rows) > 20:
        reg = np.array([r[0] for r in rows]); ksv = np.array([r[1] for r in rows]); bfv = np.array([r[2] for r in rows])
        # raw EC-vs-CA3 on this matched subset
        d0, p0, ns0 = cliffs_delta(ksv[reg == "EC"], ksv[reg == "CA3"])
        # spearman ks_gue ~ burst across the pool
        rho_kb, p_kb = stats.spearmanr(ksv, bfv)
        # residualize ks_gue on burst (rank-based: regress on burst rank), then EC-vs-CA3 on residuals
        from numpy.polynomial import polynomial as Pp
        order = np.argsort(bfv); br = np.empty_like(bfv); br[order] = np.arange(bfv.size)  # burst ranks
        coef = np.polyfit(br, ksv, 1); resid = ksv - np.polyval(coef, br)
        d1, p1, ns1 = cliffs_delta(resid[reg == "EC"], resid[reg == "CA3"])
        print(f"  ks_gue~burst_frac (pooled EC+CA3 exc): Spearman ρ={rho_kb:+.3f} p={p_kb:.1e} (n={ksv.size})")
        print(f"  EC-vs-CA3 ks_gue  RAW         : {fmt(d0,p0,ns0)}")
        print(f"  EC-vs-CA3 ks_gue  BURST-RESID : {fmt(d1,p1,ns1)}")
        print(f"  -> if RESID delta collapses toward 0, the EC-vs-CA3 NNS gap is the INTRINSIC burst axis;")
        print(f"     if it persists, there is an NNS-class difference beyond burst.")

    # ── state stratification: active vs sleep, paired by cell (same topdir = same cells) ──
    ACTIVE = {"linear", "bigSquare", "Mwheel", "wheel", "midSquare", "linearOne", "linearTwo", "plus", "Tmaze"}
    by_cell = {}  # (topdir,ele,clu,region) -> {state: {ks,burst,rate}}
    for c in cells:
        st = "sleep" if c.get("behavior") == "sleep" else ("active" if c.get("behavior") in ACTIVE else None)
        if st is None:
            continue
        key = (c["topdir"], c.get("ele"), c.get("clu"), c["region"])
        d = by_cell.setdefault(key, {})
        ks = c.get("axes_computed", {}).get(AX["ks_gue"]); bf = (c.get("burst") or {}).get("burst_frac")
        d.setdefault(st, []).append((ks, bf, c.get("rate_hz")))
    paired = {r: {"ks_a": [], "ks_s": [], "bf_a": [], "bf_s": []} for r in ("EC", "CA3", "DG")}
    for (td, ele, clu, reg), d in by_cell.items():
        if reg not in paired or "active" not in d or "sleep" not in d:
            continue
        ka = np.nanmean([x[0] for x in d["active"] if x[0] is not None]) if any(x[0] is not None for x in d["active"]) else np.nan
        ks_ = np.nanmean([x[0] for x in d["sleep"] if x[0] is not None]) if any(x[0] is not None for x in d["sleep"]) else np.nan
        ba = np.nanmean([x[1] for x in d["active"] if x[1] is not None]) if any(x[1] is not None for x in d["active"]) else np.nan
        bs = np.nanmean([x[1] for x in d["sleep"] if x[1] is not None]) if any(x[1] is not None for x in d["sleep"]) else np.nan
        if np.isfinite(ka) and np.isfinite(ks_):
            paired[reg]["ks_a"].append(ka); paired[reg]["ks_s"].append(ks_)
        if np.isfinite(ba) and np.isfinite(bs):
            paired[reg]["bf_a"].append(ba); paired[reg]["bf_s"].append(bs)
    if any(paired[r]["ks_a"] for r in paired):
        print("\n" + "#" * 76 + "\n# STATE STRATIFICATION: active vs sleep, PAIRED within cell (same topdir)\n"
              "# does the EC-vs-CA3 burst gap / class change with brain state?\n" + "#" * 76)
        for reg in ("EC", "CA3", "DG"):
            for lab, ak, sk in (("ks_gue", "ks_a", "ks_s"), ("burst_frac", "bf_a", "bf_s")):
                a = np.array(paired[reg][ak]); s = np.array(paired[reg][sk])
                if a.size >= 5:
                    try:
                        w, p = stats.wilcoxon(a, s)
                    except ValueError:
                        p = float("nan")
                    print(f"  {reg:4s} {lab:11s} active={np.median(a):.3f} sleep={np.median(s):.3f} "
                          f"Δ(med)={np.median(s)-np.median(a):+.3f}  paired-Wilcoxon p={p:.2g} n={a.size}")

    if pf:
        print("\n" + "#" * 76 + "\n# PILLAR-2: place/spatial-info ↔ ks_gue per region (EC = continuous-attractor)\n" + "#" * 76)
        for r in ("EC", "CA3", "DG", "CA1"):
            rr = [x for x in pf if x["region"] == r]
            for feat in ("spatial_info_bits_per_spike", "place_coherence"):
                rre = [x for x in rr if x.get("cell_type", x.get("celltype")) == "excitatory"]
                xs = np.array([x[feat] for x in rre], float); ys = np.array([x["ks_gue_med"] for x in rre], float)
                m = np.isfinite(xs) & np.isfinite(ys); xs, ys = xs[m], ys[m]
                if xs.size >= 8:
                    rho, p = stats.spearmanr(xs, ys)
                    print(f"  {r:4s} {feat:28s} exc: ρ={rho:+.3f} p={p:.1e} n={xs.size}")
                else:
                    print(f"  {r:4s} {feat:28s} exc: n/a (n={xs.size})")


if __name__ == "__main__":
    main()

"""
cross_substrate/buzsaki_placefields.py — CA1 place-field structure ↔ per-cell universality class (cycle 2).

Deepens the G2 framework-port finding (spatial information ρ=+0.28 was the CA1 H1-analogue) by asking WHICH
aspect of place coding drives the selectivity↔class link. Computes proper place-field metrics on the
linearized maze (Maze epoch) per cell — peak rate, field count/width, spatial coherence (Muller-Kubie),
spatial stability (1st-vs-2nd-half rate-map correlation), is-place-cell — then correlates each with per-cell
ks_gue (Maze-Awake, buzsaki-port-cell.jsonl), and contrasts place-cells vs non-place-cells.

Reuses the validated position machinery from buzsaki_selectivity. Out: coordinates/buzsaki-placefields.jsonl
+ prints the correlations + figure P_buzsaki_placefields.png. Run: --run [--sessions N | --all].
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import glob
import json
import sys
import time
from datetime import date

import numpy as np
import h5py
from scipy.ndimage import gaussian_filter1d
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from cross_substrate.buzsaki_selectivity import (_find_linearized_position, _maze_window,  # noqa: E402
                                                 _decode, N_POS_BINS)

BUZ_GLOB = "/home/combust/fmexplorer/buzsaki_cache/*.nwb"
COORD = os.path.join(_HERE, "coordinates")
SMOOTH = 2.0           # rate-map Gaussian σ (bins)
PF_THRESH = 0.2        # field = contiguous bins > 0.2 × peak
MIN_FIELD_BINS = 2
PLACE_SI = 0.5         # is-place-cell: spatial info ≥ 0.5 bits/spike + peak ≥ 1 Hz + ≥1 field


def _rate_map(spk_t, pos_t, pos_x, edges, t0, t1):
    """Occupancy-normalised smoothed firing rate per position bin over [t0,t1]."""
    m = (pos_t >= t0) & (pos_t < t1) & np.isfinite(pos_x)
    pt, px = pos_t[m], pos_x[m]
    if pt.size < 50:
        return None, None
    dt = float(np.median(np.diff(pt)))
    occ = np.histogram(px, bins=edges)[0] * dt          # seconds/bin
    sspk = spk_t[(spk_t >= t0) & (spk_t < t1)]
    spk_x = np.interp(sspk, pt, px)
    sc = np.histogram(spk_x, bins=edges)[0]
    rate = np.full(occ.size, np.nan)
    ok = occ > 0
    rate[ok] = sc[ok] / occ[ok]
    if ok.sum() < 5:
        return None, None
    rate[~ok] = np.interp(np.flatnonzero(~ok), np.flatnonzero(ok), rate[ok]) if ok.any() else 0
    return gaussian_filter1d(rate, SMOOTH), occ


def _fields(rate):
    peak = float(np.nanmax(rate))
    if peak <= 0:
        return 0, 0.0, peak
    above = rate > PF_THRESH * peak
    count, widths, cur = 0, [], 0
    for a in above:
        if a:
            cur += 1
        elif cur:
            if cur >= MIN_FIELD_BINS:
                count += 1; widths.append(cur)
            cur = 0
    if cur >= MIN_FIELD_BINS:
        count += 1; widths.append(cur)
    return count, (float(max(widths)) if widths else 0.0), peak


def _coherence(rate):
    """Muller-Kubie spatial coherence: corr(rate, neighbour-mean)."""
    nb = np.convolve(rate, [0.5, 0, 0.5], mode="same")
    if np.std(rate) < 1e-9 or np.std(nb) < 1e-9:
        return None
    return float(stats.pearsonr(rate, nb)[0])


def _spatial_info(rate, occ):
    p = occ / occ.sum()
    r = float(np.sum(p * rate))
    if r <= 0:
        return None
    nz = rate > 0
    return float(np.sum(p[nz] * (rate[nz] / r) * np.log2(rate[nz] / r)))


def run(n_sessions=1, all_sessions=False):
    files = sorted(glob.glob(BUZ_GLOB))
    if not all_sessions:
        files = files[:n_sessions]
    out = open(os.path.join(COORD, "buzsaki-placefields.jsonl"), "w")
    t0all = time.perf_counter(); n = 0
    print(f"BUZSAKI PLACE-FIELDS — {len(files)} session(s)")
    for f in files:
        sid = os.path.basename(f).replace(".nwb", "")
        with h5py.File(f, "r") as h:
            mz = _maze_window(h)
            pos = _find_linearized_position(h)
            if mz is None or pos is None:
                print(f"  {sid}: no maze/position, skip"); continue
            mt0, mt1 = mz; tmid = 0.5 * (mt0 + mt1)
            px, pt0, prate = pos
            if prate is None:
                prate = px.size / (mt1 - mt0)
            pos_t = pt0 + np.arange(px.size) / prate
            fin = np.isfinite(px)
            edges = np.linspace(np.nanmin(px[fin]), np.nanmax(px[fin]), N_POS_BINS + 1)
            cell_type = _decode(h["units/cell_type"][:]) if "cell_type" in h["units"] else ["?"] * h["units/id"].shape[0]
            sti = h["units/spike_times_index"][:]; st_all = h["units/spike_times"]
            for i in range(len(sti)):
                spk = st_all[(0 if i == 0 else int(sti[i - 1])):int(sti[i])]
                rate, occ = _rate_map(spk, pos_t, px, edges, mt0, mt1)
                if rate is None:
                    continue
                nfield, width, peak = _fields(rate)
                si = _spatial_info(rate, occ)
                r1, _ = _rate_map(spk, pos_t, px, edges, mt0, tmid)
                r2, _ = _rate_map(spk, pos_t, px, edges, tmid, mt1)
                stab = (float(stats.pearsonr(r1, r2)[0]) if r1 is not None and r2 is not None
                        and np.std(r1) > 1e-9 and np.std(r2) > 1e-9 else None)
                is_pc = bool(si is not None and si >= PLACE_SI and peak >= 1.0 and nfield >= 1)
                out.write(json.dumps({
                    "substrate": "buzsaki-placefields", "session": sid, "unit": i,
                    "cell_type": cell_type[i], "peak_rate": peak, "n_fields": nfield,
                    "field_width_bins": width, "spatial_coherence": _coherence(rate),
                    "spatial_stability": stab, "spatial_info": si, "is_place_cell": is_pc,
                    "source_artifact": "generated (CA1 Maze place-field metrics)",
                    "computed_date": date.today().isoformat()}) + "\n"); n += 1
        out.flush()
    out.close()
    print(f"→ {n} per-cell place-field records in {(time.perf_counter()-t0all)/60:.1f} min\n")
    _analyse()


def _analyse():
    pf = [json.loads(l) for l in open(os.path.join(COORD, "buzsaki-placefields.jsonl"))]
    cpath = os.path.join(COORD, "buzsaki-port-cell.jsonl")
    ks = {}
    if os.path.exists(cpath):
        for l in open(cpath):
            r = json.loads(l)
            if r.get("natural_cell") == "Maze-Awake":
                ks[(r["session"], r["unit"])] = r["axes_computed"].get("I.5q_ks_gue_med")
    merged = [(ks[(r["session"], r["unit"])], r) for r in pf
              if (r["session"], r["unit"]) in ks and isinstance(ks[(r["session"], r["unit"])], float)]
    print(f"PLACE-FIELD ↔ ks_gue (Maze-Awake) — merged {len(merged)} cells")
    metrics = ["spatial_info", "spatial_stability", "spatial_coherence", "peak_rate", "n_fields", "field_width_bins"]
    print("  metric              ρ(all)    ρ(exc only)")
    for m in metrics:
        a = [(g, r[m]) for g, r in merged if isinstance(r.get(m), (int, float))]
        e = [(g, r[m]) for g, r in merged if r.get("cell_type") == "excitatory" and isinstance(r.get(m), (int, float))]
        ra = stats.spearmanr([x for x, _ in a], [y for _, y in a])[0] if len(a) >= 8 else None
        re = stats.spearmanr([x for x, _ in e], [y for _, y in e])[0] if len(e) >= 8 else None
        flag = "  ←" if (ra is not None and abs(ra) > 0.25) else ""
        print(f"  {m:18s} {('%+.3f'%ra) if ra is not None else '  -':>8s}  {('%+.3f'%re) if re is not None else '  -':>10s}{flag}")
    # place-cell vs non-place-cell ks_gue
    pc = [g for g, r in merged if r.get("is_place_cell")]
    npc = [g for g, r in merged if not r.get("is_place_cell")]
    if pc and npc:
        u, p = stats.mannwhitneyu(pc, npc, alternative="two-sided")
        print(f"\n  place-cells (n={len(pc)}) ks_gue med={np.median(pc):.3f}  vs  "
              f"non-place (n={len(npc)}) med={np.median(npc):.3f}  (Mann-Whitney p={p:.3g})")
    print("\nFlag, don't interpret — verdict is Will's.")
    _figure(merged)


def _figure(merged):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, m in zip(axes, ["spatial_info", "spatial_stability", "spatial_coherence"]):
        pts = [(r[m], g, r.get("cell_type")) for g, r in merged if isinstance(r.get(m), (int, float))]
        if not pts:
            continue
        cols = ["#1f77b4" if c == "excitatory" else "#d62728" for _, _, c in pts]
        ax.scatter([x for x, _, _ in pts], [y for _, y, _ in pts], s=18, c=cols, alpha=0.5, edgecolor="k", linewidth=0.2)
        ax.set_xlabel(m); ax.set_ylabel("ks_gue (Maze-Awake)"); ax.grid(alpha=0.2)
    axes[1].set_title("CA1 place-field structure ↔ per-cell class (blue=exc, red=inh)")
    p = os.path.join(_HERE, "figures", "P_buzsaki_placefields.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--sessions", type=int, default=1)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.run:
        run(a.sessions, all_sessions=a.all)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()

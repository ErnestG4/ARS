"""
cross_substrate/buzsaki_swr.py — CA1 sharp-wave-ripples (cycle 2c-a): SWR participation ↔ per-cell class
+ place-coding quality, and PRE-vs-POST SWR rate (the replay/consolidation paradigm).

Cycle 2c core, framework-connected: detect SWRs (150-250 Hz ripple-band events in NonREM), then ask
  (1) does per-cell SWR PARTICIPATION (fraction of ripples a cell fires in) track per-cell universality
      class (ks_gue, Maze-Awake) and/or place-coding QUALITY (coherence / is-place-cell, cycle 2a)?
  (2) PRE-NonREM vs POST-NonREM SWR rate (events/min) — the classic post-task replay-enrichment contrast.
Reuses the validated NWB/band/place machinery. Bayesian replay-sequence decoding is a separate follow-on
(2c-b) — this establishes whether SWR engagement relates to the per-cell axes first.

Out: coordinates/buzsaki-swr-{event,cell}.jsonl + prints + figure. Run: --run [--sessions N|--all] [--workers 8].
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
from concurrent.futures import ProcessPoolExecutor
from datetime import date

import numpy as np
import h5py
from scipy.signal import butter, filtfilt, hilbert
from scipy.ndimage import gaussian_filter1d

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from cross_substrate.buzsaki_selectivity import _ts_rate, _decode                 # noqa: E402
from cross_substrate.buzsaki_port import _natural_cells                            # noqa: E402

BUZ_GLOB = "/home/combust/fmexplorer/buzsaki_cache/*.nwb"
COORD = os.path.join(_HERE, "coordinates")
RIPPLE = (150.0, 250.0)
PEAK_Z, EDGE_Z = 5.0, 2.0       # SWR peak > 5σ, boundaries at 2σ
MIN_DUR, MAX_DUR, MERGE = 0.015, 0.250, 0.030   # s
MIN_SAMP = 12_500


def _bp(x, lo, hi, fs):
    b, a = butter(3, [lo / (fs / 2), hi / (fs / 2)], btype="band")
    return filtfilt(b, a, x)


def _ripple_channel(data, fs, intervals):
    """Channel with max ripple-band power within NonREM intervals."""
    nch = data.shape[1]; cand = list(range(0, nch, max(1, nch // 16)))
    s, e = intervals[0]
    i0, i1 = int(s * fs), min(int(e * fs), int(s * fs) + 600_000)
    seg = data[i0:i1, :][:, cand].astype(float)
    best, bp = cand[0], -1.0
    for j, ch in enumerate(cand):
        p = float(np.mean(_bp(seg[:, j], *RIPPLE, fs) ** 2))
        if p > bp:
            bp, best = p, ch
    return best


def _detect_swr(chan, intervals, fs):
    """Detect SWR events within NonREM intervals: ripple envelope z>PEAK_Z, edges at EDGE_Z, dur/merge gated.
    Returns list of (start,stop,peak_t) in absolute time."""
    events = []
    for (s, e) in intervals:
        i0, i1 = int(s * fs), int(e * fs)
        if i1 - i0 < MIN_SAMP:
            continue
        env = np.abs(hilbert(_bp(chan[i0:i1], *RIPPLE, fs)))
        env = gaussian_filter1d(env, int(0.008 * fs))
        z = (env - env.mean()) / (env.std() + 1e-9)
        above = z > EDGE_Z
        # find contiguous runs above EDGE_Z that contain a PEAK_Z crossing
        d = np.diff(above.astype(int))
        starts = np.flatnonzero(d == 1) + 1
        stops = np.flatnonzero(d == -1) + 1
        if above[0]:
            starts = np.r_[0, starts]
        if above[-1]:
            stops = np.r_[stops, above.size]
        for a, b in zip(starts, stops):
            dur = (b - a) / fs
            if dur < MIN_DUR or dur > MAX_DUR:
                continue
            if z[a:b].max() < PEAK_Z:
                continue
            pk = a + int(np.argmax(z[a:b]))
            events.append((s + a / fs, s + b / fs, s + pk / fs))
    # merge events closer than MERGE
    if not events:
        return []
    events.sort()
    merged = [list(events[0])]
    for st, sp, pk in events[1:]:
        if st - merged[-1][1] < MERGE:
            merged[-1][1] = sp
        else:
            merged.append([st, sp, pk])
    return merged


def _task(arg):
    f, sid = arg
    with h5py.File(f, "r") as h:
        lfp = h["processing/ecephys/LFP/LFP"]; data = lfp["data"]
        _, fs = _ts_rate(lfp)
        if fs is None:
            fs = data.shape[0] / h["intervals/epochs/stop_time"][-1]
        cells = _natural_cells(h)
        cell_type = _decode(h["units/cell_type"][:]) if "cell_type" in h["units"] else ["?"] * h["units/id"].shape[0]
        sti = h["units/spike_times_index"][:]; st_all = h["units/spike_times"]
        nU = len(sti)
        nrem = {"PRE": cells.get("PRE-NonREM", []), "POST": cells.get("POST-NonREM", [])}
        all_iv = nrem["PRE"] + nrem["POST"]
        if not all_iv:
            return [], []
        ch = _ripple_channel(data, fs, all_iv)
        chan = data[:, ch].astype(float)
        ev_recs, swr = [], {}
        for ep in ("PRE", "POST"):
            if not nrem[ep]:
                continue
            e = _detect_swr(chan, nrem[ep], fs)
            swr[ep] = e
            dur_min = sum(b - a for a, b in nrem[ep]) / 60.0
            ev_recs.append({"substrate": "buzsaki-swr-event", "session": sid, "epoch": ep,
                            "channel": int(ch), "n_swr": len(e), "nrem_min": dur_min,
                            "swr_rate_per_min": len(e) / dur_min if dur_min > 0 else None,
                            "computed_date": date.today().isoformat()})
        # per-cell participation over POST SWRs (replay-relevant); fall back to all if no POST
        target = swr.get("POST") or swr.get("PRE") or []
        cell_recs = []
        if target:
            wins = np.array([(a, b) for a, b, _ in target])
            for i in range(nU):
                spk = st_all[(0 if i == 0 else int(sti[i - 1])):int(sti[i])]
                hit = 0; nsp = 0
                for (a, b) in wins:
                    c = int(np.sum((spk >= a) & (spk < b)))
                    if c > 0:
                        hit += 1
                    nsp += c
                tot_t = float(np.sum(wins[:, 1] - wins[:, 0]))
                cell_recs.append({"substrate": "buzsaki-swr-cell", "session": sid, "unit": i,
                                  "cell_type": cell_type[i], "epoch": "POST" if swr.get("POST") else "PRE",
                                  "swr_participation": hit / len(wins), "swr_rate": nsp / tot_t if tot_t > 0 else None,
                                  "computed_date": date.today().isoformat()})
        return ev_recs, cell_recs


def run(n_sessions=1, all_sessions=False, workers=8):
    files = sorted(glob.glob(BUZ_GLOB))
    if not all_sessions:
        files = files[:n_sessions]
    tasks = [(f, os.path.basename(f).replace(".nwb", "")) for f in files]
    print(f"BUZSAKI SWR (cycle 2c-a) — {len(tasks)} session(s), {workers}w")
    eo = open(os.path.join(COORD, "buzsaki-swr-event.jsonl"), "w")
    co = open(os.path.join(COORD, "buzsaki-swr-cell.jsonl"), "w")
    t0 = time.perf_counter(); ne = nc = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for evr, cer in ex.map(_task, tasks):
            for r in evr:
                eo.write(json.dumps(r) + "\n"); ne += 1
            for r in cer:
                co.write(json.dumps(r) + "\n"); nc += 1
            eo.flush(); co.flush()
    eo.close(); co.close()
    print(f"→ {ne} event-summary + {nc} per-cell records in {(time.perf_counter()-t0)/60:.1f} min\n")
    _analyse()


def _analyse():
    from scipy import stats
    ev = [json.loads(l) for l in open(os.path.join(COORD, "buzsaki-swr-event.jsonl"))]
    cell = [json.loads(l) for l in open(os.path.join(COORD, "buzsaki-swr-cell.jsonl"))]

    print("(2c-1) SWR RATE — PRE-NonREM vs POST-NonREM (events/min), per session + paired:")
    by = {}
    for r in ev:
        if isinstance(r.get("swr_rate_per_min"), float):
            by.setdefault(r["session"], {})[r["epoch"]] = r["swr_rate_per_min"]
    pre, post = [], []
    for s, d in by.items():
        if "PRE" in d and "POST" in d:
            pre.append(d["PRE"]); post.append(d["POST"])
    if pre:
        w = stats.wilcoxon(pre, post) if len(pre) >= 5 else (None, None)
        print(f"     PRE mean={np.mean(pre):.2f}/min  POST mean={np.mean(post):.2f}/min  "
              f"Δ={np.mean(post)-np.mean(pre):+.2f}  (n={len(pre)} sess, Wilcoxon p={w[1] if w[1] else 'n/a'})")
        print(f"     per-session POST−PRE: {[round(po-pr,1) for pr,po in zip(pre,post)]}")

    # cross-ref participation with class + place-quality
    ks, pf = {}, {}
    cp = os.path.join(COORD, "buzsaki-port-cell.jsonl")
    if os.path.exists(cp):
        for l in open(cp):
            r = json.loads(l)
            if r.get("natural_cell") == "Maze-Awake":
                ks[(r["session"], r["unit"])] = r["axes_computed"].get("I.5q_ks_gue_med")
    pp = os.path.join(COORD, "buzsaki-placefields.jsonl")
    if os.path.exists(pp):
        for l in open(pp):
            r = json.loads(l)
            pf[(r["session"], r["unit"])] = r
    print("\n(2c-2) SWR PARTICIPATION ↔ per-cell class + place-coding quality "
          "(EXC-ONLY primary — interneurons dominate participation, see cell-type below):")
    def _rho(pairs):
        return stats.spearmanr([a for a, _ in pairs], [b for _, b in pairs])[0] if len(pairs) >= 8 else None
    # ks_gue, all vs exc-only
    mk = [(ks[(r["session"], r["unit"])], r) for r in cell
          if (r["session"], r["unit"]) in ks and isinstance(ks[(r["session"], r["unit"])], float)
          and isinstance(r.get("swr_participation"), float)]
    ra = _rho([(g, r["swr_participation"]) for g, r in mk])
    re = _rho([(g, r["swr_participation"]) for g, r in mk if r.get("cell_type") == "excitatory"])
    print(f"     ρ(participation, ks_gue):          all={('%+.3f'%ra) if ra else '-'}  EXC={('%+.3f'%re) if re else '-'}  (n_all={len(mk)})")
    # place-coherence, all vs exc-only
    mp = [(pf[(r["session"], r["unit"])], r) for r in cell if (r["session"], r["unit"]) in pf
          and isinstance(r.get("swr_participation"), float)]
    coh_a = [(p["spatial_coherence"], r["swr_participation"]) for p, r in mp if isinstance(p.get("spatial_coherence"), float)]
    coh_e = [(p["spatial_coherence"], r["swr_participation"]) for p, r in mp
             if isinstance(p.get("spatial_coherence"), float) and r.get("cell_type") == "excitatory"]
    print(f"     ρ(participation, place-coherence): all={('%+.3f'%_rho(coh_a)) if _rho(coh_a) else '-'}  "
          f"EXC={('%+.3f'%_rho(coh_e)) if _rho(coh_e) else '-'}  (n_all={len(coh_a)})")
    # place-cell vs non, EXC only (place-coding is a pyramidal property)
    pc = [r["swr_participation"] for p, r in mp if p.get("is_place_cell") and r.get("cell_type") == "excitatory"]
    npc = [r["swr_participation"] for p, r in mp if not p.get("is_place_cell") and r.get("cell_type") == "excitatory"]
    if len(pc) >= 5 and len(npc) >= 5:
        u, pv = stats.mannwhitneyu(pc, npc, alternative="two-sided")
        print(f"     [EXC] place-cells participation med={np.median(pc):.3f} (n={len(pc)}) vs non-place "
              f"med={np.median(npc):.3f} (n={len(npc)})  Mann-Whitney p={pv:.3g}")
    ex = [r["swr_participation"] for r in cell if r.get("cell_type") == "excitatory" and isinstance(r.get("swr_participation"), float)]
    ih = [r["swr_participation"] for r in cell if r.get("cell_type") == "inhibitory" and isinstance(r.get("swr_participation"), float)]
    if ex and ih:
        print(f"     CELL-TYPE CONFOUND: exc med={np.median(ex):.3f} (n={len(ex)}) vs inh med={np.median(ih):.3f} "
              f"(n={len(ih)}) — interneurons participate ~{np.median(ih)/max(np.median(ex),1e-6):.0f}× more")
    print("\nFlag, don't interpret — verdict is Will's.")
    _figure(cell, pf, ks)


def _figure(cell, pf, ks):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    pts = [(ks[(r["session"], r["unit"])], r["swr_participation"], r.get("cell_type")) for r in cell
           if (r["session"], r["unit"]) in ks and isinstance(ks[(r["session"], r["unit"])], float)
           and isinstance(r.get("swr_participation"), float)]
    if pts:
        cols = ["#1f77b4" if c == "excitatory" else "#d62728" for _, _, c in pts]
        a1.scatter([x for x, _, _ in pts], [y for _, y, _ in pts], s=16, c=cols, alpha=0.5, edgecolor="k", linewidth=0.2)
        a1.set_xlabel("ks_gue (Maze-Awake)"); a1.set_ylabel("SWR participation"); a1.set_title("2c: SWR participation ↔ class (blue=exc)"); a1.grid(alpha=0.2)
    pp = [(pf[(r["session"], r["unit"])].get("spatial_coherence"), r["swr_participation"]) for r in cell
          if (r["session"], r["unit"]) in pf and isinstance(pf[(r["session"], r["unit"])].get("spatial_coherence"), float)
          and isinstance(r.get("swr_participation"), float)]
    if pp:
        a2.scatter([x for x, _ in pp], [y for _, y in pp], s=16, alpha=0.5, edgecolor="k", linewidth=0.2)
        a2.set_xlabel("place-coherence (2a)"); a2.set_ylabel("SWR participation"); a2.set_title("2c: SWR participation ↔ place-coding quality"); a2.grid(alpha=0.2)
    p = os.path.join(_HERE, "figures", "P_buzsaki_swr.png")
    fig.tight_layout(); fig.savefig(p, dpi=130); plt.close(fig)
    print("wrote", os.path.relpath(p, _HERE))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--sessions", type=int, default=1)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.run:
        run(a.sessions, all_sessions=a.all, workers=a.workers)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()

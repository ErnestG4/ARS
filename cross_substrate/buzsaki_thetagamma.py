"""
cross_substrate/buzsaki_thetagamma.py — CA1 theta-gamma coupling (cycle 2b): does TEMPORAL organisation
track per-cell universality class, as SPATIAL organisation (place-coherence, 2a) does?

Synthesis under test: organisational QUALITY of neural coding tracks class — spatial (place-coherence, 2a
confirmed ρ=+0.47) AND temporal (theta-gamma CFC). Tests:
  (1) SUBSTRATE Tort MI (theta-phase↔gamma-amplitude), slow (25-50Hz, CA3→CA1) vs fast (60-100Hz, local)
      gamma — by natural cell (STATE-dependence; Colgin: slow↑sleep, fast↑active) + vs avalanche q (G1).
  (2) PER-CELL gamma phase-locking (slow/fast MRL) ↔ ks_gue — does gamma recover the theta signal that
      theta_mrl LOST under the cell-type confound (−0.33→−0.14 exc)? slow vs fast differential.
  (3) does state-dependent CFC parallel the state-gated avalanche (G3, active≫sleep)?

Representative LFP channel = max theta power (Maze). Windows capped for MI tractability. Reuses
buzsaki_selectivity/_port machinery. Out: coordinates/buzsaki-thetagamma-{sub,cell}.jsonl + prints + figure.
Run: --run [--sessions N | --all] [--workers 8].
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

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from cross_substrate.buzsaki_selectivity import _ts_rate, _decode, _maze_window   # noqa: E402
from cross_substrate.buzsaki_port import _natural_cells                            # noqa: E402

BUZ_GLOB = "$HOME/fmexplorer/buzsaki_cache/*.nwb"
COORD = os.path.join(_HERE, "coordinates")
THETA = (6.0, 10.0); SLOW_G = (25.0, 50.0); FAST_G = (60.0, 100.0); DELTA = (1.0, 4.0)
N_PHASE_BINS = 18
MAX_SAMP = 900_000          # cap concatenated LFP per window (~720 s @1250Hz) — plenty of cycles for MI
MIN_SAMP = 12_500           # ≥10 s
THETA_DELTA_RATIO = 2.0     # CFC restricted to theta epochs (theta/delta envelope ratio > this)


def _bandpass(x, lo, hi, fs):
    b, a = butter(3, [lo / (fs / 2), hi / (fs / 2)], btype="band")
    return filtfilt(b, a, x)


def _tort_mi(phase, amp, nbins=N_PHASE_BINS):
    bins = np.linspace(-np.pi, np.pi, nbins + 1)
    idx = np.clip(np.digitize(phase, bins) - 1, 0, nbins - 1)
    m = np.array([amp[idx == j].mean() if np.any(idx == j) else 0.0 for j in range(nbins)])
    s = m.sum()
    if s <= 0:
        return None
    p = m / s
    H = -np.sum(p * np.log(p + 1e-12))
    return float((np.log(nbins) - H) / np.log(nbins))


def _theta_mask(seg, fs):
    """Theta-epoch mask: theta/delta envelope ratio > THETA_DELTA_RATIO (CFC only meaningful in theta states)."""
    from scipy.ndimage import uniform_filter1d
    th = np.abs(hilbert(_bandpass(seg, *THETA, fs)))
    de = np.abs(hilbert(_bandpass(seg, *DELTA, fs)))
    w = int(0.5 * fs)
    ratio = uniform_filter1d(th, w) / (uniform_filter1d(de, w) + 1e-9)
    return ratio > THETA_DELTA_RATIO


def _gated_mi(seg, fs, gamma_band):
    """Tort MI of theta-phase↔gamma-amplitude, restricted to theta epochs."""
    mask = _theta_mask(seg, fs)
    if mask.sum() < MIN_SAMP:
        return None
    ph = np.angle(hilbert(_bandpass(seg, *THETA, fs)))[mask]
    am = np.abs(hilbert(_bandpass(seg, *gamma_band, fs)))[mask]
    return _tort_mi(ph, am)


def _concat_lfp(chan, intervals, fs, cap):
    segs, tot = [], 0
    for (s, e) in intervals:
        i0, i1 = int(s * fs), int(e * fs)
        if i1 <= i0:
            continue
        segs.append(chan[i0:i1]); tot += (i1 - i0)
        if tot >= cap:
            break
    return np.concatenate(segs)[:cap] if segs else np.zeros(0)


def _best_cfc_channel(data, fs, t0, t1):
    """Pick the channel with max theta-gated fast-gamma MI in the Maze window (the CFC channel, not just
    max-theta — coupling is layer-specific and the naive max-theta channel under-detects it)."""
    i0, i1 = max(0, int(t0 * fs)), min(data.shape[0], int(t1 * fs))
    nch = data.shape[1]; cand = list(range(0, nch, max(1, nch // 16)))
    seg = data[i0:i1, :][:, cand].astype(float)
    best, bmi = cand[0], -1.0
    for j, ch in enumerate(cand):
        mi = _gated_mi(seg[:, j], fs, FAST_G)
        if mi is not None and mi > bmi:
            bmi, best = mi, ch
    return best, bmi


def _task(arg):
    f, sid = arg
    sub_recs, cell_recs = [], []
    with h5py.File(f, "r") as h:
        lfp = h["processing/ecephys/LFP/LFP"]; data = lfp["data"]
        _, fs = _ts_rate(lfp)
        if fs is None:
            fs = data.shape[0] / h["intervals/epochs/stop_time"][-1]
        mz = _maze_window(h)
        ch, ch_mi = _best_cfc_channel(data, fs, *(mz if mz else (0, min(data.shape[0] / fs, 600))))
        chan = data[:, ch].astype(float)
        cells = _natural_cells(h)
        cell_type = _decode(h["units/cell_type"][:]) if "cell_type" in h["units"] else ["?"] * h["units/id"].shape[0]
        sti = h["units/spike_times_index"][:]; st_all = h["units/spike_times"]
        # (1) substrate MI per natural cell
        for nc, intervals in cells.items():
            seg = _concat_lfp(chan, intervals, fs, MAX_SAMP)
            if seg.size < MIN_SAMP:
                continue
            mask = _theta_mask(seg, fs)
            sub_recs.append({"substrate": "buzsaki-thetagamma-sub", "session": sid, "natural_cell": nc,
                             "channel": int(ch), "n_samp": int(seg.size), "n_theta_samp": int(mask.sum()),
                             "MI_slow": _gated_mi(seg, fs, SLOW_G), "MI_fast": _gated_mi(seg, fs, FAST_G),
                             "source_artifact": "generated (CA1 substrate theta-gamma Tort MI, theta-gated)",
                             "computed_date": date.today().isoformat()})
        # (2) per-cell gamma phase-locking in Maze-Awake
        if "Maze-Awake" in cells:
            iv = cells["Maze-Awake"]; t0 = iv[0][0]
            seg = _concat_lfp(chan, iv, fs, 2_000_000)
            if seg.size >= MIN_SAMP:
                # build a contiguous-time analytic over Maze window [t0, t0+seg/fs] (Maze is one block)
                sg = hilbert(_bandpass(seg, *SLOW_G, fs)); fg = hilbert(_bandpass(seg, *FAST_G, fs))
                tend = t0 + seg.size / fs
                for i in range(len(sti)):
                    spk = st_all[(0 if i == 0 else int(sti[i - 1])):int(sti[i])]
                    spk = spk[(spk >= t0) & (spk < tend)]
                    if spk.size < 50:
                        continue
                    idx = np.clip(((spk - t0) * fs).astype(int), 0, seg.size - 1)
                    def _mrl(an):
                        z = an[idx]; u = z / np.abs(z)
                        return float(np.abs(np.mean(u)))
                    cell_recs.append({"substrate": "buzsaki-thetagamma-cell", "session": sid, "unit": i,
                                      "cell_type": cell_type[i], "slow_gamma_mrl": _mrl(sg),
                                      "fast_gamma_mrl": _mrl(fg),
                                      "source_artifact": "generated (CA1 per-cell gamma phase-lock, Maze)",
                                      "computed_date": date.today().isoformat()})
    return sub_recs, cell_recs


def run(n_sessions=1, all_sessions=False, workers=8):
    files = sorted(glob.glob(BUZ_GLOB))
    if not all_sessions:
        files = files[:n_sessions]
    tasks = [(f, os.path.basename(f).replace(".nwb", "")) for f in files]
    print(f"BUZSAKI THETA-GAMMA (cycle 2b) — {len(tasks)} session(s), {workers}w")
    subo = open(os.path.join(COORD, "buzsaki-thetagamma-sub.jsonl"), "w")
    cello = open(os.path.join(COORD, "buzsaki-thetagamma-cell.jsonl"), "w")
    t0 = time.perf_counter(); ns = nc = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for subr, cellr in ex.map(_task, tasks):
            for r in subr:
                subo.write(json.dumps(r) + "\n"); ns += 1
            for r in cellr:
                cello.write(json.dumps(r) + "\n"); nc += 1
            subo.flush(); cello.flush()
    subo.close(); cello.close()
    print(f"→ {ns} substrate + {nc} per-cell records in {(time.perf_counter()-t0)/60:.1f} min\n")
    _analyse()


def _analyse():
    from scipy import stats
    sub = [json.loads(l) for l in open(os.path.join(COORD, "buzsaki-thetagamma-sub.jsonl"))]
    cell = [json.loads(l) for l in open(os.path.join(COORD, "buzsaki-thetagamma-cell.jsonl"))]
    NC = ["PRE-NonREM", "PRE-REM", "Maze-Awake", "POST-NonREM", "POST-REM", "Awake-in-sleep"]

    print("(2b-1) SUBSTRATE Tort MI by natural cell (slow 25-50 / fast 60-100 Hz):")
    for nc in NC:
        s = [r["MI_slow"] for r in sub if r["natural_cell"] == nc and isinstance(r.get("MI_slow"), float)]
        fst = [r["MI_fast"] for r in sub if r["natural_cell"] == nc and isinstance(r.get("MI_fast"), float)]
        if s or fst:
            print(f"     {nc:14s} MI_slow={np.mean(s):.4f} (n={len(s)})  MI_fast={np.mean(fst):.4f} (n={len(fst)})")
    # state contrast: slow gamma sleep vs fast gamma active (Colgin)
    def _grp(band, ncs):
        return [r[band] for r in sub if r["natural_cell"] in ncs and isinstance(r.get(band), float)]
    sleep, active = ["PRE-NonREM", "POST-NonREM", "PRE-REM", "POST-REM"], ["Maze-Awake"]
    print(f"     [Colgin check] slow MI sleep={np.mean(_grp('MI_slow',sleep)):.4f} vs active={np.mean(_grp('MI_slow',active)):.4f} | "
          f"fast MI sleep={np.mean(_grp('MI_fast',sleep)):.4f} vs active={np.mean(_grp('MI_fast',active)):.4f}")

    # cross-ref MI vs avalanche q (G1)
    pop = {}
    pp = os.path.join(COORD, "buzsaki-port-pop.jsonl")
    if os.path.exists(pp):
        for l in open(pp):
            r = json.loads(l)
            if r["aggregation"] == "avl-onset" and r["cell_type"] == "all":
                pop[(r["session"], r["natural_cell"])] = r["axes_computed"].get("I.8_brody_q")
    pairs_s = [(pop[(r["session"], r["natural_cell"])], r["MI_slow"]) for r in sub
               if (r["session"], r["natural_cell"]) in pop and isinstance(pop[(r["session"], r["natural_cell"])], float)
               and isinstance(r.get("MI_slow"), float)]
    pairs_f = [(pop[(r["session"], r["natural_cell"])], r["MI_fast"]) for r in sub
               if (r["session"], r["natural_cell"]) in pop and isinstance(pop[(r["session"], r["natural_cell"])], float)
               and isinstance(r.get("MI_fast"), float)]
    if len(pairs_s) >= 8:
        print(f"\n(2b-cross) MI vs avalanche q (G1 intermediate): slow ρ={stats.spearmanr([a for a,_ in pairs_s],[b for _,b in pairs_s])[0]:+.3f} "
              f"fast ρ={stats.spearmanr([a for a,_ in pairs_f],[b for _,b in pairs_f])[0]:+.3f} (n={len(pairs_s)})")

    # (2b-2) per-cell gamma MRL vs ks_gue (the cell-type-confound probe)
    ks = {}
    cp = os.path.join(COORD, "buzsaki-port-cell.jsonl")
    if os.path.exists(cp):
        for l in open(cp):
            r = json.loads(l)
            if r.get("natural_cell") == "Maze-Awake":
                ks[(r["session"], r["unit"])] = r["axes_computed"].get("I.5q_ks_gue_med")
    merged = [(ks[(r["session"], r["unit"])], r) for r in cell
              if (r["session"], r["unit"]) in ks and isinstance(ks[(r["session"], r["unit"])], float)]
    print(f"\n(2b-2) PER-CELL gamma MRL ↔ ks_gue (Maze-Awake) — merged {len(merged)} cells:")
    for band in ["slow_gamma_mrl", "fast_gamma_mrl"]:
        a = [(g, r[band]) for g, r in merged if isinstance(r.get(band), float)]
        e = [(g, r[band]) for g, r in merged if r.get("cell_type") == "excitatory" and isinstance(r.get(band), float)]
        ra = stats.spearmanr([x for x, _ in a], [y for _, y in a])[0] if len(a) >= 8 else None
        re = stats.spearmanr([x for x, _ in e], [y for _, y in e])[0] if len(e) >= 8 else None
        print(f"     {band:16s} ρ(all)={('%+.3f'%ra) if ra is not None else '-':>7s}  ρ(exc)={('%+.3f'%re) if re is not None else '-':>7s}"
              f"   [theta_mrl was −0.33 all / −0.14 exc]")
    print("\nFlag, don't interpret — verdict is Will's.")
    _figure(sub, merged)


def _figure(sub, merged):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    NC = ["PRE-NonREM", "PRE-REM", "Maze-Awake", "POST-NonREM", "POST-REM", "Awake-in-sleep"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    ncs = [n for n in NC if any(r["natural_cell"] == n for r in sub)]
    for band, lab in [("MI_slow", "slow γ (25-50)"), ("MI_fast", "fast γ (60-100)")]:
        ys = [np.mean([r[band] for r in sub if r["natural_cell"] == n and isinstance(r.get(band), float)] or [np.nan]) for n in ncs]
        a1.plot(range(len(ncs)), ys, "o-", label=lab, ms=5)
    a1.set_xticks(range(len(ncs))); a1.set_xticklabels(ncs, rotation=35, ha="right", fontsize=7)
    a1.set_ylabel("Tort MI"); a1.set_title("2b-1: theta-gamma CFC by state (slow vs fast)"); a1.legend(fontsize=7); a1.grid(alpha=0.2)
    for band, c in [("slow_gamma_mrl", "#1f77b4"), ("fast_gamma_mrl", "#d62728")]:
        pts = [(r[band], g) for g, r in merged if isinstance(r.get(band), float)]
        if pts:
            a2.scatter([x for x, _ in pts], [y for _, y in pts], s=14, alpha=0.4, color=c, label=band)
    a2.set_xlabel("per-cell gamma MRL"); a2.set_ylabel("ks_gue (Maze-Awake)")
    a2.set_title("2b-2: per-cell gamma phase-lock ↔ class"); a2.legend(fontsize=7); a2.grid(alpha=0.2)
    p = os.path.join(_HERE, "figures", "P_buzsaki_thetagamma.png")
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

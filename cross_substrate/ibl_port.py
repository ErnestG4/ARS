"""
cross_substrate/ibl_port.py — IBL Brain-Wide-Map framework-port (THIRD substrate, pillar-2 falsification test).

Applies the Allen+Buzsáki-hardened tooling to IBL (DANDI 000409, processed NWBs) — a third substrate CLASS
(cortex+subcortex during a visual decision task). Tests the now-triangulated cross-substrate pillars:
  PILLAR 1 (structural anchors): do corr-eig→GUE and sync-event→Poisson hold on IBL?
  PILLAR 2 (H1, per-cell extrinsic-selectivity-quality↔class): IBL's selectivity axis is CONTRAST tuning
    (visual) + CHOICE selectivity (decision) — does either track per-cell ks_gue? (third substrate-general test)
Per-cell: ks_gue + Family I; contrast_tuning (|ρ(rate, |contrast|)| over trials) + choice_selectivity
(2|AUC−.5| of stim-window rate by wheel choice) — both EXTRINSIC (intrinsic-vs-extrinsic discipline).
Cell-type via spike width (peak_to_trough; narrow=putative interneuron). Population: 3 trustable observables.

Reuses ars_classify + population_fingerprint observables. Out: coordinates/ibl-port-{cell,pop}.jsonl.
Run: --run [--all] [--workers 6].
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

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for p in (_ROOT, os.path.join(_ROOT, "phase22a")):
    if p not in sys.path:
        sys.path.insert(0, p)

from ars_classify import classify                                                # noqa: E402
from cross_substrate.axes import canonical_spacings, FAMILY_I                     # noqa: E402
from cross_substrate.population_fingerprint import _corr_eig, _avalanche_onsets, _sync_events, _fp, _f  # noqa: E402

IBL_GLOB = "/home/combust/fmexplorer/ibl_cache/*.nwb"
COORD = os.path.join(_HERE, "coordinates")
STIM_WIN = 0.4          # s post stimulus-onset for rate
NARROW_MS = 0.40        # spike-width split: narrow (<0.40ms) = putative interneuron
DT = 0.025
MIN_SPIKES = 50


def _decode(a):
    return [x.decode() if isinstance(x, bytes) else x for x in a]


def _rate_in(spk, starts, win):
    """Per-trial firing rate in [start, start+win]."""
    return np.array([np.sum((spk >= s) & (spk < s + win)) / win for s in starts])


def _auc(x, y):
    """AUC of separating x (group1) from y (group0) — Mann-Whitney U / (n1 n2)."""
    from scipy.stats import rankdata
    if len(x) < 5 or len(y) < 5:
        return None
    allv = np.concatenate([x, y]); r = rankdata(allv)
    r1 = r[:len(x)].sum()
    return float((r1 - len(x) * (len(x) + 1) / 2) / (len(x) * len(y)))


def _task(arg):
    f, sid, visual_only = arg if len(arg) == 3 else (arg[0], arg[1], False)
    cell_recs = []
    with h5py.File(f, "r") as h:
        u = h["units"]
        sti = u["spike_times_index"][:]; st_all = u["spike_times"]
        nU = len(sti)
        ks_lab = _decode(u["kilosort2_label"][:]) if "kilosort2_label" in u else ["?"] * nU
        ptt = u["peak_to_trough_duration_ms"][:] if "peak_to_trough_duration_ms" in u else np.full(nU, np.nan)
        # region per unit via max_electrode → electrodes/location (CCF full name)
        try:
            eloc = np.array(_decode(h["general/extracellular_ephys/electrodes/location"][:]))
            me = u["max_electrode"][:]
            ureg = [str(eloc[e]) if 0 <= e < len(eloc) else "?" for e in me]
        except Exception:
            ureg = ["?"] * nU
        # trials
        tr = h["intervals/trials"]
        onset = tr["gabor_stimulus_onset_time"][:]
        contrast = np.abs(tr["gabor_stimulus_contrast"][:])
        choice = tr["mouse_wheel_choice"][:]
        good = np.isfinite(onset)
        onset, contrast, choice = onset[good], contrast[good], choice[good]
        per_unit = [st_all[(0 if i == 0 else int(sti[i - 1])):int(sti[i])] for i in range(nU)]
        for i in range(nU):
            spk = per_unit[i]
            if spk.size < MIN_SPIKES:
                continue
            is_vis = ("visual" in ureg[i].lower() or "geniculate" in ureg[i].lower())
            if visual_only and not is_vis:
                continue            # skip expensive per-cell classify for non-visual cells (pop still uses all)
            try:
                i5q = _f(classify(spk).get("ks_gue_med"))
            except Exception:
                i5q = None
            fI = {k: _f(fn(canonical_spacings(spk))) for k, fn in FAMILY_I.items()}
            # extrinsic selectivity
            rate = _rate_in(spk, onset, STIM_WIN)
            ct = None
            if np.unique(contrast).size >= 2 and rate.std() > 0:
                from scipy.stats import spearmanr
                ct = abs(float(spearmanr(rate, contrast)[0]))
            csel = None
            lc, rc = choice == np.unique(choice)[0], choice == np.unique(choice)[-1]
            if np.unique(choice).size >= 2:
                a = _auc(rate[lc], rate[rc])
                csel = abs(2 * (a - 0.5)) if a is not None else None
            cell_recs.append({"substrate": "ibl-port-cell", "session": sid, "unit": i,
                              "region": ureg[i], "is_visual": ("visual" in ureg[i].lower() or "geniculate" in ureg[i].lower()),
                              "ks_label": ks_lab[i], "spike_width_ms": _f(ptt[i]),
                              "cell_type": ("narrow" if ptt[i] < NARROW_MS else "wide") if np.isfinite(ptt[i]) else "?",
                              "n": int(spk.size), "contrast_tuning": ct, "choice_selectivity": csel,
                              "axes_computed": {"I.5q_ks_gue_med": i5q, **fI},
                              "source_artifact": "generated (IBL per-cell fingerprint + selectivity)",
                              "computed_date": date.today().isoformat()})
        # population observables over the task span (skip in visual_only — pillar-1 already established n=3,
        # and the big visual sessions' 2500-unit matrix OOMs the pool)
        if visual_only:
            return cell_recs, []
        t0, t1 = float(onset.min()), float(onset.max() + 2.0)
        nb = max(4, int((t1 - t0) / DT)); edges = np.linspace(t0, t1, nb + 1)
        keep = [s for s in per_unit if s.size >= MIN_SPIKES]
        M = np.array([np.histogram(s[(s >= t0) & (s < t1)], bins=edges)[0] for s in keep], float).T
        pooled = np.sort(np.concatenate([s[(s >= t0) & (s < t1)] for s in keep])) if keep else np.zeros(0)
        isi = np.diff(pooled); dtav = float(np.mean(isi[isi > 0])) if (isi > 0).any() else 5e-3
        pop_recs = []
        for agg, obj in {"corr-eig": _corr_eig(M), "avl-onset": _avalanche_onsets(pooled, dtav),
                         "sync-event": _sync_events(M, edges)}.items():
            if obj is None or len(obj) < 50:
                continue
            fp = _fp(obj, is_positions=True)
            pop_recs.append({"substrate": "ibl-port-pop", "session": sid, "aggregation": agg,
                             "n_units": len(keep), "n": int(len(obj)), "axes_computed": fp,
                             "source_artifact": "generated (IBL population aggregation)",
                             "computed_date": date.today().isoformat()})
    return cell_recs, pop_recs


def run(all_sessions=False, workers=6, visual_only=False, glob_pat=None):
    files = sorted(glob.glob(glob_pat or IBL_GLOB))
    tasks = [(f, os.path.basename(f).split("_ses-")[0].replace("sub-", "").replace("vis-", "") + "/" +
              (os.path.basename(f).split("_ses-")[1][:8] if "_ses-" in os.path.basename(f) else os.path.basename(f)[:8]),
              visual_only) for f in files]
    suf = "-visual" if visual_only else ""
    print(f"IBL PORT — {len(tasks)} session(s), {workers}w (visual_only={visual_only})")
    co = open(os.path.join(COORD, f"ibl-port-cell{suf}.jsonl"), "w")
    po = open(os.path.join(COORD, f"ibl-port-pop{suf}.jsonl"), "w")
    t0 = time.perf_counter(); nc = npop = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for cr, pr in ex.map(_task, tasks):
            for r in cr:
                co.write(json.dumps(r) + "\n"); nc += 1
            for r in pr:
                po.write(json.dumps(r) + "\n"); npop += 1
                ax = r["axes_computed"]
                print(f"  {r['session']:28s} {r['aggregation']:11s} n={r['n']:>6d} "
                      f"q={ax.get('I.8_brody_q'):.3f}" if isinstance(ax.get('I.8_brody_q'), float) else
                      f"  {r['session']:28s} {r['aggregation']:11s} q=-", flush=True)
            co.flush(); po.flush()
    co.close(); po.close()
    print(f"\n→ {nc} per-cell + {npop} population records in {(time.perf_counter()-t0)/60:.1f} min\n")
    _analyse()


def _analyse():
    from scipy import stats
    cell, pop = [], []
    for p in glob.glob(os.path.join(COORD, "ibl-port-cell*.jsonl")):
        cell += [json.loads(l) for l in open(p)]
    for p in glob.glob(os.path.join(COORD, "ibl-port-pop*.jsonl")):
        pop += [json.loads(l) for l in open(p)]
    print(f"IBL ANALYSIS — {len(cell)} cells, {len(pop)} pop records, "
          f"{len(set(r['session'] for r in cell))} sessions")
    # PILLAR 1
    print("\n(PILLAR 1) Population structural anchors — do corr-eig→GUE, sync→Poisson hold on IBL?")
    for agg in ("corr-eig", "avl-onset", "sync-event"):
        q = [r["axes_computed"].get("I.8_brody_q") for r in pop if r["aggregation"] == agg
             and isinstance(r["axes_computed"].get("I.8_brody_q"), float)]
        if q:
            print(f"     {agg:11s} q={np.mean(q):.3f}±{np.std(q):.3f} (n={len(q)})  "
                  f"[Allen/CA1: {'corr-eig~GUE 0.85-0.89' if agg=='corr-eig' else 'sync Poisson 0.00' if agg=='sync-event' else 'avl intermediate'}]")
    # PILLAR 2 — H1: extrinsic selectivity ↔ ks_gue
    print("\n(PILLAR 2) H1 — does extrinsic selectivity (contrast/choice) track per-cell ks_gue?")
    ks = [(r["axes_computed"].get("I.5q_ks_gue_med"), r) for r in cell
          if isinstance(r["axes_computed"].get("I.5q_ks_gue_med"), float)]
    for prop in ("contrast_tuning", "choice_selectivity"):
        a = [(g, r[prop]) for g, r in ks if isinstance(r.get(prop), float)]
        w = [(g, r[prop]) for g, r in ks if isinstance(r.get(prop), float) and r.get("cell_type") == "wide"]
        ra = stats.spearmanr([x for x, _ in a], [y for _, y in a])[0] if len(a) >= 8 else None
        rw = stats.spearmanr([x for x, _ in w], [y for _, y in w])[0] if len(w) >= 8 else None
        flag = "  ← H1-CANDIDATE" if (ra is not None and abs(ra) > 0.2) else ""
        print(f"     ks_gue vs {prop:18s}: ρ(all)={('%+.3f'%ra) if ra else '-':>7s}  ρ(wide)={('%+.3f'%rw) if rw else '-':>7s} (n={len(a)}){flag}")
    # PILLAR 2 — region-resolved: contrast-tuning↔class for VISUAL cells only (the proper V1-analog test)
    vis = [(g, r) for g, r in ks if r.get("is_visual")]
    print(f"\n(PILLAR 2 region-resolved) VISUAL cells only (n={len(vis)}) — the proper OSI/contrast analog:")
    for prop in ("contrast_tuning", "choice_selectivity"):
        a = [(g, r[prop]) for g, r in vis if isinstance(r.get(prop), float)]
        if len(a) >= 8:
            rho, p = stats.spearmanr([x for x, _ in a], [y for _, y in a])
            flag = "  ← H1-ANALOGUE" if abs(rho) > 0.2 and p < 0.05 else ""
            print(f"     [VISUAL] ks_gue vs {prop:18s}: ρ={rho:+.3f} (p={p:.3g}, n={len(a)}){flag}")
    # cell-type
    for prop in ("I.5q_ks_gue_med",):
        wi = [r["axes_computed"][prop] for r in cell if r.get("cell_type") == "wide" and isinstance(r["axes_computed"].get(prop), float)]
        na = [r["axes_computed"][prop] for r in cell if r.get("cell_type") == "narrow" and isinstance(r["axes_computed"].get(prop), float)]
        if wi and na:
            print(f"\n     cell-type: ks_gue wide(pyr) med={np.median(wi):.3f} (n={len(wi)}) vs narrow(int) "
                  f"med={np.median(na):.3f} (n={len(na)})")
    print("\nFlag, don't interpret — verdict is Will's.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--visual-only", action="store_true")
    ap.add_argument("--glob", default=None)
    a = ap.parse_args()
    if a.run:
        run(all_sessions=a.all, workers=a.workers, visual_only=a.visual_only, glob_pat=a.glob)
    else:
        ap.error("need --run")


if __name__ == "__main__":
    main()
